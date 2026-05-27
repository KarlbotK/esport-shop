from datetime import datetime

from sqlalchemy import String, DateTime, func, BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class PmsCategory(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "pms_category"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="分类名称")
    parent_id: Mapped[int] = mapped_column(BigInteger, default=0, comment="父分类ID")
    sort: Mapped[int] = mapped_column(Integer, default=0, comment="排序")
