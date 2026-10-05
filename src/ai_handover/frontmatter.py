from __future__ import annotations

import ast
import re
from pathlib import Path

from .models import ContextDocument


_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)


def _parse_scalar(value: str):
    value = value.strip()
    if not value:
        return ""
    if value in {"true", "false"}:
        return value == "true"
    if value.startswith("[") and value.endswith("]"):
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, list):
                return [str(v) for v in parsed]
        except (ValueError, SyntaxError):
            inner = value[1:-1].strip()
            if not inner:
                return []
            return [item.strip().strip("\"'") for item in inner.split(",")]
    return value.strip("\"'")


def parse_frontmatter(text: str) -> tuple[dict, str]:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}, text

    raw = match.group(1)
    meta: dict[str, object] = {}
    current_list_key: str | None = None

    for original_line in raw.splitlines():
        line = original_line.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        stripped = line.strip()
        if stripped.startswith("-") and current_list_key:
            meta.setdefault(current_list_key, [])
            value = stripped[1:].strip().strip("\"'")
            if value:
                casted = meta[current_list_key]
                if isinstance(casted, list):
                    casted.append(value)
            continue

        if ":" not in line:
            current_list_key = None
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not value:
            meta[key] = []
            current_list_key = key
        else:
            meta[key] = _parse_scalar(value)
            current_list_key = None

    return meta, text[match.end():]


def _first_heading(body: str) -> str:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def load_document(path: Path) -> ContextDocument:
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)

    def as_list(key: str) -> list[str]:
        value = meta.get(key, [])
        if isinstance(value, list):
            return [str(x) for x in value]
        if value in (None, ""):
            return []
        return [str(value)]

    return ContextDocument(
        path=path,
        doc_type=str(meta.get("type", "unknown")),
        scope=str(meta.get("scope", "")),
        aliases=as_list("aliases"),
        tags=as_list("tags"),
        source_paths=as_list("source_paths"),
        verified_commit=str(meta.get("verified_commit", "")),
        title=_first_heading(body) or path.stem,
        body=body,
    )
