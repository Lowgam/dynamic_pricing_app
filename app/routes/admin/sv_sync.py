# Module : sv_sync.py
# Purpose : update DB tab product with actual stock and velocity.

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse

from app.core.services.inventory_sync import sync_inventory_and_velocity
from app.core.utils import ai_logger
from app.core.utils.auth_guard import require_login

router = APIRouter(
    dependencies=[Depends(require_login)]
)

@router.post("/admin/sync-inventory")
async def admin_sv_sync():
    updated = sync_inventory_and_velocity()
    ai_logger.debug("[ADMIN] Updated stock and velocity: updated=%s", updated)
    return RedirectResponse(url=f"/admin?sync_inventory=ok&updated={updated}", status_code=303)

