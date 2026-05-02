"""
scripts/lib/printful.py — Printful API helpers and product configs.

Products are created as Printful "sync products" linked to the Shopify store.
Embroidery file type: embroidery_front_large (600 DPI PNG recommended).
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import requests

PRINTFUL_BASE_URL = "https://api.printful.com"

# Reusable gorilla icon file already uploaded to Printful (600 DPI white PNG)
UPLOADED_LOGO_FILE_ID = 121281912

# ---------------------------------------------------------------------------
# Product configs
# ---------------------------------------------------------------------------
# Each config maps a slug → product definition. Keys:
#   product_id   : Printful catalog product ID
#   variant_ids  : list of Printful variant IDs to include
#   file_id      : Printful file ID to use for embroidery (reuse existing upload)
#   title        : product name
#   description  : product description
#   retail_price : string price per unit (USD)
#   file_type    : embroidery file placement type (default: embroidery_front_large)
# ---------------------------------------------------------------------------

PRODUCT_CONFIGS: Dict[str, Dict[str, Any]] = {
    # ── Yupoong 6006 Classic Trucker (all 13 colors) ──
    "yupoong-classic-trucker": {
        "product_id": 100,
        "variant_ids": [4811, 4812, 4813, 4814, 15550, 4815, 4816, 4817, 4818, 4819, 4820, 15551, 4810],
        "file_id": UPLOADED_LOGO_FILE_ID,
        "title": "Nuwud Gorilla Classic Trucker Hat (Yupoong 6006)",
        "description": (
            "Yupoong YP Classics 6006 mesh-back trucker cap with raised embroidered "
            "Nuwud Gorilla logo. Structured front panel, adjustable snapback closure. "
            "Available in 13 colorways."
        ),
        "retail_price": "36.99",
    },
    # ── Yupoong 6606 Retro Trucker — expanded colors (all 20) ──
    "yupoong-retro-trucker": {
        "product_id": 252,
        "variant_ids": [
            8747, 8748, 8749, 20394, 20390, 16709, 20395, 20391,
            20393, 22454, 16710, 8752, 8750, 8751, 8755, 8753,
            8754, 8756, 20392, 8746,
        ],
        "file_id": UPLOADED_LOGO_FILE_ID,
        "title": "Nuwud Gorilla Retro Trucker Hat — Full Collection (Yupoong 6606)",
        "description": (
            "Yupoong YP Classics 6606 retro trucker cap with raised embroidered "
            "Nuwud Gorilla logo. Low-profile structured front, mesh back, adjustable "
            "snapback. Available in 20 colorways including Black, Navy, Charcoal, "
            "Silver, Pink, and more."
        ),
        "retail_price": "38.00",
    },
    # ── Otto Cap 105-1247 Camo Mesh Trucker (military camo + mesh back) ──
    "camo-trucker": {
        "product_id": 680,
        "variant_ids": [16856, 16857, 16858],
        "file_id": UPLOADED_LOGO_FILE_ID,
        "title": "Nuwud Gorilla Camo Mesh Trucker Hat (Embroidered)",
        "description": (
            "Otto Cap 105-1247 camouflage 6-panel low-profile trucker cap with mesh back "
            "and raised embroidered Nuwud Gorilla logo. Military camo fabric front, "
            "breathable mesh back. Available in Camo/Black, Camo/Brown, and Camo/Olive."
        ),
        "retail_price": "39.99",
    },
    # ── Flexfit 6277 Multicam (premium military OCP pattern — Multicam Black + Green) ──
    "multicam-cap": {
        "product_id": 140,
        "variant_ids": [15897, 15898, 15899, 15900],  # S/M + L/XL for each Multicam color
        "file_id": UPLOADED_LOGO_FILE_ID,
        "title": "Nuwud Gorilla Multicam Cap (Flexfit 6277)",
        "description": (
            "Flexfit 6277 Wooly Combed structured cap in premium Multicam patterns "
            "with raised embroidered Nuwud Gorilla logo. Multicam Black and Multicam "
            "Green — the same OCP-derived camo used by US special operations. "
            "Available in S/M and L/XL."
        ),
        "retail_price": "41.99",
    },
}


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

# Shopify-connected store (Ecommerce Sync API only — GET/PUT/DELETE sync variants)
PRINTFUL_SHOPIFY_STORE_ID = "17797147"

# Manual/API store ID — must be set via env var PRINTFUL_MANUAL_STORE_ID
# Create this store at: https://www.printful.com/dashboard/stores
# Choose "Manual Order / API" as the store type.
PRINTFUL_MANUAL_STORE_ID: Optional[str] = None  # populated in create_sync_product flow


def _auth_headers(token: str, store_id: Optional[str] = None) -> Dict[str, str]:
    sid = store_id or PRINTFUL_SHOPIFY_STORE_ID
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-PF-Store-Id": sid,
    }


def _raise_for_api_error(response: requests.Response, context: str) -> None:
    if not response.ok:
        print(f"ERROR during {context}: HTTP {response.status_code}")
        print(f"  {response.text[:500]}")
        sys.exit(3)


def upload_file(token: str, logo_path: str) -> int:
    """
    Upload a logo file to Printful Files API.

    Returns:
        Printful file ID (int).
    """
    import base64, mimetypes
    path = Path(logo_path)
    mime = mimetypes.guess_type(str(path))[0] or "image/png"
    b64 = base64.b64encode(path.read_bytes()).decode()

    payload = {
        "type": "embroidery_front_large",
        "filename": path.name,
        "contents": b64,
        "mime_type": mime,
    }
    response = requests.post(
        f"{PRINTFUL_BASE_URL}/files",
        headers=_auth_headers(token),
        json=payload,
        timeout=60,
    )
    _raise_for_api_error(response, "file upload")
    return response.json()["result"]["id"]


def create_sync_product(
    token: str,
    config: Dict[str, Any],
    manual_store_id: str,
) -> Dict[str, Any]:
    """
    Create a Printful sync product in a Manual/API store.

    Requires a Manual Order / API store (POST /store/products is blocked for
    Shopify-connected stores). The manual_store_id must be the Printful store ID
    for a store of type "Manual Order / API".

    Returns:
        The full sync product result dict with id and sync_variants list.
    """
    file_type = config.get("file_type", "embroidery_front_large")
    file_entry = {
        "id": config["file_id"],
        "type": file_type,
    }
    embroidery_options = [
        {"id": "embroidery_type", "value": "flat"},
        {"id": "thread_colors", "value": []},
        {"id": "text_thread_colors", "value": []},
        {"id": "thread_colors_3d", "value": []},
        {"id": f"thread_colors_{file_type}", "value": []},
        {"id": f"text_thread_colors_{file_type}", "value": []},
        {"id": f"thread_colors_3d_{file_type}", "value": []},
    ]

    sync_variants = [
        {
            "variant_id": vid,
            "retail_price": config["retail_price"],
            "sku": f"pf_{vid}",
            "files": [file_entry],
            "options": embroidery_options,
        }
        for vid in config["variant_ids"]
    ]

    payload = {
        "sync_product": {
            "name": config["title"],
        },
        "sync_variants": sync_variants,
    }

    response = requests.post(
        f"{PRINTFUL_BASE_URL}/store/products",
        headers=_auth_headers(token, manual_store_id),
        json=payload,
        timeout=60,
    )
    _raise_for_api_error(response, "sync product creation")
    sync_product_id = response.json()["result"]["id"]

    # Fetch full details including sync_variants
    r2 = requests.get(
        f"{PRINTFUL_BASE_URL}/store/products/{sync_product_id}",
        headers=_auth_headers(token, manual_store_id),
        timeout=30,
    )
    _raise_for_api_error(r2, f"fetch sync product {sync_product_id}")
    return r2.json()["result"]


# ---------------------------------------------------------------------------
# Catalog helpers (for Shopify+Printful workflow)
# ---------------------------------------------------------------------------

def get_catalog_variant_color(token: str, variant_id: int) -> str:
    """
    Return the color name for a Printful catalog variant.

    Falls back to the variant name if `color` field is empty.
    """
    response = requests.get(
        f"{PRINTFUL_BASE_URL}/products/variant/{variant_id}",
        headers=_auth_headers(token),
        timeout=30,
    )
    _raise_for_api_error(response, f"catalog variant {variant_id}")
    variant = response.json()["result"]["variant"]
    color = variant.get("color") or ""
    if color:
        return color
    # Fall back to the part after the last " (" in the name
    name: str = variant.get("name", str(variant_id))
    if "(" in name:
        return name.rsplit("(", 1)[-1].rstrip(")")
    return name


# ---------------------------------------------------------------------------
# Ecommerce sync helpers (configure Printful sync for Shopify-linked store)
# ---------------------------------------------------------------------------

def get_sync_product_by_external_id(
    token: str, shopify_product_id: int
) -> Optional[Dict[str, Any]]:
    """
    Fetch a Printful sync product by Shopify product ID.

    Returns the full result dict (with sync_product + sync_variants) or None
    if Printful hasn't imported the product yet.
    """
    response = requests.get(
        f"{PRINTFUL_BASE_URL}/sync/products/@{shopify_product_id}",
        headers=_auth_headers(token),
        timeout=30,
    )
    if response.status_code == 404:
        return None
    _raise_for_api_error(response, f"sync product @{shopify_product_id}")
    return response.json()["result"]


def configure_sync_variant(
    token: str,
    sync_variant_id: int,
    catalog_variant_id: int,
    file_id: int,
    file_type: str = "embroidery_front_large",
    retail_price: Optional[str] = None,
) -> None:
    """
    Link a Printful sync variant to a catalog variant + embroidery file.

    Uses embroidery_type: flat with empty thread color arrays (auto-detect).
    Options mirror the working Retro Trucker reference configuration.
    """
    payload: Dict[str, Any] = {
        "variant_id": catalog_variant_id,
        "files": [
            {
                "type": file_type,
                "id": file_id,
            }
        ],
        "options": [
            {"id": "embroidery_type", "value": "flat"},
            {"id": "thread_colors", "value": []},
            {"id": "text_thread_colors", "value": []},
            {"id": "thread_colors_3d", "value": []},
            {"id": f"thread_colors_{file_type}", "value": []},
            {"id": f"text_thread_colors_{file_type}", "value": []},
            {"id": f"thread_colors_3d_{file_type}", "value": []},
        ],
    }
    if retail_price is not None:
        payload["retail_price"] = retail_price

    response = requests.put(
        f"{PRINTFUL_BASE_URL}/sync/variant/{sync_variant_id}",
        headers=_auth_headers(token),
        json=payload,
        timeout=30,
    )
    _raise_for_api_error(response, f"configure sync variant {sync_variant_id}")
