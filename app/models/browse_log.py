from datetime import datetime

from sqlalchemy import String, DateTime, func, BigInteger, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PmsBrowseLog(Base):
    __tablename__ = "pms_browse_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(BigInteger, comment="用户ID(未登录为NULL)")
    spu_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="浏览商品ID")
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0, comment="停留时长(秒)")
    ip_address: Mapped[str | None] = mapped_column(String(64), comment="IP地址")
    create_time: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_spu_id", "spu_id"),
        Index("idx_create_time", "create_time"),
    )
