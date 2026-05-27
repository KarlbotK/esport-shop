from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.common import Result, PageResult
from app.schemas.spu import SpuDetailVO, HotProductVO
from app.services import spu_service

router = APIRouter(prefix="/api/spu", tags=["SPU"])


@router.get("/list")
async def spu_list(
    category_id: int | None = Query(None, alias="categoryId"),
    brand_id: int | None = Query(None, alias="brandId"),
    keyword: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Paginated SPU list with optional filters."""
    result = await spu_service.get_spu_list(db, category_id, brand_id, keyword, page, size)
    return Result.success(PageResult(**result))


@router.get("/detail/{spu_id}")
async def spu_detail(
    spu_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get SPU detail with SKU list."""
    result = await spu_service.get_spu_detail(db, spu_id)
    if result is None:
        return Result.error("SPU not found", code=404)
    return Result.success(SpuDetailVO(**result))


@router.get("/hot")
async def spu_hot(
    category_id: int | None = Query(None, alias="categoryId"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Hot products ranked by browse frequency."""
    products = await spu_service.get_hot_products(db, category_id, limit)
    return Result.success([HotProductVO(**p) for p in products])


@router.get("/similar/{spu_id}")
async def spu_similar(
    spu_id: int,
    db: AsyncSession = Depends(get_db),
):
    """"Also viewed" products."""
    products = await spu_service.get_similar_products(db, spu_id)
    return Result.success(products)


@router.get("/collaborative/{spu_id}")
async def spu_collaborative(
    spu_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Collaborative filtering recommendations."""
    products = await spu_service.get_collaborative_products(db, spu_id)
    return Result.success(products)
