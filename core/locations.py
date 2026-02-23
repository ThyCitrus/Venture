"""
core/locations.py - All location functions and shop logic.
"""

import time

from core.utils import (
    clear,
    press_any_key,
    print_color,
    write_slow,
    show_hud,
    set_terminal_title,
    menu_choice,
)
from core.constants import KIMAER_ROSLIN, KIMAER_CELESTE, KIMAER_WILSON
from data.items import ITEMS
from quests.quests import is_quest_active
from quests.hooks import get_location_hook
from dialogue.kimaer.wilson import wilson_interaction
from dialogue.kimaer.benji import benji_interaction
from dialogue.kimaer.celeste import celeste_first_meeting, celeste_repeat_greeting
from dialogue.kimaer.roslin import (
    roslin_first_meeting,
    roslin_repeat_greeting,
    roslin_gives_broomstick,
)
from dialogue.kimaer.silas import silas_interaction


# ---------------------------------------------------------------------------
# Shop config
# ---------------------------------------------------------------------------

SHOP_DATA = {
    "general": {
        "word": "Store",
        "base_items": {"Parchment": 12, "Bread": 5, "Rope": 8},
        "location_items": {
            "Kimaer": {"Fishing Rod": 25, "Basic Lure": 1},
            "Lunara": {"Moon Charm": 30},
        },
        "npcs": {
            "Kimaer": {
                "name": "roslin",
                "func": roslin_first_meeting,
                "repeat_func": roslin_repeat_greeting,
                "quest_options": [
                    {
                        "label": "Celeste needs help",
                        "condition": lambda state: (
                            is_quest_active(state, "celeste_rats")
                            and not state.inventory.has_item("Broken Broomstick")
                        ),
                        "func": roslin_gives_broomstick,
                    }
                ],
            },
        },
    },
    "alchemy": {
        "word": "Shop",
        "base_items": {"Health Potion": 15, "Mana Potion": 18, "Antidote": 12},
        "location_items": {
            "Kimaer": {"River Water": 2},
        },
        "npcs": {
            "Kimaer": {
                "name": "celeste",
                "func": celeste_first_meeting,
                "repeat_func": celeste_repeat_greeting,
                "quest_options": [],
            },
        },
    },
}


# ---------------------------------------------------------------------------
# NPC speak helper
# ---------------------------------------------------------------------------


def _speak_with_npc(state, npc_info, npc_display, location_name, shop_type):
    quest_options = npc_info.get("quest_options", [])

    active_options = [
        opt
        for opt in quest_options
        if not opt.get("condition") or opt["condition"](state)
    ]

    repeat_func = npc_info.get("repeat_func")
    if repeat_func:
        repeat_func(state)
    else:
        print_color(f"{npc_display} greets you warmly.", 150, 200, 255)
        press_any_key()

    if not active_options:
        return

    labels = [opt["label"] for opt in active_options] + ["Never mind"]
    print()
    choice = menu_choice(labels)
    if choice == len(labels):
        return

    func = active_options[choice - 1].get("func")
    if func:
        func(state)


# ---------------------------------------------------------------------------
# Generic shop
# ---------------------------------------------------------------------------


def shop(state, location_name: str, shop_type: str) -> None:
    from main import show_inventory_menu

    shop_info = SHOP_DATA.get(shop_type, {})
    shop_word = shop_info.get("word", "Shop")

    state.location = f"{location_name} {shop_type.title()} {shop_word}"
    set_terminal_title(f"Venture - {state.location}")
    state.save()
    clear()

    print_color(
        f"=== {location_name}'s {shop_type.title()} {shop_word} ===", 255, 200, 50
    )
    print()

    items = shop_info.get("base_items", {}).copy()
    items.update(shop_info.get("location_items", {}).get(location_name, {}))

    npc_info = shop_info.get("npcs", {}).get(location_name, {})
    npc_name = npc_info.get("name", "shopkeeper")
    npc_key = f"{location_name.lower()}_{npc_name}"

    if npc_key not in state.npc_met:
        dialogue_func = npc_info.get("func")
        if dialogue_func:
            dialogue_func(state)
            state.npc_met[npc_key] = npc_info.get("name", "Shopkeeper").title()
            state.save()
            clear()
            print_color(
                f"=== {location_name}'s {shop_type.title()} {shop_word} ===",
                255,
                200,
                50,
            )
            print()

    show_hud(state)
    npc_display = state.npc_met.get(npc_key, "the Shopkeeper")

    choice = menu_choice(
        ["Buy Items", "Sell Items", "Inventory", f"Speak with {npc_display}", "Leave"],
        state,
    )

    if choice == 1:
        buy_items(state, items)
        shop(state, location_name, shop_type)
    elif choice == 2:
        sell_items(state, shop_type)
        shop(state, location_name, shop_type)
    elif choice == 3:
        show_inventory_menu(state)
        shop(state, location_name, shop_type)
    elif choice == 4:
        _speak_with_npc(state, npc_info, npc_display, location_name, shop_type)
        shop(state, location_name, shop_type)
    elif choice == 5:
        write_slow(
            f"You leave the {shop_word.lower()} and return to {location_name}...",
            50,
            200,
            250,
            0,
        )
        time.sleep(1)
        if location_name == "Kimaer":
            kimaer(state)


def buy_items(state, shop_items: dict) -> None:
    clear()
    print_color("=== Buy Items ===", 255, 200, 50)
    print()

    if not shop_items:
        print("This shop has no items for sale.")
        press_any_key()
        return

    item_list = list(shop_items.items())
    for i, (name, price) in enumerate(item_list, 1):
        print(f"{i}. {name} - {price} gold")
    print(f"{len(item_list) + 1}. Cancel")
    print()
    show_hud(state)

    choice = menu_choice([n for n, _ in item_list] + ["Cancel"])
    if choice == len(item_list) + 1:
        return

    item_name, price = item_list[choice - 1]
    print(f"How many {item_name}s would you like to buy?")
    try:
        quantity = int(input("> ").strip())
        if quantity < 1:
            print_color("Invalid quantity!", 255, 50, 50)
            time.sleep(1)
            return
    except ValueError:
        print_color("Invalid input!", 255, 50, 50)
        time.sleep(1)
        return

    total_cost = price * quantity
    if state.gold >= total_cost:
        state.gold -= total_cost
        state.inventory.add_item(item_name, count=quantity)
        print_color(
            f"Purchased {quantity}x {item_name} for {total_cost} gold!", 50, 255, 50
        )
        time.sleep(1)
    else:
        print_color(
            f"Not enough gold! You need {total_cost} but only have {state.gold}.",
            255,
            50,
            50,
        )
        time.sleep(2)


def sell_items(state, shop_type: str) -> None:
    clear()
    print_color("=== Sell Items ===", 255, 200, 50)
    print()

    sellable = [
        item
        for item in state.inventory.items
        if ITEMS.get(item.name) and shop_type in ITEMS[item.name].get("sellable_to", [])
    ]

    if not sellable:
        print("You have nothing this shop will buy.")
        press_any_key()
        return

    for i, item in enumerate(sellable, 1):
        sell_price = ITEMS[item.name]["value"] // 2
        count_str = f" x{item.count}" if item.count > 1 else ""
        print(f"{i}. {item.name}{count_str} - {sell_price} gold each")
    print(f"{len(sellable) + 1}. Cancel")
    print()
    show_hud(state)

    choice = menu_choice([item.name for item in sellable] + ["Cancel"])
    if choice == len(sellable) + 1:
        return

    item = sellable[choice - 1]
    sell_price = ITEMS[item.name]["value"] // 2

    if item.count > 1:
        print(f"How many? (1-{item.count})")
        try:
            amount = int(input("> ").strip())
            if amount < 1 or amount > item.count:
                print_color("Invalid amount!", 255, 50, 50)
                time.sleep(1)
                return
        except ValueError:
            print_color("Invalid amount!", 255, 50, 50)
            time.sleep(1)
            return
    else:
        amount = 1

    state.inventory.remove_item(item.name, amount)
    state.gold += sell_price * amount
    print_color(
        f"Sold {amount}x {item.name} for {sell_price * amount} gold!", 50, 255, 50
    )
    time.sleep(1)


# ---------------------------------------------------------------------------
# Kimaer
# ---------------------------------------------------------------------------


def kimaer(state) -> None:
    state.location = "Kimaer"
    set_terminal_title(f"Venture - {state.location}")
    state.save()
    clear()

    print()
    if "Kimaer" not in state.locations_visited:
        write_slow(
            "The village is quite modest, only a few small houses and a couple businesses around one main square.\n"
            "You can see a general store, an alchemy shop, and a tavern.",
            50,
            200,
            250,
            0,
        )
        write_slow(
            "\nYou also see a beggar and a shady-looking figure in an alleyway.",
            50,
            200,
            250,
            0,
        )
        press_any_key()
        state.locations_visited["Kimaer"] = True
        state.save()
        clear()

    show_hud(state)
    print_color("You're in the village of Kimaer.", 200, 250, 0)

    choice = menu_choice(
        [
            "Enter the General Store",
            "Enter the Alchemy Shop",
            "Enter the Tavern",
            "Talk to the beggar",
            "Approach the shady figure",
        ],
        state,
    )

    if choice == 1:
        hook = get_location_hook(state, "kimaer_general")
        if hook:
            hook(state)
        else:
            write_slow("You enter the general store...", 50, 200, 250, 150)
            shop(state, "Kimaer", "general")

    elif choice == 2:
        from quests.quests import get_active_quest

        quest = get_active_quest(state, "celeste_rats")
        if quest and quest.current_stage == (1, 2):
            if not state.equipped_weapon:
                clear()
                print()
                write_slow(
                    "You grip the door handle, then hesitate.", 50, 255, 255, 255
                )
                time.sleep(1)
                write_slow(
                    "Going in there unarmed would be suicide. You should equip the broomstick first.",
                    50,
                    255,
                    200,
                    50,
                )
                print()
                press_any_key()
                kimaer(state)
                return
        hook = get_location_hook(state, "kimaer_alchemy")
        if hook:
            hook(state)
        else:
            write_slow("You enter the alchemy shop...", 50, 200, 20, 140)
            shop(state, "Kimaer", "alchemy")

    elif choice == 3:
        wilsons_bar(state)
    elif choice == 4:
        benji_interaction(state)
        kimaer(state)
    elif choice == 5:
        silas_interaction(state)
        kimaer(state)


def wilsons_bar(state) -> None:
    if KIMAER_ROSLIN not in state.npc_met or KIMAER_CELESTE not in state.npc_met:
        clear()
        print()
        write_slow(
            "You approach the tavern. A wooden sign hangs on the door:",
            50,
            235,
            200,
            75,
        )
        print()
        time.sleep(1)
        write_slow("'Closed. Come back later.'", 50, 235, 200, 75)
        print()
        time.sleep(1)
        print_color("[You should explore other areas of Kimaer first]", 150, 150, 150)
        print()
        press_any_key()
        kimaer(state)
        return

    state.location = "Wilson's Bar"
    set_terminal_title(f"Venture - {state.location}")
    state.save()
    clear()

    print()
    if "wilson_bar" not in state.locations_visited:
        write_slow(
            "As you enter the tavern, you are immediately struck by the heavy scent of alcohol "
            "and the talking of a surprisingly small number of patrons.",
            50,
            235,
            200,
            75,
        )
        print()
        time.sleep(1)
        write_slow(
            "Within the tavern, you see a staircase, a man behind the bar, and lots of mining equipment.",
            50,
            235,
            200,
            75,
        )
        press_any_key()
        state.locations_visited["wilson_bar"] = True
        state.save()
        clear()

    show_hud(state)
    print_color("You're in Wilson's Bar.", 235, 200, 75)

    choice = menu_choice(["Approach the barkeep", "Exit"], state)
    if choice == 1:
        wilson_interaction(state)
        wilsons_bar(state)
    elif choice == 2:
        write_slow("You leave the tavern...", 50, 200, 250, 0)
        kimaer(state)
