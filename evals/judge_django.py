#!/usr/bin/env python3
"""Score a Django Actor patch outside the Actor workspace."""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_PARENT = "73c5e94521c5b97e27cd2fe2d5b5c2e65f402755"
DEFAULT_TESTS = [
    "defer.tests.DeferTests.test_only",
    "defer.tests.DeferTests.test_only_related_manager_optimization",
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-repo", required=True)
    parser.add_argument("--hidden-test-patch", required=True)
    parser.add_argument("--parent", default=DEFAULT_PARENT)
    parser.add_argument("--test", action="append", dest="tests")
    parser.add_argument("--supplemental", help="Extra hidden test file copied after the patch, as DEST=SOURCE")
    parser.add_argument("--python", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--actor-patch")
    args = parser.parse_args()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(prefix="codekick-judge-ck05-") as temp:
        checkout = Path(temp) / "checkout"
        checkout.mkdir()
        archive = subprocess.run(["git", "-C", args.source_repo, "archive", args.parent],
                                 stdout=subprocess.PIPE, check=True)
        subprocess.run(["tar", "-C", str(checkout), "-xf", "-"], input=archive.stdout, check=True)
        subprocess.run(["git", "apply", str(Path(args.hidden_test_patch).resolve())], cwd=checkout, check=True)
        if args.supplemental:
            destination, source = args.supplemental.split("=", 1)
            target = checkout / destination
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(Path(source).read_bytes())
        tests = args.tests or DEFAULT_TESTS
        apply_mode = "no-actor-patch"
        if args.actor_patch:
            patch_path = Path(args.actor_patch).resolve()
            applied = subprocess.run(["git", "apply", "--binary", str(patch_path)], cwd=checkout,
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            (output / "patch-apply.log").write_text(applied.stdout)
            if applied.returncode == 0:
                apply_mode = "full-patch"
            else:
                production = []
                for part in patch_path.read_text().split("diff --git ")[1:]:
                    path = part.splitlines()[0].split(" ")[0][2:]
                    if not path.startswith("tests/"):
                        production.append("diff --git " + part)
                if not production:
                    result = {"passed": False, "reason": "actor patch did not apply", "exit_code": applied.returncode}
                    (output / "score.json").write_text(json.dumps(result, indent=2) + "\n")
                    print(json.dumps(result))
                    return
                production_patch = output / "production.patch"
                production_patch.write_text("".join(production))
                fallback = subprocess.run(["git", "apply", "--binary", str(production_patch)], cwd=checkout,
                                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                (output / "production-apply.log").write_text(fallback.stdout)
                if fallback.returncode:
                    result = {"passed": False, "reason": "actor production patch did not apply", "exit_code": fallback.returncode}
                    (output / "score.json").write_text(json.dumps(result, indent=2) + "\n")
                    print(json.dumps(result))
                    return
                apply_mode = "production-files-only"
        env = os.environ.copy()
        env.update(PYTHONPATH=str(checkout), PYTHONNOUSERSITE="1")
        completed = subprocess.run([args.python, "tests/runtests.py", *tests, "--settings=test_sqlite",
                                    "--parallel=1", "--verbosity=2"], cwd=checkout, env=env,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    (output / "stdout.txt").write_text(completed.stdout)
    passed = completed.returncode == 0 and "\nOK\n" in completed.stdout
    result = {"passed": passed, "exit_code": completed.returncode, "apply_mode": apply_mode,
              "failures_observed": "FAILED (failures=" in completed.stdout}
    (output / "score.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
    if not passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
