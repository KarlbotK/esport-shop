"""Operation logging decorator — replaces @OperationLog + OperationLogAspect.

Usage:
    @router.post("/api/sales/spu")
    @operation_log("添加商品")
    async def add_spu(...):
        ...
"""

import functools
from typing import Callable

from fastapi import Request
from sqlalchemy import insert

from app.database import AsyncSessionLocal
from app.models.operation_log import SmsOperationLog
from app.utils.ip import get_client_ip


def operation_log(operation_type: str):
    """Decorator that logs an operation to sms_operation_log on success.

    The decorated function must have `request: Request` and `current_user: dict` parameters.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            # Extract request and current_user from kwargs
            request = kwargs.get("request")
            current_user = kwargs.get("current_user")

            if request and current_user:
                content = f"{func.__name__}({kwargs})"
                ip_address = get_client_ip(request)

                async with AsyncSessionLocal() as session:
                    stmt = insert(SmsOperationLog).values(
                        sales_id=current_user["user_id"],
                        operation_type=operation_type,
                        content=content[:512],
                        ip_address=ip_address,
                    )
                    await session.execute(stmt)
                    await session.commit()

            return result
        return wrapper
    return decorator
