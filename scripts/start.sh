#!/bin/bash
set -e

cd ~/afk-andy

echo "=== Starting AFK Andy (MC Manager) ==="
echo "MC server is started via Discord (!start command)"
echo ""

# Start Discord bot
echo "Starting Discord bot..."
cd bot
~/afk-andy/venv/bin/python main.py
