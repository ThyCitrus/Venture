"""
venture.py - A simple text-based adventure game.
"""

# region Imports
import json
import math
from pathlib import Path
from typing import Optional
import time
import sys
from typing import List
import os
import subprocess
import random
from core.utils import *
from core.constants import *
from core.combat import combat, Enemy
from data.items import ITEMS
from data.map import show_map
from quests.quests import start_quest, advance_quest, is_quest_active, show_quest_log
from quests.hooks import get_location_hook
from core.locations import kimaer, wilsons_bar, shop, buy_items, sell_items, SHOP_DATA
from dialogue.kimaer.wilson import *
from dialogue.kimaer.benji import *
from dialogue.kimaer.celeste import *
from dialogue.kimaer.roslin import *
from dialogue.kimaer.silas import *

# endregion


# location ideas: ["Kimaer", "Lunara", "Duskwood", "Eldoria", "Frostholm", "Lake", "Cave", "Gulf of Burhkeria", "Nyctos Deep"]


# region NPC Keys
# Define NPC keys as constants so they can be checked anywhere
KIMAER_BENJI = "kimaer_benji"
KIMAER_ROSLIN = "kimaer_roslin"
KIMAER_CELESTE = "kimaer_celeste"
KIMAER_WILSON = "kimaer_wilson"
KIMAER_SILAS = "kimaer_silas"

# endregion


# region Classes
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


class InventoryItem:
    def __init__(self, name: str, item_type: str, count: int = 1, value: int = 0):
        self.name = name
        self.item_type = item_type  # "potion", "weapon", "quest", "misc", etc.
        self.count = count
        self.value = value


class Inventory:
    def __init__(self):
        self.items: List[InventoryItem] = []

    def add_item(self, name: str, count: int = 1) -> None:
        """Add an item to inventory using the item database"""
        if name not in ITEMS:
            print_color(f"Warning: Unknown item '{name}'", 255, 100, 100)
            return

        item_data = ITEMS[name]

        for item in self.items:
            if item.name == name:
                item.count += count
                return

        # Item doesn't exist, add new
        self.items.append(
            InventoryItem(name, item_data["type"], count, item_data["value"])
        )

    def remove_item(self, name: str, count: int = 1) -> bool:
        """Remove count of item. Returns True if successful, False if not enough"""
        for item in self.items:
            if item.name == name:
                if item.count >= count:
                    item.count -= count
                    if item.count == 0:
                        self.items.remove(item)
                    return True
                return False
        return False

    def has_item(self, name: str, count: int = 1) -> bool:
        """Check if inventory has at least count of item"""
        for item in self.items:
            if item.name == name and item.count >= count:
                return True
        return False

    def get_by_type(self, item_type: str) -> List[InventoryItem]:
        """Get all items of a specific type"""
        return [item for item in self.items if item.item_type == item_type]

    def display(self) -> None:
        """Display inventory organized by type"""
        if not self.items:
            print("Inventory is empty.")
            return

        # Group by type
        types_order = ["weapon", "armor", "potion", "quest", "misc"]
        type_names = {
            "weapon": "Weapons",
            "armor": "Armor",
            "potion": "Potions",
            "quest": "Quest Items",
            "misc": "Miscellaneous",
        }

        for item_type in types_order:
            items = self.get_by_type(item_type)
            if items:
                print_color(f"\n=== {type_names[item_type]} ===", 255, 200, 100)
                for item in items:
                    count_str = f" x{item.count}" if item.count > 1 else ""
                    print(f"  {item.name}{count_str}")

    def to_dict(self) -> List[dict]:
        """Convert to dict for JSON saving"""
        return [
            {
                "name": item.name,
                "item_type": item.item_type,
                "count": item.count,
                "value": item.value,
            }
            for item in self.items
        ]

    @staticmethod
    def from_dict(data: List[dict]) -> "Inventory":
        """Load from dict (JSON)"""
        inv = Inventory()
        for item_data in data:
            inv.items.append(
                InventoryItem(
                    item_data["name"],
                    item_data["item_type"],
                    item_data["count"],
                    item_data["value"],
                )
            )
        return inv


# endregion


# region Player Classes
FIGHTER = PlayerClass(
    "Fighter",
    "Strong and capable",
    health_mod=1.5,
    damage_mod=1.5,
    gold_mod=1.2,
    mana_mod=0.0,  # No mana
    stamina_mod=1.5,  # High stamina (90)
)

WARLOCK = PlayerClass(
    "Warlock",
    "Dark and mysterious",
    health_mod=0.9,
    damage_mod=1.1,
    gold_mod=1.2,
    mana_mod=1.5,  # High mana (90)
    stamina_mod=0.0,  # No stamina
)

ROGUE = PlayerClass(
    "Rogue",
    "Quick and lonesome",
    health_mod=1.0,
    damage_mod=1.2,
    gold_mod=1.5,
    mana_mod=0.0,  # No mana
    stamina_mod=1.3,  # Good stamina (78)
)

PALADIN = PlayerClass(
    "Paladin",
    "Holy warrior, jack of all trades",
    health_mod=1.2,
    damage_mod=1.3,
    gold_mod=1.0,
    mana_mod=0.8,  # Some mana (48)
    stamina_mod=0.8,  # Some stamina (48)
)

CLERIC = PlayerClass(
    "Cleric",
    "Divine healer and protector",
    health_mod=0.7,
    damage_mod=0.9,
    gold_mod=1.1,
    mana_mod=1.4,  # High mana (84)
    stamina_mod=0.0,  # No stamina
)
# endregion


# region Game Functions
def show_main_menu() -> None:
    set_terminal_title("Venture - Main Menu")
    clear()
    print("==============================")
    print_color("      Welcome to Venture", 255, 200, 50)
    print("==============================")
    print()
    choice = menu_choice(["Start New Game", "Load Game", "Exit"])
    if choice == 1:
        start_new_game()
    elif choice == 2:
        load_game()
    elif choice == 3:
        write_slow("...", 50, 200, 100, 100)
        sys.exit()


def start_new_game() -> None:
    print_color("Starting new game...", 50, 255, 50)
    write_slow("......", 100, 50, 255, 50)
    time.sleep(1)

    state = GameState()
    start_clearing(state)


def load_game() -> None:
    file_name = input(
        "Which save file would you like to load? (CharacterName.json): "
    ).strip()

    try:
        print_color(f"Loading game from {file_name}...", 50, 50, 255)
        write_slow("......", 100, 50, 50, 255)
        time.sleep(1.0)
        clear()

        state = GameState.load(file_name)
        print_color(f"Welcome back, {state.name}!", 50, 50, 255)
        time.sleep(2.0)

        # Route to the correct location based on saved state
        location_router(state)
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        print_color(f"Failed to load save file: {e}", 255, 50, 50)
        time.sleep(3.0)
        show_main_menu()


def location_router(state: GameState) -> None:
    """Routes the player to the correct location based on state.location"""
    location = state.location

    # Check if it's a shop (has shop type in the name)
    if "General Store" in location:
        town = location.split()[0]
        shop(state, location_name=town, shop_type="general")
    elif "Alchemy Shop" in location:
        town = location.split()[0]
        shop(state, location_name=town, shop_type="alchemy")
    elif location == "Wilson's Bar":
        wilsons_bar(state)
    # Direct location lookup
    elif location in LOCATION_MAP:
        LOCATION_MAP[location](state)
    else:
        # Fallback if location is unrecognized
        print_color(
            f"Unknown location: {location}. Returning to Kimaer...", 255, 200, 50
        )
        time.sleep(2)
        kimaer(state)


def start_character_creation(state: GameState) -> None:
    old_name = state.name  # Track old name for file cleanup

    while True:
        clear()
        set_terminal_title("Venture - Character Creation")

        print_color("=== Character Creation ===", 255, 200, 100)
        print()
        print(f"Name: {state.name}")

        color = state.player_color.split()
        if len(color) == 3:
            r, g, b = int(color[0]), int(color[1]), int(color[2])
            print_color(f"Player Color: [{state.player_color}]", r, g, b)

        # Display current class
        if state.player_class:
            print_color(f"Class: {state.player_class.name}", 150, 255, 150)
        else:
            print_color("Class: None", 200, 200, 200)

        print()
        choice = menu_choice(
            [
                "Change Color",
                "Change Name",
                "Change Class",
                "Change Race",
                "Finish Character Creation",
            ]
        )

        if choice == 1:
            # Change Color
            r = random.randint(50, 255)
            g = random.randint(50, 255)
            b = random.randint(50, 255)
            state.player_color = f"{r} {g} {b}"
            print_color(f"Player color changed to [{state.player_color}]", r, g, b)
            time.sleep(1)

        elif choice == 2:
            # Change Name
            new_name = input("Enter new name: ").strip()
            if new_name:
                print_color(
                    f"Name changed from {state.name} to {new_name}", 50, 255, 50
                )
                if not old_name:
                    old_name = state.name
                state.name = new_name
                time.sleep(1)
            else:
                print_color("Name cannot be empty!", 255, 50, 50)
                time.sleep(2)

        elif choice == 3:
            # Change Class
            clear()
            print_color("=== Choose Your Class ===", 255, 200, 100)
            print()
            class_choice = menu_choice(
                [
                    f"Fighter\n   {FIGHTER.description}\n   Health: {int(100 * FIGHTER.health_mod)} | Damage: x{FIGHTER.damage_mod} | Gold: x{FIGHTER.gold_mod}",
                    f"Warlock\n   {WARLOCK.description}\n   Health: {int(100 * WARLOCK.health_mod)} | Damage: x{WARLOCK.damage_mod} | Gold: x{WARLOCK.gold_mod}",
                    f"Rogue\n   {ROGUE.description}\n   Health: {int(100 * ROGUE.health_mod)} | Damage: x{ROGUE.damage_mod} | Gold: x{ROGUE.gold_mod}",
                    f"Paladin\n   {PALADIN.description}\n   Health: {int(100 * PALADIN.health_mod)} | Damage: x{PALADIN.damage_mod} | Gold: x{PALADIN.gold_mod}",
                    f"Cleric\n   {CLERIC.description}\n   Health: {int(100 * CLERIC.health_mod)} | Damage: x{CLERIC.damage_mod} | Gold: x{CLERIC.gold_mod}",
                ]
            )

            if class_choice == 1:
                state.player_class = FIGHTER
            elif class_choice == 2:
                state.player_class = WARLOCK
            elif class_choice == 3:
                state.player_class = ROGUE
            elif class_choice == 4:
                state.player_class = PALADIN
            elif class_choice == 5:
                state.player_class = CLERIC

            # Apply class modifiers
            state.player_class.apply_to_state(state)
            print_color(f"Class set to {state.player_class.name}!", 50, 255, 50)
            time.sleep(1)

        elif choice == 4:
            # Change Race
            print_color("Race not yet implemented, I apologize...", 100, 200, 230)
            time.sleep(2)

        elif choice == 5:
            # Finish Character Creation
            if not state.player_class:
                print_color("You must select a class before finishing!", 255, 50, 50)
                time.sleep(2)
                continue

            print_color("Finalizing character creation...", 50, 255, 50)
            time.sleep(2)
            state.save()

            # Delete the old file if name changed
            if old_name and old_name != state.name:
                old_file_path = Path("saves") / f"{old_name}.json"
                if old_file_path.exists():
                    os.remove(old_file_path)

            break

    clear()
    print()
    print("Character creation complete!")
    time.sleep(2)

    start_gameplay(state)


# endregion


# region Gameplay Functions
def start_clearing(state: GameState) -> None:
    state.location = "Clearing"
    set_terminal_title(f"Venture - {state.location}")
    state.save()
    clear()

    print()
    write_slow(
        "You awake lying in an open field, the sun's rays blinding your eyes...",
        50,
        255,
        160,
        200,
    )
    print()
    time.sleep(2.0)
    write_slow(
        "You have no memory of who you are, what you've done, or how you got here.",
        50,
        255,
        160,
        200,
    )
    print()
    time.sleep(2.0)
    write_slow("Let's change that.", 25, 255, 160, 200)
    time.sleep(1.5)

    start_character_creation(state)


def start_gameplay(state: GameState) -> None:
    step_count = 0
    while True:
        clear()
        print("Where would you like to go?")
        direction = menu_choice(["Go North", "Go South", "Go East", "Go West"])
        if direction == 1:
            print("You head north into the unknown...")
        elif direction == 2:
            print("You head south into the unknown...")
        elif direction == 3:
            print("You head east into the unknown...")
        else:
            print("You head west into the unknown...")
        time.sleep(2)
        step_count += 1
        if step_count % 5 == 0:
            write_slow(
                "You come across a small village. The sign reads 'Kimaer'.",
                50,
                255,
                200,
                50,
            )
            time.sleep(2)
            kimaer(state)
            break


def sleep(state: GameState, location: str = "unknown") -> None:
    """
    Universal sleep function - restores health and advances time.
    Call this whenever the player sleeps anywhere.
    """
    clear()

    # Sleep messages based on location
    sleep_messages = {
        "wilson_bar": [
            "You collapse onto the rough bed upstairs. The noise from below fades as exhaustion takes over.",
            "The mattress is lumpy, but sleep comes quickly after a long shift.",
            "You drift off to the muffled sounds of the tavern below.",
        ],
        "inn": [
            "You sink into the comfortable bed. The inn is quiet and peaceful.",
            "The soft mattress welcomes you as you close your eyes.",
            "Sleep comes easily in the warm, cozy room.",
        ],
        "camp": [
            "You lay your bedroll on the ground. The stars are bright above.",
            "The crackling fire provides warmth as you drift off.",
            "Despite the hard ground, exhaustion pulls you into deep sleep.",
        ],
        "unknown": [
            "You find a place to rest and close your eyes.",
            "Sleep comes, heavy and dreamless.",
            "You drift into unconsciousness.",
        ],
    }

    import random

    message = random.choice(sleep_messages.get(location, sleep_messages["unknown"]))
    write_slow(message, 50, 150, 150, 200)
    print()
    time.sleep(2)

    write_slow("...", 100, 100, 100, 100)
    time.sleep(1)
    clear()

    # Calculate healing - restore to 90% of max health (or current health if higher)
    heal_amount = int(state.max_health * 0.9)
    old_health = state.health
    state.health = max(state.health, heal_amount)
    healed = state.health - old_health

    # Restore mana and stamina to 100%
    state.mana = state.max_mana
    state.stamina = state.max_stamina

    if healed > 0:
        write_slow("You wake feeling refreshed.", 50, 50, 255, 50)
        print_color(f"Health restored: {old_health} → {state.health}", 50, 255, 50)
    else:
        write_slow("You wake feeling rested.", 50, 200, 200, 200)

    if state.max_mana > 0 or state.max_stamina > 0:
        print_color("Energy fully restored!", 100, 200, 255)

    print()

    # Could add other effects here:
    # - Remove status effects (poison, exhaustion, etc.)
    # - Advance time/day counter
    # - Trigger random events
    # - Restore mana if added

    state.save()
    time.sleep(2)


# endregion


# region Inventory
def show_inventory_menu(state: GameState) -> None:
    """Display and interact with inventory"""
    while True:
        clear()
        print_color("=== Inventory ===", 255, 200, 100)
        print()

        if not state.inventory.items:
            print("Your inventory is empty.")
            print()
            press_any_key("Press any key to return...")
            return

        # Sort items by type
        type_order = ["weapon", "armor", "potion", "food", "tool", "quest", "misc"]
        type_names = {
            "weapon": "Weapons",
            "armor": "Armor",
            "potion": "Potions",
            "food": "Food",
            "tool": "Tools",
            "quest": "Quest Items",
            "misc": "Miscellaneous",
        }

        # Build a flat list for selection
        item_list = []
        display_index = 1

        for item_type in type_order:
            items = state.inventory.get_by_type(item_type)
            if items:
                print_color(f"\n{'=' * 40}", 100, 100, 100)
                print_color(f"{type_names[item_type]}", 255, 200, 100)
                print_color(f"{'=' * 40}", 100, 100, 100)

                for item in items:
                    item_data = ITEMS.get(item.name, {})
                    count_str = f" x{item.count}" if item.count > 1 else ""

                    # Check if equipped
                    equipped_str = ""
                    if (
                        hasattr(state, "equipped_weapon")
                        and state.equipped_weapon == item.name
                    ):
                        equipped_str = " [EQUIPPED]"
                    elif (
                        hasattr(state, "equipped_armor")
                        and state.equipped_armor == item.name
                    ):
                        equipped_str = " [EQUIPPED]"

                    print(f"{display_index}. {item.name}{count_str}{equipped_str}")

                    # Show item stats if weapon/armor
                    if item_type == "weapon" and "damage" in item_data:
                        print(f"   Damage: {item_data['damage']}")
                    elif item_type == "armor" and "defense" in item_data:
                        print(f"   Defense: {item_data['defense']}")

                    item_list.append(item)
                    display_index += 1

        print()
        # print_color(f"{display_index}.", 200, 200, 200)
        print()

        # Get choice
        choice = menu_choice(
            [item.name for item in item_list] + ["Map"] + ["Exit"],
        )

        if choice == len(item_list) + 1:
            clear()
            show_map(state)
            return
        elif choice == len(item_list) + 2:  # Exit
            clear()
            location_router(state)
            return

        # Handle item interaction
        selected_item = item_list[choice - 1]
        interact_with_item(state, selected_item)


def interact_with_item(state: GameState, item: InventoryItem) -> None:
    """Handle using/equipping an item"""
    clear()
    item_data = ITEMS.get(item.name, {})

    print_color(f"=== {item.name} ===", 255, 200, 100)
    print()
    print(f"Description: {item_data.get('description', 'No description')}")
    print(f"Type: {item.item_type.title()}")
    print(f"Value: {item.value} gold")

    if item.count > 1:
        print(f"Quantity: {item.count}")

    print()

    # Build options based on item type
    options = []

    if item.item_type == "potion" or item.item_type == "food":
        options.append("Consume")
    elif item.item_type == "weapon":
        if hasattr(state, "equipped_weapon") and state.equipped_weapon == item.name:
            options.append("Unequip")
        else:
            options.append("Equip")
    elif item.item_type == "armor":
        if hasattr(state, "equipped_armor") and state.equipped_armor == item.name:
            options.append("Unequip")
        else:
            options.append("Equip")

    options.append("Back")

    choice = menu_choice(options)

    if options[choice - 1] == "Consume":
        consume_item(state, item)
    elif options[choice - 1] == "Equip":
        equip_item(state, item)
    elif options[choice - 1] == "Unequip":
        unequip_item(state, item)
    # "Back" just returns


def consume_item(state: GameState, item: InventoryItem) -> None:
    """Use a consumable item"""
    item_data = ITEMS.get(item.name, {})
    effect = item_data.get("effect", {})

    # Apply effects
    if "health" in effect:
        old_health = state.health
        state.health = min(state.max_health, state.health + effect["health"])
        healed = state.health - old_health
        print_color(f"Restored {healed} health!", 50, 255, 50)

    if "mana" in effect:
        old_mana = state.mana
        state.mana = min(state.max_mana, state.mana + effect["mana"])
        rejuved = state.mana - old_mana
        print_color(f"Restored {rejuved} mana!", 50, 255, 50)

    # Remove from inventory
    state.inventory.remove_item(item.name, 1)

    time.sleep(2)


def equip_item(state: GameState, item: InventoryItem) -> None:
    """Equip a weapon or armor"""
    if item.item_type == "weapon":
        if not hasattr(state, "equipped_weapon"):
            state.equipped_weapon = None

        if state.equipped_weapon:
            print_color(f"Unequipped {state.equipped_weapon}", 200, 200, 200)

        state.equipped_weapon = item.name
        print_color(f"Equipped {item.name}!", 50, 255, 50)

    elif item.item_type == "armor":
        if not hasattr(state, "equipped_armor"):
            state.equipped_armor = None

        if state.equipped_armor:
            print_color(f"Unequipped {state.equipped_armor}", 200, 200, 200)

        state.equipped_armor = item.name
        print_color(f"Equipped {item.name}!", 50, 255, 50)

    state.save()
    time.sleep(1)


def unequip_item(state: GameState, item: InventoryItem) -> None:
    """Unequip a weapon or armor"""
    if item.item_type == "weapon":
        state.equipped_weapon = None
        print_color(f"Unequipped {item.name}", 200, 200, 200)
    elif item.item_type == "armor":
        state.equipped_armor = None
        print_color(f"Unequipped {item.name}", 200, 200, 200)

    state.save()
    time.sleep(1)


# endregion


# region Events


def trigger_rat_quest(state):
    """Called after first sleep - triggers rat quest"""
    from dialogue.kimaer.celeste import celeste_rat_quest_panic

    clear()
    print()
    write_slow(
        "As you wake, you hear a distant scream piercing the morning air.",
        50,
        255,
        160,
        200,
    )
    print()
    time.sleep(2)
    write_slow("It came from the village square.", 50, 255, 160, 200)
    print()
    press_any_key()

    # Set flag so this doesn't repeat
    state.rat_quest_triggered = True
    state.save()

    # Route to special Kimaer event
    kimaer_rat_event(state)


def kimaer_rat_event(state):
    """Special version of Kimaer for rat quest start"""
    from dialogue.kimaer.celeste import celeste_rat_quest_panic

    state.location = "Kimaer"
    clear()
    print()

    write_slow(
        "You rush to the village square. A small crowd has gathered near the alchemy shop.",
        50,
        200,
        250,
        0,
    )
    print()
    press_any_key()
    clear()

    celeste_rat_quest_panic(state)

    # After quest dialogue, return to normal Kimaer
    kimaer(state)


def alchemy_shop_rat_combat(state):
    """Combat encounter in the alchemy shop"""
    from core.combat import combat, Enemy
    from quests.quests import is_quest_active, get_active_quest
    from dialogue.kimaer.celeste import celeste_quest_complete

    # Check if quest is at the right stage
    quest = get_active_quest(state, "celeste_rats")
    if not quest or quest.current_stage != 2:  # Stage 2 = defeat rats
        # Normal shop behavior
        shop(state, "Kimaer", "alchemy")
        return

    clear()
    write_slow(
        "You push open the door to the alchemy shop. Glass crunches underfoot.",
        50,
    )
    print()
    time.sleep(2)
    write_slow(
        "Three massive rats turn to face you, their eyes gleaming red in the dim light.",
        50,
        255,
        100,
        100,
    )
    print()
    press_any_key()

    # Combat!
    enemies = [
        Enemy("Giant Rat"),
        Enemy("Giant Rat"),
        Enemy("Giant Rat"),
    ]

    won = combat(state, enemies)

    if won:
        celeste_quest_complete(state)
        # After quest complete, go to normal shop
        shop(state, "Kimaer", "alchemy")
    else:
        # Player fled or died - return to Kimaer
        kimaer(state)


# endregion

# region Main Execution
set_terminal_title("Venture")

# This constant is down here because format, trust me.
LOCATION_MAP = {
    "Start": start_clearing,
    "Clearing": start_gameplay,
    "Kimaer": kimaer,
}


def boot_intro() -> None:
    clear()
    time.sleep(2)
    write_slow("Auxiliary Games Presents...", 100, 255, 50, 0)
    time.sleep(1)
    clear()
    print()
    write_slow("                 Venture", 150, 255, 200, 50)
    time.sleep(1)
    show_main_menu()


if __name__ == "__main__":
    boot_intro()
# endregion
