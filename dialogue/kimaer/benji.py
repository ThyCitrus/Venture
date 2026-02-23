import random
import time
from core.utils import *
from core.constants import KIMAER_BENJI
from main import unlock_journal_entry
from quests.quests import start_quest, advance_quest, is_quest_active

R, G, B = 255, 100, 75

BENJI_QUOTES = [
    "Don't eat yellow snow.",
    "To win a war, you must be more cunning.",
    "The secret to immortality is not dying.",
    "Remember to drink water.",
    "I'm watching you. Not in a creepy way.",
    "Shhh... I hear the devs talking.",
    "The cake is a lie.",
    "Always carry a towel.",
    "You've been gnomed.",
    "Look behind you! Oh, nevermind, it's just fog.",
    "Is this real life? Is this just fantasy?",
    "Run, Forrest, run!",
    "It's dangerous to go alone.",
    "I'm trying my best!",
    "The only true wisdom is knowing that you know nothing.",
    "You look nice today.",
    "A wizard is never late.",
]


def benji_first_meeting(state):
    r, g, b = get_player_color(state)

    write_slow(
        " A squat little gnome sits against a fountain, humming off-key. His eyes flick between you and the sky as if he's not sure which one's real.",
        50,
        255,
        255,
        255,
    )
    time.sleep(1)
    write_slow(
        "\n Oh! A visitor! Or maybe a hallucination. Either way hello!",
        50,
        R,
        G,
        B,
    )
    print()

    time.sleep(1)
    quote = random.choice(BENJI_QUOTES)
    write_slow(f" {quote}", 50, R, G, B)
    print()

    write_slow(
        " He grins at you with all the serenity of a man who lost his mind and liked it that way.",
        50,
        255,
        255,
        255,
    )
    print()
    press_any_key()


def benji_repeat_meeting(state):
    """Called for subsequent interactions"""
    r, g, b = get_player_color(state)

    quote = random.choice(BENJI_QUOTES)
    write_slow(f" {quote}", 50, R, G, B)
    print()
    unlock_journal_entry(state, "benji")
    press_any_key()


def benji_interaction(state):
    if KIMAER_BENJI not in state.npc_met:
        benji_first_meeting(state)
        state.npc_met[KIMAER_BENJI] = "benji"
        state.save()
    else:
        benji_repeat_meeting(state)
