import time
from core.display import clear, write_slow, press_any_key
from core.locations import kimaer, shop

# region Events


def trigger_rat_quest(state):
    """Called after first sleep - triggers rat quest"""
    from dialogue.kimaer.celeste import celeste_rat_quest_panic

    clear()
    print()
    write_slow(
        "As you wake, you hear a distant scream piercing the morning air.",
        50,
        255,
        160,
        200,
    )
    print()
    time.sleep(2)
    write_slow("It came from the village square.", 50, 255, 160, 200)
    print()
    press_any_key()

    # Set flag so this doesn't repeat
    state.rat_quest_triggered = True
    state.save()

    # Route to special Kimaer event
    kimaer_rat_event(state)


def kimaer_rat_event(state):
    """Special version of Kimaer for rat quest start"""
    from dialogue.kimaer.celeste import celeste_rat_quest_panic

    state.location = "Kimaer"
    clear()
    print()

    write_slow(
        "You rush to the village square. A small crowd has gathered near the alchemy shop.",
        50,
        200,
        250,
        0,
    )
    print()
    press_any_key()
    clear()

    celeste_rat_quest_panic(state)

    # After quest dialogue, return to normal Kimaer
    kimaer(state)


def alchemy_shop_rat_combat(state):
    """Combat encounter in the alchemy shop"""
    from core.combat import combat, Enemy
    from quests.quests import is_quest_active, get_active_quest
    from dialogue.kimaer.celeste import celeste_quest_complete

    # Check if quest is at the right stage
    quest = get_active_quest(state, "celeste_rats")
    if not quest or quest.current_stage != 2:  # Stage 2 = defeat rats
        # Normal shop behavior
        shop(state, "Kimaer", "alchemy")
        return

    clear()
    write_slow(
        "You push open the door to the alchemy shop. Glass crunches underfoot.",
        50,
    )
    print()
    time.sleep(2)
    write_slow(
        "Three massive rats turn to face you, their eyes gleaming red in the dim light.",
        50,
        255,
        100,
        100,
    )
    print()
    press_any_key()

    # Combat!
    enemies = [
        Enemy("Giant Rat"),
        Enemy("Giant Rat"),
        Enemy("Giant Rat"),
    ]

    won = combat(state, enemies)

    if won:
        celeste_quest_complete(state)
        # After quest complete, go to normal shop
        shop(state, "Kimaer", "alchemy")
    else:
        # Player fled or died - return to Kimaer
        kimaer(state)


# endregion
