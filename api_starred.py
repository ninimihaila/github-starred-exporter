# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests",
# ]
# ///

from datetime import date
from pathlib import Path
import requests
import argparse

def get_starred_repos(username):
    print(f"Getting starred repos for {username}...")

    api_url = f"https://api.github.com/users/{username}/starred"
    params = {'per_page': 100, 'page': 1}
    starred_repos = []

    while True:
        try:
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()

            if not data:
                break

            for repo in data:
                starred_repos.append(repo["clone_url"])

            print(f"  ...downloaded page {params['page']} with {len(data)} repos")
            params['page'] += 1

        except Exception as e:
            print(f"An error occurred: {e}")
            break

    print(f"Got {len(starred_repos)} starred repos.\n")
    return starred_repos


def write_file(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(f"{item}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get starred repositories for a GitHub user and save them to a file.")

    parser.add_argument(
        "--user",
        type=str,
        required=True,
        help="GitHub username."
    )

    args = parser.parse_args()

    username = args.user

    starred_repos = get_starred_repos(username)

    if starred_repos:
        today = date.today().isoformat()
        output_file = Path(__file__).parent / f"{today}-starred.txt"
        write_file(starred_repos, output_file)

    print("All done!")
