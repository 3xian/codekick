#!/usr/bin/env python3
"""Trusted Controller mailbox. Actor supplies operation IDs, never commands or roots.

Run only against an independently prepared source-free, network-none test container.
The container has no auth, Controller mounts, Docker socket, or hidden tests.
"""
import argparse
import base64
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import time


def verify_container(name, workspace, active):
    info = json.loads(subprocess.check_output(["docker", "inspect", name]))[0]
    host = info["HostConfig"]
    if host["NetworkMode"] != "none" or host.get("Privileged") or host.get("CapAdd") or host.get("SecurityOpt"):
        raise ValueError("Test container requires network=none and default unprivileged Docker confinement")
    mounts = info.get("Mounts", [])
    if len(mounts) != 1 or mounts[0]["Destination"] != active or Path(mounts[0]["Source"]).resolve() != workspace:
        raise ValueError("Test container may mount only the bound Actor workspace")
    return info["Image"]


def directory(path):
    return os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--container", required=True)
    parser.add_argument("--container-workspace", default="/workspace")
    parser.add_argument("--user", help="Fixed container user. Not chosen by the Actor.")
    parser.add_argument("--operations", required=True, help="Controller-only JSON: operation ID -> fixed argv array")
    parser.add_argument("--output", required=True, help="Controller-only raw test evidence directory")
    parser.add_argument("--time-budget", type=int, default=900)
    args = parser.parse_args()
    workspace = Path(args.workspace).resolve()
    output = Path(args.output).resolve()
    if output == workspace or workspace in output.parents:
        raise ValueError("Dispatcher evidence must be outside Actor workspace")
    output.mkdir(parents=True, exist_ok=True)
    operations = json.loads(Path(args.operations).read_text())
    def selector_schema(selector):
        allowed = {"position", "pattern"} | ({"package_pattern"} if "package_pattern" in selector else set())
        if not isinstance(selector, dict) or set(selector) != allowed or not isinstance(selector["position"], int) or selector["position"] < 0:
            raise ValueError("Selector schema must contain position, pattern, and optional package_pattern")
        for key in ("pattern", "package_pattern"):
            if key in selector:
                try:
                    re.compile(selector[key])
                except re.error as error:
                    raise ValueError(f"Selector {key} is not a valid regex") from error

    for key, spec in operations.items():
        argv = spec.get("argv") if isinstance(spec, dict) else spec
        selector = spec.get("selector") if isinstance(spec, dict) else None
        if not re.fullmatch(r"[a-z][a-z0-9_-]{0,40}", key) or not isinstance(argv, list) or not argv or not all(isinstance(s, str) and "\0" not in s for s in argv):
            raise ValueError("Operations must use fixed nonempty argv lists")
        if selector:
            selector_schema(selector)
            if selector["position"] > len(argv):
                raise ValueError("Selector position is outside fixed argv")
        if Path(argv[0]).name in ("sh", "bash", "zsh", "fish", "docker", "sudo", "su"):
            raise ValueError("Operation executables cannot be shells, privilege tools or Docker")
    image = verify_container(args.container, workspace, args.container_workspace)
    root_fd = directory(workspace)
    mailbox_fd = os.open(".codekick-runtime", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=root_fd)
    requests = os.open("requests", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=mailbox_fd)
    responses = os.open("responses", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=mailbox_fd)
    completed = set()
    print(json.dumps({"ready": True, "image_id": image, "operations": sorted(operations)}), flush=True)
    try:
        while True:
            for name in os.listdir(requests):
                if name in completed or not re.fullmatch(r"[0-9a-f]{32}\.json", name):
                    continue
                started = time.monotonic()
                try:
                    fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=requests)
                    with os.fdopen(fd, "rb") as stream:
                        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                            raise ValueError("Request is not a regular file")
                        request = json.loads(stream.read(4097))
                    expected = {"operation"} | ({"selector"} if isinstance(operations[request.get("operation")], dict) and operations[request.get("operation")].get("selector") else set())
                    if not isinstance(request, dict) or set(request) != expected or request["operation"] not in operations:
                        raise ValueError("Request fields do not match the fixed operation schema")
                    spec = operations[request["operation"]]
                    fixed_argv = spec.get("argv") if isinstance(spec, dict) else spec
                    selector_value = request.get("selector")
                    if selector_value is not None:
                        selector = spec["selector"]
                        if not isinstance(selector_value, str) or len(selector_value) > 500 or "\0" in selector_value:
                            raise ValueError("Test selector violates fixed safe pattern")
                        pieces = selector_value.split("::", 1)
                        package = pieces[0]
                        if ".." in Path(package).parts or Path(package).is_absolute() or package.startswith(("/", "\\")):
                            raise ValueError("Test selector escapes the Actor workspace")
                        if package.startswith("./"):
                            resolved = (workspace / package).resolve()
                            if resolved != workspace and workspace not in resolved.parents:
                                raise ValueError("Test selector symlink resolves outside the Actor workspace")
                        if "package_pattern" in selector:
                            if not re.fullmatch(selector["package_pattern"], package):
                                raise ValueError("Test package violates fixed safe pattern")
                            focus = pieces[1] if len(pieces) == 2 else None
                            if focus is not None and not re.fullmatch(selector["pattern"], focus):
                                raise ValueError("Focused test selector violates fixed safe pattern")
                            insertion = [package, "-run", focus] if focus else [package]
                        else:
                            if not re.fullmatch(selector["pattern"], selector_value) or ".." in Path(selector_value).parts:
                                raise ValueError("Test selector violates fixed safe pattern")
                            insertion = [selector_value]
                        fixed_argv = [*fixed_argv[:selector["position"]], *insertion, *fixed_argv[selector["position"]:]]
                    verify_container(args.container, workspace, args.container_workspace)
                    argv = ["docker", "exec", "--workdir", args.container_workspace]
                    if args.user:
                        argv.extend(["--user", args.user])
                    argv.extend([args.container, "timeout", "--signal=TERM", "--kill-after=5", str(args.time_budget), *fixed_argv])
                    result = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                            timeout=args.time_budget + 15, check=False)
                    evidence = output / name.removesuffix(".json")
                    evidence.mkdir(exist_ok=True)
                    (evidence / "stdout.bin").write_bytes(result.stdout)
                    (evidence / "stderr.bin").write_bytes(result.stderr)
                    response = {"operation": request["operation"], "argv": argv, "exit_code": result.returncode,
                                "wall_time_seconds": time.monotonic() - started,
                                "stdout_base64": base64.b64encode(result.stdout).decode(),
                                "stderr_base64": base64.b64encode(result.stderr).decode(), "image_id": image}
                    (evidence / "result.json").write_text(json.dumps(response, indent=2) + "\n")
                except (OSError, ValueError, TypeError, subprocess.SubprocessError) as error:
                    response = {"status": "BLOCKED", "error": str(error), "exit_code": 125,
                                "stdout_base64": "", "stderr_base64": base64.b64encode(str(error).encode()).decode()}
                public_response = {key: value for key, value in response.items()
                                   if key in ("status", "exit_code", "wall_time_seconds", "stdout_base64", "stderr_base64")}
                temporary = name + ".tmp"
                fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=responses)
                with os.fdopen(fd, "w") as stream:
                    json.dump(public_response, stream)
                os.rename(temporary, name, src_dir_fd=responses, dst_dir_fd=responses)
                completed.add(name)
            time.sleep(0.1)
    finally:
        for fd in (responses, requests, mailbox_fd, root_fd):
            os.close(fd)


if __name__ == "__main__":
    main()
