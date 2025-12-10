# Module : admin.py
# Purpose : admin endpoints for inspecting AI weight snapshots

from fastapi import APIRouter
from app.database.learning_store import list_snapshots
from app.utils.logger import ai_logger

router = APIRouter()


@router.get("/admin")
def admin_weights():
    snapshots = list_snapshots() or []
    ai_logger.info("[ADMIN] Loaded %s snapshots", len(snapshots))
    return {"snapshots": snapshots}
