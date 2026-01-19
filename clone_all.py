#!/usr/bin/env python3
import sys
import os
import subprocess


def clone_repositories(input_file):
    """Clone repositories from a file containing URLs."""
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        return

    with open(input_file, "r") as f:
        lines = f.readlines()

    total = 0
    successful = 0
    failed = 0

    for line_num, line in enumerate(lines, 1):
        url = line.strip()

        # Skip empty lines and comments
        if not url or url.startswith("#"):
            continue

        total += 1
        print(f"Cloning repository {total} ({url})...")

        try:
            result = subprocess.run(
                ["git", "clone", url], capture_output=True, text=True, timeout=300
            )
            if result.returncode == 0:
                print(f"✓ Successfully cloned: {url}")
                successful += 1
            else:
                print(f"✗ Failed to clone {url}: {result.stderr.strip()}")
                failed += 1
        except subprocess.TimeoutExpired:
            print(f"✗ Timeout while cloning {url}")
            failed += 1
        except Exception as e:
            print(f"✗ Error cloning {url}: {str(e)}")
            failed += 1

    print(f"\nCloning complete!")
    print(f"Total: {total}, Successful: {successful}, Failed: {failed}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    clone_repositories(input_file)
