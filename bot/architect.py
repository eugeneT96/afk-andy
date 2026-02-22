import os
import re
import json
import requests
import logging
from datetime import datetime

log = logging.getLogger("afk-andy")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = os.getenv("OLLAMA_MODEL", "qwen3:4b")
PROJECT_DIR = os.path.expanduser("~/afk-andy")

SYSTEM_PROMPT = """You are a web developer. You modify an existing gaming website.

IMPORTANT FORMAT — you MUST output complete files like this:

=== FILE: index.html ===
<!DOCTYPE html>
<html>
...entire file content here...
</html>
=== END FILE ===

=== FILE: css/style.css ===
...entire file content here...
=== END FILE ===

RULES:
- Output COMPLETE file contents, not snippets or diffs
- Use === FILE: path === and === END FILE === markers exactly as shown
- Keep dark theme: background #0a0a0f, accent #00ff41
- Use external CSS (css/style.css), no inline styles
- Vanilla HTML/CSS/JS only
- Only output files that changed
- The CONTEXT section has the current file contents — modify them, do not rewrite from scratch
"""


def query_architect(task, context=""):
    """Send a structured task to the local Qwen model and get a response."""
    prompt = "/no_think\nTASK: " + task
    if context:
        prompt = prompt + "\n\nCONTEXT (current files):\n" + context

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
    """Parse file blocks from architect response. Handles multiple formats."""
    files = []

    # Format 1: === FILE: path === ... === END FILE ===
    lines = response.split("\n")
    current_file = None
    current_content = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("=== FILE:") and stripped.endswith("==="):
            if current_file:
                files.append({"path": current_file, "content": "\n".join(current_content)})
            current_file = stripped.replace("=== FILE:", "").replace("===", "").strip()
            current_content = []
        elif stripped == "=== END FILE ===" and current_file:
            files.append({"path": current_file, "content": "\n".join(current_content)})
            current_file = None
            current_content = []
        elif current_file is not None:
            current_content.append(line)

    if current_file:
        files.append({"path": current_file, "content": "\n".join(current_content)})

    # If format 1 found files, use them
    if files:
        return files

    # Format 2: markdown code blocks with filename hints
    # Look for patterns like: ```html or ```css or ### `index.html` ... ```
    # Map language hints to known file paths
    lang_to_path = {
        "html": "index.html",
        "css": "css/style.css",
        "javascript": "js/main.js",
        "js": "js/main.js",
    }

    # Try to extract code blocks with their language
    pattern = r'```(\w+)\s*\n(.*?)```'
    matches = re.findall(pattern, response, re.DOTALL)

    for lang, content in matches:
        lang_lower = lang.lower()
        # Check if the content looks like a complete file (not a snippet)
        content = content.strip()
        is_complete = False
        if lang_lower == "html" and ("<!DOCTYPE" in content or "<html" in content):
            is_complete = True
        elif lang_lower == "css" and len(content.split("\n")) > 5:
            is_complete = True
        elif lang_lower in ("js", "javascript") and len(content.split("\n")) > 3:
            is_complete = True

        if is_complete and lang_lower in lang_to_path:
            # Check if a filename was mentioned before this code block
            path = lang_to_path[lang_lower]

            # Look for explicit filename mentions near the code block
            block_start = response.find("```" + lang)
            if block_start > 0:
                preceding = response[max(0, block_start - 200):block_start]
                # Check for filename mentions like `index.html` or index.html
                for known_path in ["index.html", "css/style.css", "js/main.js"]:
                    if known_path in preceding:
                        path = known_path
                        break

            files.append({"path": path, "content": content})

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

    if not files:
        log.warning("Architect responded but no file blocks were parsed. Response: " + response_text[:500])

    written = []
    if files:
        written = apply_file_changes(files)

    return {
        "success": True,
        "error": None,
        "files": written,
        "response": response_text,
    }
