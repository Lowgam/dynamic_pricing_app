# Module : shopify_extractor.py
# Purpose : extract data from Shopify

# Mock at the moment.

from typing import List, Dict
import requests

SHOPIFY_API_VERSION = "2026-01"

# -----------------------------------------------------
# Public API (contract)
# -----------------------------------------------------

def fecth_inventory_and_velocity(
        shop_domain: str,
        access_token: str,
        shopify_product_ids: List[int],
        window_days = 14
) -> Dict[int, Dict[str, float]]:
    # -----------------------------------------------------
    # 1) Guard clause
    # -----------------------------------------------------
    if not shopify_product_ids:
        return {}

    # -----------------------------------------------------
    # 2) Prepare request
    # -----------------------------------------------------
    headers = {
        "X-Shopify-Access-Token": access_token
    }

    ids_string = ",".join(str(pid) for pid in shopify_product_ids)

    url = f"https://{shop_domain}/admin/api/{SHOPIFY_API_VERSION}/products.json"

    params = {
        "ids": ids_string,
        "limit": 250
    }

    # -----------------------------------------------------
    # 3) Perform API call
    # -----------------------------------------------------

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30
    )

    if response.status_code >= 400:
        raise RuntimeError(
            f"Shopify API error {response.status_code}: {response.text[:300]}"
        )

    payload = response.json()
    products = payload.get("products", [])

    # -----------------------------------------------------
    # 4) Normalize data
    # -----------------------------------------------------

    data: Dict[int, Dict[str, float]] = {}

    for product in products:
        pid = product["id"]
        variants = product.get("variants", [])

        if not variants:
            continue

        variant = variants[0]

        data[pid] = {
            # Price is stored inside the variant
            "price": float(variant.get("price", 0)),

            # inventory_quantity is directly available in the variant
            "stock": variant.get("inventory_quantity", 0),

            # Velocity will be calculated later in a dedicated service
            "sales_velocity": 0,

            # Product status (active / archived / draft)
            "status": product.get("status", "active"),
        }

    # -----------------------------------------------------
    # 5) Return normalized structure
    # -----------------------------------------------------

    return data







