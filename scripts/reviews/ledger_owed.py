#!/usr/bin/env python3
"""Every pass of every check owes its row in the review ledger (feature 371).

WHY (the GM, 2026-10-10: *"a log of when our subagent checks find something that needs to be changed and when they don't, so
that we can see how often they are paying off"*). The log is `dev/review-ledger.md`'s measured table, and nothing made its rows
get written: feature 328 ran 26 glyph checks and wrote none of their rows, rebuilt by hand at a batch's close. So every check's
pass is logged when the agent returns (`hm_checks.py`, into `<git common dir>/check-passes.jsonl`, with its cost cells computed
as `make review-cost` computes them), and a pass is ANSWERED by a measured row carrying its check and those same cells - the
table copies its cost from `make review-cost`, never types it, so the cells identify the pass (two same-day rounds of one
check on one subject are two passes with two costs).

    ledger_owed.py [--log <jsonl>] [--ledger <md>]             list the unanswered passes, each with the row to add
    ledger_owed.py ... --refuse                                 exit 1 while any is unanswered (the push)

Escape at the push: LEDGER_ROWS_OK="<reason>" in sync-with-main's environment, recorded in the bypass log.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

sys.dont_write_bytecode = True  # the push runs this in the tree it is about to push
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ledger_lint  # noqa: E402

LOG = "check-passes.jsonl"
JUDGED = ("verdict", "finding", "class", "author missed?", "acted on")


def _norm(cell: str) -> str:
    return re.sub(r"\s+", " ", cell).strip()


def load_passes(path: Path) -> list[dict[str, str]]:
    """The logged passes, oldest first; a line that is not a pass is skipped."""
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(rec, dict) and rec.get("check") and rec.get("wall"):
            out.append({k: str(v) for k, v in rec.items()})
    return out


def unanswered(passes: Sequence[dict[str, str]], ledger_text: str) -> list[dict[str, str]]:
    """The passes no measured row answers - a row of the same check carrying the pass's wall and tokens cells."""
    keys = set()
    for _n, cells in ledger_lint.measured_rows(ledger_text):
        if len(cells) == len(ledger_lint.COLUMNS):
            row = dict(zip(ledger_lint.COLUMNS, cells, strict=True))
            keys.add((_norm(row["check"]), _norm(row["wall"]), _norm(row["tokens"])))
    return [p for p in passes if (_norm(p["check"]), _norm(p["wall"]), _norm(p["tokens"])) not in keys]


def row_for(p: dict[str, str]) -> str:
    """The row to add: what was measured filled in, the judgment cells left for the session (`?`)."""
    cells = [p.get("date", "?"), p["check"], p.get("subject") or "?", *("?" for _ in JUDGED), p["wall"], p["tokens"]]
    return "| " + " | ".join(_norm(c).replace("|", "/") for c in cells) + " |"


def default_log() -> Path:
    out = subprocess.run(["git", "rev-parse", "--git-common-dir"], capture_output=True, text=True, check=False).stdout.strip()
    return Path(out or ".git").resolve() / LOG


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--log", default="", help="the pass log (default: <git common dir>/check-passes.jsonl)")
    ap.add_argument("--ledger", default="dev/review-ledger.md")
    ap.add_argument("--refuse", action="store_true", help="exit 1 while a pass is unanswered")
    args = ap.parse_args(argv)
    ledger = Path(args.ledger)
    owed = unanswered(load_passes(Path(args.log) if args.log else default_log()), ledger.read_text(encoding="utf-8") if ledger.is_file() else "")
    if not owed:
        return 0
    stream = sys.stderr if args.refuse else sys.stdout
    print(f"ledger-owed: {len(owed)} check pass(es) have no row in dev/review-ledger.md's measured table - add each, filling the ?s:", file=stream)
    for p in owed:
        print("  " + row_for(p), file=stream)
    print(
        "  (a row answers a pass by its check and its cost cells, which are the pass's own `make review-cost` - feature 371; the push refuses until each has its row, or LEDGER_ROWS_OK=\"<reason>\")",
        file=stream,
    )
    return 1 if args.refuse else 0


if __name__ == "__main__":
    sys.exit(main())
