import json
from pathlib import Path
from typing import Optional, List
from core.inventory import Inventory
from core.display import print_color


class GameState:
    def __init__(self):
        self.name: str = "Adventurer"
        self.player_color: str = "255 255 255"
        self.location: str = "Start"
        self.health: int = 100
        self.max_health: int = 100
        self.mana: int = 60
        self.max_mana: int = 60
        self.stamina: int = 60
        self.max_stamina: int = 60
        self.gold: int = 0
        self.inventory: Inventory = Inventory()
        self.level: int = 1
        self.xp: int = 0
        self.next_level: int = 100
        self.player_class: Optional[PlayerClass] = None
        self.race: str = "Human"
        self.npc_met: dict = {}
        self.npc_topics_asked: dict = {}
        self.locations_visited: dict = {}
        self.wilson_employee: bool = False
        self.wilson_room_access: bool = False
        self.equipped_weapon: Optional[str] = None
        self.equipped_armor: Optional[str] = None
        self.equipped_rod: Optional[str] = None
        self.active_quests: List = []
        self.completed_quests: List[str] = []
        self.active_effects: list = []
        self.journal_entries: List[str] = []

    def save(self) -> None:
        saves_dir = Path("saves")
        saves_dir.mkdir(exist_ok=True)
        save_path = saves_dir / f"{self.name}.json"
        save_data = self.__dict__.copy()

        if isinstance(self.player_class, PlayerClass):
            save_data["player_class"] = self.player_class.name

        # Convert inventory to dict
        save_data["inventory"] = self.inventory.to_dict()

        # Convert quests to dicts
        save_data["active_quests"] = [q.to_dict() for q in self.active_quests]

        save_data["active_effects"] = list(self.active_effects)

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2)
        print_color(f"Game saved to {save_path}", 50, 255, 50)

    @staticmethod
    def load(file_path: str) -> "GameState":
        # Add saves/ prefix if not already there
        if not file_path.startswith("saves/") and not file_path.startswith("saves\\"):
            file_path = f"saves/{file_path}"

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError("Save file not found")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        state = GameState()

        # Copy all properties from JSON to the new state object
        for key, value in data.items():
            setattr(state, key, value)

        # Convert player_class string back to PlayerClass object
        if isinstance(state.player_class, str):
            class_map = {
                "Fighter": FIGHTER,
                "Warlock": WARLOCK,
                "Rogue": ROGUE,
                "Paladin": PALADIN,
                "Cleric": CLERIC,
            }
            state.player_class = class_map.get(state.player_class, None)

        if isinstance(state.inventory, list):
            state.inventory = Inventory.from_dict(state.inventory)

        # Load quests
        if isinstance(state.active_quests, list) and state.active_quests:
            from quests.quests import Quest

            loaded_quests = []
            for quest_data in state.active_quests:
                if isinstance(quest_data, dict):
                    loaded_quests.append(Quest.from_dict(quest_data))
            state.active_quests = loaded_quests

        state.save()
        return state


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
