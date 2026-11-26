
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
from pathlib import Path

# ==========================================
# AURITERM — ALL IN ONE
# Created by Auri
# ==========================================

VERSION = "2.0.0"
OWNER = "Auri"
PROJECT = "AuriTerm"

ROOT = Path(__file__).resolve().parent
START_TIME = time.time()

PINK = "\033[95m"
PURPLE = "\033[35m"
RED = "\033[91m"
CYAN = "\033[96m"
WHITE = "\033[97m"
GRAY = "\033[90m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

# ==========================================
# BANNER — ORIGINAL AURI LOGO
# ==========================================

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


def clear():
    os.system("clear" if os.name != "nt" else "cls")


def line():
    print(GRAY + "─" * 48 + RESET)


def slow(text, delay=0.008):
    for char in str(text):
        print(char, end="", flush=True)
        time.sleep(delay)
    print()


# ==========================================
# COLOR ART
# ==========================================

def color_art():
    artworks = [
        PINK + r"""
       /\_/\
      ( o.o )
       > ^ <
       PIXEL CAT
""" + RESET,

        PURPLE + r"""
       .-.
      ( A )
       `-'
      AURI STAR
""" + RESET,

        CYAN + r"""
       .------.
      / AURI  /
     /_______/
      AURI PORTAL
""" + RESET,

        GREEN + r"""
       [ 0101 ]
       [ 1010 ]
       [ 0101 ]
       DIGITAL
""" + RESET,

        YELLOW + r"""
       .--------.
       | AURIOS |
       |  2026  |
       '--------'
       SYSTEM
""" + RESET
    ]

    print(random.choice(artworks))


# ==========================================
# ABOUT
# ==========================================

def about():
    line()
    print(PINK + BOLD + PROJECT + RESET)
    print("Version:", VERSION)
    print("Creator:", OWNER)
    print("Platform:", platform.system())
    print("Python:", platform.python_version())
    print("A colorful terminal made for Termux.")
    line()


# ==========================================
# SAFE CALCULATOR
# ==========================================

def safe_calculate(expression):
    if len(expression) > 100:
        raise ValueError("Expression too long.")

    operators = {
        ast.Add: lambda a, b: a + b,
        ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: a / b,
        ast.FloorDiv: lambda a, b: a // b,
        ast.Mod: lambda a, b: a % b,
        ast.Pow: lambda a, b: a ** b
    }

    unary = {
        ast.UAdd: lambda a: +a,
        ast.USub: lambda a: -a
    }

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant):
            if type(node.value) not in (int, float):
                raise ValueError("Numbers only.")
            return node.value

        if isinstance(node, ast.BinOp):
            op = type(node.op)

            if op not in operators:
                raise ValueError("Unsupported operator.")

            left = evaluate(node.left)
            right = evaluate(node.right)

            if op == ast.Pow and abs(right) > 12:
                raise ValueError("Exponent limit is 12.")

            result = operators[op](left, right)

            if isinstance(result, (int, float)):
                if not math.isfinite(result) or abs(result) > 10**100:
                    raise ValueError("Result too large.")

            return result

        if isinstance(node, ast.UnaryOp):
            op = type(node.op)
            if op not in unary:
                raise ValueError("Unsupported operation.")
            return unary[op](evaluate(node.operand))

        raise ValueError("Invalid expression.")

    return evaluate(ast.parse(expression, mode="eval"))


# ==========================================
# DEMON DATABASE
# ==========================================

DEFAULT_DEMONS = [
    {"id": "D-001", "name": "NULLENTITY", "type": "Unknown"},
    {"id": "D-002", "name": "PINKERROR", "type": "Glitch"},
    {"id": "D-003", "name": "VOID-16", "type": "Void"},
    {"id": "D-004", "name": "UNKNOWN", "type": "Unknown"},
    {"id": "D-005", "name": "AURI-GHOST", "type": "Ghost"},
    {"id": "D-006", "name": "REDSTATIC", "type": "Static"},
    {"id": "D-007", "name": "DREAMBYTE", "type": "Digital"},
    {"id": "D-008", "name": "KERNEL-16", "type": "System"}
]


def load_demons():
    path = ROOT / "database" / "demons.json"

    if path.exists():
        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, dict):
                data = data.get("demons", data.get("entries", []))

            if isinstance(data, list):
                return data

        except (OSError, json.JSONDecodeError):
            print(YELLOW + "Database unavailable. Using built-in entries." + RESET)

    return DEFAULT_DEMONS


def database():
    line()
    print(PINK + BOLD + "DEMON DATABASE" + RESET)

    demons = load_demons()

    for demon in demons:
        if isinstance(demon, dict):
            print(
                CYAN + str(demon.get("id", "???")) + RESET,
                "|",
                WHITE + str(demon.get("name", "UNKNOWN")) + RESET,
                "|",
                GRAY + str(demon.get("type", "Unknown")) + RESET
            )

    print("\nEntries:", len(demons))
    line()


# ==========================================
# DIAGNOSTICS
# ==========================================

def diagnostics():
    total, used, free = shutil.disk_usage(ROOT)

    print(CYAN + "AURITERM DIAGNOSTICS" + RESET)
    line()
    print("Operating system:", platform.system())
    print("Platform:", platform.platform())
    print("Python:", platform.python_version())
    print("Architecture:", platform.machine())
    print("Disk free:", round(free / (1024 ** 3), 2), "GB")
    print("Project:", PROJECT)
    print("Version:", VERSION)
    print(GREEN + "Diagnostics complete. No system changes made." + RESET)
    line()


# ==========================================
# SETTINGS
# ==========================================

def settings():
    path = ROOT / "config" / "settings.json"

    print(PINK + "AURITERM SETTINGS" + RESET)
    line()

    if path.exists():
        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            print(json.dumps(data, indent=4))
        except (OSError, json.JSONDecodeError):
            print(YELLOW + "Settings could not be read." + RESET)
    else:
        print("Theme: Pink / Purple / Cyan")
        print("Effects: Enabled")
        print("System modifications: Disabled")
        print("Visual simulations: Enabled")

    line()


# ==========================================
# VISUAL CORRUPTION
# ==========================================

def corruption():
    glitches = [
        "KERNEL_16",
        "AURI//ERROR",
        "0xAURI",
        "SYSTEM_GLITCH",
        "VOID_001",
        "PINK_STATIC",
        "NULL_POINTER",
        "SIGNAL_LOST"
    ]

    print(RED + BOLD + "VISUAL CORRUPTION SIMULATION" + RESET)

    for _ in range(12):
        print(
            random.choice([RED, PURPLE, PINK, CYAN])
            + random.choice(glitches)
            + " " + str(random.randint(100, 9999))
            + RESET
        )
        time.sleep(0.08)

    print(GREEN + "Simulation finished. No files were changed." + RESET)


# ==========================================
# AURIBOT — 65 EXTRA COMMANDS
# ==========================================

BOT_COMMANDS = {
    "joke": "Tell a joke",
    "quote": "Random quote",
    "motivate": "Motivational message",
    "fact": "Random fun fact",
    "riddle": "Give a riddle",
    "coin": "Flip a coin",
    "dice": "Roll a six-sided dice",
    "roll": "Roll a number",
    "choose": "Choose between options separated by |",
    "number": "Random number from 1 to 100",
    "color": "Show a random color",
    "palette": "Show the AuriTerm palette",
    "rainbow": "Display rainbow text",
    "banner": "Show the AuriTerm banner",
    "status": "Show AuriBot status",
    "system": "Show system information",
    "python": "Show Python version",
    "platform": "Show platform information",
    "uptime": "Show session time",
    "disk": "Show disk space",
    "folders": "List folders",
    "files": "List files",
    "pwd": "Show project directory",
    "ls": "List directory contents",
    "whoami": "Show current user",
    "username": "Show username",
    "weekday": "Show weekday",
    "month": "Show current month",
    "year": "Show current year",
    "timestamp": "Show Unix timestamp",
    "calendar": "Show this month's calendar",
    "countdown": "Short countdown",
    "add": "Add numbers",
    "subtract": "Subtract numbers",
    "multiply": "Multiply numbers",
    "divide": "Divide numbers",
    "square": "Square a number",
    "cube": "Cube a number",
    "sqrt": "Square root",
    "power": "Calculate a power",
    "percent": "Calculate a percentage",
    "convert": "Convert common units",
    "hex": "Convert number to hexadecimal",
    "binary": "Convert number to binary",
    "octal": "Convert number to octal",
    "reverse": "Reverse text",
    "upper": "Convert text to uppercase",
    "lower": "Convert text to lowercase",
    "title": "Convert text to title case",
    "length": "Count characters",
    "words": "Count words",
    "chars": "Show character count",
    "palindrome": "Check for a palindrome",
    "vowels": "Count vowels",
    "consonants": "Count consonants",
    "initials": "Get text initials",
    "repeat": "Repeat text",
    "shuffle": "Shuffle words",
    "sort": "Sort words",
    "unique": "Remove repeated words",
    "countlines": "Count lines in text",
    "encode": "Base64 encode text",
    "decode": "Base64 decode text",
    "hash": "Create SHA-256 hash",
    "uuid": "Generate a UUID"
}


def bot_help():
    print(PINK + BOLD + "AURIBOT COMMAND CENTER" + RESET)
    line()
    print(CYAN + "CORE COMMANDS" + RESET)
    print("hello, hi, hey, help, time, date, art, about, back, calc")
    line()
    print(CYAN + "65 EXTRA COMMANDS" + RESET)

    for name, description in BOT_COMMANDS.items():
        print(GREEN + name.ljust(13) + RESET + GRAY + description + RESET)

    line()
    print("Example: calc 16 * 16")
    print("Example: choose pizza | pasta")


def bot_command(command, args):
    text = " ".join(args)
    now = datetime.datetime.now()

    if command == "joke":
        print(random.choice([
            "Why did the computer get cold? It left its Windows open.",
            "Why was the keyboard tired? Too many shifts.",
            "What is a computer's favorite snack? Microchips.",
            "Why did the bug go to school? To improve its debugging."
        ]))

    elif command == "quote":
        print(random.choice([
            "Every great project starts somewhere.",
            "Keep creating. Keep experimenting.",
            "A small idea can become a big project.",
            "Curiosity is the beginning of discovery."
        ]))

    elif command == "motivate":
        print(random.choice([
            "You can build something amazing.",
            "One error doesn't define your project.",
            "Keep learning, one command at a time.",
            "Your next idea could be your best one."
        ]))

    elif command == "fact":
        print(random.choice([
            "A day on Venus is longer than its year.",
            "Octopuses have three hearts.",
            "Bananas are berries in botanical classification.",
            "The first computer mouse was made of wood."
        ]))

    elif command == "riddle":
        print("What has keys but cannot open locks?")
        print("Answer: A keyboard!")

    elif command == "coin":
        print(random.choice(["HEADS!", "TAILS!"]))

    elif command == "dice":
        print("You rolled:", random.randint(1, 6))

    elif command == "roll":
        try:
            maximum = int(args[0]) if args else 100
            maximum = max(1, min(maximum, 100000))
            print("You rolled:", random.randint(1, maximum))
        except ValueError:
            print("Usage: roll [maximum]")

    elif command == "choose":
        choices = [x.strip() for x in text.split("|") if x.strip()]
        if len(choices) >= 2:
            print("AuriBot chooses:", random.choice(choices))
        else:
            print("Usage: choose pizza | pasta")

    elif command == "number":
        print("Your number:", random.randint(1, 100))

    elif command == "color":
        name, code = random.choice([
            ("PINK", PINK), ("PURPLE", PURPLE),
            ("CYAN", CYAN), ("GREEN", GREEN),
            ("YELLOW", YELLOW)
        ])
        print(code + "Your color is " + name + RESET)

    elif command == "palette":
        print(PINK + "PINK " + PURPLE + "PURPLE " +
              CYAN + "CYAN " + GREEN + "GREEN " +
              YELLOW + "YELLOW" + RESET)

    elif command == "rainbow":
        colors = [RED, YELLOW, GREEN, CYAN, PURPLE, PINK]
        for i, char in enumerate(text or "AURITERM"):
            print(colors[i % len(colors)] + char + RESET, end="")
        print()

    elif command == "banner":
        banner()

    elif command == "status":
        print("AuriBot: ONLINE")
        print("AuriTerm:", VERSION)
        print("Extra commands:", len(BOT_COMMANDS))
        print("Session:", round(time.time() - START_TIME), "seconds")

    elif command == "system":
        print(platform.platform())

    elif command == "python":
        print("Python", platform.python_version())

    elif command == "platform":
        print("System:", platform.system())
        print("Machine:", platform.machine())
        print("Processor:", platform.processor() or "Unknown")

    elif command == "uptime":
        print("Session:", int(time.time() - START_TIME), "seconds")

    elif command == "disk":
        total, used, free = shutil.disk_usage(ROOT)
        print("Total:", round(total / 1024**3, 2), "GB")
        print("Used:", round(used / 1024**3, 2), "GB")
        print("Free:", round(free / 1024**3, 2), "GB")

    elif command in ("folders", "files", "ls"):
        try:
            items = sorted(ROOT.iterdir())
            if command == "folders":
                items = [p for p in items if p.is_dir()]
            elif command == "files":
                items = [p for p in items if p.is_file()]

            if not items:
                print("Nothing found.")

            for item in items:
                color = CYAN if item.is_dir() else WHITE
                print(color + item.name + RESET)

        except OSError as error:
            print("Directory error:", error)

    elif command == "pwd":
        print(ROOT)

    elif command in ("whoami", "username"):
        print(os.environ.get("USER", os.environ.get("USERNAME", "Auri")))

    elif command == "weekday":
        print(now.strftime("%A"))

    elif command == "month":
        print(now.strftime("%B"))

    elif command == "year":
        print(now.year)

    elif command == "timestamp":
        print(int(time.time()))

    elif command == "calendar":
        print(calendar.month(now.year, now.month))

    elif command == "countdown":
        try:
            amount = int(args[0]) if args else 5
            amount = max(1, min(amount, 30))
            for number in range(amount, 0, -1):
                print(number)
                time.sleep(1)
            print(GREEN + "GO!" + RESET)
        except ValueError:
            print("Usage: countdown [1-30]")

    elif command in ("add", "subtract", "multiply", "divide"):
        try:
            numbers = [float(x) for x in args]
            if len(numbers) < 2:
                raise ValueError

            result = numbers[0]

            for number in numbers[1:]:
                if command == "add":
                    result += number
                elif command == "subtract":
                    result -= number
                elif command == "multiply":
                    result *= number
                elif command == "divide":
                    result /= number

            print("Result:", result)

        except (ValueError, ZeroDivisionError):
            print("Usage: " + command + " 10 5")

    elif command in ("square", "cube", "sqrt"):
        try:
            number = float(args[0])

            if command == "square":
                result = number ** 2
            elif command == "cube":
                result = number ** 3
            else:
                result = math.sqrt(number)

            print("Result:", result)

        except (ValueError, IndexError):
            print("Enter a valid non-negative number for sqrt.")

    elif command == "power":
        try:
            a, b = map(float, args[:2])
            if abs(b) > 12:
                print("Exponent limit is 12.")
            else:
                print("Result:", a ** b)
        except (ValueError, IndexError, OverflowError):
            print("Usage: power 2 8")

    elif command == "percent":
        try:
            value, percentage = map(float, args[:2])
            print("Result:", value * percentage / 100)
        except (ValueError, IndexError):
            print("Usage: percent 200 15")

    elif command == "convert":
        try:
            value = float(args[0])
            unit = args[1].lower()

            conversions = {
                "c2f": (value * 9 / 5) + 32,
                "f2c": (value - 32) * 5 / 9,
                "km-mi": value * 0.621371,
                "mi-km": value / 0.621371,
                "kg-lb": value * 2.20462,
                "lb-kg": value / 2.20462
            }

            if unit not in conversions:
                print("Units: c2f, f2c, km-mi, mi-km, kg-lb, lb-kg")
            else:
                print("Result:", conversions[unit])

        except (ValueError, IndexError):
            print("Usage: convert 10 km-mi")

    elif command in ("hex", "binary", "octal"):
        try:
            number = int(args[0])
            if command == "hex":
                print(hex(number))
            elif command == "binary":
                print(bin(number))
            else:
                print(oct(number))
        except (ValueError, IndexError):
            print("Enter an integer.")

    elif command == "reverse":
        print(text[::-1])

    elif command == "upper":
        print(text.upper())

    elif command == "lower":
        print(text.lower())

    elif command == "title":
        print(text.title())

    elif command in ("length", "chars"):
        print("Characters:", len(text))

    elif command == "words":
        print("Words:", len(text.split()))

    elif command == "palindrome":
        cleaned = "".join(c.lower() for c in text if c.isalnum())
        print("Palindrome!" if cleaned == cleaned[::-1] else "Not a palindrome.")

    elif command == "vowels":
        print("Vowels:", sum(c.lower() in "aeiou" for c in text))

    elif command == "consonants":
        print("Consonants:", sum(c.isalpha() and c.lower() not in "aeiou" for c in text))

    elif command == "initials":
        print("".join(word[0].upper() for word in text.split() if word))

    elif command == "repeat":
        try:
            count = int(args[0])
            phrase = " ".join(args[1:])
            print("\n".join([phrase] * max(0, min(count, 20))))
        except (ValueError, IndexError):
            print('Usage: repeat 3 "Hello"')

    elif command == "shuffle":
        words = text.split()
        random.shuffle(words)
        print(" ".join(words))

    elif command == "sort":
        print(" ".join(sorted(args, key=str.lower)))

    elif command == "unique":
        seen = []
        for word in args:
            if word.lower() not in [x.lower() for x in seen]:
                seen.append(word)
        print(" ".join(seen))

    elif command == "countlines":
        print("Lines:", len(text.splitlines()))

    elif command == "encode":
        print(base64.b64encode(text.encode()).decode())

    elif command == "decode":
        try:
            print(base64.b64decode(text.encode(), validate=True).decode())
        except Exception:
            print("Invalid Base64 text.")

    elif command == "hash":
        print(hashlib.sha256(text.encode()).hexdigest())

    elif command == "uuid":
        print(uuid.uuid4())

    else:
        print("Unknown command.")


# ==========================================
# AURIBOT MAIN LOOP
# ==========================================

def run_auribot():
    print(PINK + BOLD + "\nAuriBot is online!" + RESET)
    print("Type help to see commands.")
    print("Type back to return to AuriTerm.")

    while True:
        try:
            raw = input(CYAN + "AuriBot > " + RESET).strip()

            if not raw:
                continue

            try:
                parts = shlex.split(raw)
            except ValueError:
                print(RED + "Invalid command formatting." + RESET)
                continue

            command = parts[0].lower()
            args = parts[1:]

            if command in ("back", "exit", "quit"):
                print(PURPLE + "AuriBot signing off!" + RESET)
                break

            elif command in ("hello", "hi", "hey"):
                print("Hello! AuriBot is ready.")

            elif command == "help":
                bot_help()

            elif command == "time":
                print(datetime.datetime.now().strftime("%H:%M:%S"))

            elif command == "date":
                print(datetime.datetime.now().strftime("%d/%m/%Y"))

            elif command == "about":
                print("AuriBot — built into AuriTerm.")
                print("Version:", VERSION)

            elif command == "art":
                color_art()

            elif command == "calc":
                try:
                    expression = " ".join(args)
                    print("Result:", safe_calculate(expression))
                except Exception as error:
                    print(RED + "Calculator error: " + str(error) + RESET)

            elif command in BOT_COMMANDS:
                bot_command(command, args)

            else:
                print(RED + "Unknown command. Type help." + RESET)

        except (KeyboardInterrupt, EOFError):
            print("\nReturning to AuriTerm.")
            break


# ==========================================
# AURITERM HELP
# ==========================================

def help_menu():
    line()
    print(PINK + BOLD + "AURITERM COMMAND CENTER" + RESET)
    line()

    commands = [
        ("-help", "Show commands"),
        ("-open AuriBot", "Launch AuriBot"),
        ("-open ColorArt", "Show ASCII art"),
        ("-open DemonDatabase", "Open Demon Database"),
        ("-open Diagnostics", "System diagnostics"),
        ("-open Settings", "Show settings"),
        ("-corrupt", "Visual corruption simulation"),
        ("-clear", "Clear terminal"),
        ("-version", "Show version"),
        ("-about", "About AuriTerm"),
        ("-exit", "Exit AuriTerm")
    ]

    for command, description in commands:
        print(CYAN + command.ljust(25) + RESET + description)

    line()


# ==========================================
# COMMAND EXECUTION
# ==========================================

def execute(command):
    command = command.strip()
    lower = command.lower()

    if lower == "-help":
        help_menu()

    elif lower == "-open auribot":
        run_auribot()

    elif lower == "-open colorart":
        color_art()

    elif lower == "-open demondatabase":
        database()

    elif lower == "-open diagnostics":
        diagnostics()

    elif lower == "-open settings":
        settings()

    elif lower == "-corrupt":
        corruption()

    elif lower == "-clear":
        clear()
        banner()

    elif lower == "-version":
        print(PROJECT, VERSION)

    elif lower == "-about":
        about()

    elif lower == "-exit":
        print(PINK + "AuriTerm shutting down. Goodbye!" + RESET)
        return False

    elif lower == "":
        pass

    else:
        print(RED + "Unknown command. Type -help." + RESET)

    return True


# ==========================================
# MAIN
# ==========================================

def main():
    clear()
    banner()

    slow(GREEN + "AuriTerm initialized successfully." + RESET)
    print("Type -help to view commands.")
    print("Type -open AuriBot to launch AuriBot.")

    running = True

    while running:
        try:
            command = input(PINK + "\nAuriTerm > " + RESET)
            running = execute(command)

        except KeyboardInterrupt:
            print("\n" + YELLOW + "Use -exit to close AuriTerm." + RESET)

        except EOFError:
            print("\nAuriTerm shutting down.")
            break

        except Exception as error:
            print(RED + "Unexpected error: " + str(error) + RESET)


if __name__ == "__main__":
    main()
