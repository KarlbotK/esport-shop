"""Agent tools for DeepSeek function calling.

These are the 4 tools exposed to the AI recommendation agent.
"""

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.spu import PmsSpu
from app.models.sku import PmsSku
from app.models.brand import PmsBrand
from app.models.category import PmsCategory
from app.models.browse_log import PmsBrowseLog


async def search_products_tool(
    db: AsyncSession,
    category_id: int | None = None,
    keyword: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    limit: int = 10,
) -> str:
    """Search products with filters and return formatted markdown table.
    
    Searches by name (keyword), brand name, category, and price range.
    If keyword search returns nothing, falls back to category+price only.
    """
    from sqlalchemy import or_

    query = select(PmsSpu).where(PmsSpu.deleted == 0, PmsSpu.publish_status == 1)

    if category_id:
        query = query.where(PmsSpu.category_id == category_id)

    # Flexible keyword search — match any term against name OR brand name
    if keyword:
        terms = [t.strip() for t in keyword.replace(" ", ",").replace("，", ",").split(",") if t.strip()]
        if terms:
            # Also try joining with brand for brand-name search
            query = query.outerjoin(PmsBrand, PmsSpu.brand_id == PmsBrand.id)
            conditions = []
            for term in terms:
                conditions.append(PmsSpu.name.like(f"%{term}%"))
                conditions.append(PmsBrand.name.like(f"%{term}%"))
            query = query.where(or_(*conditions))

    # Price filter via SKU subquery
    if min_price is not None or max_price is not None:
        sku_subq = (
            select(PmsSku.spu_id)
            .where(PmsSku.deleted == 0)
            .group_by(PmsSku.spu_id)
        )
        if min_price is not None:
            sku_subq = sku_subq.having(func.min(PmsSku.price) >= min_price)
        if max_price is not None:
            sku_subq = sku_subq.having(func.max(PmsSku.price) <= max_price)
        query = query.where(PmsSpu.id.in_(sku_subq))

    result = await db.execute(query.limit(limit))
    spus = result.scalars().all()

    lines = ["| ID | Name | Category | Brand | Price Range |", "|---|---|---|---|---|"]
    for spu in spus:
        # Get category name
        cat_result = await db.execute(select(PmsCategory).where(PmsCategory.id == spu.category_id))
        cat = cat_result.scalar_one_or_none()
        cat_name = cat.name if cat else "N/A"

        # Get brand name
        brand_result = await db.execute(select(PmsBrand).where(PmsBrand.id == spu.brand_id))
        brand = brand_result.scalar_one_or_none()
        brand_name = brand.name if brand else "N/A"

        # Get price range
        price_result = await db.execute(
            select(func.min(PmsSku.price), func.max(PmsSku.price))
            .where(PmsSku.spu_id == spu.id, PmsSku.deleted == 0)
        )
        price_row = price_result.first()
        min_p = float(price_row[0]) if price_row[0] else 0
        max_p = float(price_row[1]) if price_row[1] else 0
        if min_p == max_p:
            price_range = f"¥{min_p:.0f}"
        else:
            price_range = f"¥{min_p:.0f} - ¥{max_p:.0f}"

        lines.append(f"| {spu.id} | {spu.name} | {cat_name} | {brand_name} | {price_range} |")

    return "\n".join(lines) if len(lines) > 1 else "No products found."


async def get_user_browse_history_tool(db: AsyncSession, user_id: int, limit: int = 10) -> str:
    """Get user's recent browse history as formatted markdown list."""
    result = await db.execute(
        select(PmsBrowseLog)
        .where(PmsBrowseLog.user_id == user_id)
        .order_by(desc(PmsBrowseLog.create_time))
        .limit(limit)
    )
    logs = result.scalars().all()

    if not logs:
        return "No browse history found."

    lines = ["**Your Recent Browse History:**", ""]
    seen_spus = set()
    for log in logs:
        if log.spu_id not in seen_spus:
            seen_spus.add(log.spu_id)
            spu_result = await db.execute(
                select(PmsSpu).where(PmsSpu.id == log.spu_id, PmsSpu.deleted == 0)
            )
            spu = spu_result.scalar_one_or_none()
            if spu:
                lines.append(f"- {spu.name} (ID: {spu.id})")

    return "\n".join(lines)


async def get_hot_products_tool(db: AsyncSession, category_id: int | None = None, limit: int = 10) -> str:
    """Get hot-ranked products as formatted markdown list."""
    from app.services.spu_service import get_hot_products
    products = await get_hot_products(db, category_id, limit)

    if not products:
        return "No hot products found."

    lines = ["**🔥 Hot Products:**", ""]
    for p in products:
        lines.append(f"- **{p['spu_name']}** — ¥{p['min_price']:.0f} ({p['brand_name']}) — {p['browse_count']} views")

    return "\n".join(lines)


async def compare_products_tool(db: AsyncSession, spu_id_1: int, spu_id_2: int) -> str:
    """Compare two products and return a formatted markdown comparison table."""
    spus = []
    for sid in [spu_id_1, spu_id_2]:
        result = await db.execute(select(PmsSpu).where(PmsSpu.id == sid, PmsSpu.deleted == 0))
        spu = result.scalar_one_or_none()
        if spu:
            # Brand
            brand_result = await db.execute(select(PmsBrand).where(PmsBrand.id == spu.brand_id))
            brand = brand_result.scalar_one_or_none()

            # Category
            cat_result = await db.execute(select(PmsCategory).where(PmsCategory.id == spu.category_id))
            cat = cat_result.scalar_one_or_none()

            # SKUs
            sku_result = await db.execute(
                select(PmsSku).where(PmsSku.spu_id == spu.id, PmsSku.deleted == 0)
            )
            skus = sku_result.scalars().all()

            spus.append({
                "name": spu.name,
                "brand": brand.name if brand else "N/A",
                "category": cat.name if cat else "N/A",
                "description": spu.description or "",
                "skus": [
                    {
                        "name": s.sku_name,
                        "price": float(s.price),
                        "stock": s.stock,
                        "attrs": s.attributes or "",
                    }
                    for s in skus
                ],
            })

    if len(spus) < 2:
        return "Could not find both products for comparison."

    a, b = spus

    lines = [
        f"## Comparison: {a['name']} vs {b['name']}",
        "",
        f"| Feature | **{a['name']}** | **{b['name']}** |",
        "|---|---|---|",
        f"| Brand | {a['brand']} | {b['brand']} |",
        f"| Category | {a['category']} | {b['category']} |",
        f"| Description | {a['description'][:100]}... | {b['description'][:100]}... |",
    ]

    # Price range
    if a["skus"] and b["skus"]:
        a_prices = [s["price"] for s in a["skus"]]
        b_prices = [s["price"] for s in b["skus"]]
        a_range = f"¥{min(a_prices):.0f} - ¥{max(a_prices):.0f}" if len(a_prices) > 1 else f"¥{a_prices[0]:.0f}"
        b_range = f"¥{min(b_prices):.0f} - ¥{max(b_prices):.0f}" if len(b_prices) > 1 else f"¥{b_prices[0]:.0f}"
        lines.append(f"| Price Range | {a_range} | {b_range} |")

    # SKUs
    lines.append(f"| SKU Count | {len(a['skus'])} | {len(b['skus'])} |")

    for i, sku in enumerate(a["skus"][:3]):
        b_sku = b["skus"][i] if i < len(b["skus"]) else {"name": "—", "price": 0, "attrs": ""}
        lines.append(f"| Option {i+1} | {sku['name']} (¥{sku['price']:.0f}) | {b_sku['name']} (¥{b_sku['price']:.0f}) |")

    return "\n".join(lines)
