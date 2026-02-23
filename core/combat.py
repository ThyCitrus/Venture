import time
import random
from typing import List
from core.utils import (
    clear,
    print_color,
    write_slow,
    press_any_key,
    menu_choice,
    add_xp,
)
from data.enemies import ENEMIES
from data.skills import SPELLS, TECHNIQUES
import select as _select
import threading
import sys


# region Enemy


class Enemy:
    def __init__(self, enemy_name: str):
        if enemy_name not in ENEMIES:
            raise ValueError(f"Unknown enemy: {enemy_name}")
        data = ENEMIES[enemy_name]
        self.name = enemy_name
        self.max_health = data["health"]
        self.health = data["health"]
        self.damage = data["damage"]
        self.defense = data["defense"]
        self.gold_drop = data["gold_drop"]
        self.item_drops = data["item_drops"]
        self.description = data.get("description", "")
        self.difficulty = data.get("difficulty", 1.0)
        self.exp_drop = data.get("exp_drop", (0, 0))
        self.status_effects = []

    def is_alive(self) -> bool:
        return self.health > 0

    def take_damage(self, amount: int) -> int:
        actual = max(1, amount - self.defense)
        self.health -= actual
        return actual

    def get_loot(self) -> dict:
        gold = random.randint(*self.gold_drop)
        items = [name for name, chance in self.item_drops if random.random() < chance]
        xp = random.randint(*self.exp_drop)
        return {"gold": gold, "items": items, "xp": xp}


# endregion


# region Effects


EFFECTS = {
    "damage_buff": {
        "category": "buff",
        "target": "player",
        "tick": False,
        "stat": "damage",
        "apply_type": "percent",
        "value": 1.5,
        "description": "Increases damage output",
    },
    "defense_buff": {
        "category": "buff",
        "target": "player",
        "tick": False,
        "stat": "defense",
        "apply_type": "flat",
        "value": 10,
        "description": "Increases damage resistance",
    },
    "dodge_chance": {
        "category": "buff",
        "target": "player",
        "tick": False,
        "stat": "dodge",
        "apply_type": "percent",
        "value": 0.5,
        "description": "Chance to completely avoid an attack",
    },
    "regen": {
        "category": "buff",
        "target": "player",
        "tick": True,
        "stat": "health",
        "apply_type": "flat",
        "value": 5,
        "description": "Restores health each turn",
    },
    "mana_regen": {
        "category": "buff",
        "target": "player",
        "tick": True,
        "stat": "mana",
        "apply_type": "flat",
        "value": 5,
        "description": "Restores mana each turn",
    },
    "weakness": {
        "category": "debuff",
        "target": "player",
        "tick": False,
        "stat": "damage",
        "apply_type": "percent",
        "value": 0.6,
        "description": "Reduces damage output significantly",
    },
    "slow": {
        "category": "debuff",
        "target": "player",
        "tick": False,
        "stat": "dodge",
        "apply_type": "percent",
        "value": 0.0,
        "description": "Cannot dodge attacks",
    },
    "vulnerable": {
        "category": "debuff",
        "target": "player",
        "tick": False,
        "stat": "defense",
        "apply_type": "flat",
        "value": -10,
        "description": "Defense is reduced",
    },
    "burn": {
        "category": "dot",
        "target": "player",
        "tick": True,
        "stat": "health",
        "apply_type": "flat",
        "value": -4,
        "description": "Takes fire damage each turn",
    },
    "bleed": {
        "category": "dot",
        "target": "player",
        "tick": True,
        "stat": "health",
        "apply_type": "flat",
        "value": -3,
        "description": "Loses health from bleeding each turn",
    },
    "stun": {
        "category": "debuff",
        "target": "both",
        "tick": False,
        "stat": None,
        "apply_type": None,
        "value": None,
        "description": "Skips next turn",
    },
    "poison": {
        "category": "dot",
        "target": "enemy",
        "tick": True,
        "stat": "health",
        "apply_type": "flat",
        "value": -5,
        "description": "Takes poison damage each turn",
    },
    "armor_break": {
        "category": "debuff",
        "target": "enemy",
        "tick": False,
        "stat": "defense",
        "apply_type": "flat",
        "value": -8,
        "description": "Enemy defense is reduced",
    },
    "expose": {
        "category": "debuff",
        "target": "enemy",
        "tick": False,
        "stat": "defense",
        "apply_type": "percent",
        "value": 0.5,
        "description": "Enemy is exposed, taking increased damage",
    },
}


def get_damage_mod(active_effects: list) -> float:
    mod = 1.0
    for eff in active_effects:
        defn = EFFECTS.get(eff["type"], {})
        if defn.get("stat") == "damage" and defn.get("apply_type") == "percent":
            mod *= eff.get("value", defn["value"])
    return mod


def get_defense_bonus(active_effects: list) -> int:
    bonus = 0
    for eff in active_effects:
        defn = EFFECTS.get(eff["type"], {})
        if defn.get("stat") == "defense" and defn.get("apply_type") == "flat":
            bonus += eff.get("value", defn["value"])
    return bonus


def get_dodge_mod(active_effects: list) -> float:
    mod = 1.0
    base = 0.0
    for eff in active_effects:
        defn = EFFECTS.get(eff["type"], {})
        if defn.get("stat") == "dodge" and defn.get("apply_type") == "percent":
            if defn["category"] == "buff":
                base += eff.get("value", defn["value"])
            else:
                mod *= eff.get("value", defn["value"])
    return base * mod


def is_stunned(active_effects: list) -> bool:
    return any(eff["type"] == "stun" for eff in active_effects)


def apply_effect(
    target_effects: list, effect_type: str, duration: int, value=None
) -> None:
    defn = EFFECTS.get(effect_type)
    if not defn:
        return
    actual_value = value if value is not None else defn["value"]
    for eff in target_effects:
        if eff["type"] == effect_type:
            eff["duration"] = max(eff["duration"], duration)
            eff["value"] = actual_value
            return
    target_effects.append(
        {"type": effect_type, "duration": duration, "value": actual_value}
    )


def tick_effects(active_effects: list, state=None) -> tuple:
    expired, remaining = [], []
    hp_delta = mana_delta = stamina_delta = 0

    for eff in active_effects:
        defn = EFFECTS.get(eff["type"], {})
        if defn.get("tick"):
            val = eff.get("value", defn.get("value", 0))
            stat = defn.get("stat")
            if stat == "health":
                hp_delta += val
            elif stat == "mana":
                mana_delta += val
            elif stat == "stamina":
                stamina_delta += val
        eff["duration"] -= 1
        if eff["duration"] <= 0:
            expired.append(eff["type"])
        else:
            remaining.append(eff)

    active_effects[:] = remaining

    if state:
        if hp_delta:
            state.health = max(0, min(state.max_health, state.health + hp_delta))
        if mana_delta and state.max_mana > 0:
            state.mana = max(0, min(state.max_mana, state.mana + mana_delta))
        if stamina_delta and state.max_stamina > 0:
            state.stamina = max(
                0, min(state.max_stamina, state.stamina + stamina_delta)
            )

    return expired, hp_delta, mana_delta, stamina_delta


# endregion


# region Skills


def get_available_skills(class_name: str, level: int = 1) -> dict:
    if class_name == "Paladin":
        source = {**SPELLS, **TECHNIQUES}
    elif class_name in ("Warlock", "Cleric"):
        source = SPELLS
    else:
        source = TECHNIQUES
    return {
        name: data
        for name, data in source.items()
        if data["class"] == class_name and data.get("unlock_level", 1) <= level
    }


def _setup_terminal():
    try:
        import termios, tty

        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        tty.setcbreak(fd)
        return fd, old
    except ImportError:
        return None


def _restore_terminal(saved):
    if saved is None:
        return
    try:
        import termios

        fd, old = saved
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    except Exception:
        pass


def _read_char_timeout(timeout: float, accept: set = None):
    try:
        import termios

        deadline = time.time() + timeout
        while True:
            remaining = deadline - time.time()
            if remaining <= 0:
                return None
            if _select.select([sys.stdin], [], [], min(0.02, remaining))[0]:
                ch = sys.stdin.read(1).lower()
                if accept is None or ch in accept:
                    return ch
    except ImportError:
        import msvcrt

        deadline = time.time() + timeout
        while time.time() < deadline:
            if msvcrt.kbhit():
                ch = msvcrt.getch().decode("utf-8", errors="ignore").lower()
                if accept is None or ch in accept:
                    return ch
            time.sleep(0.01)
        return None


def _skill_qte(sequence: list, time_limit: float) -> int:
    _arrows = {"w": "↑", "a": "←", "s": "↓", "d": "→"}
    key_display = {
        k: f"{k.upper()} {_arrows[k]}" if k in _arrows else k.upper() for k in sequence
    }

    bar_width = 40
    frame_delay = 0.04
    hits = 0

    for i, expected in enumerate(sequence):
        target_width = max(4, 8 - i)
        target_start = random.randint(8, bar_width - target_width - 8)
        target_end = target_start + target_width
        perfect_start = target_start + (target_width // 3)
        perfect_end = target_end - (target_width // 3)

        speed = max(2, int(8 / time_limit))
        position = [0]
        direction = [1]
        pressed = threading.Event()
        press_position = [None]
        press_key = [None]

        def check_input(ev=pressed, pos=press_position, key=press_key):
            ch = _read_char_timeout(time_limit + 0.5)
            if ch is not None:
                key[0] = ch
                pos[0] = position[0]
                ev.set()

        saved = _setup_terminal()
        try:
            t = threading.Thread(target=check_input, daemon=True)
            t.start()

            start = time.time()
            while not pressed.is_set() and time.time() - start < time_limit:
                bar = [" "] * bar_width
                for j in range(target_start, min(target_end, bar_width)):
                    bar[j] = "█"
                p = position[0]
                if 0 <= p < bar_width:
                    bar[p] = "▓"

                clear()
                print_color("=== SKILL INPUT ===", 100, 200, 255)
                print()
                parts = []
                for j, k in enumerate(sequence):
                    disp = key_display.get(k, k.upper())
                    if j < i:
                        parts.append(f"\033[38;2;50;200;50m{disp}\033[0m")
                    elif j == i:
                        parts.append(f"\033[38;2;255;255;50m[ {disp} ]\033[0m")
                    else:
                        parts.append(f"\033[38;2;150;150;150m{disp}\033[0m")
                print("  " + "  →  ".join(parts))
                print()
                print_color(
                    f"Time: {time_limit - (time.time() - start):.1f}s", 200, 200, 100
                )
                print()
                print(f"[{''.join(bar)}]")
                print()

                time.sleep(frame_delay)
                position[0] += direction[0] * speed
                if position[0] >= bar_width - 1:
                    direction[0] = -1
                elif position[0] <= 0:
                    direction[0] = 1

            pressed.set()
        finally:
            _restore_terminal(saved)

        if press_position[0] is None:
            clear()
            print_color("=== SKILL INPUT ===", 100, 200, 255)
            print()
            print_color(
                f"Too slow! Interrupted at step {i+1}/{len(sequence)}.", 255, 100, 100
            )
            time.sleep(1.5)
            break

        p = press_position[0]
        k = press_key[0]

        if k != expected:
            clear()
            print_color("=== SKILL INPUT ===", 100, 200, 255)
            print()
            print_color(
                f"Wrong key! Expected [{key_display.get(expected, expected.upper())}].",
                255,
                100,
                100,
            )
            time.sleep(1.5)
            break

        if perfect_start <= p < perfect_end:
            hits += 1
            clear()
            print_color("=== SKILL INPUT ===", 100, 200, 255)
            print()
            print_color("PERFECT!", 50, 255, 50)
            time.sleep(0.3)
        elif target_start <= p < target_end:
            hits += 1
            clear()
            print_color("=== SKILL INPUT ===", 100, 200, 255)
            print()
            print_color("Hit!", 255, 200, 50)
            time.sleep(0.3)
        else:
            clear()
            print_color("=== SKILL INPUT ===", 100, 200, 255)
            print()
            print_color("Missed!", 255, 100, 100)
            time.sleep(1.5)
            break

    return hits


def skill_menu(state, enemies: list) -> dict:
    if not state.player_class:
        return {"type": "cancelled"}

    skills = get_available_skills(state.player_class.name, state.level)
    if not skills:
        print_color("No skills available.", 200, 200, 200)
        time.sleep(1)
        return {"type": "cancelled"}

    clear()
    print_color("=== Skills ===", 100, 200, 255)
    print()

    skill_names = list(skills.keys())
    options = []
    for name in skill_names:
        sk = skills[name]
        cost_type = "MP" if "mana_cost" in sk else "SP"
        cost_val = sk.get("mana_cost", sk.get("stamina_cost", 0))
        options.append(f"{name}  [{cost_val} {cost_type}]  -  {sk['description']}")
    options.append("Cancel")

    choice = menu_choice(options)
    if choice == len(options):
        return {"type": "cancelled"}

    skill_name = skill_names[choice - 1]
    skill = skills[skill_name]

    if "mana_cost" in skill:
        if state.mana < skill["mana_cost"]:
            print_color("Not enough mana!", 255, 100, 100)
            time.sleep(1)
            return {"type": "cancelled"}
        state.mana -= skill["mana_cost"]
    elif "stamina_cost" in skill:
        if state.stamina < skill["stamina_cost"]:
            print_color("Not enough stamina!", 255, 100, 100)
            time.sleep(1)
            return {"type": "cancelled"}
        state.stamina -= skill["stamina_cost"]

    target = None
    if skill["target"] == "single":
        alive = [e for e in enemies if e.is_alive()]
        if len(alive) > 1:
            clear()
            print("Choose target:")
            target = alive[menu_choice([e.name for e in alive]) - 1]
        else:
            target = alive[0]

    hits = _skill_qte(skill["sequence"], skill["sequence_time"])
    ratio = hits / len(skill["sequence"])

    clear()
    print_color(f"=== {skill_name} ===", 100, 200, 255)
    print()

    if hits == 0:
        print_color("No inputs hit! Skill fizzled.", 255, 100, 100)
        time.sleep(2)
        return {"type": "fizzle", "skill": skill_name}

    if hits == len(skill["sequence"]):
        print_color("PERFECT!", 50, 255, 50)
    else:
        print_color(
            f"Partial: {hits}/{len(skill['sequence'])} inputs ({int(ratio * 100)}%)",
            255,
            200,
            50,
        )
    print()

    result = {"type": "skill", "skill": skill_name, "hits": hits}

    if "damage" in skill and skill["damage"] > 0:
        final_dmg = int(
            int(skill["damage"] * ratio) * get_damage_mod(state.active_effects)
        )
        targets = (
            [e for e in enemies if e.is_alive()]
            if skill["target"] == "enemies"
            else ([target] if target else [])
        )
        for e in targets:
            actual = e.take_damage(final_dmg)
            print_color(f"{e.name} takes {actual} damage!", 255, 200, 50)
            if not e.is_alive():
                print_color(f"{e.name} defeated!", 50, 255, 50)
        result["damage"] = final_dmg

    if "heal" in skill:
        heal_amt = int(skill["heal"] * ratio)
        old_hp = state.health
        state.health = min(state.max_health, state.health + heal_amt)
        print_color(f"Restored {state.health - old_hp} health!", 50, 255, 50)
        result["heal"] = state.health - old_hp

    if "effect" in skill and hits > 0:
        eff = skill["effect"].copy()
        scaled_duration = max(1, int(eff.get("duration", 1) * ratio))

        if "damage_buff" in eff:
            state.active_effects.append(
                {
                    "type": "damage_buff",
                    "value": eff["damage_buff"],
                    "duration": scaled_duration,
                }
            )
            print_color(
                f"Damage buffed x{eff['damage_buff']} for {scaled_duration} turns!",
                200,
                150,
                255,
            )
        elif "defense_buff" in eff:
            state.active_effects.append(
                {
                    "type": "defense_buff",
                    "value": eff["defense_buff"],
                    "duration": scaled_duration,
                }
            )
            print_color(
                f"+{eff['defense_buff']} defense for {scaled_duration} turns!",
                100,
                200,
                255,
            )
        elif "dodge_chance" in eff:
            state.active_effects.append(
                {
                    "type": "dodge_chance",
                    "value": eff["dodge_chance"],
                    "duration": scaled_duration,
                }
            )
            print_color(
                f"{int(eff['dodge_chance']*100)}% dodge for {scaled_duration} turns!",
                50,
                255,
                200,
            )
        elif "poison" in eff and target:
            target.status_effects.append(
                {"type": "poison", "value": -eff["poison"], "duration": scaled_duration}
            )
            print_color(
                f"{target.name} is poisoned! ({eff['poison']} dmg/turn for {scaled_duration} turns)",
                100,
                255,
                100,
            )
        elif "stun" in eff and target:
            target.status_effects.append(
                {"type": "stun", "value": 1, "duration": scaled_duration}
            )
            print_color(
                f"{target.name} is stunned for {scaled_duration} turn(s)!", 200, 200, 50
            )

    time.sleep(2)
    return result


# endregion


# region QTE Defense


def qte_defense(difficulty: float = 1.0) -> str:
    clear()
    print_color("=== INCOMING ATTACK ===", 255, 100, 100)
    print()
    print("Press SPACE when the bar hits the zone!")
    print()

    bar_width = 40
    target_start = random.randint(10, 25)
    target_width = 6
    target_end = target_start + target_width
    perfect_start = target_start + 2
    perfect_end = target_end - 2

    frame_delay = 0.04
    speed = max(1, int(bar_width * frame_delay / (5.0 * 0.6 / difficulty)))
    position = [0]
    direction = [1]
    pressed = threading.Event()
    press_position = [None]

    def check_input():
        ch = _read_char_timeout(6.0, accept={" "})
        if ch is not None:
            press_position[0] = position[0]
            pressed.set()

    saved = _setup_terminal()
    try:
        t = threading.Thread(target=check_input, daemon=True)
        t.start()

        start = time.time()
        while not pressed.is_set() and time.time() - start < 5.0:
            bar = [" "] * bar_width
            for i in range(target_start, min(target_end, bar_width)):
                bar[i] = "█"
            p = position[0]
            if 0 <= p < bar_width:
                bar[p] = "▓"
            print(f"\r[{''.join(bar)}]", end="", flush=True)
            time.sleep(frame_delay)
            position[0] += direction[0] * speed
            if position[0] >= bar_width - 1:
                direction[0] = -1
            elif position[0] <= 0:
                direction[0] = 1

        pressed.set()
        print()
    finally:
        _restore_terminal(saved)

    if press_position[0] is None:
        return "miss"
    p = press_position[0]
    if perfect_start <= p < perfect_end:
        return "perfect"
    elif target_start <= p < target_end:
        return "block"
    return "miss"


# endregion


# region Combat


def _show_combat_status(state, enemies: list, turn: int) -> None:
    print_color(f"=== Turn {turn} ===", 200, 200, 255)
    print()
    print_color(f"Your HP: {state.health}/{state.max_health}", 50, 255, 50)

    if state.max_mana > 0:
        print_color(f"Mana:    {state.mana}/{state.max_mana}", 255, 0, 255)
    if state.max_stamina > 0:
        print_color(f"Stamina: {state.stamina}/{state.max_stamina}", 255, 140, 0)

    if hasattr(state, "active_effects") and state.active_effects:
        eff_strs = []
        dmg_mod = get_damage_mod(state.active_effects)
        def_bon = get_defense_bonus(state.active_effects)
        dodge = get_dodge_mod(state.active_effects)
        if dmg_mod > 1.0:
            turns = next(
                e["duration"]
                for e in state.active_effects
                if e["type"] == "damage_buff"
            )
            eff_strs.append(f"DMG x{dmg_mod} ({turns}t)")
        if def_bon > 0:
            turns = next(
                e["duration"]
                for e in state.active_effects
                if e["type"] == "defense_buff"
            )
            eff_strs.append(f"+{def_bon} DEF ({turns}t)")
        if dodge > 0:
            turns = next(
                e["duration"]
                for e in state.active_effects
                if e["type"] == "dodge_chance"
            )
            eff_strs.append(f"{int(dodge*100)}% Dodge ({turns}t)")
        if eff_strs:
            print_color("Buffs: " + " | ".join(eff_strs), 200, 150, 255)

    print()

    for i, enemy in enumerate(enemies):
        if enemy.is_alive():
            status_str = ""
            if enemy.status_effects:
                tags = []
                for eff in enemy.status_effects:
                    if eff["type"] == "poison":
                        tags.append(f"Poisoned({eff['duration']}t)")
                    elif eff["type"] == "stun":
                        tags.append("Stunned")
                status_str = "  [" + ", ".join(tags) + "]"
            print_color(
                f"{i+1}. {enemy.name} - HP: {enemy.health}/{enemy.max_health}{status_str}",
                255,
                100,
                100,
            )
    print()


def _pick_target(enemies: list) -> Enemy:
    alive = [e for e in enemies if e.is_alive()]
    if len(alive) == 1:
        return alive[0]
    print()
    print("Choose target:")
    return alive[menu_choice([e.name for e in alive]) - 1]


def combat(state, enemies: List[Enemy]) -> bool:
    from data.items import ITEMS

    if not hasattr(state, "active_effects"):
        state.active_effects = []

    clear()
    print_color("=== COMBAT START ===", 255, 50, 50)

    if len(enemies) == 1:
        write_slow(f"A {enemies[0].name} appears!", 50, 255, 100, 100)
    else:
        write_slow(
            f"You're surrounded by: {', '.join(e.name for e in enemies)}!",
            50,
            255,
            100,
            100,
        )

    time.sleep(2)

    has_skills = bool(
        state.player_class
        and get_available_skills(state.player_class.name, state.level)
    )
    turn = 1
    last_total_damage = 5

    while state.health > 0 and any(e.is_alive() for e in enemies):
        clear()
        _show_combat_status(state, enemies, turn)

        menu_opts = ["Attack"]
        if has_skills:
            menu_opts.append("Skills")
        menu_opts += ["Items", "Flee"]

        action = menu_opts[menu_choice(menu_opts) - 1]

        if action == "Attack":
            target = _pick_target(enemies)
            weapon_damage = 0
            if state.equipped_weapon:
                raw = ITEMS.get(state.equipped_weapon, {}).get("damage", 0)
                weapon_damage = random.randint(*raw) if isinstance(raw, tuple) else raw

            class_mod = state.player_class.damage_mod if state.player_class else 1.0
            total_damage = int(
                (5 + weapon_damage + state.level)
                * class_mod
                * get_damage_mod(state.active_effects)
            )
            last_total_damage = total_damage

            actual = target.take_damage(total_damage)
            print()
            print_color(f"You attack {target.name} for {actual} damage!", 255, 200, 50)
            if not target.is_alive():
                print_color(f"{target.name} defeated!", 50, 255, 50)
            time.sleep(2)

        elif action == "Skills":
            result = skill_menu(state, [e for e in enemies if e.is_alive()])
            if result["type"] == "cancelled":
                continue
            if result.get("damage"):
                last_total_damage = result["damage"]

        elif action == "Items":
            print_color("Item usage not yet implemented!", 255, 200, 50)
            time.sleep(1)
            continue

        elif action == "Flee":
            if random.random() < 0.5:
                print_color("You fled from combat!", 200, 200, 50)
                time.sleep(2)
                return False
            print_color("Couldn't escape!", 255, 100, 100)
            time.sleep(2)

        if not any(e.is_alive() for e in enemies):
            break

        expired, hp_delta, _, _ = tick_effects(state.active_effects, state)
        for name in expired:
            print_color(f"{name.replace('_', ' ').title()} wore off.", 150, 150, 150)
        if hp_delta != 0:
            label = "regen" if hp_delta > 0 else "damage"
            print_color(
                f"Effect {label}: {abs(hp_delta)} HP",
                150,
                255 if hp_delta > 0 else 100,
                150,
            )

        for enemy in enemies:
            if not enemy.is_alive():
                continue

            enemy_stunned = is_stunned(enemy.status_effects)

            remaining = []
            hp_delta_e = 0
            for eff in enemy.status_effects:
                if eff["type"] == "poison":
                    hp_delta_e += eff["value"]
                eff["duration"] -= 1
                if eff["duration"] > 0:
                    remaining.append(eff)
            enemy.status_effects = remaining
            enemy.health += hp_delta_e

            if hp_delta_e < 0:
                print_color(
                    f"{enemy.name} takes {abs(hp_delta_e)} poison damage!",
                    100,
                    255,
                    100,
                )
                if not enemy.is_alive():
                    print_color(f"{enemy.name} succumbed to poison!", 50, 255, 50)
                    time.sleep(1)
                    continue

            if enemy_stunned:
                print_color(
                    f"{enemy.name} is stunned and skips their turn!", 200, 200, 50
                )
                time.sleep(1)
                continue

            clear()
            print_color(f"{enemy.name} attacks!", 255, 100, 100)
            time.sleep(1)

            dodge = get_dodge_mod(state.active_effects)
            if dodge > 0 and random.random() < dodge:
                print_color("You dodge the attack!", 50, 255, 200)
                time.sleep(2)
                continue

            result = qte_defense(difficulty=enemy.difficulty)

            if result == "perfect":
                print_color("PERFECT PARRY! No damage taken!", 50, 255, 50)
                print_color("Counter attack!", 255, 200, 50)
                counter_dmg = enemy.take_damage(last_total_damage // 2)
                print_color(f"You counter for {counter_dmg} damage!", 255, 200, 50)
                if not enemy.is_alive():
                    print_color(f"{enemy.name} defeated!", 50, 255, 50)

            elif result == "block":
                damage = max(
                    1, enemy.damage // 2 - get_defense_bonus(state.active_effects)
                )
                state.health -= damage
                print_color(f"Blocked! Took {damage} damage.", 255, 200, 50)

            else:
                damage = enemy.damage
                if state.equipped_armor:
                    defense = ITEMS.get(state.equipped_armor, {}).get(
                        "defense", 0
                    ) + get_defense_bonus(state.active_effects)
                    damage = max(1, damage - defense)
                state.health -= damage
                print_color(f"HIT! Took {damage} damage!", 255, 50, 50)

            time.sleep(2)

            if state.health <= 0:
                clear()
                print_color("=== DEFEAT ===", 255, 50, 50)
                write_slow("You have been defeated...", 50, 255, 100, 100)
                time.sleep(3)
                return False

        turn += 1

    clear()
    print_color("=== VICTORY ===", 50, 255, 50)
    write_slow("All enemies defeated!", 50, 50, 255, 50)
    print()
    time.sleep(2)

    total_gold, total_items, total_xp = 0, [], 0
    for enemy in enemies:
        loot = enemy.get_loot()
        total_gold += loot["gold"]
        total_items.extend(loot["items"])
        total_xp += loot["xp"]

    if total_gold > 0:
        state.gold += total_gold
        print_color(f"Gained {total_gold} gold!", 255, 200, 50)

    for item_name in total_items:
        state.inventory.add_item(item_name, 1)
        print_color(f"Found: {item_name}", 200, 255, 200)

    if total_xp > 0:
        add_xp(state, total_xp)

    if state.max_mana > 0:
        regen = int(state.max_mana * 0.05)
        state.mana = min(state.max_mana, state.mana + regen)
        print_color(f"Mana restored: +{regen}", 255, 0, 255)
    if state.max_stamina > 0:
        regen = int(state.max_stamina * 0.05)
        state.stamina = min(state.max_stamina, state.stamina + regen)
        print_color(f"Stamina restored: +{regen}", 255, 140, 0)

    print()
    state.save()
    press_any_key()
    return True


# endregion
