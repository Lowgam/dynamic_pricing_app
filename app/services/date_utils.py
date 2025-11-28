# Module : date_utils.py
# Purpose : Convert date types

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Any

# ---------------------------------------------------
# Fx: Convert values in date
# ---------------------------------------------------
def to_date(value: Any) -> Optional[date]:

    # Case 1: already a date
    if isinstance(value, date):
        return value

    # datetim -> date
    if isinstance(value, datetime):
        return value.date()

    # Decimal -> str
    if isinstance(value, Decimal):
        try:
            return datetime.strptime(str(value), "%Y-%m-%d").date()
        except:
            return None

    # str -> date
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(value, fmt).date()
            except:
                pass  # trying other format
        return None  # no valid format

    # Other types are not convertible
    return None


# ---------------------------------------------------
# Fx: Calculate days to expiry
# ---------------------------------------------------
def days_to_expiry(value: Any) -> int:

    dt = to_date(value)
    if dt is None:
        # 9999 is a safe fallback: None would make the program crash. We can then implement in ai_engine an if that
        # excludes 9999 as a possible date, changing it to 0.
        return 9999

    return (dt - date.today()).days
