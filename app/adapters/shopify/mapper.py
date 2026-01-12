# Module : mapper.py
# Purpose : transform Shopify product's map in values from DB

from typing import Dict

def map_shopify_product_to_db(product: Dict) -> Dict:
    variant = product["variants"][0]

    return {
        "shopify_id": product["id"],
        "sku": variant.get("sku"),
        "name": product.get("title"),
        "price": float(variant.get("price")) if variant.get("price") is not None else None,
        "stock": variant.get("inventory_quantity"),
        "category": None,  # non ancora gestita
        "expiry_date": product.get("metafields", {}).get("expiry_date"),
        "sales_velocity_14d": product.get("metafields", {}).get("sales_velocity_14d"),
    }