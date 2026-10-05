from __future__ import annotations

import fnmatch
import subprocess
from pathlib import Path


def _run_git(project: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(project), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def is_git_repo(project: Path) -> bool:
    result = _run_git(project, "rev-parse", "--is-inside-work-tree")
    return result.returncode == 0 and result.stdout.strip() == "true"


def head_commit(project: Path) -> str:
    result = _run_git(project, "rev-parse", "HEAD")
    return result.stdout.strip() if result.returncode == 0 else ""


def commit_exists(project: Path, commit: str) -> bool:
    if not commit:
        return False
    result = _run_git(project, "cat-file", "-e", f"{commit}^{{commit}}")
    return result.returncode == 0


def changed_files_since(project: Path, commit: str) -> list[str]:
    result = _run_git(project, "diff", "--name-only", f"{commit}..HEAD")
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def working_tree_changes(project: Path) -> list[str]:
    result = _run_git(project, "status", "--porcelain")
    if result.returncode != 0:
        return []
    files: list[str] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        payload = line[3:] if len(line) >= 4 else ""
        if " -> " in payload:
            payload = payload.split(" -> ", 1)[1]
        if payload:
            files.append(payload)
    return files


def matches_any(path: str, patterns: list[str]) -> bool:
    if not patterns:
        return False
    normalized = path.replace("\\", "/")
    for pattern in patterns:
        p = pattern.replace("\\", "/")
        if fnmatch.fnmatch(normalized, p):
            return True
        # Make directory-like globs friendlier, e.g. src/order/**
        prefix = p[:-3] if p.endswith("/**") else ""
        if prefix and (normalized == prefix or normalized.startswith(prefix.rstrip("/") + "/")):
            return True
    return False
