from pathlib import Path

from ai_handover.frontmatter import load_document, parse_frontmatter


def test_parse_multiline_lists():
    text = """---
type: module
scope: order
aliases: [订单, sales-order]
source_paths:
  - src/order/**
  - db/order/**
verified_commit: \"abc\"
---
# Module: Order
Body
"""
    meta, body = parse_frontmatter(text)
    assert meta["type"] == "module"
    assert meta["scope"] == "order"
    assert meta["aliases"] == ["订单", "sales-order"]
    assert meta["source_paths"] == ["src/order/**", "db/order/**"]
    assert meta["verified_commit"] == "abc"
    assert "# Module: Order" in body
