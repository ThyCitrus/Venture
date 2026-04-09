import random
import time
from core.display import clear, write_slow, press_any_key
from core.utils import get_player_color
from core.constants import NYCTOS_GUARD
from data.journal import unlock_journal_entry
from quests.quests import start_quest, advance_quest, is_quest_active


def triton_introduction(state):
    clear()
    write_slow("I don't know what to write here yet, but I will eventually.")
