# Module: models.py
# Purpose: Represent the structure of datas inside the DB

#FastAPI uses pydantic to 1) validate type and format, 2) automathic conversion (https -> strg 12.5 pydantic -> float) 3) automathic generation of documentation.
from pydantic import BaseModel
from typing import Optional

# -------------------------------------------------
# Product model
# -------------------------------------------------

#Product is a pydantic model, with his own "powers" FastAPI without pydantic doesn't exist.
class Product(BaseModel):
    # Optional can be a str or none(empty). It is needed because real datas are not always complete. Something can be missing
    # We use str instead of datetime because we get those datas from Shopify that uses str for days. Datetime is more rigid. I might change it later
    id: int
    shopify_id: Optional[int] = None
    sku: Optional[str] = None
    name: Optional[str] = None
    price: Optional[float] = None
    cost_price: float
    stock: Optional[int] = None
    category: Optional[str] = None
    expiry_date: Optional[str] = None
# -------------------------------------------------
# Pricing rule model
# -------------------------------------------------

class PricingRule(BaseModel):
    id: int
    rule_name: str
    factor_a: float
    factor_b: float
    threshold: float
    active: bool