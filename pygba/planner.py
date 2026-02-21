"""
Hierarchical planner with three layers:

  Strategic -- called every N turns or on badge gain. Uses a separate LLM call
               to set the current high-level goal (e.g. "Beat Brock").

  Tactical  -- when the action plan queue is empty, calls the LLM for a new
               multi-action sequence toward the current goal. Navigator provides
               path hints for overworld navigation.

  Reactive  -- on game-mode change (e.g. entering battle), the current plan is
               interrupted and a mode-appropriate plan is requested immediately.
"""

import logging

from pygba.prompt import (
    build_messages, build_strategic_prompt,
    parse_plan_response, parse_strategic_response,
)
from pygba.navigator import (
    current_location_node, path_hint, find_nearest_pokecenter,
)

log = logging.getLogger(__name__)


class Planner:
    def __init__(self, config=None):
        cfg = config or {}
        self.strategic_interval = cfg.get("strategic_interval", 50)
        self.max_plan_length = cfg.get("max_plan_length", 20)
        self.battle_plan_length = cfg.get("battle_plan_length", 3)

        self.goal_stack = []
        self.current_plan = []
        self.turn_count = 0
        self.last_strategic_turn = 0
        self.last_badge_count = 0
        self.last_mode = None
        self.history = []

        self._last_narrative = ""

    @property
    def current_goal(self):
        return self.goal_stack[-1] if self.goal_stack else "Explore and progress"

    @property
    def has_plan(self):
        return len(self.current_plan) > 0

    @property
    def last_narrative(self):
        return self._last_narrative

    def needs_strategic_update(self, progress):
        """Check if we should re-evaluate the strategic goal."""
        if not self.goal_stack:
            return True

        badge_count = progress.get("badge_count", 0)
        if badge_count > self.last_badge_count:
            return True

        if self.turn_count - self.last_strategic_turn >= self.strategic_interval:
            return True

        return False

    def update_strategy(self, progress, state, llm):
        """Call the LLM for a new strategic goal."""
        messages = build_strategic_prompt(progress, state)
        response = llm.chat(messages)
        goal, reasoning = parse_strategic_response(response)

        if goal:
            self.goal_stack.append(goal)
            log.info("Strategic goal: %s (reason: %s)", goal, reasoning)

        self.last_strategic_turn = self.turn_count
        self.last_badge_count = progress.get("badge_count", 0)
        return goal, reasoning

    def set_strategic_goal(self, goal):
        """Manually set a strategic goal."""
        self.goal_stack.append(goal)

    def interrupt(self, reason):
        """Clear the current plan due to a mode change or other interruption."""
        if self.current_plan:
            log.info("Plan interrupted: %s (had %d actions left)",
                     reason, len(self.current_plan))
        self.current_plan = []

    def get_or_create_plan(self, state, progress, llm, on_token=None):
        """Get the next action, creating a new plan via LLM if needed.

        Returns (action, narrative, was_new_plan).
        """
        self.turn_count += 1
        mode = state.get("game_mode", "overworld")

        # Reactive: interrupt on mode change
        if self.last_mode is not None and mode != self.last_mode:
            self.interrupt(f"mode changed: {self.last_mode} -> {mode}")
        self.last_mode = mode

        # Return next action from existing plan
        if self.current_plan:
            action = self.current_plan.pop(0)
            self._record_history(action, self._last_narrative, mode)
            return action, self._last_narrative, False

        # Need a new plan -- build navigation hint
        nav_hint = None
        if mode == "overworld":
            map_bank = state.get("map_bank", 0)
            map_number = state.get("map_number", 0)
            loc = current_location_node(map_bank, map_number)
            nav_hint = self._compute_nav_hint(loc, state, progress)

        # Build warnings from history
        warnings = self._get_warnings()

        messages, allowed_actions, max_plan = build_messages(
            state,
            history=self.history,
            warnings=warnings,
            progress=progress,
            nav_hint=nav_hint,
        )

        # Call LLM with streaming
        response = llm.chat_stream(messages, on_token=on_token)

        narrative, plan = parse_plan_response(response, allowed_actions, max_plan)
        self._last_narrative = narrative

        if plan:
            action = plan[0]
            self.current_plan = plan[1:]
        else:
            action = "wait"
            self.current_plan = []

        self._record_history(action, narrative, mode)
        return action, narrative, True

    def _compute_nav_hint(self, loc, state, progress):
        """Compute a navigation hint based on the current goal and location."""
        if loc is None:
            return None

        # Try to parse a destination from the goal
        goal = self.current_goal.lower()

        from pygba import navigator as nav
        target_map = {
            "brock": nav.PEWTER_GYM, "pewter": nav.PEWTER_CITY,
            "misty": nav.CERULEAN_GYM, "cerulean": nav.CERULEAN_CITY,
            "surge": nav.VERMILION_GYM, "vermilion": nav.VERMILION_CITY,
            "erika": nav.CELADON_GYM, "celadon": nav.CELADON_CITY,
            "koga": nav.FUCHSIA_GYM, "fuchsia": nav.FUCHSIA_CITY,
            "sabrina": nav.SAFFRON_GYM, "saffron": nav.SAFFRON_CITY,
            "blaine": nav.CINNABAR_GYM, "cinnabar": nav.CINNABAR_ISLAND,
            "giovanni": nav.VIRIDIAN_GYM, "viridian gym": nav.VIRIDIAN_GYM,
            "elite four": nav.INDIGO_PLATEAU, "indigo": nav.INDIGO_PLATEAU,
            "mt. moon": nav.MT_MOON_1F, "mt moon": nav.MT_MOON_1F,
            "rock tunnel": nav.ROCK_TUNNEL_1F,
            "pokemon tower": nav.POKEMON_TOWER,
            "silph": nav.SILPH_CO,
            "victory road": nav.VICTORY_ROAD_1F,
        }

        for keyword, target in target_map.items():
            if keyword in goal:
                hint = path_hint(loc, target)
                if hint:
                    return hint

        # If goal mentions healing, navigate to nearest pokecenter
        if any(w in goal for w in ("heal", "center", "rest")):
            city, _ = find_nearest_pokecenter(loc)
            if city:
                hint = path_hint(loc, city)
                if hint:
                    return hint

        return None

    def _record_history(self, action, narrative, mode):
        self.history.append({
            "action": action,
            "narrative": narrative,
            "game_mode": mode,
        })
        if len(self.history) > 20:
            self.history = self.history[-20:]

    def _get_warnings(self):
        """Generate anti-loop warnings from recent history."""
        warnings = []
        if len(self.history) >= 5:
            recent_actions = [h["action"] for h in self.history[-5:]]
            if len(set(recent_actions)) == 1:
                warnings.append(
                    "WARNING: You have repeated the same action 5 times. "
                    "Try something completely different."
                )
        return warnings

    def plan_summary(self):
        """Short summary of the current plan for display."""
        if not self.current_plan:
            return "(no plan)"
        actions = self.current_plan[:5]
        s = ", ".join(actions)
        remaining = len(self.current_plan)
        if remaining > 5:
            s += f" ... (+{remaining - 5} more)"
        return f"{s} ({remaining} actions)"
