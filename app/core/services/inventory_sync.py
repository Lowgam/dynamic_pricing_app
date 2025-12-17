# Module : inventory_sync.py
# Purpose : Synchronise sales_velocity_14d and stock in DB

from typing import List

from app.database.db import get_connection
from app.adapters.shopify.shopify_extractor import fecth_inventory_and_velocity
from app.core.utils import ai_logger

# ----------------------------------------------------------
# SYNC FOR STOCK & VELOCITY
# ----------------------------------------------------------
def sync_inventory_and_velocity(product_ids: List[int] | None = None) -> int:

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # ----------------------------------------------------------
        # 1) Get products from DB (if ids, otherwise all)
        # ----------------------------------------------------------
        if product_ids:
            sql = "SELECT id, shopify_id FROM products WHERE id IN (%s)" % ",".join(["%s"] * len(product_ids))
            cursor.execute(sql, product_ids)
        else:
            sql = "SELECT id, shopify_id FROM products"
            cursor.execute(sql)

        products = cursor.fetchall()
        if not products:
            ai_logger.info("[SYNC] No products found")
            return 0

        shopify_ids = [p["shopify_id"] for p in products]

        # ----------------------------------------------------------
        # 2) Calling extractor
        # ----------------------------------------------------------
        shopify_data = fecth_inventory_and_velocity(shopify_ids)

        # ----------------------------------------------------------
        # 3) Update DB
        # ----------------------------------------------------------
        updated = 0

        for p in products:
            sid = p["shopify_id"]
            data = shopify_data.get(sid)

            if not data:
                continue

            update_sql = """
            UPDATE products
            SET stock = %s,
            sales_velocity_14d = %s
            WHERE id = %s
            """

            cursor.execute(
                update_sql,
                (
                    data["stock"],
                    data["sales_velocity"],
                    p["id"],
                ),
            )
            updated += 1

        conn.commit()
        ai_logger.info("[SYNC] Updated inventory and velocity data for %s products", updated)
        return updated
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()