# Module : ai_engine.py
# Purpose : The heart of the machine learning structure

# Tasks :
# - Receive product features (stock, MHD, sales, new price)
# - Calculate an adjustment coefficient
# - Give back a value used by pricing engine

from typing import Dict

# ---------------------------------------------------
# Fx: Calculate the final price: AI
# ---------------------------------------------------
def calculate_ai_coefficient(engined_price: float, features: Dict) -> Dict:
    # At the moment only a mathematical logic is needed to test the connection and dashboard
    # This will be implemented with ML in the next weeks
    coeff = 1.0
    reason = []

    days_to_expire = features.get("days_to_expire")
    # or is used here as a kind of if: is the stock is none or 0? then take the "or"
    stock = features.get("stock") or 0
    sales_velocity = features.get("sales_velocity", 0) or 0

    # First calculation with expiration date
    if days_to_expire <= 3:
        coeff -= 0.10
        reason.append("Almost expired: reduce the price")
    elif days_to_expire <= 7:
        coeff -= 0.05
        reason.append("Around expiration: small discount")
    elif days_to_expire > 30:
        coeff -= 0.03
        reason.append("Far expiration: light increase")

    # Second calculation with cover days
    if sales_velocity > 0:
        cover_days = stock / sales_velocity
        if cover_days > 30:
            coeff -= 0.05
            reason.append("Big stock, no sales: increase discount")
        elif cover_days < 7:
            coeff += 0.05
            reason.append("Small stock, good sales:: slight increase")

    # Third limiting
    coeff = max(0.0, min(1.2,coeff))


    return {
        "coefficient": round(coeff,3),
        # .join unify the elements in a single str
        "reason": ", ".join(reason) if reason else "No particular reasons",
    }


