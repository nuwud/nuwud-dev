"""
scripts/lib/env.py — Environment variable validation helper.

Usage:
    from scripts.lib.env import require_env

    env = require_env(["PRINTIFY_API_TOKEN", "PRINTIFY_SHOP_ID"])
    token = env["PRINTIFY_API_TOKEN"]
"""

import os
import sys
from typing import List, Dict


def require_env(keys: List[str]) -> Dict[str, str]:
    """
    Validate that all required environment variables are set.

    Collects ALL missing keys before exiting so the user sees the full list
    in a single error message (Decision 7 — fail-fast with full list).

    Args:
        keys: List of environment variable names that must be present and non-empty.

    Returns:
        Dict mapping each key to its value (all guaranteed non-empty).

    Exits:
        sys.exit(1) if any keys are missing or empty.
    """
    missing = [k for k in keys if not os.environ.get(k)]
    if missing:
        print("ERROR: The following required environment variables are not set:")
        for key in missing:
            print(f"  - {key}")
        print()
        print("Copy .env.example to .env and fill in the missing values.")
        sys.exit(1)

    return {k: os.environ[k] for k in keys}
