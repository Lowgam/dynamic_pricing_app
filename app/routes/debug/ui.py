# Module : ui.py
# Purpose : file for HTML endpoints

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.database.queries import get_all_products
from app.core.services.debug.pricing_pipeline import simulate_new_prices_from_mock
from app.core.services.debug.pricing_db_pipeline import simulate_prices_from_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# ---------------------------------------------------
# Fx: Get all products to endpoint : UI
# ---------------------------------------------------
@router.get("/products-ui", response_class=HTMLResponse)
# Jinja2 always request a Request for a TemplateResponse.
# It is the object that represents HTMP request and allows TemplateResponse to work well.
async def products_page(request: Request):
    products = get_all_products()
    return templates.TemplateResponse(
        "debug/product_list.html",
        {
            "request": request,
            "products": products,
        }
    )

# ---------------------------------------------------------------------
# Fx: Get all products from DB and calculate new prices. UI Return
# ---------------------------------------------------------------------
@router.get("/simulate-prices-ui", response_class=HTMLResponse)
async def simulate_pricing_ui(request: Request):
    simulated_data = simulate_prices_from_db()
    products = simulated_data["products"]

    return templates.TemplateResponse(
        "debug/simulated_prices.html",
        {
            "request": request,
            "products": products,
            "count": len(products),
            "source": "DB"
        }
    )

# ---------------------------------------------------------------------
# Fx: Simulate pricing mock UI Return
# ---------------------------------------------------------------------
@router.get("/simulate-prices-mock-ui")
async def simulate_pricing_mock_ui(request: Request):
    result = simulate_new_prices_from_mock()

    return templates.TemplateResponse(
        "debug/simulated_prices.html",
        {
            "request": request,
            "products": result,
            "count": len(result),
            "source": "Shopify Mock"
        }
    )
