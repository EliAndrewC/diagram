"""Feature 306, Phase 0 round 1: a margin's capacity predicted by packing, measured against the engine's own seating.

    python3 specs/306-seat-by-packing/prototype.py observe 40 4,25,39,47    # prediction beside the engine's outcome, per margin
    python3 specs/306-seat-by-packing/prototype.py prune 40 4,25,39,47      # a margin predicted short fails at once
    python3 specs/306-seat-by-packing/prototype.py base 40 4,25,39,47       # the engine as it is, timed the same way

Monkeypatches only; edits nothing in the engine. The prediction runs where the exhaustive pass (`capacity.seat_the_rest`) would
start - the front row and the lattice rounds have seated what they seat - and is: the households standing, plus a greedy pack
of the SMALLEST homestead's envelope (`SeatRegion.sides`, the smallest side box) over the seats the pass would offer (its own
`free_seats`, filtered by the seat region), on a copy of the seat region's raster with every box standing painted. The
smallest envelope and painting only what stands make it optimistic: it errs toward seating a margin, never toward skipping
one the engine would fill (measured, not assumed: `observe` logs each margin's prediction beside what the engine seated).
"""

from __future__ import annotations

import io
import math
import sys
import time
from contextlib import redirect_stdout
from typing import Any

sys.path.insert(0, "/diagram/.clones/diagram-performance/.claude/skills/diagram")
import numpy as np  # noqa: E402

from l7r.diagram.hamletgen import HamletSpec, plan_site  # noqa: E402
from l7r.diagram.hamletgen.driver import STAGES, roll_scope  # noqa: E402
from l7r.diagram.hamletgen.homesteads import capacity as C  # noqa: E402
from l7r.diagram.hamletgen.homesteads import stages as ST  # noqa: E402
from l7r.diagram.hamletgen.plan import beyond_the_band  # noqa: E402
from l7r.diagram.settlement import Settlement  # noqa: E402

REF = {"name": "Inashiro", "down_deg": 90, "water_sink": "pond", "settlement_form": "nucleated", "fixtures_min": {"shrine": 1}}
BASE_REST = C.seat_the_rest
LOG: list[dict[str, Any]] = []


def predicted_capacity(s: Any, plan: Any, placed: int) -> tuple[int, int]:
    """(the prediction, the seats the pass would offer)."""
    region = getattr(s, "_seat_region", None)
    seats = C.free_seats(s, (float(plan.seat["cx"]), float(plan.seat["cy"])))
    if region is None:
        return placed + len(seats), len(seats)
    seats = [q for q, ok in zip(seats, region.offer(seats), strict=True) if ok]
    seats = [q for q in seats if not C._near_a_house(s, q)]
    occ = region.buildable.array().astype(bool).copy()
    cell, x0, y0 = region.buildable.cell, region.buildable.x0, region.buildable.y0
    ny, nx = occ.shape

    def span(a: float, b: float, o: float, n: int) -> tuple[int, int]:
        return max(0, math.floor((a - o) / cell)), min(n, math.ceil((b - o) / cell))

    for bx, by, bw, bh in [p[:4] for p in s.placed]:
        i0, i1 = span(bx - bw / 2, bx + bw / 2, x0, nx)
        j0, j1 = span(by - bh / 2, by + bh / 2, y0, ny)
        if i0 < i1 and j0 < j1:
            occ[j0:j1, i0:i1] = True
    sx0, sy0, sx1, sy1 = min(region.sides, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]))
    packed = 0
    for qx, qy in seats:
        i0, i1 = span(qx + sx0, qx + sx1, x0, nx)
        j0, j1 = span(qy + sy0, qy + sy1, y0, ny)
        if i0 >= i1 or j0 >= j1 or occ[j0:j1, i0:i1].any():
            continue
        occ[j0:j1, i0:i1] = True
        packed += 1
    return placed + packed, len(seats)


def make_rest(mode: str) -> Any:
    def rest(s: Any, plan: Any, placed: int) -> int:
        want = plan.spec.households
        if placed >= want:
            return placed
        t0 = time.perf_counter()
        pred, offered = predicted_capacity(s, plan, placed)
        t_pred = time.perf_counter() - t0
        if mode == "prune" and pred < want:
            LOG.append({"before": placed, "pred": pred, "offered": offered, "pruned": True, "t_pred": t_pred, "after": placed})
            return placed
        got = BASE_REST(s, plan, placed)
        LOG.append({"before": placed, "pred": pred, "offered": offered, "pruned": False, "t_pred": t_pred, "after": got})
        return got

    return rest


def run(mode: str, households: int, seed: int) -> tuple[float, int, int]:
    LOG.clear()
    ST.seat_the_rest = BASE_REST if mode == "base" else make_rest(mode)
    with beyond_the_band():
        plan = plan_site(HamletSpec(seed=seed, households=households, **REF))
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    took = 0.0
    with roll_scope(plan.spec):
        for st in STAGES:
            t0 = time.perf_counter()
            with redirect_stdout(io.StringIO()):
                st(s, plan)
            if st.__name__ == "stage_homesteads":
                took = time.perf_counter() - t0
                break
    return took, len(s.M.get("houses") or []), int((s.M.get("meta") or {}).get("seat_margin", 0))


if __name__ == "__main__":
    mode, h = sys.argv[1], int(sys.argv[2])
    for seed in [int(x) for x in sys.argv[3].split(",")]:
        took, houses, margin = run(mode, h, seed)
        print(f"{mode} h={h} seed={seed:3} homesteads={took:6.2f}s houses={houses} margin_rung={margin}", flush=True)
        if mode != "base":
            wrong = [m for m in LOG if not m["pruned"] and (m["pred"] >= h) != (m["after"] >= h)]
            print(f"   margins at the pass: {[(m['before'], m['pred'], m['after']) for m in LOG]}  (before, predicted, seated)")
            print(f"   prediction disagreed with the outcome on {len(wrong)} of {len([m for m in LOG if not m['pruned']])} margins run; predicting took {sum(m['t_pred'] for m in LOG) * 1000:.0f} ms in all")
