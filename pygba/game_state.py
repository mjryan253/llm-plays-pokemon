"""
Pokemon FireRed (US v1.0 / BPRE) RAM reader.

Ports the Gen III substructure decryption logic from lua/game_agent.lua
into Python, reading memory directly via the Emulator wrapper instead of
file-based IPC.
"""

from pygba.pokemon_data import (
    GEN3_CHARSET, enrich_state, species_name, move_name, item_name,
)

# ── Memory addresses (FireRed US v1.0) ─────────────────────────────

SAVEBLOCK1_PTR = 0x03005008
SAVEBLOCK2_PTR = 0x0300500C

MAP_BANK_FIXED   = 0x02031DBC
MAP_NUMBER_FIXED = 0x02031DBD
PLAYER_MOVING    = 0x0203707B
MOVEMENT_LOCKED  = 0x0203707E

TEXT_BUFFER     = 0x02021D18
TEXT_BUFFER_LEN = 256

BATTLE_FLAGS = 0x02022B4C

PARTY_BASE      = 0x02024284
PARTY_SIZE      = 100
PARTY_COUNT_MAX = 6

ENEMY_BASE = 0x0202402C

# Badge offset within SaveBlock1
BADGE_OFFSET = 0x0FE4
# Money offset within SaveBlock1
MONEY_OFFSET = 0x0290
# Money XOR key offset within SaveBlock2
MONEY_KEY_OFFSET = 0x0F20

# ── Gen 3 substructure order table ──────────────────────────────────

SUBSTRUCTURE_ORDER = {
    0:  "GAEM", 1:  "GAME", 2:  "GEAM", 3:  "GEMA",
    4:  "GMAE", 5:  "GMEA", 6:  "AGEM", 7:  "AGME",
    8:  "AEGM", 9:  "AEMG", 10: "AMGE", 11: "AMEG",
    12: "EGAM", 13: "EGMA", 14: "EAGM", 15: "EAMG",
    16: "EMGA", 17: "EMAG", 18: "MGAE", 19: "MGEA",
    20: "MAGE", 21: "MAEG", 22: "MEGA", 23: "MEAG",
}

BADGE_NAMES = [
    "boulder", "cascade", "thunder", "rainbow",
    "soul", "marsh", "volcano", "earth",
]


def _decode_string(emu, addr, max_len):
    """Decode a Gen 3 proprietary charset string from memory."""
    chars = []
    for i in range(max_len):
        b = emu.read_u8(addr + i)
        if b == 0xFF:
            break
        c = GEN3_CHARSET.get(b)
        if c is not None:
            chars.append(c)
    return "".join(chars)


def _read_text_buffer(emu):
    first = emu.read_u8(TEXT_BUFFER)
    if first == 0x00 or first == 0xFF:
        return ""
    return _decode_string(emu, TEXT_BUFFER, TEXT_BUFFER_LEN)


def read_pokemon(emu, base):
    """Read and decrypt a single Pokemon structure from RAM.

    Returns a dict with species, moves, stats, etc., or None if the slot is empty.
    """
    pv   = emu.read_u32(base + 0x00)
    otid = emu.read_u32(base + 0x04)

    if pv == 0 and otid == 0:
        return None

    nickname = _decode_string(emu, base + 0x08, 10)

    # Decrypt the 48-byte data section (12 dwords)
    key = pv ^ otid
    words = []
    for i in range(12):
        words.append(emu.read_u32(base + 0x20 + i * 4) ^ key)

    order = SUBSTRUCTURE_ORDER[pv % 24]

    # Growth ("G") substructure
    g_idx = order.index("G")
    g_off = g_idx * 3
    species_id = words[g_off] & 0xFFFF
    held_item  = (words[g_off] >> 16) & 0xFFFF

    # Attacks ("A") substructure
    a_idx = order.index("A")
    a_off = a_idx * 3
    move1 = words[a_off] & 0xFFFF
    move2 = (words[a_off] >> 16) & 0xFFFF
    move3 = words[a_off + 1] & 0xFFFF
    move4 = (words[a_off + 1] >> 16) & 0xFFFF

    pp_word = words[a_off + 2]
    pp1 = pp_word & 0xFF
    pp2 = (pp_word >> 8) & 0xFF
    pp3 = (pp_word >> 16) & 0xFF
    pp4 = (pp_word >> 24) & 0xFF

    # Unencrypted battle stats (party struct, offset 0x50-0x63)
    status     = emu.read_u32(base + 0x50)
    level      = emu.read_u8(base + 0x54)
    hp         = emu.read_u16(base + 0x56)
    max_hp     = emu.read_u16(base + 0x58)
    attack     = emu.read_u16(base + 0x5A)
    defense    = emu.read_u16(base + 0x5C)
    speed      = emu.read_u16(base + 0x5E)
    sp_attack  = emu.read_u16(base + 0x60)
    sp_defense = emu.read_u16(base + 0x62)

    return {
        "species_id": species_id,
        "nickname": nickname,
        "level": level,
        "hp": hp,
        "max_hp": max_hp,
        "attack": attack,
        "defense": defense,
        "speed": speed,
        "sp_attack": sp_attack,
        "sp_defense": sp_defense,
        "status": status,
        "moves": [move1, move2, move3, move4],
        "pp": [pp1, pp2, pp3, pp4],
        "held_item_id": held_item,
    }


def _read_party(emu, base):
    party = []
    for i in range(PARTY_COUNT_MAX):
        pkmn = read_pokemon(emu, base + i * PARTY_SIZE)
        if pkmn and pkmn["species_id"] != 0:
            party.append(pkmn)
    return party


def detect_game_mode(emu):
    """Detect the current game mode from RAM flags."""
    battle_flags = emu.read_u32(BATTLE_FLAGS)
    if battle_flags != 0:
        return "battle"

    text_byte = emu.read_u8(TEXT_BUFFER)
    if text_byte != 0x00 and text_byte != 0xFF:
        return "dialog"

    move_locked = emu.read_u8(MOVEMENT_LOCKED)
    if move_locked == 1:
        return "menu"

    return "overworld"


def read_badges(emu):
    """Read badge flags. Returns dict: {"boulder": True, "cascade": False, ...}"""
    sb1 = emu.read_u32(SAVEBLOCK1_PTR)
    badge_word = emu.read_u16(sb1 + BADGE_OFFSET)
    return {name: bool(badge_word & (1 << i)) for i, name in enumerate(BADGE_NAMES)}


def read_money(emu):
    """Read the player's money (XOR-encrypted in SaveBlock1)."""
    sb1 = emu.read_u32(SAVEBLOCK1_PTR)
    sb2 = emu.read_u32(SAVEBLOCK2_PTR)
    raw = emu.read_u32(sb1 + MONEY_OFFSET)
    xor_key = emu.read_u32(sb2 + MONEY_KEY_OFFSET)
    return raw ^ xor_key


def read_player_name(emu):
    """Decode the 8-byte player name from SaveBlock2."""
    sb2 = emu.read_u32(SAVEBLOCK2_PTR)
    return _decode_string(emu, sb2, 8)


def game_progress(emu):
    """Composite progress snapshot: badges, money, player name, party levels."""
    badges = read_badges(emu)
    badge_count = sum(1 for v in badges.values() if v)
    money = read_money(emu)
    name = read_player_name(emu)

    sb1 = emu.read_u32(SAVEBLOCK1_PTR)
    party = _read_party(emu, PARTY_BASE)
    levels = [p["level"] for p in party]

    return {
        "player_name": name,
        "badges": badges,
        "badge_count": badge_count,
        "money": money,
        "party_levels": levels,
        "party_size": len(party),
    }


def collect_state(emu):
    """Collect the full game state by reading RAM directly.

    Returns a dict matching the state.json schema used by the legacy bridge.
    """
    sb1 = emu.read_u32(SAVEBLOCK1_PTR)

    player_x   = emu.read_u16(sb1 + 0x000)
    player_y   = emu.read_u16(sb1 + 0x002)
    map_number = emu.read_u8(sb1 + 0x004)
    map_bank   = emu.read_u8(sb1 + 0x005)

    is_moving       = emu.read_u8(PLAYER_MOVING) != 0
    movement_locked = emu.read_u8(MOVEMENT_LOCKED) != 0
    text_on_screen  = _read_text_buffer(emu)
    battle_type     = emu.read_u32(BATTLE_FLAGS)
    game_mode       = detect_game_mode(emu)

    party = _read_party(emu, PARTY_BASE)
    enemy = []
    if game_mode == "battle":
        enemy = _read_party(emu, ENEMY_BASE)

    state = {
        "frame": emu.current_frame(),
        "game_mode": game_mode,
        "player_x": player_x,
        "player_y": player_y,
        "map_bank": map_bank,
        "map_number": map_number,
        "is_moving": is_moving,
        "movement_locked": movement_locked,
        "text_on_screen": text_on_screen,
        "battle_type": battle_type,
        "party": party,
        "enemy": enemy,
    }

    return enrich_state(state)
