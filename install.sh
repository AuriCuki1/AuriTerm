
#!/data/data/com.termux/files/usr/bin/bash

set -eu

PINK='\033[38;5;213m'
PURPLE='\033[38;5;141m'
GREEN='\033[38;5;82m'
RED='\033[38;5;196m'
RESET='\033[0m'

echo -e "${PINK}"
echo "================================"
echo "       A U R I T E R M"
echo "================================"
echo -e "${RESET}"

echo -e "${PURPLE}[INSTALLER] Checking environment...${RESET}"

if ! command -v pkg >/dev/null 2>&1; then
    echo -e "${RED}Termux package manager not found.${RESET}"
    echo "This installer is designed for Termux."
    exit 1
fi

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "[CHECK] Project directory found."

if ! command -v python >/dev/null 2>&1; then
    echo "[INSTALL] Installing Python..."
    pkg install python -y
else
    echo "[CHECK] Python is already installed."
fi

if ! command -v python >/dev/null 2>&1; then
    echo -e "${RED}Python installation could not be verified.${RESET}"
    exit 1
fi

if [ ! -f "main.py" ]; then
    echo -e "${RED}main.py is missing.${RESET}"
    exit 1
fi

mkdir -p database art config

echo -e "${GREEN}"
echo "================================"
echo "     AURITERM READY!"
echo "================================"
echo -e "${RESET}"

echo "Python: $(python --version)"
echo "Project: $PROJECT_DIR"
echo
echo "Launch AuriTerm with:"
echo "python main.py"
echo
echo "Installation check complete."
