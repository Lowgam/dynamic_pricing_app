from app.database.db import get_connection
from app.core.utils.security import hash_password

USERNAME = "admin_dev"
PASSWORD = "4"
ROLE = "admin"

conn = None
cursor = None

try:
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO users (username, password_hash, role)
    VALUES (%s, %s, %s)
    """
    cursor.execute(
        sql,
        (USERNAME, hash_password(PASSWORD), ROLE)
    )

    conn.commit()
    print(" Admin user created successfully")

except Exception as e:
    print(f" Error creating admin user: {e}")

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
