from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.common import Result
from app.schemas.__init__ import SeckillVO
from app.security.dependencies import get_current_user
from app.services import seckill_service

router = APIRouter(prefix="/api/seckill", tags=["Seckill"])


@router.post("/{sku_id}")
async def seckill(
    sku_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Participate in a seckill (flash sale) event."""
    try:
        result = await seckill_service.perform_seckill(db, current_user["user_id"], sku_id)
        return Result.success(SeckillVO(**result))
    except ValueError as e:
        return Result.error(str(e))
