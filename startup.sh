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
while [[ $# -gt 0 ]]; do
  case $1 in
    --no-mgba)
      START_MGBA=false
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
      echo "  -q, --quiet  Run bridge with --quiet (minimal output)"
      echo "  -h, --help   Show this help"
      echo ""
      echo "Environment:"
      echo "  LATERAL_RED_VENV   Venv path (default: \$HOME/GitHub/venv1)"
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

echo "[6/6] Ensuring data directory..."
mkdir -p "$PROJECT_ROOT/data"
echo "      -> $PROJECT_ROOT/data"
echo ""

# ---------------------------------------------------------------------------
# Start mGBA (if requested)
# ---------------------------------------------------------------------------
if $START_MGBA; then
  echo "───────────────────────────────────────────────────────────────"
  echo "  Starting mGBA (background)"
  echo "───────────────────────────────────────────────────────────────"
  echo "  -> ROM: $ROM_FULL"
  echo "  -> CWD: $PROJECT_ROOT (required for Lua script paths)"
  echo ""
  echo "  MANUAL STEP: In mGBA, load the game agent:"
  echo "    Tools > Scripting > File > Load Script > lua/game_agent.lua"
  echo ""
  cd "$PROJECT_ROOT"
  "$MGBA_BIN" "$ROM_FULL" &
  MGBA_PID=$!
  echo "  -> mGBA started (PID $MGBA_PID)"
  echo "  -> Waiting 3s for mGBA to initialize..."
  sleep 3
  echo ""
else
  echo "───────────────────────────────────────────────────────────────"
  echo "  Skipping mGBA (--no-mgba); ensure it is already running"
  echo "  and that the Lua script is loaded from project root."
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
