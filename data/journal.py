import time

JOURNAL_ENTRIES = {
    # === CHARACTERS ===
    # Roslin
    "roslin": {
        "title": "Roslin",
        "category": "character",
        "subject": "roslin",
        "order": 1,
        "text": "A Wood Elf shopkeeper in Kimaer. Warm, mischievous, and somehow already knows your name before you've said it twice.",
    },
    "roslin_store": {
        "title": "Roslin - Her Shop",
        "category": "character",
        "subject": "roslin",
        "order": 2,
        "text": (
            "Roslin's General Store smells of sandalwood and rain-soaked bark. "
            "She stocks the basics, but her inventory seems to shift depending on what you need."
        ),
    },
    "roslin_town": {
        "title": "Roslin - On Kimaer",
        "category": "character",
        "subject": "roslin",
        "order": 3,
        "text": "Roslin has strong opinions about Kimaer. She's protective of it in the way someone is when they've chosen a place rather than been born into it.",
    },
    # Celeste
    "celeste": {
        "title": "Celeste",
        "category": "character",
        "subject": "celeste",
        "order": 1,
        "text": "A Dhampir alchemist. Precise, tidy, and polite in the way that makes you feel like she's deciding whether you're worth her time.",
    },
    "celeste_shop": {
        "title": "Celeste - Her Shop",
        "category": "character",
        "subject": "celeste",
        "order": 2,
        "text": "Celeste sells tonics, reagents, and 'certain compounds that should not be sold.' She does not elaborate.",
    },
    "celeste_rats": {
        "title": "Celeste - Rats",
        "category": "character",
        "subject": "celeste",
        "order": 3,
        "text": "It seems Celeste doesn't like rats.",
    },
    # Wilson
    "wilson": {
        "title": "Wilson",
        "category": "character",
        "subject": "wilson",
        "order": 1,
        "text": "A Human barkeep. Broad-shouldered, tired, and already done with you before you've opened your mouth. It's his bar. He runs it.",
    },
    "wilson_tavern": {
        "title": "Wilson - His Tavern",
        "category": "character",
        "subject": "wilson",
        "order": 2,
        "text": "Wilson's Bar serves ale, food when the cook shows up, and peace when it can get it. Wilson keeps order mostly by being larger than the problem.",
    },
    "wilson_gnome": {
        "title": "Wilson - Neighbors",
        "category": "character",
        "subject": "wilson",
        "order": 3,
        "text": "Wilson seems to have a distaste for the gnome.",
    },
    # Silas
    "silas": {
        "title": "Silas",
        "category": "character",
        "subject": "silas",
        "order": 1,
        "text": "A Drow bouncer in an alley in Kimaer. Scarred knuckles, scarlet eyes, and a one-word vocabulary: 'Leave.'",
    },
    # Benji
    "benji": {
        "title": "Benji",
        "category": "character",
        "subject": "benji",
        "order": 1,
        "text": "A Gnome of unclear occupation sitting near the fountain. Either a prophet or completely unhinged. Possibly both.",
    },
    # === LOCATIONS ===
    "kimaer": {
        "title": "Kimaer",
        "category": "location",
        "subject": "kimaer",
        "order": 1,
        "text": (
            "A small town. Home to a general store, an alchemy shop, and Wilson's Bar. "
        ),
    },
    "gulf_of_burhkeria": {
        "title": "Gulf of Burhkeria",
        "category": "location",
        "subject": "gulf_of_burhkeria",
        "order": 1,
        "text": ("A gulf. "),
    },
    "lunara": {
        "title": "Lunara",
        "category": "location",
        "subject": "lunara",
        "order": 1,
        "text": "A settlement near the lake to the northwest of Kimaer.",
    },
    # === ENEMIES ===
    "giant_rat": {
        "title": "Giant Rat",
        "category": "enemy",
        "subject": "giant_rat",
        "order": 1,
        "text": "A cancerous rodent. Deserves nothing but death.",
    },
    # === LORE ===
    # Add as needed
}

CATEGORY_LABELS = {
    "character": "Characters",
    "location": "Locations",
    "enemy": "Enemies",
    "lore": "Lore",
}

CATEGORY_ORDER = ["character", "location", "enemy", "lore"]


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.state import GameState


def unlock_journal_entry(state: "GameState", key: str) -> None:
    """Call this whenever the player meets someone / visits somewhere for the first time."""
    if key in JOURNAL_ENTRIES and key not in state.journal_entries:
        state.journal_entries.append(key)
        time.sleep(1)
