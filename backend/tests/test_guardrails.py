from backend.guardrails import check, has_block
from backend.types import RiskLevel


def test_solicit_review_blocked():
    flags = check("亲，给个好评返现哦")
    assert has_block(flags)
    assert any(f.rule == "solicit_review" for f in flags)


def test_offsite_blocked():
    flags = check("加我微信 whatsapp 详聊")
    assert has_block(flags)
    assert any(f.rule == "offsite_solicit" for f in flags)


def test_remove_feedback_blocked():
    flags = check("帮我删除评价可以吗")
    assert has_block(flags)
    assert any(f.rule == "remove_feedback" for f in flags)


def test_overpromise_warned():
    flags = check("我们保证三天一定到货")
    assert any(f.level == RiskLevel.warn and f.rule == "overpromise_shipping" for f in flags)
    assert not has_block(flags)


def test_clean_message_no_flags():
    assert check("谢谢你的帮助") == []
