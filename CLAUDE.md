# AFK Andy — Project Instructions for Claude Code

## What This Is
AFK Andy is a gaming website built autonomously by AI. Users send instructions via Discord, and AI modifies the website files directly.

## Project Structure
```
~/afk-andy/
  website/           ← THE WEBSITE (this is what you modify)
    index.html       ← Main page
    css/style.css    ← All styles
    js/main.js       ← Client-side JavaScript
  bot/               ← Discord bot (do NOT modify unless asked)
  memory/            ← Logs and state (do NOT modify)
```

## Website Design Rules (MUST FOLLOW)
- **Dark gaming theme**: background `#0a0a0f`, text white/light gray
- **Neon green accent**: `#00ff41` for highlights, buttons, borders, glow effects
- **Vanilla only**: HTML, CSS, JavaScript. No frameworks, no npm, no build tools.
- **Separate files**: Keep HTML in index.html, styles in css/style.css, JS in js/main.js
- **No inline styles**: All styling goes in css/style.css
- **Existing CSS classes**: Check style.css before creating new ones — reuse existing classes
- **Responsive**: Use clamp(), flexbox, grid. Must work on mobile.

## Working Directory
Always work from `~/afk-andy/`. The website files are in `~/afk-andy/website/`.

## What NOT to Do
- Do NOT install packages or dependencies
- Do NOT create new frameworks or build systems
- Do NOT change the bot code (bot/ directory) unless explicitly asked
- Do NOT rewrite files from scratch — modify existing code
- Do NOT use inline styles — put everything in css/style.css
- Do NOT change the color scheme unless explicitly asked

## Live URL
The website is live at https://simbot.cloud via Cloudflare Tunnel.
Changes to files in website/ are immediately visible.
