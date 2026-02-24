from typing import Optional, Callable, List
from core.display import clear, press_any_key, print_color
from core.utils import add_xp


class Quest:
    def __init__(
        self,
        quest_id: str,
        name: str,
        description: str,
        stages: List[str],
        rewards: dict,
    ):
        """
        Create a quest.

        Args:
            quest_id: Unique identifier
            name: Display name
            description: Quest description
            stages: List of stage descriptions
            rewards: Dict with "gold", "items", "exp" keys
        """
        self.quest_id = quest_id
        self.name = name
        self.description = description
        self.stages = stages
        self.current_stage = 0
        self.completed = False
        self.rewards = rewards

    def advance_stage(self) -> bool:
        """
        Advance to next stage. Returns True if quest completed.
        """
        self.current_stage += 1
        if self.current_stage >= len(self.stages):
            self.completed = True
            return True
        return False

    def get_current_objective(self) -> str:
        """Get current stage description."""
        if self.completed:
            return "Quest Complete!"
        if self.current_stage < len(self.stages):
            return self.stages[self.current_stage]
        return "Unknown objective"

    def is_active(self) -> bool:
        """Check if quest is in progress."""
        return self.current_stage > 0 and not self.completed

    def to_dict(self) -> dict:
        """Convert to dict for saving."""
        return {
            "quest_id": self.quest_id,
            "current_stage": self.current_stage,
            "completed": self.completed,
        }

    @staticmethod
    def from_dict(data: dict) -> "Quest":
        """Load from save data."""
        quest_id = data["quest_id"]
        if quest_id not in QUESTS:
            raise ValueError(f"Unknown quest: {quest_id}")

        quest = create_quest(quest_id)
        quest.current_stage = data["current_stage"]
        quest.completed = data["completed"]
        return quest


# Quest database
QUESTS = {
    "celeste_rats": {
        "name": "A Scream in the Night",
        "description": "Celeste needs help dealing with a rat infestation in her shop.",
        "stages": [
            "Talk to Celeste about the scream",
            "Get a weapon from Roslin",
            "Defeat the rats in the Alchemy Shop",
            "Return to Celeste",
        ],
        "rewards": {
            "gold": 25,
            "items": ["Health Potion"],
            "exp": 50,
        },
    },
    "wilson_supplies": {
        "name": "Bar Supplies",
        "description": "Wilson needs supplies from the general store.",
        "stages": [
            "Talk to Wilson",
            "Buy supplies from Roslin",
            "Return to Wilson",
            "Buy fishing rod from Roslin",
            "Open the map and select 'Gulf of Burhkeria'",
            "Return to Wilson about the triton",
            "Open the map and select 'Lake'",
        ],
        "rewards": {
            # Spare gold
            "exp": 50,
        },
    },
    "benji_mystery": {
        "name": "The Gnome's Riddle",
        "description": "Benji has a cryptic message for you.",
        "stages": [
            "Talk to Benji",
            "Decipher his riddle",
            "Find the hidden object",
            "Return to Benji",
        ],
        "rewards": {
            "items": ["Ancient Scroll"],
            "exp": 100,
        },
    },
}


def create_quest(quest_id: str) -> Quest:
    """Create a quest from the database."""
    if quest_id not in QUESTS:
        raise ValueError(f"Unknown quest: {quest_id}")

    data = QUESTS[quest_id]
    return Quest(
        quest_id=quest_id,
        name=data["name"],
        description=data["description"],
        stages=data["stages"],
        rewards=data["rewards"],
    )


def start_quest(state, quest_id: str) -> bool:
    """
    Start a quest if not already active.

    Returns True if started, False if already active/completed.
    """
    # Check if already active
    for quest in state.active_quests:
        if quest.quest_id == quest_id:
            return False

    # Check if already completed
    if quest_id in state.completed_quests:
        return False

    # Start quest
    quest = create_quest(quest_id)
    quest.current_stage = 0  # Stage 0 = quest received but not started
    state.active_quests.append(quest)
    state.save()
    return True


def advance_quest(state, quest_id: str) -> bool:
    """
    Advance a quest to next stage.

    Returns True if quest completed, False otherwise.
    """
    for quest in state.active_quests:
        if quest.quest_id == quest_id:
            completed = quest.advance_stage()

            if completed:
                # Move to completed
                state.active_quests.remove(quest)
                state.completed_quests.append(quest_id)

                # Give rewards
                apply_quest_rewards(state, quest)

            state.save()
            return completed

    return False


def apply_quest_rewards(state, quest: Quest) -> None:
    """Apply quest rewards to player state."""

    print()
    print_color("=== QUEST COMPLETE ===", 50, 255, 50)
    print_color(f"{quest.name}", 255, 200, 100)
    print()

    rewards = quest.rewards

    if rewards.get("gold", 0) > 0:
        state.gold += rewards["gold"]
        print_color(f"Gained {rewards['gold']} gold!", 255, 200, 50)

    if rewards.get("items"):
        for item_name in rewards["items"]:
            state.inventory.add_item(item_name, 1)
            print_color(f"Received: {item_name}", 200, 255, 200)

    if rewards.get("exp", 0) > 0:
        print_color(f"Gained {rewards['exp']} experience!", 100, 200, 255)
        add_xp(state, rewards["exp"])

    print()


def get_active_quest(state, quest_id: str) -> Optional[Quest]:
    """Get an active quest by ID."""
    for quest in state.active_quests:
        if quest.quest_id == quest_id:
            return quest
    return None


def is_quest_active(state, quest_id: str) -> bool:
    """Check if a quest is currently active."""
    return get_active_quest(state, quest_id) is not None


def is_quest_completed(state, quest_id: str) -> bool:
    """Check if a quest has been completed."""
    return quest_id in state.completed_quests


def show_quest_log(state) -> None:
    """Display the quest log."""

    clear()
    print_color("=== Quest Log ===", 255, 200, 100)
    print()

    if not state.active_quests and not state.completed_quests:
        print("No quests yet.")
        print()
        press_any_key()
        return

    # Active quests
    if state.active_quests:
        print_color("Active Quests:", 255, 200, 50)
        for quest in state.active_quests:
            print()
            print_color(f"• {quest.name}", 200, 255, 200)
            print(f"  {quest.get_current_objective()}")

    # Completed quests
    if state.completed_quests:
        print()
        print_color(f"Completed Quests: {len(state.completed_quests)}", 100, 255, 100)
        for quest_id in state.completed_quests:
            if quest_id in QUESTS:
                print(f"  • {QUESTS[quest_id]['name']}")

    print()
    press_any_key()
