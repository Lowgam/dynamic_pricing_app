# Module : security.py
# Purpose : Hash and verify passwords

# Cryptcontext manages hashing algorithms. It knows how to hash, how to verify them and choose the algor.
from passlib.context import CryptContext

# We choose here the hashing system we want to use: bcrypt is the algorithm name.
# If bcrypt becomes old, passlib can verify old hash and regenerate them with a new algorithm.
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

# FX to hash a password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# .verify compares input password, understanding which hash was used, with hashed psw in DB
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

