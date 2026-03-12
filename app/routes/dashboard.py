# Module : dashboard.py
# Purpose : Creation dashboard endpoint

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from typing import List

from starlette.responses import RedirectResponse

from app.core.services.chart_data_builder import build_chart_data
from app.core.utils import days_to_expiry
from app.database.queries import get_products_by_ids, get_all_products, update_product, insert_change_price_event
from app.flows.flow_ai_pricing.b_pricing_ai_pipeline import simulate_new_prices_with_ai
from app.forecasting.forecasting_pipeline import build_sellout_forecast
from app.core.utils.auth_guard import require_login

router = APIRouter(
    dependencies=[Depends(require_login)]
)
templates = Jinja2Templates(directory="app/templates")

# ---------------------------------------------------
# FX: Get endpoint for dashboard
# ---------------------------------------------------
@router.get("/dashboard")
async def dashboard_page(request: Request):
    products = get_all_products()
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "products": products,}
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

    for p in suggestion:
        dte = days_to_expiry(p.get("expiry_date"))

        stock = p.get("stock")
        velocity_now = p.get("sales_velocity")
        old_price = float(p.get("base_price"))
        new_price = float(p.get("final_price"))

        print("DEBUG", p.get("id"), "stock=", p.get("stock"), "velocity=", p.get("velocity_14d"),
              p.get("sales_velocity_14d"), p.get("sales_velocity"))

        forecast = build_sellout_forecast(
            stock=stock,
            velocity_now=velocity_now,
            days_to_expiry=dte,
            old_price=old_price,
            new_price=new_price,
        )

        p.update(forecast)

    return templates.TemplateResponse(
        "ai_suggestions.html",
        {
            "request": request,
            "products": suggestion,
            "ids": ids,
        },
    )

# ---------------------------------------------------
# FX: Post endpoint for suggestion -> apply
# ---------------------------------------------------
@router.post("/ai-suggestions/apply")
async def ai_suggestions_apply(request: Request, ids: str= ""):
    # Reads body from POST request (in HTML template)
    form = await request.form()
    ids = (form.get("ids") or ids or "").strip()

    selected_ids: List[int] = [int(x) for x in ids.split(",") if x.strip()]
    if not selected_ids:
        raise HTTPException(status_code=400, detail="No ids selected (empty ids)")

    products = get_products_by_ids(selected_ids)
    if not products:
        raise HTTPException(status_code=404, detail="No products found")

    old_price_by_id = {p["id"]: float (p["price"]) for p in products}

    suggestion = simulate_new_prices_with_ai(products)

    for p in suggestion:
        pid = int(p["id"])
        old_price = old_price_by_id.get(pid)
        new_price = float(p["final_price"])

        update_product(pid, new_price)
        insert_change_price_event(pid,old_price, new_price, source="ai-suggestions")

    return RedirectResponse(url=f"/ai-suggestions?ids={ids}&applied=1", status_code=303)

