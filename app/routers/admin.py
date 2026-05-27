from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import UmsUser
from app.schemas.common import Result
from app.schemas.__init__ import SalesCreateDTO, SalesCreateVO, SalesUserVO
from app.security.dependencies import require_role
from app.middleware.operation_log import operation_log
from app.services import analytics_service
from app.utils.ip import get_client_ip
import bcrypt

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.post("/sales")
@operation_log("创建销售员")
async def create_sales(
    dto: SalesCreateDTO,
    request: Request = None,
    current_user: dict = Depends(require_role("ADMIN")),
    db: AsyncSession = Depends(get_db),
):
    """Create a salesperson account (ADMIN only)."""
    # Check if username exists
    result = await db.execute(
        select(UmsUser).where(UmsUser.username == dto.username, UmsUser.deleted == 0)
    )
    if result.scalar_one_or_none():
        return Result.error("Username already exists")

    hashed_password = bcrypt.hashpw(dto.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = UmsUser(
        username=dto.username,
        password=hashed_password,
        email=dto.email,
        phone=dto.phone,
        role="SALES",
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return Result.success({"id": user.id, "username": user.username})


@router.delete("/sales/{sales_id}")
@operation_log("删除销售员")
async def delete_sales(
    sales_id: int,
    request: Request = None,
    current_user: dict = Depends(require_role("ADMIN")),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a salesperson (ADMIN only)."""
    result = await db.execute(
        select(UmsUser).where(UmsUser.id == sales_id, UmsUser.deleted == 0, UmsUser.role == "SALES")
    )
    user = result.scalar_one_or_none()
    if not user:
        return Result.error("Salesperson not found", code=404)

    user.deleted = 1
    return Result.success({"id": sales_id})


@router.put("/sales/{sales_id}/pwd")
@operation_log("重置密码")
async def reset_password(
    sales_id: int,
    new_password: str = Query(..., alias="newPassword"),
    request: Request = None,
    current_user: dict = Depends(require_role("ADMIN")),
    db: AsyncSession = Depends(get_db),
):
    """Reset a salesperson's password (ADMIN only)."""
    result = await db.execute(
        select(UmsUser).where(UmsUser.id == sales_id, UmsUser.deleted == 0)
    )
    user = result.scalar_one_or_none()
    if not user:
        return Result.error("User not found", code=404)

    user.password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    return Result.success({"id": sales_id})


@router.get("/reports/sales")
async def sales_report(
    status: int | None = Query(None),
    current_user: dict = Depends(require_role("ADMIN")),
    db: AsyncSession = Depends(get_db),
):
    """Get sales report (ADMIN only)."""
    report = await analytics_service.get_sales_report(db, status)
    return Result.success(report)


@router.get("/reports/ranking")
async def sales_ranking(
    period: str = Query("daily", pattern="^(daily|weekly|monthly)$"),
    current_user: dict = Depends(require_role("ADMIN")),
    db: AsyncSession = Depends(get_db),
):
    """Get sales ranking (ADMIN only)."""
    ranking = await analytics_service.get_sales_ranking(db, period)
    return Result.success(ranking)


@router.get("/reports/trend")
async def sales_trend(
    period: str = Query("daily", pattern="^(daily|weekly|monthly)$"),
    current_user: dict = Depends(require_role("ADMIN")),
    db: AsyncSession = Depends(get_db),
):
    """Get sales trend (ADMIN only)."""
    trend = await analytics_service.get_sales_trend(db, period)
    return Result.success(trend)


@router.get("/reports/anomaly")
async def sales_anomaly(
    current_user: dict = Depends(require_role("ADMIN")),
    db: AsyncSession = Depends(get_db),
):
    """Get anomaly detection report (ADMIN only)."""
    anomaly = await analytics_service.get_anomaly_detection(db)
    return Result.success(anomaly)



