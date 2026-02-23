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
from core.constants import KIMAER_WILSON
from data.journal import unlock_journal_entry

R, G, B = 100, 140, 75


def wilson_first_meeting(state):
    r, g, b = get_player_color(state)

    # Initialize tracking for this NPC if not exists
    if "wilson" not in state.npc_topics_asked:
        state.npc_topics_asked["wilson"] = {
            "introduced": False,
            "tavern": False,
            "town": False,
            "job_offered": False,  # Track if job has been offered
        }

    topics = state.npc_topics_asked["wilson"]

    # INTRO - only plays once
    write_slow(
        "\n A broad-shouldered man behind the bar looks at you steadily. His expression says he's already tired of you.",
        50,
        255,
        255,
        255,
    )
    time.sleep(1)
    write_slow(
        "\n\n We're barely open. You lost, thirsty, or looking for trouble?",
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

        if not topics["tavern"]:
            options.append("Ask about the tavern")
            option_map[idx] = "tavern"
            idx += 1

        if not topics["town"]:
            options.append("Ask about Kimaer")
            option_map[idx] = "town"
            idx += 1

        options.append("Nod and sit down")
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
                " Passing through. Heard that one before. Name's Wilson. This is my place.",
                50,
                R,
                G,
                B,
            )
            write_slow(
                "\n Don't break anything and we're good.",
                50,
                R,
                G,
                B,
            )
            print()
            topics["introduced"] = True
            unlock_journal_entry(state, "wilson")

        elif action == "tavern":
            write_slow(f" What's the tavern like?", 50, r, g, b)
            time.sleep(1)
            print()
            write_slow(
                " Serves ale. Food when the cook shows up. Quiet when it's empty.",
                50,
                R,
                G,
                B,
            )
            write_slow(
                "\n Loud when it's not. I keep the peace. Mostly.",
                50,
                R,
                G,
                B,
            )
            if not topics["introduced"]:
                time.sleep(1)
                write_slow(
                    "\n Name's Wilson. You got a name?",
                    50,
                    R,
                    G,
                    B,
                )
            print()
            topics["tavern"] = True
            unlock_journal_entry(state, "wilson_tavern")

        elif action == "town":
            write_slow(f" What's Kimaer like?", 50, r, g, b)
            time.sleep(1)
            print()
            write_slow(
                " Small. Honest enough. You'll come to find the people are fine... mostly.",
                50,
                R,
                G,
                B,
            )
            write_slow(
                "\n That gnome... don't get me started.",
                50,
                R,
                G,
                B,
            )
            time.sleep(1)
            write_slow(
                "\n You planning to stay or just drink and go?",
                50,
                R,
                G,
                B,
            )
            print()
            topics["town"] = True
            unlock_journal_entry(state, "wilson_gnome")

        elif action == "leave":
            write_slow(f" ...", 50, r, g, b)
            time.sleep(2)
            print()
            write_slow(
                " Quiet one, eh? Fine by me. Bar's over there.",
                50,
                R,
                G,
                B,
            )
            if not topics["introduced"]:
                time.sleep(1)
                write_slow(
                    "\n Got a name if you're staying?",
                    50,
                    R,
                    G,
                    B,
                )
            print()
            break

        # Check if all topics exhausted
        if topics["introduced"] and topics["tavern"] and topics["town"]:
            time.sleep(1)
            write_slow(
                "\n Wilson leans on the bar, studying you.",
                50,
                R,
                G,
                B,
            )
            time.sleep(1)
            write_slow(
                "\n You're new here. Need a place to stay?",
                50,
                R,
                G,
                B,
            )
            print()

            room_choice = menu_choice(["Yes, I do", "No, I'm fine"])

            if room_choice == 1:
                write_slow(
                    " Thought so. Got a room upstairs. Twenty gold a night.",
                    50,
                    R,
                    G,
                    B,
                )
                time.sleep(1)
                write_slow(
                    "\n ...Or, if you're short on coin, I could use help behind the bar.",
                    50,
                    R,
                    G,
                    B,
                )
                write_slow(
                    " Work a shift, you stay for free. Deal?",
                    50,
                    R,
                    G,
                    B,
                )
                print()

                job_choice = menu_choice(
                    ["I'll work for the room", "I'll pay gold", "Maybe later"]
                )

                if job_choice == 1:
                    write_slow(
                        " Good. You start now. Don't screw it up.",
                        50,
                        R,
                        G,
                        B,
                    )
                    print()
                    # Set job flag in state
                    if not hasattr(state, "wilson_employee"):
                        state.wilson_employee = True
                    if not hasattr(state, "wilson_room_access"):
                        state.wilson_room_access = True
                    topics["job_offered"] = True
                    press_any_key()
                    break

                elif job_choice == 2:
                    if state.gold >= 20:
                        state.gold -= 20
                        write_slow(
                            " Fair enough. Room's yours for the night. Upstairs, second door.",
                            50,
                            R,
                            G,
                            B,
                        )
                        if not hasattr(state, "wilson_room_access"):
                            state.wilson_room_access = True
                    else:
                        write_slow(
                            " You're short. Offer stands if you change your mind.",
                            50,
                            R,
                            G,
                            B,
                        )
                    print()
                    press_any_key()
                    break

                else:  # Maybe later
                    write_slow(
                        " Suit yourself. Offer's there if you need it.",
                        50,
                        R,
                        G,
                        B,
                    )
                    print()
                    topics["job_offered"] = True
                    press_any_key()
                    break
            else:
                write_slow(
                    " Suit yourself.",
                    50,
                    R,
                    G,
                    B,
                )
                print()
                topics["job_offered"] = True
                press_any_key()
                break


def wilson_additional_questions(state):
    """Handle remaining questions if player left early"""
    r, g, b = get_player_color(state)
    topics = state.npc_topics_asked["wilson"]

    write_slow(
        " Wilson looks up from wiping the bar. 'Still here?'",
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

        if not topics["tavern"]:
            options.append("Ask about the tavern")
            option_map[idx] = "tavern"
            idx += 1

        if not topics["town"]:
            options.append("Ask about Kimaer")
            option_map[idx] = "town"
            idx += 1

        # Add job option if not yet offered
        if not topics.get("job_offered", False) and not hasattr(
            state, "wilson_employee"
        ):
            options.append("Ask about work")
            option_map[idx] = "job"
            idx += 1

        options.append("Just a drink")
        option_map[idx] = "leave"

        # If all topics done, exit
        if topics["tavern"] and topics["town"]:
            break

        choice = menu_choice(options)
        action = option_map[choice]

        if action == "tavern":
            write_slow(f" What's the tavern like?", 50, r, g, b)
            time.sleep(1)
            print()
            write_slow(
                " Serves ale. Food when the cook shows up. Quiet when it's empty.",
                50,
                R,
                G,
                B,
            )
            print()
            topics["tavern"] = True

        elif action == "town":
            write_slow(f" What's Kimaer like?", 50, r, g, b)
            time.sleep(1)
            print()
            write_slow(
                " Small. Honest enough. You'll come to find the people are fine... mostly.",
                50,
                R,
                G,
                B,
            )
            write_slow(
                "\n That gnome... don't get me started.",
                50,
                R,
                G,
                B,
            )
            print()
            topics["town"] = True

        elif action == "job":
            wilson_job_offer(state)
            topics["job_offered"] = True
            break

        elif action == "leave":
            write_slow(" Right. Bar's that way.", 50, R, G, B)
            print()
            break

    press_any_key()


def wilson_job_offer(state):
    """Offer job if not already employed"""
    r, g, b = get_player_color(state)

    write_slow(
        " Need work? I could use help behind the bar.",
        50,
        R,
        G,
        B,
    )
    write_slow(
        " Work a shift, you get a room upstairs for free. Deal?",
        50,
        R,
        G,
        B,
    )
    print()

    choice = menu_choice(["Take the job", "Not interested"])

    if choice == 1:
        write_slow(
            " Good. You start now.",
            50,
            R,
            G,
            B,
        )
        state.wilson_employee = True
        state.wilson_room_access = True
        print()
        wilson_work_shift(state)
    else:
        write_slow(
            " Suit yourself. Offer's there if you change your mind.",
            50,
            R,
            G,
            B,
        )
        print()


def wilson_repeat_greeting(state):
    """Called when player talks to Wilson after first meeting"""
    r, g, b = get_player_color(state)

    topics = state.npc_topics_asked.get("wilson", {})
    has_unasked = not all(topics.values())

    if has_unasked:
        wilson_additional_questions(state)
        return

    # Check if employee
    if hasattr(state, "wilson_employee") and state.wilson_employee:
        greetings = [
            f" {state.name}. Ready for another shift?",
            " Back to work? Good.",
            " Bar needs tending. You in?",
        ]
    else:
        greetings = [
            f" {state.name}. Welcome back.",
            " Back for more? Good.",
            " You again. Ale or questions?",
        ]

    import random

    greeting = random.choice(greetings)
    write_slow(greeting, 50, R, G, B)
    print()

    choice = menu_choice(["Work at the bar", "Rent a room (20 gold)", "Leave"])
    if choice == 1:
        wilson_work_shift(state)
    elif choice == 2:
        if state.gold >= 20:
            state.gold -= 20
            print_color("Paid 20 gold for the room.", 200, 255, 200)
            time.sleep(1)

            from main import sleep

            sleep(state, "wilson_bar")

            # Trigger rat quest if not yet triggered
            if not hasattr(state, "rat_quest_triggered"):
                state.rat_quest_triggered = False

            if not state.rat_quest_triggered:
                from main import trigger_rat_quest

                trigger_rat_quest(state)
        else:
            print_color(f"Not enough gold! Need 20, have {state.gold}.", 255, 100, 100)
            time.sleep(2)


def wilson_work_shift(state):
    """Start a work shift at Wilson's bar"""
    from core.utils import bar_serving_minigame

    r, g, b = get_player_color(state)

    clear()
    write_slow(
        " Wilson tosses you an apron. 'Five rounds. Don't embarrass me.'",
        50,
        R,
        G,
        B,
    )
    print()
    press_any_key()

    total_score = 0

    for round_num in range(1, 6):
        score = bar_serving_minigame(round_num)
        total_score += score

        if round_num < 5:
            print_color(f"Total so far: {total_score}", 200, 255, 200)
            press_any_key("Press any key for next round...")
            print()

    clear()
    print_color(f"=== Shift Complete ===", 255, 200, 50)
    print(f"Total Score: {total_score}")
    print()

    # Calculate payment based on performance (tips)
    tips = total_score // 100
    payment = tips // 2  # Wilson keeps half

    if total_score >= 2000:
        write_slow(
            f" Wilson nods approvingly. 'Good work. You earned {tips} gold in tips. Keep half.'",
            50,
            R,
            G,
            B,
        )
    elif total_score >= 1000:
        write_slow(
            f" Wilson gives a slight nod. 'Not bad. {tips} gold in tips. Your cut's {payment}.'",
            50,
            R,
            G,
            B,
        )
    else:
        write_slow(
            f" Wilson frowns. 'Rough shift. Only {tips} gold. Here's your half.'",
            50,
            R,
            G,
            B,
        )

    state.gold += payment
    state.wilson_room_access = True
    press_any_key()

    from main import sleep

    sleep(state, "wilson_bar")

    # Trigger rat quest if not yet triggered
    if not hasattr(state, "rat_quest_triggered"):
        state.rat_quest_triggered = False

    if not state.rat_quest_triggered:
        from main import trigger_rat_quest

        trigger_rat_quest(state)


def wilson_interaction(state):
    if KIMAER_WILSON not in state.npc_met:
        wilson_first_meeting(state)
        state.npc_met[KIMAER_WILSON] = "wilson"
        state.save()
    else:
        wilson_repeat_greeting(state)
