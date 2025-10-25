from __future__ import annotations

import pygame


from typing import List

from game.config import UNIT_DEFS
from game.assets import (
    draw_shooter,
    draw_frozen_shooter,
    draw_wall_block,
    draw_generator_icon,
    draw_bomb_icon,
    draw_charger,
    draw_tank,
    draw_laser_gun,
    draw_virus,
    draw_bubble_shooter,
    draw_shield_defender,
    draw_shadow_healer,
    draw_ice_shroom,
    draw_shovel,
    draw_gatling_pea,
    draw_doom_shroom,
    draw_sun_shroom,
    draw_puff_shroom,
    draw_scaredy_shroom,
    draw_leaf,
    draw_tangle_kelp,
    draw_sea_shroom,
    draw_cattail,
    draw_sea_mine,
    draw_spikerock,
)


class HUD:
    def __init__(self, width: int, orientation: str = "top", unit_defs: List[dict] | None = None, enable_shovel: bool = False) -> None:
        self.height = 64
        self.width = width
        self.font = pygame.font.SysFont(None, 22)
        self.selected_index = 0
        self.orientation = orientation  # "top" or "left"
        self.unit_defs: List[dict] = unit_defs if unit_defs is not None else UNIT_DEFS
        # cooldown trackers per slot
        self.hud_rect = pygame.Rect(0, 0, 0, 0) # Main rect for the HUD area
        self.cooldowns: List[float] = [0.0 for _ in self.unit_defs]
        self.shovel_mode = False
        self.enable_shovel = enable_shovel
        # scrolling for lots of units
        self.scroll = 0.0
        self._row_step = 62
        if self.orientation == "left":
            self._shovel_rect = pygame.Rect(12, 8, 96, 44) if self.enable_shovel else None
            self._slot_rects = []
            # Scrollbar drag state
            self._scroll_dragging = False
            self._scroll_drag_offset = 0
        else:
            self._shovel_rect = pygame.Rect(self.width - 90, 8, 80, 48) if self.enable_shovel else None
            self._slot_rects = [pygame.Rect(10 + i * 70, 8, 60, 48) for i in range(len(self.unit_defs))]
        # pre-render icons for seed packets (scaled)
        self.icons: List[pygame.Surface] = []
        for unit in self.unit_defs:
            key = unit["key"]
            surf = self._make_icon_surface(key)
            self.icons.append(surf)

    def _make_icon_surface(self, key: str) -> pygame.Surface:
        # get a 56x56 unit surface from assets and scale down to fit the slot
        if key == "shooter":
            base = draw_shooter()
        elif key == "frozen":
            base = draw_frozen_shooter()
        elif key == "wall":
            base = draw_wall_block()
        elif key == "generator":
            base = draw_generator_icon()
        elif key == "bomb":
            base = draw_bomb_icon()
        elif key == "charger":
            base = draw_charger()
        elif key == "tank":
            base = draw_tank()
        elif key == "laser_gun":
            base = draw_laser_gun()
        elif key == "virus":
            base = draw_virus()
        elif key == "bubble_shooter":
            base = draw_bubble_shooter()
        elif key == "shield_defender":
            base = draw_shield_defender()
        elif key == "shadow_healer":
            base = draw_shadow_healer()
        elif key == "ice_shroom":
            base = draw_ice_shroom()
        elif key == "gatling_pea":
            base = draw_gatling_pea()
        elif key == "doom_shroom":
            base = draw_doom_shroom()
        elif key == "sun_shroom":
            base = draw_sun_shroom()
        elif key == "puff_shroom":
            base = draw_puff_shroom()
        elif key == "scaredy_shroom":
            base = draw_scaredy_shroom()
        elif key == "leaf":
            base = draw_leaf()
        elif key == "tangle_kelp":
            base = draw_tangle_kelp()
        elif key == "sea_shroom":
            base = draw_sea_shroom()
        elif key == "cattail":
            base = draw_cattail()
        elif key == "spikerock":
            base = draw_spikerock()
        elif key == "sea_mine":
            base = draw_sea_mine()
        elif key == "shovel":
            base = draw_shovel()
        else:
            base = pygame.Surface((56, 56), pygame.SRCALPHA)
        return pygame.transform.smoothscale(base, (44, 36))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_1 + len(self.unit_defs) - 1:
                self.selected_index = event.key - pygame.K_1
            if event.key == pygame.K_q and self.enable_shovel:
                self.shovel_mode = not self.shovel_mode
        elif event.type == pygame.MOUSEWHEEL and self.orientation == "left":
            # scroll vertical list
            # Visible track height excludes top/bottom margins (60 top, 20 bottom ⇒ 80 total)
            track_h = max(0, self.width - 80)
            max_scroll = max(0, len(self.unit_defs) * self._row_step - track_h)
            self.scroll = max(0.0, min(self.scroll - event.y * 40.0, float(max_scroll)))
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Handle scrollbar clicks/drags for left HUD
            if self.orientation == "left":
                content_h = len(self.unit_defs) * self._row_step
                view_h = self.width
                track = pygame.Rect(108, 60, 6, max(0, view_h - 80))
                if track.h > 0 and content_h > track.h and track.collidepoint(event.pos):
                    max_scroll = max(0, content_h - track.h)
                    bar_h = max(24, int(track.h * (track.h / max(content_h, 1))))
                    frac = (self.scroll / max_scroll) if max_scroll > 0 else 0
                    bar_y = track.y + int((track.h - bar_h) * frac)
                    bar_rect = pygame.Rect(track.x, bar_y, track.w, bar_h)
                    if bar_rect.collidepoint(event.pos):
                        # Start dragging the bar
                        self._scroll_dragging = True
                        self._scroll_drag_offset = event.pos[1] - bar_y
                        return
                    else:
                        # Jump scroll to clicked position on track
                        new_bar_y = max(track.y, min(event.pos[1] - bar_h // 2, track.y + track.h - bar_h))
                        frac = (new_bar_y - track.y) / max(1, (track.h - bar_h))
                        self.scroll = frac * max_scroll
                        return
            # click shovel
            if self.enable_shovel and self._shovel_rect and self._shovel_rect.collidepoint(event.pos):
                self.shovel_mode = not self.shovel_mode
                return
            # click seed slots to select
            for i, r in enumerate(self._slot_rects):
                if r.collidepoint(event.pos):
                    self.selected_index = i
                    return
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            # Stop dragging on mouse up
            self._scroll_dragging = False
        elif event.type == pygame.MOUSEMOTION and self.orientation == "left":
            # Update scroll while dragging
            if self._scroll_dragging:
                content_h = len(self.unit_defs) * self._row_step
                view_h = self.width
                track = pygame.Rect(108, 60, 6, max(0, view_h - 80))
                if track.h > 0 and content_h > track.h:
                    max_scroll = max(0, content_h - track.h)
                    bar_h = max(24, int(track.h * (track.h / max(content_h, 1))))
                    new_bar_y = max(track.y, min(event.pos[1] - self._scroll_drag_offset, track.y + track.h - bar_h))
                    frac = (new_bar_y - track.y) / max(1, (track.h - bar_h))
                    self.scroll = frac * max_scroll

    def is_pos_on_hud(self, pos: tuple[int, int]) -> bool:
        """Check if a given position is on the HUD area."""
        if self.hud_rect.collidepoint(pos):
            return True
        # Also check individual slot rects in case they are outside the main HUD rect (scrolling)
        return any(r.collidepoint(pos) for r in self._slot_rects)

    def draw(self, screen: pygame.Surface, energy: int) -> None:
        if self.orientation == "left":
            # left vertical bar (full height)
            pygame.draw.rect(screen, (35, 35, 35), (0, 0, 120, screen.get_height()))
        else:
            pygame.draw.rect(screen, (30, 30, 30), (0, 0, self.width, self.height))

        # Update the main HUD rect for click detection
        if self.orientation == "left":
            self.hud_rect = pygame.Rect(0, 0, 120, screen.get_height())
        else:
            self.hud_rect = pygame.Rect(0, 0, self.width, self.height)

        # rebuild slot rects each draw to reflect scroll
        self._slot_rects = []
        for i, unit in enumerate(self.unit_defs):
            if self.orientation == "left":
                rect = pygame.Rect(12, 60 + i * self._row_step - int(self.scroll), 96, 52)
            else:
                rect = self._slot_rects[i] if i < len(self._slot_rects) else pygame.Rect(10 + i * 70, 8, 60, 48)
            self._slot_rects.append(rect)
            is_sel = i == self.selected_index
            # seed packet background
            packet_color = (85, 85, 85) if not is_sel else (110, 150, 110)
            pygame.draw.rect(screen, packet_color, rect, border_radius=8)
            inner = rect.inflate(-8, -10)
            pygame.draw.rect(screen, (235, 235, 235), inner, border_radius=6)
            # icon
            icon = self.icons[i]
            screen.blit(icon, (inner.centerx - icon.get_width() // 2, inner.y + 3))
            # small cost badge bottom-right
            cost_badge = pygame.Rect(inner.right - 26, inner.bottom - 18, 24, 16)
            pygame.draw.rect(screen, (255, 255, 255), cost_badge, border_radius=6)
            cost_text = self.font.render(str(unit["cost"]), True, (20, 20, 20))
            screen.blit(cost_text, (cost_badge.x + 2, cost_badge.y + 1))
            # cooldown visual overlay
            cd = self.cooldowns[i]
            if cd > 0:
                alpha = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                alpha.fill((10, 10, 10, 140))
                screen.blit(alpha, (rect.x, rect.y))
            # insufficient energy overlay
            if energy < unit["cost"]:
                alpha = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                alpha.fill((140, 20, 20, 80))
                screen.blit(alpha, (rect.x, rect.y))

        # Shovel button (only if enabled)
        if self.enable_shovel and self._shovel_rect is not None:
            shovel_color = (160, 90, 60) if self.shovel_mode else (80, 50, 40)
            pygame.draw.rect(screen, shovel_color, self._shovel_rect, border_radius=8)
            sh = self.font.render("Shovel", True, (230, 230, 230))
            screen.blit(sh, (self._shovel_rect.x + 10, self._shovel_rect.y + 14))

        # simple scrollbar on left orientation
        if self.orientation == "left":
            content_h = len(self.unit_defs) * self._row_step
            view_h = self.width
            track = pygame.Rect(108, 60, 6, max(0, view_h - 80))
            if content_h > track.h:
                bar_h = max(24, int(track.h * (track.h / max(content_h, 1))))
                pygame.draw.rect(screen, (60, 60, 60), track, border_radius=3)
                max_scroll = max(0, content_h - track.h)
                # Clamp scroll in case content/view changed
                self.scroll = max(0.0, min(self.scroll, float(max_scroll)))
                frac = (self.scroll / max_scroll) if max_scroll > 0 else 0
                bar_y = track.y + int((track.h - bar_h) * frac)
                pygame.draw.rect(screen, (180, 180, 180), pygame.Rect(track.x, bar_y, track.w, bar_h), border_radius=3)

    def tick_cooldowns(self, dt: float) -> None:
        for i in range(len(self.cooldowns)):
            self.cooldowns[i] = max(0.0, self.cooldowns[i] - dt)
