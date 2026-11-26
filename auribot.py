
import datetime
import ast
import operator

from art.gallery import show_gallery

PINK = "\033[38;5;213m"
PURPLE = "\033[38;5;141m"
CYAN = "\033[38;5;51m"
WHITE = "\033[97m"
GRAY = "\033[90m"
RED = "\033[38;5;196m"
RESET = "\033[0m"

VERSION = "1.0.0"
BOT_NAME = "AuriBot"

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos
}


def calculate(expression):
    def evaluate(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value

        if isinstance(node, ast.BinOp):
            op = OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError("Unsupported operator")
            return op(evaluate(node.left), evaluate(node.right))

        if isinstance(node, ast.UnaryOp):
            op = OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError("Unsupported operator")
            return op(evaluate(node.operand))

        raise ValueError("Invalid expression")

    if len(expression) > 100:
        raise ValueError("Expression is too long")

    tree = ast.parse(expression, mode="eval")
    result = evaluate(tree.body)

    if isinstance(result, float) and not result.is_integer():
        return round(result, 8)

    return result


def help_menu():
    print(PURPLE + "\n--- AURIBOT COMMANDS ---" + RESET)
    commands = [
        "hello, hi, hey",
        "time",
        "date",
        "art",
        "calc 10 + 5",
        "about",
        "help",
        "back"
    ]

    for command in commands:
        print(PINK + "  " + command + RESET)


def respond(message):
    if message in ("hello", "hi", "hey"):
        print(PINK + "AuriBot > Hello! Welcome to AuriTerm!" + RESET)

    elif message == "time":
        print(datetime.datetime.now().strftime("%H:%M:%S"))

    elif message == "date":
        print(datetime.date.today())

    elif message == "art":
        show_gallery()

    elif message.startswith("calc "):
        expression = message[5:].strip()

        try:
            print(CYAN + "Result: " + WHITE + str(calculate(expression)) + RESET)
        except (ValueError, SyntaxError, ZeroDivisionError, OverflowError):
            print(RED + "AuriBot > Invalid calculation." + RESET)

    elif message == "about":
        print("AuriBot is a programmed assistant.")
        print("It does not use artificial intelligence.")
        print("Created by Auri for AuriTerm.")

    elif message == "help":
        help_menu()

    else:
        print(PINK + "AuriBot > I don't know that yet." + RESET)


def run():
    print(PINK + "\n[AuriBot] Hello, Auri!" + RESET)
    print(GRAY + "Programmed assistant | Version " + VERSION + RESET)
    print("Type 'help' for commands or 'back' to return.")

    while True:
        try:
            message = input(CYAN + "You > " + WHITE).strip().lower()
        except (KeyboardInterrupt, EOFError):
            print(RESET)
            return

        if message == "back":
            print(PURPLE + "AuriBot disconnected." + RESET)
            return

        if not message:
            continue

        respond(message)


if __name__ == "__main__":
    run()
