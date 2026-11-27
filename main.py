
import os
import sys
import time
import json
import math
import ast
import random
import datetime
import platform
import shutil
import hashlib
import base64
import uuid
import calendar
import shlex
import string
import colorsys
import re
from pathlib import Path

# ============================================================
# AURITERM 2.1 BISCUIT
# ============================================================

PROJECT = "AuriTerm"
VERSION = "2.1 Biscuit"
OWNER = "Auri"

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATABASE = ROOT / "database"

DATA.mkdir(exist_ok=True)
DATABASE.mkdir(exist_ok=True)

NOTES_FILE = DATA / "notes.json"
SETTINGS_FILE = DATA / "settings.json"
DEMONS_FILE = DATABASE / "demons.json"

START_TIME = time.time()
AURITERM_OPEN = True
PROGRAM_RUNNING = True
RAINBOW_MODE = False
STOPWATCH_START = None

# ============================================================
# COLORS
# ============================================================

PINK = "\033[38;5;213m"
PURPLE = "\033[38;5;141m"
RED = "\033[91m"
CYAN = "\033[96m"
WHITE = "\033[97m"
GRAY = "\033[90m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

RAINBOW = [
    196, 202, 208, 214, 220, 226,
    190, 154, 118, 82, 46, 47,
    48, 49, 51, 45, 39, 33,
    27, 63, 99, 135, 171, 207
]

ANSI_PATTERN = re.compile(r"\033\[[0-9;]*m")


def rainbow_text(text):
    text = ANSI_PATTERN.sub("", str(text))
    result = []

    offset = int(time.monotonic() * 3) % len(RAINBOW)

    for index, char in enumerate(text):
        if char in "\n\r":
            result.append(char)
            continue

        color = RAINBOW[(index + offset) % len(RAINBOW)]
        result.append(f"\033[38;5;{color}m{char}")

    return "".join(result) + RESET


def output(*args, **kwargs):
    if RAINBOW_MODE:
        sep = kwargs.get("sep", " ")
        end = kwargs.get("end", "\n")
        flush = kwargs.get("flush", False)

        message = sep.join(str(arg) for arg in args)
        sys.stdout.write(rainbow_text(message) + end)

        if flush:
            sys.stdout.flush()
    else:
        print(*args, **kwargs)


def terminal_input(prompt=""):
    if RAINBOW_MODE:
        prompt = rainbow_text(prompt)
    return input(prompt)


def clear():
    os.system("clear" if os.name != "nt" else "cls")


def line():
    output("─" * 48)


def slow(text, delay=0.012):
    for char in str(text):
        output(char, end="", flush=True)
        time.sleep(delay)
    output()


# ============================================================
# BANNER
# ============================================================

def banner():
    art = r"""
     █████╗ ██╗   ██╗██████╗ ██╗
    ██╔══██╗██║   ██║██╔══██╗██║
    ███████║██║   ██║██████╔╝██║
    ██╔══██║██║   ██║██╔══██╗██║
    ██║  ██║╚██████╔╝██║  ██║██║
    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝
    """

    # Every banner line goes through the same output engine.
    # This includes the large ASCII AURI logo.
    if RAINBOW_MODE:
        output(art)
        output("          A U R I T E R M")
        output("       COLORFUL TERMINAL ENVIRONMENT")
        output("       Version " + VERSION + " | By " + OWNER)
    else:
        output(PINK + BOLD + art + RESET)
        output(PURPLE + BOLD + "          A U R I T E R M" + RESET)
        output(CYAN + "       COLORFUL TERMINAL ENVIRONMENT" + RESET)
        output(GRAY + "       Version " + VERSION + " | By " + OWNER + RESET)

    output()


# ============================================================
# GENERAL INFORMATION
# ============================================================

def about():
    line()
    output("ABOUT AURITERM")
    output("Project:", PROJECT)
    output("Version:", VERSION)
    output("Creator:", OWNER)
    output("Platform:", platform.system())
    output("Python:", platform.python_version())
    output("Environment: Termux / Python")
    line()


def show_info():
    line()
    output("SYSTEM INFORMATION")
    output("Project:", PROJECT)
    output("Version:", VERSION)
    output("Owner:", OWNER)
    output("Python:", platform.python_version())
    output("Platform:", platform.platform())
    output("Uptime:", round(time.time() - START_TIME, 2), "seconds")
    line()


def show_modules():
    modules = [
        "AuriBot", "ColorArt", "DemonDatabase",
        "Diagnostics", "Settings", "Rainbow Engine",
        "Matrix Display", "Notes System", "Timer",
        "Stopwatch", "Text Tools", "Calculator"
    ]

    line()
    output("AURITERM MODULES")

    for module in modules:
        output("[AVAILABLE]", module)

    line()


# ============================================================
# SAFE CALCULATOR
# ============================================================

ALLOWED_NODES = (
    ast.Expression, ast.BinOp, ast.UnaryOp,
    ast.Constant, ast.Add, ast.Sub, ast.Mult,
    ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
    ast.USub, ast.UAdd, ast.Load
)


def safe_calculate(expression):
    try:
        tree = ast.parse(expression, mode="eval")

        if len(list(ast.walk(tree))) > 100:
            raise ValueError("Expression is too complex.")

        for node in ast.walk(tree):
            if not isinstance(node, ALLOWED_NODES):
                raise ValueError("Unsupported expression")

            if isinstance(node, ast.Constant):
                if not isinstance(node.value, (int, float)):
                    raise ValueError("Only numbers are allowed.")

            if isinstance(node, ast.Pow):
                pass

        result = eval(
            compile(tree, "<calculator>", "eval"),
            {"__builtins__": {}},
            {}
        )

        if isinstance(result, (int, float)) and abs(result) > 10**100:
            raise ValueError("Result is too large.")

        return result

    except Exception as error:
        return "Calculation error: " + str(error)


# ============================================================
# COLOR ART
# ============================================================

def color_art():
    clear()
    output("COLOR ART STUDIO")

    art = [
        "   ✦       .       ✦",
        "       .       .",
        "  A U R I T E R M",
        "       .       .",
        "   ✦       .       ✦"
    ]

    for row in art:
        output(row)


# ============================================================
# NOTES
# ============================================================

def load_notes():
    try:
        if NOTES_FILE.exists():
            with open(NOTES_FILE, encoding="utf-8") as file:
                data = json.load(file)
                return data if isinstance(data, list) else []
    except Exception:
        pass

    return []


def save_notes(notes):
    with open(NOTES_FILE, "w", encoding="utf-8") as file:
        json.dump(notes, file, indent=4)


def command_note(args):
    if not args:
        output("Usage: -note <text>")
        return

    notes = load_notes()
    notes.append({
        "text": " ".join(args),
        "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    save_notes(notes)
    output("Note saved!")


def command_notes():
    notes = load_notes()

    if not notes:
        output("No saved notes.")
        return

    line()
    output("SAVED NOTES")

    for index, note in enumerate(notes, 1):
        if isinstance(note, dict):
            output(str(index) + ".", note.get("text", ""))
            output("   " + note.get("created", ""))

    line()


def command_find(args):
    if not args:
        output("Usage: -find <word>")
        return

    term = " ".join(args).lower()

    matches = [
        (i, note) for i, note in enumerate(load_notes(), 1)
        if isinstance(note, dict)
        and term in note.get("text", "").lower()
    ]

    if not matches:
        output("No matching notes.")
        return

    for index, note in matches:
        output(str(index) + ".", note["text"])


# ============================================================
# DEMON DATABASE
# ============================================================

DEFAULT_DEMONS = [
    {"name": "Stereo Madness", "difficulty": "Easy"},
    {"name": "Back on Track", "difficulty": "Easy"},
    {"name": "Polargeist", "difficulty": "Normal"},
    {"name": "Dry Out", "difficulty": "Normal"},
    {"name": "Base After Base", "difficulty": "Hard"},
    {"name": "Cant Let Go", "difficulty": "Hard"},
    {"name": "Jumper", "difficulty": "Hard"},
    {"name": "Time Machine", "difficulty": "Harder"}
]


def load_demons():
    try:
        if DEMONS_FILE.exists():
            with open(DEMONS_FILE, encoding="utf-8") as file:
                data = json.load(file)

                if isinstance(data, list):
                    return data
    except Exception:
        pass

    with open(DEMONS_FILE, "w", encoding="utf-8") as file:
        json.dump(DEFAULT_DEMONS, file, indent=4)

    return DEFAULT_DEMONS


def database():
    line()
    output("DEMON DATABASE")

    for index, demon in enumerate(load_demons(), 1):
        if isinstance(demon, dict):
            output(
                str(index) + ".",
                demon.get("name", "Unknown"),
                "—",
                demon.get("difficulty", "Unknown")
            )
        else:
            output(str(index) + ".", demon)

    line()


# ============================================================
# DIAGNOSTICS AND SETTINGS
# ============================================================

def diagnostics():
    line()
    output("AURITERM DIAGNOSTICS")

    checks = {
        "Python": platform.python_version(),
        "Operating system": platform.system(),
        "Architecture": platform.machine(),
        "Project folder": str(ROOT),
        "Data folder": DATA.exists(),
        "Database folder": DATABASE.exists()
    }

    for name, value in checks.items():
        output("[OK]", name + ":", value)

    line()


def settings():
    line()
    output("AURITERM SETTINGS")

    defaults = {
        "owner": OWNER,
        "version": VERSION,
        "rainbow": RAINBOW_MODE,
        "theme": "Pink / Purple"
    }

    try:
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, encoding="utf-8") as file:
                data = json.load(file)
        else:
            data = defaults

            with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)

        output(json.dumps(data, indent=4))

    except Exception as error:
        output("Settings error:", error)

    line()


# ============================================================
# EFFECTS
# ============================================================

def corruption():
    output("SIMULATED CORRUPTION")
    output("Visual effect only. No files are damaged.")

    for _ in range(12):
        output(
            random.choice(["ERROR", "0x00", "SYSTEM", "GLITCH", "WARNING"]),
            random.randint(100, 9999)
        )
        time.sleep(0.08)

    output("Simulation completed. No damage detected.")


def matrix_effect():
    output("MATRIX DISPLAY")

    for _ in range(12):
        output("".join(random.choice("01ABCDEF") for _ in range(48)))
        time.sleep(0.06)


def project_size():
    total = 0

    for path in ROOT.rglob("*"):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue

        try:
            if path.is_file():
                total += path.stat().st_size
        except OSError:
            pass

    output("Project size:", round(total / 1024, 2), "KB")


def show_tree():
    output("AURITERM PROJECT TREE")

    count = 0

    for path in ROOT.rglob("*"):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue

        if count >= 80:
            output("More files not displayed.")
            break

        output(
            ("DIR " if path.is_dir() else "FILE ")
            + str(path.relative_to(ROOT))
        )
        count += 1


# ============================================================
# THEME
# ============================================================

def theme_menu():
    global PINK, PURPLE, CYAN, GREEN, YELLOW

    output("THEME SELECTOR")
    output("1. Pink / Purple")
    output("2. Blue")
    output("3. Green")
    output("4. Classic")

    choice = terminal_input("Choose theme: ").strip()

    if choice == "1":
        PINK, PURPLE = "\033[38;5;213m", "\033[38;5;141m"
        CYAN, GREEN, YELLOW = "\033[96m", "\033[92m", "\033[93m"

    elif choice == "2":
        PINK, PURPLE = "\033[94m", "\033[38;5;39m"
        CYAN, GREEN, YELLOW = "\033[96m", "\033[92m", "\033[93m"

    elif choice == "3":
        PINK, PURPLE = "\033[92m", "\033[38;5;40m"
        CYAN, GREEN, YELLOW = "\033[96m", "\033[92m", "\033[93m"

    elif choice == "4":
        PINK, PURPLE = "\033[97m", "\033[90m"
        CYAN, GREEN, YELLOW = "\033[96m", "\033[92m", "\033[93m"

    else:
        output("Invalid theme.")
        return

    output("Theme changed!")


# ============================================================
# 16 EXTRA COMMANDS
# ============================================================

MORSE = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..",
    "E": ".", "F": "..-.", "G": "--.", "H": "....",
    "I": "..", "J": ".---", "K": "-.-", "L": ".-..",
    "M": "--", "N": "-.", "O": "---", "P": ".--.",
    "Q": "--.-", "R": ".-.", "S": "...", "T": "-",
    "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
    "Y": "-.--", "Z": "--..",
    "0": "-----", "1": ".----", "2": "..---",
    "3": "...--", "4": "....-", "5": ".....",
    "6": "-....", "7": "--...", "8": "---..",
    "9": "----."
}

REVERSE_MORSE = {v: k for k, v in MORSE.items()}


def command_timer(args):
    if not args:
        output("Usage: -timer <seconds>")
        return

    try:
        seconds = int(args[0])

        if not 1 <= seconds <= 3600:
            output("Choose between 1 and 3600 seconds.")
            return

        output("Timer started:", seconds, "seconds")

        while seconds:
            output("Remaining:", seconds, end="\r", flush=True)
            time.sleep(1)
            seconds -= 1

        output("\nTimer finished!")

    except ValueError:
        output("Enter a valid number.")


def command_stopwatch():
    global STOPWATCH_START

    if STOPWATCH_START is None:
        STOPWATCH_START = time.time()
        output("Stopwatch started!")
    else:
        elapsed = time.time() - STOPWATCH_START
        STOPWATCH_START = None
        output("Elapsed:", round(elapsed, 2), "seconds")


def command_count(args):
    text = " ".join(args)

    output("Characters:", len(text))
    output("Words:", len(text.split()))
    output("Letters:", sum(c.isalpha() for c in text))
    output("Digits:", sum(c.isdigit() for c in text))


def command_slug(args):
    text = " ".join(args).lower()
    output(re.sub(r"[^a-z0-9]+", "-", text).strip("-") or "empty")


def command_morse(args):
    text = " ".join(args).upper()

    if not text:
        output("Usage: -morse <text>")
        return

    output(" ".join(
        "/" if char == " " else MORSE.get(char, "?")
        for char in text
    ))


def command_unmorse(args):
    if not args:
        output("Usage: -unmorse <code>")
        return

    words = " ".join(args).split(" / ")
    decoded = []

    for word in words:
        decoded.append("".join(
            REVERSE_MORSE.get(code, "?")
            for code in word.split()
        ))

    output(" ".join(decoded))


def command_progress(args):
    try:
        value = max(0, min(100, int(args[0])))
        filled = value // 5

        output(
            "[" + "█" * filled + "░" * (20 - filled) + "]",
            str(value) + "%"
        )

    except (ValueError, IndexError):
        output("Usage: -progress <0-100>")


def command_table(args):
    try:
        number = int(args[0])

        for i in range(1, 13):
            output(f"{number} × {i} = {number * i}")

    except (ValueError, IndexError):
        output("Usage: -table <number>")


def command_fact():
    facts = [
        "Octopuses have three hearts.",
        "A day on Venus is longer than its year.",
        "Bananas are berries in botanical terms.",
        "The Moon is slowly moving away from Earth.",
        "A group of flamingos is called a flamboyance.",
        "Honey can remain edible for a very long time when stored properly."
    ]

    output(random.choice(facts))


def command_coinflip():
    output(random.choice(["Heads!", "Tails!"]))


# ============================================================
# AURIBOT — 65 COMMANDS
# ============================================================

BOT_COMMANDS = """
joke quote motivate fact riddle coin dice roll choose number
color palette rainbow banner status system python platform uptime
disk folders files pwd ls whoami username weekday month year
timestamp calendar countdown add subtract multiply divide square
cube sqrt power percent convert hex binary octal reverse upper
lower title length words chars palindrome vowels consonants initials
repeat shuffle sort unique countlines encode decode hash uuid
""".split()


def bot_help():
    line()
    output("AURIBOT COMMANDS")

    for i in range(0, len(BOT_COMMANDS), 4):
        output("   ".join(BOT_COMMANDS[i:i + 4]))

    line()


def bot_command(command):
    try:
        parts = shlex.split(command)

    except ValueError as error:
        output("Parsing error:", error)
        return

    if not parts:
        return

    name = parts[0].lower()
    args = parts[1:]
    text = " ".join(args)

    jokes = [
        "Why did the computer get cold? It left its Windows open.",
        "Why did the programmer quit? Too many bugs.",
        "Why was the computer tired? Too many tabs open."
    ]

    quotes = [
        "Keep building. Keep learning.",
        "Every great project starts somewhere.",
        "Creativity is intelligence having fun."
    ]

    if name in ("help", "-help"):
        bot_help()

    elif name == "joke":
        output(random.choice(jokes))

    elif name == "quote":
        output(random.choice(quotes))

    elif name == "motivate":
        output("Keep going. Your next idea could become your best project!")

    elif name == "fact":
        command_fact()

    elif name == "riddle":
        output("What has keys but cannot open locks? A keyboard!")

    elif name in ("coin", "coinflip"):
        command_coinflip()

    elif name in ("dice", "roll"):
        output("You rolled:", random.randint(1, 6))

    elif name == "choose":
        output(random.choice(args) if args else "Usage: choose option1 option2")

    elif name == "number":
        output(random.randint(1, 100))

    elif name == "color":
        output(random.choice(["Pink", "Purple", "Blue", "Green", "Orange"]))

    elif name == "palette":
        output(" ".join(str(c) for c in RAINBOW))

    elif name == "rainbow":
        output("A U R I B O T   R A I N B O W")

    elif name == "banner":
        banner()

    elif name == "status":
        output("AuriBot is online.")

    elif name == "system":
        output(platform.platform())

    elif name == "python":
        output(platform.python_version())

    elif name == "platform":
        output(platform.system())

    elif name == "uptime":
        output(round(time.time() - START_TIME, 2), "seconds")

    elif name == "disk":
        usage = shutil.disk_usage(ROOT)
        output("Used:", round(usage.used / 1024**3, 2), "GB")
        output("Free:", round(usage.free / 1024**3, 2), "GB")

    elif name in ("folders", "files", "ls"):
        for item in os.listdir(ROOT):
            output(item)

    elif name == "pwd":
        output(ROOT)

    elif name in ("whoami", "username"):
        output(os.environ.get("USER", OWNER))

    elif name == "weekday":
        output(datetime.datetime.now().strftime("%A"))

    elif name == "month":
        output(datetime.datetime.now().strftime("%B"))

    elif name == "year":
        output(datetime.datetime.now().year)

    elif name == "timestamp":
        output(time.time())

    elif name == "calendar":
        now = datetime.datetime.now()
        output(calendar.month(now.year, now.month))

    elif name == "countdown":
        seconds = 60 - datetime.datetime.now().second

        for number in range(seconds, 0, -1):
            output(number, end="\r", flush=True)
            time.sleep(1)

        output("Time!")

    elif name in ("add", "subtract", "multiply", "divide"):
        try:
            a, b = float(args[0]), float(args[1])

            if name == "add":
                result = a + b
            elif name == "subtract":
                result = a - b
            elif name == "multiply":
                result = a * b
            else:
                result = a / b

            output(result)

        except Exception:
            output("Usage:", name, "number number")

    elif name in ("square", "cube", "sqrt"):
        try:
            n = float(args[0])

            result = (
                n ** 2 if name == "square"
                else n ** 3 if name == "cube"
                else math.sqrt(n)
            )

            output(result)

        except Exception:
            output("Usage:", name, "number")

    elif name == "power":
        try:
            output(float(args[0]) ** float(args[1]))
        except Exception:
            output("Usage: power base exponent")

    elif name == "percent":
        try:
            output(float(args[0]) / 100 * float(args[1]))
        except Exception:
            output("Usage: percent percentage number")

    elif name == "convert":
        try:
            output(float(args[0]) * 1000, "(×1000)")
        except Exception:
            output("Usage: convert number")

    elif name in ("hex", "binary", "octal"):
        try:
            n = int(args[0])

            output(
                hex(n) if name == "hex"
                else bin(n) if name == "binary"
                else oct(n)
            )

        except Exception:
            output("Usage:", name, "number")

    elif name == "reverse":
        output(text[::-1])

    elif name == "upper":
        output(text.upper())

    elif name == "lower":
        output(text.lower())

    elif name == "title":
        output(text.title())

    elif name in ("length", "chars"):
        output(len(text))

    elif name == "words":
        output(len(text.split()))

    elif name == "palindrome":
        cleaned = re.sub(r"[^a-z0-9]", "", text.lower())
        output("Yes!" if cleaned == cleaned[::-1] else "No!")

    elif name == "vowels":
        output(sum(c.lower() in "aeiou" for c in text))

    elif name == "consonants":
        output(sum(c.isalpha() and c.lower() not in "aeiou" for c in text))

    elif name == "initials":
        output("".join(w[0].upper() for w in text.split() if w))

    elif name == "repeat":
        try:
            amount = max(0, min(100, int(args[0])))
            output(" ".join(args[1:]) * amount)
        except Exception:
            output("Usage: repeat amount text")

    elif name == "shuffle":
        chars = list(text)
        random.shuffle(chars)
        output("".join(chars))

    elif name == "sort":
        output("".join(sorted(text)))

    elif name == "unique":
        output("".join(dict.fromkeys(text)))

    elif name == "countlines":
        output(len(text.splitlines()))

    elif name == "encode":
        output(base64.b64encode(text.encode()).decode())

    elif name == "decode":
        try:
            output(base64.b64decode(text.encode()).decode())
        except Exception:
            output("Invalid Base64.")

    elif name == "hash":
        output(hashlib.sha256(text.encode()).hexdigest())

    elif name == "uuid":
        output(uuid.uuid4())

    else:
        output("Unknown AuriBot command. Type help.")


def run_auribot():
    clear()
    output("AURIBOT ONLINE")
    output("Type help for commands.")
    output("Type back to return to AuriTerm.")

    while True:
        try:
            command = terminal_input("AuriBot > ").strip()

            if command.lower() in (
                "back", "exit", "quit", "-open auriterm"
            ):
                output("Returning to AuriTerm...")
                return

            if command:
                bot_command(command)

        except KeyboardInterrupt:
            output("\nReturning to AuriTerm...")
            return


# ============================================================
# HELP
# ============================================================

def help_menu():
    commands = [
        "-help",
        "-open AuriBot",
        "-open ColorArt",
        "-open DemonDatabase",
        "-open Diagnostics",
        "-open Settings",
        "-open AuriTerm",
        "-rainbow",
        "-cancel",
        "-time",
        "-date",
        "-whoami",
        "-pwd",
        "-ls",
        "-tree",
        "-size",
        "-uptime",
        "-random",
        "-quote",
        "-joke",
        "-matrix",
        "-theme",
        "-modules",
        "-refresh",
        "-info",
        "-corrupt",
        "-echo <text>",
        "-timer <seconds>",
        "-stopwatch",
        "-note <text>",
        "-notes",
        "-clear-notes",
        "-find <word>",
        "-count <text>",
        "-slug <text>",
        "-morse <text>",
        "-unmorse <code>",
        "-ascii <text>",
        "-progress <0-100>",
        "-table <number>",
        "-fact",
        "-coinflip",
        "-clear",
        "-version",
        "-about",
        "-exit",
        "quit"
    ]

    line()
    output("AURITERM COMMANDS")

    for command in commands:
        output("  " + command)

    output()
    output("-exit = standby; commands remain available.")
    output("-open AuriTerm = reopen the main terminal.")
    output("quit = close the program.")
    line()


# ============================================================
# COMMAND ROUTER
# ============================================================

def execute(command):
    global AURITERM_OPEN
    global PROGRAM_RUNNING
    global RAINBOW_MODE

    try:
        parts = shlex.split(command)

    except ValueError as error:
        output("Command parsing error:", error)
        return

    if not parts:
        return

    cmd = parts[0].lower()
    args = parts[1:]
    full = command.strip().lower()

    if full == "-help":
        help_menu()

    elif full == "-open auribot":
        run_auribot()

    elif full == "-open colorart":
        color_art()

    elif full == "-open demondatabase":
        database()

    elif full == "-open diagnostics":
        diagnostics()

    elif full == "-open settings":
        settings()

    elif full == "-open auriterm":
        AURITERM_OPEN = True
        clear()
        banner()
        output("AuriTerm reopened successfully!")

    elif full == "-rainbow":
        RAINBOW_MODE = True
        output("RAINBOW MODE ENABLED!")

    elif full == "-cancel":
        RAINBOW_MODE = False
        output(GREEN + "Rainbow mode disabled." + RESET)

    elif full == "-time":
        output(datetime.datetime.now().strftime("%H:%M:%S"))

    elif full == "-date":
        output(datetime.datetime.now().strftime("%d/%m/%Y"))

    elif full == "-whoami":
        output(os.environ.get("USER", OWNER))

    elif full == "-pwd":
        output(ROOT)

    elif full == "-ls":
        for item in os.listdir(ROOT):
            output(item)

    elif full == "-tree":
        show_tree()

    elif full == "-size":
        project_size()

    elif full == "-uptime":
        output(round(time.time() - START_TIME, 2), "seconds")

    elif full == "-random":
        output(random.randint(1, 100))

    elif full == "-quote":
        output(random.choice([
            "Keep building. Keep learning.",
            "Every project starts with an idea.",
            "Make something that makes you curious."
        ]))

    elif full == "-joke":
        output(random.choice([
            "Why did the computer get cold? It left its Windows open.",
            "Why was the computer tired? Too many tabs open.",
            "Why did the programmer quit? Too many bugs."
        ]))

    elif full == "-matrix":
        matrix_effect()

    elif full == "-theme":
        theme_menu()

    elif full == "-modules":
        show_modules()

    elif full == "-refresh":
        clear()
        banner()
        output("AuriTerm refreshed.")

    elif full == "-info":
        show_info()

    elif full == "-corrupt":
        corruption()

    elif cmd == "-echo":
        output(" ".join(args))

    elif cmd == "-timer":
        command_timer(args)

    elif cmd == "-stopwatch":
        command_stopwatch()

    elif cmd == "-note":
        command_note(args)

    elif full == "-notes":
        command_notes()

    elif full == "-clear-notes":
        save_notes([])
        output("All notes cleared.")

    elif cmd == "-find":
        command_find(args)

    elif cmd == "-count":
        command_count(args)

    elif cmd == "-slug":
        command_slug(args)

    elif cmd == "-morse":
        command_morse(args)

    elif cmd == "-unmorse":
        command_unmorse(args)

    elif cmd == "-ascii":
        text = " ".join(args)
        output(" ".join(text.upper()) if text else "Usage: -ascii <text>")

    elif cmd == "-progress":
        command_progress(args)

    elif cmd == "-table":
        command_table(args)

    elif full == "-fact":
        command_fact()

    elif full == "-coinflip":
        command_coinflip()

    elif full == "-clear":
        clear()

        if AURITERM_OPEN:
            banner()

    elif full == "-version":
        output(PROJECT, VERSION)

    elif full == "-about":
        about()

    elif full == "-exit":
        AURITERM_OPEN = False
        output("AuriTerm exited.")
        output("Standby mode: commands are still available.")
        output("Use -open AuriTerm to reopen.")
        output("Use quit to close the program.")

    elif full in ("quit", "shutdown", "close"):
        PROGRAM_RUNNING = False
        output("AuriTerm shutting down. Goodbye!")

    else:
        output("Unknown command. Type -help.")


# ============================================================
# MAIN LOOP
# ============================================================

def main():
    global PROGRAM_RUNNING

    clear()
    banner()

    slow("AuriTerm 2.1 Biscuit initialized successfully.")

    output("Type -help to view commands.")
    output("Type -exit for standby mode.")
    output("Type -open AuriTerm to reopen.")
    output("Type quit to close the program.")

    while PROGRAM_RUNNING:
        try:
            if AURITERM_OPEN:
                prompt = "\nAuriTerm > "
            else:
                prompt = "\nAuriTerm [STANDBY] > "

            command = terminal_input(prompt)
            execute(command)

        except KeyboardInterrupt:
            output("\nUse quit to close the program.")

        except EOFError:
            output("\nAuriTerm session ended.")
            break

        except Exception as error:
            output("Unexpected error:", error)

    output("AuriTerm session ended.")


if __name__ == "__main__":
    try:
        main()

    except Exception as error:
        print("Fatal error:", error)
