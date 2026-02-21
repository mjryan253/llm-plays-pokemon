"""
Multi-action prompt builder and response parser for Pokemon FireRed.

Key differences from the legacy bridge/prompt.py:
  - Requests multi-action plans (up to 10-20 in overworld, 1-3 in battle/dialog)
  - Includes progress context (badges, money, party composition)
  - Includes navigation hints when the navigator has computed a path
  - Uses a compressed single-line party format
"""

import json
import re

from pygba.actions import get_actions_for_mode

SYSTEM_PROMPT = """\
You are an autonomous AI playing Pokemon FireRed. Your goal is to beat the Elite Four.

RULES:
- You receive the current game state each turn.
- You MUST respond with valid JSON: {"narrative": "<your thoughts>", "plan": ["action1", "action2", ...]}
- Pick actions ONLY from the provided list.
- The narrative should be 1-3 sentences about what you observe and why you chose these actions.
- Think strategically: progress the story, heal when needed, use type advantages in battle.
- In dialog, always advance the conversation unless you need to choose YES or NO.
- In battle, consider your Pokemon's HP, PP, and type matchups before attacking.
- If you seem stuck, try a completely different approach."""


def _format_pokemon_compact(pkmn):
    """Compressed single-line format: Charizard L36 HP:102/115 [Ember/Slash/DragonRage/Fly]"""
    name = pkmn.get("species_name", pkmn.get("nickname", "???"))
    lv = pkmn.get("level", 0)
    hp = pkmn.get("hp", 0)
    mhp = pkmn.get("max_hp", 0)
    status = pkmn.get("status_text", "OK")

    moves = []
    for md in pkmn.get("move_details", []):
        moves.append(md["name"])
    move_str = "/".join(moves) if moves else "---"

    s = f"{name} L{lv} HP:{hp}/{mhp} [{move_str}]"
    if status != "OK":
        s += f" {{{status}}}"
    return s


def _format_pokemon_battle(pkmn):
    """Detailed view for battle including move PP and types."""
    lines = [_format_pokemon_compact(pkmn)]
    lines.append(f"  ATK:{pkmn.get('attack',0)} DEF:{pkmn.get('defense',0)} "
                 f"SPD:{pkmn.get('speed',0)} SpA:{pkmn.get('sp_attack',0)} "
                 f"SpD:{pkmn.get('sp_defense',0)}")
    for md in pkmn.get("move_details", []):
        lines.append(f"  Move {md['slot']}: {md['name']} ({md['type']}) PP:{md['pp']}")
    return "\n".join(lines)


def _format_badges(badges):
    """Format badge display: [X][X][ ][ ][ ][ ][ ][ ]"""
    if not badges:
        return "[ ]" * 8
    names = ["boulder", "cascade", "thunder", "rainbow",
             "soul", "marsh", "volcano", "earth"]
    return "".join("[X]" if badges.get(n) else "[ ]" for n in names)


def _progress_block(progress):
    """Build a progress context block for strategic prompts."""
    if not progress:
        return ""
    lines = []
    badge_str = _format_badges(progress.get("badges"))
    lines.append(f"Badges: {badge_str} ({progress.get('badge_count', 0)}/8)")
    lines.append(f"Money: ${progress.get('money', 0)}")
    name = progress.get("player_name", "???")
    lines.append(f"Player: {name}")
    levels = progress.get("party_levels", [])
    if levels:
        lines.append(f"Party levels: {', '.join(str(l) for l in levels)}")
    return "\n".join(lines)


# ── Mode-specific prompt builders ──────────────────────────────────

def _overworld_prompt(state, actions, extra):
    plan_len = 10
    lines = [
        f"MODE: Overworld",
        f"Position: ({state.get('player_x', '?')}, {state.get('player_y', '?')}) on {state.get('map_name', '???')}",
        "",
        "PARTY:",
    ]
    for p in state.get("party", []):
        lines.append(f"  {_format_pokemon_compact(p)}")
    lines.append("")
    lines.extend(extra)
    lines.append(f"Plan up to {plan_len} actions.")
    lines.append("AVAILABLE ACTIONS: " + ", ".join(actions))
    return "\n".join(lines), plan_len


def _dialog_prompt(state, actions, extra):
    plan_len = 3
    text = state.get("text_on_screen", "")
    lines = [
        f"MODE: Dialog",
        f'Text on screen: "{text}"',
        "",
    ]
    lines.extend(extra)
    lines.append(f"Plan up to {plan_len} actions.")
    lines.append("AVAILABLE ACTIONS: " + ", ".join(actions))
    return "\n".join(lines), plan_len


def _battle_prompt(state, actions, extra):
    plan_len = 3
    party = state.get("party", [])
    enemy = state.get("enemy", [])
    lines = ["MODE: Battle", ""]

    if party:
        lines.append("YOUR ACTIVE POKEMON:")
        lines.append(_format_pokemon_battle(party[0]))
        lines.append("")
    if enemy:
        lines.append("ENEMY POKEMON:")
        lines.append(_format_pokemon_battle(enemy[0]))
        lines.append("")
    if len(party) > 1:
        lines.append("REST OF YOUR PARTY:")
        for i, p in enumerate(party[1:], start=2):
            lines.append(f"  Slot {i}: {_format_pokemon_compact(p)}")
        lines.append("")

    text = state.get("text_on_screen", "")
    if text:
        lines.append(f'Text on screen: "{text}"')
        lines.append("")

    lines.extend(extra)
    lines.append(f"Plan up to {plan_len} actions.")
    lines.append("AVAILABLE ACTIONS: " + ", ".join(actions))
    return "\n".join(lines), plan_len


def _menu_prompt(state, actions, extra):
    plan_len = 5
    lines = [
        f"MODE: Start Menu",
        f"Position: ({state.get('player_x', '?')}, {state.get('player_y', '?')}) on {state.get('map_name', '???')}",
        "",
        "PARTY:",
    ]
    for p in state.get("party", []):
        lines.append(f"  {_format_pokemon_compact(p)}")
    lines.append("")
    lines.extend(extra)
    lines.append(f"Plan up to {plan_len} actions.")
    lines.append("AVAILABLE ACTIONS: " + ", ".join(actions))
    return "\n".join(lines), plan_len


_MODE_BUILDERS = {
    "overworld": _overworld_prompt,
    "dialog": _dialog_prompt,
    "battle": _battle_prompt,
    "menu": _menu_prompt,
}


# ── Public API ──────────────────────────────────────────────────────

def build_messages(state, history=None, warnings=None, progress=None, nav_hint=None):
    """Build the full message list for the LLM.

    Returns (messages, allowed_actions, max_plan_length).
    """
    mode = state.get("game_mode", "overworld")
    actions = get_actions_for_mode(mode, state)

    extra = []
    if progress:
        extra.append(_progress_block(progress))
        extra.append("")
    if nav_hint:
        extra.append(f"NAVIGATION: {nav_hint}")
        extra.append("")
    if warnings:
        extra.extend(warnings)

    builder = _MODE_BUILDERS.get(mode, _overworld_prompt)
    user_content, plan_len = builder(state, actions, extra)

    if history:
        recent = history[-5:]
        history_lines = ["RECENT HISTORY (oldest first):"]
        for h in recent:
            act = h.get("action", "?")
            narr = h.get("narrative", "")[:80]
            history_lines.append(f"  Action: {act} -> {narr}")
        user_content = "\n".join(history_lines) + "\n\n" + user_content

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]
    return messages, actions, plan_len


def build_strategic_prompt(progress, state):
    """Build a big-picture strategic prompt for the planner.

    Returns messages list for a strategic LLM call.
    """
    system = (
        "You are a strategic advisor for an AI playing Pokemon FireRed. "
        "Given the current progress, decide the next major goal. "
        'Respond with JSON: {"goal": "<goal description>", "reasoning": "<why>"}'
    )

    lines = ["CURRENT PROGRESS:"]
    lines.append(_progress_block(progress))
    lines.append("")
    lines.append(f"Current location: {state.get('map_name', '???')}")
    lines.append(f"Party:")
    for p in state.get("party", []):
        lines.append(f"  {_format_pokemon_compact(p)}")
    lines.append("")
    lines.append("What should the next major goal be? Consider:")
    lines.append("- Which gym to challenge next")
    lines.append("- Whether the party needs leveling")
    lines.append("- Story progression requirements")
    lines.append("- Healing / item needs")

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": "\n".join(lines)},
    ]


# ── Response parsing ────────────────────────────────────────────────

def parse_plan_response(text, allowed_actions, max_plan_length):
    """Parse a multi-action plan response.

    Returns (narrative, plan_list) where plan_list contains valid actions.
    """
    narrative = ""
    plan = []

    # Try direct JSON parse
    try:
        data = json.loads(text.strip())
        narrative = data.get("narrative", "")
        raw_plan = data.get("plan", [])
        if isinstance(raw_plan, str):
            raw_plan = [raw_plan]
        plan = raw_plan
    except (json.JSONDecodeError, AttributeError):
        pass

    # Fallback: extract JSON from markdown fences or embedded braces
    if not plan:
        patterns = [
            r"```(?:json)?\s*(\{.*?\})\s*```",
            r'(\{[^{}]*"plan"[^{}]*\})',
            r'(\{[^{}]*"action"[^{}]*\})',
        ]
        for pat in patterns:
            m = re.search(pat, text, re.DOTALL)
            if m:
                try:
                    data = json.loads(m.group(1))
                    narrative = narrative or data.get("narrative", "")
                    raw = data.get("plan", data.get("action", []))
                    if isinstance(raw, str):
                        raw = [raw]
                    if raw:
                        plan = raw
                        break
                except (json.JSONDecodeError, AttributeError):
                    continue

    # Validate each action
    valid_plan = []
    for action in plan:
        if not isinstance(action, str):
            continue
        action_clean = action.lower().strip()
        if action_clean in allowed_actions:
            valid_plan.append(action_clean)
        else:
            for a in allowed_actions:
                if a == action_clean:
                    valid_plan.append(a)
                    break

    valid_plan = valid_plan[:max_plan_length]

    # Fallback: if empty plan, pick a safe default
    if not valid_plan:
        if "continue" in allowed_actions:
            valid_plan = ["continue"]
        elif "wait" in allowed_actions:
            valid_plan = ["wait"]
        elif allowed_actions:
            valid_plan = [allowed_actions[0]]

    if not narrative:
        narrative = "(no narrative)"

    return narrative, valid_plan


def parse_strategic_response(text):
    """Parse the strategic planner's goal response.

    Returns (goal, reasoning).
    """
    try:
        data = json.loads(text.strip())
        return data.get("goal", ""), data.get("reasoning", "")
    except (json.JSONDecodeError, AttributeError):
        pass

    # Regex fallback
    m = re.search(r'"goal"\s*:\s*"([^"]*)"', text)
    goal = m.group(1) if m else text[:100].strip()
    m2 = re.search(r'"reasoning"\s*:\s*"([^"]*)"', text)
    reasoning = m2.group(1) if m2 else ""
    return goal, reasoning
