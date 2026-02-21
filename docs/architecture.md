# Architecture

Explanation of how Lateral Red works and the design philosophy behind it.

## Philosophy: Lateral Thinking with Withered Technology

By invoking **Gunpei Yokoi's "Lateral Thinking with Withered Technology"** (*Kareshi Gijutsu no Shisō*), we avoid building a cutting-edge computer vision monster. Instead, we use "withered" (mature, stable) tech like **mGBA's Lua API** and **text-based memory scraping** to give a modern LLM "eyes" without the overhead of heavy video processing.

> "The Nintendo way of adapting technology is not to look for the state-of-the-art... but to utilize mature technology that can be mass-produced cheaply." — Gunpei Yokoi

**Guiding Principles:**

1. **Do More with Less:** Prioritize text-based state over image-processing.
2. **The "Ghost in the Machine":** The LLM is both the player and the narrator.
3. **Sideways Thinking:** If the AI gets stuck in a corner, don't build a pathfinding algorithm — give the AI a "Compass" in its prompt.

---

## System Architecture

The project consists of three components working in a loop:

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

### 1. The Senses (mGBA + Lua)

A Lua script runs inside mGBA. It polls specific memory addresses (Player X/Y, Map ID, Menu Open, Dialogue Active) and writes game state to `state.json`. It also reads commands from `command.json` and executes button sequences via mGBA's API.

### 2. The Brain (LLM)

A local LLM (Llama, Qwen, Mistral, etc.) running an OpenAI-compatible server. It receives the game state as a prompt and outputs a JSON object containing narrative reasoning and a chosen action.

### 3. The Nervous System (Python Bridge)

A lightweight Python script that:

- Reads `state.json`
- Enriches IDs with species/move/map names
- Builds mode-aware prompts
- Sends requests to the LLM
- Parses the response and writes button sequences to `command.json`

---

## Data Flow

**File-based IPC** between mGBA and Python via `data/state.json` and `data/command.json`:

- **state.json** — written by Lua, read by the bridge. Contains player position, party, battle state, dialog text, game mode.
- **command.json** — written by the bridge, read by Lua. Contains button sequences (keys + frame counts).

Atomic writes (write to `.tmp`, then rename) prevent partial reads.

---

## Gen III Pokemon Data

The Lua script decrypts the Gen III Pokemon data structure to extract full party data including all four moves and PP for each Pokemon.

- **Encryption:** XOR cipher with `personality_value XOR ot_id`
- **Substructure order:** Determined by `personality_value % 24` (24 possible permutations)

See [lua/game_agent.lua](../lua/game_agent.lua) for implementation details.

---

## Mode-Aware Prompts

The bridge detects four game modes and adapts the action space:

- **Overworld** — movement, interact, menu
- **Dialog** — continue, yes/no choices
- **Battle** — fight moves, switch, items, run
- **Menu** — navigate menus or close

In battle mode, the LLM sees each move's name, type, and remaining PP alongside enemy info. Moves with 0 PP are excluded; only party members with HP > 0 are offered as switch targets.

---

## Anti-Loop Detection

The bridge warns the LLM when it has been at the same position for 5+ turns or repeating the same action 4+ times. This helps avoid getting stuck in corners or repetitive loops.

---

## Model-Agnostic Design

The `model` field is required for Ollama (the default backend). For LM Studio, llamafile, or other single-model servers, you can omit it — the bridge talks to whatever the server is running.

---

## Junior Dev Roadmap

For contributors extending or rebuilding parts of the system:

### Phase 1: Memory Scraping

- Find a Pokemon FireRed RAM map
- Write Lua to read Player X/Y, Map ID
- Output a simple context string: *"You are at (10,5) in Pallet Town."*

### Phase 2: Command Bridge

- Use mGBA's Lua API to inject inputs
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
