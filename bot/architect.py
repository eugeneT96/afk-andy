import os
import json
import requests
import logging
from datetime import datetime

log = logging.getLogger("afk-andy")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = os.getenv("OLLAMA_MODEL", "qwen3:4b")
PROJECT_DIR = os.path.expanduser("~/afk-andy")

SYSTEM_PROMPT = """You are AFK Andy's AI architect. You are a focused web developer.
Your job is to modify and extend an existing gaming website (dark theme, neon green accents).

Rules:
- You will receive the CURRENT file contents in the CONTEXT section.
- MODIFY the existing code — do NOT rewrite from scratch.
- Keep the existing design: dark background (#0a0a0f), neon green (#00ff41), existing CSS classes.
- Use the existing external CSS file (css/style.css) — do NOT use inline styles.
- Use vanilla HTML, CSS, and JavaScript only.
- When outputting code, wrap each COMPLETE file in a block like:
  === FILE: path/relative/to/website ===
  <full file contents with your changes incorporated>
  === END FILE ===
- Only output files that need to change.
- Be concise in explanations.
"""


def query_architect(task, context=""):
    """Send a structured task to the local Qwen model and get a response."""
    prompt = "/no_think\nTASK: " + task
    if context:
        prompt = prompt + "\n\nCONTEXT:\n" + context

    try:
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "system": SYSTEM_PROMPT,
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 8192},
            },
            timeout=300,
        )
        resp.raise_for_status()
        data = resp.json()
        return {"success": True, "response": data.get("response", ""), "error": None}
    except requests.ConnectionError:
        return {"success": False, "response": "", "error": "Ollama is not running. Start it with: ollama serve"}
    except requests.Timeout:
        return {"success": False, "response": "", "error": "Architect timed out (300s limit)."}
    except Exception as e:
        return {"success": False, "response": "", "error": str(e)}


def parse_file_blocks(response):
    """Parse === FILE: ... === blocks from architect response into file operations."""
    files = []
    lines = response.split("\n")
    current_file = None
    current_content = []

    for line in lines:
        if line.startswith("=== FILE:") and line.endswith("==="):
            if current_file:
                files.append({"path": current_file, "content": "\n".join(current_content)})
            current_file = line.replace("=== FILE:", "").replace("===", "").strip()
            current_content = []
        elif line.strip() == "=== END FILE ===" and current_file:
            files.append({"path": current_file, "content": "\n".join(current_content)})
            current_file = None
            current_content = []
        elif current_file is not None:
            current_content.append(line)

    if current_file:
        files.append({"path": current_file, "content": "\n".join(current_content)})

    return files


def apply_file_changes(files):
    """Write parsed file blocks to disk. Returns list of written paths."""
    written = []
    website_dir = os.path.join(PROJECT_DIR, "website")

    for f in files:
        filepath = os.path.join(website_dir, f["path"])
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as fh:
            fh.write(f["content"])
        written.append(f["path"])
        log.info("Wrote: " + filepath)

    return written


def build_task(task_description, context=""):
    """Full pipeline: query architect -> parse files -> write to disk."""
    log.info("Architect received task: " + task_description)

    result = query_architect(task_description, context)
    if not result["success"]:
        return {"success": False, "error": result["error"], "files": [], "response": ""}

    response_text = result["response"]
    files = parse_file_blocks(response_text)

    written = []
    if files:
        written = apply_file_changes(files)

    return {
        "success": True,
        "error": None,
        "files": written,
        "response": response_text,
    }
