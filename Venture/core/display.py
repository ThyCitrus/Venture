import sys
import time
import os


def flush_input() -> None:
    """Discard any buffered keystrokes so they don't bleed into the next prompt."""
    try:
        import termios

        termios.tcflush(sys.stdin, termios.TCIFLUSH)
    except ImportError:
        import msvcrt

        while msvcrt.kbhit():
            msvcrt.getch()


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


def print_color(text: str, r: int, g: int, b: int) -> None:
    print(f"\033[38;2;{r};{g};{b}m{text}\033[0m")


def write_slow(
    text: str, delay_ms: int = 50, r: int = 255, g: int = 255, b: int = 255
) -> None:
    for char in text:
        print(f"\033[38;2;{r};{g};{b}m{char}\033[0m", end="", flush=True)
        time.sleep(delay_ms / 1000.0)
    print()
