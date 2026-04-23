"""
PDF报告生成服务 - 带三川田品牌标识
"""
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 颜色定义
PRIMARY = HexColor('#3b82f6')
CYAN = HexColor('#06b6d4')
DARK = HexColor('#0a0e1a')
LIGHT_BG = HexColor('#f0f4ff')
GREEN = HexColor('#10b981')
GRAY = HexColor('#6b7280')
DARK_TEXT = HexColor('#1f2937')
MID_TEXT = HexColor('#4b5563')
LIGHT_LINE = HexColor('#e5e7eb')


def generate_pdf_report(result_data: dict) -> bytes:
    """
    生成带品牌标识的概算PDF报告
    result_data: EstimationResponse 的 dict 表示
    返回 PDF bytes
    """
    buf = io.BytesIO()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=25 * mm,
        rightMargin=25 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()

    # 自定义样式
    style_title = ParagraphStyle(
        'Title', parent=styles['Title'],
        fontSize=22, leading=28, textColor=DARK_TEXT,
        alignment=TA_CENTER, spaceAfter=4 * mm,
        fontName='Helvetica-Bold',
    )
    style_subtitle = ParagraphStyle(
        'Subtitle', parent=styles['Normal'],
        fontSize=11, textColor=MID_TEXT,
        alignment=TA_CENTER, spaceAfter=6 * mm,
    )
    style_heading = ParagraphStyle(
        'Heading', parent=styles['Heading2'],
        fontSize=14, textColor=DARK_TEXT, spaceAfter=3 * mm,
        spaceBefore=5 * mm, fontName='Helvetica-Bold',
    )
    style_body = ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontSize=10, textColor=MID_TEXT, leading=16,
    )
    style_total_min = ParagraphStyle(
        'TotalMin', parent=styles['Normal'],
        fontSize=28, textColor=PRIMARY,
        alignment=TA_CENTER, fontName='Helvetica-Bold',
    )
    style_total_label = ParagraphStyle(
        'TotalLabel', parent=styles['Normal'],
        fontSize=11, textColor=GRAY, alignment=TA_CENTER,
        spaceAfter=2 * mm,
    )
    style_small = ParagraphStyle(
        'Small', parent=styles['Normal'],
        fontSize=9, textColor=GRAY,
    )
    style_brand = ParagraphStyle(
        'Brand', parent=styles['Normal'],
        fontSize=12, textColor=GREEN,
        alignment=TA_CENTER, fontName='Helvetica-Bold',
        spaceAfter=2 * mm,
    )
    style_brand_desc = ParagraphStyle(
        'BrandDesc', parent=styles['Normal'],
        fontSize=9, textColor=MID_TEXT,
        alignment=TA_CENTER, spaceAfter=4 * mm,
    )
    style_disclaimer = ParagraphStyle(
        'Disclaimer', parent=styles['Normal'],
        fontSize=8, textColor=GRAY,
        alignment=TA_CENTER, spaceBefore=8 * mm,
    )

    elements = []

    # ===== 品牌头部 =====
    elements.append(Paragraph("◆ 三川田数字科技", style_brand))
    elements.append(Paragraph("展厅智能概算报告", style_title))
    elements.append(Paragraph(f"报告编号：SCT-{datetime.now().strftime('%Y%m%d%H%M%S')}", style_subtitle))
    elements.append(HRFlowable(width="100%", thickness=1, color=LIGHT_LINE, spaceAfter=6 * mm))

    # ===== 项目参数 =====
    params = result_data.get('params', {})
    param_data = [
        [Paragraph('<b>展厅类型</b>', style_body), params.get('hall_type_name', ''),
         Paragraph('<b>面积</b>', style_body), f"{params.get('area', '')} ㎡"],
        [Paragraph('<b>城市等级</b>', style_body), params.get('city_level_name', ''),
         Paragraph('<b>档次定位</b>', style_body), params.get('level_name', '')],
        [Paragraph('<b>预计工期</b>', style_body), f"{params.get('schedule_days', '')}天",
         Paragraph('<b>报告日期</b>', style_body), datetime.now().strftime('%Y-%m-%d')],
    ]
    param_table = Table(param_data, colWidths=[30 * mm, 55 * mm, 30 * mm, 55 * mm])
    param_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('GRID', (0, 0), (-1, -1), 0.5, LIGHT_LINE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(param_table)
    elements.append(Spacer(1, 6 * mm))

    # ===== 总价 =====
    total = result_data.get('total', {})
    unit_price = result_data.get('unit_price', {})
    elements.append(Paragraph("项目概算总价", style_total_label))
    elements.append(Spacer(1, 2 * mm))

    min_price = f"¥{total.get('min', 0):,.0f}"
    max_price = f"¥{total.get('max', 0):,.0f}"
    elements.append(Paragraph(f"{min_price}  ~  {max_price}", style_total_min))

    unit_min = f"¥{unit_price.get('min', 0):,.0f}"
    unit_max = f"¥{unit_price.get('max', 0):,.0f}"
    elements.append(Paragraph(f"参考单价：{unit_min} ~ {unit_max} / ㎡", style_subtitle))
    elements.append(Spacer(1, 4 * mm))

    # ===== 分项明细 =====
    elements.append(Paragraph("分项概算明细", style_heading))
    details = result_data.get('details', [])

    detail_data = [
        [Paragraph('<b>费用项目</b>', style_body),
         Paragraph('<b>占比</b>', style_body),
         Paragraph('<b>区间（元）</b>', style_body)],
    ]
    for item in details:
        r = item.get('range', {})
        detail_data.append([
            Paragraph(item.get('name', ''), style_body),
            Paragraph(f"{item.get('percent', 0)}%", style_body),
            Paragraph(f"¥{r.get('min', 0):,.0f} ~ ¥{r.get('max', 0):,.0f}", style_body),
        ])

    detail_table = Table(detail_data, colWidths=[55 * mm, 25 * mm, 90 * mm])
    detail_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e0e7ff')),
        ('GRID', (0, 0), (-1, -1), 0.5, LIGHT_LINE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(detail_table)

    # ===== 展项明细 =====
    exhibit_details = result_data.get('exhibit_details', [])
    if exhibit_details:
        elements.append(Spacer(1, 4 * mm))
        elements.append(Paragraph("多媒体展项明细", style_heading))

        exhibit_data = [
            [Paragraph('<b>展项名称</b>', style_body),
             Paragraph('<b>区间（元）</b>', style_body),
             Paragraph('<b>单位</b>', style_body)],
        ]
        for item in exhibit_details:
            r = item.get('range', {})
            exhibit_data.append([
                Paragraph(item.get('name', ''), style_body),
                Paragraph(f"¥{r.get('min', 0):,.0f} ~ ¥{r.get('max', 0):,.0f}", style_body),
                Paragraph(item.get('unit', '项'), style_body),
            ])

        exhibit_table = Table(exhibit_data, colWidths=[60 * mm, 75 * mm, 35 * mm])
        exhibit_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e0e7ff')),
            ('GRID', (0, 0), (-1, -1), 0.5, LIGHT_LINE),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(exhibit_table)

    # ===== 系数说明 =====
    elements.append(Spacer(1, 4 * mm))
    coef_data = [
        [Paragraph('<b>城市成本系数</b>', style_body),
         Paragraph(f"{params.get('city_coefficient', 1.0)}", style_body),
         Paragraph('<b>工期加价系数</b>', style_body),
         Paragraph(f"{params.get('schedule_coefficient', 1.0)}", style_body)],
    ]
    coef_table = Table(coef_data, colWidths=[42 * mm, 38 * mm, 42 * mm, 38 * mm])
    coef_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('GRID', (0, 0), (-1, -1), 0.5, LIGHT_LINE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(coef_table)

    # ===== 底部品牌 =====
    elements.append(Spacer(1, 8 * mm))
    elements.append(HRFlowable(width="100%", thickness=1, color=LIGHT_LINE, spaceAfter=4 * mm))
    elements.append(Paragraph("◆ 三川田数字科技", style_brand))
    elements.append(Paragraph("深耕数字展厅20年，为政府、企业提供一站式展厅解决方案", style_brand_desc))
    elements.append(Paragraph("📞 400-888-6363    🌐 www.sanchuantian.com", style_subtitle))
    elements.append(Paragraph(
        "如需详细方案与精准报价，欢迎联系我们的专业顾问",
        style_brand_desc
    ))

    # ===== 免责声明 =====
    elements.append(Paragraph(
        "以上为市场参考价区间，最终报价以实际方案为准。概算有效期30天。本报告由三川田展厅智能概算系统自动生成。",
        style_disclaimer
    ))

    doc.build(elements)
    return buf.getvalue()
