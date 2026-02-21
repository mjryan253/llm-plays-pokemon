#!/bin/bash
# Lateral Red (LR-1) -- Orchestrated startup
# Launches mGBA and the Python bridge with verbose pre-flight checks.

set -e

# ---------------------------------------------------------------------------
# Configuration (override with environment variables)
# ---------------------------------------------------------------------------
ROM_PATH="gamefile/Pokemon_ FireRed Version.zip"

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR" && pwd)"
PROJECT_VENV="$PROJECT_ROOT/.venv"
if [[ -n "$LATERAL_RED_VENV" && -f "$LATERAL_RED_VENV/bin/python" ]]; then
  VENV="$LATERAL_RED_VENV"
else
  VENV="$PROJECT_VENV"
fi

# Parse flags
START_MGBA=true
BRIDGE_QUIET=""
NO_TAIL=false
NO_LOG=false
while [[ $# -gt 0 ]]; do
  case $1 in
    --no-mgba)
      START_MGBA=false
      shift
      ;;
    --no-tail)
      NO_TAIL=true
      shift
      ;;
    --no-log)
      NO_LOG=true
      shift
      ;;
    -q|--quiet)
      BRIDGE_QUIET="--quiet"
      shift
      ;;
    -h|--help)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "  Launches mGBA (with ROM) and the Lateral Red bridge."
      echo ""
      echo "Options:"
      echo "  --no-mgba    Skip launching mGBA (use when already running)"
      echo "  --no-tail    Skip spawning a separate terminal for log tail"
      echo "  --no-log     Skip logging output to logs/ (no tee, no tail window)"
      echo "  -q, --quiet  Run bridge with --quiet (minimal output)"
      echo "  -h, --help   Show this help"
      echo ""
      echo "Environment:"
      echo "  LATERAL_RED_VENV   Venv path (default: <project>/.venv)"
      echo "  LATERAL_RED_NO_TAIL  Set to 1 to disable tail window"
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

MGBA_PID=""

# ---------------------------------------------------------------------------
# Log setup (tee all output to timestamped log file) — skipped if --no-log
# ---------------------------------------------------------------------------
if ! $NO_LOG; then
  mkdir -p "$PROJECT_ROOT/logs"
  LOG_FILE="$PROJECT_ROOT/logs/LPP-$(date +%Y-%m-%d-%H-%M-%S).txt"
  touch "$LOG_FILE"

  # Spawn separate terminal with tail -f (unless disabled)
  if [[ -z "$LATERAL_RED_NO_TAIL" || "$LATERAL_RED_NO_TAIL" != "1" ]] && ! $NO_TAIL && [[ -n "$DISPLAY" ]]; then
  SPAWNED_TAIL=false
  if [[ -n "$LATERAL_RED_TAIL_TERM" ]]; then
    if command -v "$LATERAL_RED_TAIL_TERM" &>/dev/null; then
      case "$LATERAL_RED_TAIL_TERM" in
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
          "$LATERAL_RED_TAIL_TERM" -e "tail -f \"$LOG_FILE\"" &
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

  # Tee all output to log file and terminal
  exec > >(tee -a "$LOG_FILE") 2>&1
fi

# ---------------------------------------------------------------------------
# Cleanup on exit
# ---------------------------------------------------------------------------
cleanup() {
  if [[ -n "$MGBA_PID" ]] && kill -0 "$MGBA_PID" 2>/dev/null; then
    echo ""
    echo "[shutdown] Stopping mGBA (PID $MGBA_PID)..."
    kill "$MGBA_PID" 2>/dev/null || true
    wait "$MGBA_PID" 2>/dev/null || true
    echo "[shutdown] mGBA stopped."
  fi
  exit 0
}
trap cleanup EXIT INT TERM

# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  LATERAL RED (LR-1) — Orchestrated Startup"
echo "═══════════════════════════════════════════════════════════════"
if ! $NO_LOG; then
  echo "  Log file: $LOG_FILE"
fi
echo ""

# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------
echo "[1/9] Resolving project root..."
echo "      -> $PROJECT_ROOT"
cd "$PROJECT_ROOT"
echo ""

echo "[2/9] Checking mGBA (0.11+ required for --script)..."
if ! command -v mgba-qt &>/dev/null; then
  echo "      ERROR: mgba-qt not found in PATH"
  echo "      Install: sudo apt install mgba-qt"
  echo "      See docs/getting-started.md and docs/troubleshooting.md"
  exit 1
fi
MGBA_BIN="$(command -v mgba-qt)"
MGBA_VERSION_RAW="$("$MGBA_BIN" --version 2>/dev/null || echo "0.0")"
MGBA_VERSION="$(echo "$MGBA_VERSION_RAW" | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -1)"
version_ge() { test "$(printf '%s\n' "$1" "$2" | sort -V | head -1)" = "$2"; }
if ! version_ge "${MGBA_VERSION:-0}" "0.11"; then
  echo "      ERROR: mGBA version ${MGBA_VERSION:-unknown} is below 0.11"
  echo "      --script requires mGBA 0.11+. On Linux, packaged 0.10.5 has --script disabled."
  echo "      See docs/getting-started.md and docs/troubleshooting.md for mGBA 0.11+ / development downloads."
  exit 1
fi
echo "      -> $MGBA_BIN"
echo "      -> Version: $MGBA_VERSION"
echo ""

echo "[3/9] Setting up virtual environment..."
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

echo "[4/9] Checking Ollama..."
if ! command -v ollama &>/dev/null; then
  echo "      ERROR: ollama not found in PATH"
  echo "      Ollama must be installed for the default LLM backend."
  echo "      See docs/getting-started.md (Prerequisites, Step 1) for install and setup."
  exit 1
fi
echo "      -> $(command -v ollama)"
echo ""

echo "[5/9] Checking ROM file..."
ROM_FULL="$PROJECT_ROOT/$ROM_PATH"
if [[ ! -f "$ROM_FULL" ]]; then
  echo "      ERROR: ROM not found at $ROM_PATH"
  exit 1
fi
echo "      -> $ROM_PATH"
echo ""

echo "[6/9] Checking config..."
if [[ ! -f "$PROJECT_ROOT/config.json" ]]; then
  echo "      ERROR: config.json not found"
  exit 1
fi
echo "      -> config.json"
echo ""

echo "[7/9] Ensuring data directory and Lua script..."
mkdir -p "$PROJECT_ROOT/data"
if [[ ! -f "$PROJECT_ROOT/lua/game_agent.lua" ]]; then
  echo "      ERROR: lua/game_agent.lua not found"
  exit 1
fi
echo "      -> $PROJECT_ROOT/data"
echo "      -> lua/game_agent.lua"
echo ""

echo "[8/9] Ollama server..."
echo "      Please start the Ollama server (ollama serve) if not already running."
echo "      See docs/getting-started.md for details."
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
echo ""

echo "[9/9] Ready to launch."
echo ""

# ---------------------------------------------------------------------------
# Start mGBA (if requested)
# ---------------------------------------------------------------------------
if $START_MGBA; then
  LUA_SCRIPT="$PROJECT_ROOT/lua/game_agent.lua"
  echo "───────────────────────────────────────────────────────────────"
  echo "  Starting mGBA (background)"
  echo "───────────────────────────────────────────────────────────────"
  echo "  -> ROM: $ROM_FULL"
  echo "  -> Script: --script $LUA_SCRIPT (auto-loaded, mGBA 0.11+)"
  echo "  -> CWD: $PROJECT_ROOT (required for Lua data paths)"
  echo ""
  cd "$PROJECT_ROOT"
  "$MGBA_BIN" --script "$LUA_SCRIPT" "$ROM_FULL" &
  MGBA_PID=$!
  echo "  -> mGBA started (PID $MGBA_PID)"
  echo "  -> Waiting 3s for mGBA to initialize..."
  sleep 3
  echo ""
else
  echo "───────────────────────────────────────────────────────────────"
  echo "  Skipping mGBA (--no-mgba); ensure it is already running"
  echo "  with lua/game_agent.lua loaded (--script or Tools > Scripting)."
  echo "───────────────────────────────────────────────────────────────"
  echo ""
fi

# ---------------------------------------------------------------------------
# Start bridge
# ---------------------------------------------------------------------------
echo "───────────────────────────────────────────────────────────────"
echo "  Starting Bridge (foreground)"
echo "───────────────────────────────────────────────────────────────"
echo "  -> Venv: $VENV (already active)"
echo "  -> Running: python3 -m bridge $BRIDGE_QUIET"
echo "  -> Bridge writes lua/data_dir.txt so Lua finds the data folder"
echo ""
echo "  Press Ctrl+C to stop the bridge (mGBA will also close)."
echo "───────────────────────────────────────────────────────────────"
echo ""

python3 -m bridge $BRIDGE_QUIET
