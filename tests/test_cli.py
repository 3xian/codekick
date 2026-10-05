from argparse import Namespace
from pathlib import Path

from ai_handover.cli import cmd_init, cmd_new_card


def test_init_does_not_create_placeholder_cards(tmp_path: Path):
    assert cmd_init(Namespace(project=str(tmp_path), force=False)) == 0
    assert (tmp_path / ".ai" / "PROJECT_MAP.md").exists()
    assert (tmp_path / ".ai" / "KNOWLEDGE.md").exists()
    assert not (tmp_path / ".ai" / "context" / "modules" / "_MODULE.md").exists()
    assert not (tmp_path / ".ai" / "context" / "flows" / "_FLOW.md").exists()


def test_new_card(tmp_path: Path):
    cmd_init(Namespace(project=str(tmp_path), force=False))
    args = Namespace(
        kind="module",
        name="Order",
        project=str(tmp_path),
        scope="order",
        filename=None,
        force=False,
    )
    assert cmd_new_card(args) == 0
    card = tmp_path / ".ai" / "context" / "modules" / "order.md"
    assert card.exists()
    text = card.read_text(encoding="utf-8")
    assert "scope: order" in text
    assert "# Module: Order" in text
