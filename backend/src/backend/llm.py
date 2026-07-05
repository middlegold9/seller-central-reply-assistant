"""LLM 草稿生成（US3）。支持语言对齐与政策护栏双跑。"""

from __future__ import annotations

import json
import re
from typing import Callable, Optional

from . import classify, guardrails
from .enrich import enrich_context
from .types import Context, Draft, RiskFlag, RiskLevel

POLICY_REDLINES = (
    "政策红线（绝对禁止）：\n"
    "1) 索要或暗示好评、以利益换评价（返现/礼品卡/折扣换好评）；\n"
    "2) 引导站外沟通（微信/WhatsApp/外部链接）；\n"
    "3) 要求删除或更改评价/反馈；\n"
    "4) 操纵排名或虚假陈述。\n"
    "若买家提及删差评/改评价/A-to-Z 索赔，不要自行回复，输出 needs_human 信号。"
)


def detect_lang(text: str) -> str:
    if re.search(r"[一-鿿]", text or ""):
        return "zh"
    return "en"


def build_system(settings) -> str:
    return (
        f"你是 {settings.brand_name} 的亚马逊客服助手。语气：{settings.tone}。\n"
        f"{POLICY_REDLINES}\n"
        "只回复与当前订单相关的事实性内容；不编造物流信息；无法确认时引导联系官方渠道。"
    )


def build_user(context: Context, lang: str) -> str:
    parts = [f"买家语言：{lang}", f"站点：{context.market}"]
    if context.order_id:
        parts.append(f"订单号：{context.order_id}")
    if context.order_status:
        parts.append(f"订单状态：{context.order_status}")
    if context.ship_status:
        parts.append(f"物流状态：{context.ship_status}")
    parts.append(f"买家消息：{context.message_text}")
    return "\n".join(parts)


def default_llm_fn(settings, system: str, user: str) -> str:
    """默认走 OpenAI 兼容接口；未配置时回退到模板（便于本地无密钥运行）。"""
    if not settings.llm_api_key or settings.llm_provider == "stub":
        return _template_reply(user)
    import httpx

    resp = httpx.post(
        f"{settings.llm_base_url.rstrip('/')}/chat/completions",
        headers={"Authorization": f"Bearer {settings.llm_api_key}"},
        json={
            "model": settings.llm_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.3,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _template_reply(user: str) -> str:
    return (
        "Thank you for reaching out to us. We have received your message and are "
        "looking into it. We will get back to you with a solution shortly. "
        "(This is a stub draft — configure an LLM key for full generation.)\n\n"
        f"[context]\n{user}"
    )


def _parse_draft(raw: str) -> tuple[str, list]:
    """尝试解析 JSON（含 draft / suggested_actions），否则整段作为草稿。"""
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict) and "draft" in obj:
            return obj["draft"], obj.get("suggested_actions", []) or []
    except (json.JSONDecodeError, TypeError):
        pass
    return raw.strip(), []


def generate_draft(
    context: Context,
    settings,
    llm_fn: Optional[Callable[[str, str], str]] = None,
    enricher=None,
    fake_enricher=None,
) -> Draft:
    llm_fn = llm_fn or (lambda s, u: default_llm_fn(settings, s, u))
    category = classify.classify(context.message_text)

    # 高风险类别：不生成发送草稿，转人工
    if classify.is_high_risk(category):
        return Draft(
            draft="",
            language=detect_lang(context.message_text) or context.buyer_lang,
            risk_flags=[RiskFlag(level=RiskLevel.block, rule="high_risk_route",
                                 detail=f"命中高风险类别 {category.value}，建议人工处理")],
            blocked=True,
            needs_human=True,
            category=category,
        )

    lang = detect_lang(context.message_text) or context.buyer_lang
    # 丰富上下文（实时物流 / 订单状态）
    order_status, ship_status = enrich_context(
        context, enricher=enricher, fake=fake_enricher
    )
    ctx = context.model_copy()
    if order_status:
        ctx.order_status = order_status
    if ship_status:
        ctx.ship_status = ship_status

    system = build_system(settings)
    user = build_user(ctx, lang)
    raw = llm_fn(system, user)
    draft_text, suggested = _parse_draft(raw)

    # 护栏双跑：买家消息 + 生成草稿
    flags = guardrails.check(context.message_text) + guardrails.check(draft_text)
    blocked = guardrails.has_block(flags)

    return Draft(
        draft=draft_text,
        language=lang,
        suggested_actions=suggested,
        risk_flags=flags,
        confidence=0.9 if not blocked else 0.5,
        blocked=blocked,
        needs_human=blocked,
        category=category,
        order_status=order_status,
        ship_status=ship_status,
    )
