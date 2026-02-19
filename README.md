# Lateral Red (LR-1)

An autonomous Pokemon FireRed agent powered by local LLMs. Uses mGBA's Lua scripting to read game memory directly -- no computer vision required -- and feeds structured game state to a small language model that decides what to do next.

> "The Nintendo way of adapting technology is not to look for the state-of-the-art... but to utilize mature technology that can be mass-produced cheaply." -- Gunpei Yokoi

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

## Prerequisites

**OS:** Ubuntu / ZorinOS (or any Linux). Python 3.10+.

**mGBA** (v0.10+):
```bash
sudo apt install mgba-qt
```

**Python dependencies:**
```bash
pip install -r requirements.txt
```

**A local LLM backend** (pick one):

| Backend | Install | Default Port |
|---------|---------|-------------|
| **Ollama** | `curl -fsSL https://ollama.com/install.sh \| sh` | 11434 |
| **LM Studio** | Download from [lmstudio.ai](https://lmstudio.ai) | 1234 |
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

**Pokemon FireRed ROM** (US v1.0, game code BPRE) -- user-supplied, not included in this repo.

## Quick Start

1. **Pull a model** (Ollama example):
   ```bash
   ollama pull qwen2.5:7b
   ollama serve  # if not already running
   ```

2. **Edit `config.json`** if using a different backend:
   ```json
   {
     "llm": {
       "backend": "openai-compat",
       "base_url": "http://localhost:11434",
       "model": "qwen2.5:7b"
     }
   }
   ```
   For LM Studio, set `base_url` to `http://localhost:1234`.
   For llama.cpp/llamafile, set `base_url` to `http://localhost:8080`.

3. **Open mGBA**, load the FireRed ROM.

4. **Load the Lua script**: In mGBA, go to **Tools > Scripting**, then **File > Load Script** and select `lua/game_agent.lua`.

5. **Start the bridge**:
   ```bash
   python3 -m bridge.main
   ```

6. Watch the AI play and narrate in the terminal.

## Configuration

All settings live in `config.json`:

```json
{
  "llm": {
    "backend": "openai-compat",
    "base_url": "http://localhost:11434",
    "model": "qwen2.5:7b",
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

- **backend**: `"openai-compat"` works with Ollama (via its `/v1/` endpoint), LM Studio, llama.cpp, and llamafile. Set to `"ollama"` only if you want the native Ollama `/api/chat` endpoint.
- **api_key**: Leave `null` for local backends. Set for cloud APIs.
- **temperature**: Lower values (0.2-0.4) give more consistent play. Higher values are more creative but erratic.

## Project Structure

```
llm-plays-pokemon/
  config.json               # LLM + timing configuration
  requirements.txt          # Python dependencies
  lua/
    game_agent.lua          # mGBA Lua script (RAM reader, command executor)
  bridge/
    __init__.py
    main.py                 # Main loop, action-to-button translator
    llm_client.py           # Universal LLM client
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
