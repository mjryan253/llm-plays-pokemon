"""
Lateral Red (LR-1) -- Main Bridge Loop

Polls state.json from the Lua agent, sends the game state to a local LLM,
parses the response, and writes a button-sequence command back.
"""

import argparse
import json
import logging
import os
import sys
import time
from collections import deque
from pathlib import Path

from bridge.llm_client import LLMClient
from bridge.prompt import build_messages, get_actions_for_mode, parse_response
from bridge.pokemon_data import enrich_state, map_name

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("lateral-red")

# -----------------------------------------------------------------------
# Terminal colors (ANSI, works on every modern terminal)
# -----------------------------------------------------------------------
class C:
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    CYAN    = "\033[36m"
    YELLOW  = "\033[33m"
    GREEN   = "\033[32m"
    RED     = "\033[31m"
    MAGENTA = "\033[35m"
    RESET   = "\033[0m"

MODE_COLORS = {
    "overworld": C.GREEN,
    "dialog":    C.CYAN,
    "battle":    C.RED,
    "menu":      C.YELLOW,
}

def _separator(char="─", width=70):
    return C.DIM + char * width + C.RESET

def _print_turn_header(turn, mode, state):
    color = MODE_COLORS.get(mode, C.RESET)
    loc = map_name(state.get("map_bank", 0), state.get("map_number", 0))
    x, y = state.get("player_x", "?"), state.get("player_y", "?")
    print()
    print(_separator("═"))
    print(f"{C.BOLD}  TURN {turn}{C.RESET}  "
          f"{color}{C.BOLD}{mode.upper()}{C.RESET}  "
          f"{C.DIM}|{C.RESET}  {loc}  ({x}, {y})")
    print(_separator("─"))

# -----------------------------------------------------------------------
# GBA key bitmask values (bit positions from C.GBA_KEY)
# -----------------------------------------------------------------------
KEY = {
    "A": 1, "B": 2, "SELECT": 4, "START": 8,
    "RIGHT": 16, "LEFT": 32, "UP": 64, "DOWN": 128,
    "R": 256, "L": 512,
}

# -----------------------------------------------------------------------
# High-level action -> button sequence mapping
# Each step: {"keys": <bitmask>, "frames": <hold duration>}
# A zero-keys step is a gap (release all buttons briefly).
# -----------------------------------------------------------------------
ACTION_SEQUENCES = {
    # Overworld movement
    "move_up":    [{"keys": KEY["UP"],    "frames": 16}],
    "move_down":  [{"keys": KEY["DOWN"],  "frames": 16}],
    "move_left":  [{"keys": KEY["LEFT"],  "frames": 16}],
    "move_right": [{"keys": KEY["RIGHT"], "frames": 16}],
    "interact":   [{"keys": KEY["A"], "frames": 8}],
    "open_menu":  [{"keys": KEY["START"], "frames": 8}],
    "wait":       [{"keys": 0, "frames": 30}],

    # Dialog
    "continue":   [{"keys": KEY["A"], "frames": 8}],
    "choose_yes": [
        {"keys": KEY["UP"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["A"],  "frames": 8},
    ],
    "choose_no": [
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["A"],    "frames": 8},
    ],

    # Battle -- FIGHT menu (cursor starts at move 1 = top-left)
    # Layout:  Move1  Move2
    #          Move3  Move4
    "fight_move_1": [
        {"keys": KEY["A"], "frames": 6}, {"keys": 0, "frames": 6},
        {"keys": KEY["A"], "frames": 6},
    ],
    "fight_move_2": [
        {"keys": KEY["A"],     "frames": 6}, {"keys": 0, "frames": 6},
        {"keys": KEY["RIGHT"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["A"],     "frames": 6},
    ],
    "fight_move_3": [
        {"keys": KEY["A"],    "frames": 6}, {"keys": 0, "frames": 6},
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["A"],    "frames": 6},
    ],
    "fight_move_4": [
        {"keys": KEY["A"],     "frames": 6}, {"keys": 0, "frames": 6},
        {"keys": KEY["DOWN"],  "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["RIGHT"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["A"],     "frames": 6},
    ],

    # Battle -- RUN (cursor: right to BAG column, down to RUN, press A)
    "run": [
        {"keys": KEY["RIGHT"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["DOWN"],  "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["A"],     "frames": 6},
    ],

    # Battle -- use_item (select BAG: right from FIGHT)
    "use_item": [
        {"keys": KEY["RIGHT"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["A"],     "frames": 6},
    ],

    # Battle -- switch pokemon (select POKEMON: down from FIGHT)
    # Then navigate to the correct slot and press A
    "switch_2": [
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["A"],    "frames": 6}, {"keys": 0, "frames": 8},
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["A"],    "frames": 6},
    ],
    "switch_3": [
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["A"],    "frames": 6}, {"keys": 0, "frames": 8},
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["A"],    "frames": 6},
    ],
    "switch_4": [
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["A"],    "frames": 6}, {"keys": 0, "frames": 8},
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["A"],    "frames": 6},
    ],
    "switch_5": [
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["A"],    "frames": 6}, {"keys": 0, "frames": 8},
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["A"],    "frames": 6},
    ],
    "switch_6": [
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["A"],    "frames": 6}, {"keys": 0, "frames": 8},
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["A"],    "frames": 6},
    ],

    # START menu navigation
    # FireRed menu order: POKEDEX, POKEMON, BAG, <PLAYER>, SAVE, OPTION, EXIT
    "menu_pokemon": [
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["A"],    "frames": 8},
    ],
    "menu_bag": [
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["A"],    "frames": 8},
    ],
    "menu_save": [
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["DOWN"], "frames": 4}, {"keys": 0, "frames": 2},
        {"keys": KEY["A"],    "frames": 8},
    ],
    "menu_close": [
        {"keys": KEY["B"], "frames": 8},
    ],
}


# -----------------------------------------------------------------------
# File I/O
# -----------------------------------------------------------------------

def load_config(path="config.json"):
    with open(path) as f:
        return json.load(f)


def read_state(filepath):
    """Read state.json, return dict or None if unchanged/missing."""
    try:
        with open(filepath) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def write_command(filepath, steps):
    """Atomically write command.json."""
    tmp = filepath + ".tmp"
    with open(tmp, "w") as f:
        json.dump({"steps": steps}, f)
    os.replace(tmp, filepath)


# -----------------------------------------------------------------------
# Anti-loop / "Compass" detection
# -----------------------------------------------------------------------

class LoopDetector:
    def __init__(self, max_history=20):
        self.positions = deque(maxlen=max_history)
        self.actions = deque(maxlen=max_history)

    def record(self, state, action):
        pos = (
            state.get("player_x", 0),
            state.get("player_y", 0),
            state.get("map_bank", 0),
            state.get("map_number", 0),
        )
        self.positions.append(pos)
        self.actions.append(action)

    def get_warnings(self):
        warnings = []
        if len(self.positions) >= 5:
            recent = list(self.positions)[-5:]
            if len(set(recent)) == 1:
                warnings.append(
                    "WARNING: You have been at the same position for 5 turns. "
                    "Try a completely different direction or action."
                )
        if len(self.actions) >= 4:
            recent = list(self.actions)[-4:]
            if len(set(recent)) == 1:
                warnings.append(
                    "WARNING: You have repeated the same action 4 times. "
                    "Try something different."
                )
        return warnings


# -----------------------------------------------------------------------
# Main loop
# -----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Lateral Red (LR-1) -- Pokemon FireRed AI Bridge")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Minimal output: only show narrative + action per turn")
    args = parser.parse_args()
    verbose = not args.quiet

    config = load_config()
    data_dir = config.get("data_dir", "data")
    project_root = os.getcwd()
    data_dir_abs = os.path.abspath(data_dir)
    state_path = os.path.join(data_dir_abs, "state.json")
    cmd_path = os.path.join(data_dir_abs, "command.json")
    poll_interval = config.get("state_poll_interval_seconds", 0.5)
    max_history = config.get("history_length", 10)

    os.makedirs(data_dir_abs, exist_ok=True)

    # So mGBA's Lua script can find the same data dir (when mGBA is run from project root)
    lua_data_dir_file = os.path.join(project_root, "lua", "data_dir.txt")
    try:
        with open(lua_data_dir_file, "w") as f:
            f.write(data_dir_abs + "\n")
    except OSError:
        pass

    llm = LLMClient(config.get("llm", {}))

    # Startup banner
    print()
    print(f"{C.BOLD}{C.CYAN}  LATERAL RED (LR-1){C.RESET}")
    print(f"  Autonomous Pokemon FireRed Agent")
    print(_separator("─"))
    print(f"  Backend : {C.BOLD}{llm.backend}{C.RESET} @ {llm.base_url}")
    print(f"  Model   : {C.BOLD}{llm.model or '(server default)'}{C.RESET}")
    print(f"  Verbose : {'ON' if verbose else 'OFF'} {C.DIM}(use --quiet to hide prompts){C.RESET}")
    print(_separator("─"))

    sys.stdout.write(f"  Checking LLM backend... ")
    sys.stdout.flush()
    if llm.health_check():
        print(f"{C.GREEN}connected{C.RESET}")
    else:
        print(f"{C.YELLOW}not reachable (will retry){C.RESET}")

    print(f"  Waiting for state.json from mGBA...")
    print(_separator("═"))

    history = deque(maxlen=max_history)
    loop_detector = LoopDetector()
    last_mtime = 0
    turn = 0

    while True:
        # Poll for new state
        try:
            mtime = os.path.getmtime(state_path)
        except OSError:
            time.sleep(poll_interval)
            continue

        if mtime <= last_mtime:
            time.sleep(poll_interval)
            continue
        last_mtime = mtime

        state = read_state(state_path)
        if not state:
            time.sleep(poll_interval)
            continue

        turn += 1
        mode = state.get("game_mode", "overworld")
        enriched = enrich_state(state)

        # Build warnings
        warnings = loop_detector.get_warnings()

        # Build prompt and get allowed actions
        messages, allowed_actions = build_messages(state, list(history), warnings)

        # Print turn header
        _print_turn_header(turn, mode, enriched)

        # Show what the LLM sees
        if verbose:
            print(f"{C.DIM}  GAME STATE SENT TO LLM:{C.RESET}")
            for line in messages[-1]["content"].split("\n"):
                print(f"  {C.DIM}│{C.RESET} {line}")
            print(_separator("─"))

        # Show anti-loop warnings
        for w in warnings:
            print(f"  {C.YELLOW}{C.BOLD}⚠ {w}{C.RESET}")

        # Call LLM
        sys.stdout.write(f"  {C.DIM}Thinking...{C.RESET}")
        sys.stdout.flush()
        t0 = time.time()
        response_text = llm.chat(messages)
        elapsed = time.time() - t0
        print(f"\r  {C.DIM}Responded in {elapsed:.1f}s{C.RESET}                ")

        if not response_text:
            print(f"  {C.RED}(empty response, using safe default){C.RESET}")
            response_text = '{"narrative": "No response", "action": "wait"}'

        # Show raw LLM output
        if verbose:
            print(f"{C.DIM}  RAW LLM RESPONSE:{C.RESET}")
            for line in response_text.strip().split("\n"):
                print(f"  {C.DIM}│{C.RESET} {line}")
            print(_separator("─"))

        # Parse response
        narrative, action = parse_response(response_text, allowed_actions)

        # The main event: show the AI's thinking and decision
        color = MODE_COLORS.get(mode, C.RESET)
        print(f"  {C.MAGENTA}{C.BOLD}THINKING:{C.RESET} {narrative}")
        print(f"  {color}{C.BOLD}ACTION:{C.RESET}   {C.BOLD}{action}{C.RESET}")

        # Record for anti-loop
        loop_detector.record(state, action)
        history.append({
            "action": action,
            "narrative": narrative,
            "game_mode": mode,
        })

        # Translate to button sequence and write command
        seq = ACTION_SEQUENCES.get(action)
        if seq:
            write_command(cmd_path, seq)
        else:
            print(f"  {C.RED}No button mapping for '{action}', skipping{C.RESET}")

        # Brief pause before next poll to let the command execute
        time.sleep(poll_interval)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.info("Shutting down")
        sys.exit(0)
