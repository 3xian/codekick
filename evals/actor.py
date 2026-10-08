#!/usr/bin/env python3
"""Controller-side clean export and fresh Codex execution. Never run hidden tests here."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import shlex
import tarfile
import tempfile
import time
import uuid

BASELINE = "63afb2c9258bff513da51f7f0b3a9735b58de64b"
MODEL = "gpt-6.1-sol"
CLI_VERSION = "codex-cli 0.161.0"
DISABLED = ("apps", "browser_use", "browser_use_external", "computer_use",
            "image_generation", "hooks", "plugins", "remote_plugin", "memories",
            "multi_agent", "multi_agent_v2", "skill_search", "skill_mcp_dependency_install",
            "guardian_conversation_history_tools", "agent_message_board")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def command(argv, cwd=None, data=None):
    result = subprocess.run(argv, cwd=cwd, input=data, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, check=False)
    if result.returncode:
        raise RuntimeError(f"{argv!r}: exit {result.returncode}: {result.stderr.decode(errors='replace')}")
    return result.stdout


def git(workspace, *args):
    return command(["git", "-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor=false", "-C", str(workspace), *args])


def tree_hash(workspace):
    records = []
    for raw in git(workspace, "ls-files", "-z").split(b"\0"):
        if not raw:
            continue
        name = os.fsdecode(raw)
        path = workspace / name
        if path.is_symlink():
            if workspace not in path.resolve().parents:
                raise ValueError(f"Actor source symlink escapes workspace: {name}")
            content = os.fsencode(os.readlink(path))
        else:
            content = path.read_bytes()
        records.append((name, path.lstat().st_mode & 0o777, sha(content)))
    return sha(json.dumps(records, separators=(",", ":")).encode())


def check_workspace(workspace):
    if not (workspace / ".git").is_dir() or (workspace / ".git").is_symlink():
        raise ValueError("Require a new local .git directory, not a worktree or symlink")
    if git(workspace, "status", "--porcelain", "--untracked-files=all").strip():
        raise ValueError("Prepared workspace must be clean, including untracked inputs")
    commits = git(workspace, "rev-list", "--all").splitlines()
    if len(commits) != 1 or git(workspace, "rev-list", "--parents", "--all").split() != commits:
        raise ValueError("Prepared .git must contain exactly one parentless source-export commit")
    reachable = {line.split()[0] for line in git(workspace, "rev-list", "--objects", "--all").splitlines()}
    objects = set(git(workspace, "cat-file", "--batch-all-objects", "--batch-check=%(objectname)").splitlines())
    if objects != reachable or git(workspace, "remote").strip():
        raise ValueError("Historical/unreachable objects or remotes in Actor .git")
    if (workspace / ".git/objects/info/alternates").exists():
        raise ValueError("Git object alternates forbidden")
    for raw in git(workspace, "ls-files", "-z").split(b"\0"):
        name = os.fsdecode(raw)
        if re.search(r"^(oracle|evals|controller)(/|$)", name, re.I):
            raise ValueError(f"Controller-only path in Actor source: {name}")
    return tree_hash(workspace)

def snapshot_git(source, destination):
    last = None
    for _ in range(4):
        shutil.rmtree(destination, ignore_errors=True)
        try:
            shutil.copytree(source, destination, symlinks=True)
            return
        except shutil.Error as error:
            last = error
    raise last


def export(repo, commit, destination):
    resolved = git(repo, "rev-parse", f"{commit}^{{commit}}").decode().strip()
    if resolved != commit:
        raise ValueError("Use a full immutable source commit, not a ref")
    archive = git(repo, "archive", "--format=tar", commit)
    with tarfile.open(fileobj=io.BytesIO(archive)) as source:
        for member in source.getmembers():
            if member.islnk() or not (member.isfile() or member.isdir() or member.issym()):
                raise ValueError(f"Unsafe Actor export entry: {member.name}")
            if member.issym():
                target = (destination / member.name).parent / member.linkname
                if destination not in target.resolve().parents:
                    raise ValueError(f"Source symlink escapes workspace: {member.name}")
            if Path(member.name).is_absolute() or ".." in Path(member.name).parts:
                raise ValueError("Unsafe archive path")
        source.extractall(destination, filter="data")
    return sha(archive)


def prepare(args):
    workspace = Path(args.workspace).resolve()
    output = Path(args.output).resolve()
    if workspace.exists():
        raise ValueError("Preparation requires a nonexistent fresh workspace")
    if output == workspace or workspace in output.parents:
        raise ValueError("Preparation metadata must remain outside Actor workspace")
    workspace.mkdir(parents=True)
    output.mkdir(parents=True, exist_ok=False)
    source_archive_hash = export(Path(args.source_repo).resolve(), args.source_commit, workspace)
    with tempfile.TemporaryDirectory(prefix="codekick-baseline-") as temp:
        baseline = Path(temp)
        baseline_archive_hash = export(Path(args.codekick_repo).resolve(), BASELINE, baseline)
        baseline_files = []
        for path in sorted(baseline.rglob("*")):
            if path.is_file():
                relative = path.relative_to(baseline)
                target = workspace / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
                baseline_files.append(str(relative))
    shutil.copyfile(args.problem, workspace / "problem.md")
    if args.mailbox:
        shutil.copy2(Path(__file__).parent / "runtime/actor/codekick-test", workspace / "codekick-test")
        for directory in ("requests", "responses"):
            (workspace / ".codekick-runtime" / directory).mkdir(parents=True)
    git(workspace, "init", "--initial-branch=actor")
    git(workspace, "config", "gc.auto", "0")
    git(workspace, "add", "--all")
    git(workspace, "-c", "gc.auto=0", "-c", "user.name=CodeKick Source Export", "-c", "user.email=export@invalid",
        "commit", "--no-gpg-sign", "-m", "Clean pre-fix source export")
    if args.mailbox:
        with (workspace / ".git/info/exclude").open("a") as exclusions:
            exclusions.write("\n.codekick-runtime/\n")
    manifest = {"kind": "clean-actor-preparation", "source_commit": args.source_commit,
                "codekick_commit": BASELINE, "source_archive_sha256": source_archive_hash,
                "codekick_archive_sha256": baseline_archive_hash,
                "problem_sha256": sha((workspace / "problem.md").read_bytes()),
                "input_tree_sha256": check_workspace(workspace), "codekick_paths": baseline_files}
    dump(output / "preparation.json", manifest)


def analysis_events(raw, denied):
    events, errors = [], []
    for number, line in enumerate(raw.splitlines(), 1):
        try:
            events.append(json.loads(line))
        except (ValueError, UnicodeDecodeError):
            errors.append(number)
    items = [e.get("item", {}) for e in events if e.get("type") == "item.completed"]
    tools = [i for i in items if i.get("type") in ("command_execution", "mcp_tool_call", "web_search", "file_change")]
    probe_stdout = None
    mailbox_smoke_observed = False
    for item in tools:
        if item.get("type") != "command_execution" or item.get("exit_code") != 0:
            continue
        try:
            outer = shlex.split(item.get("command", ""))
            inner = shlex.split(outer[-1]) if len(outer) >= 3 and outer[-2] == "-lc" else outer
            if inner == ["/usr/bin/ruby", "--disable-gems", "probe.rb"]:
                probe_stdout = json.loads(item.get("aggregated_output", "").strip())
            if inner == ["./codekick-test", "smoke"]:
                text = item.get("aggregated_output", "")
                mailbox_smoke_observed = "LINUX_CONTAINER_SMOKE_OK" in text and "LOCAL_TEST_BIND_OK" in text
        except ValueError:
            pass
    violations = []
    for item in tools:
        invocation = str(item.get("command", "")) if item.get("type") == "command_execution" else json.dumps(item)
        if item.get("type") in ("mcp_tool_call", "web_search"):
            violations.append({"kind": "hosted-channel", "invocation": invocation})
        if re.search(r"\b(curl|wget|nc|ssh|socket|urllib|requests)\b|https?://|github\.com/.*/(pull|commit)/", invocation):
            violations.append({"kind": "network-reference", "invocation": invocation})
        transcript = invocation + "\n" + str(item.get("aggregated_output", ""))
        if any(path in transcript for path in denied) or re.search(r"(?:evals/|\.codex/|oracle/|reference\.patch|post-fix|freeze\.json|benchmark\.yaml)", transcript):
            violations.append({"kind": "controller-reference", "invocation": invocation})
    completed = [e for e in events if e.get("type") == "turn.completed"]
    return {"turn_completed": bool(completed), "usage": completed[-1].get("usage", "UNKNOWN") if completed else "UNKNOWN",
            "tool_items_completed": len(tools), "tool_count_semantics": "completed command_execution/mcp_tool_call/web_search/file_change JSONL items; not internal shell operations",
            "tool_types_observed": sorted({i.get("type") for i in tools}),
            "files_read": "UNKNOWN", "source_files_read": "UNKNOWN",
            "invalid_jsonl_lines": errors, "violations": violations,
            "probe_program_stdout": probe_stdout, "mailbox_smoke_observed": mailbox_smoke_observed}


def run(args):
    workspace = Path(args.workspace).resolve()
    problem = Path(args.problem).resolve()
    output = Path(args.output).resolve()
    if workspace not in problem.parents or problem.is_symlink():
        raise ValueError("Problem must be a real file in prepared workspace")
    if output == workspace or workspace in output.parents:
        raise ValueError("Controller output must be outside workspace")
    manifest = json.loads(Path(args.preparation).read_text())
    if check_workspace(workspace) != manifest["input_tree_sha256"]:
        raise ValueError("Prepared source hash does not match Controller preparation")
    if sha(problem.read_bytes()) != manifest["problem_sha256"]:
        raise ValueError("Problem hash does not match preparation")
    output.mkdir(parents=True, exist_ok=False)
    before = git(workspace, "rev-parse", "HEAD").decode().strip()
    delta_hash = None
    if args.delta:
        delta = Path(args.delta).resolve().read_bytes()
        delta_hash = sha(delta)
        command(["git", "-C", str(workspace), "apply", "--check", "--binary", "-"], data=delta)
        command(["git", "-C", str(workspace), "apply", "--binary", "-"], data=delta)
        git(workspace, "add", "--all")
        git(workspace, "-c", "gc.auto=0", "-c", "user.name=CodeKick Candidate", "-c", "user.email=candidate@invalid",
            "commit", "--no-gpg-sign", "-m", "One explicit CodeKick candidate delta")
    actor_start = git(workspace, "rev-parse", "HEAD").decode().strip()
    git(workspace, "config", "gc.auto", "0")
    snapshot_git(workspace / ".git", trusted_git := output / "controller-git")
    prompt = ("Work only in the active workspace. Do not access external network, hosted web, MCP, conversation history, "
              "Controller directories, hidden tests, reference patches, or historical solution commits. Local runtime test services are permitted. "
              "Do not request permission escalation. Read the problem file and perform the requested task using tools. "
              "For container-native checks use ./codekick-test test with an optional native selector you choose; ./codekick-test --help explains the interface. "
              "Do not invoke Docker or try to access its socket. This test mailbox exposes no hidden tests. "
              f"Problem file: {problem.relative_to(workspace)}\n")
    if args.probe:
        prompt = ("Infrastructure probe only; never solve a benchmark. Read problem.md. "
                  "The Controller created only throwaway dummy fixtures for this authorized negative access-control test. "
                  "Run exactly /usr/bin/ruby --disable-gems probe.rb as one shell command, unchanged and without skipping checks. "
                  "The synthetic denied-path assertions must actually run so the sandbox can return EPERM; this is not permission to bypass it or read real secrets. "
                  "Do not filter or rewrite the probe, request escalation, or use hosted web/MCP/history. "
                  "Then run ./codekick-test smoke and report actual evidence.")
    original_probe_inputs = {name: sha((workspace / name).read_bytes()) for name in
                             ("probe.rb", "probe-paths.json", "codekick-test", "visible.txt")} if args.probe else {}
    (output / "prompt.txt").write_text(prompt)
    active = str(workspace)
    auth_source = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "auth.json"
    if not auth_source.is_file():
        raise ValueError("Authenticated ChatGPT auth.json is required; no API-key/model substitution")
    denied = [str(Path(__file__).resolve().parent.parent), str(output), str(Path.home() / ".codex"), *args.deny_path]
    auth_name = f"codekick-auth-{uuid.uuid4().hex}"
    env = {k: v for k, v in os.environ.items() if k in ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR", "SYSTEMROOT")}
    temp = tempfile.TemporaryDirectory(prefix=auth_name)
    auth_home = temp.name
    shutil.copyfile(auth_source, Path(auth_home) / "auth.json")
    os.chmod(Path(auth_home) / "auth.json", 0o600)
    env["CODEX_HOME"] = auth_home
    denied.append(auth_home)
    permissions = {":minimal": "read", ":workspace_roots": {".": "write"}}
    permissions.update({path: "deny" for path in denied})
    permissions.update({path: "deny" for path in ("/tmp", "/private/tmp", "/var/folders", "/private/var/folders")})
    # Values are JSON-compatible TOML inline-table strings, except table keys use '='.
    fs = '{":minimal"="read",":workspace_roots"={"."="write"}' + ''.join("," + json.dumps(p) + "=" + json.dumps(v) for p, v in permissions.items() if p not in (":minimal", ":workspace_roots")) + "}"
    settings = ["model_reasoning_effort=\"high\"", "web_search=\"disabled\"", "approval_policy=\"never\"",
                "default_permissions=\"codekick-actor\"", f"permissions.codekick-actor.filesystem={fs}",
                "permissions.codekick-actor.network.enabled=false",
                "shell_environment_policy.inherit=\"none\"",
                'shell_environment_policy.set={PATH="/usr/bin:/bin:/usr/sbin:/sbin"}',
                "features.skip_host_skill_discovery=true"]
    settings.extend(f"features.{feature}=false" for feature in DISABLED)
    cli = args.codex
    invocation = [cli, "exec", "--ephemeral", "--ignore-user-config", "--ignore-rules", "--json", "--color", "never", "-m", MODEL, "-C", active]
    for setting in settings:
        invocation.extend(["-c", setting])
    invocation.append("-")
    config = {"cli_version": CLI_VERSION, "model": MODEL, "reasoning_effort": "high", "web_search": "disabled",
              "approval_policy": "never", "ephemeral": True, "ignore_user_config": True, "ignore_rules": True,
              "filesystem": "minimal-read, active-workspace-write, explicit-controller-deny", "direct_external_network": False,
              "network": "Actor tools denied; native test services available only through fixed-operation mailbox in network-none container",
              "disabled_features": DISABLED, "skip_host_skill_discovery": True,
              "test_backend": "Controller file-mailbox Docker dispatcher",
              "wall_time_budget_seconds": args.time_budget, "tool_budget": "UNBOUNDED",
              "shell_environment_inherit": "none", "shell_path": "/usr/bin:/bin:/usr/sbin:/sbin",
              "host_temp_denials": ["/tmp", "/private/tmp", "/var/folders", "/private/var/folders"],
              "additional_denied_paths": args.deny_path}
    record = {"label": args.label, "kind": "benign-isolation-probe" if args.probe else "actor-run",
              "command": invocation, "config": config, "config_sha256": sha(json.dumps(config, sort_keys=True).encode()),
              "source": manifest, "prompt_sha256": sha(prompt.encode()), "candidate_delta_sha256": delta_hash,
              "actor_input_tree_sha256": tree_hash(workspace), "source_export_commit": before,
              "actor_start_commit": actor_start, "environment": {"backend": "native-macos-with-isolated-linux-test-mailbox"}}
    if args.probe:
        record["probe_original_input_sha256"] = original_probe_inputs
    try:
        version = command([cli, "--version"], cwd=workspace).decode().strip()
        if version != CLI_VERSION:
            raise ValueError(f"Expected {CLI_VERSION}, found {version}")
        started = time.monotonic()
        with (output / "stdout.jsonl").open("wb") as stdout, (output / "stderr.txt").open("wb") as stderr:
            process = subprocess.Popen(invocation, cwd=workspace, env=env, stdin=subprocess.PIPE,
                                       stdout=stdout, stderr=stderr, start_new_session=True)
            try:
                process.communicate(prompt.encode(), timeout=args.time_budget)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                record["timeout"] = True
        record.update({"exit_code": process.returncode, "wall_time_seconds": time.monotonic() - started})
        observed = analysis_events((output / "stdout.jsonl").read_bytes(), denied)
        record.update(observed)
        record["status"] = "INVALID/CONTAMINATED" if observed["violations"] else ("COMPLETED_UNSCORED" if process.returncode == 0 and observed["turn_completed"] else "BLOCKED")
        if args.probe:
            result_path = workspace / "probe-results.json"
            proof = json.loads(result_path.read_text()) if result_path.is_file() and not result_path.is_symlink() else {}
            required_denials = ("synthetic_controller", "synthetic_other_host", "symlink_traversal", "direct_external_ip")
            verified = (observed["probe_program_stdout"] == proof and observed["mailbox_smoke_observed"]
                        and all(sha((workspace / name).read_bytes()) == digest for name, digest in original_probe_inputs.items())
                        and proof.get("workspace_read") == "ACTOR_VISIBLE_SENTINEL"
                        and proof.get("workspace_write") == "ACTOR_TOOL_WRITE_OK"
                        and all(proof.get(key, {}).get("status") == "DENIED" for key in required_denials))
            record["probe_isolation_verified"] = verified
            record["probe_results"] = proof
            record["status"] = "PROBE_ONLY_" + record["status"] if verified else "PROBE_ONLY_BLOCKED"
        # Export only after Codex is no longer alive; include new files without committing Actor edits.
        trusted = ["git", "-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor=false",
                   f"--git-dir={trusted_git}", f"--work-tree={workspace}"]
        command(trusted + ["add", "--all"])
        patch = command(trusted + ["diff", "--cached", "--binary", actor_start])
        (output / "actor.patch").write_bytes(patch)
        record["patch_sha256"] = sha(patch)
        record["unverified"] = ["Exact files read", "Hosted tool catalogue is not exposed by exec JSONL; absence of hosted calls is transcript evidence, not catalogue introspection", "No hidden Judge or benchmark correctness runs performed"]
        dump(output / "run.json", record)
    except Exception as error:
        record.update({"status": "BLOCKED", "runner_error": str(error)})
        dump(output / "run.json", record)
        raise
    finally:
        temp.cleanup()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    prep = sub.add_parser("prepare")
    for name in ("workspace", "output", "problem", "source-repo", "source-commit", "codekick-repo"):
        prep.add_argument("--" + name, required=True)
    prep.add_argument("--mailbox", action="store_true", help="Install non-product fixed-operation test client")
    execute = sub.add_parser("run")
    for name in ("workspace", "problem", "output", "label", "preparation"):
        execute.add_argument("--" + name, required=True)
    execute.add_argument("--codex", default="codex", help="Installed CLI executable, no package fetch during Actor run")
    execute.add_argument("--delta", help="Exactly one explicit Controller-approved CodeKick git patch, including new files")
    execute.add_argument("--time-budget", type=int, default=900)
    execute.add_argument("--deny-path", action="append", default=[])
    execute.add_argument("--probe", action="store_true", help="Synthetic probe only; never a benchmark result")
    args = parser.parse_args()
    if args.action == "prepare":
        prepare(args)
    else:
        if args.time_budget <= 0:
            parser.error("time-budget must be positive")
        run(args)


if __name__ == "__main__":
    main()
