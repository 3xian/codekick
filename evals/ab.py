#!/usr/bin/env python3
"""Pair baseline and one-candidate runs. Does not launch a model unless asked."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def require_probe(path):
    record = load(path)
    if record.get("kind") != "benign-isolation-probe" or record.get("probe_isolation_verified") is not True:
        raise ValueError("Real Actor launch requires a verified benign isolation probe")
    github = record.get("probe_program_stdout", {}).get("external_github", {})
    return {"status": "PROBE_ACCEPTED", "github_name_lookup": github.get("status", "MISSING"),
            "note": "GitHub name lookup is not relabeled DENIED. Raw IP denial is a separate probe field."}


def check_pair(a_prep, b_prep, delta_sha):
    left = load(a_prep)
    right = load(b_prep)
    if left.get("kind") != "clean-actor-preparation" or right.get("kind") != "clean-actor-preparation":
        raise ValueError("Both sides must be clean Actor preparations")
    keys = ("source_commit", "codekick_commit", "source_archive_sha256", "problem_sha256")
    for key in keys:
        if left.get(key) != right.get(key):
            raise ValueError(f"A/B input differs in {key}")
    if left["input_tree_sha256"] == right["input_tree_sha256"] and delta_sha:
        raise ValueError("Candidate side must differ by exactly the approved delta")
    if not delta_sha and left["input_tree_sha256"] != right["input_tree_sha256"]:
        raise ValueError("Baseline pair must have identical input trees")
    return {"status": "PAIR_OK", "shared_source_commit": left["source_commit"],
            "shared_codekick_commit": left["codekick_commit"], "delta_sha256": delta_sha}


def score_both(a_source, b_source, hidden_test, output, command):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    results = {}
    for label, source in (("A", a_source), ("B", b_source)):
        completed = subprocess.run([sys.executable, str(Path(__file__).with_name("judge.py")), "score",
                                    "--source", source, "--hidden-test", hidden_test,
                                    "--output", str(output / label), "--command", *command],
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False)
        (output / f"{label}.log").write_text(completed.stdout)
        if completed.returncode:
            raise RuntimeError(f"Judge failed for {label}: {completed.stdout}")
        results[label] = json.loads((output / label / "score.json").read_text())
    summary = {"A_passed": results["A"]["passed"], "B_passed": results["B"]["passed"],
               "winner": "B" if results["B"]["passed"] and not results["A"]["passed"] else "NONE",
               "note": "Fixture or supplied command score only. Not a CodeKick product ACCEPT."}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def self_check():
    import tempfile
    with tempfile.TemporaryDirectory(prefix="codekick-ab-smoke-") as temp:
        root = Path(temp)
        a = root / "a"
        b = root / "b"
        a.mkdir()
        b.mkdir()
        (a / "app.py").write_text("def value():\n    return 1\n")
        (b / "app.py").write_text("def value():\n    return 2\n")
        hidden = root / "hidden_test.py"
        hidden.write_text("import app\nassert app.value() == 2\n")
        summary = score_both(a, b, hidden, root / "out", [sys.executable, "hidden_test.py"])
        (root / "bad-probe.json").write_text('{"kind":"actor-run","probe_isolation_verified":false}\n')
        try:
            require_probe(root / "bad-probe.json")
        except ValueError:
            rejected = True
        else:
            rejected = False
    if not rejected or summary != {"A_passed": False, "B_passed": True, "winner": "B",
                                   "note": "Fixture or supplied command score only. Not a CodeKick product ACCEPT."}:
        raise SystemExit(f"A/B self-check failed: {summary} rejected={rejected}")
    print(json.dumps({"status": "AB_SELF_CHECK_PASS", **summary, "unverified_probe_rejected": rejected}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("self-check")
    check = sub.add_parser("check-pair")
    check.add_argument("--a-preparation", required=True)
    check.add_argument("--b-preparation", required=True)
    check.add_argument("--delta-sha256", default="")
    probe = sub.add_parser("require-probe")
    probe.add_argument("--probe", required=True)
    args = parser.parse_args()
    if args.action == "self-check":
        self_check()
    elif args.action == "require-probe":
        print(json.dumps(require_probe(args.probe)))
    else:
        print(json.dumps(check_pair(args.a_preparation, args.b_preparation, args.delta_sha256)))


if __name__ == "__main__":
    main()
