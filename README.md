# LLM Plays Pokemon

An autonomous Pokemon FireRed agent powered by local LLMs. Two approaches to the same goal: an LLM beating Pokemon FireRed with zero human intervention.

> "The Nintendo way of adapting technology is not to look for the state-of-the-art... but to utilize mature technology that can be mass-produced cheaply." — Gunpei Yokoi

## Components

| Component | Description | Architecture | Status |
|-----------|-------------|--------------|--------|
| [pygba/](pygba/) | Pure Python via mGBA bindings | Single process, direct RAM access, streaming LLM, hierarchical planner | New |
| [mgba-lua/](mgba-lua/) | Lua + Python bridge via file IPC | mGBA Lua script ↔ JSON files ↔ Python bridge | Stable |

Both components read game memory directly — no computer vision — and feed structured state to a local LLM that decides what to do next.

## Quick Start

**Prerequisites:** Python 3.10+, Ollama, ROM in `gamefile/`.

**Option A — pygba** (recommended):

Requires mGBA built with Python bindings (see [pygba/README.md](pygba/README.md) or run `bash pygba/setup_mgba.sh`).

```bash
cd pygba && ./startup.sh
```

The launcher performs preflight checks (venv/deps, `mgba.core`, config/ROM path, Ollama binary) and then starts `python -m pygba`.

**Option B — mgba-lua** (legacy):

Requires mGBA 0.11+ (on Linux, use [development downloads](https://mgba.io/downloads.html#development-downloads)).

```bash
cd mgba-lua && ./startup.sh
```

See [docs/getting-started.md](docs/getting-started.md) for full setup, LLM backend options, and ROM guidance.

## Shared Assets

- `gamefile/` — place your legally owned FireRed/LeafGreen ROM here
- `docs/` — full documentation (covers both components)
- `logs/` — output logs from either component

## Documentation

| Doc | Description |
|-----|-------------|
| [Getting Started](docs/getting-started.md) | Setup tutorial for both components |
| [Architecture](docs/architecture.md) | System design and philosophy |
| [Reference](docs/reference.md) | Config schemas, project structure, RAM addresses |
| [Troubleshooting](docs/troubleshooting.md) | Common issues and fixes |

## Project Structure

```
llm-plays-pokemon/
  AGENTS.md                # Changelog
  README.md                # This file
  gamefile/                 # ROM directory (user-supplied)
  logs/                    # Output logs
  docs/                    # Shared documentation (Diátaxis)
  pygba/                   # Pure Python agent (mGBA bindings)
    config.json            # ROM path, LLM, planner settings
    setup_mgba.sh          # Build mGBA with Python bindings
    agent.py               # Main loop + streaming terminal display
    emulator.py            # mgba.core wrapper
    game_state.py          # RAM reader + Gen III decryption
    planner.py             # Hierarchical goal stack
    navigator.py           # BFS pathfinding (70-node map graph)
    llm_client.py          # Streaming Ollama/OpenAI client
    prompt.py              # Multi-action prompt builder
  mgba-lua/                # Lua + Python bridge (file IPC)
    config.json            # LLM backend + timing
    startup.sh             # Orchestrated launch
    lua/game_agent.lua     # mGBA Lua agent (RAM reader)
    bridge/                # Python: main loop, LLM client, prompts
    data/                  # state.json, command.json (runtime)
```

See [docs/reference.md](docs/reference.md) for full details.

---
*Last updated: 2026-02-21*
