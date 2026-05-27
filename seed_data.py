"""
Seed script to populate realistic test data for ShopAgent.
Run: "E:/KarlShop/venv/Scripts/python" seed_data.py

IMPORTANT: Run init.sql first to create tables + base data, then run this script.
"""

import asyncio
import random
import bcrypt
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select, text
from app.database import AsyncSessionLocal
from app.models.user import UmsUser
from app.models.spu import PmsSpu
from app.models.sku import PmsSku
from app.models.brand import PmsBrand
from app.models.category import PmsCategory
from app.models.order import OmsOrder
from app.models.order_item import OmsOrderItem
from app.models.browse_log import PmsBrowseLog
from app.models.login_log import UmsLoginLog

NUM_CUSTOMERS = 50
NUM_SALES = 3
NUM_BROWSE_LOGS = 800
NUM_ORDERS = 200
DAYS_OF_HISTORY = 60

PASSWORD = bcrypt.hashpw("123456".encode(), bcrypt.gensalt()).decode()

IPS = [f"192.168.1.{i}" for i in range(1, 60)] + \
      [f"10.0.0.{i}" for i in range(1, 30)] + \
      [f"114.92.{i}.{j}" for i in range(10, 20) for j in range(1, 5)]

USER_PROFILES = [
    ("FPS玩家", 1, "high", "high"),
    ("FPS玩家", 1, "mid", "high"),
    ("FPS玩家", 1, "high", "medium"),
    ("MOBA玩家", 2, "high", "high"),
    ("MOBA玩家", 2, "mid", "medium"),
    ("游戏爱好者", 3, "mid", "medium"),
    ("游戏爱好者", 1, "low", "medium"),
    ("游戏爱好者", 2, "low", "low"),
    ("主播", 3, "high", "high"),
    ("主播", 1, "high", "medium"),
    ("学生党", 1, "low", "high"),
    ("学生党", 2, "low", "medium"),
    ("学生党", 3, "low", "low"),
    ("上班族", 5, "high", "low"),
    ("上班族", 2, "mid", "medium"),
    ("上班族", 1, "mid", "low"),
    ("外设发烧友", 4, "high", "high"),
    ("外设发烧友", 2, "high", "high"),
    ("外设发烧友", 3, "high", "medium"),
]

# All products: (category_id, brand_id, name, base_price, stock)
ALL_PRODUCTS = [
    # -- Mice (cat 1) -- original 3 + new 5
    (1, 1, "罗技 PRO X SUPERLIGHT 2", 1099.00, 50),
    (1, 2, "雷蛇 毒蝰V3 Pro", 1299.00, 40),
    (1, 5, "卓威 EC3-CW", 1099.00, 35),
    (1, 1, "罗技 G304 无线游戏鼠标", 199.00, 100),
    (1, 2, "雷蛇 巴塞利斯蛇V3", 499.00, 45),
    (1, 3, "赛睿 Prime Mini Wireless", 899.00, 30),
    (1, 6, "ROG 龙鳞ACE 无线鼠标", 1199.00, 25),
    (1, 7, "HyperX Pulsefire Haste", 349.00, 55),
    # -- Keyboards (cat 2) -- original 3 + new 4
    (2, 8, "Wooting 60HE+", 1399.00, 15),
    (2, 1, "罗技 G913 TKL", 999.00, 25),
    (2, 2, "雷蛇 黑寡妇V4 Pro", 1599.00, 20),
    (2, 4, "海盗船 K70 MAX 磁轴键盘", 1399.00, 20),
    (2, 6, "ROG 夜魔 无线键盘", 1699.00, 15),
    (2, 7, "HyperX Alloy Origins", 699.00, 35),
    (2, 3, "赛睿 Apex Pro TKL", 1599.00, 18),
    # -- Headsets (cat 3) -- original 2 + new 4
    (3, 7, "HyperX Cloud III", 599.00, 60),
    (3, 3, "赛睿 Arctis Nova Pro Wireless", 2699.00, 10),
    (3, 1, "罗技 G733 无线游戏耳机", 999.00, 30),
    (3, 2, "雷蛇 北海巨妖V3", 699.00, 40),
    (3, 4, "海盗船 HS80 无线耳机", 1099.00, 22),
    (3, 6, "ROG Delta S 无线耳机", 1299.00, 18),
    # -- Mousepads (cat 4) -- all new (6 items)
    (4, 8, "Wooting 同款鼠标垫", 349.00, 80),
    (4, 1, "罗技 G840 超大鼠标垫", 299.00, 60),
    (4, 2, "雷蛇 Gigantus V2", 199.00, 100),
    (4, 5, "卓威 G-SR-SE", 299.00, 50),
    (4, 3, "赛睿 QcK Heavy", 179.00, 120),
    (4, 6, "ROG 月刃鼠标垫", 259.00, 40),
    # -- Gaming Chairs (cat 5) -- all new (5 items)
    (5, 2, "雷蛇 Iskur X 电竞椅", 2999.00, 15),
    (5, 7, "HyperX Cloud 电竞椅", 2499.00, 20),
    (5, 3, "赛睿 Arctis 电竞椅", 3299.00, 10),
    (5, 6, "ROG Chariot 电竞椅", 3599.00, 8),
    (5, 4, "海盗船 T3 Rush 电竞椅", 2799.00, 12),
]


def rand_time(days_ago: int) -> datetime:
    seconds = random.randint(0, days_ago * 24 * 3600)
    return datetime.now(timezone.utc) - timedelta(seconds=seconds)


async def clear_dynamic_data():
    """Clear orders, browse logs, login logs — keep products/users/categories/brands."""
    async with AsyncSessionLocal() as db:
        for table in ["oms_order_item", "oms_order", "pms_browse_log",
                       "ums_login_log", "sms_operation_log"]:
            await db.execute(text(f"DELETE FROM {table}"))
        await db.commit()
    print("  Cleared orders & logs (kept products + users).")


async def seed_all_products():
    """Delete existing SPUs/SKUs and insert ALL products from scratch."""
    async with AsyncSessionLocal() as db:
        # Delete existing products
        await db.execute(text("DELETE FROM pms_sku"))
        await db.execute(text("DELETE FROM pms_spu"))
        await db.commit()

        for cat_id, brand_id, name, base_price, stock in ALL_PRODUCTS:
            spu = PmsSpu(
                name=name,
                category_id=cat_id,
                brand_id=brand_id,
                description=f"{name} — 专业电竞装备，品质保障",
                publish_status=1,
            )
            db.add(spu)
            await db.flush()

            # Create 1-3 SKU variants per product
            if "电竞椅" in name:
                variants = [("标准版", 1.0)]
            elif "鼠标垫" in name:
                variants = [("大号", 1.0), ("超大号", 1.3)] if "超大" not in name else [("标准", 1.0)]
            else:
                variants = [("标准版", 1.0)]
                if random.random() < 0.6:
                    variants.append(("Pro版", 1.25))
                if random.random() < 0.3:
                    variants.append(("无线版", 1.45))

            for suffix, multiplier in variants:
                sku = PmsSku(
                    spu_id=spu.id,
                    sku_name=f"{name} {suffix}",
                    price=round(base_price * multiplier, 2),
                    stock=random.randint(3, max(5, stock)),
                    attributes='{"variant": "' + suffix + '"}',
                )
                db.add(sku)

        await db.commit()
    print(f"  Inserted {len(ALL_PRODUCTS)} SPUs with SKU variants.")


async def seed_users():
    """Add SALES + CUSTOMER users (keep existing admin)."""
    async with AsyncSessionLocal() as db:
        # Delete non-admin users
        await db.execute(text("DELETE FROM ums_user WHERE role != 'ADMIN'"))
        await db.commit()

        customer_ids = []
        sales_ids = []

        for i in range(NUM_SALES):
            user = UmsUser(
                username=f"sales{i + 1}",
                password=PASSWORD,
                email=f"sales{i + 1}@shopagent.com",
                phone=f"1380013{4000 + i:04d}",
                role="SALES",
            )
            db.add(user)
            await db.flush()
            sales_ids.append(user.id)

        for i in range(NUM_CUSTOMERS):
            profile = random.choice(USER_PROFILES)
            name_prefix = profile[0]
            user = UmsUser(
                username=f"{name_prefix}{i + 1}",
                password=PASSWORD,
                email=f"user{i + 1}@test.com",
                phone=f"139{random.randint(10000000, 99999999)}",
                role="CUSTOMER",
            )
            db.add(user)
            await db.flush()
            customer_ids.append(user.id)

        await db.commit()
    print(f"  Created {NUM_SALES} SALES + {NUM_CUSTOMERS} CUSTOMER users.")
    return customer_ids, sales_ids


async def seed_browse_logs(customer_ids, sku_spu_map):
    """Generate browse logs with user category preferences."""
    async with AsyncSessionLocal() as db:
        user_fav = {uid: random.randint(1, 5) for uid in customer_ids}
        spu_by_category = {}
        for spu_id, cat_id in sku_spu_map.values():
            spu_by_category.setdefault(cat_id, []).append(spu_id)

        logs = []
        for _ in range(NUM_BROWSE_LOGS):
            uid = random.choice(customer_ids + [None] * 10)
            fav_cat = user_fav.get(uid, random.randint(1, 5))

            if random.random() < 0.6 and fav_cat in spu_by_category:
                spu_id = random.choice(spu_by_category[fav_cat])
            else:
                all_spus = list(set(s for _, s in sku_spu_map.values()))
                spu_id = random.choice(all_spus)

            log = PmsBrowseLog(
                user_id=uid,
                spu_id=spu_id,
                duration_seconds=random.randint(5, 300),
                ip_address=random.choice(IPS),
            )
            log.create_time = rand_time(DAYS_OF_HISTORY)
            logs.append(log)

        db.add_all(logs)
        await db.commit()
    print(f"  Generated {len(logs)} browse logs ({DAYS_OF_HISTORY} day span).")


async def seed_orders(customer_ids, all_skus):
    """Generate orders with diverse statuses and item counts."""
    async with AsyncSessionLocal() as db:
        for _ in range(NUM_ORDERS):
            uid = random.choice(customer_ids)
            num_items = random.choices([1, 2, 3], weights=[50, 35, 15])[0]
            picked = random.sample(all_skus, min(num_items, len(all_skus)))

            total = Decimal("0.00")
            items = []
            for sku in picked:
                qty = random.choices([1, 2, 3], weights=[70, 20, 10])[0]
                items.append((sku["id"], sku["price"], qty))
                total += Decimal(str(sku["price"])) * qty

            status = random.choices([1, 2, 3, 0, 4], weights=[15, 10, 55, 10, 10])[0]

            order = OmsOrder(
                user_id=uid,
                total_amount=float(total),
                status=status,
            )
            order.create_time = rand_time(DAYS_OF_HISTORY)
            db.add(order)
            await db.flush()

            for sku_id, price, qty in items:
                item = OmsOrderItem(
                    order_id=order.id,
                    sku_id=sku_id,
                    quantity=qty,
                    price=price,
                )
                db.add(item)

        await db.commit()
    print(f"  Generated {NUM_ORDERS} orders.")


async def seed_login_logs(customer_ids, sales_ids):
    """Generate login logs — more for active users."""
    async with AsyncSessionLocal() as db:
        all_uids = customer_ids + sales_ids + [1]
        logs = []
        for uid in all_uids:
            # Active users: 5-25 logins; less active: 2-8
            count = random.randint(5, 25) if random.random() < 0.6 else random.randint(2, 8)
            for _ in range(count):
                log = UmsLoginLog(user_id=uid, ip_address=random.choice(IPS))
                log.login_time = rand_time(DAYS_OF_HISTORY)
                logs.append(log)

        db.add_all(logs)
        await db.commit()
    print(f"  Generated {len(logs)} login logs.")


async def main():
    print("=== ShopAgent Seed Data Generator ===\n")

    print("[1/5] Clearing dynamic data (orders, logs)...")
    await clear_dynamic_data()

    print("[2/5] Seeding ALL products...")
    await seed_all_products()

    # Fetch SKU data for orders and browse logs
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(PmsSku.id, PmsSku.price, PmsSku.spu_id, PmsSpu.category_id)
            .join(PmsSpu, PmsSku.spu_id == PmsSpu.id)
            .where(PmsSku.deleted == 0)
        )
        rows = result.all()
        all_skus = [{"id": r[0], "price": float(r[1])} for r in rows]
        sku_spu_map = {r[0]: (r[2], r[3]) for r in rows}  # sku_id → (spu_id, cat_id)
    print(f"  SKUs available: {len(all_skus)} across categories")

    print("[3/5] Seeding users...")
    customer_ids, sales_ids = await seed_users()

    print("[4/5] Seeding browse logs...")
    await seed_browse_logs(customer_ids, sku_spu_map)

    print("[5/5] Seeding orders & login logs...")
    await seed_orders(customer_ids, all_skus)
    await seed_login_logs(customer_ids, sales_ids)

    print(f"""
=== Done! Test Data Summary ===
  Users:      1 ADMIN + {NUM_SALES} SALES + {NUM_CUSTOMERS} CUSTOMERS
  Products:   {len(ALL_PRODUCTS)} SPUs across 5 categories
  SKUs:       ~{len(all_skus)} variants
  Orders:     {NUM_ORDERS} (status 0-4)
  Browse:     {NUM_BROWSE_LOGS} logs ({DAYS_OF_HISTORY} days)
  Login:      many login logs

  Login test accounts:
    admin   / 123456  (ADMIN)
    sales1  / 123456  (SALES)
    sales2  / 123456  (SALES)
    sales3  / 123456  (SALES)
    学生党1  / 123456  (CUSTOMER, budget-focused)
    FPS玩家1 / 123456  (CUSTOMER, mice enthusiast)
    外设发烧友1 / 123456 (CUSTOMER, high-end gear)
""")


if __name__ == "__main__":
    asyncio.run(main())
