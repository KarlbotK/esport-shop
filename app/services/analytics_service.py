from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import OmsOrder
from app.models.order_item import OmsOrderItem
from app.models.sku import PmsSku
from app.models.spu import PmsSpu


async def get_sales_report(db: AsyncSession, status: int | None = None) -> list[dict]:
    """Get sales report, optionally filtered by status."""
    from sqlalchemy import text

    # Aggregate order items → revenue by SKU
    conditions = "oi.deleted = 0 AND o.deleted = 0"
    if status is not None:
        conditions += f" AND o.status = {status}"

    query = text(f"""
        SELECT
            oi.sku_id,
            s.sku_name,
            COALESCE(sp.name, '') AS spu_name,
            SUM(oi.quantity) AS quantity,
            SUM(oi.quantity * oi.price) AS revenue
        FROM oms_order_item oi
        JOIN oms_order o ON oi.order_id = o.id
        LEFT JOIN pms_sku s ON oi.sku_id = s.id
        LEFT JOIN pms_spu sp ON s.spu_id = sp.id
        WHERE {conditions}
        GROUP BY oi.sku_id, s.sku_name, sp.name
        ORDER BY revenue DESC
        LIMIT 100
    """)

    result = await db.execute(query)
    rows = result.all()

    return [
        {
            "skuId": row.sku_id,
            "skuName": row.sku_name,
            "spuName": row.spu_name,
            "quantity": int(row.quantity),
            "revenue": float(row.revenue),
        }
        for row in rows
    ]


async def get_sales_ranking(db: AsyncSession, period: str = "daily") -> list[dict]:
    """Get sales ranking by period (daily/weekly/monthly)."""
    from sqlalchemy import text

    date_filter = ""
    if period == "daily":
        date_filter = "AND o.create_time >= DATE_SUB(NOW(), INTERVAL 1 DAY)"
    elif period == "weekly":
        date_filter = "AND o.create_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
    elif period == "monthly":
        date_filter = "AND o.create_time >= DATE_SUB(NOW(), INTERVAL 30 DAY)"

    query = text(f"""
        SELECT
            oi.sku_id,
            s.sku_name,
            COALESCE(sp.name, '') AS spu_name,
            SUM(oi.quantity) AS quantity,
            SUM(oi.quantity * oi.price) AS revenue
        FROM oms_order_item oi
        JOIN oms_order o ON oi.order_id = o.id
        LEFT JOIN pms_sku s ON oi.sku_id = s.id
        LEFT JOIN pms_spu sp ON s.spu_id = sp.id
        WHERE oi.deleted = 0 AND o.deleted = 0
          AND o.status IN (1, 2, 3)
          {date_filter}
        GROUP BY oi.sku_id, s.sku_name, sp.name
        ORDER BY revenue DESC
        LIMIT 20
    """)

    result = await db.execute(query)
    rows = result.all()

    return [
        {
            "sku_id": row.sku_id,
            "sku_name": row.sku_name,
            "spu_name": row.spu_name,
            "quantity": int(row.quantity),
            "revenue": float(row.revenue),
        }
        for row in rows
    ]


async def get_sales_trend(db: AsyncSession, period: str = "daily") -> list[dict]:
    """Get sales trend grouped by period."""
    from sqlalchemy import text

    if period == "daily":
        group_expr = "DATE(o.create_time)"
        label_expr = "DATE_FORMAT(o.create_time, '%Y-%m-%d')"
    elif period == "weekly":
        group_expr = "YEARWEEK(o.create_time, 1)"
        label_expr = "CONCAT(YEAR(o.create_time), '-W', LPAD(WEEK(o.create_time, 1), 2, '0'))"
    elif period == "monthly":
        group_expr = "DATE_FORMAT(o.create_time, '%Y-%m')"
        label_expr = "DATE_FORMAT(o.create_time, '%Y-%m')"
    else:
        group_expr = "DATE(o.create_time)"
        label_expr = "DATE_FORMAT(o.create_time, '%Y-%m-%d')"

    query = text(f"""
        SELECT
            {label_expr} AS period_label,
            SUM(oi.quantity * oi.price) AS revenue,
            COUNT(DISTINCT o.id) AS order_count
        FROM oms_order o
        JOIN oms_order_item oi ON o.id = oi.order_id
        WHERE o.deleted = 0 AND oi.deleted = 0
          AND o.status IN (1, 2, 3)
        GROUP BY {group_expr}, {label_expr}
        ORDER BY {group_expr} DESC
        LIMIT 30
    """)

    result = await db.execute(query)
    rows = result.all()

    return [
        {
            "period": period,
            "periodLabel": row.period_label,
            "revenue": float(row.revenue),
            "orderCount": int(row.order_count),
        }
        for row in rows
    ]


async def get_anomaly_detection(db: AsyncSession) -> dict:
    """Detect anomalies in daily revenue using 3-sigma."""
    from sqlalchemy import text
    import math

    query = text("""
        SELECT
            DATE(o.create_time) AS day,
            SUM(oi.quantity * oi.price) AS revenue
        FROM oms_order o
        JOIN oms_order_item oi ON o.id = oi.order_id
        WHERE o.deleted = 0 AND oi.deleted = 0
          AND o.status IN (1, 2, 3)
        GROUP BY DATE(o.create_time)
        ORDER BY day
    """)

    result = await db.execute(query)
    rows = result.all()

    if not rows:
        return {
            "mean": 0,
            "stddev": 0,
            "upperBound": 0,
            "lowerBound": 0,
            "anomalies": [],
        }

    revenues = [float(row.revenue) for row in rows]
    n = len(revenues)
    mean = sum(revenues) / n
    variance = sum((r - mean) ** 2 for r in revenues) / n
    stddev = math.sqrt(variance)

    upper_bound = mean + 3 * stddev
    lower_bound = mean - 3 * stddev

    anomalies = []
    for row in rows:
        rev = float(row.revenue)
        day_str = row.day.isoformat() if hasattr(row.day, 'isoformat') else str(row.day)
        if rev > upper_bound:
            anomalies.append({"date": day_str, "revenue": rev, "type": "surge"})
        elif rev < lower_bound:
            anomalies.append({"date": day_str, "revenue": rev, "type": "drop"})

    return {
        "mean": round(mean, 2),
        "stddev": round(stddev, 2),
        "upperBound": round(upper_bound, 2),
        "lowerBound": round(lower_bound, 2),
        "anomalies": anomalies,
    }
