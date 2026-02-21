# mgba-lua — Lua + Python Bridge

The original LLM Plays Pokemon component. A Lua script inside mGBA reads game RAM every 30 frames and writes structured state to JSON. A Python bridge polls this file, builds mode-aware prompts, sends them to a local LLM, and writes button-sequence commands back for the Lua agent to execute.

## Architecture

```
mGBA  ←──Lua API──→  game_agent.lua
                        ↕  (state.json / command.json)
                      bridge/  ←──HTTP──→  Ollama / LM Studio / llama.cpp
```

- **lua/game_agent.lua** — mGBA script: reads RAM (player position, party, enemy, text, battle flags), decrypts Gen III substructures, writes `data/state.json`, reads `data/command.json`.
- **bridge/** — Python package: polls `state.json`, enriches it with species/move names, builds a prompt, calls the LLM, parses the response into a high-level action, translates it to GBA button bitmasks, writes `command.json`.

## Quick Start

From the repo root:

```bash
cd mgba-lua
./startup.sh
```

The startup script creates a `.venv`, installs deps, checks mGBA 0.11+ and Ollama, then launches mGBA with the Lua agent and the bridge.

### Manual Launch

Terminal 1 — mGBA:

```bash
cd mgba-lua
mgba-qt --script lua/game_agent.lua ../gamefile/YourROM.gba
```

Terminal 2 — Bridge:

```bash
cd mgba-lua
source .venv/bin/activate
python -m bridge
```

## Configuration

See `config.json` in this directory. Full reference: [docs/reference.md](../docs/reference.md).

## See Also

- [Getting Started](../docs/getting-started.md) — full setup tutorial
- [Architecture](../docs/architecture.md) — design and philosophy
- [Troubleshooting](../docs/troubleshooting.md) — common issues

---
*Last updated: 2026-02-21*
