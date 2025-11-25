# Module: db.py
# Purpose: connection manager for dynamic_pricing_DB

import mysql.connector
from mysql.connector import Error

#Dictionary: contains couples keys values. Here contains all the info needed to connect with the DB
#host: where it is, port: service door (3306 predefined for mySQL, user: what will be used to connect #password: psw, database: name of DB
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "PavardAcerbiDevrijBastoni20",
    "database": "dynamic_pricing_app",
}
# ---------------------------------------------------
# Fx: Open a connection with DB
# ---------------------------------------------------
def get_connection():
    try:
        #conn here is a mysql.connector.MySQLConnection object used to manage the connection. It opens the DB door. You get a message only in case of failed connection.
        #calling method of library mysql.connector.connect with the info of DB_CCONFIG/ **: Fundamental in py, we can pass the entire dict just with **
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Connection with DB failed:  {e}")
        raise

# Cursor generators. They will be used in queries.py to return tuples or dictionaries.
# They have conn as parameter because they need to know from which connection is the command arriving. A cursor needs to be linked with the connection

# ---------------------------------------------------
# Fx: Get cursor from a connection with DB
# ---------------------------------------------------
def get_cursor(conn):
    return conn.cursor()

# ---------------------------------------------------
# Fx: Get a specific cursor for DICT
# ---------------------------------------------------
def get_dict_cursor(conn):
    return conn.cursor(dictionary=True)


# ---------------------------------------------------
# ------------------- TESTING -----------------------
# ---------------------------------------------------

# Py assign every file if directly executed or imported (undirectly executed) a __name__
# Here down means: if I directly launched db.py as main (py assign automatically __main__ as __name__ if the file is directly launched), then do this test.
# NB!!!! Py can be launched from every file, a main as Java is not needed.
if __name__ == "__main__":
    conn = get_connection()
    if conn is not None and conn.is_connected():
        print("Connected to MySQL database")
        conn.close()
    else:
        print("Failed to connect to MySQL database")