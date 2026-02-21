# AGENTS.md -- Lateral Red (LR-1) Changelog

*Last updated: 2026-02-21*

## 2026-02-21

- **ROM documentation**: Clarified that `gamefile/` expects a user-supplied ROM. Noted that one can use any legally owned FireRed or LeafGreen ROM backup. Added DuckDuckGo search guidance for obtaining a backup, with explicit legal-use-only disclaimer. (README.md, docs/getting-started.md, docs/reference.md, docs/troubleshooting.md)
- **gamefile/ placeholder**: Added `Not-a-real-pokemon-ROM` so the directory exists when cloned. Updated .gitignore to `gamefile/*` with exception for the placeholder, so ROMs/saves stay untracked. (.gitignore, gamefile/Not-a-real-pokemon-ROM)

## 2026-02-20

- **mGBA Linux limitation**: Documented that published mGBA (0.10.5) on Linux has `--script` disabled; users need 0.11+ from [development downloads](https://mgba.io/downloads.html#development-downloads). (README.md, docs/getting-started.md, docs/troubleshooting.md)
- **Documentation last-updated dates**: Added "Last updated: 2026-02-20" footer to README.md, AGENTS.md, guide-doc.md, and all docs/*.md files.
- **startup.sh --no-log**: Added `--no-log` flag to skip logging (no tee, no tail window). Logging remains on by default. (startup.sh, README.md, docs/getting-started.md)
- **startup.sh logging and tail terminal**: All output is teed to `logs/LPP-YYYY-MM-DD-HH-MM-SS.txt`. Spawns a separate terminal with `tail -f` (gnome-terminal, xfce4-terminal, konsole, xterm). Added `--no-tail` flag and `LATERAL_RED_NO_TAIL` env var. `logs/` added to .gitignore. (startup.sh, .gitignore, README.md, docs/getting-started.md, docs/reference.md)
- **docs/ + Diátaxis restructure**: Reorganized documentation into `docs/` using the Diátaxis framework. Created `getting-started.md`, `architecture.md`, `reference.md`, `troubleshooting.md`, and `docs/README.md` index. Slimmed main README to ~70 lines with links to detailed docs. Superseded `guide-doc.md` with redirect to `docs/architecture.md`. Updated changelog-and-docs rule to include `docs/`. (docs/, README.md, guide-doc.md, .cursor/rules/changelog-and-docs.mdc)
- **mGBA 0.11 --script**: Integrated mGBA 0.11 `--script FILE` flag to auto-load the Lua game agent on launch. `startup.sh` now passes `--script lua/game_agent.lua`; manual step removed. README updated with `--script` usage and fallback for mGBA 0.10. (startup.sh, README.md)

## 2026-02-19

- **README venv**: Updated Quick Start and Prerequisites to use `~/GitHub/venv1` instead of raw pip install; bridge commands now source the venv before running. (README.md)
- **startup.sh**: Added orchestrated launch script with verbose pre-flight checks; starts mGBA and bridge, supports `--no-mgba`, `--quiet`, and `LATERAL_RED_VENV` env var. Cleans up mGBA on Ctrl+C. (startup.sh, README.md)
- **docs/MGBA_SCRIPTING_REQUEST.md**: Outreach document for mGBA dev team—describes Lateral Red use case, --script support in source vs. packaged 0.10.x, questions about availability and build, workaround for building from source. (docs/MGBA_SCRIPTING_REQUEST.md)
- **docs/MGBA_SUBMISSION_KIT.md**: Submission kit aligned with mGBA CONTRIBUTING.md—checklist, issue template, full copy-paste body for manual submission to mGBA GitHub. (docs/MGBA_SUBMISSION_KIT.md)
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
