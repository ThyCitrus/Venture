# region Inventory

import time
from typing import List
from data.items import ITEMS
from data.map import show_map
from core.utils import (
    location_router,
    print_color,
    clear,
    press_any_key,
    menu_choice,
    show_journal,
)
from core.state import GameState


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
            [item.name for item in item_list] + ["Map"] + ["Journal"] + ["Exit"],
        )

        if choice == len(item_list) + 1:
            clear()
            show_map(state)
            return
        elif choice == len(item_list) + 2:
            clear()
            show_journal(state)
            return
        elif choice == len(item_list) + 3:
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
