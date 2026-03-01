import os
import json
import subprocess
import logging
from datetime import datetime

log = logging.getLogger("afk-andy")

PROJECT_DIR = os.path.expanduser("~/afk-andy")
MEMORY_DIR = os.path.join(PROJECT_DIR, "memory")


def log_task(task: str, status: str, details=None):
    """Append a task entry to task-log.json."""
    log_path = os.path.join(MEMORY_DIR, "task-log.json")
    try:
        with open(log_path) as f:
            tasks = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        tasks = []

    tasks.append({
        "task": task,
        "status": status,
        "details": details,
        "timestamp": datetime.utcnow().isoformat(),
    })

    with open(log_path, "w") as f:
        json.dump(tasks, f, indent=2)

    log.info(f"Task logged: [{status}] {task}")


def git_sync(message: str) -> str:
    """Auto-commit and push changes to GitHub."""
    try:
        subprocess.run(["git", "add", "-A"], cwd=PROJECT_DIR, check=True)

        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=PROJECT_DIR,
        )
        if result.returncode == 0:
            return "No changes to commit."

        subprocess.run(
            ["git", "commit", "-m", f"Auto: {message}"],
            cwd=PROJECT_DIR,
            check=True,
        )
        subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=PROJECT_DIR,
            check=True,
        )
        return f"Pushed: {message}"
    except subprocess.CalledProcessError as e:
        log.error(f"Git sync failed: {e}")
        return f"Git sync failed: {e}"
