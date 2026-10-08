#!/usr/bin/env python3
"""Deterministic checks for the product installer stamp. Not a benchmark."""
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INSTALL = ROOT / "scripts" / "install.py"
sys.path.insert(0, str(ROOT))
from scripts.install import install, sha


def tree(root: Path, files: dict[str, str]) -> None:
    for relative, text in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def stamp(dest: Path) -> dict:
    return json.loads((dest / ".ai" / ".codekick-install.json").read_text())


def test_matrix() -> None:
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        source = base / "src"
        dest = base / "dst"
        tree(source, {
            "AGENTS.md": "template-agents-v1\n",
            ".ai/PROJECT.md": "template-project-v1\n",
            ".ai/KNOWLEDGE.md": "template-knowledge-v1\n",
            "skills/change/SKILL.md": "skill-v1\n",
            "templates/TASK.md": "task-v1\n",
            "scripts/note.py": "print(1)\n",
        })
        first = install(source, dest, "1")
        assert first["complete"] is True, first
        assert stamp(dest)["version"] == "1"
        assert stamp(dest)["files"]["AGENTS.md"]["sha256"] == sha(dest / "AGENTS.md")
        second = install(source, dest, "1")
        assert all(item["action"] == "unchanged" for item in second["actions"]), second
        tree(source, {
            "AGENTS.md": "template-agents-v2\n",
            ".ai/PROJECT.md": "template-project-v2\n",
            ".ai/KNOWLEDGE.md": "template-knowledge-v2\n",
            "skills/change/SKILL.md": "skill-v2\n",
            "templates/TASK.md": "task-v2\n",
            "scripts/note.py": "print(2)\n",
        })
        upgraded = install(source, dest, "2")
        assert upgraded["complete"] is True
        assert "skill-v2" in (dest / "skills/change/SKILL.md").read_text()
        (dest / "AGENTS.md").write_text("user-agents\n")
        (dest / ".ai/PROJECT.md").write_text("user-project\n")
        (dest / ".ai/KNOWLEDGE.md").write_text("user-knowledge\n")
        (dest / "skills/change/SKILL.md").write_text("user-skill\n")
        tree(source, {
            "AGENTS.md": "template-agents-v3\n",
            ".ai/PROJECT.md": "template-project-v3\n",
            ".ai/KNOWLEDGE.md": "template-knowledge-v3\n",
            "skills/change/SKILL.md": "skill-v3\n",
            "templates/TASK.md": "task-v3\n",
            "scripts/note.py": "print(3)\n",
        })
        kept = install(source, dest, "3")
        assert kept["complete"] is False, kept
        assert kept["version"] is None
        assert set(kept["preserved"]) == {
            "AGENTS.md", ".ai/PROJECT.md", ".ai/KNOWLEDGE.md", "skills/change/SKILL.md"}
        assert (dest / "AGENTS.md").read_text() == "user-agents\n"
        assert (dest / ".ai/PROJECT.md").read_text() == "user-project\n"
        assert (dest / ".ai/KNOWLEDGE.md").read_text() == "user-knowledge\n"
        assert (dest / "skills/change/SKILL.md").read_text() == "user-skill\n"
        record = stamp(dest)
        assert record["complete"] is False
        assert record["version"] is None
        assert record["source_version"] == "3"
        for relative in kept["preserved"]:
            assert record["files"][relative]["sha256"] == sha(dest / relative)
            assert record["files"][relative]["sha256"] != record["files"][relative]["source_sha256"]
        assert (dest / "templates/TASK.md").read_text() == "task-v3\n"
        again = install(source, dest, "4")
        assert "user-agents" in (dest / "AGENTS.md").read_text()
        assert "user-skill" in (dest / "skills/change/SKILL.md").read_text()
        assert again["complete"] is False


def test_real_interrupt() -> None:
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        source = base / "src"
        dest = base / "dst"
        tree(source, {"AGENTS.md": "template-agents\n", "skills/a/SKILL.md": "installed-before-kill\n"})
        tree(dest, {"AGENTS.md": "user-agents\n", ".ai/PROJECT.md": "user-project\n"})
        large = source / "skills" / "b" / "SKILL.md"
        large.parent.mkdir(parents=True)
        large.write_bytes(b"x" * (64 * 1024 * 1024))
        proc = subprocess.Popen([sys.executable, str(INSTALL), str(source), str(dest), "9"], stdout=subprocess.DEVNULL)
        deadline = time.time() + 10
        pending = dest / ".ai" / ".codekick-install.pending"
        while time.time() < deadline and proc.poll() is None and not pending.exists():
            time.sleep(0.001)
        assert pending.exists(), "install did not reach the pending window"
        os.kill(proc.pid, signal.SIGKILL)
        proc.wait(timeout=5)
        assert (dest / "AGENTS.md").read_text() == "user-agents\n"
        assert (dest / ".ai/PROJECT.md").read_text() == "user-project\n"
        assert pending.exists()
        large.write_text("installed-after-resume\n")
        resumed = install(source, dest, "9")
        assert (dest / "AGENTS.md").read_text() == "user-agents\n"
        assert (dest / ".ai/PROJECT.md").read_text() == "user-project\n"
        assert (dest / "skills/b/SKILL.md").read_text() == "installed-after-resume\n"
        assert not pending.exists()
        assert resumed["repaired_incomplete"] is True
        assert "AGENTS.md" in resumed["preserved"]
        assert stamp(dest)["files"]["AGENTS.md"]["state"] == "preserved-user"


if __name__ == "__main__":
    test_matrix()
    test_real_interrupt()
    print("install stamp tests passed")
