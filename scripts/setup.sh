#!/bin/bash
set -e

cd ~/afk-andy

echo "=== AFK Andy Setup (MC Manager) ==="

# Python venv + deps
echo "[1/4] Installing Python dependencies..."
python3 -m venv venv
venv/bin/pip install -r requirements.txt

# Check for screen
echo "[2/4] Checking for screen..."
if ! command -v screen &> /dev/null; then
    echo "Installing screen..."
    sudo apt install -y screen
else
    echo "screen is installed."
fi

# Check for Java
echo "[3/4] Checking for Java..."
if ! command -v java &> /dev/null; then
    echo "Java not found. Installing OpenJDK 21..."
    sudo apt install -y openjdk-21-jre-headless
else
    java -version 2>&1 | head -1
fi

# Paper server setup
echo "[4/4] Setting up Paper Minecraft server..."
bash scripts/setup-paper.sh

echo ""
echo "=== Setup complete! ==="
echo "1. Copy env.example to .env and fill in your Discord tokens + RCON password"
echo "2. Run: bash scripts/start.sh"
echo "3. Use !start in Discord to boot the MC server"
