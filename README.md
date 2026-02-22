# AFK Andy

A gaming website built by an AI architect that works autonomously while the team is AFK.

## How It Works

1. Humans send instructions via Discord
2. Discord bot receives and structures the task
3. Local AI architect (Qwen3 4B via Ollama) writes the code
4. Changes auto-sync to GitHub
5. Bot reports results back in Discord

## Quick Start

```bash
# First-time setup
bash scripts/setup.sh

# Start the bot and website
bash scripts/start.sh
```

## Team

- **Eugene (dGen)** — Project owner, runs the build server
- **Leo** — Co-builder, gives instructions via Discord
