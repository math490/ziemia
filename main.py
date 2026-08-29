"""
Ziemia - A Terraria-style game built with Python and Arcade
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from game.game import ZiemiaGame


def main():
    """Initialize and run the Ziemia game."""
    game = ZiemiaGame()
    game.run()


if __name__ == "__main__":
    main()
