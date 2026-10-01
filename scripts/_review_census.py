#!/usr/bin/env python3
"""Is each review check pulling its weight? The ledger's totals, by a command (feature 294, FR-013 and US7).

WHY (feature 294, GM 2026-10-01: *"I want to take a hard look at what it is doing, what it is buying us"*). The spec's R0 census
was a hand count of the ledger by an agent; this is the same count by a script, so the answer is re-taken on demand and every
new check (the glyph check, the fix check) shows up from its first run - including a check that never finds anything. The rows
before feature 294 carry no class, so they are classified once, as data (`docs/review-ledger-r0.json`); the measured table's
rows carry their class and cost in the row (`scripts/_ledger_lint.py` holds them to it).

Usage: _review_census.py [--root CLONE]   prints one line per check: runs, NOT-REVIEWABLE runs, findings by class, author-missed,
and - for the measured rows - wall time and tokens.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path
from typing import Any

CLASSES = ("geometric", "judgment", "paperwork", "nothing")
_TOK = re.compile(r"^(\d+)k in")


def _lint() -> Any:
    spec = importlib.util.spec_from_file_location("ledger_lint_for_census", Path(__file__).resolve().parent / "_ledger_lint.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def tally(r0: Sequence[dict[str, Any]], ledger_text: str) -> dict[str, dict[str, float]]:
    """{check: {"runs", "not_reviewable", <class>..., "author_missed", "wall_s", "tokens_k"}} over the old rows' data and the
    measured table's rows. A measured row is one finding; its run is counted once per (date, check, subject, wall)."""
    out: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for row in r0:
        t = out[str(row.get("agent"))]
        t["runs"] += float(row.get("runs") or 0)
        t["not_reviewable"] += float(row.get("not_reviewable_runs") or 0)
        for c in CLASSES:
            t[c] += float((row.get("findings") or {}).get(c) or 0)
        t["author_missed"] += float(row.get("author_missed_fixed") or 0)
        t["wall_s"] += 60.0 * float(row.get("wall_min") or 0)
    seen: set[tuple[str, ...]] = set()
    lint = _lint()
    for _n, cells in lint.measured_rows(ledger_text):
        if len(cells) != len(lint.COLUMNS):
            continue
        row = dict(zip(lint.COLUMNS, cells, strict=True))
        t = out[row["check"]]
        if row["class"] in CLASSES:
            t[row["class"]] += 1
        t["author_missed"] += row["author missed?"] == "yes"
        run = (row["date"], row["check"], row["subject"], row["wall"])
        if run not in seen:
            seen.add(run)
            t["runs"] += 1
            t["not_reviewable"] += row["verdict"].upper() == "NOT-REVIEWABLE"
            wall = row["wall"].split()[0]
            t["wall_s"] += float(wall) if wall.isdigit() else 0.0
            tok = _TOK.match(row["tokens"])
            t["tokens_k"] += float(tok.group(1)) if tok else 0.0
    return {k: dict(v) for k, v in out.items()}


def report(totals: dict[str, dict[str, float]]) -> str:
    lines = ["check | runs | not-reviewable | geometric | judgment | paperwork | nothing | author missed | wall (min) | tokens (M)"]
    for check, t in sorted(totals.items(), key=lambda kv: -kv[1].get("runs", 0)):
        lines.append(
            f"{check} | {t.get('runs', 0):.0f} | {t.get('not_reviewable', 0):.0f} | "
            + " | ".join(f"{t.get(c, 0):.0f}" for c in CLASSES)
            + f" | {t.get('author_missed', 0):.0f} | {t.get('wall_s', 0) / 60:.0f} | {t.get('tokens_k', 0) / 1000:.1f}"
        )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[1]), help="the clone")
    args = ap.parse_args(argv)
    root = Path(args.root)
    r0_path = root / "docs" / "review-ledger-r0.json"
    r0 = json.loads(r0_path.read_text(encoding="utf-8")) if r0_path.is_file() else []
    print(report(tally(r0, (root / "docs" / "review-ledger.md").read_text(encoding="utf-8"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
