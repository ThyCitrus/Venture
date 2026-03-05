# Venture
A terminal-based RPG built in Python. Developed by Auxiliary Games (that's me!).

---

## About

Venture is a text-based RPG set in a handcrafted fantasy world. You wake up in a field with nothing: no name, no class, no direction; and go from there. The world is driven by dialogue, exploration, and consequence, which sounds impressive until you realize it's also driven by me having to write all of it.

It's in active development. "Playable" is being used generously here. There isn't a ton to do yet, and things will break. That's a promise, not a warning.

---

## Features

- **Character creation** - Name your character, pick a class, pick a race (eventually), and receive a randomly generated color. If you roll three identical values, send me a screenshot. I might put you in the game. Or just, be helpful, that warrants a cameo.
- **Five playable classes** - Fighter, Warlock, Rogue, Paladin, and Cleric. Each has unique stat modifiers and resource pools (HP, mana, stamina). Some have no mana. Some have no stamina.
- **Turn-based combat** - Fight enemies using class-specific skills, spells, and techniques that unlock as you level up.
- **Quest system** - Multi-stage quests with branching dialogue and actual consequences. In theory.
- **NPC dialogue** - Named characters with distinct personalities, memory of past interactions, and evolving conversations. They're more interesting than I am.
- **Inventory & shops** - Buy, sell, and manage items across multiple vendors.
- **ASCII world map** - Handmade. I spent three hours making it, I hope you all like it.
- **Save/load system** - JSON-based saves tied to your character name.
- **Journal** - In-game lore entries on characters, enemies, and locations.
- **Audio** - Audio. Sound. Something to listen to.

Yes, most of these are just standard RPG features. We'll get to the unique stuff eventually.

---

## World

The game currently takes place in and around **Kimaer**, a small village on the land of Burhkeria. The rest of the world map exists, it just has nothing in it yet.

Planned locations include Lunara, Duskwood, Eldoria, Frostholm, the Gulf of Burhkeria, and more. In some order. To be determined.

---

## Getting Started

**Requirements:** Python 3.10+ (developed on 3.12), pygame 2.0+, git to be installed

```bash
python -m pip install pygame
git clone https://github.com/ThyCitrus/venture.git
cd venture
python main.py
```

One dependency, pygame, is required, above is a series of commands to perform in your terminal (after downloading python) on how to play the game

---

## Project Structure

```
venture/
├── main.py               # Entry point and core game loop
├── requirements.txt      # *A* dependency: pygame
├── README.md             # You're looking at it
├── core/
|   ├── audio             # FOR MUSIC!! WE HAVE THAT!!
|   |   ├──music
|   |   └──sfx
│   ├── combat.py         # Combat engine
│   ├── locations.py      # Location handlers
│   ├── utils.py          # Shared utilities (printing, input, XP, etc.)
│   └── constants.py      # Game constants
├── data/
│   ├── items.py          # Item definitions
│   ├── map.py            # ASCII world map
│   ├── journal.py        # Journal entries
│   └── skills.py         # Spells and techniques
├── dialogue/
│   └── kimaer/           # NPC dialogue by location
├── quests/
│   ├── quests.py         # Quest state management
│   └── hooks.py          # Location-based quest triggers
```

No, I will not be updating this as new files are added. I am doing this all for free. Maybe Water will.

---

## Status

Early development. The tutorial arc and Kimaer are playable. Most of the world map is currently geography with labels you can't see unless you look through the code. Don't. It's bad. I'm ashamed.

**Planned (not in order):**
- Fishing minigame
- Dungeon crawling
- Additional locations (Lunara, the Gulf, the Lake)

**Development doc:** [Google Docs](https://docs.google.com/document/d/1618JGgBIqtmNnqrlXR5Ycyos6SO8HVzB-CSbSv6EmsQ/edit?usp=sharing)

---

## License

Not licensed for redistribution. All rights reserved.