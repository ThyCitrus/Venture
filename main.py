"""
venture.py - A simple text-based adventure game.
"""

# region Imports
import json
import time
import sys
from core.classes import *
from dialogue.kimaer.wilson import *
from dialogue.kimaer.benji import *
from dialogue.kimaer.celeste import *
from dialogue.kimaer.roslin import *
from dialogue.kimaer.silas import *
from core.display import set_terminal_title
from core.utils import location_router
from core.state import GameState

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
    from core.locations import start_clearing

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


# endregion


# endregion


# region Main Execution
set_terminal_title("Venture")

# This constant is down here because format, trust me.


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
