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
from pathlib import Path

# ============================================================
# AURITERM 2.2 DEMONING EDITION — SINGLE FILE BUILD
# ============================================================

PROJECT = "AuriTerm"
VERSION = "2.2 Demoning Edition"
OWNER = "Auri"

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATABASE = ROOT / "database"
BACKUPS = ROOT / "backups"
for folder in (DATA, DATABASE, BACKUPS):
    folder.mkdir(exist_ok=True)

NOTES_FILE = DATA / "notes.json"
SETTINGS_FILE = DATA / "settings.json"
DEMONS_FILE = DATABASE / "demons.json"
TODO_FILE = DATA / "todo.json"
LOG_FILE = DATA / "dem oning.log"
START_TIME = time.time()
AURITERM_OPEN = True
PROGRAM_RUNNING = True
RAINBOW_MODE = False
STOPWATCH_START = None
XP = 0
THEME = "Pink / Purple"

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
RAINBOW = [196,202,208,214,220,226,190,154,118,82,46,47,48,49,51,45,39,33,27,63,99,135,171,207]
ANSI_PATTERN = re.compile(r"\033\[[0-9;]*m")


def rainbow_at(text, offset):
    text = ANSI_PATTERN.sub("", str(text))
    out = []
    for i, char in enumerate(text):
        if char in "\r\n":
            out.append(char)
        else:
            out.append(f"\033[38;5;{RAINBOW[(i + offset) % len(RAINBOW)]}m{char}")
    return "".join(out) + RESET


def rainbow_text(text):
    return rainbow_at(text, int(time.monotonic() * 3))


def output(*args, **kwargs):
    sep, end = kwargs.get("sep", " "), kwargs.get("end", "\n")
    message = sep.join(str(x) for x in args)
    if RAINBOW_MODE:
        message = rainbow_text(message)
    sys.stdout.write(message + end)
    if kwargs.get("flush", False):
        sys.stdout.flush()


def terminal_input(prompt=""):
    return input(rainbow_text(prompt) if RAINBOW_MODE else prompt)


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def line():
    output("─" * 52)


def slow(text, delay=0.008):
    for char in str(text):
        output(char, end="", flush=True)
        time.sleep(delay)
    output()


def load_json(path, default):
    try:
        if path.exists():
            with path.open(encoding="utf-8") as f:
                return json.load(f)
    except (OSError, json.JSONDecodeError):
        pass
    return default


def save_json(path, data):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


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
    print(rainbow_text(" ".join(str(x) for x in args)))


def dinput(prompt="DEMONING > "):
    return input(rainbow_text(prompt))


def demoning_banner():
    # Short moving-rainbow intro, then a stable rainbow logo.
    for frame in range(12):
        clear()
        print(rainbow_at(DEMONING_ART, frame * 2))
        print(rainbow_at("             D E M O N I N G", frame * 2))
        print(rainbow_at("        LOCAL SECURITY & SYSTEM TOOLS", frame * 2))
        time.sleep(0.08)
    clear()
    print(rainbow_text(DEMONING_ART))
    print(rainbow_text("             D E M O N I N G"))
    print(rainbow_text("        LOCAL SECURITY & SYSTEM TOOLS\n"))


ALLOWED_NODES = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Add,
    ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
    ast.USub, ast.UAdd, ast.Load
)


def safe_calculate(expression):
    try:
        tree = ast.parse(expression, mode="eval")
        nodes = list(ast.walk(tree))
        if len(nodes) > 100:
            raise ValueError("Expression is too complex.")
        for node in nodes:
            if not isinstance(node, ALLOWED_NODES):
                raise ValueError("Unsupported expression.")
            if isinstance(node, ast.Constant) and not isinstance(node.value, (int, float)):
                raise ValueError("Only numbers are allowed.")
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
                if not isinstance(node.right, ast.Constant) or abs(node.right.value) > 100:
                    raise ValueError("Exponent is too large.")
        result = eval(compile(tree, "<calculator>", "eval"), {"__builtins__": {}}, {})
        if isinstance(result, complex) or (isinstance(result, float) and not math.isfinite(result)):
            raise ValueError("Invalid result.")
        if abs(result) > 10**100:
            raise ValueError("Result is too large.")
        return result
    except Exception as exc:
        return "Calculation error: " + str(exc)


def about():
    line()
    output("ABOUT AURITERM", " | ", PROJECT, VERSION, OWNER)
    output("Platform:", platform.platform())
    output("Python:", platform.python_version())
    line()


def show_info():
    output("SYSTEM INFORMATION")
    output("Project:", PROJECT, "| Version:", VERSION, "| Owner:", OWNER)
    output("Python:", platform.python_version())
    output("Platform:", platform.platform())
    output("Uptime:", round(time.time() - START_TIME, 2), "seconds")


def show_modules():
    for item in ["AuriBot", "ColorArt", "DemonDatabase", "Diagnostics",
                 "Settings", "Rainbow Engine", "Matrix Display", "Notes",
                 "Timer", "Stopwatch", "Text Tools", "Calculator",
                 "DEMONING", "Games", "Backup System", "Todo"]:
        output("[AVAILABLE]", item)


def color_art():
    clear()
    for row in ["   ✦       .       ✦", "       .       .",
                "  A U R I T E R M", "       .       .", "   ✦       .       ✦"]:
        output(row)


def load_notes():
    data = load_json(NOTES_FILE, [])
    return data if isinstance(data, list) else []


def command_note(args):
    if not args:
        output("Usage: -note <text>")
        return
    notes = load_notes()
    notes.append({"text": " ".join(args), "created": datetime.datetime.now().isoformat(timespec="seconds")})
    save_json(NOTES_FILE, notes)
    output("Note saved!")


def command_notes():
    notes = load_notes()
    if not notes:
        output("No saved notes.")
    for i, note in enumerate(notes, 1):
        if isinstance(note, dict):
            output(f"{i}. {note.get('text', '')} [{note.get('created', '')}]")


def command_find(args):
    term = " ".join(args).lower()
    if not term:
        output("Usage: -find <word>")
        return
    found = [n for n in load_notes() if isinstance(n, dict) and term in n.get("text", "").lower()]
    for i, note in enumerate(found, 1):
        output(f"{i}. {note.get('text', '')}")
    if not found:
        output("No matching notes.")


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


def database():
    demons = load_json(DEMONS_FILE, DEFAULT_DEMONS)
    if not isinstance(demons, list):
        demons = DEFAULT_DEMONS
    save_json(DEMONS_FILE, demons)
    line()
    output("DEMON DATABASE")
    for i, demon in enumerate(demons, 1):
        if isinstance(demon, dict):
            output(f"{i}. {demon.get('name', 'Unknown')} — {demon.get('difficulty', 'Unknown')}")
        else:
            output(f"{i}. {demon}")
    line()


def diagnostics():
    output("AURITERM DIAGNOSTICS")
    for name, value in {
        "Python": platform.python_version(), "OS": platform.system(),
        "Architecture": platform.machine(), "Project": ROOT,
        "Data folder": DATA.exists(), "Database folder": DATABASE.exists()
    }.items():
        output("[OK]", name + ":", value)


def settings():
    defaults = {"owner": OWNER, "version": VERSION, "rainbow": RAINBOW_MODE, "theme": THEME}
    output("AURITERM SETTINGS")
    output(json.dumps(load_json(SETTINGS_FILE, defaults), indent=4))


def corruption():
    output("SIMULATED CORRUPTION — visual only; no files are damaged.")
    for _ in range(12):
        output(random.choice(["ERROR", "0x00", "SYSTEM", "GLITCH", "WARNING"]), random.randint(100, 9999))
        time.sleep(0.06)
    output("Simulation completed. No damage detected.")


def matrix_effect():
    output("MATRIX DISPLAY")
    for _ in range(12):
        output("".join(random.choice("01ABCDEF") for _ in range(48)))
        time.sleep(0.05)


def project_size():
    total = 0
    for path in ROOT.rglob("*"):
        if any(x in path.parts for x in (".git", "__pycache__", "backups")):
            continue
        try:
            if path.is_file():
                total += path.stat().st_size
        except OSError:
            pass
    output("Project size:", round(total / 1024, 2), "KB")


def show_tree():
    output("AURITERM PROJECT TREE")
    for i, path in enumerate(ROOT.rglob("*")):
        if any(x in path.parts for x in (".git", "__pycache__", "backups")):
            continue
        if i >= 80:
            output("More files not displayed.")
            break
        output(("DIR " if path.is_dir() else "FILE ") + str(path.relative_to(ROOT)))


def theme_menu():
    global PINK, PURPLE, CYAN, GREEN, YELLOW, THEME
    output("1. Pink / Purple\n2. Blue\n3. Green\n4. Classic")
    choice = terminal_input("Choose theme: ").strip()
    themes = {
        "1": ("Pink / Purple", "\033[38;5;213m", "\033[38;5;141m"),
        "2": ("Blue", "\033[94m", "\033[38;5;39m"),
        "3": ("Green", "\033[92m", "\033[38;5;40m"),
        "4": ("Classic", "\033[97m", "\033[90m")
    }
    if choice not in themes:
        output("Invalid theme.")
        return
    THEME, PINK, PURPLE = themes[choice]
    CYAN, GREEN, YELLOW = "\033[96m", "\033[92m", "\033[93m"
    save_json(SETTINGS_FILE, {"owner": OWNER, "version": VERSION, "rainbow": RAINBOW_MODE, "theme": THEME})
    output("Theme changed:", THEME)


MORSE = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.",
    "G": "--.", "H": "....", "I": "..", "J": ".---", "K": "-.-", "L": ".-..",
    "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.",
    "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
    "Y": "-.--", "Z": "--..", "0": "-----", "1": ".----", "2": "..---",
    "3": "...--", "4": "....-", "5": ".....", "6": "-....", "7": "--...",
    "8": "---..", "9": "----."
}
REVERSE_MORSE = {v: k for k, v in MORSE.items()}


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
    output("Characters:", len(text), "| Words:", len(text.split()),
           "| Letters:", sum(c.isalpha() for c in text), "| Digits:", sum(c.isdigit() for c in text))


def command_morse(args):
    text = " ".join(args).upper()
    if not text:
        output("Usage: -morse <text>")
        return
    output(" ".join("/" if c == " " else MORSE.get(c, "?") for c in text))


def command_unmorse(args):
    if not args:
        output("Usage: -unmorse <code>")
        return
    output(" ".join("".join(REVERSE_MORSE.get(c, "?") for c in word.split())
                    for word in " ".join(args).split(" / ")))


def command_progress(args):
    try:
        n = max(0, min(100, int(args[0])))
        output("[" + "█" * (n // 5) + "░" * (20 - n // 5) + "]", f"{n}%")
    except (ValueError, IndexError):
        output("Usage: -progress <0-100>")


def command_table(args):
    try:
        n = int(args[0])
        for i in range(1, 13):
            output(f"{n} × {i} = {n*i}")
    except (ValueError, IndexError):
        output("Usage: -table <number>")


def command_fact():
    output(random.choice([
        "Octopuses have three hearts.", "A day on Venus is longer than its year.",
        "Bananas are berries in botanical terms.", "The Moon is slowly moving away from Earth.",
        "A group of flamingos is called a flamboyance."
    ]))


def command_coinflip():
    output(random.choice(["Heads!", "Tails!"]))


BOT_COMMANDS = """joke quote motivate fact riddle coin dice roll choose number color palette rainbow banner status system python platform uptime disk folders files pwd ls whoami username weekday month year timestamp calendar countdown add subtract multiply divide square cube sqrt power percent convert hex binary octal reverse upper lower title length words chars palindrome vowels consonants initials repeat shuffle sort unique countlines encode decode hash uuid""".split()


def bot_help():
    line()
    output("AURIBOT COMMANDS")
    for i in range(0, len(BOT_COMMANDS), 4):
        output("   ".join(BOT_COMMANDS[i:i+4]))
    line()


def bot_command(command):
    try:
        parts = shlex.split(command)
    except ValueError as exc:
        output("Parsing error:", exc)
        return
    if not parts:
        return
    name, args = parts[0].lower(), parts[1:]
    text = " ".join(args)
    if name in ("help", "-help"):
        bot_help()
    elif name == "joke":
        output(random.choice(["Why did the computer get cold? It left its Windows open.", "Why did the programmer quit? Too many bugs."]))
    elif name == "quote":
        output(random.choice(["Keep building. Keep learning.", "Every great project starts somewhere.", "Creativity is intelligence having fun."]))
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
        output(random.choice(["Pink", "Purple", "Blue", "Green", "Orange"]) if name == "color" else RAINBOW)
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
        u = shutil.disk_usage(ROOT)
        output("Used:", round(u.used/1024**3, 2), "GB | Free:", round(u.free/1024**3, 2), "GB")
    elif name in ("folders", "files", "ls"):
        for item in ROOT.iterdir():
            output(item.name)
    elif name == "pwd":
        output(ROOT)
    elif name in ("whoami", "username"):
        output(os.environ.get("USER", OWNER))
    elif name in ("weekday", "month", "year", "timestamp", "calendar"):
        now = datetime.datetime.now()
        output({"weekday": now.strftime("%A"), "month": now.strftime("%B"),
                "year": now.year, "timestamp": time.time(),
                "calendar": calendar.month(now.year, now.month)}[name])
    elif name == "countdown":
        for n in range(60 - datetime.datetime.now().second, 0, -1):
            output(n, end="\r", flush=True)
            time.sleep(1)
        output("Time!")
    elif name in ("add", "subtract", "multiply", "divide"):
        try:
            a, b = float(args[0]), float(args[1])
            output({"add": a+b, "subtract": a-b, "multiply": a*b,
                    "divide": a/b}[name])
        except Exception:
            output("Usage:", name, "number number")
    elif name in ("square", "cube", "sqrt"):
        try:
            n = float(args[0])
            output(n*n if name == "square" else n*n*n if name == "cube" else math.sqrt(n))
        except Exception:
            output("Usage:", name, "number")
    elif name == "power":
        output(safe_calculate(" ".join(args[:1]) + "**" + " ".join(args[1:])) if len(args) >= 2 else "Usage: power base exponent")
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
            output(hex(n) if name == "hex" else bin(n) if name == "binary" else oct(n))
        except Exception:
            output("Usage:", name, "number")
    elif name in ("reverse", "upper", "lower", "title"):
        output({"reverse": text[::-1], "upper": text.upper(), "lower": text.lower(), "title": text.title()}[name])
    elif name in ("length", "chars"):
        output(len(text))
    elif name == "words":
        output(len(text.split()))
    elif name == "palindrome":
        s = re.sub(r"[^a-z0-9]", "", text.lower())
        output("Yes!" if s == s[::-1] else "No!")
    elif name == "vowels":
        output(sum(c.lower() in "aeiou" for c in text))
    elif name == "consonants":
        output(sum(c.isalpha() and c.lower() not in "aeiou" for c in text))
    elif name == "initials":
        output("".join(w[0].upper() for w in text.split() if w))
    elif name == "repeat":
        try:
            count = max(0, min(100, int(args[0])))
            output(" ".join(args[1:]) * count)
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
            if command.lower() in ("back", "exit", "quit", "-open auriterm"):
                return
            if command:
                bot_command(command)
        except (KeyboardInterrupt, EOFError):
            return


# --------------------------- DEMONING ---------------------------

DEMONING_COMMANDS = [
    "phone info", "phone battery", "phone storage", "phone files",
    "phone flashlight", "phone vibrate", "phone apps", "phone brightness", "phone wifi",
    "scan", "audit", "password", "hash", "cipher", "vault", "integrity",
    "network", "firewall", "sandbox", "monitor", "logs", "forensic",
    "encode", "generator", "challenge", "sysinfo", "cpu", "memory",
    "diskcheck", "processes", "environment", "permissions", "uptime",
    "temperature", "diagnostics", "phone camera", "phone settings",
    "phone date", "phone time", "phone clipboard", "phone notification",
    "phone volume", "phone rotation", "phone display", "phone decime",
    "base64", "hex", "binary", "rot13", "checksum", "compare", "metadata",
    "json", "xml", "regex", "python", "piplist", "modules", "compile",
    "syntax", "benchmark", "uuid", "timestamp", "converter", "calculator",
    "overdrive", "glitch", "rainbow", "theme", "rank", "xp",
    "achievements", "leaderboard", "secrets", "history", "report"
]
assert len(DEMONING_COMMANDS) == 76


def demon_help():
    line()
    dprint("DEMONING COMMAND INDEX — 76 COMMANDS")
    for i, command in enumerate(DEMONING_COMMANDS, 1):
        dprint(f"{i:02}. {command}")
    line()
    dprint("Commands may accept arguments. Type exit/back to return.")


def log_event(message):
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(datetime.datetime.now().isoformat() + " | " + str(message) + "\n")
    except OSError:
        pass


def local_system_report():
    return {
        "platform": platform.platform(), "python": platform.python_version(),
        "machine": platform.machine(), "processor": platform.processor(),
        "hostname": socket.gethostname(), "uptime_seconds": round(time.time()-START_TIME, 2)
    }


def file_hash(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def phone_api(feature):
    dprint("Optional Android feature:", feature)
    dprint("Requires the Termux:API Android app and `pkg install termux-api`.")
    dprint("This build does not change device settings or access sensors automatically.")


def demoning_command(command):
    global XP
    try:
        parts = shlex.split(command)
    except ValueError as exc:
        dprint("Parsing error:", exc)
        return
    if not parts:
        return

    # Correctly parse multi-word commands (e.g. "phone info") while
    # keeping the remaining words as arguments (e.g. "hash hello").
    two_word = " ".join(parts[:2]).lower() if len(parts) >= 2 else ""
    multi = {x for x in DEMONING_COMMANDS if " " in x}
    if two_word in multi:
        name, args = two_word, parts[2:]
    else:
        name, args = parts[0].lower(), parts[1:]
    value = " ".join(args)

    XP += 1
    log_event(command)

    if name.startswith("phone "):
        feature = name[6:]
        if feature == "info":
            dprint("Device:", platform.platform(), "| Host:", socket.gethostname(), "| Python:", platform.python_version())
        elif feature == "storage":
            u = shutil.disk_usage(ROOT)
            dprint("Total:", round(u.total/1024**3, 2), "GB | Used:", round(u.used/1024**3, 2), "GB | Free:", round(u.free/1024**3, 2), "GB")
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
            for i in range(5):
                dprint("✦" * (i+1), "DEMONING")
                time.sleep(0.1)
        else:
            phone_api(feature)

    elif name == "scan":
        dprint("LOCAL PROJECT CHECK")
        for path in ROOT.iterdir():
            dprint("FOUND:", path.name)
        dprint("Only this project folder is checked.")
    elif name == "audit":
        for label, path in [("Data", DATA), ("Database", DATABASE), ("Backups", BACKUPS)]:
            dprint(label, "exists:", path.exists(), "writable:", os.access(path, os.W_OK))
    elif name == "password":
        if not value:
            dprint("Usage: password <text>")
        else:
            score = sum([len(value) >= 12, any(c.islower() for c in value),
                         any(c.isupper() for c in value), any(c.isdigit() for c in value),
                         any(not c.isalnum() for c in value)])
            dprint("Length:", len(value), "| Strength estimate:", score, "/ 5")
            dprint("Do not enter a real password here.")
    elif name in ("hash", "checksum"):
        dprint(hashlib.sha256(value.encode()).hexdigest() if value else "Usage: " + name + " <text>")
    elif name == "cipher":
        dprint("ROT13:", codecs.encode(value, "rot_13") if value else "Usage: cipher <text>")
        dprint("Demo only; ROT13 is not secure encryption.")
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
        dprint("SHA256:", file_hash(target) if target.exists() else "main.py not found.")
    elif name == "network":
        dprint("Hostname:", socket.gethostname())
        try:
            dprint("Local IP:", socket.gethostbyname(socket.gethostname()))
        except OSError:
            dprint("Local IP unavailable.")
        dprint("No remote hosts are scanned.")
    elif name == "firewall":
        dprint("Firewall status is not exposed by standard Python. Check system security settings.")
    elif name == "sandbox":
        dprint("Safe math-only sandbox.")
        if value:
            dprint(safe_calculate(value))
    elif name == "monitor":
        dprint("Processor:", platform.processor() or "Not reported")
        dprint("Uptime:", round(time.time()-START_TIME, 2), "seconds")
        dprint("For accurate RAM use Android Settings.")
    elif name in ("logs", "history"):
        entries = LOG_FILE.read_text(encoding="utf-8").splitlines() if LOG_FILE.exists() else []
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
                dprint("Name:", target.name, "| Size:", stat.st_size, "bytes")
                dprint("Modified:", datetime.datetime.fromtimestamp(stat.st_mtime))
                dprint("SHA256:", file_hash(target))
    elif name == "encode":
        dprint(base64.b64encode(value.encode()).decode())
    elif name == "generator":
        dprint("Generated token:", uuid.uuid4())
    elif name == "challenge":
        a, b = random.randint(2, 20), random.randint(2, 20)
        dprint("Solve:", a, "+", b)
        try:
            if dinput("Answer: ").strip() == str(a+b):
                XP += 10
                dprint("Correct! +10 XP")
            else:
                dprint("Answer:", a+b)
        except (KeyboardInterrupt, EOFError):
            dprint("Challenge cancelled.")
    elif name in ("sysinfo", "report"):
        report = local_system_report()
        if name == "report":
            report.update({"project": PROJECT, "version": VERSION, "dem oning_xp": XP})
            save_json(DATA / "dem oning_report.json", report)
            dprint("Report saved in data/dem oning_report.json")
        else:
            dprint(json.dumps(report, indent=2))
    elif name == "cpu":
        dprint("Processor:", platform.processor() or "Not reported", "| Machine:", platform.machine())
    elif name == "memory":
        dprint("Use Android Settings for accurate device RAM totals.")
    elif name == "diskcheck":
        u = shutil.disk_usage(ROOT)
        dprint("Total:", u.total, "| Used:", u.used, "| Free:", u.free, "bytes")
    elif name == "processes":
        dprint("Process listing is not available in standard Python on all Termux devices.")
    elif name == "environment":
        dprint("Environment variable names:")
        for key in sorted(os.environ):
            dprint(key)
    elif name == "permissions":
        for p in (ROOT, DATA, DATABASE, BACKUPS):
            dprint(p.name, "read:", os.access(p, os.R_OK), "write:", os.access(p, os.W_OK))
    elif name == "uptime":
        dprint(round(time.time()-START_TIME, 2), "seconds")
    elif name == "temperature":
        dprint("Hardware temperature is not exposed by standard Python.")
    elif name == "diagnostics":
        diagnostics()
    elif name in ("base64", "hex", "binary", "rot13"):
        if name == "base64":
            result = base64.b64encode(value.encode()).decode()
        elif name == "hex":
            result = value.encode().hex()
        elif name == "binary":
            result = " ".join(format(ord(c), "08b") for c in value)
        else:
            result = codecs.encode(value, "rot_13")
        dprint(result if value else "Usage: " + name + " <text>")
    elif name == "compare":
        if "|" not in value:
            dprint("Usage: compare text1 | text2")
        else:
            left, right = value.split("|", 1)
            dprint("Identical:", left.strip() == right.strip())
            dprint("Length difference:", abs(len(left.strip())-len(right.strip())))
    elif name == "metadata":
        dprint(PROJECT, VERSION, "Owner:", OWNER, "Python:", platform.python_version())
    elif name == "json":
        try:
            dprint(json.dumps(json.loads(value), indent=2) if value else "Usage: json <JSON text>")
        except json.JSONDecodeError as exc:
            dprint("Invalid JSON:", exc)
    elif name == "xml":
        dprint("XML parser is not included in this standard-library-only build.")
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
        dprint("Python:", platform.python_version(), "| Executable:", sys.executable)
    elif name == "piplist":
        dprint("Modules currently loaded in this Python process:")
        for module in sorted(sys.modules):
            dprint(module)
    elif name == "modules":
        show_modules()
    elif name == "compile":
        target = (ROOT / value).resolve() if value else None
        if not value or target.parent != ROOT.resolve() or not target.is_file() or target.suffix != ".py":
            dprint("Usage: compile <.py file directly inside project folder>")
        else:
            try:
                py_compile.compile(str(target), doraise=True)
                dprint("Syntax compilation successful.")
            except py_compile.PyCompileError as exc:
                dprint(exc)
    elif name == "syntax":
        try:
            ast.parse(value, mode="exec")
            dprint("Syntax looks valid." if value else "Usage: syntax <Python code>")
        except SyntaxError as exc:
            dprint("Syntax error:", exc)
    elif name == "benchmark":
        start = time.perf_counter()
        checksum = sum(i*i for i in range(100000))
        dprint("Benchmark:", round(time.perf_counter()-start, 5), "seconds | Checksum:", checksum)
    elif name == "uuid":
        dprint(uuid.uuid4())
    elif name == "timestamp":
        dprint(time.time())
    elif name == "converter":
        try:
            n = float(args[0])
            dprint("Meters to centimeters:", n*100, "| Kilometers to meters:", n*1000)
        except (ValueError, IndexError):
            dprint("Usage: converter <number>")
    elif name == "calculator":
        dprint(safe_calculate(value) if value else "Usage: calculator <math>")
    elif name == "overdrive":
        for i in range(8):
            dprint("OVERDRIVE", "█"*(i+1))
            time.sleep(0.06)
    elif name == "glitch":
        for _ in range(8):
            dprint("".join(random.choice("01#@$%!?") for _ in range(35)))
            time.sleep(0.05)
    elif name == "rainbow":
        for i in range(8):
            print(rainbow_at("A U R I T E R M   D E M O N I N G", i*3))
            time.sleep(0.1)
    elif name == "theme":
        dprint("Current main theme:", THEME, "| Use -theme to change.")
    elif name == "rank":
        dprint("Current rank:", "DEMONING INITIATE" if XP < 50 else "DEMONING EXPLORER")
    elif name == "xp":
        dprint("XP:", XP)
    elif name == "achievements":
        dprint("DEMONING LAUNCHED")
        dprint("COMMAND EXPLORER" if XP >= 10 else "Keep exploring!")
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
    dprint("Type help or -help for the index. Type exit/back to return.")
    while True:
        try:
            command = dinput().strip()
            normalized = command.strip().lower()
            if normalized in ("exit", "back", "quit", "return"):
                dprint("Leaving DEMONING...")
                return
            if normalized in ("-demoning", "demoning", "-demon", "demon"):
                dprint("You are already inside DEMONING. Type help to see its commands.")
                continue
            if normalized in ("help", "-help", "?"):
                demon_help()
            elif command:
                demoning_command(command)
        except (KeyboardInterrupt, EOFError):
            dprint("\nReturning to AuriTerm...")
            return


# ------------------------------ GAMES ------------------------------

def game_keyboard():
    output()
    output("             FANMADE KEYBOARD")
    output("                 ┌─────┐")
    output("                 │  W  │")
    output("   ┌─────┐ ┌─────┐ ┌─────┐")
    output("   │  A  │ │  S  │ │  D  │")
    output("   └─────┘ └─────┘ └─────┘")
    output("   WASD / arrow words = move | type dir quit to exit")
    output()


def play_maze():
    width, height = 9, 7
    player, goal = [1, 1], [7, 5]
    walls = {(3,1),(3,2),(3,3),(3,4),(5,2),(5,3),(5,4),(1,4),(2,4),(6,1),(7,1)}
    moves = {"w":(0,-1),"a":(-1,0),"s":(0,1),"d":(1,0),
             "up":(0,-1),"left":(-1,0),"down":(0,1),"right":(1,0)}
    while True:
        clear()
        output("AURITERM MAZE — Reach E, avoid #.")
        for y in range(height):
            row = ""
            for x in range(width):
                row += "@ " if [x,y] == player else "E " if [x,y] == goal else "# " if (x,y) in walls else ". "
            output(row)
        game_keyboard()
        if player == goal:
            output(GREEN + "YOU WON! +10 XP" + RESET)
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
            time.sleep(0.7)
            continue
        dx, dy = moves[move]
        nx, ny = player[0]+dx, player[1]+dy
        if 0 <= nx < width and 0 <= ny < height and (nx,ny) not in walls:
            player = [nx,ny]


def play_number_game():
    target, tries = random.randint(1,30), 0
    while True:
        clear()
        output("NUMBER GUESS — Pick a number from 1 to 30.")
        game_keyboard()
        guess = input("Your guess (or dir quit) > ").strip().lower()
        if guess == "dir quit":
            return
        try:
            number = int(guess)
            tries += 1
            if number == target:
                output("CORRECT! Attempts:", tries, "| +5 XP")
                time.sleep(1.3)
                return
            output("Higher!" if number < target else "Lower!")
            time.sleep(0.7)
        except ValueError:
            output("Enter a number or dir quit.")
            time.sleep(0.7)


def games_menu():
    while True:
        clear()
        output("AURITERM GAMES")
        line()
        output("1. Maze Runner — WASD")
        output("2. Number Guess")
        output("3. Back")
        line()
        choice = input("games > ").strip().lower()
        if choice in ("1","maze"):
            play_maze()
        elif choice in ("2","guess"):
            play_number_game()
        elif choice in ("3","back","exit","dir quit"):
            return
        else:
            output("Unknown game.")
            time.sleep(0.6)


# ------------------------ EXTRA MAIN COMMANDS ------------------------

def show_clock():
    output(datetime.datetime.now().strftime("%H:%M:%S"))


def show_calendar():
    now = datetime.datetime.now()
    output(calendar.month(now.year, now.month))


def todo_add(args):
    if not args:
        output("Usage: -todo <task>")
        return
    tasks = load_json(TODO_FILE, [])
    if not isinstance(tasks, list):
        tasks = []
    tasks.append({"task": " ".join(args), "done": False})
    save_json(TODO_FILE, tasks)
    output("Task added!")


def todo_list():
    tasks = load_json(TODO_FILE, [])
    if not isinstance(tasks, list) or not tasks:
        output("No tasks.")
        return
    for i, task in enumerate(tasks, 1):
        if isinstance(task, dict):
            output(f"{i}. [{'✓' if task.get('done') else ' '}] {task.get('task', '')}")


def backup_project():
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    destination = BACKUPS / f"auriterm_backup_{stamp}.zip"
    try:
        with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in ROOT.rglob("*"):
                if not path.is_file() or any(p in path.parts for p in (".git", "__pycache__", "backups")):
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
    for i, path in enumerate(backups, 1):
        output(i, path.name)
    choice = terminal_input("Backup number (or cancel): ").strip()
    if choice.lower() == "cancel":
        return
    try:
        selected = backups[int(choice)-1]
        with zipfile.ZipFile(selected) as archive:
            for member in archive.infolist():
                dest = (ROOT / member.filename).resolve()
                if dest != ROOT.resolve() and ROOT.resolve() not in dest.parents:
                    output("Unsafe archive path rejected.")
                    return
            archive.extractall(ROOT)
        output("Backup restored.")
    except (ValueError, IndexError, OSError, zipfile.BadZipFile) as exc:
        output("Restore failed:", exc)


def json_tool(args):
    text = " ".join(args)
    try:
        output(json.dumps(json.loads(text), indent=4) if text else "Usage: -json <JSON text>")
    except json.JSONDecodeError as exc:
        output("Invalid JSON:", exc)


def calc_tool(args):
    output(safe_calculate(" ".join(args)) if args else "Usage: -calc <math>")


def search_tool(args):
    if not args:
        output("Usage: -search <filename fragment>")
        return
    term, found = " ".join(args).lower(), 0
    for path in ROOT.rglob("*"):
        if any(p in path.parts for p in (".git", "__pycache__", "backups")):
            continue
        if term in path.name.lower():
            output(path.relative_to(ROOT))
            found += 1
    output("Matches:", found)


def version_info():
    output(PROJECT, VERSION, "| Owner:", OWNER)
    output("Python:", platform.python_version(), "| Platform:", platform.platform())


MAIN_COMMANDS = [
    "-help", "-open AuriBot", "-open ColorArt", "-open DemonDatabase",
    "-open Diagnostics", "-open Settings", "-open AuriTerm",
    "-demoning (aliases: demoning, -demon, demon)", "games / -games", "-clock", "-calendar", "-todo <task>",
    "-todo list", "-backup", "-restore", "-json <text>", "-calc <math>",
    "-search <filename>", "-versioninfo", "-rainbow", "-cancel", "-time",
    "-date", "-whoami", "-pwd", "-ls", "-tree", "-size", "-uptime",
    "-random", "-quote", "-joke", "-matrix", "-theme", "-modules",
    "-refresh", "-info", "-corrupt", "-echo <text>", "-timer <seconds>",
    "-stopwatch", "-note <text>", "-notes", "-clear-notes", "-find <word>",
    "-count <text>", "-slug <text>", "-morse <text>", "-unmorse <code>",
    "-ascii <text>", "-progress <0-100>", "-table <number>", "-fact",
    "-coinflip", "-clear", "-version", "-about", "-exit", "quit"
]


def help_menu():
    line()
    output("AURITERM COMMANDS")
    for command in MAIN_COMMANDS:
        output("  " + command)
    output("\nDEMONING: -demoning (76 commands; type help inside)")
    output("GAMES: games or -games; type dir quit inside a game to leave.")
    output("-exit = standby; -open AuriTerm = reopen; quit = close.")
    line()


def execute(command):
    global AURITERM_OPEN, PROGRAM_RUNNING, RAINBOW_MODE
    try:
        parts = shlex.split(command)
    except ValueError as exc:
        output("Command parsing error:", exc)
        return
    if not parts:
        return
    cmd, args = parts[0].lower(), parts[1:]
    full = command.strip().lower()

    if full == "-help":
        help_menu()
    elif cmd in ("-demoning", "demoning", "-demon", "demon"):
        run_demoning()
    elif full in ("games", "-games"):
        games_menu()
    elif full == "-clock":
        show_clock()
    elif full == "-calendar":
        show_calendar()
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
    elif full in ("-time", "-date"):
        output(datetime.datetime.now().strftime("%H:%M:%S" if full == "-time" else "%d/%m/%Y"))
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
        output(round(time.time()-START_TIME, 2), "seconds")
    elif full == "-random":
        output(random.randint(1,100))
    elif full == "-quote":
        output(random.choice(["Keep building. Keep learning.", "Every project starts with an idea.", "Make something that makes you curious."]))
    elif full == "-joke":
        output(random.choice(["Why did the computer get cold? It left its Windows open.", "Why was the computer tired? Too many tabs open.", "Why did the programmer quit? Too many bugs."]))
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
        output(re.sub(r"[^a-z0-9]+", "-", " ".join(args).lower()).strip("-") or "empty")
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
        output("AuriTerm entered standby. Commands remain available.")
        output("Use -open AuriTerm to reopen; quit to close.")
    elif full in ("quit", "shutdown", "close"):
        PROGRAM_RUNNING = False
        output("AuriTerm shutting down. Goodbye!")
    else:
        output("Unknown command. Type -help.")


def main():
    global PROGRAM_RUNNING
    clear()
    banner()
    slow("AuriTerm 2.2 Demoning Edition initialized successfully.")
    output("Type -help for commands | -demoning for DEMONING | games to play.")
    output("Type -exit for standby mode | quit to close.")
    while PROGRAM_RUNNING:
        try:
            prompt = "\nAuriTerm > " if AURITERM_OPEN else "\nAuriTerm [STANDBY] > "
            execute(terminal_input(prompt).strip())
        except KeyboardInterrupt:
            output("\nUse quit to close the program.")
        except EOFError:
            output("\nAuriTerm session ended.")
            break
        except Exception as exc:
            output("Unexpected error:", exc)
    output("AuriTerm session ended.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("Fatal error:", error)
