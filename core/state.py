import json
from pathlib import Path
from typing import Optional, List
from core.classes import PlayerClass, FIGHTER, WARLOCK, ROGUE, PALADIN, CLERIC
from core.inventory import Inventory
from core.utils import print_color


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
