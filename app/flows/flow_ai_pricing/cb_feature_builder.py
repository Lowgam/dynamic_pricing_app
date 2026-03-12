# Module : cb_feature_builder.py
# Purpose : Extract and prepare necessary features for ai_engine

from typing import Dict, Any
from app.core.utils.date_utils import days_to_expiry

# ---------------------------------------------------
# Fx: Build the features for AI
# ---------------------------------------------------
def build_features(product: Dict[str, Any], engined_price:float) -> Dict[str, Any]:

    """ PLACEHOLDER
    parameters:
    product (dict): da DB o MOCK
    -expiry_date
    - stock
    - sales_last_7_day
    - engined_price

    returns:
    dict: feature for ia
    - product_id:
    - days_to_expire
    - stock:
    - recent_sales:
    - engined_price:
    """


    features = {
        "product_id": product.get("id"),
        # Calling function of date_utils
        "days_to_expire": days_to_expiry(product.get("expiry_date")),
        # with ,0 we are building an inner if: py understans: get the value for stock, if it is none or 0, then take the argument after , (0 in this case)
        "stock": product.get("stock",0),
        "recent_sales": product.get("sales_last_7_day",0),
        # Compact way to write an if
        "sales_velocity": product.get("sales_velocity_14d") or 0.0,
        "engined_price": engined_price,
    }

    return features