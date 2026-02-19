# AGENTS.md -- Lateral Red (LR-1) Changelog

## 2026-02-18

- **Initial build**: Scaffolded full project -- Lua game agent with Gen III substructure decryption, Python bridge with mode-aware prompting, multi-backend LLM client, Pokemon data tables (386 species, 354 moves, map names) (`lua/game_agent.lua`, `bridge/`, `config.json`, `requirements.txt`)
- **Multi-backend support**: LLM client supports Ollama, LM Studio, llama.cpp, llamafile, and any OpenAI-compatible API via config (`bridge/llm_client.py`)
- **Model field optional**: `model` can be omitted from `config.json` when the server (e.g. LM Studio) picks the loaded model automatically (`bridge/llm_client.py`, `config.json`)
- **Verbose CLI output**: Default output shows full game state sent to LLM, raw response, thinking/narrative, and chosen action per turn with color-coded mode headers; `--quiet` flag available for minimal output (`bridge/main.py`)
