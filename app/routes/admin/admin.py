from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from app.core.services.product_check import count_missing_active_products
from app.core.utils.auth_guard import require_login

router = APIRouter(
    dependencies=[Depends(require_login)]
)
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
