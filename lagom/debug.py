"""Module for helping with debugging and issue logging"""
from lagom import version


def get_commit_hash():
    with open("githash.txt") as f:
        return f.read()


if __name__ == "__main__":
    print(f"Lagom version {version.__version__} commit {get_commit_hash()}")
