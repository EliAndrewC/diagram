"""THE ROLL AUDIT (feature 216, GM 2026-09-08): for every rolling coverage context of the gate's baseline, the engine
lines NO other context of the suite reaches.

The question it answers is the GM's, asked three times in two days: *"is it ACTUALLY the case that the test's behavior
needs a roll of its own?"*, *"are you really, truly not able to combine?"* - and the answer that settled each was this
measurement (feature 215's `census/unique_lines.py`, which this is): if a roll went, which lines would lose ALL
coverage. Zero means the roll exists for a behavior, not for the floor, and the doctrine (constitution VI) says such
a test belongs in the tier above the gate. *"I imagine that we will do this again. If not for hamlets, then for
villages or towns. or provincial cities or capital cities"* - so it is a command, `make roll-audit`, and the one knob is
`--min-lines`: a context is a ROLL when it executed at least that many engine lines (a hamlet roll is ~7,000; a unit
test a few hundred), and a larger tier sets it higher.

It reads the baseline `make done` saves after a green full run (`ci/incremental.baseline_dir`), where feature 207 keeps
one context per test phase and per fixture and feature 213 labels a roll child's lines with its requester's context.
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

DEFAULT_MIN_LINES = 2000


def read_contexts(db: Path, engine_marker: str = "/l7r/diagram/", skip_marker: str = "/tests/") -> dict[str, set[tuple[str, int]]]:
    """context name -> the (file, line) pairs it executed, engine files only (tests excluded)."""
    from coverage.numbits import numbits_to_nums

    by_ctx: dict[str, set[tuple[str, int]]] = defaultdict(set)
    con = sqlite3.connect(str(db))
    try:
        rows = con.execute("select c.context, f.path, l.numbits from line_bits l join file f on f.id = l.file_id join context c on c.id = l.context_id").fetchall()
    finally:
        con.close()
    for ctx, path, nb in rows:
        if engine_marker not in path or skip_marker in path:
            continue
        short = path.split(engine_marker, 1)[-1]
        for ln in numbits_to_nums(nb):
            by_ctx[ctx].add((short, int(ln)))
    return dict(by_ctx)


def unique_lines(by_ctx: dict[str, set[tuple[str, int]]], min_lines: int) -> list[tuple[str, int, list[tuple[str, int]]]]:
    """Per rolling context (at least `min_lines` engine lines), sorted by unique count: (context, executed, the lines only it reaches)."""
    count: Counter[tuple[str, int]] = Counter()
    for lines in by_ctx.values():
        count.update(lines)
    out = []
    for ctx, lines in by_ctx.items():
        if len(lines) < min_lines:
            continue
        uniq = sorted(x for x in lines if count[x] == 1)
        out.append((ctx, len(lines), uniq))
    return sorted(out, key=lambda t: (-len(t[2]), t[0]))


def report(rows: list[tuple[str, int, list[tuple[str, int]]]], min_lines: int) -> str:
    lines = [f"roll audit: {len(rows)} rolling context(s) (>= {min_lines} engine lines each); per context, the engine lines NO other context reaches"]
    for ctx, total, uniq in rows:
        files = Counter(f for f, _ in uniq)
        where = ", ".join(f"{f}:{n}" for f, n in files.most_common(6))
        lines.append(f"  {len(uniq):5d} unique of {total:6d}  {ctx[:100]}" + (f"\n        {where}" if uniq else ""))
    if rows and not any(u for _c, _t, u in rows):
        lines.append("  every rolling context is covered by others: nothing here is strictly necessary for the floor")
    return "\n".join(lines)


def baseline_db(root: Path) -> Path:
    from l7r.diagram.ci import incremental

    return incremental.baseline_dir(root) / incremental.COVERAGE_DB


def main(argv: list[str] | None = None, root: Path | None = None, out: Any = None) -> int:
    ap = argparse.ArgumentParser(description="the engine lines each roll alone reaches, off the gate's coverage baseline")
    ap.add_argument("--min-lines", type=int, default=DEFAULT_MIN_LINES, help="a context is a roll when it executed at least this many engine lines")
    ap.add_argument("--db", default=None, help="a coverage data file to audit instead of the gate baseline's")
    a = ap.parse_args(argv)
    out = out or sys.stdout
    if a.db:
        db = Path(a.db)
    else:
        if root is None:
            # tools/ diagram/ l7r/ diagram/ skills/ .claude/ -> the repository root is SIX levels up; the
            # first draft said five and landed on `.claude/`, which is what the unit test proves against.
            root = Path(__file__).resolve().parents[6]
        db = baseline_db(root)
    if not db.is_file():
        print(f"roll audit: no baseline at {db} - a green full `make done` (INCREMENTAL=0) records one", file=out)
        return 2
    print(report(unique_lines(read_contexts(db), a.min_lines), a.min_lines), file=out)
    return 0


if __name__ == "__main__":  # pragma: no cover - the make target's entry; `main` is the tested body
    raise SystemExit(main())
