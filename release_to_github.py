#!/usr/bin/env python3
"""Release automation script."""
import subprocess
import sys


def main():
    """Create a release tag and push to GitHub."""
    if len(sys.argv) != 2:
        print("Usage: python release_to_github.py <version>")
        sys.exit(1)

    version = sys.argv[1]

    # Create tag
    subprocess.run(['git', 'tag', '-a', f'v{version}', '-m', f'Release v{version}'], check=True)

    # Push branch and tag
    subprocess.run(['git', 'push', 'origin', 'master'], check=True)
    subprocess.run(['git', 'push', 'origin', f'v{version}'], check=True)

    print(f"Released version {version}")


if __name__ == "__main__":
    main()