"""Checks the features catalogue (docs/features.md) against the tests (MAINT-03).

Each test carries the identifiers of what it proves: `@pytest.mark.feature("ADM-01")` in Python, the
`describe` that names them in the component's tests (`describe("MAP-01 …")`, tests/component). Fails if
a test carries no identifier, if an identifier is not in the catalogue, if an identifier appears
twice in the catalogue, or if a feature marked Done has neither a tagged test nor another proof
("Check: …" or "Manual: …"): the catalogue cannot lie.

  python tools/check_features.py
"""

import ast
import re
import sys
from pathlib import Path

from checks import ROOT, utf8_console

CATALOGUE = ROOT / "docs" / "features.md"
ROW = re.compile(r"^\| ([A-Z]+-\d+) \|(.*)$", re.MULTILINE)
OTHER_PROOF = re.compile(r"\b(Check|Manual):")
COMPONENT_TESTS = ROOT / "tests" / "component"
DESCRIBE = re.compile(r"\bdescribe(?:\.each\([^)]*\))?\(\s*\"([^\"]*)\"")
IDENTIFIER = re.compile(r"\b[A-Z]+-\d+\b")


def catalogue() -> tuple[dict[str, tuple[str, str]], list[str]]:
    """{id: (status, proof)} and the identifiers that appear more than once."""
    features, duplicates = {}, []
    for identifier, rest in ROW.findall(CATALOGUE.read_text(encoding="utf-8")):
        cells = [cell.strip() for cell in rest.split("|")]
        if identifier in features:
            duplicates.append(identifier)
        features[identifier] = (cells[2], cells[3])
    return features, duplicates


def feature_ids(decorators: list[ast.expr]) -> list[str]:
    ids = []
    for decorator in decorators:
        if isinstance(decorator, ast.Call) and ast.unparse(decorator.func).endswith("mark.feature"):
            ids += [arg.value for arg in decorator.args if isinstance(arg, ast.Constant)]
    return ids


def tested_features() -> tuple[dict[str, set[str]], list[str]]:
    """{feature id: test files} and the tests that carry no identifier."""
    proofs: dict[str, set[str]] = {}
    untagged = []
    for path in sorted((ROOT / "tests").rglob("test_*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                ids = feature_ids(node.decorator_list)
                name = f"{path.relative_to(ROOT).as_posix()}::{node.name}"
                untagged += [] if ids else [name]
                for identifier in ids:
                    proofs.setdefault(identifier, set()).add(path.relative_to(ROOT).as_posix())
    return proofs, untagged


def component_tested_features(folder: Path = COMPONENT_TESTS) -> tuple[dict[str, set[str]], list[str]]:
    """The same from the component's tests: the identifiers a `describe` names, and the files with none."""
    proofs: dict[str, set[str]] = {}
    untagged = []
    for path in sorted(folder.rglob("*.test.ts")):
        ids = [i for title in DESCRIBE.findall(path.read_text(encoding="utf-8")) for i in IDENTIFIER.findall(title)]
        name = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.name
        untagged += [] if ids else [name]
        for identifier in ids:
            proofs.setdefault(identifier, set()).add(name)
    return proofs, untagged


def main() -> int:
    features, duplicates = catalogue()
    proofs, untagged = tested_features()
    component_proofs, component_untagged = component_tested_features()
    untagged += component_untagged
    for identifier, files in component_proofs.items():
        proofs.setdefault(identifier, set()).update(files)
    problems = [f"{i}: appears more than once in the catalogue" for i in duplicates]
    problems += [f"test without a feature identifier: {name}" for name in untagged]
    problems += [f"tests tagged {i}: no such feature in the catalogue" for i in sorted(set(proofs) - set(features))]
    for identifier, (status, proof) in features.items():
        if status == "Done" and identifier not in proofs and not OTHER_PROOF.search(proof):
            problems.append(f"{identifier}: Done without a tagged test or another proof")
    for problem in problems:
        print(f"✗ {problem}")
    if not problems:
        print(f"✓ {len(features)} features, {len(proofs)} proven by tagged tests")
    return 1 if problems else 0


if __name__ == "__main__":
    utf8_console()
    sys.exit(main())
