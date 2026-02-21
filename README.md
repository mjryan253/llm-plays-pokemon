# Lateral Red (LR-1)

An autonomous Pokemon FireRed agent powered by local LLMs. Uses mGBA's Lua scripting to read game memory directly — no computer vision required — and feeds structured game state to a small language model that decides what to do next.

> "The Nintendo way of adapting technology is not to look for the state-of-the-art... but to utilize mature technology that can be mass-produced cheaply." — Gunpei Yokoi

## Summary

**Lateral Red (LR-1)** uses "withered technology" — mGBA's Lua API and local LLMs — to play Pokemon FireRed without computer vision. A Lua script reads RAM every 30 frames and writes game state to JSON. A Python bridge polls this, builds mode-aware prompts, and sends them to an LLM (Ollama, LM Studio, llama.cpp, llamafile). The LLM responds with reasoning and an action; the bridge translates that into button sequences for mGBA.

**Key features:**
- **No computer vision** — reads game state from RAM addresses
- **Full party + moveset awareness** — decrypts Gen III Pokemon data including all 4 moves and PP
- **Mode-aware AI** — adapts actions for overworld, dialog, battle, menu
- **Multi-backend LLM support** — works with any OpenAI-compatible API
- **Small model friendly** — designed for 2B–8B models on laptops

**Goal:** Beat the Elite Four with zero human intervention, narrated by the LLM.

## Quick Start

1. **Prerequisites:** mGBA 0.11+ (on Linux, use [development downloads](https://mgba.io/downloads.html#development-downloads) — packaged 0.10.5 has `--script` disabled), Python 3.10+, Ollama installed, ROM in `gamefile/`. The startup script creates a project `.venv` and installs deps automatically.
2. **Run:** `./startup.sh` — checks mGBA version, creates `.venv`, checks Ollama, prompts to start `ollama serve`, then launches mGBA + bridge (output logged to `logs/`). Use `--no-tail` or `--no-log` if needed.
3. **Alternate:** Launch [manually](docs/getting-started.md#4-optional-manual-launch) with separate mGBA and bridge terminals; see [docs/getting-started.md](docs/getting-started.md) for LLM backends.

**Troubleshooting:** Bridge stuck on "Waiting for state.json"? Start both mGBA and the bridge from the project root. See [docs/troubleshooting.md](docs/troubleshooting.md).

## Documentation

| Doc | Description |
|-----|-------------|
| [Getting Started](docs/getting-started.md) | Full setup tutorial, prerequisites, first run |
| [Architecture](docs/architecture.md) | System design, philosophy, data flow |
| [Reference](docs/reference.md) | Config, game modes, project structure |
| [Troubleshooting](docs/troubleshooting.md) | Common issues and fixes |

## Project Structure

```
llm-plays-pokemon/
  config.json          # LLM backend + timing
  startup.sh           # Orchestrated launch
  gamefile/            # Place your legally owned FireRed/LeafGreen ROM here (see docs)
  lua/game_agent.lua   # mGBA script (RAM reader, command executor)
  bridge/              # Python: main loop, LLM client, prompts
  data/                # state.json, command.json (runtime)
  docs/                # Documentation
```

See [docs/reference.md](docs/reference.md) for full structure and config details.

---
*Last updated: 2026-02-21*
