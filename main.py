"""
venture.py - A simple text-based adventure game.
"""

# region Imports
import json
from pathlib import Path
import time
import sys
import os
import random
from core.locations import kimaer
from core.classes import *
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
