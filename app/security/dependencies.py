from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> dict:
    """FastAPI dependency that extracts and validates the JWT from the Authorization header.

    Returns a dict with sub (user_id), username, role if valid.
    Raises 401 if missing or invalid.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token",
        )
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return {
        "user_id": int(payload["sub"]),
        "username": payload.get("username", ""),
        "role": payload.get("role", "CUSTOMER"),
    }


async def get_optional_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> dict | None:
    """FastAPI dependency like get_current_user but returns None instead of raising 401."""
    if credentials is None:
        return None
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        return None
    return {
        "user_id": int(payload["sub"]),
        "username": payload.get("username", ""),
        "role": payload.get("role", "CUSTOMER"),
    }


def require_role(required_role: str):
    """Factory that returns a dependency that requires a specific role.

    Usage:
        @router.get("/admin/reports")
        async def reports(user: dict = Depends(require_role("ADMIN"))):
            ...
    """
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["role"] != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role} role",
            )
        return current_user
    return role_checker
