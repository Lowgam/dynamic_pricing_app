# Module: queries.py
# Purpose: define fxs that will be used with MySQL

from db import get_connection, get_dict_cursor
from mysql.connector import Error

# ---------------------------------------------------
# Fx: get all products from DB
# ---------------------------------------------------
def get_all_products():
    try:
        conn = get_connection()
        # Object used in an open SQL session to send commands and receive results. If conn is the door, cursor is the conversation.
        # In this case we use a cursor created in db.py, that is able to return dict
        cursor = get_dict_cursor(conn)
        query = "SELECT * FROM products"
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
# Test for successful queries
# ---------------------------------------------------

if __name__ == "__main__":
    products = get_all_products()
    print("PRODUCTS FOUND:")
    for p in products:
        print(p)

    rules = get_all_rules()
    print("RULES FOUND:")
    for r in rules:
        print(r)