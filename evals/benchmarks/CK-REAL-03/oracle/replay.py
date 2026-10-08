#!/usr/bin/env python3
"""Controller-only replay of the original GitLab release migration failure."""
import datetime
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile


ORACLE_TEST = "TestCodeKickGitlabHistoricalReleaseMigration"
TEST_PATTERN = "^(" + ORACLE_TEST + "|TestAwardsToReactions)$"
IMAGE = "codekick-gitea-runtime:1.25.5"


def main():
    oracle = Path(__file__).resolve().parent
    manifest = json.loads((oracle.parent / "manifest.json").read_text())
    workspace = Path(tempfile.mkdtemp(prefix="codekick-gitea-replay-"))
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    evidence = oracle / "replays" / stamp
    evidence.mkdir(parents=True)

    def prepare(command):
        completed = subprocess.run(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, text=True, timeout=600)
        with (evidence / "setup.log").open("a") as log:
            log.write(f"Command: {command!r}\n{completed.stdout}\nExit: {completed.returncode}\n")
        completed.check_returncode()
        return completed.stdout.strip()

    image_identity = prepare(["docker", "image", "inspect", IMAGE, "--format", "{{.Id}}"])
    repo = workspace / "repository"
    prepare(["git", "init", "--bare", str(repo)])
    git = ["git", f"--git-dir={repo}"]
    reference = manifest["reference_sha"]
    parent = manifest["verified_parent_sha"]
    prepare(git + ["fetch", "--depth=2", manifest["repo_url"], reference])
    if prepare(git + ["rev-parse", reference + "^"]) != parent:
        raise RuntimeError("Reference parent mismatch")
    results = {}
    for stage, revision in (("pre", parent), ("post", reference)):
        checkout = workspace / stage
        checkout.mkdir()
        archive = workspace / (stage + ".tar")
        with archive.open("wb") as stream:
            subprocess.run(git + ["archive", revision], stdout=stream, check=True, timeout=60)
        with tarfile.open(archive) as source:
            source.extractall(checkout, filter="data")
        package = checkout / "services" / "migrations"
        shutil.copyfile(oracle / "gitlab_release_oracle_test.go",
                        package / "codekick_release_oracle_test.go")
        (package / "testdata").mkdir(exist_ok=True)
        shutil.copyfile(oracle / "gitlab-release-fixture.json",
                        package / "testdata" / "codekick_gitlab_releases.json")
        command = ["docker", "run", "--rm", "--user", "1000:1000", "--network=none", "--cpus=2", "--memory=3g",
                   "--mount", f"type=bind,src={checkout},dst=/workspace,readonly",
                   "--tmpfs", "/home/codekick/.cache:uid=1000,gid=1000,mode=700",
                   "-w", "/workspace", IMAGE,
                   "go", "test", "-p", "2", "-tags", "sqlite,sqlite_unlock_notify",
                   "./services/migrations", "-run", TEST_PATTERN, "-count=1", "-v"]
        completed = subprocess.run(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, text=True, timeout=1800)
        (evidence / (stage + ".log")).write_text(
            f"Revision: {revision}\nImage: {image_identity}\nCommand: {command!r}\n"
            + completed.stdout + f"\nExit: {completed.returncode}\n")
        if stage == "pre":
            semantic = (completed.returncode != 0
                        and "index out of range [4] with length 4" in completed.stdout
                        and "convertGitlabRelease" in completed.stdout
                        and ORACLE_TEST in completed.stdout)
        else:
            semantic = (completed.returncode == 0
                        and "--- PASS: " + ORACLE_TEST in completed.stdout
                        and "--- PASS: TestAwardsToReactions" in completed.stdout)
        results[stage] = {"exit_code": completed.returncode,
                          "expected_behavior_observed": semantic,
                          "log": str(evidence / (stage + ".log"))}
    record = {"workspace": str(workspace), "image": image_identity,
              "oracle_origin": "Controller-designed test, captured original issue-linked GitLab response",
              "results": results}
    (evidence / "result.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({"evidence": str(evidence), **record}, indent=2))
    if not all(stage["expected_behavior_observed"] for stage in results.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
