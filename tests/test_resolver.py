from pathlib import Path

from ai_handover.resolver import discover_documents, rank_documents


def _write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_order_cancellation_prefers_flow(tmp_path: Path):
    _write(
        tmp_path / ".ai" / "PROJECT_MAP.md",
        "---\ntype: project-map\n---\n# Project Map\norder inventory payment\n",
    )
    _write(
        tmp_path / ".ai" / "context" / "flows" / "cancel-order.md",
        "---\ntype: flow\nscope: cancel-order\naliases: [订单取消, cancellation]\ntags: [order, inventory]\n---\n# Cancel Order\n订单取消 releases inventory.\n",
    )
    _write(
        tmp_path / ".ai" / "context" / "modules" / "payment.md",
        "---\ntype: module\nscope: payment\naliases: [支付]\n---\n# Payment\nrefund authorization\n",
    )

    docs = discover_documents(tmp_path)
    ranked = rank_documents("订单取消增加信用检查", docs)
    assert ranked
    assert ranked[0].document.path.name == "cancel-order.md"
