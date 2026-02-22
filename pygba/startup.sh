#!/bin/bash
# LLM Plays Pokemon -- PyGBA orchestrated startup
# Launches the pure Python agent with pre-flight checks and clear guidance.

set -e

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR" && pwd)"
REPO_ROOT="$(cd "$PROJECT_ROOT/.." && pwd)"
PROJECT_VENV="$PROJECT_ROOT/.venv"
if [[ -n "$LPP_VENV" && -f "$LPP_VENV/bin/python" ]]; then
  VENV="$LPP_VENV"
else
  VENV="$PROJECT_VENV"
fi

CONFIG_PATH="$PROJECT_ROOT/config.json"
DEFAULT_ROM_PATH="../gamefile/Pokemon FireRed.gba"
ROM_PATH="$DEFAULT_ROM_PATH"
LLM_BACKEND="ollama"
NO_TAIL=false
NO_LOG=false
QUIET=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --no-tail)
      NO_TAIL=true
      shift
      ;;
    --no-log)
      NO_LOG=true
      shift
      ;;
    -q|--quiet)
      QUIET=true
      shift
      ;;
    -h|--help)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "  Launches the PyGBA agent (python -m pygba) with pre-flight checks."
      echo ""
      echo "Options:"
      echo "  --no-tail    Skip spawning a separate terminal for log tail"
      echo "  --no-log     Skip logging output to logs/ (no tee, no tail window)"
      echo "  -q, --quiet  Reduce startup-script output (agent output unchanged)"
      echo "  -h, --help   Show this help"
      echo ""
      echo "Environment:"
      echo "  LPP_VENV      Venv path (default: <project>/pygba/.venv)"
      echo "  LPP_NO_TAIL   Set to 1 to disable tail window"
      echo "  LPP_TAIL_TERM Terminal emulator for tail window"
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

if ! $NO_LOG; then
  mkdir -p "$REPO_ROOT/logs"
  LOG_FILE="$REPO_ROOT/logs/LPP-$(date +%Y-%m-%d-%H-%M-%S).txt"
  touch "$LOG_FILE"

  if [[ -z "$LPP_NO_TAIL" || "$LPP_NO_TAIL" != "1" ]] && ! $NO_TAIL && [[ -n "$DISPLAY" ]]; then
    SPAWNED_TAIL=false
    if [[ -n "$LPP_TAIL_TERM" ]]; then
      if command -v "$LPP_TAIL_TERM" &>/dev/null; then
        case "$LPP_TAIL_TERM" in
          gnome-terminal)
            gnome-terminal -q -- tail -f "$LOG_FILE" &
            SPAWNED_TAIL=true
            ;;
          xfce4-terminal)
            xfce4-terminal -e "tail -f \"$LOG_FILE\"" &
            SPAWNED_TAIL=true
            ;;
          konsole)
            konsole -e "tail -f \"$LOG_FILE\"" &
            SPAWNED_TAIL=true
            ;;
          xterm)
            xterm -e "tail -f \"$LOG_FILE\"" &
            SPAWNED_TAIL=true
            ;;
          *)
            "$LPP_TAIL_TERM" -e "tail -f \"$LOG_FILE\"" &
            SPAWNED_TAIL=true
            ;;
        esac
      fi
    else
      if command -v gnome-terminal &>/dev/null; then
        gnome-terminal -q -- tail -f "$LOG_FILE" &
        SPAWNED_TAIL=true
      elif command -v xfce4-terminal &>/dev/null; then
        xfce4-terminal -e "tail -f \"$LOG_FILE\"" &
        SPAWNED_TAIL=true
      elif command -v konsole &>/dev/null; then
        konsole -e "tail -f \"$LOG_FILE\"" &
        SPAWNED_TAIL=true
      elif command -v xterm &>/dev/null; then
        xterm -e "tail -f \"$LOG_FILE\"" &
        SPAWNED_TAIL=true
      fi
    fi
    if $SPAWNED_TAIL; then
      sleep 0.5
    fi
  fi

  exec > >(tee -a "$LOG_FILE") 2>&1
fi

print_msg() {
  if ! $QUIET; then
    echo "$@"
  fi
}

echo ""
print_msg "═══════════════════════════════════════════════════════════════"
print_msg "  LLM PLAYS POKEMON -- PyGBA Startup"
print_msg "═══════════════════════════════════════════════════════════════"
if ! $NO_LOG; then
  print_msg "  Log file: $LOG_FILE"
fi
print_msg ""

echo "[1/7] Resolving project root..."
echo "      -> $PROJECT_ROOT"
cd "$PROJECT_ROOT"
echo ""

echo "[2/7] Checking config..."
if [[ ! -f "$CONFIG_PATH" ]]; then
  echo "      ERROR: config.json not found at $CONFIG_PATH"
  echo "      See ../docs/reference.md for expected pygba config schema."
  exit 1
fi
echo "      -> $CONFIG_PATH"
echo ""

echo "[3/7] Setting up virtual environment..."
if [[ ! -f "$VENV/bin/python" ]]; then
  echo "      Creating .venv at $PROJECT_VENV"
  python3 -m venv "$PROJECT_VENV"
  VENV="$PROJECT_VENV"
fi
source "$VENV/bin/activate"
echo "      -> Installing dependencies..."
pip install -q -r "$PROJECT_ROOT/requirements.txt"
echo "      -> $VENV"
echo "      -> Python: $(python3 --version 2>&1)"
echo ""

echo "[4/7] Reading config (ROM + LLM backend)..."
CONFIG_VALUES="$(python3 - "$CONFIG_PATH" <<'PY'
import json
import sys

config_path = sys.argv[1]
with open(config_path, "r", encoding="utf-8") as f:
    data = json.load(f)

rom_path = data.get("rom_path", "../gamefile/Pokemon FireRed.gba")
llm = data.get("llm", {})
backend = llm.get("backend", "ollama")

print(rom_path)
print(backend)
PY
)"
ROM_PATH="$(printf '%s\n' "$CONFIG_VALUES" | sed -n '1p')"
LLM_BACKEND="$(printf '%s\n' "$CONFIG_VALUES" | sed -n '2p')"
if [[ -z "$ROM_PATH" ]]; then
  ROM_PATH="$DEFAULT_ROM_PATH"
fi
if [[ -z "$LLM_BACKEND" ]]; then
  LLM_BACKEND="ollama"
fi
echo "      -> rom_path: $ROM_PATH"
echo "      -> llm.backend: $LLM_BACKEND"
echo ""

echo "[5/7] Checking ROM file..."
ROM_FULL="$(cd "$PROJECT_ROOT" && realpath "$ROM_PATH" 2>/dev/null || echo "$PROJECT_ROOT/$ROM_PATH")"
if [[ ! -f "$ROM_FULL" ]]; then
  GAMEFILE_DIR="$REPO_ROOT/gamefile"
  shopt -s nullglob nocaseglob
  ROM_CANDIDATES=("$GAMEFILE_DIR"/pokemon*.zip "$GAMEFILE_DIR"/pokemon*.gba)
  shopt -u nocaseglob nullglob

  if [[ ${#ROM_CANDIDATES[@]} -gt 0 ]]; then
    ROM_FULL="${ROM_CANDIDATES[0]}"
    echo "      -> Configured rom_path not found: $ROM_PATH"
    echo "      -> Auto-detected ROM in gamefile/: $(basename "$ROM_FULL")"
  else
    echo "      ERROR: ROM not found at $ROM_PATH"
    echo "      Also checked: gamefile/pokemon*.zip and gamefile/pokemon*.gba"
    echo "      Set rom_path in pygba/config.json to your FireRed/LeafGreen ROM."
    echo "      See ../docs/getting-started.md and ../docs/troubleshooting.md"
    exit 1
  fi
fi
echo "      -> $ROM_FULL"
echo ""

echo "[6/7] Checking mGBA Python bindings..."
if ! python3 -c "import mgba.core" >/dev/null 2>&1; then
  echo "      ERROR: mGBA Python bindings not found (import mgba.core failed)"
  echo "      Run: bash pygba/setup_mgba.sh"
  echo "      See ../docs/getting-started.md, ../docs/troubleshooting.md, and ../pygba/README.md"
  exit 1
fi
echo "      -> mgba.core import successful"
echo ""

echo "[7/7] LLM backend check..."
if [[ "$LLM_BACKEND" == "ollama" ]]; then
  if ! command -v ollama &>/dev/null; then
    echo "      ERROR: ollama not found in PATH"
    echo "      Install: curl -fsSL https://ollama.com/install.sh | sh"
    echo "      See ../docs/getting-started.md and ../docs/troubleshooting.md"
    exit 1
  fi
  echo "      -> $(command -v ollama)"
  echo "      Please start Ollama now if it is not already running: ollama serve"
  echo "      Press Enter to continue, or wait 60 seconds to proceed automatically..."
  if [[ -t 0 ]]; then
    (
      for ((i=60; i>=0; i-=5)); do
        echo "      [$i seconds remaining...]"
        sleep 5
      done
    ) &
    COUNTDOWN_PID=$!
    read -r -t 60 || true
    kill "$COUNTDOWN_PID" 2>/dev/null || true
    wait "$COUNTDOWN_PID" 2>/dev/null || true
  else
    echo "      Non-interactive mode: skipping pause. Ensure Ollama is already running."
  fi
else
  echo "      -> llm.backend is '$LLM_BACKEND'; skipping ollama binary check."
fi
echo ""

echo "───────────────────────────────────────────────────────────────"
echo "  Starting PyGBA Agent (foreground)"
echo "───────────────────────────────────────────────────────────────"
echo "  -> Working directory: $PROJECT_ROOT"
echo "  -> Running: python3 -m pygba"
echo "  -> PYTHONPATH includes repo root for package resolution"
echo "  Press Ctrl+C to stop."
echo "───────────────────────────────────────────────────────────────"
echo ""

PYTHONPATH="$REPO_ROOT${PYTHONPATH:+:$PYTHONPATH}" python3 -m pygba
