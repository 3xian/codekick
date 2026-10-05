from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ContextDocument:
    path: Path
    doc_type: str = "unknown"
    scope: str = ""
    aliases: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    source_paths: list[str] = field(default_factory=list)
    verified_commit: str = ""
    title: str = ""
    body: str = ""


@dataclass
class RankedDocument:
    document: ContextDocument
    score: float
    reasons: list[str] = field(default_factory=list)


@dataclass
class FreshnessResult:
    path: Path
    status: str
    verified_commit: str
    changed_files: list[str] = field(default_factory=list)
    note: str = ""
