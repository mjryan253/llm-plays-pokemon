#!/bin/bash
# Lateral Red (LR-1) -- Orchestrated startup
# Launches mGBA and the Python bridge with verbose pre-flight checks.

set -e

# ---------------------------------------------------------------------------
# Configuration (override with environment variables)
# ---------------------------------------------------------------------------
VENV="${LATERAL_RED_VENV:-$HOME/GitHub/venv1}"
ROM_PATH="gamefile/Pokemon_ FireRed Version.zip"

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR" && pwd)"

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
      echo "  LATERAL_RED_VENV   Venv path (default: \$HOME/GitHub/venv1)"
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
echo "[1/6] Resolving project root..."
echo "      -> $PROJECT_ROOT"
cd "$PROJECT_ROOT"
echo ""

echo "[2/6] Checking virtual environment..."
if [[ ! -f "$VENV/bin/python" ]]; then
  echo "      ERROR: venv not found at $VENV"
  echo "      Install deps: $VENV/bin/pip install -r requirements.txt"
  exit 1
fi
echo "      -> $VENV"
echo "      -> Python: $($VENV/bin/python --version 2>&1)"
echo ""

echo "[3/6] Checking ROM file..."
ROM_FULL="$PROJECT_ROOT/$ROM_PATH"
if [[ ! -f "$ROM_FULL" ]]; then
  echo "      ERROR: ROM not found at $ROM_PATH"
  exit 1
fi
echo "      -> $ROM_PATH"
echo ""

echo "[4/6] Checking mGBA..."
if ! command -v mgba-qt &>/dev/null; then
  echo "      ERROR: mgba-qt not found in PATH"
  echo "      Install: sudo apt install mgba-qt"
  exit 1
fi
MGBA_BIN="$(command -v mgba-qt)"
echo "      -> $MGBA_BIN"
echo ""

echo "[5/6] Checking config..."
if [[ ! -f "$PROJECT_ROOT/config.json" ]]; then
  echo "      ERROR: config.json not found"
  exit 1
fi
echo "      -> config.json"
echo ""

echo "[6/6] Ensuring data directory and Lua script..."
mkdir -p "$PROJECT_ROOT/data"
if [[ ! -f "$PROJECT_ROOT/lua/game_agent.lua" ]]; then
  echo "      ERROR: lua/game_agent.lua not found"
  exit 1
fi
echo "      -> $PROJECT_ROOT/data"
echo "      -> lua/game_agent.lua"
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
echo "  -> Activating venv: $VENV"
source "$VENV/bin/activate"
echo "  -> Running: python3 -m bridge $BRIDGE_QUIET"
echo "  -> Bridge writes lua/data_dir.txt so Lua finds the data folder"
echo ""
echo "  Press Ctrl+C to stop the bridge (mGBA will also close)."
echo "───────────────────────────────────────────────────────────────"
echo ""

python3 -m bridge $BRIDGE_QUIET
