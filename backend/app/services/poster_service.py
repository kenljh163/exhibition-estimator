"""
分享海报生成服务
生成带品牌信息和二维码的估价结果海报图
"""
from PIL import Image, ImageDraw, ImageFont
import qrcode
import io
import math


# 海报尺寸（竖版，适配手机）
POSTER_W = 750
POSTER_H = 1334

# 品牌色
BRAND_BLUE = (0, 90, 160)        # 深蓝
BRAND_LIGHT_BLUE = (0, 140, 220) # 亮蓝
BRAND_DARK = (20, 30, 50)        # 深色背景
BRAND_WHITE = (255, 255, 255)
BRAND_GRAY = (180, 180, 180)
BRAND_GOLD = (218, 175, 100)     # 金色点缀
BG_TOP = (15, 25, 45)
BG_BOTTOM = (25, 40, 65)
CARD_BG = (35, 50, 75)
CARD_BORDER = (60, 85, 120)


def generate_poster(share_data: dict, share_url: str) -> bytes:
    """
    生成分享海报图
    :param share_data: 分享数据（从get_share_data获取）
    :param share_url: 完整分享URL
    :return: PNG图片字节
    """
    img = Image.new("RGB", (POSTER_W, POSTER_H), BG_TOP)
    draw = ImageDraw.Draw(img)

    # 尝试加载中文字体，回退到默认
    font_path = _find_font()
    font_large = ImageFont.truetype(font_path, 42) if font_path else ImageFont.load_default()
    font_medium = ImageFont.truetype(font_path, 30) if font_path else ImageFont.load_default()
    font_small = ImageFont.truetype(font_path, 24) if font_path else ImageFont.load_default()
    font_tiny = ImageFont.truetype(font_path, 20) if font_path else ImageFont.load_default()
    font_price = ImageFont.truetype(font_path, 56) if font_path else ImageFont.load_default()
    font_brand = ImageFont.truetype(font_path, 34) if font_path else ImageFont.load_default()

    # ========= 1. 顶部渐变背景 =========
    for y in range(400):
        ratio = y / 400
        r = int(BG_TOP[0] * (1 - ratio) + BG_BOTTOM[0] * ratio)
        g = int(BG_TOP[1] * (1 - ratio) + BG_BOTTOM[1] * ratio)
        b = int(BG_TOP[2] * (1 - ratio) + BG_BOTTOM[2] * ratio)
        draw.line([(0, y), (POSTER_W, y)], fill=(r, g, b))

    # 底部区域
    draw.rectangle([(0, 400), (POSTER_W, POSTER_H)], fill=BG_BOTTOM)

    # ========= 2. 品牌头部 =========
    # 分割装饰线
    draw.rectangle([(40, 60), (710, 62)], fill=BRAND_GOLD)

    # 公司名
    brand_text = "三川田股份 832545"
    _draw_text_center(draw, brand_text, POSTER_W // 2, 110, font_brand, BRAND_GOLD)

    # 副标题
    sub_text = "专业展厅解决方案 · 深耕行业20年"
    _draw_text_center(draw, sub_text, POSTER_W // 2, 160, font_small, BRAND_GRAY)

    # ========= 3. 项目参数卡片区 =========
    card_y = 210
    _draw_card(draw, 40, card_y, POSTER_W - 80, 160, CARD_BG, CARD_BORDER)

    hall = share_data.get("hall_type_name", "展厅")
    area = share_data.get("area", 0)
    level = share_data.get("level_name", "")
    city = share_data.get("city_level_name", "")

    _draw_text_center(draw, f"{hall} · {level}", POSTER_W // 2, card_y + 35, font_medium, BRAND_WHITE)
    _draw_text_center(draw, f"{int(area)}㎡ | {city}", POSTER_W // 2, card_y + 80, font_small, BRAND_GRAY)

    # 工期
    days = share_data.get("schedule_days", 60)
    _draw_text_center(draw, f"参考工期 {days} 天", POSTER_W // 2, card_y + 120, font_small, BRAND_LIGHT_BLUE)

    # ========= 4. 核心价格区 =========
    price_y = 410
    # 大卡片
    _draw_card(draw, 40, price_y, POSTER_W - 80, 230, CARD_BG, CARD_BORDER)

    _draw_text_center(draw, "预估总造价", POSTER_W // 2, price_y + 40, font_medium, BRAND_GRAY)

    total_min = share_data.get("total_min", 0)
    total_max = share_data.get("total_max", 0)

    # 格式化价格
    if total_min >= 10000:
        price_text = f"¥ {total_min / 10000:.0f}万 - {total_max / 10000:.0f}万"
    else:
        price_text = f"¥ {total_min:,.0f} - {total_max:,.0f}"

    _draw_text_center(draw, price_text, POSTER_W // 2, price_y + 110, font_price, BRAND_GOLD)

    # 单价
    unit_min = share_data.get("unit_min", 0)
    unit_max = share_data.get("unit_max", 0)
    unit_text = f"单价 {unit_min:,.0f} - {unit_max:,.0f} 元/㎡"
    _draw_text_center(draw, unit_text, POSTER_W // 2, price_y + 180, font_small, BRAND_GRAY)

    # ========= 5. 分项明细 =========
    detail_y = 680
    details = share_data.get("details", [])
    if details:
        _draw_text(draw, "费用明细", 50, detail_y, font_medium, BRAND_WHITE)
        for i, d in enumerate(details[:4]):
            dy = detail_y + 50 + i * 45
            name = d.get("name", "")
            r = d.get("range", {})
            d_min = r.get("min", 0)
            d_max = r.get("max", 0)
            if d_min >= 10000:
                amt = f"{d_min / 10000:.0f}-{d_max / 10000:.0f}万"
            else:
                amt = f"{d_min:,.0f}-{d_max:,.0f}元"
            _draw_text(draw, name, 60, dy, font_small, BRAND_WHITE)
            _draw_text(draw, amt, POSTER_W - 60, dy, font_small, BRAND_LIGHT_BLUE, anchor="rm")

    # ========= 6. 分割线 =========
    line_y = 900
    draw.rectangle([(60, line_y), (POSTER_W - 60, line_y + 1)], fill=CARD_BORDER)

    # ========= 7. 二维码区域 =========
    qr_y = 930

    # 生成二维码
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(share_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color=BG_TOP, back_color=BRAND_WHITE).convert("RGB")
    qr_size = 200
    qr_img = qr_img.resize((qr_size, qr_size), Image.LANCZOS)

    # 二维码居中
    qr_x = (POSTER_W - qr_size) // 2
    img.paste(qr_img, (qr_x, qr_y))

    # 二维码下方文字
    _draw_text_center(draw, "长按识别 · 查看详细报价", POSTER_W // 2, qr_y + qr_size + 20, font_small, BRAND_GRAY)

    # ========= 8. 底部品牌信息 =========
    footer_y = 1200
    draw.rectangle([(40, footer_y), (POSTER_W - 40, footer_y + 1)], fill=BRAND_GOLD)

    _draw_text_center(draw, "三川田股份 832545", POSTER_W // 2, footer_y + 35, font_medium, BRAND_GOLD)
    _draw_text_center(draw, "官网：trf.333f.com", POSTER_W // 2, footer_y + 75, font_small, BRAND_GRAY)
    _draw_text_center(draw, "咨询热线：400-888-6363", POSTER_W // 2, footer_y + 110, font_small, BRAND_GRAY)

    # ========= 9. 底部声明 =========
    _draw_text_center(draw, "* 以上价格仅供参考，以最终方案报价为准", POSTER_W // 2, POSTER_H - 30, font_tiny, (100, 110, 130))

    # 输出为PNG字节
    buf = io.BytesIO()
    img.save(buf, format="PNG", quality=95)
    return buf.getvalue()


def _draw_card(draw, x, y, w, h, fill, border):
    """绘制圆角卡片"""
    radius = 16
    draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=radius, fill=fill, outline=border, width=1)


def _find_font() -> str:
    """查找系统中文字体"""
    import os
    font_paths = [
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/wqy-microhei/wqy-microhei.ttc",
        "/usr/share/fonts/wqy-zenhei/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
    ]
    for p in font_paths:
        if os.path.exists(p):
            return p
    return ""


def _draw_text(draw, text, x, y, font, fill, anchor="la"):
    """绘制文字（支持锚点）"""
    bbox = draw.textbbox((0, 0), text, font=font) if hasattr(draw, 'textbbox') else None
    if anchor == "lm":  # 左中
        if bbox:
            h = bbox[3] - bbox[1]
            draw.text((x, y - h // 2), text, font=font, fill=fill)
        else:
            draw.text((x, y - 10), text, font=font, fill=fill)
    elif anchor == "rm":  # 右中
        if bbox:
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            draw.text((x - w, y - h // 2), text, font=font, fill=fill)
        else:
            draw.text((x - 80, y - 10), text, font=font, fill=fill)
    else:  # la 左上
        draw.text((x, y), text, font=font, fill=fill)


def _draw_text_center(draw, text, cx, y, font, fill):
    """居中绘制文字"""
    bbox = draw.textbbox((0, 0), text, font=font) if hasattr(draw, 'textbbox') else None
    if bbox:
        w = bbox[2] - bbox[0]
        draw.text((cx - w // 2, y), text, font=font, fill=fill)
    else:
        # 回退：用 textsize
        try:
            tw, th = draw.textsize(text, font=font)
            draw.text((cx - tw // 2, y), text, font=font, fill=fill)
        except:
            draw.text((cx - len(text) * 8, y), text, font=font, fill=fill)
