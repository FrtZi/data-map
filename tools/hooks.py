"""Runs the guards for the git hooks (.githooks/) and for CI — the same commands everywhere.

  pre-commit: the checks concerned by the staged files, the Python tests, gitleaks.
  pre-push:   on a folder equal to its last commit only, every check on the whole repository and every test;
              refused too if a tracked file was written while they ran.
  ci:         pre-push, plus gitleaks over the whole history.

Hooks are never skipped (no --no-verify): CI runs the same checks and blocks anyway.
"""

import os
import re
import subprocess
import sys
import time

from checks import CHECKS, PY, ROOT, utf8_console

# Pinned by version and digest (stack.toml's target); Dependabot cannot read this line, so it is raised by hand.
GITLEAKS_IMAGE = (
    "ghcr.io/gitleaks/gitleaks:v8.30.1@sha256:c00b6bd0aeb3071cbcb79009cb16a60dd9e0a7c60e2be9ab65d25e6bc8abbb7f"
)
GITLEAKS = ["docker", "run", "--rm", "-v", f"{ROOT}:/repo", "-w", "/repo", GITLEAKS_IMAGE]
PYTEST = [PY, "-m", "pytest", "-q"]
failed: list[str] = []


def run(command: list[str], **options) -> subprocess.CompletedProcess:
    return subprocess.run(command, cwd=ROOT, check=False, env=os.environ, **options)


def step(name: str, command: list[str]) -> None:
    print(f"• {name} ...", flush=True)
    if run(command).returncode != 0:
        failed.append(name)
        print(f"  ✗ {name}", flush=True)


def git_lines(*arguments: str) -> list[str]:
    out = run(["git", *arguments], capture_output=True, text=True)
    return [line for line in out.stdout.splitlines() if line]


def run_checks(files: list[str], whole_repo: bool) -> None:
    for check in CHECKS:
        matching = [f for f in files if re.search(check.pattern, f)]
        if not whole_repo and not matching:
            continue
        if check.targets is None:
            step(check.name, check.command)
        else:
            step(check.name, check.command + (check.targets if whole_repo else matching))


def gitleaks(arguments: list[str]) -> None:
    if run(["docker", "info"], capture_output=True).returncode != 0:
        print("⚠ Docker is stopped: secret detection SKIPPED here (CI runs it).")
        return
    step("gitleaks (secrets)", GITLEAKS + [*arguments, "--redact", "--no-banner"])


def pre_commit() -> None:
    run_checks(git_lines("diff", "--cached", "--name-only", "--diff-filter=ACMR"), whole_repo=False)
    step("Python tests", PYTEST)
    gitleaks(["git", "--pre-commit", "--staged", "/repo"])


def written_since(started: float) -> list[str]:
    """The tracked files written after `started`: an edit undone before the end leaves the folder clean, yet the
    checks may have read it half-way. The checks themselves write no tracked file."""
    paths = (ROOT / name for name in git_lines("ls-files"))
    return [str(path) for path in paths if path.exists() and path.stat().st_mtime > started]


def pre_push() -> None:
    changes = git_lines("status", "--porcelain")
    if changes:
        print("✗ Commit or stash first: the checks run on the folder, which is not what is pushed:")
        print(*(f"   {change}" for change in changes[:10]), sep="\n")
        failed.append("uncommitted changes")
        return
    started = time.time()
    run_checks([], whole_repo=True)
    step("Python tests", PYTEST)
    if git_lines("status", "--porcelain") or written_since(started):  # what passed is not the commit
        print("✗ The folder changed while the checks ran: their result is not the commit's; push again.")
        failed.append("folder changed during the checks")


def ci() -> None:
    pre_push()
    gitleaks(["git", "/repo"])


def main() -> None:
    hook = sys.argv[1] if len(sys.argv) > 1 else "pre-commit"
    {"pre-commit": pre_commit, "pre-push": pre_push, "ci": ci}[hook]()
    if failed:
        print("\n✗ Blocked by:", ", ".join(failed))
        sys.exit(1)
    print("✓ guards OK")


if __name__ == "__main__":
    utf8_console()
    main()
