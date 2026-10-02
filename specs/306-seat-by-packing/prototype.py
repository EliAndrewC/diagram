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


#: Round 2's seats beside the tree: setbacks from a leg (house center to the leg's line) and the step along it, in bundle pitches.
TREE_SETBACKS = (0.55, 0.8, 1.05)
TREE_STEP = 0.5


def beside_the_tree(s: Any, plan: Any, placed: int) -> int:
    """ROUND 2 (research R2: the exhaustive pass's offers fail for want of a corridor to the access tree): seats proposed on
    both sides of every leg of the tree at `TREE_SETBACKS`, every `TREE_STEP` along it, nearest the seat's center first; each
    house seated adds its corridor's legs and so new seats beside them. The placer asks every rule of each, as today."""
    import heapq

    from l7r.diagram.hamletgen.consts import BUNDLE_PITCH

    want = plan.spec.households
    tree = getattr(s, "_access", None)
    if placed >= want or tree is None:
        return BASE_REST(s, plan, placed)
    cx, cy = float(plan.seat["cx"]), float(plan.seat["cy"])
    heap: list[tuple[float, float, float]] = []
    seen: set[tuple[int, int]] = set()
    done = 0

    def grow() -> None:
        nonlocal done
        for a, b in tree.segs[done:]:
            dx, dy = b[0] - a[0], b[1] - a[1]
            m = math.hypot(dx, dy) or 1.0
            ux, uy, nx_, ny_ = dx / m, dy / m, -dy / m, dx / m
            k = 0
            while k * TREE_STEP * BUNDLE_PITCH <= m:
                t = k * TREE_STEP * BUNDLE_PITCH
                for d in TREE_SETBACKS:
                    for sgn in (1.0, -1.0):
                        q = (a[0] + ux * t + sgn * nx_ * d * BUNDLE_PITCH, a[1] + uy * t + sgn * ny_ * d * BUNDLE_PITCH)
                        key = (round(q[0] / 8.0), round(q[1] / 8.0))
                        if key not in seen:
                            seen.add(key)
                            heapq.heappush(heap, (math.hypot(q[0] - cx, q[1] - cy), q[0], q[1]))
                k += 1
        done = len(tree.segs)

    grow()
    offered = took = 0
    while heap and placed < want:
        _, qx, qy = heapq.heappop(heap)
        if C._near_a_house(s, (qx, qy)):
            continue
        offered += 1
        s._seat_search["candidates"] += 1
        if s.try_place(qx, qy, "plain"):
            placed += 1
            took += 1
            grow()
    s._seat_search["exhaustive_offered"], s._seat_search["exhaustive_took"] = offered, took
    LOG.append({"before": placed - took, "pred": -1, "offered": offered, "pruned": False, "t_pred": 0.0, "after": placed})
    return placed


#: Round 3's gap between a standing homestead's envelope and its neighbor's, px.
GROW_GAP = 4.0


def grow_from_the_houses(s: Any, plan: Any, placed: int) -> int:
    """ROUND 3 (research R3: margins seat 15-40 on ground that holds 200-odd boxes - the greedy seating blocks itself): seats
    proposed NEXT TO the homesteads standing - each house's envelope (`geom["bbox"]`) offers the eight positions one envelope
    away, plus `GROW_GAP` - nearest the seat's center first; each house seated offers its own. The placer asks every rule."""
    import heapq

    want = plan.spec.households
    if placed >= want:
        return placed
    cx, cy = float(plan.seat["cx"]), float(plan.seat["cy"])
    heap: list[tuple[float, float, float]] = []
    seen: set[tuple[int, int]] = set()
    done = 0

    def grow() -> None:
        nonlocal done
        houses = s.M.get("houses") or []
        for h in houses[done:]:
            g = h.get("geom") or {}
            bx, by, bw, bh = (g.get("bbox") or (h["x"], h["y"], 140.0, 100.0))[:4]
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                q = (float(h["x"]) + dx * (bw + GROW_GAP), float(h["y"]) + dy * (bh + GROW_GAP))
                key = (round(q[0] / 8.0), round(q[1] / 8.0))
                if key not in seen:
                    seen.add(key)
                    heapq.heappush(heap, (math.hypot(q[0] - cx, q[1] - cy), q[0], q[1]))
        done = len(houses)

    grow()
    offered = took = 0
    while heap and placed < want:
        _, qx, qy = heapq.heappop(heap)
        if C._near_a_house(s, (qx, qy)):
            continue
        offered += 1
        s._seat_search["candidates"] += 1
        if s.try_place(qx, qy, "plain"):
            placed += 1
            took += 1
            grow()
    s._seat_search["exhaustive_offered"], s._seat_search["exhaustive_took"] = offered, took
    LOG.append({"before": placed - took, "pred": -1, "offered": offered, "pruned": False, "t_pred": 0.0, "after": placed})
    return placed


#: Round 4's layout, px: rows of homesteads one `LANE_ROW` apart, each fronting a lane with its yard; along a lane every
#: `LANE_PITCH`; a house's center `LANE_SETBACK` from its lane (the yard's far edge, 30 px south of the house's center in its
#: own frame, the corridor's half-width and a margin).
LANE_ROW = float(__import__("os").environ.get("LANE_ROW", "120"))
LANE_PITCH = float(__import__("os").environ.get("LANE_PITCH", "50"))
LANE_SETBACK = 41.0
LANE_REACH = 700.0


def lanes_first(s: Any, plan: Any, placed: int) -> int:
    """ROUND 4 (research R4: a seat needs a straight corridor to the access tree, and a cluster seated in any order blocks its
    own; widening the corridor search moves which margin succeeds, not whether): FRONTAGE LANES laid first as legs of the
    tree - a spine through the seat's center along the houses' facing, and lanes across it one row apart, parallel to the
    houses, each leg kept only on lawful ground (`lawful_ground`, the corridors' own test) - then homesteads offered along
    each lane, side by side, yards toward it, nearest the center first. The placer asks every rule of each."""
    import heapq

    from l7r.diagram.hamletgen.ways.corridors import STRIP_ROLE
    from l7r.diagram.hamletgen.ways.tree import admits, seating_law
    from l7r.diagram.settlement.rolling.access import lawful_ground

    want = plan.spec.households
    tree = getattr(s, "_access", None)
    if placed >= want or tree is None:
        return BASE_REST(s, plan, placed)
    cx, cy = float(plan.seat["cx"]), float(plan.seat["cy"])
    th = math.radians(s._turn_at(cx, cy))
    ux, uy = math.cos(th), math.sin(th)  # along the houses
    nx_, ny_ = -math.sin(th), math.cos(th)  # toward their yards

    def lay(a: Any, d: Any, length: float) -> float:
        """The longest leg from `a` along `d` on lawful ground, halving down to 30 px; added to the tree; its length."""
        n = length
        while n >= 30.0:
            b = (a[0] + d[0] * n, a[1] + d[1] * n)
            if lawful_ground(s, a, b) and admits(seating_law(s), s.M, [b, a], STRIP_ROLE):  # oriented toward the tree, as a corridor is
                tree.add(b, a)
                s.M.setdefault("access_corridors", []).append({"pts": [[round(b[0], 1), round(b[1], 1)], [round(a[0], 1), round(a[1], 1)]], "lane": True})
                return n
            n /= 2.0
        return 0.0

    heap: list[tuple[float, float, float]] = []
    for sgn in (1.0, -1.0):
        spine = lay((cx, cy), (nx_ * sgn, ny_ * sgn), LANE_REACH / 2)
        k = 0
        while k * LANE_ROW <= spine:
            p = (cx + nx_ * sgn * k * LANE_ROW, cy + ny_ * sgn * k * LANE_ROW)
            for side in (1.0, -1.0):
                run = lay(p, (ux * side, uy * side), LANE_REACH / 2) if k else LANE_REACH / 2
                t = LANE_PITCH
                while t <= run:
                    q = (p[0] + ux * side * t - nx_ * LANE_SETBACK, p[1] + uy * side * t - ny_ * LANE_SETBACK)
                    heapq.heappush(heap, (math.hypot(q[0] - cx, q[1] - cy), q[0], q[1]))
                    t += LANE_PITCH
            k += 1
    offered = took = 0
    while heap and placed < want:
        _, qx, qy = heapq.heappop(heap)
        if C._near_a_house(s, (qx, qy)):
            continue
        offered += 1
        s._seat_search["candidates"] += 1
        if s.try_place(qx, qy, "plain"):
            placed += 1
            took += 1
    s._seat_search["exhaustive_offered"], s._seat_search["exhaustive_took"] = offered, took
    LOG.append({"before": placed - took, "pred": -1, "offered": offered, "pruned": False, "t_pred": 0.0, "after": placed})
    if placed < want:
        return BASE_REST(s, plan, placed)
    return placed


#: Round 5: a margin's exhaustive pass is given up after this many offers in a row seat no one (env `DRY`; 0 = never).
DRY = int(__import__("os").environ.get("DRY", "0"))


def rest_with_takes(s: Any, plan: Any, placed: int) -> int:
    """ROUND 5 (research R5): the engine's exhaustive pass, verbatim in order, recording at which offer each house was taken -
    and, where `DRY` is set, giving the margin up after `DRY` offers in a row that seat no one."""
    want = plan.spec.households
    if placed >= want:
        return placed
    seats = C.free_seats(s, (float(plan.seat["cx"]), float(plan.seat["cy"])))
    region = getattr(s, "_seat_region", None)
    if region is not None:
        seats = [q for q, ok in zip(seats, region.offer(seats), strict=True) if ok]
    offered = took = dry = 0
    takes: list[int] = []
    for q in seats:
        if placed >= want or (DRY and dry >= DRY):
            break
        if C._near_a_house(s, q):
            continue
        offered += 1
        dry += 1
        s._seat_search["candidates"] += 1
        if s.try_place(q[0], q[1], "plain"):
            placed += 1
            took += 1
            takes.append(offered)
            dry = 0
    s._seat_search["exhaustive_offered"], s._seat_search["exhaustive_took"] = offered, took
    gaps = [b - a for a, b in zip([0, *takes], takes, strict=False)]
    LOG.append({"before": placed - took, "pred": max(gaps, default=0), "offered": offered, "pruned": bool(DRY and dry >= DRY), "t_pred": 0.0, "after": placed, "takes": takes})
    return placed


def make_rest(mode: str) -> Any:
    if mode == "rescue":
        return rest_then_rescue
    if mode == "takes":
        return rest_with_takes
    if mode == "comb":
        return comb_off_the_strip
    if mode == "lanes":
        return lanes_first
    if mode == "grow":
        return grow_from_the_houses
    if mode == "tree":
        return beside_the_tree

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
        print(f"{mode} h={h} seed={seed:3} homesteads={took:6.2f}s houses={houses} margin_rung={margin} exhaustive (before, offered, after): {[(m['before'], m['offered'], m['after']) for m in LOG]}", flush=True)
        if mode not in ("base", "tree", "grow", "lanes", "takes"):
            wrong = [m for m in LOG if not m["pruned"] and (m["pred"] >= h) != (m["after"] >= h)]
            print(f"   margins at the pass: {[(m['before'], m['pred'], m['offered'], m['after']) for m in LOG]}  (before, predicted, offered, seated)")
            print(f"   prediction disagreed with the outcome on {len(wrong)} of {len([m for m in LOG if not m['pruned']])} margins run; predicting took {sum(m['t_pred'] for m in LOG) * 1000:.0f} ms in all")
        if mode == "takes":
            for m in LOG:
                print(f"   margin: before {m['before']:2} after {m['after']:2} offered {m['offered']:5} longest dry spell before a take {m['pred']:4} takes at {m['takes']}")


def no_lattice() -> None:
    """Round 4b: the front row and the lattice rounds offer nothing, so the lanes lay out the whole cluster."""
    from l7r.diagram.settlement import Settlement as _S

    ST.front_row = lambda *a, **k: []
    _S.cluster_seeds = lambda self, *a, **k: []


if __import__("os").environ.get("NOLATTICE"):
    no_lattice()


#: Round 4c's setbacks from a lane to a house's center, px (both sides; the placer decides).
COMB_SETBACKS = (45.0, 65.0)


def comb_off_the_strip(s: Any, plan: Any, placed: int) -> int:
    """ROUND 4c (research R4: a spine from the strip's END is a corner the lane law refuses): frontage lanes laid as T-junctions
    off the exit strip along its length, every `LANE_ROW`, both sides, each oriented toward the strip and admitted by the
    tree's own test; homesteads offered on both sides of the strip and of every lane at `COMB_SETBACKS`, every `LANE_PITCH`,
    nearest the seat's center first. The placer asks every rule of each."""
    import heapq

    from l7r.diagram.hamletgen.ways.corridors import STRIP_ROLE
    from l7r.diagram.hamletgen.ways.tree import admits, seating_law
    from l7r.diagram.settlement.rolling.access import lawful_ground

    want = plan.spec.households
    tree = getattr(s, "_access", None)
    if placed >= want or tree is None or not tree.segs:
        return BASE_REST(s, plan, placed)
    cx, cy = float(plan.seat["cx"]), float(plan.seat["cy"])
    (ax_, ay_), (bx_, by_) = tree.segs[0]  # the exit strip, from the seat's center outward
    m = math.hypot(bx_ - ax_, by_ - ay_) or 1.0
    ux, uy = (bx_ - ax_) / m, (by_ - ay_) / m
    legs: list[tuple[Any, Any]] = [((ax_, ay_), (bx_, by_))]

    def lay(a: Any, d: Any, length: float) -> float:
        n = length
        while n >= 40.0:
            b = (a[0] + d[0] * n, a[1] + d[1] * n)
            if lawful_ground(s, a, b) and admits(seating_law(s), s.M, [b, a], STRIP_ROLE):
                tree.add(b, a)
                s.M.setdefault("access_corridors", []).append({"pts": [[round(b[0], 1), round(b[1], 1)], [round(a[0], 1), round(a[1], 1)]], "lane": True})
                legs.append((a, b))
                return n
            n *= 0.75
        return 0.0

    k = 1
    while k * LANE_ROW < min(m, LANE_REACH):
        p = (ax_ + ux * k * LANE_ROW, ay_ + uy * k * LANE_ROW)
        for sgn in (1.0, -1.0):
            lay(p, (-uy * sgn, ux * sgn), LANE_REACH / 2)
        k += 1
    heap: list[tuple[float, float, float]] = []
    for a, b in legs:
        L = math.dist(a, b) or 1.0
        vx, vy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        t = LANE_PITCH / 2
        while t <= L:
            for d in COMB_SETBACKS:
                for sgn in (1.0, -1.0):
                    q = (a[0] + vx * t - vy * d * sgn, a[1] + vy * t + vx * d * sgn)
                    heapq.heappush(heap, (math.hypot(q[0] - cx, q[1] - cy), q[0], q[1]))
            t += LANE_PITCH
    offered = took = 0
    while heap and placed < want:
        _, qx, qy = heapq.heappop(heap)
        if C._near_a_house(s, (qx, qy)):
            continue
        offered += 1
        s._seat_search["candidates"] += 1
        if s.try_place(qx, qy, "plain"):
            placed += 1
            took += 1
    s._seat_search["exhaustive_offered"], s._seat_search["exhaustive_took"] = offered, took
    LOG.append({"before": placed - took, "pred": len(legs), "offered": offered, "pruned": False, "t_pred": 0.0, "after": placed})
    if placed < want and not __import__("os").environ.get("NOFALLBACK"):
        return BASE_REST(s, plan, placed)
    return placed


#: Round 6: a margin left at most `RESCUE` households short by the exhaustive pass is searched again, finer, before the ladder
#: gives it up - the seat grid at `RESCUE_STEP` of a pitch and the corridor search over `RESCUE_TARGETS` tree points.
RESCUE = int(__import__("os").environ.get("RESCUE", "0"))
RESCUE_STEP = 1.0 / 6.0
RESCUE_TARGETS = 40


def rest_then_rescue(s: Any, plan: Any, placed: int) -> int:
    """ROUND 6 (research R6: seed 47's margins reach 38-39 of 40 and are thrown away): the exhaustive pass as round 5 runs it,
    then, where it leaves no more than `RESCUE` households, a finer pass over the same margin before the ladder moves on."""
    from l7r.diagram.settlement.rolling import access as A

    placed = rest_with_takes(s, plan, placed)
    want = plan.spec.households
    if placed >= want or want - placed > RESCUE:
        return placed
    seats = C.free_seats(s, (float(plan.seat["cx"]), float(plan.seat["cy"])), RESCUE_STEP)
    region = getattr(s, "_seat_region", None)
    if region is not None:
        seats = [q for q, ok in zip(seats, region.offer(seats), strict=True) if ok]
    keep = A.TARGETS_TRIED
    A.TARGETS_TRIED = RESCUE_TARGETS
    s.__dict__.pop("_corridor_memo", None)  # the corridor candidates remembered at 12 targets
    tree = getattr(s, "_access", None)
    if tree is not None:
        tree._targets = {}
    offered = 0
    try:
        for q in seats:
            if placed >= want:
                break
            if C._near_a_house(s, q):
                continue
            offered += 1
            if s.try_place(q[0], q[1], "plain"):
                placed += 1
    finally:
        A.TARGETS_TRIED = keep
        s.__dict__.pop("_corridor_memo", None)
        if tree is not None:
            tree._targets = {}
    LOG[-1]["rescue"] = (offered, placed)
    return placed
