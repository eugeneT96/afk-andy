import os
import random
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

# Casual chat responses for non-command messages
CHAT_RESPONSES = {
    "greetings": {
        "triggers": ["hey andy", "hi andy", "yo andy", "sup andy", "hello andy", "whats up andy", "hey", "yo", "sup", "hello"],
        "replies": [
            "Yo! What's up?",
            "Hey! Need something built?",
            "What's good! Got a task for me?",
            "Sup! I'm here. Hit me with a `!build` if you need something.",
            "Hey hey! What are we working on?",
        ],
    },
    "thanks": {
        "triggers": ["thanks andy", "thank you andy", "thanks", "thank you", "thx", "ty", "good job", "nice work", "nice one", "well done", "great job", "looks good", "perfect", "awesome"],
        "replies": [
            "Anytime! That's what I'm here for.",
            "No problem. Got more for me?",
            "Glad you like it! What's next?",
            "Thanks! I try. Want me to keep going?",
            "Appreciate it! I'm ready for the next one.",
        ],
    },
    "how": {
        "triggers": ["how are you", "how you doing", "you good", "you alive"],
        "replies": [
            "I'm good! Servers are warm, code is flowing. You?",
            "Living the dream. Literally. I'm a bot.",
            "Running smooth. Ready to build whenever you are.",
            "Online and caffeinated. Well, electrically speaking.",
        ],
    },
    "what": {
        "triggers": ["what can you do", "what do you do", "help", "commands"],
        "replies": [
            "Here's what I got:\n`!build <task>` - I'll build/change the website\n`!status` - What's been built\n`!log` - My recent work\n`!git` - Git history\n`!site` - Website info\n`!yo` - Just say hi\n\nOr just talk to me, I'm not just a command bot!",
        ],
    },
    "opinion": {
        "triggers": ["what do you think", "thoughts?", "your opinion", "how does it look", "is it good"],
        "replies": [
            "I think it's looking solid. But I'm biased - I built it.",
            "Honestly? Pretty clean. But you tell me - you're the boss.",
            "I dig it. Want me to change anything?",
            "It's getting there! What do you think needs work?",
        ],
    },
    "bored": {
        "triggers": ["im bored", "i'm bored", "nothing to do", "boring"],
        "replies": [
            "Bored? Let's build something wild. Give me a `!build` challenge.",
            "You're bored but I'm right here? Come on, let's make something cool.",
            "I'm literally a website-building AI and you're bored? `!build` something!",
        ],
    },
    "funny": {
        "triggers": ["tell me a joke", "joke", "make me laugh", "lol", "lmao", "haha"],
        "replies": [
            "Why do programmers prefer dark mode? Because light attracts bugs.",
            "I'd tell you a UDP joke, but you might not get it.",
            "A SQL query walks into a bar, walks up to two tables and asks... 'Can I JOIN you?'",
            "There are only 10 types of people in the world. Those who understand binary, and those who don't.",
            "Why was the JavaScript developer sad? Because he didn't Node how to Express himself.",
        ],
    },
}

# Fallback when nothing matches
FALLBACK_REPLIES = [
    "Not sure what you mean, but I'm here! Need a `!build`?",
    "I'm better at building websites than conversations, ngl. Try `!build <something>`.",
    "Hmm, didn't catch that. But if you need something built, I'm your bot.",
    "I hear you. Want me to do something? `!build` is the magic word.",
]


@bot.event
async def on_ready():
    log.info("AFK Andy is online as " + str(bot.user))
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        startup = random.choice([
            "AFK Andy is online. Ready to build. Send `!build` to get started.",
            "I'm back! What are we building today?",
            "Andy's in the building. Literally. What's the move?",
            "Online and ready. Drop a `!build` and let's go.",
        ])
        await channel.send("**" + startup + "**")


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.channel.id != CHANNEL_ID:
        return
    if message.author.id not in ALLOWED_USERS:
        return

    content = message.content.strip()

    # If it's a command, just react and process
    if content.startswith("!"):
        await message.add_reaction("\u2705")
        await bot.process_commands(message)
        return

    # Casual chat — check triggers
    content_lower = content.lower().strip("?.!,")
    for category in CHAT_RESPONSES.values():
        for trigger in category["triggers"]:
            if trigger in content_lower:
                await message.add_reaction("\U0001f4ac")  # speech bubble
                reply = random.choice(category["replies"])
                await message.reply(reply, mention_author=False)
                return

    # If nothing matched and message is short (likely directed at Andy), use fallback
    # Skip fallback for long messages (probably people talking to each other)
    if len(content) < 100:
        # 50% chance to respond to unrecognized short messages
        if random.random() < 0.5:
            await message.add_reaction("\U0001f914")  # thinking face
            await message.reply(random.choice(FALLBACK_REPLIES), mention_author=False)


async def setup_hook():
    from commands import setup_commands
    setup_commands(bot)


bot.setup_hook = setup_hook

if __name__ == "__main__":
    if not TOKEN:
        log.error("DISCORD_BOT_TOKEN not set in .env")
        exit(1)
    bot.run(TOKEN)
