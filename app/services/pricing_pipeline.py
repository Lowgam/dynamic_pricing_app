# Module : pricing_pipeline.py
# Purpose : connect pricing_engine to shopify_connector.py(mock atm)

from __future__ import annotations

from typing import List, Dict, Optional

from app.services.pricing_engine import calculate_engined_price
from app.services.shopify_connector import fetch_products_from_shopify_mock, ShopifyProduct

# ---------------------------------------------------
# Fx: Connect shopify_connector with the engine
# ---------------------------------------------------
def simulate_new_prices_from_mock() -> List[Dict]:

    product_from_mock = fetch_products_from_shopify_mock()
    simulated_prices_from_mock = []

    for p in product_from_mock:
        final_price = calculate_engined_price(
            base_price=p["base_price"],
            cost_price=p["cost_price"],
            stock=p["stock"],
            sales_velocity=p["sales_velocity"],
            expiry_date_str = p['expiry_date']
        )

        simulated_prices_from_mock.append(
            {
                "sku": p["sku"],
                "name": p["name"],
                "category": p["category"],
                "base_price": p["base_price"],
                "cost_price": p["cost_price"],
                "simulated_price": final_price,
                "expiry_date": p["expiry_date"],
                "stock": p["stock"],
                "sales_velocity": p["sales_velocity"],
            }
        )

    return simulated_prices_from_mock

# ---------------------------------------------------
# ------------------- TESTING -----------------------
# ---------------------------------------------------

# ---------------------------------------------------
# Test for successful connection and calculation
# ---------------------------------------------------
if __name__ == "__main__":
    result = simulate_new_prices_from_mock()
    for r in result:
        print(
            f"{r['sku']} | {r['name']} | base={r['base_price']}€ "
            f"→ simulated={r['simulated_price']}€ "
            f"| expiry={r['expiry_date']} | stock={r['stock']} "
            f"| velocity={r['sales_velocity']}"
        )



