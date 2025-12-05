# Module : dashboard.py
# Purpose : Creation dashboard endpoint

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from typing import List

from app.services.chart_data_builder import build_chart_data
from app.database.queries import get_products_by_ids
from app.services.pricing_ai_pipeline import simulate_new_prices_with_ai

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# ---------------------------------------------------
# FX: Get endpoint for dashboard
# ---------------------------------------------------
@router.get("/dashboard")
async def dashboard_page(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )

# ---------------------------------------------------
# FX: Get endpoint for chart data
# ---------------------------------------------------
@router.get("/chart-data")
async def chart_data(product_id: int = 1):
    data = build_chart_data(product_id)
    return JSONResponse(content=data)

# ---------------------------------------------------
# FX: Get endpoint for ai suggestions
# ---------------------------------------------------
@router.get("/ai-suggestions")
async def ai_suggestions(request: Request, ids: str= ""):
# When the user select ids on the dashboard, the JS script redirects him to /ai-suggestion?ids=${ids.join(",")};
# FastAPI receive the GET request at the URL with ids in it. Take the string in ?ids=... and puts it into ids parameter of the following function
# How does this happen? All the parameters that are NOT in the path (in this case /ai-suggestion) are automatically read by FastAPI
# as query parameters. Then it reads and compares with the functions is coming after, and assign it where the names coincide.
    selected_ids: List[int] = []
    if ids:
        # list comprehension: compact method for creating lists
        # for every element of the list, the string is divided and transformed in an int
        # .strip erases empty spaces
        selected_ids = [int(x) for x in ids.split(",") if x.strip()]
    if not selected_ids:
        products = []
    else:
        products = get_products_by_ids(selected_ids)

    suggestion = simulate_new_prices_with_ai(products)

    return templates.TemplateResponse(
        "ai_suggestions.html",
        {
            "request": request,
            "products": suggestion,
        },
    )
