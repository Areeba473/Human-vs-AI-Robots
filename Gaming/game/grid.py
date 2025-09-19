from __future__ import annotations

from dataclasses import dataclass
import pygame

from game.config import NUM_LANES, TILES_PER_LANE, TILE_SIZE


@dataclass
class Tile:
    col: int
    row: int
    rect: pygame.Rect


class Grid:
    def __init__(self, origin_x: int, origin_y: int) -> None:
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.tiles: list[list[Tile]] = []
        for r in range(NUM_LANES):
            row: list[Tile] = []
            for c in range(TILES_PER_LANE):
                rect = pygame.Rect(
                    origin_x + c * TILE_SIZE,
                    origin_y + r * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE,
                )
                row.append(Tile(c, r, rect))
            self.tiles.append(row)

    def get_tile_at_pos(self, pos: tuple[int, int]) -> Tile | None:
        x, y = pos
        for row in self.tiles:
            for tile in row:
                if tile.rect.collidepoint(x, y):
                    return tile
        return None

    def draw(self, screen: pygame.Surface) -> None:
        # Grid lines are now invisible - no drawing
        pass


