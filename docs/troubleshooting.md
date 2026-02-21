# Troubleshooting

Common issues and how to fix them.

## mGBA Version Too Old

**Symptom:** `./startup.sh` exits with "mGBA version X.X is below 0.11" or similar.

**Cause:** The startup script requires mGBA 0.11+ for `--script` auto-load. On Linux, the packaged release (0.10.5) has `--script` disabled even though it appears in `--help`.

**Fix:**

1. Get mGBA 0.11+ from the [development downloads](https://mgba.io/downloads.html#development-downloads) (Ubuntu AppImage or build from source).
2. Or build from source. See the mGBA repo for build instructions.
3. Verify: run `mgba-qt --version` — you should see 0.11 or higher.

See [Getting Started](getting-started.md) Prerequisites for more detail.

---

## Ollama Not Installed

**Symptom:** `./startup.sh` exits with "ollama not found in PATH".

**Cause:** The default config uses Ollama. The script checks for `ollama` before launch.

**Fix:**

1. Install Ollama: `curl -fsSL https://ollama.com/install.sh | sh`
2. Pull a model: `ollama pull qwen2.5:7b`
3. Start the server when prompted by the script, or run `ollama serve` in a separate terminal before `./startup.sh`.

To use a different LLM backend (LM Studio, llama.cpp, etc.), edit `config.json` and set `backend` and `base_url` accordingly. The script will still check for `ollama`; if you use another backend exclusively, you may need to modify the script or install a dummy `ollama` for the check to pass. (Future versions may make this config-aware.)

See [Getting Started](getting-started.md) for backend options.

---

## "Waiting for state.json from mGBA..."

**Symptom:** The bridge prints "Waiting for state.json from mGBA..." and never advances.

**Cause:** The Lua script and bridge use different paths for the `data/` folder. They must share the same location.

**Fix:**

1. Start **both** mGBA and the bridge from the project root:
   ```bash
   cd ~/GitHub/llm-plays-pokemon
   # Terminal 1: mGBA
   mgba-qt --script lua/game_agent.lua gamefile/Pokemon_\ FireRed\ Version.zip
   # Terminal 2: bridge (after mGBA is running)
   source .venv/bin/activate && python3 -m bridge
   ```

2. The bridge writes `lua/data_dir.txt` on startup with the absolute path to `data/`. The Lua script reads this so both use the same folder. If you start mGBA before the bridge, the Lua script falls back to relative `"data"` — which works only when mGBA's working directory is the project root.

3. Ensure the game has loaded (past the title screen). The Lua script only writes state when a game is active.

---

## LLM Not Reachable

**Symptom:** Bridge shows "not reachable (will retry)" or times out on requests.

**Cause:** The LLM backend is not running, wrong port, or wrong URL.

**Fix:**

1. **Check the backend is running:** Ollama needs `ollama serve`. LM Studio must have the local server started. llama.cpp/llamafile must be serving.

2. **Check `config.json`** `base_url`:
   - Ollama (default): `http://localhost:11434`
   - LM Studio: `http://localhost:1234`
   - llama.cpp / llamafile: `http://localhost:8080` (or your configured port)

3. **Ollama native API:** If using `"backend": "ollama"`, set `"model"` (e.g. `"qwen2.5:7b"`). The native Ollama API requires a model name.

4. **Firewall:** Ensure nothing is blocking localhost connections to the LLM port.

---

## mGBA Script Not Loading

**Symptom:** No "Lateral Red (LR-1) game agent loaded" message. Game runs but bridge never gets state.

**Cause:** The Lua script was not loaded into mGBA.

**Fix:**

1. **mGBA 0.11+:** Use `--script` when launching:
   ```bash
   mgba-qt --script lua/game_agent.lua gamefile/Pokemon_\ FireRed\ Version.zip
   ```

2. **Linux known limitation:** The published mGBA release (0.10.5) on Linux shows `--script` in `--help` but it is **disabled**. For `--script` to work on Linux, you must use mGBA 0.11+ from the [development downloads](https://mgba.io/downloads.html#development-downloads) (Ubuntu AppImage or build from source). The packaged `sudo apt install mgba-qt` will not support `--script`.

3. **mGBA 0.10 (or packaged Linux build):** Load manually: **Tools > Scripting > File > Load Script** → select `lua/game_agent.lua`.

4. **Check version:** Run `mgba-qt --version`. If you see 0.10.x from a Linux package, use development builds or build from source for 0.11+.

5. **Working directory:** mGBA must be started from the project root so `lua/game_agent.lua` resolves correctly. Use `cd ~/GitHub/llm-plays-pokemon` before launching.

---

## Wrong ROM or Game Version

**Symptom:** Garbage data, crashes, or nonsensical state.

**Cause:** Lateral Red targets **Pokemon FireRed US v1.0** (game code BPRE). Other ROMs (Ruby, Sapphire, Emerald, non-US) use different memory layouts.

**Fix:** Use a FireRed or LeafGreen US v1.0 ROM (game code BPRE/BPGE) in `gamefile/`. See [Getting Started](getting-started.md#prerequisites) for notes on obtaining a legally owned ROM backup.

---

## Empty or Malformed LLM Response

**Symptom:** Bridge shows "(empty response, using safe default)" or fails to parse JSON.

**Cause:** The model returned text that isn't valid JSON, or returned nothing.

**Fix:**

1. **Temperature:** Lower `temperature` in config (e.g. 0.2) for more consistent structured output.

2. **Model capability:** Use a model with strong instruction-following (Qwen 2.5, Llama 3.1, Mistral). Small models may struggle with strict JSON.

3. **max_tokens:** Ensure `max_tokens` is at least 200–300 so the model has room to respond.

---

## Venv or Python Not Found

**Symptom:** `python3 -m bridge` fails with module or venv errors.

**Fix:**

1. Use `./startup.sh` — it creates `.venv` and installs dependencies automatically.
2. If running the bridge manually, activate the project venv:
   ```bash
   source .venv/bin/activate
   python3 -m bridge
   ```
3. Or set `LATERAL_RED_VENV` to an existing venv path; see [Reference](reference.md).

---
*Last updated: 2026-02-21*
