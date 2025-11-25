# Module : Shopify Connector
# Purpose : connect the web app to shopify

from __future__ import annotations

from datetime import date, timedelta
from typing import List, Dict, Optional, TypedDict

# Class for the future Shopify products
class ShopifyProduct(TypedDict):
    shopify_products_id: int
    shopify_variant_id: int
    sku: str
    name: str
    category: str

    base_price: float
    cost_price: float
    stock: int
    currency: str

    expiry_date: Optional[date]
    expiry_source: str # metafield | manual | none

    sales_velocity: float

# Function that fakes products incoming from Shopify
# -> just help pycharm to understand what kind of value I want to get back from this function
def fetch_products_from_shopify_mock() -> List[ShopifyProduct]:
    today = date.today()

    products: List[ShopifyProduct] = [
        ShopifyProduct(
            shopify_product_id=1001,
            shopify_variant_id=2001,
            sku="YOG-STR-150",
            name="Yogurt Fragola 150g",
            category="Latticini",
            base_price=1.99,
            cost_price=0.60,
            stock=120,
            currency="EUR",
            expiry_date=today + timedelta(days=2),
            expiry_source="metafield",
            sales_velocity=8.0,
        ),
        ShopifyProduct(
            shopify_product_id=1002,
            shopify_variant_id=2002,
            sku="PST-PENNE-500",
            name="Pasta Penne 500g",
            category="Dispensa",
            base_price=1.49,
            cost_price=0.40,
            stock=60,
            currency="EUR",
            expiry_date=today + timedelta(days=45),
            expiry_source="metafield",
            sales_velocity=2.0,
        ),
        ShopifyProduct(
            shopify_product_id=1003,
            shopify_variant_id=2003,
            sku="BSC-COOKIES-200",
            name="Biscotti Integrali 200g",
            category="Snack",
            base_price=2.49,
            cost_price=0.80,
            stock=30,
            currency="EUR",
            expiry_date=today - timedelta(days=5),
            expiry_source="metafield",
            sales_velocity=8.5,
        ),
        ShopifyProduct(
            shopify_product_id=1004,
            shopify_variant_id=2004,
            sku="HNY-JAR-250",
            name="Miele Millefiori 250g",
            category="Dispensa",
            base_price=4.99,
            cost_price=2.00,
            stock=15,
            currency="EUR",
            expiry_date=None,
            expiry_source="none",
            sales_velocity=1.0,
        ),
    ]

    return products


# ---------------------------------------------------
# ------------------- TESTING -----------------------
# ---------------------------------------------------

# ---------------------------------------------------
# Test for successful SELECT
# ---------------------------------------------------
if __name__ == "__main__":
    mock_products = fetch_products_from_shopify_mock()
    print(f"Found {len(mock_products)} mock products from Shopify:\n")
    for p in mock_products:
        print(
            f"- {p['sku']} | {p['name']} | base_price={p['base_price']} "
            f"| stock={p['stock']} | expiry={p['expiry_date']}"
            f"| velocity={p['sales_velocity']} pieces/day"
              )