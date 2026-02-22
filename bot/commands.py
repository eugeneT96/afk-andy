import os
import json
import subprocess
import discord
from discord.ext import commands
from datetime import datetime
import asyncio
import logging

log = logging.getLogger("afk-andy")

PROJECT_DIR = os.path.expanduser("~/afk-andy")


def setup_commands(bot: commands.Bot):

    @bot.command(name="build")
    async def build_cmd(ctx, *, description: str = None):
        """Tell the architect to build something."""
        if not description:
            await ctx.send("Usage: `!build <description of what to build>`")
            return

        await ctx.send(f"**Building:** {description}\nArchitect is working on it...")

        from architect import build_task
        from utils import log_task, update_project_state, git_sync

        # Feed existing website files as context so architect modifies, not replaces
        from utils import get_file_context
        context = get_file_context(["index.html", "css/style.css", "js/main.js"])
        result = build_task(description, context)

        if not result["success"]:
            await ctx.send(f"**Build failed:** {result['error']}")
            log_task(description, "failed", result["error"])
            return

        files_changed = result["files"]
        response_text = result["response"]

        # Log the task
        log_task(description, "completed", files_changed)
        update_project_state(description, files_changed)

        # Auto-sync to GitHub
        sync_result = git_sync("Build: " + description[:50])

        # Build response embed
        embed = discord.Embed(
            title="Build Complete",
            description=description,
            color=0x00FF41,
            timestamp=datetime.utcnow(),
        )
        if files_changed:
            embed.add_field(
                name="Files Changed",
                value="\n".join("`" + f + "`" for f in files_changed[:10]),
                inline=False,
            )
        if sync_result:
            embed.add_field(name="Git", value=sync_result, inline=False)

        # Truncate architect response for Discord
        if response_text:
            preview = response_text[:500] + ("..." if len(response_text) > 500 else "")
            embed.add_field(name="Architect Notes", value="```\n" + preview + "\n```", inline=False)

        await ctx.send(embed=embed)

    @bot.command(name="status")
    async def status_cmd(ctx):
        """Get current project status."""
        state_path = os.path.join(PROJECT_DIR, "memory", "project-state.json")
        try:
            with open(state_path) as f:
                state = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            await ctx.send("No project state yet. Use `!build` to start building.")
            return

        embed = discord.Embed(title="Project Status", color=0x00BFFF)
        features = state.get("features", [])
        if features:
            recent = features[-5:]
            embed.add_field(
                name="Recent Features",
                value="\n".join("- " + f for f in recent),
                inline=False,
            )
        embed.add_field(
            name="Total Features",
            value=str(len(features)),
            inline=True,
        )
        await ctx.send(embed=embed)

    @bot.command(name="log")
    async def log_cmd(ctx):
        """Show recent task log."""
        log_path = os.path.join(PROJECT_DIR, "memory", "task-log.json")
        try:
            with open(log_path) as f:
                tasks = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            await ctx.send("No tasks logged yet.")
            return

        recent = tasks[-5:]
        embed = discord.Embed(title="Recent Tasks", color=0xFFA500)
        for t in recent:
            status_icon = "\u2705" if t["status"] == "completed" else "\u274C"
            embed.add_field(
                name=status_icon + " " + t["task"][:50],
                value="Status: " + t["status"] + " | " + t["timestamp"],
                inline=False,
            )
        await ctx.send(embed=embed)

    @bot.command(name="git")
    async def git_cmd(ctx):
        """Show recent git activity."""
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

        embed = discord.Embed(title="Recent Git Log", color=0x6E5494)
        embed.description = "```\n" + output + "\n```"
        await ctx.send(embed=embed)

    @bot.command(name="claude")
    async def claude_cmd(ctx, *, description: str = None):
        """Use Claude Code (flagship AI) for complex tasks."""
        if not description:
            await ctx.send("Usage: `!claude <description of what to build or change>`")
            return

        await ctx.send("**Claude is working on:** " + description + "\nThis may take a minute...")

        from utils import log_task, update_project_state, git_sync

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
                    ["claude", "-p", "--output-format", "text", prompt],
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=PROJECT_DIR,
                )
            )

            if result.returncode != 0:
                error_msg = result.stderr[:500] if result.stderr else "Unknown error"
                await ctx.send("**Claude failed:** ```" + error_msg + "```")
                log_task("[claude] " + description, "failed", error_msg)
                return

            response_text = result.stdout.strip()

            # Check what files changed
            diff_result = subprocess.run(
                ["git", "diff", "--name-only"],
                capture_output=True, text=True, cwd=PROJECT_DIR,
            )
            files_changed = [f for f in diff_result.stdout.strip().split("\n") if f]

            log_task("[claude] " + description, "completed", files_changed)
            if files_changed:
                update_project_state("[claude] " + description, files_changed)

            sync_result = git_sync("Claude: " + description[:50])

            embed = discord.Embed(
                title="Claude Build Complete",
                description=description,
                color=0x7C3AED,
                timestamp=datetime.utcnow(),
            )
            if files_changed:
                embed.add_field(
                    name="Files Changed",
                    value="\n".join("`" + f + "`" for f in files_changed[:10]),
                    inline=False,
                )
            if sync_result:
                embed.add_field(name="Git", value=sync_result, inline=False)
            if response_text:
                preview = response_text[:800] + ("..." if len(response_text) > 800 else "")
                embed.add_field(name="Claude Notes", value="```\n" + preview + "\n```", inline=False)

            await ctx.send(embed=embed)

        except subprocess.TimeoutExpired:
            await ctx.send("**Claude timed out** (5 minute limit).")
            log_task("[claude] " + description, "failed", "Timeout")
        except Exception as e:
            await ctx.send("**Error:** " + str(e))
            log_task("[claude] " + description, "failed", str(e))

    @bot.command(name="preview")
    async def preview_cmd(ctx):
        """Get info about the current website state."""
        index_path = os.path.join(PROJECT_DIR, "website", "index.html")
        if not os.path.exists(index_path):
            await ctx.send("No website built yet. Use `!build` to create one.")
            return

        size = os.path.getsize(index_path)
        file_count = sum(len(files) for _, _, files in os.walk(os.path.join(PROJECT_DIR, "website")))

        embed = discord.Embed(title="Website Preview", color=0xFF6EC7)
        embed.add_field(name="index.html", value=str(size) + " bytes", inline=True)
        embed.add_field(name="Total Files", value=str(file_count), inline=True)
        embed.add_field(
            name="View",
            value="Website is live at `https://simbot.cloud`",
            inline=False,
        )
        await ctx.send(embed=embed)
