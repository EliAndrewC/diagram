"""Feature 308, Phase 0: seat a cluster margin by GROWTH, measured against the engine's seating (monkeypatches only).

    python3 specs/308-grow-the-cluster/prototype.py grow 40 1,2,...   # the grower in place of the three passes
    python3 specs/308-grow-the-cluster/prototype.py base 40 1,2,...   # the engine as it is, timed the same way

THE GROWER (the GM, 2026-10-02: "once you've placed the first house, you should notionally be able to compute the minimum distance
needed to seat a second house, then place it in a direction, then repeat, with a little randomized jitter"; and "keep in mind the
sunlight / shade requirements when computing minimum distance"). The first house is offered at the cluster's seed point; every
house standing offers the seats around it in eight directions, each at the MINIMUM DISTANCE in that direction - the homestead's
FOOTPRINT (its envelope, its reserved woodlot seats) on both sides, and to the SOUTH of a threshing yard its sun corridor
(`SUN_CORRIDOR_FT`) clear of the next house - jittered in direction and spacing by the seed; the seat nearest the cluster's
center is offered first. Each seat is still asked the placer's full rules (`try_place`), whose corridor search joins the house to
the nearest point of the access tree - the neighbor's corridor beside it. The front row and the lattice offer nothing; the
grower replaces the exhaustive pass.
"""

from __future__ import annotations

import heapq
import io
import math
import os
import sys
import time
from contextlib import redirect_stdout
from typing import Any

sys.path.insert(0, os.environ.get("ROOT", "/diagram/.clones/diagram-performance") + "/.claude/skills/diagram")
from l7r.diagram.hamletgen import HamletSpec, plan_site  # noqa: E402
from l7r.diagram.hamletgen.consts import SUN_CORRIDOR_FT  # noqa: E402
from l7r.diagram.hamletgen.driver import STAGES, roll_scope  # noqa: E402
from l7r.diagram.hamletgen.homesteads import capacity as C  # noqa: E402
from l7r.diagram.hamletgen.homesteads import stages as ST  # noqa: E402
from l7r.diagram.hamletgen.plan import beyond_the_band  # noqa: E402
from l7r.diagram.settlement import Settlement  # noqa: E402

REF = {"name": "Inashiro", "down_deg": 90, "water_sink": "pond", "settlement_form": "nucleated", "fixtures_min": {"shrine": 1}}
BASE_REST = C.seat_the_rest
GAP = float(os.environ.get("GAP", "6"))  # px between two footprints
JITTER_DEG = float(os.environ.get("JITTER_DEG", "12"))  # +- the direction
JITTER_FRAC = float(os.environ.get("JITTER_FRAC", "0.12"))  # + up to this share of the spacing
RINGS = tuple(float(r) for r in os.environ.get("RINGS", "1").split(","))  # each direction offered at these multiples of its least distance
#: the growth's widening levels: (directions, rings) - the next level offered when the margin's heap runs dry
LEVELS = tuple((int(a), tuple(float(r) for r in b.split("/"))) for a, b in (lv.split(":") for lv in os.environ.get("LEVELS", "8:1,12:1/1.5,16:1.25/1.75/2.0").split(",")))
CLUMP = 12.0  # px round a reserved woodlot seat (a copse clump's half-width)
STATS: dict[str, Any] = {}


def footprint(h: dict[str, Any], s: Any) -> tuple[float, float, float, float]:
    """(west, east, north, south) reach from the house's center: its envelope and its woodlot seats; south to its yard's far edge
    PLUS the yard's sun corridor (no house may stand there)."""
    g = h.get("geom") or {}
    hx, hy = float(h["x"]), float(h["y"])
    bx, by, bw, bh = g.get("bbox") or (hx, hy, 140.0, 100.0)
    w, e, n, so = hx - (bx - bw / 2), (bx + bw / 2) - hx, hy - (by - bh / 2), (by + bh / 2) - hy
    for p in (h.get("wood_share") or {}).get("seats") or ():
        w, e = max(w, hx - p[0] + CLUMP), max(e, p[0] - hx + CLUMP)
        n, so = max(n, hy - p[1] + CLUMP), max(so, p[1] - hy + CLUMP)
    yard = (g.get("boxes") or {}).get("yard") or g.get("yard")
    if yard is not None:
        so = max(so, (yard[1] + yard[3] / 2) - hy + s.px(SUN_CORRIDOR_FT))
    return w, e, n, so


def grow(s: Any, plan: Any, placed: int) -> int:
    want = plan.spec.households
    if placed >= want:
        return placed
    cx, cy = float(plan.seat["cx"]), float(plan.seat["cy"])
    dep, lat = ST.band_extent(plan.spec.households, plan.cluster_shape, ST.SEATING_GROUND_FT)
    bound = 1.15 * math.hypot(lat, dep)
    heap: list[tuple[float, int, float, float]] = []
    seen: set[tuple[int, int]] = set()
    n = [0]

    def push(q: tuple[float, float]) -> None:
        key = (round(q[0] / 10.0), round(q[1] / 10.0))
        if key in seen or math.hypot(q[0] - cx, q[1] - cy) > bound:
            return
        seen.add(key)
        n[0] += 1
        heapq.heappush(heap, (math.hypot(q[0] - cx, q[1] - cy), n[0], q[0], q[1]))

    done = 0
    level = [0]
    proto: list[tuple[float, float, float, float]] = []

    def offer_around() -> None:
        nonlocal done
        houses = s.M.get("houses") or []
        for h in houses[done:]:
            w, e, nn, so = footprint(h, s)
            pw, pe, pn, ps = proto[0] if proto else (w, e, nn, so)
            hx, hy = float(h["x"]), float(h["y"])
            ndir, rings = LEVELS[level[0]]
            for k in range(ndir):
                ang = math.radians(360.0 / ndir * k + (s._hjit(hx, hy, 300.0 + k) - 0.5) * 2 * JITTER_DEG)
                dx, dy = math.cos(ang), math.sin(ang)
                # the distance along (dx, dy) at which the two footprints' boxes part, plus the gap: the larger axis's need
                need_x = (e + pw) if dx > 0 else (w + pe)
                need_y = (so + pn) if dy > 0 else (nn + ps)
                t = min(need_x / abs(dx) if abs(dx) > 1e-6 else math.inf, need_y / abs(dy) if abs(dy) > 1e-6 else math.inf) + GAP
                t *= 1.0 + s._hjit(hx, hy, 400.0 + k) * JITTER_FRAC
                for ring in rings:
                    push((hx + dx * t * ring, hy + dy * t * ring))
        done = len(houses)

    segs_done = [0]
    MODE = os.environ.get("GROW", "tree")

    def own_reach(v: tuple[float, float]) -> float:
        """How far the new homestead's envelope reaches from its house's center toward the unit direction v."""
        w, e, nn, so = proto_box[0]
        return (e if v[0] > 0 else w) * abs(v[0]) + (so if v[1] > 0 else nn) * abs(v[1])

    def offer_along_tree() -> None:
        """ROUND 2 (FR-005, the path first): a seat beside every reserved corridor and the exit strip, on either side, its
        envelope's near edge a footpath's half-width (plus GAP) off the path - so its door's run onto the path is short and
        clear by construction - every `step` along the path, step the envelope's own width along it."""
        tree = getattr(s, "_access", None)
        if tree is None or not proto_box:
            return
        half = float(tree.half)
        for a, b in tree.segs[segs_done[0]:]:
            L = math.dist(a, b)
            if L < 1e-6:
                continue
            u = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
            nv = (-u[1], u[0])
            for side in (1.0, -1.0):
                m = (side * nv[0], side * nv[1])
                d = own_reach((-m[0], -m[1])) + half + GAP
                step = own_reach(u) + own_reach((-u[0], -u[1])) + GAP + float(os.environ.get("ROWGAP", "0")) * 2 * half
                phase = s._hjit(a[0], a[1], 500.0 + side) * step * JITTER_FRAC * 2
                k = 0
                while True:
                    tt = phase + k * step
                    if tt > L:
                        break
                    j = 1.0 + (s._hjit(a[0] + tt, a[1], 600.0 + side) - 0.5) * JITTER_FRAC
                    push((a[0] + u[0] * tt + m[0] * d * j, a[1] + u[1] * tt + m[1] * d * j))
                    k += 1
        segs_done[0] = len(tree.segs)

    proto_box: list[tuple[float, float, float, float]] = []

    offered = took = 0
    if not (s.M.get("houses") or []):
        # THE FIRST HOUSE: the free ground nearest the seat, in order, until one stands (the seat point itself is the
        # margin's center, often on the field's edge)
        seats = C.free_seats(s, (cx, cy))
        region = getattr(s, "_seat_region", None)
        if region is not None:
            seats = [q for q, ok in zip(seats, region.offer(seats), strict=True) if ok]
        placed, o1, t1 = C.offer_seats(s, seats, placed, placed + 1, C.DRY_SPELL)
        offered, took = o1, t1
        STATS.setdefault("first", []).append(o1)
        if not s.M.get("houses"):
            STATS.setdefault("margins", []).append((offered, took, placed))
            return placed
    while placed < want:
        if not proto_box and s.M.get("houses"):
            h0 = s.M["houses"][0]
            bx, by, bw, bh = h0["geom"]["bbox"]
            proto_box.append((float(h0["x"]) - (bx - bw / 2), (bx + bw / 2) - float(h0["x"]), float(h0["y"]) - (by - bh / 2), (by + bh / 2) - float(h0["y"])))
        if MODE in ("house", "both"):
            offer_around()
        if MODE in ("tree", "both"):
            offer_along_tree()
        if not proto and s.M.get("houses"):
            proto.append(footprint(s.M["houses"][0], s))
        if not heap:
            # DRY: widen the growth - every standing house offers again, more directions, farther rings
            if level[0] + 1 >= len(LEVELS):
                break
            level[0] += 1
            done = 0
            offer_around()
            if not heap:
                continue
        _, _, qx, qy = heapq.heappop(heap)
        if C._near_a_house(s, (qx, qy)):
            continue
        offered += 1
        s._seat_search["candidates"] += 1
        ok = s.try_place(qx, qy, "plain")
        STATS.setdefault("offers", []).append((qx, qy, bool(ok), LAST[0]))
        if ok:
            placed += 1
            took += 1
    STATS.setdefault("margins", []).append((offered, took, placed))
    if os.environ.get("PICTURE") and len(STATS["margins"]) == 1:
        picture(s, os.environ["PICTURE"])
    return placed


LAST: list[str] = [""]

COLORS = {"envelope": "#888", "house_box": "#c0c", "tree_reach": "#f00", "corridor": "#f80", "reach": "#08f", "wood_cover": "#0a0", "wood_share": "#060", "other": "#000"}


def picture(s: Any, out: str) -> None:
    """The first margin as grown: homestead boxes, yards, reserved corridors, wood seats, each offer colored by its refusal."""
    hs = s.M.get("houses") or []
    xs = [float(h["x"]) for h in hs] or [0.0]
    ys = [float(h["y"]) for h in hs] or [0.0]
    x0, y0, x1, y1 = min(xs) - 300, min(ys) - 300, max(xs) + 300, max(ys) + 300
    el = []
    fg = getattr(s, "_free_ground", None)
    if fg is not None:
        for gx in range(int(x0), int(x1), 8):
            for gy in range(int(y0), int(y1), 8):
                if fg.point_taken(gx, gy):
                    el.append(f'<rect x="{gx-4}" y="{gy-4}" width="8" height="8" fill="#ddd"/>')
    if hs:
        print("GEOM KEYS", sorted((hs[0].get("geom") or {}).keys()), "REC KEYS", sorted(hs[0].keys()), file=sys.stderr)
    for poly in s.field_polys or ():
        el.append('<polygon points="%s" fill="#cfe" stroke="none"/>' % " ".join(f"{p[0]:.0f},{p[1]:.0f}" for p in poly))
    for h in hs:
        g = h.get("geom") or {}
        for k, c in (("bbox", "none"),):
            bx, by, bw, bh = g.get(k) or (0, 0, 0, 0)
            el.append(f'<rect x="{bx-bw/2:.0f}" y="{by-bh/2:.0f}" width="{bw:.0f}" height="{bh:.0f}" fill="none" stroke="#999"/>')
        boxes = g.get("boxes") or {}
        for k, c in (("house", "#a52"), ("yard", "#fd8")):
            b = boxes.get(k)
            if b:
                el.append(f'<rect x="{b[0]-b[2]/2:.0f}" y="{b[1]-b[3]/2:.0f}" width="{b[2]:.0f}" height="{b[3]:.0f}" fill="{c}"/>')
        for p in (h.get("wood_share") or {}).get("seats") or ():
            el.append(f'<circle cx="{p[0]:.0f}" cy="{p[1]:.0f}" r="5" fill="#3a3" opacity="0.6"/>')
    tree = getattr(s, "_access", None)
    for a, b in (tree.segs if tree is not None else ()):
        el.append(f'<line x1="{a[0]:.0f}" y1="{a[1]:.0f}" x2="{b[0]:.0f}" y2="{b[1]:.0f}" stroke="#00f" stroke-width="4" opacity="0.5"/>')
    for x, y, ok, why in STATS.get("offers", []):
        c = "#0f0" if ok else COLORS.get(why, "#ff0")
        el.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="4" fill="{c}" stroke="#000" stroke-width="0.5"/>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.0f} {y0:.0f} {x1-x0:.0f} {y1-y0:.0f}" width="{(x1-x0)*1.2:.0f}" height="{(y1-y0)*1.2:.0f}"><rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="#fff"/>{"".join(el)}</svg>'
    open(out, "w").write(svg)


def trace() -> None:
    """TRACE=1: name the rule that refused each failed offer - the LAST refusing predicate asked inside it (each wrapper
    records its own refusal; `_parts_fit` short-circuits, so the last refusal is the deciding one)."""
    from l7r.diagram.settlement.homestead_parts import wood_share as WS
    from l7r.diagram.settlement.rolling import fit as F
    from l7r.diagram.settlement.rolling import place as P

    def wrap(owner: Any, name: str, tag: str, refused: Any) -> None:
        f = getattr(owner, name)

        def w(*a: Any, **k: Any) -> Any:
            r = f(*a, **k)
            if refused(r):
                LAST[0] = tag
            return r

        setattr(owner, name, w)

    wrap(Settlement, "_house_box_refused", "house_box", bool)
    wrap(P, "within_field_reach", "reach", lambda r: not r)
    wrap(Settlement, "_envelope_blocked", "envelope", lambda r: r is not None)
    wrap(P, "seat_reaches_tree", "tree_reach", lambda r: not r)
    wrap(WS.WoodShares, "covers_a_seat", "wood_cover", bool)
    wrap(WS.WoodShares, "share", "wood_share", lambda r: r is None)
    wrap(Settlement, "_sun_corridor_ok", "sun_corridor", lambda r: not r)
    wrap(Settlement, "_yard_sun_conflict", "yard_grove", bool)
    wrap(Settlement, "_gardens_sun_ok", "garden_sun", lambda r: not r)
    wrap(F, "access_corridor", "corridor", lambda r: r is None)
    wrap(Settlement, "_wall_on_the_bund", "bund", bool)
    wrap(F, "bundle_admitted", "admitted", lambda r: not r)
    wrap(Settlement, "_house_too_near_a_neighbor", "eave", bool)
    wrap(Settlement, "_house_unreachable", "unreachable", bool)
    wrap(Settlement, "_parts_across_stream", "stream", bool)
    tp = Settlement.try_place

    def counted(self: Any, *a: Any, **k: Any) -> Any:
        LAST[0] = "other"
        r = tp(self, *a, **k)
        if not r:
            STATS.setdefault("why", {}).setdefault(LAST[0], 0)
            STATS["why"][LAST[0]] += 1
        return r

    Settlement.try_place = counted  # type: ignore[method-assign]


def base_pictured(s: Any, plan: Any, placed: int) -> int:
    placed = BASE_REST(s, plan, placed)
    STATS.setdefault("margins", []).append((0, 0, placed))
    if os.environ.get("PICTURE") and len(STATS["margins"]) == 1:
        picture(s, os.environ["PICTURE"])
    return placed


def routed(s: Any, tree: Any, geom: Any) -> Any:
    """ROUND 5 (FR-005, the path laid back to the tree round what stands): where no straight corridor clears, a path ROUTED
    from a dooryard door over a grid of the open ground (Dijkstra, 8 neighbors, `ROUTE_STEP` px, within `ROUTE_R` px of the
    door) to the nearest point of the tree, then pulled taut - each leg the farthest node the engine's own leg tests admit
    (its house, fixtures, beds, the standing ground and the ways' ground test) - at most `ROUTE_LEGS` legs, no hairpin."""
    from l7r.diagram.settlement._geom import seg_closest, seg_dist
    from l7r.diagram.settlement.rolling import access as A

    step = float(os.environ.get("ROUTE_STEP", "10"))
    R = float(os.environ.get("ROUTE_R", "320"))
    maxlegs = int(os.environ.get("ROUTE_LEGS", "5"))
    half = float(tree.half)
    hgap = A.house_gap(s)
    memo = A._standing_memo(s)[1]
    fg = getattr(s, "_free_ground", None)
    wood = getattr(s, "_wood", None)
    own = (geom.get("boxes") or {}).get("house") or geom["house"]
    idx = s._reach_index(s.placed, "placed_reach")

    def leg_ok(a: Any, b: Any) -> bool:
        return A.house_clear(a, b, geom, hgap) and A.fixtures_clear(s, a, b, geom) and A.parts_clear(s, a, b, geom) and A.standing_ground(s, a, b, memo) and A.lawful_leg(s, a, b, memo)

    for door in A.doors_of(geom, half)[:2]:
        if (door, "routed") in memo:
            got = memo[(door, "routed")]
            if got is not None:
                yield got
            continue
        memo[(door, "routed")] = None
        x0, y0 = door

        def free(i: int, j: int) -> bool:
            x, y = x0 + i * step, y0 + j * step
            if fg is not None and fg.point_taken(x, y):
                return False
            if A.seg_box_within((x, y), (x, y), own, hgap) and (i, j) != (0, 0):
                return False
            for it in idx.near(x, y, half + 60):
                if A.seg_box_within((x, y), (x, y), (it[0], it[1], it[2], it[3]), half):
                    return False
            return not (wood is not None and wood.corridor_bars((x, y), (x, y)))

        def goal(i: int, j: int) -> Any:
            x, y = x0 + i * step, y0 + j * step
            for a, b, *_ in tree.grid.near(x, y, step + half):
                if seg_dist(x, y, a, b) <= step:
                    return seg_closest(x, y, a, b)
            return None

        aims = [((q[0] - x0) / step, (q[1] - y0) / step) for q in tree.targets(door)] or [(0.0, 0.0)]
        W = float(os.environ.get("ROUTE_W", "1.5"))

        def h(c: Any) -> float:
            return W * min(math.hypot(c[0] - a[0], c[1] - a[1]) for a in aims)

        dist = {(0, 0): 0.0}
        prev: dict[Any, Any] = {}
        heap = [(h((0, 0)), (0, 0))]
        okc: dict[Any, bool] = {}
        end = None
        n = int(R / step)
        while heap:
            f, c = heapq.heappop(heap)
            d = dist[c]
            if f > d + h(c) + 1e-9:
                continue
            q = goal(*c)
            if q is not None and c != (0, 0):
                end = (c, q)
                break
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    if di == dj == 0:
                        continue
                    nc = (c[0] + di, c[1] + dj)
                    if abs(nc[0]) > n or abs(nc[1]) > n:
                        continue
                    if nc not in okc:
                        okc[nc] = free(*nc)
                    if not okc[nc]:
                        continue
                    nd = d + math.hypot(di, dj)
                    if nd < dist.get(nc, 1e18):
                        dist[nc] = nd
                        prev[nc] = c
                        heapq.heappush(heap, (nd + h(nc), nc))
        STATS["routes"] = STATS.get("routes", 0) + 1
        if end is None:
            continue
        cells = [end[0]]
        while cells[-1] != (0, 0):
            cells.append(prev[cells[-1]])
        pts = [(x0 + i * step, y0 + j * step) for i, j in reversed(cells)] + [end[1]]
        pts[0] = door
        out = [door]
        k = 0
        while k < len(pts) - 1 and len(out) <= maxlegs + 1:
            far = None
            for m in range(len(pts) - 1, k, -1):
                if leg_ok(pts[k], pts[m]) and (len(out) < 2 or not A.doubles_back(out[-2], out[-1], pts[m])):
                    far = m
                    break
            if far is None:
                break
            out.append(pts[far])
            k = far
        if k == len(pts) - 1 and len(out) <= maxlegs + 1:
            got = tuple(out)
            memo[(door, "routed")] = got
            STATS["routed_ok"] = STATS.get("routed_ok", 0) + 1
            yield got


def route() -> None:
    from l7r.diagram.settlement.rolling import access as A

    base = A._house_candidates

    def cands(s: Any, tree: Any, geom: Any) -> Any:
        yield from base(s, tree, geom)
        yield from routed(s, tree, geom)

    A._house_candidates = cands


def use(mode: str) -> None:
    if os.environ.get("ROUTE"):
        route()
    if os.environ.get("TRACE"):
        trace()
    if mode == "base":
        ST.seat_the_rest = base_pictured
    if mode == "grow":
        from l7r.diagram.settlement import Settlement as _S

        ST.front_row = lambda *a, **k: []
        _S.cluster_seeds = lambda self, *a, **k: []
        ST.seat_the_rest = grow


def run(households: int, seed: int) -> tuple[float, int, int, int]:
    STATS.clear()
    with beyond_the_band():
        plan = plan_site(HamletSpec(seed=seed, households=households, **REF))
    s = Settlement(W=plan.W, H=plan.H, seed=seed)
    calls = [0]
    tp = s.try_place

    def counted(*a: Any, **k: Any) -> Any:
        calls[0] += 1
        return tp(*a, **k)

    s.try_place = counted  # type: ignore[method-assign]
    took = 0.0
    with roll_scope(plan.spec):
        for st in STAGES:
            t0 = time.perf_counter()
            with redirect_stdout(io.StringIO()):
                st(s, plan)
            if st.__name__ == "stage_homesteads":
                took = time.perf_counter() - t0
                if not os.environ.get("FULL"):
                    break
    return took, int(s.M["meta"].get("seat_margin", 0)), calls[0], len(s.M.get("houses") or [])


if __name__ == "__main__":
    mode, h = sys.argv[1], int(sys.argv[2])
    use(mode)
    for seed in [int(x) for x in sys.argv[3].split(",")]:
        try:
            t, rung, offers, houses = run(h, seed)
            print(f"{mode} hh={h} seed={seed}: homesteads={t:.2f}s rung={rung} offers={offers} houses={houses} per-margin={STATS.get('margins')} why={STATS.get('why')} routes={STATS.get('routes')}/{STATS.get('routed_ok')}", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"{mode} hh={h} seed={seed}: {type(e).__name__} {str(e)[:80]} first={STATS.get('first', [])[:6]} per-margin={STATS.get('margins', [])[:6]} why={STATS.get('why')}", flush=True)
