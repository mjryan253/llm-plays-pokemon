# mGBA Submission Kit: Script Auto-Load Feature Request

Submit to: **https://github.com/mgba-emu/mgba/issues**

Per [CONTRIBUTING.md](https://github.com/mgba-emu/mgba/blob/master/CONTRIBUTING.md): include your build, OS, and describe the request in detail.

---

## Copy-Paste Submission (Markdown)

Copy everything between the dashed lines below and paste it into a new GitHub issue. Edit the bracketed fields in the header first.

---

```
**Build:** mgba-qt 0.10.2 (Ubuntu apt)
**OS:** Ubuntu 24.04 64-bit
**Type:** Feature request
**Contact:** Matthew Ryan, LLM-plays-pokemon@tutamail.com, github.com/mjryan253

---

## Summary

We're building an AI agent (Lateral Red) that uses mGBA's Lua scripting API to read game RAM and inject inputs—no computer vision. The project works today but requires manually loading the Lua script via Tools → Scripting → Load Script every time mGBA starts. We've inspected the mGBA source and see that `--script` exists in the codebase; we're seeking clarity on availability in released builds and any guidance for our workflow.

## Current Workflow (Manual)

1. Start mGBA from project root: `mgba-qt "gamefile/Pokemon_ FireRed Version.zip"`
2. Wait for game to load
3. Manually: Tools → Scripting → File → Load Script → select `lua/game_agent.lua`
4. Start Python bridge in another terminal
5. Agent runs

## Desired Workflow (Automated)

    mgba-qt --script lua/game_agent.lua "gamefile/Pokemon_ FireRed Version.zip"

Then the bridge starts and the agent runs with no manual steps.

## What We Use From mGBA Scripting

- **RAM access:** `memory:read8/16/32`, `memory.wram`, `memory.iwram`
- **Input injection:** gamepad API
- **File I/O:** `io.open` for `state.json`, `command.json` (file-based IPC with a Python bridge)
- **Frame callback:** `callbacks:add("frame", fn)`
- **CWD:** Script loads `lua/data_dir.txt` and writes to `data/`. mGBA must run from project root so relative paths resolve.

## What We Found in the Source

We cloned the repo and see `--script` in:

- **ConfigController.cpp** (lines 24–26, 166–169, 190–198): option registration and parsing
- **Window.cpp** (lines 2304–2312): loads scripts when game/scripting is ready

**Observed behavior:**

- mgba-qt 0.10.2 (Ubuntu apt): `--script` not in `--help`; passing it yields "unrecognized option"
- mGBA master source: Full `--script` logic under `ENABLE_SCRIPTING`

We assume either ENABLE_SCRIPTING is off in the distro build, or the package predates this feature.

## Questions for the mGBA Team

1. **Availability:** Is `--script` intended for the standard Qt build? In which version will it be documented and available?
2. **Packaging:** Are there known build/packaging flags that omit it (e.g. Ubuntu)?
3. **Timing/CWD:** When does the script run relative to ROM load? Is process CWD well-defined?
4. **Build from source:** For users who need `--script` now, is building with `ENABLE_SCRIPTING=ON` the recommended path? Any platform gotchas (e.g. Ubuntu)?
5. **Autorun scripts:** Does "Edit autorun scripts…" persist and auto-load with the game? Could that be an alternative?

## References

- mGBA scripting API: https://mgba.io/docs/scripting.html
- Source: ConfigController.cpp, Window.cpp, ScriptingController.cpp
```

---

## Notes

- **Issues:** https://github.com/mgba-emu/mgba/issues (or http://mgba.io/i/)
- **Discussions:** https://github.com/mgba-emu/mgba/discussions (for informal Q&A)
- Suggested issue title: **Feature request: document/expose --script for auto-loading Lua scripts**
