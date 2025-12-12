# Module : sync.py
# Purpose : Close events open from 7 days

from fastapi import APIRouter
from fastapi.responses import  RedirectResponse
from app.database.db import get_connection

router = APIRouter()

@router.post("/admin/sync")
async def admin_sync(days: int = 7):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Chiude eventi OPEN più vecchi di N giorni
        sql = """
        UPDATE change_price_events
        SET status='CLOSED',
            closed_at=NOW(),
            window_days=%s
        WHERE status='OPEN'
          AND changed_at <= DATE_SUB(NOW(), INTERVAL %s DAY)
        """
        cursor.execute(sql, (days,days))
        conn.commit()

        closed_count = cursor.rowcount
        return RedirectResponse(url=f"/admin?sync=ok&closed={closed_count}&days={days}", status_code=303)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
