"""
概算引擎 - 核心计算逻辑
"""
from sqlalchemy.orm import Session
from app.models.models import PriceParam, CityCoefficient, ScheduleCoefficient, ExhibitItem
from app.schemas.schemas import (
    EstimationRequest, EstimationResponse, RangeValue, DetailItem,
    HALL_TYPE_MAP, LEVEL_MAP, CITY_LEVEL_MAP
)
from typing import List, Union


def calculate_estimation(db: Session, req: EstimationRequest) -> EstimationResponse:
    """
    核心概算计算
    总概算 = 基础空间造价 + 展陈制作费 + 多媒体展项费 + 设计费 + 税金及管理费
    """

    # 1. 获取基础单价参数
    price_param = db.query(PriceParam).filter(
        PriceParam.hall_type == req.hall_type,
        PriceParam.level == req.level
    ).first()

    if not price_param:
        # 无数据时使用行业参考默认值
        price_param = PriceParam(
            decoration_unit=_default_decoration(req.hall_type, req.level),
            exhibition_unit=_default_exhibition(req.hall_type, req.level),
            light_sound_unit=_default_light_sound(req.level),
            design_rate=0.10,
            tax_manage_rate=0.18,
        )

    # 2. 获取城市系数
    city_coef = _get_city_coefficient(db, req.city_level)

    # 3. 获取工期加价系数
    schedule_coef = _get_schedule_coefficient(db, req.schedule_days)

    # 4. 计算基础空间造价
    base_decoration = price_param.decoration_unit * req.area
    base_light_sound = price_param.light_sound_unit * req.area

    # 5. 计算展陈制作费
    base_exhibition = price_param.exhibition_unit * req.area

    # 6. 应用系数，生成区间（±10%浮动）
    float_ratio = 0.10
    base_min = (base_decoration + base_exhibition + base_light_sound) * city_coef * schedule_coef * (1 - float_ratio)
    base_max = (base_decoration + base_exhibition + base_light_sound) * city_coef * schedule_coef * (1 + float_ratio)

    # 7. 计算多媒体展项费
    exhibit_total_min = 0.0
    exhibit_total_max = 0.0
    exhibit_details = []
    if req.exhibit_items:
        for item_key in req.exhibit_items:
            exhibit = db.query(ExhibitItem).filter(
                ExhibitItem.item_key == item_key,
                ExhibitItem.level == req.level,
                ExhibitItem.is_active == 1
            ).first()
            if exhibit:
                # 展项价格单位是万元，转成元
                exhibit_min = exhibit.price_min * 10000
                exhibit_max = exhibit.price_max * 10000
                exhibit_total_min += exhibit_min
                exhibit_total_max += exhibit_max
                exhibit_details.append({
                    "name": exhibit.item_name,
                    "range": {"min": exhibit_min, "max": exhibit_max},
                    "unit": exhibit.unit,
                })
            else:
                # 无数据时使用默认值
                default = _default_exhibit_price(item_key, req.level)
                if default:
                    exhibit_total_min += default["min"]
                    exhibit_total_max += default["max"]
                    exhibit_details.append({
                        "name": default["name"],
                        "range": {"min": default["min"], "max": default["max"]},
                        "unit": "项",
                    })

    # 8. 汇总设计费
    design_min = (base_min + exhibit_total_min) * price_param.design_rate
    design_max = (base_max + exhibit_total_max) * price_param.design_rate

    # 9. 汇总税管费
    tax_min = (base_min + exhibit_total_min + design_min) * price_param.tax_manage_rate
    tax_max = (base_max + exhibit_total_max + design_max) * price_param.tax_manage_rate

    # 10. 计算总计
    total_min = base_min + exhibit_total_min + design_min + tax_min
    total_max = base_max + exhibit_total_max + design_max + tax_max

    # 11. 构建分项明细
    subtotal = total_min + total_max
    details = [
        DetailItem(
            name="基础装修（含灯光音响）",
            range=RangeValue(min=round(base_min), max=round(base_max)),
            percent=round((base_min + base_max) / subtotal * 100, 1) if subtotal > 0 else 0
        ),
        DetailItem(
            name="展陈制作",
            range=RangeValue(min=round(base_exhibition * city_coef * schedule_coef * (1 - float_ratio)),
                             max=round(base_exhibition * city_coef * schedule_coef * (1 + float_ratio))),
            percent=round((base_exhibition * city_coef * schedule_coef * 2) / subtotal * 100, 1) if subtotal > 0 else 0
        ),
    ]

    if exhibit_details:
        details.append(DetailItem(
            name="多媒体展项",
            range=RangeValue(min=round(exhibit_total_min), max=round(exhibit_total_max)),
            percent=round((exhibit_total_min + exhibit_total_max) / subtotal * 100, 1) if subtotal > 0 else 0
        ))

    details.append(DetailItem(
        name="设计费",
        range=RangeValue(min=round(design_min), max=round(design_max)),
        percent=round((design_min + design_max) / subtotal * 100, 1) if subtotal > 0 else 0
    ))
    details.append(DetailItem(
        name="税金及管理费",
        range=RangeValue(min=round(tax_min), max=round(tax_max)),
        percent=round((tax_min + tax_max) / subtotal * 100, 1) if subtotal > 0 else 0
    ))

    return EstimationResponse(
        total=RangeValue(min=round(total_min), max=round(total_max)),
        unit_price=RangeValue(
            min=round(total_min / req.area),
            max=round(total_max / req.area)
        ),
        details=details,
        exhibit_details=exhibit_details,
        params={
            "hall_type": req.hall_type,
            "hall_type_name": HALL_TYPE_MAP.get(req.hall_type, req.hall_type),
            "area": req.area,
            "city_level": req.city_level,
            "city_level_name": CITY_LEVEL_MAP.get(req.city_level, req.city_level),
            "level": req.level,
            "level_name": LEVEL_MAP.get(req.level, req.level),
            "schedule_days": req.schedule_days,
            "city_coefficient": city_coef,
            "schedule_coefficient": schedule_coef,
        },
    )


def _get_city_coefficient(db: Session, city_level: str) -> float:
    """获取城市成本系数"""
    coef = db.query(CityCoefficient).filter(CityCoefficient.city_level == city_level).first()
    if coef:
        return coef.coefficient
    # 默认值
    defaults = {"tier1": 1.2, "tier2": 1.1, "tier3": 1.0, "tier4": 0.85}
    return defaults.get(city_level, 1.0)


def _get_schedule_coefficient(db: Session, days: int) -> float:
    """获取工期加价系数"""
    # 找最接近的工期档位
    records = db.query(ScheduleCoefficient).order_by(ScheduleCoefficient.days).all()
    if records:
        # 找到不超过请求天数的最大档位
        matched = 1.0
        for r in records:
            if r.days >= days:
                matched = r.coefficient
                break
            matched = r.coefficient
        return matched
    # 默认值
    defaults = [(30, 1.50), (45, 1.30), (60, 1.15), (90, 1.05), (120, 1.0)]
    result = 1.0
    for d, c in defaults:
        if d >= days:
            result = c
            break
        result = c
    return result


def _default_decoration(hall_type: str, level: str) -> float:
    """默认装修单价（元/㎡），待老刘提供真实数据后替换"""
    base = {
        "enterprise": 1500, "tech": 2000, "government": 1800,
        "museum": 2200, "commercial": 1200, "industrial": 1000,
    }
    multiplier = {"economy": 0.7, "standard": 1.0, "premium": 1.8}
    return base.get(hall_type, 1500) * multiplier.get(level, 1.0)


def _default_exhibition(hall_type: str, level: str) -> float:
    """默认展陈单价（元/㎡），待替换"""
    base = {
        "enterprise": 600, "tech": 800, "government": 700,
        "museum": 900, "commercial": 400, "industrial": 300,
    }
    multiplier = {"economy": 0.6, "standard": 1.0, "premium": 2.0}
    return base.get(hall_type, 600) * multiplier.get(level, 1.0)


def _default_light_sound(level: str) -> float:
    """默认灯光音响单价（元/㎡），待替换"""
    base = {"economy": 200, "standard": 350, "premium": 600}
    return base.get(level, 350)


def _default_exhibit_price(item_key: str, level: str) -> Union[dict, None]:
    """默认展项价格（元），待替换"""
    prices = {
        "digital_sandtable": {"name": "数字沙盘", "economy": (8, 15), "standard": (15, 30), "premium": (30, 80)},
        "interactive_wall": {"name": "多媒体互动墙", "economy": (5, 10), "standard": (10, 25), "premium": (25, 60)},
        "hologram": {"name": "全息投影", "economy": (10, 20), "standard": (20, 50), "premium": (50, 120)},
        "ar_vr": {"name": "AR/VR体验区", "economy": (8, 15), "standard": (15, 30), "premium": (30, 80)},
        "smart_control": {"name": "智能中控系统", "economy": (3, 8), "standard": (8, 15), "premium": (15, 30)},
        "voice_guide": {"name": "语音导览系统", "economy": (2, 5), "standard": (5, 10), "premium": (10, 20)},
        "immersive_space": {"name": "环幕/沉浸式空间", "economy": (20, 40), "standard": (40, 80), "premium": (80, 200)},
        "e_book": {"name": "电子翻书", "economy": (3, 6), "standard": (6, 12), "premium": (12, 25)},
    }
    item = prices.get(item_key)
    if not item:
        return None
    price_range = item.get(level, item.get("standard", (5, 10)))
    return {
        "name": item["name"],
        "min": price_range[0] * 10000,
        "max": price_range[1] * 10000,
    }
