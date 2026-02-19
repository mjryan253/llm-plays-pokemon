"""
Universal LLM client supporting any OpenAI-compatible API (Ollama, LM Studio,
llama.cpp server, llamafile) and the native Ollama chat API.
"""

import json
import logging
import time

import requests

log = logging.getLogger(__name__)


class LLMClient:
    """
    Config-driven LLM client.

    backend: "openai-compat" | "ollama"
      - openai-compat: POST {base_url}/v1/chat/completions  (works with
        Ollama's compat endpoint, LM Studio, llama.cpp, llamafile, cloud APIs)
      - ollama: POST {base_url}/api/chat  (native Ollama streaming format)
    """

    def __init__(self, config: dict):
        self.backend   = config.get("backend", "openai-compat")
        self.base_url  = config.get("base_url", "http://localhost:1234").rstrip("/")
        self.model     = config.get("model")
        self.temp      = config.get("temperature", 0.3)
        self.max_tok   = config.get("max_tokens", 300)
        self.api_key   = config.get("api_key")
        self.timeout   = config.get("timeout_seconds", 30)
        self._session  = requests.Session()

    def _headers(self):
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def chat(self, messages: list[dict]) -> str:
        """
        Send a chat completion request and return the assistant's text.

        messages: list of {"role": "system"|"user"|"assistant", "content": str}
        """
        if self.backend == "ollama":
            return self._chat_ollama(messages)
        return self._chat_openai_compat(messages)

    def _chat_openai_compat(self, messages: list[dict]) -> str:
        url = f"{self.base_url}/v1/chat/completions"
        payload = {
            "messages": messages,
            "temperature": self.temp,
            "max_tokens": self.max_tok,
            "stream": False,
        }
        if self.model:
            payload["model"] = self.model

        for attempt in range(3):
            try:
                resp = self._session.post(
                    url, headers=self._headers(),
                    data=json.dumps(payload), timeout=self.timeout,
                )
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            except (requests.RequestException, KeyError, IndexError) as exc:
                log.warning("LLM request failed (attempt %d): %s", attempt + 1, exc)
                if attempt < 2:
                    time.sleep(2 ** attempt)
        return ""

    def _chat_ollama(self, messages: list[dict]) -> str:
        """Native Ollama /api/chat (non-streaming)."""
        url = f"{self.base_url}/api/chat"
        payload = {
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.temp,
                "num_predict": self.max_tok,
            },
        }
        if self.model:
            payload["model"] = self.model
        else:
            log.warning("Ollama native API requires a model name -- set 'model' in config")

        for attempt in range(3):
            try:
                resp = self._session.post(
                    url, headers=self._headers(),
                    data=json.dumps(payload), timeout=self.timeout,
                )
                resp.raise_for_status()
                data = resp.json()
                return data.get("message", {}).get("content", "")
            except (requests.RequestException, KeyError) as exc:
                log.warning("Ollama request failed (attempt %d): %s", attempt + 1, exc)
                if attempt < 2:
                    time.sleep(2 ** attempt)
        return ""

    def health_check(self) -> bool:
        """Quick check that the backend is reachable."""
        try:
            if self.backend == "ollama":
                r = self._session.get(f"{self.base_url}/api/tags", timeout=5)
            else:
                r = self._session.get(f"{self.base_url}/v1/models", timeout=5)
            return r.status_code == 200
        except requests.RequestException:
            return False
