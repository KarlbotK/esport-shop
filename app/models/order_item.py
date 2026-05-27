from sqlalchemy import BigInteger, Integer, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SoftDeleteMixin


class OmsOrderItem(Base, SoftDeleteMixin):
    __tablename__ = "oms_order_item"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="订单ID")
    sku_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="SKU ID")
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, comment="数量")
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, comment="下单时单价")

    __table_args__ = (
        Index("idx_order_id", "order_id"),
    )
