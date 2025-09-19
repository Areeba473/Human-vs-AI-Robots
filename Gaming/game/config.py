from __future__ import annotations

WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 576
WINDOW_TITLE = "Humans vs AI Robots"

FPS = 60

# Board/Grid
NUM_LANES = 5
TILES_PER_LANE = 9
TILE_SIZE = 80

# Themes and progression
THEMES = ["Day", "Night", "Fog", "Water", "Roof"]
LEVELS_PER_THEME = 10

# Colors
COLOR_BG = {
    "Day": (120, 180, 120),
    "Night": (40, 60, 100),
    "Fog": (100, 120, 120),
    "Water": (70, 130, 180),
    "Roof": (160, 120, 80),
}

# Economy
START_ENERGY = 50
ENERGY_DROP_VALUE = 25
SKY_DROP_INTERVAL = (4.0, 12.0)  # random range: 4 to 12 seconds

# Unit costs and cooldowns (seconds)
UNIT_DEFS = [
    {"key": "shooter", "name": "Shooter", "cost": 100, "cooldown": 7.5},  # Basic ranged attacker
    {"key": "wall", "name": "Wall", "cost": 50, "cooldown": 10.0},  # High HP blocker (30 HP) - stops robots from advancing
    {"key": "generator", "name": "Generator", "cost": 50, "cooldown": 7.5},  # Produces energy drops
    {"key": "bomb", "name": "Bomb", "cost": 150, "cooldown": 25.0},  # Cross-lane explosion (affects 3 lanes)
    {"key": "frozen", "name": "Frozen", "cost": 125, "cooldown": 8.0},  # Slows robots with ice projectiles
    {"key": "charger", "name": "Charger", "cost": 75, "cooldown": 10.0},  # Electrocutes nearby robots
    {"key": "tank", "name": "Tank", "cost": 200, "cooldown": 15.0},  # Heavy defender with powerful shells
    {"key": "laser_gun", "name": "Laser Gun", "cost": 125, "cooldown": 5.0},  # Fast shooter
    {"key": "virus", "name": "Virus", "cost": 150, "cooldown": 12.0},  # Contact-kill hazard with spread effect
    {"key": "bubble_shooter", "name": "Bubble Shooter", "cost": 0, "cooldown": 3.0},  # Free bubble shooter for Night theme
    {"key": "shield_defender", "name": "Shield Defender", "cost": 100, "cooldown": 8.0},  # Energy shield defender for Night theme
]

# Combat
ROBOT_BASE_SPEED = 75.0
ROBOT_CHEW_DAMAGE_PER_SEC = 12
PROJECTILE_SPEED = 220.0
PROJECTILE_DAMAGE = 1
SHOOTER_COOLDOWN = 1.2
# Wall durability and contact damage
# With two robots chewing (24 dps), 120 HP gives ~5 seconds of blocking time.
WALL_HP = 300
WALL_CONTACT_DAMAGE_PER_SEC = 24.0  # Thorns damage to robots while they chew the wall
SHOOTER_HP = 6
GENERATOR_HP = 6
BOMB_ARM_TIME = 1.0
BOMB_RADIUS = TILE_SIZE * 1.5  # Increased radius for better cross-lane coverage
BOMB_DAMAGE = 100  # Increased damage for cross-lane explosions

# Mowers
MOWER_SPEED = 420.0

# Frozen shooter effects
SLOW_FACTOR = 0.4
SLOW_DURATION = 2.5

# Healer
HEAL_AMOUNT = 2
HEAL_COOLDOWN = 4.0
HEAL_RADIUS = TILE_SIZE * 1.1

# Virus
VIRUS_RADIUS = TILE_SIZE * 1.0
VIRUS_GROW_TIME = 0.8
VIRUS_DAMAGE = 9999
VIRUS_LIFETIME = 12.0

# Night Stalker
NIGHT_STALKER_HP = 8
NIGHT_STALKER_DAMAGE = 3
NIGHT_STALKER_STEALTH_DURATION = 5.0
NIGHT_STALKER_STEALTH_COOLDOWN = 8.0

# Shadow Healer
SHADOW_HEALER_HP = 10
SHADOW_HEALER_HEAL_AMOUNT = 3
SHADOW_HEALER_HEAL_RADIUS = TILE_SIZE * 1.3
SHADOW_HEALER_HEAL_COOLDOWN = 3.0
SHADOW_HEALER_CLOAK_DURATION = 4.0

# Level Configuration
# Progression: Level 1=Wall, Level 2=Generator, Level 3=Frozen, Level 4=Frozen, Level 5=Bomb, Level 6=Healer
LEVEL_CONFIGS = {
    1: {
        "robot_count": 6,
        "lanes": [0, 1, 2, 3, 4],  # All 5 lanes
        "spawn_interval": 3.0,
        "power_up": "wall"  # Wall unlocked at level 1
    },
    2: {
        "robot_count": 8,
        "lanes": [0, 1, 2, 3, 4],  # All 5 lanes
        "spawn_interval": 2.5,
        "power_up": "generator"  # Generator unlocked at level 2
    },
    3: {
        "robot_count": 10,
        "lanes": [0, 1, 2, 3, 4],  # All 5 lanes
        "spawn_interval": 2.0,
        "power_up": "frozen"  # Frozen shooter unlocked at level 3
    },
    4: {
        "robot_count": 12,
        "lanes": [0, 1, 2, 3, 4],  # All 5 lanes
        "spawn_interval": 1.8,
        "power_up": "frozen"  # Frozen shooter unlocked at level 4
    },
    5: {
        "robot_count": 15,
        "lanes": [0, 1, 2, 3, 4],  # All 5 lanes
        "spawn_interval": 1.5,
        "power_up": "bomb"  # Bomb unlocked at level 5
    },
    6: {
        "robot_count": 18,
        "lanes": [0, 1, 2, 3, 4],  # All 5 lanes
        "spawn_interval": 1.3,
        "power_up": "charger"  # Charger unlocked at level 6
    },
    7: {
        "robot_count": 20,
        "lanes": [0, 1, 2, 3, 4],  # All 5 lanes
        "spawn_interval": 1.2,
        "power_up": "wall_upgrade"
    },
    8: {
        "robot_count": 22,
        "lanes": [0, 1, 2, 3, 4],  # All 5 lanes
        "spawn_interval": 1.1,
        "power_up": "generator_upgrade"
    },
    9: {
        "robot_count": 25,
        "lanes": [0, 1, 2, 3, 4],  # All 5 lanes
        "spawn_interval": 1.0,
        "power_up": "bomb_upgrade"
    },
    10: {
        "robot_count": 30,
        "lanes": [0, 1, 2, 3, 4],  # All 5 lanes
        "spawn_interval": 0.9,
        "power_up": "ultimate"
    }
}
