from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.state import GameState


class PlayerClass:
    def __init__(
        self,
        name: str,
        description: str,
        health_mod: float = 1.0,
        damage_mod: float = 1.0,
        gold_mod: float = 1.0,
        mana_mod: float = 0.0,
        stamina_mod: float = 0.0,
    ):
        self.name = name
        self.description = description
        self.health_mod = health_mod
        self.damage_mod = damage_mod
        self.gold_mod = gold_mod
        self.mana_mod = mana_mod
        self.stamina_mod = stamina_mod

    def apply_to_state(self, state: GameState) -> None:
        """Apply class modifiers to a game state"""
        state.max_health = int(100 * self.health_mod)
        state.health = state.max_health
        state.max_mana = int(60 * self.mana_mod)
        state.mana = state.max_mana
        state.max_stamina = int(60 * self.stamina_mod)
        state.stamina = state.max_stamina


# region Player Classes
FIGHTER = PlayerClass(
    "Fighter",
    "Strong and capable",
    health_mod=1.5,
    damage_mod=1.5,
    gold_mod=1.2,
    mana_mod=0.0,
    stamina_mod=1.5,
)

WARLOCK = PlayerClass(
    "Warlock",
    "Dark and mysterious",
    health_mod=0.9,
    damage_mod=1.1,
    gold_mod=1.2,
    mana_mod=1.5,
    stamina_mod=0.0,
)

ROGUE = PlayerClass(
    "Rogue",
    "Quick and lonesome",
    health_mod=1.0,
    damage_mod=1.2,
    gold_mod=1.5,
    mana_mod=0.0,
    stamina_mod=1.3,
)

PALADIN = PlayerClass(
    "Paladin",
    "Holy warrior, jack of all trades",
    health_mod=1.2,
    damage_mod=1.3,
    gold_mod=1.0,
    mana_mod=0.8,
    stamina_mod=0.8,
)

CLERIC = PlayerClass(
    "Cleric",
    "Divine healer and protector",
    health_mod=0.7,
    damage_mod=0.9,
    gold_mod=1.1,
    mana_mod=1.4,
    stamina_mod=0.0,
)
# endregion
