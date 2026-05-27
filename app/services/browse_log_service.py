from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.browse_log import PmsBrowseLog
from app.models.spu import PmsSpu
from app.models.sku import PmsSku


async def get_browse_logs(
    db: AsyncSession,
    page: int = 1,
    size: int = 20,
) -> dict:
    """Get paginated browse logs."""
    count_query = select(func.count(PmsBrowseLog.id))
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = (
        select(PmsBrowseLog, PmsSpu.name.label("spu_name"))
        .outerjoin(PmsSpu, PmsBrowseLog.spu_id == PmsSpu.id)
        .order_by(desc(PmsBrowseLog.create_time))
        .offset((page - 1) * size)
        .limit(size)
    )
    result = await db.execute(query)
    rows = result.all()

    records = []
    for log, spu_name in rows:
        records.append({
            "id": log.id,
            "userId": log.user_id,
            "spuId": log.spu_id,
            "spuName": spu_name or "",
            "durationSeconds": log.duration_seconds,
            "ipAddress": log.ip_address,
            "createTime": log.create_time.isoformat() if log.create_time else None,
        })

    return {
        "records": records,
        "total": total,
        "size": size,
        "current": page,
        "pages": (total + size - 1) // size if total > 0 else 0,
    }


async def get_dashboard_stats(db: AsyncSession) -> dict:
    """Get dashboard statistics for sales."""
    # SPU count
    spu_result = await db.execute(
        select(func.count(PmsSpu.id)).where(PmsSpu.deleted == 0)
    )
    spu_count = spu_result.scalar() or 0

    # SKU count
    sku_result = await db.execute(
        select(func.count(PmsSku.id)).where(PmsSku.deleted == 0)
    )
    sku_count = sku_result.scalar() or 0

    # Browse count (last 24h)
    from datetime import datetime, timedelta, timezone
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    browse_result = await db.execute(
        select(func.count(PmsBrowseLog.id)).where(PmsBrowseLog.create_time >= yesterday)
    )
    browse_count = browse_result.scalar() or 0

    # Hot ranking
    from app.services.spu_service import get_hot_products
    hot_ranking = await get_hot_products(db, limit=10)

    return {
        "spuCount": spu_count,
        "skuCount": sku_count,
        "browseCount": browse_count,
        "hotRanking": hot_ranking,
    }
