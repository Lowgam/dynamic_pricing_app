# Module : pricing_db_pipeline.py
# Purpose : calculate simulation of new prices taking datas from DB

from app.database.queries import get_all_products
from app.services.pricing_engine import calculate_engined_price

# ---------------------------------------------------------------------
# Fx: Calculate a pricing simulation from DB
# ---------------------------------------------------------------------
def simulate_prices_from_db():
    products = get_all_products()

    if products is None:
        return {"Error": "No products found"}
    simulated_prices = []

    for p in products:
        base_price = p["price"]
        cost_price = p["cost_price"]
        stock = p["stock"]
        expiry_date = p["expiry_date"]

        # Not calculated yet
        sales_velocity = None

        new_price = calculate_engined_price(
            base_price=base_price,
            cost_price=cost_price,
            stock=stock,
            sales_velocity=sales_velocity,
            expiry_date_str=expiry_date
        )

        # Must be implemented with the missing values (like shopify_id, sku etc)
        simulated_prices.append({
            "id": p["id"],
            "name": p["name"],
            "cost_price": float (cost_price),
            "old_price": float (base_price),
            "new_price": float (new_price),
            "stock": int (stock) if stock is not None else None,
            "expiry_date": expiry_date,
        })

    return {"products": simulated_prices}