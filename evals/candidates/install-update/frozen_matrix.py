#!/usr/bin/env python3
"""Run the install/update matrix against frozen benchmark parent checkouts."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INSTALL = Path(__file__).with_name("install.py")
TARGETS = {
    "zulip": Path("/tmp/codekick-zulip-oracles.JS2a2B/CK-REAL-01/pre"),
    "gitea": Path("/tmp/codekick-install-parents/gitea"),
    "discourse": Path("/tmp/codekick-install-parents/discourse"),
    "django": Path("/tmp/codekick-install-parents/django"),
}
EXPECTED = {
    "zulip": "8b8ccfbe79853488760c51f0f820295b279ad40b",
    "gitea": "426bb491c0c2a92de8e25bfd5d1d3bc4b3e5922f",
    "discourse": "ffbf6cb8837e9e8d5012f6e215ff035fa11e8c8e",
    "django": "73c5e94521c5b97e27cd2fe2d5b5c2e65f402755",
}


def head(path):
    return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()


def run_install(source, dest, version):
    completed = subprocess.run([sys.executable, str(INSTALL), str(source), str(dest), version],
                               text=True, capture_output=True)
    if completed.returncode:
        raise RuntimeError(completed.stderr or completed.stdout)
    return json.loads(completed.stdout)


def manual_copy(source, dest):
    for name in ("AGENTS.md", ".ai", "skills", "templates", "scripts"):
        src = source / name
        target = dest / name
        if target.exists():
            shutil.rmtree(target) if target.is_dir() else target.unlink()
        if src.is_dir():
            shutil.copytree(src, target)
        else:
            shutil.copy2(src, target)


def check(name, checkout):
    observed = head(checkout)
    if observed != EXPECTED[name]:
        raise RuntimeError(f"{name} HEAD {observed} != {EXPECTED[name]}")
    parent = Path(tempfile.mkdtemp(prefix=f"codekick-frozen-{name}-"))
    subprocess.run(["cp", "-cR", f"{checkout}/.", str(parent)], check=True)
    upstream_agents = (parent / "AGENTS.md").read_text() if (parent / "AGENTS.md").is_file() else None
    manual = Path(tempfile.mkdtemp(prefix=f"codekick-manual-{name}-"))
    subprocess.run(["cp", "-cR", f"{parent}/.", str(manual)], check=True)
    if upstream_agents is None:
        (manual / "AGENTS.md").write_text("USER CUSTOM RULE\n")
    manual_before = (manual / "AGENTS.md").read_text()
    manual_copy(ROOT, manual)

    first = run_install(ROOT, parent, "baseline")
    fresh_preserved = (parent / "AGENTS.md").read_text() == upstream_agents if upstream_agents is not None else None
    second = run_install(ROOT, parent, "baseline")
    (parent / "AGENTS.md").write_text("USER CUSTOM RULE\n")
    (parent / ".ai").mkdir(exist_ok=True)
    (parent / ".ai/PROJECT.md").write_text("user project\n")
    (parent / ".ai/KNOWLEDGE.md").write_text("user knowledge must survive\n")
    run_install(ROOT, parent, "baseline")

    skill = parent / "skills/understand/SKILL.md"
    skill_bytes = skill.read_bytes()
    shutil.rmtree(parent / "skills")
    (parent / ".ai/.codekick-install.pending").write_text("interrupted\n")
    repaired = run_install(ROOT, parent, "baseline")
    restored_skill = skill.read_bytes() == skill_bytes
    pending_cleared = not (parent / ".ai/.codekick-install.pending").exists()
    knowledge_after_repair = (parent / ".ai/KNOWLEDGE.md").read_text() == "user knowledge must survive\n"

    source = Path(tempfile.mkdtemp(prefix=f"codekick-payload-{name}-"))
    for payload in ("AGENTS.md", ".ai", "skills", "templates", "scripts"):
        src = ROOT / payload
        target = source / payload
        if src.is_dir():
            shutil.copytree(src, target)
        else:
            shutil.copy2(src, target)
    marker = source / "skills/understand/SKILL.md"
    marker.write_text(marker.read_text() + "\n<!-- upgrade marker -->\n")
    upgraded = run_install(source, parent, "v2")
    return {
        "repo": name,
        "head": observed,
        "upstream_agents_present": upstream_agents is not None,
        "manual_overwrote_existing_agents": (manual / "AGENTS.md").read_text() != manual_before,
        "fresh_preserved_upstream_agents": fresh_preserved,
        "reinstall_skill_unchanged": any(item["path"] == "skills/understand/SKILL.md" and item["action"] == "unchanged" for item in second["actions"]),
        "custom_preserved_agents": (parent / "AGENTS.md").read_text() == "USER CUSTOM RULE\n",
        "custom_preserved_project": (parent / ".ai/PROJECT.md").read_text() == "user project\n",
        "custom_preserved_knowledge": knowledge_after_repair,
        "partial_restored_skill": restored_skill,
        "partial_preserved_knowledge": knowledge_after_repair,
        "pending_cleared": pending_cleared,
        "upgrade_preserved_agents": (parent / "AGENTS.md").read_text() == "USER CUSTOM RULE\n",
        "upgrade_updated_skill": "upgrade marker" in skill.read_text(),
        "stamp_version": json.loads((parent / ".ai/.codekick-install.json").read_text())["version"],
        "repaired_incomplete": repaired["repaired_incomplete"],
        "upgrade_action": next(item["action"] for item in upgraded["actions"] if item["path"] == "skills/understand/SKILL.md"),
        "fresh_actions_install": sum(item["action"] == "install" for item in first["actions"]),
    }


def main():
    results = [check(name, path) for name, path in TARGETS.items()]
    required = (
        "manual_overwrote_existing_agents", "reinstall_skill_unchanged", "custom_preserved_agents",
        "custom_preserved_project", "custom_preserved_knowledge", "partial_restored_skill",
        "partial_preserved_knowledge", "pending_cleared", "upgrade_preserved_agents",
        "upgrade_updated_skill", "repaired_incomplete",
    )
    failed = [item["repo"] for item in results if not all(item[key] for key in required)
              or item["stamp_version"] != "v2" or item["fresh_preserved_upstream_agents"] is False]
    out = Path(__file__).with_name("frozen-parent-matrix.json")
    out.write_text(json.dumps({"results": results, "failed": failed}, indent=2) + "\n")
    print(out.read_text())
    if failed:
        raise SystemExit(f"matrix failed: {failed}")


if __name__ == "__main__":
    main()
