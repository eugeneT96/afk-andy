import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.expanduser("~/afk-andy/memory/errors.log")),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("afk-andy")

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
ALLOWED_USERS = {
    int(os.getenv("LEO_DISCORD_ID")),
    int(os.getenv("EUGENE_DISCORD_ID")),
}

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    log.info(f"AFK Andy is online as {bot.user}")
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("**AFK Andy is online.** Ready to build. Send `!help` for commands.")


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.channel.id != CHANNEL_ID:
        return
    if message.author.id not in ALLOWED_USERS:
        return
    # Acknowledge receipt
    await message.add_reaction("\u2705")
    await bot.process_commands(message)


async def setup_hook():
    from commands import setup_commands
    setup_commands(bot)


bot.setup_hook = setup_hook

if __name__ == "__main__":
    if not TOKEN:
        log.error("DISCORD_BOT_TOKEN not set in .env")
        exit(1)
    bot.run(TOKEN)
