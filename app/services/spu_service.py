import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func, and_, desc, join, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.spu import PmsSpu
from app.models.sku import PmsSku
from app.models.brand import PmsBrand
from app.models.browse_log import PmsBrowseLog
from app.background.cache import cache_get, cache_set, CACHE_SPU_DETAIL


async def get_spu_detail(db: AsyncSession, spu_id: int) -> dict | None:
    """Get SPU detail with SKU list. Uses cache-aside pattern."""
    # Try cache
    cache_key = f"spu_detail:{spu_id}"
    cached = cache_get(CACHE_SPU_DETAIL, cache_key)
    if cached is not None:
        return cached

    # Query SPU
    spu_result = await db.execute(
        select(PmsSpu).where(PmsSpu.id == spu_id, PmsSpu.deleted == 0)
    )
    spu = spu_result.scalar_one_or_none()
    if not spu:
        # Cache empty result to prevent cache penetration (5min TTL)
        cache_set(CACHE_SPU_DETAIL, cache_key, None, ttl=300)
        return None

    # Query SKUs
    sku_result = await db.execute(
        select(PmsSku).where(PmsSku.spu_id == spu_id, PmsSku.deleted == 0)
    )
    skus = sku_result.scalars().all()

    sku_list = []
    for sku in skus:
        sku_list.append({
            "id": sku.id,
            "spu_id": sku.spu_id,
            "sku_name": sku.sku_name,
            "price": float(sku.price),
            "stock": sku.stock,
            "attributes": sku.attributes,
        })

    result = {
        "spu_id": spu.id,
        "spu_name": spu.name,
        "category_id": spu.category_id,
        "brand_id": spu.brand_id,
        "description": spu.description,
        "sku_list": sku_list,
    }

    # Cache with randomized TTL to prevent avalanche
    ttl = 3600 + random.randint(0, 1800)  # 60-90 min
    cache_set(CACHE_SPU_DETAIL, cache_key, result, ttl=ttl)

    return result


async def get_spu_list(
    db: AsyncSession,
    category_id: int | None = None,
    brand_id: int | None = None,
    keyword: str | None = None,
    page: int = 1,
    size: int = 20,
) -> dict:
    """Paginated SPU list with optional filters."""
    query = select(PmsSpu).where(PmsSpu.deleted == 0, PmsSpu.publish_status == 1)

    if category_id:
        query = query.where(PmsSpu.category_id == category_id)
    if brand_id:
        query = query.where(PmsSpu.brand_id == brand_id)
    if keyword:
        query = query.where(PmsSpu.name.like(f"%{keyword}%"))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Fetch page
    query = query.order_by(desc(PmsSpu.create_time)).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    spus = result.scalars().all()

    # Batch fetch min prices for all SPUs
    spu_ids = [spu.id for spu in spus]
    price_rows = {}
    if spu_ids:
        price_query = (
            select(PmsSku.spu_id, func.min(PmsSku.price).label("min_price"))
            .where(PmsSku.spu_id.in_(spu_ids), PmsSku.deleted == 0)
            .group_by(PmsSku.spu_id)
        )
        price_result = await db.execute(price_query)
        for row in price_result.all():
            price_rows[row.spu_id] = float(row.min_price)

    records = []
    for spu in spus:
        records.append({
            "id": spu.id,
            "name": spu.name,
            "categoryId": spu.category_id,
            "brandId": spu.brand_id,
            "description": spu.description,
            "publishStatus": spu.publish_status,
            "createTime": spu.create_time.isoformat() if spu.create_time else None,
            "minPrice": price_rows.get(spu.id),
        })

    return {
        "records": records,
        "total": total,
        "size": size,
        "current": page,
        "pages": (total + size - 1) // size if total > 0 else 0,
    }


async def get_hot_products(
    db: AsyncSession,
    category_id: int | None = None,
    limit: int = 10,
) -> list:
    """Hot products ranked by browse frequency in the last 7 days."""
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

    query = (
        select(
            PmsBrowseLog.spu_id,
            func.count(PmsBrowseLog.id).label("browse_count"),
        )
        .where(PmsBrowseLog.create_time >= seven_days_ago)
        .group_by(PmsBrowseLog.spu_id)
        .order_by(func.count(PmsBrowseLog.id).desc())
        .limit(limit)
    )

    if category_id:
        query = query.join(PmsSpu, PmsBrowseLog.spu_id == PmsSpu.id).where(
            PmsSpu.category_id == category_id,
            PmsSpu.deleted == 0,
        )

    result = await db.execute(query)
    rows = result.all()

    hot_list = []
    for row in rows:
        spu_result = await db.execute(
            select(PmsSpu).where(PmsSpu.id == row.spu_id, PmsSpu.deleted == 0)
        )
        spu = spu_result.scalar_one_or_none()
        if not spu:
            continue

        brand_name = ""
        if spu.brand_id:
            brand_result = await db.execute(
                select(PmsBrand).where(PmsBrand.id == spu.brand_id)
            )
            brand = brand_result.scalar_one_or_none()
            if brand:
                brand_name = brand.name

        # Get min price
        price_result = await db.execute(
            select(func.min(PmsSku.price)).where(
                PmsSku.spu_id == spu.id, PmsSku.deleted == 0
            )
        )
        min_price = float(price_result.scalar() or 0)

        hot_list.append({
            "id": spu.id,
            "name": spu.name,
            "spuId": spu.id,
            "spuName": spu.name,
            "categoryId": spu.category_id,
            "brandName": brand_name,
            "minPrice": min_price,
            "browseCount": row.browse_count,
        })

    return hot_list


async def get_similar_products(db: AsyncSession, spu_id: int) -> list:
    """"Also viewed" — users who viewed this SPU also viewed these."""
    # Find users who viewed this SPU
    user_subquery = (
        select(PmsBrowseLog.user_id)
        .where(PmsBrowseLog.spu_id == spu_id)
        .distinct()
        .subquery()
    )

    # Find other SPUs those users viewed
    query = (
        select(PmsBrowseLog.spu_id, func.count(PmsBrowseLog.id).label("cnt"))
        .where(
            and_(
                PmsBrowseLog.user_id.in_(select(user_subquery.c.user_id)),
                PmsBrowseLog.spu_id != spu_id,
            )
        )
        .group_by(PmsBrowseLog.spu_id)
        .order_by(func.count(PmsBrowseLog.id).desc())
        .limit(10)
    )
    result = await db.execute(query)
    rows = result.all()

    spus = []
    for row in rows:
        spu_result = await db.execute(
            select(PmsSpu).where(PmsSpu.id == row.spu_id, PmsSpu.deleted == 0)
        )
        spu = spu_result.scalar_one_or_none()
        if spu:
            spus.append({
                "id": spu.id,
                "name": spu.name,
                "categoryId": spu.category_id,
                "brandId": spu.brand_id,
                "description": spu.description,
                "publishStatus": spu.publish_status,
                "createTime": spu.create_time.isoformat() if spu.create_time else None,
            })

    return spus


async def get_collaborative_products(db: AsyncSession, spu_id: int) -> list:
    """Item-Item collaborative filtering from precomputed similarity matrix."""
    # Try to get from DB table item_similarity
    try:
        from sqlalchemy import Table, MetaData
        metadata = MetaData()
        metadata.reflect(bind=db.get_bind())
        if "item_similarity" in metadata.tables:
            item_similarity = metadata.tables["item_similarity"]
            query = (
                select(item_similarity)
                .where(item_similarity.c.spu_id_a == spu_id)
                .order_by(item_similarity.c.similarity_score.desc())
                .limit(20)
            )
            result = await db.execute(query)
            rows = result.all()

            spus = []
            for row in rows:
                spu_result = await db.execute(
                    select(PmsSpu).where(PmsSpu.id == row.spu_id_b, PmsSpu.deleted == 0)
                )
                spu = spu_result.scalar_one_or_none()
                if spu:
                    spus.append({
                        "id": spu.id,
                        "name": spu.name,
                        "categoryId": spu.category_id,
                        "brandId": spu.brand_id,
                        "description": spu.description,
                        "publishStatus": spu.publish_status,
                        "createTime": spu.create_time.isoformat() if spu.create_time else None,
                    })
            return spus
    except Exception:
        pass

    # Fallback: return similar products (also viewed)
    return await get_similar_products(db, spu_id)
