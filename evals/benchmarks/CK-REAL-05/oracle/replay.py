#!/usr/bin/env python3
"""Replay the frozen historical benchmark. Controller-only; never mount for Actor."""
import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main():
    if sys.version_info < (3, 12):
        raise SystemExit("Python 3.12 or newer is required.")
    oracle = Path(__file__).resolve().parent
    manifest = json.loads((oracle.parent / "manifest.json").read_text())
    workspace = Path(tempfile.mkdtemp(prefix="codekick-django-replay-"))
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    evidence = oracle / "replays" / stamp
    evidence.mkdir(parents=True)
    setup_log = evidence / "setup.log"

    def run(command, cwd=None, env=None):
        completed = subprocess.run(command, cwd=cwd, env=env,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, timeout=600)
        with setup_log.open("a") as log:
            log.write(f"Command: {command!r}\nCWD: {str(cwd)!r}\n")
            log.write(completed.stdout + f"\nExit: {completed.returncode}\n")
        if completed.returncode:
            raise RuntimeError(f"Command failed; see {setup_log}")
        return completed.stdout.strip()

    git = shutil.which("git")
    if not git:
        raise SystemExit("git is required.")
    repo = workspace / "repo"
    run([git, "init", "--bare", str(repo)])
    git_repo = [git, f"--git-dir={repo}"]
    reference = manifest["reference_sha"]
    parent = manifest["verified_parent_sha"]
    run(git_repo + ["fetch", "--depth=2", manifest["repo_url"], reference])
    if run(git_repo + ["rev-parse", reference]) != reference:
        raise RuntimeError("Reference identity mismatch.")
    if run(git_repo + ["rev-parse", reference + "^"]) != parent:
        raise RuntimeError("Verified parent identity mismatch.")
    venv = workspace / "venv"
    run([sys.executable, "-m", "venv", str(venv)])
    python = venv / "bin" / "python"
    run([str(python), "-m", "pip", "install", "-r", str(oracle / "requirements.lock")])
    patch = oracle / "regression-tests.patch"
    for line in patch.read_text().splitlines():
        if line.startswith("diff --git ") and not line.startswith("diff --git a/tests/"):
            raise RuntimeError("Backport contains a non-test path.")
    results = {}
    for stage, revision in (("pre", parent), ("post", reference)):
        checkout = workspace / stage
        run(git_repo + ["worktree", "add", "--detach", str(checkout), revision])
        if stage == "pre":
            run([git, "-C", str(checkout), "apply", str(patch)])
        supplement = manifest.get("supplemental_test")
        if supplement:
            shutil.copyfile(oracle.parent / supplement,
                            checkout / "tests/admin_changelist/test_codekick_index.py")
        changed = run([git, "-C", str(checkout), "diff", "--name-only"])
        if any(not path.startswith("tests/") for path in changed.splitlines()):
            raise RuntimeError("Production files changed before replay.")
        env = os.environ.copy()
        env.update(PYTHONPATH=str(checkout), PYTHONNOUSERSITE="1")
        command = [str(python), "tests/runtests.py", *manifest["commands"]["tests"],
                   *manifest["commands"]["runner_flags"]]
        completed = subprocess.run(command, cwd=checkout, env=env,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, timeout=600)
        log = evidence / f"{stage}.log"
        log.write_text(f"HEAD: {revision}\nCommand: {command!r}\nCWD: {checkout}\n"
                       f"PYTHONPATH: {checkout}\nPYTHONNOUSERSITE: 1\n"
                       + completed.stdout + f"\nExit: {completed.returncode}\n")
        expected = manifest[stage]["exit_code"]
        behavioral = ("FAILED (failures=" in completed.stdout if stage == "pre"
                      else "\nOK\n" in completed.stdout)
        results[stage] = {"exit_code": completed.returncode,
                          "expected_exit_code": expected,
                          "behavioral_result_observed": behavioral, "log": str(log)}
    (evidence / "result.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps({"workspace": str(workspace), "evidence": str(evidence),
                      "results": results}, indent=2))
    if any(r["exit_code"] != r["expected_exit_code"] or not r["behavioral_result_observed"]
           for r in results.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
