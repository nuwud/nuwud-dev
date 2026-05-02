"""
scripts/create_hat_product.py — Create embroidered hat products in Printful + Shopify.

Architecture:
  Printful's API blocks POST /store/products for Shopify-connected stores.
  Instead, we use a separate Printful "Manual Order / API" store for scripted
  product creation, then create a matching Shopify product. A JSON mapping file
  records how to route Shopify orders to Printful for fulfillment.

  One-time setup:
    1. In Printful dashboard → Stores → Add store → Manual Order / API
    2. Copy the store ID from the store settings URL
    3. Add PRINTFUL_MANUAL_STORE_ID=<id> to .env

Workflow:
  1. Fetch Printful catalog variant colors.
  2. Create Printful sync product (with embroidery config) in Manual/API store.
  3. Create matching Shopify product (draft) with same color variants + SKUs.
  4. Save variant mapping to products/<slug>-mapping.json for order routing.

Usage:
    python scripts/create_hat_product.py --product yupoong-classic-trucker
    python scripts/create_hat_product.py --product yupoong-retro-trucker --dry-run
    python scripts/create_hat_product.py --product camo-trucker
    python scripts/create_hat_product.py --product multicam-cap

Exit codes:
    0  Success (or --dry-run validated)
    1  Missing required env vars
    3  Printful API error
    4  Shopify API error
"""

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

_project_root = Path(__file__).parent.parent
load_dotenv(_project_root / ".env", override=True)

if str(_project_root / "scripts") not in sys.path:
    sys.path.insert(0, str(_project_root / "scripts"))

from lib.env import require_env  # noqa: E402
from lib.printful import (  # noqa: E402
    PRODUCT_CONFIGS,
    create_sync_product,
    get_catalog_variant_color,
)
from lib.shopify_admin import create_product  # noqa: E402

SUPPORTED_PRODUCTS = list(PRODUCT_CONFIGS.keys())
MAPPING_DIR = _project_root / "products"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create an embroidered hat in Printful (Manual/API store) + Shopify.",
    )
    parser.add_argument(
        "--product",
        required=True,
        choices=SUPPORTED_PRODUCTS,
        help=f"Product slug. One of: {', '.join(SUPPORTED_PRODUCTS)}",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config and fetch variant colors; nothing is created.",
    )
    args = parser.parse_args()

    env = require_env(
        [
            "PRINTFUL_API_TOKEN",
            "PRINTFUL_MANUAL_STORE_ID",
            "SHOPIFY_ADMIN_TOKEN",
            "SHOPIFY_STORE_DOMAIN",
        ]
    )
    pf_token = env["PRINTFUL_API_TOKEN"]
    pf_manual_store_id = env["PRINTFUL_MANUAL_STORE_ID"]
    sh_token = env["SHOPIFY_ADMIN_TOKEN"]
    sh_domain = env["SHOPIFY_STORE_DOMAIN"]

    config = PRODUCT_CONFIGS[args.product]

    # ── Step 1: Fetch color names from Printful catalog ──────────────────────
    print(f"\nFetching variant colors from Printful catalog ...")
    variant_colors: list[tuple[int, str]] = []  # [(printful_variant_id, color_name), ...]
    for vid in config["variant_ids"]:
        color = get_catalog_variant_color(pf_token, vid)
        variant_colors.append((vid, color))
        print(f"  {vid} → {color}")

    # ── Dry-run: stop here ────────────────────────────────────────────────────
    if args.dry_run:
        print("\nDRY RUN — nothing created.\n")
        print(f"  Product slug      : {args.product}")
        print(f"  Title             : {config['title']}")
        print(f"  Printful product  : {config['product_id']}")
        print(f"  Variants          : {len(variant_colors)}")
        for vid, color in variant_colors:
            print(f"    pf_{vid:>7}  →  {color}")
        print(f"  Retail price      : ${config['retail_price']}")
        print(f"  Embroidery file   : {config['file_id']}")
        print(f"  Manual store ID   : {pf_manual_store_id}")
        print(f"  Shopify domain    : {sh_domain}")
        print()
        print("Config valid. Run without --dry-run to create the product.")
        sys.exit(0)

    # ── Step 2: Create Printful sync product in Manual/API store ─────────────
    print(f"\nCreating Printful sync product in Manual/API store {pf_manual_store_id} ...")
    sync_result = create_sync_product(pf_token, config, pf_manual_store_id)
    sync_product = sync_result["sync_product"]
    sync_variants = sync_result["sync_variants"]

    pf_sync_id = sync_product["id"]
    print(f"  Printful sync product created: ID {pf_sync_id}")
    print(f"  {len(sync_variants)} sync variants configured with embroidery")

    # Build SKU → printful_sync_variant_id lookup (SKU = "pf_<catalog_variant_id>")
    sku_to_pf_sync: dict[str, int] = {}
    for sv in sync_variants:
        sku = sv.get("sku") or ""
        if sku:
            sku_to_pf_sync[sku] = sv["id"]

    # ── Step 3: Create Shopify product ───────────────────────────────────────
    print(f"\nCreating Shopify product: {config['title']} ...")
    shopify_variants = [
        {
            "option1": color,
            "price": config["retail_price"],
            "sku": f"pf_{vid}",
        }
        for vid, color in variant_colors
    ]

    shopify_product = create_product(
        token=sh_token,
        store_domain=sh_domain,
        title=config["title"],
        body_html=f"<p>{config['description']}</p>",
        variants=shopify_variants,
    )
    shopify_product_id = shopify_product["id"]
    shopify_variants_created = shopify_product["variants"]

    print(f"  Shopify product created: ID {shopify_product_id}")
    print(f"  {len(shopify_variants_created)} variants (status: draft)")

    # ── Step 4: Save variant mapping for order routing ───────────────────────
    MAPPING_DIR.mkdir(exist_ok=True)
    mapping_path = MAPPING_DIR / f"{args.product}-mapping.json"

    mapping = {
        "product_slug": args.product,
        "printful_manual_store_id": pf_manual_store_id,
        "printful_sync_product_id": pf_sync_id,
        "shopify_product_id": shopify_product_id,
        "variants": [],
    }
    for sh_variant in shopify_variants_created:
        sku = sh_variant.get("sku", "")
        pf_sv_id = sku_to_pf_sync.get(sku)
        mapping["variants"].append(
            {
                "shopify_variant_id": sh_variant["id"],
                "sku": sku,
                "color": sh_variant.get("option1", ""),
                "printful_sync_variant_id": pf_sv_id,
            }
        )
    mapping_path.write_text(json.dumps(mapping, indent=2))
    print(f"\n  Variant mapping saved → {mapping_path.relative_to(_project_root)}")

    # ── Done ─────────────────────────────────────────────────────────────────
    configured = sum(1 for v in mapping["variants"] if v["printful_sync_variant_id"])
    print(f"\n✓ Done!")
    print(f"  Printful sync product ID : {pf_sync_id} (store {pf_manual_store_id})")
    print(f"  Shopify product ID       : {shopify_product_id}")
    print(f"  Variants mapped          : {configured}/{len(mapping['variants'])}")
    print()
    print("Next steps:")
    print(f"  1. Publish the Shopify product when ready:")
    print(f"     https://{sh_domain}/admin/products/{shopify_product_id}")
    print(f"  2. When a Shopify order arrives, route it to Printful using:")
    print(f"     mapping file: {mapping_path.relative_to(_project_root)}")
    print(f"     POST https://api.printful.com/orders with sync_variant_id from mapping")
    print(f"  3. (Optional) Set up a Shopify webhook handler to automate order routing.")


if __name__ == "__main__":
    main()
