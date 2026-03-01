# AFK Andy — Minecraft Server Manager

## What This Is
AFK Andy is a Discord bot that manages a Paper Minecraft server. Leo and Eugene control it via Discord commands to start/stop the server, manage the whitelist, send commands, and more.

## Project Structure
```
~/afk-andy/
  bot/
    main.py          ← Discord bot, personality, chat responses
    commands.py      ← MC management commands (!start, !stop, !whitelist, etc.)
    minecraft.py     ← Server process management + RCON wrapper
    utils.py         ← Logging helpers
  minecraft/         ← Paper server directory (JAR, world, config)
  scripts/           ← Setup and start scripts
  memory/            ← Task/event logging
```

## Do NOT modify
- `.env` (contains secrets)
- `minecraft/world*` (world data)
- `minecraft/server.properties` (server config — edit via RCON or manually)
