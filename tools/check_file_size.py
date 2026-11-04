"""Refuses code files over 150 useful lines, and Python functions over 60 (golden rule).

Useful lines: not blank, not a comment alone. Beyond the limit, the file or the function is split
by role. The component's files are held to the same limits by eslint.

  python tools/check_file_size.py              # whole repository
  python tools/check_file_size.py a.py b.py   # only these files (pre-commit)
"""

import ast
import re
import subprocess
import sys

from checks import ROOT, utf8_console

MAX_FILE_LINES = 150
MAX_FUNCTION_LINES = 60
CODE = re.compile(r"\.py$")
COMMENT = re.compile(r"^\s*(#|--|\{#)")
EXCLUDED: tuple[str, ...] = ()


def tracked_code_files() -> list[str]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [f for f in out.splitlines() if CODE.search(f) and not f.startswith(EXCLUDED)]


def useful(lines: list[str]) -> int:
    return sum(1 for line in lines if line.strip() and not COMMENT.match(line))


def long_functions(path: str, lines: list[str]) -> list[str]:
    problems = []
    for node in ast.walk(ast.parse("\n".join(lines))):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.end_lineno:
            count = useful(lines[node.lineno - 1 : node.end_lineno])
            if count > MAX_FUNCTION_LINES:
                problems.append(f"{path}: function {node.name}() has {count} useful lines (limit {MAX_FUNCTION_LINES})")
    return problems


def problems_in(path: str) -> list[str]:
    if not (ROOT / path).exists():  # tracked but deleted, its removal not staged yet: nothing to measure
        return []
    lines = (ROOT / path).read_text(encoding="utf-8").splitlines()
    problems = []
    if useful(lines) > MAX_FILE_LINES:
        problems.append(f"{path}: {useful(lines)} useful lines (limit {MAX_FILE_LINES}) — split it by role")
    if path.endswith(".py"):
        problems += long_functions(path, lines)
    return problems


def main(files: list[str]) -> int:
    candidates = [f.replace("\\", "/") for f in (files or tracked_code_files())]
    problems = [p for f in candidates if CODE.search(f) and not f.startswith(EXCLUDED) for p in problems_in(f)]
    for problem in problems:
        print(f"✗ {problem}")
    if not problems:
        print(f"✓ no file over {MAX_FILE_LINES} useful lines, no function over {MAX_FUNCTION_LINES}")
    return 1 if problems else 0


if __name__ == "__main__":
    utf8_console()
    sys.exit(main(sys.argv[1:]))
