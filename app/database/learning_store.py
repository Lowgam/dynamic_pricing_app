# Module : learning_store.py
# Purpose : managing AI weights (read, snapshot, rollback)

from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta

from app.database.db import get_connection
from app.core.utils.logger import ai_logger

Weights = Dict[str, float]

# --------------------------------------------
# Read current weights from DB
# --------------------------------------------
def load_current_weights() -> Optional[Weights]:
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = "SELECT w_stock, w_mhd, w_velocity, w_base FROM ai_current_weights WHERE id = 1"
        cursor.execute(sql)
        row = cursor.fetchone()

        if not row:
            return None

        return {
            "w_stock": float(row["w_stock"]),
            "w_mhd": float(row["w_mhd"]),
            "w_velocity": float(row["w_velocity"]),
            "w_base": float(row["w_base"]),
        }
    except Exception as ex:
        print(f"[learning_store] Error loading current weights: {ex}")
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --------------------------------------------
# Save a new snapshot and update current weights
# --------------------------------------------
def save_new_weights_snapshot(new_weights: Weights, note: str = None) -> int:
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 1) Insert snapshot for history
        sql_snap = """
        INSERT INTO weights_snapshots (
        created_at,
        w_stock, w_mhd, w_velocity, w_base,
        note
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        values_snap = (
            datetime.now(),
            new_weights.get("w_stock"),
            new_weights.get("w_mhd"),
            new_weights.get("w_velocity"),
            new_weights.get("w_base"),
            note,
        )
        cursor.execute(sql_snap, values_snap)
        snapshot_id = cursor.lastrowid

        # 2) Update ai_current_weights
        sql_update = """
        UPDATE ai_current_weights
        SET w_stock = %s, 
            w_mhd = %s, 
            w_velocity = %s, 
            w_base = %s,
            updated_at = %s
        WHERE id = 1
        """
        values_update = (
            new_weights.get("w_stock"),
            new_weights.get("w_mhd"),
            new_weights.get("w_velocity"),
            new_weights.get("w_base"),
            datetime.now(),
        )
        cursor.execute(sql_update, values_update)
        # Permanently confirms all modifications for INSERT, UPDATE, DELETE
        conn.commit()
        return snapshot_id
    except Exception as ex:
        print(f"[learning_store] Error saving new weights: {ex}")

        if conn:
            conn.rollback()
        return -1 # -1 just a sign for us that something went wrong. It should give us a positive ID (1)


    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --------------------------------------------
# Snapshot list for admin
# --------------------------------------------
def list_snapshots() -> List[Dict]:
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = "SELECT * FROM weights_snapshots ORDER BY created_at DESC"
        cursor.execute(sql)
        ret = cursor.fetchall()
        return ret

    except Exception as ex:
        print(f"[learning_store] Error listing snapshots: {ex}")
        return []

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --------------------------------------------
# Rollback to a snapshot
# --------------------------------------------
def rollback_weights(snapshot_id: int) -> bool:
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql_select = "SELECT * FROM weights_snapshots WHERE id = %s"
        cursor.execute(sql_select, (snapshot_id,))
        selected_snap = cursor.fetchone()
        if not selected_snap:
            print(f"[learning_store] No snapshot with id {snapshot_id}")
            return False

        sql_update = """
                UPDATE ai_current_weights
                SET w_stock = %s, 
                    w_mhd = %s, 
                    w_velocity = %s, 
                    w_base = %s,
                    updated_at = %s
                WHERE id = 1
                """
        values_update = (
            selected_snap.get("w_stock"),
            selected_snap.get("w_mhd"),
            selected_snap.get("w_velocity"),
            selected_snap.get("w_base"),
            datetime.now(),
        )
        cursor.execute(sql_update, values_update)
        conn.commit()
        return True
    except Exception as ex:
        print(f"[learning_store] Error rolling back snapshot: {ex}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --------------------------------------------
# Load information from change price events
# --------------------------------------------
TrainingExample = Dict[str, Any]
def load_closed_change_price_events(start_date: date, end_date:date) -> List[TrainingExample]:

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
        SELECT
            product_id,
            old_price,
            new_price,
            units_before,
            units_after,
            stock_at_close,
            days_to_expiry_at_close,
            velocity_at_close
        FROM change_price_events
        WHERE status = 'CLOSED'
          AND closed_at IS NOT NULL
          AND DATE(changed_at) >= %s
          AND DATE(changed_at) <= %s
        ORDER BY changed_at DESC
        """

        cursor.execute(sql, (start_date, end_date))
        rows = cursor.fetchall()

        examples : List[TrainingExample] = []
        for r in rows:
            if r["units_before"] is None or r["units_after"] is None:
                continue

            examples.append({
                "product_id": int(r["product_id"]),
                "old_price": float(r["old_price"]),
                "new_price": float(r["new_price"]),
                "units_before": int(r["units_before"]),
                "units_after": int(r["units_after"]),
                "stock": int(r.get("stock_at_close") or 0),
                "days_to_expiry": int(r.get("days_to_expiry_at_close") or 0),
                "velocity": float(r.get("velocity_at_close") or 0.0),
            })

        ai_logger.info("[AI TRAINER] Loaded %s training examples from CLOSED events", len(examples))
        return examples

    except Exception as ex:
        ai_logger.error("[AI TRAINER] Failed to load training examples: %s", ex)
        return []

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()