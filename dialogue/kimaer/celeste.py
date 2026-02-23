from core.utils import (
    clear,
    write_slow,
    menu_choice,
    press_any_key,
    print_color,
    display_dialogue,
    get_player_color,
)
import time
from core.constants import KIMAER_CELESTE

R, G, B = 200, 20, 140


def celeste_first_meeting(state):
    r, g, b = get_player_color(state)

    # Initialize tracking for this NPC if not exists
    if "celeste" not in state.npc_topics_asked:
        state.npc_topics_asked["celeste"] = {
            "introduced": False,
            "store": False,
            "town": False,
        }

    topics = state.npc_topics_asked["celeste"]

    # INTRO - only plays once
    write_slow(
        " A faint bell rings as you enter. The air is sharp with the scent of chemicals, lavender, and something metallic beneath.",
        50,
        255,
        255,
        255,
    )
    write_slow(
        "\n A dhampir with pale skin and dark hair stands behind a spotless counter. Her eyes lift from a flask only long enough to judge your presence.",
        50,
        255,
        255,
        255,
    )
    time.sleep(1)
    write_slow(
        "\n\n If you are here to browse, do so carefully. Most of what I keep is fragile... or volatile.",
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

        # Build dynamic menu
        if not topics["introduced"]:
            options.append("Introduce yourself")
            option_map[idx] = "introduce"
            idx += 1

        if not topics["store"]:
            options.append("Ask about the shop")
            option_map[idx] = "store"
            idx += 1

        if not topics["town"]:
            options.append("Ask about the town")
            option_map[idx] = "town"
            idx += 1

        options.append("Say nothing and look around")
        option_map[idx] = "leave"

        choice = menu_choice(options)
        action = option_map[choice]

        if action == "introduce":
            write_slow(f" I'm {state.name}. Just exploring.", 50, r, g, b)
            time.sleep(1)
            print()
            write_slow(" Hm. Another traveler. Bon... I see.", 50, R, G, B)
            write_slow(
                " Welcome to Kimaer, then. I am Celeste, alchemist and librarian of sorts.",
                50,
                R,
                G,
                B,
            )
            write_slow(
                f"\n If you need potions or reagents, I can provide.... within reason.",
                50,
                R,
                G,
                B,
            )
            print()
            topics["introduced"] = True

        elif action == "store":
            write_slow(f" What is it you sell here?", 50, r, g, b)
            time.sleep(1)
            print()
            write_slow(
                " Tonics, herbs, distillates, and certain compounds that should not be sold but are, regardless.",
                50,
                R,
                G,
                B,
            )
            write_slow(
                " Alchemy is not trade, it is transformation. But coin still keeps the fire lit, so I sell.",
                50,
                R,
                G,
                B,
            )
            if not topics["introduced"]:
                time.sleep(1)
                write_slow(
                    "\n I am Celeste. Try not to touch the glassware, s'il vous plaît.",
                    50,
                    R,
                    G,
                    B,
                )
            print()
            topics["store"] = True

        elif action == "town":
            write_slow(f" What can you tell me about Kimaer?", 50, r, g, b)
            time.sleep(1)
            print()
            write_slow(
                " Small. Predictable. The seasons change faster than the people do.",
                50,
                R,
                G,
                B,
            )
            write_slow(
                " It is... comforting, in a way. No one asks too many questions here.",
                50,
                R,
                G,
                B,
            )
            time.sleep(1)
            write_slow(
                " The tavern is loud. The forest quieter. I prefer the latter.",
                50,
                R,
                G,
                B,
            )
            print()
            topics["town"] = True

        elif action == "leave":
            write_slow(f" ...", 50, r, g, b)
            time.sleep(2)
            print()
            write_slow(
                " Quiet. Hm. I can respect that.",
                50,
                R,
                G,
                B,
            )
            if not topics["introduced"]:
                time.sleep(1)
                write_slow(
                    "\n That said, if you are here to buy, speech is occasionally required.",
                    50,
                    R,
                    G,
                    B,
                )
            print()
            break

        # After all branches exhausted
        if all(topics.values()):
            time.sleep(1)
            write_slow(
                "\n Celeste folds her arms. 'You ask many questions for someone just exploring. Do you actually intend to purchase something?'",
                50,
                R,
                G,
                B,
            )
            print()
            break

    press_any_key()


def celeste_additional_questions(state):
    """Handle remaining questions if player left early"""
    r, g, b = get_player_color(state)
    topics = state.npc_topics_asked["celeste"]

    write_slow(
        " Celeste glances up from her work. 'Something else you need to know?'",
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
            options.append("Ask about the shop")
            option_map[idx] = "store"
            idx += 1

        if not topics["town"]:
            options.append("Ask about the town")
            option_map[idx] = "town"
            idx += 1

        options.append("Nothing, just looking")
        option_map[idx] = "leave"

        # If all topics done, exit
        if topics["store"] and topics["town"]:
            break

        choice = menu_choice(options)
        action = option_map[choice]

        if action == "store":
            write_slow(f" What is it you sell here?", 50, r, g, b)
            time.sleep(1)
            print()
            write_slow(
                " Tonics, herbs, distillates, and certain compounds that should not be sold but are, regardless.",
                50,
                R,
                G,
                B,
            )
            write_slow(
                " Alchemy is not trade, it is transformation. But coin still keeps the fire lit, so I sell.",
                50,
                R,
                G,
                B,
            )
            print()
            topics["store"] = True

        elif action == "town":
            write_slow(f" What can you tell me about Kimaer?", 50, r, g, b)
            time.sleep(1)
            print()
            write_slow(
                " Small. Predictable. The seasons change faster than the people do.",
                50,
                R,
                G,
                B,
            )
            write_slow(
                " It is... comforting, in a way. No one asks too many questions here.",
                50,
                R,
                G,
                B,
            )
            print()
            topics["town"] = True

        elif action == "leave":
            write_slow(
                " Very well. Let me know if you require assistance.", 50, R, G, B
            )
            print()
            break

    press_any_key()


def celeste_repeat_greeting(state):
    """Called when player talks to Celeste after first meeting"""
    r, g, b = get_player_color(state)

    # Check if there are unasked questions
    topics = state.npc_topics_asked.get("celeste", {})
    has_unasked = not all(topics.values())

    if has_unasked:
        celeste_additional_questions(state)
    else:
        # Regular repeat greeting
        greetings = [
            f" Back again, {state.name}? Bon. Try not to disturb the order this time.",
            f" Hm. {state.name}. I suppose you found the place tolerable after all.",
            f" You again. Very well. What is it you require?",
        ]
        import random

        greeting = random.choice(greetings)
        write_slow(greeting, 50, R, G, B)
        print()
        press_any_key()


def celeste_rat_quest_panic(state):
    """Celeste panicking about rats - FIRST ENCOUNTER"""
    from quests.quests import start_quest, advance_quest

    r, g, b = get_player_color(state)

    write_slow(
        " You find Celeste outside her shop, hands clenched, apron stained with spilled potion. Stray hairs escape her usually perfect bun.",
        50,
        255,
        255,
        255,
    )
    time.sleep(1)
    write_slow(
        "\n\n Rats. In my shop. My... everything overturned.",
        25,
        R,
        G,
        B,
    )
    time.sleep(1)
    write_slow(
        "\n Her breath hitches. She presses fingers to her temple.",
        50,
        255,
        255,
        255,
    )
    print()
    time.sleep(1)
    write_slow(
        "\n Mon dieu... I cannot go back in there alone. Will you... help me?",
        100,
        R,
        G,
        B,
    )
    print()

    choice = menu_choice(["Of course", "Not right now"], state)

    if choice == 1:
        write_slow(
            "\n Bon... merci. You will need a weapon.",
            50,
            R,
            G,
            B,
        )
        time.sleep(1)
        write_slow(
            "\n Roslin might have something. Tell her it's for moi- tell her Celeste sent you...",
            50,
            R,
            G,
            B,
        )
        print()

        start_quest(state, "celeste_rats")
        advance_quest(state, "celeste_rats")
        print_color("New Quest: A Scream in the Night", 255, 200, 50)
        print()
        press_any_key()
    else:
        write_slow(
            "\n Très bien. I will... manage.",
            50,
            R,
            G,
            B,
        )
        print()
        press_any_key()


def celeste_quest_complete(state):
    """Quest completion"""
    from quests.quests import advance_quest

    r, g, b = get_player_color(state)

    clear()
    write_slow(
        "The last rat falls. Silence fills the shop.",
        50,
        255,
        255,
        255,
    )
    print()
    time.sleep(2)
    write_slow(
        "Celeste steps through the doorway. Her eyes scan the carnage, then settle on you.",
        50,
        255,
        255,
        255,
    )
    print()
    time.sleep(1)
    write_slow(
        "\n You... succeeded.",
        50,
        R,
        G,
        B,
    )
    time.sleep(1)
    write_slow(
        "\n She straightens a fallen vial, avoiding your gaze.",
        50,
        255,
        255,
        255,
    )
    print()
    time.sleep(1)
    write_slow(
        "\n My reaction earlier was... undignified. I do not lose control.",
        50,
        R,
        G,
        B,
    )
    time.sleep(1)
    write_slow(
        "\n A faint flush colors her pale cheeks. 'Non, that is not true. Not always.'",
        50,
        R,
        G,
        B,
    )
    print()
    time.sleep(1)
    write_slow(
        "\n You have my thanks. More than I can repay with coin.",
        50,
        R,
        G,
        B,
    )
    press_any_key()
    clear()

    # Complete quest
    advance_quest(state, "celeste_rats")  # Stage 3: Return to Celeste
    advance_quest(state, "celeste_rats")  # Complete
    state.save()

    print()
    press_any_key()
