"""Defects register: checks docs/defects.toml and generates its readable page, docs/defects.md.

Ported from Portfolio Advisor's tools/build_defects.py (the format shared by every project of the workspace:
same keys everywhere, values in the repository's language). Fails if an entry is incomplete, if a value is
outside the lists below, if the entries do not follow each other (DEF-001, DEF-002… in date order), if a proof
file is missing or does not name its defect, or if a link is neither a commit nor a catalogue feature.

  python tools/build_defects.py
Run by the git hooks and CI (tools/checks.py).
"""

import datetime
import re
import sys
import tomllib

from checks import ROOT, register_today, utf8_console

SOURCE = ROOT / "docs" / "defects.toml"
PAGE = ROOT / "docs" / "defects.md"
CATALOGUE = ROOT / "docs" / "features.md"
TYPES = ("code", "configuration", "content", "tool", "environment", "third party", "process")
SEVERITIES = ("blocking", "major", "minor")
STATUSES = {"fixed": "✓", "worked around": "↷", "open": "○"}  # the symbol goes with the label, never alone
TAGS = (
    "ci", "component", "dbt", "dependabot", "format", "git", "guards", "producer", "tests", "windows",
)  # fmt: skip
REQUIRED = ("id", "date", "titre", "type", "etiquettes", "gravite", "statut", "constat", "cause", "solution")
REQUIRED += ("resultat", "preuve")
OPTIONAL = ("lecon", "liens", "reconstitue")
STATED_PROOF = ("Manual:", "Rule:")  # a proof without a file: stated and explained, as in the catalogue
FEATURE_ID = re.compile(r"^[A-Z0-9]+-\d+$")
COMMIT = re.compile(r"^[0-9a-f]{7,40}$")


def check_values(defect: dict, number: int, previous_date: datetime.date | None) -> list[str]:
    """Identifier, date and values taken from the fixed lists."""
    problems = []
    if defect["id"] != f"DEF-{number:03d}":
        problems.append(f"identifier expected DEF-{number:03d} (entries follow each other, no gap)")
    if not isinstance(defect["date"], datetime.date) or defect["date"] > register_today():
        problems.append("date missing from the calendar or in the future")
    elif previous_date and defect["date"] < previous_date:
        problems.append("date before the previous entry's (entries are in order)")
    for key, allowed in (("type", TYPES), ("gravite", SEVERITIES), ("statut", STATUSES)):
        if defect[key] not in allowed:
            problems.append(f"{key} '{defect[key]}' outside the list: {', '.join(allowed)}")
    return problems + [f"tag '{tag}' outside the list (TAGS)" for tag in defect["etiquettes"] if tag not in TAGS]


def check_references(defect: dict, features: set[str]) -> list[str]:
    """Proofs (existing files naming the defect, or a stated proof) and links (commit or known feature)."""
    problems = []
    for proof in defect["preuve"]:
        if proof.startswith(STATED_PROOF):
            continue
        if not (ROOT / proof).is_file():
            problems.append(f"proof '{proof}': file not found")
        elif defect["id"] not in (ROOT / proof).read_text(encoding="utf-8"):
            problems.append(f"proof '{proof}' does not name {defect['id']}")
    if not defect["preuve"] and defect["statut"] != "open":
        problems.append("no proof: a settled defect has its test, its check or its rule")
    for link in defect.get("liens", []):
        if not COMMIT.match(link) and link not in features:
            problems.append(f"link '{link}': neither a commit nor a catalogue feature")
    return problems


def check(defect: dict, number: int, previous_date: datetime.date | None, features: set[str]) -> list[str]:
    """What is wrong with an entry (empty when it is complete and consistent)."""
    name = defect.get("id", f"entry #{number}")
    problems = [f"field '{key}' missing" for key in REQUIRED if key not in defect]
    problems += [f"field '{key}' unknown" for key in defect if key not in REQUIRED + OPTIONAL]
    if not problems:
        problems = check_values(defect, number, previous_date) + check_references(defect, features)
    return [f"{name}: {problem}" for problem in problems]


def status_label(defect: dict) -> str:
    return f"{STATUSES[defect['statut']]} {defect['statut']}"


def card(defect: dict) -> list[str]:
    """One defect's section, in Markdown."""
    meta = [f"`{defect['date']}`", defect["type"], defect["gravite"], status_label(defect)]
    meta.append("tags: " + ", ".join(f"`{tag}`" for tag in defect["etiquettes"]))
    meta += ["*reconstructed after the fact*"] if defect.get("reconstitue") else []
    proofs = ", ".join(p if p.startswith(STATED_PROOF) else f"`{p}`" for p in defect["preuve"]) or "to cover"
    links = ", ".join(f"`{link}`" if COMMIT.match(link) else link for link in defect.get("liens", []))
    fields = [("Finding", defect["constat"]), ("Cause", defect["cause"]), ("Solution", defect["solution"])]
    fields += [("Result", defect["resultat"]), ("Lesson", defect.get("lecon")), ("Proof", proofs), ("Links", links)]
    lines = [f'<a id="{defect["id"].lower()}"></a>', f"### {defect['id']} · {defect['titre']}", "", " · ".join(meta)]
    return lines + [""] + [f"- **{label}:** {text}" for label, text in fields if text] + [""]


def page(defects: list[dict]) -> str:
    """The whole page: introduction, index, then one section per defect."""
    totals = {status: sum(d["statut"] == status for d in defects) for status in STATUSES}
    counts = ", ".join(f"{n} {status}" for status, n in totals.items())
    lines = [
        "<!-- Generated by tools/build_defects.py from docs/defects.toml: never edit by hand. -->",
        "# Defects register",
        "",
        "[← Overview](../ARCHITECTURE.md) · Source: [defects.toml](defects.toml) · Catalogue:",
        "[features.md](features.md)",
        "",
        "What broke, why, how it was settled, and what keeps it from coming back. One entry per real defect",
        "detected (code, configuration, content, tool, environment, third party or the way we work), each",
        f"with its regression test, check or rule. **{len(defects)} defects**: {counts}.",
        "",
        f"Types: {', '.join(TYPES)}. Tags: {', '.join(TAGS)}.",
        "",
        "## Index",
        "",
        "| ID | Date | Defect | Type | Severity | Status |",
        "|---|---|---|---|---|---|",
    ]
    for d in defects:
        cells = (f"[{d['id']}](#{d['id'].lower()})", str(d["date"]), d["titre"], d["type"], d["gravite"])
        lines.append("| " + " | ".join((*cells, status_label(d))) + " |")
    lines += ["", "## Entries", ""]
    for defect in defects:
        lines += card(defect)
    return "\n".join(lines)


def main() -> int:
    defects = tomllib.loads(SOURCE.read_text(encoding="utf-8")).get("defaut", [])
    rows = CATALOGUE.read_text(encoding="utf-8").split("\n")
    features = {row.split("|")[1].strip() for row in rows if row.startswith("| ")}
    features = {name for name in features if FEATURE_ID.match(name)}
    problems, previous = [], None
    for number, defect in enumerate(defects, start=1):
        problems += check(defect, number, previous, features)
        previous = defect.get("date") if isinstance(defect.get("date"), datetime.date) else previous
    if not problems:
        expected = page(defects)
        if not PAGE.exists() or PAGE.read_text(encoding="utf-8") != expected:
            PAGE.write_text(expected, encoding="utf-8", newline="\n")
            problems.append("docs/defects.md was out of date: regenerated, `git add` it and retry")
    for problem in problems:
        print(f"✗ {problem}")
    if not problems:
        print(f"✓ {len(defects)} defects, register and page aligned")
    return 1 if problems else 0


if __name__ == "__main__":
    utf8_console()
    sys.exit(main())
