# Troubleshooting

Common issues and how to fix them. Issues are labeled with which component they apply to, or **Both** if shared.

---

## mGBA Version Too Old (mgba-lua)

**Symptom:** `./startup.sh` exits with "mGBA version X.X is below 0.11" or similar.

**Cause:** The startup script requires mGBA 0.11+ for `--script` auto-load. On Linux, the packaged release (0.10.5) has `--script` disabled even though it appears in `--help`.

**Fix:**

1. Get mGBA 0.11+ from the [development downloads](https://mgba.io/downloads.html#development-downloads) (Ubuntu AppImage or build from source).
2. Or build from source. See the mGBA repo for build instructions.
3. Verify: run `mgba-qt --version` — you should see 0.11 or higher.

See [Getting Started](getting-started.md) Option B prerequisites for more detail.

---

## mGBA Python Bindings Not Found (pygba)

**Symptom:** `python -m pygba` fails with `ModuleNotFoundError: No module named 'mgba'`.

**Cause:** The standard mGBA package does not include Python bindings. You must build mGBA from source with `-DBUILD_PYTHON=ON`.

**Fix:**

1. Run the setup helper: `bash pygba/setup_mgba.sh`
2. Or build manually:
   ```bash
   git clone https://github.com/mgba-emu/mgba.git /tmp/mgba-build
   cd /tmp/mgba-build && mkdir build && cd build
   cmake .. -DBUILD_PYTHON=ON
   make -j$(nproc)
   sudo make install && sudo ldconfig
   ```
3. Verify: `python3 -c "import mgba.core"` should succeed.

See [Getting Started](getting-started.md) Option A for full instructions.

---

## Ollama Not Installed (Both)

**Symptom:** mgba-lua's `./startup.sh` exits with "ollama not found in PATH". pygba fails to connect to LLM.

**Cause:** The default config uses Ollama. The mgba-lua script checks for `ollama` before launch.

**Fix:**

1. Install Ollama: `curl -fsSL https://ollama.com/install.sh | sh`
2. Pull a model: `ollama pull qwen2.5:7b`
3. Start the server: `ollama serve`

To use a different LLM backend, edit the component's `config.json` and set `backend` and `base_url` accordingly. See [Getting Started](getting-started.md) for backend options.

---

## "Waiting for state.json from mGBA..." (mgba-lua)

**Symptom:** The bridge prints "Waiting for state.json from mGBA..." and never advances.

**Cause:** The Lua script and bridge use different paths for the `data/` folder. They must share the same location.

**Fix:**

1. Start **both** mGBA and the bridge from `mgba-lua/`:
   ```bash
   cd mgba-lua
   # Terminal 1: mGBA
   mgba-qt --script lua/game_agent.lua ../gamefile/Pokemon_\ FireRed\ Version.zip
   # Terminal 2: bridge (after mGBA is running)
   source .venv/bin/activate && python3 -m bridge
   ```

2. The bridge writes `lua/data_dir.txt` on startup with the absolute path to `data/`. The Lua script reads this so both use the same folder. If you start mGBA before the bridge, the Lua script falls back to relative `"data"` — which works only when mGBA's working directory is `mgba-lua/`.

3. Ensure the game has loaded (past the title screen). The Lua script only writes state when a game is active.

---

## LLM Not Reachable (Both)

**Symptom:** Bridge or agent shows "not reachable (will retry)" or times out on requests.

**Cause:** The LLM backend is not running, wrong port, or wrong URL.

**Fix:**

1. **Check the backend is running:** Ollama needs `ollama serve`. LM Studio must have the local server started. llama.cpp/llamafile must be serving.

2. **Check the component's `config.json`** `base_url`:
   - Ollama (default): `http://localhost:11434`
   - LM Studio: `http://localhost:1234`
   - llama.cpp / llamafile: `http://localhost:8080` (or your configured port)

3. **Ollama native API:** If using `"backend": "ollama"`, set `"model"` (e.g. `"qwen2.5:7b"`). The native Ollama API requires a model name.

4. **Firewall:** Ensure nothing is blocking localhost connections to the LLM port.

---

## mGBA Script Not Loading (mgba-lua)

**Symptom:** No "LLM Plays Pokemon game agent loaded" message. Game runs but bridge never gets state.

**Cause:** The Lua script was not loaded into mGBA.

**Fix:**

1. **mGBA 0.11+:** Use `--script` when launching:
   ```bash
   cd mgba-lua
   mgba-qt --script lua/game_agent.lua ../gamefile/Pokemon_\ FireRed\ Version.zip
   ```

2. **Linux known limitation:** The published mGBA release (0.10.5) on Linux shows `--script` in `--help` but it is **disabled**. Use mGBA 0.11+ from the [development downloads](https://mgba.io/downloads.html#development-downloads).

3. **mGBA 0.10:** Load manually: **Tools > Scripting > File > Load Script** → select `lua/game_agent.lua`.

4. **Check version:** Run `mgba-qt --version`. If you see 0.10.x from a Linux package, use development builds or build from source for 0.11+.

5. **Working directory:** mGBA must be started from `mgba-lua/` so `lua/game_agent.lua` resolves correctly.

---

## Wrong ROM or Game Version (Both)

**Symptom:** Garbage data, crashes, or nonsensical state.

**Cause:** Both components target **Pokemon FireRed US v1.0** (game code BPRE). Other ROMs (Ruby, Sapphire, Emerald, non-US) use different memory layouts.

**Fix:** Use a FireRed or LeafGreen US v1.0 ROM (game code BPRE/BPGE) in `gamefile/`. See [Getting Started](getting-started.md) for notes on obtaining a legally owned ROM backup.

---

## Empty or Malformed LLM Response (Both)

**Symptom:** Bridge/agent shows "(empty response, using safe default)" or fails to parse JSON.

**Cause:** The model returned text that isn't valid JSON, or returned nothing.

**Fix:**

1. **Temperature:** Lower `temperature` in config (e.g. 0.2) for more consistent structured output.

2. **Model capability:** Use a model with strong instruction-following (Qwen 2.5, Llama 3.1, Mistral). Small models may struggle with strict JSON.

3. **max_tokens:** Ensure `max_tokens` is at least 200–300 (mgba-lua) or 400–512 (pygba, which requests multi-action plans).

---

## Venv or Python Not Found (mgba-lua)

**Symptom:** `python3 -m bridge` fails with module or venv errors.

**Fix:**

1. Use `./startup.sh` from `mgba-lua/` — it creates `.venv` and installs dependencies automatically.
2. If running the bridge manually, activate the project venv:
   ```bash
   cd mgba-lua
   source .venv/bin/activate
   python3 -m bridge
   ```
3. Or set `LPP_VENV` to an existing venv path; see [Reference](reference.md).

---

## pygba Dependencies Missing (pygba)

**Symptom:** `python -m pygba` fails with `ModuleNotFoundError` for `requests` or similar.

**Fix:**

```bash
cd pygba
pip install -r requirements.txt
```

Or create a venv first:

```bash
cd pygba
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---
*Last updated: 2026-02-21*
