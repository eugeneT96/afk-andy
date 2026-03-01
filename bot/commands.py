import os
import subprocess
import random
import discord
from discord.ext import commands
from datetime import datetime
import asyncio
import logging

log = logging.getLogger("afk-andy")

PROJECT_DIR = os.path.expanduser("~/afk-andy")

# Personality lines
START_LINES = [
    "Firing up the server... give it a minute.",
    "Server's booting. Grab your pickaxe.",
    "Starting the world. Hold tight...",
    "Spinning up the server. ETA ~30 seconds.",
]
STOP_LINES = [
    "Shutting it down. Save your stuff!",
    "Server going offline. Peace out.",
    "Pulling the plug. Hope you saved.",
    "Lights out. Server going down.",
]
RESTART_LINES = [
    "Restarting... back in a sec.",
    "Bouncing the server. Hang tight.",
    "Quick restart. Don't panic.",
]
FAIL_LINES = [
    "Yikes, something broke:",
    "Hit a wall on this one:",
    "Ran into trouble:",
]

ACK_LINES = [
    "On it, boss. Give me a sec...",
    "Say less. I'm on it.",
    "Got it. Let me think about this...",
    "Roger that. Working on it...",
    "Copy. Let me cook.",
]

PROGRESS_LINES = [
    "Thinking about the best approach...",
    "Running some commands...",
    "Almost there...",
    "Figuring it out...",
    "Working on it...",
]

DONE_LINES = [
    "Done! Here's what I did:",
    "All wrapped up:",
    "Handled it:",
]


def setup_commands(bot: commands.Bot):

    @bot.command(name="start")
    async def start_cmd(ctx):
        """Start the Minecraft server."""
        from minecraft import start_server
        await ctx.send(random.choice(START_LINES))
        success, msg = start_server()
        if success:
            await ctx.send("Server is starting. Give it 30-60 seconds to fully load, then `!status` to check.")
        else:
            await ctx.send(f"{random.choice(FAIL_LINES)} {msg}")

    @bot.command(name="stop")
    async def stop_cmd(ctx):
        """Stop the Minecraft server."""
        from minecraft import stop_server
        await ctx.send(random.choice(STOP_LINES))
        success, msg = stop_server()
        await ctx.send(msg)

    @bot.command(name="restart")
    async def restart_cmd(ctx):
        """Restart the Minecraft server."""
        from minecraft import stop_server, start_server, is_server_running
        await ctx.send(random.choice(RESTART_LINES))
        if is_server_running():
            stop_server()
            await asyncio.sleep(10)
        success, msg = start_server()
        if success:
            await ctx.send("Server is coming back up! Give it 30-60 seconds.")
        else:
            await ctx.send(f"{random.choice(FAIL_LINES)} {msg}")

    @bot.command(name="status")
    async def status_cmd(ctx):
        """Show server status."""
        from minecraft import is_server_running, async_rcon
        if not is_server_running():
            await ctx.send("Server is **offline**. Use `!start` to fire it up.")
            return
        try:
            players = await async_rcon("list")
            embed = discord.Embed(title="Server Status", color=0x55FF55, timestamp=datetime.utcnow())
            embed.add_field(name="State", value="Online", inline=True)
            embed.add_field(name="Players", value=players, inline=False)
            embed.set_footer(text="AFK Andy MC")
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Server is running but RCON isn't responding yet: `{e}`\nMight still be booting -- try again in a bit.")

    @bot.command(name="players", aliases=["list"])
    async def players_cmd(ctx):
        """Show online players."""
        from minecraft import is_server_running, async_rcon
        if not is_server_running():
            await ctx.send("Server is offline. No one's playing.")
            return
        try:
            result = await async_rcon("list")
            await ctx.send(result)
        except Exception as e:
            await ctx.send(f"Couldn't check players: `{e}`")

    @bot.command(name="whitelist")
    async def whitelist_cmd(ctx, action: str = None, player: str = None):
        """Manage the whitelist: !whitelist add/remove/list <player>"""
        from minecraft import async_rcon
        if not action:
            await ctx.send("Usage: `!whitelist add <name>`, `!whitelist remove <name>`, `!whitelist list`")
            return
        action = action.lower()
        if action == "list":
            try:
                result = await async_rcon("whitelist list")
                await ctx.send(result)
            except Exception as e:
                await ctx.send(f"Failed: `{e}`")
        elif action in ("add", "remove") and player:
            try:
                result = await async_rcon(f"whitelist {action} {player}")
                await ctx.send(result)
            except Exception as e:
                await ctx.send(f"Failed: `{e}`")
        else:
            await ctx.send("Usage: `!whitelist add <name>` or `!whitelist remove <name>`")

    @bot.command(name="cmd")
    async def cmd_cmd(ctx, *, command: str = None):
        """Send a raw command to the MC console via RCON."""
        if not command:
            await ctx.send("What command? Usage: `!cmd <minecraft command>`")
            return
        from minecraft import async_rcon
        try:
            result = await async_rcon(command)
            response = result if result.strip() else "(no output)"
            await ctx.send(f"```\n{response}\n```")
        except Exception as e:
            await ctx.send(f"Command failed: `{e}`")

    @bot.command(name="say")
    async def say_cmd(ctx, *, message: str = None):
        """Broadcast a message in-game from Discord."""
        if not message:
            await ctx.send("Say what? Usage: `!say <message>`")
            return
        from minecraft import async_rcon
        try:
            await async_rcon(f"say [Discord] {ctx.author.display_name}: {message}")
            await ctx.send(f"Sent to server: {message}")
        except Exception as e:
            await ctx.send(f"Couldn't send: `{e}`")

    @bot.command(name="backup")
    async def backup_cmd(ctx):
        """Save the world."""
        from minecraft import is_server_running, async_rcon
        if not is_server_running():
            await ctx.send("Server is offline, nothing to back up.")
            return
        await ctx.send("Saving world...")
        try:
            await async_rcon("save-all")
            await asyncio.sleep(3)
            await ctx.send("World saved!")
        except Exception as e:
            await ctx.send(f"Save failed: `{e}`")

    @bot.command(name="build")
    async def build_cmd(ctx, *, description: str = None):
        """Hand off a complex task to Claude Code CLI."""
        if not description:
            await ctx.send("What do you need? Usage: `!build <describe what you want>`")
            return

        ack = random.choice(ACK_LINES)
        await ctx.send(f"**{description}**\n{ack}")

        async def send_progress(stop_event):
            available = list(PROGRESS_LINES)
            random.shuffle(available)
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=15)
                return
            except asyncio.TimeoutError:
                pass
            while not stop_event.is_set() and available:
                await ctx.send(f"*{available.pop()}*")
                try:
                    await asyncio.wait_for(stop_event.wait(), timeout=25)
                    return
                except asyncio.TimeoutError:
                    pass

        stop_event = asyncio.Event()
        progress_task = asyncio.create_task(send_progress(stop_event))

        try:
            rcon_script = os.path.join(PROJECT_DIR, "scripts", "rcon.py")
            python_bin = os.path.join(PROJECT_DIR, "venv", "bin", "python")
            prompt = (
                f"You are managing a Minecraft server. "
                f"To send commands to the server, run: {python_bin} {rcon_script} <command>\n"
                f"Examples:\n"
                f"  {python_bin} {rcon_script} time set day\n"
                f"  {python_bin} {rcon_script} gamemode creative Steve\n"
                f"  {python_bin} {rcon_script} gamerule doDaylightCycle false\n"
                f"  {python_bin} {rcon_script} whitelist add Steve\n"
                f"  {python_bin} {rcon_script} give Steve diamond 64\n\n"
                f"Server config is at /home/eugene/minecraft-server/server.properties\n"
                f"TASK: {description}\n"
                f"Do what's needed. If it requires multiple commands, run them all."
            )

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    [
                        "claude", "-p", "--output-format", "text",
                        "--allowedTools", "Bash Read Edit Write Glob Grep",
                        "--max-budget-usd", "1.00",
                        prompt,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=PROJECT_DIR,
                )
            )

            stop_event.set()
            await progress_task

            if result.returncode != 0:
                error_msg = result.stderr[:500] if result.stderr else "No details"
                await ctx.send(f"{random.choice(FAIL_LINES)}\n```{error_msg}```")
                return

            response_text = result.stdout.strip()
            done = random.choice(DONE_LINES)

            embed = discord.Embed(
                title=done,
                description=description,
                color=0x00FF41,
                timestamp=datetime.utcnow(),
            )

            if response_text:
                preview = response_text[:800] + ("..." if len(response_text) > 800 else "")
                embed.add_field(name="Andy's Notes", value=f"```\n{preview}\n```", inline=False)

            embed.set_footer(text="Powered by Claude")
            await ctx.send(embed=embed)

        except subprocess.TimeoutExpired:
            stop_event.set()
            await progress_task
            await ctx.send("That one took too long. Timed out after 5 minutes.")
        except Exception as e:
            stop_event.set()
            await progress_task
            await ctx.send(f"{random.choice(FAIL_LINES)} `{e}`")

    @bot.command(name="yo")
    async def yo_cmd(ctx):
        """Just say hi to Andy."""
        greetings = [
            "Yo! Server's humming. Need anything?",
            "What's up! Want me to check on the server?",
            "Hey! I'm here. `!status` to see how the server's doing.",
            "Sup. I'm watching the server. What do you need?",
        ]
        await ctx.send(random.choice(greetings))
