# Module : b_pricing_ai_pipeline.py
# Purpose : create the final flow for pricing calculation:
# pricing_engine > feature_builder > ai_engine > pricing_engine

# __future__ allows to import or use name of variable before they are imported or defined
from __future__ import annotations

from typing import List, Dict

from app.flows.flow_ai_pricing.ca_pricing_engine import calculate_engined_price, apply_engined_price
from app.flows.flow_ai_pricing.cb_feature_builder import build_features
from app.flows.flow_ai_pricing.cc_ai_coeff_engine import calculate_ai_coefficient
from app.core.utils.logger import ai_logger

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
            sales_velocity= p["sales_velocity_14d"],
            expiry_date_str=p["expiry_date"]
        )

        # 2) Build features for ai
        features = build_features(p, engined_price)

        # 3) Calculate ai coefficient
        ai_output = calculate_ai_coefficient(engined_price, features)
        ai_coeff = ai_output["coefficient"]

        # 4) Calculate the final price with AI coefficient
        final_price = apply_engined_price(engined_price, ai_coeff)

        # 4.1) Log AI suggestions
        ai_logger.info(
            "AI suggestion | product_id=%s | sku=%s | name=%s | base_price=%s | "
            "engined_price=%s | ai_coeff=%s | final_price=%s | reason=%s",
            p.get("id"),
            p.get("sku"),
            p.get("name") or p.get("title"),
            p.get("price"),
            engined_price,
            ai_coeff,
            final_price,
            ai_output["reason"],
        )

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
            "sales_velocity": p.get("sales_velocity_14d"),
        })

    return result