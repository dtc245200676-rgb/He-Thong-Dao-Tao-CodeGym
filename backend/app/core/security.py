import base64
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Iterable

import jwt
from dotenv import load_dotenv
from jwt import ExpiredSignatureError, InvalidTokenError

try:
    import bcrypt  # type: ignore
except ImportError:  # pragma: no cover - local fallback for environments without the wheel
    bcrypt = None

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
SESSION_EXPIRE_MINUTES = int(os.getenv("SESSION_EXPIRE_MINUTES", "60"))
RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", "30"))
ACTIVATION_TOKEN_EXPIRE_HOURS = int(os.getenv("ACTIVATION_TOKEN_EXPIRE_HOURS", "24"))


def utcnow() -> datetime:
    return datetime.utcnow()


def hash_password(password: str) -> str:
    if bcrypt is not None:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # The application normally uses bcrypt. This standards-library fallback only
    # keeps tests/runs possible in minimal environments where bcrypt is unavailable.
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return "$pbkdf2$" + base64.b64encode(salt + digest).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        if hashed_password.startswith("$2") and bcrypt is not None:
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        if hashed_password.startswith("$pbkdf2$"):
            raw = base64.b64decode(hashed_password[len("$pbkdf2$") :])
            salt, expected = raw[:16], raw[16:]
            actual = hashlib.pbkdf2_hmac("sha256", plain_password.encode(), salt, 310_000)
            return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False
    return False


def validate_password(password: str) -> None:
    if len(password) < 8 or not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
        raise ValueError("Mật khẩu phải có ít nhất 8 ký tự, bao gồm chữ và số.")


def create_access_token(user_id: int, session_id: str, roles: Iterable[str]) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "sid": session_id,
        "roles": list(roles),
        "type": "access",
        "iat": datetime.now(timezone.utc),
        "exp": expires_at,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


def decode_access_token(token: str, *, verify_exp: bool = True) -> dict:
    try:
        return jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[ALGORITHM],
            options={"verify_exp": verify_exp},
        )
    except ExpiredSignatureError as exc:
        raise ValueError("TOKEN_EXPIRED") from exc
    except InvalidTokenError as exc:
        raise ValueError("TOKEN_INVALID") from exc


def generate_one_time_token() -> str:
    return secrets.token_urlsafe(32)


def hash_one_time_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_temporary_password() -> str:
    # Guaranteed letter + digit and long enough for Sprint 1 policy.
    return f"Tmp{secrets.randbelow(900000) + 100000}{secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}"
