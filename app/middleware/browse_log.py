"""Browse tracking middleware — replaces Kafka producers + ViewLogAspect.

Intercepts SPU detail view requests and records browse logs + user browse history.
"""

import time
import re
from typing import Callable

from fastapi import Request, Response
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.browse_log import PmsBrowseLog
from app.utils.ip import get_client_ip


async def track_browse_middleware(request: Request, call_next: Callable) -> Response:
    """ASGI middleware that tracks GET /api/spu/detail/{id} requests.

    Records browse_log row + updates user browse history.
    """
    start_time = time.time()

    response = await call_next(request)

    # Only track GET /api/spu/detail/{id}
    path = request.url.path
    match = re.match(r"^/api/spu/detail/(\d+)$", path)
    if request.method != "GET" or not match:
        return response

    spu_id = int(match.group(1))
    duration = int(time.time() - start_time)

    # Extract user_id from JWT if present
    user_id = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        from app.security import decode_access_token
        token = auth_header[7:]
        payload = decode_access_token(token)
        if payload:
            user_id = int(payload["sub"])

    ip_address = get_client_ip(request)

    # Write browse log asynchronously
    async with AsyncSessionLocal() as session:
        stmt = insert(PmsBrowseLog).values(
            user_id=user_id,
            spu_id=spu_id,
            duration_seconds=duration,
            ip_address=ip_address,
        )
        await session.execute(stmt)
        await session.commit()

    return response
