"""The guards run by the git hooks and by CI (tools/hooks.py): one line per check.

Adding a check = adding a line to CHECKS. `pattern`: the staged files that trigger it before a commit;
`targets`: what it receives when run on the whole repository (None: it always runs on the whole repository).
"""

import datetime
import shutil
import sys
from pathlib import Path
from typing import NamedTuple
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
# The register's dates are written on the author's calendar; CI runs in UTC, up to two hours behind.
REGISTER_TIME_ZONE = ZoneInfo("Europe/Paris")


def register_today(now: datetime.datetime | None = None) -> datetime.date:
    """Today on the register's calendar, wherever the check runs."""
    return (now or datetime.datetime.now(datetime.UTC)).astimezone(REGISTER_TIME_ZONE).date()


def utf8_console() -> None:
    """The Windows console (cp1252) cannot print ✓ and ✗: force UTF-8 on the standard streams."""
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]


def node_tool(name: str) -> str:
    """A Node tool on the PATH (Node 22, stack.toml); npm installs the component's own tools."""
    found = shutil.which(name)
    if found is None:
        raise FileNotFoundError(f"{name} is not on the PATH: install Node 22, then `npm ci`.")
    return found


class Check(NamedTuple):
    name: str
    pattern: str
    command: list[str]
    targets: list[str] | None


CHECKS = [
    Check("ruff (Python lint)", r"\.py$", [PY, "-m", "ruff", "check"], ["."]),
    Check("ruff (Python format)", r"\.py$", [PY, "-m", "ruff", "format", "--check"], ["."]),
    Check("pyright (Python types)", r"\.py$", [PY, "-m", "pyright"], None),
    Check("file size (150 lines, 60 per function)", r"\.py$", [PY, "tools/check_file_size.py"], []),
    Check("documentation links", r"\.md$", [PY, "tools/check_links.py"], None),
    Check("features catalogue", r"^tests/|features\.md$", [PY, "tools/check_features.py"], None),
    Check("defects register", r"defects\.(toml|md)$|features\.md$", [PY, "tools/build_defects.py"], None),
    Check("format generated", r"^data_map/document\.py$|^format/|document\.ts$", [PY, "tools/build_format.py"], None),
    Check(
        "component (format, lint, types, tests, build)",
        r"^(component|demo|tests/component)/|\.(json|js|ts|svelte|css)$",
        [node_tool("npm"), "run", "check"],
        None,
    ),
]
