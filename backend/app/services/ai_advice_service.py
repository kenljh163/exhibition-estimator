"""
AI智能建议服务 - 基于DeepSeek大模型生成预算优化建议
"""
import httpx
import json
import os

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-ff6747cc2a254afeb25fffb6984815ca")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")


async def generate_budget_advice(
    budget: float,
    estimation_data: dict,
) -> dict:
    """
    根据客户预算和概算结果，生成AI智能调优建议
    
    :param budget: 客户预算（元）
    :param estimation_data: 概算结果数据
    :return: AI建议结构化数据
    """
    total_min = estimation_data.get("total", {}).get("min", 0)
    total_max = estimation_data.get("total", {}).get("max", 0)
    total_avg = (total_min + total_max) / 2
    details = estimation_data.get("details", [])
    params = estimation_data.get("params", {})

    # 1. 先做数值对比分析（不依赖AI）
    comparison = _build_comparison(budget, total_min, total_max, details)

    # 2. 如果预算和概算差距不大（±15%内），只返回数值分析
    diff_ratio = (budget - total_avg) / total_avg * 100 if total_avg > 0 else 0
    if abs(diff_ratio) <= 15:
        return {
            "feasibility": comparison["feasibility"],
            "comparison": comparison,
            "advice": None,
            "message": f"预算与概算基本匹配（偏差{abs(diff_ratio):.1f}%），无需大幅调整。",
        }

    # 3. 差距较大时，调用DeepSeek生成建议
    try:
        ai_advice = await _call_deepseek(budget, estimation_data, comparison)
        return {
            "feasibility": comparison["feasibility"],
            "comparison": comparison,
            "advice": ai_advice,
            "message": None,
        }
    except Exception as e:
        print(f"[AI] DeepSeek调用失败: {e}")
        # 降级为规则引擎建议
        fallback = _fallback_advice(budget, total_avg, details, params)
        return {
            "feasibility": comparison["feasibility"],
            "comparison": comparison,
            "advice": fallback,
            "message": "智能建议服务暂时不可用，以下为系统默认建议。",
        }


def _build_comparison(budget: float, total_min: float, total_max: float, details: list) -> dict:
    """
    构建预算vs概算的数值对比
    """
    total_avg = (total_min + total_max) / 2
    diff = budget - total_avg
    diff_ratio = diff / total_avg * 100 if total_avg > 0 else 0

    # 可行性评级
    if diff_ratio >= 20:
        feasibility = "sufficient"   # 充裕
        feasibility_label = "预算充裕"
    elif diff_ratio >= 5:
        feasibility = "adequate"     # 适中
        feasibility_label = "预算适中"
    elif diff_ratio >= -5:
        feasibility = "tight"        # 紧张
        feasibility_label = "预算紧张"
    elif diff_ratio >= -20:
        feasibility = "insufficient" # 不足
        feasibility_label = "预算不足"
    else:
        feasibility = "severe"       # 严重不足
        feasibility_label = "严重不足"

    # 分项对比（按比例分配预算到各项）
    subtotal = sum((d["range"]["min"] + d["range"]["max"]) / 2 for d in details)
    items = []
    for d in details:
        item_avg = (d["range"]["min"] + d["range"]["max"]) / 2
        item_percent = item_avg / subtotal * 100 if subtotal > 0 else 0
        allocated = budget * item_percent / 100
        item_diff = allocated - item_avg
        items.append({
            "name": d["name"],
            "estimate_min": d["range"]["min"],
            "estimate_max": d["range"]["max"],
            "estimate_avg": round(item_avg),
            "allocated": round(allocated),
            "diff": round(item_diff),
            "percent": round(item_percent, 1),
        })

    return {
        "budget": budget,
        "estimate_min": total_min,
        "estimate_max": total_max,
        "estimate_avg": round(total_avg),
        "diff": round(diff),
        "diff_ratio": round(diff_ratio, 1),
        "feasibility": feasibility,
        "feasibility_label": feasibility_label,
        "items": items,
    }


async def _call_deepseek(budget: float, estimation_data: dict, comparison: dict) -> dict:
    """
    调用DeepSeek API生成智能建议
    """
    params = estimation_data.get("params", {})
    details = estimation_data.get("details", [])
    diff_ratio = comparison["diff_ratio"]

    # 格式化分项数据
    details_text = ""
    for d in details:
        avg = (d["range"]["min"] + d["range"]["max"]) / 2
        details_text += f"  - {d['name']}: {avg/10000:.1f}万元（占比约{d.get('percent', 0):.0f}%）\n"

    # 构建prompt
    if diff_ratio < 0:
        direction = "缩减"
        prompt = f"""你是一位资深的展厅项目顾问，在三川田股份（NEEQ:832545）工作，拥有20年数字展厅行业经验。

当前有一个展厅项目的概算结果和客户预算如下：

【项目参数】
- 展厅类型：{params.get('hall_type_name', '未知')}
- 档次：{params.get('level_name', '未知')}
- 面积：{params.get('area', 0)}㎡
- 所在城市等级：{params.get('city_level_name', '未知')}
- 参考工期：{params.get('schedule_days', 60)}天

【概算结果】（总计约{(comparison['estimate_avg']/10000):.1f}万元）
{details_text}

【客户预算】{budget/10000:.1f}万元
【差距】预算比概算低{abs(diff_ratio):.1f}%

请你作为专业顾问，给出具体的预算缩减方案。要求：
1. 针对每个费用分项，给出具体的缩减建议（可以省多少、怎么省）
2. 建议要切实可行，不能简单说"降低标准"
3. 每条建议要标注预计可节省的金额（万元）
4. 最后给出一个缩减后的预算分配方案
5. 总缩减金额要尽量覆盖预算缺口

请严格以JSON格式返回，结构如下：
{{
  "summary": "一句话总结建议方向（20字内）",
  "suggestions": [
    {{
      "target": "分项名称",
      "action": "具体操作建议",
      "saving_min": 最小节省金额(元),
      "saving_max": 最大节省金额(元),
      "impact": "对效果的影响程度：低/中/高"
    }}
  ],
  "optimized_plan": [
    {{
      "name": "分项名称",
      "original_avg": 原始均摊金额(元),
      "optimized": 优化后金额(元),
      "note": "调整说明"
    }}
  ],
  "overall_advice": "整体专业建议（50字内，给客户的沟通话术）"
}}

注意：
- 只返回JSON，不要有任何其他文字
- 金额单位统一为元（不是万元）
- 优化后的各项总额应接近客户预算"""

    else:
        direction = "增配"
        prompt = f"""你是一位资深的展厅项目顾问，在三川田股份（NEEQ:832545）工作，拥有20年数字展厅行业经验。

当前有一个展厅项目的概算结果和客户预算如下：

【项目参数】
- 展厅类型：{params.get('hall_type_name', '未知')}
- 档次：{params.get('level_name', '未知')}
- 面积：{params.get('area', 0)}㎡
- 所在城市等级：{params.get('city_level_name', '未知')}
- 参考工期：{params.get('schedule_days', 60)}天

【概算结果】（总计约{(comparison['estimate_avg']/10000):.1f}万元）
{details_text}

【客户预算】{budget/10000:.1f}万元
【差距】预算比概算高{diff_ratio:.1f}%

客户预算充裕，请你给出增配升级建议。要求：
1. 建议增加哪些可以提升展厅效果的配置
2. 每条建议标注增加的金额
3. 增配总额尽量接近预算盈余
4. 给出一个增配后的预算分配方案

请严格以JSON格式返回，结构如下：
{{
  "summary": "一句话总结建议方向（20字内）",
  "suggestions": [
    {{
      "target": "增配方向",
      "action": "具体增配建议",
      "addition_min": 最小增加金额(元),
      "addition_max": 最大增加金额(元),
      "value": "增值程度：低/中/高"
    }}
  ],
  "optimized_plan": [
    {{
      "name": "分项名称",
      "original_avg": 原始均摊金额(元),
      "optimized": 优化后金额(元),
      "note": "调整说明"
    }}
  ],
  "overall_advice": "整体专业建议（50字内，给客户的沟通话术）"
}}

注意：
- 只返回JSON，不要有任何其他文字
- 金额单位统一为元（不是万元）
- 优化后的各项总额应接近客户预算"""

    # 调用DeepSeek
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{DEEPSEEK_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": DEEPSEEK_MODEL,
                "messages": [
                    {"role": "system", "content": "你是三川田股份的高级展厅顾问，回复只输出JSON，不要有任何markdown标记或其他文字。"},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.7,
                "max_tokens": 2000,
            },
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]

    # 解析JSON（可能被markdown包裹）
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1] if "\n" in content else content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
    if content.startswith("json"):
        content = content[4:].strip()

    return json.loads(content)


def _fallback_advice(budget: float, total_avg: float, details: list, params: dict) -> dict:
    """
    降级：基于规则的简单建议（当AI不可用时）
    """
    gap = budget - total_avg
    suggestions = []
    optimized = []

    for d in details:
        item_avg = (d["range"]["min"] + d["range"]["max"]) / 2
        name = d["name"]

        if gap < 0:
            # 预算不足，每项缩减一些
            ratio = 0.8  # 缩减20%
            if "多媒体" in name or "展项" in name:
                ratio = 0.65  # 多媒体可缩减更多
                suggestions.append({
                    "target": name,
                    "action": "减少展项数量或降低设备规格",
                    "saving_min": round(item_avg * 0.2),
                    "saving_max": round(item_avg * 0.35),
                    "impact": "中",
                })
            elif "设计" in name:
                ratio = 0.9
                suggestions.append({
                    "target": name,
                    "action": "精简设计方案，聚焦核心展示区域",
                    "saving_min": round(item_avg * 0.05),
                    "saving_max": round(item_avg * 0.1),
                    "impact": "低",
                })
            elif "税金" in name or "管理" in name:
                ratio = 0.95
            else:
                suggestions.append({
                    "target": name,
                    "action": "采用性价比更高的材料方案",
                    "saving_min": round(item_avg * 0.1),
                    "saving_max": round(item_avg * 0.2),
                    "impact": "中",
                })
            optimized.append({
                "name": name,
                "original_avg": round(item_avg),
                "optimized": round(item_avg * ratio),
                "note": "按比例缩减",
            })
        else:
            # 预算充裕
            if "多媒体" in name or "展项" in name:
                ratio = 1.3
                suggestions.append({
                    "target": name,
                    "action": "增加互动展项，提升沉浸式体验",
                    "addition_min": round(item_avg * 0.2),
                    "addition_max": round(item_avg * 0.3),
                    "value": "高",
                })
            elif "设计" in name:
                ratio = 1.15
                suggestions.append({
                    "target": name,
                    "action": "增加创意设计元素和定制化内容",
                    "addition_min": round(item_avg * 0.1),
                    "addition_max": round(item_avg * 0.15),
                    "value": "中",
                })
            else:
                ratio = 1.1
            optimized.append({
                "name": name,
                "original_avg": round(item_avg),
                "optimized": round(item_avg * ratio),
                "note": "适度增配",
            })

    return {
        "summary": "系统默认建议" if gap < 0 else "建议增配升级",
        "suggestions": suggestions,
        "optimized_plan": optimized,
        "overall_advice": "以上为系统自动生成的建议，具体方案请联系三川田专业顾问获取详细报价。" if gap < 0 else "预算充裕，建议适当增加投入提升展厅整体效果。",
    }
