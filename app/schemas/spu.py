from typing import Optional
from pydantic import Field

from app.schemas.common import CommonBase


class SkuVO(CommonBase):
    id: int
    spu_id: int
    sku_name: str
    price: float
    stock: int
    attributes: Optional[str] = None


class SpuDetailVO(CommonBase):
    spu_id: int = Field(alias="spuId")
    spu_name: str = Field(alias="spuName")
    category_id: Optional[int] = Field(default=None, alias="categoryId")
    brand_id: Optional[int] = Field(default=None, alias="brandId")
    description: Optional[str] = None
    sku_list: list[SkuVO] = Field(default_factory=list, alias="skuList")


class HotProductVO(CommonBase):
    spu_id: int = Field(alias="spuId")
    spu_name: str = Field(alias="spuName")
    category_id: Optional[int] = Field(default=None, alias="categoryId")
    brand_name: str = Field(default="", alias="brandName")
    min_price: float = Field(default=0, alias="minPrice")
    browse_count: int = Field(default=0, alias="browseCount")


class SpuListVO(CommonBase):
    id: int
    name: str
    category_id: int = Field(alias="categoryId")
    brand_id: int = Field(alias="brandId")
    description: Optional[str] = None
    publish_status: int = Field(alias="publishStatus")
    create_time: Optional[str] = Field(default=None, alias="createTime")
