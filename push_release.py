#!/usr/bin/env python3
"""Push release script."""
import subprocess
import sys


def main():
    """Push release to GitHub."""
    if len(sys.argv) != 2:
        print("Usage: python push_release.py <version>")
        sys.exit(1)

    version = sys.argv[1]

    # Push tag
    subprocess.run(['git', 'push', 'origin', f'v{version}'], check=True)

    print(f"Pushed release {version}")


if __name__ == "__main__":
    main()