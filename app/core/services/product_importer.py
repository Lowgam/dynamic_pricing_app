# Module : product_importer.py
# Purpose : compare the list of products coming from Shopify with the list coming from DB
# Import only products that are missing in DB (comparator = shopify_id)

from typing import List, Dict
from app.database.queries import get_existing_product_id, insert_product

def import_missing_products(products: List[Dict]) -> int:
    existing_ids = get_existing_product_id()
    imported_count = 0

    for p in products:
        shopify_id = p.get("shopify_id")
        if shopify_id is None:
            continue

        if shopify_id in existing_ids:
            continue

        insert_product(p)
        imported_count += 1

    return imported_count
