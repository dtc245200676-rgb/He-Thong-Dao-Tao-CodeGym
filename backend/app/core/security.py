import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv(
    "JWT_SECRET",
    "change-me"
)

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "60"
    )
)

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

    return hashed.decode("utf-8")


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def create_access_token(
    user_id: int,
    email: str,
    role: str
) -> str:

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "exp": expires_at
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=ALGORITHM
    )