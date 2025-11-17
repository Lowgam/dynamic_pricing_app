# Module: queries.py
# Purpose: define fxs that will be used with MySQL

from .db import get_connection
from mysql.connector import Error

# ---------------------------------------------------
# Fx: get all products from DB
# ---------------------------------------------------
def get_all_products():
    try:
        conn = get_connection()
        # Object used in an open SQL session to send commands and receive results. If conn is the door, cursor is the conversation.
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, current_price, expiration_date, category, stock FROM products")
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
        cursor = conn.cursor()
        cursor.execute("SELECT id, rule_name, factor_a, factor_b, threshold, active FROM pricing_rules")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

    except Error as e:
        print(f"Error during query get_all_rules: {e}")
        return None