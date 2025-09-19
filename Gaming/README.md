# Humans vs AI Robots (Pygame)

A tower-defense game inspired by Plants vs Zombies, re-imagined as Humans vs AI Robots.

- Themes: Day, Night, Fog, Water, Roof
- 10 levels per theme (50 total)
- Each level unlocks 1 new thing (unit, obstacle, mechanic, or upgrade)

## Quickstart

1. Python 3.10+
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run:

```bash
python -m game
```

## Controls

- Left-click: place the selected unit on a tile (blocked on water lane in Water theme)
- Right-click: collect yellow energy drops
- 1..4 or click seed packet: select unit type
- Q or click Shovel: toggle shovel mode; then left-click a placed unit/tile to remove it
- ESC: quit
- Menu: Left/Right to choose theme, Enter to start

## Gameplay

- Energy economy: start with 50 energy. Energy drops fall from the sky and are produced by Generators. Right-click a drop to collect.
- Seed packets have costs and cooldowns. Packets show a dark overlay when cooling down and a red overlay if you don’t have enough energy.
- Lawn mowers: one per lane; if a robot reaches the left edge of a lane, that lane’s mower triggers and sweeps through robots.
- Win/Lose: survive the level timer to win; if robots breach lanes three times, you lose.

### Units and costs

- 1 Shooter: 100 energy, fires projectiles in its lane
- 2 Wall: 50 energy, high HP blocker
- 3 Generator: 50 energy, periodically spawns energy drops
- 4 Bomb: 150 energy, arms briefly then explodes in a small radius

### Themes

- Day/Night: visual palettes
- Fog: translucent fog overlay
- Water: middle lane is water; placement is blocked there for now
- Roof: visual palette (slope mechanics not yet added)

## Project Structure

- `game/`: source code
  - `__init__.py`, `__main__.py`: entry
  - `config.py`: constants and theme/level config
  - `assets.py`: lazy asset generation (colors/shapes)
  - `core.py`: engine, scenes, game loop
  - `grid.py`: board/grid logic
  - `entities/`: actors (humans/robots/projectiles)
  - `ui/`: HUD, selection bar
  - `levels/`: level manager

## Notes

- Assets are procedurally drawn shapes for now to keep the project lightweight.
- Save file `save.json` will store unlocks and progress.

### Use your own sprites

- Robots: Put PNGs in `game/images/robots/` (any names). The game randomly picks among them. Single-sprite fallbacks: `game/images/robot.png` or `game/images/robot_basic.png`.
- Humans: Place unit PNGs at `game/images/units/` or `game/images/`. Supported names: `shooter.png`, `frozen.png` (or `frozen_shooter.png`), `wall.png`, `generator.png`, `bomb.png`, `healer.png`. Size 56x56 recommended. If missing, simple shapes are used.

## License

MIT
