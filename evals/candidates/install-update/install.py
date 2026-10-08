#!/usr/bin/env python3
"""Experimental CodeKick installer. Not a product entrypoint until an ACCEPT decision."""
import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path

PAYLOAD = ("AGENTS.md", ".ai", "skills", "templates", "scripts")
USER_OWNED = {"AGENTS.md", ".ai/PROJECT.md", ".ai/KNOWLEDGE.md"}
STAMP = ".ai/.codekick-install.json"
PENDING = ".ai/.codekick-install.pending"


def sha(path):
    data = path.read_bytes() if path.is_file() else b""
    return hashlib.sha256(data).hexdigest()


def files(root):
    found = {}
    for name in PAYLOAD:
        path = root / name
        if path.is_file():
            found[name] = sha(path)
        elif path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.is_file() and ".codekick-install.json" not in child.parts:
                    found[str(child.relative_to(root))] = sha(child)
    return found


def read_stamp(dest):
    path = dest / STAMP
    if not path.is_file():
        return None
    return json.loads(path.read_text())


def install(source, dest, version):
    source = Path(source).resolve()
    dest = Path(dest).resolve()
    payload = files(source)
    previous = read_stamp(dest)
    owned = previous.get("files", {}) if previous else {}
    incomplete = (dest / PENDING).is_file()
    actions = []
    staged_files = []
    staging = Path(tempfile.mkdtemp(prefix="codekick-install-", dir=dest))
    try:
        for relative, digest in payload.items():
            src = source / relative
            target = dest / relative
            current = sha(target) if target.is_file() else None
            user_edit = False
            if target.exists() and current != digest:
                if relative in USER_OWNED and owned.get(relative) != current:
                    user_edit = True
                elif not incomplete and owned.get(relative) and current != owned.get(relative):
                    user_edit = True
            if user_edit:
                actions.append({"path": relative, "action": "preserve-user"})
                continue
            if current == digest:
                actions.append({"path": relative, "action": "unchanged"})
                continue
            staged = staging / relative
            staged.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, staged)
            staged_files.append(relative)
            actions.append({"path": relative, "action": "install"})
        if staged_files:
            pending = dest / PENDING
            pending.parent.mkdir(parents=True, exist_ok=True)
            temporary_pending = pending.with_suffix(".pending.tmp")
            temporary_pending.write_text(version + "\n")
            os.replace(temporary_pending, pending)
        for relative in staged_files:
            target = dest / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(staging / relative, target)
        stamp_path = dest / STAMP
        stamp_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = stamp_path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps({"version": version, "files": payload}, indent=2, sort_keys=True) + "\n")
        os.replace(temporary, stamp_path)
        pending = dest / PENDING
        if pending.exists():
            pending.unlink()
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    return {"version": version, "actions": actions, "repaired_incomplete": incomplete}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("dest")
    parser.add_argument("version")
    args = parser.parse_args()
    print(json.dumps(install(args.source, args.dest, args.version)))


if __name__ == "__main__":
    main()
