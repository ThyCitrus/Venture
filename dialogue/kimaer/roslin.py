from core.display import write_slow, press_any_key, print_color
from core.utils import get_player_color, menu_choice
import time

from core.constants import KIMAER_ROSLIN
from data.journal import unlock_journal_entry

R, G, B = 200, 250, 150


def roslin_first_meeting(state):
    r, g, b = get_player_color(state)

    # Initialize tracking for this NPC if not exists
    if "roslin" not in state.npc_topics_asked:
        state.npc_topics_asked["roslin"] = {
            "introduced": False,
            "store": False,
            "town": False,
        }

    topics = state.npc_topics_asked["roslin"]

    # INTRO - only plays once
    write_slow(
        " A soft chime greets you as you step inside. Incense drifts lazily through the air: sandalwood, sage, a hint of rain-soaked bark.",
        50,
        255,
        255,
        255,
    )
    write_slow(
        "\n Behind the counter stands a wood elf with a crown of antlers and a grin that feels equal parts mischief and welcome.",
        50,
        255,
        255,
        255,
    )
    time.sleep(1)
    write_slow(
        "\n\n Well, look at you. Not a face I've seen before, and I tend to remember faces. Mmh... a traveler, perhaps?",
        50,
        R,
        G,
        B,
    )
    print()

    # CONVERSATION LOOP
    while True:
        options = []
        option_map = {}
        idx = 1

        # Build dynamic menu based on what's been asked
        if not topics["introduced"]:
            options.append("Introduce yourself")
            option_map[idx] = "introduce"
            idx += 1

        if not topics["store"]:
            options.append("Ask about the store")
            option_map[idx] = "store"
            idx += 1

        if not topics["town"]:
            options.append("Ask about Kimaer")
            option_map[idx] = "town"
            idx += 1

        options.append("Say nothing and browse")
        option_map[idx] = "leave"

        choice = menu_choice(options)
        action = option_map[choice]

        if action == "introduce":
            write_slow(
                f" My name is {state.name}. Just passing through.",
                50,
                r,
                g,
                b,
            )
            time.sleep(1)
            print()
            write_slow(
                " Mmh, 'passing through.' They all say that. Still...", 50, R, G, B
            )
            write_slow(
                " Welcome to Kimaer, love. If you find yourself staying longer, I might even remember what you like to buy.",
                50,
                R,
                G,
                B,
            )
            write_slow(
                f"\n I'm Roslin, and I'll remember you, {state.name}.", 50, R, G, B
            )
            print()
            topics["introduced"] = True
            unlock_journal_entry(state, "roslin")

        elif action == "store":
            write_slow(f" What do you sell here?", 50, r, g, b)
            time.sleep(1)
            print()
            write_slow(
                " Oh, a bit of everything that matters: bread for the belly, rope for the journey, charms for luck if you're the believing sort.",
                50,
                R,
                G,
                B,
            )
            if not topics["introduced"]:
                time.sleep(1)
                write_slow(
                    "\n My name is Roslin, sweetheart. And you are...?", 50, R, G, B
                )
            print()
            topics["store"] = True
            unlock_journal_entry(state, "roslin_store")

        elif action == "town":
            write_slow(f" What's this town like?", 50, r, g, b)
            time.sleep(1)
            print()
            write_slow(
                " Peaceful enough, most days. The trees hum when the wind's right.",
                50,
                R,
                G,
                B,
            )
            write_slow(
                "\n You'll find honest folk here, and a few less so. Depends how deep you wander.",
                50,
                R,
                G,
                B,
            )
            time.sleep(1)
            write_slow(
                "\n But don't worry, I'll keep an eye on you. Someone has to.",
                50,
                R,
                G,
                B,
            )
            print()
            topics["town"] = True
            unlock_journal_entry(state, "roslin_town")

        elif action == "leave":
            write_slow(f" ...", 50, r, g, b)
            time.sleep(2)
            print()
            write_slow(
                " Not much of a talker, hm? That's all right. The quiet ones usually listen best.",
                50,
                R,
                G,
                B,
            )
            if not topics["introduced"]:
                time.sleep(1)
                write_slow(
                    "\n Still, you'll have to speak up eventually if you want to buy something.",
                    50,
                    R,
                    G,
                    B,
                )
            print()
            break

        # Check if all topics exhausted
        if all(topics.values()):
            time.sleep(1)
            write_slow(
                "\n Roslin smiles warmly. 'Well then, shall we talk business?'",
                50,
                R,
                G,
                B,
            )
            print()
            break

    press_any_key()


def roslin_additional_questions(state):
    """Handle remaining questions if player left early"""
    r, g, b = get_player_color(state)
    topics = state.npc_topics_asked["roslin"]

    write_slow(
        " Roslin looks up from organizing shelves. 'Something else on your mind, love?'",
        50,
        R,
        G,
        B,
    )
    print()

    while True:
        options = []
        option_map = {}
        idx = 1

        if not topics["store"]:
            options.append("Ask about the store")
            option_map[idx] = "store"
            idx += 1

        if not topics["town"]:
            options.append("Ask about Kimaer")
            option_map[idx] = "town"
            idx += 1

        options.append("Nothing, just browsing")
        option_map[idx] = "leave"

        # If all topics done, exit
        if topics["store"] and topics["town"]:
            break

        choice = menu_choice(options)
        action = option_map[choice]

        if action == "store":
            write_slow(f" What do you sell here?", 50, r, g, b)
            time.sleep(1)
            print()
            write_slow(
                " Oh, a bit of everything that matters: bread for the belly, rope for the journey, charms for luck if you're the believing sort.",
                50,
                R,
                G,
                B,
            )
            print()
            topics["store"] = True

        elif action == "town":
            write_slow(f" What's this town like?", 50, r, g, b)
            time.sleep(1)
            print()
            write_slow(
                " Peaceful enough, most days. The trees hum when the wind's right.",
                50,
                R,
                G,
                B,
            )
            write_slow(
                "\n You'll find honest folk here, and a few less so. Depends how deep you wander.",
                50,
                R,
                G,
                B,
            )
            print()
            topics["town"] = True

        elif action == "leave":
            write_slow(" Understood. Let me know if you need anything.", 50, R, G, B)
            print()
            break

    press_any_key()


def roslin_repeat_greeting(state):
    """Called when player talks to Roslin after first meeting - normal greetings only"""
    r, g, b = get_player_color(state)

    topics = state.npc_topics_asked.get("roslin", {})
    has_unasked = not all(topics.values())

    if has_unasked:
        roslin_additional_questions(state)
    else:
        greetings = [
            f" Ah, {state.name}. Back again already? I'm flattered.",
            f" Welcome back, love. Need something, or just here for the ambience?",
            f" Mmh. {state.name}. You're becoming a regular.",
        ]
        import random

        greeting = random.choice(greetings)
        write_slow(greeting, 50, R, G, B)
        print()
        press_any_key()


def roslin_gives_broomstick(state):
    """Roslin gives player the starting weapon"""
    from quests.quests import advance_quest, is_quest_active

    if not is_quest_active(state, "celeste_rats"):
        return

    r, g, b = get_player_color(state)

    write_slow(
        " Ah, Celeste sent you? Rats, she said?",
        50,
        R,
        G,
        B,
    )
    time.sleep(1)
    write_slow(
        "\n Roslin reaches behind the counter and pulls out an old broomstick.",
        50,
        255,
        255,
        255,
    )
    print()
    time.sleep(1)
    write_slow(
        "\n Here. It's not much, but it's sturdy. On the house, hero.",
        50,
        R,
        G,
        B,
    )
    print()

    state.inventory.add_item("Broken Broomstick", 1)
    print_color("Received: Broken Broomstick", 50, 255, 50)

    # Advance quest
    advance_quest(state, "celeste_rats")  # Stage 2: Defeat rats
    print_color("Quest Updated: Return to the Alchemy Shop", 255, 200, 50)
    print()
    press_any_key()
