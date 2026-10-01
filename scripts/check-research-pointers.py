#!/usr/bin/env python3
"""Every pointer to the research names a fragment that exists, and none names a built page (feature 301, FR-014).

The GM, 2026-10-01: keep the requirement that a rendering decision points at its research, but *"not link to the
generated HTML page, but to link to the source which is fed into and used to generate that HTML page, because that is
the canonical location of the research"*. The pages are built and no longer committed, so a pointer of the old form -
`research/water.html "Reservoir ponds (tameike)"` - points at nothing in the repository. This holds the new form:

  - a pointer to a question, `research/<page dir>/<prefix>-<heading id>.html`, names a file that exists;
  - a pointer to a page, `research/<page dir>/`, names a fragment directory that exists;
  - no pointer names a built page - `research/<page>.html`, `research/citations/<page>.html` - outside the files that
    name those paths as what they ARE (the build's code and tests, and the records of what happened).

A fragment renamed or moved by hand breaks its pointers, and this says which; `make fragment-move` moves a fragment and
rewrites them in the same change (FR-015). Run at the gate (`tests/tooling/test_research_pointers.py`) and at the push
(`sync-with-main.sh`, because a docs-only or spec-only delta takes the DIRECT route and runs no gate).

Usage: check-research-pointers.py [ROOT] | --selftest
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

SKILL = ".claude/skills/diagram"
RECORD = f"{SKILL}/research"
#: A question's fragment, named from anywhere (`research/...`, `../research/...`, `.claude/skills/diagram/research/...`).
FRAGMENT = re.compile(r"(?<![\w.-])research/((?:[a-z][a-z-]*/)+)(\d{3,5}-[^\s\"'`)\]<>,;|#*]+?\.html)(?![\w.-])")
#: A page's fragment directory.
DIRECTORY = re.compile(r"(?<![\w.-])research/((?:[a-z][a-z-]*/)+)(?![\w.-])")
#: The built pages, before 301 committed: a page, a collection's page, the registry, a citations page.
OLD_PAGE = re.compile(r"(?<![\w.-])research/(citations/)?((?:cities/|rendering/cities/|rendering/)?[A-Za-z][A-Za-z-]*\.html)(?![\w/-])")
#: Directories under research/ that are not fragment directories but are real: the built site (absent until built),
#: the assets, the citations directory of old (named only by the files below).
NOT_PAGES = ("site/", "assets/", "citations/")

#: Files that name the built pages as PATHS - what the build reads or writes, or a record of what happened - and so may
#: carry the old form. Every other tracked file is held to the rule.
EXEMPT_PREFIXES = (
    f"{RECORD}/",                                  # the record itself: its links are page-relative and resolved at build
    f"{SKILL}/l7r/diagram/interactive/sources.py",  # the build's code, naming the paths it reads and writes
    f"{SKILL}/l7r/diagram/interactive/citations.py",
    f"{SKILL}/l7r/diagram/interactive/record/",
    f"{SKILL}/l7r/diagram/tools/record_asset.py",
    f"{SKILL}/tests/",                              # the build's tests and their fixtures
    f"{SKILL}/dev/bypass-log/",                     # records of what happened
    f"{SKILL}/dev/run-log/",
    f"{SKILL}/dev/perf-log/",
    f"{SKILL}/legacy-hand-authored-pool/",          # frozen exhibits
    "scripts/",                                     # the tooling over the record names its paths
    "specs/301-record-site/",                       # this feature's own spec: the old forms are its subject
    ".gitignore",
)
#: Inside the record, these are documents a reader follows a pointer FROM, so they are held to the rule too.
RECORD_DOCS = (f"{RECORD}/CLAUDE.md", f"{RECORD}/STYLE.md")


def exempt(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    if path in RECORD_DOCS:
        return False
    if name in ("request.md", "gm-request.md", "README.md"):
        return True  # the GM's own words
    return path.startswith(EXEMPT_PREFIXES) or path.endswith((".png", ".webp", ".svg", ".jpg", ".pdf", ".gz"))


def problems(text: str, record: Path, *, old_form_banned: bool) -> list[str]:
    """What is wrong with the pointers in one file's text."""
    out: list[str] = []
    for m in FRAGMENT.finditer(text):
        if m.group(1).startswith(NOT_PAGES):
            continue
        if not (record / m.group(1) / m.group(2)).is_file():
            out.append(f"`research/{m.group(1)}{m.group(2)}` - no such fragment")
    for m in DIRECTORY.finditer(text):
        if m.group(1).startswith(NOT_PAGES) or (record / m.group(1)).is_dir():
            continue
        out.append(f"`research/{m.group(1)}` - no such page directory")
    if old_form_banned:
        out += [f"`{m.group(0)}` - a built page; name the fragment (`research/<page>/<prefix>-<heading id>.html`) or the page's directory" for m in OLD_PAGE.finditer(text)]
    return out


def tracked(root: Path) -> list[str]:
    out = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True, check=True).stdout
    return out.splitlines()


def check(root: Path) -> list[str]:
    record = root / RECORD
    if not record.is_dir():
        return []  # a repository with no record has no pointers to be right or wrong about
    bad: list[str] = []
    for path in tracked(root):
        if path.startswith(f"{RECORD}/") and path not in RECORD_DOCS:
            continue
        try:
            text = (root / path).read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            continue
        if "research/" not in text:
            continue
        if exempt(path):
            continue  # its paths are what the build reads or writes, a test's fixture, or a record of what happened
        for line_no, line in enumerate(text.splitlines(), 1):
            if "research/" in line:
                bad += [f"{path}:{line_no}: {p}" for p in problems(line, record, old_form_banned=True)]
    return bad


def selftest() -> int:
    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as td:
        record = Path(td)
        (record / "water").mkdir()
        (record / "water" / "120-reservoir-ponds-tameike.html").write_text("x", encoding="utf-8")
        (record / "cities" / "fabric").mkdir(parents=True)
        assert problems("see research/water/120-reservoir-ponds-tameike.html.", record, old_form_banned=True) == []
        assert problems("the page, research/water/ and research/cities/fabric/", record, old_form_banned=True) == []
        assert problems("research/water/130-gone.html", record, old_form_banned=True), "a missing fragment is named"
        assert problems("research/nowhere/", record, old_form_banned=True), "a missing directory is named"
        assert problems("research/water.html#x", record, old_form_banned=True), "a built page is refused"
        assert problems("research/citations/water.html", record, old_form_banned=True)
        assert problems("research/cities/fabric.html 'H'", record, old_form_banned=True)
        assert problems("research/water.html#x", record, old_form_banned=False) == [], "an exempt file may name it"
        assert problems("research/site/water/x.html and research/assets/record.css", record, old_form_banned=True) == [], "the built site and the assets are not pointers"
        assert problems("research/<page>/NNN-<heading id>.html", record, old_form_banned=True) == [], "a placeholder is not a pointer"
        assert problems("specs/229-rule-files-into-research/audit/x.md", record, old_form_banned=True) == [], "a word ending in -research is not the record"
    assert exempt("specs/180-x/request.md") and exempt(f"{SKILL}/tests/x.py") and not exempt("CLAUDE.md") and not exempt(f"{RECORD}/CLAUDE.md")
    print("check-research-pointers selftest ok")
    return 0


def main(argv: list[str]) -> int:
    if argv and argv[0] == "--selftest":
        return selftest()
    root = Path(argv[0] if argv else ".").resolve()
    bad = check(root)
    if bad:
        print("pointers to the research that do not resolve, or name a built page (feature 301):", file=sys.stderr)
        for line in bad[:60]:
            print(f"  {line}", file=sys.stderr)
        if len(bad) > 60:
            print(f"  ... and {len(bad) - 60} more", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
