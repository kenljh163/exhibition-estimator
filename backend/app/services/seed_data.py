"""
种子数据 - 初始化城市系数、工期系数等
"""
from sqlalchemy import select, func
from app.models.models import CityCoefficient, ScheduleCoefficient, ExhibitItem, PriceParam


def seed_initial_data(db_session):
    """填充初始参考数据"""
    # 城市系数
    if db_session.scalar(select(func.count()).select_from(CityCoefficient)) == 0:
        city_data = [
            CityCoefficient(city_level="tier1", coefficient=1.20, cities="北京,上海,深圳,广州"),
            CityCoefficient(city_level="tier2", coefficient=1.10, cities="成都,杭州,武汉,南京,重庆,天津,苏州,西安,长沙,沈阳,青岛,郑州,大连,厦门"),
            CityCoefficient(city_level="tier3", coefficient=1.00, cities="昆明,贵阳,南宁,合肥,济南,福州,太原,石家庄,长春,哈尔滨,南昌,温州,无锡,佛山,东莞,宁波"),
            CityCoefficient(city_level="tier4", coefficient=0.85, cities="其他城市"),
        ]
        db_session.add_all(city_data)

    # 工期系数
    if db_session.scalar(select(func.count()).select_from(ScheduleCoefficient)) == 0:
        schedule_data = [
            ScheduleCoefficient(days=30, coefficient=1.50),
            ScheduleCoefficient(days=45, coefficient=1.30),
            ScheduleCoefficient(days=60, coefficient=1.15),
            ScheduleCoefficient(days=90, coefficient=1.05),
            ScheduleCoefficient(days=120, coefficient=1.00),
        ]
        db_session.add_all(schedule_data)

    # 附加展项参考价
    if db_session.scalar(select(func.count()).select_from(ExhibitItem)) == 0:
        exhibit_data = [
            # 数字沙盘
            ExhibitItem(item_name="数字沙盘", item_key="digital_sandtable", level="economy", price_min=8, price_max=15, unit="项", sort_order=1),
            ExhibitItem(item_name="数字沙盘", item_key="digital_sandtable", level="standard", price_min=15, price_max=30, unit="项", sort_order=1),
            ExhibitItem(item_name="数字沙盘", item_key="digital_sandtable", level="premium", price_min=30, price_max=80, unit="项", sort_order=1),
            # 多媒体互动墙
            ExhibitItem(item_name="多媒体互动墙", item_key="interactive_wall", level="economy", price_min=5, price_max=10, unit="项", sort_order=2),
            ExhibitItem(item_name="多媒体互动墙", item_key="interactive_wall", level="standard", price_min=10, price_max=25, unit="项", sort_order=2),
            ExhibitItem(item_name="多媒体互动墙", item_key="interactive_wall", level="premium", price_min=25, price_max=60, unit="项", sort_order=2),
            # 全息投影
            ExhibitItem(item_name="全息投影", item_key="hologram", level="economy", price_min=10, price_max=20, unit="项", sort_order=3),
            ExhibitItem(item_name="全息投影", item_key="hologram", level="standard", price_min=20, price_max=50, unit="项", sort_order=3),
            ExhibitItem(item_name="全息投影", item_key="hologram", level="premium", price_min=50, price_max=120, unit="项", sort_order=3),
            # AR/VR体验区
            ExhibitItem(item_name="AR/VR体验区", item_key="ar_vr", level="economy", price_min=8, price_max=15, unit="项", sort_order=4),
            ExhibitItem(item_name="AR/VR体验区", item_key="ar_vr", level="standard", price_min=15, price_max=30, unit="项", sort_order=4),
            ExhibitItem(item_name="AR/VR体验区", item_key="ar_vr", level="premium", price_min=30, price_max=80, unit="项", sort_order=4),
            # 智能中控
            ExhibitItem(item_name="智能中控系统", item_key="smart_control", level="economy", price_min=3, price_max=8, unit="套", sort_order=5),
            ExhibitItem(item_name="智能中控系统", item_key="smart_control", level="standard", price_min=8, price_max=15, unit="套", sort_order=5),
            ExhibitItem(item_name="智能中控系统", item_key="smart_control", level="premium", price_min=15, price_max=30, unit="套", sort_order=5),
            # 语音导览
            ExhibitItem(item_name="语音导览系统", item_key="voice_guide", level="economy", price_min=2, price_max=5, unit="套", sort_order=6),
            ExhibitItem(item_name="语音导览系统", item_key="voice_guide", level="standard", price_min=5, price_max=10, unit="套", sort_order=6),
            ExhibitItem(item_name="语音导览系统", item_key="voice_guide", level="premium", price_min=10, price_max=20, unit="套", sort_order=6),
            # 环幕/沉浸式空间
            ExhibitItem(item_name="环幕/沉浸式空间", item_key="immersive_space", level="economy", price_min=20, price_max=40, unit="项", sort_order=7),
            ExhibitItem(item_name="环幕/沉浸式空间", item_key="immersive_space", level="standard", price_min=40, price_max=80, unit="项", sort_order=7),
            ExhibitItem(item_name="环幕/沉浸式空间", item_key="immersive_space", level="premium", price_min=80, price_max=200, unit="项", sort_order=7),
            # 电子翻书
            ExhibitItem(item_name="电子翻书", item_key="e_book", level="economy", price_min=3, price_max=6, unit="项", sort_order=8),
            ExhibitItem(item_name="电子翻书", item_key="e_book", level="standard", price_min=6, price_max=12, unit="项", sort_order=8),
            ExhibitItem(item_name="电子翻书", item_key="e_book", level="premium", price_min=12, price_max=25, unit="项", sort_order=8),
        ]
        db_session.add_all(exhibit_data)

    db_session.commit()
