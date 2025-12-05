# Module : pricing_ai_pipeline.py
# Purpose : create the final flow for pricing calculation:
# pricing_engine > feature_builder > ai_engine > pricing_engine

# __future__ allows to import or use name of variable before they are imported or defined
from __future__ import annotations

from typing import List, Dict

from app.services.pricing_engine import calculate_engined_price, apply_engined_price
from app.services.feature_builder import build_features
from app.services.ai_engine import calculate_ai_coefficient

# ---------------------------------------------------
# Fx: simulate new prices using AI
# ---------------------------------------------------
def simulate_new_prices_with_ai(products: List[Dict]) -> List[Dict]:

    # In pyt : can be used to give a hint of what kind of variable we want to use
    result : List[Dict] = []
    for p in products:

        # 0) Calculate sales velocity FOR LATER
        # sales_last_7_days = p["sales_last_7_days"]
        sales_velocity = None # sales_last_7_days / 7 if sales_last_7_days > 0 else 0.0

        # 1) calculate the engined price
        engined_price = calculate_engined_price(
            base_price=p["price"],
            cost_price=p["cost_price"],
            stock=p["stock"],
            sales_velocity= sales_velocity,
            expiry_date_str=p["expiry_date"]
        )

        # 2) Build features for ai
        features = build_features(p, engined_price)

        # 3) Calculate ai coefficient
        ai_output = calculate_ai_coefficient(engined_price, features)
        ai_coeff = ai_output["coefficient"]

        # 4) Calculate the final price back to the engine
        final_price = apply_engined_price(engined_price, ai_coeff)

        # 5) Return completed package for UI / API
        result.append({
            "id": p.get("id"),
            "sku": p.get("sku"),
            "name": p.get("name") or p.get("title"),
            "category": p.get("category"),
            "base_price": p.get("price"),
            "cost_price": p.get("cost_price"),
            "engined_price": engined_price,
            "ai_coefficient": ai_coeff,
            "ai_reason": ai_output["reason"],
            "final_price": final_price,
            "expiry_date": p.get("expiry_date"),
            "stock": p.get("stock"),
            "sales_velocity": p.get("sales_velocity"),
        })

    return result