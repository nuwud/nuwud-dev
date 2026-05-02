"""
scripts/list_printful_stores.py — List all Printful stores for this API token.

Run this after creating a Manual Order / API store in the Printful dashboard
to find its store ID, then add it to .env as PRINTFUL_MANUAL_STORE_ID.

Usage:
    python scripts/list_printful_stores.py
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

_project_root = Path(__file__).parent.parent
load_dotenv(_project_root / ".env", override=True)

if str(_project_root / "scripts") not in sys.path:
    sys.path.insert(0, str(_project_root / "scripts"))

import requests
from lib.env import require_env

env = require_env(["PRINTFUL_API_TOKEN"])
token = env["PRINTFUL_API_TOKEN"]

resp = requests.get(
    "https://api.printful.com/stores",
    headers={"Authorization": f"Bearer {token}"},
    timeout=15,
)
if not resp.ok:
    print(f"ERROR {resp.status_code}: {resp.text[:300]}")
    sys.exit(1)

stores = resp.json().get("result", [])
if not stores:
    print("No stores found.")
    sys.exit(0)

print(f"\nPrintful stores for this token ({len(stores)} total):\n")
for s in stores:
    sid = s.get("id")
    name = s.get("name")
    stype = s.get("type")
    country = s.get("country_name", "")
    print(f"  ID: {sid:>10}  type: {stype:<25} name: {name}  ({country})")

print()
print("Add the Manual Order / API store ID to .env as:")
print("  PRINTFUL_MANUAL_STORE_ID=<id>")
