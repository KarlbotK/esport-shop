from typing import Optional
from pydantic import Field

from app.schemas.common import CommonBase


class OrderCreateDTO(CommonBase):
    items: list["OrderItemDTO"]

    model_config = {"alias_generator": lambda s: "".join(word.capitalize() if i else word for i, word in enumerate(s.split("_")))}


class OrderItemDTO(CommonBase):
    sku_id: int = Field(alias="skuId")
    quantity: int


class OrderCreateVO(CommonBase):
    order_id: int = Field(alias="orderId")


class OrderItemVO(CommonBase):
    id: int
    sku_id: int = Field(alias="skuId")
    quantity: int
    price: float
    sku_name: Optional[str] = Field(default=None, alias="skuName")


class OrderVO(CommonBase):
    id: int
    user_id: int = Field(alias="userId")
    total_amount: float = Field(alias="totalAmount")
    status: int
    create_time: Optional[str] = Field(default=None, alias="createTime")
    items: list[OrderItemVO] = Field(default_factory=list)
