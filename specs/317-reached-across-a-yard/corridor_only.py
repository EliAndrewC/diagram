"""How many seats does the seating lose to the corridor ALONE? (feature 317: the most a passage across a neighbor's yard could
relieve - a household offered a passage is one whose every other rule passed and whose corridor the tree could not take)

    ROOT=<repo> python3 corridor_only.py 15 1,2,3,4,5,6,7,8

Per seed, every side the parts are asked of (`_parts_fit`): where `access_corridor` finds none, the rest of the parts' rules
are asked as though one were found (a stub corridor of no legs), and the side counted CORRIDOR-ONLY if they all pass - then
refused as before, so the roll is the shipped one. A placer call (a seat) none of whose sides passed but one of which was
corridor-only is a seat lost to the corridor alone.
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
from l7r.diagram.hamletgen.homesteads import stages as ST  # noqa: E402
from l7r.diagram.hamletgen.plan import beyond_the_band  # noqa: E402
from l7r.diagram.settlement import Settlement  # noqa: E402
from l7r.diagram.settlement.rolling import fit as F  # noqa: E402

REF = {"name": "Inashiro", "down_deg": 90, "water_sink": "pond", "settlement_form": "nucleated", "fixtures_min": {"shrine": 1}}
N: dict[str, int] = defaultdict(int)
T: dict[str, float] = defaultdict(float)
STATE: dict[str, Any] = {"probe": False, "stubbed": False, "seat_corr_only": False}
DIST: dict[str, list[float]] = defaultdict(list)  # feet from a corridor-only side's door to: a seated neighbor's yard, its house, the tree


def distances(s: Any, geom: Any) -> None:
    """From the side's first door: the nearest seated neighbor's yard and house (box edge), and the access tree's nearest leg."""
    import math

    from l7r.diagram.settlement import seg_dist
    from l7r.diagram.settlement.rolling.access import doors_of

    tree = getattr(s, "_access", None)
    if tree is None:
        return
    door = doors_of(geom, tree.half)[0]
    ft = s.px(1.0)

    def to_box(b: Any) -> float:
        cx, cy, w, h = (float(v) for v in b[:4])
        return math.dist(door, (min(max(door[0], cx - w / 2), cx + w / 2), min(max(door[1], cy - h / 2), cy + h / 2))) / ft

    yards = [to_box(b) for r in s.M.get("houses") or [] if (b := ((r.get("geom") or {}).get("boxes") or {}).get("yard")) is not None]
    houses = [to_box(b) for r in s.M.get("houses") or [] if (b := ((r.get("geom") or {}).get("boxes") or {}).get("house")) is not None]
    if yards:
        DIST["yard"].append(min(yards))
    if houses:
        DIST["house"].append(min(houses))
    if tree.segs:
        DIST["tree"].append(min(seg_dist(door[0], door[1], a, b) for a, b in tree.segs) / ft)


def install() -> None:
    from l7r.diagram.settlement.rolling import access as A
    from l7r.diagram.settlement.rolling import route as R

    real_ac = F.access_corridor
    real_admits = A.tree_admits

    def admits(s: Any, corridor: Any, geom: Any) -> bool:
        STATE["admits_asked"] += 1
        return real_admits(s, corridor, geom)

    A.tree_admits = admits
    real_search = R.search

    def search(*a: Any, **k: Any) -> Any:
        got = real_search(*a, **k)
        N["route_searched"] += 1
        N["route_none"] += got is None
        return got

    R.search = search

    def ac(s: Any, geom: Any) -> Any:
        STATE["admits_asked"] = 0
        t0 = time.perf_counter()
        c = real_ac(s, geom)
        dt = time.perf_counter() - t0
        T["corridor_found" if c is not None else "corridor_none"] += dt
        if c is None and STATE["probe"]:
            boxes = geom.get("boxes") or {}
            key = ("corridor", tuple(boxes.get("house") or geom["house"]), tuple(boxes.get("yard") or geom.get("yard") or ()))
            seen = [x for x in (A._standing_memo(s)[1].get(key) or ([], None))[0] if x is not A.ROUTE_LATER]
            STATE["why"] = "lane-law" if STATE["admits_asked"] else ("leg-tests" if seen else "no-candidate")
            if STATE["why"] == "leg-tests":
                import math

                memo = A._standing_memo(s)[1]
                kinds = set()
                for cor in seen:
                    last = len(cor) - 2
                    ls = [(a, b) for n, (a, b) in enumerate(A.legs(cor)) if not (n == last and math.dist(a, b) < 1e-6)]
                    own = all(A.fixtures_clear(s, a, b, geom) and A.parts_clear(s, a, b, geom) for a, b in ls)
                    law = all(A.lawful_leg(s, a, b, memo) for a, b in ls)
                    kinds.add("own" if not own and law else "ground" if own and not law else "both")
                STATE["why"] = "leg-own-parts" if kinds == {"own"} else "leg-ground" if kinds == {"ground"} else "leg-mixed"
            STATE["stubbed"] = True
            h = geom["house"]
            return ((float(h[0]), float(h[1])),)
        return c

    F.access_corridor = ac
    real_pf = Settlement._parts_fit

    def pf(self: Any, geom: Any) -> bool:
        STATE["stubbed"], STATE["probe"] = False, True
        try:
            ok = real_pf(self, geom)
        finally:
            STATE["probe"] = False
        N["sides"] += 1
        if not STATE["stubbed"]:
            N["sides_passed" if ok else "sides_refused_else"] += 1
            return ok
        N["corridor_none"] += 1
        if ok:
            N["corridor_only"] += 1
            N["why_" + STATE["why"]] += 1
            STATE["seat_corr_only"] = True
            distances(self, geom)
        geom.pop("access", None)
        geom.pop("wood", None)
        return False

    Settlement._parts_fit = pf
    tp = Settlement.try_place

    def try_place(self: Any, x: float, y: float, kind: str, *a: Any, **k: Any) -> Any:
        if not getattr(self, "_growing", False):
            return tp(self, x, y, kind, *a, **k)
        STATE["seat_corr_only"] = False
        ok = tp(self, x, y, kind, *a, **k)
        N["seats"] += 1
        if ok:
            N["seated"] += 1
        elif STATE["seat_corr_only"]:
            N["seats_lost_to_corridor"] += 1
        return ok

    Settlement.try_place = try_place
    gm = G.grow_the_margin

    def grow(s: Any, *a: Any, **k: Any) -> Any:
        s._growing = True
        try:
            return gm(s, *a, **k)
        finally:
            s._growing = False

    G.grow_the_margin = grow
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
    keys = ("seats", "seated", "seats_lost_to_corridor", "sides", "sides_passed", "sides_refused_else", "corridor_none", "corridor_only")
    print("seed stage_s houses | " + " ".join(keys) + " | s: corridor_none corridor_found")
    tot: dict[str, int] = defaultdict(int)
    WHY: dict[str, int] = defaultdict(int)
    for seed in [int(x) for x in sys.argv[2].split(",")]:
        N.clear()
        T.clear()
        took, houses = run(h, seed)
        print(f"{seed:4d} {took:6.2f} {houses:5d} | " + " ".join(str(N[k]) for k in keys) + f" | {T['corridor_none']:.2f} {T['corridor_found']:.2f}", flush=True)
        for k in keys:
            tot[k] += N[k]
        for k, v in N.items():
            if k.startswith(("why_", "route_")):
                WHY[k] += v
    print("ALL | " + " ".join(f"{k}={tot[k]}" for k in keys))
    print("WHY | " + " ".join(f"{k}={v}" for k, v in sorted(WHY.items())))
    for k, v in sorted(DIST.items()):
        v = sorted(v)
        q = [v[int(f * (len(v) - 1))] for f in (0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0)]
        print(f"door to nearest {k:5s} ft (n={len(v)}): min/p10/p25/median/p75/p90/max " + " ".join(f"{x:.0f}" for x in q))
