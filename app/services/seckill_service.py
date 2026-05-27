from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sku import PmsSku
from app.models.order import OmsOrder
from app.models.order_item import OmsOrderItem
from app.utils.seckill import seckill_manager


async def perform_seckill(
    db: AsyncSession,
    user_id: int,
    sku_id: int,
) -> dict:
    """Process a seckill (flash sale) request with atomic stock check + user dedup."""
    sku_lock = seckill_manager.get_lock(sku_id)

    async with sku_lock:
        # Check stock
        sku_result = await db.execute(
            select(PmsSku).where(PmsSku.id == sku_id, PmsSku.deleted == 0)
        )
        sku = sku_result.scalar_one_or_none()
        if not sku:
            raise ValueError("SKU not found")

        # Ensure seckill stock is loaded
        if sku_id not in seckill_manager._stock or seckill_manager.get_stock(sku_id) <= 0:
            seckill_manager.load_stock(sku_id, sku.stock)

        # Check available
        if seckill_manager.get_stock(sku_id) <= 0:
            raise ValueError("Out of stock")

        # Anti-repeat check
        if seckill_manager.has_user(sku_id, user_id):
            raise ValueError("Already participated")

        # Atomic operations
        seckill_manager.decrement_stock(sku_id)
        seckill_manager.add_user(sku_id, user_id)

    # Create order outside the lock
    total_amount = float(sku.price)

    order = OmsOrder(
        user_id=user_id,
        total_amount=total_amount,
        status=1,  # PAID
    )
    db.add(order)
    await db.flush()
    await db.refresh(order)

    order_item = OmsOrderItem(
        order_id=order.id,
        sku_id=sku_id,
        quantity=1,
        price=float(sku.price),
    )
    db.add(order_item)

    # Deduct DB stock
    sku.stock -= 1

    return {
        "status": "queued",
        "message": "Seckill request submitted, processing...",
    }
