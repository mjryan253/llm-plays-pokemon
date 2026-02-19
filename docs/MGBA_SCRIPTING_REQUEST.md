# mGBA Scripting: Lateral Red Use Case & Feature Request

**Audience:** mGBA development team  
**Project:** Lateral Red (LR-1) — An autonomous Pokemon FireRed agent powered by local LLMs  
**Contact:** Matthew Ryan, LLM-plays-pokemon@tutamail.com and here on GitHub (github.com/mjryan253) 

---

## Executive Summary

We're building an AI agent that uses mGBA's Lua scripting API to read game RAM and inject inputs—no computer vision required. The project works today but requires **manually loading the Lua script** via Tools → Scripting → Load Script every time mGBA starts. We've inspected the mGBA source and see that `--script` exists in the codebase; we're seeking clarity on availability in released builds and any guidance for our workflow.

---

## What We Do With mGBA Scripting

### Architecture

```
mGBA (Lua)                    Python Bridge              Local LLM
+-------------------+         +------------------+        +-----------+
| Poll RAM every    | state   | Poll state.json  |        | LM Studio |
| 30 frames:        |-------->| Build prompts    |------->| Ollama    |
| - Player pos      | .json   | Parse JSON       |        | etc.      |
| - Party + moves   |         | Enrich IDs       |<-------|
| - Game mode       | command |                  |  JSON  |
| - Dialog/battle   |<--------| Write command    |        |
| Execute buttons   | .json   |                  |        |
+-------------------+         +------------------+        +
```

- **Lua script** (`game_agent.lua`): Reads FireRed RAM, decrypts Gen III Pokémon data (XOR + substructure permutation), writes `state.json` to a shared `data/` folder, reads `command.json` with button sequences, and injects input via the scripting API.
- **Python bridge**: Polls `state.json`, sends state to an LLM, parses the response, writes `command.json` with button steps.
- **IPC**: File-based (`data/state.json`, `data/command.json`). Both processes must agree on the same `data/` path.

### Script Requirements

| Requirement | Details |
|-------------|---------|
| **RAM access** | `memory:read8/16/32`, `memory.wram`, `memory.iwram` — already used |
| **Input injection** | `input.game()` / gamepad API — already used |
| **File I/O** | `io.open` for `state.json`, `command.json` — works |
| **Frame callback** | `callbacks:add("frame", fn)` — core loop |
| **CWD / paths** | Script loads `lua/data_dir.txt` (path from bridge). Fallback: relative `data/`. mGBA must run from project root so relative paths resolve correctly. |

---

## The Friction: Manual Script Loading

**Current workflow:**

1. Start mGBA from project root: `mgba-qt "gamefile/Pokemon_ FireRed Version.zip"`
2. Wait for game to load
3. **Manually:** Tools → Scripting → File → Load Script → select `lua/game_agent.lua`
4. Start Python bridge in another terminal
5. Agent runs

**Ideal workflow:**

```bash
mgba-qt --script lua/game_agent.lua "gamefile/Pokemon_ FireRed Version.zip"
# Or with absolute path:
mgba-qt --script /path/to/llm-plays-pokemon/lua/game_agent.lua /path/to/rom.zip
```

Then the bridge starts and the agent runs with no manual steps.

---

## What We Found in the mGBA Source

We cloned the mGBA repo and inspected the Qt frontend:

### `--script` support in source

**ConfigController.cpp** (lines 24–26, 166–169, 190–198):

```cpp
#ifdef ENABLE_SCRIPTING
	{ "script", true, '\0' },
#endif
// ...
"  --script FILE  Run a script on start. Can be passed multiple times\n"
// ...
if (optionName == QLatin1String("script")) {
    QStringList scripts;
    // ... appends arg to scripts, stores in m_argvOptions
}
```

**Window.cpp** (lines 2304–2312):

```cpp
#ifdef ENABLE_SCRIPTING
	if (!m_scripting) {
		QStringList scripts = m_config->getArgvOption("script").toStringList();
		if (!scripts.isEmpty()) {
			scriptingOpen();
			for (const auto& scriptPath : scripts) {
				m_scripting->loadFile(scriptPath);
			}
		}
	}
#endif
```

So `--script` is wired through the config parser and invoked when the game/scripting layer is ready.

### Observed behavior

- **mgba-qt 0.10.2** (Ubuntu `apt install mgba-qt`): `--script` is not present in `--help`; passing it yields "unrecognized option".
- **mGBA source (master):** Contains full `--script` logic under `ENABLE_SCRIPTING`.

We assume either:

1. ENABLE_SCRIPTING (or related deps) is disabled in the Ubuntu build, or  
2. The distro package is from a version before `--script` was added or exposed.

---

## Questions for the mGBA Team

1. **`--script` in released builds**
   - Is `--script` intended to be part of the standard Qt build?
   - In which version/release will it be documented and available?
   - Are there known packaging/build flags that omit it?

2. **Timing and CWD**
   - When `--script` is used, at what point does the script run relative to ROM load?
   - Is the process CWD well-defined at that moment? We depend on mGBA being started from the project root so paths like `lua/data_dir.txt` and `data/` resolve correctly.

3. **Build instructions**
   - For users who need `--script` today, is building from source with `ENABLE_SCRIPTING=ON` (and any required Lua/JSON deps) the recommended path?
   - Are there platform-specific gotchas (e.g. Ubuntu)?

4. **Autorun scripts**
   - We see `AutorunScriptModel` and “Edit autorun scripts…” in the UI. Do autorun scripts persist across sessions and load automatically with the game?
   - If so, would that be a supported alternative to `--script` for our use case?

---

## Proposed Changes (If Helpful)

If the team is open to small improvements, we’d be interested in:

- **Docs:** Document `--script` in the user-facing docs (e.g. scripting page, man page) with path and CWD behavior.
- **Path handling:** If `--script` receives a relative path, confirm it’s resolved against process CWD when the script is loaded.
- **Pre-load option:** An option to load scripts before or immediately with the ROM (for scripts that depend on early setup) could help automation use cases.

We’re also happy to contribute documentation or example workflows if that would be useful.

---

## References

- **Our project:** `llm-plays-pokemon` (Lateral Red)
- **Lua script:** Reads FireRed RAM, Gen III decryption, file-based IPC
- **mGBA scripting API:** https://mgba.io/docs/scripting.html
- **Relevant source paths:**
  - `src/platform/qt/ConfigController.cpp` — `--script` registration
  - `src/platform/qt/Window.cpp` — script loading on game load
  - `src/platform/qt/scripting/ScriptingController.cpp` — `loadFile()`, autorun

---

Thank you for maintaining mGBA and the scripting system. It’s enabling projects like ours that wouldn’t be practical without direct RAM access and input injection.
