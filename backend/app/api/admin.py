"""
管理后台API - 单价参数、展项、供应商、产品库
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.schemas.schemas import (
    SimpleResponse, PriceParamCreate, PriceParamUpdate,
    ExhibitItemCreate, ExhibitItemUpdate,
    SupplierCreate, SupplierUpdate,
    ProductCreate, ProductUpdate,
    SupplierQuoteCreate, SupplierQuoteUpdate,
    HALL_TYPE_MAP, LEVEL_MAP, CITY_LEVEL_MAP,
)
from app.models.models import (
    PriceParam, ExhibitItem, CityCoefficient, ScheduleCoefficient,
    Supplier, Product, SupplierQuote, EstimationRecord, ShareToken, LeadContact
)
from datetime import datetime

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ============ 单价参数管理 ============

@router.get("/price-params")
async def list_price_params(
    hall_type: Optional[str] = None,
    level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取单价参数列表"""
    query = db.query(PriceParam)
    if hall_type:
        query = query.filter(PriceParam.hall_type == hall_type)
    if level:
        query = query.filter(PriceParam.level == level)
    items = query.all()
    return SimpleResponse(data=[{
        "id": i.id, "hall_type": i.hall_type, "level": i.level,
        "decoration_unit": i.decoration_unit, "exhibition_unit": i.exhibition_unit,
        "light_sound_unit": i.light_sound_unit, "design_rate": i.design_rate,
        "tax_manage_rate": i.tax_manage_rate, "updated_at": str(i.updated_at) if i.updated_at else None,
    } for i in items])


@router.post("/price-params")
async def create_price_param(data: PriceParamCreate, db: Session = Depends(get_db)):
    """创建单价参数"""
    existing = db.query(PriceParam).filter(
        PriceParam.hall_type == data.hall_type,
        PriceParam.level == data.level
    ).first()
    if existing:
        raise HTTPException(400, "该类型×档次组合已存在，请使用更新接口")
    item = PriceParam(**data.model_dump())
    db.add(item)
    db.commit()
    return SimpleResponse(message="创建成功", data={"id": item.id})


@router.put("/price-params/{item_id}")
async def update_price_param(item_id: int, data: PriceParamUpdate, db: Session = Depends(get_db)):
    """更新单价参数"""
    item = db.query(PriceParam).filter(PriceParam.id == item_id).first()
    if not item:
        raise HTTPException(404, "未找到该记录")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    item.updated_at = datetime.now()
    db.commit()
    return SimpleResponse(message="更新成功")


@router.delete("/price-params/{item_id}")
async def delete_price_param(item_id: int, db: Session = Depends(get_db)):
    """删除单价参数"""
    item = db.query(PriceParam).filter(PriceParam.id == item_id).first()
    if not item:
        raise HTTPException(404, "未找到该记录")
    db.delete(item)
    db.commit()
    return SimpleResponse(message="删除成功")


# ============ 展项管理 ============

@router.get("/exhibit-items")
async def list_exhibit_items(
    level: Optional[str] = None,
    is_active: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取展项列表"""
    query = db.query(ExhibitItem)
    if level:
        query = query.filter(ExhibitItem.level == level)
    if is_active is not None:
        query = query.filter(ExhibitItem.is_active == is_active)
    items = query.order_by(ExhibitItem.sort_order).all()
    return SimpleResponse(data=[{
        "id": i.id, "item_name": i.item_name, "item_key": i.item_key,
        "level": i.level, "price_min": i.price_min, "price_max": i.price_max,
        "unit": i.unit, "description": i.description,
        "sort_order": i.sort_order, "is_active": i.is_active,
    } for i in items])


@router.post("/exhibit-items")
async def create_exhibit_item(data: ExhibitItemCreate, db: Session = Depends(get_db)):
    """创建展项"""
    existing = db.query(ExhibitItem).filter(ExhibitItem.item_key == data.item_key, ExhibitItem.level == data.level).first()
    if existing:
        raise HTTPException(400, "该展项×档次组合已存在")
    item = ExhibitItem(**data.model_dump())
    db.add(item)
    db.commit()
    return SimpleResponse(message="创建成功", data={"id": item.id})


@router.put("/exhibit-items/{item_id}")
async def update_exhibit_item(item_id: int, data: ExhibitItemUpdate, db: Session = Depends(get_db)):
    """更新展项"""
    item = db.query(ExhibitItem).filter(ExhibitItem.id == item_id).first()
    if not item:
        raise HTTPException(404, "未找到该记录")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit()
    return SimpleResponse(message="更新成功")


@router.delete("/exhibit-items/{item_id}")
async def delete_exhibit_item(item_id: int, db: Session = Depends(get_db)):
    """删除展项"""
    item = db.query(ExhibitItem).filter(ExhibitItem.id == item_id).first()
    if not item:
        raise HTTPException(404, "未找到该记录")
    db.delete(item)
    db.commit()
    return SimpleResponse(message="删除成功")


# ============ 供应商管理 ============

@router.get("/suppliers")
async def list_suppliers(
    category: Optional[str] = None,
    city: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取供应商列表"""
    query = db.query(Supplier).filter(Supplier.is_active == 1)
    if category:
        query = query.filter(Supplier.category == category)
    if city:
        query = query.filter(Supplier.city == city)
    if keyword:
        query = query.filter(Supplier.name.contains(keyword))
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return SimpleResponse(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [{
            "id": i.id, "name": i.name, "category": i.category,
            "contact_name": i.contact_name, "contact_phone": i.contact_phone,
            "city": i.city, "cooperation_level": i.cooperation_level,
            "rating": i.rating, "remark": i.remark,
        } for i in items]
    })


@router.post("/suppliers")
async def create_supplier(data: SupplierCreate, db: Session = Depends(get_db)):
    """创建供应商"""
    item = Supplier(**data.model_dump())
    db.add(item)
    db.commit()
    return SimpleResponse(message="创建成功", data={"id": item.id})


@router.put("/suppliers/{item_id}")
async def update_supplier(item_id: int, data: SupplierUpdate, db: Session = Depends(get_db)):
    """更新供应商"""
    item = db.query(Supplier).filter(Supplier.id == item_id).first()
    if not item:
        raise HTTPException(404, "未找到该供应商")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    item.updated_at = datetime.now()
    db.commit()
    return SimpleResponse(message="更新成功")


@router.get("/suppliers/{item_id}")
async def get_supplier(item_id: int, db: Session = Depends(get_db)):
    """获取供应商详情（含关联产品和报价）"""
    supplier = db.query(Supplier).filter(Supplier.id == item_id).first()
    if not supplier:
        raise HTTPException(404, "未找到该供应商")
    products = db.query(Product).filter(Product.supplier_id == item_id, Product.is_active == 1).all()
    quotes = db.query(SupplierQuote).filter(SupplierQuote.supplier_id == item_id).order_by(SupplierQuote.created_at.desc()).limit(20).all()
    return SimpleResponse(data={
        "supplier": {
            "id": supplier.id, "name": supplier.name, "category": supplier.category,
            "contact_name": supplier.contact_name, "contact_phone": supplier.contact_phone,
            "city": supplier.city, "cooperation_level": supplier.cooperation_level,
            "rating": supplier.rating, "remark": supplier.remark,
        },
        "products": [{"id": p.id, "name": p.name, "category": p.category, "brand": p.brand,
                       "model": p.model, "unit": p.unit, "unit_price": p.unit_price,
                       "min_order_qty": p.min_order_qty, "lead_time_days": p.lead_time_days,
                       "specification": p.specification} for p in products],
        "recent_quotes": [{"id": q.id, "category": q.category, "item_name": q.item_name,
                           "unit_price": q.unit_price, "quantity": q.quantity, "total_price": q.total_price,
                           "valid_until": str(q.valid_until) if q.valid_until else None,
                           "created_at": str(q.created_at)} for q in quotes],
    })


# ============ 产品库管理 ============

@router.get("/products")
async def list_products(
    category: Optional[str] = None,
    supplier_id: Optional[int] = None,
    keyword: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取产品列表"""
    query = db.query(Product).filter(Product.is_active == 1)
    if category:
        query = query.filter(Product.category == category)
    if supplier_id:
        query = query.filter(Product.supplier_id == supplier_id)
    if keyword:
        query = query.filter(Product.name.contains(keyword))
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return SimpleResponse(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [{
            "id": i.id, "name": i.name, "category": i.category,
            "brand": i.brand, "model": i.model, "unit": i.unit,
            "unit_price": i.unit_price, "min_order_qty": i.min_order_qty,
            "lead_time_days": i.lead_time_days, "supplier_id": i.supplier_id,
            "specification": i.specification, "remark": i.remark,
        } for i in items]
    })


@router.post("/products")
async def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    """创建产品"""
    item = Product(**data.model_dump())
    db.add(item)
    db.commit()
    return SimpleResponse(message="创建成功", data={"id": item.id})


@router.put("/products/{item_id}")
async def update_product(item_id: int, data: ProductUpdate, db: Session = Depends(get_db)):
    """更新产品"""
    item = db.query(Product).filter(Product.id == item_id).first()
    if not item:
        raise HTTPException(404, "未找到该产品")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    item.updated_at = datetime.now()
    db.commit()
    return SimpleResponse(message="更新成功")


# ============ 供应商报价管理 ============

@router.get("/supplier-quotes")
async def list_supplier_quotes(
    supplier_id: Optional[int] = None,
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取供应商报价列表"""
    query = db.query(SupplierQuote)
    if supplier_id:
        query = query.filter(SupplierQuote.supplier_id == supplier_id)
    if category:
        query = query.filter(SupplierQuote.category == category)
    total = query.count()
    items = query.order_by(SupplierQuote.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return SimpleResponse(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [{
            "id": i.id, "supplier_id": i.supplier_id, "product_id": i.product_id,
            "category": i.category, "item_name": i.item_name,
            "specification": i.specification, "unit_price": i.unit_price,
            "quantity": i.quantity, "total_price": i.total_price,
            "valid_until": str(i.valid_until) if i.valid_until else None,
            "project_type": i.project_type, "city_scope": i.city_scope,
            "remark": i.remark, "created_at": str(i.created_at),
        } for i in items]
    })


@router.post("/supplier-quotes")
async def create_supplier_quote(data: SupplierQuoteCreate, db: Session = Depends(get_db)):
    """创建供应商报价"""
    item = SupplierQuote(**data.model_dump())
    db.add(item)
    db.commit()
    return SimpleResponse(message="创建成功", data={"id": item.id})


@router.put("/supplier-quotes/{item_id}")
async def update_supplier_quote(item_id: int, data: SupplierQuoteUpdate, db: Session = Depends(get_db)):
    """更新供应商报价"""
    item = db.query(SupplierQuote).filter(SupplierQuote.id == item_id).first()
    if not item:
        raise HTTPException(404, "未找到该报价")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    item.updated_at = datetime.now()
    db.commit()
    return SimpleResponse(message="更新成功")


# ============ 估价记录 ============

@router.get("/estimation-records")
async def list_estimation_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取估价记录列表"""
    query = db.query(EstimationRecord)
    total = query.count()
    items = query.order_by(EstimationRecord.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return SimpleResponse(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [{
            "id": i.id,
            "hall_type": i.hall_type,
            "hall_type_name": HALL_TYPE_MAP.get(i.hall_type, i.hall_type),
            "area": i.area,
            "city_level": i.city_level,
            "city_level_name": CITY_LEVEL_MAP.get(i.city_level, i.city_level),
            "level": i.level,
            "level_name": LEVEL_MAP.get(i.level, i.level),
            "schedule_days": i.schedule_days,
            "total_min": i.total_min, "total_max": i.total_max,
            "unit_min": i.unit_min, "unit_max": i.unit_max,
            "contact_name": i.contact_name, "contact_phone": i.contact_phone,
            "contact_company": i.contact_company,
            "source": i.source, "created_at": str(i.created_at),
        } for i in items]
    })


@router.get("/statistics")
async def get_statistics(db: Session = Depends(get_db)):
    """获取统计概览"""
    from sqlalchemy import func
    total_records = db.query(func.count(EstimationRecord.id)).scalar() or 0
    total_contacts = db.query(func.count(EstimationRecord.id)).filter(
        EstimationRecord.contact_name.isnot(None)
    ).scalar() or 0
    total_suppliers = db.query(func.count(Supplier.id)).filter(Supplier.is_active == 1).scalar() or 0
    total_products = db.query(func.count(Product.id)).filter(Product.is_active == 1).scalar() or 0

    # 按展厅类型统计
    type_stats = db.query(
        EstimationRecord.hall_type,
        func.count(EstimationRecord.id),
        func.avg(EstimationRecord.total_min),
        func.avg(EstimationRecord.total_max),
    ).group_by(EstimationRecord.hall_type).all()

    return SimpleResponse(data={
        "total_estimations": total_records,
        "total_contacts": total_contacts,
        "total_suppliers": total_suppliers,
        "total_products": total_products,
        "total_leads": db.query(func.count(LeadContact.id)).scalar() or 0,
        "by_hall_type": [{
            "type": s[0], "count": s[1],
            "avg_min": round(s[2]) if s[2] else 0,
            "avg_max": round(s[3]) if s[3] else 0,
        } for s in type_stats],
    })


# ============ 分享链接管理 ============

@router.get("/share-links")
async def list_share_links(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取分享链接列表"""
    query = db.query(ShareToken)
    total = query.count()
    items = query.order_by(ShareToken.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return SimpleResponse(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [{
            "id": s.id, "token": s.token,
            "record_id": s.record_id,
            "is_active": s.is_active,
            "view_count": s.view_count,
            "expires_at": str(s.expires_at) if s.expires_at else None,
            "created_at": str(s.created_at),
        } for s in items]
    })


@router.delete("/share-links/{share_id}")
async def disable_share_link(share_id: int, db: Session = Depends(get_db)):
    """禁用分享链接"""
    share = db.query(ShareToken).filter(ShareToken.id == share_id).first()
    if not share:
        raise HTTPException(404, "未找到该分享链接")
    share.is_active = 0
    db.commit()
    return SimpleResponse(message="已禁用")


# ============ 客户留资 ============

@router.get("/leads")
async def list_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取客户留资列表"""
    query = db.query(LeadContact)
    total = query.count()
    items = query.order_by(LeadContact.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return SimpleResponse(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [{
            "id": l.id,
            "record_id": l.record_id,
            "share_token_id": l.share_token_id,
            "name": l.name,
            "phone": l.phone,
            "company": l.company,
            "remark": l.remark,
            "created_at": str(l.created_at),
        } for l in items]
    })
