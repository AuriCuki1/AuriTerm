#!/usr/bin/env python3
# ============================================================
# AURITERM 2.2 — DEMONING EXTREME EDITION
# Single-file Android / Termux terminal
# Python 3.9+
# ============================================================

import os
import sys
import re
import json
import time
import math
import ast
import shlex
import socket
import hashlib
import secrets
import string
import base64
import random
import platform
import datetime
import subprocess
import zipfile
import getpass
import shutil
import textwrap
import statistics
import calendar
import uuid
from pathlib import Path
from collections import Counter

VERSION = "2.2 DEMONING EXTREME"
ROOT = Path(__file__).resolve().parent
DATA = ROOT / "auriterm_data"
BACKUPS = DATA / "backups"
LOGFILE = DATA / "auriterm.log"
NOTES_FILE = DATA / "notes.json"
TODOS_FILE = DATA / "todos.json"
CONFIG_FILE = DATA / "config.json"
HISTORY_FILE = DATA / "history.json"

for folder in (DATA, BACKUPS):
    folder.mkdir(parents=True, exist_ok=True)

DEFAULT_CONFIG = {
    "hackmode": False,
    "username": "Auri",
    "theme": "PURPLE",
    "commands_used": 0,
    "xp": 0,
    "rank": "ROOKIE",
    "achievements": [],
    "demon_mode": False
}

def load_json(path, default):
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
        return result
    except Exception:
        return default.copy() if isinstance(default, (dict, list)) else default

def save_json(path, data):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    temporary.replace(path)

config = load_json(CONFIG_FILE, DEFAULT_CONFIG)
notes = load_json(NOTES_FILE, [])
todos = load_json(TODOS_FILE, [])
history = load_json(HISTORY_FILE, [])

if not isinstance(config, dict):
    config = DEFAULT_CONFIG.copy()
if not isinstance(notes, list):
    notes = []
if not isinstance(todos, list):
    todos = []
if not isinstance(history, list):
    history = []

for key, value in DEFAULT_CONFIG.items():
    config.setdefault(key, value)

def log(message):
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with LOGFILE.open("a", encoding="utf-8") as file:
            file.write(f"[{stamp}] {message}\n")
    except OSError:
        pass

def save_all():
    save_json(CONFIG_FILE, config)
    save_json(NOTES_FILE, notes)
    save_json(TODOS_FILE, todos)
    save_json(HISTORY_FILE, history)

def clear_screen():
    os.system("clear" if os.name != "nt" else "cls")

def banner():
    clear_screen()
    print(r"""
    █████╗ ██╗   ██╗██████╗ ██╗████████╗███████╗██████╗
   ██╔══██╗██║   ██║██╔══██╗██║╚══██╔══╝██╔════╝██╔══██╗
   ███████║██║   ██║██████╔╝██║   ██║   █████╗  ██████╔╝
   ██╔══██║██║   ██║██╔══██╗██║   ██║   ██╔══╝  ██╔══██╗
   ██║  ██║╚██████╔╝██║  ██║██║   ██║   ███████╗██║  ██║
   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝

       ██████╗ ███████╗███╗   ███╗ ██████╗ ███╗   ██╗
       ██╔══██╗██╔════╝████╗ ████║██╔═══██╗████╗  ██║
       ██║  ██║█████╗  ██╔████╔██║██║   ██║██╔██╗ ██║
       ██║  ██║██╔══╝  ██║╚██╔╝██║██║   ██║██║╚██╗██║
       ██████╔╝███████╗██║ ╚═╝ ██║╚██████╔╝██║ ╚████║
       ╚═════╝ ╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
    """)
    print(f"       AuriTerm {VERSION}")
    print("       [ DEMONING SYSTEM ONLINE ]")
    print("       [ LOCAL TERMINAL READY ]")
    print("       Type -help for commands.\n")

def safe_path(name):
    target = (ROOT / name).resolve()
    if target != ROOT and ROOT not in target.parents:
        raise ValueError("Access denied: outside project directory.")
    return target

def run_termux_api(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(result.stdout.strip() or "Command completed.")
        else:
            print(result.stderr.strip() or "Command failed.")
    except FileNotFoundError:
        print("Termux:API command not found.")
        print("Install the Termux:API app and run: pkg install termux-api")
    except subprocess.TimeoutExpired:
        print("API command timed out.")
    except Exception as error:
        print("API error:", error)

# ============================================================
# XP / RANK / ACHIEVEMENTS
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
    (5000, "LEGENDARY")
]

ACHIEVEMENTS = {
    "first_command": "First Command",
    "ten_commands": "10 Commands Used",
    "fifty_commands": "50 Commands Used",
    "first_game": "First Game Played",
    "first_note": "First Note Saved",
    "first_backup": "First Backup Created",
    "demon_user": "DEMONING Activated",
    "matrix_user": "Matrix Initiated",
    "file_inspector": "File Inspector"
}

def update_rank():
    xp = int(config.get("xp", 0))
    rank = "ROOKIE"
    for threshold, name in RANKS:
        if xp >= threshold:
            rank = name
    config["rank"] = rank

def award_xp(amount):
    config["xp"] = int(config.get("xp", 0)) + amount
    update_rank()
    save_json(CONFIG_FILE, config)

def achievement(name):
    unlocked = config.get("achievements", [])
    if name not in unlocked and name in ACHIEVEMENTS:
        unlocked.append(name)
        config["achievements"] = unlocked
        save_json(CONFIG_FILE, config)
        print("[ACHIEVEMENT UNLOCKED]", ACHIEVEMENTS[name])

def show_profile():
    update_rank()
    print("\n========== AURI PROFILE ==========")
    print("Username:", config.get("username"))
    print("Rank:", config.get("rank"))
    print("XP:", config.get("xp"))
    print("Commands used:", config.get("commands_used"))
    print("Achievements:", len(config.get("achievements", [])))
    print("==================================")

def show_achievements():
    print("\n========== ACHIEVEMENTS ==========")
    unlocked = config.get("achievements", [])
    for key, title in ACHIEVEMENTS.items():
        marker = "[UNLOCKED]" if key in unlocked else "[LOCKED]"
        print(f"{marker} {title}")
    print("=================================")

# ============================================================
# SAFE CALCULATOR
# ============================================================

ALLOWED_OPS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.FloorDiv: lambda a, b: a // b,
    ast.Mod: lambda a, b: a % b,
    ast.Pow: lambda a, b: a ** b
}

def calculate(expression):
    if len(expression) > 250:
        raise ValueError("Expression too long.")

    tree = ast.parse(expression, mode="eval")

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                raise ValueError("Boolean values are not allowed.")
            if isinstance(node.value, (int, float)):
                return node.value

        if isinstance(node, ast.UnaryOp):
            value = evaluate(node.operand)
            if isinstance(node.op, ast.USub):
                return -value
            if isinstance(node.op, ast.UAdd):
                return value

        if isinstance(node, ast.BinOp):
            operation = ALLOWED_OPS.get(type(node.op))
            if operation is None:
                raise ValueError("Operator not allowed.")

            left = evaluate(node.left)
            right = evaluate(node.right)

            if isinstance(node.op, ast.Pow) and abs(right) > 10:
                raise ValueError("Exponent too large.")

            result = operation(left, right)

            if isinstance(result, (int, float)) and abs(result) > 10**100:
                raise ValueError("Result too large.")

            return result

        raise ValueError("Invalid calculation.")

    return evaluate(tree)

# ============================================================
# SYSTEM INFORMATION
# ============================================================

def system_info():
    print("\n========== SYSTEM REPORT ==========")
    print("Platform:", platform.platform())
    print("System:", platform.system())
    print("Release:", platform.release())
    print("Machine:", platform.machine())
    print("Python:", platform.python_version())
    print("Executable:", sys.executable)
    print("Hostname:", socket.gethostname())
    print("Process ID:", os.getpid())
    print("Current folder:", ROOT)

    try:
        usage = shutil.disk_usage(ROOT)
        print("\nDisk:")
        print("Total:", usage.total // (1024**3), "GB")
        print("Used:", usage.used // (1024**3), "GB")
        print("Free:", usage.free // (1024**3), "GB")
    except Exception as error:
        print("Disk information unavailable:", error)

    print("===================================")

def network_info():
    hostname = socket.gethostname()
    print("\n========== LOCAL NETWORK ==========")
    print("Hostname:", hostname)

    try:
        addresses = socket.getaddrinfo(hostname, None)
        unique = sorted({item[4][0] for item in addresses})
        for address in unique:
            print("Address:", address)
    except Exception as error:
        print("Address lookup failed:", error)

    print("===================================")

def dns_lookup(domain):
    if not domain or len(domain) > 253:
        print("Usage: -dns example.com")
        return

    if not re.fullmatch(r"[A-Za-z0-9.-]+", domain):
        print("Invalid domain format.")
        return

    try:
        results = socket.getaddrinfo(domain, None)
        addresses = sorted({item[4][0] for item in results})
        print(f"\nDNS results for {domain}:")
        for address in addresses:
            print(" ", address)
    except socket.gaierror:
        print("DNS lookup failed.")

def local_ping():
    print("Checking localhost...")
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "127.0.0.1"],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(result.stdout.strip() or result.stderr.strip())
        print("Result:", "OK" if result.returncode == 0 else "FAILED")
    except FileNotFoundError:
        print("ping is not installed.")
    except Exception as error:
        print("Ping error:", error)

def local_portcheck(port_text):
    try:
        port = int(port_text)
        if not 1 <= port <= 65535:
            raise ValueError
    except Exception:
        print("Usage: -portcheck 8080")
        return

    print(f"Checking localhost port {port}...")
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1):
            print("OPEN on this device.")
    except OSError:
        print("CLOSED or unavailable on this device.")

def simulated_trace():
    print("\n========== SIMULATED TRACE ==========")
    print("This is an animation, not a real route scan.")
    nodes = [
        "LOCAL DEVICE",
        "LOCAL ROUTER",
        "NETWORK GATEWAY",
        "DESTINATION"
    ]
    for index, node in enumerate(nodes, 1):
        time.sleep(0.3)
        print(f"{index:02}  {node:<24} [SIMULATED]")
    print("=====================================")

# ============================================================
# FILE TOOLS
# ============================================================

def hash_text(text, algorithm="sha256"):
    try:
        return hashlib.new(algorithm, text.encode()).hexdigest()
    except Exception:
        raise ValueError("Unsupported hash algorithm.")

def hash_file(name):
    try:
        path = safe_path(name)
        if not path.is_file():
            print("File not found.")
            return

        digest = hashlib.sha256()
        with path.open("rb") as file:
            for chunk in iter(lambda: file.read(65536), b""):
                digest.update(chunk)

        print("File:", path.name)
        print("SHA-256:", digest.hexdigest())
    except Exception as error:
        print("Hash error:", error)

def hex_view(name):
    try:
        path = safe_path(name)
        if not path.is_file():
            print("File not found.")
            return

        data = path.read_bytes()[:512]
        print(f"\n========== HEX VIEW: {path.name} ==========")

        for offset in range(0, len(data), 16):
            chunk = data[offset:offset + 16]
            hex_part = " ".join(f"{byte:02X}" for byte in chunk)
            text_part = "".join(
                chr(byte) if 32 <= byte < 127 else "."
                for byte in chunk
            )
            print(f"{offset:08X}  {hex_part:<47}  {text_part}")

        if len(data) == 512:
            print("Output limited to first 512 bytes.")

    except Exception as error:
        print("Hex error:", error)

def file_check(name):
    try:
        path = safe_path(name)

        if not path.exists():
            print("File does not exist.")
            return

        if not path.is_file():
            print("Not a regular file.")
            return

        data = path.read_bytes()

        print("\n========== FILE REPORT ==========")
        print("Name:", path.name)
        print("Size:", len(data), "bytes")
        print("Suffix:", path.suffix or "(none)")
        print("SHA-256:", hashlib.sha256(data).hexdigest())

        try:
            data.decode("utf-8")
            print("UTF-8 readable: YES")
        except UnicodeDecodeError:
            print("UTF-8 readable: NO")

        print("=================================")
        achievement("file_inspector")

    except Exception as error:
        print("File inspection error:", error)

def list_files():
    print("\n========== PROJECT FILES ==========")
    for path in sorted(ROOT.iterdir()):
        kind = "DIR " if path.is_dir() else "FILE"
        print(f"[{kind}] {path.name}")
    print("===================================")

def create_text_file(name, content):
    try:
        path = safe_path(name)
        if path.exists():
            print("File already exists. Use -writeforce to replace it.")
            return
        path.write_text(content, encoding="utf-8")
        print("File created:", path.name)
    except Exception as error:
        print("Write error:", error)

def read_text_file(name):
    try:
        path = safe_path(name)
        if not path.is_file():
            print("File not found.")
            return
        print(path.read_text(encoding="utf-8"))
    except Exception as error:
        print("Read error:", error)

# ============================================================
# TEXT / ENCODING / CRYPTO DEMOS
# ============================================================

def encode_text(text):
    print(base64.b64encode(text.encode()).decode())

def decode_text(text):
    try:
        print(base64.b64decode(text, validate=True).decode())
    except Exception:
        print("Invalid Base64 or invalid UTF-8.")

def caesar(text, shift):
    output = []

    for char in text:
        if char.isalpha() and char.isascii():
            base = ord("A") if char.isupper() else ord("a")
            output.append(chr((ord(char) - base + shift) % 26 + base))
        else:
            output.append(char)

    return "".join(output)

def toy_encrypt(text):
    print("Educational Caesar cipher. NOT secure encryption.")
    print(caesar(text, 7))

def toy_decrypt(text):
    print("Educational Caesar cipher. NOT secure encryption.")
    print(caesar(text, -7))

def generate_key():
    print("Random demo token:")
    print(secrets.token_hex(32))
    print("Not saved by AuriTerm.")

def generate_password(length="20"):
    try:
        size = int(length)
        if not 8 <= size <= 128:
            raise ValueError

        alphabet = string.ascii_letters + string.digits + "!@#$%^&*_-+="
        password = "".join(secrets.choice(alphabet) for _ in range(size))

        print("Generated password:", password)
        print("This is displayed only, not saved.")
    except Exception:
        print("Usage: -passgen 20 (8–128)")

def reverse_text(text):
    print(text[::-1])

def word_count(text):
    words = re.findall(r"\b[\w'-]+\b", text)
    print("Characters:", len(text))
    print("Words:", len(words))
    print("Lines:", len(text.splitlines()))

# ============================================================
# NOTES
# ============================================================

def note_command(args):
    if not args:
        action = "list"
    else:
        action = args[0].lower()

    if action == "add":
        content = " ".join(args[1:])
        if not content:
            print("Usage: -note add your note")
            return

        notes.append({
            "text": content,
            "time": time.time()
        })
        save_json(NOTES_FILE, notes)
        print("Note saved.")
        achievement("first_note")

    elif action == "list":
        if not notes:
            print("No notes.")
            return

        for index, note in enumerate(notes, 1):
            print(f"{index}. {note.get('text', '')}")

    elif action == "clear":
        confirm = input("Clear all notes? Type YES: ")
        if confirm == "YES":
            notes.clear()
            save_json(NOTES_FILE, notes)
            print("Notes cleared.")
        else:
            print("Cancelled.")

    elif action == "delete":
        try:
            index = int(args[1]) - 1
            if not 0 <= index < len(notes):
                raise IndexError
            removed = notes.pop(index)
            save_json(NOTES_FILE, notes)
            print("Deleted:", removed.get("text", ""))
        except Exception:
            print("Usage: -note delete NUMBER")

    else:
        print("Usage: -note add|list|delete|clear")

# ============================================================
# TASK MANAGER
# ============================================================

def todo_command(args):
    action = args[0].lower() if args else "list"

    if action == "add":
        content = " ".join(args[1:])
        if not content:
            print("Usage: -todo add task")
            return

        todos.append({
            "text": content,
            "done": False,
            "created": time.time()
        })
        save_json(TODOS_FILE, todos)
        print("Task added.")

    elif action == "list":
        if not todos:
            print("No tasks.")
            return

        for index, item in enumerate(todos, 1):
            marker = "X" if item.get("done") else " "
            print(f"{index}. [{marker}] {item.get('text', '')}")

    elif action == "done":
        try:
            index = int(args[1]) - 1
            todos[index]["done"] = True
            save_json(TODOS_FILE, todos)
            print("Task completed.")
        except Exception:
            print("Usage: -todo done NUMBER")

    elif action == "delete":
        try:
            index = int(args[1]) - 1
            removed = todos.pop(index)
            save_json(TODOS_FILE, todos)
            print("Deleted:", removed.get("text", ""))
        except Exception:
            print("Usage: -todo delete NUMBER")

    elif action == "clear":
        confirm = input("Clear all tasks? Type YES: ")
        if confirm == "YES":
            todos.clear()
            save_json(TODOS_FILE, todos)
            print("Tasks cleared.")
        else:
            print("Cancelled.")

    else:
        print("Usage: -todo add|list|done|delete|clear")

# ============================================================
# BACKUPS
# ============================================================

def make_backup():
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    destination = BACKUPS / f"auriterm_{stamp}.zip"

    try:
        with zipfile.ZipFile(
            destination,
            "w",
            zipfile.ZIP_DEFLATED
        ) as archive:
            for path in ROOT.rglob("*"):
                if not path.is_file():
                    continue

                if DATA in path.parents:
                    continue

                if path == destination:
                    continue

                archive.write(path, path.relative_to(ROOT))

        print("Backup created:", destination.name)
        achievement("first_backup")

    except Exception as error:
        print("Backup error:", error)

def list_backups():
    files = sorted(BACKUPS.glob("*.zip"))

    if not files:
        print("No backups.")
        return

    for file in files:
        print(f"{file.name} — {file.stat().st_size} bytes")

# ============================================================
# ANDROID / TERMUX API
# ============================================================

def phone_command(args):
    if not args:
        print("Usage: -phone battery|torch|vibrate|clipboard")
        return

    action = args[0].lower()

    if action == "battery":
        run_termux_api(["termux-battery-status"])

    elif action == "torch":
        if len(args) < 2 or args[1] not in ("on", "off"):
            print("Usage: -phone torch on|off")
            return
        run_termux_api(["termux-torch", args[1]])

    elif action == "vibrate":
        try:
            duration = int(args[1]) if len(args) > 1 else 500
            duration = max(1, min(duration, 10000))
            run_termux_api(["termux-vibrate", "-d", str(duration)])
        except ValueError:
            print("Usage: -phone vibrate 500")

    elif action == "clipboard":
        run_termux_api(["termux-clipboard-get"])

    else:
        print("Unknown phone action.")

# ============================================================
# GAMES
# ============================================================

def play_maze():
    board = [
        list("##########"),
        list("#P...#...#"),
        list("#.#..#.#.#"),
        list("#.#....#.#"),
        list("#.####...#"),
        list("#......G.#"),
        list("##########")
    ]

    player = [1, 1]
    goal = [5, 7]
    moves = {
        "w": (-1, 0),
        "s": (1, 0),
        "a": (0, -1),
        "d": (0, 1)
    }

    print("\nAURITERM MAZE")
    print("W A S D to move | dir to redraw | quit to exit")

    while True:
        for row in board:
            print("".join(row))

        command = input("GAME> ").strip().lower()

        if command in ("quit", "exit"):
            print("Game closed.")
            return

        if command == "dir":
            continue

        if command not in moves:
            print("Use W, A, S, D, dir, or quit.")
            continue

        dy, dx = moves[command]
        ny = player[0] + dy
        nx = player[1] + dx

        if board[ny][nx] == "#":
            print("Wall detected.")
            continue

        board[player[0]][player[1]] = "."
        player = [ny, nx]

        if player == goal:
            print("YOU WIN!")
            award_xp(25)
            achievement("first_game")
            return

        board[ny][nx] = "P"

def play_number_game():
    target = random.randint(1, 50)
    attempts = 0

    print("\nNUMBER GUESS")
    print("Guess a number from 1 to 50.")
    print("Type quit to leave.")

    while True:
        answer = input("GUESS> ").strip().lower()

        if answer == "quit":
            return

        try:
            number = int(answer)
        except ValueError:
            print("Enter a number.")
            continue

        attempts += 1

        if number == target:
            print("CORRECT!")
            print("Attempts:", attempts)
            award_xp(max(5, 30 - attempts))
            return

        if number < target:
            print("Too low.")
        else:
            print("Too high.")

def game_menu():
    print("""
========== GAME CENTER ==========
1. Maze
2. Number Guess
3. Exit
=================================
""")

    choice = input("GAME CENTER> ").strip()

    if choice == "1":
        play_maze()
    elif choice == "2":
        play_number_game()
    elif choice == "3":
        print("Game center closed.")
    else:
        print("Unknown game.")

# ============================================================
# VISUAL EFFECTS
# ============================================================

def matrix_effect():
    achievement("matrix_user")
    chars = "01ABCDEF#$%&"
    print("\nMATRIX MODE")
    for _ in range(16):
        print("".join(random.choice(chars) for _ in range(55)))
        time.sleep(0.05)

def glitch_effect():
    chars = "▓▒░#@$!?01"
    print("\nGLITCH MODE")
    for _ in range(10):
        print("".join(random.choice(chars) for _ in range(50)))
        time.sleep(0.06)

def rainbow_text(text):
    colors = [
        "\033[91m", "\033[93m", "\033[92m",
        "\033[96m", "\033[94m", "\033[95m"
    ]
    output = ""
    for index, char in enumerate(text):
        output += colors[index % len(colors)] + char
    print(output + "\033[0m")

def show_logs():
    if not LOGFILE.exists():
        print("No logs yet.")
        return

    try:
        lines = LOGFILE.read_text(encoding="utf-8").splitlines()
        for line in lines[-40:]:
            print(line)
    except Exception as error:
        print("Log error:", error)

def show_status():
    print("\n========== AURITERM STATUS ==========")
    print("Version:", VERSION)
    print("Hack mode:", "ON" if config.get("hackmode") else "OFF")
    print("Demon mode:", "ON" if config.get("demon_mode") else "OFF")
    print("Theme:", config.get("theme"))
    print("Commands used:", config.get("commands_used"))
    print("XP:", config.get("xp"))
    print("Rank:", config.get("rank"))
    print("Notes:", len(notes))
    print("Tasks:", len(todos))
    print("DEMONING executions:", len(DEMONING_HISTORY))
    print("Data folder:", DATA)
    print("=====================================")

# ============================================================
# DEMONING ENGINE
# ============================================================

DEMONING_VERSION = "1.0"
DEMONING_HISTORY = []

DEMONING_INDEX = [
    "about",
    "status",
    "syscheck",
    "whoami",
    "rootcheck",
    "terminal",
    "hackmode",
    "netinfo",
    "ipinfo",
    "dns",
    "ping",
    "portcheck",
    "netmap",
    "trace",
    "hash",
    "hashfile",
    "hexview",
    "filecheck",
    "keygen",
    "passgen",
    "encode",
    "decode",
    "encrypt",
    "decrypt",
    "calc",
    "note",
    "todo",
    "backup",
    "backups",
    "logs",
    "phone",
    "game",
    "matrix",
    "glitch",
    "clear",
    "help",
    "commands"
]

def demon_banner():
    print(r"""
╔════════════════════════════════════════╗
║            AURITERM DEMONING           ║
║                SYSTEM 1.0              ║
╠════════════════════════════════════════╣
║          COMMAND CONTROL HUB           ║
╚════════════════════════════════════════╝
""")

def demon_help():
    print("""
========== DEMONING HELP ==========

-demoning help
    Display DEMONING help.

-demoning list
    List indexed commands.

-demoning search NAME
    Search the index.

-demoning run NAME
    Execute an indexed command.

-demoning random
    Select a random command.

-demoning stats
    Show DEMONING statistics.

-demoning history
    Show DEMONING execution history.

-demoning exit
    Return to AuriTerm.

===================================
""")

def demon_list():
    print("\n========== DEMONING INDEX ==========")
    for index, name in enumerate(DEMONING_INDEX, 1):
        print(f"[{index:02}] -{name}")
    print("====================================")
    print("Total indexed:", len(DEMONING_INDEX))

def demon_search(args):
    if not args:
        print("Usage: -demoning search NAME")
        return

    query = " ".join(args).lower()
    matches = [
        name for name in DEMONING_INDEX
        if query in name.lower()
    ]

    print("\n[ DEMONING SEARCH ]")

    if matches:
        for match in matches:
            print("[FOUND]", match)
    else:
        print("[NO MATCHES]")

def demon_run(args):
    if not args:
        print("Usage: -demoning run NAME")
        return

    name = args[0].lower().lstrip("-")

    if name not in DEMONING_INDEX:
        print("[DENIED] Command not in index.")
        return

    if name in ("help", "commands", "clear"):
        print("Use the main AuriTerm interface for this command.")
        return

    DEMONING_HISTORY.append(name)
    save_json(HISTORY_FILE, history + [
        {"time": time.time(), "command": "demoning run " + name}
    ])

    print("\n[ DEMONING EXECUTION ]")
    print("Command:", name)
    print("------------------------------------")

    execute(
        "-" + name + (
            " " + shlex.join(args[1:])
            if len(args) > 1 else ""
        )
    )

    print("------------------------------------")
    print("[ DEMONING COMPLETE ]")

def demon_random():
    name = random.choice(DEMONING_INDEX)
    print("[ RANDOM COMMAND ]")
    print("Try:", "-" + name)

def demon_stats():
    print("\n========== DEMONING STATS ==========")
    print("Version:", DEMONING_VERSION)
    print("Indexed commands:", len(DEMONING_INDEX))
    print("Executed commands:", len(DEMONING_HISTORY))
    print("Unique executed:", len(set(DEMONING_HISTORY)))
    print("====================================")

def demon_history():
    print("\n========== DEMONING HISTORY ==========")

    if not DEMONING_HISTORY:
        print("No DEMONING commands executed.")
        return

    for index, name in enumerate(DEMONING_HISTORY, 1):
        print(f"{index:02}. -{name}")

    print("======================================")

def demon_exit():
    print("[ DEMONING CLOSED ]")
    print("Returning to AuriTerm...")

def demoning_command(args):
    if not args:
        demon_banner()
        demon_help()
        return

    action = args[0].lower().lstrip("-")
    rest = args[1:]

    actions = {
        "help": lambda: demon_help(),
        "list": lambda: demon_list(),
        "search": lambda: demon_search(rest),
        "run": lambda: demon_run(rest),
        "random": lambda: demon_random(),
        "stats": lambda: demon_stats(),
        "history": lambda: demon_history(),
        "exit": lambda: demon_exit()
    }

    if action in actions:
        config["demon_mode"] = action != "exit"
        save_json(CONFIG_FILE, config)
        actions[action]()
    else:
        print("[ DEMONING ERROR ] Unknown command.")
        print("Use: -demoning help")

# ============================================================
# HELP
# ============================================================

def show_help():
    print(r"""
==================== CORE ====================
-help                 Show all commands
-about                About AuriTerm
-status               System status
-syscheck             System report
-whoami               User information
-rootcheck            Root status
-terminal             Terminal information
-hackmode             Toggle hacker prompt
-profile              Player profile
-achievements         Show achievements

================== DEMONING ==================
-demoning             Open DEMONING
-demoning help        DEMONING help
-demoning list        List indexed commands
-demoning search X    Search commands
-demoning run X       Execute indexed command
-demoning random      Random command
-demoning stats       Statistics
-demoning history     Execution history
-demoning exit        Leave DEMONING

================== NETWORK ===================
-netinfo              Local network info
-ipinfo               Local IP information
-dns DOMAIN           DNS lookup
-ping                 Ping localhost
-portcheck PORT       Check localhost port
-netmap               Local interface summary
-trace                Simulated route animation

==================== FILES ====================
-ls                   List project files
-read FILE            Read text file
-write FILE TEXT      Create text file
-hash TEXT            SHA-256 text hash
-hashfile FILE        SHA-256 file hash
-hexview FILE         Hex view
-filecheck FILE       File inspection
-backup               Create ZIP backup
-backups              List backups

================= CRYPTO / TEXT ==============
-keygen               Generate demo token
-passgen LENGTH       Generate random password
-encode TEXT          Base64 encode
-decode TEXT          Base64 decode
-encrypt TEXT         Caesar cipher demonstration
-decrypt TEXT         Reverse Caesar demonstration
-reverse TEXT         Reverse text
-wordcount TEXT       Count words and characters

==================== TOOLS ===================
-calc EXPRESSION      Safe calculator
-note add TEXT        Save note
-note list            List notes
-note delete NUMBER   Delete note
-note clear           Clear notes
-todo add TEXT        Add task
-todo list            List tasks
-todo done NUMBER     Complete task
-todo delete NUMBER   Delete task
-todo clear           Clear tasks
-logs                 View logs

================ ANDROID / GAMES ==============
-phone battery        Battery information
-phone torch on|off   Flashlight control
-phone vibrate MS     Vibrate
-phone clipboard      Clipboard
-game                 Open game center
-matrix               Matrix effect
-glitch               Glitch effect
-rainbow TEXT         Rainbow text
-clear                Clear screen
-exit                 Exit AuriTerm

===============================================
""")

# ============================================================
# COMMAND ROUTER
# ============================================================

def execute(raw):
    raw = raw.strip()

    if not raw:
        return True

    try:
        parts = shlex.split(raw)
    except ValueError as error:
        print("Parsing error:", error)
        return True

    command = parts[0].lower().lstrip("-")
    args = parts[1:]

    config["commands_used"] = int(config.get("commands_used", 0)) + 1

    history.append({
        "time": time.time(),
        "command": raw
    })

    if len(history) > 500:
        del history[:-500]

    save_json(CONFIG_FILE, config)
    save_json(HISTORY_FILE, history)
    log(raw)

    if config["commands_used"] == 1:
        achievement("first_command")
    if config["commands_used"] >= 10:
        achievement("ten_commands")
    if config["commands_used"] >= 50:
        achievement("fifty_commands")

    try:
        if command == "demoning":
            demoning_command(args)

        elif command in ("help", "commands"):
            show_help()

        elif command == "about":
            print(f"AuriTerm {VERSION}")
            print("A single-file Termux terminal project.")

        elif command == "status":
            show_status()

        elif command in ("syscheck", "sys"):
            system_info()

        elif command == "whoami":
            print("Username:", config.get("username"))
            print("Process:", os.getpid())
            print("Home:", Path.home())

        elif command == "rootcheck":
            is_root = hasattr(os, "geteuid") and os.geteuid() == 0
            print("Root access:", "YES" if is_root else "NO")
            print("No rooting operation is performed.")

        elif command == "terminal":
            print("Platform:", platform.platform())
            print("Shell:", os.environ.get("SHELL", "Unknown"))
            print("Python:", sys.executable)
            print("Project:", ROOT)

        elif command == "hackmode":
            config["hackmode"] = not config.get("hackmode", False)
            save_json(CONFIG_FILE, config)
            print("HACK MODE:", "ON" if config["hackmode"] else "OFF")

        elif command == "profile":
            show_profile()

        elif command == "achievements":
            show_achievements()

        elif command in ("netinfo", "ipinfo", "netmap"):
            network_info()

        elif command == "dns":
            dns_lookup(args[0] if args else "")

        elif command == "ping":
            local_ping()

        elif command == "portcheck":
            local_portcheck(args[0] if args else "")

        elif command == "trace":
            simulated_trace()

        elif command == "hash":
            if not args:
                print("Usage: -hash TEXT")
            else:
                print(hash_text(" ".join(args)))

        elif command == "hashfile":
            hash_file(args[0] if args else "")

        elif command == "hexview":
            hex_view(args[0] if args else "")

        elif command == "filecheck":
            file_check(args[0] if args else "")

        elif command == "ls":
            list_files()

        elif command == "read":
            if not args:
                print("Usage: -read FILE")
            else:
                read_text_file(args[0])

        elif command == "write":
            if len(args) < 2:
                print("Usage: -write FILE TEXT")
            else:
                create_text_file(args[0], " ".join(args[1:]))

        elif command == "keygen":
            generate_key()

        elif command == "passgen":
            generate_password(args[0] if args else "20")

        elif command == "encode":
            encode_text(" ".join(args))

        elif command == "decode":
            decode_text(" ".join(args))

        elif command == "encrypt":
            toy_encrypt(" ".join(args))

        elif command == "decrypt":
            toy_decrypt(" ".join(args))

        elif command == "reverse":
            reverse_text(" ".join(args))

        elif command == "wordcount":
            word_count(" ".join(args))

        elif command == "calc":
            if not args:
                print("Usage: -calc EXPRESSION")
            else:
                print(calculate(" ".join(args)))

        elif command == "note":
            note_command(args)

        elif command == "todo":
            todo_command(args)

        elif command == "backup":
            make_backup()

        elif command == "backups":
            list_backups()

        elif command == "logs":
            show_logs()

        elif command == "phone":
            phone_command(args)

        elif command == "game":
            game_menu()

        elif command == "matrix":
            matrix_effect()

        elif command == "glitch":
            glitch_effect()

        elif command == "rainbow":
            rainbow_text(" ".join(args))

        elif command == "clear":
            clear_screen()

        elif command in ("exit", "quit"):
            print("AuriTerm shutting down...")
            return False

        else:
            print("Unknown command:", parts[0])
            print("Type -help for the command list.")

    except ZeroDivisionError:
        print("Math error: division by zero.")

    except KeyboardInterrupt:
        print("\nCommand interrupted.")

    except Exception as error:
        print(f"Command error: {type(error).__name__}: {error}")
        log(f"ERROR {type(error).__name__}: {error}")

    return True

# ============================================================
# MAIN LOOP
# ============================================================

def main():
    banner()

    print("AuriTerm initialized.")
    print("DEMONING engine loaded.")
    print("Type -demoning to enter DEMONING.")
    print("Commands may start with - or without it.")
    print("Example: -syscheck\n")

    while True:
        try:
            if config.get("hackmode"):
                prompt = "AURI-ROOT# "
            elif config.get("demon_mode"):
                prompt = "DEMONING# "
            else:
                prompt = "AURI> "

            raw = input(prompt)

            if not execute(raw):
                break

        except KeyboardInterrupt:
            print("\nUse -exit to close AuriTerm.")

        except EOFError:
            print("\nAuriTerm closed.")
            break

    save_all()

if __name__ == "__main__":
    main()