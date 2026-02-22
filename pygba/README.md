# PyGBA -- Pure Python Pokemon FireRed Agent

Pure Python agent that drives Pokemon FireRed through mGBA's Python bindings.
No file-based IPC, no Lua -- direct memory access and button control from a
single Python process.

## How It Differs from mgba-lua/

| Feature            | mgba-lua (legacy)         | pygba                          |
|--------------------|---------------------------|--------------------------------|
| Architecture       | Lua script + Python bridge via file IPC | Single Python process  |
| Memory access      | Lua `emu:read*` -> JSON file -> Python  | Python `mgba.core` direct |
| LLM interaction    | One action per turn       | Multi-action plan per turn     |
| Navigation         | None                      | BFS pathfinding (70-node map)  |
| Planning           | Reactive only             | Hierarchical (strategic/tactical/reactive) |
| LLM output         | Non-streaming             | Streaming with live display    |
| Display            | mGBA GUI window           | Headless (terminal display)    |

## Prerequisites

- **Python 3.10+**
- **mGBA built with Python bindings** (`-DBUILD_PYTHON=ON`)
- **Ollama** (or any OpenAI-compatible LLM backend) running locally

### Building mGBA with Python Bindings

The standard mGBA package does **not** include Python bindings. You must build
from source:

```bash
bash pygba/setup_mgba.sh
```

This clones the mGBA repo, installs build dependencies, and compiles with
`-DBUILD_PYTHON=ON`. Requires `sudo` for system dependencies and installation.

If `setup_mgba.sh` doesn't work for your system, build manually:

```bash
git clone https://github.com/mgba-emu/mgba.git /tmp/mgba-build
cd /tmp/mgba-build && mkdir build && cd build
cmake .. -DBUILD_PYTHON=ON
make -j$(nproc)
sudo make install && sudo ldconfig
python3 -c "import mgba.core"  # verify
```

### LLM Backend

Start Ollama (default backend):

```bash
ollama serve
ollama pull qwen2.5:7b
```

## Setup

```bash
cd pygba
pip install -r requirements.txt
```

Place your ROM in `../gamefile/` (see the root README for ROM guidance).

## Usage

### Recommended: Startup Script

```bash
cd pygba
./startup.sh
```

`startup.sh` performs preflight checks and then launches the agent:

- Creates/uses `pygba/.venv` (or `LPP_VENV`) and installs requirements
- Validates `pygba/config.json` and `rom_path`
- Verifies mGBA bindings (`import mgba.core`)
- Checks Ollama binary when `llm.backend` is `"ollama"`
- Logs output to `../logs/LPP-YYYY-MM-DD-HH-MM-SS.txt` (unless `--no-log`)

Flags:

```bash
./startup.sh --no-tail
./startup.sh --no-log
./startup.sh --quiet
```

### Manual

From the repository root:

```bash
cd pygba
PYTHONPATH=.. python -m pygba
```

The agent runs headless -- all output goes to the terminal:

```
═════════════════════════════════════════════════════════════════
  TURN 42  OVERWORLD  |  Pewter City  (12, 8)
  Badges: [X][X][ ][ ][ ][ ][ ][ ]   Money: $3200
  Goal: Navigate to Cerulean City via Mt. Moon
─────────────────────────────────────────────────────────────────
  THINKING:
  │ I need to head east toward Route 3. My team is strong
  │ enough after beating Brock. Let me keep moving...
─────────────────────────────────────────────────────────────────
  PLAN: move_right, move_right, move_right, move_up (4 actions)
  EXECUTING: move_right [1/4]
═════════════════════════════════════════════════════════════════
```

The "THINKING" section streams live as LLM tokens arrive.

## Config Reference

Edit `pygba/config.json`:

```json
{
  "rom_path": "../gamefile/Pokemon FireRed.gba",
  "save_path": null,
  "log_dir": "../logs",
  "llm": {
    "backend": "ollama",
    "base_url": "http://localhost:11434",
    "model": "qwen2.5:7b",
    "temperature": 0.3,
    "max_tokens": 512,
    "timeout_seconds": 60
  },
  "planner": {
    "strategic_interval": 50,
    "max_plan_length": 20,
    "battle_plan_length": 3
  }
}
```

| Key                          | Description                                    | Default              |
|------------------------------|------------------------------------------------|----------------------|
| `rom_path`                   | Path to the GBA ROM file                       | `../gamefile/...`    |
| `save_path`                  | Path to a `.sav` file (null = fresh start)     | `null`               |
| `log_dir`                    | Directory for log output                       | `../logs`            |
| `llm.backend`                | `"ollama"` or `"openai-compat"`                | `"ollama"`           |
| `llm.base_url`               | LLM server URL                                 | `http://localhost:11434` |
| `llm.model`                  | Model name                                     | `"qwen2.5:7b"`      |
| `llm.temperature`            | Sampling temperature                           | `0.3`                |
| `llm.max_tokens`             | Max response tokens                            | `512`                |
| `llm.timeout_seconds`        | Request timeout                                | `60`                 |
| `planner.strategic_interval` | Turns between strategic re-evaluation           | `50`                 |
| `planner.max_plan_length`    | Max actions per overworld plan                  | `20`                 |
| `planner.battle_plan_length` | Max actions per battle plan                     | `3`                  |

## Architecture

```
__main__.py  ->  Agent.run()
                   │
                   ├── Emulator (mgba.core wrapper)
                   │     └── read_u8/u16/u32, press_key, tick
                   │
                   ├── GameState (RAM reader)
                   │     └── collect_state, game_progress, read_badges
                   │
                   ├── Planner (hierarchical)
                   │     ├── Strategic: LLM sets high-level goal
                   │     ├── Tactical: LLM creates multi-action plan
                   │     └── Reactive: interrupts on mode change
                   │
                   ├── Navigator (BFS pathfinding)
                   │     └── 70-node FireRed map graph
                   │
                   ├── StreamingLLMClient
                   │     └── Ollama / OpenAI-compat with on_token callback
                   │
                   └── Prompt (multi-action builder)
                         └── progress context, nav hints, compressed party
```

*Last updated: 2026-02-21*
