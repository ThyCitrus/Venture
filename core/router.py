from utils import print_color
from core.state import GameState
import time


def location_router(state: GameState) -> None:
    from core.locations import kimaer, shop, wilsons_bar, LOCATION_MAP

    """Routes the player to the correct location based on state.location"""
    location = state.location

    # Check if it's a shop (has shop type in the name)
    if "General Store" in location:
        town = location.split()[0]
        shop(state, location_name=town, shop_type="general")
    elif "Alchemy Shop" in location:
        town = location.split()[0]
        shop(state, location_name=town, shop_type="alchemy")
    elif location == "Wilson's Bar":
        wilsons_bar(state)
    # Direct location lookup
    elif location in LOCATION_MAP:
        LOCATION_MAP[location](state)
    else:
        # Fallback if location is unrecognized
        print_color(
            f"Unknown location: {location}. Returning to Kimaer...", 255, 200, 50
        )
        time.sleep(2)
        kimaer(state)
