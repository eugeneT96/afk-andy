#!/bin/bash
# Manual git sync script
cd ~/afk-andy

MESSAGE="${1:-Manual sync}"

git add -A
if git diff --cached --quiet; then
    echo "Nothing to commit."
else
    git commit -m "Auto: $MESSAGE"
    git push origin main
    echo "Pushed: $MESSAGE"
fi
