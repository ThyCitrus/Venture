import random
import time
from core.display import clear, write_slow, press_any_key
from core.utils import get_player_color
from core.constants import KIMAER_BENJI
from data.journal import unlock_journal_entry
from quests.quests import start_quest, advance_quest, is_quest_active

R, G, B = 255, 100, 75

BENJI_QUOTES = [
    "Mark well thy footing, and never sup from yellowed snow.",
    "To triumph in war, one must weave cunning like thread through steel.",
    "The secret to immortality? Why... simply refuse to perish.",
    "Keep thy waters close, for thirst is death's sly herald.",
    "I've seen you, traveler. Nay, not like that, more like a thought that knows your name.",
    "Hush now… the makers whisper beyond the veil of code.",
    "They promised cake, yet all I found was deceit and crumbs.",
    "A towel, ah yes, armor against chaos and spilled stew alike.",
    "You've been… gnomed? Oh! It tickles my third eye just to say it.",
    "Behind thee! No, no, only the fog wears such faces.",
    "Is this the waking world or some dream caught in its own throat?",
    "Run, dear Forrest! The trees themselves wish to race thee.",
    "'Tis perilous to walk alone; take something sharp... or someone kind.",
    "My best effort, yes! Though best is a slippery creature, isn't it?",
    "True wisdom hides in ignorance, knowing naught, and knowing it well.",
    "You look… radiant today. Like a candle that hasn't yet realized it's burning.",
    "A wizard is never tardy, no, time itself just waits for him to arrive.",
    "The drowned one fell in love, poor kelpy fool. Thought beauty could keep its shape under pressure. Ha! It cannot.",
    "If you find a cave that seems deeper than it should be, leave it be. That's no cave.",
    "The spire inverted, the thing that breathes smoke and remembers pain. I went there once. Came back with my hair humming.",
    "He carved her name into the tide, see? But names don't float. They sink.",
    "The fire beneath the world dreams of daylight. Best not to wake it.",
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
    unlock_journal_entry(state, "benji")
    press_any_key()


def benji_repeat_meeting(state):
    """Called for subsequent interactions"""
    r, g, b = get_player_color(state)

    quote = random.choice(BENJI_QUOTES)
    write_slow(f" {quote}", 50, R, G, B)
    print()
    press_any_key()


def benji_interaction(state):
    if KIMAER_BENJI not in state.npc_met:
        benji_first_meeting(state)
        state.npc_met[KIMAER_BENJI] = "benji"
        state.save()
    else:
        benji_repeat_meeting(state)
