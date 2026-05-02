"""
scripts/create_printful_product.py — Create and publish a Printful POD product to Shopify.

Usage:
    python scripts/create_printful_product.py --product yupoong-classic-trucker
    python scripts/create_printful_product.py --product camo-trucker
    python scripts/create_printful_product.py --product multicam-cap
    python scripts/create_printful_product.py --product yupoong-retro-trucker --dry-run

Supported products:
    yupoong-classic-trucker  Yupoong 6006 Classic Trucker, 13 colors
    yupoong-retro-trucker    Yupoong 6606 Retro Trucker, 20 colors (full collection)
    camo-trucker             Otto Cap 105-1247 Camo Mesh Trucker, 3 military camo colors
    multicam-cap             Flexfit 6277 Multicam (OCP) cap, S/M + L/XL

Exit codes:
    0  Success OR --dry-run (validated, no API calls)
    1  Missing required environment variables
    3  Printful API error
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

_project_root = Path(__file__).parent.parent
load_dotenv(_project_root / ".env", override=True)

if str(_project_root / "scripts") not in sys.path:
    sys.path.insert(0, str(_project_root / "scripts"))

from lib.env import require_env  # noqa: E402
from lib.printful import PRODUCT_CONFIGS, create_sync_product  # noqa: E402

SUPPORTED_PRODUCTS = list(PRODUCT_CONFIGS.keys())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a Printful POD product linked to Shopify.",
    )
    parser.add_argument(
        "--product",
        required=True,
        choices=SUPPORTED_PRODUCTS,
        help=f"Product to create. One of: {', '.join(SUPPORTED_PRODUCTS)}",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config without making any API calls. Exits 0 if valid.",
    )
    args = parser.parse_args()

    env = require_env(["PRINTFUL_API_TOKEN"])
    token = env["PRINTFUL_API_TOKEN"]
    config = PRODUCT_CONFIGS[args.product]

    if args.dry_run:
        print("DRY RUN — no API calls will be made.")
        print()
        print(f"  Product slug  : {args.product}")
        print(f"  Title         : {config['title']}")
        print(f"  Product ID    : {config['product_id']}")
        print(f"  Variants      : {len(config['variant_ids'])} variants")
        print(f"  Retail price  : ${config['retail_price']}")
        print(f"  Embroidery file ID: {config['file_id']}")
        print()
        print("Config valid. Run without --dry-run to create the product.")
        sys.exit(0)

    print(f"Creating Printful product: {config['title']} ...")
    print(f"  {len(config['variant_ids'])} variants at ${config['retail_price']} each")
    product_id = create_sync_product(token, config)
    print(f"  Product created. Printful sync product ID: {product_id}")
    print()
    print(f"Done! '{config['title']}' is synced to your Shopify store.")
    sys.exit(0)


if __name__ == "__main__":
    main()
