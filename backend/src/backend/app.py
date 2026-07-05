"""FastAPI 入口：/draft /classify /enrich。"""

from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from . import learn
from .config import get_settings
from .enrich import EnrichmentClient
from .llm import generate_draft
from .types import BrandSettings, Context, Draft

app = FastAPI(title="Seller Central Reply Assistant Backend", version="0.1.0")

_store = learn.LearnStore()
_enricher = None


class DraftRequest(BaseModel):
    context: Context
    settings: Optional[BrandSettings] = None


class ClassifyRequest(BaseModel):
    message_text: str


class EnrichRequest(BaseModel):
    order_id: str


def _resolve_settings(override: Optional[BrandSettings]):
    base = get_settings()
    if override is None:
        return base
    return base.model_copy(update=override.model_dump(exclude_unset=True))


@app.post("/draft", response_model=Draft)
def draft(req: DraftRequest) -> Draft:
    settings = _resolve_settings(req.settings)
    global _enricher
    if _enricher is None and settings.mcp_base_url:
        _enricher = EnrichmentClient(settings.mcp_base_url, settings.mcp_token)
    result = generate_draft(req.context, settings, enricher=_enricher)
    # 记录到学习库（无论是否采用，供后续检索；脱敏在 LearnStore 内完成）
    if req.context.message_text:
        _store.record(
            message_text=req.context.message_text,
            draft_text=result.draft,
            category=(result.category.value if result.category else "other"),
            adopted=False,
            risk_level="block" if result.blocked else "info",
        )
    return result


@app.post("/classify")
def classify(req: ClassifyRequest):
    from . import classify as cl

    cat = cl.classify(req.message_text)
    return {"category": cat.value, "high_risk": cl.is_high_risk(cat)}


@app.post("/enrich")
def enrich(req: EnrichRequest):
    global _enricher
    settings = get_settings()
    if not _enricher and settings.mcp_base_url:
        _enricher = EnrichmentClient(settings.mcp_base_url, settings.mcp_token)
    if _enricher is None:
        raise HTTPException(status_code=400, detail="MCP base url not configured")
    try:
        data = _enricher.get_order(req.order_id)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=str(e))
    return data


@app.get("/health")
def health():
    return {"status": "ok"}
