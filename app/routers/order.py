from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.common import Result
from app.schemas.order import OrderCreateDTO, OrderCreateVO, OrderVO
from app.security.dependencies import get_current_user
from app.services import order_service

router = APIRouter(prefix="/api/order", tags=["Order"])


@router.post("/create")
async def create_order(
    dto: OrderCreateDTO,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create an order from cart items."""
    try:
        items = [{"sku_id": item.sku_id, "quantity": item.quantity} for item in dto.items]
        order_id = await order_service.create_order(db, current_user["user_id"], items)
        return Result.success(OrderCreateVO(order_id=order_id))
    except ValueError as e:
        return Result.error(str(e))


@router.get("/list")
async def order_list(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all orders for the current user."""
    orders = await order_service.get_user_orders(db, current_user["user_id"])
    return Result.success([OrderVO(**o) for o in orders])


@router.get("/{order_id}")
async def order_detail(
    order_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single order by ID."""
    order = await order_service.get_order_by_id(db, current_user["user_id"], order_id)
    if order is None:
        return Result.error("Order not found", code=404)
    return Result.success(OrderVO(**order))
