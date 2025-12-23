#!/usr/bin/env python3
"""Local test runner."""
import subprocess
import sys


def main():
    """Run tests locally."""
    # Run unit tests
    print("Running unit tests...")
    result = subprocess.run([sys.executable, '-m', 'pytest', 'tests/unit', '-v'])
    if result.returncode != 0:
        sys.exit(result.returncode)

    # Run component tests
    print("Running component tests...")
    result = subprocess.run([sys.executable, '-m', 'pytest', 'tests/component', '-v'])
    if result.returncode != 0:
        sys.exit(result.returncode)

    print("All tests passed!")


if __name__ == "__main__":
    main()