"""买家消息分类（US4/FR5）。高风险类别转人工。"""

from __future__ import annotations

from .types import Category

HIGH_RISK = {Category.feedback_removal, Category.a_to_z}

_KEYWORDS = {
    Category.feedback_removal: ["删差评", "删除差评", "改评价", "删除评价", "remove review",
                                 "delete review", "change your review"],
    Category.a_to_z: ["a-to-z", "a to z", "claim", "仲裁", "纠纷", " lawsuit"],
    Category.refund: ["退款", "refund", "return money", "退钱", "return my money"],
    Category.logistics: ["物流", "发货", "快递", "tracking", "where is my order",
                          "delivery", "shipping", "还没收到", "not received"],
    Category.quality: ["质量", "坏", "破损", "broken", "defective", "damaged",
                       "not working", "坏了", "faulty"],
}


def classify(message: str) -> Category:
    low = (message or "").lower()
    # 优先级：先高风险
    # feedback_removal：差评/评价 + 删除/移除/改（兼容「删除我的差评」这类被分隔写法）
    if ("差评" in low or "评价" in low) and any(
        v in low for v in ["删", "移除", "remove", "delete", "change your"]
    ):
        return Category.feedback_removal
    if any(k in low for k in _KEYWORDS[Category.a_to_z]):
        return Category.a_to_z
    for cat, kws in _KEYWORDS.items():
        if cat in (Category.feedback_removal, Category.a_to_z):
            continue
        if any(k in low for k in kws):
            return cat
    return Category.other


def is_high_risk(category: Category) -> bool:
    return category in HIGH_RISK
