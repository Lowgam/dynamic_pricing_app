# scripts/fulfill_db_to_test.py
# Purpose: seed change_price_events with valid CLOSED events for AI training

import random
from datetime import datetime, timedelta

from app.database.db import get_connection

NUM_EVENTS = 30
WINDOW_DAYS = 7


def _get_existing_product_ids(cursor, limit=50):
    cursor.execute("SELECT id FROM products ORDER BY id LIMIT %s", (limit,))
    rows = cursor.fetchall()
    return [r[0] for r in rows]


def seed_events():
    conn = get_connection()
    cursor = conn.cursor()

    product_ids = _get_existing_product_ids(cursor, limit=200)

    if not product_ids:
        raise RuntimeError("No products found in DB. Insert products first, then seed events.")

    now = datetime.now()

    for _ in range(NUM_EVENTS):
        product_id = random.choice(product_ids)

        changed_at = now - timedelta(days=random.randint(10, 40))
        closed_at = changed_at + timedelta(days=WINDOW_DAYS)

        old_price = round(random.uniform(1.5, 5.0), 2)
        new_price = round(old_price * random.uniform(0.7, 0.95), 2)

        units_before = random.randint(50, 200)
        units_after = max(units_before - random.randint(5, 40), 0)

        stock_at_close = units_after
        velocity_at_close = round(random.uniform(0.2, 2.5), 2)
        days_to_expiry_at_close = random.randint(1, 20)

        sql = """
        INSERT INTO change_price_events (
            product_id,
            old_price,
            new_price,
            units_before,
            units_after,
            stock_at_close,
            velocity_at_close,
            days_to_expiry_at_close,
            status,
            changed_at,
            closed_at,
            window_days
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'CLOSED', %s, %s, %s)
        """

        cursor.execute(
            sql,
            (
                product_id,
                old_price,
                new_price,
                units_before,
                units_after,
                stock_at_close,
                velocity_at_close,
                days_to_expiry_at_close,
                changed_at,
                closed_at,
                WINDOW_DAYS,
            ),
        )

    conn.commit()
    cursor.close()
    conn.close()

    print(f"[SEED] Inserted {NUM_EVENTS} CLOSED change_price_events using {len(product_ids)} real products.")


if __name__ == "__main__":
    seed_events()

