from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings


def create_access_token(user_id: int, username: str, role: str) -> str:
    """Create a JWT access token with HMAC-SHA256."""
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expiry_hours),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_access_token(token: str) -> dict | None:
    """Decode and verify a JWT token. Returns payload dict or None if invalid."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
