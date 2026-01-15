from app.database.queries import create_user, delete_user_by_id
from app.core.utils.security import hash_password

def register_user(username: str, password: str, role: str = "user"):
    password_hash = hash_password(password)
    create_user(username, password_hash, role)

def delete_user(user_id: int):
    delete_user_by_id(user_id)