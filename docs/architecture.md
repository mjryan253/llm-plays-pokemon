# Architecture

Explanation of how LLM Plays Pokemon works and the design philosophy behind both components.

## Philosophy: Lateral Thinking with Withered Technology

By invoking **Gunpei Yokoi's "Lateral Thinking with Withered Technology"** (*Kareshi Gijutsu no Shisō*), we avoid building a cutting-edge computer vision monster. Instead, we use "withered" (mature, stable) tech like **mGBA's Lua API**, **direct Python bindings**, and **text-based memory scraping** to give a modern LLM "eyes" without the overhead of heavy video processing.

> "The Nintendo way of adapting technology is not to look for the state-of-the-art... but to utilize mature technology that can be mass-produced cheaply." — Gunpei Yokoi

**Guiding Principles:**

1. **Do More with Less:** Prioritize text-based state over image-processing.
2. **The "Ghost in the Machine":** The LLM is both the player and the narrator.
3. **Sideways Thinking:** If the AI gets stuck in a corner, don't build a pathfinding algorithm — give the AI a "Compass" in its prompt. (pygba takes this further with actual BFS pathfinding to *complement* the LLM.)

---

## Component Comparison

| Aspect | pygba | mgba-lua |
|--------|-------|----------|
| **Language** | Pure Python | Lua (mGBA) + Python (bridge) |
| **IPC** | None — single process | File-based: `state.json` / `command.json` |
| **Memory access** | `mgba.core` Python bindings | `emu:read*` Lua API |
| **Display** | Headless, streaming terminal | mGBA GUI window |
| **Actions per turn** | Multi-action plan (up to 20) | One action per turn |
| **Planning** | Hierarchical (strategic / tactical / reactive) | Reactive only |
| **Navigation** | BFS pathfinding over 70-node map graph | None (LLM navigates by itself) |
| **LLM streaming** | Yes (live token display) | No (waits for full response) |
| **Progress tracking** | Badges, money, player name, party levels | Turn count, position |
| **LLM backends** | Ollama, OpenAI-compatible | Ollama, LM Studio, llama.cpp, llamafile |

---

## pygba Architecture

A single Python process drives everything:

```
Agent.run() loop
  │
  ├── Emulator (mgba.core wrapper)
  │     └── read_u8/u16/u32, press_key, tick
  │
  ├── GameState (RAM reader)
  │     └── collect_state, game_progress, read_badges, read_money
  │
  ├── Planner (hierarchical)
  │     ├── Strategic: LLM sets high-level goal every N turns
  │     ├── Tactical: LLM creates multi-action plan toward goal
  │     └── Reactive: interrupts on mode change (e.g. battle start)
  │
  ├── Navigator (BFS pathfinding)
  │     └── 70-node FireRed map graph, directional edges
  │
  ├── StreamingLLMClient
  │     └── Ollama native / OpenAI-compat with on_token callback
  │
  └── Prompt (multi-action builder)
        └── progress context, nav hints, compressed party format
```

### Loop

```
tick(30 frames) → collect_state(emu) → planner.get_or_create_plan() → execute_action(emu)
```

No file I/O, no polling. The emulator ticks forward, RAM is read directly, the planner calls the LLM when its action queue is empty (or on mode change), and button presses go straight to the emulator.

### Hierarchical Planning

- **Strategic layer** — every N turns (default 50), or when a badge is gained, a separate LLM call evaluates big-picture progress and sets a goal (e.g. "Beat Brock", "Navigate to Cerulean City").
- **Tactical layer** — when the plan queue is empty, the LLM generates a multi-action sequence toward the current goal. Navigator provides path hints for overworld navigation.
- **Reactive layer** — on mode change (entering battle, dialog, menu), the current plan is interrupted and a mode-appropriate plan is requested immediately.

---

## mgba-lua Architecture

Three components working in a loop:

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

### The Senses (mGBA + Lua)

A Lua script runs inside mGBA. It polls specific memory addresses (Player X/Y, Map ID, Menu Open, Dialogue Active) and writes game state to `state.json`. It also reads commands from `command.json` and executes button sequences via mGBA's API.

### The Brain (LLM)

A local LLM (Llama, Qwen, Mistral, etc.) running an OpenAI-compatible server. It receives the game state as a prompt and outputs a JSON object containing narrative reasoning and a chosen action.

### The Nervous System (Python Bridge)

A lightweight Python script that reads `state.json`, enriches IDs with species/move/map names, builds mode-aware prompts, sends requests to the LLM, parses the response, and writes button sequences to `command.json`.

### File-based IPC

Communication between mGBA and Python via `data/state.json` and `data/command.json`:

- **state.json** — written by Lua, read by the bridge. Contains player position, party, battle state, dialog text, game mode.
- **command.json** — written by the bridge, read by Lua. Contains button sequences (keys + frame counts).

Atomic writes (write to `.tmp`, then rename) prevent partial reads.

---

## Gen III Pokemon Data

Both components decrypt the Gen III Pokemon data structure to extract full party data including all four moves and PP for each Pokemon.

- **Encryption:** XOR cipher with `personality_value XOR ot_id`
- **Substructure order:** Determined by `personality_value % 24` (24 possible permutations)

pygba adds badge/money/player-name reading on top of the base party data.

---

## Mode-Aware Prompts

Both components detect game modes and adapt the action space:

- **Overworld** — movement, interact, menu
- **Dialog** — continue, yes/no choices
- **Battle** — fight moves, switch, items, run
- **Menu** — navigate menus or close

In battle mode, moves with 0 PP are excluded and only party members with HP > 0 are offered as switch targets.

pygba's prompts additionally include progress context (badges, money, party composition), navigation hints from the BFS pathfinder, and request multi-action plans rather than single actions.

---

## Anti-Loop Detection (mgba-lua)

The bridge warns the LLM when it has been at the same position for 5+ turns or repeating the same action 4+ times. pygba addresses this differently through its hierarchical planner, which interrupts and re-plans when goals aren't being met.

---

## Model-Agnostic Design

The `model` field is required for Ollama (the default backend). For LM Studio, llamafile, or other single-model servers, you can omit it — the client talks to whatever the server is running.

---

## Junior Dev Roadmap

For contributors extending or rebuilding parts of the system:

### Phase 1: Memory Scraping

- Find a Pokemon FireRed RAM map
- Write Lua or Python to read Player X/Y, Map ID
- Output a simple context string: *"You are at (10,5) in Pallet Town."*

### Phase 2: Command Bridge

- Use mGBA's Lua or Python API to inject inputs
- Create macros like `Walk_North` (hold Up for 16 frames) rather than single button presses

### Phase 3: Narrative Prompt

- Format: `{"narrative": "...", "action": "MOVE_NORTH"}`
- Force the LLM to think before it acts

### Win Condition

1. Obtain 8 Badges
2. Defeat the Elite Four
3. Zero human intervention — the human only watches and listens to the narration

---
*Last updated: 2026-02-21*
