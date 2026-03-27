# Module : cb_velocity_service.py
# Purpose : - call shopify API
#           - read line_items sold in the last N days
#           - calculate items quantity
#           - calculate velocity

from typing import List, Dict
from datetime import datetime, timedelta
import requests

SHOPIFY_API_VERSION = "2026-01"

# -----------------------------------------------------
# Public API
# -----------------------------------------------------
def calculate_sales_velocity(
        shop_domain:str,
        access_token:str,
        shopify_product_ids:List[int],
        window_days: int = 14
) -> Dict[int, float]:
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

    url = f"https://{shop_domain}/admin/api/{SHOPIFY_API_VERSION}/orders.json"

    created_at_min = (
            datetime.utcnow() - timedelta(days=window_days)
    ).isoformat()

    params = {
        "status": "any",
        "limit": 250,
        "created_at_min": created_at_min,
        "fields": "line_items"
    }

    # -----------------------------------------------------
    # 3) Call Shopify Orders API
    # -----------------------------------------------------
    orders = []
    seen_next_urls = set()

    while True:

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
        page_orders = payload.get("orders", [])

        orders.extend(page_orders)

        # -----------------------------------------------------
        # Shopify pagination
        # -----------------------------------------------------
        next_link = response.links.get("next")

        if not next_link:
            break

        next_url = next_link.get("url")
        if not next_url:
            break

        # Anti-loop protection
        if next_url in seen_next_urls:
            break

        seen_next_urls.add(next_url)

        url = next_url
        params = None
    # -----------------------------------------------------
    # 4) Aggregate units sold per product
    # -----------------------------------------------------
    units_sold= {}

    for pid in shopify_product_ids:
        units_sold[pid] = 0

    for order in orders:

        # skip cancelled orders
        if order.get("cancelled_at") is not None:
            continue

        # skip test orders
        if order.get("test"):
            continue

        line_items = order.get("line_items", [])

        for item in line_items:

            product_id = item.get("product_id")
            quantity = item.get("quantity", 0)

            if product_id in units_sold:
                units_sold[product_id] += quantity

    # -----------------------------------------------------
    # 5) Calculate velocity
    # -----------------------------------------------------
    velocity: Dict[int, float] = {}

    for pid, units in units_sold.items():
        velocity[pid] = units / float(window_days)

    # -----------------------------------------------------
    # 6) Return velocity map
    # -----------------------------------------------------
    return velocity