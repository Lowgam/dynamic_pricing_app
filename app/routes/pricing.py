# Module : pricing.py
# Purpose : create an endpoint used to simulate calculation of new pricing using pricing_engine.py

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.database.queries import get_all_products
from app.services.pricing_engine import calculate_new_price

# Create new route
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/simulate-prices-ui", response_class=HTMLResponse)
def simulate_pricing_ui(request: Request):
    simulated_data = simulate_prices()
    products = simulated_data["products"]

    return templates.TemplateResponse(
        "simulated_prices.html",
        {
            "request": request,
            "products": products,
        }
    )

@router.get("/simulate-prices")
def simulate_prices():
    products = get_all_products()

    if products is None:
        return {"Error": "No products found"}
    simulated_prices = []

    for p in products:
        base_price = p["price"]
        cost_price = p["cost_price"]
        stock = p["stock"]
        expiry_date = p["expiry_date"]

        # Not calculated yet
        sales_velocity = None

        new_price = calculate_new_price(
            base_price=base_price,
            cost_price=cost_price,
            stock=stock,
            sales_velocity=sales_velocity,
            expiry_date_str=expiry_date
        )

        # Must be implemented with the missing values (like shopify_id, sku etc)
        simulated_prices.append({
            "id": p["id"],
            "name": p["name"],
            "cost_price": float (cost_price),
            "old_price": float (base_price),
            "new_price": float (new_price),
            "stock": int (stock) if stock is not None else None,
            "expiry_date": expiry_date,
        })

    return {"products": simulated_prices}