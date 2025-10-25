from __future__ import annotations

import os
import random
import pygame

from game.config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    COLOR_BG,
    TILE_SIZE,
    NUM_LANES,
    TILES_PER_LANE,
    THEMES,
)
from game.core import Scene
from game.grid import Grid
from game.ui import HUD, hud
from game.entities import Human, Robot, FastRobot, WhiteBlueRobot, WallHuman, Generator, Bomb, EnergyDrop, Mower, FrozenShooter, Charger, Tank, LaserGun, Virus, BubbleShooter, ShieldDefender, NightStalker, ShadowHealer, IceShroom, GatlingPea, DoomShroom, Crater, ExplosionEffect, SunShroom, PuffShroom, ScaredyShroom, Leaf, TangleKelp, SeaShroom, Cattail, Spikerock
from game.config import START_ENERGY, SKY_DROP_INTERVAL, UNIT_DEFS, MOWER_SPEED, LEVELS_PER_THEME
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
    draw_night_stalker,
    draw_shadow_healer,
    draw_ice_shroom,
    draw_gatling_pea,
    draw_doom_shroom,
    draw_sun_shroom,
    draw_puff_shroom,
    draw_scaredy_shroom,
    draw_leaf,
    draw_tangle_kelp,
    draw_sea_shroom,
    draw_cattail,
    draw_spikerock,
    draw_shovel,
)
from game.levels import LevelManager

# Custom event for screen shake
SCREEN_SHAKE_EVENT = pygame.USEREVENT + 1


class MenuScene(Scene):
    def __init__(self) -> None:
        super().__init__()
        self.font = pygame.font.SysFont(None, 32)
        self.small = pygame.font.SysFont(None, 24)
        self.next_scene = None
        self.selection = 0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.next_scene = PlayScene(theme=THEMES[self.selection])
            if event.key == pygame.K_RIGHT:
                self.selection = (self.selection + 1) % len(THEMES)
            if event.key == pygame.K_LEFT:
                self.selection = (self.selection - 1) % len(THEMES)

    def update(self, dt: float) -> None:
        pass

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((25, 25, 35))
        title = self.font.render("Humans vs AI Robots", True, (230, 230, 230))
        screen.blit(title, (40, 40))
        hint = self.small.render("Left/Right to choose theme, Enter to start", True, (200, 200, 200))
        screen.blit(hint, (40, 80))
        y = 140
        for i, t in enumerate(THEMES):
            col = (240, 220, 100) if i == self.selection else (180, 180, 180)
            txt = self.small.render(t, True, col)
            screen.blit(txt, (60 + i * 120, y))


class SplashScene(Scene):
    def __init__(self) -> None:
        super().__init__()
        self.next_scene = None
        self.font = pygame.font.SysFont(None, 28)
        # Try to load background image: game/images/title.(png|jpg|jpeg)
        self.bg: pygame.Surface | None = None
        try:
            base = os.path.dirname(__file__)
            for name in ("title.png", "title.jpg", "title.jpeg"):
                img_path = os.path.join(base, "images", name)
                if os.path.exists(img_path):
                    img = pygame.image.load(img_path).convert()
                    self.bg = pygame.transform.smoothscale(img, (WINDOW_WIDTH, WINDOW_HEIGHT))
                    break
        except Exception:
            self.bg = None
        self.timer = 0.0
        self.auto_time = 3.0

    def handle_event(self, event: pygame.event.Event) -> None:
        # No-op; we auto-advance
        pass

    def update(self, dt: float) -> None:
        self.timer += dt
        if self.timer >= self.auto_time and self.next_scene is None:
            self.next_scene = HomeMenuScene()

    def draw(self, screen: pygame.Surface) -> None:
        if self.bg is not None:
            screen.blit(self.bg, (0, 0))
        else:
            # Fallback gradient-like background
            screen.fill((50, 90, 140))
            pygame.draw.rect(screen, (210, 230, 250), (0, 0, WINDOW_WIDTH, 120))
            pygame.draw.rect(screen, (60, 110, 70), (0, WINDOW_HEIGHT - 160, WINDOW_WIDTH, 160))
        # No hint; auto-advance


class HomeMenuScene(Scene):
    def __init__(self) -> None:
        super().__init__()
        self.next_scene = None
        self.font_title = pygame.font.SysFont(None, 54, bold=True)
        self.font_btn = pygame.font.SysFont(None, 36, bold=True)
        self.options = [
            ("Adventure", "adventure"),
            ("More Modes", "modes"),
            ("Zen Garden", "garden"),
        ]
        self.buttons: list[pygame.Rect] = []
        self._build_buttons()
        # optional background image: game/images/home.(png|jpg|jpeg)
        self.bg: pygame.Surface | None = None
        try:
            base = os.path.dirname(__file__)
            candidates = ("home.png", "home.jpg", "home.jpeg", "Home.png", "Home.jpg", "Home.jpeg")
            for name in candidates:
                p = os.path.join(base, "images", name)
                if os.path.exists(p):
                    img = pygame.image.load(p).convert()
                    self.bg = pygame.transform.smoothscale(img, (WINDOW_WIDTH, WINDOW_HEIGHT))
                    break
        except Exception:
            self.bg = None

    def _build_buttons(self) -> None:
        x = 80
        y = 140
        w = 280
        h = 56
        gap = 18
        self.buttons = []
        for _ in self.options:
            self.buttons.append(pygame.Rect(x, y, w, h))
            y += h + gap

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for idx, r in enumerate(self.buttons):
                if r.collidepoint(event.pos):
                    label, key = self.options[idx]
                    # For now, only Adventure goes to our theme menu
                    if key == "adventure":
                        self.next_scene = LevelSelectScene()
                    # Others could be wired later
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.next_scene = LevelSelectScene()

    def update(self, dt: float) -> None:
        pass

    def draw(self, screen: pygame.Surface) -> None:
        if self.bg is not None:
            screen.blit(self.bg, (0, 0))
        else:
            # Simple garden-like backdrop
            screen.fill((120, 180, 220))
            pygame.draw.rect(screen, (120, 180, 120), (0, WINDOW_HEIGHT - 180, WINDOW_WIDTH, 180))
        title = self.font_title.render("Main Menu", True, (20, 40, 20))
        screen.blit(title, (40, 40))
        for idx, r in enumerate(self.buttons):
            label, _ = self.options[idx]
            pygame.draw.rect(screen, (60, 60, 60), r, border_radius=10)
            inner = r.inflate(-8, -8)
            pygame.draw.rect(screen, (230, 230, 230), inner, border_radius=10)
            text = self.font_btn.render(label, True, (20, 30, 20))
            screen.blit(text, (inner.centerx - text.get_width() // 2, inner.centery - text.get_height() // 2))


class LevelSelectScene(Scene):
    def __init__(self) -> None:
        super().__init__()
        self.next_scene = None
        self.manager = LevelManager()
        self.font = pygame.font.SysFont(None, 26)
        self.font_big = pygame.font.SysFont(None, 32, bold=True)
        self.theme_idx = 0
        self.level_idx = 1
        # precompute level button rects
        self.level_rects: list[pygame.Rect] = []
        self.play_rect = pygame.Rect(0, 0, 140, 48)
        self._layout()

    def _layout(self) -> None:
        self.level_rects = []
        start_x = 80
        start_y = 120
        w, h = 96, 60
        gap_x, gap_y = 14, 14
        x, y = start_x, start_y
        for i in range(LEVELS_PER_THEME):
            self.level_rects.append(pygame.Rect(x, y, w, h))
            x += w + gap_x
            if (i + 1) % 5 == 0:
                x = start_x
                y += h + gap_y
        self.play_rect = pygame.Rect(80, y + 80, 140, 48)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_scene = HomeMenuScene()
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                self.theme_idx = (self.theme_idx + 1) % len(THEMES)
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.theme_idx = (self.theme_idx - 1) % len(THEMES)
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                theme = THEMES[self.theme_idx]
                self.manager.set_current(theme, self.level_idx)
                if theme == "Day" and self.level_idx < 9:
                    self.next_scene = PlayScene(theme=theme, level=self.level_idx)
                else:
                    self.next_scene = UnitSelectScene(theme=theme, level=self.level_idx)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for idx, r in enumerate(self.level_rects, start=1):
                if r.collidepoint(event.pos):
                    # only allow select up to unlocked
                    unlocked = self.manager.unlocked.get(THEMES[self.theme_idx], 1)
                    if idx <= unlocked:
                        self.level_idx = idx
                    return
            # bottom theme tabs
            tab_y = 400
            tab_w, tab_h = 120, 46
            for i, _ in enumerate(THEMES):
                tab = pygame.Rect(40 + i * (tab_w + 10), tab_y, tab_w, tab_h)
                if tab.collidepoint(event.pos):
                    self.theme_idx = i
                    return
            if self.play_rect.collidepoint(event.pos):
                theme = THEMES[self.theme_idx]
                self.manager.set_current(theme, self.level_idx)
                if theme == "Day" and self.level_idx < 9:
                    self.next_scene = PlayScene(theme=theme, level=self.level_idx)
                else:
                    self.next_scene = UnitSelectScene(theme=theme, level=self.level_idx)

    def update(self, dt: float) -> None:
        pass

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((110, 160, 210))
        pygame.draw.rect(screen, (110, 160, 110), (0, WINDOW_HEIGHT - 180, WINDOW_WIDTH, 180))
        title = self.font_big.render("Adventure", True, (20, 30, 20))
        screen.blit(title, (40, 36))
        # level cards
        theme = THEMES[self.theme_idx]
        unlocked = self.manager.unlocked.get(theme, 1)
        for i, r in enumerate(self.level_rects, start=1):
            enabled = i <= unlocked
            border = (240, 240, 240) if enabled else (130, 130, 130)
            face = (250, 250, 250) if enabled else (170, 170, 170)
            pygame.draw.rect(screen, border, r, border_radius=10)
            inner = r.inflate(-8, -8)
            pygame.draw.rect(screen, face, inner, border_radius=8)
            text = self.font.render(f"Level {i}", True, (20, 20, 20))
            screen.blit(text, (inner.centerx - text.get_width() // 2, inner.centery - 10))
            if i == self.level_idx:
                pygame.draw.rect(screen, (80, 160, 80), r, 3, border_radius=10)

        # theme tabs
        tab_y = 400
        tab_w, tab_h = 120, 46
        for i, t in enumerate(THEMES):
            rect = pygame.Rect(40 + i * (tab_w + 10), tab_y, tab_w, tab_h)
            base = (60, 60, 60)
            color = (100, 160, 100) if i == self.theme_idx else base
            pygame.draw.rect(screen, color, rect, border_radius=10)
            inner = rect.inflate(-8, -8)
            pygame.draw.rect(screen, (235, 235, 235), inner, border_radius=10)
            label = self.font.render(t, True, (20, 30, 20))
            screen.blit(label, (inner.centerx - label.get_width() // 2, inner.centery - label.get_height() // 2))

        # play button
        pygame.draw.rect(screen, (70, 120, 60), self.play_rect, border_radius=10)
        inner = self.play_rect.inflate(-6, -6)
        pygame.draw.rect(screen, (200, 240, 180), inner, border_radius=10)
        play_txt = self.font_big.render("PLAY", True, (20, 40, 20))
        screen.blit(play_txt, (inner.centerx - play_txt.get_width() // 2, inner.centery - play_txt.get_height() // 2))


class UnitSelectScene(Scene):
    def __init__(self, theme: str, level: int) -> None:
        super().__init__()
        self.next_scene = None
        self.theme = theme
        self.level = level
        self.font_title = pygame.font.SysFont(None, 40, bold=True)
        self.font = pygame.font.SysFont(None, 26)
        # Get unlocked units for this level to display
        unlocked_keys = self._get_unlocked_units()
        if self.theme == "Night" and self.level in (1, 2, 3):
            # Special ordering for Night level 1 as requested
            day_units = [u for u in UNIT_DEFS if u["key"] in unlocked_keys and u["key"] not in ("bubble_shooter", "shield_defender", "night_stalker")]
            bubble_shooter = next((u for u in UNIT_DEFS if u["key"] == "bubble_shooter"), None)
            shield_defender = next((u for u in UNIT_DEFS if u["key"] == "shield_defender"), None)
            night_stalker = next((u for u in UNIT_DEFS if u["key"] == "night_stalker"), None)
            
            self.all_units = day_units + [{"key": "shovel", "name": "Shovel", "cost": 0, "cooldown": 0}]
            if bubble_shooter:
                self.all_units.append(bubble_shooter)
            if self.level >= 2 and shield_defender:
                self.all_units.append(shield_defender)
            if self.level >= 3 and night_stalker:
                self.all_units.append(night_stalker)
        else:
            self.all_units = [u for u in UNIT_DEFS if u["key"] in unlocked_keys]
            if (self.theme == "Day" and self.level >= 10):
                self.all_units.append({"key": "shovel", "name": "Shovel", "cost": 0, "cooldown": 0})
        self.max_select = 8
        self.selected: set[str] = set()
        # icon cache
        self._icons: dict[str, pygame.Surface] = {}
        # layout
        self._cells: list[tuple[str, pygame.Rect]] = []
        self._build_grid()
        self.play_rect = pygame.Rect(WINDOW_WIDTH - 200, WINDOW_HEIGHT - 70, 160, 48)
        self.back_rect = pygame.Rect(40, WINDOW_HEIGHT - 70, 160, 48)

    def _get_unlocked_units(self) -> list[str]:
        """Helper to get unlocked units based on current level and theme."""
        # This logic is duplicated from PlayScene to be used here.
        # Day theme (levels 1-10)
        if self.theme == "Day":
            if self.level == 1: return ["shooter"]
            if self.level == 2: return ["shooter", "generator"]
            if self.level == 3: return ["shooter", "generator", "wall"]
            if self.level == 4: return ["shooter", "generator", "wall", "frozen"]
            if self.level == 5: return ["shooter", "generator", "wall", "frozen", "bomb"]
            if self.level == 6: return ["shooter", "generator", "wall", "frozen", "bomb", "charger"]
            if self.level == 7: return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank"]
            if self.level == 8: return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun"]
            if self.level == 9: return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus"]
            if self.level >= 10: return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus"]
        # Night theme (starts after Day level 10)
        elif self.theme == "Night":
            if self.level == 1:
                return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus", "bubble_shooter"]
            if self.level == 2:
                return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus", "bubble_shooter", "shield_defender"]
            if self.level == 3:
                return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus", "bubble_shooter", "shield_defender", "night_stalker"]
            if self.level == 4:
                return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus", "bubble_shooter", "shield_defender", "night_stalker", "shadow_healer"]
            if self.level == 5:
                return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus", "bubble_shooter", "shield_defender", "night_stalker", "shadow_healer", "ice_shroom"]
            if self.level == 6:
                return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus", "bubble_shooter", "shield_defender", "night_stalker", "shadow_healer", "ice_shroom", "gatling_pea"]
            if self.level == 7:
                return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus", "bubble_shooter", "shield_defender", "night_stalker", "shadow_healer", "ice_shroom", "gatling_pea", "doom_shroom"]
            if self.level == 8:
                return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus", "bubble_shooter", "shield_defender", "night_stalker", "shadow_healer", "ice_shroom", "gatling_pea", "doom_shroom", "sun_shroom"]
            if self.level == 9:
                return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus", "bubble_shooter", "shield_defender", "night_stalker", "shadow_healer", "ice_shroom", "gatling_pea", "doom_shroom", "sun_shroom", "puff_shroom"]
            if self.level >= 10:
                return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus", "bubble_shooter", "shield_defender", "night_stalker", "shadow_healer", "ice_shroom", "gatling_pea", "doom_shroom", "sun_shroom", "puff_shroom", "scaredy_shroom"]
        elif self.theme == "Pool":
            if self.level == 1:
                return [
                    "shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus",
                    "bubble_shooter", "shield_defender", "night_stalker", "shadow_healer", "ice_shroom",
                    "gatling_pea", "doom_shroom", "sun_shroom", "puff_shroom", "scaredy_shroom", "leaf", "tangle_kelp"
                ]
            if self.level == 2:
                return [
                    "shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus",
                    "bubble_shooter", "shield_defender", "night_stalker", "shadow_healer", "ice_shroom",
                    "gatling_pea", "doom_shroom", "sun_shroom", "puff_shroom", "scaredy_shroom", "leaf", "tangle_kelp"
                ]
            if self.level == 3:
                return [
                    "shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus", "shovel",
                    "bubble_shooter", "shield_defender", "night_stalker", "shadow_healer", "ice_shroom",
                    "gatling_pea", "doom_shroom", "sun_shroom", "puff_shroom", "scaredy_shroom", "leaf", "tangle_kelp", "sea_shroom"
                ]
            if self.level == 4:
                return [
                    "shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus", "shovel",
                    "bubble_shooter", "shield_defender", "night_stalker", "shadow_healer", "ice_shroom",
                    "gatling_pea", "doom_shroom", "sun_shroom", "puff_shroom", "scaredy_shroom", "leaf", "tangle_kelp", "sea_shroom", "cattail"
                ]
            if self.level >= 5:
                return [
                    "shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus", "shovel", "bubble_shooter", "shield_defender", "night_stalker", "shadow_healer", "ice_shroom", "gatling_pea", "doom_shroom", "sun_shroom", "puff_shroom", "scaredy_shroom", "leaf", "tangle_kelp", "sea_shroom", "cattail", "spikerock"
                ]
            return ["shooter", "leaf", "tangle_kelp", "sea_shroom"] # Fallback for other pool levels
        # Fallback for other themes like Fog, Roof
        elif self.theme in ("Fog", "Roof"):
            return ["shooter", "generator", "wall", "frozen", "bomb"]
        
        return ["shooter"]

    def _build_grid(self) -> None:
        self._cells = []
        cols = 4
        card_w, card_h = 200, 64
        gap_x, gap_y = 16, 12
        start_x, start_y = 40, 100
        x, y = start_x, start_y
        for unit in self.all_units:
            rect = pygame.Rect(x, y, card_w, card_h)
            self._cells.append((unit["key"], rect))
            x += card_w + gap_x
            if len(self._cells) % cols == 0:
                x = start_x
                y += card_h + gap_y

    def _make_icon(self, key: str) -> pygame.Surface:
        if key in self._icons:
            return self._icons[key]
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
        elif key == "night_stalker":
            base = draw_night_stalker()
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
        # scale for card
        icon = pygame.transform.smoothscale(base, (44, 44))
        self._icons[key] = icon
        return icon

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_scene = LevelSelectScene()
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._start_if_any()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_rect.collidepoint(event.pos):
                self.next_scene = LevelSelectScene()
                return
            if self.play_rect.collidepoint(event.pos):
                self._start_if_any()
                return
            for key, rect in self._cells:
                if rect.collidepoint(event.pos):
                    if key in self.selected:
                        self.selected.remove(key)
                    else:
                        if len(self.selected) < self.max_select:
                            self.selected.add(key)

    def _start_if_any(self) -> None:
        if len(self.selected) == 0:
            return
        chosen = list(self.selected)
        self.next_scene = PlayScene(theme=self.theme, level=self.level, unit_keys=chosen)

    def update(self, dt: float) -> None:
        pass

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((105, 150, 200))
        pygame.draw.rect(screen, (110, 160, 110), (0, WINDOW_HEIGHT - 180, WINDOW_WIDTH, 180))
        title = self.font_title.render("Choose up to 8 units", True, (20, 30, 20))
        screen.blit(title, (40, 36))
        # draw cards with icons
        for key, rect in self._cells:
            is_sel = key in self.selected
            border = (80, 160, 80) if is_sel else (60, 60, 60)
            face = (235, 235, 235) if is_sel else (250, 250, 250)
            pygame.draw.rect(screen, border, rect, border_radius=10)
            inner = rect.inflate(-6, -6)
            pygame.draw.rect(screen, face, inner, border_radius=8)
            # icon on left
            icon = self._make_icon(key)
            icon_pos = (inner.x + 10, inner.centery - icon.get_height() // 2)
            screen.blit(icon, icon_pos)
            # name text next to icon
            name = next((u["name"] for u in self.all_units if u["key"] == key), key)
            txt = self.font.render(name, True, (20, 20, 20))
            text_x = icon_pos[0] + icon.get_width() + 10
            text_y = inner.centery - txt.get_height() // 2
            screen.blit(txt, (text_x, text_y))

        # selected count
        count_txt = self.font.render(f"Selected: {len(self.selected)}/{self.max_select}", True, (20, 30, 20))
        screen.blit(count_txt, (40, WINDOW_HEIGHT - 110))

        # back / play buttons
        pygame.draw.rect(screen, (120, 120, 120), self.back_rect, border_radius=10)
        pygame.draw.rect(screen, (70, 120, 60) if self.selected else (120, 120, 120), self.play_rect, border_radius=10)
        back_txt = self.font.render("BACK", True, (20, 20, 20))
        play_txt = self.font.render("PLAY", True, (20, 40, 20))
        back_inner = self.back_rect.inflate(-6, -6)
        play_inner = self.play_rect.inflate(-6, -6)
        pygame.draw.rect(screen, (230, 230, 230), back_inner, border_radius=10)
        pygame.draw.rect(screen, (200, 240, 180) if self.selected else (220, 220, 220), play_inner, border_radius=10)
        screen.blit(back_txt, (back_inner.centerx - back_txt.get_width() // 2, back_inner.centery - back_txt.get_height() // 2))
        screen.blit(play_txt, (play_inner.centerx - play_txt.get_width() // 2, play_inner.centery - play_txt.get_height() // 2))

class LevelCompleteScene(Scene):
    def __init__(self, theme: str, level: int, power_up: str) -> None:
        super().__init__()
        self.next_scene = None
        self.theme = theme
        self.level = level
        self.power_up = power_up
        self.font_big = pygame.font.SysFont(None, 48, bold=True)
        self.font = pygame.font.SysFont(None, 32)
        self.font_small = pygame.font.SysFont(None, 24)
        self.timer = 0.0
        self.auto_time = 4.0
        self.animation_timer = 0.0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                self.next_scene = LevelSelectScene()

    def update(self, dt: float) -> None:
        self.timer += dt
        self.animation_timer += dt
        if self.timer >= self.auto_time and self.next_scene is None:
            # Automatically advance to next level instead of level select
            from game.levels import LevelManager
            manager = LevelManager()
            current = manager.get_current()
            if current.index < LEVELS_PER_THEME:
                # Go to next level automatically
                if current.theme == "Day" and (current.index + 1) < 9:
                    self.next_scene = PlayScene(theme=current.theme, level=current.index + 1)
                else:
                    self.next_scene = UnitSelectScene(theme=current.theme, level=current.index + 1)
            else:
                # If at max level, go to level select
                self.next_scene = LevelSelectScene()

    def draw(self, screen: pygame.Surface) -> None:
        # Animated background with celebration effect
        bg_color = (50 + int(20 * (self.animation_timer % 1.0)), 100, 50)
        screen.fill(bg_color)
        
        # Celebration particles
        import random
        for _ in range(20):
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT)
            color = random.choice([(255, 255, 100), (255, 100, 100), (100, 255, 100), (100, 100, 255)])
            pygame.draw.circle(screen, color, (x, y), 2)
        
        # Animated level complete message with larger font
        title = self.font_big.render(f"🎉 LEVEL {self.level} COMPLETED! 🎉", True, (255, 255, 255))
        title_x = WINDOW_WIDTH // 2 - title.get_width() // 2
        title_y = 80 + int(15 * (self.animation_timer % 0.5))
        screen.blit(title, (title_x, title_y))
        
        # Next level message
        next_level_text = self.font.render(f"🚀 Moving to Level {self.level + 1}...", True, (100, 255, 100))
        next_x = WINDOW_WIDTH // 2 - next_level_text.get_width() // 2
        next_y = 160 + int(5 * (self.animation_timer % 0.4))
        screen.blit(next_level_text, (next_x, next_y))
        
        # Animated border effect
        border_width = 5
        border_color = (255, 255, 100, 150)
        border_alpha = int(100 + 50 * (self.animation_timer % 1.0))
        
        # Draw animate4d border
        pygame.draw.rect(screen, (255, 255, 100), (0, 0, WINDOW_WIDTH, border_width))
        pygame.draw.rect(screen, (255, 255, 100), (0, WINDOW_HEIGHT - border_width, WINDOW_WIDTH, border_width))
        pygame.draw.rect(screen, (255, 255, 100), (0, 0, border_width, WINDOW_HEIGHT))
        pygame.draw.rect(screen, (255, 255, 100), (WINDOW_WIDTH - border_width, 0, border_width, WINDOW_HEIGHT))
        
        # Continue message
        continue_text = self.font_small.render("Press any key to continue...", True, (200, 200, 200))
        continue_x = WINDOW_WIDTH // 2 - continue_text.get_width() // 2
        continue_y = 210 + int(3 * (self.animation_timer % 0.2))
        screen.blit(continue_text, (continue_x, continue_y))


class PlayScene(Scene):
    def __init__(self, theme: str = "Day", level: int | None = None, unit_keys: list[str] | None = None) -> None:
        super().__init__()
        self.theme = theme
        self.level = level or 1
        self.next_scene = None
        self.grid_adjustment_mode = False # Grid is set, no need for adjustment mode

        
        # Screen shake attributes
        self.shake_magnitude = 0
        self.shake_timer = 0.0

        
        # Get level configuration
        from game.config import LEVEL_CONFIGS
        self.level_config = LEVEL_CONFIGS.get(self.level, LEVEL_CONFIGS[1])
        self.robots_to_spawn = self.level_config["robot_count"]
        self.robots_spawned = 0
        self.robots_killed = 0
        # Ensure only 5 lanes are used (0-4)
        self.active_lanes = {0, 1, 2, 3, 4}
        self.completed_lanes = set()
        
        # Lane progress tracking
        self.lane_progress = {lane: 0.0 for lane in self.active_lanes}  # 0.0 to 1.0
        self.lane_robot_counts = {lane: 0 for lane in self.active_lanes}  # robots spawned per lane
        self.lane_kill_counts = {lane: 0 for lane in self.active_lanes}   # robots killed per lane
        
        # Visual effects
        self.kill_effects = []  # List of kill effect particles
        self.completion_message_timer = 0.0  # Timer for completion message
        self.show_completion_message = False  # Flag to show completion message
        

        
        # Choose units for HUD
        if unit_keys is not None and len(unit_keys) > 0:
            unit_defs = [u for u in UNIT_DEFS if u["key"] in unit_keys][:8]
        else:
            # fallback to previous unlock flow if none provided
            unlocked_units = self._get_unlocked_units()
            unit_defs = [u for u in UNIT_DEFS if u["key"] in unlocked_units][:8]

        
        # Vertical HUD for Day theme, horizontal for others
        is_vertical_hud = self.theme == "Day"
        # For left-oriented HUD we need the screen height for vertical scroll calculations.
        hud_primary_size = WINDOW_HEIGHT if is_vertical_hud else WINDOW_WIDTH
        enable_shovel = "shovel" in (unit_keys or [])
        self.hud = HUD(hud_primary_size, orientation="left" if is_vertical_hud else "top", unit_defs=unit_defs, enable_shovel=enable_shovel)
        
        # Adjust grid origin to align with background lawn art
        if theme in ("Day", "Night"):
            # Use the same placement for Day and Night so mowers align by the house
            self.grid_origin = [360, 140]
        elif self.theme == "Pool":
            # Shifted right 2.5 tiles and down 0.5 tiles to better fit the background art
            self.grid_origin = [int(64 + (2.5 * TILE_SIZE)), 136]
        else:
            self.grid_origin = [64, 96]
        self.grid = Grid(*self.grid_origin)
        self.tile_size = TILE_SIZE # Add tile_size attribute for dynamic adjustment
        self.humans = pygame.sprite.Group()
        self.robots = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.generators = pygame.sprite.Group()
        self.bombs = pygame.sprite.Group()
        self.energy_drops = pygame.sprite.Group()
        self.mowers = pygame.sprite.Group()
        self.craters = pygame.sprite.Group()
        self.effects = pygame.sprite.Group() # For visual effects like explosions
        self.font = pygame.font.SysFont(None, 24)
        # Set initial spawn timer to 50 seconds for first robot
        # Add some randomness to prevent predictable timing
        base_delay = 50.0  # Base 50 second delay
        random_offset = random.uniform(-2.0, 5.0)  # -2 to +5 seconds variation
        self.spawn_timer = max(45.0, base_delay + random_offset)  # Minimum 45 seconds
        self.elapsed = 0.0
        self.lives = 3
        self.fog_surface = None
        self.water_rows = set()
        self.energy = START_ENERGY
        # Sky drop interval (reduced energy at night)
        if self.level == 1:
            # Special faster energy drops for the first level to help the player start
            self.sky_interval = (2.0, 8.0)
        else:
            self.sky_interval = SKY_DROP_INTERVAL
            if theme == "Night":
                self.sky_interval = (SKY_DROP_INTERVAL[0] * 1.8, SKY_DROP_INTERVAL[1] * 1.8)
        self.sky_timer = random.uniform(*self.sky_interval)
        # Optional background art for Day and Night themes
        self.bg_image: pygame.Surface | None = None
        if self.theme == "Day":
            try:
                base = os.path.dirname(__file__)
                # Try to load the specific Day background image
                for name in ("day_background.jpg", "day_background.png", "day_bg.jpg", "day_bg.png", "bg_day.jpg", "bg_day.png", "day_level1.jpg", "day_level1.png"):
                    p = os.path.join(base, "images", name)
                    if os.path.exists(p):
                        img = pygame.image.load(p).convert()
                        self.bg_image = pygame.transform.smoothscale(img, (WINDOW_WIDTH, WINDOW_HEIGHT))
                        break
            except Exception:
                self.bg_image = None
        elif self.theme == "Night":
            try:
                base = os.path.dirname(__file__)
                # Try multiple possible Night background filenames
                night_names = ("Night.png", "night.png", "Night.jpg", "night.jpg", "Night_bg.png", "night_bg.png")
                for name in night_names:
                    p = os.path.join(base, "images", name)
                    if os.path.exists(p):
                        img = pygame.image.load(p).convert()
                        self.bg_image = pygame.transform.smoothscale(img, (WINDOW_WIDTH, WINDOW_HEIGHT))
                        print(f"🌙 Loaded Night background: {p}")
                        break
                if self.bg_image is None:
                    print("❌ Night background not found (tried Night.png, night.png, Night.jpg, night.jpg, Night_bg.png, night_bg.png)")
            except Exception as e:
                print(f"⚠️ Error loading Night background: {e}")
                self.bg_image = None
        elif self.theme == "Pool":
            try:
                base = os.path.dirname(__file__)
                # Try to load the Pool background image
                pool_names = ("pool_bg.jpeg", "pool_bg.jpg", "pool_bg.png", "pool.jpeg", "pool.jpg", "pool.png", "bg_pool.jpeg", "bg_pool.jpg", "bg_pool.png")
                for name in pool_names:
                    p = os.path.join(base, "images", name)
                    if os.path.exists(p):
                        img = pygame.image.load(p).convert()
                        self.bg_image = pygame.transform.smoothscale(img, (WINDOW_WIDTH, WINDOW_HEIGHT))
                        print(f"🌊 Loaded Pool background: {p}")
                        break
            except Exception as e:
                print(f"⚠️ Error loading Pool background: {e}")
                self.bg_image = None

        if self.theme == "Fog":
            self.fog_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            self.fog_surface.fill((200, 200, 200, 90))
        # Place lawn mowers on each lane
        for lane in range(NUM_LANES):
            y = self.grid_origin[1] + lane * TILE_SIZE + TILE_SIZE // 2
            mower_x = self.grid_origin[0] - 40
            # In Night theme, place mower ~1.5 tiles further behind (slightly forward vs previous)
            if self.theme == "Night":
                mower_x -= TILE_SIZE * 3 // 2
            self.mowers.add(Mower((mower_x, y), speed=MOWER_SPEED))

    def _get_unlocked_units(self) -> list[str]:
        """Get list of unlocked units based on current level and theme"""
        # Day theme (levels 1-10)
        if self.theme == "Day":
            if self.level == 1:
                return ["shooter"]
            if self.level == 2:
                return ["shooter", "generator"]
            if self.level == 3:
                return ["shooter", "generator", "wall"]
            if self.level == 4:
                return ["shooter", "generator", "wall", "frozen"]
            if self.level == 5:
                return ["shooter", "generator", "wall", "frozen", "bomb"]
            if self.level == 6:
                return ["shooter", "generator", "wall", "frozen", "bomb", "charger"]
            if self.level == 7:
                return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank"]
            if self.level == 8:
                return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun"]
            if self.level == 9:
                return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus"]
            if self.level >= 10:
                return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus"]
        
        # Night theme (starts after Day level 10)
        elif self.theme == "Night":
            if self.level == 1: # Custom units for Night level 1
                return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus", "bubble_shooter"]
            if self.level == 2: # Custom units for Night level 2
                return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus", "bubble_shooter", "shield_defender"]
            if self.level == 3: # Custom units for Night level 3
                return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus", "bubble_shooter", "shield_defender", "night_stalker"]
            if self.level == 4: # Custom units for Night level 4
                return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus", "bubble_shooter", "shield_defender", "night_stalker", "shadow_healer"]
            if self.level == 5: # Custom units for Night level 5
                return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus", "bubble_shooter", "shield_defender", "night_stalker", "shadow_healer", "ice_shroom"]
            if self.level == 6: # Custom units for Night level 6
                return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus", "bubble_shooter", "shield_defender", "night_stalker", "shadow_healer", "ice_shroom", "gatling_pea"]
            if self.level == 7: # Custom units for Night level 7
                return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus", "bubble_shooter", "shield_defender", "night_stalker", "shadow_healer", "ice_shroom", "gatling_pea", "doom_shroom"]
            if self.level == 8: # Custom units for Night level 8
                return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus", "bubble_shooter", "shield_defender", "night_stalker", "shadow_healer", "ice_shroom", "gatling_pea", "doom_shroom", "sun_shroom"]
            if self.level == 9: # Custom units for Night level 9
                return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus", "bubble_shooter", "shield_defender", "night_stalker", "shadow_healer", "ice_shroom", "gatling_pea", "doom_shroom", "sun_shroom", "puff_shroom"]
            if self.level >= 10: # Custom units for Night level 10+
                return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus", "bubble_shooter", "shield_defender", "night_stalker", "shadow_healer", "ice_shroom", "gatling_pea", "doom_shroom", "sun_shroom", "puff_shroom", "scaredy_shroom"]
        
        # Pool theme unlocks
        elif self.theme == "Pool":
            return ["shooter", "generator", "wall", "frozen", "bomb", "charger", "tank", "laser_gun", "virus", "shovel", "bubble_shooter", "shield_defender", "night_stalker", "shadow_healer", "ice_shroom", "gatling_pea", "doom_shroom", "sun_shroom", "puff_shroom", "scaredy_shroom", "leaf", "tangle_kelp", "sea_shroom", "cattail", "spikerock", "sea_mine"]
        
        return ["shooter"]

    def _complete_level(self) -> None:
        """Complete the current level and unlock the next one"""
        from game.levels import LevelManager
        manager = LevelManager()
        manager.complete_current()
        
        # Special handling for Night theme level completions
        if self.theme == "Night" and self.level == 1:
            # Shield Defender gets unlocked when Night level 1 is completed
            print(f"🎉 NIGHT LEVEL 1 COMPLETED! SHIELD DEFENDER UNLOCKED! 🛡️")
        
        # Check if we should move to next theme
        if self.theme == "Day" and self.level >= 10:
            # Move to Night theme level 1
            manager.set_current("Night", 1)
        elif self.level < LEVELS_PER_THEME:
            # Continue in same theme
            manager.set_current(self.theme, self.level + 1)

    def handle_event(self, event: pygame.event.Event) -> None:
        # Pass all events to the HUD first
        self.hud.handle_event(event)
        
        # Handle placing units with left-click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # If the click was on the HUD, the HUD handles it, so we don't place a unit.
            if not self.hud.is_pos_on_hud(event.pos):
                # This was calling a non-existent method. Let's integrate the logic here.
                pos = event.pos
                tile = self.grid.get_tile_at_pos(pos)
                if tile is None:
                    return

                # Check if tile is occupied by any existing unit
                is_occupied = any(ent.rect.colliderect(tile.rect) for ent in self.humans) or \
                              any(ent.rect.colliderect(tile.rect) for ent in self.generators) or \
                              any(ent.rect.colliderect(tile.rect) for ent in self.bombs)

                # Check if tile is blocked by a crater
                is_cratered = any(crater.rect.colliderect(tile.rect) for crater in self.craters)

                # Handle Shovel mode first and exit
                if self.hud.shovel_mode and self.hud.enable_shovel:
                    for group in (self.humans, self.generators, self.bombs):
                        for ent in list(group):
                            if ent.rect.colliderect(tile.rect):
                                ent.kill()
                                return
                    return # Exit after attempting to shovel, even if nothing was there

                # Special placement logic for Cattail (upgrade for Lily Pad)
                idx = self.hud.selected_index
                unit = getattr(self.hud, "unit_defs", UNIT_DEFS)[idx]
                key = unit["key"]
                if key == "cattail":
                    # Must be placed on a Lily Pad (Leaf)
                    lily_pad_found = any(isinstance(ent, Leaf) and ent.rect.colliderect(tile.rect) for ent in self.humans)
                    if not lily_pad_found:
                        return # Can't place Cattail here
                elif key == "spikerock":
                    # Must be placed on a WallHuman
                    wall_found = any(isinstance(ent, WallHuman) and not isinstance(ent, Spikerock) and ent.rect.colliderect(tile.rect) for ent in self.humans)
                    if not wall_found:
                        return # Can't place Spikerock here

                if is_occupied or is_cratered:
                    return

                idx = self.hud.selected_index
                unit = getattr(self.hud, "unit_defs", UNIT_DEFS)[idx]
                key = unit["key"]

                # Water restriction
                if tile.row in self.water_rows and key not in ("leaf", "tangle_kelp", "sea_shroom", "cattail", "sea_mine"):
                    return

                # Get selected unit and check cost/cooldown
                if self.energy < unit["cost"] or self.hud.cooldowns[idx] > 0:
                    return

                # All checks passed, place the unit
                self.energy -= unit["cost"]
                self.hud.cooldowns[idx] = unit["cooldown"]
                self._place_unit_at_tile(tile, key)
                return # Placement handled
        
        # Handle collecting energy with right-click
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3: # right-click collects energy drops if clicked on
            for drop in list(self.energy_drops):
                if hasattr(drop, 'collect_rect') and drop.collect_rect.collidepoint(event.pos):
                    self.energy += drop.value
                    drop.kill()
        
        # Handle screen shake event
        elif event.type == SCREEN_SHAKE_EVENT:
            self.shake_magnitude = getattr(event, 'magnitude', 10)
            self.shake_timer = getattr(event, 'duration', 0.4)

    def _place_unit_at_tile(self, tile, key: str) -> None:
        center = tile.rect.center
        # Adjust center based on dynamic tile size
        center = (self.grid_origin[0] + tile.col * self.tile_size + self.tile_size // 2,
                  self.grid_origin[1] + tile.row * self.tile_size + self.tile_size // 2)

        lane_row = tile.row

        # Create and add the unit to the appropriate group
        if key == "shooter": self.humans.add(Human(center, lane_row=lane_row))
        elif key == "wall": self.humans.add(WallHuman(center))
        elif key in ("generator", "energy_generator", "Energy_generator", "Energy generator"): self.generators.add(Generator(center))
        elif key == "bomb": self.bombs.add(Bomb(center, lane_row=lane_row))
        elif key == "frozen": self.humans.add(FrozenShooter(center, lane_row=lane_row))
        elif key == "charger": self.humans.add(Charger(center))
        elif key == "tank": self.humans.add(Tank(center, lane_row=lane_row))
        elif key == "laser_gun": self.humans.add(LaserGun(center, lane_row=lane_row))
        elif key == "virus": self.humans.add(Virus(center))
        elif key == "bubble_shooter": self.humans.add(BubbleShooter(center, lane_row=lane_row))
        elif key == "shield_defender": self.humans.add(ShieldDefender(center))
        elif key == "night_stalker": self.humans.add(NightStalker(center, lane_row=lane_row))
        elif key == "shadow_healer": self.humans.add(ShadowHealer(center))
        elif key == "ice_shroom": self.humans.add(IceShroom(center))
        elif key == "gatling_pea": self.humans.add(GatlingPea(center, lane_row=lane_row))
        elif key == "doom_shroom": self.humans.add(DoomShroom(center, self.craters, self.effects))
        elif key == "sun_shroom": self.generators.add(SunShroom(center))
        elif key == "puff_shroom": self.humans.add(PuffShroom(center, lane_row=lane_row))
        elif key == "scaredy_shroom": self.humans.add(ScaredyShroom(center, lane_row=lane_row))
        elif key == "leaf": self.humans.add(Leaf(center))
        elif key == "tangle_kelp": self.humans.add(TangleKelp(center))
        elif key == "sea_shroom": self.humans.add(SeaShroom(center, lane_row=lane_row))
        elif key == "cattail": self.humans.add(Cattail(center))
        elif key == "spikerock": self.humans.add(Spikerock(center))
        elif key == "sea_mine": self.humans.add(SeaMine(center))

    def update(self, dt: float) -> None:
        self.elapsed += dt
        if self.grid_adjustment_mode:
            # In adjustment mode, we don't update game logic.
            return

        self.hud.tick_cooldowns(dt)
        
        # Update screen shake timer
        if self.shake_timer > 0:
            self.shake_timer = max(0.0, self.shake_timer - dt)
            if self.shake_timer == 0.0:
                self.shake_magnitude = 0
        
        all_units = pygame.sprite.Group(self.humans, self.generators, self.bombs)
        
        # Update kill effects
        self._update_kill_effects(dt)
        
        # Update general visual effects
        self.effects.update(dt)
        

        
        # Spawn robots based on level configuration
        if self.robots_spawned < self.robots_to_spawn:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0.0:
                # Check if we should trigger the final wave
                final_wave_threshold = int(self.robots_to_spawn * 0.8)  # 80% of total robots
                if self.robots_spawned >= final_wave_threshold and not hasattr(self, '_final_wave_triggered'):
                    # Trigger final wave - spawn many robots quickly
                    self._final_wave_triggered = True
                    # Calculate remaining robots to spawn for the final wave
                    self._final_wave_robots = self.robots_to_spawn - self.robots_spawned
                    self._final_wave_spawned = 0
                    self._final_wave_timer = 0.0
                    self._final_wave_message_timer = 0.0  # Timer for showing the message
                    print(f"🚨 FINAL WAVE! Spawning {self._final_wave_robots} robots!")
                
                if hasattr(self, '_final_wave_triggered') and self._final_wave_triggered:
                    # Final wave spawning logic - spawn robots in ALL lanes simultaneously
                    if self._final_wave_spawned < self._final_wave_robots:
                        self._final_wave_timer += dt
                        if self._final_wave_timer >= 0.3:  # Spawn every 0.3 seconds for chaos
                            self._final_wave_timer = 0.0
                            
                            # Spawn robots in ALL active lanes at once
                            available_lanes = list(self.active_lanes - self.completed_lanes)
                            for lane in available_lanes:
                                spawn_x = self.grid_origin[0] + (TILES_PER_LANE - 1) * TILE_SIZE + TILE_SIZE
                                spawn_y = self.grid_origin[1] + lane * TILE_SIZE + TILE_SIZE // 2
                                
                                # Mix of robot types in final wave
                                robot_type = random.choice(["robot", "fast", "fast", "white_blue"])  # More fast robots
                                if robot_type == "fast":
                                    self.robots.add(FastRobot((spawn_x, spawn_y), lane_row=lane))
                                elif robot_type == "white_blue":
                                    self.robots.add(WhiteBlueRobot((spawn_x, spawn_y), lane_row=lane))
                                else:
                                    self.robots.add(Robot((spawn_x, spawn_y), lane_row=lane))
                                self.robots_spawned += 1
                                self.lane_robot_counts[lane] += 1
                                print(f"🚨 Final wave robot {self._final_wave_spawned}/{self._final_wave_robots} spawned in lane {lane}")
                    else:
                        # Final wave complete, reset spawn timer for any remaining robots
                        self.spawn_timer = 2.0
                else:
                    # Normal spawning logic
                    # Choose a random active lane
                    available_lanes = list(self.active_lanes - self.completed_lanes)
                    if available_lanes:
                        # More random lane selection for higher levels
                        if self.level >= 4:
                            # Prevent spawning in the same lane too frequently
                            if hasattr(self, '_last_spawn_lanes'):
                                # Avoid spawning in recently used lanes
                                recent_lanes = self._last_spawn_lanes[-2:] if len(self._last_spawn_lanes) >= 2 else []
                                available_lanes_filtered = [l for l in available_lanes if l not in recent_lanes]
                                
                                if available_lanes_filtered:
                                    lane = random.choice(available_lanes_filtered)
                                else:
                                    lane = random.choice(available_lanes)
                            else:
                                self._last_spawn_lanes = []
                                lane = random.choice(available_lanes)
                            
                            # Track spawn lanes for better distribution
                            self._last_spawn_lanes.append(lane)
                            if len(self._last_spawn_lanes) > 4:  # Keep only last 4 spawns
                                self._last_spawn_lanes.pop(0)
                        else:
                            lane = random.choice(available_lanes)
                        
                        # Check if any robot in the same lane is too close
                        spawn_x = self.grid_origin[0] + (TILES_PER_LANE - 1) * TILE_SIZE + TILE_SIZE
                        spawn_y = self.grid_origin[1] + lane * TILE_SIZE + TILE_SIZE // 2
                        
                        can_spawn = True
                        for robot in self.robots:
                            if robot.lane_row == lane:
                                distance = abs(robot.rect.centerx - spawn_x)
                                if distance < TILE_SIZE * 0.8:
                                    can_spawn = False
                                    break
                        
                        if can_spawn:
                            # Robot type selection based on spawn count
                            if self.robots_spawned < 3:
                                # First 3 robots are always normal
                                robot_type = "robot"
                            elif self.robots_spawned < 7:
                                # After 3 robots, start mixing in fast robots
                                robot_type = random.choice(["robot", "robot", "fast"])  # 2/3 normal, 1/3 fast
                            else:
                                # After 7 robots, more variety
                                robot_type = random.choice(["robot", "fast", "white_blue"])

                            if robot_type == "fast":
                                self.robots.add(FastRobot((spawn_x, spawn_y), lane_row=lane))
                            elif robot_type == "white_blue":
                                self.robots.add(WhiteBlueRobot((spawn_x, spawn_y), lane_row=lane))
                            else:
                                self.robots.add(Robot((spawn_x, spawn_y), lane_row=lane))

                            self.robots_spawned += 1
                            self.lane_robot_counts[lane] += 1
                            
                            # Set spawn timer to 10 seconds for next robot spawn
                            # Add some randomness to prevent predictable timing
                            base_delay = 10.0  # Base 10 second delay
                            random_offset = random.uniform(-1.0, 2.0)  # -1 to +2 seconds variation
                            self.spawn_timer = max(8.0, base_delay + random_offset)  # Minimum 8 seconds
                        else:
                            # Try again in a shorter time if we can't spawn
                            self.spawn_timer = 2.0

        # economy sky drops
        self.sky_timer -= dt
        if self.sky_timer <= 0.0:
            self.sky_timer = random.uniform(*self.sky_interval)
            x = random.randint(self.grid_origin[0], self.grid_origin[0] + TILES_PER_LANE * TILE_SIZE)
            y = 64
            # Sky drops use the default energy value
            from game.config import ENERGY_DROP_VALUE
            self.energy_drops.add(EnergyDrop((x, y), value=ENERGY_DROP_VALUE))

        for g in list(self.generators):
            g.update(dt, self.energy_drops)

        # Update bombs so their arm timers count down and they can explode
        for b in list(self.bombs):
            b.update(dt, self.robots)
        # chargers / virus
        for ent in list(self.humans):
            if isinstance(ent, Charger):
                ent.update(dt, self.robots)
            elif isinstance(ent, (Virus, TangleKelp)):
                ent.update(dt, self.robots)
            elif isinstance(ent, NightStalker):
                ent.update(dt, self.robots) # The signature is now (dt, robots)
            elif isinstance(ent, ShadowHealer):
                ent.update(dt, all_units, self.robots)
            elif isinstance(ent, (IceShroom, DoomShroom)):
                ent.update(dt, self.projectiles, self.robots)

        for h in list(self.humans):
            if isinstance(h, (Charger, Virus, NightStalker, ShadowHealer, IceShroom, DoomShroom)):
                # already updated above, skip
                continue
            elif isinstance(h, WallHuman):
                # Walls need robots group to block them
                h.update(dt, None, self.robots)
            else:
                h.update(dt, self.projectiles, self.robots)

        for p in list(self.projectiles):
            p.update(dt, self.robots)

        # robots vs defenders collision for chewing
        for r in list(self.robots):
            # engage nearest overlapping defender/generator/bomb
            if r.chewing_target is None:
                # Do not include bombs here; robots should not chew bombs.
                # Bombs are handled independently by their own timers/updates.
                for group in (self.humans, self.generators):
                    for target in group:
                        if r.rect.colliderect(target.rect):
                            r.chewing_target = target
                            # Ensure robots stop at walls immediately on contact
                            if isinstance(target, WallHuman):
                                r.rect.x = max(r.rect.x, target.rect.right)
                            break
                    if r.chewing_target:
                        break

        # Track robot deaths and update robots in a single loop
        for r in list(self.robots):
            prev_right = r.rect.right
            
            # Check if robot is dead
            if r.alive_hp <= 0:
                self.robots_killed += 1
                if r.lane_row in self.lane_kill_counts:
                    self.lane_kill_counts[r.lane_row] += 1
                    # Update lane progress
                    if self.lane_robot_counts[r.lane_row] > 0:
                        self.lane_progress[r.lane_row] = self.lane_kill_counts[r.lane_row] / self.lane_robot_counts[r.lane_row]
                
                # Add visual feedback for robot death
                self._add_kill_effect(r.rect.center)

                r.kill()
                continue  # Skip further processing for dead robots
            
            # Update live robots
            r.update(dt)
            
            # Early mower trigger: as soon as a robot approaches the home side
            # (enters the first column near the mower), activate the mower in that lane.
            # This avoids waiting until a robot fully escapes the left edge.
            # Check if robot is in first tile - trigger mower if available, or lose game if no mower
            if r.rect.left <= self.grid_origin[0] + TILE_SIZE:
                mower_found = False
                for m in self.mowers:
                    if abs(m.rect.centery - r.rect.centery) < TILE_SIZE // 2:
                        mower_found = True
                        if not getattr(m, "active", False):
                            m.trigger()
                        break
                
                # If no mower exists in this lane, lose game immediately
                if not mower_found:
                    self.next_scene = MenuScene()
                    return
            
            # Check if lane is completed (all robots in this lane are killed)
            if r.lane_row in self.lane_kill_counts and r.lane_row in self.lane_robot_counts:
                if self.lane_kill_counts[r.lane_row] >= self.lane_robot_counts[r.lane_row]:
                    self.completed_lanes.add(r.lane_row)
                    self.lane_progress[r.lane_row] = 1.0  # Mark as fully complete
            
            if prev_right >= 0 and r.rect.right < 0:
                # trigger mower if present and inactive
                lane = int((r.rect.centery - self.grid_origin[1]) // TILE_SIZE)
                for m in self.mowers:
                    if abs(m.rect.centery - r.rect.centery) < TILE_SIZE // 2 and not m.active:
                        m.trigger()
                        break
                self.lives -= 1
                if self.lives <= 0:
                    self.next_scene = MenuScene()
                    return

        # Update mowers so active ones move forward and kill robots on contact
        for m in list(self.mowers):
            m.update(dt, self.robots)

        # Update craters so they time out and disappear
        for c in list(self.craters):
            c.update(dt)

        # Update and remove finished effects
        for effect in list(self.effects):
            effect.update(dt)

        # Win condition: all robots spawned and killed
        if (self.robots_spawned >= self.robots_to_spawn and 
            self.robots_killed >= self.robots_to_spawn and 
            len(self.robots) == 0):

            # Show completion message first
            if not self.show_completion_message:
                self.show_completion_message = True
                self.completion_message_timer = 0.0
                print(f"🎉 LEVEL {self.level} COMPLETED! 🎉")
                
                # Special message for Night levels
                if self.theme == "Night" and self.level == 1:
                    print(f"🎁 New Power Unlocked: SHIELD DEFENDER 🛡️")
                else:
                    print(f"🎁 New Power Unlocked: {self.level_config['power_up']}")
                print(f"🚀 Moving to Level {self.level + 1}...")
            
            # Wait 2 seconds then transition
            # self.completion_message_timer += dt
            # if self.completion_message_timer >= 2.0:
            self._complete_level()
            
            # Special power-up message for Night levels
            if self.theme == "Night" and self.level == 1:
                power_up = "Shield Defender"
            else:
                power_up = self.level_config["power_up"]
            self.next_scene = LevelCompleteScene(self.theme, self.level, power_up)

    def draw(self, screen: pygame.Surface) -> None:
        # Calculate screen shake offset
        offset_x, offset_y = 0, 0
        if self.shake_timer > 0 and not self.grid_adjustment_mode:
            offset_x = random.randint(-self.shake_magnitude, self.shake_magnitude)
            offset_y = random.randint(-self.shake_magnitude, self.shake_magnitude)
        
        render_surface = screen.copy()
        # Background: draw themed art if available; otherwise fallback colors
        if self.bg_image is not None:
            # Works for both Day and Night (and any future themes with art)
            render_surface.blit(self.bg_image, (0, 0))
        else:
            if self.theme == "Day":
                screen.fill((110, 160, 110))
                # Only show grid lines if no background image
                for r in range(NUM_LANES):
                    for c in range(TILES_PER_LANE):
                        rect = pygame.Rect(
                            self.grid_origin[0] + c * TILE_SIZE,
                            self.grid_origin[1] + r * TILE_SIZE,
                            TILE_SIZE,
                            TILE_SIZE,
                        )
                        pygame.draw.rect(screen, (0, 0, 0), rect, 1)
            else:
                render_surface.fill(COLOR_BG.get(self.theme, (40, 40, 40)))
        
        self.grid.draw(render_surface)
        # custom render for spawn/idle effects
        for g in self.generators:
            g.render(render_surface)
        for h in self.humans:
            h.render(render_surface)
        for b in self.bombs:
            b.render(render_surface)
        for r in self.robots:
            r.render(render_surface)
        for p in self.projectiles:
            p.render(render_surface)
        for m in self.mowers:
            m.render(render_surface)
        for c in self.craters:
            c.render(render_surface)
        self.energy_drops.draw(render_surface)
        
        # Draw visual effects on top of most other things
        self.effects.draw(render_surface)
        # Draw kill effects
        self._draw_kill_effects(render_surface)
        
        if self.fog_surface is not None:
            render_surface.blit(self.fog_surface, (0, 0))
        
        # Blit the entire game surface with the shake offset
        screen.fill(COLOR_BG.get(self.theme, (40, 40, 40))) # Clear screen with bg color
        screen.blit(render_surface, (offset_x, offset_y))
        
        # Draw HUD and other static UI elements last, so they don't shake
        self.hud.draw(screen, self.energy)
        # Level info
        level_text = self.font.render(f"Level {self.level} | Robots: {self.robots_killed}/{self.robots_to_spawn} | Energy: {self.energy} | Lives: {self.lives}", True, (20, 20, 20))
        screen.blit(level_text, (8, WINDOW_HEIGHT - 28))

        # Draw level progress bar
        self._draw_level_progress(screen)
        
        # Draw completion message if level is complete
        if self.show_completion_message:
            self._draw_completion_message(screen)
        # Draw final wave message if triggered
        if hasattr(self, '_final_wave_triggered') and self._final_wave_triggered:
            self._draw_final_wave_message(screen)
        
    def _draw_level_progress(self, screen: pygame.Surface) -> None:
        """Draw animated level progress bar at the top of the screen"""
        bar_width = 400
        bar_height = 25
        
        bar_x = (WINDOW_WIDTH - bar_width) // 2
        bar_y = 10
        
        # Background with gradient effect
        for i in range(bar_height):
            alpha = 100 + (i * 2)
            color = (100, 100, 100, alpha)
            pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y + i, bar_width, 1))
        
        # Progress with smooth animation
        progress = self.robots_killed / max(1, self.robots_to_spawn)
        progress_width = int(bar_width * progress)
        
        # Animated progress bar with gradient
        if progress_width > 0:
            for i in range(progress_width):
                # Create gradient effect from green to yellow to red
                if progress < 0.5:
                    # Green to yellow
                    ratio = progress * 2
                    r = int(max(0, min(255, 0 + (255 * ratio))))
                    g = 255
                    b = 0
                else:
                    # Yellow to red
                    ratio = (progress - 0.5) * 2
                    r = 255
                    g = int(max(0, min(255, 255 - (255 * ratio))))
                    b = 0
                
                # Add some animation based on time
                animation_offset = int(5 * (self.elapsed % 0.5))
                bar_segment_height = bar_height + (animation_offset if i % 10 == 0 else 0)
                
                pygame.draw.rect(screen, (r, g, b), (bar_x + i, bar_y, 1, bar_segment_height))
        
        # Border with glow effect
        border_color = (255, 255, 255) if progress >= 1.0 else (200, 200, 200)
        pygame.draw.rect(screen, border_color, (bar_x, bar_y, bar_width, bar_height), 3)
        
        # Inner border
        pygame.draw.rect(screen, (50, 50, 50), (bar_x + 2, bar_y + 2, bar_width - 4, bar_height - 4), 1)
        
        # Progress text with animation
        progress_text = self.font.render(f"Progress: {self.robots_killed}/{self.robots_to_spawn}", True, (255, 255, 255))
        text_x = bar_x + bar_width // 2 - progress_text.get_width() // 2
        text_y = bar_y + bar_height // 2 - progress_text.get_height() // 2
        
        # Add slight bounce animation when progress increases
        if hasattr(self, '_last_progress') and self.robots_killed > getattr(self, '_last_killed', 0):
            text_y += int(3 * (self.elapsed % 0.3))
        
        screen.blit(progress_text, (text_x, text_y))
        
        # Store last progress for animation
        self._last_progress = progress
        self._last_killed = self.robots_killed

    def _draw_completion_message(self, screen: pygame.Surface) -> None:
        """Draw completion message overlay when level is complete"""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Completion message
        font_big = pygame.font.SysFont(None, 64, bold=True)
        font_med = pygame.font.SysFont(None, 36)
        
        # Main completion text
        title = font_big.render(f"🎉 LEVEL {self.level} COMPLETED! 🎉", True, (255, 255, 255))
        title_x = WINDOW_WIDTH // 2 - title.get_width() // 2
        title_y = WINDOW_HEIGHT // 2 - 80
        screen.blit(title, (title_x, title_y))
        
        # Power-up text
        power_text = font_med.render(f"🎁 New Power: {self.level_config['power_up'].title()} 🎁", True, (255, 255, 100))
        power_x = WINDOW_WIDTH // 2 - power_text.get_width() // 2
        power_y = WINDOW_HEIGHT // 2 - 20
        screen.blit(power_text, (power_x, power_y))
        
        # Next level text
        next_text = font_med.render(f"🚀 Moving to Level {self.level + 1}...", True, (100, 255, 100))
        next_x = WINDOW_WIDTH // 2 - next_text.get_width() // 2
        next_y = WINDOW_HEIGHT // 2 + 40
        screen.blit(next_text, (next_x, next_y))


    def _draw_final_wave_message(self, screen: pygame.Surface) -> None:
        """Draw the "FINAL WAVE!" message without dimming the screen"""
        # Final wave text only (no blur/dim overlay)
        font_big = pygame.font.SysFont(None, 72, bold=True)
        text = font_big.render("FINAL WAVE!", True, (255, 0, 0))  # Red text for urgency
        text_x = WINDOW_WIDTH // 2 - text.get_width() // 2
        text_y = WINDOW_HEIGHT // 2 - 100
        screen.blit(text, (text_x, text_y))

    def _add_kill_effect(self, pos: tuple[int, int]) -> None:
        """Add a visual effect when a robot is killed"""
        import random
        # Create particles for kill effect
        for _ in range(8):
            particle = {
                'pos': list(pos),
                'vel': [random.uniform(-100, 100), random.uniform(-150, -50)],
                'life': 1.0,
                'color': (255, 100, 100),
                'size': random.randint(2, 6)
            }
            self.kill_effects.append(particle)

    def _update_kill_effects(self, dt: float) -> None:
        """Update kill effect particles"""
        for particle in self.kill_effects[:]:
            particle['life'] -= dt * 2.0
            particle['pos'][0] += particle['vel'][0] * dt
            particle['pos'][1] += particle['vel'][1] * dt
            particle['vel'][1] += 200 * dt  # Gravity
            
            if particle['life'] <= 0:
                self.kill_effects.remove(particle)

    def _draw_kill_effects(self, screen: pygame.Surface) -> None:
        """Draw kill effect particles"""
        for particle in self.kill_effects:
            alpha = int(255 * particle['life'])
            color = (*particle['color'], alpha)
            size = int(particle['size'] * particle['life'])
            if size > 0:
                pygame.draw.circle(screen, particle['color'], 
                                 (int(particle['pos'][0]), int(particle['pos'][1])), size)
        bar_width = 400
        bar_height = 25
        
        bar_x = (WINDOW_WIDTH - bar_width) // 2
        bar_y = 10
        
        # Background with gradient effect
        for i in range(bar_height):
            alpha = 100 + (i * 2)
            color = (100, 100, 100, alpha)
            pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y + i, bar_width, 1))
        
        # Progress with smooth animation
        progress = self.robots_killed / max(1, self.robots_to_spawn)
        progress_width = int(bar_width * progress)
        
        # Animated progress bar with gradient
        if progress_width > 0:
            for i in range(progress_width):
                # Create gradient effect from green to yellow to red
                if progress < 0.5:
                    # Green to yellow
                    ratio = progress * 2
                    r = int(max(0, min(255, 0 + (255 * ratio))))
                    g = 255
                    b = 0
                else:
                    # Yellow to red
                    ratio = (progress - 0.5) * 2
                    r = 255
                    g = int(max(0, min(255, 255 - (255 * ratio))))
                    b = 0
                
                # Add some animation based on time
                animation_offset = int(5 * (self.elapsed % 0.5))
                bar_segment_height = bar_height + (animation_offset if i % 10 == 0 else 0)
                
                pygame.draw.rect(screen, (r, g, b), (bar_x + i, bar_y, 1, bar_segment_height))
        
        # Border with glow effect
        border_color = (255, 255, 255) if progress >= 1.0 else (200, 200, 200)
        pygame.draw.rect(screen, border_color, (bar_x, bar_y, bar_width, bar_height), 3)
        
        # Inner border
        pygame.draw.rect(screen, (50, 50, 50), (bar_x + 2, bar_y + 2, bar_width - 4, bar_height - 4), 1)
        
        # Progress text with animation
        progress_text = self.font.render(f"Progress: {self.robots_killed}/{self.robots_to_spawn}", True, (255, 255, 255))
        text_x = bar_x + bar_width // 2 - progress_text.get_width() // 2
        text_y = bar_y + bar_height // 2 - progress_text.get_height() // 2
        
        # Add slight bounce animation when progress increases
        if hasattr(self, '_last_progress') and self.robots_killed > getattr(self, '_last_killed', 0):
            text_y += int(3 * (self.elapsed % 0.3))
        
        screen.blit(progress_text, (text_x, text_y))
        
        # Store last progress for animation
        self._last_progress = progress
        self._last_killed = self.robots_killed

    def _draw_completion_message(self, screen: pygame.Surface) -> None:
        """Draw completion message overlay when level is complete"""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Completion message
        font_big = pygame.font.SysFont(None, 64, bold=True)
        font_med = pygame.font.SysFont(None, 36)
        
        # Main completion text
        title = font_big.render(f"🎉 LEVEL {self.level} COMPLETED! 🎉", True, (255, 255, 255))
        title_x = WINDOW_WIDTH // 2 - title.get_width() // 2
        title_y = WINDOW_HEIGHT // 2 - 80
        screen.blit(title, (title_x, title_y))
        
        # Power-up text
        power_text = font_med.render(f"🎁 New Power: {self.level_config['power_up'].title()} 🎁", True, (255, 255, 100))
        power_x = WINDOW_WIDTH // 2 - power_text.get_width() // 2
        power_y = WINDOW_HEIGHT // 2 - 20
        screen.blit(power_text, (power_x, power_y))
        
        # Next level text
        next_text = font_med.render(f"🚀 Moving to Level {self.level + 1}...", True, (100, 255, 100))
        next_x = WINDOW_WIDTH // 2 - next_text.get_width() // 2
        next_y = WINDOW_HEIGHT // 2 + 40
        screen.blit(next_text, (next_x, next_y))


    def _draw_final_wave_message(self, screen: pygame.Surface) -> None:
        """Draw the "FINAL WAVE!" message without dimming the screen"""
        # Final wave text only (no blur/dim overlay)
        font_big = pygame.font.SysFont(None, 72, bold=True)
        text = font_big.render("FINAL WAVE!", True, (255, 0, 0))  # Red text for urgency
        text_x = WINDOW_WIDTH // 2 - text.get_width() // 2
        text_y = WINDOW_HEIGHT // 2 - 100
        screen.blit(text, (text_x, text_y))

    def _draw_grid_adjustment_overlay(self, screen: pygame.Surface) -> None:
        """Draw instructions for adjusting the grid."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        font_big = pygame.font.SysFont(None, 48, bold=True)
        font_med = pygame.font.SysFont(None, 32)

        title = font_big.render("Grid Adjustment Mode", True, (255, 255, 255))
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 150))

        instructions = [
            "Use Arrow Keys to move the grid.",
            "Use '+' and '-' to change tile size.",
            "Press ENTER to confirm and start the level."
        ]
        for i, line in enumerate(instructions):
            text = font_med.render(line, True, (220, 220, 220))
            screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, 220 + i * 40))

    def _update_kill_effects(self, dt: float) -> None:
        """Update kill effect particles"""
        for particle in self.kill_effects[:]:
            particle['life'] -= dt * 2.0
            particle['pos'][0] += particle['vel'][0] * dt
            particle['pos'][1] += particle['vel'][1] * dt
            particle['vel'][1] += 200 * dt  # Gravity
            
            if particle['life'] <= 0:
                self.kill_effects.remove(particle)

    def _draw_kill_effects(self, screen: pygame.Surface) -> None:
        """Draw kill effect particles"""
        for particle in self.kill_effects:
            alpha = int(255 * particle['life'])
            color = (*particle['color'], alpha)
            size = int(particle['size'] * particle['life'])
            if size > 0:
                pygame.draw.circle(screen, particle['color'], 
                                 (int(particle['pos'][0]), int(particle['pos'][1])), size)
