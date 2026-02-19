# AGENTS.md -- Lateral Red (LR-1) Changelog

## 2026-02-19

- **README venv**: Updated Quick Start and Prerequisites to use `~/GitHub/venv1` instead of raw pip install; bridge commands now source the venv before running. (README.md)
- **startup.sh**: Added orchestrated launch script with verbose pre-flight checks; starts mGBA and bridge, supports `--no-mgba`, `--quiet`, and `LATERAL_RED_VENV` env var. Cleans up mGBA on Ctrl+C. (startup.sh, README.md)
- **.gitignore**: Added Python exclusions (__pycache__/, *.pyc, .venv, .egg-info, etc.). (.gitignore)

## 2026-02-18

- **Initial build**: Scaffolded full project -- Lua game agent with Gen III substructure decryption, Python bridge with mode-aware prompting, multi-backend LLM client, Pokemon data tables (386 species, 354 moves, map names) (`lua/game_agent.lua`, `bridge/`, `config.json`, `requirements.txt`)
- **Multi-backend support**: LLM client supports Ollama, LM Studio, llama.cpp, llamafile, and any OpenAI-compatible API via config (`bridge/llm_client.py`)
- **Model field optional**: `model` can be omitted from `config.json` when the server (e.g. LM Studio) picks the loaded model automatically (`bridge/llm_client.py`, `config.json`)
- **Verbose CLI output**: Default output shows full game state sent to LLM, raw response, thinking/narrative, and chosen action per turn with color-coded mode headers; `--quiet` flag available for minimal output (`bridge/main.py`)
- **Package entrypoint**: Added `bridge/__main__.py` so `python3 -m bridge` works as the launch command (`bridge/__main__.py`)
- **Bridge–mGBA path sync**: Bridge writes absolute data path to `lua/data_dir.txt` on startup; Lua script reads it so both use the same `data/` folder regardless of mGBA's CWD. README updated: start mGBA from project root and added troubleshooting for "Waiting for state.json". (bridge/main.py, lua/game_agent.lua, README.md, .gitignore)
- **ROM path and quickstart**: Updated README Quick Start with complete command sequence using `gamefile/Pokemon_ FireRed Version.zip`. Added step-by-step setup including LLM backend launch, mGBA launch command with proper path escaping, and bridge startup. Project structure updated to show gamefile directory. (README.md)
- **README reorganization**: Added Executive Summary section at top with high-level overview and key features. Moved Quick Start to immediately follow Executive Summary for better discoverability. Removed duplicate troubleshooting text. (README.md)
