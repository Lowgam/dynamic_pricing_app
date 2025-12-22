# Module : sellout_estimator.py
# Purpose : sell-out and expiry overshoot estimator (not complex)

from typing import Optional

def calculate_days_to_sellout(stock: float, velocity_per_days: float) -> Optional[float]:
    if stock is None or velocity_per_days is None:
        return None

    try:
        s = float(stock)
        v = float(velocity_per_days)
    except (TypeError, ValueError):
        return None
    if s <= 0:
        return None
    if v <= 0:
        return None

    return s / v

def calculate_overshoot(days_to_sellout: Optional[float], days_to_expiry: int) -> Optional[float]:
    if days_to_sellout is None:
        return None

    try:
        dts = float(days_to_sellout)
        dte = int(days_to_expiry)

    except (TypeError, ValueError):
        return None

    return dts - dte

