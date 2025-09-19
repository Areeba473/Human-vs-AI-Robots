#!/usr/bin/env python3
"""
Launcher script for the game.
Run this script to start the game.
"""

import sys
import os

# Add the game directory to Python path
game_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'game')
sys.path.insert(0, game_dir)

# Run the game module
if __name__ == "__main__":
    # Import and run the main function
    sys.path.insert(0, game_dir)
    from game.__main__ import main
    main()
