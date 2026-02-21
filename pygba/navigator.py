"""
FireRed map adjacency graph with BFS pathfinding.

Hardcoded adjacency list of ~70 key locations covering the main storyline
path from Pallet Town through Victory Road and Indigo Plateau, including
all 8 gym cities, major routes, and key dungeons.

Each node is identified by (map_bank, map_number) matching the values in
pokemon_data.MAP_NAMES.  Edges carry a cardinal direction hint for the LLM.
"""

from collections import deque

# ── Node aliases (map_bank, map_number) for readability ─────────────

PALLET_TOWN     = (3, 0)
VIRIDIAN_CITY   = (3, 1)
PEWTER_CITY     = (3, 2)
CERULEAN_CITY   = (3, 3)
LAVENDER_TOWN   = (3, 4)
VERMILION_CITY  = (3, 5)
CELADON_CITY    = (3, 6)
FUCHSIA_CITY    = (3, 7)
CINNABAR_ISLAND = (3, 8)
INDIGO_PLATEAU  = (3, 9)
SAFFRON_CITY    = (3, 10)

ROUTE_1  = (3, 18)
ROUTE_2  = (3, 19)
ROUTE_3  = (3, 20)
ROUTE_4  = (3, 21)
ROUTE_5  = (3, 22)
ROUTE_6  = (3, 23)
ROUTE_7  = (3, 24)
ROUTE_8  = (3, 25)
ROUTE_9  = (3, 26)
ROUTE_10 = (3, 27)
ROUTE_11 = (3, 28)
ROUTE_12 = (3, 29)
ROUTE_13 = (3, 30)
ROUTE_14 = (3, 31)
ROUTE_15 = (3, 32)
ROUTE_16 = (3, 33)
ROUTE_17 = (3, 34)
ROUTE_18 = (3, 35)
ROUTE_19 = (3, 36)
ROUTE_20 = (3, 37)
ROUTE_21 = (3, 38)
ROUTE_22 = (3, 39)
ROUTE_23 = (3, 40)
ROUTE_24 = (3, 41)
ROUTE_25 = (3, 42)

VIRIDIAN_FOREST = (8, 0)
MT_MOON_1F      = (8, 1)
MT_MOON_B1F     = (8, 2)
MT_MOON_B2F     = (8, 3)
ROCK_TUNNEL_1F  = (8, 32)
ROCK_TUNNEL_B1F = (8, 33)
POKEMON_TOWER   = (8, 14)
SILPH_CO        = (8, 21)
VICTORY_ROAD_1F = (8, 11)
VICTORY_ROAD_2F = (8, 12)
VICTORY_ROAD_3F = (8, 13)
SEAFOAM_1F      = (10, 6)
POWER_PLANT     = (10, 14)
DIGLETTS_CAVE_N = (10, 0)
DIGLETTS_CAVE_S = (10, 1)
POKEMON_MANSION = (10, 11)
CERULEAN_CAVE   = (10, 3)

OAKS_LAB        = (4, 3)

# Gym identifiers for goal matching
PEWTER_GYM      = (4, 12)
CERULEAN_GYM    = (4, 19)
VERMILION_GYM   = (4, 38)
CELADON_GYM     = (4, 49)
SAFFRON_GYM     = (4, 53)
FUCHSIA_GYM     = (4, 60)
CINNABAR_GYM    = (4, 63)
VIRIDIAN_GYM    = (4, 8)

# ── Adjacency graph ────────────────────────────────────────────────
# Format: { node: [(neighbor, direction), ...] }
# Directions are hints for the LLM, not precise compass readings.

ADJACENCY = {
    PALLET_TOWN:     [(ROUTE_1, "north"), (ROUTE_21, "south"), (OAKS_LAB, "enter")],
    OAKS_LAB:        [(PALLET_TOWN, "exit")],
    ROUTE_1:         [(PALLET_TOWN, "south"), (VIRIDIAN_CITY, "north")],
    VIRIDIAN_CITY:   [(ROUTE_1, "south"), (ROUTE_2, "north"), (ROUTE_22, "west")],
    ROUTE_2:         [(VIRIDIAN_CITY, "south"), (VIRIDIAN_FOREST, "north")],
    VIRIDIAN_FOREST: [(ROUTE_2, "south"), (PEWTER_CITY, "north")],
    PEWTER_CITY:     [(VIRIDIAN_FOREST, "south"), (ROUTE_3, "east")],
    ROUTE_3:         [(PEWTER_CITY, "west"), (MT_MOON_1F, "east")],
    MT_MOON_1F:      [(ROUTE_3, "west"), (MT_MOON_B1F, "down")],
    MT_MOON_B1F:     [(MT_MOON_1F, "up"), (MT_MOON_B2F, "down")],
    MT_MOON_B2F:     [(MT_MOON_B1F, "up"), (ROUTE_4, "exit")],
    ROUTE_4:         [(MT_MOON_B2F, "west"), (CERULEAN_CITY, "east")],
    CERULEAN_CITY:   [(ROUTE_4, "west"), (ROUTE_24, "north"), (ROUTE_5, "south"),
                      (ROUTE_9, "east")],
    ROUTE_24:        [(CERULEAN_CITY, "south"), (ROUTE_25, "east")],
    ROUTE_25:        [(ROUTE_24, "west")],
    ROUTE_5:         [(CERULEAN_CITY, "north"), (SAFFRON_CITY, "south")],
    SAFFRON_CITY:    [(ROUTE_5, "north"), (ROUTE_6, "south"), (ROUTE_7, "west"),
                      (ROUTE_8, "east")],
    ROUTE_6:         [(SAFFRON_CITY, "north"), (VERMILION_CITY, "south")],
    VERMILION_CITY:  [(ROUTE_6, "north"), (ROUTE_11, "east")],
    ROUTE_11:        [(VERMILION_CITY, "west"), (ROUTE_12, "east"),
                      (DIGLETTS_CAVE_S, "enter")],
    DIGLETTS_CAVE_S: [(ROUTE_11, "exit"), (DIGLETTS_CAVE_N, "through")],
    DIGLETTS_CAVE_N: [(DIGLETTS_CAVE_S, "through"), (ROUTE_2, "exit")],
    ROUTE_7:         [(SAFFRON_CITY, "east"), (CELADON_CITY, "west")],
    CELADON_CITY:    [(ROUTE_7, "east"), (ROUTE_16, "west")],
    ROUTE_8:         [(SAFFRON_CITY, "west"), (LAVENDER_TOWN, "east")],
    LAVENDER_TOWN:   [(ROUTE_8, "west"), (ROUTE_12, "south"), (ROUTE_10, "north")],
    ROUTE_9:         [(CERULEAN_CITY, "west"), (ROUTE_10, "east"),
                      (ROCK_TUNNEL_1F, "enter")],
    ROUTE_10:        [(ROUTE_9, "west"), (LAVENDER_TOWN, "south"),
                      (POWER_PLANT, "enter"), (ROCK_TUNNEL_1F, "enter")],
    ROCK_TUNNEL_1F:  [(ROUTE_9, "exit"), (ROCK_TUNNEL_B1F, "down")],
    ROCK_TUNNEL_B1F: [(ROCK_TUNNEL_1F, "up"), (LAVENDER_TOWN, "exit")],
    ROUTE_12:        [(LAVENDER_TOWN, "north"), (ROUTE_13, "south"),
                      (ROUTE_11, "west")],
    ROUTE_13:        [(ROUTE_12, "north"), (ROUTE_14, "south")],
    ROUTE_14:        [(ROUTE_13, "north"), (ROUTE_15, "south")],
    ROUTE_15:        [(ROUTE_14, "north"), (FUCHSIA_CITY, "west")],
    FUCHSIA_CITY:    [(ROUTE_15, "east"), (ROUTE_18, "west"), (ROUTE_19, "south")],
    ROUTE_16:        [(CELADON_CITY, "east"), (ROUTE_17, "south")],
    ROUTE_17:        [(ROUTE_16, "north"), (ROUTE_18, "south")],
    ROUTE_18:        [(ROUTE_17, "north"), (FUCHSIA_CITY, "east")],
    ROUTE_19:        [(FUCHSIA_CITY, "north"), (ROUTE_20, "south")],
    ROUTE_20:        [(ROUTE_19, "north"), (CINNABAR_ISLAND, "west"),
                      (SEAFOAM_1F, "enter")],
    SEAFOAM_1F:      [(ROUTE_20, "exit")],
    CINNABAR_ISLAND: [(ROUTE_20, "east"), (ROUTE_21, "north")],
    ROUTE_21:        [(CINNABAR_ISLAND, "south"), (PALLET_TOWN, "north")],
    ROUTE_22:        [(VIRIDIAN_CITY, "east"), (ROUTE_23, "west")],
    ROUTE_23:        [(ROUTE_22, "east"), (VICTORY_ROAD_1F, "enter"),
                      (INDIGO_PLATEAU, "north")],
    VICTORY_ROAD_1F: [(ROUTE_23, "exit"), (VICTORY_ROAD_2F, "up")],
    VICTORY_ROAD_2F: [(VICTORY_ROAD_1F, "down"), (VICTORY_ROAD_3F, "up")],
    VICTORY_ROAD_3F: [(VICTORY_ROAD_2F, "down"), (INDIGO_PLATEAU, "exit")],
    INDIGO_PLATEAU:  [(ROUTE_23, "south"), (VICTORY_ROAD_3F, "enter")],
    POWER_PLANT:     [(ROUTE_10, "exit")],
    POKEMON_TOWER:   [(LAVENDER_TOWN, "exit")],
    SILPH_CO:        [(SAFFRON_CITY, "exit")],
    POKEMON_MANSION: [(CINNABAR_ISLAND, "exit")],
    CERULEAN_CAVE:   [(CERULEAN_CITY, "exit")],
}

# Add gym entrances from their cities
_GYM_CITY = {
    PEWTER_GYM: PEWTER_CITY, CERULEAN_GYM: CERULEAN_CITY,
    VERMILION_GYM: VERMILION_CITY, CELADON_GYM: CELADON_CITY,
    SAFFRON_GYM: SAFFRON_CITY, FUCHSIA_GYM: FUCHSIA_CITY,
    CINNABAR_GYM: CINNABAR_ISLAND, VIRIDIAN_GYM: VIRIDIAN_CITY,
}
for gym, city in _GYM_CITY.items():
    ADJACENCY.setdefault(gym, []).append((city, "exit"))
    ADJACENCY[city].append((gym, "enter"))

# Add dungeon entrances from cities
_DUNGEON_CITY = {
    POKEMON_TOWER: LAVENDER_TOWN,
    SILPH_CO: SAFFRON_CITY,
    POKEMON_MANSION: CINNABAR_ISLAND,
    CERULEAN_CAVE: CERULEAN_CITY,
}
for dungeon, city in _DUNGEON_CITY.items():
    if (dungeon, "enter") not in ADJACENCY.get(city, []):
        ADJACENCY[city].append((dungeon, "enter"))

# Import map names for display
from pygba.pokemon_data import MAP_NAMES


def _node_name(node):
    return MAP_NAMES.get(node, f"({node[0]},{node[1]})")


def find_path(current, target):
    """BFS shortest path from current to target.

    Returns a list of (node, direction) tuples representing the path,
    or an empty list if no path exists.
    """
    if current == target:
        return []

    if current not in ADJACENCY:
        return []

    visited = {current}
    queue = deque([(current, [])])

    while queue:
        node, path = queue.popleft()
        for neighbor, direction in ADJACENCY.get(node, []):
            if neighbor in visited:
                continue
            visited.add(neighbor)
            new_path = path + [(neighbor, direction)]
            if neighbor == target:
                return new_path
            queue.append((neighbor, new_path))

    return []


def path_hint(current, target):
    """Generate a human-readable navigation hint for the LLM.

    Returns a string like "Path to Cerulean City: Route 3 -> Mt. Moon 1F -> ... Head east."
    or None if no path is found.
    """
    path = find_path(current, target)
    if not path:
        return None

    location_names = [_node_name(n) for n, _ in path]
    first_dir = path[0][1] if path else ""

    hint = f"Path to {_node_name(target)}: {' -> '.join(location_names)}."
    if first_dir:
        hint += f" Head {first_dir}."
    return hint


def find_nearest_pokecenter(current):
    """Find the nearest Pokemon Center accessible from the current location.

    Returns (city_node, path) or (None, []) if not reachable.
    """
    pokecenter_cities = [
        VIRIDIAN_CITY, PEWTER_CITY, CERULEAN_CITY, VERMILION_CITY,
        LAVENDER_TOWN, CELADON_CITY, SAFFRON_CITY, FUCHSIA_CITY,
        CINNABAR_ISLAND, INDIGO_PLATEAU,
    ]

    best_city = None
    best_path = None

    for city in pokecenter_cities:
        p = find_path(current, city)
        if p and (best_path is None or len(p) < len(best_path)):
            best_city = city
            best_path = p

    return best_city, best_path or []


def current_location_node(map_bank, map_number):
    """Convert map_bank/map_number to a graph node, or find the closest match."""
    node = (map_bank, map_number)
    if node in ADJACENCY:
        return node

    # Interior maps: check if it's a gym or known interior
    if node in _GYM_CITY:
        return node
    if node in _DUNGEON_CITY:
        return node

    # Fall back to the city for known interior map banks
    # Bank 4 = city interiors, bank 5 = E4, bank 9 = gates
    if map_bank == 4:
        city_ranges = [
            (range(0, 4), PALLET_TOWN), (range(4, 10), VIRIDIAN_CITY),
            (range(10, 16), PEWTER_CITY), (range(16, 21), CERULEAN_CITY),
            (range(36, 40), VERMILION_CITY), (range(43, 53), CELADON_CITY),
            (range(53, 58), SAFFRON_CITY), (range(58, 62), FUCHSIA_CITY),
            (range(62, 66), CINNABAR_ISLAND),
        ]
        for r, city in city_ranges:
            if map_number in r:
                return city

    if map_bank == 5:
        return INDIGO_PLATEAU

    return None
