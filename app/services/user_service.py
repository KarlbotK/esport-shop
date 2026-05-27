from datetime import datetime, timedelta, timezone

import bcrypt
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import UmsUser
from app.models.login_log import UmsLoginLog
from app.models.order import OmsOrder
from app.models.browse_log import PmsBrowseLog
from app.security import create_access_token


async def register_user(
    db: AsyncSession,
    username: str,
    password: str,
    email: str | None = None,
    phone: str | None = None,
) -> UmsUser:
    """Register a new CUSTOMER user."""
    # Check if username already exists
    result = await db.execute(select(UmsUser).where(UmsUser.username == username, UmsUser.deleted == 0))
    existing = result.scalar_one_or_none()
    if existing:
        raise ValueError("Username already exists")

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = UmsUser(
        username=username,
        password=hashed_password,
        email=email,
        phone=phone,
        role="CUSTOMER",
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def login_user(
    db: AsyncSession,
    username: str,
    password: str,
    ip_address: str | None = None,
) -> dict:
    """Authenticate user and return token + user info."""
    result = await db.execute(
        select(UmsUser).where(UmsUser.username == username, UmsUser.deleted == 0)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("Invalid username or password")

    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        raise ValueError("Invalid username or password")

    # Record login log
    login_log = UmsLoginLog(user_id=user.id, ip_address=ip_address)
    db.add(login_log)

    # Generate JWT
    token = create_access_token(user.id, user.username, user.role)

    return {
        "token": token,
        "username": user.username,
        "role": user.role,
    }


async def get_user_profile(db: AsyncSession, user_id: int) -> dict:
    """Get user analytics profile."""
    user_result = await db.execute(
        select(UmsUser).where(UmsUser.id == user_id, UmsUser.deleted == 0)
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")

    # Favorite category (most browsed)
    fav_result = await db.execute(
        select(PmsBrowseLog.spu_id, func.count(PmsBrowseLog.id).label("cnt"))
        .where(PmsBrowseLog.user_id == user_id)
        .group_by(PmsBrowseLog.spu_id)
        .order_by(func.count(PmsBrowseLog.id).desc())
        .limit(1)
    )
    fav_row = fav_result.first()
    favorite_category = None
    if fav_row:
        from app.models.spu import PmsSpu
        spu_result = await db.execute(
            select(PmsSpu).where(PmsSpu.id == fav_row.spu_id)
        )
        spu = spu_result.scalar_one_or_none()
        if spu:
            from app.models.category import PmsCategory
            cat_result = await db.execute(
                select(PmsCategory).where(PmsCategory.id == spu.category_id)
            )
            cat = cat_result.scalar_one_or_none()
            if cat:
                favorite_category = cat.name

    # Browse count
    total_browse_result = await db.execute(
        select(func.count(PmsBrowseLog.id)).where(PmsBrowseLog.user_id == user_id)
    )
    browse_count = total_browse_result.scalar() or 0

    # Browse count last 7 days
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    browse_7d_result = await db.execute(
        select(func.count(PmsBrowseLog.id)).where(
            and_(PmsBrowseLog.user_id == user_id, PmsBrowseLog.create_time >= seven_days_ago)
        )
    )
    browse_count_7d = browse_7d_result.scalar() or 0

    # Activity level
    if browse_count > 10:
        activity_level = "high"
    elif browse_count > 3:
        activity_level = "medium"
    else:
        activity_level = "low"

    # Orders
    order_result = await db.execute(
        select(func.count(OmsOrder.id), func.coalesce(func.sum(OmsOrder.total_amount), 0))
        .where(
            and_(
                OmsOrder.user_id == user_id,
                OmsOrder.deleted == 0,
                OmsOrder.status.in_([1, 2, 3]),  # PAID, SHIPPED, COMPLETED
            )
        )
    )
    order_row = order_result.first()
    order_count = order_row[0] or 0
    total_spending = float(order_row[1] or 0)

    # Purchasing power
    if order_count > 0:
        avg_order = total_spending / order_count
        if avg_order > 1000:
            purchasing_power = "high-end"
        elif avg_order > 500:
            purchasing_power = "mid-range"
        else:
            purchasing_power = "entry-level"
    else:
        purchasing_power = "no purchases"

    return {
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
        "favorite_category": favorite_category,
        "browse_count": browse_count,
        "browse_count_7d": browse_count_7d,
        "purchasing_power": purchasing_power,
        "total_spending": total_spending,
        "order_count": order_count,
        "activity_level": activity_level,
    }
