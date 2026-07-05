from backend.enrich import enrich_context
from backend.llm import generate_draft
from backend.types import BrandSettings, Context


def test_enrich_merges_order_status():
    fake = lambda order_id: {"order_status": "Shipped", "ship_status": "InTransit"}
    ctx = Context(message_text="where is my order", order_id="111", market="US")
    d = generate_draft(ctx, BrandSettings(), llm_fn=lambda s, u: "ok", fake_enricher=fake)
    assert d.order_status == "Shipped"
    assert d.ship_status == "InTransit"


def test_enrich_no_order_id_returns_none():
    ctx = Context(message_text="hi", market="US")
    assert enrich_context(ctx, fake=lambda o: {"order_status": "X"}) == (None, None)
