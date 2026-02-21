# Reference

Technical reference for configuration, game modes, project structure, and memory addresses. Covers both components.

---

## pygba Config (`pygba/config.json`)

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

### pygba Field Reference

| Field | Description | Default |
|-------|-------------|---------|
| **rom_path** | Path to the GBA ROM file | `../gamefile/...` |
| **save_path** | Path to a `.sav` file (`null` = fresh start) | `null` |
| **log_dir** | Directory for log output | `../logs` |
| **llm.backend** | `"ollama"` (native API) or `"openai-compat"` (SSE streaming) | `"ollama"` |
| **llm.base_url** | LLM server URL (no trailing path) | `http://localhost:11434` |
| **llm.model** | Model name (required for Ollama) | `"qwen2.5:7b"` |
| **llm.temperature** | Sampling temperature (lower = more consistent) | `0.3` |
| **llm.max_tokens** | Max response tokens | `512` |
| **llm.timeout_seconds** | Request timeout | `60` |
| **planner.strategic_interval** | Turns between strategic LLM re-evaluation | `50` |
| **planner.max_plan_length** | Max actions per overworld plan | `20` |
| **planner.battle_plan_length** | Max actions per battle plan | `3` |

---

## mgba-lua Config (`mgba-lua/config.json`)

```json
{
  "llm": {
    "backend": "ollama",
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

### mgba-lua Field Reference

| Field | Description |
|-------|-------------|
| **backend** | `"ollama"` (default) uses native Ollama `/api/chat`. `"openai-compat"` works with LM Studio, llama.cpp, llamafile. |
| **base_url** | Host and port of the LLM server. No path — the client appends it. |
| **model** | Required for Ollama. Optional for single-model servers (LM Studio, llamafile). |
| **api_key** | `null` for local backends. Set for cloud APIs. |
| **temperature** | Lower (0.2–0.4) = more consistent play. Higher = more creative but erratic. |
| **max_tokens** | Cap on LLM response length. 300 is enough for the JSON output. |
| **timeout_seconds** | How long to wait for an LLM response before retrying. |
| **data_dir** | Directory for `state.json` and `command.json`. Relative to `mgba-lua/`. |
| **state_poll_interval_seconds** | How often the bridge polls for new state. |
| **history_length** | How many past turns to keep in the LLM's context window. |
| **lua.frame_poll_interval** | How many frames between state writes (Lua side). |

---

## Environment Variables (mgba-lua/startup.sh)

| Variable | Description |
|----------|-------------|
| **LPP_VENV** | Override venv path. If set and the path exists, the script uses it instead of creating `mgba-lua/.venv`. |
| **LPP_NO_TAIL** | Set to `1` to disable spawning a separate terminal for log tail. Same as `--no-tail`. |
| **LPP_TAIL_TERM** | Terminal emulator for tail window (e.g. `gnome-terminal`, `xfce4-terminal`, `konsole`, `xterm`). Auto-detected if unset. |

LPP = LLM Plays Pokemon. By default the script creates `mgba-lua/.venv` if it does not exist and runs `pip install -r requirements.txt` inside it.

---

## Game Modes

Both components detect four game modes and adapt the action space:

| Mode | Detection | Available Actions |
|------|-----------|-------------------|
| **Overworld** | Default state | move_up, move_down, move_left, move_right, interact, open_menu, wait |
| **Dialog** | Text buffer active | continue, choose_yes, choose_no |
| **Battle** | Battle flags set | fight_move_1 through fight_move_4, switch_2 through switch_6, use_item, run |
| **Menu** | Movement locked | menu_pokemon, menu_bag, menu_save, menu_close |

In battle mode, moves with 0 PP are excluded from the action list, and only party members with HP > 0 are offered as switch targets.

pygba additionally supports multi-action plans: overworld/menu prompts request up to 10–20 actions, while battle/dialog prompts request 1–3.

---

## Project Structure

```
llm-plays-pokemon/
  AGENTS.md                    # Changelog
  README.md                    # Project overview, links to both components
  .gitignore                   # Updated for both component paths
  gamefile/                    # Shared ROM directory (user-supplied)
  logs/                        # Shared log output
  docs/                        # Shared documentation (Diátaxis)
    README.md                  # Docs index
    getting-started.md         # Setup tutorial (both components)
    architecture.md            # Design comparison and philosophy
    reference.md               # This file
    troubleshooting.md         # Issues for both components

  pygba/                       # Pure Python agent
    README.md                  # Component-specific setup + usage
    config.json                # ROM path, LLM, planner settings
    requirements.txt           # Python deps (requests)
    setup_mgba.sh              # Build mGBA with Python bindings
    __init__.py
    __main__.py                # Entry: python -m pygba
    agent.py                   # Main loop + streaming terminal display
    emulator.py                # mgba.core wrapper
    game_state.py              # RAM reading, party decryption, badge/progress
    llm_client.py              # Streaming Ollama/OpenAI client
    planner.py                 # Hierarchical goal stack + plan queue
    navigator.py               # FireRed map graph + BFS pathfinding
    prompt.py                  # Multi-action prompts + response parser
    actions.py                 # GBA key bitmasks + action->button sequences
    pokemon_data.py            # Species/move/item/map tables (Gen III)

  mgba-lua/                    # Lua + Python bridge (legacy)
    README.md                  # Component-specific quick start
    config.json                # LLM backend + timing
    requirements.txt           # Python deps (requests)
    startup.sh                 # Orchestrated launch (mGBA + bridge)
    bridge/                    # Python bridge
      __init__.py
      __main__.py              # Entry: python -m bridge
      main.py                  # Main loop, CLI output, action translator
      llm_client.py            # Universal LLM client
      prompt.py                # Mode-aware prompt builder + response parser
      pokemon_data.py          # Species/move/map name tables (Gen III)
    lua/
      game_agent.lua           # mGBA Lua script (RAM reader, decrypter, executor)
    data/
      .gitkeep                 # Runtime exchange dir (state.json, command.json)
```

---

## FireRed RAM Addresses (US v1.0 / BPRE)

Both components read these memory addresses. Values are in the game's native format and decoded by each component's reader.

| Symbol | Address | Description |
|--------|---------|-------------|
| SAVEBLOCK1_PTR | 0x03005008 | Pointer to SaveBlock1 |
| SAVEBLOCK2_PTR | 0x0300500C | Pointer to SaveBlock2 |
| MAP_BANK_FIXED | 0x02031DBC | Current map bank |
| MAP_NUMBER_FIXED | 0x02031DBD | Current map number |
| PLAYER_MOVING | 0x0203707B | Player movement state |
| MOVEMENT_LOCKED | 0x0203707E | Movement locked (menu/dialog) |
| TEXT_BUFFER | 0x02021D18 | Dialog text buffer (256 bytes) |
| BATTLE_FLAGS | 0x02022B4C | Battle state flags |
| PARTY_BASE | 0x02024284 | Party Pokemon data base |
| PARTY_SIZE | 100 | Bytes per party slot |
| PARTY_COUNT_MAX | 6 | Max party members |
| ENEMY_BASE | 0x0202402C | Enemy Pokemon data |

Player X/Y and other derived values are read via SaveBlock pointers.

pygba additionally reads:

| Symbol | Address / Offset | Description |
|--------|-----------------|-------------|
| Badges | SB1 + 0x0FE4 | Bits 0–7 = badges 1–8 |
| Money | SB1 + 0x0290 XOR SB2 + 0x0F20 | Player money (XOR-encrypted) |
| Player Name | SB2 + 0x0000 | 8 bytes, Gen III charset encoding |

---
*Last updated: 2026-02-21*
