"""
Password hashing and JWT helpers.

This file is scaffolded in Week 1 and implemented in Week 2 (auth module).
Keeping it as a separate module from the start means route handlers never
touch bcrypt or jose directly — they only call these functions.
"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# JWT creation/validation functions are added in Week 2, once the auth
# endpoints are being built — no point defining the token shape before
# we know exactly what claims the frontend needs.
