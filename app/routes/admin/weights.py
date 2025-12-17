# Module : weights.py
# Purpose : admin endpoints for inspecting AI weight snapshots

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.database.learning_store import (
    list_snapshots,
    load_current_weights,
    rollback_weights
)
from app.core.utils import ai_logger

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/admin/weights")
def admin_weights(request: Request):
    snapshots = list_snapshots() or []
    current_weights = load_current_weights() or None

    # Shortcut for if else. Basically if the four things are equal to what follows, then s is current, otherwise no
    if current_weights:
        # We can add a key to the DICT, where the value of the four conditions is true. The added value can be used
        # by HTML template to get the only right value.
        for s in snapshots:
            s["is_current"] = (
                s.get("w_stock") == current_weights["w_stock"]
                and s.get("w_mhd") == current_weights["w_mhd"]
                and s.get("w_velocity") == current_weights["w_velocity"]
                and s.get("w_base") == current_weights["w_base"]
            )
    else:
        for s in snapshots:
            s["is_current"] = False

        ai_logger.info(
            "[ADMIN] Loaded %s snapshots (current weights present: %s)",
            len(snapshots),
            bool(current_weights),
        )

    return templates.TemplateResponse(
        "admin_weights_list.html",
        {
            "request": request,
            "snapshots": snapshots,
            "current_weights": current_weights,
        }
    )

@router.get("/admin/weights/{snapshot_id}", response_class=HTMLResponse)
def admin_weights_list(snapshot_id: int, request: Request):
    snapshots = list_snapshots() or []
    snapshot = next((s for s in snapshots if s.get("id") == snapshot_id), None)

    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")

    current_weights = load_current_weights() or None

    is_current = False
    if current_weights:
        is_current = (
                snapshot.get("w_stock") == current_weights.get("w_stock")
                and snapshot.get("w_mhd") == current_weights.get("w_mhd")
                and snapshot.get("w_velocity") == current_weights.get("w_velocity")
                and snapshot.get("w_base") == current_weights.get("w_base")
        )

    return templates.TemplateResponse(
        "admin_weights_detail.html",
        {
            "request": request,
            "snapshot": snapshot,
            "current_weights": current_weights,
            "is_current": is_current,
        },
    )

@router.post("/admin/weights/{snapshot_id}/rollback")
def admin_weights_rollback(snapshot_id: int, request: Request):
    ai_logger.info("[ADMIN] Rollback requested for snapshot id=%s", snapshot_id)

    try:
        rollback_weights(snapshot_id)
    except Exception as ex:
        ai_logger.error("[ADMIN] Rollback failed for snapshot id=%s: %s", snapshot_id, ex)
        raise HTTPException(status_code=500, detail="Rollback non riuscito")

    ai_logger.info("[ADMIN] Rollback DONE for snapshot id=%s", snapshot_id)

    return RedirectResponse(url="/admin/weights?rollback=success", status_code=303)
