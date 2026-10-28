"""The counted work of the reference hamlet, stage by stage, against each stage's budget (feature 443 T02, D4).

    make work-budget [SEED=<n>] [SIZES=10,20,40,80]

WHY (the GM, 2026-10-27, `specs/443-work-budget-tooling/request.md`): the speed work of eleven features asked whether a slice saved
time; none said what the whole roll should cost. This rolls the reference hamlet (`perf_snapshot.REFERENCE`) on its seeds
(`perf_snapshot.DEFAULT_SEEDS` - seed 25 and the snapshot's other reference seeds; `SEED=` one seed) at each size, and records per
stage the basic operations the counters of `l7r/diagram/work_counts.py` took (by kind and by function), the things the stage
placed, its Python calls and its seconds. It prints, per stage, the operations in total and per thing placed, their growth exponent
from 20 to 80 households, the stage's budget (`dev/work-budget.json`, unbudgeted until feature 444 sets one) and the ratio, then
the whole roll. The run goes to `dev/work-budget/<stamp>-<code id>.json` and regenerates the standing record, `dev/work-budget.md`.

Python calls and seconds are recorded beside the counts; neither is the budget. Calls are counted in a second roll of each seed
(`perf_snapshot.count_calls`), as the snapshot counts them, so the timed roll is not slowed by the counting callback. A stage's
count is a LOWER BOUND until its rebuild: inline arithmetic outside the counted sites is not counted (D2), so its Python calls are
printed beside it - a stage whose calls are large against its counts shows it.

Research: plumbing - NONE: it counts and reports, and decides nothing about the place
"""

from __future__ import annotations

import argparse
import io
import json
import math
import os
import subprocess
import time
from contextlib import redirect_stdout
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
RUN_DIR = os.path.join(SKILL, "dev", "work-budget")
RECORD = os.path.join(SKILL, "dev", "work-budget.md")
BUDGETS = os.path.join(SKILL, "dev", "work-budget.json")
SIZES = (10, 20, 40, 80)
"""Research: plumbing - NONE: the sizes the design names (10, 20, 40 and 80 households; 80 past the band, as the scaling legs roll it)"""
FIT = (20, 80)
"""Research: plumbing - NONE: the exponent is fitted from 20 to 80 households (rubric S6)"""


def roll(seed: int, households: int) -> dict[str, Any]:
    """One roll of the reference at `households`: per stage its counts (`work_counts.BY_STAGE`'s difference across it), the
    things it placed (`perf_profile.placed_counts`) and its seconds; a roll the generator refuses keeps the stages it ran."""
    from l7r.diagram import work_counts
    from l7r.diagram.hamletgen import HamletSpec, plan_site
    from l7r.diagram.hamletgen.driver import STAGES, roll_scope
    from l7r.diagram.hamletgen.plan import beyond_the_band
    from l7r.diagram.settlement import Settlement
    from l7r.diagram.tools.perf_profile import placed_counts
    from l7r.diagram.tools.perf_snapshot import REFERENCE

    with beyond_the_band():
        plan = plan_site(HamletSpec(seed=seed, **{**REFERENCE, "households": households}))
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    stages: dict[str, dict[str, Any]] = {}
    refused: str | None = None
    work_counts.reset()
    with roll_scope(plan.spec):
        for st in STAGES:
            name = st.__name__.replace("stage_", "")
            before, had, t0 = dict(work_counts.OPS), placed_counts(s.M), time.time()
            try:
                with redirect_stdout(io.StringIO()):
                    st(s, plan)
                s.standing.resync()
            except (ValueError, RuntimeError) as e:  # the generator's refusals, as the snapshot reads them
                refused = f"{type(e).__name__}: {str(e)[:120]}"
            ops = {k: n - before.get(k, 0) for k, n in work_counts.OPS.items() if n != before.get(k, 0)}
            placed = sum(max(0, n - had.get(k, 0)) for k, n in placed_counts(s.M).items())
            stages[name] = {"ops": ops, "placed": placed, "seconds": round(time.time() - t0, 3)}
            if refused:
                break
    return {"seed": seed, "households": households, "stages": stages, "refused": refused}


def total(ops: dict[str, int]) -> int:
    """A stage's basic operations: every counted kind but `placed`, `dropped` and `moved`, which count outcomes, not work."""
    return sum(n for k, n in ops.items() if k.split("@", 1)[0] not in ("placed", "dropped", "moved"))


def exponent(points: list[tuple[int, float]]) -> float | None:
    """The least-squares slope of log(work) on log(households) over `points` (sizes with work above zero); None under two."""
    pts = [(math.log(h), math.log(w)) for h, w in points if h > 0 and w > 0]
    if len(pts) < 2:
        return None
    mx, my = sum(x for x, _ in pts) / len(pts), sum(y for _, y in pts) / len(pts)
    den = sum((x - mx) ** 2 for x, _ in pts)
    return None if den == 0 else sum((x - mx) * (y - my) for x, y in pts) / den


def budgets(path: str = BUDGETS) -> dict[str, Any]:
    """The budget table (T03 writes it); absent, every stage unbudgeted."""
    try:
        with open(path, encoding="utf-8") as fh:
            return dict(json.load(fh))
    except FileNotFoundError:
        return {"program": {}, "stages": {}}


def _figure(r: dict[str, Any], name: str, key: str) -> float:
    """One roll's `key` (`ops` counted by `total`, or a stage's own field) for stage `name`, or summed over its stages for `roll`."""
    st = r["stages"].values() if name == "roll" else [r["stages"][name]]
    return float(sum(total(x["ops"]) if key == "ops" else x.get(key) or 0 for x in st))


def summarize(rows: list[dict[str, Any]], table: dict[str, Any]) -> dict[str, Any]:
    """Per stage and for the roll: at each size the mean over the seeds that reached it of the operations, things placed, calls and
    seconds, the operations per thing placed, the exponent over `FIT`, and the budget and its ratio where one is set."""
    order: list[str] = []
    for r in rows:
        order += [k for k in r["stages"] if k not in order]
    sizes = sorted({r["households"] for r in rows})
    out: dict[str, Any] = {"stages": {}, "sizes": sizes}
    for name in [*order, "roll"]:
        per: dict[int, dict[str, float]] = {}
        for h in sizes:
            got = [r for r in rows if r["households"] == h and (name == "roll" or name in r["stages"])]
            if not got:
                continue
            per[h] = {k: sum(_figure(r, name, k) for r in got) / len(got) for k in ("ops", "placed", "calls", "seconds")}
        fit = [(h, v["ops"]) for h, v in per.items() if FIT[0] <= h <= FIT[1]]
        b = (table.get("stages") or {}).get(name, {}) if name != "roll" else table.get("program") or {}
        at40 = per.get(40, {})
        budget = b.get("ops_at_40") if name == "roll" else (b.get("per_thing") and at40.get("placed") and b["per_thing"] * at40["placed"])
        out["stages"][name] = {
            "per": per,
            "exponent": exponent(fit),
            "status": b.get("status", "unbudgeted") if name != "roll" else ("budgeted" if b.get("ops_at_40") else "unbudgeted"),
            "budget_at_40": budget or None,
            "ratio": (at40.get("ops", 0) / budget) if budget else None,
        }
    return out


def table_md(summary: dict[str, Any], meta: dict[str, Any]) -> str:
    """The standing record, `dev/work-budget.md`."""
    sizes = summary["sizes"]
    head = "| stage | " + " | ".join(f"ops @{h}" for h in sizes) + " | per thing @40 | exponent | calls @40 | budget @40 | ratio | status |"
    lines = [
        "# The work budget - the standing record (feature 443)",
        "",
        "Load this file when: you need what each stage of the hamlet roll costs in counted operations, against its budget.",
        "",
        f"Generated by `make work-budget` at {meta['utc']} on engine {meta['commit']} (code id {meta['code_id']}), seeds"
        f" {', '.join(str(x) for x in meta['seeds'])}, the reference spec; each figure the mean over the seeds that rolled that size."
        " Counts are a lower bound until a stage's rebuild (feature 444): inline arithmetic outside the counted sites is not counted,"
        " so each stage's Python calls are beside its counts. Budgets come from `dev/work-budget.json` (`make budget-set`).",
        "",
        head,
        "|" + "---|" * (len(sizes) + 7),
    ]
    for name, st in summary["stages"].items():
        per, at40 = st["per"], st["per"].get(40, {})
        pt = f"{at40['ops'] / at40['placed']:,.0f}" if at40.get("placed") else "-"
        ex = f"{st['exponent']:.2f}" if st["exponent"] is not None else "-"
        bud = f"{st['budget_at_40']:,.0f}" if st["budget_at_40"] else "-"
        ratio = f"{st['ratio']:.1f}x" if st["ratio"] else "-"
        cells = " | ".join(f"{per[h]['ops']:,.0f}" if h in per else "-" for h in sizes)
        label = "**the whole roll**" if name == "roll" else name
        lines.append(f"| {label} | {cells} | {pt} | {ex} | {at40.get('calls', 0):,.0f} | {bud} | {ratio} | {st['status']} |")
    if meta.get("refused"):
        lines += ["", "Refused rolls (left out of their size's means): " + "; ".join(meta["refused"])]
    return "\n".join(lines) + "\n"


def _code_id() -> str:
    """The engine key of the working tree (`ci/delta.engine_key_worktree`: each engine `.py` by its docstring-blind id), so a run
    is keyed to the engine it measured - what the push's ratchet (T04) reads it by."""
    from pathlib import Path

    from l7r.diagram.ci.delta import engine_key_worktree

    return engine_key_worktree(Path(SKILL))[:12]


def _commit() -> str:
    return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=SKILL, capture_output=True, text=True).stdout.strip() or "unknown"


def run(seeds: tuple[int, ...], sizes: tuple[int, ...], calls: Any = None) -> tuple[dict[str, Any], str, str]:
    """Roll, count, summarize; write the run and the standing record. `calls` is `perf_snapshot.count_calls` (a seam for tests)."""
    from l7r.diagram.tools import perf_snapshot

    count = calls or perf_snapshot.count_calls
    rows: list[dict[str, Any]] = []
    for h in sizes:
        by_seed = count(seeds, h)
        for seed in seeds:
            r = roll(seed, h)
            for name, n in (by_seed.get(seed) or {}).items():
                if name in r["stages"]:
                    r["stages"][name]["calls"] = n
            rows.append(r)
    ok = [r for r in rows if not r["refused"]]
    summary = summarize(ok, budgets())
    meta = {
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "commit": _commit(),
        "code_id": _code_id(),
        "seeds": list(seeds),
        "sizes": list(sizes),
        "refused": [f"seed {r['seed']} at {r['households']}: {r['refused']}" for r in rows if r["refused"]],
    }
    os.makedirs(RUN_DIR, exist_ok=True)
    path = os.path.join(RUN_DIR, f"{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{meta['code_id']}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"meta": meta, "rows": rows, "summary": summary}, fh, indent=1, sort_keys=True)
    with open(RECORD, "w", encoding="utf-8") as fh:
        fh.write(table_md(summary, meta))
    return summary, path, RECORD


HELD = (40, 80)
"""Research: plumbing - NONE: the sizes an accepted stage is held at (443 FR-006)"""


def newest_run(code_id: str, run_dir: str = RUN_DIR) -> dict[str, Any] | None:
    """The newest run recorded at `code_id` (its file `<stamp>-<code id>.json`), or None."""
    try:
        names = sorted(n for n in os.listdir(run_dir) if n.endswith(f"-{code_id}.json"))
    except FileNotFoundError:
        return None
    if not names:
        return None
    with open(os.path.join(run_dir, names[-1]), encoding="utf-8") as fh:
        return dict(json.load(fh))


def held(table: dict[str, Any], summary: dict[str, Any]) -> list[str]:
    """Each refusal of an ACCEPTED stage whose counted operations at 40 or 80 households exceed its accepted figure or its budget
    (`per_thing` times the things it placed at that size), naming the figures and the two commands."""
    out: list[str] = []
    for name, b in (table.get("stages") or {}).items():
        if b.get("status") != "accepted":
            continue
        per = ((summary.get("stages") or {}).get(name) or {}).get("per") or {}
        for h in HELD:
            got = per.get(str(h)) or per.get(h)  # a run read back from JSON keys its sizes by string
            if not got:
                out.append(f"{name}: the run has no roll at {h} households to hold it to")
                continue
            ops, accepted, budget = got["ops"], (b.get("accepted") or {}).get(str(h)), b["per_thing"] * got["placed"]
            if accepted is not None and ops > accepted:
                out.append(f"{name}: {ops:,.0f} counted operations at {h} households, over its accepted {accepted:,.0f}")
            if ops > budget:
                out.append(f"{name}: {ops:,.0f} counted operations at {h} households, over its budget {budget:,.0f} ({b['per_thing']:g} per thing x {got['placed']:,.0f})")
    return out


def review(route: str, table: dict[str, Any] | None = None, code_id: str | None = None, run_dir: str = RUN_DIR) -> tuple[int, str]:
    """`make work-budget-review` at the push (443 FR-006, plan D7): (exit, message). Nothing to hold while no stage is accepted, or
    on a push that carries no engine code (a DIRECT route); else a run at the pushed engine's code id is required and every
    accepted stage held to it. No round-arbiter accept clears a refusal: the GM's words through `make budget-change` do."""
    table = budgets() if table is None else table
    if not any(b.get("status") == "accepted" for b in (table.get("stages") or {}).values()):
        return 0, "work-budget-review: no stage is accepted - nothing to hold"
    if route not in ("GATED", "GATED-LOCAL"):
        return 0, "work-budget-review: the push carries no engine code - nothing to hold"
    code_id = code_id or _code_id()
    run = newest_run(code_id, run_dir)
    if run is None:
        return 1, f"work-budget-review: REFUSED - no work-budget run at the pushed engine (code id {code_id}): run `make work-budget`, commit dev/work-budget/, push again"
    bad = held(table, run["summary"])
    if bad:
        fix = "make the stage do less work, or raise its figure with the GM's words: make budget-change PHASE=<stage> TO=<per thing> WORDS=\"<the GM's words>\""
        return 1, "work-budget-review: REFUSED - an accepted stage grew past its figure:\n" + "\n".join(f"  {x}" for x in bad) + f"\n  {fix}"
    return 0, f"work-budget-review: every accepted stage within its figures at {' and '.join(str(h) for h in HELD)} households"


def main(argv: list[str] | None = None) -> int:
    from l7r.diagram.tools.perf_snapshot import DEFAULT_SEEDS

    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--seed", type=int, default=None, help="one seed (default: the reference seeds)")
    ap.add_argument("--sizes", default=",".join(str(h) for h in SIZES))
    ap.add_argument("--review", metavar="ROUTE", help="the push's ratchet on the route sync-with-main.sh chose (`make work-budget-review`)")
    a = ap.parse_args(argv)
    if a.review is not None:
        rc, msg = review(a.review)
        print(msg)
        return rc
    seeds = (a.seed,) if a.seed is not None else DEFAULT_SEEDS
    _summary, path, record = run(seeds, tuple(int(x) for x in a.sizes.split(",") if x.strip()))
    with open(record, encoding="utf-8") as fh:
        print(fh.read())
    print(f"wrote {os.path.relpath(path, SKILL)} and {os.path.relpath(record, SKILL)}")
    return 0


if __name__ == "__main__":
    from l7r.diagram._invocation import guard

    guard("l7r.diagram.tools.work_budget")
    raise SystemExit(main())
