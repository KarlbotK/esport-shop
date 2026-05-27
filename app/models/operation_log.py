from datetime import datetime

from sqlalchemy import String, DateTime, func, BigInteger, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SmsOperationLog(Base):
    __tablename__ = "sms_operation_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    sales_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="操作人ID")
    operation_type: Mapped[str] = mapped_column(String(64), nullable=False, comment="操作类型")
    content: Mapped[str | None] = mapped_column(String(512), comment="操作内容")
    ip_address: Mapped[str | None] = mapped_column(String(64), comment="IP地址")
    create_time: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    __table_args__ = (
        Index("idx_sales_id", "sales_id"),
        Index("idx_create_time", "create_time"),
    )
