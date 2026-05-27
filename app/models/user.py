from datetime import datetime

from sqlalchemy import String, DateTime, func, BigInteger, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class UmsUser(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "ums_user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, comment="用户名")
    password: Mapped[str] = mapped_column(String(256), nullable=False, comment="BCrypt加密密码")
    email: Mapped[str | None] = mapped_column(String(128), comment="邮箱")
    phone: Mapped[str | None] = mapped_column(String(20), comment="手机号")
    role: Mapped[str] = mapped_column(String(20), default="CUSTOMER", comment="角色: CUSTOMER/SALES/ADMIN")

    __table_args__ = (
        Index("idx_role", "role"),
    )
