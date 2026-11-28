#!/usr/bin/env python3
# ============================================================
# AURITERM 2.2 — EXTREME KEYBOARD EDITION
# Single-file Termux terminal
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
from pathlib import Path
from collections import Counter

VERSION = "2.2 EXTREME"
ROOT = Path(__file__).resolve().parent
DATA = ROOT / "auriterm_data"
BACKUPS = DATA / "backups"
LOGFILE = DATA / "auriterm.log"
NOTES = DATA / "notes.json"
TODOS = DATA / "todos.json"
CONFIG = DATA / "config.json"

for folder in (DATA, BACKUPS):
    folder.mkdir(parents=True, exist_ok=True)

DEFAULT_CONFIG = {
    "hackmode": False,
    "username": "Auri",
    "theme": "PURPLE",
    "commands_used": 0
}

def load_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default.copy() if isinstance(default, dict) else list(default)

def save_json(path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

config = load_json(CONFIG, DEFAULT_CONFIG)
notes = load_json(NOTES, [])
todos = load_json(TODOS, [])

def log(message):
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOGFILE.open("a", encoding="utf-8") as f:
        f.write(f"[{stamp}] {message}\n")

def banner():
    os.system("clear")
    print(r"""
   █████╗ ██╗   ██╗██████╗ ██╗████████╗███████╗██████╗ ███╗   ███╗
  ██╔══██╗██║   ██║██╔══██╗██║╚══██╔══╝██╔════╝██╔══██╗████╗ ████║
  ███████║██║   ██║██████╔╝██║   ██║   █████╗  ██████╔╝██╔████╔██║
  ██╔══██║██║   ██║██╔══██╗██║   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║
  ██║  ██║╚██████╔╝██║  ██║██║   ██║   ███████╗██║  ██║██║ ╚═╝ ██║
  ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝
    """)
    print(f"       AuriTerm {VERSION} // KEYBOARD EDITION")
    print("       [ LOCAL SYSTEM // SAFE TOOLKIT // READY ]")
    print("       Type -help to view commands.\n")

def say(text=""):
    print(text)

def safe_path(name):
    """Only allow files inside the AuriTerm project directory."""
    target = (ROOT / name).resolve()
    if target != ROOT and ROOT not in target.parents:
        raise ValueError("Access denied: path outside AuriTerm folder.")
    return target

def run_termux_api(command):
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=8
        )
        if result.returncode == 0:
            print(result.stdout.strip() or "Command completed.")
        else:
            print(result.stderr.strip() or "Command failed.")
    except FileNotFoundError:
        print("Termux:API command not found.")
        print("Install the Termux:API app and run: pkg install termux-api")
    except Exception as e:
        print("API error:", e)

# ------------------------------------------------------------
# SAFE CALCULATOR
# ------------------------------------------------------------

ALLOWED_OPS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.FloorDiv: lambda a, b: a // b,
    ast.Mod: lambda a, b: a % b,
    ast.Pow: lambda a, b: a ** b,
}

def calculate(expression):
    tree = ast.parse(expression, mode="eval")

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.UnaryOp):
            value = evaluate(node.operand)
            if isinstance(node.op, ast.USub):
                return -value
            if isinstance(node.op, ast.UAdd):
                return value
        if isinstance(node, ast.BinOp):
            op = ALLOWED_OPS.get(type(node.op))
            if not op:
                raise ValueError("Operator not allowed.")
            left, right = evaluate(node.left), evaluate(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 10:
                raise ValueError("Exponent too large.")
            result = op(left, right)
            if abs(result) > 10**100:
                raise ValueError("Result too large.")
            return result
        raise ValueError("Invalid calculation.")

    return evaluate(tree)

# ------------------------------------------------------------
# SYSTEM / NETWORK INFORMATION
# ------------------------------------------------------------

def system_info():
    print("\n[ SYSTEM REPORT ]")
    print("OS:", platform.system(), platform.release())
    print("Python:", platform.python_version())
    print("Architecture:", platform.machine())
    print("Hostname:", socket.gethostname())
    print("Current folder:", ROOT)
    print("Disk usage:")
    try:
        usage = shutil.disk_usage(ROOT)
        print(f"  Total: {usage.total // (1024**3)} GB")
        print(f"  Used:  {usage.used // (1024**3)} GB")
        print(f"  Free:  {usage.free // (1024**3)} GB")
    except Exception as e:
        print("  Unavailable:", e)

def network_info():
    host = socket.gethostname()
    print("\n[ LOCAL NETWORK INFORMATION ]")
    print("Hostname:", host)
    try:
        for item in socket.getaddrinfo(host, None):
            print("Address:", item[4][0])
    except Exception as e:
        print("Could not read addresses:", e)

def dns_lookup(domain):
    if not domain or len(domain) > 253:
        print("Usage: -dns example.com")
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
    print("Checking the local network stack...")
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "127.0.0.1"],
            capture_output=True, text=True, timeout=5
        )
        print(result.stdout.strip() or result.stderr.strip())
        print("Local ping:", "OK" if result.returncode == 0 else "FAILED")
    except FileNotFoundError:
        print("The ping utility is not installed.")
    except Exception as e:
        print("Ping error:", e)

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
            print(f"Port {port}: OPEN on this device")
    except OSError:
        print(f"Port {port}: CLOSED or unavailable on this device")

def local_netmap():
    print("\n[ LOCAL INTERFACE SUMMARY ]")
    print("This displays this device's own hostname addresses.")
    network_info()

def simulated_trace():
    print("\n[ SIMULATED ROUTE TRACE ]")
    print("This is a visual simulation, not a real route scan.")
    nodes = ["LOCAL DEVICE", "LOCAL ROUTER", "NETWORK GATEWAY", "DESTINATION"]
    for i, node in enumerate(nodes, 1):
        time.sleep(0.35)
        print(f" {i:02}  {node:<24} [SIMULATED]")

# ------------------------------------------------------------
# FILE ANALYSIS
# ------------------------------------------------------------

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
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                digest.update(chunk)
        print("File:", path.name)
        print("SHA-256:", digest.hexdigest())
    except Exception as e:
        print("File error:", e)

def hex_view(name):
    try:
        path = safe_path(name)
        data = path.read_bytes()[:512]
        print(f"\n[ HEX VIEW: {path.name} ]")
        for offset in range(0, len(data), 16):
            chunk = data[offset:offset + 16]
            hex_part = " ".join(f"{b:02X}" for b in chunk)
            text_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
            print(f"{offset:08X}  {hex_part:<47}  {text_part}")
        if len(data) == 512:
            print("... limited to first 512 bytes")
    except Exception as e:
        print("Hex error:", e)

def file_check(name):
    try:
        path = safe_path(name)
        if not path.exists():
            print("File does not exist.")
            return
        if not path.is_file():
            print("That path is not a file.")
            return
        data = path.read_bytes()
        print("\n[ FILE INSPECTION ]")
        print("Name:", path.name)
        print("Size:", len(data), "bytes")
        print("Suffix:", path.suffix or "(none)")
        print("SHA-256:", hashlib.sha256(data).hexdigest())
        print("Readable UTF-8:", end=" ")
        try:
            data.decode("utf-8")
            print("YES")
        except UnicodeDecodeError:
            print("NO")
    except Exception as e:
        print("File check error:", e)

# ------------------------------------------------------------
# ENCODING / DEMO CIPHER
# ------------------------------------------------------------

def encode_text(text):
    print(base64.b64encode(text.encode()).decode())

def decode_text(text):
    try:
        print(base64.b64decode(text, validate=True).decode())
    except Exception:
        print("Invalid Base64 or text is not UTF-8.")

def caesar(text, shift):
    output = []
    for char in text:
        if char.isalpha():
            base = ord("A") if char.isupper() else ord("a")
            output.append(chr((ord(char) - base + shift) % 26 + base))
        else:
            output.append(char)
    return "".join(output)

def toy_encrypt(text):
    print("Educational Caesar cipher only — NOT secure encryption.")
    print(caesar(text, 7))

def toy_decrypt(text):
    print("Educational Caesar cipher only — NOT secure encryption.")
    print(caesar(text, -7))

def generate_key():
    print("Random demo key:", secrets.token_hex(32))
    print("Keep real account secrets private; this key is not stored.")

def generate_password(length="20"):
    try:
        size = int(length)
        if not 8 <= size <= 128:
            raise ValueError
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*_-+="
        print("Generated password:", "".join(secrets.choice(alphabet) for _ in range(size)))
        print("It is displayed only; AuriTerm does not save it.")
    except Exception:
        print("Usage: -passgen 20  (length 8–128)")

# ------------------------------------------------------------
# NOTES / TASKS / BACKUPS
# ------------------------------------------------------------

def note_command(args):
    global notes
    action = args[0].lower() if args else "list"
    if action == "add":
        content = " ".join(args[1:])
        if not content:
            print("Usage: -note add your note")
            return
        notes.append({"text": content, "time": time.time()})
        save_json(NOTES, notes)
        print("Note saved.")
    elif action == "list":
        if not notes:
            print("No notes yet.")
        for i, note in enumerate(notes, 1):
            print(f"{i}. {note['text']}")
    elif action == "clear":
        notes = []
        save_json(NOTES, notes)
        print("Notes cleared.")
    else:
        print("Usage: -note add|list|clear")

def todo_command(args):
    global todos
    action = args[0].lower() if args else "list"
    if action == "add":
        text = " ".join(args[1:])
        if not text:
            print("Usage: -todo add task")
            return
        todos.append({"text": text, "done": False})
        save_json(TODOS, todos)
        print("Task added.")
    elif action == "list":
        if not todos:
            print("No tasks.")
        for i, item in enumerate(todos, 1):
            mark = "✓" if item["done"] else " "
            print(f"{i}. [{mark}] {item['text']}")
    elif action == "done":
        try:
            index = int(args[1]) - 1
            todos[index]["done"] = True
            save_json(TODOS, todos)
            print("Task completed.")
        except Exception:
            print("Usage: -todo done 1")
    elif action == "clear":
        todos = []
        save_json(TODOS, todos)
        print("Tasks cleared.")
    else:
        print("Usage: -todo add|list|done|clear")

def make_backup():
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    destination = BACKUPS / f"auriterm_backup_{stamp}.zip"
    try:
        with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in ROOT.rglob("*"):
                if not path.is_file():
                    continue
                if DATA in path.parents or path == destination:
                    continue
                archive.write(path, path.relative_to(ROOT))
        print("Backup created:", destination.name)
    except Exception as e:
        print("Backup failed:", e)

def list_backups():
    files = sorted(BACKUPS.glob("*.zip"))
    if not files:
        print("No backups yet.")
    for file in files:
        print(f"{file.name} — {file.stat().st_size} bytes")

# ------------------------------------------------------------
# ANDROID / TERMUX API
# ------------------------------------------------------------

def phone_command(args):
    if not args:
        print("Usage: -phone battery|torch on|torch off|vibrate [ms]|clipboard")
        return

    action = args[0].lower()

    if action == "battery":
        run_termux_api(["termux-battery-status"])
    elif action == "torch":
        if len(args) < 2 or args[1] not in ("on", "off"):
            print("Usage: -phone torch on|off")
        else:
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

# ------------------------------------------------------------
# KEYBOARD MINI-GAME
# ------------------------------------------------------------

def play_game():
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

    print("\nAURITERM MAZE // Find G")
    print("Controls: W A S D | dir = show map | quit = exit")

    while True:
        for row in board:
            print("".join(row))
        command = input("GAME> ").strip().lower()

        if command in ("quit", "exit"):
            print("Game closed.")
            return
        if command == "dir":
            continue

        moves = {"w": (-1, 0), "s": (1, 0), "a": (0, -1), "d": (0, 1)}
        if command not in moves:
            print("Use W, A, S, D, dir, or quit.")
            continue

        dy, dx = moves[command]
        ny, nx = player[0] + dy, player[1] + dx

        if board[ny][nx] == "#":
            print("Wall detected.")
            continue

        board[player[0]][player[1]] = "."
        player = [ny, nx]

        if player == goal:
            print("YOU WIN! AuriTerm maze completed.")
            return

        board[ny][nx] = "P"

# ------------------------------------------------------------
# VISUAL / TERMINAL COMMANDS
# ------------------------------------------------------------

def matrix_effect():
    chars = "01ABCDEF#$%&"
    for _ in range(12):
        print("".join(random.choice(chars) for _ in range(55)))
        time.sleep(0.06)

def glitch_effect():
    for _ in range(7):
        print("".join(random.choice("▓▒░#@$!?01") for _ in range(48)))
        time.sleep(0.08)

def show_logs():
    if not LOGFILE.exists():
        print("No logs yet.")
        return
    lines = LOGFILE.read_text(encoding="utf-8").splitlines()
    for line in lines[-30:]:
        print(line)

def show_status():
    print("\n[ AURITERM STATUS ]")
    print("Version:", VERSION)
    print("Hack mode:", "ON" if config.get("hackmode") else "OFF")
    print("Theme:", config.get("theme", "PURPLE"))
    print("Commands used:", config.get("commands_used", 0))
    print("Notes:", len(notes))
    print("Tasks:", len(todos))
    print("Data folder:", DATA)

def show_help():
    print(r"""
==================== CORE ====================
-help                 Show all commands
-about                About AuriTerm
-status               AuriTerm status
-syscheck             System report
-whoami               Current user
-rootcheck            Check Android root status
-terminal             Terminal configuration
-hackmode             Toggle hacker visuals

================== NETWORK ===================
-netinfo              Local network information
-ipinfo               Local device IP information
-dns DOMAIN           DNS lookup
-ping                 Ping localhost only
-portcheck PORT       Check a localhost port
-netmap               Display local interface addresses
-trace                Simulated route animation

==================== FILES ====================
-hash TEXT            SHA-256 text hash
-hashfile FILE        SHA-256 file hash
-hexview FILE         Hex view (first 512 bytes)
-filecheck FILE       File metadata and hash
-backup               Create project ZIP backup
-backups              List backups

================= CRYPTO / TEXT ==============
-keygen               Generate random demo key
-passgen LENGTH       Generate random password
-encode TEXT          Base64 encode
-decode TEXT          Base64 decode
-encrypt TEXT         Caesar cipher demonstration
-decrypt TEXT         Reverse Caesar demonstration

==================== TOOLS ===================
-calc EXPRESSION      Safe calculator
-note add TEXT        Save note
-note list            List notes
-note clear           Clear notes
-todo add TEXT        Add task
-todo list            List tasks
-todo done NUMBER     Complete task
-todo clear           Clear tasks
-logs                 View recent logs

================ ANDROID / GAMES ==============
-phone battery        Battery information
-phone torch on|off   Flashlight control
-phone vibrate MS     Vibrate (milliseconds)
-phone clipboard      Read clipboard
-game                 Start keyboard maze
-matrix               Matrix-style animation
-glitch               Glitch animation
-clear                Clear screen
-exit                 Exit AuriTerm

Network commands are limited to local diagnostics and DNS lookups.
The trace command is simulated. The cipher is NOT secure encryption.
""")

# ------------------------------------------------------------
# COMMAND ROUTER
# ------------------------------------------------------------

def execute(raw):
    raw = raw.strip()
    if not raw:
        return True

    try:
        parts = shlex.split(raw)
    except ValueError as e:
        print("Parsing error:", e)
        return True

    command = parts[0].lower().lstrip("-")
    args = parts[1:]

    config["commands_used"] = config.get("commands_used", 0) + 1
    save_json(CONFIG, config)
    log(raw)

    try:
        if command in ("help", "commands"):
            show_help()
        elif command == "about":
            print(f"AuriTerm {VERSION} — single-file Android terminal project.")
        elif command == "status":
            show_status()
        elif command in ("syscheck", "sys"):
            system_info()
        elif command == "whoami":
            print("User:", config.get("username", "Auri"))
            print("Python process:", os.getpid())
            print("Home:", str(Path.home()))
        elif command == "rootcheck":
            is_root = hasattr(os, "geteuid") and os.geteuid() == 0
            print("Root access:", "YES" if is_root else "NO")
            print("AuriTerm does not attempt to gain root access.")
        elif command == "terminal":
            print("Platform:", platform.platform())
            print("Shell:", os.environ.get("SHELL", "Unknown"))
            print("Python:", sys.executable)
            print("Project:", ROOT)
        elif command == "hackmode":
            config["hackmode"] = not config.get("hackmode", False)
            save_json(CONFIG, config)
            print("HACK MODE:", "ACTIVATED" if config["hackmode"] else "DEACTIVATED")
        elif command == "netinfo":
            network_info()
        elif command == "ipinfo":
            network_info()
        elif command == "dns":
            dns_lookup(args[0] if args else "")
        elif command == "ping":
            local_ping()
        elif command == "portcheck":
            local_portcheck(args[0] if args else "")
        elif command == "netmap":
            local_netmap()
        elif command == "trace":
            simulated_trace()
        elif command == "hash":
            if not args:
                print("Usage: -hash text")
            else:
                print(hash_text(" ".join(args)))
        elif command == "hashfile":
            hash_file(args[0] if args else "")
        elif command == "hexview":
            hex_view(args[0] if args else "")
        elif command == "filecheck":
            file_check(args[0] if args else "")
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
        elif command == "calc":
            expression = " ".join(args)
            print(calculate(expression))
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
            play_game()
        elif command == "matrix":
            matrix_effect()
        elif command == "glitch":
            glitch_effect()
        elif command == "clear":
            os.system("clear")
        elif command in ("exit", "quit"):
            print("AuriTerm shutting down...")
            return False
        else:
            print(f"Unknown command: {parts[0]}")
            print("Type -help for the command list.")

    except ZeroDivisionError:
        print("Math error: division by zero.")
    except Exception as e:
        print(f"Command error: {type(e).__name__}: {e}")
        log(f"ERROR {type(e).__name__}: {e}")

    return True

# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main():
    banner()
    print("AuriTerm initialized.")
    print("Tip: commands can start with - or without it.")
    print("Example: -syscheck\n")

    while True:
        try:
            prompt = "AURI-ROOT# " if config.get("hackmode") else "AURI> "
            command = input(prompt)
            if not execute(command):
                break
        except KeyboardInterrupt:
            print("\nUse -exit to close AuriTerm.")
        except EOFError:
            print("\nAuriTerm closed.")
            break

if __name__ == "__main__":
    main()