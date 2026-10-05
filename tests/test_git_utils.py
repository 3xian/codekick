from ai_handover.git_utils import matches_any


def test_matches_recursive_prefix():
    assert matches_any("src/order/service.py", ["src/order/**"])
    assert not matches_any("src/payment/service.py", ["src/order/**"])
