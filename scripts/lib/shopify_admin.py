"""
scripts/lib/shopify_admin.py — Shopify Admin API helpers for product creation.

Uses Custom App access token authentication (X-Shopify-Access-Token header).
"""

import sys
from typing import Any, Dict, List, Optional

import requests

SHOPIFY_API_VERSION = "2024-10"


def _headers(token: str) -> Dict[str, str]:
    return {
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json",
    }


def _base_url(store_domain: str) -> str:
    return f"https://{store_domain}/admin/api/{SHOPIFY_API_VERSION}"


def create_product(
    token: str,
    store_domain: str,
    title: str,
    body_html: str,
    variants: List[Dict[str, Any]],
    product_type: str = "Hat",
    vendor: str = "Nuwud Multimedia",
    tags: str = "embroidery, hat, printful",
    status: str = "draft",
) -> Dict[str, Any]:
    """
    Create a product in Shopify and return the full product dict.

    Each entry in `variants` should be:
        {"option1": "<color name>", "price": "36.99", "sku": "pf_<variant_id>"}

    Returns the created Shopify product dict (including id and variants[].id).
    """
    payload = {
        "product": {
            "title": title,
            "body_html": body_html,
            "product_type": product_type,
            "vendor": vendor,
            "tags": tags,
            "status": status,
            "options": [{"name": "Color"}],
            "variants": [
                {
                    "option1": v["option1"],
                    "price": v["price"],
                    "sku": v.get("sku", ""),
                    "fulfillment_service": "manual",
                    "inventory_management": None,
                    "requires_shipping": True,
                }
                for v in variants
            ],
        }
    }

    response = requests.post(
        f"{_base_url(store_domain)}/products.json",
        headers=_headers(token),
        json=payload,
        timeout=30,
    )

    if not response.ok:
        print(f"ERROR creating Shopify product: HTTP {response.status_code}")
        print(f"  {response.text[:600]}")
        sys.exit(4)

    return response.json()["product"]


def get_product(
    token: str,
    store_domain: str,
    product_id: int,
) -> Optional[Dict[str, Any]]:
    """Fetch a Shopify product by ID. Returns None if not found."""
    response = requests.get(
        f"{_base_url(store_domain)}/products/{product_id}.json",
        headers=_headers(token),
        timeout=30,
    )
    if response.status_code == 404:
        return None
    if not response.ok:
        print(f"ERROR fetching Shopify product {product_id}: HTTP {response.status_code}")
        sys.exit(4)
    return response.json()["product"]
