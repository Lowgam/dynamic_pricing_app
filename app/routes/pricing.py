# Module : pricing.py
# Purpose : create an endpoint used to simulate calculation of new pricing using pricing_engine.py

from fastapi import APIRouter, Request

from app.database.queries import get_all_products
from app.core.services.pricing_db_pipeline import simulate_prices_from_db
from app.core.services.pricing_pipeline import simulate_new_prices_from_mock
from app.core.services.pricing_ai_pipeline import simulate_new_prices_with_ai

# Create new route
router = APIRouter()

# ---------------------------------------------------------------------
# Fx: Get all products from DB and calculate new prices.
# ---------------------------------------------------------------------
@router.get("/simulate-prices")
async def simulate_prices(request: Request):
    return simulate_prices_from_db()

# ---------------------------------------------------------------------
# Fx: Simulate pricing mock
# ---------------------------------------------------------------------
@router.get("/simulate-prices-mock")
# async is here used because FastAPI is able to work asynchronically. That means we can  execute many request at the same time
# using a normal def means that the program need the server won't be blocked by multiple requests. It is  more flexible with I/O
async def simulate_pricing_mock():
    result = simulate_new_prices_from_mock()
    return result

# ---------------------------------------------------------------------
# Fx: Simulate pricing AI
# ---------------------------------------------------------------------
@router.get("/simulate-prices-ai")
async def simulate_pricing_ai():
    products = get_all_products()

    if not products:
        return {"Error": "No products found"}

    results = simulate_new_prices_with_ai(products)
    return results

