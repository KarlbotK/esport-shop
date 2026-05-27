from decimal import Decimal

from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import OmsOrder
from app.models.order_item import OmsOrderItem
from app.models.sku import PmsSku
from app.middleware.email_sender import send_order_confirmation_email
from app.config import settings


async def create_order(
    db: AsyncSession,
    user_id: int,
    items: list[dict],
) -> int:
    """Create an order with items. Validates stock, deducts, creates order."""
    if not items:
        raise ValueError("Order must have at least one item")

    # Validate SKUs and calculate total
    total_amount = Decimal("0.00")
    order_items_data = []

    for item in items:
        sku_id = item["sku_id"]
        quantity = item["quantity"]

        sku_result = await db.execute(
            select(PmsSku).where(PmsSku.id == sku_id, PmsSku.deleted == 0)
        )
        sku = sku_result.scalar_one_or_none()
        if not sku:
            raise ValueError(f"SKU {sku_id} not found")

        if sku.stock < quantity:
            raise ValueError(f"SKU {sku.sku_name} has insufficient stock (requested {quantity}, available {sku.stock})")

        item_total = Decimal(str(sku.price)) * quantity
        total_amount += item_total

        order_items_data.append({
            "sku_id": sku_id,
            "quantity": quantity,
            "price": float(sku.price),
            "sku": sku,
        })

    # Create order
    order = OmsOrder(
        user_id=user_id,
        total_amount=float(total_amount),
        status=0,  # PENDING
    )
    db.add(order)
    await db.flush()
    await db.refresh(order)

    # Create order items and deduct stock
    for data in order_items_data:
        order_item = OmsOrderItem(
            order_id=order.id,
            sku_id=data["sku_id"],
            quantity=data["quantity"],
            price=data["price"],
        )
        db.add(order_item)

        # Deduct stock
        sku = data["sku"]
        sku.stock -= data["quantity"]

    # Send confirmation email in background
    user_result = await db.execute(
        select(__import__("app.models.user", fromlist=["UmsUser"]).UmsUser)
        .where(__import__("app.models.user", fromlist=["UmsUser"]).UmsUser.id == user_id)
    )
    from app.models.user import UmsUser
    user_result = await db.execute(select(UmsUser).where(UmsUser.id == user_id))
    user = user_result.scalar_one_or_none()

    if user and user.email:
        import asyncio
        asyncio.ensure_future(
            send_order_confirmation_email(
                to_email=user.email,
                order_id=order.id,
                total_amount=float(total_amount),
                items=[
                    {"sku_id": d["sku_id"], "sku_name": d["sku"].sku_name, "quantity": d["quantity"]}
                    for d in order_items_data
                ],
                smtp_host=settings.smtp_host,
                smtp_port=settings.smtp_port,
                smtp_username=settings.smtp_username,
                smtp_password=settings.smtp_password,
            )
        )

    return order.id


async def get_user_orders(db: AsyncSession, user_id: int) -> list:
    """Get all orders for a user, with items."""
    result = await db.execute(
        select(OmsOrder)
        .where(OmsOrder.user_id == user_id, OmsOrder.deleted == 0)
        .order_by(desc(OmsOrder.create_time))
    )
    orders = result.scalars().all()

    order_list = []
    for order in orders:
        items_result = await db.execute(
            select(OmsOrderItem).where(OmsOrderItem.order_id == order.id, OmsOrderItem.deleted == 0)
        )
        items = items_result.scalars().all()

        item_list = []
        for item in items:
            item_list.append({
                "id": item.id,
                "skuId": item.sku_id,
                "quantity": item.quantity,
                "price": float(item.price),
                "skuName": None,
            })

        order_list.append({
            "id": order.id,
            "userId": order.user_id,
            "totalAmount": float(order.total_amount),
            "status": order.status,
            "createTime": order.create_time.isoformat() if order.create_time else None,
            "items": item_list,
        })

    return order_list


async def get_order_by_id(db: AsyncSession, user_id: int, order_id: int) -> dict | None:
    """Get a single order by ID, ensuring it belongs to the user."""
    result = await db.execute(
        select(OmsOrder).where(
            OmsOrder.id == order_id,
            OmsOrder.user_id == user_id,
            OmsOrder.deleted == 0,
        )
    )
    order = result.scalar_one_or_none()
    if not order:
        return None

    items_result = await db.execute(
        select(OmsOrderItem).where(OmsOrderItem.order_id == order.id, OmsOrderItem.deleted == 0)
    )
    items = items_result.scalars().all()

    item_list = []
    for item in items:
        item_list.append({
            "id": item.id,
            "skuId": item.sku_id,
            "quantity": item.quantity,
            "price": float(item.price),
            "skuName": None,
        })

    return {
        "id": order.id,
        "userId": order.user_id,
        "totalAmount": float(order.total_amount),
        "status": order.status,
        "createTime": order.create_time.isoformat() if order.create_time else None,
        "items": item_list,
    }
