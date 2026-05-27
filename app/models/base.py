from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    """Mixin that adds create_time and update_time columns."""

    @declared_attr
    def create_time(cls) -> Mapped[datetime]:
        return mapped_column(DateTime, default=func.now(), nullable=False)

    @declared_attr
    def update_time(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime,
            default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )


class SoftDeleteMixin:
    """Mixin that adds a `deleted` column for soft deletes."""

    @declared_attr
    def deleted(cls) -> Mapped[int]:
        return mapped_column(default=0, comment="逻辑删除: 0正常 1已删除")
