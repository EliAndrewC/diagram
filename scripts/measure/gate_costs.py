#!/usr/bin/env python3
"""gate_costs.py - what a gate run costs here, read from the run records (feature 415 T04, D7; FR-007).

    make gate-costs [SINCE=2026-10-24]     the table of runs, the fit, and the selection's growth

WHY (the GM, 2026-10-24: "First measure the fixed cost and the per-test cost on a few real landings, so the change rests on
numbers rather than a second guess"). The incremental planner's `FULL_FRACTION` (0.6) was "a knob with its reason; not a
measured optimum". Since T01 every `make done` record carries `phases` (seconds each), `plan_mode`, `plan_reason`,
`selected` and `collected`. This reads the green ones:

- THE TABLE: each run's mode, selected and collected counts, its test phase (`pytest`) and floors seconds, its total, and the
  host's load at its start.
- THE FIT: the test phase's seconds against the selected count, least squares - `fixed` (what a run of no tests costs:
  collection, the workers, the rolls a fixture always makes) and `per_test`. A full run's rows count too: they are the far end.
- THE GROWTH: for each incremental run, its selected count against the number of runs since the last full one - how the
  selection grows between full runs (the baseline is the last FULL run, never a merged one, `incremental.py`'s docstring).
"""

from __future__ import annotations

import glob
import json
import os
import sys
from pathlib import Path


def records(root: Path, since: str = "") -> list[dict]:
    """The `make done` run records with T01's fields, oldest first."""
    out = []
    for f in sorted(glob.glob(str(root / "dev" / "run-log" / "*" / "*.json"))):
        try:
            rec = json.loads(Path(f).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if rec.get("target") in ("done", "idle-done") and "phases" in rec and str(rec.get("utc", "")) >= since:
            out.append(rec)
    return sorted(out, key=lambda r: str(r.get("utc")))


def fit(points: list[tuple[float, float]]) -> tuple[float, float] | None:
    """(fixed, per_test) by least squares over (selected, seconds); None under two distinct x."""
    if len({x for x, _ in points}) < 2:
        return None
    n = len(points)
    mx = sum(x for x, _ in points) / n
    my = sum(y for _, y in points) / n
    slope = sum((x - mx) * (y - my) for x, y in points) / sum((x - mx) ** 2 for x, _ in points)
    return my - slope * mx, slope


def growth(recs: list[dict]) -> list[tuple[str, int, int]]:
    """(utc, runs since the last full, selected) for each green incremental run."""
    out, since_full = [], 0
    for r in recs:
        if r.get("plan_mode") == "full":
            since_full = 0
            continue
        if r.get("plan_mode") == "incremental":
            since_full += 1
            out.append((str(r.get("utc")), since_full, int(r.get("selected") or 0)))
    return out


def main(argv: list[str]) -> int:
    since = argv[argv.index("--since") + 1] if "--since" in argv else ""
    root = Path(os.environ.get("L7R_ROOT") or Path(__file__).resolve().parents[2])
    green = [r for r in records(root, since) if r.get("result") == "green" and r.get("plan_mode")]
    print(f"{'utc':20} {'mode':11} {'selected':>8} {'collected':>9} {'pytest_s':>8} {'floors_s':>8} {'total_s':>7} {'load':>5}")
    for r in green:
        ph = r.get("phases") or {}
        load = ((r.get("host") or {}).get("load") or [None])[0]
        print(f"{str(r.get('utc')):20} {str(r.get('plan_mode')):11} {r.get('selected', ''):>8} {r.get('collected', ''):>9} {ph.get('pytest', ''):>8} {ph.get('floors', ''):>8} {r.get('seconds', ''):>7} {load if load is not None else '':>5}")
    pts = [(float(r["selected"]), float(r["phases"]["pytest"])) for r in green if isinstance(r.get("selected"), int) and "pytest" in (r.get("phases") or {})]
    f = fit(pts)
    print(f"fit over {len(pts)} run(s): " + (f"test phase = {f[0]:.1f} s fixed + {f[1] * 1000:.2f} ms per selected test" if f else "too few distinct selections to fit"))
    for utc, n, sel in growth(green):
        print(f"growth: {utc} - incremental run {n} since the last full, {sel} test(s) selected")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks" / "lib"))
    sys.dont_write_bytecode = True  # a record leaves no __pycache__ in the worktree (feature 406)
    import usage_log  # noqa: E402 - feature 406: every tool records its run

    sys.exit(usage_log.exited("gate_costs", main(sys.argv[1:])))
