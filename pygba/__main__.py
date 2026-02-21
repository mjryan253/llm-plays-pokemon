"""Entry point: python -m pygba"""

import json
import os
import sys


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path) as f:
        return json.load(f)


def main():
    config = load_config()

    try:
        from pygba.emulator import Emulator
    except ImportError as exc:
        print(f"Failed to import mGBA Python bindings: {exc}")
        print()
        print("You need mGBA built with -DBUILD_PYTHON=ON.")
        print("Run: bash pygba/setup_mgba.sh")
        sys.exit(1)

    from pygba.agent import Agent

    rom_path = config.get("rom_path", "../gamefile/Pokemon FireRed.gba")
    save_path = config.get("save_path")

    emu = Emulator.load(rom_path, save_path)
    agent = Agent(emu, config)
    agent.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down.")
        sys.exit(0)
