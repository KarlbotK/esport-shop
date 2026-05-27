from datetime import datetime

from sqlalchemy import String, DateTime, func, BigInteger, Integer, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class OmsOrder(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "oms_order"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="用户ID")
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, comment="订单总金额")
    status: Mapped[int] = mapped_column(Integer, default=0, comment="0待付款 1已付款 2已发货 3已完成 4已取消")

    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_status", "status"),
    )
