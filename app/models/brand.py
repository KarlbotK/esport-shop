from datetime import datetime

from sqlalchemy import String, DateTime, func, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class PmsBrand(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "pms_brand"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="品牌名称")
    logo_url: Mapped[str | None] = mapped_column(String(256), comment="Logo地址")
    description: Mapped[str | None] = mapped_column(String(512), comment="品牌描述")
