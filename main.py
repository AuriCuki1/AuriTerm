#!/usr/bin/env python3
# ============================================================
# AURITERM 2.2 — ALIVE + DEMONING EXTREME EDITION
# Single-file Python terminal for Termux
# Python 3.9+
# ============================================================

import os, sys, re, json, time, math, ast, shlex
import socket, hashlib, secrets, string, base64, random
import platform, datetime, subprocess, zipfile, shutil
import getpass, uuid, calendar, statistics, textwrap
import colorsys, threading
from pathlib import Path
from collections import Counter

VERSION = "2.2 ALIVE DEMONING"
ROOT = Path(__file__).resolve().parent
DATA = ROOT / "auriterm_data"
BACKUPS = DATA / "backups"

for folder in (DATA, BACKUPS):
    folder.mkdir(parents=True, exist_ok=True)

FILES = {
    "config": DATA / "config.json",
    "notes": DATA / "notes.json",
    "todos": DATA / "todos.json",
    "history": DATA / "history.json",
    "logs": DATA / "auriterm.log",
}

DEFAULT_CONFIG = {
    "username": "Auri",
    "theme": "RAINBOW",
    "hackmode": False,
    "ambient": True,
    "rainbow": True,
    "xp": 0,
    "rank": "ROOKIE",
    "commands_used": 0,
    "achievements": [],
}

def load_json(path, default):
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value
    except Exception:
        return default.copy()

def save_json(path, value):
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False),
                    encoding="utf-8")
    temp.replace(path)

config = load_json(FILES["config"], DEFAULT_CONFIG)
notes = load_json(FILES["notes"], [])
todos = load_json(FILES["todos"], [])
history = load_json(FILES["history"], [])

if not isinstance(config, dict):
    config = DEFAULT_CONFIG.copy()

for key, value in DEFAULT_CONFIG.items():
    config.setdefault(key, value)

if not isinstance(notes, list):
    notes = []
if not isinstance(todos, list):
    todos = []
if not isinstance(history, list):
    history = []

# ============================================================
# COLOR ENGINE — SHIFTING HUE
# ============================================================

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CLEAR = "\033[2J\033[H"
HUE_OFFSET = 0.0

def rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

def hue_color(position):
    h = (position + HUE_OFFSET) % 1.0
    r, g, b = colorsys.hsv_to_rgb(h, 0.9, 1.0)
    return rgb(int(r * 255), int(g * 255), int(b * 255))

def rainbow(text, speed=0.035):
    global HUE_OFFSET
    result = []
    for index, char in enumerate(str(text)):
        color = hue_color(index * speed)
        result.append(color + char)
    HUE_OFFSET = (HUE_OFFSET + 0.025) % 1.0
    return "".join(result) + RESET

def paint(text, color="cyan"):
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "purple": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
    }
    if config.get("rainbow", True):
        return rainbow(text)
    return colors.get(color, "") + str(text) + RESET

def out(text="", color="cyan"):
    print(paint(text, color))

def rainbow_animation(text, frames=24, delay=0.07):
    global HUE_OFFSET
    for _ in range(frames):
        print("\r" + rainbow(text), end="", flush=True)
        time.sleep(delay)
        HUE_OFFSET = (HUE_OFFSET + 0.045) % 1.0
    print()

# ============================================================
# LIVING BACKGROUND
# ============================================================

def living_background(seconds=5):
    """Animated terminal wallpaper. Press Ctrl+C to stop."""
    width = shutil.get_terminal_size((70, 20)).columns
    width = max(30, min(width, 100))
    symbols = " .:*+x01░▒▓"
    start = time.time()
    frame = 0

    try:
        while time.time() - start < seconds:
            line = []
            for x in range(width):
                wave = math.sin((x * 0.18) + frame * 0.25)
                value = int((wave + 1) * 4.5)
                line.append(symbols[value])
            print("\r" + rainbow("".join(line)), end="", flush=True)
            frame += 1
            time.sleep(0.06)
        print()
    except KeyboardInterrupt:
        print("\nAnimation stopped.")

def ambient_tick():
    if not config.get("ambient", True):
        return
    frames = ["◐", "◓", "◑", "◒"]
    frame = frames[int(time.time() * 4) % len(frames)]
    print(paint(frame, "purple"), end=" ")

# ============================================================
# STORAGE / LOGGING
# ============================================================

def log(message):
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with FILES["logs"].open("a", encoding="utf-8") as file:
            file.write(f"[{stamp}] {message}\n")
    except OSError:
        pass

def save_all():
    save_json(FILES["config"], config)
    save_json(FILES["notes"], notes)
    save_json(FILES["todos"], todos)
    save_json(FILES["history"], history)

def safe_path(name):
    target = (ROOT / name).resolve()
    if target != ROOT and ROOT not in target.parents:
        raise ValueError("Path outside AuriTerm folder is blocked.")
    return target

def clear_screen():
    os.system("clear" if os.name != "nt" else "cls")

# ============================================================
# BANNER
# ============================================================

def banner():
    clear_screen()
    logo = r"""
       █████╗ ██╗   ██╗██████╗ ██╗████████╗███████╗██████╗
      ██╔══██╗██║   ██║██╔══██╗██║╚══██╔══╝██╔════╝██╔══██╗
      ███████║██║   ██║██████╔╝██║   ██║   █████╗  ██████╔╝
      ██╔══██║██║   ██║██╔══██╗██║   ██║   ██╔══╝  ██╔══██╗
      ██║  ██║╚██████╔╝██║  ██║██║   ██║   ███████╗██║  ██║
      ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝

            C O L O R F U L   T E R M I N A L
                  E N V I R O N M E N T
    """
    print(rainbow(logo))
    print(rainbow(f"              AuriTerm {VERSION}"))
    print(paint("              OWNER: AURI", "purple"))
    print(paint("       ALIVE BACKGROUND ENGINE: ONLINE", "green"))
    print(paint("       DEMONING COMMAND SYSTEM: ONLINE", "green"))
    print()

# ============================================================
# PROFILE / XP
# ============================================================

RANKS = [
    (0, "ROOKIE"),
    (50, "SCRIPT KID"),
    (150, "CODE RUNNER"),
    (300, "TERMINAL USER"),
    (600, "SYSTEM EXPLORER"),
    (1000, "DEMONING MEMBER"),
    (1800, "AURI ENGINEER"),
    (3000, "AURI MASTER"),
    (5000, "LEGENDARY"),
]

ACHIEVEMENTS = {
    "first": "First Command",
    "ten": "10 Commands",
    "fifty": "50 Commands",
    "uuid": "UUID Generated",
    "note": "First Note",
    "game": "First Game",
    "backup": "First Backup",
    "demon": "DEMONING Activated",
}

def update_rank():
    rank = "ROOKIE"
    for points, name in RANKS:
        if config.get("xp", 0) >= points:
            rank = name
    config["rank"] = rank

def award_xp(amount):
    config["xp"] = int(config.get("xp", 0)) + amount
    update_rank()
    save_json(FILES["config"], config)

def achievement(key):
    unlocked = config.setdefault("achievements", [])
    if key in ACHIEVEMENTS and key not in unlocked:
        unlocked.append(key)
        save_json(FILES["config"], config)
        out("ACHIEVEMENT UNLOCKED: " + ACHIEVEMENTS[key], "yellow")

def profile():
    update_rank()
    out("\n========== AURI PROFILE ==========")
    out("Username: " + str(config["username"]))
    out("Rank: " + config["rank"])
    out("XP: " + str(config["xp"]))
    out("Commands: " + str(config["commands_used"]))
    out("Achievements: " + str(len(config["achievements"])))
    out("==================================")

def achievements():
    for key, name in ACHIEVEMENTS.items():
        state = "UNLOCKED" if key in config["achievements"] else "LOCKED"
        out(f"[{state}] {name}")

# ============================================================
# CALCULATOR
# ============================================================

OPS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.FloorDiv: lambda a, b: a // b,
    ast.Mod: lambda a, b: a % b,
    ast.Pow: lambda a, b: a ** b,
}

def calc(expression):
    if len(expression) > 250:
        raise ValueError("Expression too long.")

    tree = ast.parse(expression, mode="eval")

    def walk(node):
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                return node.value
        if isinstance(node, ast.UnaryOp):
            value = walk(node.operand)
            if isinstance(node.op, ast.USub):
                return -value
            if isinstance(node.op, ast.UAdd):
                return value
        if isinstance(node, ast.BinOp):
            operation = OPS.get(type(node.op))
            if operation is None:
                raise ValueError("Unsupported operator.")
            left, right = walk(node.left), walk(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 10:
                raise ValueError("Exponent too large.")
            result = operation(left, right)
            if isinstance(result, (int, float)) and abs(result) > 10**100:
                raise ValueError("Result too large.")
            return result
        raise ValueError("Invalid expression.")

    return walk(tree)

# ============================================================
# UUID / RANDOM GENERATORS
# ============================================================

def uuid_command():
    value = str(uuid.uuid4())
    out("UUID: " + value, "purple")
    achievement("uuid")
    return value

def generator_command(args):
    kind = args[0].lower() if args else "uuid"
    if kind == "uuid":
        uuid_command()
    elif kind == "hex":
        out(secrets.token_hex(16))
    elif kind == "token":
        out(secrets.token_urlsafe(32))
    elif kind == "number":
        out(str(secrets.randbelow(10**12)))
    elif kind == "password":
        password_generator(args[1] if len(args) > 1 else "24")
    else:
        out("Generator types: uuid, hex, token, number, password")

def password_generator(length="20"):
    try:
        size = int(length)
        if not 8 <= size <= 128:
            raise ValueError
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*_-+="
        out("".join(secrets.choice(alphabet) for _ in range(size)), "green")
    except Exception:
        out("Usage: -passgen 20 (8–128)")

# ============================================================
# AURIBOT — 65 COMMAND LIBRARY
# ============================================================

BOT_COMMANDS = {
    "joke": "Tell a random joke",
    "quote": "Show a random quote",
    "motivate": "Motivational message",
    "fact": "Random fact",
    "riddle": "Random riddle",
    "coin": "Flip a coin",
    "dice": "Roll a dice",
    "roll": "Roll a custom number",
    "choose": "Choose between options",
    "number": "Random number",
    "color": "Random color",
    "palette": "Show color palette",
    "rainbow": "Rainbow text",
    "banner": "Show AuriTerm banner",
    "status": "Show status",
    "system": "System information",
    "python": "Python version",
    "platform": "Platform information",
    "uptime": "Session uptime",
    "disk": "Disk information",
    "folders": "Show folders",
    "files": "Show files",
    "pwd": "Current directory",
    "ls": "List files",
    "whoami": "Show username",
    "username": "Show username",
    "weekday": "Current weekday",
    "month": "Current month",
    "year": "Current year",
    "timestamp": "Unix timestamp",
    "calendar": "Show calendar",
    "countdown": "Countdown timer",
    "add": "Add numbers",
    "subtract": "Subtract numbers",
    "multiply": "Multiply numbers",
    "divide": "Divide numbers",
    "square": "Square a number",
    "cube": "Cube a number",
    "sqrt": "Square root",
    "power": "Power calculation",
    "percent": "Percentage calculation",
    "convert": "Unit conversion",
    "hex": "Decimal to hexadecimal",
    "binary": "Decimal to binary",
    "octal": "Decimal to octal",
    "reverse": "Reverse text",
    "upper": "Uppercase text",
    "lower": "Lowercase text",
    "title": "Title case text",
    "length": "Text length",
    "words": "Word count",
    "chars": "Character count",
    "palindrome": "Palindrome checker",
    "vowels": "Count vowels",
    "consonants": "Count consonants",
    "initials": "Get initials",
    "repeat": "Repeat text",
    "shuffle": "Shuffle text",
    "sort": "Sort words",
    "unique": "Unique words",
    "countlines": "Count lines",
    "encode": "Base64 encode",
    "decode": "Base64 decode",
    "hash": "SHA-256 hash",
    "uuid": "Generate a UUID",
}

JOKES = [
    "Why did the programmer quit? The work had too many bugs.",
    "There are 10 types of people: those who understand binary and those who don't.",
    "A SQL query walks into a bar and asks: can I join you?",
    "Why do Java developers wear glasses? They don't C#.",
]

QUOTES = [
    "Every great project starts with one line.",
    "Build something that makes you curious.",
    "Small progress is still progress.",
    "The terminal is only the beginning.",
]

FACTS = [
    "A UUID is commonly represented as 32 hexadecimal digits and hyphens.",
    "Python was first released in 1991.",
    "The Linux kernel was first released in 1991.",
    "ASCII originally used 7 bits per character.",
]

RIDDLES = [
    ("What has keys but no locks?", "keyboard"),
    ("What gets wetter as it dries?", "towel"),
    ("What has a face and hands but no arms?", "clock"),
]

def auribot(args):
    if not args:
        out("AuriBot commands: -bot help")
        return

    action = args[0].lower()
    values = args[1:]
    text_value = " ".join(values)

    if action == "help":
        for name, description in BOT_COMMANDS.items():
            out(f"{name:<14} {description}")
        return

    if action not in BOT_COMMANDS:
        out("Unknown AuriBot command.")
        return

    if action == "joke":
        out(random.choice(JOKES))
    elif action == "quote":
        out(random.choice(QUOTES))
    elif action == "motivate":
        out(random.choice([
            "Keep building. Your next idea could be your best.",
            "One bug at a time.",
            "You don't need to finish everything today.",
        ]))
    elif action == "fact":
        out(random.choice(FACTS))
    elif action == "riddle":
        question, answer = random.choice(RIDDLES)
        out(question)
        guess = input("ANSWER> ").strip().lower()
        out("Correct!" if guess == answer else "Answer: " + answer)
    elif action == "coin":
        out(random.choice(["HEADS", "TAILS"]))
    elif action == "dice":
        out(str(random.randint(1, 6)))
    elif action == "roll":
        try:
            maximum = int(values[0]) if values else 100
            out(str(random.randint(1, max(1, maximum))))
        except Exception:
            out("Usage: -bot roll 100")
    elif action == "choose":
        if len(values) < 2:
            out("Usage: -bot choose red blue green")
        else:
            out(random.choice(values))
    elif action == "number":
        out(str(random.randint(0, 999999)))
    elif action == "color":
        color = "#{:06X}".format(random.randint(0, 0xFFFFFF))
        out(color)
    elif action == "palette":
        for i in range(12):
            out("██████  " + f"HUE {i * 30}°")
    elif action == "rainbow":
        rainbow_animation(text_value or "AURITERM RAINBOW", 30)
    elif action == "banner":
        banner()
    elif action == "status":
        show_status()
    elif action in ("system", "platform"):
        system_info()
    elif action == "python":
        out(sys.version)
    elif action == "uptime":
        out(f"Session uptime: {int(time.time() - START_TIME)} seconds")
    elif action == "disk":
        usage = shutil.disk_usage(ROOT)
        out(f"Total {usage.total // 1024**3} GB")
        out(f"Free {usage.free // 1024**3} GB")
    elif action == "folders":
        for p in ROOT.iterdir():
            if p.is_dir():
                out(p.name + "/")
    elif action in ("files", "ls"):
        for p in ROOT.iterdir():
            if p.is_file():
                out(p.name)
    elif action == "pwd":
        out(str(ROOT))
    elif action in ("whoami", "username"):
        out(str(config["username"]))
    elif action == "weekday":
        out(datetime.datetime.now().strftime("%A"))
    elif action == "month":
        out(datetime.datetime.now().strftime("%B"))
    elif action == "year":
        out(str(datetime.datetime.now().year))
    elif action == "timestamp":
        out(str(int(time.time())))
    elif action == "calendar":
        now = datetime.datetime.now()
        print(calendar.month(now.year, now.month))
    elif action == "countdown":
        try:
            seconds = min(60, max(1, int(values[0])))
            for n in range(seconds, 0, -1):
                print(f"\r{rainbow(str(n))}", end="", flush=True)
                time.sleep(1)
            print("\nDONE!")
        except Exception:
            out("Usage: -bot countdown 5")
    elif action in ("add", "subtract", "multiply", "divide"):
        try:
            a, b = float(values[0]), float(values[1])
            result = {
                "add": lambda: a + b,
                "subtract": lambda: a - b,
                "multiply": lambda: a * b,
                "divide": lambda: a / b,
            }[action]()
            out(str(result))
        except Exception as error:
            out("Usage: -bot add 5 2")
            if isinstance(error, ZeroDivisionError):
                out("Cannot divide by zero.")
    elif action in ("square", "cube", "sqrt"):
        try:
            n = float(values[0])
            result = n*n if action == "square" else n*n*n if action == "cube" else math.sqrt(n)
            out(str(result))
        except Exception:
            out("Usage: -bot square 5")
    elif action == "power":
        try:
            out(str(float(values[0]) ** float(values[1])))
        except Exception:
            out("Usage: -bot power 2 8")
    elif action == "percent":
        try:
            out(str(float(values[0]) * float(values[1]) / 100))
        except Exception:
            out("Usage: -bot percent 20 80")
    elif action == "convert":
        try:
            n = float(values[0])
            unit = values[1].lower()
            if unit == "km-mi":
                out(str(n * 0.621371) + " miles")
            elif unit == "mi-km":
                out(str(n / 0.621371) + " km")
            elif unit == "c-f":
                out(str(n * 9/5 + 32) + " °F")
            elif unit == "f-c":
                out(str((n - 32) * 5/9) + " °C")
            elif unit == "kg-lb":
                out(str(n * 2.20462) + " lb")
            elif unit == "lb-kg":
                out(str(n / 2.20462) + " kg")
            else:
                out("Units: km-mi, mi-km, c-f, f-c, kg-lb, lb-kg")
        except Exception:
            out("Usage: -bot convert 10 km-mi")
    elif action in ("hex", "binary", "octal"):
        try:
            n = int(values[0])
            result = {"hex": hex, "binary": bin, "octal": oct}[action](n)
            out(result)
        except Exception:
            out("Usage: -bot hex 255")
    elif action == "reverse":
        out(text_value[::-1])
    elif action == "upper":
        out(text_value.upper())
    elif action == "lower":
        out(text_value.lower())
    elif action == "title":
        out(text_value.title())
    elif action == "length":
        out(str(len(text_value)))
    elif action == "words":
        out(str(len(text_value.split())))
    elif action == "chars":
        out(str(len(text_value)))
    elif action == "palindrome":
        cleaned = re.sub(r"[^a-z0-9]", "", text_value.lower())
        out("YES" if cleaned == cleaned[::-1] else "NO")
    elif action == "vowels":
        out(str(sum(c.lower() in "aeiou" for c in text_value)))
    elif action == "consonants":
        out(str(sum(c.isalpha() and c.lower() not in "aeiou" for c in text_value)))
    elif action == "initials":
        out("".join(word[0].upper() for word in values if word))
    elif action == "repeat":
        try:
            count = min(100, max(1, int(values[0])))
            out(" ".join(values[1:]) * count)
        except Exception:
            out("Usage: -bot repeat 3 hello")
    elif action == "shuffle":
        chars = list(text_value)
        random.shuffle(chars)
        out("".join(chars))
    elif action == "sort":
        out(" ".join(sorted(values)))
    elif action == "unique":
        out(" ".join(dict.fromkeys(values)))
    elif action == "countlines":
        out(str(len(text_value.splitlines())))
    elif action == "encode":
        out(base64.b64encode(text_value.encode()).decode())
    elif action == "decode":
        try:
            out(base64.b64decode(text_value, validate=True).decode())
        except Exception:
            out("Invalid Base64.")
    elif action == "hash":
        out(hashlib.sha256(text_value.encode()).hexdigest())
    elif action == "uuid":
        uuid_command()

# ============================================================
# SYSTEM TOOLS
# ============================================================

def system_info():
    out("\n========== SYSTEM REPORT ==========")
    out("Platform: " + platform.platform())
    out("System: " + platform.system())
    out("Release: " + platform.release())
    out("Machine: " + platform.machine())
    out("Python: " + platform.python_version())
    out("Hostname: " + socket.gethostname())
    out("PID: " + str(os.getpid()))
    out("Home: " + str(Path.home()))
    try:
        disk = shutil.disk_usage(ROOT)
        out(f"Disk total: {disk.total // 1024**3} GB")
        out(f"Disk free: {disk.free // 1024**3} GB")
    except Exception:
        pass

def network_info():
    out("Hostname: " + socket.gethostname())
    try:
        for item in sorted({x[4][0] for x in socket.getaddrinfo(socket.gethostname(), None)}):
            out("Local address: " + item)
    except Exception as error:
        out(str(error))

def dns_lookup(domain):
    if not re.fullmatch(r"[A-Za-z0-9.-]{1,253}", domain or ""):
        out("Usage: -dns example.com")
        return
    try:
        for item in sorted({x[4][0] for x in socket.getaddrinfo(domain, None)}):
            out(item)
    except Exception as error:
        out("DNS error: " + str(error))

def local_ping():
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "127.0.0.1"],
            capture_output=True, text=True, timeout=5
        )
        out(result.stdout or result.stderr)
    except Exception as error:
        out("Ping unavailable: " + str(error))

def port_check(port):
    try:
        port = int(port)
        if not 1 <= port <= 65535:
            raise ValueError
        with socket.create_connection(("127.0.0.1", port), timeout=1):
            out(f"Local port {port}: OPEN")
    except Exception:
        out("Local port closed or invalid.")

def simulated_trace():
    out("SIMULATED TRACE — no external route scan")
    for item in ("LOCAL DEVICE", "LOCAL ROUTER", "GATEWAY", "DESTINATION"):
        out("-> " + item)
        time.sleep(0.2)

# ============================================================
# FILE TOOLS
# ============================================================

def file_hash(name):
    try:
        path = safe_path(name)
        digest = hashlib.sha256()
        with path.open("rb") as file:
            for chunk in iter(lambda: file.read(65536), b""):
                digest.update(chunk)
        out(digest.hexdigest())
    except Exception as error:
        out("Hash error: " + str(error))

def hex_view(name):
    try:
        path = safe_path(name)
        data = path.read_bytes()[:512]
        for offset in range(0, len(data), 16):
            chunk = data[offset:offset+16]
            hx = " ".join(f"{b:02X}" for b in chunk)
            txt = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
            out(f"{offset:08X}  {hx:<47} {txt}")
    except Exception as error:
        out("Hex error: " + str(error))

def file_check(name):
    try:
        path = safe_path(name)
        if not path.is_file():
            out("File not found.")
            return
        data = path.read_bytes()
        out("Name: " + path.name)
        out("Size: " + str(len(data)) + " bytes")
        out("SHA-256: " + hashlib.sha256(data).hexdigest())
        try:
            data.decode("utf-8")
            out("UTF-8: YES")
        except UnicodeDecodeError:
            out("UTF-8: NO")
    except Exception as error:
        out(str(error))

def list_files():
    for path in sorted(ROOT.iterdir()):
        out(("[DIR] " if path.is_dir() else "[FILE] ") + path.name)

def read_file(name):
    try:
        out(safe_path(name).read_text(encoding="utf-8"))
    except Exception as error:
        out("Read error: " + str(error))

def write_file(name, content):
    try:
        path = safe_path(name)
        if path.exists():
            out("File exists. Use -writeforce to replace.")
            return
        path.write_text(content, encoding="utf-8")
        out("Created " + path.name)
    except Exception as error:
        out("Write error: " + str(error))

# ============================================================
# NOTES / TODO
# ============================================================

def note_command(args):
    action = args[0].lower() if args else "list"
    if action == "add":
        text = " ".join(args[1:])
        if not text:
            out("Usage: -note add TEXT")
            return
        notes.append({"text": text, "time": time.time()})
        save_json(FILES["notes"], notes)
        achievement("note")
        out("Note saved.")
    elif action == "list":
        for i, item in enumerate(notes, 1):
            out(f"{i}. {item['text']}")
        if not notes:
            out("No notes.")
    elif action == "delete":
        try:
            removed = notes.pop(int(args[1])-1)
            save_json(FILES["notes"], notes)
            out("Deleted: " + removed["text"])
        except Exception:
            out("Usage: -note delete NUMBER")
    elif action == "clear":
        if input("Type YES to clear notes: ") == "YES":
            notes.clear()
            save_json(FILES["notes"], notes)
            out("Notes cleared.")
    else:
        out("Usage: -note add|list|delete|clear")

def todo_command(args):
    action = args[0].lower() if args else "list"
    if action == "add":
        text = " ".join(args[1:])
        if not text:
            out("Usage: -todo add TEXT")
            return
        todos.append({"text": text, "done": False})
        save_json(FILES["todos"], todos)
        out("Task added.")
    elif action == "list":
        for i, item in enumerate(todos, 1):
            out(f"{i}. [{'X' if item['done'] else ' '}] {item['text']}")
        if not todos:
            out("No tasks.")
    elif action == "done":
        try:
            todos[int(args[1])-1]["done"] = True
            save_json(FILES["todos"], todos)
            out("Task completed.")
        except Exception:
            out("Usage: -todo done NUMBER")
    elif action == "delete":
        try:
            item = todos.pop(int(args[1])-1)
            save_json(FILES["todos"], todos)
            out("Deleted: " + item["text"])
        except Exception:
            out("Usage: -todo delete NUMBER")
    elif action == "clear":
        if input("Type YES to clear tasks: ") == "YES":
            todos.clear()
            save_json(FILES["todos"], todos)
            out("Tasks cleared.")

# ============================================================
# TERMUX CLIPBOARD — FIXED GET AND SET
# ============================================================

def clipboard_command(args):
    action = args[0].lower() if args else "get"

    if action in ("get", "read"):
        executable = shutil.which("termux-clipboard-get")
        if not executable:
            out("Clipboard command is missing.", "red")
            out("Install Termux:API app, then run:")
            out("pkg install termux-api")
            out("Make sure Termux and Termux:API came from compatible sources.")
            return

        try:
            result = subprocess.run(
                [executable],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                out("Clipboard read failed: " + result.stderr.strip(), "red")
            elif result.stdout == "":
                out("[Clipboard is empty]")
            else:
                out(result.stdout.rstrip("\n"))
        except subprocess.TimeoutExpired:
            out("Clipboard read timed out.", "red")
        except Exception as error:
            out("Clipboard error: " + str(error), "red")

    elif action in ("set", "copy"):
        text = " ".join(args[1:])
        if not text:
            out("Usage: -clipboard set TEXT")
            return

        executable = shutil.which("termux-clipboard-set")
        if not executable:
            out("Clipboard command is missing.", "red")
            out("Install Termux:API app, then run:")
            out("pkg install termux-api")
            return

        try:
            result = subprocess.run(
                [executable],
                input=text,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                out("Copied to Android clipboard!", "green")
            else:
                out("Clipboard write failed: " + result.stderr.strip(), "red")
        except Exception as error:
            out("Clipboard error: " + str(error), "red")
    else:
        out("Usage: -clipboard get")
        out("       -clipboard set TEXT")

# ============================================================
# ANDROID API
# ============================================================

def phone_command(args):
    if not args:
        out("Usage: -phone battery|torch on|torch off|vibrate MS")
        return

    action = args[0].lower()

    commands = {
        "battery": ["termux-battery-status"],
    }

    if action == "battery":
        cmd = commands["battery"]
    elif action == "torch":
        if len(args) < 2 or args[1] not in ("on", "off"):
            out("Usage: -phone torch on|off")
            return
        cmd = ["termux-torch", args[1]]
    elif action == "vibrate":
        try:
            duration = max(1, min(10000, int(args[1])))
            cmd = ["termux-vibrate", "-d", str(duration)]
        except Exception:
            out("Usage: -phone vibrate 500")
            return
    else:
        out("Unknown phone action.")
        return

    if not shutil.which(cmd[0]):
        out("Missing Termux:API command: " + cmd[0], "red")
        out("Install the Termux:API app and run pkg install termux-api.")
        return

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            out(result.stdout.strip() or "Done.", "green")
        else:
            out(result.stderr.strip() or "Android API command failed.", "red")
    except Exception as error:
        out("API error: " + str(error), "red")

# ============================================================
# GAMES
# ============================================================

def maze_game():
    board = [
        list("##########"),
        list("#P...#...#"),
        list("#.#..#.#.#"),
        list("#.#....#.#"),
        list("#.####...#"),
        list("#......G.#"),
        list("##########"),
    ]
    y, x = 1, 1
    moves = {"w": (-1,0), "s": (1,0), "a": (0,-1), "d": (0,1)}

    out("MAZE: WASD move, dir redraw, quit exit.")
    while True:
        for row in board:
            print(rainbow("".join(row)))
        command = input("GAME> ").strip().lower()

        if command in ("quit", "exit"):
            return
        if command == "dir":
            continue
        if command not in moves:
            out("Use WASD.")
            continue

        dy, dx = moves[command]
        ny, nx = y + dy, x + dx

        if board[ny][nx] == "#":
            out("Wall!")
            continue

        board[y][x] = "."
        y, x = ny, nx

        if board[y][x] == "G":
            out("YOU WIN!")
            award_xp(25)
            achievement("game")
            return

        board[y][x] = "P"

def number_game():
    target = random.randint(1, 50)
    attempts = 0
    out("Guess a number from 1 to 50. Type quit to leave.")
    while True:
        value = input("GUESS> ").strip().lower()
        if value == "quit":
            return
        try:
            number = int(value)
        except ValueError:
            out("Enter a number.")
            continue
        attempts += 1
        if number == target:
            out("CORRECT! Attempts: " + str(attempts), "green")
            award_xp(max(5, 30 - attempts))
            achievement("game")
            return
        out("Too low." if number < target else "Too high.")

def game_menu():
    out("1. Maze")
    out("2. Number guess")
    out("3. Exit")
    choice = input("GAME CENTER> ")
    if choice == "1":
        maze_game()
    elif choice == "2":
        number_game()

# ============================================================
# DEMONING — 8 COMMANDS
# ============================================================

DEMONING_HISTORY = []

DEMONING_INDEX = [
    "about", "status", "syscheck", "whoami", "rootcheck",
    "terminal", "hackmode", "netinfo", "ipinfo", "dns",
    "ping", "portcheck", "netmap", "trace", "hash",
    "hashfile", "hexview", "filecheck", "keygen", "passgen",
    "encode", "decode", "encrypt", "decrypt", "calc",
    "note", "todo", "backup", "backups", "logs", "phone",
    "clipboard", "uuid", "generator", "timestamp", "calendar",
    "game", "matrix", "glitch", "rainbow", "ambient",
    "bot", "clear", "help", "commands"
]

def demon_help():
    out("""
========== DEMONING ==========
help       Show help
list       List indexed commands
search X   Search commands
run X      Execute indexed command
random     Random command suggestion
stats      DEMONING statistics
history    DEMONING history
exit       Return to AuriTerm
==============================
""")

def demon_list():
    for i, name in enumerate(DEMONING_INDEX, 1):
        out(f"{i:02}. -{name}")
    out("Indexed commands: " + str(len(DEMONING_INDEX)))

def demon_search(args):
    if not args:
        out("Usage: -demoning search NAME")
        return
    query = " ".join(args).lower()
    matches = [name for name in DEMONING_INDEX if query in name]
    if matches:
        for name in matches:
            out("[FOUND] -" + name)
    else:
        out("No matches.")

def demon_run(args):
    if not args:
        out("Usage: -demoning run COMMAND")
        return
    name = args[0].lower().lstrip("-")
    if name not in DEMONING_INDEX:
        out("Command not in DEMONING index.", "red")
        return
    if name in ("help", "commands", "clear", "exit"):
        out("Use the main terminal command for this action.")
        return
    DEMONING_HISTORY.append(name)
    out("[DEMONING] Running -" + name)
    execute("-" + name + (" " + shlex.join(args[1:]) if len(args) > 1 else ""))

def demon_random():
    out("Try: -" + random.choice(DEMONING_INDEX))

def demon_stats():
    out("DEMONING version: 1.0")
    out("Indexed: " + str(len(DEMONING_INDEX)))
    out("Executed: " + str(len(DEMONING_HISTORY)))
    out("Unique: " + str(len(set(DEMONING_HISTORY))))

def demon_history():
    if not DEMONING_HISTORY:
        out("No DEMONING history.")
        return
    for i, name in enumerate(DEMONING_HISTORY, 1):
        out(f"{i}. -{name}")

def demoning(args):
    achievement("demon")
    if not args:
        demon_help()
        return

    action, rest = args[0].lower(), args[1:]
    actions = {
        "help": demon_help,
        "list": demon_list,
        "search": lambda: demon_search(rest),
        "run": lambda: demon_run(rest),
        "random": demon_random,
        "stats": demon_stats,
        "history": demon_history,
        "exit": lambda: out("Returning to AuriTerm.")
    }

    if action in actions:
        actions[action]()
    else:
        out("Unknown DEMONING command. Use -demoning help.")

# ============================================================
# MATRIX / GLITCH / AMBIENT
# ============================================================

def matrix_effect():
    chars = "01ABCDEF#$%&"
    for _ in range(18):
        out("".join(random.choice(chars) for _ in range(55)))
        time.sleep(0.04)

def glitch_effect():
    chars = "▓▒░#@$!?01"
    for _ in range(12):
        out("".join(random.choice(chars) for _ in range(55)))
        time.sleep(0.05)

def ambient_mode(args):
    if args and args[0].lower() == "off":
        config["ambient"] = False
        save_json(FILES["config"], config)
        out("Ambient mode OFF.")
    elif args and args[0].lower() == "on":
        config["ambient"] = True
        save_json(FILES["config"], config)
        out("Ambient mode ON.")
    else:
        living_background(8)

# ============================================================
# STATUS / HELP
# ============================================================

def show_status():
    out("\n========== AURITERM STATUS ==========")
    out("Version: " + VERSION)
    out("Username: " + str(config["username"]))
    out("Rainbow: " + str(config["rainbow"]))
    out("Ambient: " + str(config["ambient"]))
    out("Hack mode: " + str(config["hackmode"]))
    out("Commands used: " + str(config["commands_used"]))
    out("XP: " + str(config["xp"]))
    out("Rank: " + str(config["rank"]))
    out("Notes: " + str(len(notes)))
    out("Tasks: " + str(len(todos)))
    out("DEMONING runs: " + str(len(DEMONING_HISTORY)))
    out("=====================================")

def show_help():
    out("""
================ AURITERM COMMANDS ================

CORE
-help                 Show help
-about                About AuriTerm
-status               Status
-syscheck             System report
-profile              Player profile
-achievements         Achievements
-hackmode             Toggle hack prompt
-clear                Clear screen
-exit                 Exit

DEMONING
-demoning             Open DEMONING
-demoning help        Help
-demoning list        List
-demoning search X    Search
-demoning run X       Execute
-demoning random      Random suggestion
-demoning stats       Statistics
-demoning history     History
-demoning exit        Leave

AURIBOT — 65 COMMANDS
-bot help             List all 65 commands
-bot uuid             Generate UUID
-bot timestamp        Unix timestamp
-bot calendar         Current month calendar
-bot joke             Joke
-bot quote            Quote
-bot fact             Fact
-bot riddle           Riddle
-bot rainbow TEXT     Animated rainbow
-bot add 5 2          Add
-bot convert 10 km-mi Convert units
-bot encode TEXT      Base64
-bot hash TEXT        SHA-256
(and many more)

GENERATORS
-uuid                 Generate UUID
-generator uuid       UUID generator
-generator hex        Hex token
-generator token      Random token
-generator number    Random number
-passgen 24           Password generator
-keygen               Random token

FILES
-ls                   List files
-read FILE            Read file
-write FILE TEXT      Create file
-hash TEXT            Hash text
-hashfile FILE        Hash file
-hexview FILE         Hex view
-filecheck FILE       File inspection
-backup               ZIP backup
-backups              List backups

NETWORK — LOCAL / EDUCATIONAL
-netinfo              Local network info
-ipinfo               Local IP info
-dns DOMAIN           DNS lookup
-ping                 Ping localhost
-portcheck PORT       Check localhost
-trace                Simulated trace

PHONE
-phone battery        Battery info
-phone torch on       Flashlight on
-phone torch off      Flashlight off
-phone vibrate 500    Vibrate for 500 ms
-clipboard get        Read clipboard
-clipboard set TEXT   Copy text

PERSONAL TOOLS
-note add TEXT        Save note
-note list            List notes
-note delete NUMBER   Delete note
-todo add TEXT        Add task
-todo list            List tasks
-todo done NUMBER     Complete task
-todo delete NUMBER   Delete task

VISUALS
-rainbow TEXT         Animated hue shift
-ambient              Moving background
-ambient on|off       Ambient toggle
-matrix               Matrix effect
-glitch               Glitch effect

GAMES
-game                 Game center
===================================================
""")

# ============================================================
# MAIN COMMAND ROUTER
# ============================================================

START_TIME = time.time()

def execute(raw):
    raw = raw.strip()
    if not raw:
        return True

    try:
        parts = shlex.split(raw)
    except ValueError as error:
        out("Input error: " + str(error), "red")
        return True

    command = parts[0].lower().lstrip("-")
    args = parts[1:]

    config["commands_used"] += 1
    history.append({"time": time.time(), "command": raw})
    if len(history) > 500:
        del history[:-500]

    save_json(FILES["config"], config)
    save_json(FILES["history"], history)
    log(raw)

    count = config["commands_used"]
    if count == 1:
        achievement("first")
    if count >= 10:
        achievement("ten")
    if count >= 50:
        achievement("fifty")

    try:
        if command == "help" or command == "commands":
            show_help()

        elif command == "demoning":
            demoning(args)

        elif command == "bot":
            auribot(args)

        elif command in ("about",):
            out("AuriTerm " + VERSION)
            out("A colorful single-file terminal made for Auri.")

        elif command == "status":
            show_status()

        elif command in ("syscheck", "system"):
            system_info()

        elif command in ("whoami", "username"):
            out(str(config["username"]))

        elif command == "rootcheck":
            root = hasattr(os, "geteuid") and os.geteuid() == 0
            out("Root: " + ("YES" if root else "NO"))

        elif command == "terminal":
            out("Python: " + sys.version)
            out("Shell: " + os.environ.get("SHELL", "Unknown"))
            out("Folder: " + str(ROOT))

        elif command == "hackmode":
            config["hackmode"] = not config["hackmode"]
            save_json(FILES["config"], config)
            out("Hack mode: " + str(config["hackmode"]))

        elif command == "profile":
            profile()

        elif command == "achievements":
            achievements()

        elif command in ("netinfo", "ipinfo", "netmap"):
            network_info()

        elif command == "dns":
            dns_lookup(args[0] if args else "")

        elif command == "ping":
            local_ping()

        elif command == "portcheck":
            port_check(args[0] if args else "")

        elif command == "trace":
            simulated_trace()

        elif command == "uuid":
            uuid_command()

        elif command == "generator":
            generator_command(args)

        elif command == "timestamp":
            out(str(int(time.time())))

        elif command == "calendar":
            now = datetime.datetime.now()
            print(calendar.month(now.year, now.month))

        elif command == "calc":
            if not args:
                out("Usage: -calc 5 * (2 + 3)")
            else:
                out(str(calc(" ".join(args))))

        elif command == "hash":
            out(hashlib.sha256(" ".join(args).encode()).hexdigest())

        elif command == "hashfile":
            file_hash(args[0] if args else "")

        elif command == "hexview":
            hex_view(args[0] if args else "")

        elif command == "filecheck":
            file_check(args[0] if args else "")

        elif command == "ls":
            list_files()

        elif command == "read":
            read_file(args[0] if args else "")

        elif command == "write":
            if len(args) < 2:
                out("Usage: -write FILE TEXT")
            else:
                write_file(args[0], " ".join(args[1:]))

        elif command == "writeforce":
            if len(args) < 2:
                out("Usage: -writeforce FILE TEXT")
            else:
                try:
                    safe_path(args[0]).write_text(" ".join(args[1:]), encoding="utf-8")
                    out("File replaced.")
                except Exception as error:
                    out(str(error))

        elif command == "keygen":
            out(secrets.token_hex(32))

        elif command == "passgen":
            password_generator(args[0] if args else "20")

        elif command == "encode":
            out(base64.b64encode(" ".join(args).encode()).decode())

        elif command == "decode":
            try:
                out(base64.b64decode(" ".join(args), validate=True).decode())
            except Exception:
                out("Invalid Base64.")

        elif command == "encrypt":
            text = " ".join(args)
            out("Educational Caesar cipher; not secure encryption.")
            out("".join(chr((ord(c)-65+7)%26+65) if c.isupper()
                        else chr((ord(c)-97+7)%26+97) if c.islower()
                        else c for c in text))

        elif command == "decrypt":
            text = " ".join(args)
            out("Educational Caesar cipher; not secure encryption.")
            out("".join(chr((ord(c)-65-7)%26+65) if c.isupper()
                        else chr((ord(c)-97-7)%26+97) if c.islower()
                        else c for c in text))

        elif command == "note":
            note_command(args)

        elif command == "todo":
            todo_command(args)

        elif command == "backup":
            stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            destination = BACKUPS / f"backup_{stamp}.zip"
            try:
                with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
                    for path in ROOT.rglob("*"):
                        if path.is_file() and DATA not in path.parents:
                            archive.write(path, path.relative_to(ROOT))
                out("Backup created: " + destination.name)
                achievement("backup")
            except Exception as error:
                out("Backup error: " + str(error))

        elif command == "backups":
            for path in sorted(BACKUPS.glob("*.zip")):
                out(path.name)

        elif command == "logs":
            if FILES["logs"].exists():
                for line in FILES["logs"].read_text(encoding="utf-8").splitlines()[-40:]:
                    out(line)
            else:
                out("No logs.")

        elif command == "phone":
            phone_command(args)

        elif command == "clipboard":
            clipboard_command(args)

        elif command == "game":
            game_menu()

        elif command == "matrix":
            matrix_effect()

        elif command == "glitch":
            glitch_effect()

        elif command == "rainbow":
            rainbow_animation(" ".join(args) or "AURITERM", 30)

        elif command == "ambient":
            ambient_mode(args)

        elif command == "rainbowtoggle":
            config["rainbow"] = not config["rainbow"]
            save_json(FILES["config"], config)
            out("Rainbow: " + str(config["rainbow"]))

        elif command == "exit" or command == "quit":
            out("AuriTerm shutting down...")
            save_all()
            return False

        else:
            out("Unknown command: " + parts[0], "red")
            out("Type -help.")

    except ZeroDivisionError:
        out("Math error: division by zero.", "red")
    except KeyboardInterrupt:
        out("Command interrupted.", "yellow")
    except Exception as error:
        out(f"Error: {type(error).__name__}: {error}", "red")
        log(f"ERROR: {type(error).__name__}: {error}")

    return True

# ============================================================
# MAIN LOOP
# ============================================================

def main():
    banner()
    out("AuriTerm is alive.")
    out("65 AuriBot commands loaded.")
    out("UUID generator loaded.")
    out("DEMONING loaded.")
    out("Clipboard GET + SET loaded.")
    out("Type -help to explore.\n")

    while True:
        try:
            ambient_tick()

            if config.get("hackmode"):
                prompt = "AURI-ROOT# "
            else:
                prompt = "AURI> "

            raw = input(paint(prompt, "purple"))

            if not execute(raw):
                break

        except KeyboardInterrupt:
            print("\nUse -exit to close AuriTerm.")
        except EOFError:
            break

    save_all()
    out("AuriTerm closed.")

if __name__ == "__main__":
    main()