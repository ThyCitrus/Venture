import random
import time
import sys
from core.utils import print_color, clear, flush_input


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


def fishing_minigame(catch_difficulty, bait_type, rod_type):
    """Fishing minigame."""
    pass
