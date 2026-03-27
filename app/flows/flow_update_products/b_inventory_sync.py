# Module : b_inventory_sync.py
# Purpose : PIPELINE. Synchronise sales_velocity_14d and stock in DB

from typing import List

from app.database.db import get_connection
from app.flows.flow_update_products.ca_shopify_extractor import fecth_inventory_and_velocity
from app.core.utils import ai_logger
from app.flows.flow_update_products.cb_velocity_service import calculate_sales_velocity

# ----------------------------------------------------------
# SYNC FOR STOCK & VELOCITY
# ----------------------------------------------------------
def sync_inventory_and_velocity(shop_domain: str, access_token: str, product_ids: List[int] | None = None) -> int:

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # ----------------------------------------------------------
        # 1) Get products from DB (if ids, otherwise all)
        # ----------------------------------------------------------
        if product_ids:
            sql = "SELECT id, shopify_id, price FROM products WHERE id IN (%s)" % ",".join(["%s"] * len(product_ids))
            cursor.execute(sql, product_ids)
        else:
            sql = "SELECT id, shopify_id, price FROM products"
            cursor.execute(sql)

        products = cursor.fetchall()
        if not products:
            ai_logger.info("[SYNC] No products found")
            return 0

        shopify_ids = [p["shopify_id"] for p in products]

        # ----------------------------------------------------------
        # 2.1) Calling extractor
        # ----------------------------------------------------------
        shopify_data = fecth_inventory_and_velocity(
            shop_domain,
            access_token,
            shopify_ids,
        )

        # ----------------------------------------------------------
        # 2.2) Calling velocity_service
        # ----------------------------------------------------------
        velocity_map = calculate_sales_velocity(
            shop_domain,
            access_token,
            shopify_ids,
        )

        # ----------------------------------------------------------
        # 3) Price check & Update DB
        # ----------------------------------------------------------
        updated = 0

        for p in products:
            product_id = p["id"]
            sid = p["shopify_id"]
            db_price = float(p["price"])

            data = shopify_data.get(sid)
            if not data:
                print("MISSING FROM SHOPIFY:", sid)
                update_sql = """
                        UPDATE products
                        SET status = 'inactive'
                        WHERE id = %s
                    """
                cursor.execute(update_sql, (product_id,))
                continue

            shopify_price = float(data.get("price", db_price))
            velocity = velocity_map.get(sid, 0)

            # ------------------------------------------------------
            # Price control with open event check
            # ------------------------------------------------------
            update_price = False

            if shopify_price != db_price:
                sql_price_check = """
                SELECT 1
                FROM change_price_events
                WHERE product_id = %s
                AND status = 'OPEN'
                LIMIT 1
                """
                cursor.execute(sql_price_check, (product_id,))
                open_event = cursor.fetchone()

                if not open_event:
                    update_price = True
                else:
                    ai_logger.warning(
                        "[SYNC] External price change detected during OPEN event | product_id=%s | shopify_price=%s | db_price=%s",
                        product_id,
                        shopify_price,
                        db_price
                    )

            # ------------------------------------------------------
            # Update query
            # ------------------------------------------------------
            if update_price:
                update_sql = """
                            UPDATE products
                            SET price = %s,
                            stock = %s,
                            sales_velocity_14d = %s,
                            status = %s
                            WHERE id = %s
                            """

                cursor.execute(
                    update_sql,
                    (
                        shopify_price,
                        data["stock"],
                        velocity,
                        "active",
                        p["id"],
                    ),
                )
            else:
                update_sql = """
                            UPDATE products
                            SET stock = %s,
                            sales_velocity_14d = %s,
                            status = %s
                            WHERE id = %s
                            """
                cursor.execute(
                    update_sql,
                    (
                        data["stock"],
                        velocity,
                        "active",
                        product_id,
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