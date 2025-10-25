
from __future__ import annotations

import os
import sys
import pygame

# Add the project root to the Python path to allow direct execution of this file
if __package__ is None:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, project_root)

# Use module imports
from game.config import WINDOW_HEIGHT, WINDOW_WIDTH, WINDOW_TITLE, FPS
from game.scenes import SplashScene
from game.core import Game


def main() -> None:
    try:
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)
        # Try fullscreen first, fallback to windowed mode if it fails
        try:
            screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
        except pygame.error:
            # Fallback to windowed mode if fullscreen fails
            screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        
        game = Game(screen)
        game.set_scene(SplashScene())
        game.run()
    except Exception as e:
        print(f"Error starting game: {e}")
    finally:
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    main()
