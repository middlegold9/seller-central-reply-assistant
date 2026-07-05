from backend import classify
from backend.types import Category


def test_feedback_removal_high_risk():
    cat = classify.classify("怎么删除我的差评")
    assert cat == Category.feedback_removal
    assert classify.is_high_risk(cat)


def test_a_to_z_high_risk():
    cat = classify.classify("I want to open an A-to-Z claim")
    assert cat == Category.a_to_z
    assert classify.is_high_risk(cat)


def test_refund():
    assert classify.classify("我要申请退款") == Category.refund


def test_logistics():
    assert classify.classify("我的物流到哪了 where is my order") == Category.logistics


def test_quality():
    assert classify.classify("产品坏了 not working") == Category.quality


def test_other():
    assert classify.classify("你好") == Category.other
