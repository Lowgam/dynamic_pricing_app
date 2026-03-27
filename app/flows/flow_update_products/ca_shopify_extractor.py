# Module : ca_shopify_extractor.py
# Purpose : extract data from Shopify

# Mock at the moment.

from typing import List, Dict
import requests

SHOPIFY_API_VERSION = "2026-01"
# -----------------------------------------------------
# Helper: split list into chunks
# -----------------------------------------------------
def chunk_list(lst, size):
    for i in range (0, len(lst), size):
        yield lst[i:i + size]
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
    print("INPUT IDS:", len(shopify_product_ids))

    # -----------------------------------------------------
    # 2) Prepare request
    # -----------------------------------------------------
    headers = {
        "X-Shopify-Access-Token": access_token
    }

    data: Dict[int, Dict[str, float]] = {}
       # -----------------------------------------------------
       # LOOP OVER CHUNKS (max 250 IDs per request)
       # -----------------------------------------------------
    for chunk in chunk_list(shopify_product_ids, 250):

        ids_string = ",".join(str(pid) for pid in chunk)
        url = f"https://{shop_domain}/admin/api/{SHOPIFY_API_VERSION}/products.json"
        params = {
            "ids": ids_string,
            "limit": 250
        }
    # -----------------------------------------------------
    # 3) API call
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

    print("RETURNED IDS:", len(data))
    return data







