"""APScheduler jobs for scheduled tasks."""

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.browse_log import PmsBrowseLog
from app.models.spu import PmsSpu
from app.models.order import OmsOrder
from app.models.order_item import OmsOrderItem
from app.models.sku import PmsSku
from app.background.cache import cache_clear, CACHE_HOT_RANKING, CACHE_COLLABORATIVE

logger = logging.getLogger(__name__)


async def refresh_hot_ranking():
    """Refresh hot ranking — scheduled hourly at :30.

    Query last 24 hours of orders, aggregate revenue by SPU.
    """
    logger.info("Starting hot ranking refresh...")
    try:
        async with AsyncSessionLocal() as db:
            yesterday = datetime.now(timezone.utc) - timedelta(hours=24)

            # Aggregate revenue by SPU from recent orders
            query = text("""
                SELECT
                    sp.id AS spu_id,
                    sp.name AS spu_name,
                    SUM(oi.quantity * oi.price) AS revenue,
                    COUNT(DISTINCT o.id) AS order_count
                FROM oms_order o
                JOIN oms_order_item oi ON o.id = oi.order_id
                JOIN pms_sku sk ON oi.sku_id = sk.id
                JOIN pms_spu sp ON sk.spu_id = sp.id
                WHERE o.deleted = 0 AND oi.deleted = 0
                  AND o.status IN (1, 2, 3)
                  AND o.create_time >= :since
                GROUP BY sp.id, sp.name
                ORDER BY revenue DESC
                LIMIT 20
            """)

            result = await db.execute(query, {"since": yesterday})
            rows = result.all()

            # Store ranking in a DB table (sales_ranking)
            try:
                # Create temp table if not exists
                await db.execute(text("""
                    CREATE TABLE IF NOT EXISTS sales_ranking (
                        spu_id BIGINT PRIMARY KEY,
                        revenue DECIMAL(10,2) DEFAULT 0,
                        rank_num INT DEFAULT 0,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )
                """))
                # Clear old data
                await db.execute(text("DELETE FROM sales_ranking"))
                # Insert new ranking
                for i, row in enumerate(rows):
                    await db.execute(
                        text("INSERT INTO sales_ranking (spu_id, revenue, rank_num) VALUES (:spu_id, :revenue, :rank_num)"),
                        {"spu_id": row.spu_id, "revenue": float(row.revenue), "rank_num": i + 1},
                    )
                await db.commit()
                logger.info(f"Hot ranking refreshed: {len(rows)} items")
            except Exception as e:
                logger.error(f"Failed to store sales_ranking: {e}")
                await db.rollback()

        # Clear hot ranking cache
        cache_clear(CACHE_HOT_RANKING)
    except Exception as e:
        logger.error(f"Hot ranking refresh failed: {e}")


async def compute_item_similarity():
    """Compute item-item collaborative filtering matrix — scheduled daily at 3 AM.

    Uses Jaccard similarity on browse logs.
    """
    logger.info("Starting collaborative filtering matrix computation...")
    try:
        async with AsyncSessionLocal() as db:
            # Get all browse logs
            result = await db.execute(
                select(PmsBrowseLog.spu_id, PmsBrowseLog.user_id)
                .where(PmsBrowseLog.user_id.isnot(None))
            )
            rows = result.all()

            # Build user->items map
            user_items: dict[int, set[int]] = {}
            for row in rows:
                if row.user_id not in user_items:
                    user_items[row.user_id] = set()
                user_items[row.user_id].add(row.spu_id)

            # Compute pairwise Jaccard similarity
            spu_ids = set()
            for items in user_items.values():
                spu_ids.update(items)
            spu_ids = list(spu_ids)

            similarities = []
            n = len(spu_ids)
            for i in range(n):
                for j in range(i + 1, n):
                    a, b = spu_ids[i], spu_ids[j]
                    users_a = {uid for uid, items in user_items.items() if a in items}
                    users_b = {uid for uid, items in user_items.items() if b in items}
                    intersection = users_a & users_b
                    if not intersection:
                        continue
                    union = users_a | users_b
                    score = len(intersection) / len(union) if union else 0
                    if score > 0.05:  # Only store meaningful similarities
                        similarities.append((a, b, score))
                        similarities.append((b, a, score))

            # Sort by score and keep top 20 per item
            from collections import defaultdict
            top_per_item: dict[int, list[tuple[int, float]]] = defaultdict(list)
            for a, b, score in similarities:
                top_per_item[a].append((b, score))

            for key in top_per_item:
                top_per_item[key].sort(key=lambda x: x[1], reverse=True)
                top_per_item[key] = top_per_item[key][:20]

            # Store in DB table
            try:
                await db.execute(text("""
                    CREATE TABLE IF NOT EXISTS item_similarity (
                        spu_id_a BIGINT NOT NULL,
                        spu_id_b BIGINT NOT NULL,
                        similarity_score DECIMAL(10,6) DEFAULT 0,
                        PRIMARY KEY (spu_id_a, spu_id_b)
                    )
                """))
                await db.execute(text("DELETE FROM item_similarity"))

                for spu_a, pairs in top_per_item.items():
                    for spu_b, score in pairs:
                        await db.execute(
                            text("INSERT INTO item_similarity (spu_id_a, spu_id_b, similarity_score) VALUES (:a, :b, :score)"),
                            {"a": spu_a, "b": spu_b, "score": round(score, 6)},
                        )

                await db.commit()
                logger.info(f"Collaborative filtering computed: {len(top_per_item)} items with similarities")
            except Exception as e:
                logger.error(f"Failed to store item_similarity: {e}")
                await db.rollback()

        # Clear collaborative cache
        cache_clear(CACHE_COLLABORATIVE)
    except Exception as e:
        logger.error(f"Item similarity computation failed: {e}")
