#!/usr/bin/env python3
"""Score an Actor workspace without exposing hidden tests to that workspace."""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def reject_actor_leak(workspace):
    workspace = Path(workspace).resolve()
    forbidden = []
    for path in workspace.rglob("*"):
        if not path.is_file():
            continue
        name = str(path.relative_to(workspace))
        if name.startswith("oracle/") or name in {"manifest.json", "manifest.yaml", "reference.patch", "regression.patch"}:
            forbidden.append(name)
    if forbidden:
        raise ValueError(f"Actor workspace contains controller-only paths: {forbidden}")


def score_behavior(source, hidden_test, output, command):
    """Copy source, add the hidden test only in the judge copy, run command."""
    source = Path(source).resolve()
    output = Path(output).resolve()
    reject_actor_leak(source)
    if output == source or source in output.parents or output in source.parents:
        raise ValueError("Judge evidence must stay outside the Actor workspace")
    output.mkdir(parents=True, exist_ok=False)
    judge = Path(tempfile.mkdtemp(prefix="codekick-judge-", dir=output))
    shutil.copytree(source, judge / "workspace", symlinks=True)
    hidden = judge / "workspace" / hidden_test.name
    if hidden.exists():
        raise ValueError("Hidden test name already exists in Actor source")
    shutil.copy2(hidden_test, hidden)
    completed = subprocess.run(command, cwd=judge / "workspace", stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, text=True, timeout=60, check=False)
    (output / "stdout.txt").write_text(completed.stdout)
    result = {"exit_code": completed.returncode, "passed": completed.returncode == 0,
              "hidden_test_sha256": sha(Path(hidden_test).read_bytes()),
              "actor_workspace_unchanged": not (source / hidden_test.name).exists()}
    (output / "score.json").write_text(json.dumps(result, indent=2) + "\n")
    if not result["actor_workspace_unchanged"]:
        raise RuntimeError("Judge wrote the hidden test into the Actor workspace")
    return result


def self_check():
    with tempfile.TemporaryDirectory(prefix="codekick-judge-smoke-") as temp:
        root = Path(temp)
        actor = root / "actor"
        actor.mkdir()
        (actor / "app.py").write_text("def value():\n    return 1\n")
        hidden = root / "hidden_test.py"
        hidden.write_text("import app\nassert app.value() == 2\n")
        failed = score_behavior(actor, hidden, root / "pre", [sys.executable, "hidden_test.py"])
        (actor / "app.py").write_text("def value():\n    return 2\n")
        passed = score_behavior(actor, hidden, root / "post", [sys.executable, "hidden_test.py"])
        leaked = actor / "oracle" / "reference.patch"
        leaked.parent.mkdir()
        leaked.write_text("diff\n")
        try:
            score_behavior(actor, hidden, root / "leak", [sys.executable, "hidden_test.py"])
        except ValueError:
            leak_rejected = True
        else:
            leak_rejected = False
    if not (failed["passed"] is False and passed["passed"] is True and leak_rejected
            and failed["actor_workspace_unchanged"] and passed["actor_workspace_unchanged"]):
        raise SystemExit(f"Judge self-check failed: pre={failed} post={passed} leak={leak_rejected}")
    print(json.dumps({"status": "JUDGE_SELF_CHECK_PASS", "pre_exit": failed["exit_code"],
                      "post_exit": passed["exit_code"], "hidden_test_not_written_to_actor": True}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("self-check")
    score = sub.add_parser("score")
    score.add_argument("--source", required=True)
    score.add_argument("--hidden-test", required=True)
    score.add_argument("--output", required=True)
    score.add_argument("--command", nargs="+", required=True)
    args = parser.parse_args()
    if args.action == "self-check":
        self_check()
    else:
        result = score_behavior(args.source, Path(args.hidden_test), Path(args.output), args.command)
        print(json.dumps(result))


if __name__ == "__main__":
    main()
