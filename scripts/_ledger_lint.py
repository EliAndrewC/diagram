#!/usr/bin/env python3
"""Does every review-ledger row of the measured table carry its check, its class and its cost? (feature 294, FR-010)

WHY (feature 294, spec US7: "a review row without cost, class or check is refused at commit"). The ledger answered "is the
review pulling its weight" by impression: 7 of 133 settlement-review rows recorded a wall time, none a token count, and the
"author had missed?" column went empty from 2026-09-27 (research R0). From feature 294 on a review pass is a row of the
MEASURED table (`MEASURED_HEADING`), whose cells a script can total (`make review-census`): the check that ran, the finding's
class, and the run's wall time and tokens copied from `make review-cost AGENT=<id>`.

Usage: _ledger_lint.py [LEDGER]   exit 1, naming each row, when one is short of a cell.
"""

from __future__ import annotations

import re
import sys
from collections.abc import Sequence
from pathlib import Path

MEASURED_HEADING = "## Review checks, measured (feature 294 on)"
#: the checks a row may name - the five map reviews (feature 294's occasions) and the record and plan checks the ledger also logs
CHECKS = frozenset(
    {
        "settlement-review", "glyph-check", "fix-check", "building-review", "size-audit",
        "spec-fidelity", "spec-fidelity-verify", "quote-check", "record-format", "record-style", "source-reader",
        "source-applicability", "entry-drift", "translation-check", "escalation-check", "perf-audit",
    }
)  # fmt: skip
CLASSES = frozenset({"geometric", "judgment", "paperwork", "nothing"})
MISSED = frozenset({"yes", "no", "-"})
_WALL = re.compile(r"^\d+ s$")
_TOKENS = re.compile(r"^\d+k in \(\d+k cached\) / [\d.]+k out$")
COLUMNS = ("date", "check", "subject", "verdict", "finding", "class", "author missed?", "acted on", "wall", "tokens")


def measured_rows(text: str) -> list[tuple[int, list[str]]]:
    """(line number, cells) of every data row under the measured table's heading."""
    lines = text.splitlines()
    try:
        start = next(i for i, ln in enumerate(lines) if ln.strip() == MEASURED_HEADING)
    except StopIteration:
        return []
    out = []
    for i in range(start + 1, len(lines)):
        ln = lines[i]
        if ln.startswith("## "):
            break
        if not ln.startswith("| ") or set(ln.replace("|", "").strip()) <= {"-", " "}:
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if cells[0] == "date":
            continue
        out.append((i + 1, cells))
    return out


def problems(text: str) -> list[str]:
    """Each measured row short of a cell, by line."""
    out = []
    for n, cells in measured_rows(text):
        if len(cells) != len(COLUMNS):
            out.append(f"line {n}: {len(cells)} cells, the table has {len(COLUMNS)} ({' | '.join(COLUMNS)})")
            continue
        row = dict(zip(COLUMNS, cells, strict=True))
        if row["check"] not in CHECKS:
            out.append(f"line {n}: check {row['check']!r} is none of the checks this ledger logs")
        if row["class"] not in CLASSES:
            out.append(f"line {n}: class {row['class']!r} - one of {', '.join(sorted(CLASSES))}")
        if row["author missed?"] not in MISSED:
            out.append(f"line {n}: author missed? {row['author missed?']!r} - yes, no or -")
        if not _WALL.match(row["wall"]) or not _TOKENS.match(row["tokens"]):
            out.append(f"line {n}: the cost cells are not `make review-cost AGENT=<id>`'s ({row['wall']!r} | {row['tokens']!r})")
    return out


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    ledger = Path(args[0]) if args else Path(__file__).resolve().parents[1] / "docs" / "review-ledger.md"
    found = problems(ledger.read_text(encoding="utf-8"))
    for p in found:
        print(p)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
