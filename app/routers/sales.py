from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.category import PmsCategory
from app.models.spu import PmsSpu
from app.models.sku import PmsSku
from app.schemas.common import Result, PageResult
from app.schemas.__init__ import (
    SpuCreateDTO, SpuUpdateDTO, CategoryCreateDTO,
    BrowseLogVO, DashboardVO, CategoryVO,
)
from app.schemas.spu import SpuListVO
from app.security.dependencies import require_role
from app.middleware.operation_log import operation_log
from app.services import spu_service, browse_log_service
from app.utils.ip import get_client_ip

router = APIRouter(prefix="/api/sales", tags=["Sales"])


@router.post("/spu")
@operation_log("添加商品")
async def add_spu(
    dto: SpuCreateDTO,
    request: Request = None,
    current_user: dict = Depends(require_role("SALES")),
    db: AsyncSession = Depends(get_db),
):
    """Add a new SPU (SALES only)."""
    spu = PmsSpu(
        name=dto.name,
        category_id=dto.category_id,
        brand_id=dto.brand_id,
        description=dto.description,
        publish_status=dto.publish_status,
    )
    db.add(spu)
    await db.flush()
    await db.refresh(spu)
    return Result.success({"id": spu.id, "name": spu.name})


@router.put("/spu/{spu_id}")
@operation_log("修改商品")
async def update_spu(
    spu_id: int,
    dto: SpuUpdateDTO,
    request: Request = None,
    current_user: dict = Depends(require_role("SALES")),
    db: AsyncSession = Depends(get_db),
):
    """Update an SPU (SALES only)."""
    result = await db.execute(
        select(PmsSpu).where(PmsSpu.id == spu_id, PmsSpu.deleted == 0)
    )
    spu = result.scalar_one_or_none()
    if not spu:
        return Result.error("SPU not found", code=404)

    spu.name = dto.name
    spu.category_id = dto.category_id
    spu.brand_id = dto.brand_id
    spu.description = dto.description
    spu.publish_status = dto.publish_status
    return Result.success({"id": spu.id, "name": spu.name})


@router.delete("/spu/{spu_id}")
@operation_log("删除商品")
async def delete_spu(
    spu_id: int,
    request: Request = None,
    current_user: dict = Depends(require_role("SALES")),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete an SPU (SALES only)."""
    result = await db.execute(
        select(PmsSpu).where(PmsSpu.id == spu_id, PmsSpu.deleted == 0)
    )
    spu = result.scalar_one_or_none()
    if not spu:
        return Result.error("SPU not found", code=404)
    spu.deleted = 1
    return Result.success({"id": spu.id})


@router.put("/sku/{sku_id}/stock")
@operation_log("修改库存")
async def update_sku_stock(
    sku_id: int,
    stock: int = Query(..., ge=0),
    request: Request = None,
    current_user: dict = Depends(require_role("SALES")),
    db: AsyncSession = Depends(get_db),
):
    """Update SKU stock (SALES only)."""
    result = await db.execute(
        select(PmsSku).where(PmsSku.id == sku_id, PmsSku.deleted == 0)
    )
    sku = result.scalar_one_or_none()
    if not sku:
        return Result.error("SKU not found", code=404)

    sku.stock = stock
    return Result.success({"id": sku.id, "stock": sku.stock})


@router.post("/category")
@operation_log("添加分类")
async def add_category(
    dto: CategoryCreateDTO,
    request: Request = None,
    current_user: dict = Depends(require_role("SALES")),
    db: AsyncSession = Depends(get_db),
):
    """Add a new category (SALES only)."""
    category = PmsCategory(
        name=dto.name,
        parent_id=dto.parent_id,
        sort=dto.sort,
    )
    db.add(category)
    await db.flush()
    await db.refresh(category)
    return Result.success({"id": category.id, "name": category.name})


@router.delete("/category/{category_id}")
@operation_log("删除分类")
async def delete_category(
    category_id: int,
    request: Request = None,
    current_user: dict = Depends(require_role("SALES")),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a category (SALES only)."""
    result = await db.execute(
        select(PmsCategory).where(PmsCategory.id == category_id, PmsCategory.deleted == 0)
    )
    category = result.scalar_one_or_none()
    if not category:
        return Result.error("Category not found", code=404)

    category.deleted = 1
    return Result.success({"id": category.id})


@router.get("/browse-logs")
async def browse_logs(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(require_role("SALES")),
    db: AsyncSession = Depends(get_db),
):
    """Get paginated browse logs (SALES only)."""
    result = await browse_log_service.get_browse_logs(db, page, size)
    return Result.success(PageResult(**result))


@router.get("/dashboard")
async def dashboard(
    current_user: dict = Depends(require_role("SALES")),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard statistics (SALES only)."""
    stats = await browse_log_service.get_dashboard_stats(db)
    return Result.success(DashboardVO(**stats))
