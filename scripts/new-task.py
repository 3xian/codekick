#!/usr/bin/env python3
"""Create a task artifact from templates/TASK.md.

Usage:
    python scripts/new-task.py JIRA-1234 "Add credit limit validation"
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: python scripts/new-task.py <TASK_ID> [TITLE]')
        return 2

    task_id = sys.argv[1].strip()
    title = " ".join(sys.argv[2:]).strip() or task_id

    if not re.fullmatch(r"[A-Za-z0-9._-]+", task_id):
        print("TASK_ID may contain only letters, numbers, dot, underscore and hyphen.")
        return 2

    root = Path(__file__).resolve().parents[1]
    template = root / "templates" / "TASK.md"
    target_dir = root / ".ai" / "tasks"
    target = target_dir / f"{task_id}.md"

    if target.exists():
        print(f"Task already exists: {target}")
        return 1

    content = template.read_text(encoding="utf-8")
    content = content.replace("{{TASK_ID}}", task_id).replace("{{TITLE}}", title)

    target_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    print(target.relative_to(root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
