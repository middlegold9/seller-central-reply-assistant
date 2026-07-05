import time

from backend import learn


def test_record_and_retrieve_similar():
    store = learn.LearnStore()
    store.record(message_text="我的物流到哪了 where is my order 111",
                 draft_text="我们会查询物流", category="logistics", adopted=True)
    store.record(message_text="产品坏了 not working", draft_text="抱歉，我们补发",
                 category="quality", adopted=False)
    results = store.retrieve("我的物流到哪了 where is my order")
    assert len(results) >= 1
    assert results[0].category == "logistics"
    assert results[0].adopted is True


def test_desensitize_redacts_pii():
    out = learn._desensitize("email me at a@b.com or http://x.com order #123")
    assert "a@b.com" not in out
    assert "http://x.com" not in out
    assert "[REDACTED]" in out
