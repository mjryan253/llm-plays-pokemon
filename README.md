# Lateral Red (LR-1)

An autonomous Pokemon FireRed agent powered by local LLMs. Uses mGBA's Lua scripting to read game memory directly — no computer vision required — and feeds structured game state to a small language model that decides what to do next.

> "The Nintendo way of adapting technology is not to look for the state-of-the-art... but to utilize mature technology that can be mass-produced cheaply." — Gunpei Yokoi

## Summary

**Lateral Red (LR-1)** uses "withered technology" — mGBA's Lua API and local LLMs — to play Pokemon FireRed without computer vision. A Lua script reads RAM every 30 frames and writes game state to JSON. A Python bridge polls this, builds mode-aware prompts, and sends them to an LLM (LM Studio, Ollama, llama.cpp, llamafile). The LLM responds with reasoning and an action; the bridge translates that into button sequences for mGBA.

**Key features:**
- **No computer vision** — reads game state from RAM addresses
- **Full party + moveset awareness** — decrypts Gen III Pokemon data including all 4 moves and PP
- **Mode-aware AI** — adapts actions for overworld, dialog, battle, menu
- **Multi-backend LLM support** — works with any OpenAI-compatible API
- **Small model friendly** — designed for 2B–8B models on laptops

**Goal:** Beat the Elite Four with zero human intervention, narrated by the LLM.

## Quick Start

1. **Prerequisites:** mGBA 0.11+ (on Linux, use [development downloads](https://mgba.io/downloads.html#development-downloads) — packaged 0.10.5 has `--script` disabled), Python 3.10+, venv with `pip install -r requirements.txt`
2. **LLM:** Start LM Studio (port 1234) or Ollama — see [docs/getting-started.md](docs/getting-started.md)
3. **mGBA:** `mgba-qt --script lua/game_agent.lua gamefile/Pokemon_\ FireRed\ Version.zip` (from project root)
4. **Bridge:** `source ~/GitHub/venv1/bin/activate && python3 -m bridge`

**Or use the startup script:** `./startup.sh` (launches mGBA + bridge together). Output is logged to `logs/LPP-YYYY-MM-DD-HH-MM-SS.txt` and, if a display is available, a separate terminal window opens with a live `tail -f` of the log. Use `--no-tail` to disable the tail window or `--no-log` to skip logging entirely (e.g. SSH).

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
  lua/game_agent.lua   # mGBA script (RAM reader, command executor)
  bridge/              # Python: main loop, LLM client, prompts
  data/                # state.json, command.json (runtime)
  docs/                # Documentation
```

See [docs/reference.md](docs/reference.md) for full structure and config details.

---
*Last updated: 2026-02-20*
