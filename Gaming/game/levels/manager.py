from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Tuple

from game.config import THEMES, LEVELS_PER_THEME


@dataclass
class LevelRef:
    theme: str
    index: int  # 1..10


class LevelManager:
    def __init__(self, save_path: str = "save.json") -> None:
        self.save_path = save_path
        self.unlocked: dict[str, int] = {t: 1 for t in THEMES}
        self.current: LevelRef = LevelRef(THEMES[0], 1)
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.save_path):
            try:
                with open(self.save_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.unlocked = data.get("unlocked", self.unlocked)
                t = data.get("current_theme", THEMES[0])
                i = int(data.get("current_index", 1))
                self.current = LevelRef(t, i)
            except Exception:
                pass

    def _save(self) -> None:
        data = {
            "unlocked": self.unlocked,
            "current_theme": self.current.theme,
            "current_index": self.current.index,
        }
        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def set_current(self, theme: str, idx: int) -> None:
        self.current = LevelRef(theme, idx)
        self._save()

    def complete_current(self) -> None:
        unlocked_idx = self.unlocked.get(self.current.theme, 1)
        if self.current.index >= unlocked_idx and self.current.index < LEVELS_PER_THEME:
            self.unlocked[self.current.theme] = self.current.index + 1
        self._save()

    def get_current(self) -> LevelRef:
        return self.current


