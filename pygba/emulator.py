"""
mGBA Python bindings wrapper.

Provides a clean interface over mgba.core for loading ROMs, reading memory,
pressing buttons, and advancing frames.  Adapted from the PyGBA project
(https://github.com/dvruette/pygba).
"""

import sys

try:
    import mgba.core
    import mgba.image
    from mgba._pylib import ffi, lib
except ImportError:
    print("=" * 60)
    print("ERROR: mGBA Python bindings not found.")
    print()
    print("You need mGBA built from source with -DBUILD_PYTHON=ON.")
    print("Run:  bash pygba/setup_mgba.sh")
    print("=" * 60)
    sys.exit(1)


# GBA key constants matching mgba C enum
class GBAKey:
    A      = 0
    B      = 1
    SELECT = 2
    START  = 3
    RIGHT  = 4
    LEFT   = 5
    UP     = 6
    DOWN   = 7
    R      = 8
    L      = 9

KEY_MAP = {
    "A": GBAKey.A, "B": GBAKey.B, "SELECT": GBAKey.SELECT,
    "START": GBAKey.START, "RIGHT": GBAKey.RIGHT, "LEFT": GBAKey.LEFT,
    "UP": GBAKey.UP, "DOWN": GBAKey.DOWN, "R": GBAKey.R, "L": GBAKey.L,
}


class Emulator:
    """Thin wrapper around mgba.core for headless GBA emulation."""

    def __init__(self, core):
        self._core = core
        self._screen = mgba.image.Image(240, 160)
        core.set_video_buffer(self._screen)
        core.reset()
        self._frame = 0

    @staticmethod
    def load(rom_path, save_path=None):
        """Load a GBA ROM (and optional .sav) and return an Emulator."""
        core = mgba.core.load_path(rom_path)
        if core is None:
            raise FileNotFoundError(f"Could not load ROM: {rom_path}")

        if save_path:
            core.load_save(save_path)

        return Emulator(core)

    # ── memory reads ────────────────────────────────────────────────

    def read_u8(self, addr):
        """Read an unsigned 8-bit value from the given address."""
        return self._core._native.memory.u8[addr]

    def read_u16(self, addr):
        """Read an unsigned 16-bit value (little-endian)."""
        return self._core._native.memory.u16[addr >> 1]

    def read_u32(self, addr):
        """Read an unsigned 32-bit value (little-endian)."""
        return self._core._native.memory.u32[addr >> 2]

    def read_bytes(self, addr, length):
        """Read a block of raw bytes."""
        return bytes(self._core._native.memory.u8[addr + i] for i in range(length))

    # ── input ───────────────────────────────────────────────────────

    def press_key(self, key, frames=16):
        """Press a single key (by name or GBAKey int) for N frames."""
        if isinstance(key, str):
            key = KEY_MAP[key.upper()]
        for _ in range(frames):
            self._core.set_keys(1 << key)
            self._core.run_frame()
            self._frame += 1
        self._core.set_keys(0)

    def set_keys_raw(self, bitmask):
        """Set the raw key bitmask (matching action step format)."""
        self._core.set_keys(bitmask)

    def release_keys(self):
        self._core.set_keys(0)

    # ── frame control ───────────────────────────────────────────────

    def tick(self, frames=1):
        """Advance the emulator by N frames (no input)."""
        for _ in range(frames):
            self._core.run_frame()
            self._frame += 1

    def current_frame(self):
        return self._frame

    # ── save state ──────────────────────────────────────────────────

    def save_state(self, slot=0):
        """Save a state to the given slot (in-memory)."""
        state = self._core.save_state()
        return state

    def load_state(self, state):
        """Restore a previously saved state."""
        self._core.load_state(state)
