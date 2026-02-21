# Troubleshooting

Common issues and how to fix them.

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
   source ~/GitHub/venv1/bin/activate && python3 -m bridge
   ```

2. The bridge writes `lua/data_dir.txt` on startup with the absolute path to `data/`. The Lua script reads this so both use the same folder. If you start mGBA before the bridge, the Lua script falls back to relative `"data"` — which works only when mGBA's working directory is the project root.

3. Ensure the game has loaded (past the title screen). The Lua script only writes state when a game is active.

---

## LLM Not Reachable

**Symptom:** Bridge shows "not reachable (will retry)" or times out on requests.

**Cause:** The LLM backend is not running, wrong port, or wrong URL.

**Fix:**

1. **Check the backend is running:** LM Studio must have the local server started. Ollama needs `ollama serve`. llama.cpp/llamafile must be serving.

2. **Check `config.json`** `base_url`:
   - LM Studio: `http://localhost:1234`
   - Ollama: `http://localhost:11434`
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

1. Activate the venv before running:
   ```bash
   source ~/GitHub/venv1/bin/activate
   python3 -m bridge
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---
*Last updated: 2026-02-21*
