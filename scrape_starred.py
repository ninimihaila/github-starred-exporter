# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "playwright",
# ]
# ///

"""
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
"""

import argparse
import re
from datetime import date
from pathlib import Path

from playwright.sync_api import sync_playwright

# Session storage location (next to script)
SCRIPT_DIR = Path(__file__).parent
SESSION_FILE = SCRIPT_DIR / "session.json"


def get_logged_in_username(page) -> str | None:
    """Check if user is logged in and return username, or None if not logged in."""
    try:
        # Check for user menu (only visible when logged in)
        user_menu = page.locator('button[aria-label="Open user navigation menu"]')
        if user_menu.count() == 0:
            return None

        user_menu.click()
        username = page.locator('div[aria-label="User navigation"] .text-bold').text_content()
        page.keyboard.press("Escape")

        return username if username else None
    except Exception:
        return None


def wait_for_login(page) -> str:
    """Wait for the user to log in and return their username."""
    print("Please log in to GitHub in the browser window...")
    print("Waiting for login to complete...")

    # Wait until we're redirected away from login page and can find the user menu
    page.wait_for_selector('button[aria-label="Open user navigation menu"]', timeout=300000)

    # Extract username from the page
    # The username is typically in the user menu or profile link
    user_menu = page.locator('button[aria-label="Open user navigation menu"]')
    user_menu.click()

    # Look for the profile link which contains the username
    username = page.locator('div[aria-label="User navigation"] .text-bold').text_content()

    # Close the menu by pressing Escape
    page.keyboard.press("Escape")

    if username:
        print(f"Logged in as: {username}")
        return username

    raise RuntimeError("Could not determine username after login")


def scrape_starred_repos(page, username: str) -> list[str]:
    """Scrape all starred repositories for the given user."""
    starred_url = f"https://github.com/{username}?tab=stars"
    page.goto(starred_url)

    print("Navigating to starred repositories...")
    # page.wait_for_load_state("networkidle")

    all_repos = []
    page_num = 1

    while True:
        print(f"Scraping page {page_num}...")

        # Find all repository links on the current page
        # Starred repos have links in the format /owner/repo
        repo_links = page.locator('h3 a[href*="/"]').all()

        repos_on_page = []
        for link in repo_links:
            href = link.get_attribute("href")
            if href and re.match(r"^/[^/]+/[^/]+$", href):
                full_url = f"https://github.com{href}"
                if full_url not in all_repos:
                    repos_on_page.append(full_url)

        all_repos.extend(repos_on_page)
        print(f"  Found {len(repos_on_page)} repositories on this page")

        # Check for next page button
        next_button = page.locator('div[data-test-selector="pagination"]').get_by_text("Next")
        if next_button.count() > 0 and next_button.is_enabled():
            next_button.click()
            # page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)  # Small delay to ensure page loads
            page_num += 1
        else:
            break

    return all_repos


def main():
    parser = argparse.ArgumentParser(
        description="Scrape starred repositories from your GitHub account"
    )
    parser.add_argument(
        "--save-session",
        action="store_true",
        help="Save browser session after login for future use",
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Ignore saved session and start fresh (forces new login)",
    )
    args = parser.parse_args()

    print("GitHub Starred Repositories Scraper")
    print("=" * 40)

    # Determine if we should try to use saved session
    use_saved_session = SESSION_FILE.exists() and not args.fresh

    with sync_playwright() as p:
        # Launch browser in non-headless mode for manual login
        browser = p.chromium.launch(headless=False)

        # Create context with saved session if available
        if use_saved_session:
            print(f"Loading saved session from {SESSION_FILE}")
            context = browser.new_context(storage_state=str(SESSION_FILE))
        else:
            context = browser.new_context()

        page = context.new_page()

        # Navigate to GitHub
        page.goto("https://github.com")
        # page.wait_for_load_state("networkidle")

        # Check if already logged in (from saved session)
        username = get_logged_in_username(page)

        if username:
            print(f"Already logged in as: {username}")
        else:
            if use_saved_session:
                print("Saved session expired, need to log in again...")
            # Navigate to login page
            page.goto("https://github.com/login")
            username = wait_for_login(page)

        # Save session if requested
        if args.save_session:
            context.storage_state(path=str(SESSION_FILE))
            print(f"Session saved to {SESSION_FILE}")

        # Scrape starred repositories
        repos = scrape_starred_repos(page, username)

        browser.close()

    # Generate output filename with current date
    today = date.today().isoformat()
    output_file = Path(__file__).parent / f"{today}-starred.txt"

    # Write repos to file
    with open(output_file, "w") as f:
        for repo in repos:
            f.write(f"{repo}\n")

    print("=" * 40)
    print(f"Successfully scraped {len(repos)} starred repositories")
    print(f"Output saved to: {output_file}")


if __name__ == "__main__":
    main()
