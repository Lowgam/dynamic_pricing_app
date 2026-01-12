# Module : clear_products.py
# Purpose : clear products table (local DB only)

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.database.queries import clear_products_table
from app.core.utils import ai_logger

router = APIRouter()

@router.post("/admin/clear-products")
def admin_clear_products():
    deleted = clear_products_table()
    ai_logger.warning("[ADMIN] Products table cleared: %s rows", deleted)

    return RedirectResponse(
        url=f"/admin?products_cleared={deleted}",
        status_code=303
    )
