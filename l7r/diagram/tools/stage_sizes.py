"""What a stage of the hamlet roll is handed, measured: the reference hamlet rolled up to the stage on the work budget's seeds and
sizes, and each part of the manifest and of the plan that holds points counted - records and points - with the canvas (feature 444
T27).

WHY. A stage's derivation states its bounds - the outline's points, the plots, the brook's stations - measured on the reference
rolls at 20, 40 and 80 households (`.specify/templates/derivation.md`), and the hamlet CLI refuses a roll past the hamlet band, so
until this tool each phase measured them with a probe of its own. Read-only: nothing is written but the report.

Research: plumbing - NONE: it measures, and decides nothing about the place
"""

from __future__ import annotations

import argparse
import io
import json
import statistics
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any

from l7r.diagram.tools.perf_snapshot import DEFAULT_SEEDS as SEEDS
from l7r.diagram.tools.work_budget import SIZES


def _points(v: Any) -> int | None:
    """The points a value holds: a ring or polyline of pairs, or a list of records each with a `poly`, `pts`, `outline` or `ring`;
    None for a value that holds none."""
    if not isinstance(v, (list, tuple)) or not v:
        return None
    if all(isinstance(q, (list, tuple)) and len(q) == 2 and all(isinstance(c, (int, float)) for c in q) for q in v):
        return len(v)
    n = 0
    for rec in v:
        ring = next((rec[k] for k in ("poly", "pts", "outline", "ring") if isinstance(rec, dict) and isinstance(rec.get(k), (list, tuple))), None)
        if ring is None and isinstance(rec, (list, tuple)):
            ring = rec
        got = _points(ring) if ring is not None else None
        if got is None:
            return None
        n += got
    return n


def sizes(seed: int, households: int, stage: str, calls: tuple[str, ...] = (), dump: str = "", spec: dict[str, Any] | None = None) -> dict[str, Any]:
    """The parts of the manifest and the plan that hold points, as `stage` is handed them on the reference roll at `households`:
    each as (records, points); `calls` names settlement methods taking no argument whose returned ring is counted too. A roll
    refused before `stage` reports where. `dump` names a file the stage's input is written to as JSON - the manifest, the plan's
    parts that serialize, and each call's ring - for a measurement this table does not make. `spec` overrides the reference's
    fields - a pool hamlet's own (its name, its declared fall) - the households still `households`."""
    from l7r.diagram.hamletgen import HamletSpec, plan_site
    from l7r.diagram.hamletgen.driver import STAGES, roll_scope, walks_after
    from l7r.diagram.hamletgen.plan import beyond_the_band
    from l7r.diagram.settlement import Settlement
    from l7r.diagram.tools.perf_snapshot import REFERENCE

    names = [st.__name__ for st in STAGES]
    if f"stage_{stage}" not in names:
        raise ValueError(f"no stage `{stage}` in STAGES")
    with beyond_the_band():
        plan = plan_site(HamletSpec(seed=seed, **{**REFERENCE, **(spec or {}), "households": households}))
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    with roll_scope(plan.spec):
        for st in STAGES[: names.index(f"stage_{stage}")]:
            try:
                with redirect_stdout(io.StringIO()):
                    st(s, plan)
                if walks_after(st):
                    s.standing.resync()
            except (ValueError, RuntimeError) as e:  # the generator's refusals
                return {"refused": f"{st.__name__}: {type(e).__name__}"}
        got: dict[str, Any] = {"canvas": [float(plan.W), float(plan.H)]}
        for k, v in s.M.items():
            if (n := _points(v)) is not None:
                got[f"M.{k}"] = [len(v), n]
        for k, v in vars(plan).items():
            if (n := _points(v)) is not None:
                got[f"plan.{k}"] = [len(v), n]
        rings: dict[str, Any] = {}
        for c in calls:
            ring = rings[c] = getattr(s, c)() or []
            got[f"s.{c}()"] = [1 if ring else 0, len(ring)]
    if dump:
        plain = {k: v for k, v in vars(plan).items() if _plain(v)}
        Path(dump).write_text(json.dumps({"M": s.M, "plan": plain, "calls": rings}, default=list))
    return got


def _plain(v: Any) -> bool:
    """Does `v` serialize as JSON as it stands - numbers, strings, and lists and dicts of them?"""
    try:
        json.dumps(v)
    except TypeError:
        return False
    return True


def table(rows: dict[int, list[dict[str, Any]]]) -> str:
    """Each part's mean records and points over the seeds at each size, the sizes as columns."""
    keys = sorted({k for runs in rows.values() for r in runs for k in r if k not in ("refused", "canvas", "seed")})
    out = ["| part | " + " | ".join(f"@{h} records / points" for h in rows) + " |", "|---|" + "---|" * len(rows)]
    for k in keys:
        cells = []
        for runs in rows.values():
            have = [r[k] for r in runs if k in r]
            cells.append(f"{statistics.mean(a for a, _b in have):.1f} / {statistics.mean(b for _a, b in have):.0f}" if have else "-")
        out.append(f"| {k} | " + " | ".join(cells) + " |")
    canv = [" x ".join(f"{c:.0f}" for c in runs[0]["canvas"]) if runs and "canvas" in runs[0] else "-" for runs in rows.values()]
    out.append("| canvas (first seed) | " + " | ".join(canv) + " |")
    refused = [f"seed {r['seed']} at {h}: {r['refused']}" for h, runs in rows.items() for r in runs if "refused" in r]
    return "\n".join(out + ([f"\nRefused before the stage: {'; '.join(refused)}"] if refused else []))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("stage", help="the stage whose input is measured, by its name in STAGES without `stage_`")
    ap.add_argument("--sizes", default=",".join(str(h) for h in SIZES if h >= 20))
    ap.add_argument("--calls", default="", help="settlement methods taking no argument whose ring is counted, comma-separated")
    ap.add_argument("--dump", default="", help="a directory each roll's input is written to, as <seed>-<households>.json")
    ap.add_argument("--spec", default="", help="a JSON object overriding the reference spec's fields (a pool hamlet's own)")
    ap.add_argument("--seeds", default="", help="the seeds, comma-separated (default: the reference seeds)")
    a = ap.parse_args(argv)
    calls = tuple(c for c in a.calls.split(",") if c)
    spec = json.loads(a.spec) if a.spec else None
    seeds = tuple(int(x) for x in a.seeds.split(",")) if a.seeds else SEEDS
    rows: dict[int, list[dict[str, Any]]] = {}
    for h in (int(x) for x in a.sizes.split(",")):
        rows[h] = []
        for seed in seeds:
            r = sizes(seed, h, a.stage, calls, str(Path(a.dump) / f"{seed}-{h}.json") if a.dump else "", spec)
            rows[h].append({"seed": seed, **r})
    print(f"stage-sizes: what `{a.stage}` is handed on the {'given spec' if spec else 'reference'} roll, seeds {', '.join(map(str, seeds))}, the mean over the seeds that reach it\n")
    print(table(rows))
    return 0


if __name__ == "__main__":  # pragma: no cover - `make stage-sizes` runs it
    raise SystemExit(main())
