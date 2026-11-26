
import os
import time
import random
import datetime
import platform
import shutil

PINK = "\033[38;5;213m"
PURPLE = "\033[38;5;141m"
RED = "\033[38;5;196m"
CYAN = "\033[38;5;51m"
WHITE = "\033[97m"
GRAY = "\033[90m"
GREEN = "\033[38;5;82m"
RESET = "\033[0m"
BOLD = "\033[1m"

VERSION = "1.0.0"
OWNER = "Auri"
PROJECT = "AuriTerm"


def clear():
    os.system("clear")


def slow(text, delay=0.01):
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()


def banner():
    print(PINK + BOLD + r"""
     █████╗ ██╗   ██╗██████╗ ██╗
    ██╔══██╗██║   ██║██╔══██╗██║
    ███████║██║   ██║██████╔╝██║
    ██╔══██║██║   ██║██╔══██╗██║
    ██║  ██║╚██████╔╝██║  ██║██║
    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝
    """ + RESET)

    print(PURPLE + BOLD + "          A U R I T E R M" + RESET)
    print(CYAN + "       COLORFUL TERMINAL ENVIRONMENT" + RESET)
    print(GRAY + "       Version " + VERSION + " | By " + OWNER + RESET)
    print()


def color_art():
    arts = [
        r"""
          /\_/\
         ( o.o )
          > ^ <
        """,
        r"""
        .-==========-.
        |   A U R I  |
        '-==========-'
        """,
        r"""
          . * . * .
        *   DEMON   *
          . * . * .
        """,
        r"""
         /\     /\
        /  \___/  \
        \  AURI   /
         \_______/
        """
    ]

    color = random.choice([PINK, PURPLE, CYAN, RED])
    print(color + random.choice(arts) + RESET)


def auribot():
    print(PINK + "\n[AuriBot] Hello, Auri!" + RESET)
    print(GRAY + "A programmed assistant, not AI." + RESET)
    print("Type 'back' to return.")

    while True:
        try:
            msg = input(CYAN + "You > " + WHITE).strip().lower()
        except (KeyboardInterrupt, EOFError):
            print(RESET)
            return

        if msg == "back":
            return

        elif msg in ("hello", "hi", "hey"):
            print(PINK + "AuriBot > Welcome back!" + RESET)

        elif msg == "help":
            print("Commands: hello, hi, hey, time, date,")
            print("art, about, help, back")

        elif msg == "time":
            print(datetime.datetime.now().strftime("%H:%M:%S"))

        elif msg == "date":
            print(datetime.date.today())

        elif msg == "art":
            color_art()

        elif msg == "about":
            print("AuriBot is a programmed assistant.")
            print("Created for AuriTerm by Auri.")

        else:
            print(PINK + "AuriBot > I don't know that yet." + RESET)


def database():
    entries = [
        ("D-001", "NULLENTITY"),
        ("D-002", "PINKERROR"),
        ("D-003", "VOID-16"),
        ("D-004", "UNKNOWN"),
        ("D-005", "AURI-GHOST"),
        ("D-006", "REDSTATIC"),
        ("D-007", "DREAMBYTE"),
        ("D-008", "KERNEL-16")
    ]

    print(PURPLE + "\n--- DEMON DATABASE ---" + RESET)

    for code, name in entries:
        print(PINK + "[" + code + "] " + WHITE + name + RESET)

    print(GRAY + "All entries are fictional." + RESET)


def diagnostics():
    print(CYAN + "\n--- SYSTEM DIAGNOSTICS ---" + RESET)

    print("Project:", PROJECT)
    print("Platform:", platform.system())
    print("Python:", platform.python_version())
    print("Architecture:", platform.machine())

    try:
        free = shutil.disk_usage(".").free
        print("Free storage:", round(free / 1024**3, 2), "GB")
    except OSError:
        print("Free storage: unavailable")

    print(GREEN + "AuriTerm status: ONLINE" + RESET)
    print("Real system modifications: NONE")


def settings():
    print(PURPLE + "\n--- SETTINGS ---" + RESET)
    print("Project:", PROJECT)
    print("Version:", VERSION)
    print("Owner:", OWNER)
    print("Theme: Pink / Purple")
    print("Color effects: Enabled")
    print("Visual corruption: Enabled")
    print("System modifications: Disabled")


def corruption():
    print(RED + "\n[CORRUPTION ENGINE]" + RESET)

    glitches = [
        "010101 ERROR",
        "REALITY_MISMATCH",
        "0xDEMON_FOUND",
        "AURITERM::GLITCH",
        "MEMORY_SIGNAL_LOST",
        "VOID_CONNECTION",
        "SYSTEM_GHOST_FOUND",
        "PIXEL_FAILURE"
    ]

    for _ in range(8):
        print(RED + random.choice(glitches) + RESET)
        time.sleep(0.15)

    print(PINK + "[END] Visual simulation complete." + RESET)


def help_menu():
    print(PURPLE + BOLD + "\n--- AURITERM COMMANDS ---" + RESET)

    commands = [
        "-help",
        "-open AuriBot",
        "-open ColorArt",
        "-open DemonDatabase",
        "-open Diagnostics",
        "-open Settings",
        "-corrupt",
        "-clear",
        "-version",
        "-about",
        "-exit"
    ]

    for command in commands:
        print(PINK + "  " + command + RESET)


def about():
    print(PURPLE + "\n--- ABOUT AURITERM ---" + RESET)
    print("Name:", PROJECT)
    print("Version:", VERSION)
    print("Creator:", OWNER)
    print("Environment: Termux / Python")
    print("A colorful command-driven terminal.")
    print("AuriOS OS is a separate project.")


def execute(command):
    cmd = command.strip().lower()

    if cmd == "-help":
        help_menu()

    elif cmd == "-open auribot":
        auribot()

    elif cmd == "-open colorart":
        color_art()

    elif cmd == "-open demondatabase":
        database()

    elif cmd == "-open diagnostics":
        diagnostics()

    elif cmd == "-open settings":
        settings()

    elif cmd == "-corrupt":
        corruption()

    elif cmd == "-clear":
        clear()
        banner()

    elif cmd == "-version":
        print(PROJECT, VERSION)

    elif cmd == "-about":
        about()

    elif cmd == "-exit":
        slow(PURPLE + "AuriTerm shutting down safely..." + RESET)
        return False

    elif cmd == "":
        pass

    else:
        print(RED + "Unknown command. Type -help." + RESET)

    return True


def main():
    clear()

    slow(PINK + "[AuriTerm] Starting..." + RESET)
    slow(CYAN + "[SYSTEM] Loading modules..." + RESET)
    slow(GREEN + "[SYSTEM] Modules ready." + RESET)

    banner()

    print(GRAY + "Type -help to see available commands." + RESET)

    while True:
        try:
            command = input(PINK + "\nroot@auriterm:~$ " + WHITE + RESET)

            if not execute(command):
                break

        except (KeyboardInterrupt, EOFError):
            print(RESET + "\nAuriTerm stopped safely.")
            break


if __name__ == "__main__":
    main()
