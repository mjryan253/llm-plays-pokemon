# Getting Started

A step-by-step tutorial for first-time setup and running Lateral Red.

## Prerequisites

**OS:** Ubuntu / ZorinOS (or any Linux). Python 3.10+.

**mGBA** (v0.10+; 0.11+ required for `--script` auto-load):

```bash
sudo apt install mgba-qt
```

**Linux limitation:** The published release (0.10.5) on Linux has `--script` present in the help but **disabled**. For `--script` to work, you need mGBA 0.11+ from the [development downloads](https://mgba.io/downloads.html#development-downloads) (Ubuntu AppImage, or build from source). The current release (0.10.5) supports manual script loading only: **Tools > Scripting > File > Load Script**.

**Python dependencies:** Use a venv with dependencies installed (e.g. `~/GitHub/venv1`):

```bash
cd ~/GitHub/llm-plays-pokemon
source ~/GitHub/venv1/bin/activate
pip install -r requirements.txt
```

**A local LLM backend** (pick one):

| Backend | Install | Default Port |
|---------|---------|-------------|
| **LM Studio** | Download from [lmstudio.ai](https://lmstudio.ai) | 1234 |
| **Ollama** | `curl -fsSL https://ollama.com/install.sh \| sh` | 11434 |
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

**Pokemon FireRed ROM** (US v1.0, game code BPRE) — included in `gamefile/Pokemon_ FireRed Version.zip`. mGBA loads ROMs directly from ZIP archives.

---

## Step-by-Step Setup

### 1. Install Prerequisites

```bash
# Install mGBA
sudo apt install mgba-qt

# Activate venv (must have requirements installed: pip install -r requirements.txt)
cd ~/GitHub/llm-plays-pokemon  # or your project path
source ~/GitHub/venv1/bin/activate
```

On Linux, the published build (0.10.5) does not support `--script` — use [development downloads](https://mgba.io/downloads.html#development-downloads) for mGBA 0.11+ if you want auto-load.

### 2. Start Your LLM Backend

**Option A: LM Studio** (recommended)

- Download and install from [lmstudio.ai](https://lmstudio.ai)
- Load a model (e.g. Qwen 2.5 7B, Llama 3.1 8B)
- Start the local server (default port 1234)
- The `config.json` is already set for LM Studio at `localhost:1234`

**Option B: Ollama**

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:7b
ollama serve  # runs on port 11434
```

Then edit `config.json` to set `"base_url": "http://localhost:11434"` and `"model": "qwen2.5:7b"`.

### 3. Launch mGBA and Bridge

**Terminal 1: Start mGBA** (from project root)

mGBA 0.11+ supports `--script` to auto-load the Lua agent:

```bash
cd ~/GitHub/llm-plays-pokemon
mgba-qt --script lua/game_agent.lua gamefile/Pokemon_\ FireRed\ Version.zip
```

On mGBA 0.10, load the script manually: **Tools > Scripting > File > Load Script** → `lua/game_agent.lua`.

You should see: "Lateral Red (LR-1) game agent loaded" in the scripting console.

**Terminal 2: Start the Bridge** (from project root)

```bash
cd ~/GitHub/llm-plays-pokemon
source ~/GitHub/venv1/bin/activate
python3 -m bridge
```

The bridge will:

- Connect to your LLM backend
- Wait for `state.json` from mGBA
- Once it appears, start the AI playthrough

### 4. Use the Startup Script (Alternative)

The orchestrated script launches mGBA and the bridge together:

```bash
./startup.sh          # Launches mGBA with --script, then bridge (mGBA 0.11+)
./startup.sh --quiet  # Same, with minimal bridge output
./startup.sh --no-mgba  # Bridge only (mGBA already running)
./startup.sh --no-tail  # Skip spawning a separate terminal for log tail (e.g. SSH)
./startup.sh --no-log   # Skip logging to logs/ (no tee, no tail window)
```

All output is logged to `logs/LPP-YYYY-MM-DD-HH-MM-SS.txt`. When running under a graphical display, a separate terminal window opens with a live `tail -f` of the log. Set `LATERAL_RED_NO_TAIL=1` or use `--no-tail` to disable the tail window.

---

## First Run: What to Expect

The bridge prints verbose, color-coded output by default:

```
══════════════════════════════════════════════════════════════════════
  TURN 12  BATTLE  |  Route 1  (10, 14)
──────────────────────────────────────────────────────────────────────
  GAME STATE SENT TO LLM:
  │ MODE: Battle
  │
  │ YOUR ACTIVE POKEMON:
  │ Charmander Lv7 HP:24/26
  │   Move 1: Scratch (Normal) PP:33
  │   Move 2: Growl (Normal) PP:39
  │ ...
──────────────────────────────────────────────────────────────────────
  Responded in 1.9s
  RAW LLM RESPONSE:
  │ {"narrative": "A wild Rattata. Let's use Scratch.", "action": "fight_move_1"}
──────────────────────────────────────────────────────────────────────
  THINKING: A wild Rattata. Let's use Scratch.
  ACTION:   fight_move_1
```

Each turn shows:

- **Turn header** — turn number, game mode (color-coded), map name, coordinates
- **Game state** — the exact prompt the LLM received
- **Raw LLM response** — the model's full output before parsing
- **THINKING** — the model's narrative reasoning
- **ACTION** — the chosen action sent to the game

Run with `--quiet` to show only thinking and action lines:

```bash
source ~/GitHub/venv1/bin/activate && python3 -m bridge --quiet
```

---

## Next Steps

- [Architecture](architecture.md) — how the system works
- [Reference](reference.md) — config, game modes, project structure
- [Troubleshooting](troubleshooting.md) — common issues and fixes

---
*Last updated: 2026-02-20*
