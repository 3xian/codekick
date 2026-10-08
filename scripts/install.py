#!/usr/bin/env python3
"""Install CodeKick into an existing project without overwriting user-owned files.

Usage:
    python scripts/install.py /path/to/project
    python scripts/install.py SOURCE DEST VERSION
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

PAYLOAD = ("AGENTS.md", ".ai", "skills", "templates", "scripts")
USER_OWNED = {"AGENTS.md", ".ai/PROJECT.md", ".ai/KNOWLEDGE.md"}
STAMP = ".ai/.codekick-install.json"
PENDING = ".ai/.codekick-install.pending"
VERSION = "1"


def sha(path: Path) -> str:
    data = path.read_bytes() if path.is_file() else b""
    return hashlib.sha256(data).hexdigest()


def files(root: Path) -> dict[str, str]:
    found = {}
    for name in PAYLOAD:
        path = root / name
        if path.is_file():
            found[name] = sha(path)
        elif path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.is_file() and ".codekick-install.json" not in child.parts and child.name != ".codekick-install.pending":
                    found[str(child.relative_to(root))] = sha(child)
    return found


def read_stamp(dest: Path) -> dict | None:
    path = dest / STAMP
    if not path.is_file():
        return None
    return json.loads(path.read_text())


def recorded_hash(entry) -> str | None:
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict):
        return entry.get("sha256")
    return None


def install(source: Path, dest: Path, version: str = VERSION) -> dict:
    source = source.resolve()
    dest = dest.resolve()
    payload = files(source)
    previous = read_stamp(dest)
    owned = previous.get("files", {}) if previous else {}
    incomplete = (dest / PENDING).is_file()
    actions = []
    planned = []
    records = {}
    preserved = []
    for relative, digest in payload.items():
        target = dest / relative
        current = sha(target) if target.is_file() else None
        entry = owned.get(relative)
        last = recorded_hash(entry)
        state = entry.get("state") if isinstance(entry, dict) else None
        user_edit = False
        if target.is_file() and current != digest:
            if state == "preserved-user" and current == last:
                user_edit = True
            elif relative in USER_OWNED and current != last:
                user_edit = True
            elif not incomplete and last is not None and current != last:
                user_edit = True
        if user_edit:
            actions.append({"path": relative, "action": "preserve-user"})
            preserved.append(relative)
            records[relative] = {"sha256": current, "state": "preserved-user", "source_sha256": digest}
            continue
        if current == digest:
            actions.append({"path": relative, "action": "unchanged"})
            records[relative] = {"sha256": current, "state": "unchanged", "source_sha256": digest}
            continue
        planned.append(relative)
        actions.append({"path": relative, "action": "install"})
        records[relative] = {"sha256": digest, "state": "installed", "source_sha256": digest}
    if planned:
        pending = dest / PENDING
        pending.parent.mkdir(parents=True, exist_ok=True)
        temporary_pending = pending.with_suffix(".pending.tmp")
        temporary_pending.write_text(version + "\n")
        os.replace(temporary_pending, pending)
        for relative in planned:
            target = dest / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = Path(tempfile.mkstemp(prefix=".codekick-", dir=target.parent)[1])
            try:
                shutil.copy2(source / relative, temporary)
                os.replace(temporary, target)
            finally:
                if temporary.exists():
                    temporary.unlink()
    complete = not preserved
    stamp = {
        "source_version": version,
        "version": version if complete else None,
        "complete": complete,
        "files": records,
        "preserved": preserved,
    }
    stamp_path = dest / STAMP
    stamp_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = stamp_path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(stamp, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, stamp_path)
    pending = dest / PENDING
    if pending.exists():
        pending.unlink()
    return {
        "source_version": version,
        "version": stamp["version"],
        "complete": complete,
        "preserved": preserved,
        "actions": actions,
        "repaired_incomplete": incomplete,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    if len(args.paths) == 1:
        source, dest, version = root, Path(args.paths[0]), VERSION
    elif len(args.paths) == 3:
        source, dest, version = Path(args.paths[0]), Path(args.paths[1]), args.paths[2]
    else:
        parser.error("usage: install.py DEST | install.py SOURCE DEST VERSION")
    if not dest.exists():
        dest.mkdir(parents=True)
    print(json.dumps(install(source, dest, version)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
