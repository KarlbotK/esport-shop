from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.common import Result
from app.schemas.user import LoginDTO, RegisterDTO, LoginVO, UserProfileVO
from app.security.dependencies import get_current_user, require_role
from app.services import user_service
from app.utils.ip import get_client_ip

router = APIRouter(prefix="/api/user", tags=["User"])


@router.post("/login")
async def login(
    dto: LoginDTO,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """User login — returns JWT token + role."""
    try:
        ip = get_client_ip(request)
        result = await user_service.login_user(db, dto.username, dto.password, ip)
        return Result.success(LoginVO(**result))
    except ValueError as e:
        return Result.error(str(e))


@router.post("/register")
async def register(
    dto: RegisterDTO,
    db: AsyncSession = Depends(get_db),
):
    """Register a new CUSTOMER user."""
    try:
        user = await user_service.register_user(
            db, dto.username, dto.password, dto.email, dto.phone
        )
        return Result.success({"id": user.id, "username": user.username})
    except ValueError as e:
        return Result.error(str(e))


@router.get("/profile")
async def profile(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user analytics profile."""
    try:
        profile_data = await user_service.get_user_profile(db, current_user["user_id"])
        return Result.success(UserProfileVO(**profile_data))
    except ValueError as e:
        return Result.error(str(e))
