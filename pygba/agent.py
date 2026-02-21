"""
Main agent loop with streaming terminal display.

Core loop (no file I/O, no polling -- direct memory access):
  1. Advance emulator by N frames
  2. Read RAM for full game state
  3. Ask the planner for the next action (may trigger LLM call with streaming)
  4. Execute the action by pressing GBA buttons
"""

import logging
import sys
import time

from pygba.actions import ACTION_SEQUENCES
from pygba.game_state import collect_state, game_progress
from pygba.llm_client import StreamingLLMClient
from pygba.planner import Planner
from pygba.pokemon_data import map_name

log = logging.getLogger(__name__)

FRAMES_PER_TICK = 30


# ── Terminal display ────────────────────────────────────────────────

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


def _sep(char="─", width=65):
    return C.DIM + char * width + C.RESET


def _format_badges(badges):
    if not badges:
        return "[ ]" * 8
    names = ["boulder", "cascade", "thunder", "rainbow",
             "soul", "marsh", "volcano", "earth"]
    return "".join("[X]" if badges.get(n) else "[ ]" for n in names)


def _print_header(turn, mode, state, progress, goal):
    color = MODE_COLORS.get(mode, C.RESET)
    loc = state.get("map_name", "???")
    x, y = state.get("player_x", "?"), state.get("player_y", "?")
    badges = _format_badges(progress.get("badges"))
    money = progress.get("money", 0)

    print()
    print(_sep("═"))
    print(f"  {C.BOLD}TURN {turn}{C.RESET}  "
          f"{color}{C.BOLD}{mode.upper()}{C.RESET}  "
          f"{C.DIM}|{C.RESET}  {loc}  ({x}, {y})")
    print(f"  Badges: {badges}   Money: ${money}")
    print(f"  {C.DIM}Goal: {goal}{C.RESET}")
    print(_sep())


def _print_thinking_start():
    sys.stdout.write(f"  {C.MAGENTA}{C.BOLD}THINKING:{C.RESET}\n")
    sys.stdout.write(f"  {C.DIM}│{C.RESET} ")
    sys.stdout.flush()


def _on_token(token):
    """Streaming callback -- writes LLM tokens live to the terminal."""
    for ch in token:
        if ch == "\n":
            sys.stdout.write(f"\n  {C.DIM}│{C.RESET} ")
        else:
            sys.stdout.write(ch)
    sys.stdout.flush()


def _print_plan(action, plan_summary, mode):
    color = MODE_COLORS.get(mode, C.RESET)
    print()
    print(_sep())
    print(f"  {C.DIM}PLAN: {plan_summary}{C.RESET}")
    print(f"  {color}{C.BOLD}EXECUTING:{C.RESET} {C.BOLD}{action}{C.RESET}")
    print(_sep("═"))


# ── Action execution ────────────────────────────────────────────────

def execute_action(emu, action_name):
    """Execute a named action by pressing the right GBA buttons."""
    seq = ACTION_SEQUENCES.get(action_name)
    if not seq:
        log.warning("No button mapping for '%s'", action_name)
        return

    for step in seq:
        keys = step.get("keys", 0)
        frames = step.get("frames", 8)
        emu.set_keys_raw(keys)
        emu.tick(frames)

    emu.release_keys()


# ── Agent ───────────────────────────────────────────────────────────

class Agent:
    def __init__(self, emu, config):
        self.emu = emu
        self.config = config
        self.llm = StreamingLLMClient(config.get("llm", {}))
        self.planner = Planner(config.get("planner", {}))
        self.turn = 0

    def run(self):
        """Main agent loop -- runs until interrupted."""
        self._print_banner()
        self._check_llm()

        while True:
            self.emu.tick(FRAMES_PER_TICK)
            self._step()

    def _step(self):
        self.turn += 1

        state = collect_state(self.emu)
        progress = game_progress(self.emu)
        mode = state.get("game_mode", "overworld")

        # Strategic re-evaluation
        if self.planner.needs_strategic_update(progress):
            goal, reason = self.planner.update_strategy(
                progress, state, self.llm
            )

        _print_header(
            self.turn, mode, state, progress,
            self.planner.current_goal,
        )

        # Get next action (may call LLM with streaming)
        _print_thinking_start()

        action, narrative, was_new_plan = self.planner.get_or_create_plan(
            state, progress, self.llm,
            on_token=_on_token if not self.planner.has_plan else None,
        )

        if not was_new_plan:
            sys.stdout.write(f"{C.DIM}(executing queued plan){C.RESET}")

        plan_summary = self.planner.plan_summary()
        _print_plan(action, plan_summary, mode)

        execute_action(self.emu, action)

    def _print_banner(self):
        print()
        print(f"{C.BOLD}{C.CYAN}  LLM PLAYS POKEMON -- PyGBA{C.RESET}")
        print(f"  Pure Python agent via mGBA bindings")
        print(_sep())
        print(f"  Backend : {C.BOLD}{self.llm.backend}{C.RESET} @ {self.llm.base_url}")
        print(f"  Model   : {C.BOLD}{self.llm.model or '(server default)'}{C.RESET}")
        print(f"  ROM     : {C.BOLD}{self.config.get('rom_path', '???')}{C.RESET}")
        print(_sep())

    def _check_llm(self):
        sys.stdout.write(f"  Checking LLM backend... ")
        sys.stdout.flush()
        if self.llm.health_check():
            print(f"{C.GREEN}connected{C.RESET}")
        else:
            print(f"{C.YELLOW}not reachable (will retry){C.RESET}")
        print(_sep("═"))
