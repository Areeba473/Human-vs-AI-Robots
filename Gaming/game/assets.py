from __future__ import annotations

import os
import glob
import random
import pygame


def draw_human(surface: pygame.Surface, color: tuple[int, int, int] = (240, 220, 120)) -> pygame.Surface:
    surf = pygame.Surface((56, 56), pygame.SRCALPHA)
    pygame.draw.rect(surf, color, pygame.Rect(8, 16, 40, 32), border_radius=8)
    pygame.draw.circle(surf, (255, 240, 200), (28, 12), 10)
    return surf


def _load_scaled_image_if_exists(relative_path: str, size: tuple[int, int]) -> pygame.Surface | None:
    try:
        base_dir = os.path.dirname(__file__)  # game/
        full_path = os.path.join(base_dir, relative_path)
        print(f"🔍 Checking path: {full_path}")
        if os.path.exists(full_path):
            print(f"✅ File exists: {full_path}")
            img = pygame.image.load(full_path).convert_alpha()
            if img.get_width() != size[0] or img.get_height() != size[1]:
                img = pygame.transform.smoothscale(img, size)
            return img
        else:
            print(f"❌ File does not exist: {full_path}")
    except Exception as e:
        print(f"⚠️ Error loading {relative_path}: {e}")
    return None


# Cache of robot sprites so we only scan disk once
_ROBOT_SPRITES: list[pygame.Surface] = []
_UNIT_SPRITES: dict[str, pygame.Surface] = {}

def clear_unit_sprite_cache() -> None:
    """Clear the unit sprite cache to force reloading of images"""
    global _UNIT_SPRITES
    _UNIT_SPRITES.clear()
    print("🧹 Unit sprite cache cleared")


def _ensure_robot_sprites(size: tuple[int, int]) -> None:
    global _ROBOT_SPRITES
    if _ROBOT_SPRITES:
        return
    # Single-file fallbacks
    for candidate in [
        os.path.join("images", "robot.png"),
        os.path.join("images", "robot_basic.png"),
    ]:
        sprite = _load_scaled_image_if_exists(candidate, size)
        if sprite is not None:
            _ROBOT_SPRITES.append(sprite)
    # Directory of variants
    base_dir = os.path.dirname(__file__)
    robots_dir = os.path.join(base_dir, "images", "robots")
    try:
        patterns = ["*.png", "*.PNG", "*.jpg", "*.jpeg", "*.JPG", "*.JPEG"]
        for pattern in patterns:
            for path in glob.glob(os.path.join(robots_dir, pattern)):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    if img.get_size() != size:
                        img = pygame.transform.smoothscale(img, size)
                    _ROBOT_SPRITES.append(img)
                    print(f"🤖 Loaded robot sprite: {os.path.basename(path)}")
                except Exception:
                    continue
    except Exception:
        pass


def _load_unit_sprite(key: str, size: tuple[int, int]) -> pygame.Surface | None:
    # Cache lookup
    if key in _UNIT_SPRITES:
        return _UNIT_SPRITES[key]
    candidates = [
        os.path.join("images", "units", f"{key}.png"),
        os.path.join("images", f"{key}.png"),
    ]
    if key == "frozen":
        candidates.append(os.path.join("images", "units", "frozen_shooter.png"))
        candidates.append(os.path.join("images", "frozen_shooter.png"))
    if key == "generator":
        # Accept custom filenames for the generator provided by the user
        candidates.extend([
            os.path.join("images", "units", "Energy_generator.png"),
            os.path.join("images", "Energy_generator.png"),
            os.path.join("images", "units", "energy_generator.png"),
            os.path.join("images", "energy_generator.png"),
            os.path.join("images", "units", "Energy generator.png"),  # space variant
            os.path.join("images", "Energy generator.png"),
        ])
    if key == "charger":
        # Accept multiple filenames, including user's custom asset with spaces
        candidates.extend([
            os.path.join("images", "units", "charger.png"),
            os.path.join("images", "charger.png"),
            os.path.join("images", "units", "Robot current charger.png"),
            os.path.join("images", "Robot current charger.png"),
        ])
    
    print(f"🔍 Looking for {key} sprite in candidates: {candidates}")
    
    for rel in candidates:
        sprite = _load_scaled_image_if_exists(rel, size)
        if sprite is not None:
            print(f"✅ Found {key} sprite at: {rel}")
            _UNIT_SPRITES[key] = sprite
            return sprite
        else:
            print(f"❌ No sprite found at: {rel}")
    
    print(f"⚠️ No sprite found for {key}, using fallback")
    return None


def draw_robot(surface: pygame.Surface | None = None, color: tuple[int, int, int] = (150, 200, 220)) -> pygame.Surface:
    # Try to load one of many real sprites if provided by the user
    _ensure_robot_sprites((56, 56))
    if _ROBOT_SPRITES:
        return random.choice(_ROBOT_SPRITES).copy()

    # Fallback: simple robot block
    surf = pygame.Surface((56, 56), pygame.SRCALPHA)
    pygame.draw.rect(surf, color, pygame.Rect(6, 8, 44, 40), border_radius=4)
    pygame.draw.rect(surf, (20, 20, 20), pygame.Rect(14, 14, 28, 12))
    return surf


def draw_fast_robot() -> pygame.Surface:
    """Variant robot sprite with a visual accent to distinguish fast robots.

    Uses any available robot sprite as a base and overlays a red lightning
    bolt/stripe so it looks different from the normal robot even when using
    user-provided images.
    """
    base = draw_robot()
    surf = base.copy()
    try:
        # Add a simple red lightning/stripe accent
        pygame.draw.polygon(
            surf,
            (220, 60, 60),
            [(8, 10), (22, 10), (16, 20), (26, 20), (12, 36), (18, 24), (10, 24)],
        )
    except Exception:
        # If drawing fails for any reason, just return the base
        return base
    return surf


def draw_white_blue_robot() -> pygame.Surface:
    """White and blue robot variant with distinct visual styling.

    Uses any available robot sprite as a base and overlays a blue
    accent pattern to distinguish it from normal and fast robots.
    """
    # Try to load the specific white-blue robot image first
    try:
        base = os.path.dirname(__file__)
        robot_path = os.path.join(base, "images", "robots", "Humanoid Robot with Blue Accents.png")
        if os.path.exists(robot_path):
            img = pygame.image.load(robot_path).convert_alpha()
            # Scale to 56x56 to match other units
            return pygame.transform.scale(img, (56, 56))
    except Exception:
        pass
    
    # Fallback: use base robot with blue accents
    base = draw_robot()
    surf = base.copy()
    try:
        # Add blue accent pattern (stripe and highlights)
        pygame.draw.rect(surf, (100, 150, 220), (8, 8, 40, 8), border_radius=2)  # top stripe
        pygame.draw.rect(surf, (80, 120, 200), (12, 16, 32, 4), border_radius=2)  # middle accent
        pygame.draw.circle(surf, (120, 180, 255), (20, 44), 6)  # bottom accent
    except Exception:
        # If drawing fails for any reason, just return the base
        return base
    return surf

def draw_projectile(color: tuple[int, int, int] = (240, 240, 80)) -> pygame.Surface:
    surf = pygame.Surface((16, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, color, pygame.Rect(0, 0, 16, 8))
    return surf

def draw_ice_projectile() -> pygame.Surface:
    import pygame
    surf = pygame.Surface((16, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, (140, 200, 255), pygame.Rect(0, 0, 16, 8))
    return surf


def draw_bubble_projectile() -> pygame.Surface:
    import pygame
    surf = pygame.Surface((20, 20), pygame.SRCALPHA)
    pygame.draw.circle(surf, (150, 200, 255), (10, 10), 8)
    pygame.draw.circle(surf, (180, 220, 255), (10, 10), 6)
    pygame.draw.circle(surf, (200, 240, 255), (10, 10), 4)
    return surf


def draw_energy() -> pygame.Surface:
    import pygame
    surf = pygame.Surface((36, 36), pygame.SRCALPHA)
    pygame.draw.circle(surf, (255, 220, 80), (18, 18), 16)
    pygame.draw.circle(surf, (255, 250, 200), (14, 14), 6)
    return surf


def draw_mower() -> pygame.Surface:
    # Try to load the user's lawn_mower.png image first
    try:
        base = os.path.dirname(__file__)
        mower_path = os.path.join(base, "images", "lawn_mower.png")
        if os.path.exists(mower_path):
            img = pygame.image.load(mower_path).convert_alpha()
            # Scale to a larger height (72px) while preserving aspect ratio
            # so it appears bigger but not stretched. Fits within 80px lane.
            original_w, original_h = img.get_size()
            if original_h > 0:
                target_h = 72
                scale = target_h / float(original_h)
                scaled_w = int(round(original_w * scale))
                # keep a sensible width range so it doesn't look oversized
                scaled_w = max(72, min(scaled_w, 128))
                scaled_h = int(round(original_h * (scaled_w / float(original_w))))
                scaled_h = min(scaled_h, target_h)
                return pygame.transform.smoothscale(img, (scaled_w, scaled_h))
            # Fallback if something is wrong with dimensions
            return pygame.transform.smoothscale(img, (108, 72))
    except Exception:
        pass
    
    # Fallback: simple mower drawing at ~108x72 to match target height
    surf = pygame.Surface((108, 72), pygame.SRCALPHA)
    # body
    pygame.draw.rect(surf, (200, 50, 50), pygame.Rect(10, 18, 88, 36), border_radius=8)
    # outline for clarity
    pygame.draw.rect(surf, (40, 40, 40), pygame.Rect(10, 18, 88, 36), 2, border_radius=8)
    # wheels
    pygame.draw.circle(surf, (20, 20, 20), (30, 56), 10)
    pygame.draw.circle(surf, (20, 20, 20), (88, 56), 10)
    return surf


# Distinct unit visuals
def draw_shooter() -> pygame.Surface:
    sprite = _load_unit_sprite("shooter", (56, 56))
    if sprite is not None:
        return sprite.copy()
    surf = pygame.Surface((56, 56), pygame.SRCALPHA)
    # body
    pygame.draw.rect(surf, (230, 210, 120), pygame.Rect(10, 20, 32, 28), border_radius=8)
    # head
    pygame.draw.circle(surf, (255, 240, 200), (26, 16), 9)
    # barrel
    pygame.draw.rect(surf, (90, 90, 90), pygame.Rect(40, 28, 10, 6), border_radius=2)
    return surf


def draw_frozen_shooter() -> pygame.Surface:
    sprite = _load_unit_sprite("frozen", (56, 56))
    if sprite is not None:
        print(f"❄️ Frozen shooter: Loaded custom sprite from frozen.png")
        return sprite.copy()
    print(f"❄️ Frozen shooter: Using fallback drawn version")
    surf = pygame.Surface((56, 56), pygame.SRCALPHA)
    # body
    pygame.draw.rect(surf, (170, 210, 240), pygame.Rect(10, 20, 32, 28), border_radius=8)
    # head
    pygame.draw.circle(surf, (220, 240, 255), (26, 16), 9)
    # barrel
    pygame.draw.rect(surf, (120, 160, 200), pygame.Rect(40, 28, 10, 6), border_radius=2)
    return surf


def draw_healer() -> pygame.Surface:
    sprite = _load_unit_sprite("healer", (56, 56))
    if sprite is not None:
        return sprite.copy()
    surf = pygame.Surface((56, 56), pygame.SRCALPHA)
    pygame.draw.rect(surf, (200, 160, 200), pygame.Rect(10, 16, 36, 28), border_radius=8)
    pygame.draw.circle(surf, (240, 210, 240), (28, 14), 8)
    # plus sign
    pygame.draw.rect(surf, (255, 255, 255), pygame.Rect(25, 26, 6, 18), border_radius=2)
    pygame.draw.rect(surf, (255, 255, 255), pygame.Rect(20, 31, 16, 6), border_radius=2)
    return surf


def draw_charger() -> pygame.Surface:
    sprite = _load_unit_sprite("charger", (56, 56))
    if sprite is not None:
        return sprite.copy()
    # Fallback simple charger icon
    surf = pygame.Surface((56, 56), pygame.SRCALPHA)
    pygame.draw.rect(surf, (60, 120, 200), pygame.Rect(16, 10, 24, 36), border_radius=6)
    pygame.draw.rect(surf, (255, 255, 255), pygame.Rect(25, 14, 6, 14))
    pygame.draw.polygon(surf, (255, 255, 100), [(28, 30), (22, 40), (30, 36), (34, 44), (34, 34), (38, 34)])
    return surf


def draw_wall_block() -> pygame.Surface:
    # Try to load the user's wall.png image first
    try:
        base = os.path.dirname(__file__)
        wall_path = os.path.join(base, "images", "units", "wall.png")
        if os.path.exists(wall_path):
            img = pygame.image.load(wall_path).convert_alpha()
            # Scale to 56x56 to match other units
            return pygame.transform.scale(img, (56, 56))
    except Exception:
        pass
    
    # Fallback to sprite or drawn version
    sprite = _load_unit_sprite("wall", (56, 56))
    if sprite is not None:
        return sprite.copy()
    surf = pygame.Surface((56, 56), pygame.SRCALPHA)
    pygame.draw.rect(surf, (170, 180, 200), pygame.Rect(8, 12, 40, 32), border_radius=6)
    # grooves
    pygame.draw.rect(surf, (140, 150, 170), pygame.Rect(12, 20, 32, 4), border_radius=2)
    pygame.draw.rect(surf, (140, 150, 170), pygame.Rect(12, 30, 32, 4), border_radius=2)
    return surf


def draw_generator_icon() -> pygame.Surface:
    sprite = _load_unit_sprite("generator", (56, 56))
    if sprite is not None:
        return sprite.copy()
    surf = pygame.Surface((56, 56), pygame.SRCALPHA)
    pygame.draw.circle(surf, (255, 220, 90), (28, 28), 12)
    # rays
    for i in range(8):
        angle = i * (360 // 8)
        pygame.draw.line(surf, (255, 230, 150), (28, 28), (
            28 + int(20 * pygame.math.Vector2(1, 0).rotate(angle).x),
            28 + int(20 * pygame.math.Vector2(1, 0).rotate(angle).y),
        ), 2)
    return surf


def draw_bomb_icon() -> pygame.Surface:
    sprite = _load_unit_sprite("bomb", (56, 56))
    if sprite is not None:
        return sprite.copy()
    surf = pygame.Surface((56, 56), pygame.SRCALPHA)
    pygame.draw.circle(surf, (200, 70, 70), (26, 30), 12)
    # fuse
    pygame.draw.line(surf, (80, 60, 40), (32, 22), (42, 12), 3)
    pygame.draw.circle(surf, (255, 200, 80), (44, 10), 3)
    return surf


def draw_laser_gun() -> pygame.Surface:
    """Load laser_gun sprite if present, else draw a simple laser gun."""
    sprite = _load_unit_sprite("laser_gun", (56, 56))
    if sprite is not None:
        return sprite.copy()
    # Fallback simple laser gun icon
    surf = pygame.Surface((56, 56), pygame.SRCALPHA)
    # handle/body
    pygame.draw.rect(surf, (40, 100, 140), pygame.Rect(10, 26, 30, 12), border_radius=4)
    pygame.draw.rect(surf, (30, 80, 120), pygame.Rect(16, 20, 18, 8), border_radius=3)
    # barrel
    pygame.draw.rect(surf, (80, 200, 240), pygame.Rect(40, 26, 10, 6), border_radius=2)
    # glow
    pygame.draw.circle(surf, (120, 240, 255), (46, 28), 3)
    return surf


def draw_tank() -> pygame.Surface:
    """Load tank sprite if present, else draw a simple tank."""
    sprite = _load_unit_sprite("tank", (56, 56))
    if sprite is not None:
        return sprite.copy()
    # Fallback simple tank icon
    surf = pygame.Surface((56, 56), pygame.SRCALPHA)
    # body
    pygame.draw.rect(surf, (80, 80, 90), pygame.Rect(8, 18, 40, 24), border_radius=6)
    # turret
    pygame.draw.rect(surf, (60, 60, 70), pygame.Rect(18, 14, 22, 10), border_radius=3)
    # barrel
    pygame.draw.rect(surf, (60, 60, 70), pygame.Rect(38, 16, 12, 6), border_radius=2)
    # treads
    pygame.draw.rect(surf, (30, 30, 30), pygame.Rect(8, 40, 40, 8), border_radius=3)
    return surf


def draw_virus() -> pygame.Surface:
    """Load virus sprite if present, else draw a simple spiky ball."""
    sprite = _load_unit_sprite("virus", (56, 56))
    if sprite is not None:
        return sprite.copy()
    surf = pygame.Surface((56, 56), pygame.SRCALPHA)
    center = (28, 28)
    pygame.draw.circle(surf, (180, 40, 40), center, 16)
    for i in range(12):
        ang = i * (360 // 12)
        v = pygame.math.Vector2(1, 0).rotate(ang)
        pygame.draw.line(surf, (255, 90, 90), (center[0] + int(v.x * 16), center[1] + int(v.y * 16)), (center[0] + int(v.x * 24), center[1] + int(v.y * 24)), 4)
    pygame.draw.circle(surf, (255, 120, 120), center, 10)
    return surf


def draw_bubble_shooter() -> pygame.Surface:
    """Load bubble shooter sprite if present, else draw a simple bubble shooter."""
    sprite = _load_unit_sprite("bubble_shooter", (56, 56))
    if sprite is not None:
        return sprite.copy()
    # Fallback simple bubble shooter icon
    surf = pygame.Surface((56, 56), pygame.SRCALPHA)
    # body
    pygame.draw.rect(surf, (100, 150, 200), pygame.Rect(10, 20, 32, 28), border_radius=8)
    # head
    pygame.draw.circle(surf, (150, 200, 255), (26, 16), 9)
    # bubble barrel
    pygame.draw.circle(surf, (200, 220, 255), (42, 28), 8)
    pygame.draw.circle(surf, (180, 200, 255), (42, 28), 6)
    return surf


def draw_shield_defender() -> pygame.Surface:
    """Load shield defender sprite if present, else draw a simple shield defender."""
    sprite = _load_unit_sprite("shield_defender", (56, 56))
    if sprite is not None:
        return sprite.copy()
    # Fallback simple shield defender icon
    surf = pygame.Surface((56, 56), pygame.SRCALPHA)
    # body
    pygame.draw.rect(surf, (100, 120, 180), pygame.Rect(10, 20, 32, 28), border_radius=8)
    # head
    pygame.draw.circle(surf, (200, 220, 255), (26, 16), 9)
    # shield
    pygame.draw.ellipse(surf, (120, 200, 255), pygame.Rect(8, 8, 40, 40))
    pygame.draw.ellipse(surf, (80, 160, 220), pygame.Rect(12, 12, 32, 32))
    # energy lines
    pygame.draw.line(surf, (200, 240, 255), (16, 28), (40, 28), 2)
    pygame.draw.line(surf, (200, 240, 255), (28, 16), (28, 40), 2)
    return surf


def draw_shovel() -> pygame.Surface:
    """Draws a simple shovel icon."""
    surf = pygame.Surface((56, 56), pygame.SRCALPHA)
    # Handle
    pygame.draw.rect(surf, (160, 90, 60), pygame.Rect(25, 10, 6, 30), border_radius=2)
    # Blade
    pygame.draw.polygon(surf, (180, 180, 180), [(22, 38), (34, 38), (38, 48), (18, 48)])
    return surf


def draw_night_stalker() -> pygame.Surface:
    """Load night stalker sprite if present, else draw a simple night stalker."""
    sprite = _load_unit_sprite("night_stalker", (56, 56))
    if sprite is not None:
        return sprite.copy()
    # Fallback simple night stalker icon
    surf = pygame.Surface((56, 56), pygame.SRCALPHA)
    # body - dark stealth colors
    pygame.draw.rect(surf, (60, 60, 90), pygame.Rect(10, 20, 32, 28), border_radius=8)
    # head
    pygame.draw.circle(surf, (80, 80, 120), (26, 16), 9)
    # stealth cloak effect
    pygame.draw.ellipse(surf, (40, 40, 80, 150), pygame.Rect(6, 6, 44, 44))
    # glowing eyes
    pygame.draw.circle(surf, (255, 100, 100), (22, 14), 2)
    pygame.draw.circle(surf, (255, 100, 100), (30, 14), 2)
    # blade
    pygame.draw.polygon(surf, (200, 200, 220), [(40, 26), (48, 22), (48, 30), (42, 32)])
    return surf


def draw_shadow_healer() -> pygame.Surface:
    """Load shadow healer sprite if present, else draw a simple shadow healer."""
    sprite = _load_unit_sprite("shadow_healer", (56, 56))
    if sprite is not None:
        return sprite.copy()
    # Fallback simple shadow healer icon
    surf = pygame.Surface((56, 56), pygame.SRCALPHA)
    # body - dark mystical colors
    pygame.draw.rect(surf, (80, 60, 120), pygame.Rect(10, 20, 32, 28), border_radius=8)
    # head
    pygame.draw.circle(surf, (120, 100, 160), (26, 16), 9)
    # mystical hood
    pygame.draw.ellipse(surf, (60, 40, 100, 200), pygame.Rect(8, 8, 40, 30))
    # healing cross with shadow effect
    pygame.draw.rect(surf, (100, 255, 150), pygame.Rect(25, 26, 6, 18), border_radius=2)
    pygame.draw.rect(surf, (100, 255, 150), pygame.Rect(20, 31, 16, 6), border_radius=2)
    # shadow aura
    pygame.draw.circle(surf, (150, 100, 200, 100), (28, 28), 25, width=2)
    return surf
