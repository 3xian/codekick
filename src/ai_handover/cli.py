from __future__ import annotations

import argparse
from pathlib import Path
from importlib import resources

from .frontmatter import load_document
from .git_utils import head_commit, is_git_repo
from .resolver import build_context_pack, discover_documents, freshness_for_document, resolve_context


def _template_text(*parts: str) -> str:
    target = resources.files("ai_handover").joinpath("templates", *parts)
    return target.read_text(encoding="utf-8")


def cmd_init(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve()
    project.mkdir(parents=True, exist_ok=True)
    ai_dir = project / ".ai"
    (ai_dir / "context" / "modules").mkdir(parents=True, exist_ok=True)
    (ai_dir / "context" / "flows").mkdir(parents=True, exist_ok=True)

    files = {
        ai_dir / "PROJECT_MAP.md": ("PROJECT_MAP.md",),
        ai_dir / "KNOWLEDGE.md": ("KNOWLEDGE.md",),
    }

    created = []
    for target, template_parts in files.items():
        if target.exists() and not args.force:
            continue
        target.write_text(_template_text(*template_parts), encoding="utf-8")
        created.append(target.relative_to(project))

    print(f"Initialized {ai_dir}")
    if is_git_repo(project):
        print(f"Current Git HEAD: {head_commit(project)}")
    for path in created:
        print(f"  created {path}")
    if not created:
        print("  nothing changed (use --force to overwrite templates)")
    return 0


def _slugify(value: str) -> str:
    import re
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", value)
    return value.strip("-") or "card"


def cmd_new_card(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve()
    kind = args.kind
    folder = "modules" if kind == "module" else "flows"
    template_name = "_MODULE.md" if kind == "module" else "_FLOW.md"
    target_dir = project / ".ai" / "context" / folder
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = args.filename or (_slugify(args.name) + ".md")
    if not filename.endswith(".md"):
        filename += ".md"
    target = target_dir / filename
    if target.exists() and not args.force:
        print(f"File exists: {target}")
        return 1

    text = _template_text("context", folder, template_name)
    text = text.replace("scope: replace-me", f"scope: {args.scope or args.name}")
    if kind == "module":
        text = text.replace("# Module: Replace Me", f"# Module: {args.name}")
    else:
        text = text.replace("# Flow: Replace Me", f"# Flow: {args.name}")
    target.write_text(text, encoding="utf-8")
    print(target)
    return 0


def cmd_resolve(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve()
    ranked = resolve_context(args.task, project, limit=args.limit)
    if not ranked:
        print("No relevant context cards found.")
        return 1

    for idx, item in enumerate(ranked, 1):
        doc = item.document
        freshness = freshness_for_document(doc, project)
        rel = doc.path.relative_to(project)
        reasons = "; ".join(item.reasons)
        print(f"{idx}. {rel}  score={item.score:.2f}  freshness={freshness.status}")
        if reasons:
            print(f"   {reasons}")
        if freshness.changed_files:
            print("   changed: " + ", ".join(freshness.changed_files[:8]))
    return 0


def cmd_pack(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve()
    content = build_context_pack(args.task, project, limit=args.limit)
    if args.output:
        output = Path(args.output)
        if not output.is_absolute():
            output = project / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")
        print(output)
    else:
        print(content, end="")
    return 0


def cmd_freshness(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve()
    docs = discover_documents(project)
    if not docs:
        print("No .ai context documents found.")
        return 1

    status_rank = {"fresh": 0, "unknown": 1, "potentially-stale": 2}
    worst = 0
    for doc in docs:
        result = freshness_for_document(doc, project)
        worst = max(worst, status_rank.get(result.status, 1))
        rel = doc.path.relative_to(project)
        print(f"{result.status:18} {rel}")
        if result.note:
            print(f"  {result.note}")
        for changed in result.changed_files[:12]:
            print(f"  - {changed}")
    return 2 if worst == 2 else 0


def cmd_stamp(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve()
    if not is_git_repo(project):
        print("Not a Git repository.")
        return 1
    commit = args.commit or head_commit(project)
    if not commit:
        print("Could not determine commit.")
        return 1

    target = Path(args.file)
    if not target.is_absolute():
        target = project / target
    if not target.exists():
        print(f"File not found: {target}")
        return 1

    text = target.read_text(encoding="utf-8")
    if "verified_commit:" not in text:
        print("File has no verified_commit field in frontmatter.")
        return 1

    import re
    new_text, count = re.subn(
        r'(?m)^(verified_commit:\s*)["\']?[^\n"\']*["\']?\s*$',
        lambda m: f'{m.group(1)}"{commit}"',
        text,
        count=1,
    )
    if count != 1:
        print("Could not update verified_commit.")
        return 1
    target.write_text(new_text, encoding="utf-8")
    print(f"Stamped {target.relative_to(project)} with {commit}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-handover", description="Context cache utilities for AI-assisted legacy-system handover.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Initialize .ai/ templates in a project")
    p_init.add_argument("project", nargs="?", default=".")
    p_init.add_argument("--force", action="store_true")
    p_init.set_defaults(func=cmd_init)

    p_card = sub.add_parser("new-card", help="Create a module or flow card from a template")
    p_card.add_argument("kind", choices=["module", "flow"])
    p_card.add_argument("name")
    p_card.add_argument("project", nargs="?", default=".")
    p_card.add_argument("--scope")
    p_card.add_argument("--filename")
    p_card.add_argument("--force", action="store_true")
    p_card.set_defaults(func=cmd_new_card)

    p_resolve = sub.add_parser("resolve", help="Rank relevant project context for a task")
    p_resolve.add_argument("task")
    p_resolve.add_argument("project", nargs="?", default=".")
    p_resolve.add_argument("--limit", type=int, default=5)
    p_resolve.set_defaults(func=cmd_resolve)

    p_pack = sub.add_parser("pack", help="Build a compact Markdown context pack")
    p_pack.add_argument("task")
    p_pack.add_argument("project", nargs="?", default=".")
    p_pack.add_argument("--limit", type=int, default=5)
    p_pack.add_argument("--output", "-o")
    p_pack.set_defaults(func=cmd_pack)

    p_fresh = sub.add_parser("freshness", help="Check whether cards may be stale relative to Git")
    p_fresh.add_argument("project", nargs="?", default=".")
    p_fresh.set_defaults(func=cmd_freshness)

    p_stamp = sub.add_parser("stamp", help="Set a card's verified_commit to current HEAD or a supplied commit")
    p_stamp.add_argument("file")
    p_stamp.add_argument("project", nargs="?", default=".")
    p_stamp.add_argument("--commit")
    p_stamp.set_defaults(func=cmd_stamp)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
