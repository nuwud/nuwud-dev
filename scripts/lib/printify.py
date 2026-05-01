"""
scripts/lib/printify.py — Printify API helper functions and product config.

Provides:
  - PRODUCT_CONFIGS: dict keyed by slug (sticker-3in, sticker-sheet, tote)
  - upload_image(token, file_path) -> image_id
  - get_variants(token, blueprint_id, provider_id) -> list
  - create_product(token, shop_id, config, image_id, variant_ids) -> product_id
  - publish(token, shop_id, product_id)
"""

import base64
import sys
from pathlib import Path
from typing import Dict, List, Any

import requests

PRINTIFY_BASE_URL = "https://api.printify.com/v1"

# ---------------------------------------------------------------------------
# Product configuration registry
# ---------------------------------------------------------------------------

PRODUCT_CONFIGS: Dict[str, Dict[str, Any]] = {
    "sticker-3in": {
        "blueprint_id": 358,
        "provider_id": 73,
        "placeholders": ["front"],
        "logo_asset": "Nuwud-Gorilla-Logo-Fixed.png",
        "title": 'Nuwud Gorilla Die-Cut Sticker 3"',
        "description": 'Premium 3" die-cut Nuwud Gorilla sticker.',
    },
    "sticker-sheet": {
        "blueprint_id": 661,
        "provider_id": 73,
        "placeholders": ["front_1", "front_2", "front_3", "front_4"],
        "logo_asset": "Nuwud-Gorilla-Logo-Fixed.png",
        "title": "Nuwud Gorilla Sticker Sheet",
        "description": "Sheet of Nuwud Gorilla logo stickers.",
    },
    "tote": {
        "blueprint_id": 51,
        "provider_id": 73,
        "placeholders": ["front"],
        "logo_asset": "Nuwud-Gorilla-Logo-Fixed.png",
        "title": "Nuwud Gorilla Tote Bag",
        "description": "Canvas tote bag with Nuwud Gorilla logo.",
    },
}


def _auth_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def _raise_for_api_error(response: requests.Response, context: str) -> None:
    """Check response and exit with code 3 on Printify API errors."""
    if not response.ok:
        print(f"ERROR: Printify API error during {context}.")
        print(f"  Status: {response.status_code}")
        try:
            body = response.json()
            print(f"  Response: {body}")
        except Exception:
            print(f"  Response: {response.text}")
        sys.exit(3)


# ---------------------------------------------------------------------------
# API functions
# ---------------------------------------------------------------------------


def upload_image(token: str, file_path: str) -> str:
    """
    Upload an image to Printify via base64 encoding.

    Args:
        token: Printify API bearer token.
        file_path: Absolute path to the image file.

    Returns:
        The Printify image ID string.

    Exits:
        sys.exit(3) on API error.
    """
    path = Path(file_path)
    with open(path, "rb") as f:
        contents = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "file_name": path.name,
        "contents": contents,
    }

    response = requests.post(
        f"{PRINTIFY_BASE_URL}/uploads/images.json",
        headers=_auth_headers(token),
        json=payload,
        timeout=60,
    )
    _raise_for_api_error(response, "image upload")
    image_id = response.json()["id"]
    return image_id


def get_variants(token: str, blueprint_id: int, provider_id: int) -> List[Dict]:
    """
    Fetch all available variants for a blueprint + provider combination.

    Always fetches live — no caching (Decision 2).

    Args:
        token: Printify API bearer token.
        blueprint_id: Blueprint ID (e.g. 358 for die-cut sticker 3").
        provider_id: Print provider ID (e.g. 73 for Printed Simply).

    Returns:
        List of variant dicts from the Printify catalog API.

    Exits:
        sys.exit(3) on API error.
    """
    url = (
        f"{PRINTIFY_BASE_URL}/catalog/blueprints/{blueprint_id}"
        f"/print_providers/{provider_id}/variants.json"
    )
    response = requests.get(
        url,
        headers=_auth_headers(token),
        timeout=30,
    )
    _raise_for_api_error(response, "variant fetch")
    data = response.json()
    # The API returns {"variants": [...]} or a list directly
    if isinstance(data, list):
        return data
    return data.get("variants", data)


def create_product(
    token: str,
    shop_id: str,
    config: Dict[str, Any],
    image_id: str,
    variant_ids: List[int],
) -> str:
    """
    Create a Printify product using the given config and uploaded image.

    Args:
        token: Printify API bearer token.
        shop_id: Printify shop ID string.
        config: Product config dict (from PRODUCT_CONFIGS).
        image_id: Printify image ID returned by upload_image().
        variant_ids: List of variant IDs to include on the product.

    Returns:
        The Printify product ID string.

    Exits:
        sys.exit(3) on API error.
    """
    print_areas = []
    for placeholder in config["placeholders"]:
        print_areas.append(
            {
                "variant_ids": variant_ids,
                "placeholders": [
                    {
                        "position": placeholder,
                        "images": [
                            {
                                "id": image_id,
                                "x": 0.5,
                                "y": 0.5,
                                "scale": 1,
                                "angle": 0,
                            }
                        ],
                    }
                ],
            }
        )

    payload = {
        "title": config["title"],
        "description": config["description"],
        "blueprint_id": config["blueprint_id"],
        "print_provider_id": config["provider_id"],
        "variants": [{"id": vid, "price": 0, "is_enabled": True} for vid in variant_ids],
        "print_areas": print_areas,
    }

    response = requests.post(
        f"{PRINTIFY_BASE_URL}/shops/{shop_id}/products.json",
        headers=_auth_headers(token),
        json=payload,
        timeout=60,
    )
    _raise_for_api_error(response, "product creation")
    product_id = response.json()["id"]
    return product_id


def publish(token: str, shop_id: str, product_id: str) -> None:
    """
    Publish a Printify product to the connected Shopify store.

    Args:
        token: Printify API bearer token.
        shop_id: Printify shop ID string.
        product_id: Printify product ID to publish.

    Exits:
        sys.exit(3) on API error.
    """
    payload = {
        "title": True,
        "description": True,
        "images": True,
        "variants": True,
        "tags": True,
        "keyFeatures": True,
        "shipping_template": True,
    }

    response = requests.post(
        f"{PRINTIFY_BASE_URL}/shops/{shop_id}/products/{product_id}/publish.json",
        headers=_auth_headers(token),
        json=payload,
        timeout=60,
    )
    _raise_for_api_error(response, "product publish")
