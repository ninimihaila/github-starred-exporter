GitHub Starred Repositories Scraper

Scrapes all starred repositories from a GitHub user's account.
Opens a browser for manual login, then scrapes the starred repos.

Usage:
    uv run scrape_starred.py [options]

Options:
    --save-session    Save browser session after login for future use
    --fresh           Ignore saved session and start fresh (forces new login)

After running, you'll need to install Playwright browsers once:
    uv run playwright install chromium
