# Reference

Technical reference for configuration, game modes, project structure, and memory addresses.

## config.json

All settings live in `config.json` at the project root:

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

### Field Reference

| Field | Description |
|-------|-------------|
| **backend** | `"ollama"` (default) uses native Ollama `/api/chat`. `"openai-compat"` works with LM Studio, Ollama (via `/v1/`), llama.cpp, llamafile. |
| **base_url** | Host and port of the LLM server. No path — the client appends it. |
| **model** | Required for Ollama (default backend). Optional for LM Studio, llamafile (single-model servers). |
| **api_key** | `null` for local backends. Set for cloud APIs. |
| **temperature** | Lower (0.2–0.4) = more consistent play. Higher = more creative but erratic. |
| **max_tokens** | Cap on LLM response length. 300 is enough for the JSON output. |
| **timeout_seconds** | How long to wait for an LLM response before retrying. |
| **data_dir** | Directory for `state.json` and `command.json`. Relative to project root. |
| **state_poll_interval_seconds** | How often the bridge polls for new state. |
| **history_length** | How many past turns to keep in the LLM's context window. |
| **lua.frame_poll_interval** | How many frames between state writes (Lua side). |

---

## Game Modes

The agent detects four game modes and adapts its action space:

| Mode | Detection | Available Actions |
|------|-----------|-------------------|
| **Overworld** | Default state | move_up, move_down, move_left, move_right, interact, open_menu, wait |
| **Dialog** | Text buffer active | continue, choose_yes, choose_no |
| **Battle** | Battle flags set | fight_move_1 through fight_move_4, switch_2 through switch_6, use_item, run |
| **Menu** | Movement locked | menu_pokemon, menu_bag, menu_save, menu_close |

In battle mode, moves with 0 PP are excluded from the action list, and only party members with HP > 0 are offered as switch targets.

---

## Project Structure

```
llm-plays-pokemon/
  config.json               # LLM backend + timing configuration
  startup.sh                # Orchestrated launch (mGBA + bridge)
  logs/                     # Log files (LPP-YYYY-MM-DD-HH-MM-SS.txt)
  requirements.txt          # Python dependencies (requests)
  AGENTS.md                 # Changelog of all accepted changes
  docs/
    getting-started.md      # Setup and first-run tutorial
    architecture.md         # System design and philosophy
    reference.md            # This file
    troubleshooting.md      # Common issues and fixes
  gamefile/                       # Place your legally owned FireRed/LeafGreen ROM here
    (user-supplied .zip or .gba)  # mGBA loads directly from ZIP; see getting-started for backup notes
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

---

## FireRed RAM Addresses (US v1.0 / BPRE)

The Lua script reads these memory addresses. Values are in the game's native format and decoded by the script.

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

Player X/Y and other derived values are read via SaveBlock pointers. See [lua/game_agent.lua](../lua/game_agent.lua) for full implementation.

---
*Last updated: 2026-02-21*
