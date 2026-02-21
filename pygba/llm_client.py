"""
Streaming LLM client supporting Ollama native API and OpenAI-compatible APIs.

Provides both streaming (with on_token callback for live display) and
non-streaming fallback modes.
"""

import json
import logging
import time

import requests

log = logging.getLogger(__name__)


class StreamingLLMClient:
    """
    Config-driven LLM client with streaming support.

    backend: "ollama" | "openai-compat"
      - ollama: POST {base_url}/api/chat  (native newline-delimited JSON stream)
      - openai-compat: POST {base_url}/v1/chat/completions  (SSE stream)
    """

    def __init__(self, config: dict):
        self.backend   = config.get("backend", "ollama")
        self.base_url  = config.get("base_url", "http://localhost:11434").rstrip("/")
        self.model     = config.get("model")
        self.temp      = config.get("temperature", 0.3)
        self.max_tok   = config.get("max_tokens", 512)
        self.api_key   = config.get("api_key")
        self.timeout   = config.get("timeout_seconds", 60)
        self._session  = requests.Session()

    def _headers(self):
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def chat(self, messages):
        """Non-streaming fallback. Returns the full response text."""
        return self.chat_stream(messages, on_token=None)

    def chat_stream(self, messages, on_token=None):
        """Streaming chat. Calls on_token(text) per chunk. Returns full text.

        Falls back to non-streaming if on_token is None.
        """
        if self.backend == "ollama":
            return self._stream_ollama(messages, on_token)
        return self._stream_openai_compat(messages, on_token)

    # ── Ollama native streaming ─────────────────────────────────────

    def _stream_ollama(self, messages, on_token=None):
        url = f"{self.base_url}/api/chat"
        stream = on_token is not None
        payload = {
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": self.temp,
                "num_predict": self.max_tok,
            },
        }
        if self.model:
            payload["model"] = self.model
        else:
            log.warning("Ollama requires a model name -- set 'model' in config")

        for attempt in range(3):
            try:
                resp = self._session.post(
                    url, headers=self._headers(),
                    data=json.dumps(payload),
                    timeout=self.timeout,
                    stream=stream,
                )
                resp.raise_for_status()

                if not stream:
                    data = resp.json()
                    return data.get("message", {}).get("content", "")

                # Newline-delimited JSON stream
                full_text = []
                for line in resp.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    token = chunk.get("message", {}).get("content", "")
                    if token:
                        full_text.append(token)
                        on_token(token)
                    if chunk.get("done"):
                        break
                return "".join(full_text)

            except (requests.RequestException, KeyError) as exc:
                log.warning("Ollama request failed (attempt %d): %s", attempt + 1, exc)
                if attempt < 2:
                    time.sleep(2 ** attempt)
        return ""

    # ── OpenAI-compatible streaming (SSE) ───────────────────────────

    def _stream_openai_compat(self, messages, on_token=None):
        url = f"{self.base_url}/v1/chat/completions"
        stream = on_token is not None
        payload = {
            "messages": messages,
            "temperature": self.temp,
            "max_tokens": self.max_tok,
            "stream": stream,
        }
        if self.model:
            payload["model"] = self.model

        for attempt in range(3):
            try:
                resp = self._session.post(
                    url, headers=self._headers(),
                    data=json.dumps(payload),
                    timeout=self.timeout,
                    stream=stream,
                )
                resp.raise_for_status()

                if not stream:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]

                # SSE format: lines starting with "data: "
                full_text = []
                for line in resp.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    token = delta.get("content", "")
                    if token:
                        full_text.append(token)
                        on_token(token)
                return "".join(full_text)

            except (requests.RequestException, KeyError, IndexError) as exc:
                log.warning("LLM request failed (attempt %d): %s", attempt + 1, exc)
                if attempt < 2:
                    time.sleep(2 ** attempt)
        return ""

    # ── health check ────────────────────────────────────────────────

    def health_check(self):
        """Quick check that the backend is reachable."""
        try:
            if self.backend == "ollama":
                r = self._session.get(f"{self.base_url}/api/tags", timeout=5)
            else:
                r = self._session.get(f"{self.base_url}/v1/models", timeout=5)
            return r.status_code == 200
        except requests.RequestException:
            return False
