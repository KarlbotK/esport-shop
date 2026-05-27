from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.category import PmsCategory
from app.models.brand import PmsBrand
from app.schemas.common import Result
from app.schemas.__init__ import CategoryVO, BrandVO

router = APIRouter(prefix="/api/category", tags=["Category"])


@router.get("/list")
async def category_list(
    db: AsyncSession = Depends(get_db),
):
    """Get all categories."""
    result = await db.execute(
        select(PmsCategory).where(PmsCategory.deleted == 0).order_by(PmsCategory.sort)
    )
    categories = result.scalars().all()
    return Result.success([
        CategoryVO(id=c.id, name=c.name, parent_id=c.parent_id, sort=c.sort)
        for c in categories
    ])


@router.get("/brands")
async def brand_list(
    db: AsyncSession = Depends(get_db),
):
    """Get all brands."""
    result = await db.execute(
        select(PmsBrand).where(PmsBrand.deleted == 0)
    )
    brands = result.scalars().all()
    return Result.success([
        BrandVO(id=b.id, name=b.name, logo_url=b.logo_url, description=b.description)
        for b in brands
    ])
