from quests.quests import get_active_quest

QUEST_HOOKS = {
    "kimaer_alchemy": {
        "celeste_rats:2": "alchemy_shop_rat_combat",
    },
}


def get_location_hook(state, location_key):
    import main

    hooks = QUEST_HOOKS.get(location_key, {})
    for quest in state.active_quests:
        hook_key = f"{quest.quest_id}:{quest.current_stage}"
        if hook_key in hooks:
            func_name = hooks[hook_key]
            return getattr(main, func_name, None)
    return None
