# enemies.py

ENEMIES = {
    "Giant Rat": {
        "health": 15,
        "damage": 3,
        "defense": 0,
        "gold_drop": (1, 3),
        "item_drops": [
            ("Rat Tail", 0.3),
        ],
        "description": "A cancerous rodent, that deserves nothing but death",
        "difficulty": 0.8,
        "exp_drop": (3, 5),
    },
    "Goblin": {
        "health": 25,
        "damage": 5,
        "defense": 2,
        "gold_drop": (3, 8),
        "item_drops": [
            ("Goblin Ear", 0.5),
            ("Health Potion", 0.2),
        ],
        "description": "A scrappy green Wildkin with a rusty blade",
        "difficulty": 1,
        "exp_drop": (5, 10),
    },
    "Bandit": {
        "health": 40,
        "damage": 8,
        "defense": 3,
        "gold_drop": (10, 20),
        "item_drops": [
            ("Iron Dagger", 0.05),
            ("Bread", 0.1),
        ],
        "description": "A desperate being driven to crime",
        "difficulty": 1.3,
        "exp_drop": (10, 15),
    },
    "Wolf": {
        "health": 30,
        "damage": 7,
        "defense": 1,
        "gold_drop": (0, 2),
        "item_drops": [
            ("Wolf Pelt", 0.6),
        ],
        "description": "A Wildkin predator, hungry and aggressive",
        "difficulty": 1,
        "exp_drop": (5, 15),
    },
    "Skeleton": {
        "health": 35,
        "damage": 9,
        "defense": 5,
        "gold_drop": (5, 12),
        "item_drops": [
            ("Bone", 0.8),
            ("Rusty Sword", 0.2),
        ],
        "description": "Animated bones held together by dark magic",
        "difficulty": 1.5,
        "exp_drop": (10, 20),
    },
}
