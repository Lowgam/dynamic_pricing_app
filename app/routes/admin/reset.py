# Module: admin_reset.py
# Purpose: DB reset (tests cleanup + neutral baseline)

from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from app.database.db import get_connection
from app.core.utils.logger import ai_logger

router = APIRouter()

def _column_exists(cursor, table: str, column: str) -> bool:
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
        """,
        (table, column),
    )
    return cursor.fetchone()[0] > 0


@router.post("/admin/reset")
async def admin_reset():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        ai_logger.info("[ADMIN] RESET requested")

        # 1) Truncate tables (cleanup test history)
        cursor.execute("TRUNCATE TABLE weights_snapshots")
        cursor.execute("TRUNCATE TABLE change_price_events")

        # 2) Reset ai_current_weights to baseline 1.0
        # If table is meant to be single-row, enforce that:
        cursor.execute("SELECT COUNT(*) FROM ai_current_weights")
        count = cursor.fetchone()[0]

        if count == 0:
            cursor.execute(
                """
                INSERT INTO ai_current_weights (w_stock, w_mhd, w_velocity, w_base)
                VALUES (1.0, 1.0, 1.0, 1.0)
                """
            )
        else:
            cursor.execute(
                """
                UPDATE ai_current_weights
                SET w_stock = 1.0, w_mhd = 1.0, w_velocity = 1.0, w_base = 1.0
                """
            )

        # 3) Restore product prices to something "decent"
        # Prefer base_price, else original_price, else *1.3
        has_base = _column_exists(cursor, "products", "base_price")
        has_original = _column_exists(cursor, "products", "original_price")

        if has_base:
            cursor.execute(
                """
                UPDATE products
                SET price = CASE
                    WHEN base_price IS NOT NULL THEN base_price
                    ELSE ROUND(price * 1.3, 2)
                END
                """
            )
        elif has_original:
            cursor.execute(
                """
                UPDATE products
                SET price = CASE
                    WHEN original_price IS NOT NULL THEN original_price
                    ELSE ROUND(price * 1.3, 2)
                END
                """
            )
        else:
            cursor.execute(
                """
                UPDATE products
                SET price = ROUND(price * 1.3, 2)
                """
            )

        conn.commit()
        ai_logger.info("[ADMIN] RESET done")
        return RedirectResponse(url="/admin?reset=ok", status_code=303)

    except Exception as ex:
        if conn:
            conn.rollback()
        ai_logger.error("[ADMIN] RESET failed: %s", ex)
        return RedirectResponse(url="/admin?reset=fail", status_code=303)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
