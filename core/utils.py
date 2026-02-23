import os
import sys
import time
from typing import TYPE_CHECKING, List


def print_color(text: str, r: int, g: int, b: int) -> None:
    print(f"\033[38;2;{r};{g};{b}m{text}\033[0m")


def write_slow(
    text: str, delay_ms: int = 50, r: int = 255, g: int = 255, b: int = 255
) -> None:
    for char in text:
        print(f"\033[38;2;{r};{g};{b}m{char}\033[0m", end="", flush=True)
        time.sleep(delay_ms / 1000.0)
    print()


def menu_choice(options: List[str], state=None) -> int:
    """
    Display menu options and get player choice.

    Args:
        options: List of menu options
        state: GameState object (if provided, enables inventory/quest hotkeys)

    Returns:
        int: Selected option number (1-indexed)
    """
    flush_input()

    def _handle_hotkey(key, state):
        """Handle i/q hotkeys. Returns True if handled (location_router was called)."""
        if key.lower() == "i" and state is not None and state.inventory.items:
            from main import show_inventory_menu

            show_inventory_menu(state)
            # show_inventory_menu calls location_router on exit
            return True
        if (
            key.lower() == "q"
            and state is not None
            and (state.active_quests or state.completed_quests)
        ):
            from quests.quests import show_quest_log
            from main import location_router

            show_quest_log(state)
            location_router(state)
            return True
        return False

    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

    hints = []
    if state is not None:
        if state.inventory.items:
            hints.append("'i' for Inventory")
        if state.active_quests or state.completed_quests:
            hints.append("'q' for Quests")
    if hints:
        print_color(f"\n[{'  |  '.join(hints)}]", 150, 150, 150)
    print()

    # >9 options: text input
    if len(options) > 9:
        while True:
            try:
                choice = input("Enter choice: ").strip()
                if _handle_hotkey(choice, state):
                    return  # location_router took over
                num = int(choice)
                if 1 <= num <= len(options):
                    return num
                print("Invalid choice. Try again.")
            except ValueError:
                print("Invalid choice. Try again.")

    # <=9 options: single keypress
    sys.stdout.flush()
    valid_keys = [str(i) for i in range(1, len(options) + 1)]

    try:
        import termios, tty

        def getch():
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                return sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)

    except ImportError:
        import msvcrt

        def getch():
            ch = msvcrt.getch()
            if ch in (
                b"\xe0",
                b"\x00",
            ):  # extended key prefix - consume the second byte and ignore
                msvcrt.getch()
                return ""
            return ch.decode("utf-8", errors="ignore")

    while True:
        key = getch()
        if _handle_hotkey(key, state):
            return  # location_router took over
        if key in valid_keys:
            return int(key)
        print("Invalid choice. Try again.")


def clear() -> None:
    """
    Clear the console screen in different operating systems.
    """
    if os.name == "nt":  # Windows
        os.system("cls")
    else:  # Unix/Linux/Mac
        os.system("clear")


def set_terminal_title(title: str) -> None:
    if sys.platform == "win32":
        # Method 1: os.system('title ...') spawns subprocess, reliable
        os.system(f"title {title}")
        # Alternative with ctypes (no subprocess, but resets on exit):
        # import ctypes
        # ctypes.windll.kernel32.SetConsoleTitleW(title)
    else:
        # ANSI escape for Unix/Linux/macOS terminals
        print(f"\033]2;{title}\007", end="", flush=True)


def press_any_key(message: str = "Press any key to continue...") -> None:
    flush_input()
    print(message)

    try:
        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except ImportError:
        # Windows fallback
        import msvcrt

        msvcrt.getch()


def display_dialogue(
    lines: List[str], delay_ms: int = 50, r: int = 200, g: int = 200, b: int = 200
) -> None:
    """Display multiple lines of dialogue with automatic formatting"""
    for line in lines:
        write_slow(line, delay_ms, r, g, b)
        print()


def get_player_color(state):
    """Parse player color string into RGB tuple"""
    color = state.player_color.split()
    return int(color[0]), int(color[1]), int(color[2])


def quick_time_event(duration: float, key_to_press: str = "space") -> bool:
    """
    Quick time event - player must press a key within duration seconds.
    Returns True if successful, False if failed.
    """
    import select

    flush_input()

    print(f"Press {key_to_press.upper()} quickly!")
    start_time = time.time()

    try:
        # Unix/Linux/Mac
        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setcbreak(fd)

            # Wait for input with timeout
            rlist, _, _ = select.select([sys.stdin], [], [], duration)

            if rlist:
                ch = sys.stdin.read(1)
                elapsed = time.time() - start_time
                return elapsed <= duration
            else:
                return False

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    except ImportError:
        # Windows
        import msvcrt

        end_time = start_time + duration

        while time.time() < end_time:
            if msvcrt.kbhit():
                msvcrt.getch()
                return True
            time.sleep(0.01)

        return False


def quick_time_event_countdown(duration: float) -> bool:
    """QTE with visual countdown"""
    import threading

    flush_input()

    success = False
    pressed = threading.Event()

    def check_input():
        nonlocal success
        try:
            import termios
            import tty

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)
                sys.stdin.read(1)
                success = True
                pressed.set()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except ImportError:
            import msvcrt

            msvcrt.getch()
            success = True
            pressed.set()

    # Start input thread
    input_thread = threading.Thread(target=check_input, daemon=True)
    input_thread.start()

    # Countdown
    start = time.time()
    while time.time() - start < duration:
        if pressed.is_set():
            break
        remaining = duration - (time.time() - start)
        print(f"\rTime remaining: {remaining:.1f}s", end="", flush=True)
        time.sleep(0.1)

    print()
    return success


def add_xp(state, amount: int) -> None:
    """
    Add XP to the player, handle level-ups, and announce newly unlocked skills.
    Call this any time XP is earned (combat, quests, etc).
    """
    from data.skills import SPELLS, TECHNIQUES

    state.xp += amount
    print_color(f"+{amount} XP", 100, 200, 255)

    while state.xp >= state.next_level:
        state.xp -= state.next_level
        state.level += 1
        state.next_level = int(state.next_level * 1.5)  # Scale XP requirement

        print_color(f"LEVEL UP! You are now level {state.level}!", 255, 255, 50)

        # Check for newly unlocked skills
        if state.player_class:
            all_skills = {**SPELLS, **TECHNIQUES}
            for skill_name, data in all_skills.items():
                if (
                    data["class"] == state.player_class.name
                    and data.get("unlock_level") == state.level
                ):
                    # Pick color based on resource type
                    if "mana_cost" in data:
                        r, g, b = 180, 100, 255  # Purple for spells
                    else:
                        r, g, b = 255, 140, 0  # Orange for techniques

                    cost_type = "MP" if "mana_cost" in data else "SP"
                    cost_val = data.get("mana_cost", data.get("stamina_cost", 0))

                    print_color(
                        f"New skill unlocked: {skill_name} [{cost_val} {cost_type}] - {data['description']}",
                        r,
                        g,
                        b,
                    )
                    print_color(
                        f"  Use in combat via the Skills menu.", r - 40, g, b - 40
                    )

    state.save()


def flush_input() -> None:
    """Discard any buffered keystrokes so they don't bleed into the next prompt."""
    try:
        import termios

        termios.tcflush(sys.stdin, termios.TCIFLUSH)
    except ImportError:
        import msvcrt

        while msvcrt.kbhit():
            msvcrt.getch()


def show_hud(state) -> None:
    # Location
    print_color(f"Current Location: {state.location}", 200, 200, 255)

    # Health color based on percentage
    health_percent = (state.health / state.max_health) * 100
    if health_percent > 75:
        h_r, h_g, h_b = 50, 255, 50  # Green
    elif health_percent > 50:
        h_r, h_g, h_b = 255, 255, 50  # Yellow
    elif health_percent > 25:
        h_r, h_g, h_b = 255, 165, 50  # Orange
    else:
        h_r, h_g, h_b = 255, 50, 50  # Red

    # Mana - Magenta
    mana_r, mana_g, mana_b = 255, 0, 255

    # Stamina - Orange/Brown
    stam_r, stam_g, stam_b = 255, 140, 0

    # Gold color - gets more yellow as gold increases
    total_drain = state.gold // 10
    g_r = 255
    g_b = max(0, 255 - total_drain)
    green_drain = max(0, total_drain - 255)
    g_g = max(150, 255 - green_drain)

    # Level - cyan
    l_r, l_g, l_b = 0, 255, 255

    # Build the HUD string with color codes
    health_text = (
        f"\033[38;2;{h_r};{h_g};{h_b}mHealth: {state.health}/{state.max_health}\033[0m"
    )

    # Show mana/stamina based on class
    energy_parts = []
    if state.max_mana > 0:
        mana_text = f"\033[38;2;{mana_r};{mana_g};{mana_b}mMana: {state.mana}/{state.max_mana}\033[0m"
        energy_parts.append(mana_text)

    if state.max_stamina > 0:
        stamina_text = f"\033[38;2;{stam_r};{stam_g};{stam_b}mStamina: {state.stamina}/{state.max_stamina}\033[0m"
        energy_parts.append(stamina_text)

    gold_text = f"\033[38;2;{g_r};{g_g};{g_b}mGold: {state.gold}\033[0m"
    level_text = f"\033[38;2;{l_r};{l_g};{l_b}mLevel: {state.level}\033[0m"

    # Combine all parts
    parts = [health_text] + energy_parts + [gold_text, level_text]
    print(" | ".join(parts))


# region Minigames


def bar_serving_minigame(round_number: int) -> int:
    """
    Bar serving minigame with multiple simultaneous orders.
    Returns total points earned.
    """
    import random
    import threading

    # Round configuration
    base_time = max(1.0, 6.0 - (round_number / 2))
    patrons = 10 + (round_number * 5)  # 15, 20, 25, 30...
    points_per_second = 10 * round_number  # Scales with difficulty

    print_color(f"=== Round {round_number} ===", 255, 200, 50)
    print(f"Serve {patrons} patrons!")
    print(
        f"Time limit: {base_time}s per order | Points lost: {points_per_second}/second"
    )
    print()
    time.sleep(2)

    total_score = 0
    active_orders = []  # List of (key, start_time, points)
    max_active = min(5, 1 + round_number)
    completed = 0

    alphabet = "qwertyuiopasdfghjklzxcvbnm"

    def get_input():
        """Non-blocking input check"""
        try:
            import termios
            import tty

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)
                import select

                if select.select([sys.stdin], [], [], 0)[0]:
                    return sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except ImportError:
            import msvcrt

            if msvcrt.kbhit():
                return msvcrt.getch().decode("utf-8")
        return None

    start_time = time.time()
    last_spawn = start_time
    spawn_delay = 3 / (round_number * 1.5)  # Faster spawning in later rounds

    while completed < patrons:
        current_time = time.time()

        # Spawn new orders
        if (
            current_time - last_spawn >= spawn_delay
            and len(active_orders) < max_active
            and completed + len(active_orders) < patrons
        ):

            key = random.choice(alphabet)
            active_orders.append({"key": key, "start_time": current_time, "points": 50})
            last_spawn = current_time

        # Update and display active orders
        clear()
        print_color(
            f"Round {round_number} | Completed: {completed}/{patrons}", 255, 200, 50
        )
        print()

        if active_orders:
            print_color("Active Orders:", 200, 200, 255)
            for i, order in enumerate(active_orders, 1):
                elapsed = current_time - order["start_time"]
                remaining = base_time - elapsed

                # Update points
                order["points"] = max(0, 50 - int(elapsed * points_per_second))

                if remaining > 0:
                    bar_length = int((remaining / base_time) * 20)
                    bar = "█" * bar_length + "░" * (20 - bar_length)
                    print(f"  [{order['key'].upper()}] {bar} {order['points']}pts")
                else:
                    print_color(f"  [{order['key'].upper()}] EXPIRED!", 255, 50, 50)

        print()
        print_color("Type the letter shown!", 150, 150, 150)

        # Check for input
        key_pressed = get_input()

        if key_pressed:
            # Check if it matches any active order
            for order in active_orders[:]:  # Copy list to avoid modification issues
                if key_pressed.lower() == order["key"]:
                    total_score += order["points"]
                    active_orders.remove(order)
                    completed += 1
                    break
            flush_input()

        # Remove expired orders
        for order in active_orders[:]:
            elapsed = current_time - order["start_time"]
            if elapsed >= base_time:
                # Order failed - patron leaves
                active_orders.remove(order)
                completed += 1  # Still counts as "completed" (failed)

        time.sleep(0.05)  # 20 FPS update rate

    clear()
    print_color(f"Round {round_number} Complete!", 50, 255, 50)
    print(f"Score: {total_score}")
    print()
    return total_score


# endregion
