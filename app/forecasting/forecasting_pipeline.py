# Module : forecasting_pipeline.py
# Purpose : pipeline used to forecast and prepare datas for UI

from typing import Optional, Dict

from app.forecasting.sellout_estimator import (
calculate_overshoot,
calculate_days_to_sellout
)
from app.forecasting.simple_forecasting import estimate_velocity_from_price_change

def build_sellout_forecast(
        *,
        stock: float,
        velocity_now: float,
        days_to_expiry: int,
        old_price: float,
        new_price: float,
) -> Dict[str, Optional[float]]:
    # --- CURRENT STATUS ---
    days_to_sellout_now = calculate_days_to_sellout(stock, velocity_now)
    overshoot_now =calculate_overshoot(days_to_sellout_now, days_to_expiry)

    # --- AI ESTIMATED STATUS ---
    velocity_ai = estimate_velocity_from_price_change(
        velocity_now = velocity_now,
        old_price = old_price,
        new_price = new_price,
    )

    days_to_sellout_ai = (
        calculate_days_to_sellout(stock, velocity_ai)
        if velocity_ai is not None
        else None
    )

    overshoot_ai = calculate_overshoot(days_to_sellout_ai, days_to_expiry)

    return {
        "days_to_sellout_now": days_to_sellout_now,
        "overshoot_now": overshoot_now,
        "days_to_sellout_ai": days_to_sellout_ai,
        "overshoot_ai": overshoot_ai,
    }