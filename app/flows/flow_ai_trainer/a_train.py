# Module : a_train.py
# Purpose : endpoint for admin to start training sessions

from fastapi import APIRouter, Form, Depends
from fastapi.responses import RedirectResponse

from app.flows.flow_ai_trainer.b_ai_trainer import train_once
from app.core.utils import ai_logger
from app.core.utils.auth_guard import require_login, require_role

router = APIRouter(
    dependencies=[Depends(require_role("admin"))]
)

@router.post("/admin/train")
async def admin_train(lookback_days: int = Form(14)):
    ai_logger.info("[ADMIN] Train requested (lookback_days=%s)", lookback_days)

    try:
        result = train_once(lookback_days=lookback_days)
    except TypeError:
        # fallback
        result = train_once()
    except Exception as ex:
        ai_logger.error("[ADMIN] Train failed: %s", ex)
        return RedirectResponse(url="/admin?train=error", status_code=303)

    # For safety issues (train_once can return a DICT or None)
    examples_used = 0
    snapshot_id = ""

    # isinstance: py basic function. Controls the type of a variable
    if isinstance(result, dict):
        examples_used = int(result.get("num_examples", 0) or 0 )
        snapshot_id = result.get("snapshot_id", "") or ""

    if examples_used == 0:
        ai_logger.warning("[ADMIN] Train skipped: no CLOSED events available")

        return RedirectResponse(
            url="/admin?train=skipped&msg=no_closed_events",
            status_code=303
        )

    ai_logger.info(
        "[ADMIN] Train DONE (examples=%s, snapshot=%s)",
        examples_used, snapshot_id
    )

    return RedirectResponse(
        url=f"/admin?train=ok&examples={examples_used}&snapshot={snapshot_id}",
        status_code=303
    )