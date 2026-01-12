from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.services.product_check import count_missing_active_products

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/admin")
async def admin_dashboard(request: Request):
    missing_products = count_missing_active_products()
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "missing_products": missing_products,
        }
    )
