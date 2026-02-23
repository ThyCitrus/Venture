from core.utils import (
    write_slow,
    menu_choice,
    press_any_key,
    get_player_color,
)
import time
from core.constants import KIMAER_SILAS
from data.journal import unlock_journal_entry

R, G, B = 100, 30, 40


def silas_first_encounter(state):
    """Silas' cold initial rejection - FIRST MEETING"""
    r, g, b = get_player_color(state)

    write_slow(
        " A tall Drow leans against the alley wall, scarlet eyes glinting under his hood. Scars crisscross his knuckles.",
        50,
        255,
        255,
        255,
    )
    time.sleep(1)
    write_slow(
        "\n\n He stares through you like you're not worth the effort.",
        50,
        255,
        255,
        255,
    )
    print()

    # Single hostile exchange, no real conversation
    write_slow(f" What's your name?", 50, r, g, b)
    time.sleep(1)
    print()
    write_slow(
        " ...",
        50,
        R,
        G,
        B,
    )
    time.sleep(2)
    print()

    write_slow(f" What's down this alley?", 50, r, g, b)
    time.sleep(1)
    print()
    write_slow(
        " Get lost.",
        50,
        R,
        G,
        B,
    )
    print()
    press_any_key()


def silas_repeat_encounter(state):
    """Silas gets more hostile on repeat approaches"""
    r, g, b = get_player_color(state)

    hostile_lines = [
        " Are you deaf? I said get lost!",
        " Walk away. Now.",
        " Persistent. Annoying. Leave.",
        " One more word and you limp.",
    ]
    import random

    write_slow(
        " The Drow's eyes narrow. He straightens slightly.",
        50,
        255,
        255,
        255,
    )
    print()
    time.sleep(1)
    write_slow(
        random.choice(hostile_lines),
        50,
        R,
        G,
        B,
    )
    print()
    unlock_journal_entry(state, "silas")
    press_any_key()


def silas_interaction(state):
    """Main interaction dispatcher"""
    if "silas" not in state.npc_met:
        silas_first_encounter(state)
        state.npc_met["silas"] = True
        state.save()
    else:
        silas_repeat_encounter(state)
