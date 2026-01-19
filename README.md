# GitHub Starred Repositories Scraper

Scrapes all starred repositories from a GitHub user's account.


## API Version

This version is much faster, and doesn't use a browser to scrape the repositories.

    Usage:
        uv run api_starred.py --user username

The output will be a file named `yyyy-mm-dd-starred.txt` containing all the starred repositories (one per line)


## Cloning

To clone all the repositories locally, run

    uv run clone_all.py starred-repos-file.txt


## Scraper version

Opens a browser for manual login, then scrapes the starred repos.
Use this if the API version fails.

    Usage:
        uv run scrape_starred.py [options]

    Options:
        --save-session    Save browser session after login for future use
        --fresh           Ignore saved session and start fresh (forces new login)

After running, you'll need to install Playwright browsers once:

    uv run playwright install chromium

