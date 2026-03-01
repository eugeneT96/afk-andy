import os
import subprocess
import asyncio
import logging

from mcrcon import MCRcon

log = logging.getLogger("afk-andy")

MC_DIR = os.getenv("MC_SERVER_DIR", os.path.expanduser("~/afk-andy/minecraft"))
MC_JAR = os.getenv("MC_JAR", "paper.jar")
MC_RAM = os.getenv("MC_RAM", "4G")
RCON_HOST = os.getenv("RCON_HOST", "localhost")
RCON_PORT = int(os.getenv("RCON_PORT", "25575"))
RCON_PASSWORD = os.getenv("RCON_PASSWORD", "changeme")
SCREEN_NAME = "minecraft-afkandy"


def is_server_running() -> bool:
    """Check if the MC screen session exists."""
    result = subprocess.run(["screen", "-list"], capture_output=True, text=True)
    return SCREEN_NAME in result.stdout


def start_server() -> tuple:
    """Start the Paper server in a detached screen session."""
    if is_server_running():
        return False, "Server is already running."

    jar_path = os.path.join(MC_DIR, MC_JAR)
    if not os.path.exists(jar_path):
        return False, f"Server JAR not found at {jar_path}"

    cmd = [
        "screen", "-dmS", SCREEN_NAME,
        "java", f"-Xms{MC_RAM}", f"-Xmx{MC_RAM}",
        "-jar", MC_JAR, "nogui",
    ]
    try:
        subprocess.run(cmd, cwd=MC_DIR, check=True)
        return True, "Server starting up..."
    except subprocess.CalledProcessError as e:
        return False, f"Failed to start: {e}"


def stop_server() -> tuple:
    """Stop the server gracefully via RCON, fall back to screen."""
    if not is_server_running():
        return False, "Server is not running."

    try:
        response = rcon_command("stop")
        return True, "Server shutting down... " + response
    except Exception:
        subprocess.run([
            "screen", "-S", SCREEN_NAME, "-p", "0", "-X", "stuff", "stop\n",
        ])
        return True, "Sent stop command via console."


def rcon_command(command: str) -> str:
    """Send a command to the MC server via RCON and return the response."""
    with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
        response = mcr.command(command)
    return response


async def async_rcon(command: str) -> str:
    """Async wrapper around RCON for use in discord.py commands."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, rcon_command, command)
