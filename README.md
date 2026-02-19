# Lateral Red (LR-1)

An autonomous Pokemon FireRed agent powered by local LLMs. Uses mGBA's Lua scripting to read game memory directly -- no computer vision required -- and feeds structured game state to a small language model that decides what to do next.

> "The Nintendo way of adapting technology is not to look for the state-of-the-art... but to utilize mature technology that can be mass-produced cheaply." -- Gunpei Yokoi

## Executive Summary

**Lateral Red (LR-1)** is an autonomous Pokemon FireRed player that uses "withered technology" -- mature, stable tools like mGBA's Lua API and local LLMs -- to play the game without computer vision. A Lua script running inside mGBA reads game RAM every 30 frames, decrypts Pokemon data structures, and writes game state to JSON. A Python bridge polls this state, builds mode-aware prompts (overworld/dialog/battle/menu), and sends them to a local LLM (LM Studio, Ollama, llama.cpp, or llamafile). The LLM responds with JSON containing its reasoning and a chosen action, which the bridge translates into button sequences that mGBA executes.

**Key Features:**
- **No computer vision** -- reads game state directly from RAM addresses
- **Full party + moveset awareness** -- decrypts Gen III Pokemon data including all 4 moves and PP
- **Mode-aware AI** -- adapts action space based on game mode (overworld, dialog, battle, menu)
- **Multi-backend LLM support** -- works with any OpenAI-compatible API or Ollama
- **Verbose CLI output** -- watch the AI think in real-time with full prompts and responses
- **Small model friendly** -- designed for 2B-8B parameter models running on laptops

**Goal:** Beat the Elite Four with zero human intervention, narrated by the LLM's reasoning process.

## Quick Start

Complete setup and launch sequence:

### 1. Install Prerequisites

```bash
# Install mGBA
sudo apt install mgba-qt

# Activate venv (must have requirements installed: pip install -r requirements.txt)
cd ~/GitHub/llm-plays-pokemon  # or your project path
source ~/GitHub/venv1/bin/activate
```

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

### 3. Launch Everything

**Terminal 1: Start mGBA** (from project root)
```bash
cd ~/GitHub/llm-plays-pokemon
mgba-qt gamefile/Pokemon_\ FireRed\ Version.zip
```

**In mGBA:**
- Wait for the game to load
- Go to **Tools > Scripting**
- Click **File > Load Script**
- Select `lua/game_agent.lua`
- You should see: "Lateral Red (LR-1) game agent loaded" in the console

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

### 4. Watch It Play

The bridge prints verbose output showing:
- Game state sent to the LLM
- Raw LLM response
- AI's thinking/narrative
- Action chosen

Run with `--quiet` for minimal output:
```bash
source ~/GitHub/venv1/bin/activate && python3 -m bridge --quiet
```

**Option: Use the startup script** (orchestrates mGBA + bridge, verbose pre-flight):
```bash
./startup.sh          # Launches both; load lua/game_agent.lua in mGBA when prompted
./startup.sh --quiet  # Same, with minimal bridge output
./startup.sh --no-mgba  # Bridge only (mGBA already running)
```

**Troubleshooting:** If the bridge stays on "Waiting for state.json from mGBA..." — make sure both mGBA and the bridge are started from the project root directory. The bridge writes `lua/data_dir.txt` so the Lua script knows where to write `state.json`.

## How It Works

```
mGBA (Lua script)          Python Bridge           Local LLM
+-----------------+       +----------------+      +---------------+
| Read RAM every  | state | Poll state.json|      | Ollama        |
| 30 frames:      |------>| Enrich IDs with|----->| LM Studio     |
| - Player pos    | .json | species/move   |      | llama.cpp     |
| - Party + moves |       | names, build   |<-----| llamafile     |
| - Game mode     |       | mode-aware     | JSON | (any OpenAI   |
| - Dialog text   |  cmd  | prompt, parse  |      |  compatible)  |
| - Battle state  |<------| response       |      +---------------+
| Execute buttons | .json +----------------+
+-----------------+
```

The Lua script decrypts the Gen III Pokemon data structure (XOR cipher with personality value, 24 substructure permutations) to extract full party data including all four moves and PP for each Pokemon.

The Python bridge detects the current game mode (overworld, dialog, battle, menu) and presents only the relevant actions to the LLM. In battle, the LLM sees each move's name, type, and remaining PP alongside enemy info.

## CLI Output

The bridge prints a verbose, color-coded play-by-play to your terminal by default:

```
══════════════════════════════════════════════════════════════════════
  TURN 12  BATTLE  |  Route 1  (10, 14)
──────────────────────────────────────────────────────────────────────
  GAME STATE SENT TO LLM:
  │ MODE: Battle
  │
  │ YOUR ACTIVE POKEMON:
  │ Charmander Lv7 HP:24/26
  │   ATK:12 DEF:11 SPD:13 SpA:12 SpD:11
  │   Move 1: Scratch (Normal) PP:33
  │   Move 2: Growl (Normal) PP:39
  │   Move 3: Ember (Fire) PP:25
  │ ...
──────────────────────────────────────────────────────────────────────
  Responded in 1.9s
  RAW LLM RESPONSE:
  │ {"narrative": "A wild Rattata. Ember is super effective against
  │ nothing here, but Scratch has more PP. Let's use Scratch.",
  │ "action": "fight_move_1"}
──────────────────────────────────────────────────────────────────────
  THINKING: A wild Rattata. Ember is super effective against nothing
            here, but Scratch has more PP. Let's use Scratch.
  ACTION:   fight_move_1
```

Each turn shows:
- **Turn header** -- turn number, game mode (color-coded), map name, coordinates
- **Game state** -- the exact prompt the LLM received
- **Raw LLM response** -- the model's full output before parsing
- **THINKING** -- the model's narrative reasoning
- **ACTION** -- the chosen action sent to the game

Run with `--quiet` to show only the thinking and action lines:

```bash
source ~/GitHub/venv1/bin/activate && python3 -m bridge --quiet
```

## Prerequisites

**OS:** Ubuntu / ZorinOS (or any Linux). Python 3.10+.

**mGBA** (v0.10+):
```bash
sudo apt install mgba-qt
```

**Python dependencies:** Use a venv with dependencies installed (e.g. `~/GitHub/venv1`). Activate with `source ~/GitHub/venv1/bin/activate` before running the bridge.

**A local LLM backend** (pick one):

| Backend | Install | Default Port |
|---------|---------|-------------|
| **LM Studio** | Download from [lmstudio.ai](https://lmstudio.ai) | 1234 |
| **Ollama** | `curl -fsSL https://ollama.com/install.sh \| sh` | 11434 |
| **llama.cpp** | Build from [source](https://github.com/ggerganov/llama.cpp) | 8080 |
| **llamafile** | Download from [HuggingFace](https://huggingface.co/models?sort=trending&search=llamafile) | 8080 |

**Recommended small models** (for laptops with 8-16GB RAM):

| Model | Size | Notes |
|-------|------|-------|
| Qwen 2.5 7B Q4_K_M | ~4.4 GB | Strong instruction following, great structured output |
| Llama 3.1 8B Q4_K_M | ~4.9 GB | Well-rounded, widely available |
| Mistral 7B Q4_K_M | ~4.4 GB | Fast inference, good reasoning |
| Phi-3 Mini 3.8B Q4_K_M | ~2.4 GB | Fits 8GB RAM easily |
| Gemma 2 2B | ~1.6 GB | Minimal footprint for constrained hardware |

**Pokemon FireRed ROM** (US v1.0, game code BPRE) -- included in `gamefile/Pokemon_ FireRed Version.zip`. mGBA can load ROMs directly from ZIP archives.

## Configuration

All settings live in `config.json`:

```json
{
  "llm": {
    "backend": "openai-compat",
    "base_url": "http://localhost:1234",
    "temperature": 0.3,
    "max_tokens": 300,
    "api_key": null,
    "timeout_seconds": 30
  },
  "data_dir": "data",
  "state_poll_interval_seconds": 0.5,
  "history_length": 10,
  "lua": {
    "frame_poll_interval": 30
  }
}
```

| Field | Description |
|-------|-------------|
| **backend** | `"openai-compat"` works with LM Studio, Ollama (via `/v1/`), llama.cpp, llamafile. Set to `"ollama"` for the native Ollama `/api/chat` endpoint. |
| **base_url** | Host and port of the LLM server. No path -- the client appends it. |
| **model** | Optional. Omit when the server serves one model (LM Studio, llamafile). Required for Ollama native API and multi-model servers. |
| **api_key** | `null` for local backends. Set for cloud APIs. |
| **temperature** | Lower (0.2-0.4) = more consistent play. Higher = more creative but erratic. |
| **max_tokens** | Cap on LLM response length. 300 is enough for the JSON output. |
| **timeout_seconds** | How long to wait for an LLM response before retrying. |
| **history_length** | How many past turns to keep in the LLM's context window. |

## Project Structure

```
llm-plays-pokemon/
  config.json               # LLM backend + timing configuration
  startup.sh                # Orchestrated launch (mGBA + bridge)
  requirements.txt          # Python dependencies (requests)
  AGENTS.md                 # Changelog of all accepted changes
  gamefile/
    Pokemon_ FireRed Version.zip  # ROM file (mGBA loads directly from ZIP)
  lua/
    game_agent.lua          # mGBA Lua script (RAM reader, decrypter, command executor)
  bridge/
    __init__.py
    main.py                 # Main loop, CLI output, action-to-button translator
    llm_client.py           # Universal LLM client (OpenAI-compat / Ollama native)
    prompt.py               # Mode-aware prompt builder + response parser
    pokemon_data.py         # Species/move/map name lookup tables (Gen III)
  data/
    .gitkeep                # Runtime exchange dir (state.json, command.json)
```

## Game Modes

The agent detects four game modes and adapts its action space:

| Mode | Detection | Available Actions |
|------|-----------|-------------------|
| **Overworld** | Default state | move_up/down/left/right, interact, open_menu, wait |
| **Dialog** | Text buffer active | continue, choose_yes, choose_no |
| **Battle** | Battle flags set | fight_move_1-4, switch_2-6, use_item, run |
| **Menu** | Movement locked | menu_pokemon, menu_bag, menu_save, menu_close |

In battle mode, moves with 0 PP are excluded from the action list, and only party members with HP > 0 are offered as switch targets.

## Architecture Notes

- **No computer vision** -- all game state is read from RAM addresses documented in the FireRed RAM map.
- **Gen III encryption** is handled in Lua: the 48-byte Pokemon data section is XOR-decrypted using `personality_value XOR ot_id`, with substructure order determined by `personality_value % 24`.
- **File-based IPC** between mGBA and Python via `data/state.json` and `data/command.json`. Atomic writes (write to `.tmp`, then rename) prevent partial reads.
- **Anti-loop detection** warns the LLM when it has been at the same position for 5+ turns or repeating the same action 4+ times.
- **Model-agnostic** -- the `model` field is optional in config. LM Studio, llamafile, and single-model servers work without it. The bridge talks to whatever the server is running.
