"""Where does the homesteads seating spend its time on refused seats? (GM 2026-10-02: would a window pre-trimmed to the
buildable ground, or a bigger one, make placement faster?)

    python3 refusals.py 40 2,6,8,9,10,12,13,39

Per seed: the stages run up to and including stage_homesteads; inside it every grown seat popped from the heap is followed to
its outcome, and the time of each phase is summed by outcome:

  settle      `settled_seat` (rolling the next household's own reach at the seat) - every popped seat pays it
  dropped     popped, settled, then dropped before the placer: no settle, near a house, past the bound
  house-box   the placer refused the house's own box (the free-ground raster, the canvas, a corridor, two homesteads)
  reach/water refused for the field's reach or the water
  envelope    every garden side's box refused (raster or placed boxes, after the one computed move)
  corridor    no corridor candidate from the house and yard (`seat_reaches_tree`)
  parts       every side refused by `_parts_fit` (incl. the corridor search's lawful legs and the lane law, `tree_admits`)
  seated      the placer took it; its commit (reserve the corridor, record the parts) timed apart
"""

from __future__ import annotations

import io
import os
import sys
import time
from collections import defaultdict
from contextlib import redirect_stdout
from typing import Any

sys.path.insert(0, os.environ.get("ROOT", "/diagram/.clones/diagram-performance") + "/.claude/skills/diagram")
from l7r.diagram.hamletgen import HamletSpec, plan_site  # noqa: E402
from l7r.diagram.hamletgen.driver import STAGES, roll_scope  # noqa: E402
from l7r.diagram.hamletgen.homesteads import growth as G  # noqa: E402
from l7r.diagram.hamletgen.plan import beyond_the_band  # noqa: E402
from l7r.diagram.settlement import Settlement  # noqa: E402
from l7r.diagram.settlement.rolling import access as A  # noqa: E402
from l7r.diagram.settlement.rolling import place as P  # noqa: E402
from l7r.diagram.settlement.rolling import fit as F  # noqa: E402

REF = {"name": "Inashiro", "down_deg": 90, "water_sink": "pond", "settlement_form": "nucleated", "fixtures_min": {"shrine": 1}}

T: dict[str, float] = defaultdict(float)  # seconds by outcome
N: dict[str, int] = defaultdict(int)  # seats by outcome
SUB: dict[str, float] = defaultdict(float)  # seconds inside the placer by sub-test
CUR: dict[str, Any] = {}
PEND: dict[str, float] = {}
ST_BY: dict[str, float] = defaultdict(float)  # settle seconds by the outcome they led to


def timed(name: str, fn: Any) -> Any:
    def w(*a: Any, **k: Any) -> Any:
        t0 = time.perf_counter()
        try:
            return fn(*a, **k)
        finally:
            SUB[name] += time.perf_counter() - t0

    return w


def install() -> None:
    settle = G.settled_seat

    def settled(*a: Any, **k: Any) -> Any:
        t0 = time.perf_counter()
        got = settle(*a, **k)
        dt = time.perf_counter() - t0
        T["settle"] += dt
        N["popped"] += 1
        PEND["settle"] = PEND.get("settle", 0.0) + dt  # charged to the outcome of the next placer call, else dropped
        return got

    G.settled_seat = settled
    # the placer's own refusal points, each timed; the verdict classified by which fired last
    S = Settlement
    for name in ("_house_box_refused", "_envelope_blocked", "_parts_fit", "_bundle_geom"):
        setattr(S, name, timed(name, getattr(S, name)))
    P.within_field_reach = timed("within_field_reach", P.within_field_reach) if hasattr(P, "within_field_reach") else None
    rr = P.seat_reaches_tree

    def reaches(s: Any, geom: Any) -> bool:
        t0 = time.perf_counter()
        ok = rr(s, geom)
        SUB["seat_reaches_tree"] += time.perf_counter() - t0
        CUR["reached"] = ok
        return ok

    P.seat_reaches_tree = reaches
    A.tree_admits = timed("tree_admits", A.tree_admits)
    A.access_corridor = timed("access_corridor", A.access_corridor)
    F_access = getattr(F, "access_corridor", None)
    if F_access is not None:
        F.access_corridor = A.access_corridor
    hb = S._house_box_refused

    def house_box(self: Any, box: Any) -> Any:
        r = hb(self, box)
        CUR["house_box"] = bool(r)
        return r

    S._house_box_refused = house_box
    tp = S.try_place

    def try_place(self: Any, x: float, y: float, kind: str, *a: Any, **k: Any) -> Any:
        if not getattr(self, "_growing", False):
            return tp(self, x, y, kind, *a, **k)
        CUR.clear()
        before = dict(SUB)
        t0 = time.perf_counter()
        ok = tp(self, x, y, kind, *a, **k)
        dt = time.perf_counter() - t0
        if ok:
            out = "seated"
        elif CUR.get("house_box"):
            out = "house-box"
        elif "reached" not in CUR and SUB["_bundle_geom"] == before.get("_bundle_geom", 0.0):
            out = "reach/water"
        elif CUR.get("reached") is False:
            out = "corridor"
        elif SUB["_parts_fit"] > before.get("_parts_fit", 0.0):
            out = "parts"
        else:
            out = "envelope"
        T[out] += dt
        N[out] += 1
        ST_BY[out] += PEND.pop("settle", 0.0)
        return ok

    S.try_place = try_place
    gm = G.grow_the_margin

    def grow(s: Any, *a: Any, **k: Any) -> Any:
        N["margins"] += 1
        s._growing = True
        try:
            return gm(s, *a, **k)
        finally:
            s._growing = False

    G.grow_the_margin = grow
    from l7r.diagram.hamletgen.homesteads import stages as ST

    ST.grow_the_margin = grow


def run(households: int, seed: int) -> tuple[float, int]:
    with beyond_the_band():
        plan = plan_site(HamletSpec(seed=seed, households=households, **REF))
    s = Settlement(W=plan.W, H=plan.H, seed=seed)
    took = 0.0
    with roll_scope(plan.spec):
        for st in STAGES:
            t0 = time.perf_counter()
            with redirect_stdout(io.StringIO()):
                st(s, plan)
            if st.__name__ == "stage_homesteads":
                took = time.perf_counter() - t0
                break
    return took, len(s.M.get("houses") or [])


if __name__ == "__main__":
    install()
    h = int(sys.argv[1])
    print("seed  stage_s  houses margins popped | outcome: n / s ...")
    tot: dict[str, float] = defaultdict(float)
    totn: dict[str, int] = defaultdict(int)
    stage_total = 0.0
    for seed in [int(x) for x in sys.argv[2].split(",")]:
        T.clear()
        N.clear()
        PEND.clear()
        took, houses = run(h, seed)
        stage_total += took
        dropped = N["popped"] - sum(N[k] for k in ("seated", "house-box", "reach/water", "envelope", "corridor", "parts"))
        parts = " ".join(f"{k}={N[k]}/{T[k]:.2f}" for k in ("settle", "seated", "house-box", "reach/water", "envelope", "corridor", "parts"))
        print(f"{seed:4d} {took:7.2f} {houses:6d} {N['margins']:7d} {N['popped']:6d} | dropped={dropped} {parts}", flush=True)
        for k, v in T.items():
            tot[k] += v
        for k, v in N.items():
            totn[k] += v
    print(f"\nALL: homesteads stage {stage_total:.1f} s")
    for k in ("settle", "seated", "house-box", "reach/water", "envelope", "corridor", "parts"):
        print(f"  {k:12s} n={totn[k]:6d}  {tot[k]:7.2f} s  ({100 * tot[k] / stage_total:4.1f}% of the stage)")
    print("  settle time by what the seat came to:", " ".join(f"{k}={v:.2f}" for k, v in sorted(ST_BY.items(), key=lambda kv: -kv[1])), f"dropped~={tot['settle'] - sum(ST_BY.values()):.2f}")
    print("  placer sub-tests (all calls, s):", " ".join(f"{k}={v:.2f}" for k, v in sorted(SUB.items(), key=lambda kv: -kv[1])))
