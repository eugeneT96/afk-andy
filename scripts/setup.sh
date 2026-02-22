#!/bin/bash
set -e

echo "=== AFK Andy Setup ==="

cd ~/afk-andy

# Install Python dependencies
echo "[1/3] Installing Python dependencies..."
python3 -m venv venv
venv/bin/pip install -r requirements.txt

# Check Ollama
echo "[2/3] Checking Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "Ollama not found. Installing..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi

# Pull model
echo "[3/3] Pulling Qwen3 4B model..."
ollama pull qwen3:4b

echo ""
echo "=== Setup complete! ==="
echo "Run 'bash scripts/start.sh' to launch AFK Andy."
