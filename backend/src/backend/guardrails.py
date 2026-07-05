"""政策护栏引擎（US2/FR4）。

亚马逊 Buyer-Seller Messaging 红线（硬编码规则库，可随政策更新版本）：
- block：索评 / 站外引流 / 操纵排名 / 删除或更改评价 / 以利益换好评
- warn：过度承诺时效 / 无政策全额退款 / 医疗或疗效宣称
- info：提示性建议
护栏是「人类在环」的最后一道闸：block 级使发送按钮禁用。
"""

from __future__ import annotations

from typing import List

from .types import RiskFlag, RiskLevel

# (rule, [触发词/短语])
BLOCK_RULES: List[tuple] = [
    ("solicit_review", ["好评", "留个好评", "给好评", "五星好评", "review for a discount",
                         "leave a good review", "positive review", "5-star review"]),
    ("offsite_solicit", ["微信", "whatsapp", "telegram", "加我", "line.me", "skype",
                          "external link", "contact me outside"]),
    ("remove_feedback", ["删差评", "改评价", "删除评价", "remove review", "delete review",
                          "change your review", "modify your feedback"]),
    ("compensation_for_review", ["返现", "好评返", "cashback for review", "gift card for review",
                                  "refund for review"]),
]

WARN_RULES: List[tuple] = [
    ("overpromise_shipping", ["保证", "guaranteed delivery", "一定到", "必定送达",
                               "100% deliver", "肯定能收到"]),
    ("refund_without_policy", ["全额退款", "full refund no question", "无理由退款",
                                "refund no matter what"]),
    ("medical_claim", ["治愈", "cures", "治疗", "medical claim", "疗效"]),
]

INFO_RULES: List[tuple] = [
    ("mention_link", ["http://", "https://", "www."]),
]


def check(text: str) -> List[RiskFlag]:
    """对一段文本跑护栏，返回命中的 RiskFlag 列表。"""
    flags: List[RiskFlag] = []
    low = (text or "").lower()
    for rule, kws in BLOCK_RULES:
        for kw in kws:
            if kw.lower() in low:
                flags.append(RiskFlag(level=RiskLevel.block, rule=rule,
                                      detail=f"命中亚马逊政策红线词：{kw}"))
                break
    for rule, kws in WARN_RULES:
        for kw in kws:
            if kw.lower() in low:
                flags.append(RiskFlag(level=RiskLevel.warn, rule=rule,
                                      detail=f"疑似过度承诺/越权：{kw}"))
                break
    for rule, kws in INFO_RULES:
        for kw in kws:
            if kw.lower() in low:
                flags.append(RiskFlag(level=RiskLevel.info, rule=rule,
                                      detail="消息含外链，请确认非站外引流"))
                break
    return flags


def has_block(flags: List[RiskFlag]) -> bool:
    return any(f.level == RiskLevel.block for f in flags)
