from datetime import datetime

from sqlalchemy import String, DateTime, func, BigInteger, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class UmsLoginLog(Base):
    __tablename__ = "ums_login_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="用户ID")
    login_time: Mapped[datetime] = mapped_column(DateTime, default=func.now(), comment="登录时间")
    ip_address: Mapped[str | None] = mapped_column(String(64), comment="IP地址")

    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_login_time", "login_time"),
    )
