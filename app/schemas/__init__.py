from typing import Optional
from pydantic import Field
from datetime import datetime

from app.schemas.common import CommonBase


class RecommendRequestDTO(CommonBase):
    message: str


class RecommendVO(CommonBase):
    reply: str
    product_ids: str = Field(default="", alias="productIds")


class CategoryVO(CommonBase):
    id: int
    name: str
    parent_id: int = Field(alias="parentId")
    sort: int


class BrandVO(CommonBase):
    id: int
    name: str
    logo_url: Optional[str] = Field(default=None, alias="logoUrl")
    description: Optional[str] = None


class BrowseLogVO(CommonBase):
    id: int
    user_id: Optional[int] = Field(default=None, alias="userId")
    spu_id: int = Field(alias="spuId")
    spu_name: str = Field(default="", alias="spuName")
    duration_seconds: int = Field(default=0, alias="durationSeconds")
    ip_address: Optional[str] = Field(default=None, alias="ipAddress")
    create_time: Optional[str] = Field(default=None, alias="createTime")


class DashboardVO(CommonBase):
    spu_count: int = Field(default=0, alias="spuCount")
    sku_count: int = Field(default=0, alias="skuCount")
    browse_count: int = Field(default=0, alias="browseCount")
    hot_ranking: list = Field(default_factory=list, alias="hotRanking")


class SalesReportVO(CommonBase):
    period: str
    period_label: str = Field(alias="periodLabel")
    revenue: float
    order_count: int = Field(alias="orderCount")


class RankingVO(CommonBase):
    sku_id: int = Field(alias="skuId")
    sku_name: str = Field(alias="skuName")
    spu_name: str = Field(alias="spuName")
    quantity: int
    revenue: float


class AnomalyVO(CommonBase):
    mean: float
    stddev: float
    upper_bound: float = Field(alias="upperBound")
    lower_bound: float = Field(alias="lowerBound")
    anomalies: list["AnomalyItemVO"] = Field(default_factory=list)


class AnomalyItemVO(CommonBase):
    date: str
    revenue: float
    type: str


class SalesUserVO(CommonBase):
    id: int
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    create_time: Optional[str] = Field(default=None, alias="createTime")


class SpuCreateDTO(CommonBase):
    name: str
    category_id: int = Field(alias="categoryId")
    brand_id: int = Field(alias="brandId")
    description: Optional[str] = None
    publish_status: int = Field(default=1, alias="publishStatus")


class SpuUpdateDTO(SpuCreateDTO):
    pass


class CategoryCreateDTO(CommonBase):
    name: str
    parent_id: int = Field(default=0, alias="parentId")
    sort: int = 0


class SalesCreateDTO(CommonBase):
    username: str
    password: str
    email: Optional[str] = None
    phone: Optional[str] = None


class SalesCreateVO(CommonBase):
    id: int
    username: str


class SeckillVO(CommonBase):
    status: str
    message: str
