"""学习库（US6/FR10）：发送后脱敏写入，新会话检索相似高采用率回复。"""

from __future__ import annotations

import hashlib
import re
from typing import List

from .types import ReplyRecord

_SENSITIVE = re.compile(r"(?i)([a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}|https?://\S+|order\s*#?\s*\w+|asin\s*#?\s*\w+)")


def _desensitize(text: str) -> str:
    return _SENSITIVE.sub("[REDACTED]", text or "")


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


class LearnStore:
    def __init__(self) -> None:
        self.records: List[ReplyRecord] = []

    def record(self, *, message_text: str, draft_text: str, category: str,
               adopted: bool, risk_level: str = "info") -> ReplyRecord:
        rec = ReplyRecord(
            ts=__import__("time").time(),
            order_id=None,
            category=category,
            adopted=adopted,
            risk_level=risk_level,
            message_snippet=_desensitize(message_text)[:200],
            draft_snippet=_desensitize(draft_text)[:200],
        )
        self.records.append(rec)
        return rec

    def retrieve(self, message_text: str, top_k: int = 3) -> List[ReplyRecord]:
        """按关键词重叠检索历史相似案例（优先高采用率）。"""
        q_tokens = set(_desensitize(message_text).lower().split())
        scored = []
        for rec in self.records:
            rec_tokens = set(rec.message_snippet.lower().split())
            overlap = len(q_tokens & rec_tokens)
            if overlap == 0:
                continue
            score = overlap * (2 if rec.adopted else 1)
            scored.append((score, rec))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in scored[:top_k]]
