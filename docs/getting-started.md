# Getting Started

A step-by-step tutorial for first-time setup and running LLM Plays Pokemon. The project has two components — choose one:

| Component | Best for | Requires |
|-----------|----------|----------|
| **pygba** (recommended) | Headless agent, multi-action plans, streaming display | mGBA built with Python bindings |
| **mgba-lua** (legacy) | Visual mGBA window, simpler setup | mGBA 0.11+ binary |

## Shared Prerequisites

**OS:** Ubuntu / ZorinOS (or any Linux). Python 3.10+.

**A local LLM backend** (pick one):

| Backend | Install | Default Port |
|---------|---------|-------------|
| **Ollama** (recommended) | `curl -fsSL https://ollama.com/install.sh \| sh` | 11434 |
| **LM Studio** | Download from [lmstudio.ai](https://lmstudio.ai) | 1234 |
| **llama.cpp** | Build from [source](https://github.com/ggerganov/llama.cpp) | 8080 |
| **llamafile** | Download from [HuggingFace](https://huggingface.co/models?sort=trending&search=llamafile) | 8080 |

**Recommended small models** (for laptops with 8–16 GB RAM):

| Model | Size | Notes |
|-------|------|-------|
| Qwen 2.5 7B Q4_K_M | ~4.4 GB | Strong instruction following, great structured output |
| Llama 3.1 8B Q4_K_M | ~4.9 GB | Well-rounded, widely available |
| Mistral 7B Q4_K_M | ~4.4 GB | Fast inference, good reasoning |
| Phi-3 Mini 3.8B Q4_K_M | ~2.4 GB | Fits 8 GB RAM easily |
| Gemma 2 2B | ~1.6 GB | Minimal footprint for constrained hardware |

**Pokemon ROM** — Place your legally owned FireRed or LeafGreen ROM backup in `gamefile/` (e.g. `gamefile/Pokemon_ FireRed Version.zip`). mGBA loads ROMs directly from ZIP archives. If you need a backup and cannot find one, a [DuckDuckGo search for "pokemon gba rom"](https://duckduckgo.com/?q=pokemon+gba+rom) will lead to sites where you can download a ROM backup — **only** of a game you legally own.

---

## Option A: pygba (Recommended)

The pure-Python agent runs headless with streaming terminal output, multi-action planning, and BFS pathfinding.

### 1. Build mGBA with Python Bindings

The standard mGBA package does **not** include Python bindings. Build from source:

```bash
bash pygba/setup_mgba.sh
```

Or build manually:

```bash
git clone https://github.com/mgba-emu/mgba.git /tmp/mgba-build
cd /tmp/mgba-build && mkdir build && cd build
cmake .. -DBUILD_PYTHON=ON
make -j$(nproc)
sudo make install && sudo ldconfig
python3 -c "import mgba.core"  # verify
```

### 2. Install Dependencies

```bash
cd pygba
pip install -r requirements.txt
```

### 3. Start the LLM Backend

```bash
ollama pull qwen2.5:7b
ollama serve  # runs on port 11434
```

### 4. Run the Agent

From the repository root:

```bash
python -m pygba
```

The agent runs headless — all output goes to the terminal with a streaming display:

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

The "THINKING" section streams live as LLM tokens arrive. See [pygba/README.md](../pygba/README.md) for config details.

---

## Option B: mgba-lua (Legacy)

Uses mGBA's Lua scripting and a Python bridge communicating via JSON files.

### 1. Install mGBA 0.11+

```bash
sudo apt install mgba-qt
```

**Linux limitation:** The published release (0.10.5) on Linux has `--script` **disabled**. For `--script` to work, use mGBA 0.11+ from the [development downloads](https://mgba.io/downloads.html#development-downloads) (Ubuntu AppImage, or build from source). See [Troubleshooting](troubleshooting.md) if the script reports "mGBA version too old".

### 2. Run the Startup Script

```bash
cd mgba-lua
./startup.sh
```

The script will:

- Check mGBA is 0.11+ (exits with doc pointers if not)
- Create `.venv` and install Python dependencies if needed
- Check Ollama is installed (exits with doc pointers if not)
- Prompt you to start the Ollama server (press Enter when ready, or wait 60 seconds to auto-continue)
- Launch mGBA with `--script` and the bridge

```bash
./startup.sh          # Full launch (mGBA + bridge)
./startup.sh --quiet  # Same, minimal bridge output
./startup.sh --no-mgba  # Bridge only (mGBA already running)
./startup.sh --no-tail  # Skip log tail window (e.g. SSH)
./startup.sh --no-log   # Skip logging
```

All output is logged to `logs/LPP-YYYY-MM-DD-HH-MM-SS.txt`. With a graphical display, a separate terminal opens with a live `tail -f`. Set `LPP_NO_TAIL=1` or use `--no-tail` to disable.

### 3. (Optional) Use a Different LLM Backend

**Ollama** (default) — Start the server before or when prompted:

```bash
ollama serve  # runs on port 11434
```

The `config.json` is set for Ollama at `localhost:11434` with `qwen2.5:7b`.

**LM Studio** — Download from [lmstudio.ai](https://lmstudio.ai), load a model, start the server (port 1234), then edit `mgba-lua/config.json`: `"base_url": "http://localhost:1234"`, `"backend": "openai-compat"`.

### 4. (Optional) Manual Launch

If you prefer to run mGBA and the bridge in separate terminals:

**Terminal 1: Start mGBA** (from `mgba-lua/`)

```bash
cd mgba-lua
mgba-qt --script lua/game_agent.lua ../gamefile/Pokemon_\ FireRed\ Version.zip
```

On mGBA 0.10, load the script manually: **Tools > Scripting > File > Load Script** → `lua/game_agent.lua`.

**Terminal 2: Start the Bridge** (from `mgba-lua/`)

```bash
cd mgba-lua
source .venv/bin/activate
python3 -m bridge
```

The bridge will connect to your LLM backend, wait for `state.json` from mGBA, and start the AI playthrough once it appears.

---

## First Run: What to Expect

### pygba

The streaming terminal display updates each turn with badges, money, map, goal, the LLM's live thinking, and a multi-action plan. The agent runs headless — no mGBA window.

### mgba-lua

The bridge prints verbose, color-coded output by default:

```
══════════════════════════════════════════════════════════════════════
  TURN 12  BATTLE  |  Route 1  (10, 14)
──────────────────────────────────────────────────────────────────────
  GAME STATE SENT TO LLM:
  │ MODE: Battle
  │ YOUR ACTIVE POKEMON:
  │ Charmander Lv7 HP:24/26
  │   Move 1: Scratch (Normal) PP:33
  │   Move 2: Growl (Normal) PP:39
──────────────────────────────────────────────────────────────────────
  Responded in 1.9s
  RAW LLM RESPONSE:
  │ {"narrative": "A wild Rattata. Let's use Scratch.", "action": "fight_move_1"}
──────────────────────────────────────────────────────────────────────
  THINKING: A wild Rattata. Let's use Scratch.
  ACTION:   fight_move_1
```

Run with `--quiet` to show only thinking and action lines:

```bash
cd mgba-lua
source .venv/bin/activate && python3 -m bridge --quiet
```

---

## Next Steps

- [Architecture](architecture.md) — how both systems work
- [Reference](reference.md) — config schemas, game modes, project structure
- [Troubleshooting](troubleshooting.md) — common issues and fixes

---
*Last updated: 2026-02-21*
