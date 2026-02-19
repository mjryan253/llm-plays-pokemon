"""
Mode-aware prompt builder and response parser for Pokemon FireRed.
Builds system + user messages based on the current game mode, and parses
the LLM's JSON response into (narrative, action).
"""

import json
import re

from bridge.pokemon_data import enrich_state

SYSTEM_PROMPT = """\
You are an autonomous AI playing Pokemon FireRed. Your goal is to beat the Elite Four.

RULES:
- You receive the current game state each turn.
- You MUST respond with valid JSON: {"narrative": "<your thoughts>", "action": "<action_name>"}
- Pick exactly ONE action from the list provided.
- The narrative should be 1-3 sentences about what you observe and why you chose this action.
- Think strategically: progress the story, heal when needed, use type advantages in battle.
- In dialog, always advance the conversation unless you need to choose YES or NO.
- In battle, consider your Pokemon's HP, PP, and type matchups before attacking.
- If you seem stuck, try a different direction or approach."""


def _format_pokemon_brief(pkmn):
    """One-line party summary: 'Charizard Lv36 HP:102/115'"""
    name = pkmn.get("species_name", pkmn.get("nickname", "???"))
    lv = pkmn.get("level", 0)
    hp = pkmn.get("hp", 0)
    mhp = pkmn.get("max_hp", 0)
    status = pkmn.get("status_text", "OK")
    s = f"{name} Lv{lv} HP:{hp}/{mhp}"
    if status != "OK":
        s += f" [{status}]"
    return s


def _format_pokemon_battle(pkmn, slot_index):
    """Detailed view for the active battler including moves."""
    lines = [_format_pokemon_brief(pkmn)]
    item = pkmn.get("held_item_name", "None")
    if item and item != "None":
        lines.append(f"  Held: {item}")
    lines.append(f"  ATK:{pkmn.get('attack',0)} DEF:{pkmn.get('defense',0)} "
                 f"SPD:{pkmn.get('speed',0)} SpA:{pkmn.get('sp_attack',0)} "
                 f"SpD:{pkmn.get('sp_defense',0)}")
    for md in pkmn.get("move_details", []):
        lines.append(f"  Move {md['slot']}: {md['name']} ({md['type']}) PP:{md['pp']}")
    return "\n".join(lines)


def _overworld_prompt(state, actions, extra_warnings):
    """Build user prompt for overworld mode."""
    lines = [
        f"MODE: Overworld",
        f"Position: ({state['player_x']}, {state['player_y']}) on {state.get('map_name', '???')}",
        f"Moving: {state.get('is_moving', False)}",
        "",
        "PARTY:",
    ]
    for p in state.get("party", []):
        lines.append(f"  {_format_pokemon_brief(p)}")
    lines.append("")
    lines.extend(extra_warnings)
    lines.append("AVAILABLE ACTIONS: " + ", ".join(actions))
    return "\n".join(lines)


def _dialog_prompt(state, actions, extra_warnings):
    """Build user prompt for dialog mode."""
    text = state.get("text_on_screen", "")
    lines = [
        f"MODE: Dialog",
        f"Text on screen: \"{text}\"",
        "",
    ]
    lines.extend(extra_warnings)
    lines.append("AVAILABLE ACTIONS: " + ", ".join(actions))
    return "\n".join(lines)


def _battle_prompt(state, actions, extra_warnings):
    """Build user prompt for battle mode."""
    party = state.get("party", [])
    enemy = state.get("enemy", [])

    lines = ["MODE: Battle", ""]

    if party:
        lines.append("YOUR ACTIVE POKEMON:")
        lines.append(_format_pokemon_battle(party[0], 0))
        lines.append("")

    if enemy:
        lines.append("ENEMY POKEMON:")
        lines.append(_format_pokemon_battle(enemy[0], 0))
        lines.append("")

    if len(party) > 1:
        lines.append("REST OF YOUR PARTY:")
        for i, p in enumerate(party[1:], start=2):
            lines.append(f"  Slot {i}: {_format_pokemon_brief(p)}")
        lines.append("")

    text = state.get("text_on_screen", "")
    if text:
        lines.append(f"Text on screen: \"{text}\"")
        lines.append("")

    lines.extend(extra_warnings)
    lines.append("AVAILABLE ACTIONS: " + ", ".join(actions))
    return "\n".join(lines)


def _menu_prompt(state, actions, extra_warnings):
    """Build user prompt for the START menu."""
    lines = [
        f"MODE: Start Menu",
        f"Position: ({state['player_x']}, {state['player_y']}) on {state.get('map_name', '???')}",
        "",
        "PARTY:",
    ]
    for p in state.get("party", []):
        lines.append(f"  {_format_pokemon_brief(p)}")
    lines.append("")
    lines.extend(extra_warnings)
    lines.append("AVAILABLE ACTIONS: " + ", ".join(actions))
    return "\n".join(lines)


# -----------------------------------------------------------------------
# Actions available per mode
# -----------------------------------------------------------------------

OVERWORLD_ACTIONS = [
    "move_up", "move_down", "move_left", "move_right",
    "interact", "open_menu", "wait",
]

DIALOG_ACTIONS = [
    "continue", "choose_yes", "choose_no",
]

MENU_ACTIONS = [
    "menu_pokemon", "menu_bag", "menu_save", "menu_close",
]


def get_battle_actions(state):
    """
    Dynamic battle actions -- exclude moves with 0 PP, include switch slots
    only for alive party members beyond slot 1.
    """
    actions = []
    party = state.get("party", [])
    if party:
        active = party[0]
        for md in active.get("move_details", []):
            if md["pp"] > 0:
                actions.append(f"fight_move_{md['slot']}")
    if not actions:
        actions.append("fight_move_1")

    for i, p in enumerate(party[1:], start=2):
        if p.get("hp", 0) > 0:
            actions.append(f"switch_{i}")

    actions.append("use_item")
    actions.append("run")
    return actions


def get_actions_for_mode(mode, state):
    if mode == "battle":
        return get_battle_actions(state)
    elif mode == "dialog":
        return list(DIALOG_ACTIONS)
    elif mode == "menu":
        return list(MENU_ACTIONS)
    return list(OVERWORLD_ACTIONS)


# -----------------------------------------------------------------------
# Prompt assembly
# -----------------------------------------------------------------------

_MODE_BUILDERS = {
    "overworld": _overworld_prompt,
    "dialog": _dialog_prompt,
    "battle": _battle_prompt,
    "menu": _menu_prompt,
}


def build_messages(state_raw, history, warnings=None):
    """
    Build the full message list for the LLM.

    state_raw:  raw dict from state.json
    history:    list of recent {"state": ..., "action": ..., "narrative": ...}
    warnings:   list of extra warning strings (anti-loop, etc.)
    """
    state = enrich_state(state_raw)
    mode = state.get("game_mode", "overworld")
    actions = get_actions_for_mode(mode, state)

    extra = list(warnings or [])
    builder = _MODE_BUILDERS.get(mode, _overworld_prompt)
    user_content = builder(state, actions, extra)

    # Include recent history as context (compact)
    if history:
        recent = history[-5:]
        history_lines = ["RECENT HISTORY (oldest first):"]
        for h in recent:
            history_lines.append(f"  Action: {h.get('action','?')} -> {h.get('narrative','')[:80]}")
        user_content = "\n".join(history_lines) + "\n\n" + user_content

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]
    return messages, actions


# -----------------------------------------------------------------------
# Response parsing
# -----------------------------------------------------------------------

def parse_response(text, allowed_actions):
    """
    Parse the LLM's response. Returns (narrative, action).
    Tries JSON first, then regex fallback, then defaults.
    """
    narrative = ""
    action = ""

    # Try direct JSON parse
    try:
        data = json.loads(text.strip())
        narrative = data.get("narrative", "")
        action = data.get("action", "")
    except (json.JSONDecodeError, AttributeError):
        pass

    # Fallback: extract JSON from markdown code fences or embedded braces
    if not action:
        patterns = [
            r"```(?:json)?\s*(\{.*?\})\s*```",
            r"(\{[^{}]*\"action\"[^{}]*\})",
        ]
        for pat in patterns:
            m = re.search(pat, text, re.DOTALL)
            if m:
                try:
                    data = json.loads(m.group(1))
                    narrative = narrative or data.get("narrative", "")
                    action = data.get("action", "")
                    if action:
                        break
                except (json.JSONDecodeError, AttributeError):
                    continue

    # Validate action against allowed set
    if action not in allowed_actions:
        # Try case-insensitive / partial match
        action_lower = action.lower().strip()
        for a in allowed_actions:
            if a == action_lower:
                action = a
                break
        else:
            action = ""

    # Final fallback: pick a safe default
    if not action:
        if "continue" in allowed_actions:
            action = "continue"
        elif "wait" in allowed_actions:
            action = "wait"
        elif allowed_actions:
            action = allowed_actions[0]

    if not narrative:
        narrative = "(no narrative)"

    return narrative, action
