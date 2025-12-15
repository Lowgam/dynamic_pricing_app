# Module : sync.py
# Purpose : Close events open from 7 days

from fastapi import APIRouter
from fastapi.responses import  RedirectResponse
from app.database.db import get_connection

router = APIRouter()

# ---------------------------------------------------
# FX: Close OPEN events if days >= 7
# ---------------------------------------------------
@router.post("/admin/sync")
async def admin_sync(days: int = 7):
    if days < 1:
        days = 1

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Close events older than 7 days and saves
        sql = """
        UPDATE change_price_events e
        JOIN products p ON p.id = e.product_id
        SET
            e.status = 'CLOSED',
            e.closed_at = NOW(),
            e.window_days = DATEDIFF(NOW(), e.changed_at),
            e.stock_at_close = p.stock,
            e.days_to_expiry_at_close = DATEDIFF(p.expiry_date, NOW()),
            e.velocity_at_close = 0
        WHERE e.status = 'OPEN'
          AND e.changed_at <= DATE_SUB(NOW(), INTERVAL %s DAY)
        """
        cursor.execute(sql, (days,))
        conn.commit()

        closed_count = cursor.rowcount
        return RedirectResponse(url=f"/admin?sync=ok&closed={closed_count}&days={days}", status_code=303)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
