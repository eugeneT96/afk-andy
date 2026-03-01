import random
import discord
from discord.ext import commands
from datetime import datetime
import asyncio
import logging

log = logging.getLogger("afk-andy")

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
