"""The citation-rule inventory in `docs/research-doctrine.md` names tools that exist (feature 312, FR-005, SC-003).

The GM, 2026-10-02: *"we should definitely make sure that our citation rules are enforced by tooling and not just
remembering to do the correct thing."* The inventory lists every citation rule with the tool that holds it; a tool renamed
or deleted would leave a rule held by nothing while the table still claimed otherwise. So every file the table names - a
script, a hook, an agent contract, a test, an engine module - is checked to exist, and every row names one or says why
it is out of scope."""

from __future__ import annotations

import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[1]
# the scripts live by purpose since 2026-10-08 (scripts/CLAUDE.md), so every directory under scripts/ is a root a bare name may name
ROOTS = (REPO, REPO / "scripts", *sorted(p for p in (REPO / "scripts").rglob("*") if p.is_dir() and p.name != "__pycache__"),
         REPO / "l7r" / "diagram" / "interactive", REPO / "l7r" / "diagram" / "interactive" / "record", REPO / "research", REPO / "tests" / "interactive", REPO / "tests" / "hooks")
_PATH = re.compile(r"`([A-Za-z0-9_./-]+\.(?:py|sh|md|json|jsonl))(?:::[A-Za-z0-9_]+)?`")


def _section() -> str:
    text = (REPO / "docs" / "research-doctrine.md").read_text(encoding="utf-8")
    start = text.index("## What enforces each citation rule (feature 312, FR-005)")
    return text[start:]


def _rows() -> list[list[str]]:
    # a cell may hold an escaped pipe (`make canon TERMS="a\\|b"`), which is not a column break
    return [[c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))] for line in _section().splitlines() if re.match(r"^\| \d+ \|", line)]


def test_every_file_the_inventory_names_exists() -> None:
    missing = []
    for row in _rows():
        for path in _PATH.findall(row[3]):
            if not any((root / path).exists() for root in ROOTS):
                missing.append(f"rule {row[0]}: `{path}`")
    assert not missing, "the inventory names tools that do not exist:\n" + "\n".join(missing)


def test_every_rule_has_a_tool_or_says_why_not() -> None:
    rows = _rows()
    assert len(rows) >= 60
    bare = [r[0] for r in rows if not _PATH.search(r[3]) and "out of FR-005's scope" not in r[3] and "private" not in r[3]]
    assert not bare, f"rules naming no tool: {bare}"
