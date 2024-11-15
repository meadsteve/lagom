"""Module for helping with debugging and issue logging"""

import os
from pathlib import Path

from lagom import version


def get_commit_hash():
    return "DISABLED_FOR_NOW"


def get_build_info():
    return {"version": version.__version__, "commit_hash": get_commit_hash()}


if __name__ == "__main__":
    print(f"Lagom version {version.__version__} commit {get_commit_hash()}")
