# AFK Andy — Minecraft Server Manager

A Discord bot that manages a Paper Minecraft server. Start, stop, and control your MC server from Discord.

## How It Works

1. Leo or Eugene send commands via Discord (e.g. `!start`, `!whitelist add Steve`)
2. AFK Andy manages the Minecraft server process and communicates via RCON
3. Server status and player info reported back in Discord

## Commands

| Command | What It Does |
|---------|-------------|
| `!start` | Start the MC server |
| `!stop` | Stop the MC server |
| `!restart` | Restart the server |
| `!status` | Show server state + players |
| `!players` | Who's online |
| `!whitelist add/remove/list <name>` | Manage the whitelist |
| `!cmd <command>` | Run any MC console command |
| `!say <message>` | Broadcast in-game from Discord |
| `!backup` | Save the world |
| `!yo` | Just say hi |

## Tech Stack

- **Server**: Paper MC (latest)
- **Bot**: Python, discord.py
- **Communication**: RCON (mcrcon)
- **Process Management**: GNU screen

## Quick Start

```bash
# First time setup
bash scripts/setup.sh

# Copy and edit .env
cp env.example .env
nano .env  # Fill in Discord tokens + RCON password

# Start the bot
bash scripts/start.sh

# Then use !start in Discord to boot the MC server
```

## Ports

| Service | Port | Notes |
|---------|------|-------|
| Minecraft | 25565 | Must be open for players |
| RCON | 25575 | Localhost only |

## Team

- **Eugene (dGen)** — Project owner
- **Leo** — Co-admin
- **AFK Andy** — The bot that runs it all
