import os
import json
import subprocess
import random
import discord
from discord.ext import commands
from datetime import datetime
import asyncio
import logging

log = logging.getLogger("afk-andy")

PROJECT_DIR = os.path.expanduser("~/afk-andy")

# Andy's personality lines
ACK_LINES = [
    "On it, boss. Give me a sec...",
    "Say less. I'm on it.",
    "Got it. Putting the engineer on this now...",
    "Roger that. Brewing some code...",
    "Heard you loud and clear. Working on it...",
    "Already on it. Sit tight.",
    "Copy. Let me cook.",
]

# Progress updates while Claude works (sent at intervals)
PROGRESS_LINES = [
    "Reading through the code...",
    "Hmm, I see what you're going for...",
    "Making some changes...",
    "Tweaking the styles...",
    "Almost there, just cleaning things up...",
    "Looking good so far...",
    "Writing some fresh code...",
    "Touching up a few things...",
    "Putting the finishing touches on...",
    "Just about wrapped up...",
]

DONE_LINES = [
    "Done! Check it out:",
    "All wrapped up. Here's what I did:",
    "Boom. Built it. Take a look:",
    "Ship it! Here's the rundown:",
    "That's a wrap. Here's the damage report:",
]

FAIL_LINES = [
    "Yikes, something broke. Here's what happened:",
    "Hit a wall on this one:",
    "Ran into trouble. Details below:",
    "Not gonna lie, this one didn't go great:",
]

TIMEOUT_LINES = [
    "That one was too big for me. Timed out after 5 minutes.",
    "I choked on that one. Hit the 5 minute limit.",
    "Took too long, had to bail. Try breaking it into smaller tasks.",
]

NO_CHANGES_LINES = [
    "I looked at it but didn't end up changing anything. Might need more detail.",
    "Hmm, nothing actually changed. Can you be more specific?",
    "Came back empty-handed. Try rephrasing what you need?",
]


async def send_progress(ctx, stop_event):
    """Send progress messages while Claude is working."""
    used = []
    available = list(PROGRESS_LINES)
    random.shuffle(available)

    # Wait 15 seconds before first progress message
    try:
        await asyncio.wait_for(stop_event.wait(), timeout=15)
        return  # Claude finished before first update
    except asyncio.TimeoutError:
        pass

    while not stop_event.is_set() and available:
        line = available.pop()
        await ctx.send("*" + line + "*")

        # Wait 20-35 seconds between messages
        delay = random.randint(20, 35)
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=delay)
            return  # Claude finished
        except asyncio.TimeoutError:
            pass


def setup_commands(bot: commands.Bot):

    @bot.command(name="build")
    async def build_cmd(ctx, *, description: str = None):
        """Tell Andy to build something."""
        if not description:
            await ctx.send("You gotta tell me what to build! Try: `!build <what you want>`")
            return

        ack = random.choice(ACK_LINES)
        await ctx.send("**" + description + "**\n" + ack)

        from utils import log_task, update_project_state, git_sync

        # Start progress chatter in the background
        stop_event = asyncio.Event()
        progress_task = asyncio.create_task(send_progress(ctx, stop_event))

        try:
            website_dir = os.path.join(PROJECT_DIR, "website")
            prompt = (
                "You are modifying a gaming website at " + website_dir + ". "
                "The site uses a dark theme (#0a0a0f background, #00ff41 neon green accents), "
                "vanilla HTML/CSS/JS, with separate files: index.html, css/style.css, js/main.js. "
                "TASK: " + description + ". "
                "Make the changes directly to the files. Do not create new frameworks or dependencies. "
                "Keep the existing dark gaming aesthetic."
            )

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    ["claude", "-p", "--output-format", "text", "--dangerously-skip-permissions", prompt],
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=PROJECT_DIR,
                )
            )

            # Stop progress chatter
            stop_event.set()
            await progress_task

            if result.returncode != 0:
                error_msg = result.stderr[:500] if result.stderr else "No details available"
                fail = random.choice(FAIL_LINES)
                await ctx.send(fail + "\n```" + error_msg + "```")
                log_task(description, "failed", error_msg)
                return

            response_text = result.stdout.strip()

            # Check what files changed
            diff_result = subprocess.run(
                ["git", "diff", "--name-only"],
                capture_output=True, text=True, cwd=PROJECT_DIR,
            )
            files_changed = [f for f in diff_result.stdout.strip().split("\n") if f]

            if not files_changed:
                await ctx.send(random.choice(NO_CHANGES_LINES))
                log_task(description, "completed", [])
                return

            log_task(description, "completed", files_changed)
            update_project_state(description, files_changed)

            sync_result = git_sync(description[:50])

            done = random.choice(DONE_LINES)
            embed = discord.Embed(
                title=done,
                description=description,
                color=0x00FF41,
                timestamp=datetime.utcnow(),
            )
            embed.add_field(
                name="Files Touched",
                value="\n".join("`" + f + "`" for f in files_changed[:10]),
                inline=False,
            )
            if sync_result:
                embed.add_field(name="Git", value=sync_result, inline=False)
            embed.set_footer(text="Live at simbot.cloud")

            if response_text:
                preview = response_text[:600] + ("..." if len(response_text) > 600 else "")
                embed.add_field(name="Andy's Notes", value="```\n" + preview + "\n```", inline=False)

            await ctx.send(embed=embed)

        except subprocess.TimeoutExpired:
            stop_event.set()
            await progress_task
            await ctx.send(random.choice(TIMEOUT_LINES))
            log_task(description, "failed", "Timeout")
        except Exception as e:
            stop_event.set()
            await progress_task
            fail = random.choice(FAIL_LINES)
            await ctx.send(fail + "\n`" + str(e) + "`")
            log_task(description, "failed", str(e))

    @bot.command(name="status")
    async def status_cmd(ctx):
        """Ask Andy what's been going on."""
        state_path = os.path.join(PROJECT_DIR, "memory", "project-state.json")
        try:
            with open(state_path) as f:
                state = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            await ctx.send("Nothing built yet. I'm just sitting here. Give me something to do with `!build`.")
            return

        features = state.get("features", [])
        embed = discord.Embed(
            title="Here's where we're at",
            color=0x00BFFF,
        )
        if features:
            recent = features[-5:]
            embed.add_field(
                name="Latest stuff I built",
                value="\n".join("- " + f for f in recent),
                inline=False,
            )
        embed.add_field(
            name="Total features shipped",
            value=str(len(features)),
            inline=True,
        )
        embed.set_footer(text="Live at simbot.cloud")
        await ctx.send(embed=embed)

    @bot.command(name="log")
    async def log_cmd(ctx):
        """Show Andy's recent work history."""
        log_path = os.path.join(PROJECT_DIR, "memory", "task-log.json")
        try:
            with open(log_path) as f:
                tasks = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            await ctx.send("No tasks in the log yet. I've been slacking.")
            return

        recent = tasks[-5:]
        embed = discord.Embed(title="My recent work", color=0xFFA500)
        for t in recent:
            icon = "\u2705" if t["status"] == "completed" else "\u274C"
            embed.add_field(
                name=icon + " " + t["task"][:50],
                value=t["status"] + " | " + t["timestamp"],
                inline=False,
            )
        await ctx.send(embed=embed)

    @bot.command(name="git")
    async def git_cmd(ctx):
        """Show recent commits."""
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-10"],
                capture_output=True,
                text=True,
                cwd=PROJECT_DIR,
            )
            output = result.stdout.strip() or "No commits yet."
        except Exception as e:
            output = "Error: " + str(e)

        embed = discord.Embed(title="Git history", color=0x6E5494)
        embed.description = "```\n" + output + "\n```"
        await ctx.send(embed=embed)

    @bot.command(name="site")
    async def site_cmd(ctx):
        """Check on the website."""
        index_path = os.path.join(PROJECT_DIR, "website", "index.html")
        if not os.path.exists(index_path):
            await ctx.send("No website yet. Tell me what to build!")
            return

        size = os.path.getsize(index_path)
        file_count = sum(len(files) for _, _, files in os.walk(os.path.join(PROJECT_DIR, "website")))

        embed = discord.Embed(title="The site's up", color=0xFF6EC7)
        embed.add_field(name="index.html", value=str(size) + " bytes", inline=True)
        embed.add_field(name="Total files", value=str(file_count), inline=True)
        embed.add_field(
            name="Check it out",
            value="**https://simbot.cloud**",
            inline=False,
        )
        await ctx.send(embed=embed)

    @bot.command(name="yo")
    async def yo_cmd(ctx):
        """Just say hi to Andy."""
        greetings = [
            "Yo! What's good? Need me to build something?",
            "What's up! I'm online and ready to work.",
            "Hey! Got a task for me? Hit me with `!build <whatever>`.",
            "Sup. I'm here, I'm caffeinated, and I'm ready to code.",
        ]
        await ctx.send(random.choice(greetings))
