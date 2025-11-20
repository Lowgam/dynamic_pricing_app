# Module : Shopify Connector
# Purpose : connect the web app to shopify

from typing import List, Dict

# Function that fakes products
# -> just help pycharm to understand what kind of value I want to get back from this function
def fetch_products_from_shopify_mock() -> List[Dict]:
    mock_products = [
        {
            "shopify_id": 1001,
            "sku": "TEST-APPLE-001",
            "name": "Mela bio in scadenza",
            "price": 1.99,
            "stock": 50,
            "category": "Frutta",
            "expiry_date": "2025-11-30",
        },
        {
            "shopify_id": 1002,
            "sku": "TEST-PASTA-002",
            "name": "Pasta integrale - lotto vicino scadenza",
            "price": 2.49,
            "stock": 120,
            "category": "Pasta",
            "expiry_date": "2026-01-15",
        },
        {
            "shopify_id": 1003,
            "sku": "TEST-YOGURT-003",
            "name": "Yogurt fragola (short MHD)",
            "price": 0.79,
            "stock": 80,
            "category": "Latticini",
            "expiry_date": "2025-11-25",
        },
    ]
    return mock_products