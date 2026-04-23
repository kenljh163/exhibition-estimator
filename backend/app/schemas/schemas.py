from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime


# ============ 请求模型 ============

class EstimationRequest(BaseModel):
    """概算请求"""
    hall_type: str = Field(..., description="展厅类型: enterprise/tech/government/museum/commercial/industrial")
    area: float = Field(..., gt=0, description="展厅面积(㎡)")
    city_level: str = Field(..., description="城市等级: tier1/tier2/tier3/tier4")
    level: str = Field("standard", description="档次: economy/standard/premium")
    schedule_days: int = Field(60, description="工期天数")
    exhibit_items: List[str] = Field(default_factory=list, description="附加展项key列表")
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_company: Optional[str] = None


# ============ 响应模型 ============

class RangeValue(BaseModel):
    """区间值"""
    min: float
    max: float


class DetailItem(BaseModel):
    """分项明细"""
    name: str
    range: RangeValue
    percent: float


class EstimationResponse(BaseModel):
    """概算响应"""
    total: RangeValue
    unit_price: RangeValue
    details: List[DetailItem]
    exhibit_details: List[dict]
    params: dict
    note: str = "以上为市场参考价区间，最终报价以实际方案为准"


class SimpleResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[Union[dict, list]] = None


# ============ 管理后台模型 ============

class PriceParamCreate(BaseModel):
    hall_type: str
    level: str
    decoration_unit: float = 0
    exhibition_unit: float = 0
    light_sound_unit: float = 0
    design_rate: float = 0.10
    tax_manage_rate: float = 0.18


class PriceParamUpdate(BaseModel):
    decoration_unit: Optional[float] = None
    exhibition_unit: Optional[float] = None
    light_sound_unit: Optional[float] = None
    design_rate: Optional[float] = None
    tax_manage_rate: Optional[float] = None


class ExhibitItemCreate(BaseModel):
    item_name: str
    item_key: str
    level: str
    price_min: float = 0
    price_max: float = 0
    unit: str = "项"
    description: str = ""
    sort_order: int = 0


class ExhibitItemUpdate(BaseModel):
    item_name: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    unit: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[int] = None


class SupplierCreate(BaseModel):
    name: str
    category: str = ""
    contact_name: str = ""
    contact_phone: str = ""
    city: str = ""
    cooperation_level: str = "normal"
    rating: float = 3.0
    remark: str = ""


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    city: Optional[str] = None
    cooperation_level: Optional[str] = None
    rating: Optional[float] = None
    is_active: Optional[int] = None
    remark: Optional[str] = None


class ProductCreate(BaseModel):
    name: str
    category: str = ""
    brand: str = ""
    model: str = ""
    unit: str = "个"
    unit_price: float = 0
    min_order_qty: int = 1
    lead_time_days: int = 7
    supplier_id: Optional[int] = None
    specification: str = ""
    remark: str = ""


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    min_order_qty: Optional[int] = None
    lead_time_days: Optional[int] = None
    supplier_id: Optional[int] = None
    specification: Optional[str] = None
    is_active: Optional[int] = None
    remark: Optional[str] = None


class SupplierQuoteCreate(BaseModel):
    supplier_id: int
    product_id: Optional[int] = None
    category: str = ""
    item_name: str = ""
    specification: str = ""
    unit_price: float = 0
    quantity: int = 1
    total_price: float = 0
    valid_until: Optional[str] = None
    project_type: str = ""
    city_scope: str = ""
    remark: str = ""


class SupplierQuoteUpdate(BaseModel):
    unit_price: Optional[float] = None
    quantity: Optional[int] = None
    total_price: Optional[float] = None
    valid_until: Optional[str] = None
    remark: Optional[str] = None


# ============ 字典映射 ============

HALL_TYPE_MAP = {
    "enterprise": "企业馆",
    "tech": "科技馆",
    "government": "政府馆",
    "museum": "博物馆",
    "commercial": "商业空间",
    "industrial": "产业园区",
}

LEVEL_MAP = {
    "economy": "经济型",
    "standard": "标准型",
    "premium": "高端定制",
}

CITY_LEVEL_MAP = {
    "tier1": "一线城市",
    "tier2": "新一线城市",
    "tier3": "二线城市",
    "tier4": "三线及以下",
}
