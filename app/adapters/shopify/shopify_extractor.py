# Module : shopify_extractor.py
# Purpose : extract data from Shopify

# Mock at the moment.

from typing import List, Dict

# -----------------------------------------------------
# Public API (contract)
# -----------------------------------------------------

def fecth_products() -> List[Dict]:
    # MOCK MOCK MOCK MOCK MOCK MOCK MOCK
    # MOCK MOCK MOCK MOCK MOCK MOCK MOCK
    # MOCK MOCK MOCK MOCK MOCK MOCK MOCK
    return [
        {
            "shopify_id": 101,
            "sku": "TEST-APPLE-001",
            "name": "Mela Bio",
            "price": 0.50,
            "stock": 42,
            "expiry_date": "2025-12-20"
        },
        {
            "shopify_id": 102,
            "sku": "TEST-PASTA-002",
            "name": "Pasta Integrale",
            "price": 1.20,
            "stock": 30,
            "expiry_date": "2026-01-15"
        }
    ]

def fecth_inventory_and_velocity(
        shopify_product_ids: List[int],
        window_days = 14
) -> Dict[int, Dict[str, float]]:
    data = {}

    for pid in shopify_product_ids:
        data[pid] = {
            "stock": _mock_stock(pid),
            "sales_velocity": _mock_sales_velocity(pid, window_days),
            "status": _mock_status(pid)
        }
    return data

# -----------------------------------------------------
# MOCK HELPERS
# -----------------------------------------------------
def _mock_stock(shopify_product_id: int) -> int:
    return 20 + (shopify_product_id % 15)

def _mock_sales_velocity(shopify_product_id: int, window_days: int) -> float:
    base = (shopify_product_id % 7) + 1
    return round(base / float(window_days), 4)

def _mock_status(shopify_product_id: int) -> str:
    return "archived" if (shopify_product_id % 2 == 0) else "active"

