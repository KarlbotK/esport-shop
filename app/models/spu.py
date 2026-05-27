from datetime import datetime

from sqlalchemy import String, DateTime, func, BigInteger, Integer, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class PmsSpu(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "pms_spu"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False, comment="商品名称")
    category_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="分类ID")
    brand_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="品牌ID")
    description: Mapped[str | None] = mapped_column(Text, comment="图文详情")
    publish_status: Mapped[int] = mapped_column(Integer, default=1, comment="上架状态: 0下架 1上架")

    __table_args__ = (
        Index("idx_category", "category_id"),
        Index("idx_brand", "brand_id"),
    )
