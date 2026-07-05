"""后端数据模型。"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class RiskLevel(str, Enum):
    block = "block"
    warn = "warn"
    info = "info"


class Category(str, Enum):
    logistics = "logistics"
    quality = "quality"
    refund = "refund"
    feedback_removal = "feedback_removal"
    a_to_z = "a_to_z"
    other = "other"


class Context(BaseModel):
    """从 Seller Central 消息页解析出的上下文。"""

    message_text: str
    market: str = "US"
    buyer_lang: str = "en"
    order_id: Optional[str] = None
    asin: Optional[str] = None
    order_status: Optional[str] = None
    ship_status: Optional[str] = None


class RiskFlag(BaseModel):
    level: RiskLevel
    rule: str
    detail: str


class Draft(BaseModel):
    draft: str
    language: str
    suggested_actions: List[str] = []
    risk_flags: List[RiskFlag] = []
    confidence: float = 0.0
    blocked: bool = False
    needs_human: bool = False
    category: Optional[Category] = None
    # 丰富后的实时上下文（来自 SP-API）
    order_status: Optional[str] = None
    ship_status: Optional[str] = None


class ReplyRecord(BaseModel):
    """脱敏后的学习库记录。"""

    ts: float
    order_id: Optional[str] = None
    category: Optional[str] = None
    adopted: bool = False
    risk_level: str = "info"
    message_snippet: str  # 已脱敏的买家消息片段（用于相似检索）
    draft_snippet: str


class BrandSettings(BaseModel):
    brand_name: str = "YourBrand"
    tone: str = "friendly, professional, concise"
    refund_limit: float = 20.0  # 自动可批退款上限（USD）
    guardrail_strictness: str = "strict"  # strict | normal
    llm_provider: str = "stub"
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_model: str = "stub-model"
