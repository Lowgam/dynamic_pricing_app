# Module : dashboard.py
# Purpose : Creation dashboard endpoint

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

from app.services.chart_data_builder import build_chart_data

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

