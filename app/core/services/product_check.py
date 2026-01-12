# Module : product_check.py
# Purpose : check active products on Shopify who are missing on DB

import json

from app.database.queries import get_existing_product_id

def count_missing_active_products() -> int:
    # 1) Load MOCK
    with open("data/samples/product_shopify_mock.json", "r") as f:
        payload = json.load(f)

    # 2) Shopify products from mock
    shopify_products= payload.get("products", [])

    # 2) Get existing Shopi IDs from DB
    existing_ids = get_existing_product_id()

    # 3) Count missing active products
    missing_count = 0

    for p in shopify_products:
        if p.get("status") != "active":
            continue

        shopify_id = p.get("id")
        if shopify_id not in existing_ids:
            missing_count += 1

    return missing_count

