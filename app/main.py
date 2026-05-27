"""ShopAgent FastAPI Application — Main Entry Point.

Rewrite of the original Spring Boot + MyBatis-Plus + Redis + Kafka backend
into a lightweight Python/FastAPI stack.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import engine
from app.routers import user, spu, category, order, seckill, recommend, sales, admin
from app.middleware.browse_log import track_browse_middleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Scheduler reference
scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup tasks + graceful shutdown."""
    global scheduler

    logger.info("Starting ShopAgent backend...")

    # Start APScheduler
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        scheduler = AsyncIOScheduler()

        # Register jobs
        from app.background.jobs import refresh_hot_ranking, compute_item_similarity

        scheduler.add_job(
            refresh_hot_ranking,
            trigger="cron",
            minute=30,
            hour="*",
            id="refresh_hot_ranking",
            replace_existing=True,
            name="Hot ranking refresh (hourly at :30)",
        )
        scheduler.add_job(
            compute_item_similarity,
            trigger="cron",
            hour=3,
            minute=0,
            id="compute_item_similarity",
            replace_existing=True,
            name="Collaborative filtering rebuild (daily 3 AM)",
        )

        scheduler.start()
        logger.info("APScheduler started with 2 jobs")
    except Exception as e:
        logger.warning(f"APScheduler not available or failed to start: {e}")

    yield  # App runs here

    # Shutdown
    logger.info("Shutting down ShopAgent backend...")
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
    await engine.dispose()
    logger.info("Shutdown complete")


app = FastAPI(
    title="ShopAgent API",
    description="Esports Equipment E-commerce Platform (Python Rewrite)",
    version="1.0.0",
    lifespan=lifespan,
)

# ─── CORS ────────────────────────────────────────────────────────────────
origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Browse Tracking Middleware ──────────────────────────────────────────
app.middleware("http")(track_browse_middleware)

# ─── Routers ────────────────────────────────────────────────────────────
app.include_router(user.router)
app.include_router(spu.router)
app.include_router(category.router)
app.include_router(order.router)
app.include_router(seckill.router)
app.include_router(recommend.router)
app.include_router(sales.router)
app.include_router(admin.router)


# ─── Exception Handlers ─────────────────────────────────────────────────
class BusinessException(Exception):
    """Business logic exception — returned as HTTP 200 with code=500 in body."""

    def __init__(self, message: str):
        self.message = message


@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    return JSONResponse(
        status_code=200,
        content={"code": 500, "msg": exc.message, "data": None},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all: return HTTP 200 with generic error message."""
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=200,
        content={"code": 500, "msg": "System busy, please try again later", "data": None},
    )


# ─── Health Check ───────────────────────────────────────────────────────
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "ShopAgent"}
