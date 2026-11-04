"""Refuses broken links in the documentation: a relative link whose file, or whose
`#anchor` heading, does not exist. Web links are not fetched.

  python tools/check_links.py
"""

import re
import subprocess
import sys
from pathlib import Path

from checks import ROOT, utf8_console

LINK = re.compile(r"\]\(([^)\s]+)\)")
HEADING = re.compile(r"^#{1,6}\s+(.*)$", re.MULTILINE)
HTML_ANCHOR = re.compile(r'<a id="([^"]+)"')  # explicit anchors, e.g. one per entry in docs/defects.md
EXCLUDED: tuple[str, ...] = ()


def slug(heading: str) -> str:
    """The anchor GitHub gives a heading: lowercase, punctuation dropped, spaces as hyphens."""
    text = re.sub(r"[`*_]", "", heading.strip().lower())
    return re.sub(r"[^\w\- ]", "", text).replace(" ", "-")


def anchors(path: Path) -> set[str]:
    """Every link target of a page: its headings' anchors and its explicit HTML anchors (docs/defects.md has one
    per entry)."""
    text = path.read_text(encoding="utf-8")
    return {slug(h) for h in HEADING.findall(text)} | set(HTML_ANCHOR.findall(text))


def broken_links(document: Path) -> list[str]:
    problems = []
    for target in LINK.findall(document.read_text(encoding="utf-8")):
        if re.match(r"^(https?:|mailto:)", target):
            continue
        file_part, _, anchor = target.partition("#")
        linked = (document.parent / file_part).resolve() if file_part else document
        where = document.relative_to(ROOT).as_posix()
        if not linked.exists():
            problems.append(f"{where}: link to missing {file_part}")
        elif anchor and linked.suffix == ".md" and anchor not in anchors(linked):
            problems.append(f"{where}: no heading #{anchor} in {file_part or 'this page'}")
    return problems


def main() -> int:
    out = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    documents = [ROOT / f for f in out.splitlines() if not f.startswith(EXCLUDED)]
    problems = [p for document in documents for p in broken_links(document)]
    for problem in problems:
        print(f"✗ {problem}")
    if not problems:
        print(f"✓ {len(documents)} documents, no broken link")
    return 1 if problems else 0


if __name__ == "__main__":
    utf8_console()
    sys.exit(main())
