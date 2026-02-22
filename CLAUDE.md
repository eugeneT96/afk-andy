# AFK Andy — Project Instructions for Claude Code

## SECURITY BOUNDARIES (MANDATORY)
- You may ONLY read and modify files inside `~/afk-andy/website/`
- You may NOT access, read, or modify anything outside `~/afk-andy/website/`
- You may NOT access `~/afk-andy/bot/`, `~/afk-andy/.env`, `~/afk-andy/memory/`, or any other directory
- You may NOT access `~/.ssh/`, `~/.git-credentials`, `~/.config/`, or any home directory files
- You may NOT run shell commands, install packages, or execute scripts
- You may NOT access any other git repositories on this machine
- You may NOT make network requests or access external services
- If a task requires actions outside these boundaries, refuse and explain why

## What This Is
AFK Andy is a gaming website built autonomously by AI. Users send instructions via Discord, and AI modifies the website files directly.

## Project Structure (your scope is website/ ONLY)
```
~/afk-andy/website/        ← YOUR ENTIRE SCOPE
  index.html               ← Main page
  css/style.css            ← All styles
  js/main.js               ← Client-side JavaScript
  (additional pages/assets as needed)
```

## Website Design Rules (MUST FOLLOW)
- **Dark gaming theme**: background `#0a0a0f`, text white/light gray
- **Neon green accent**: `#00ff41` for highlights, buttons, borders, glow effects
- **Vanilla only**: HTML, CSS, JavaScript. No frameworks, no npm, no build tools.
- **Separate files**: Keep HTML in index.html, styles in css/style.css, JS in js/main.js
- **No inline styles**: All styling goes in css/style.css
- **Existing CSS classes**: Check style.css before creating new ones — reuse existing classes
- **Responsive**: Use clamp(), flexbox, grid. Must work on mobile.

## What NOT to Do
- Do NOT install packages or dependencies
- Do NOT create new frameworks or build systems
- Do NOT touch anything outside the website/ directory
- Do NOT rewrite files from scratch — modify existing code
- Do NOT use inline styles — put everything in css/style.css
- Do NOT change the color scheme unless explicitly asked
- Do NOT create more than 5 new files per task

## Live URL
The website is live at https://simbot.cloud via Cloudflare Tunnel.
Changes to files in website/ are immediately visible.
