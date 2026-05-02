"""
scripts/list_blueprints.py — List available Printify blueprints.

Usage:
    python scripts/list_blueprints.py
    python scripts/list_blueprints.py --provider 73

Exit codes:
    0  Success
    1  Missing required environment variables
    3  Printify API error
"""

import argparse
import sys

from dotenv import load_dotenv

# Load .env from the project root (one level up from scripts/)
from pathlib import Path
_project_root = Path(__file__).parent.parent
load_dotenv(_project_root / ".env", override=True)

# Allow `from lib.xxx import` when running as a script from project root
if str(_project_root / "scripts") not in sys.path:
    sys.path.insert(0, str(_project_root / "scripts"))

from lib.env import require_env  # noqa: E402

import requests  # noqa: E402

PRINTIFY_BASE_URL = "https://api.printify.com/v1"


def fetch_blueprints(token: str) -> list:
    response = requests.get(
        f"{PRINTIFY_BASE_URL}/catalog/blueprints.json",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        timeout=30,
    )
    if not response.ok:
        print(f"ERROR: Printify API error fetching blueprints.")
        print(f"  Status: {response.status_code}")
        try:
            print(f"  Response: {response.json()}")
        except Exception:
            print(f"  Response: {response.text}")
        sys.exit(3)
    data = response.json()
    if isinstance(data, list):
        return data
    return data.get("data", data)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="List available Printify blueprints with their IDs.",
    )
    parser.add_argument(
        "--provider",
        type=int,
        default=73,
        help="Filter results by print provider ID (default: 73 = Printed Simply)",
    )
    args = parser.parse_args()

    env = require_env(["PRINTIFY_API_TOKEN"])
    token = env["PRINTIFY_API_TOKEN"]

    blueprints = fetch_blueprints(token)

    # Filter by provider if --provider is given and blueprint data supports it
    # (The blueprints catalog endpoint returns all blueprints; provider filter
    # is informational — used when fetching variants for a specific blueprint)
    print(f"\n{'ID':<8} {'Title'}")
    print("-" * 60)
    for bp in blueprints:
        bp_id = bp.get("id", "?")
        title = bp.get("title", "(no title)")
        print(f"{bp_id:<8} {title}")

    print(f"\nTotal: {len(blueprints)} blueprints")
    if args.provider != 73:
        print(
            f"Note: Use --provider {args.provider} when fetching variants for a specific blueprint."
        )


if __name__ == "__main__":
    main()
