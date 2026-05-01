"""
scripts/create_printify_product.py — Create and publish a Printify POD product to Shopify.

Usage:
    python scripts/create_printify_product.py --product sticker-3in
    python scripts/create_printify_product.py --product sticker-sheet
    python scripts/create_printify_product.py --product tote
    python scripts/create_printify_product.py --product sticker-3in --dry-run
    python scripts/create_printify_product.py --product sticker-3in --logo-path "C:\\path\\to\\logo.png"

Exit codes:
    0  Success (product published) OR --dry-run (validated, no API calls)
    1  Missing required environment variables
    2  Logo file not found
    3  Printify API error
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the project root (one level up from scripts/)
_project_root = Path(__file__).parent.parent
load_dotenv(_project_root / ".env")

# Allow `from lib.xxx import` when running as a script from project root
if str(_project_root / "scripts") not in sys.path:
    sys.path.insert(0, str(_project_root / "scripts"))

from lib.env import require_env  # noqa: E402
from lib.printify import (  # noqa: E402
    PRODUCT_CONFIGS,
    upload_image,
    get_variants,
    create_product,
    publish,
)

SUPPORTED_PRODUCTS = list(PRODUCT_CONFIGS.keys())


def resolve_logo_path(logo_dir: str, logo_asset: str, logo_path_override: str | None) -> Path:
    """
    Resolve the logo file path.

    Priority:
      1. --logo-path CLI override (if provided)
      2. LOGO_DIR env var + product config logo_asset filename

    Returns:
        Resolved Path object (guaranteed to exist — caller checks).
    """
    if logo_path_override:
        return Path(logo_path_override)
    return Path(logo_dir) / logo_asset


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create and publish a Printify POD product to Shopify.",
    )
    parser.add_argument(
        "--product",
        required=True,
        choices=SUPPORTED_PRODUCTS,
        help=f"Product type to create. One of: {', '.join(SUPPORTED_PRODUCTS)}",
    )
    parser.add_argument(
        "--logo-path",
        default=None,
        help=(
            "Override logo file path. If omitted, uses LOGO_DIR env var "
            "combined with the product's canonical logo filename."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Validate config and logo path without making any API calls. "
            "Exits 0 if everything looks good."
        ),
    )
    args = parser.parse_args()

    # --- Step 1: Validate env vars (exit 1 if missing) ---
    env = require_env(["PRINTIFY_API_TOKEN", "PRINTIFY_SHOP_ID", "LOGO_DIR"])
    token = env["PRINTIFY_API_TOKEN"]
    shop_id = env["PRINTIFY_SHOP_ID"]
    logo_dir = env["LOGO_DIR"]

    # --- Step 2: Resolve product config ---
    config = PRODUCT_CONFIGS[args.product]

    # --- Step 3: Resolve logo path ---
    logo_path = resolve_logo_path(logo_dir, config["logo_asset"], args.logo_path)

    # --- Step 4: Validate logo file exists (exit 2 if not found) ---
    if not logo_path.exists():
        print(f"ERROR: Logo file not found: {logo_path}")
        print(f"  Expected logo: {config['logo_asset']}")
        print(f"  Searched in LOGO_DIR: {logo_dir}")
        print()
        print("Set LOGO_DIR in .env to the directory containing your logo files,")
        print("or use --logo-path to specify the file directly.")
        sys.exit(2)

    # --- Dry-run: print resolved config and exit 0 ---
    if args.dry_run:
        print("DRY RUN — no API calls will be made.")
        print()
        print(f"  Product slug  : {args.product}")
        print(f"  Title         : {config['title']}")
        print(f"  Blueprint ID  : {config['blueprint_id']}")
        print(f"  Provider ID   : {config['provider_id']}")
        print(f"  Placeholders  : {config['placeholders']}")
        print(f"  Logo path     : {logo_path}")
        print(f"  Shop ID       : {shop_id}")
        print()
        print("Config valid. Run without --dry-run to create the product.")
        sys.exit(0)

    # --- Step 5: Upload image ---
    print(f"Uploading logo: {logo_path.name} ...")
    image_id = upload_image(token, str(logo_path))
    print(f"  Image uploaded. ID: {image_id}")

    # --- Step 6: Fetch variants ---
    print(f"Fetching variants for blueprint {config['blueprint_id']} / provider {config['provider_id']} ...")
    variants = get_variants(token, config["blueprint_id"], config["provider_id"])
    if not variants:
        print("ERROR: No variants returned from Printify catalog API.")
        sys.exit(3)
    variant_ids = [v["id"] for v in variants]
    print(f"  {len(variant_ids)} variants fetched.")

    # --- Step 7: Create product ---
    print(f"Creating product: {config['title']} ...")
    product_id = create_product(token, shop_id, config, image_id, variant_ids)
    print(f"  Product created. ID: {product_id}")

    # --- Step 8: Publish to Shopify ---
    print("Publishing to Shopify ...")
    publish(token, shop_id, product_id)
    print("  Published successfully.")

    print()
    print(f"Done! Product '{config['title']}' is live in your Shopify store.")
    print(f"  Printify product ID: {product_id}")
    sys.exit(0)


if __name__ == "__main__":
    main()
