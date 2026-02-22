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


def update_project_state(feature: str, files: list):
    """Update project-state.json with new feature info."""
    state_path = os.path.join(MEMORY_DIR, "project-state.json")
    try:
        with open(state_path) as f:
            state = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        state = {"features": [], "files": [], "last_updated": None}

    state["features"].append(feature)
    for fp in files:
        if fp not in state["files"]:
            state["files"].append(fp)
    state["last_updated"] = datetime.utcnow().isoformat()

    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)


def git_sync(message: str) -> str:
    """Auto-commit and push changes to GitHub."""
    try:
        subprocess.run(["git", "add", "-A"], cwd=PROJECT_DIR, check=True)

        # Check if there's anything to commit
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


def clean_message(raw: str) -> str:
    """Clean up user message for the architect.
    Strips filler words and formats as a clear instruction.
    """
    filler = ["um", "uh", "like", "you know", "basically", "literally", "just"]
    words = raw.split()
    cleaned = [w for w in words if w.lower().strip(",.!?") not in filler]
    return " ".join(cleaned).strip()


def get_file_context(files: list) -> str:
    """Read relevant website files to provide context to the architect."""
    context_parts = []
    website_dir = os.path.join(PROJECT_DIR, "website")

    for fname in files:
        fpath = os.path.join(website_dir, fname)
        if os.path.exists(fpath):
            try:
                with open(fpath) as f:
                    content = f.read()
                context_parts.append(f"=== {fname} ===\n{content}\n=== END ===")
            except Exception:
                pass

    return "\n\n".join(context_parts)
