from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, UniqueConstraint
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class PriceParam(Base):
    """单价参数表 - 各类型×档次的基础单价"""
    __tablename__ = "price_params"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hall_type = Column(String(50), nullable=False, comment="展厅类型")
    level = Column(String(20), nullable=False, comment="档次: economy/standard/premium")
    decoration_unit = Column(Float, default=0, comment="装修单价(元/㎡)")
    exhibition_unit = Column(Float, default=0, comment="展陈制作单价(元/㎡)")
    light_sound_unit = Column(Float, default=0, comment="灯光音响单价(元/㎡)")
    design_rate = Column(Float, default=0.10, comment="设计费率")
    tax_manage_rate = Column(Float, default=0.18, comment="税管费率")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class CityCoefficient(Base):
    """城市系数表"""
    __tablename__ = "city_coefficients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    city_level = Column(String(20), nullable=False, comment="城市等级: tier1/tier2/tier3/tier4")
    coefficient = Column(Float, default=1.0, comment="成本系数")
    cities = Column(Text, default="", comment="包含城市列表，逗号分隔")


class ScheduleCoefficient(Base):
    """工期加价系数表"""
    __tablename__ = "schedule_coefficients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    days = Column(Integer, nullable=False, comment="工期天数")
    coefficient = Column(Float, default=1.0, comment="加价系数")


class ExhibitItem(Base):
    """附加展项参考价表"""
    __tablename__ = "exhibit_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_name = Column(String(100), nullable=False, comment="展项名称")
    item_key = Column(String(50), nullable=False, comment="展项标识key")
    level = Column(String(20), nullable=False, comment="档次")
    price_min = Column(Float, default=0, comment="最低参考价(万元)")
    price_max = Column(Float, default=0, comment="最高参考价(万元)")
    unit = Column(String(20), default="项", comment="计价单位")
    description = Column(Text, default="", comment="说明")
    sort_order = Column(Integer, default=0, comment="排序")
    is_active = Column(Integer, default=1, comment="是否启用")

    __table_args__ = (
        UniqueConstraint('item_key', 'level', name='uq_exhibit_item_key_level'),
    )


class Supplier(Base):
    """供应商表 - B阶段数据接口预留"""
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, comment="供应商名称")
    category = Column(String(100), comment="供应类别: 装修/多媒体/展具/灯光/软件等")
    contact_name = Column(String(100), comment="联系人")
    contact_phone = Column(String(50), comment="联系电话")
    city = Column(String(50), comment="所在城市")
    cooperation_level = Column(String(20), default="normal", comment="合作等级: strategic/preferred/normal")
    rating = Column(Float, default=3.0, comment="评分1-5")
    is_active = Column(Integer, default=1, comment="是否启用")
    remark = Column(Text, default="", comment="备注")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Product(Base):
    """产品/材料库 - B阶段数据接口预留"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, comment="产品/材料名称")
    category = Column(String(100), comment="类别")
    brand = Column(String(100), comment="品牌")
    model = Column(String(200), comment="型号")
    unit = Column(String(20), default="个", comment="单位")
    unit_price = Column(Float, default=0, comment="单价")
    min_order_qty = Column(Integer, default=1, comment="最小起订量")
    lead_time_days = Column(Integer, default=7, comment="供货周期(天)")
    supplier_id = Column(Integer, comment="关联供应商ID")
    specification = Column(Text, default="", comment="规格说明")
    is_active = Column(Integer, default=1, comment="是否启用")
    remark = Column(Text, default="", comment="备注")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class SupplierQuote(Base):
    """供应商报价记录 - 对接三川田供应链"""
    __tablename__ = "supplier_quotes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(Integer, nullable=False, comment="供应商ID")
    product_id = Column(Integer, comment="产品ID")
    category = Column(String(100), comment="报价类别")
    item_name = Column(String(200), comment="报价项目名称")
    specification = Column(Text, default="", comment="规格要求")
    unit_price = Column(Float, default=0, comment="单价")
    quantity = Column(Integer, default=1, comment="数量")
    total_price = Column(Float, default=0, comment="总价")
    valid_until = Column(DateTime, comment="报价有效期")
    project_type = Column(String(50), comment="适用项目类型")
    city_scope = Column(String(200), comment="适用城市范围")
    remark = Column(Text, default="", comment="备注")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class EstimationRecord(Base):
    """估价记录表"""
    __tablename__ = "estimation_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hall_type = Column(String(50), comment="展厅类型")
    area = Column(Float, comment="面积(㎡)")
    city_level = Column(String(20), comment="城市等级")
    level = Column(String(20), comment="档次")
    schedule_days = Column(Integer, comment="工期天数")
    exhibit_items = Column(JSON, comment="选择的展项JSON")
    total_min = Column(Float, comment="最低概算(元)")
    total_max = Column(Float, comment="最高概算(元)")
    unit_min = Column(Float, comment="最低单价(元/㎡)")
    unit_max = Column(Float, comment="最高单价(元/㎡)")
    detail = Column(JSON, comment="分项明细JSON")
    contact_name = Column(String(100), comment="联系人")
    contact_phone = Column(String(20), comment="联系电话")
    contact_company = Column(String(200), comment="联系人公司")
    source = Column(String(20), default="web", comment="来源: web/miniapp/admin")
    created_at = Column(DateTime, default=datetime.now)


class ShareToken(Base):
    """分享链接表"""
    __tablename__ = "share_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(32), unique=True, nullable=False, index=True, comment="唯一分享token")
    record_id = Column(Integer, nullable=False, comment="关联估价记录ID")
    is_active = Column(Integer, default=1, comment="是否有效")
    view_count = Column(Integer, default=0, comment="浏览次数")
    expires_at = Column(DateTime, comment="过期时间")
    created_at = Column(DateTime, default=datetime.now)


class LeadContact(Base):
    """客户留资表"""
    __tablename__ = "lead_contacts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    share_token_id = Column(Integer, comment="关联分享token ID")
    record_id = Column(Integer, nullable=False, comment="关联估价记录ID")
    name = Column(String(100), nullable=False, comment="客户姓名")
    phone = Column(String(20), nullable=False, comment="联系电话")
    company = Column(String(200), comment="公司名称")
    remark = Column(Text, default="", comment="备注/需求说明")
    created_at = Column(DateTime, default=datetime.now)
