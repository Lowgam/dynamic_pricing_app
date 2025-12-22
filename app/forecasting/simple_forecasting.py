# Module : simple_forecasting.py
# Purpose : mathematical function to "forecast" the new selling velocity after price change
# This module doesn't have at the moment the claim to be an exacting forecast. An exact forecast
# can be implemented with future works.

from typing import Optional

def estimate_velocity_from_price_change(
        velocity_now: float,
        old_price: float,
        new_price: float,
        k: float = 0.8,
        min_factor: float = 0.5,
        max_factor: float = 3.0,
) -> Optional[float]:
    if velocity_now is None or old_price is None or new_price is None:
        return None

    try:
        v_now = float(velocity_now)
        p_old = float(old_price)
        p_new = float(new_price)
    except (TypeError, ValueError):
        return None

    if v_now <= 0 or p_old <= 0:
        return None

    # The way we calculate now is simple. Inverted proportionality.
    # The upper the price goes, the lower the future velocity will be.
    # For example: v_now = 2u/d; p_old = 10, p_new = 8. price_change_pct = -20% -> 0.20
    # factor = 1 + (0.5 * 0.20) = 1.10. Velocity_ai = 2 * 1.10 = 2.2u/d
    price_change_pct = (p_old - p_new) / p_old
    factor = 1.0 + (k * price_change_pct)

    if factor < min_factor:
        factor = min_factor
    if factor > max_factor:
        factor = max_factor

    return v_now * factor