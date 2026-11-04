"""Follows the CI workflow's run of the pushed commit to its end, never "the latest run" (Dependabot runs too).

Right after a push, GitHub may not have created the run yet: the run is looked for again until it exists, instead
of watching an empty identifier (which `gh run watch` takes for a usage error).

  python tools/watch_ci.py
"""

import subprocess
import sys
import time
from collections.abc import Callable

from checks import utf8_console

ATTEMPTS = 20
WAIT_SECONDS = 6


def ci_run_of(commit: str) -> str:
    """The CI workflow's run for this commit, or "" while GitHub has not created it."""
    command = ["gh", "run", "list", "--workflow", "CI", "--commit", commit, "--json", "databaseId"]
    result = subprocess.run([*command, "-q", ".[0].databaseId"], capture_output=True, text=True, check=True)
    return result.stdout.strip()


def wait_for_run(
    commit: str, find: Callable[[str], str] = ci_run_of, pause: Callable[[float], None] = time.sleep
) -> str:
    """Looks for the run until it exists; fails after ATTEMPTS tries rather than watching nothing."""
    for _ in range(ATTEMPTS):
        run_id = find(commit)
        if run_id:
            return run_id
        pause(WAIT_SECONDS)
    raise TimeoutError(f"no CI run for {commit} after {ATTEMPTS * WAIT_SECONDS} s: was it pushed?")


def main() -> int:
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    run_id = wait_for_run(commit)
    print(f"CI run {run_id} for {commit[:7]}")
    return subprocess.run(["gh", "run", "watch", run_id, "--exit-status", "--compact"]).returncode


if __name__ == "__main__":
    utf8_console()
    sys.exit(main())
