from datetime import datetime

from sqlalchemy import String, DateTime, func, BigInteger, Integer, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class PmsSku(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "pms_sku"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    spu_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="关联SPU ID")
    sku_name: Mapped[str] = mapped_column(String(256), nullable=False, comment="规格名称")
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, comment="单价")
    stock: Mapped[int] = mapped_column(Integer, default=0, comment="库存")
    attributes: Mapped[str | None] = mapped_column(String(512), comment="规格属性JSON")

    __table_args__ = (
        Index("idx_spu_id", "spu_id"),
    )
