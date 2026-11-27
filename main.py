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
import re
import socket
import codecs
import py_compile
import zipfile
import statistics
import subprocess
from pathlib import Path

# ============================================================
# AURITERM 2.2 DEMONING EDITION
# COMPLETE SINGLE-FILE BUILD
# ============================================================

PROJECT = "AuriTerm"
VERSION = "2.2 Demoning Edition"
OWNER = "Auri"

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATABASE = ROOT / "database"
BACKUPS = ROOT / "backups"

for folder in (DATA, DATABASE, BACKUPS):
    folder.mkdir(parents=True, exist_ok=True)

NOTES_FILE = DATA / "notes.json"
SETTINGS_FILE = DATA / "settings.json"
TODO_FILE = DATA / "todo.json"
DEMONS_FILE = DATABASE / "demons.json"
LOG_FILE = DATA / "demoning.log"
PROFILE_FILE = DATA / "profile.json"
MOTD_FILE = DATA / "motd.txt"

START_TIME = time.time()
AURITERM_OPEN = True
PROGRAM_RUNNING = True
RAINBOW_MODE = False
STOPWATCH_START = None

DEFAULT_SETTINGS = {
    "theme": "Pink / Purple",
    "rainbow": False,
    "xp": 0
}

SETTINGS = {}

# ============================================================
# THEMES
# ============================================================

THEMES = {
    "Pink / Purple": {
        "pink": "\033[38;5;213m",
        "purple": "\033[38;5;141m",
        "cyan": "\033[96m",
        "green": "\033[92m",
        "yellow": "\033[93m"
    },
    "Blue": {
        "pink": "\033[94m",
        "purple": "\033[38;5;39m",
        "cyan": "\033[96m",
        "green": "\033[92m",
        "yellow": "\033[93m"
    },
    "Green": {
        "pink": "\033[92m",
        "purple": "\033[38;5;40m",
        "cyan": "\033[96m",
        "green": "\033[92m",
        "yellow": "\033[93m"
    },
    "Classic": {
        "pink": "\033[97m",
        "purple": "\033[90m",
        "cyan": "\033[97m",
        "green": "\033[97m",
        "yellow": "\033[97m"
    }
}

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
    196, 202, 208, 214, 220, 226, 190, 154,
    118, 82, 46, 47, 48, 49, 51, 45, 39, 33,
    27, 63, 99, 135, 171, 207
]

ANSI_PATTERN = re.compile(r"\033\[[0-9;]*m")


def load_json(path, default):
    try:
        if path.exists():
            with path.open("r", encoding="utf-8") as file:
                return json.load(file)
    except (OSError, json.JSONDecodeError):
        pass
    return default


def save_json(path, data):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        return True
    except OSError as exc:
        print("Save error:", exc)
        return False


SETTINGS = load_json(SETTINGS_FILE, DEFAULT_SETTINGS.copy())

if not isinstance(SETTINGS, dict):
    SETTINGS = DEFAULT_SETTINGS.copy()

THEME = SETTINGS.get("theme", "Pink / Purple")
if THEME not in THEMES:
    THEME = "Pink / Purple"

RAINBOW_MODE = bool(SETTINGS.get("rainbow", False))
XP = max(0, int(SETTINGS.get("xp", 0) or 0))


def apply_theme(name):
    global THEME, PINK, PURPLE, CYAN, GREEN, YELLOW

    if name not in THEMES:
        return False

    THEME = name
    colors = THEMES[name]

    PINK = colors["pink"]
    PURPLE = colors["purple"]
    CYAN = colors["cyan"]
    GREEN = colors["green"]
    YELLOW = colors["yellow"]

    SETTINGS["theme"] = THEME
    save_json(SETTINGS_FILE, SETTINGS)
    return True


apply_theme(THEME)


def save_progress():
    SETTINGS["xp"] = XP
    SETTINGS["theme"] = THEME
    SETTINGS["rainbow"] = RAINBOW_MODE
    save_json(SETTINGS_FILE, SETTINGS)


def add_xp(amount):
    global XP
    XP += max(0, int(amount))
    save_progress()


# ============================================================
# TERMINAL DISPLAY
# ============================================================

def rainbow_at(text, offset=0):
    text = ANSI_PATTERN.sub("", str(text))
    result = []

    for index, char in enumerate(text):
        if char in "\r\n":
            result.append(char)
        else:
            color = RAINBOW[(index + offset) % len(RAINBOW)]
            result.append(f"\033[38;5;{color}m{char}")

    return "".join(result) + RESET


def rainbow_text(text):
    return rainbow_at(text, int(time.monotonic() * 3))


def output(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    end = kwargs.get("end", "\n")
    flush = kwargs.get("flush", False)

    message = sep.join(str(item) for item in args)

    if RAINBOW_MODE:
        message = rainbow_text(message)

    sys.stdout.write(message + end)

    if flush:
        sys.stdout.flush()


def terminal_input(prompt=""):
    if RAINBOW_MODE:
        prompt = rainbow_text(prompt)
    return input(prompt)


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def line():
    output("─" * 52)


def slow(text, delay=0.004):
    for char in str(text):
        output(char, end="", flush=True)
        time.sleep(delay)
    output()


def normalize_command(command):
    """Normalize pasted prompts, whitespace and BOM characters."""
    command = str(command).replace("\ufeff", "").strip()

    if command.lower().startswith("auriterm >"):
        command = command.split(">", 1)[1].strip()

    if command.lower().startswith("auriterm [standby] >"):
        command = command.split(">", 1)[1].strip()

    return command


def banner():
    art = r"""
     █████╗ ██╗   ██╗██████╗ ██╗
    ██╔══██╗██║   ██║██╔══██╗██║
    ███████║██║   ██║██████╔╝██║
    ██╔══██║██║   ██║██╔══██╗██║
    ██║  ██║╚██████╔╝██║  ██║██║
    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝
    """

    output(PINK + BOLD + art + RESET)
    output(PURPLE + BOLD + "          A U R I T E R M" + RESET)
    output(CYAN + "       COLORFUL TERMINAL ENVIRONMENT" + RESET)
    output(GRAY + f"       Version {VERSION} | By {OWNER}" + RESET)
    output()


# ============================================================
# GENERAL TOOLS
# ============================================================

def safe_calculate(expression):
    allowed = (
        ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv,
        ast.Mod, ast.Pow, ast.USub, ast.UAdd, ast.Load
    )

    try:
        tree = ast.parse(expression, mode="eval")
        nodes = list(ast.walk(tree))

        if len(nodes) > 100:
            raise ValueError("Expression too complex.")

        for node in nodes:
            if not isinstance(node, allowed):
                raise ValueError("Unsupported expression.")

            if isinstance(node, ast.Constant):
                if not isinstance(node.value, (int, float)):
                    raise ValueError("Numbers only.")

            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
                if not isinstance(node.right, ast.Constant):
                    raise ValueError("Use a simple exponent.")

                if abs(node.right.value) > 100:
                    raise ValueError("Exponent too large.")

        result = eval(
            compile(tree, "<calculator>", "eval"),
            {"__builtins__": {}},
            {}
        )

        if isinstance(result, complex):
            raise ValueError("Complex results are unsupported.")

        if isinstance(result, float) and not math.isfinite(result):
            raise ValueError("Invalid result.")

        if abs(result) > 10**100:
            raise ValueError("Result too large.")

        return result

    except Exception as exc:
        return "Calculation error: " + str(exc)


def show_info():
    output("SYSTEM INFORMATION")
    output("Project:", PROJECT)
    output("Version:", VERSION)
    output("Owner:", OWNER)
    output("Python:", platform.python_version())
    output("Platform:", platform.platform())
    output("Uptime:", round(time.time() - START_TIME, 2), "seconds")
    output("Theme:", THEME)
    output("XP:", XP)


def about():
    line()
    output("ABOUT AURITERM")
    output(PROJECT, VERSION, OWNER)
    output("Python:", platform.python_version())
    line()


def diagnostics():
    output("AURITERM DIAGNOSTICS")

    checks = {
        "Python": platform.python_version(),
        "OS": platform.system(),
        "Architecture": platform.machine(),
        "Project folder": ROOT.exists(),
        "Data folder": DATA.exists(),
        "Database folder": DATABASE.exists(),
        "Backup folder": BACKUPS.exists(),
        "Settings file": SETTINGS_FILE.exists()
    }

    for name, value in checks.items():
        output("[OK]", name + ":", value)


def show_modules():
    modules = [
        "AuriBot", "ColorArt", "DemonDatabase", "Diagnostics",
        "Settings", "Rainbow Engine", "Matrix Display", "Notes",
        "Timer", "Stopwatch", "Text Tools", "Calculator",
        "DEMONING", "Games", "Backup System", "Todo",
        "Profile", "MOTD", "Export Tools"
    ]

    for item in modules:
        output("[AVAILABLE]", item)


def color_art():
    clear()

    for row in [
        "   ✦       .       ✦",
        "       .       .",
        "  A U R I T E R M",
        "       .       .",
        "   ✦       .       ✦"
    ]:
        output(PINK + row + RESET)


def matrix_effect():
    output("MATRIX DISPLAY")

    for _ in range(15):
        output("".join(random.choice("01ABCDEF") for _ in range(48)))
        time.sleep(0.04)


def corruption():
    output("SIMULATED CORRUPTION — visual only.")

    for _ in range(12):
        output(
            random.choice(["ERROR", "0x00", "SYSTEM", "GLITCH", "WARNING"]),
            random.randint(100, 9999)
        )
        time.sleep(0.05)

    output("Simulation completed. No files damaged.")


def project_size():
    total = 0

    for path in ROOT.rglob("*"):
        if any(part in path.parts for part in (
            ".git", "__pycache__", "backups"
        )):
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
        if any(part in path.parts for part in (
            ".git", "__pycache__", "backups"
        )):
            continue

        if count >= 100:
            output("More files not displayed.")
            break

        kind = "DIR " if path.is_dir() else "FILE "
        output(kind + str(path.relative_to(ROOT)))
        count += 1


# ============================================================
# THEME SYSTEM — FIXED AND PERSISTENT
# ============================================================

def theme_menu():
    output()
    output("AURITERM THEME SELECTOR")
    line()

    choices = list(THEMES.keys())

    for index, name in enumerate(choices, 1):
        output(f"{index}. {name}")

    output("0. Cancel")
    line()
    output("Current theme:", THEME)

    choice = terminal_input("Choose theme: ").strip().lower()

    if choice in ("0", "cancel", "back", "exit"):
        output("Theme selection cancelled.")
        return

    if choice.isdigit():
        number = int(choice)

        if 1 <= number <= len(choices):
            selected = choices[number - 1]
        else:
            output("Invalid theme number.")
            return
    else:
        selected = next(
            (name for name in choices if name.lower() == choice),
            None
        )

    if selected is None:
        output("Unknown theme.")
        return

    apply_theme(selected)
    output(PINK + BOLD + "THEME CHANGED: " + selected + RESET)
    output("Your theme will remain saved after restarting AuriTerm.")


# ============================================================
# NOTES
# ============================================================

def load_notes():
    notes = load_json(NOTES_FILE, [])
    return notes if isinstance(notes, list) else []


def command_note(args):
    if not args:
        output("Usage: -note <text>")
        return

    notes = load_notes()

    notes.append({
        "text": " ".join(args),
        "created": datetime.datetime.now().isoformat(timespec="seconds")
    })

    save_json(NOTES_FILE, notes)
    output("Note saved!")


def command_notes():
    notes = load_notes()

    if not notes:
        output("No saved notes.")
        return

    for index, note in enumerate(notes, 1):
        if isinstance(note, dict):
            output(f"{index}. {note.get('text', '')} [{note.get('created', '')}]")


def command_find(args):
    term = " ".join(args).lower()

    if not term:
        output("Usage: -find <word>")
        return

    found = [
        note for note in load_notes()
        if isinstance(note, dict)
        and term in str(note.get("text", "")).lower()
    ]

    if not found:
        output("No matching notes.")
        return

    for index, note in enumerate(found, 1):
        output(f"{index}. {note.get('text', '')}")


# ============================================================
# DEMON DATABASE
# ============================================================

DEFAULT_DEMONS = [
    {"name": "Stereo Madness", "difficulty": "Easy"},
    {"name": "Back on Track", "difficulty": "Easy"},
    {"name": "Polargeist", "difficulty": "Normal"},
    {"name": "Dry Out", "difficulty": "Normal"},
    {"name": "Base After Base", "difficulty": "Hard"},
    {"name": "Can't Let Go", "difficulty": "Hard"},
    {"name": "Jumper", "difficulty": "Hard"},
    {"name": "Time Machine", "difficulty": "Harder"}
]


def database():
    demons = load_json(DEMONS_FILE, DEFAULT_DEMONS)

    if not isinstance(demons, list):
        demons = DEFAULT_DEMONS

    save_json(DEMONS_FILE, demons)

    line()
    output("DEMON DATABASE")

    for index, demon in enumerate(demons, 1):
        if isinstance(demon, dict):
            output(
                f"{index}. {demon.get('name', 'Unknown')} — "
                f"{demon.get('difficulty', 'Unknown')}"
            )
        else:
            output(f"{index}. {demon}")

    line()


# ============================================================
# TIME AND TEXT TOOLS
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

REVERSE_MORSE = {value: key for key, value in MORSE.items()}


def command_timer(args):
    try:
        seconds = int(args[0])

        if not 1 <= seconds <= 3600:
            raise ValueError

        for remaining in range(seconds, 0, -1):
            output("Remaining:", remaining, end="\r", flush=True)
            time.sleep(1)

        output("\nTimer finished!")

    except (ValueError, IndexError):
        output("Usage: -timer <1-3600 seconds>")


def command_stopwatch():
    global STOPWATCH_START

    if STOPWATCH_START is None:
        STOPWATCH_START = time.time()
        output("Stopwatch started.")
    else:
        output("Elapsed:", round(time.time() - STOPWATCH_START, 2), "seconds")
        STOPWATCH_START = None


def command_count(args):
    text = " ".join(args)

    output(
        "Characters:", len(text),
        "| Words:", len(text.split()),
        "| Letters:", sum(char.isalpha() for char in text),
        "| Digits:", sum(char.isdigit() for char in text)
    )


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
        decoded.append(
            "".join(REVERSE_MORSE.get(code, "?") for code in word.split())
        )

    output(" ".join(decoded))


def command_progress(args):
    try:
        number = max(0, min(100, int(args[0])))
        filled = number // 5

        output(
            "[" + "█" * filled + "░" * (20 - filled) + "]",
            f"{number}%"
        )

    except (ValueError, IndexError):
        output("Usage: -progress <0-100>")


def command_table(args):
    try:
        number = int(args[0])

        for index in range(1, 13):
            output(f"{number} × {index} = {number * index}")

    except (ValueError, IndexError):
        output("Usage: -table <number>")


def command_fact():
    output(random.choice([
        "Octopuses have three hearts.",
        "A day on Venus is longer than its year.",
        "Bananas are berries in botanical terms.",
        "The Moon is slowly moving away from Earth.",
        "A group of flamingos is called a flamboyance."
    ]))


def command_coinflip():
    output(random.choice(["Heads!", "Tails!"]))


# ============================================================
# AURIBOT
# ============================================================

BOT_COMMANDS = """
joke quote motivate fact riddle coin dice roll choose number color
palette rainbow banner status system python platform uptime disk
folders files pwd ls whoami username weekday month year timestamp
calendar countdown add subtract multiply divide square cube sqrt
power percent convert hex binary octal reverse upper lower title
length words chars palindrome vowels consonants initials repeat
shuffle sort unique countlines encode decode hash uuid
""".split()


def bot_help():
    line()
    output("AURIBOT COMMANDS")

    for index in range(0, len(BOT_COMMANDS), 4):
        output("   ".join(BOT_COMMANDS[index:index + 4]))

    line()


def bot_command(command):
    try:
        parts = shlex.split(command)
    except ValueError as exc:
        output("Parsing error:", exc)
        return

    if not parts:
        return

    name = parts[0].lower()
    args = parts[1:]
    text = " ".join(args)

    if name in ("help", "-help"):
        bot_help()

    elif name == "joke":
        output(random.choice([
            "Why did the computer get cold? It left its Windows open.",
            "Why did the programmer quit? Too many bugs."
        ]))

    elif name == "quote":
        output(random.choice([
            "Keep building. Keep learning.",
            "Every great project starts somewhere.",
            "Creativity is intelligence having fun."
        ]))

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

    elif name in ("color", "palette", "rainbow"):
        output(random.choice(["Pink", "Purple", "Blue", "Green", "Orange"]))

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
        for item in ROOT.iterdir():
            output(item.name)

    elif name == "pwd":
        output(ROOT)

    elif name in ("whoami", "username"):
        output(os.environ.get("USER", OWNER))

    elif name in ("weekday", "month", "year", "timestamp", "calendar"):
        now = datetime.datetime.now()

        values = {
            "weekday": now.strftime("%A"),
            "month": now.strftime("%B"),
            "year": now.year,
            "timestamp": time.time(),
            "calendar": calendar.month(now.year, now.month)
        }

        output(values[name])

    elif name == "countdown":
        for number in range(10, 0, -1):
            output(number, end="\r", flush=True)
            time.sleep(1)

        output("Time!")

    elif name in ("add", "subtract", "multiply", "divide"):
        try:
            a = float(args[0])
            b = float(args[1])

            results = {
                "add": a + b,
                "subtract": a - b,
                "multiply": a * b,
                "divide": a / b
            }

            output(results[name])

        except Exception:
            output("Usage:", name, "number number")

    elif name in ("square", "cube", "sqrt"):
        try:
            number = float(args[0])

            if name == "sqrt" and number < 0:
                raise ValueError("Cannot square-root a negative number.")

            result = (
                number * number if name == "square"
                else number ** 3 if name == "cube"
                else math.sqrt(number)
            )

            output(result)

        except Exception as exc:
            output("Calculation error:", exc)

    elif name == "power":
        if len(args) >= 2:
            output(safe_calculate(args[0] + "**" + args[1]))
        else:
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
            number = int(args[0])

            result = (
                hex(number) if name == "hex"
                else bin(number) if name == "binary"
                else oct(number)
            )

            output(result)

        except Exception:
            output("Usage:", name, "number")

    elif name in ("reverse", "upper", "lower", "title"):
        results = {
            "reverse": text[::-1],
            "upper": text.upper(),
            "lower": text.lower(),
            "title": text.title()
        }

        output(results[name])

    elif name in ("length", "chars"):
        output(len(text))

    elif name == "words":
        output(len(text.split()))

    elif name == "palindrome":
        sample = re.sub(r"[^a-z0-9]", "", text.lower())
        output("Yes!" if sample == sample[::-1] else "No!")

    elif name == "vowels":
        output(sum(char.lower() in "aeiou" for char in text))

    elif name == "consonants":
        output(sum(
            char.isalpha() and char.lower() not in "aeiou"
            for char in text
        ))

    elif name == "initials":
        output("".join(word[0].upper() for word in text.split() if word))

    elif name == "repeat":
        try:
            count = max(0, min(100, int(args[0])))
            output((" ".join(args[1:]) + " ") * count)
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
            output(base64.b64decode(text, validate=True).decode())
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
    output("AURIBOT ONLINE — type help; back returns.")

    while True:
        try:
            command = terminal_input("AuriBot > ").strip()

            if command.lower() in ("back", "exit", "quit"):
                return

            if command:
                bot_command(command)

        except (KeyboardInterrupt, EOFError):
            return


# ============================================================
# DEMONING — EXACTLY 76 COMMANDS
# ============================================================

DEMONING_ART = r"""
DDDDDDDDDDDD        EEEEEEEEEEEE        MMMMM       MMMMM
DDDDDDDDDDDDDD      EEEEEEEEEEEE        MMMMMM     MMMMMM
DDD         DDD     EEE                 MMM MMM   MMM MMM
DDD          DDD    EEE                 MMM  MMM MMM  MMM
DDD          DDD    EEEEEEEEE           MMM   MMMMM   MMM
DDD          DDD    EEEEEEEEE           MMM    MMM    MMM
DDD         DDD     EEE                 MMM           MMM
DDDDDDDDDDDDDD      EEEEEEEEEEEE        MMM           MMM
DDDDDDDDDDDD        EEEEEEEEEEEE        MMM           MMM

NNNNN       NNN     IIIIIIIIIIII        NNNN       NNN       GGGGGGGGGG
NNNNNN      NNN         III              NNNN      NNN      GGGGGGGGGGGG
NNNNNNN     NNN         III              NNNNN     NNN     GGGG
NNN NNNN    NNN         III              NNN NNN   NNN     GGGG   GGGGG
NNN  NNNN   NNN         III              NNN  NNN  NNN     GGGG   GGGGGG
NNN   NNNN  NNN         III              NNN   NNN NNN     GGGG      GGG
NNN    NNNN NNN         III              NNN    NNNNNN      GGGG     GGG
NNN     NNNNNNN         III              NNN     NNNNN       GGGGGGGGGGG
NNN      NNNNNN     IIIIIIIIIIII         NNN      NNNN        GGGGGGGGGG
"""


def dprint(*args):
    print(rainbow_text(" ".join(str(item) for item in args)))


def dinput(prompt="DEMONING > "):
    return input(rainbow_text(prompt))


def demoning_banner():
    for frame in range(8):
        clear()
        print(rainbow_at(DEMONING_ART, frame * 3))
        print(rainbow_at("             D E M O N I N G", frame * 3))
        print(rainbow_at("        LOCAL SECURITY & SYSTEM TOOLS", frame * 3))
        time.sleep(0.07)

    clear()
    print(rainbow_text(DEMONING_ART))
    print(rainbow_text("             D E M O N I N G"))
    print(rainbow_text("        LOCAL SECURITY & SYSTEM TOOLS\n"))


DEMONING_COMMANDS = [
    "phone info", "phone battery", "phone storage", "phone files",
    "phone flashlight", "phone vibrate", "phone apps", "phone brightness",
    "phone wifi", "scan", "audit", "password", "hash", "cipher", "vault",
    "integrity", "network", "firewall", "sandbox", "monitor", "logs",
    "forensic", "encode", "generator", "challenge", "sysinfo", "cpu",
    "memory", "diskcheck", "processes", "environment", "permissions",
    "uptime", "temperature", "diagnostics", "phone camera",
    "phone settings", "phone date", "phone time", "phone clipboard",
    "phone notification", "phone volume", "phone rotation",
    "phone display", "phone decime", "base64", "hex", "binary",
    "rot13", "checksum", "compare", "metadata", "json", "xml",
    "regex", "python", "piplist", "modules", "compile", "syntax",
    "benchmark", "uuid", "timestamp", "converter", "calculator",
    "overdrive", "glitch", "rainbow", "theme", "rank", "xp",
    "achievements", "leaderboard", "secrets", "history", "report"
]

assert len(DEMONING_COMMANDS) == 76


def demon_help():
    line()
    dprint("DEMONING COMMAND INDEX — 76 COMMANDS")

    for index, command in enumerate(DEMONING_COMMANDS, 1):
        dprint(f"{index:02}. {command}")

    line()
    dprint("Type exit/back to return to AuriTerm.")


def log_event(message):
    try:
        with LOG_FILE.open("a", encoding="utf-8") as file:
            file.write(
                datetime.datetime.now().isoformat()
                + " | " + str(message) + "\n"
            )
    except OSError:
        pass


def local_system_report():
    return {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "hostname": socket.gethostname(),
        "uptime_seconds": round(time.time() - START_TIME, 2)
    }


def file_hash(path):
    digest = hashlib.sha256()

    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            digest.update(chunk)

    return digest.hexdigest()


def phone_api(feature):
    dprint("Optional Android feature:", feature)
    dprint("Requires Termux:API app and the termux-api package.")
    dprint("This command does not change Android settings automatically.")


def demoning_command(command):
    global XP

    command = normalize_command(command)

    try:
        parts = shlex.split(command)
    except ValueError as exc:
        dprint("Parsing error:", exc)
        return

    if not parts:
        return

    two_word = " ".join(parts[:2]).lower() if len(parts) >= 2 else ""

    multi = {item for item in DEMONING_COMMANDS if " " in item}

    if two_word in multi:
        name = two_word
        args = parts[2:]
    else:
        name = parts[0].lower().lstrip("-")
        args = parts[1:]

    value = " ".join(args)

    XP += 1
    save_progress()
    log_event(command)

    # PHONE COMMANDS
    if name.startswith("phone "):
        feature = name[6:]

        if feature == "info":
            dprint("Device:", platform.platform())
            dprint("Host:", socket.gethostname())
            dprint("Python:", platform.python_version())

        elif feature == "storage":
            usage = shutil.disk_usage(ROOT)
            dprint("Total:", round(usage.total / 1024**3, 2), "GB")
            dprint("Used:", round(usage.used / 1024**3, 2), "GB")
            dprint("Free:", round(usage.free / 1024**3, 2), "GB")

        elif feature == "files":
            for item in ROOT.iterdir():
                dprint(("DIR " if item.is_dir() else "FILE "), item.name)

        elif feature == "date":
            dprint(datetime.datetime.now().strftime("%d/%m/%Y"))

        elif feature == "time":
            dprint(datetime.datetime.now().strftime("%H:%M:%S"))

        elif feature == "wifi":
            try:
                dprint("Local IP:", socket.gethostbyname(socket.gethostname()))
            except OSError:
                dprint("Local IP unavailable.")

        elif feature == "apps":
            dprint("Use Android Settings to view installed apps.")

        elif feature == "settings":
            dprint("Open Android Settings manually.")

        elif feature == "rotation":
            dprint("Use Android Quick Settings to change rotation.")

        elif feature == "display":
            dprint(platform.system(), platform.machine())

        elif feature == "decime":
            for index in range(5):
                dprint("✦" * (index + 1), "DEMONING")
                time.sleep(0.1)

        else:
            phone_api(feature)

    elif name == "scan":
        dprint("LOCAL PROJECT CHECK")

        for path in ROOT.iterdir():
            dprint("FOUND:", path.name)

        dprint("Only this project folder is checked.")

    elif name == "audit":
        for label, path in [
            ("Data", DATA),
            ("Database", DATABASE),
            ("Backups", BACKUPS)
        ]:
            dprint(
                label,
                "exists:", path.exists(),
                "writable:", os.access(path, os.W_OK)
            )

    elif name == "password":
        if not value:
            dprint("Usage: password <sample text>")
        else:
            score = sum([
                len(value) >= 12,
                any(char.islower() for char in value),
                any(char.isupper() for char in value),
                any(char.isdigit() for char in value),
                any(not char.isalnum() for char in value)
            ])

            dprint("Length:", len(value))
            dprint("Strength estimate:", score, "/ 5")
            dprint("Do not enter a real password here.")

    elif name in ("hash", "checksum"):
        dprint(
            hashlib.sha256(value.encode()).hexdigest()
            if value else "Usage: " + name + " <text>"
        )

    elif name == "cipher":
        dprint(
            "ROT13:",
            codecs.encode(value, "rot_13")
            if value else "Usage: cipher <text>"
        )
        dprint("ROT13 is not secure encryption.")

    elif name == "vault":
        vault = DATA / "demo_vault.txt"

        if value:
            vault.write_text(value, encoding="utf-8")
            dprint("Demo text saved locally.")
        elif vault.exists():
            dprint(vault.read_text(encoding="utf-8"))
        else:
            dprint("Usage: vault <text>")

    elif name == "integrity":
        target = ROOT / "main.py"
        dprint(
            "SHA256:",
            file_hash(target) if target.exists() else "main.py not found."
        )

    elif name == "network":
        dprint("Hostname:", socket.gethostname())

        try:
            dprint("Local IP:", socket.gethostbyname(socket.gethostname()))
        except OSError:
            dprint("Local IP unavailable.")

        dprint("No remote hosts are scanned.")

    elif name == "firewall":
        dprint("Check your device security settings for firewall status.")

    elif name == "sandbox":
        dprint("Safe math-only sandbox.")

        if value:
            dprint(safe_calculate(value))

    elif name == "monitor":
        dprint("Processor:", platform.processor() or "Not reported")
        dprint("Uptime:", round(time.time() - START_TIME, 2), "seconds")
        dprint("For accurate RAM usage, check Android Settings.")

    elif name in ("logs", "history"):
        entries = (
            LOG_FILE.read_text(encoding="utf-8").splitlines()
            if LOG_FILE.exists() else []
        )

        for entry in entries[-20:]:
            dprint(entry)

        if not entries:
            dprint("No log entries yet.")

    elif name == "forensic":
        if not value:
            dprint("Usage: forensic <filename in project root>")
        else:
            target = (ROOT / value).resolve()

            if target.parent != ROOT.resolve() or not target.is_file():
                dprint("Only files directly inside the project folder are allowed.")
            else:
                stat = target.stat()
                dprint("Name:", target.name)
                dprint("Size:", stat.st_size, "bytes")
                dprint("Modified:", datetime.datetime.fromtimestamp(stat.st_mtime))
                dprint("SHA256:", file_hash(target))

    elif name == "encode":
        dprint(base64.b64encode(value.encode()).decode())

    elif name == "generator":
        dprint("Generated token:", uuid.uuid4())

    elif name == "challenge":
        a = random.randint(2, 20)
        b = random.randint(2, 20)

        dprint("Solve:", a, "+", b)

        try:
            if dinput("Answer: ").strip() == str(a + b):
                add_xp(10)
                dprint("Correct! +10 XP")
            else:
                dprint("Answer:", a + b)

        except (KeyboardInterrupt, EOFError):
            dprint("Challenge cancelled.")

    elif name in ("sysinfo", "report"):
        report = local_system_report()

        if name == "report":
            report.update({
                "project": PROJECT,
                "version": VERSION,
                "demoning_xp": XP
            })

            save_json(DATA / "demoning_report.json", report)
            dprint("Report saved in data/demoning_report.json")
        else:
            dprint(json.dumps(report, indent=2))

    elif name == "cpu":
        dprint("Processor:", platform.processor() or "Not reported")
        dprint("Machine:", platform.machine())

    elif name == "memory":
        dprint("Use Android Settings for accurate device RAM totals.")

    elif name == "diskcheck":
        usage = shutil.disk_usage(ROOT)

        dprint("Total:", usage.total, "bytes")
        dprint("Used:", usage.used, "bytes")
        dprint("Free:", usage.free, "bytes")

    elif name == "processes":
        dprint("Process listing is not available on all Termux devices.")

    elif name == "environment":
        dprint("Environment variable names:")

        for key in sorted(os.environ):
            dprint(key)

    elif name == "permissions":
        for path in (ROOT, DATA, DATABASE, BACKUPS):
            dprint(
                path.name,
                "read:", os.access(path, os.R_OK),
                "write:", os.access(path, os.W_OK)
            )

    elif name == "uptime":
        dprint(round(time.time() - START_TIME, 2), "seconds")

    elif name == "temperature":
        dprint("Hardware temperature is not exposed by standard Python.")

    elif name == "diagnostics":
        diagnostics()

    elif name in ("base64", "hex", "binary", "rot13"):
        if not value:
            dprint("Usage:", name, "<text>")
        elif name == "base64":
            dprint(base64.b64encode(value.encode()).decode())
        elif name == "hex":
            dprint(value.encode().hex())
        elif name == "binary":
            dprint(" ".join(format(ord(char), "08b") for char in value))
        else:
            dprint(codecs.encode(value, "rot_13"))

    elif name == "compare":
        if "|" not in value:
            dprint("Usage: compare text1 | text2")
        else:
            left, right = value.split("|", 1)
            left, right = left.strip(), right.strip()

            dprint("Identical:", left == right)
            dprint("Length difference:", abs(len(left) - len(right)))

    elif name == "metadata":
        dprint(PROJECT, VERSION)
        dprint("Owner:", OWNER)
        dprint("Python:", platform.python_version())

    elif name == "json":
        try:
            if not value:
                dprint("Usage: json <JSON text>")
            else:
                dprint(json.dumps(json.loads(value), indent=2))
        except json.JSONDecodeError as exc:
            dprint("Invalid JSON:", exc)

    elif name == "xml":
        dprint("XML parsing is not included in this standard-library build.")

    elif name == "regex":
        if "|" not in value:
            dprint("Usage: regex <pattern> | <text>")
        else:
            pattern, sample = value.split("|", 1)

            try:
                dprint(re.findall(pattern.strip(), sample))
            except re.error as exc:
                dprint("Regex error:", exc)

    elif name == "python":
        dprint("Python:", platform.python_version())
        dprint("Executable:", sys.executable)

    elif name == "piplist":
        dprint("Loaded Python modules:")

        for module in sorted(sys.modules):
            dprint(module)

    elif name == "modules":
        show_modules()

    elif name == "compile":
        target = (ROOT / value).resolve() if value else None

        if (
            not value
            or target.parent != ROOT.resolve()
            or not target.is_file()
            or target.suffix != ".py"
        ):
            dprint("Usage: compile <.py file directly inside project folder>")
        else:
            try:
                py_compile.compile(str(target), doraise=True)
                dprint("Syntax compilation successful.")
            except py_compile.PyCompileError as exc:
                dprint(exc)

    elif name == "syntax":
        try:
            if not value:
                dprint("Usage: syntax <Python code>")
            else:
                ast.parse(value, mode="exec")
                dprint("Syntax looks valid.")
        except SyntaxError as exc:
            dprint("Syntax error:", exc)

    elif name == "benchmark":
        start = time.perf_counter()
        checksum = sum(index * index for index in range(100000))

        dprint(
            "Benchmark:",
            round(time.perf_counter() - start, 5),
            "seconds | Checksum:",
            checksum
        )

    elif name == "uuid":
        dprint(uuid.uuid4())

    elif name == "timestamp":
        dprint(time.time())

    elif name == "converter":
        try:
            number = float(args[0])
            dprint("Meters to centimeters:", number * 100)
            dprint("Kilometers to meters:", number * 1000)
        except (ValueError, IndexError):
            dprint("Usage: converter <number>")

    elif name == "calculator":
        dprint(safe_calculate(value) if value else "Usage: calculator <math>")

    elif name == "overdrive":
        for index in range(8):
            dprint("OVERDRIVE", "█" * (index + 1))
            time.sleep(0.06)

    elif name == "glitch":
        for _ in range(8):
            dprint("".join(random.choice("01#@$%!?") for _ in range(35)))
            time.sleep(0.05)

    elif name == "rainbow":
        for index in range(8):
            print(rainbow_at("A U R I T E R M   D E M O N I N G", index * 3))
            time.sleep(0.1)

    elif name == "theme":
        # FIX: DEMONING THEME NOW OPENS THE REAL THEME SELECTOR.
        theme_menu()

    elif name == "rank":
        rank = (
            "DEMONING INITIATE" if XP < 50
            else "DEMONING EXPLORER" if XP < 150
            else "DEMONING MASTER" if XP < 300
            else "DEMONING LEGEND"
        )

        dprint("Current rank:", rank)

    elif name == "xp":
        dprint("XP:", XP)

    elif name == "achievements":
        dprint("[UNLOCKED] DEMONING LAUNCHED")

        if XP >= 10:
            dprint("[UNLOCKED] COMMAND EXPLORER")
        else:
            dprint("[LOCKED] COMMAND EXPLORER — Need 10 XP")

    elif name == "leaderboard":
        dprint("LOCAL LEADERBOARD")
        dprint("1. Auri —", XP, "XP")

    elif name == "secrets":
        dprint("Secret message: Keep building strange things.")

    else:
        dprint("Unknown command. Type help.")


def run_demoning():
    demoning_banner()

    dprint("DEMONING READY — 76 commands loaded.")
    dprint("Type help or -help for the index.")
    dprint("Type exit/back to return.")

    while True:
        try:
            command = normalize_command(dinput())

            normalized = command.lower().strip()

            if normalized in ("exit", "back", "quit", "return"):
                dprint("Leaving DEMONING...")
                return

            if normalized in ("-demoning", "demoning", "-demon", "demon"):
                dprint("Already inside DEMONING. Type help.")
                continue

            if normalized in ("help", "-help", "?"):
                demon_help()
            elif command:
                demoning_command(command)

        except (KeyboardInterrupt, EOFError):
            dprint("\nReturning to AuriTerm...")
            return


# ============================================================
# GAMES — FANMADE KEYBOARD
# ============================================================

def game_keyboard():
    output()
    output("             FANMADE KEYBOARD")
    output("                 ┌─────┐")
    output("                 │  W  │")
    output("   ┌─────┐ ┌─────┐ ┌─────┐")
    output("   │  A  │ │  S  │ │  D  │")
    output("   └─────┘ └─────┘ └─────┘")
    output("   WASD / arrow words = move")
    output("   Type dir quit to quit the game.")
    output()


def play_maze():
    width, height = 9, 7
    player = [1, 1]
    goal = [7, 5]

    walls = {
        (3, 1), (3, 2), (3, 3), (3, 4),
        (5, 2), (5, 3), (5, 4),
        (1, 4), (2, 4), (6, 1), (7, 1)
    }

    moves = {
        "w": (0, -1), "a": (-1, 0),
        "s": (0, 1), "d": (1, 0),
        "up": (0, -1), "left": (-1, 0),
        "down": (0, 1), "right": (1, 0)
    }

    while True:
        clear()
        output("AURITERM MAZE — Reach E, avoid #.")

        for y in range(height):
            row = ""

            for x in range(width):
                if [x, y] == player:
                    row += "@ "
                elif [x, y] == goal:
                    row += "E "
                elif (x, y) in walls:
                    row += "# "
                else:
                    row += ". "

            output(row)

        game_keyboard()

        if player == goal:
            output(GREEN + "YOU WON! +10 XP" + RESET)
            add_xp(10)
            time.sleep(1)
            return

        try:
            move = input("Game key > ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            return

        if move == "dir quit":
            output("Game closed.")
            return

        if move not in moves:
            output("Use W/A/S/D, arrow words, or dir quit.")
            time.sleep(0.6)
            continue

        dx, dy = moves[move]
        nx = player[0] + dx
        ny = player[1] + dy

        if (
            0 <= nx < width
            and 0 <= ny < height
            and (nx, ny) not in walls
        ):
            player = [nx, ny]


def play_number_game():
    target = random.randint(1, 30)
    tries = 0

    while True:
        clear()
        output("NUMBER GUESS — Pick a number from 1 to 30.")
        game_keyboard()

        guess = input("Your guess (or dir quit) > ").strip().lower()

        if guess == "dir quit":
            return

        try:
            number = int(guess)

            if not 1 <= number <= 30:
                output("Choose a number from 1 to 30.")
                time.sleep(0.6)
                continue

            tries += 1

            if number == target:
                output("CORRECT! Attempts:", tries, "| +5 XP")
                add_xp(5)
                time.sleep(1.2)
                return

            output("Higher!" if number < target else "Lower!")
            time.sleep(0.6)

        except ValueError:
            output("Enter a number or dir quit.")
            time.sleep(0.6)


def games_menu():
    while True:
        clear()
        output(PINK + BOLD + "AURITERM GAMES" + RESET)
        line()
        output("1. Maze Runner — WASD")
        output("2. Number Guess")
        output("3. Back")
        line()

        choice = input("games > ").strip().lower()

        if choice in ("1", "maze"):
            play_maze()

        elif choice in ("2", "guess"):
            play_number_game()

        elif choice in ("3", "back", "exit", "dir quit"):
            return

        else:
            output("Unknown game.")
            time.sleep(0.5)


# ============================================================
# TODO / BACKUPS / JSON
# ============================================================

def todo_add(args):
    if not args:
        output("Usage: -todo <task>")
        return

    tasks = load_json(TODO_FILE, [])

    if not isinstance(tasks, list):
        tasks = []

    tasks.append({
        "task": " ".join(args),
        "done": False
    })

    save_json(TODO_FILE, tasks)
    output("Task added!")


def todo_list():
    tasks = load_json(TODO_FILE, [])

    if not isinstance(tasks, list) or not tasks:
        output("No tasks.")
        return

    for index, task in enumerate(tasks, 1):
        if isinstance(task, dict):
            mark = "✓" if task.get("done") else " "
            output(f"{index}. [{mark}] {task.get('task', '')}")


def backup_project():
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    destination = BACKUPS / f"auriterm_backup_{stamp}.zip"

    try:
        with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in ROOT.rglob("*"):
                if not path.is_file():
                    continue

                if any(part in path.parts for part in (
                    ".git", "__pycache__", "backups"
                )):
                    continue

                archive.write(path, path.relative_to(ROOT))

        output("Backup created:", destination.name)

    except OSError as exc:
        output("Backup failed:", exc)


def restore_backup():
    backups = sorted(BACKUPS.glob("*.zip"), reverse=True)

    if not backups:
        output("No backups found.")
        return

    for index, path in enumerate(backups, 1):
        output(index, path.name)

    choice = terminal_input("Backup number (or cancel): ").strip()

    if choice.lower() == "cancel":
        return

    try:
        selected = backups[int(choice) - 1]
        root_resolved = ROOT.resolve()

        with zipfile.ZipFile(selected) as archive:
            for member in archive.infolist():
                dest = (ROOT / member.filename).resolve()

                if dest != root_resolved and root_resolved not in dest.parents:
                    output("Unsafe archive path rejected.")
                    return

                # Reject symbolic-link archive entries.
                mode = member.external_attr >> 16

                if (mode & 0o170000) == 0o120000:
                    output("Symbolic link in archive rejected.")
                    return

            archive.extractall(ROOT)

        output("Backup restored.")

    except (
        ValueError, IndexError, OSError, zipfile.BadZipFile
    ) as exc:
        output("Restore failed:", exc)


def json_tool(args):
    text = " ".join(args)

    try:
        if not text:
            output("Usage: -json <JSON text>")
        else:
            output(json.dumps(json.loads(text), indent=4))
    except json.JSONDecodeError as exc:
        output("Invalid JSON:", exc)


def calc_tool(args):
    output(
        safe_calculate(" ".join(args))
        if args else "Usage: -calc <math>"
    )


def search_tool(args):
    if not args:
        output("Usage: -search <filename fragment>")
        return

    term = " ".join(args).lower()
    found = 0

    for path in ROOT.rglob("*"):
        if any(part in path.parts for part in (
            ".git", "__pycache__", "backups"
        )):
            continue

        if term in path.name.lower():
            output(path.relative_to(ROOT))
            found += 1

    output("Matches:", found)


def version_info():
    output(PROJECT, VERSION, "| Owner:", OWNER)
    output("Python:", platform.python_version())
    output("Platform:", platform.platform())


# ============================================================
# 12 NEW MAIN COMMANDS
# ============================================================

def command_profile():
    profile = load_json(PROFILE_FILE, {
        "owner": OWNER,
        "nickname": "Auri",
        "project": PROJECT
    })

    output("AURITERM USER PROFILE")
    output(json.dumps(profile, indent=4))


def command_motd():
    if MOTD_FILE.exists():
        output(MOTD_FILE.read_text(encoding="utf-8"))
    else:
        output("Welcome to AuriTerm!")
        output("Keep creating. Keep experimenting. Keep building.")


def command_dice(args):
    try:
        sides = int(args[0]) if args else 6

        if not 2 <= sides <= 1000:
            raise ValueError

        output("You rolled:", random.randint(1, sides))

    except ValueError:
        output("Usage: -dice [sides, 2-1000]")


def command_flip():
    output(random.choice(["Heads!", "Tails!"]))


def command_choose(args):
    if not args:
        output("Usage: -choose option1 option2 option3")
        return

    output("Selected:", random.choice(args))


def command_base64(args):
    text = " ".join(args)

    if not text:
        output("Usage: -base64 <text>")
        return

    output(base64.b64encode(text.encode()).decode())


def command_unbase64(args):
    text = " ".join(args)

    if not text:
        output("Usage: -unbase64 <encoded text>")
        return

    try:
        output(base64.b64decode(text, validate=True).decode("utf-8"))
    except Exception:
        output("Invalid Base64 input.")


def command_sha256(args):
    text = " ".join(args)

    if not text:
        output("Usage: -sha256 <text>")
        return

    output(hashlib.sha256(text.encode()).hexdigest())


def command_countdown():
    try:
        seconds = int(terminal_input("Countdown seconds (1-300): "))

        if not 1 <= seconds <= 300:
            raise ValueError

        for number in range(seconds, 0, -1):
            output(f"{number}...", end="\r", flush=True)
            time.sleep(1)

        output("\nCOUNTDOWN FINISHED!")

    except ValueError:
        output("Enter a number from 1 to 300.")


def command_weatherhelp():
    output("WEATHER HELP")
    output("AuriTerm does not currently fetch live weather.")
    output("Use a weather app or browser for current forecasts.")


def command_exportnotes():
    notes = load_notes()
    destination = DATA / "notes_export.txt"

    try:
        with destination.open("w", encoding="utf-8") as file:
            for index, note in enumerate(notes, 1):
                if isinstance(note, dict):
                    file.write(
                        f"{index}. {note.get('text', '')}\n"
                        f"   {note.get('created', '')}\n\n"
                    )

        output("Notes exported to:", destination.relative_to(ROOT))

    except OSError as exc:
        output("Export failed:", exc)


def command_resetxp():
    global XP

    confirm = terminal_input("Reset all DEMONING XP? Type YES: ").strip()

    if confirm == "YES":
        XP = 0
        save_progress()
        output("XP reset to 0.")
    else:
        output("Cancelled.")


# ============================================================
# MAIN COMMAND INDEX
# ============================================================

MAIN_COMMANDS = [
    "-help",
    "-open AuriBot",
    "-open ColorArt",
    "-open DemonDatabase",
    "-open Diagnostics",
    "-open Settings",
    "-open AuriTerm",
    "-demoning",
    "games / -games",
    "-clock",
    "-calendar",
    "-todo <task>",
    "-todo list",
    "-backup",
    "-restore",
    "-json <text>",
    "-calc <math>",
    "-search <filename>",
    "-versioninfo",
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
    "quit",
    "-profile",
    "-motd",
    "-dice [sides]",
    "-flip",
    "-choose <options>",
    "-base64 <text>",
    "-unbase64 <text>",
    "-sha256 <text>",
    "-countdown",
    "-weatherhelp",
    "-exportnotes",
    "-resetxp"
]


def help_menu():
    line()
    output(PINK + BOLD + "AURITERM COMMANDS" + RESET)

    for command in MAIN_COMMANDS:
        output("  " + command)

    output()
    output("DEMONING: -demoning (76 commands; type help inside)")
    output("GAMES: games or -games")
    output("Inside a game, type dir quit to leave.")
    output("-exit = standby | -open AuriTerm = reopen | quit = close")
    line()


# ============================================================
# COMMAND EXECUTION
# ============================================================

def execute(command):
    global AURITERM_OPEN, PROGRAM_RUNNING, RAINBOW_MODE

    command = normalize_command(command)

    try:
        parts = shlex.split(command)
    except ValueError as exc:
        output("Command parsing error:", exc)
        return

    if not parts:
        return

    cmd = parts[0].lower()
    args = parts[1:]
    full = command.lower().strip()

    # MAIN HELP
    if full in ("-help", "help"):
        help_menu()

    # DEMONING LAUNCH — accepts aliases and pasted prompt text.
    elif cmd.lstrip("-") in ("demoning", "demon"):
        run_demoning()

    # GAMES
    elif full in ("games", "-games"):
        games_menu()

    # ORIGINAL COMMANDS
    elif full == "-clock":
        output(datetime.datetime.now().strftime("%H:%M:%S"))

    elif full == "-calendar":
        now = datetime.datetime.now()
        output(calendar.month(now.year, now.month))

    elif cmd == "-todo" and args and args[0].lower() == "list":
        todo_list()

    elif cmd == "-todo":
        todo_add(args)

    elif full == "-backup":
        backup_project()

    elif full == "-restore":
        restore_backup()

    elif cmd == "-json":
        json_tool(args)

    elif cmd == "-calc":
        calc_tool(args)

    elif cmd == "-search":
        search_tool(args)

    elif full == "-versioninfo":
        version_info()

    # OPEN COMMANDS
    elif full == "-open auribot":
        run_auribot()

    elif full == "-open colorart":
        color_art()

    elif full == "-open demondatabase":
        database()

    elif full == "-open diagnostics":
        diagnostics()

    elif full == "-open settings":
        settings = load_json(SETTINGS_FILE, DEFAULT_SETTINGS)
        output(json.dumps(settings, indent=4))

    elif full == "-open auriterm":
        AURITERM_OPEN = True
        clear()
        banner()
        output("AuriTerm reopened successfully!")

    # RAINBOW
    elif full == "-rainbow":
        RAINBOW_MODE = True
        save_progress()
        output("RAINBOW MODE ENABLED!")

    elif full == "-cancel":
        RAINBOW_MODE = False
        save_progress()
        output(GREEN + "Rainbow mode disabled." + RESET)

    # BASIC INFO
    elif full in ("-time", "-date"):
        output(datetime.datetime.now().strftime(
            "%H:%M:%S" if full == "-time" else "%d/%m/%Y"
        ))

    elif full == "-whoami":
        output(os.environ.get("USER", OWNER))

    elif full == "-pwd":
        output(ROOT)

    elif full == "-ls":
        for item in ROOT.iterdir():
            output(item.name)

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

    # TEXT
    elif cmd == "-echo":
        output(" ".join(args))

    elif cmd == "-timer":
        command_timer(args)

    elif full == "-stopwatch":
        command_stopwatch()

    elif cmd == "-note":
        command_note(args)

    elif full == "-notes":
        command_notes()

    elif full == "-clear-notes":
        save_json(NOTES_FILE, [])
        output("All notes cleared.")

    elif cmd == "-find":
        command_find(args)

    elif cmd == "-count":
        command_count(args)

    elif cmd == "-slug":
        output(
            re.sub(
                r"[^a-z0-9]+",
                "-",
                " ".join(args).lower()
            ).strip("-") or "empty"
        )

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

    # 12 NEW COMMANDS
    elif full == "-profile":
        command_profile()

    elif full == "-motd":
        command_motd()

    elif cmd == "-dice":
        command_dice(args)

    elif full == "-flip":
        command_flip()

    elif cmd == "-choose":
        command_choose(args)

    elif cmd == "-base64":
        command_base64(args)

    elif cmd == "-unbase64":
        command_unbase64(args)

    elif cmd == "-sha256":
        command_sha256(args)

    elif full == "-countdown":
        command_countdown()

    elif full == "-weatherhelp":
        command_weatherhelp()

    elif full == "-exportnotes":
        command_exportnotes()

    elif full == "-resetxp":
        command_resetxp()

    # STANDBY / EXIT
    elif full == "-exit":
        AURITERM_OPEN = False
        output("AuriTerm entered standby.")
        output("Use -open AuriTerm to reopen; quit to close.")

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

    slow("AuriTerm 2.2 Demoning Edition initialized successfully.")

    output("Type -help for commands.")
    output("Type -demoning to launch DEMONING.")
    output("Type games to play.")
    output("Type -exit for standby mode | quit to close.")
    output()

    while PROGRAM_RUNNING:
        try:
            prompt = (
                "\nAuriTerm > "
                if AURITERM_OPEN
                else "\nAuriTerm [STANDBY] > "
            )

            command = terminal_input(prompt)
            execute(command)

        except KeyboardInterrupt:
            output("\nUse quit to close the program.")

        except EOFError:
            output("\nAuriTerm session ended.")
            break

        except Exception as exc:
            output("Unexpected error:", type(exc).__name__, exc)

    save_progress()
    output("AuriTerm session ended.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("Fatal error:", error)