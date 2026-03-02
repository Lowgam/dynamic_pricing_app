# Module : sv_sync.py
# Purpose : update DB tab product with actual stock and velocity.

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse

from app.core.services.inventory_sync import sync_inventory_and_velocity
from app.core.utils import ai_logger
from app.core.utils.auth_guard import require_login
from app.database.queries import get_latest_shopify_connection

router = APIRouter(
    dependencies=[Depends(require_login)]
)

@router.post("/admin/sync-inventory")
async def admin_sv_sync():
    # 1) Read shop_domain and token from DB
    conn = get_latest_shopify_connection()
    if not conn:
        return RedirectResponse(url="/admin?imported=0&error=no_shopify_connection", status_code=303)
    shop_domain = conn["shop_domain"]
    access_token = conn["access_token"]

    try:
        updated = sync_inventory_and_velocity(shop_domain, access_token)
        ai_logger.debug("[ADMIN] Updated stock and velocity: updated=%s", updated)
    except Exception as e:
        return RedirectResponse(url="/admin?sync_inventory=0&error=shopify_fetch_failed", status_code=303)

    return RedirectResponse(url=f"/admin?sync_inventory=ok&updated={updated}", status_code=303)

