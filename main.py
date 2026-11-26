# ============================================================
# AuriTerm 2.1 Biscuit
# A colorful terminal environment for Termux
# Created by Auri
# ============================================================

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

# -------------------- CONFIGURATION --------------------

VERSION = "2.1 Biscuit"
OWNER = "Auri"
PROJECT = "AuriTerm"

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

# -------------------- COLORS --------------------

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

RAINBOW_COLORS = [
    "\033[38;5;196m",
    "\033[38;5;202m",
    "\033[38;5;226m",
    "\033[38;5;46m",
    "\033[38;5;51m",
    "\033[38;5;93m",
    "\033[38;5;201m"
]

ORIGINAL_PRINT = print


def rainbow_text(text):
    result = ""
    for i, char in enumerate(str(text)):
        result += RAINBOW_COLORS[i % len(RAINBOW_COLORS)] + char
    return result + RESET


def output(*args, **kwargs):
    text = " ".join(str(x) for x in args)

    if RAINBOW_MODE:
        ORIGINAL_PRINT(rainbow_text(text), **kwargs)
    else:
        ORIGINAL_PRINT(*args, **kwargs)


# -------------------- BASIC FUNCTIONS --------------------

def clear():
    os.system("clear" if os.name != "nt" else "cls")


def line():
    output(PURPLE + "─" * 48 + RESET)


def slow(text, delay=0.012):
    for char in str(text):
        output(char, end="", flush=True)
        time.sleep(delay)
    output()


def banner():
    output(PINK + BOLD + r"""
     █████╗ ██╗   ██╗██████╗ ██╗
    ██╔══██╗██║   ██║██╔══██╗██║
    ███████║██║   ██║██████╔╝██║
    ██╔══██║██║   ██║██╔══██╗██║
    ██║  ██║╚██████╔╝██║  ██║██║
    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝
    """ + RESET)

    output(PURPLE + BOLD + "          A U R I T E R M" + RESET)
    output(CYAN + "       COLORFUL TERMINAL ENVIRONMENT" + RESET)
    output(GRAY + "       Version " + VERSION + " | By " + OWNER + RESET)
    output()


def about():
    line()
    output(PINK + BOLD + "ABOUT AURITERM" + RESET)
    output("Project:       " + PROJECT)
    output("Version:       " + VERSION)
    output("Creator:       " + OWNER)
    output("Platform:      " + platform.system())
    output("Python:        " + platform.python_version())
    output("Environment:   Termux / Python")
    output("Purpose:       A colorful terminal experience")
    line()


def color_art():
    clear()
    output(PINK + BOLD + "COLOR ART STUDIO" + RESET)
    output()
    art = [
        "   ✦       .       ✦",
        "       .       .",
        "  A U R I T E R M",
        "       .       .",
        "   ✦       .       ✦"
    ]

    for row in art:
        output(rainbow_text(row) if RAINBOW_MODE else CYAN + row + RESET)

    output()


# -------------------- SAFE CALCULATOR --------------------

ALLOWED_NODES = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Constant,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Pow,
    ast.USub,
    ast.UAdd,
    ast.Load,
    ast.Tuple
)


def safe_calculate(expression):
    try:
        tree = ast.parse(expression, mode="eval")

        for node in ast.walk(tree):
            if not isinstance(node, ALLOWED_NODES):
                raise ValueError("Unsupported expression")

        result = eval(
            compile(tree, "<calculator>", "eval"),
            {"__builtins__": {}},
            {}
        )

        return result

    except Exception as error:
        return "Calculation error: " + str(error)


# -------------------- NOTES SYSTEM --------------------

def load_notes():
    try:
        if NOTES_FILE.exists():
            with open(NOTES_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data if isinstance(data, list) else []
    except Exception:
        pass

    return []


def save_notes(notes):
    with open(NOTES_FILE, "w", encoding="utf-8") as file:
        json.dump(notes, file, indent=4)


# -------------------- DEMON DATABASE --------------------

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
            with open(DEMONS_FILE, "r", encoding="utf-8") as file:
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
    output(PINK + BOLD + "DEMON DATABASE" + RESET)

    demons = load_demons()

    for index, demon in enumerate(demons, 1):
        if isinstance(demon, dict):
            name = demon.get("name", "Unknown")
            difficulty = demon.get("difficulty", "Unknown")
            output(f"{index}. {name} — {difficulty}")
        else:
            output(f"{index}. {demon}")

    line()


# -------------------- DIAGNOSTICS --------------------

def diagnostics():
    line()
    output(CYAN + BOLD + "AURITERM DIAGNOSTICS" + RESET)

    checks = {
        "Python": platform.python_version(),
        "Operating system": platform.system(),
        "Architecture": platform.machine(),
        "Current folder": str(ROOT),
        "Data folder": "Available" if DATA.exists() else "Missing",
        "Database folder": "Available" if DATABASE.exists() else "Missing",
        "Notes file": "Available" if NOTES_FILE.exists() else "Not created yet",
        "Settings file": "Available" if SETTINGS_FILE.exists() else "Not created yet"
    }

    for name, value in checks.items():
        output(GREEN + "[OK] " + RESET + name + ": " + str(value))

    line()


# -------------------- SETTINGS --------------------

def settings():
    line()
    output(PINK + BOLD + "AURITERM SETTINGS" + RESET)

    try:
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
        else:
            data = {
                "owner": OWNER,
                "version": VERSION,
                "rainbow": False,
                "theme": "Pink / Purple"
            }

            with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)

        output(json.dumps(data, indent=4))

    except Exception as error:
        output(RED + "Settings error: " + str(error) + RESET)

    line()


# -------------------- CORRUPTION SIMULATION --------------------

def corruption():
    output(RED + BOLD + "SIMULATED CORRUPTION EFFECT" + RESET)
    output(YELLOW + "This is only a visual effect. No files are being damaged." + RESET)

    for _ in range(12):
        output(
            random.choice(["ERROR", "0x00", "SYSTEM", "GLITCH", "???", "WARNING"]),
            random.choice(["###", "!!!", "///", "???", "000"]),
            random.randint(100, 9999)
        )
        time.sleep(0.08)

    output(GREEN + "Simulation completed. No damage detected." + RESET)


# -------------------- MATRIX EFFECT --------------------

def matrix_effect():
    output(GREEN + BOLD + "MATRIX DISPLAY" + RESET)

    for _ in range(12):
        output("".join(random.choice("01ABCDEF") for _ in range(48)))
        time.sleep(0.06)


# -------------------- TREE / SIZE / MODULES --------------------

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

    output("Project size: " + str(round(total / 1024, 2)) + " KB")


def show_tree():
    output(PINK + BOLD + "AURITERM PROJECT TREE" + RESET)

    count = 0

    for path in ROOT.rglob("*"):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue

        if count >= 80:
            output(GRAY + "... more files not displayed" + RESET)
            break

        relative = path.relative_to(ROOT)
        prefix = "📁 " if path.is_dir() else "📄 "
        output(prefix + str(relative))
        count += 1


def show_modules():
    modules = [
        "AuriBot",
        "ColorArt",
        "DemonDatabase",
        "Diagnostics",
        "Settings",
        "Rainbow Engine",
        "Matrix Display",
        "Notes System",
        "Timer",
        "Stopwatch",
        "Text Tools",
        "Calculator"
    ]

    line()
    output(PINK + BOLD + "AURITERM MODULES" + RESET)

    for module in modules:
        output(GREEN + "[AVAILABLE] " + RESET + module)

    line()


def show_info():
    line()
    output(PINK + BOLD + "SYSTEM INFORMATION" + RESET)
    output("Project: " + PROJECT)
    output("Version: " + VERSION)
    output("Owner: " + OWNER)
    output("Python: " + platform.python_version())
    output("Platform: " + platform.platform())
    output("Uptime: " + str(round(time.time() - START_TIME, 2)) + " seconds")
    line()


# -------------------- THEME MENU --------------------

def theme_menu():
    global PINK, PURPLE, CYAN, GREEN, YELLOW

    output(PINK + BOLD + "THEME SELECTOR" + RESET)
    output("1. Pink / Purple")
    output("2. Blue")
    output("3. Green")
    output("4. Classic")

    choice = input("Choose theme: ").strip()

    if choice == "1":
        PINK = "\033[38;5;213m"
        PURPLE = "\033[38;5;141m"
        CYAN = "\033[96m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"

    elif choice == "2":
        PINK = "\033[94m"
        PURPLE = "\033[38;5;39m"
        CYAN = "\033[96m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"

    elif choice == "3":
        PINK = "\033[92m"
        PURPLE = "\033[38;5;40m"
        CYAN = "\033[96m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"

    elif choice == "4":
        PINK = "\033[97m"
        PURPLE = "\033[90m"
        CYAN = "\033[96m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"

    else:
        output(RED + "Invalid theme." + RESET)
        return

    output(GREEN + "Theme changed!" + RESET)


# -------------------- 16 NEW COMMANDS --------------------

MORSE_CODE = {
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

REVERSE_MORSE = {value: key for key, value in MORSE_CODE.items()}


def command_echo(args):
    output(" ".join(args))


def command_timer(args):
    if not args:
        output("Usage: -timer <seconds>")
        return

    try:
        seconds = int(args[0])

        if seconds < 1 or seconds > 3600:
            output("Choose a time between 1 and 3600 seconds.")
            return

        output(YELLOW + f"Timer started: {seconds} seconds." + RESET)

        while seconds > 0:
            output(f"Remaining: {seconds} seconds", end="\r", flush=True)
            time.sleep(1)
            seconds -= 1

        output()
        output(GREEN + BOLD + "Timer finished!" + RESET)

    except ValueError:
        output(RED + "Enter a valid number of seconds." + RESET)


def command_stopwatch():
    global STOPWATCH_START

    if STOPWATCH_START is None:
        STOPWATCH_START = time.time()
        output(GREEN + "Stopwatch started!" + RESET)
    else:
        elapsed = time.time() - STOPWATCH_START
        STOPWATCH_START = None
        output(CYAN + f"Stopwatch stopped: {elapsed:.2f} seconds." + RESET)


def command_note(args):
    if not args:
        output("Usage: -note <your note>")
        return

    notes = load_notes()

    notes.append({
        "text": " ".join(args),
        "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    save_notes(notes)
    output(GREEN + "Note saved!" + RESET)


def command_notes():
    notes = load_notes()

    if not notes:
        output(YELLOW + "No saved notes." + RESET)
        return

    line()
    output(PINK + BOLD + "SAVED NOTES" + RESET)

    for index, note in enumerate(notes, 1):
        output(f"{index}. {note.get('text', '')}")
        output(GRAY + "   " + note.get("created", "") + RESET)

    line()


def command_clear_notes():
    save_notes([])
    output(GREEN + "All notes cleared." + RESET)


def command_find(args):
    if not args:
        output("Usage: -find <word>")
        return

    term = " ".join(args).lower()
    matches = []

    for index, note in enumerate(load_notes(), 1):
        if term in note.get("text", "").lower():
            matches.append((index, note))

    if not matches:
        output(YELLOW + "No matching notes found." + RESET)
        return

    for index, note in matches:
        output(f"{index}. {note.get('text', '')}")


def command_count(args):
    text = " ".join(args)

    output("Characters: " + str(len(text)))
    output("Words: " + str(len(text.split())))
    output("Letters: " + str(sum(char.isalpha() for char in text)))
    output("Digits: " + str(sum(char.isdigit() for char in text)))


def command_slug(args):
    text = " ".join(args).lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")

    output(text or "empty")


def command_morse(args):
    text = " ".join(args).upper()

    if not text:
        output("Usage: -morse <text>")
        return

    encoded = []

    for char in text:
        if char == " ":
            encoded.append("/")
        elif char in MORSE_CODE:
            encoded.append(MORSE_CODE[char])
        else:
            encoded.append("?")

    output(" ".join(encoded))


def command_unmorse(args):
    if not args:
        output("Usage: -unmorse <morse code>")
        return

    text = " ".join(args)
    words = text.split(" / ")
    decoded_words = []

    for word in words:
        letters = []

        for code in word.split():
            letters.append(REVERSE_MORSE.get(code, "?"))

        decoded_words.append("".join(letters))

    output(" ".join(decoded_words))


def command_ascii(args):
    text = " ".join(args)

    if not text:
        output("Usage: -ascii <text>")
        return

    output(" ".join(text.upper()))


def command_progress(args):
    if not args:
        output("Usage: -progress <0-100>")
        return

    try:
        value = max(0, min(100, int(args[0])))
        filled = value // 5
        bar = "█" * filled + "░" * (20 - filled)

        output(f"[{bar}] {value}%")

    except ValueError:
        output("Enter a number between 0 and 100.")


def command_table(args):
    if not args:
        output("Usage: -table <number>")
        return

    try:
        number = int(args[0])

        for i in range(1, 13):
            output(f"{number} × {i} = {number * i}")

    except ValueError:
        output("Enter a valid number.")


def command_fact():
    facts = [
        "Octopuses have three hearts.",
        "A day on Venus is longer than its year.",
        "Bananas are berries in botanical terms.",
        "The Moon is slowly moving away from Earth.",
        "Some turtles can breathe through specialized tissue near their tails.",
        "A group of flamingos is called a flamboyance.",
        "Honey can remain edible for a very long time when stored properly.",
        "The shortest war in recorded history lasted less than an hour."
    ]

    output(random.choice(facts))


def command_coinflip():
    output(random.choice(["Heads!", "Tails!"]))


# -------------------- AURIBOT --------------------

BOT_COMMANDS = [
    "joke", "quote", "motivate", "fact", "riddle",
    "coin", "dice", "roll", "choose", "number",
    "color", "palette", "rainbow", "banner", "status",
    "system", "python", "platform", "uptime", "disk",
    "folders", "files", "pwd", "ls", "whoami",
    "username", "weekday", "month", "year", "timestamp",
    "calendar", "countdown", "add", "subtract", "multiply",
    "divide", "square", "cube", "sqrt", "power",
    "percent", "convert", "hex", "binary", "octal",
    "reverse", "upper", "lower", "title", "length",
    "words", "chars", "palindrome", "vowels", "consonants",
    "initials", "repeat", "shuffle", "sort", "unique",
    "countlines", "encode", "decode", "hash", "uuid"
]


def bot_help():
    line()
    output(PINK + BOLD + "AURIBOT COMMANDS" + RESET)

    for index, command in enumerate(BOT_COMMANDS, 1):
        output(f"{command:<15}", end="")
        if index % 4 == 0:
            output()

    output()
    line()


def bot_command(command):
    parts = shlex.split(command)
    if not parts:
        return

    name = parts[0].lower()
    args = parts[1:]
    text = " ".join(args)

    jokes = [
        "Why did the computer get cold? It left its Windows open.",
        "There are 10 types of people: those who understand binary and those who don't.",
        "Why did the programmer quit? Too many bugs."
    ]

    quotes = [
        "Keep building. Keep learning.",
        "Every great project starts somewhere.",
        "Creativity is intelligence having fun."
    ]

    riddles = [
        ("What has keys but cannot open locks?", "A keyboard"),
        ("What has a face and two hands but no arms?", "A clock"),
        ("What gets wetter as it dries?", "A towel")
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
        question, answer = random.choice(riddles)
        output(question)
        output("Answer: " + answer)

    elif name in ("coin", "coinflip"):
        command_coinflip()

    elif name in ("dice", "roll"):
        output("You rolled: " + str(random.randint(1, 6)))

    elif name == "choose":
        if len(args) < 2:
            output("Usage: choose option1 option2 ...")
        else:
            output(random.choice(args))

    elif name == "number":
        output("Random number: " + str(random.randint(1, 100)))

    elif name == "color":
        output("Random color: " + random.choice([
            "Pink", "Purple", "Blue", "Green",
            "Orange", "Red", "Cyan", "Yellow"
        ]))

    elif name == "palette":
        output(" ".join(RAINBOW_COLORS) + RESET)

    elif name == "rainbow":
        output(rainbow_text("A U R I B O T   R A I N B O W"))

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
        output(str(round(time.time() - START_TIME, 2)) + " seconds")

    elif name == "disk":
        usage = shutil.disk_usage(ROOT)
        output(f"Used: {round(usage.used / (1024 ** 3), 2)} GB")
        output(f"Free: {round(usage.free / (1024 ** 3), 2)} GB")

    elif name in ("folders", "files", "ls"):
        for item in os.listdir(ROOT):
            output(item)

    elif name == "pwd":
        output(str(ROOT))

    elif name in ("whoami", "username"):
        output(os.environ.get("USER", os.environ.get("USERNAME", OWNER)))

    elif name == "weekday":
        output(datetime.datetime.now().strftime("%A"))

    elif name == "month":
        output(datetime.datetime.now().strftime("%B"))

    elif name == "year":
        output(str(datetime.datetime.now().year))

    elif name == "timestamp":
        output(str(time.time()))

    elif name == "calendar":
        now = datetime.datetime.now()
        output(calendar.month(now.year, now.month))

    elif name == "countdown":
        output("Countdown to the next minute:")
        seconds = 60 - datetime.datetime.now().second

        for number in range(seconds, 0, -1):
            output(str(number), end="\r", flush=True)
            time.sleep(1)

        output("Time!" + " " * 10)

    elif name in ("add", "subtract", "multiply", "divide"):
        try:
            a = float(args[0])
            b = float(args[1])

            if name == "add":
                result = a + b
            elif name == "subtract":
                result = a - b
            elif name == "multiply":
                result = a * b
            else:
                result = a / b

            output(str(result))

        except Exception:
            output("Usage: " + name + " number number")

    elif name in ("square", "cube", "sqrt"):
        try:
            number = float(args[0])

            if name == "square":
                result = number ** 2
            elif name == "cube":
                result = number ** 3
            else:
                result = math.sqrt(number)

            output(str(result))

        except Exception:
            output("Usage: " + name + " number")

    elif name == "power":
        try:
            output(str(float(args[0]) ** float(args[1])))
        except Exception:
            output("Usage: power base exponent")

    elif name == "percent":
        try:
            output(str(float(args[0]) / 100 * float(args[1])))
        except Exception:
            output("Usage: percent percentage number")

    elif name == "convert":
        try:
            output(str(float(args[0]) * 1000) + " (×1000)")
        except Exception:
            output("Usage: convert number")

    elif name == "hex":
        try:
            output(hex(int(args[0])))
        except Exception:
            output("Usage: hex number")

    elif name == "binary":
        try:
            output(bin(int(args[0])))
        except Exception:
            output("Usage: binary number")

    elif name == "octal":
        try:
            output(oct(int(args[0])))
        except Exception:
            output("Usage: octal number")

    elif name == "reverse":
        output(text[::-1])

    elif name == "upper":
        output(text.upper())

    elif name == "lower":
        output(text.lower())

    elif name == "title":
        output(text.title())

    elif name == "length":
        output(str(len(text)))

    elif name == "words":
        output(str(len(text.split())))

    elif name == "chars":
        output(str(len(text)))

    elif name == "palindrome":
        cleaned = re.sub(r"[^a-z0-9]", "", text.lower())
        output("Yes!" if cleaned == cleaned[::-1] else "No!")

    elif name == "vowels":
        output(str(sum(char.lower() in "aeiou" for char in text)))

    elif name == "consonants":
        output(str(sum(char.isalpha() and char.lower() not in "aeiou" for char in text)))

    elif name == "initials":
        output("".join(word[0].upper() for word in text.split() if word))

    elif name == "repeat":
        try:
            amount = int(args[0])
            output(" ".join(args[1:]) * max(0, min(amount, 100)))
        except Exception:
            output("Usage: repeat amount text")

    elif name == "shuffle":
        letters = list(text)
        random.shuffle(letters)
        output("".join(letters))

    elif name == "sort":
        output("".join(sorted(text)))

    elif name == "unique":
        output("".join(dict.fromkeys(text)))

    elif name == "countlines":
        output(str(len(text.splitlines())))

    elif name == "encode":
        output(base64.b64encode(text.encode()).decode())

    elif name == "decode":
        try:
            output(base64.b64decode(text.encode()).decode())
        except Exception:
            output("Invalid Base64 input.")

    elif name == "hash":
        output(hashlib.sha256(text.encode()).hexdigest())

    elif name == "uuid":
        output(str(uuid.uuid4()))

    else:
        output(RED + "Unknown AuriBot command. Type help." + RESET)


def run_auribot():
    clear()
    output(PINK + BOLD + "AURIBOT ONLINE" + RESET)
    output("Type help for commands.")
    output("Type back to return to AuriTerm.")
    output()

    while True:
        try:
            command = input(CYAN + "AuriBot > " + RESET).strip()

            if command.lower() in ("back", "exit", "quit", "-open auriterm"):
                output(YELLOW + "Returning to AuriTerm..." + RESET)
                return

            if command:
                bot_command(command)

        except KeyboardInterrupt:
            output("\nReturning to AuriTerm...")
            return


# -------------------- HELP MENU --------------------

def help_menu():
    line()
    output(PINK + BOLD + "AURITERM COMMANDS" + RESET)

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

    for command in commands:
        output(GREEN + "  " + command + RESET)

    output()
    output(YELLOW + "-exit = standby mode; commands remain available." + RESET)
    output(YELLOW + "-open AuriTerm = reopen the main terminal." + RESET)
    output(YELLOW + "quit = close the program completely." + RESET)
    line()


# -------------------- COMMAND EXECUTION --------------------

def execute(command):
    global AURITERM_OPEN
    global PROGRAM_RUNNING
    global RAINBOW_MODE

    try:
        parts = shlex.split(command)
    except ValueError as error:
        output(RED + "Command parsing error: " + str(error) + RESET)
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
        output(GREEN + "AuriTerm reopened successfully!" + RESET)

    elif full == "-rainbow":
        RAINBOW_MODE = True
        output(rainbow_text("RAINBOW MODE ENABLED!"))

    elif full == "-cancel":
        RAINBOW_MODE = False
        output(GREEN + "Rainbow mode disabled." + RESET)

    elif full == "-time":
        output(datetime.datetime.now().strftime("%H:%M:%S"))

    elif full == "-date":
        output(datetime.datetime.now().strftime("%d/%m/%Y"))

    elif full == "-whoami":
        output(os.environ.get("USER", os.environ.get("USERNAME", OWNER)))

    elif full == "-pwd":
        output(str(ROOT))

    elif full == "-ls":
        for item in os.listdir(ROOT):
            output(item)

    elif full == "-tree":
        show_tree()

    elif full == "-size":
        project_size()

    elif full == "-uptime":
        output(str(round(time.time() - START_TIME, 2)) + " seconds")

    elif full == "-random":
        output(str(random.randint(1, 100)))

    elif full == "-quote":
        output(random.choice([
            "Keep building. Keep learning.",
            "Every project starts with an idea.",
            "Make something that makes you curious."
        ]))

    elif full == "-joke":
        output(random.choice([
            "Why did the computer get cold? It left its Windows open.",
            "Why was the computer tired? It had too many tabs open.",
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
        output(GREEN + "AuriTerm refreshed." + RESET)

    elif full == "-info":
        show_info()

    elif full == "-corrupt":
        corruption()

    # 16 NEW COMMANDS

    elif cmd == "-echo":
        command_echo(args)

    elif cmd == "-timer":
        command_timer(args)

    elif cmd == "-stopwatch":
        command_stopwatch()

    elif cmd == "-note":
        command_note(args)

    elif cmd == "-notes":
        command_notes()

    elif cmd == "-clear-notes":
        command_clear_notes()

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
        command_ascii(args)

    elif cmd == "-progress":
        command_progress(args)

    elif cmd == "-table":
        command_table(args)

    elif cmd == "-fact":
        command_fact()

    elif cmd == "-coinflip":
        command_coinflip()

    elif full == "-clear":
        clear()
        if AURITERM_OPEN:
            banner()

    elif full == "-version":
        output(PROJECT + " " + VERSION)

    elif full == "-about":
        about()

    elif full == "-exit":
        AURITERM_OPEN = False
        output(PINK + "AuriTerm exited." + RESET)
        output(YELLOW + "Standby mode: commands are still available." + RESET)
        output("Use -open AuriTerm to reopen the terminal.")
        output("Use quit to close the program completely.")

    elif full in ("quit", "shutdown", "close"):
        PROGRAM_RUNNING = False
        output(PINK + "AuriTerm program shutting down. Goodbye!" + RESET)

    else:
        output(RED + "Unknown command. Type -help." + RESET)


# -------------------- MAIN LOOP --------------------

def main():
    global PROGRAM_RUNNING

    clear()
    banner()

    slow(GREEN + "AuriTerm 2.1 Biscuit initialized successfully." + RESET)
    output("Type -help to view commands.")
    output("Type -exit for standby mode.")
    output("Type -open AuriTerm to reopen.")
    output("Type quit to close the program.")
    output()

    while PROGRAM_RUNNING:
        try:
            if AURITERM_OPEN:
                prompt = PINK + "\nAuriTerm > " + RESET
            else:
                prompt = YELLOW + "\nAuriTerm [STANDBY] > " + RESET

            command = input(prompt)
            execute(command)

        except KeyboardInterrupt:
            output("\n" + YELLOW + "Use quit to close the program." + RESET)

        except EOFError:
            output("\nAuriTerm program shutting down.")
            break

        except Exception as error:
            output(RED + "Unexpected error: " + str(error) + RESET)

    output(GRAY + "AuriTerm session ended." + RESET)


# -------------------- START --------------------

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        ORIGINAL_PRINT(RED + "Fatal error: " + str(error) + RESET)