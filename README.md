# AFK Andy

A gaming website built by AI architects that work autonomously while the team is AFK.

**Live at: [simbot.cloud](https://simbot.cloud)**

## How It Works

1. Leo or Eugene send instructions via Discord (e.g. `!build add a leaderboard`)
2. Discord bot (AFK Andy#9271) receives the task
3. AI architect writes/modifies the website code
4. Changes auto-sync to GitHub and go live immediately
5. Bot reports results back in Discord

## Two AI Tiers

| Command | Engine | Speed | Best For |
|---------|--------|-------|----------|
| `!build` | Qwen3 4B (local, via Ollama) | Fast (~30s) | Simple edits, new sections, styling |
| `!claude` | Claude Code CLI (Anthropic) | Slower (~2min) | Complex features, multi-file changes |

## All Commands

- `!build <task>` — Local AI architect modifies the website
- `!claude <task>` — Claude Code handles complex tasks
- `!status` — Show project feature list
- `!log` — Show recent task history
- `!git` — Show recent git commits
- `!preview` — Show website info and live URL

## Tech Stack

- **Website**: Vanilla HTML/CSS/JS, dark theme (#0a0a0f + #00ff41 neon green)
- **Bot**: Python, discord.py
- **Local AI**: Ollama + Qwen3 4B
- **Flagship AI**: Claude Code CLI
- **Hosting**: Cloudflare Tunnel → Ubuntu laptop
- **Version Control**: GitHub (auto-push on every build)

## Quick Start (on the build server)

```bash
# Start Ollama (usually auto-starts)
ollama serve

# Start the website server
cd ~/afk-andy/website && python3 -m http.server 8080 &

# Start the Discord bot
cd ~/afk-andy/bot && ~/afk-andy/venv/bin/python main.py &
```

## Team

- **Eugene (dGen)** — Project owner, runs the build server
- **Leo** — Co-builder, gives instructions via Discord
- **AFK Andy** — The AI that does the actual work
