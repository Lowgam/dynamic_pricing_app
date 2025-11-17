# Module: db.py
# Purpose: connection manager for dynamic_pricing_DB

import mysql.connector
from mysql.connector import Error

#Dictionary: contains couples keys values. Here contains all the info needed to connect with the DB
#host: where it is, port: service door (3306 predefined for mySQL, user: what will be used to connect #password: psw, database: name of DB
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "nico",
    "password": " xxx ",
    "database": "dynamic_pricing",
}

def get_connection():
    try:
        #conn here is a mysql.connector.MySQLConnection object used to manage the connection. It opens the DB door. You get a message only in case of failed connection.
        #calling method of library mysql.connector.connect with the info of DB_CCONFIG/ **: Fundamental in py, we can pass the entire dict just with **
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Connection with DB failed:  {e}")
        raise