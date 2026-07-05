from backend.llm import generate_draft
from backend.types import BrandSettings, Context


def _fake_llm(system, user):
    return "Hello, we have received your message and will assist you shortly."


def test_normal_draft():
    ctx = Context(message_text="Where is my order?", market="US", buyer_lang="en")
    d = generate_draft(ctx, BrandSettings(), llm_fn=_fake_llm)
    assert d.draft
    assert d.language == "en"
    assert isinstance(d.suggested_actions, list)
    assert d.blocked is False
    assert d.needs_human is False


def test_high_risk_routes_to_human():
    ctx = Context(message_text="帮我删除差评", market="CN", buyer_lang="zh")
    d = generate_draft(ctx, BrandSettings())
    assert d.needs_human is True
    assert d.blocked is True
    assert d.draft == ""
    assert d.category.value == "feedback_removal"


def test_draft_with_redline_gets_blocked():
    def evil_llm(system, user):
        return "Please leave a good review and we will refund you."
    ctx = Context(message_text="my item broke", market="US", buyer_lang="en")
    d = generate_draft(ctx, BrandSettings(), llm_fn=evil_llm)
    assert d.blocked is True
    assert any(f.level.value == "block" for f in d.risk_flags)


def test_language_detection_zh():
    ctx = Context(message_text="我的订单什么时候到", market="CN", buyer_lang="zh")
    d = generate_draft(ctx, BrandSettings(), llm_fn=_fake_llm)
    assert d.language == "zh"
