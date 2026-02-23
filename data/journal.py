from core.utils import print_color
import time

JOURNAL_ENTRIES = {
    # === CHARACTERS ===
    # Roslin
    "roslin": {
        "title": "Roslin",
        "category": "character",
        "text": "A Wood Elf shopkeeper in Kimaer. Warm, mischievous, and somehow already knows your name before you've said it twice.",
    },
    "roslin_store": {
        "title": "Roslin - Her Shop",
        "category": "character",
        "text": (
            "Roslin's General Store smells of sandalwood and rain-soaked bark. "
            "She stocks the basics, but her inventory seems to shift depending on what you need."
        ),
    },
    "roslin_town": {
        "title": "Roslin - On Kimaer",
        "category": "character",
        "text": "Roslin has strong opinions about Kimaer. She's protective of it in the way someone is when they've chosen a place rather than been born into it.",
    },
    # Celeste
    "celeste": {
        "title": "Celeste",
        "category": "character",
        "text": "A Dhampir alchemist. Precise, tidy, and polite in the way that makes you feel like she's deciding whether you're worth her time.",
    },
    "celeste_shop": {
        "title": "Celeste - Her Shop",
        "category": "character",
        "text": "Celeste sells tonics, reagents, and 'certain compounds that should not be sold.' She does not elaborate.",
    },
    "celeste_rats": {
        "title": "Celeste - Rats",
        "category": "character",
        "text": "It seems Celeste doesn't like rats.",
    },
    # Wilson
    "wilson": {
        "title": "Wilson",
        "category": "character",
        "text": "A Human barkeep. Broad-shouldered, tired, and already done with you before you've opened your mouth. It's his bar. He runs it.",
    },
    "wilson_tavern": {
        "title": "Wilson - His Tavern",
        "category": "character",
        "text": "Wilson's Bar serves ale, food when the cook shows up, and peace when it can get it. Wilson keeps order mostly by being larger than the problem.",
    },
    "wilson_gnome": {
        "title": "Wilson - Neighbors",
        "category": "character",
        "text": "Wilson seems to have a distaste for the gnome.",
    },
    # Silas
    "silas": {
        "title": "Silas",
        "category": "character",
        "text": "A Drow bouncer in an alley in Kimaer. Scarred knuckles, scarlet eyes, and a one-word vocabulary: 'Leave.'",
    },
    # Benji
    "benji": {
        "title": "Benji",
        "category": "character",
        "text": "A Gnome of unclear occupation sitting near the fountain. Either a prophet or completely unhinged. Possibly both.",
    },
    # === LOCATIONS ===
    "kimaer": {
        "title": "Kimaer",
        "category": "location",
        "text": (
            "A small town. Home to a general store, an alchemy shop, and Wilson's Bar. "
        ),
    },
    "lunara": {
        "title": "Lunara",
        "category": "location",
        "text": "A settlement near the lake to the northwest of Kimaer.",
    },
    # === ENEMIES ===
    "giant_rat": {
        "title": "Giant Rat",
        "category": "enemy",
        "text": "A cancerous rodent, that deserves nothing but death.",
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
        title = JOURNAL_ENTRIES[key]["title"]
        print_color(f'[Journal updated: "{title}"]', 150, 150, 255)
        time.sleep(1)
