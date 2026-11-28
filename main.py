#!/usr/bin/env python3
# ============================================================
# AURITERM 2.3 — ALIVE + DEMONING + EXTREME EDITION
# 50+ NEW FEATURES | SINGLE FILE | TERMUX
# ============================================================

import os, sys, re, json, time, math, ast, shlex
import socket, hashlib, secrets, string, base64, random
import platform, datetime, subprocess, zipfile, shutil
import getpass, uuid, calendar, statistics, textwrap
import colorsys, threading, urllib.parse
from pathlib import Path
from collections import Counter

VERSION = "2.3 ALIVE DEMONING EXTREME"
START_TIME = time.time()

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
    "aliases": {},
    "favorites": [],
}

def load_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default.copy()

def save_json(path, value):
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")
    temp.replace(path)

config = load_json(FILES["config"], DEFAULT_CONFIG)
notes = load_json(FILES["notes"], [])
todos = load_json(FILES["todos"], [])
history = load_json(FILES["history"], [])

if not isinstance(config, dict):
    config = DEFAULT_CONFIG.copy()

for key, value in DEFAULT_CONFIG.items():
    config.setdefault(key, value)

if not isinstance(notes, list): notes = []
if not isinstance(todos, list): todos = []
if not isinstance(history, list): history = []

# ============================================================
# COLOR ENGINE
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
    r, g, b = colorsys.hsv_to_rgb(h, 0.9, 1)
    return rgb(int(r*255), int(g*255), int(b*255))

def rainbow(text, speed=0.035):
    global HUE_OFFSET
    result = []
    for i, char in enumerate(str(text)):
        result.append(hue_color(i*speed) + char)
    HUE_OFFSET = (HUE_OFFSET + 0.025) % 1
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

def clear_screen():
    os.system("clear" if os.name != "nt" else "cls")

def rainbow_animation(text, frames=30, delay=0.07):
    global HUE_OFFSET
    for _ in range(frames):
        print("\r" + rainbow(text), end="", flush=True)
        time.sleep(delay)
        HUE_OFFSET = (HUE_OFFSET + 0.045) % 1
    print()

# ============================================================
# FULLSCREEN VISUAL ENGINE
# ============================================================

def fullscreen_visual():
    chars = "01ABCDEF#$%&▓▒░"
    width = max(30, min(shutil.get_terminal_size((80, 24)).columns, 120))
    height = max(10, min(shutil.get_terminal_size((80, 24)).lines - 2, 35))
    drops = [random.randint(0, height) for _ in range(width)]
    particles = [
        [random.randrange(width), random.randrange(height)]
        for _ in range(25)
    ]
    frame = 0
    paused = False
    demoning_visual = False

    logo = [
        "   █████╗ ██╗   ██╗██████╗ ██╗",
        "  ██╔══██╗██║   ██║██╔══██╗██║",
        "  ███████║██║   ██║██████╔╝██║",
        "  ██╔══██║██║   ██║██╔══██╗██║",
        "  ██║  ██║╚██████╔╝██║  ██║██║",
    ]

    try:
        import select
        import termios
        import tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setcbreak(fd)

        while True:
            if select.select([sys.stdin], [], [], 0)[0]:
                key = sys.stdin.read(1).lower()
                if key == "q":
                    break
                elif key == " ":
                    paused = not paused
                elif key == "d":
                    demoning_visual = not demoning_visual

            if not paused:
                screen = [[" " for _ in range(width)] for _ in range(height)]

                for x in range(width):
                    y = drops[x]
                    if 0 <= y < height:
                        screen[y][x] = random.choice(chars)
                    drops[x] += 1
                    if drops[x] > height + random.randint(2, 12):
                        drops[x] = random.randint(-height, 0)

                for particle in particles:
                    x, y = particle
                    if 0 <= x < width and 0 <= y < height:
                        screen[y][x] = "·"
                    particle[1] = (particle[1] - 1) % height
                    if random.random() < 0.08:
                        particle[0] = random.randrange(width)

                print(CLEAR, end="")
                for line in logo:
                    print(rainbow(line))
                print(rainbow("       AURITERM 2.3 — FULLSCREEN ALIVE"))
                print()

                for row in screen:
                    print(rainbow("".join(row)))

                mode = "DEMONING VISUALS" if demoning_visual else "MATRIX + PARTICLES"
                state = "PAUSED" if paused else "RUNNING"
                print(paint(f"{mode} | {state} | Q EXIT | SPACE PAUSE | D TOGGLE"))
                frame += 1
                time.sleep(0.06)

    except Exception as error:
        out("Fullscreen animation unavailable: " + str(error), "yellow")
    finally:
        try:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except Exception:
            pass
        clear_screen()
        out("Returned to AuriTerm.")

def living_background(seconds=5):
    width = max(30, min(shutil.get_terminal_size((70, 20)).columns, 100))
    symbols = " .:*+x01░▒▓"
    start = time.time()
    frame = 0
    try:
        while time.time() - start < seconds:
            line = []
            for x in range(width):
                wave = math.sin(x*0.18 + frame*0.25)
                value = int((wave+1)*4.5)
                line.append(symbols[value])
            print("\r" + rainbow("".join(line)), end="", flush=True)
            frame += 1
            time.sleep(0.06)
        print()
    except KeyboardInterrupt:
        print()

def ambient_tick():
    if config.get("ambient", True):
        frames = ["◐", "◓", "◑", "◒"]
        print(paint(frames[int(time.time()*4) % 4], "purple"), end=" ")

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
    out("              OWNER: AURI", "purple")
    out("       ALIVE BACKGROUND ENGINE: ONLINE", "green")
    out("       DEMONING COMMAND SYSTEM: ONLINE", "green")
    print()

# ============================================================
# PROFILE / XP / ACHIEVEMENTS
# ============================================================

RANKS = [
    (0, "ROOKIE"), (50, "SCRIPT KID"), (150, "CODE RUNNER"),
    (300, "TERMINAL USER"), (600, "SYSTEM EXPLORER"),
    (1000, "DEMONING MEMBER"), (1800, "AURI ENGINEER"),
    (3000, "AURI MASTER"), (5000, "LEGENDARY"),
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
    "visual": "Fullscreen Activated",
}

def update_rank():
    config["rank"] = "ROOKIE"
    for points, name in RANKS:
        if config.get("xp", 0) >= points:
            config["rank"] = name

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
    ast.Add: lambda a,b: a+b,
    ast.Sub: lambda a,b: a-b,
    ast.Mult: lambda a,b: a*b,
    ast.Div: lambda a,b: a/b,
    ast.FloorDiv: lambda a,b: a//b,
    ast.Mod: lambda a,b: a%b,
    ast.Pow: lambda a,b: a**b,
}

def calc(expression):
    if len(expression) > 250:
        raise ValueError("Expression too long.")
    tree = ast.parse(expression, mode="eval")

    def walk(node):
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int,float)) and not isinstance(node.value,bool):
                return node.value
        if isinstance(node, ast.UnaryOp):
            value = walk(node.operand)
            if isinstance(node.op, ast.USub): return -value
            if isinstance(node.op, ast.UAdd): return value
        if isinstance(node, ast.BinOp):
            operation = OPS.get(type(node.op))
            if operation is None: raise ValueError("Unsupported operator.")
            left, right = walk(node.left), walk(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 10:
                raise ValueError("Exponent too large.")
            result = operation(left, right)
            if isinstance(result,(int,float)) and abs(result)>10**100:
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
    if kind == "uuid": uuid_command()
    elif kind == "hex": out(secrets.token_hex(16))
    elif kind == "token": out(secrets.token_urlsafe(32))
    elif kind == "number": out(str(secrets.randbelow(10**12)))
    elif kind == "password": password_generator(args[1] if len(args)>1 else "24")
    elif kind == "batch":
        count = min(100, max(1, int(args[1]) if len(args)>1 else 10))
        for _ in range(count): out(str(uuid.uuid4()))
    elif kind == "color":
        out("#{0:06X}".format(random.randint(0,0xFFFFFF)))
    elif kind == "name":
        first = ["Auri","Pixel","Nova","Echo","Luna","Byte","Cocoa"]
        second = ["OS","Term","Core","Bot","Dev","X","Engine"]
        out(random.choice(first)+random.choice(second))
    else:
        out("Types: uuid, hex, token, number, password, batch, color, name")

def password_generator(length="20"):
    try:
        size = int(length)
        if not 8 <= size <= 128: raise ValueError
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*_-+="
        out("".join(secrets.choice(alphabet) for _ in range(size)), "green")
    except Exception:
        out("Usage: -passgen 20 (8–128)")

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
        out(f"Disk total: {disk.total//1024**3} GB")
        out(f"Disk free: {disk.free//1024**3} GB")
    except Exception:
        pass

def network_info():
    out("Hostname: " + socket.gethostname())
    try:
        for item in sorted({x[4][0] for x in socket.getaddrinfo(socket.gethostname(),None)}):
            out("Local address: " + item)
    except Exception as error:
        out(str(error))

def dns_lookup(domain):
    if not re.fullmatch(r"[A-Za-z0-9.-]{1,253}", domain or ""):
        out("Usage: -dns example.com")
        return
    try:
        for item in sorted({x[4][0] for x in socket.getaddrinfo(domain,None)}):
            out(item)
    except Exception as error:
        out("DNS error: " + str(error))

def local_ping():
    try:
        result = subprocess.run(["ping","-c","1","127.0.0.1"],capture_output=True,text=True,timeout=5)
        out(result.stdout or result.stderr)
    except Exception as error:
        out("Ping unavailable: " + str(error))

def port_check(port):
    try:
        port = int(port)
        if not 1 <= port <= 65535: raise ValueError
        with socket.create_connection(("127.0.0.1",port),timeout=1):
            out(f"Local port {port}: OPEN")
    except Exception:
        out("Local port closed or invalid.")

def process_view():
    out("Process viewer:")
    try:
        if shutil.which("ps"):
            result = subprocess.run(["ps","-A"],capture_output=True,text=True,timeout=5)
            print(result.stdout[:7000])
        else:
            out("ps unavailable.")
    except Exception as error:
        out(str(error))

def environment_view():
    for key,value in sorted(os.environ.items()):
        out(f"{key}={value}")

def python_modules():
    modules = sorted(sys.modules.keys())
    out("Loaded modules: " + str(len(modules)))
    for module in modules[:100]:
        out(module)

def folder_size(name="."):
    try:
        path = safe_path(name)
        total = sum(p.stat().st_size for p in path.rglob("*") if p.is_file())
        out(f"{path.name}: {total:,} bytes")
    except Exception as error:
        out(str(error))

def search_files(query):
    if not query:
        out("Usage: -findfile NAME")
        return
    matches = 0
    for path in ROOT.rglob("*"):
        if path.is_file() and query.lower() in path.name.lower():
            out(str(path.relative_to(ROOT)))
            matches += 1
            if matches >= 100: break
    out(f"Matches: {matches}")

def json_view(name):
    try:
        data = json.loads(safe_path(name).read_text(encoding="utf-8"))
        print(json.dumps(data,indent=2,ensure_ascii=False))
    except Exception as error:
        out("JSON error: " + str(error))

def json_format(name):
    try:
        path = safe_path(name)
        data = json.loads(path.read_text(encoding="utf-8"))
        path.write_text(json.dumps(data,indent=4,ensure_ascii=False),encoding="utf-8")
        out("JSON formatted.")
    except Exception as error:
        out(str(error))

def text_stats(name):
    try:
        data = safe_path(name).read_text(encoding="utf-8")
        out("Characters: " + str(len(data)))
        out("Words: " + str(len(data.split())))
        out("Lines: " + str(len(data.splitlines())))
        out("Unique words: " + str(len(set(data.split()))))
    except Exception as error:
        out(str(error))

def duplicate_finder():
    seen = {}
    duplicates = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or DATA in path.parents:
            continue
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest in seen:
                duplicates.append((seen[digest],path))
            else:
                seen[digest] = path
        except OSError:
            pass
    if not duplicates:
        out("No duplicate files found.")
    for first,second in duplicates:
        out(f"{first.name} = {second.name}")

# ============================================================
# FILE TOOLS
# ============================================================

def file_hash(name):
    try:
        digest = hashlib.sha256()
        with safe_path(name).open("rb") as file:
            for chunk in iter(lambda:file.read(65536),b""):
                digest.update(chunk)
        out(digest.hexdigest())
    except Exception as error:
        out("Hash error: " + str(error))

def hex_view(name):
    try:
        data = safe_path(name).read_bytes()[:512]
        for offset in range(0,len(data),16):
            chunk = data[offset:offset+16]
            hx = " ".join(f"{b:02X}" for b in chunk)
            txt = "".join(chr(b) if 32<=b<127 else "." for b in chunk)
            out(f"{offset:08X} {hx:<47} {txt}")
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

def write_file(name,content,force=False):
    try:
        path = safe_path(name)
        if path.exists() and not force:
            out("File exists. Use -writeforce to replace.")
            return
        path.write_text(content,encoding="utf-8")
        out("Saved " + path.name)
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
        notes.append({"text":text,"time":time.time()})
        save_json(FILES["notes"],notes)
        achievement("note")
        out("Note saved.")
    elif action == "list":
        for i,item in enumerate(notes,1): out(f"{i}. {item['text']}")
        if not notes: out("No notes.")
    elif action == "delete":
        try:
            removed = notes.pop(int(args[1])-1)
            save_json(FILES["notes"],notes)
            out("Deleted: "+removed["text"])
        except Exception: out("Usage: -note delete NUMBER")
    elif action == "clear":
        if input("Type YES to clear notes: ") == "YES":
            notes.clear()
            save_json(FILES["notes"],notes)
            out("Notes cleared.")

def todo_command(args):
    action = args[0].lower() if args else "list"
    if action == "add":
        text = " ".join(args[1:])
        if not text: out("Usage: -todo add TEXT"); return
        todos.append({"text":text,"done":False})
        save_json(FILES["todos"],todos)
        out("Task added.")
    elif action == "list":
        for i,item in enumerate(todos,1):
            out(f"{i}. [{'X' if item['done'] else ' '}] {item['text']}")
        if not todos: out("No tasks.")
    elif action == "done":
        try:
            todos[int(args[1])-1]["done"] = True
            save_json(FILES["todos"],todos)
            out("Task completed.")
        except Exception: out("Usage: -todo done NUMBER")
    elif action == "delete":
        try:
            item = todos.pop(int(args[1])-1)
            save_json(FILES["todos"],todos)
            out("Deleted: "+item["text"])
        except Exception: out("Usage: -todo delete NUMBER")
    elif action == "clear":
        if input("Type YES to clear tasks: ") == "YES":
            todos.clear()
            save_json(FILES["todos"],todos)
            out("Tasks cleared.")

# ============================================================
# TERMUX CLIPBOARD / PHONE
# ============================================================

def clipboard_command(args):
    action = args[0].lower() if args else "get"
    if action in ("get","read"):
        executable = shutil.which("termux-clipboard-get")
        if not executable:
            out("Missing Termux:API clipboard command.", "red")
            return
        try:
            result = subprocess.run([executable],capture_output=True,text=True,timeout=10)
            out(result.stdout.rstrip("\n") or "[Clipboard empty]")
        except Exception as error: out(str(error),"red")
    elif action in ("set","copy"):
        text = " ".join(args[1:])
        if not text: out("Usage: -clipboard set TEXT"); return
        executable = shutil.which("termux-clipboard-set")
        if not executable: out("Missing Termux:API clipboard command.","red"); return
        try:
            result = subprocess.run([executable],input=text,capture_output=True,text=True,timeout=10)
            out("Copied!" if result.returncode == 0 else result.stderr)
        except Exception as error: out(str(error),"red")

def run_termux_api(cmd):
    if not shutil.which(cmd[0]):
        out("Missing Termux:API command: "+cmd[0],"red")
        return
    try:
        result = subprocess.run(cmd,capture_output=True,text=True,timeout=15)
        out(result.stdout.strip() or "Done." if result.returncode == 0 else result.stderr)
    except Exception as error: out("API error: "+str(error),"red")

def vibrate_command(args):
    try:
        duration = max(1,min(10000,int(args[0])))
        run_termux_api(["termux-vibrate","-d",str(duration),"-f"])
    except Exception:
        out("Usage: -vibrate 5000")

def phone_command(args):
    if not args: out("Usage: -phone battery|torch on|off|vibrate MS"); return
    action = args[0].lower()
    if action == "battery":
        run_termux_api(["termux-battery-status"])
    elif action == "torch":
        if len(args)<2 or args[1].lower() not in ("on","off"):
            out("Usage: -phone torch on|off"); return
        run_termux_api(["termux-torch",args[1].lower()])
    elif action == "vibrate":
        vibrate_command(args[1:])
    else: out("Unknown phone action.")

def termux_command(args):
    if args and args[0].lower() == "vibrate":
        vibrate_command(args[1:])
    else:
        out("Usage: -termux vibrate MS")

# ============================================================
# UTILITIES — 50+ ADDITIONS
# ============================================================

def timer_command(args):
    try:
        seconds = min(3600,max(1,int(args[0])))
        while seconds:
            print(f"\rTIMER: {seconds:04d}s",end="",flush=True)
            time.sleep(1)
            seconds -= 1
        print("\nTIMER FINISHED!")
    except Exception: out("Usage: -timer SECONDS")

def stopwatch():
    out("Stopwatch running. Press ENTER to stop.")
    start = time.time()
    try: input()
    except KeyboardInterrupt: pass
    out(f"Elapsed: {time.time()-start:.3f} seconds")

def date_info():
    now = datetime.datetime.now()
    out("Date: "+now.strftime("%Y-%m-%d"))
    out("Time: "+now.strftime("%H:%M:%S"))
    out("Weekday: "+now.strftime("%A"))
    out("Day of year: "+str(now.timetuple().tm_yday))
    out("ISO week: "+str(now.isocalendar().week))

def convert_command(args):
    try:
        n = float(args[0])
        unit = args[1].lower()
        conversions = {
            "km-mi": n*0.621371,
            "mi-km": n/0.621371,
            "c-f": n*9/5+32,
            "f-c": (n-32)*5/9,
            "kg-lb": n*2.20462,
            "lb-kg": n/2.20462,
            "m-ft": n*3.28084,
            "ft-m": n/3.28084,
            "cm-in": n/2.54,
            "in-cm": n*2.54,
        }
        if unit not in conversions: raise ValueError
        out(str(conversions[unit]))
    except Exception:
        out("Units: km-mi, mi-km, c-f, f-c, kg-lb, lb-kg, m-ft, ft-m, cm-in, in-cm")

def regex_test(args):
    try:
        pattern = args[0]
        text = " ".join(args[1:])
        matches = re.findall(pattern,text)
        out("Matches: "+str(matches))
    except Exception as error: out("Regex error: "+str(error))

def url_encode(args):
    out(urllib.parse.quote(" ".join(args),safe=""))

def url_decode(args):
    out(urllib.parse.unquote(" ".join(args)))

def color_info():
    color = "#{:06X}".format(random.randint(0,0xFFFFFF))
    out("Random color: "+color)
    out("RGB: "+str(tuple(int(color[i:i+2],16) for i in (1,3,5))))

def sequence(args):
    try:
        start = int(args[0]); end = int(args[1])
        step = int(args[2]) if len(args)>2 else 1
        if step == 0: raise ValueError
        values = list(range(start,end,step))[:500]
        out(" ".join(map(str,values)))
    except Exception: out("Usage: -sequence START END [STEP]")

def word_scramble():
    words = ["terminal","rainbow","python","auriterm","matrix","keyboard","developer"]
    word = random.choice(words)
    scrambled = "".join(random.sample(word,len(word)))
    out("Unscramble: "+scrambled)
    answer = input("ANSWER> ").strip().lower()
    out("Correct!" if answer == word else "Answer: "+word)

def reaction_test():
    out("Wait for GO...")
    time.sleep(random.uniform(2,5))
    out("GO!")
    start = time.time()
    input()
    out(f"Reaction time: {(time.time()-start)*1000:.0f} ms")

def trivia_game():
    questions = [
        ("What language is AuriTerm written in?","python"),
        ("What does UUID stand for?","universally unique identifier"),
        ("What does CPU stand for?","central processing unit"),
    ]
    score = 0
    for question,answer in questions:
        guess = input(question+" ").strip().lower()
        if guess == answer:
            out("Correct!")
            score += 1
        else: out("Answer: "+answer)
    out(f"Score: {score}/{len(questions)}")
    award_xp(score*5)

def dice_battle():
    player = random.randint(1,6)
    computer = random.randint(1,6)
    out(f"You: {player} | Computer: {computer}")
    out("YOU WIN!" if player>computer else "DRAW!" if player==computer else "Computer wins.")

def memory_game():
    sequence = [str(random.randint(0,9)) for _ in range(5)]
    out("Remember: "+" ".join(sequence))
    time.sleep(2)
    clear_screen()
    guess = input("Repeat the numbers: ").split()
    if guess == sequence:
        out("PERFECT!")
        award_xp(20)
    else: out("Not quite. Sequence: "+" ".join(sequence))

def initials(args):
    out("".join(word[0].upper() for word in args if word))

def text_reverse(args):
    out(" ".join(args)[::-1])

def text_analyze(args):
    text = " ".join(args)
    out("Characters: "+str(len(text)))
    out("Words: "+str(len(text.split())))
    out("Vowels: "+str(sum(c.lower() in "aeiou" for c in text)))
    out("Digits: "+str(sum(c.isdigit() for c in text)))
    out("Spaces: "+str(text.count(" ")))

def hash_text(args):
    out(hashlib.sha256(" ".join(args).encode()).hexdigest())

def base64_encode(args):
    out(base64.b64encode(" ".join(args).encode()).decode())

def base64_decode(args):
    try: out(base64.b64decode(" ".join(args),validate=True).decode())
    except Exception: out("Invalid Base64.")

def json_string(args):
    try:
        data = json.loads(" ".join(args))
        print(json.dumps(data,indent=4,ensure_ascii=False))
    except Exception as error: out("JSON error: "+str(error))

def countdown(args):
    timer_command(args)

def uptime():
    elapsed = int(time.time()-START_TIME)
    out(f"Uptime: {elapsed//3600}h {(elapsed%3600)//60}m {elapsed%60}s")

def alias_command(args):
    if not args:
        for key,value in config["aliases"].items(): out(f"{key} = {value}")
        return
    if len(args)<2:
        out("Usage: -alias NAME COMMAND")
        return
    config["aliases"][args[0]] = " ".join(args[1:])
    save_json(FILES["config"],config)
    out("Alias saved.")

def favorite_command(args):
    favorites = config.setdefault("favorites",[])
    if not args:
        for item in favorites: out(item)
        return
    command = " ".join(args)
    if command not in favorites:
        favorites.append(command)
        save_json(FILES["config"],config)
        out("Favorite saved.")
    else:
        favorites.remove(command)
        save_json(FILES["config"],config)
        out("Favorite removed.")

def command_search(args):
    query = " ".join(args).lower()
    if not query: out("Usage: -search COMMAND"); return
    names = sorted(COMMANDS)
    found = [name for name in names if query in name]
    for name in found: out("-"+name)
    out("Results: "+str(len(found)))

def backup_command():
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    destination = BACKUPS / f"backup_{stamp}.zip"
    try:
        with zipfile.ZipFile(destination,"w",zipfile.ZIP_DEFLATED) as archive:
            for path in ROOT.rglob("*"):
                if path.is_file() and DATA not in path.parents:
                    archive.write(path,path.relative_to(ROOT))
        out("Backup created: "+destination.name)
        achievement("backup")
    except Exception as error: out("Backup error: "+str(error))

def backups_command():
    files = sorted(BACKUPS.glob("*.zip"))
    if not files: out("No backups.")
    for path in files: out(path.name)

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

def simulated_trace():
    out("SIMULATED TRACE — no external route scan")
    for item in ("LOCAL DEVICE","LOCAL ROUTER","GATEWAY","DESTINATION"):
        out("-> "+item)
        time.sleep(0.2)

# ============================================================
# DEMONING
# ============================================================

DEMONING_HISTORY = []

DEMONING_INDEX = [
    "about","status","syscheck","whoami","rootcheck","terminal",
    "hackmode","netinfo","ipinfo","dns","ping","portcheck","netmap",
    "trace","hash","hashfile","hexview","filecheck","keygen","passgen",
    "encode","decode","encrypt","decrypt","calc","note","todo",
    "backup","backups","logs","phone","clipboard","uuid","generator",
    "timestamp","calendar","game","matrix","glitch","rainbow","ambient",
    "bot","clear","help","commands","visual","timer","stopwatch",
    "process","environment","modules","findfile","folder-size",
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
    for i,name in enumerate(DEMONING_INDEX,1): out(f"{i:02}. -{name}")
    out("Indexed commands: "+str(len(DEMONING_INDEX)))

def demon_search(args):
    query = " ".join(args).lower()
    matches = [name for name in DEMONING_INDEX if query in name]
    for name in matches: out("[FOUND] -"+name)
    if not matches: out("No matches.")

def demon_run(args):
    if not args: out("Usage: -demoning run COMMAND"); return
    name = args[0].lower().lstrip("-")
    if name not in DEMONING_INDEX:
        out("Command not indexed.","red")
        return
    DEMONING_HISTORY.append(name)
    out("[DEMONING] Running -"+name)
    execute("-"+name+(" "+shlex.join(args[1:]) if len(args)>1 else ""))

def demoning(args):
    achievement("demon")
    if not args: demon_help(); return
    action,rest = args[0].lower(),args[1:]
    if action == "help": demon_help()
    elif action == "list": demon_list()
    elif action == "search": demon_search(rest)
    elif action == "run": demon_run(rest)
    elif action == "random": out("Try: -"+random.choice(DEMONING_INDEX))
    elif action == "stats":
        out("Indexed: "+str(len(DEMONING_INDEX)))
        out("Executed: "+str(len(DEMONING_HISTORY)))
        out("Unique: "+str(len(set(DEMONING_HISTORY))))
    elif action == "history":
        for i,name in enumerate(DEMONING_HISTORY,1): out(f"{i}. -{name}")
    elif action == "exit": out("Returning to AuriTerm.")
    else: out("Unknown DEMONING command. Use -demoning help.")

# ============================================================
# AURIBOT
# ============================================================

JOKES = [
    "Why did the programmer quit? Too many bugs.",
    "There are 10 types of people: binary readers and everyone else.",
    "A SQL query walks into a bar and asks: can I join you?",
]
QUOTES = [
    "Every great project starts with one line.",
    "Build something that makes you curious.",
    "Small progress is still progress.",
]
FACTS = [
    "Python was first released in 1991.",
    "ASCII originally used 7 bits per character.",
    "UUIDs are designed to identify items uniquely.",
]

BOT_COMMANDS = [
    "joke","quote","motivate","fact","coin","dice","roll","choose",
    "number","color","rainbow","banner","status","system","python",
    "platform","uptime","disk","folders","files","pwd","whoami",
    "weekday","month","year","timestamp","calendar","countdown",
    "add","subtract","multiply","divide","square","cube","sqrt",
    "power","percent","reverse","upper","lower","title","length",
    "words","chars","palindrome","vowels","consonants","initials",
    "repeat","shuffle","sort","unique","encode","decode","hash","uuid",
]

def auribot(args):
    if not args:
        out("Usage: -bot COMMAND")
        return
    action = args[0].lower()
    values = args[1:]
    text_value = " ".join(values)
    if action == "help":
        for item in BOT_COMMANDS: out(item)
    elif action == "joke": out(random.choice(JOKES))
    elif action == "quote": out(random.choice(QUOTES))
    elif action == "motivate": out("Keep building. One bug at a time!")
    elif action == "fact": out(random.choice(FACTS))
    elif action == "coin": out(random.choice(["HEADS","TAILS"]))
    elif action == "dice": out(str(random.randint(1,6)))
    elif action == "roll":
        try: out(str(random.randint(1,max(1,int(values[0])))))
        except Exception: out("Usage: -bot roll 100")
    elif action == "choose":
        out(random.choice(values) if len(values)>1 else "Give me at least two choices.")
    elif action == "number": out(str(random.randint(0,999999)))
    elif action == "color": color_info()
    elif action == "rainbow": rainbow_animation(text_value or "AURITERM")
    elif action == "banner": banner()
    elif action == "status": show_status()
    elif action in ("system","platform"): system_info()
    elif action == "python": out(sys.version)
    elif action == "uptime": uptime()
    elif action == "disk":
        usage = shutil.disk_usage(ROOT)
        out(f"Total {usage.total//1024**3} GB | Free {usage.free//1024**3} GB")
    elif action in ("folders","files","pwd","ls"):
        if action == "pwd": out(str(ROOT))
        else: list_files()
    elif action in ("whoami","username"): out(str(config["username"]))
    elif action == "weekday": out(datetime.datetime.now().strftime("%A"))
    elif action == "month": out(datetime.datetime.now().strftime("%B"))
    elif action == "year": out(str(datetime.datetime.now().year))
    elif action == "timestamp": out(str(int(time.time())))
    elif action == "calendar":
        now = datetime.datetime.now()
        print(calendar.month(now.year,now.month))
    elif action == "countdown": countdown(values)
    elif action in ("add","subtract","multiply","divide"):
        try:
            a,b = float(values[0]),float(values[1])
            result = {
                "add":a+b,"subtract":a-b,
                "multiply":a*b,"divide":a/b,
            }[action]
            out(str(result))
        except Exception: out("Usage: -bot add 5 2")
    elif action in ("square","cube","sqrt"):
        try:
            n = float(values[0])
            out(str(n*n if action=="square" else n*n*n if action=="cube" else math.sqrt(n)))
        except Exception: out("Usage: -bot square 5")
    elif action == "power":
        try: out(str(float(values[0])**float(values[1])))
        except Exception: out("Usage: -bot power 2 8")
    elif action == "percent":
        try: out(str(float(values[0])*float(values[1])/100))
        except Exception: out("Usage: -bot percent 20 80")
    elif action == "reverse": text_reverse(values)
    elif action == "upper": out(text_value.upper())
    elif action == "lower": out(text_value.lower())
    elif action == "title": out(text_value.title())
    elif action in ("length","chars"): out(str(len(text_value)))
    elif action == "words": out(str(len(values)))
    elif action == "palindrome":
        cleaned = re.sub(r"[^a-z0-9]","",text_value.lower())
        out("YES" if cleaned==cleaned[::-1] else "NO")
    elif action == "vowels": out(str(sum(c.lower() in "aeiou" for c in text_value)))
    elif action == "consonants": out(str(sum(c.isalpha() and c.lower() not in "aeiou" for c in text_value)))
    elif action == "initials": initials(values)
    elif action == "repeat":
        try: out(" ".join(values[1:])*min(100,max(1,int(values[0]))))
        except Exception: out("Usage: -bot repeat 3 hello")
    elif action == "shuffle":
        chars = list(text_value); random.shuffle(chars); out("".join(chars))
    elif action == "sort": out(" ".join(sorted(values)))
    elif action == "unique": out(" ".join(dict.fromkeys(values)))
    elif action == "encode": base64_encode(values)
    elif action == "decode": base64_decode(values)
    elif action == "hash": hash_text(values)
    elif action == "uuid": uuid_command()
    else: out("Unknown AuriBot command.")

# ============================================================
# STATUS / HELP
# ============================================================

def show_status():
    out("\n========== AURITERM STATUS ==========")
    out("Version: "+VERSION)
    out("Username: "+str(config["username"]))
    out("Rainbow: "+str(config["rainbow"]))
    out("Ambient: "+str(config["ambient"]))
    out("Hack mode: "+str(config["hackmode"]))
    out("Commands used: "+str(config["commands_used"]))
    out("XP: "+str(config["xp"]))
    out("Rank: "+str(config["rank"]))
    out("Notes: "+str(len(notes)))
    out("Tasks: "+str(len(todos)))
    out("DEMONING runs: "+str(len(DEMONING_HISTORY)))
    out("=====================================")

def show_help():
    out("""
================ AURITERM 2.3 HELP ================

CORE
-help -about -status -syscheck -profile
-achievements -hackmode -clear -exit

DEMONING
-demoning help|list|search|run|random|stats|history

GENERATORS
-uuid
-generator uuid|hex|token|number|password|batch|color|name
-passgen 24
-keygen

CALCULATOR
-calc 5 * (2 + 3)

FILES
-ls -read FILE -write FILE TEXT -writeforce FILE TEXT
-hashfile FILE -hexview FILE -filecheck FILE
-findfile NAME -folder-size [PATH]
-jsonview FILE -jsonformat FILE -textstats FILE
-duplicates

SYSTEM
-process -environment -modules -netinfo -ipinfo
-dns DOMAIN -ping -portcheck PORT -trace

PHONE
-phone battery
-phone torch on|off
-phone vibrate 5000
-termux vibrate 5000
-termux-vibrate 5000
-vibrate 5000
-clipboard get
-clipboard set TEXT

PERSONAL
-note add|list|delete|clear
-todo add|list|done|delete|clear
-backup -backups -logs
-alias NAME COMMAND
-favorite COMMAND
-search COMMAND

UTILITIES
-timer SECONDS
-stopwatch
-date
-uptime
-convert NUMBER UNIT
-sequence START END STEP
-regex PATTERN TEXT
-urlencode TEXT
-urldecode TEXT
-color
-initials WORDS
-reverse TEXT
-analyze TEXT
-json STRING

GAMES
-reaction
-trivia
-dicebattle
-memorygame
-scramble

VISUALS
-rainbow TEXT
-ambient
-matrix
-glitch
-visual
-fullscreen

===================================================
""")

# ============================================================
# COMMAND ROUTER
# ============================================================

def execute(raw):
    raw = raw.strip()
    if not raw: return True

    try:
        parts = shlex.split(raw)
    except ValueError as error:
        out("Input error: "+str(error),"red")
        return True

    command = parts[0].lower().lstrip("-")
    args = parts[1:]

    aliases = config.get("aliases",{})
    if command in aliases:
        raw = aliases[command] + (" "+shlex.join(args) if args else "")
        return execute(raw)

    config["commands_used"] += 1
    history.append({"time":time.time(),"command":raw})
    if len(history)>500: del history[:-500]
    save_json(FILES["config"],config)
    save_json(FILES["history"],history)
    log(raw)

    count = config["commands_used"]
    if count==1: achievement("first")
    if count>=10: achievement("ten")
    if count>=50: achievement("fifty")

    try:
        if command in ("help","commands"): show_help()
        elif command=="demoning": demoning(args)
        elif command=="bot": auribot(args)
        elif command=="about":
            out("AuriTerm "+VERSION)
            out("A colorful single-file terminal made for Auri.")
        elif command=="status": show_status()
        elif command in ("syscheck","system"): system_info()
        elif command in ("whoami","username"): out(str(config["username"]))
        elif command=="rootcheck":
            root = hasattr(os,"geteuid") and os.geteuid()==0
            out("Root: "+("YES" if root else "NO"))
        elif command=="terminal":
            out("Python: "+sys.version)
            out("Shell: "+os.environ.get("SHELL","Unknown"))
            out("Folder: "+str(ROOT))
        elif command=="hackmode":
            config["hackmode"] = not config["hackmode"]
            save_json(FILES["config"],config)
            out("Hack mode: "+str(config["hackmode"]))
        elif command=="profile": profile()
        elif command=="achievements": achievements()
        elif command in ("netinfo","ipinfo","netmap"): network_info()
        elif command=="dns": dns_lookup(args[0] if args else "")
        elif command=="ping": local_ping()
        elif command=="portcheck": port_check(args[0] if args else "")
        elif command=="trace": simulated_trace()
        elif command=="uuid": uuid_command()
        elif command=="generator": generator_command(args)
        elif command=="timestamp": out(str(int(time.time())))
        elif command=="calendar":
            now = datetime.datetime.now()
            print(calendar.month(now.year,now.month))
        elif command=="calc":
            if not args: out("Usage: -calc 5 * (2 + 3)")
            else: out(str(calc(" ".join(args))))
        elif command=="hash": hash_text(args)
        elif command=="hashfile": file_hash(args[0] if args else "")
        elif command=="hexview": hex_view(args[0] if args else "")
        elif command=="filecheck": file_check(args[0] if args else "")
        elif command=="ls": list_files()
        elif command=="read": read_file(args[0] if args else "")
        elif command=="write":
            if len(args)<2: out("Usage: -write FILE TEXT")
            else: write_file(args[0]," ".join(args[1:]))
        elif command=="writeforce":
            if len(args)<2: out("Usage: -writeforce FILE TEXT")
            else: write_file(args[0]," ".join(args[1:]),True)
        elif command=="keygen": out(secrets.token_hex(32))
        elif command=="passgen": password_generator(args[0] if args else "20")
        elif command=="encode": base64_encode(args)
        elif command=="decode": base64_decode(args)
        elif command=="encrypt":
            text = " ".join(args)
            out("Educational Caesar cipher; not secure encryption.")
            out("".join(chr((ord(c)-65+7)%26+65) if c.isupper() else chr((ord(c)-97+7)%26+97) if c.islower() else c for c in text))
        elif command=="decrypt":
            text = " ".join(args)
            out("Educational Caesar cipher; not secure encryption.")
            out("".join(chr((ord(c)-65-7)%26+65) if c.isupper() else chr((ord(c)-97-7)%26+97) if c.islower() else c for c in text))
        elif command=="note": note_command(args)
        elif command=="todo": todo_command(args)
        elif command=="backup": backup_command()
        elif command=="backups": backups_command()
        elif command=="logs":
            if FILES["logs"].exists():
                for line in FILES["logs"].read_text(encoding="utf-8").splitlines()[-40:]: out(line)
            else: out("No logs.")
        elif command=="phone": phone_command(args)
        elif command=="termux": termux_command(args)
        elif command in ("termux-vibrate","vibrate"): vibrate_command(args)
        elif command=="clipboard": clipboard_command(args)
        elif command=="matrix": matrix_effect()
        elif command=="glitch": glitch_effect()
        elif command=="rainbow": rainbow_animation(" ".join(args) or "AURITERM")
        elif command=="ambient":
            if args and args[0].lower() in ("on","off"):
                config["ambient"] = args[0].lower()=="on"
                save_json(FILES["config"],config)
                out("Ambient: "+str(config["ambient"]))
            else: living_background(8)
        elif command=="rainbowtoggle":
            config["rainbow"] = not config["rainbow"]
            save_json(FILES["config"],config)
            out("Rainbow: "+str(config["rainbow"]))
        elif command in ("visual","fullscreen"):
            achievement("visual")
            fullscreen_visual()
        elif command=="timer": timer_command(args)
        elif command=="stopwatch": stopwatch()
        elif command=="date": date_info()
        elif command=="uptime": uptime()
        elif command=="convert": convert_command(args)
        elif command=="sequence": sequence(args)
        elif command=="regex": regex_test(args)
        elif command=="urlencode": url_encode(args)
        elif command=="urldecode": url_decode(args)
        elif command=="color": color_info()
        elif command=="initials": initials(args)
        elif command=="reverse": text_reverse(args)
        elif command=="analyze": text_analyze(args)
        elif command=="json": json_string(args)
        elif command=="jsonview": json_view(args[0] if args else "")
        elif command=="jsonformat": json_format(args[0] if args else "")
        elif command=="textstats": text_stats(args[0] if args else "")
        elif command=="findfile": search_files(" ".join(args))
        elif command=="folder-size": folder_size(args[0] if args else ".")
        elif command=="duplicates": duplicate_finder()
        elif command=="process": process_view()
        elif command=="environment": environment_view()
        elif command=="modules": python_modules()
        elif command=="alias": alias_command(args)
        elif command=="favorite": favorite_command(args)
        elif command=="search": command_search(args)
        elif command=="reaction": reaction_test()
        elif command=="trivia": trivia_game()
        elif command=="dicebattle": dice_battle()
        elif command=="memorygame": memory_game()
        elif command=="scramble": word_scramble()
        elif command in ("clear","cls"): clear_screen()
        elif command in ("exit","quit"):
            out("AuriTerm shutting down...")
            save_all()
            return False
        else:
            out("Unknown command: "+parts[0],"red")
            out("Type -help.")
    except KeyboardInterrupt:
        out("Command interrupted.","yellow")
    except Exception as error:
        out(f"Error: {type(error).__name__}: {error}","red")
        log(f"ERROR: {type(error).__name__}: {error}")
    return True

# ============================================================
# MAIN LOOP
# ============================================================

def main():
    banner()
    out("AuriTerm is alive.")
    out("50+ new feature commands loaded.")
    out("UUID generator loaded.")
    out("DEMONING loaded.")
    out("Clipboard GET + SET loaded.")
    out("FOUR VIBRATION COMMANDS loaded.")
    out("Fullscreen visual engine loaded.")
    out("Type -help to explore.\n")

    while True:
        try:
            ambient_tick()
            prompt = "AURI-ROOT# " if config.get("hackmode") else "AURI> "
            raw = input(paint(prompt,"purple"))
            if not execute(raw): break
        except KeyboardInterrupt:
            print("\nUse -exit to close AuriTerm.")
        except EOFError:
            break

    save_all()
    out("AuriTerm closed.")

if __name__ == "__main__":
    main()