from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pygame

from game.assets import (
    draw_human,
    draw_robot,
    draw_fast_robot,
    draw_white_blue_robot,
    draw_projectile,
    draw_energy,
    draw_mower,
    draw_shooter,
    draw_wall_block,
    draw_generator_icon,
    draw_bomb_icon,
    draw_frozen_shooter,
    draw_ice_projectile,
    draw_charger,
    draw_tank,
    draw_laser_gun,
    draw_virus,
    draw_bubble_shooter,
    draw_bubble_projectile,
    draw_shield_defender,
    draw_night_stalker,
    draw_shadow_healer,
    draw_ice_shroom,
    draw_gatling_pea,
    draw_doom_shroom,
    draw_crater,
    draw_sun_shroom,
    draw_puff_shroom,
    draw_scaredy_shroom,
    draw_leaf,
    draw_tangle_kelp,
    draw_sea_shroom,
    draw_cattail,
    draw_sea_mine,
    draw_spike_projectile,
    draw_spikerock,
)
from game.config import (
    ROBOT_BASE_SPEED,
    PROJECTILE_SPEED,
    PROJECTILE_DAMAGE,
    SHOOTER_COOLDOWN,
    WALL_HP,
    ENERGY_DROP_VALUE,
    SHOOTER_HP,
    GENERATOR_HP,
    ROBOT_CHEW_DAMAGE_PER_SEC,
    BOMB_ARM_TIME,
    BOMB_RADIUS,
    BOMB_DAMAGE,
    SLOW_FACTOR,
    SLOW_DURATION,
    HEAL_AMOUNT,
    HEAL_COOLDOWN,
    HEAL_RADIUS,
    WALL_CONTACT_DAMAGE_PER_SEC,
    VIRUS_RADIUS,
    VIRUS_GROW_TIME,
    VIRUS_DAMAGE,
    VIRUS_LIFETIME,
    TILE_SIZE,
    NIGHT_STALKER_HP,
    NIGHT_STALKER_DAMAGE,
    NIGHT_STALKER_STEALTH_DURATION,
    NIGHT_STALKER_STEALTH_COOLDOWN,
    SHADOW_HEALER_HP,
    SHADOW_HEALER_HEAL_AMOUNT,
    SHADOW_HEALER_HEAL_RADIUS,
    SHADOW_HEALER_HEAL_COOLDOWN,
    SHADOW_HEALER_CLOAK_DURATION,
    DOOM_SHROOM_ARM_TIME,
    DOOM_SHROOM_RADIUS,
    CRATER_LIFETIME,
    SUN_SHROOM_GROW_TIME,
    SUN_SHROOM_SMALL_ENERGY,
    SUN_SHROOM_INITIAL_COOLDOWN,
    SUN_SHROOM_NORMAL_COOLDOWN,
    PUFF_SHROOM_LIFETIME,
    PUFF_SHROOM_RANGE,
    PUFF_SHROOM_HP,
    SCAREDY_SHROOM_SCARED_RANGE,
    SCAREDY_SHROOM_HP,
    BOMB_RADIUS,
    BOMB_DAMAGE,
    SPIKEROCK_HP,
    SPIKEROCK_CONTACT_DAMAGE_PER_SEC,
    GENERATOR_HP,
)


class Entity(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.alive_hp = 1

    def damage(self, amount: int) -> None:
        self.alive_hp -= amount
        if self.alive_hp <= 0:
            # Mark as dead before killing
            self.alive_hp = 0
            # Don't call kill() here - let the PlayScene handle it

    def render(self, screen: pygame.Surface) -> None:
        # Default render just draws the sprite normally
        screen.blit(self.image, self.rect)


class Human(Entity):
    def __init__(self, pos: tuple[int, int], lane_row: int | None = None) -> None:
        super().__init__()
        self.image = draw_shooter()
        self.rect = self.image.get_rect(center=pos)
        self.alive_hp = SHOOTER_HP
        self.shoot_cooldown = SHOOTER_COOLDOWN
        self.shoot_timer = 0.0
        self.lane_row = lane_row

    def try_shoot(self, projectiles: pygame.sprite.Group, robots: pygame.sprite.Group | None) -> None:
        if self.shoot_timer <= 0.0:
            # lane-aware: fire only if robot is to the right in the same lane
            should_fire = False
            if robots is None:
                should_fire = True
            else:
                for r in robots:
                    lane_r = getattr(r, "lane_row", None)
                    if self.lane_row is not None and lane_r is not None:
                        if lane_r == self.lane_row and r.rect.centerx > self.rect.centerx:
                            should_fire = True
                            break
                    else:
                        # fallback: vertical proximity and to the right
                        if r.rect.centerx > self.rect.centerx and abs(r.rect.centery - self.rect.centery) < self.rect.h // 2:
                            should_fire = True
                            break
            if should_fire:
                proj = Projectile((self.rect.right - 8, self.rect.centery))
                projectiles.add(proj)
                self.shoot_timer = self.shoot_cooldown

    def update(self, dt: float, projectiles: pygame.sprite.Group, robots: pygame.sprite.Group | None = None) -> None:
        self.shoot_timer = max(0.0, self.shoot_timer - dt)
        self.try_shoot(projectiles, robots)


class Robot(Entity):
    def __init__(self, pos: tuple[int, int], lane_row: int | None = None) -> None:
        super().__init__()
        self.image = draw_robot()
        self.rect = self.image.get_rect(center=pos)
        self.alive_hp = 8
        self.speed = ROBOT_BASE_SPEED
        self.chewing_target: Human | WallHuman | Generator | None = None
        self.lane_row = lane_row
        self.slow_timer = 0.0
        self.slow_multiplier = 1.0

    def update(self, dt: float) -> None:
        if self.chewing_target and self.chewing_target.alive():
            damage_amount = int(ROBOT_CHEW_DAMAGE_PER_SEC * dt)
            self.chewing_target.alive_hp -= damage_amount
            if self.chewing_target.alive_hp <= 0:
                self.chewing_target.kill()
                self.chewing_target = None
        else:
            effective_speed = self.speed * (self.slow_multiplier if self.slow_timer > 0 else 1.0)
            if self.slow_timer > 0:
                self.slow_timer = max(0.0, self.slow_timer - dt)
            self.rect.x -= int(effective_speed * dt)
        if self.rect.left < 0:
            self.kill()

    def damage(self, amount: int) -> None:
        """Override Entity damage method to notify wall when robot dies"""
        self.alive_hp -= amount
        if self.alive_hp <= 0:
            # Mark as dead before killing
            self.alive_hp = 0
            # Notify wall if this robot was engaging it
            if self.chewing_target and isinstance(self.chewing_target, WallHuman):
                self.chewing_target.robot_killed()
            # Don't call kill() here - let the PlayScene handle it

    def apply_slow(self, factor: float, duration: float) -> None:
        # Allow a factor of 0.0 for a complete freeze
        self.slow_multiplier = max(0.0, factor)
        self.slow_timer = max(self.slow_timer, duration)

    def render(self, screen: pygame.Surface) -> None:
        # Default render
        super().render(screen)
        # Draw ice effect if completely frozen by Ice Shroom
        if self.slow_timer > 0 and self.slow_multiplier == 0.0:
            ice_overlay = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            # Fade the ice effect in and out slightly
            alpha = 100 + 50 * (0.5 + 0.5 * pygame.math.Vector2(1, 0).rotate(pygame.time.get_ticks() * 0.5).y)
            ice_overlay.fill((180, 220, 255, alpha))
            screen.blit(ice_overlay, self.rect.topleft)


class FastRobot(Robot):
    """A faster, slightly weaker robot variant."""

    def __init__(self, pos: tuple[int, int], lane_row: int | None = None) -> None:
        super().__init__(pos, lane_row)
        # Increase speed, reduce HP a bit
        self.speed = ROBOT_BASE_SPEED * 1.6
        self.alive_hp = 6
        # Distinct look
        self.image = draw_fast_robot()

class WhiteBlueRobot(Robot):
    """A slower but tougher robot variant with blue accents."""

    def __init__(self, pos: tuple[int, int], lane_row: int | None = None) -> None:
        super().__init__(pos, lane_row)
        # Slower speed, higher HP for variety
        self.speed = ROBOT_BASE_SPEED * 0.8
        self.alive_hp = 10
        # Distinct look
        self.image = draw_white_blue_robot()

class Projectile(Entity):
    def __init__(self, pos: tuple[int, int]) -> None:
        super().__init__()
        self.image = draw_projectile()
        self.rect = self.image.get_rect(center=pos)
        self.speed = PROJECTILE_SPEED
        self.damage_value = PROJECTILE_DAMAGE

    def update(self, dt: float, robots: pygame.sprite.Group) -> None:
        self.rect.x += int(self.speed * dt)
        hits = pygame.sprite.spritecollide(self, robots, False)  # type: ignore
        if hits:
            for rob in hits:
                if isinstance(rob, Robot):
                    rob.damage(self.damage_value)
            self.kill()
        if self.rect.left > 1400:
            self.kill()


class SpikeProjectile(Projectile):
    """A homing projectile that targets a specific robot."""

    def __init__(self, pos: tuple[int, int], target: Robot) -> None:
        super().__init__(pos)
        self.image = draw_spike_projectile()
        self.target = target
        self.speed = PROJECTILE_SPEED * 1.5 # Faster than normal projectiles

    def update(self, dt: float, robots: pygame.sprite.Group) -> None:
        if not self.target.alive():
            self.kill()
            return

        # Move towards the target
        direction = pygame.math.Vector2(self.target.rect.center) - pygame.math.Vector2(self.rect.center)
        if direction.length() > 0:
            direction.normalize_ip()
        
        self.rect.centerx += direction.x * self.speed * dt
        self.rect.centery += direction.y * self.speed * dt

        # Use the same collision logic as the base projectile
        super().update(dt, robots)


class IceProjectile(Projectile):
    def __init__(self, pos: tuple[int, int]) -> None:
        super().__init__(pos)
        self.image = draw_ice_projectile()

    def update(self, dt: float, robots: pygame.sprite.Group) -> None:
        self.rect.x += int(self.speed * dt)
        hits = pygame.sprite.spritecollide(self, robots, False)  # type: ignore
        if hits:
            for rob in hits:
                if isinstance(rob, Robot):
                    rob.damage(self.damage_value)
                    rob.apply_slow(SLOW_FACTOR, SLOW_DURATION)
            self.kill()
        if self.rect.left > 1400:
            self.kill()


class WallHuman(Entity):
    def __init__(self, pos: tuple[int, int]) -> None:
        super().__init__()
        self.image = draw_wall_block()
        self.rect = self.image.get_rect(center=pos)
        self.alive_hp = WALL_HP
        self.regen_timer = 0.0
        self.robots_killed = 0  # Track how many robots this wall has killed
        self.max_robots = 3  # Wall automatically removes after killing 3 robots
        self.contact_damage_per_sec = WALL_CONTACT_DAMAGE_PER_SEC

    def update(self, dt: float, projectiles: pygame.sprite.Group | None = None, robots: pygame.sprite.Group | None = None) -> None:
        # Regenerate health
        self.regen_timer += dt
        if self.regen_timer >= 3.0 and self.alive_hp < WALL_HP:
            self.alive_hp += 1
            self.regen_timer = 0.0
        
        # Block robots from advancing and deal contact damage while colliding
        if robots:
            for robot in list(robots):
                if isinstance(robot, Robot) and self.rect.colliderect(robot.rect):
                    # Stop the robot from moving forward
                    robot.rect.x = self.rect.right
                    # Make robot engage with wall (chewing)
                    if robot.chewing_target is None:
                        robot.chewing_target = self
                    # Thorns/contact damage to the robot
                    if self.contact_damage_per_sec > 0:
                        # Apply damage; Robot.damage will notify the wall exactly once if it dies
                        damage_amount = int(self.contact_damage_per_sec * dt)
                        robot.damage(damage_amount)

    def robot_killed(self) -> None:
        """Called when a robot is killed while engaging this wall"""
        self.robots_killed += 1
        if self.robots_killed >= self.max_robots:
            # Wall has killed its maximum robots, remove it
            self.kill()
            print(f"🏗️ Wall removed after killing {self.robots_killed} robots!")

class Spikerock(WallHuman):
    """An upgrade to the Wall, with more health and contact damage."""

    def __init__(self, pos: tuple[int, int]) -> None:
        super().__init__(pos)
        self.image = draw_spikerock()
        self.rect = self.image.get_rect(center=pos)
        self.alive_hp = SPIKEROCK_HP
        self.contact_damage_per_sec = SPIKEROCK_CONTACT_DAMAGE_PER_SEC


class Generator(Entity):
    def __init__(self, pos: tuple[int, int]) -> None:
        super().__init__()
        self.image = draw_generator_icon()
        self.rect = self.image.get_rect(center=pos)
        self.alive_hp = GENERATOR_HP
        self.spawn_cd = 17.0  # Changed from 10.0 to 17.0 seconds
        self.timer = 2.0

    def update(self, dt: float, energy_group: pygame.sprite.Group) -> None:
        self.timer -= dt
        if self.timer <= 0.0:
            self.timer = self.spawn_cd
            drop = EnergyDrop((self.rect.centerx, self.rect.y - 10))
            energy_group.add(drop)


class EnergyDrop(Entity):
    def __init__(self, pos: tuple[int, int], value: int = ENERGY_DROP_VALUE) -> None:
        super().__init__()
        self.image = draw_energy()
        self.rect = self.image.get_rect(center=pos)
        self.fall_speed = 40.0
        self.value = value
        self.collect_rect = self.rect.copy()

    def update(self, dt: float) -> None:
        self.rect.y += int(self.fall_speed * dt)


class Bomb(Entity):
    def __init__(self, pos: tuple[int, int], lane_row: int | None = None) -> None:
        super().__init__()
        self.image = draw_bomb_icon()
        self.rect = self.image.get_rect(center=pos)
        self.lane_row = lane_row  # Track which lane the bomb is in
        self.timer = BOMB_ARM_TIME

    def update(self, dt: float, robots: pygame.sprite.Group) -> None:
        self.timer -= dt
        if self.timer <= 0.0:
            # explode with cross-lane effect
            center = self.rect.center
            affected_lanes = set()
            
            # Add the bomb's lane and adjacent lanes
            if self.lane_row is not None:
                affected_lanes.add(self.lane_row)  # Bomb's lane
                if self.lane_row > 0:
                    affected_lanes.add(self.lane_row - 1)  # Lane above
                if self.lane_row < 4:  # Changed from 5 to 4 for 5 lanes (0-4)
                    affected_lanes.add(self.lane_row + 1)  # Lane below
            
            for r in list(robots):
                if isinstance(r, Robot):
                    # Check if robot is in affected lanes
                    if r.lane_row in affected_lanes:
                        # Also check horizontal distance for realistic explosion
                        horizontal_distance = abs(r.rect.centerx - center[0])
                        if horizontal_distance <= BOMB_RADIUS:
                            r.damage(BOMB_DAMAGE)
                            print(f"💥 Bomb exploded! Killed robot in lane {r.lane_row}")
            
            self.kill()


class Mower(Entity):
    def __init__(self, pos: tuple[int, int], speed: float) -> None:
        super().__init__()
        self.image = draw_mower()
        self.rect = self.image.get_rect(midleft=pos)
        self.speed = speed
        self.active = False

    def trigger(self) -> None:
        self.active = True

    def update(self, dt: float, robots: pygame.sprite.Group) -> None:
        if self.active:
            self.rect.x += int(self.speed * dt)
            for r in list(robots):
                if self.rect.colliderect(r.rect):
                    r.kill()
            if self.rect.left > 2000:
                self.kill()


class FrozenShooter(Human):
    def __init__(self, pos: tuple[int, int], lane_row: int | None = None) -> None:
        super().__init__(pos, lane_row)
        self.image = draw_frozen_shooter()

    def try_shoot(self, projectiles: pygame.sprite.Group, robots: pygame.sprite.Group | None) -> None:
        if self.shoot_timer <= 0.0:
            should_fire = False
            if robots is None:
                should_fire = True
            else:
                for r in robots:
                    lane_r = getattr(r, "lane_row", None)
                    if self.lane_row is not None and lane_r is not None:
                        if lane_r == self.lane_row and r.rect.centerx > self.rect.centerx:
                            should_fire = True
                            break
                    else:
                        if r.rect.centerx > self.rect.centerx and abs(r.rect.centery - self.rect.centery) < self.rect.h // 2:
                            should_fire = True
                            break
            if should_fire:
                proj = IceProjectile((self.rect.right - 8, self.rect.centery))
                projectiles.add(proj)
                self.shoot_timer = self.shoot_cooldown



class Charger(Entity):
    """Electrifies nearby robots, damaging them over time.

    Replaces the Healer slot. Deals continuous damage to robots within a
    radius and shows a visual 'current' effect when damaging.
    """

    def __init__(self, pos: tuple[int, int]) -> None:
        super().__init__()
        self.image = draw_charger()
        self.rect = self.image.get_rect(center=pos)
        self.alive_hp = WALL_HP // 2
        self.radius = HEAL_RADIUS  # reuse radius constant
        self.dps = 25  # damage per second

    def update(self, dt: float, robots: pygame.sprite.Group) -> None:
        cx, cy = self.rect.center
        damage_amount = int(self.dps * dt)
        for r in list(robots):
            if isinstance(r, Robot):
                dx = r.rect.centerx - cx
                dy = r.rect.centery - cy
                if dx * dx + dy * dy <= self.radius * self.radius:
                    r.damage(damage_amount)


class Tank(Entity):
    """Heavy defender with high HP and slow, high-damage shells in-lane."""

    def __init__(self, pos: tuple[int, int], lane_row: int | None = None) -> None:
        super().__init__()
        self.image = draw_tank()
        self.rect = self.image.get_rect(center=pos)
        self.alive_hp = WALL_HP * 2
        self.lane_row = lane_row
        self.shoot_timer = 0.0
        self.shoot_cooldown = 2.0
        self.shell_damage = 3

    def update(self, dt: float, projectiles: pygame.sprite.Group, robots: pygame.sprite.Group | None = None) -> None:
        self.shoot_timer = max(0.0, self.shoot_timer - dt)
        if self.shoot_timer <= 0.0 and robots is not None:
            # fire only if robot to the right in same lane
            for r in robots:
                if isinstance(r, Robot) and self.lane_row is not None and getattr(r, "lane_row", None) == self.lane_row and r.rect.centerx > self.rect.centerx:
                    # Reuse Projectile with higher damage
                    p = Projectile((self.rect.right - 8, self.rect.centery))
                    p.damage_value = self.shell_damage
                    projectiles.add(p)
                    self.shoot_timer = self.shoot_cooldown
                    break


class LaserGun(Human):
    """Fires very fast, low-damage laser shots in-lane."""

    def __init__(self, pos: tuple[int, int], lane_row: int | None = None) -> None:
        super().__init__(pos, lane_row)
        self.image = draw_laser_gun()
        self.shoot_cooldown = 0.4
        self.laser_damage = 1

    def try_shoot(self, projectiles: pygame.sprite.Group, robots: pygame.sprite.Group | None) -> None:
        if self.shoot_timer <= 0.0:
            should_fire = False
            if robots is None:
                should_fire = True
            else:
                for r in robots:
                    lane_r = getattr(r, "lane_row", None)
                    if self.lane_row is not None and lane_r is not None:
                        if lane_r == self.lane_row and r.rect.centerx > self.rect.centerx:
                            should_fire = True
                            break
            if should_fire:
                proj = Projectile((self.rect.right - 8, self.rect.centery))
                proj.damage_value = self.laser_damage
                projectiles.add(proj)
                self.shoot_timer = self.shoot_cooldown


class GatlingPea(LaserGun):
    """A very fast-firing unit, an upgrade to the LaserGun."""

    def __init__(self, pos: tuple[int, int], lane_row: int | None = None) -> None:
        super().__init__(pos, lane_row)
        self.image = draw_gatling_pea()
        self.shoot_cooldown = 0.25  # Even faster than LaserGun
        self.laser_damage = 1


class Virus(Entity):
    """Stationary hazard that kills robots on contact and briefly grows to show spread."""

    def __init__(self, pos: tuple[int, int]) -> None:
        super().__init__()
        self.image = draw_virus()
        self.rect = self.image.get_rect(center=pos)
        self.alive_hp = WALL_HP // 3
        self.radius = VIRUS_RADIUS
        self.grow_timer = VIRUS_GROW_TIME
        self.life_timer = VIRUS_LIFETIME

    def update(self, dt: float, robots: pygame.sprite.Group) -> None:
        # Grow animation on place
        if self.grow_timer > 0:
            self.grow_timer = max(0.0, self.grow_timer - dt)
        self.life_timer -= dt
        if self.life_timer <= 0:
            self.kill()
            return
        # Contact kill: on touch or near-radius
        cx, cy = self.rect.center
        rr = self.radius * (1.1 if self.grow_timer > 0 else 1.0)
        rr2 = rr * rr
        kill_box = self.rect.inflate(20, 20)
        for r in list(robots):
            if r.rect.colliderect(kill_box):
                r.damage(VIRUS_DAMAGE)
                continue
            dx = r.rect.centerx - cx
            dy = r.rect.centery - cy
            if dx * dx + dy * dy <= rr2:
                r.damage(VIRUS_DAMAGE)

    def render(self, screen: pygame.Surface) -> None:
        # Base image
        super().render(screen)
        # Subtle spread ring
        cx, cy = self.rect.center
        rr = int(self.radius * (1.2 if self.grow_timer > 0 else 1.0))
        ring = pygame.Surface((rr * 2 + 6, rr * 2 + 6), pygame.SRCALPHA)
        # pulsing alpha
        import math
        pulse = int(120 + 100 * (0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.008)))
        pygame.draw.circle(ring, (255, 40, 40, pulse), (rr + 3, rr + 3), rr, width=8)
        pygame.draw.circle(ring, (255, 60, 60, 60), (rr + 3, rr + 3), max(1, rr - 6))
        screen.blit(ring, (cx - rr - 2, cy - rr - 2))


class BubbleShooter(Human):
    """Fires bubble projectiles that slow and damage robots."""
    
    def __init__(self, pos: tuple[int, int], lane_row: int | None = None) -> None:
        super().__init__(pos, lane_row)
        self.image = draw_bubble_shooter()
        self.shoot_cooldown = 2.0  # Slower than regular shooter
        self.bubble_damage = 2  # More damage than regular projectiles
    
    def try_shoot(self, projectiles: pygame.sprite.Group, robots: pygame.sprite.Group | None) -> None:
        if self.shoot_timer <= 0.0:
            should_fire = False
            if robots is None:
                should_fire = True
            else:
                for r in robots:
                    lane_r = getattr(r, "lane_row", None)
                    if self.lane_row is not None and lane_r is not None:
                        if lane_r == self.lane_row and r.rect.centerx > self.rect.centerx:
                            should_fire = True
                            break
                    else:
                        if r.rect.centerx > self.rect.centerx and abs(r.rect.centery - self.rect.centery) < self.rect.h // 2:
                            should_fire = True
                            break
            if should_fire:
                proj = BubbleProjectile((self.rect.right - 8, self.rect.centery))
                projectiles.add(proj)
                self.shoot_timer = self.shoot_cooldown


class BubbleProjectile(Projectile):
    def __init__(self, pos: tuple[int, int]) -> None:
        super().__init__(pos)
        self.image = draw_bubble_projectile()
        self.damage_value = 2  # More damage than regular projectiles
    
    def update(self, dt: float, robots: pygame.sprite.Group) -> None:
        self.rect.x += int(self.speed * dt)
        hits = pygame.sprite.spritecollide(self, robots, False)  # type: ignore
        if hits:
            for rob in hits:
                if isinstance(rob, Robot):
                    rob.damage(self.damage_value)
                    rob.apply_slow(0.6, 1.5)  # Slow robots with bubbles
            self.kill()
        if self.rect.left > 1400:
            self.kill()


class ShieldDefender(Entity):
    """Creates energy shields that protect nearby units from damage."""
    
    def __init__(self, pos: tuple[int, int]) -> None:
        super().__init__()
        self.image = draw_shield_defender()
        self.rect = self.image.get_rect(center=pos)
        self.alive_hp = WALL_HP // 2  # 150 HP
        self.shield_radius = TILE_SIZE * 1.5  # Shield covers 1.5 tiles around
        self.shield_timer = 0.0
        self.shield_cooldown = 3.0  # Shield recharges every 3 seconds
        self.shield_active = True
        self.shield_strength = 50  # Absorbs 50 damage before going down
        self.current_shield = self.shield_strength
    
    def update(self, dt: float, robots: pygame.sprite.Group, units: pygame.sprite.Group | None = None) -> None:
        # Recharge shield over time
        if not self.shield_active:
            self.shield_timer += dt
            if self.shield_timer >= self.shield_cooldown:
                self.shield_active = True
                self.current_shield = self.shield_strength
                self.shield_timer = 0.0
                print(f"🛡️ Shield recharged!")
        
        # Protect nearby units by absorbing damage from robots
        if self.shield_active and units:
            cx, cy = self.rect.center
            for unit in units:
                if unit == self:  # Don't protect self
                    continue
                    
                unit_distance = ((unit.rect.centerx - cx) ** 2 + (unit.rect.centery - cy) ** 2) ** 0.5
                if unit_distance <= self.shield_radius:
                    # Check if any robots are attacking this unit
                    for robot in robots:
                        if (hasattr(robot, 'chewing_target') and 
                            robot.chewing_target == unit and 
                            self.current_shield > 0):
                            # Absorb some of the damage
                            absorbed_damage = min(5, self.current_shield)  # Absorb up to 5 damage per frame
                            self.current_shield -= absorbed_damage
                            
                            if self.current_shield <= 0:
                                self.shield_active = False
                                self.shield_timer = 0.0
                                print(f"🛡️ Shield depleted! Recharging...")
                                break
    
    def render(self, screen: pygame.Surface) -> None:
        # Draw the unit
        super().render(screen)
        
        # Draw shield effect if active
        if self.shield_active:
            cx, cy = self.rect.center
            shield_radius = int(self.shield_radius)
            
            # Calculate shield alpha based on current strength
            alpha = int(100 + (self.current_shield / self.shield_strength) * 100)
            
            # Create shield surface
            shield_surface = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
            
            # Draw shield ring
            pygame.draw.circle(shield_surface, (100, 200, 255, alpha), (shield_radius, shield_radius), shield_radius, width=3)
            pygame.draw.circle(shield_surface, (150, 220, 255, alpha // 2), (shield_radius, shield_radius), shield_radius - 10, width=2)
            
            # Position shield surface
            shield_rect = shield_surface.get_rect(center=(cx, cy))
            screen.blit(shield_surface, shield_rect)


class NightStalker(Entity):
    """Unit with a square shield that produces a deadly electric wave."""
    
    def __init__(self, pos: tuple[int, int], lane_row: int | None = None) -> None:
        super().__init__()
        self.image = draw_night_stalker()
        self.rect = self.image.get_rect(center=pos)
        self.alive_hp = NIGHT_STALKER_HP
        self.lane_row = lane_row
        
        # Electric wave mechanics
        self.wave_cooldown = 5.0  # Time between waves
        self.wave_timer = self.wave_cooldown
        self.wave_active = False
        self.wave_radius = 0.0
        self.wave_max_radius = TILE_SIZE * 2.5
        self.wave_speed = 250.0
        self.wave_count = 0
        self.max_waves = 3
    
    def update(self, dt: float, robots: pygame.sprite.Group) -> None:
        # If max waves have been produced, do nothing further.
        if self.wave_count >= self.max_waves and not self.wave_active:
            return

        # Update timers
        self.wave_timer = max(0.0, self.wave_timer - dt)

        if self.wave_timer <= 0.0 and not self.wave_active and self.wave_count < self.max_waves:
            self.wave_active = True
            self.wave_radius = 0.0

        if self.wave_active:
            self.wave_radius += self.wave_speed * dt
            wave_rect = pygame.Rect(
                self.rect.centerx - self.wave_radius,
                self.rect.centery - self.wave_radius,
                self.wave_radius * 2,
                self.wave_radius * 2,
            )

            for robot in list(robots):
                if wave_rect.colliderect(robot.rect):
                    robot.damage(9999) # Instant kill

            if self.wave_radius >= self.wave_max_radius:
                self.wave_count += 1
                self.wave_active = False
                if self.wave_count >= self.max_waves:
                    self.kill() # Disappear after the final wave
                else:
                    self.wave_timer = self.wave_cooldown
    
    def render(self, screen: pygame.Surface) -> None:
        # Draw the unit
        super().render(screen)
        
        # Draw the square shield
        shield_size = TILE_SIZE * 1.2
        shield_rect = pygame.Rect(0, 0, shield_size, shield_size)
        shield_rect.center = self.rect.center
        
        # Pulsing alpha for the shield
        import math
        pulse = 100 + 50 * (0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.004))
        shield_color = (100, 200, 255, pulse)
        pygame.draw.rect(screen, shield_color, shield_rect, 4, border_radius=8)

        # Draw the expanding electric wave
        if self.wave_active:
            wave_rect = pygame.Rect(0, 0, self.wave_radius * 2, self.wave_radius * 2)
            wave_rect.center = self.rect.center
            
            # Fade out the wave as it expands
            wave_alpha = 255 * (1 - (self.wave_radius / self.wave_max_radius))
            wave_color = (200, 255, 255, wave_alpha)
            pygame.draw.rect(screen, wave_color, wave_rect, 5, border_radius=12)


class ShadowHealer(Entity):
    """Night-themed healer that can cloak and heal nearby units."""
    
    def __init__(self, pos: tuple[int, int]) -> None:
        super().__init__()
        self.image = draw_shadow_healer()
        self.rect = self.image.get_rect(center=pos)
        self.alive_hp = SHADOW_HEALER_HP
        
        # Healing mechanics
        self.heal_amount = SHADOW_HEALER_HEAL_AMOUNT
        self.heal_radius = SHADOW_HEALER_HEAL_RADIUS
        self.heal_cooldown = SHADOW_HEALER_HEAL_COOLDOWN
        self.heal_timer = 0.0
        
        # Cloak mechanics
        self.is_cloaked = False
        self.cloak_timer = 0.0
        self.cloak_duration = SHADOW_HEALER_CLOAK_DURATION
        self.cloak_cooldown = 10.0
        self.cloak_cooldown_timer = 0.0
        
        # Visual effects
        self.original_image = self.image.copy()
        self.cloaked_alpha = 120  # Semi-transparent when cloaked
    
    def update(self, dt: float, units: pygame.sprite.Group, robots: pygame.sprite.Group | None = None) -> None:
        # Update timers
        self.heal_timer = max(0.0, self.heal_timer - dt)
        
        # Handle cloak mechanics
        if self.is_cloaked:
            self.cloak_timer -= dt
            if self.cloak_timer <= 0:
                self._exit_cloak()
        else:
            self.cloak_cooldown_timer = max(0.0, self.cloak_cooldown_timer - dt)
            # Auto-activate cloak when under threat and cooldown is ready
            if self.cloak_cooldown_timer <= 0 and robots:
                nearby_threats = self._count_nearby_threats(robots)
                if nearby_threats >= 2:  # Cloak when 2+ robots nearby
                    self._enter_cloak()
        
        # Heal nearby units
        if self.heal_timer <= 0:
            healed_count = self._heal_nearby_units(units)
            if healed_count > 0:
                self.heal_timer = self.heal_cooldown
    
    def _enter_cloak(self) -> None:
        """Activate cloak mode."""
        self.is_cloaked = True
        self.cloak_timer = self.cloak_duration
        # Create semi-transparent image
        self.image = self.original_image.copy()
        self.image.set_alpha(self.cloaked_alpha)
        print(f"🌙 Shadow Healer cloaked!")
    
    def _exit_cloak(self) -> None:
        """Deactivate cloak mode."""
        self.is_cloaked = False
        self.cloak_cooldown_timer = self.cloak_cooldown
        # Restore full opacity
        self.image = self.original_image.copy()
        self.image.set_alpha(255)
        print(f"✨ Shadow Healer cloak ended")
    
    def _count_nearby_threats(self, robots: pygame.sprite.Group) -> int:
        """Count robots within threat detection range."""
        threat_count = 0
        cx, cy = self.rect.center
        threat_range = self.heal_radius * 1.5  # Larger threat detection
        
        for robot in robots:
            if isinstance(robot, Robot):
                dx = robot.rect.centerx - cx
                dy = robot.rect.centery - cy
                distance = (dx * dx + dy * dy) ** 0.5
                if distance <= threat_range:
                    threat_count += 1
        
        return threat_count
    
    def _heal_nearby_units(self, units: pygame.sprite.Group) -> int:
        """Heal nearby damaged units and return count of units healed."""
        healed_count = 0
        cx, cy = self.rect.center
        
        for unit in units:
            if unit == self:  # Don't heal self
                continue
            
            # Check if unit is within heal range
            dx = unit.rect.centerx - cx
            dy = unit.rect.centery - cy
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance <= self.heal_radius:
                # Check if unit needs healing
                max_hp = self._get_unit_max_hp(unit)
                if hasattr(unit, 'alive_hp') and unit.alive_hp < max_hp:
                    # Heal the unit
                    old_hp = unit.alive_hp
                    unit.alive_hp = min(max_hp, unit.alive_hp + self.heal_amount)
                    if unit.alive_hp > old_hp:
                        healed_count += 1
                        print(f"✨ Shadow Healer healed unit for {unit.alive_hp - old_hp} HP")
        
        return healed_count
    
    def _get_unit_max_hp(self, unit) -> int:
        """Get the maximum HP for a given unit type."""
        if isinstance(unit, WallHuman):
            return WALL_HP
        elif isinstance(unit, Human):
            return SHOOTER_HP
        elif isinstance(unit, Generator):
            return GENERATOR_HP
        elif isinstance(unit, ShieldDefender):
            return WALL_HP // 2  # 150 HP
        elif isinstance(unit, NightStalker):
            return NIGHT_STALKER_HP
        elif isinstance(unit, ShadowHealer):
            return SHADOW_HEALER_HP
        else:
            return 10  # Default for unknown units
    
    def render(self, screen: pygame.Surface) -> None:
        # Draw the unit
        super().render(screen)
        
        # Draw healing aura
        cx, cy = self.rect.center
        heal_radius = int(self.heal_radius)
        
        # Pulsing heal aura
        import math
        pulse = int(80 + 40 * (0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.005)))
        
        # Create healing aura surface
        aura_surface = pygame.Surface((heal_radius * 2, heal_radius * 2), pygame.SRCALPHA)
        
        # Draw healing ring
        pygame.draw.circle(aura_surface, (100, 255, 150, pulse), (heal_radius, heal_radius), heal_radius, width=2)
        pygame.draw.circle(aura_surface, (150, 255, 180, pulse // 2), (heal_radius, heal_radius), heal_radius - 10, width=1)
        
        # Position aura surface
        aura_rect = aura_surface.get_rect(center=(cx, cy))
        screen.blit(aura_surface, aura_rect)
        
        # Draw cloak effect if active
        if self.is_cloaked:
            # Create pulsing cloak effect
            cloak_pulse = int(60 + 30 * (0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.008)))
            
            # Draw cloak aura
            cloak_surface = pygame.Surface((90, 90), pygame.SRCALPHA)
            pygame.draw.circle(cloak_surface, (150, 100, 200, cloak_pulse), (45, 45), 40, width=3)
            pygame.draw.circle(cloak_surface, (180, 130, 230, cloak_pulse // 2), (45, 45), 35, width=2)
            
            cloak_rect = cloak_surface.get_rect(center=(cx, cy))
            screen.blit(cloak_surface, cloak_rect)


class IceShroom(Entity):
    """Instant-use unit that freezes all robots on the screen upon placement."""

    def __init__(self, pos: tuple[int, int]) -> None:
        super().__init__()
        self.image = draw_ice_shroom()
        self.rect = self.image.get_rect(center=pos)
        self.alive_hp = 1  # It's an instant-use unit
        self.effect_triggered = False

    def update(self, dt: float, projectiles: pygame.sprite.Group, robots: pygame.sprite.Group | None = None) -> None:
        if not self.effect_triggered and robots is not None:
            print("❄️🍄 Ice Shroom deployed! Freezing all robots!")
            for robot in robots:
                if isinstance(robot, Robot):
                    # Apply a strong slow effect for a long duration
                    robot.apply_slow(0.0, 6.0)  # 0.0 factor means a complete freeze for 6 seconds
            
            self.effect_triggered = True
            # Remove itself after the effect is triggered
            self.kill()


class DoomShroom(Entity):
    """Instant-use unit that creates a massive explosion and leaves a crater."""

    def __init__(self, pos: tuple[int, int], crater_group: pygame.sprite.Group, effects_group: pygame.sprite.Group) -> None:
        super().__init__()
        self.image = draw_doom_shroom()
        self.rect = self.image.get_rect(center=pos)
        self.alive_hp = 1
        self.timer = DOOM_SHROOM_ARM_TIME
        self.crater_group = crater_group
        self.effects_group = effects_group

    def update(self, dt: float, projectiles: pygame.sprite.Group, robots: pygame.sprite.Group | None = None) -> None:
        self.timer -= dt
        if self.timer <= 0.0:
            print("💥🍄 DOOM! Massive explosion!")
            center = self.rect.center

            # Post a screen shake event
            from game.scenes import SCREEN_SHAKE_EVENT
            shake_event = pygame.event.Event(SCREEN_SHAKE_EVENT, magnitude=15, duration=0.4)
            pygame.event.post(shake_event)
            # Create the visual explosion effect
            self.effects_group.add(ExplosionEffect(center, DOOM_SHROOM_RADIUS))

            if robots:
                for r in list(robots):
                    if isinstance(r, Robot):
                        distance = pygame.math.Vector2(r.rect.center).distance_to(center)
                        if distance <= DOOM_SHROOM_RADIUS:
                            r.damage(9999) # Instant kill
            
            # Leave a crater
            crater = Crater(center)
            self.crater_group.add(crater)
            
            self.kill()


class Crater(Entity):
    """A temporary crater that blocks planting."""

    def __init__(self, pos: tuple[int, int]) -> None:
        super().__init__()
        self.image = draw_crater()
        self.rect = self.image.get_rect(center=pos)
        self.alive_hp = 1
        self.lifetime = CRATER_LIFETIME

    def update(self, dt: float) -> None:
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()


class ExplosionEffect(Entity):
    """A visual effect for a large explosion, like from DoomShroom."""

    def __init__(self, pos: tuple[int, int], radius: float, duration: float = 0.5) -> None:
        super().__init__()
        self.center = pos
        self.max_radius = radius
        self.duration = duration
        self.lifetime = duration

    def update(self, dt: float) -> None:
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()

    def render(self, screen: pygame.Surface) -> None:
        if self.lifetime <= 0:
            return

        progress = 1.0 - (self.lifetime / self.duration)  # 0 to 1
        current_radius = self.max_radius * progress
        alpha = int(255 * (1.0 - progress**2))  # Fade out quickly

        # Draw multiple expanding circles for a shockwave effect
        pygame.draw.circle(screen, (255, 200, 100, alpha), self.center, int(current_radius), width=int(current_radius * 0.2))
        pygame.draw.circle(screen, (255, 100, 50, alpha * 0.7), self.center, int(current_radius * 0.7), width=int(current_radius * 0.15))
        pygame.draw.circle(screen, (255, 255, 255, alpha * 0.5), self.center, int(current_radius * 0.4))


class SunShroom(Entity):
    """Grows over time to produce more energy."""

    def __init__(self, pos: tuple[int, int]) -> None:
        super().__init__()
        self.stage = 0  # 0 for small, 1 for large
        self.image = draw_sun_shroom(self.stage)
        self.rect = self.image.get_rect(center=pos)
        self.alive_hp = GENERATOR_HP
        self.growth_timer = SUN_SHROOM_GROW_TIME
        self.spawn_timer = SUN_SHROOM_INITIAL_COOLDOWN

    def update(self, dt: float, energy_group: pygame.sprite.Group) -> None:
        # Handle growth
        if self.stage == 0 and self.growth_timer > 0:
            self.growth_timer -= dt
            if self.growth_timer <= 0:
                self.stage = 1
                center = self.rect.center
                self.image = draw_sun_shroom(self.stage)
                self.rect = self.image.get_rect(center=center)
                print("🍄 Sun-shroom grew to full size!")

        # Handle energy production
        self.spawn_timer -= dt
        if self.spawn_timer <= 0.0:
            if self.stage == 0:
                self.spawn_timer = SUN_SHROOM_INITIAL_COOLDOWN
                drop = EnergyDrop((self.rect.centerx, self.rect.y - 10), value=SUN_SHROOM_SMALL_ENERGY)
            else: # stage 1
                self.spawn_timer = SUN_SHROOM_NORMAL_COOLDOWN
                drop = EnergyDrop((self.rect.centerx, self.rect.y - 10), value=ENERGY_DROP_VALUE)
            
            energy_group.add(drop)


class PuffShroom(Human):
    """A free, short-range, temporary attacker."""

    def __init__(self, pos: tuple[int, int], lane_row: int | None = None) -> None:
        super().__init__(pos, lane_row)
        self.image = draw_puff_shroom()
        self.rect = self.image.get_rect(center=pos)
        self.alive_hp = PUFF_SHROOM_HP
        self.lifetime = PUFF_SHROOM_LIFETIME
        self.attack_range = PUFF_SHROOM_RANGE

    def update(self, dt: float, projectiles: pygame.sprite.Group, robots: pygame.sprite.Group | None = None) -> None:
        # Countdown lifetime
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return
        
        # Use base Human update for shooting
        super().update(dt, projectiles, robots)

    def try_shoot(self, projectiles: pygame.sprite.Group, robots: pygame.sprite.Group | None) -> None:
        # Override to use a custom attack range
        if self.shoot_timer <= 0.0 and robots:
            for r in robots:
                if self.lane_row is not None and getattr(r, "lane_row", None) == self.lane_row and 0 < (r.rect.centerx - self.rect.centerx) < self.attack_range:
                    proj = Projectile((self.rect.right - 8, self.rect.centery))
                    projectiles.add(proj)
                    self.shoot_timer = self.shoot_cooldown
                    break


class ScaredyShroom(Human):
    """A cheap, long-range shooter that hides when robots get close."""

    def __init__(self, pos: tuple[int, int], lane_row: int | None = None) -> None:
        super().__init__(pos, lane_row)
        self.is_scared = False
        self.original_image = draw_scaredy_shroom(scared=False)
        self.scared_image = draw_scaredy_shroom(scared=True)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=pos)
        self.alive_hp = SCAREDY_SHROOM_HP
        self.scared_range = SCAREDY_SHROOM_SCARED_RANGE

    def update(self, dt: float, projectiles: pygame.sprite.Group, robots: pygame.sprite.Group | None = None) -> None:
        self.shoot_timer = max(0.0, self.shoot_timer - dt)
        
        # Check if scared
        self.is_scared = False
        if robots:
            for r in robots:
                distance = abs(r.rect.centerx - self.rect.centerx)
                if distance < self.scared_range:
                    self.is_scared = True
                    break
        
        # Update visual state based on fear
        self.image = self.scared_image if self.is_scared else self.original_image

        # Only try to shoot if not scared
        if not self.is_scared:
            self.try_shoot(projectiles, robots)


class Leaf(Entity):
    """A simple leaf that can be placed on water, acting as a weak blocker."""

    def __init__(self, pos: tuple[int, int]) -> None:
        super().__init__()
        self.image = draw_leaf()
        self.rect = self.image.get_rect(center=pos)
        self.alive_hp = GENERATOR_HP # Same HP as a generator


class SeaMine(Entity):
    """Aquatic mine that explodes when robots get close"""

    def __init__(self, pos: tuple[int, int]) -> None:
        super().__init__()
        self.image = draw_sea_mine()
        self.rect = self.image.get_rect(center=pos)
        self.timer = 1.5 # arming time
        self.effect_triggered = False

    def update(self, dt: float, robots: pygame.sprite.Group) -> None:
        self.timer -= dt
        if self.timer <= 0.0 and not self.effect_triggered:
            # Find a robot in proximity and detonate the mine
            for robot in robots:
                if self.rect.colliderect(robot.rect):
                    # Explosion!
                    from game.scenes import SCREEN_SHAKE_EVENT
                    shake_event = pygame.event.Event(SCREEN_SHAKE_EVENT, magnitude=10, duration=0.3)
                    pygame.event.post(shake_event)

                    robot.damage(BOMB_DAMAGE)
                    self.kill() # Sea Mine disappears after use
                    self.effect_triggered = True # Ensure it only runs once
                    print(f"💥 Sea Mine exploded!")
                    break



class TangleKelp(Entity):
    """An instant-use plant that drags the first robot on its tile underwater."""

    def __init__(self, pos: tuple[int, int]) -> None:
        super().__init__()
        self.image = draw_tangle_kelp()
        self.rect = self.image.get_rect(center=pos)
        self.alive_hp = 1 # Instant use
        self.effect_triggered = False

    def update(self, dt: float, robots: pygame.sprite.Group) -> None:
        if not self.effect_triggered:
            # Find a robot on the same tile and kill it
            for robot in robots:
                if self.rect.colliderect(robot.rect):
                    robot.damage(9999) # Instant kill
                    self.kill() # Tangle Kelp disappears after use
                    break
            self.effect_triggered = True # Ensure it only runs once


class SeaShroom(PuffShroom):
    """An aquatic, temporary attacker, similar to PuffShroom."""

    def __init__(self, pos: tuple[int, int], lane_row: int | None = None) -> None:
        super().__init__(pos, lane_row)
        self.image = draw_sea_shroom()


class Cattail(Human):
    """An upgrade for Lily Pad that shoots homing spikes at the nearest robot."""

    def __init__(self, pos: tuple[int, int]) -> None:
        # Cattail doesn't have a lane, it can target any lane
        super().__init__(pos, lane_row=None)
        self.image = draw_cattail()
        self.rect = self.image.get_rect(center=pos)
        self.alive_hp = SHOOTER_HP * 2 # Tougher than a normal shooter
        self.shoot_cooldown = 1.0 # Fires reasonably fast

    def try_shoot(self, projectiles: pygame.sprite.Group, robots: pygame.sprite.Group | None) -> None:
        if self.shoot_timer <= 0.0 and robots and len(robots) > 0:
            # Find the nearest robot on the entire screen
            my_pos = pygame.math.Vector2(self.rect.center)
            
            closest_robot = None
            min_dist_sq = float('inf')

            for robot in robots:
                dist_sq = my_pos.distance_to_squared(robot.rect.center)
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    closest_robot = robot
            
            if closest_robot:
                proj = SpikeProjectile(self.rect.center, closest_robot)
                projectiles.add(proj)
                self.shoot_timer = self.shoot_cooldown
