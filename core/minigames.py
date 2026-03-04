import random
import time
import sys
from core.utils import (
    print_color,
    clear,
    flush_input,
    _read_char_timeout,
    _restore_terminal,
    _setup_terminal,
)


def bar_serving_minigame(round_number: int) -> int:
    """
    Bar serving minigame with multiple simultaneous orders.
    Returns total points earned.
    """

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


def fishing_minigame(state) -> None:
    """
    Fishing minigame.

    Flow:
    1. Check player has a rod.
    2. Show bait selection (or no-bait dead end).
    3. Roll a fish weighted by bait affinity.
    4. Run the sliding-bar catch minigame.
    5. On catch, add fish to inventory and consume bait.
    """
    from data.items import ITEMS
    from core.utils import menu_choice
    import random, time, threading

    # Resolve equipped rod
    rod_name = getattr(state, "equipped_rod", None)

    # Fallback: if the player has any rod in inventory but hasn't equipped one,
    # just pick the first one found. You may want a proper equip flow later.
    if rod_name is None:
        rod_items = [
            i.name
            for i in state.inventory.items
            if ITEMS.get(i.name, {}).get("rod_width") is not None
        ]
        if not rod_items:
            clear()
            print_color("You don't have a fishing rod.", 255, 100, 100)
            time.sleep(2)
            return
        rod_name = rod_items[0]

    rod_data = ITEMS[rod_name]
    rod_width = rod_data["rod_width"]  # chars
    drain_ratio = rod_data["drain_ratio"]  # drain per gain unit

    # Bait selection
    while True:
        clear()
        print_color("=== FISHING ===", 50, 180, 255)
        print()

        bait_items = [i for i in state.inventory.items if i.item_type == "bait"]

        if not bait_items:
            print_color("You have no bait.", 200, 200, 200)
            print()
            menu_choice(["Leave"])
            return

        print("Choose bait:")
        print()
        bait_options = [
            f"{b.name} x{b.count}  —  {ITEMS[b.name]['description']}"
            for b in bait_items
        ]
        bait_options.append("Leave")
        choice = menu_choice(bait_options)

        if choice == len(bait_options):
            return

        chosen_bait = bait_items[choice - 1]
        bait_affinity = ITEMS[chosen_bait.name].get("affinity", [])
        break

    # Roll a fish (affinity fish 3× more likely)
    all_fish = {
        name: data for name, data in ITEMS.items() if data.get("type") == "fish"
    }

    pool = []
    for name, data in all_fish.items():
        weight = 3 if name in bait_affinity else 1
        pool.extend([name] * weight)

    fish_name = random.choice(pool)
    fish_data = all_fish[fish_name]
    difficulty = fish_data["difficulty"]  # 0.0–1.0

    clear()
    print_color("=== FISHING ===", 50, 180, 255)
    print()
    print_color("Something's biting...", 150, 220, 255)
    time.sleep(1.5)

    # Minigame constants
    BAR_WIDTH = 50
    FRAME_DELAY = 0.05  # seconds per frame  (20 fps)
    # fish moves this many chars per frame on average
    FISH_SPEED = difficulty * 0.4  # at diff 1.0 → 0.4 chars/frame; feels manageable

    # Catch progress: 0.0 → 1.0
    # While fish is inside rod zone:  progress += GAIN_RATE per frame
    # While outside:                  progress -= DRAIN_RATE per frame
    GAIN_RATE = 0.008
    DRAIN_RATE = GAIN_RATE * drain_ratio

    # Fish movement: accumulate fractional position, move by whole chars
    fish_pos = BAR_WIDTH // 2  # start centre
    fish_frac = 0.0  # sub-char accumulator
    fish_dir = random.choice([-1, 1])
    fish_remaining = 0  # chars left to travel in this burst

    def _new_burst():
        dist = random.choice([1, 5])
        return dist

    fish_remaining = _new_burst()

    # Rod starts centre
    rod_pos = BAR_WIDTH // 2 - rod_width // 2
    rod_pos = max(0, min(rod_pos, BAR_WIDTH - rod_width))

    catch_progress = 0.0  # 0.0–1.0
    caught = False
    lost = False

    # Input thread — reads 'a' / 'd' continuously
    rod_move = [0]  # -1, 0, or 1 set by input thread
    stop_ev = threading.Event()

    def _input_loop():
        while not stop_ev.is_set():
            ch = _read_char_timeout(0.05, accept={"a", "d"})
            if ch == "a":
                rod_move[0] = -1
            elif ch == "d":
                rod_move[0] = 1
            else:
                rod_move[0] = 0
            flush_input()

    saved = _setup_terminal()
    try:
        t = threading.Thread(target=_input_loop, daemon=True)
        t.start()

        # Main loop
        while not caught and not lost:

            # -- Move rod --
            rod_pos = max(0, min(rod_pos + rod_move[0], BAR_WIDTH - rod_width))
            rod_move[0] = 0

            # -- Move fish --
            fish_frac += FISH_SPEED
            steps = int(fish_frac)
            fish_frac -= steps

            for _ in range(steps):
                if fish_remaining <= 0:
                    fish_dir = random.choice([-1, 1])
                    fish_remaining = _new_burst()

                next_pos = fish_pos + fish_dir
                if next_pos < 0 or next_pos >= BAR_WIDTH:
                    fish_dir *= -1
                    next_pos = fish_pos + fish_dir

                fish_pos = max(0, min(next_pos, BAR_WIDTH - 1))
                fish_remaining -= 1

            # -- Check overlap --
            in_zone = rod_pos <= fish_pos < rod_pos + rod_width

            if in_zone:
                catch_progress = min(1.0, catch_progress + GAIN_RATE)
            else:
                catch_progress = max(0.0, catch_progress - DRAIN_RATE)

            if catch_progress >= 1.0:
                caught = True
                break
            if catch_progress <= 0.0 and not in_zone:
                # Only lose once progress has been established and then drained
                # (avoids instant-lose at the very start before any contact)
                if catch_progress == 0.0 and in_zone is False:
                    # give a tiny grace window at the start
                    pass
                lost = True
                break

            # -- Render --
            clear()
            print_color("=== FISHING ===", 50, 180, 255)
            print()
            print_color(f"Fish: {fish_name}  |  Rod: {rod_name}", 150, 220, 255)
            print()

            # Fish + rod bar
            bar = [" "] * BAR_WIDTH
            for i in range(rod_pos, rod_pos + rod_width):
                bar[i] = "░"
            bar[fish_pos] = "▓"
            print(f"[{''.join(bar)}]")
            print()
            print_color("  a ←  move rod  → d", 150, 150, 150)
            print()

            # Catch progress bar (20 chars wide)
            prog_width = 20
            filled = int(catch_progress * prog_width)
            prog_bar = "█" * filled + "░" * (prog_width - filled)
            pct = int(catch_progress * 100)
            print(f"Catch: [{prog_bar}] {pct}%")
            print()

            time.sleep(FRAME_DELAY)

    finally:
        stop_ev.set()
        _restore_terminal(saved)

    # Result
    clear()
    print_color("=== FISHING ===", 50, 180, 255)
    print()

    if caught:
        print_color(f"You caught a {fish_name}!", 50, 255, 100)
        state.inventory.add_item(fish_name)
        state.inventory.remove_item(chosen_bait.name, 1)
        state.save()
    else:
        print_color("The fish got away.", 255, 100, 100)
        state.inventory.remove_item(chosen_bait.name, 1)
        state.save()

    time.sleep(2)
