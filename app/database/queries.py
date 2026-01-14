# Module: queries.py
# Purpose: define fxs that will be used with MySQL

from .db import get_connection, get_dict_cursor
from mysql.connector import Error
from typing import List, Optional, Set

# ---------------------------------------------------
# Fx: get all products from DB
# ---------------------------------------------------
def get_all_products():
    try:
        conn = get_connection()
        # Object used in an open SQL session to send commands and receive results. If conn is the door, cursor is the conversation.
        # In this case we use a cursor created in db.py, that is able to return dict
        cursor = get_dict_cursor(conn)
        query = "SELECT * FROM products WHERE status = 'active'"
        cursor.execute(query)
        # fetchall() = give me all the results you found. rows become a tuple list
        rows = cursor.fetchall()
        # You always have to close the connection in order to do not overload the server.
        cursor.close()
        conn.close()
        return rows

    except Error as e:
        print(f"Error during query get_all_products: {e}")
        return None

# ---------------------------------------------------
# Fx: get all rules from DB
# ---------------------------------------------------
def get_all_rules():
    try:
        conn = get_connection()
        cursor = get_dict_cursor(conn)
        query = "SELECT * FROM pricing_rules"
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    except Error as e:
        print(f"Error during query get_all_rules: {e}")
        return None

# ---------------------------------------------------
# Fx: insert products in DB
# ---------------------------------------------------
def insert_product(product: dict):
    # Here we add the following two lines as a security net in case of error. We are exiting anyway the connection at the end, but if conn and cursor
    # are not defined before any error could happen, we would execute the finally anyway, trying to close objects that are not created yet.
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # """ Allow us to use more lines for a str
        # Here placeholders are created
        sql_insert = """INSERT INTO products (shopify_id, sku, name, price, stock, category, expiry_date, sales_velocity_14d)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        # product is a dict, we are preparing how we want the values of real products to be passed to our function curso.execute
        # Here we use tuple (unchangeable)
        values = (
            product.get("shopify_id"),
            product.get("sku"),
            product.get("name"),
            product.get("price"),
            product.get("stock"),
            product.get("category"),
            product.get("expiry_date"),
            product.get("sales_velocity_14d"),
        )
        cursor.execute(sql_insert, values)
        # commit necessary when we modify the DB. The other queries I wrote earlier (SELECT) just wanted to fetch some datas
        conn.commit()

    except Error as e:
        print(f"Error during query insert_products: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ---------------------------------------------------
# Repeater for insert_products
# ---------------------------------------------------
def import_mock_products(products: list):
    for p in products:
        insert_product(p)

# ---------------------------------------------------
# Fx: update products
# ---------------------------------------------------
def update_product(product_id: int, new_price: float):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sqp_update = """
        UPDATE products 
        SET price = %s
        WHERE id = %s
        """
        cursor.execute(sqp_update, (new_price, product_id))
        conn.commit()

    except Error as e:
        print(f"Error during query update_product: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
                conn.close()

# ---------------------------------------------------
# Fx: get products by id
# ---------------------------------------------------
def get_products_by_ids(ids: List[int]):
    if not ids:
        return []

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Heart of this function. The following query needs holes as many are the ids entering as parameters
        # placeholders basically creates a string with %s (placeholders).
        # I do not want to insert the ids directly in SQL string. We will attach them later with cursor.execute.
        # Why? To avoid SQL injections.
        placeholders = ",".join(["%s"] * len(ids))
        sql = f"SELECT * FROM products WHERE id IN ({placeholders})"

        cursor.execute(sql, ids)
        rows = cursor.fetchall()
        return rows

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ---------------------------------------------------
# Test for successful SELECT
# ---------------------------------------------------
# if __name__ == "__main__":
    products = get_all_products()
    print("PRODUCTS FOUND:")
    for p in products:
        print(p)

    rules = get_all_rules()
    print("RULES FOUND:")
    for r in rules:
        print(r)

# ---------------------------------------------------
# Test for successful UPDATE
# ---------------------------------------------------
#if __name__ == "__main__":
#    update_product(1, 1.59)
#    print("Test Update completed")

# ---------------------------------------------------
# Test for successful get_all_products
# ---------------------------------------------------
# if __name__ == "__main__":
    from pprint import pprint
    rows = get_all_products()
    print("TEST get_all_products():")
    pprint(rows)

# ---------------------------------------------------
# Fx: insert change in price events
# ---------------------------------------------------
def insert_change_price_event(
        product_id: int,
        old_price: float,
        new_price: float,
        source: str = "dashboard",
        weights_snapshot_id: Optional[int] = None
):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # 0) Read current stock
        cursor.execute("SELECT stock FROM products WHERE id = %s", (product_id,))
        row = cursor.fetchone()
        units_before = int((row or {}).get("stock") or 0)

        # 1) Control : if there is an OPEN product with the same id, close it
        sql_search = """
            SELECT id, changed_at
            FROM change_price_events
            WHERE product_id = %s AND status = 'OPEN'
            ORDER BY changed_at DESC
            LIMIT 1
            """
        cursor.execute(sql_search, (product_id,))
        existing = cursor.fetchone()

        if existing:
            sql_close_event = """
                UPDATE change_price_events
                SET status = 'CLOSED',
                    closed_at = NOW(),
                    window_days = DATEDIFF(NOW(), changed_at)
                WHERE id = %s
                """
            cursor.execute(sql_close_event, (existing["id"],))


        # 2) Create new event
        sql_insert = """
        INSERT INTO change_price_events
        (
        product_id,
        old_price,
        new_price,
        source,
        status,
        weights_snapshot_id,
        units_before
        )
        VALUES (%s, %s, %s, %s, 'OPEN', %s, %s)
        """

        cursor.execute(
            sql_insert,
            (
                product_id,
                old_price,
                new_price,
                source,
                weights_snapshot_id,
                units_before,
            )
        )

        conn.commit()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ---------------------------------------------------
# Fx: get existing products from DB
# ---------------------------------------------------
def get_existing_product_id() -> Set[int]:
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
        SELECT shopify_id 
        FROM products
        WHERE shopify_id IS NOT NULL
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        return {int(r[0]) for r in rows if r and r[0] is not None}

    except Error as e:
        print(f"Error during query get_existing_product_id: {e}")
        return set()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ---------------------------------------------------
# Fx: clear products table
# ---------------------------------------------------
def clear_products_table() -> int:
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM products")
        cursor.execute("ALTER TABLE products AUTO_INCREMENT = 1")
        deleted = cursor.rowcount

        conn.commit()
        return deleted

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ---------------------------------------------------
# Fx: get user by name
# ---------------------------------------------------
def get_user_by_username(username: str):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
        SELECT id, username, password_hash, role
        FROM users
        WHERE username = %s AND is_active = 1
        """
        cursor.execute(sql, (username,))
        return cursor.fetchone()

    except Error as e:
        print(f"Error during query get_user_by_name: {e}")
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()