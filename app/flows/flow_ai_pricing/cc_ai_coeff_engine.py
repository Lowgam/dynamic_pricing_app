# Module : cc_ai_coeff_engine.py
# Purpose : The heart of the machine learning structure

# Tasks :
# - Receive product features (stock, MHD, sales, new price)
# - Calculate an adjustment coefficient
# - Give back a value used by pricing engine

from typing import Dict
from app.database.learning_store import load_current_weights

# ---------------------------------------------------
# Fx: Calculate the final price: AI
# ---------------------------------------------------
def calculate_ai_coefficient(engined_price: float, features: Dict) -> Dict:
    # 1) Load current weights
    weights = load_current_weights()

    # 2) Assign single weights
    w_stock = float(weights.get("w_stock", 1.0))
    w_mhd = float(weights.get("w_mhd", 1.0))
    w_velocity = float(weights.get("w_velocity", 1.0))
    w_base = float(weights.get("w_base", 1.0))

    # 3) Extracting features for explanations purposes
    stock = int(features.get("stock") or 0)
    days_to_expire = int(features.get("days_to_expiry") or 0)
    sales_velocity = float(features.get("sales_velocity") or 0.0)
    reason = []

    # 4) Modulation logic
    # Convert weights into a "strategy tilt" around 1.0.
    # If weights drift above 1.0 -> slightly more aggressive (lower coeff).
    # If weights drift below 1.0 -> slightly more conservative (higher coeff).
    #
    # This is intentionally mild: it just nudges the final price.
    # 4.1) Calculate average weight
    avg_w = (w_stock + w_mhd + w_velocity) / 3.0

    # 4.2) Choose a sensitivity coefficient.
    # If we want to make AI more aggressive we can modify the following variable
    ai_sensitivity = 0.10
    # 4.3) Calculate tile
    tilt = (avg_w - 1.0) * ai_sensitivity
    # 4.4) Calculate the final coefficient
    coeff = 1.0 - (tilt * w_base)

    # 5) Thresholds
    coeff = max(0.95, min(1.05, coeff))

    # 6) Explainability
    reason.append(
        f"w_stock={round(w_stock, 3)} w_mhd={round(w_mhd, 3)} w_velocity={round(w_velocity, 3)} w_base={round(w_base, 3)}")
    reason.append(f"context: stock={stock}, days_to_expire={days_to_expire}, velocity={sales_velocity}")
    reason.append(f"avg_w={round(avg_w, 3)} tilt={round(tilt, 3)}")

    return {
        "coefficient": round(coeff, 3),
        "reason": " | ".join(reason),
    }

