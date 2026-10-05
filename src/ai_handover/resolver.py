from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path

from .frontmatter import load_document
from .git_utils import (
    changed_files_since,
    commit_exists,
    head_commit,
    is_git_repo,
    matches_any,
    working_tree_changes,
)
from .models import ContextDocument, FreshnessResult, RankedDocument


TOKEN_RE = re.compile(r"[A-Za-z0-9_.$:/-]+|[\u4e00-\u9fff]{1,8}")


STOPWORDS = {
    "the", "a", "an", "to", "of", "and", "or", "for", "in", "on", "with",
    "is", "are", "be", "this", "that", "it", "add", "change", "modify",
    "增加", "修改", "调整", "问题", "需求", "一下", "这个", "那个", "功能",
}


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    for raw in TOKEN_RE.findall(text.lower()):
        token = raw.strip("._$:/-")
        if len(token) < 2 or token in STOPWORDS:
            continue
        tokens.append(token)
        # Add Chinese bigrams for fuzzy overlap across longer phrases.
        if re.fullmatch(r"[\u4e00-\u9fff]+", token) and len(token) > 2:
            tokens.extend(token[i:i+2] for i in range(len(token) - 1))
    return tokens


def discover_documents(project: Path) -> list[ContextDocument]:
    ai_dir = project / ".ai"
    if not ai_dir.exists():
        return []

    candidates: list[Path] = []
    for special in (ai_dir / "PROJECT_MAP.md", ai_dir / "KNOWLEDGE.md"):
        if special.exists():
            candidates.append(special)

    context_dir = ai_dir / "context"
    if context_dir.exists():
        candidates.extend(sorted(context_dir.rglob("*.md")))

    return [load_document(path) for path in candidates]


def _field_text(doc: ContextDocument) -> dict[str, str]:
    return {
        "scope": doc.scope,
        "aliases": " ".join(doc.aliases),
        "tags": " ".join(doc.tags),
        "title": doc.title,
        "body": doc.body,
    }


def rank_documents(task: str, docs: list[ContextDocument]) -> list[RankedDocument]:
    task_tokens = tokenize(task)
    if not task_tokens:
        return []
    task_counts = Counter(task_tokens)

    ranked: list[RankedDocument] = []
    weights = {
        "scope": 8.0,
        "aliases": 7.0,
        "tags": 5.0,
        "title": 4.0,
        "body": 1.0,
    }

    for doc in docs:
        score = 0.0
        reasons: list[str] = []
        for field, text in _field_text(doc).items():
            field_tokens = Counter(tokenize(text))
            overlap = set(task_counts) & set(field_tokens)
            if not overlap:
                continue
            weighted = sum(
                min(task_counts[t], field_tokens[t]) * weights[field]
                for t in overlap
            )
            score += weighted
            reasons.append(f"{field}: {', '.join(sorted(overlap)[:6])}")

        # Always make project map available as a low-cost navigation base.
        if doc.doc_type == "project-map":
            score += 1.25
            reasons.append("base project map")

        # Durable knowledge should only appear when it has some textual match.
        if doc.doc_type == "durable-knowledge" and score <= 0:
            continue

        if score > 0:
            # Small length penalty prevents giant docs dominating just by token count.
            length_penalty = 1.0 + math.log10(max(len(doc.body), 10)) / 10.0
            ranked.append(RankedDocument(doc, score / length_penalty, reasons))

    ranked.sort(key=lambda item: (-item.score, str(item.document.path)))
    return ranked


def resolve_context(task: str, project: Path, limit: int = 5) -> list[RankedDocument]:
    docs = discover_documents(project)
    return rank_documents(task, docs)[:limit]


def freshness_for_document(doc: ContextDocument, project: Path) -> FreshnessResult:
    if not is_git_repo(project):
        return FreshnessResult(doc.path, "unknown", doc.verified_commit, note="not a git repository")
    if not doc.verified_commit:
        return FreshnessResult(doc.path, "unknown", "", note="no verified_commit")
    if not commit_exists(project, doc.verified_commit):
        return FreshnessResult(doc.path, "unknown", doc.verified_commit, note="verified_commit not found")
    if not doc.source_paths:
        return FreshnessResult(doc.path, "unknown", doc.verified_commit, note="no source_paths")

    changed = changed_files_since(project, doc.verified_commit)
    changed.extend(working_tree_changes(project))
    relevant = sorted({path for path in changed if matches_any(path, doc.source_paths)})

    if relevant:
        return FreshnessResult(
            doc.path,
            "potentially-stale",
            doc.verified_commit,
            changed_files=relevant,
            note="relevant source paths changed",
        )

    return FreshnessResult(doc.path, "fresh", doc.verified_commit, note=f"no relevant changes through {head_commit(project)[:12]}")


def build_context_pack(task: str, project: Path, limit: int = 5) -> str:
    ranked = resolve_context(task, project, limit=limit)
    lines = [
        "# AI Context Pack",
        "",
        f"Task: {task}",
        "",
        "> This pack is a navigation cache. Validate material claims against source code, tests, schema, configuration, git history, or runtime evidence.",
        "",
    ]

    if not ranked:
        lines += [
            "No relevant context cards were found.",
            "",
            "Start with repository search and create/update cards only if durable navigation knowledge is discovered.",
        ]
        return "\n".join(lines) + "\n"

    for item in ranked:
        doc = item.document
        freshness = freshness_for_document(doc, project)
        rel = doc.path.relative_to(project)
        lines += [
            "---",
            "",
            f"## {doc.title}",
            "",
            f"- Path: `{rel}`",
            f"- Type: `{doc.doc_type}`",
            f"- Resolver score: `{item.score:.2f}`",
            f"- Freshness: `{freshness.status}`",
        ]
        if freshness.changed_files:
            lines.append("- Relevant changed files: " + ", ".join(f"`{p}`" for p in freshness.changed_files[:12]))
        lines += ["", doc.body.strip(), ""]

    return "\n".join(lines).rstrip() + "\n"
