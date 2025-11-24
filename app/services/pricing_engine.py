# Module : pricing_engine.py
# Purpose : Create the heart of the modifying logic for the prices

from datetime import date
from typing import Optional, Union

# This function is used to calculate how many days are left to the expiration of a product
# It is the base of the next function.
# In order to calculate the number, it takes a string as expiry date (from shopify)
def days_to_expiry_converter(expiry_value : Optional[Union[str, date]]) -> Optional[int]:
    if not expiry_value:
        return None
# Then converts it to a date format with datetime library.
    if isinstance(expiry_value, date):
        expiry_date = expiry_value
    else:
        expiry_date = date.isoformat(expiry_value)
    today = date.today()
# Here it calculate the difference between the expiry date and today. It is a timedelta object, adding .days we just get a number, an int.
    delta = (expiry_date - today).days
    return delta

def calculate_new_price(
        base_price: float,
        cost_price: float,
        stock: Optional[int],
        sales_velocity: Optional[float],
        expiry_date_str,
) -> float:
    # 0) Conversion of base_price and cost_price from decimal.Decimal (coming from DB Py reads those datas as decimal)
    # to float, the variables we are using to calculate the discount
    base_price = float(base_price) if base_price is not None else 0.0
    cost_price = float(cost_price) if cost_price is not None else 0.0

    # 1) Calculate days before expiration date
    days_to_expiry = days_to_expiry_converter(expiry_date_str)

    # 2) Discount based on days to expiry
    discount = 0.0
    if days_to_expiry is None:
        # If we do not have any expiration date the discount is 0
        discount = 0.0

    else:
        if days_to_expiry <= 0:
            discount = 0.5
        elif days_to_expiry <= 3:
            discount = 0.4
        elif days_to_expiry <= 7:
            discount = 0.3
        elif days_to_expiry <= 14:
            discount = 0.2
        else:
            discount = 0.1

    # 3) Correction based on stock
    if stock is not None:
        if stock > 100:
            discount += 0.05
        elif stock < 20:
            discount -= 0.05

    # 4) Correction based on sales velocity
    if sales_velocity is not None:
        if sales_velocity < 0.2:
            discount += 0.05

    # 5) Tresholds for discounts between 0% and 80%. Here the max value between 0.0 and the min value between discount and 0.80 is chosen
    discount = max(0.0, min(discount, 0.80))

    # 6) Calculation discounted price through percentage
    simulated_price = base_price * (1 - discount)

    # 7) Treshplds for final price. Here the max value between simulated_price and cost_price is chosen.
    final_price = max(simulated_price, cost_price)

    # 8) Rounding to two decimals
    final_price = round(final_price, 2)

    return final_price

# ---------------------------------------------------
# ------------------- TESTING -----------------------
# ---------------------------------------------------

if __name__ == "__main__":
    price = 1.59
    cost = 0.80
    stock = 50
    sales_vel = 0.3
    expiry = "2025-11-30"

    new_price = calculate_new_price(price, cost, stock, sales_vel, expiry)
    print(f"Prezzo originale: {price} €  ->  Prezzo simulato: {new_price} €")

