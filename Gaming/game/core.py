from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import pygame

from game.config import FPS


class Scene:
    def __init__(self) -> None:
        self.next_scene: Optional[Scene] = None

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, screen: pygame.Surface) -> None:
        pass


class Game:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.scene: Optional[Scene] = None

    def set_scene(self, scene: Scene) -> None:
        self.scene = scene

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                elif self.scene:
                    self.scene.handle_event(event)

            if self.scene:
                self.scene.update(dt)
                # Handle scene transitions
                if self.scene.next_scene is not None:
                    self.scene = self.scene.next_scene
                    continue
                self.scene.draw(self.screen)
                pygame.display.flip()
            else:
                self.running = False


