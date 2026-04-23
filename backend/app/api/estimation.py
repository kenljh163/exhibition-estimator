"""
概算相关API
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import (
    EstimationRequest, EstimationResponse,
    HALL_TYPE_MAP, LEVEL_MAP, CITY_LEVEL_MAP
)
from app.services.estimation import calculate_estimation
from app.services.pdf_service import generate_pdf_report
from app.services.poster_service import generate_poster
from app.services.ai_advice_service import generate_budget_advice
from app.models.models import EstimationRecord, ShareToken, LeadContact
import json
import uuid
from datetime import datetime, timedelta

router = APIRouter(prefix="/api", tags=["estimation"])


@router.post("/estimate")
async def create_estimation(req: EstimationRequest, db: Session = Depends(get_db)):
    """
    执行展厅概算
    """
    result = calculate_estimation(db, req)

    # 保存估价记录
    record = EstimationRecord(
        hall_type=req.hall_type,
        area=req.area,
        city_level=req.city_level,
        level=req.level,
        schedule_days=req.schedule_days,
        exhibit_items=json.dumps(req.exhibit_items) if req.exhibit_items else None,
        total_min=result.total.min,
        total_max=result.total.max,
        unit_min=result.unit_price.min,
        unit_max=result.unit_price.max,
        detail=json.dumps([d.model_dump() for d in result.details], ensure_ascii=False),
        contact_name=req.contact_name,
        contact_phone=req.contact_phone,
        contact_company=req.contact_company,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # 将record_id附加到返回结果
    result_dict = result.model_dump()
    result_dict['record_id'] = record.id

    return result_dict


@router.post("/estimate-pdf")
async def create_estimation_pdf(req: EstimationRequest, db: Session = Depends(get_db)):
    """
    执行概算并返回PDF报告
    """
    result = calculate_estimation(db, req)

    # 保存估价记录
    record = EstimationRecord(
        hall_type=req.hall_type,
        area=req.area,
        city_level=req.city_level,
        level=req.level,
        schedule_days=req.schedule_days,
        exhibit_items=json.dumps(req.exhibit_items) if req.exhibit_items else None,
        total_min=result.total.min,
        total_max=result.total.max,
        unit_min=result.unit_price.min,
        unit_max=result.unit_price.max,
        detail=json.dumps([d.model_dump() for d in result.details], ensure_ascii=False),
        contact_name=req.contact_name,
        contact_phone=req.contact_phone,
        contact_company=req.contact_company,
    )
    db.add(record)
    db.commit()

    # 生成PDF
    result_dict = result.model_dump()
    result_dict['exhibit_details'] = result.exhibit_details
    pdf_bytes = generate_pdf_report(result_dict)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=exhibition-estimate-report.pdf"
        }
    )


@router.get("/dictionaries")
async def get_dictionaries():
    """
    获取所有字典数据（展厅类型、档次、城市等级、工期选项等）
    """
    exhibit_keys = [
        {"key": "digital_sandtable", "name": "数字沙盘"},
        {"key": "interactive_wall", "name": "多媒体互动墙"},
        {"key": "hologram", "name": "全息投影"},
        {"key": "ar_vr", "name": "AR/VR体验区"},
        {"key": "smart_control", "name": "智能中控系统"},
        {"key": "voice_guide", "name": "语音导览系统"},
        {"key": "immersive_space", "name": "环幕/沉浸式空间"},
        {"key": "e_book", "name": "电子翻书"},
    ]

    return {
        "hall_types": [{"key": k, "name": v} for k, v in HALL_TYPE_MAP.items()],
        "levels": [{"key": k, "name": v} for k, v in LEVEL_MAP.items()],
        "city_levels": [{"key": k, "name": v} for k, v in CITY_LEVEL_MAP.items()],
        "schedule_options": [
            {"days": 30, "label": "30天（极紧）"},
            {"days": 45, "label": "45天（较紧）"},
            {"days": 60, "label": "60天（正常）"},
            {"days": 90, "label": "90天（充裕）"},
            {"days": 120, "label": "120天（宽松）"},
        ],
        "exhibit_items": exhibit_keys,
    }


# ============ 分享链接 ============

class ShareCreateRequest(BaseModel):
    record_id: int


class LeadSubmitRequest(BaseModel):
    name: str
    phone: str
    company: Optional[str] = ""
    remark: Optional[str] = ""


@router.post("/share/create")
async def create_share_link(data: ShareCreateRequest, db: Session = Depends(get_db)):
    """
    为估价记录生成唯一分享链接（有效期30天）
    """
    record = db.query(EstimationRecord).filter(EstimationRecord.id == data.record_id).first()
    if not record:
        raise HTTPException(404, "估价记录不存在")

    # 生成唯一token
    token = uuid.uuid4().hex[:24]
    share = ShareToken(
        token=token,
        record_id=data.record_id,
        is_active=1,
        view_count=0,
        expires_at=datetime.now() + timedelta(days=30),
    )
    db.add(share)
    db.commit()

    return {"token": token, "url": f"/share/{token}"}


@router.get("/share/{token}")
async def get_share_data(token: str, db: Session = Depends(get_db)):
    """
    通过分享token获取估价结果数据
    """
    share = db.query(ShareToken).filter(
        ShareToken.token == token,
        ShareToken.is_active == 1,
    ).first()

    if not share:
        raise HTTPException(404, "分享链接不存在或已失效")

    # 检查过期
    if share.expires_at and share.expires_at < datetime.now():
        share.is_active = 0
        db.commit()
        raise HTTPException(410, "分享链接已过期")

    # 增加浏览次数
    share.view_count += 1
    db.commit()

    # 获取估价记录
    record = db.query(EstimationRecord).filter(EstimationRecord.id == share.record_id).first()
    if not record:
        raise HTTPException(404, "估价记录不存在")

    # 解析明细数据
    detail = []
    if record.detail:
        try:
            detail = json.loads(record.detail) if isinstance(record.detail, str) else record.detail
        except:
            pass

    exhibit_items_selected = []
    if record.exhibit_items:
        try:
            exhibit_items_selected = json.loads(record.exhibit_items) if isinstance(record.exhibit_items, str) else record.exhibit_items
        except:
            pass

    # 展项名称映射
    exhibit_name_map = {
        "digital_sandtable": "数字沙盘", "interactive_wall": "多媒体互动墙",
        "hologram": "全息投影", "ar_vr": "AR/VR体验区",
        "smart_control": "智能中控系统", "voice_guide": "语音导览系统",
        "immersive_space": "环幕/沉浸式空间", "e_book": "电子翻书",
    }

    exhibit_details = []
    if exhibit_items_selected:
        dicts = await get_dictionaries()
        for ek in exhibit_items_selected:
            name = exhibit_name_map.get(ek, ek)
            # 简单估算展项价格区间
            exhibit_details.append({
                "name": name,
                "range": {"min": 50000, "max": 200000},
            })

    return {
        "share_id": share.id,
        "hall_type_name": HALL_TYPE_MAP.get(record.hall_type, record.hall_type),
        "area": record.area,
        "city_level_name": CITY_LEVEL_MAP.get(record.city_level, record.city_level),
        "level_name": LEVEL_MAP.get(record.level, record.level),
        "schedule_days": record.schedule_days,
        "total_min": record.total_min,
        "total_max": record.total_max,
        "unit_min": record.unit_min,
        "unit_max": record.unit_max,
        "details": detail,
        "exhibit_details": exhibit_details,
        "created_at": str(record.created_at),
        "brand": {
            "company": "三川田股份 832545",
            "phone": "400-888-6363",
            "website": "trf.333f.com",
            "desc": "深耕数字展厅20年，为政府、企业提供一站式展厅解决方案",
        },
    }


@router.post("/share/{token}/lead")
async def submit_lead(token: str, data: LeadSubmitRequest, db: Session = Depends(get_db)):
    """
    客户通过分享链接提交留资信息
    """
    share = db.query(ShareToken).filter(
        ShareToken.token == token,
        ShareToken.is_active == 1,
    ).first()

    if not share:
        raise HTTPException(404, "分享链接不存在或已失效")

    lead = LeadContact(
        share_token_id=share.id,
        record_id=share.record_id,
        name=data.name,
        phone=data.phone,
        company=data.company or "",
        remark=data.remark or "",
    )
    db.add(lead)
    db.commit()

    return {"message": "提交成功，我们的顾问将尽快与您联系", "lead_id": lead.id}


@router.get("/share/{token}/poster")
async def get_share_poster(
    token: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    生成分享海报图（带二维码）
    """
    share = db.query(ShareToken).filter(
        ShareToken.token == token,
        ShareToken.is_active == 1,
    ).first()

    if not share:
        raise HTTPException(404, "分享链接不存在或已失效")

    # 获取估价记录
    record = db.query(EstimationRecord).filter(EstimationRecord.id == share.record_id).first()
    if not record:
        raise HTTPException(404, "估价记录不存在")

    # 构建分享数据
    detail = []
    if record.detail:
        try:
            detail = json.loads(record.detail) if isinstance(record.detail, str) else record.detail
        except:
            pass

    share_data = {
        "hall_type_name": HALL_TYPE_MAP.get(record.hall_type, record.hall_type),
        "area": record.area,
        "city_level_name": CITY_LEVEL_MAP.get(record.city_level, record.city_level),
        "level_name": LEVEL_MAP.get(record.level, record.level),
        "schedule_days": record.schedule_days,
        "total_min": record.total_min,
        "total_max": record.total_max,
        "unit_min": record.unit_min,
        "unit_max": record.unit_max,
        "details": detail,
    }

    # 构建完整分享URL（Nginx反向代理，必须用外部地址）
    share_url = f"http://47.121.115.81:8091/share/{token}"

    # 生成海报
    poster_bytes = generate_poster(share_data, share_url)

    return Response(
        content=poster_bytes,
        media_type="image/png",
        headers={
            "Content-Disposition": "inline; filename=share-poster.png"
        }
    )


# ============ 预算对比 & AI智能建议 ============

class BudgetCompareRequest(BaseModel):
    record_id: int
    budget: float  # 客户预算（元）


@router.post("/budget-compare")
async def compare_budget(data: BudgetCompareRequest, db: Session = Depends(get_db)):
    """
    预算对比分析 + AI智能调优建议
    客户有预算时，对比概算结果给出可行性判断和调整建议
    """
    record = db.query(EstimationRecord).filter(EstimationRecord.id == data.record_id).first()
    if not record:
        raise HTTPException(404, "估价记录不存在")

    # 解析明细数据
    details = []
    if record.detail:
        try:
            details = json.loads(record.detail) if isinstance(record.detail, str) else record.detail
        except:
            pass

    # 构建概算数据
    estimation_data = {
        "total": {"min": record.total_min, "max": record.total_max},
        "unit_price": {"min": record.unit_min, "max": record.unit_max},
        "details": details,
        "params": {
            "hall_type": record.hall_type,
            "hall_type_name": HALL_TYPE_MAP.get(record.hall_type, record.hall_type),
            "area": record.area,
            "city_level": record.city_level,
            "city_level_name": CITY_LEVEL_MAP.get(record.city_level, record.city_level),
            "level": record.level,
            "level_name": LEVEL_MAP.get(record.level, record.level),
            "schedule_days": record.schedule_days,
        },
    }

    # 调用AI建议服务
    result = await generate_budget_advice(data.budget, estimation_data)

    return result
