#!/bin/bash
set -e

cd ~/afk-andy

echo "=== Starting AFK Andy ==="

# Start Ollama in background if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo "[1/3] Starting Ollama..."
    ollama serve &
    sleep 3
else
    echo "[1/3] Ollama already running."
fi

# Start website server in background
echo "[2/3] Starting website server on port 8080..."
cd website
python3 -m http.server 8080 &
WEBPID=$!
cd ..

# Start Discord bot
echo "[3/3] Starting Discord bot..."
cd bot
python3 main.py
