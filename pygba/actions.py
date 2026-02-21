"""
GBA key bitmask values and high-level action -> button sequence mapping.

Each action maps to a list of steps: {"keys": <bitmask>, "frames": <hold duration>}.
A zero-keys step is a release gap between presses.
"""

KEY = {
    "A": 1, "B": 2, "SELECT": 4, "START": 8,
    "RIGHT": 16, "LEFT": 32, "UP": 64, "DOWN": 128,
    "R": 256, "L": 512,
}

# Reverse lookup for display
KEY_NAMES = {v: k for k, v in KEY.items()}

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

    # Battle -- RUN
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

    # Battle -- switch pokemon
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

ALL_ACTIONS = list(ACTION_SEQUENCES.keys())

OVERWORLD_ACTIONS = [
    "move_up", "move_down", "move_left", "move_right",
    "interact", "open_menu", "wait",
]

DIALOG_ACTIONS = ["continue", "choose_yes", "choose_no"]

MENU_ACTIONS = ["menu_pokemon", "menu_bag", "menu_save", "menu_close"]


def get_battle_actions(state):
    """Dynamic battle actions based on PP and alive party members."""
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


def total_frames(action_name):
    """Total frame count for an action sequence."""
    seq = ACTION_SEQUENCES.get(action_name, [])
    return sum(s.get("frames", 0) for s in seq)
