"""Split from settlement/structures/fixtures.py by feature 173 - see this package's CLAUDE.md for the index.

Research: board-siting plumbing - NONE: walks, joins, routes and their indexes
"""

import math
from collections.abc import Callable, Sequence
from typing import Any

from ..._geom import (
    PointGrid,
    seg_closest,
    seg_dist,
    seg_reach_index,
)

# The lane clearance `place_kosatsuba` asks of the caption room beside a candidate board seat - a SITING heuristic
# (is there room for a caption here?), not a caption seat: the caption itself is seated by the one placer
# (feature 266), which scores a lane crossed within the gate's 2 ft notch at Esri's way weight.
CAPTION_LANE_TARGET_FT = 3.0
"""Research: caption room beside a board - CONVENTION: 3 ft lane clearance for the caption probe"""

# THE BOARD IS ROADSIDE (GM 2026-08-26, feature 133 T13: *"I would expect it to be essentially
# roadside ... puts it right next to one of the village lanes"*). Real feet from the tread's EDGE to
# the board's near edge. Research (research/contents.json#trades-and-services): the kosatsu stood where traffic
# passed - the village entrance, the roadside, a crossroads, a bridgehead, the headman's gate - so a
# board 24 ft off its lane (Inashiro before this) is set back from the very thing it is for. The
# placer searched out to 60 ft and ranked caption clearance above nearness, which is how it walked
# out. Now: at the hamlet and village tiers only seats inside this band are eligible when any fits
# (the 60 ft band remains the fallback, and `kosatsuba_by_the_road` tightens to this band at those
# tiers); towns and cities keep the 60 ft rule until their pool maps are re-rolled at unlock.
KOSATSUBA_VERGE_FT = 6.0
"""Research: board at the roadside - research/questions/0190-notice-boards-kosatsuba.drawing.html: 6 ft from the tread's edge at a hamlet or village"""

KOSATSUBA_ENTRANCE_REACH_FT = 100.0
"""How near a dwelling the approach must come before it counts as having ARRIVED at the settlement.

THE ENTRANCE IS THE FIRST BUILDINGS, NOT A RADIUS (settlement-review, feature 154). The first version
measured arrival against the cluster's own reach - the greatest distance from any house to the house
centroid - which is isotropic, and a settlement is not. On Sawada, a ribbon cluster of drawn aspect
4.06, that radius is set by the ribbon's HALF-LENGTH: 382 ft. The approach crossed that circle 148 ft
from the nearest house, out in the woodland and 3 ft above the top edge of the drawn sheet, so the
board was sited off the page, `stage_notice`'s frame guard threw the seat away, and the map recorded
an `entrance` placement it had not drawn.

100 ft is not a new figure: it is the reach `farmhouses_reach_a_way` uses to decide whether a dwelling
is served by a way at all. Where the approach first comes within serving distance of a house is where
a walker would say the hamlet begins, and it is the same measure the rest of the engine already makes.

Research: where the settlement begins - UNRESEARCHED: the approach within 100 ft of a dwelling"""

KOSATSUBA_ANCHOR_BAND_FT = 60.0
"""How far from the best seat at an anchored placement another seat may stand and still compete.

Not a new figure: it is `place_kosatsuba`'s own siting band, the ~60 real feet within which a board
counts as belonging to the way it stands on (`kosatsuba_by_the_road`'s fallback tolerance). Reused
here so an anchored placement admits the seats that genuinely front the entrance or the gate, and no
others, and then hands the choice to the caption and roadside preferences that already existed.
Making it TIGHTER would let a caption-blocked seat win on a foot of proximity; making it LOOSER would
let the traffic term drag the board off the anchor, which is the defect this feature exists to fix.

Research: anchored siting band - UNRESEARCHED: 60 ft from the best seat, the board's siting distance reused"""


def kosatsuba_affordances(M: Any) -> dict[str, bool]:
    """Which board placements this map can SITE, read from the manifest the validator reads.

    The same-source doctrine: a guard against a placement asks the question the checks ask. An
    approach is a recorded road or a connector track; an official's gate is a house carrying
    `role == "headman"`, which every pool VILLAGE records exactly once and no hamlet records at all.
    """
    lanes = M.get("lanes") or []
    has_approach = bool(M.get("road") or (M.get("roads") or []) or any(ln.get("connector") for ln in lanes))
    return {
        "has_approach": has_approach,
        "has_headman_house": any(h.get("role") == "headman" for h in (M.get("houses") or [])),
    }


KOSATSUBA_HANDOVER_PX = 6.0
"""How near another way's recorded point the connector's inner end must lie to count as handing over to it: the router
joins a way to the web at a shared vertex, so a true handover is a coincident point, and 6 px allows for the rounding a
manifest applies to its coordinates."""


KOSATSUBA_HANDOVER_BAND_FT = 20.0
"""How far from the connector's handover an `entrance` board may stand. Every departure ends its walk through the lanes
at the handover, so a board beside it is passed by all of them; the wider anchor band let the caption and structure
preferences carry the board 70-100 ft off it, onto a lane two of Kashikawa's households and one of Sawada's never took
(feature 261). 20 ft is the board's own verge off the tread plus a board's length either way along it.

Research: entrance board beside the handover - UNRESEARCHED: within 20 ft of where every departure passes"""


DWELLING_REACH_FT = 150.0
"""How far from a way a dwelling may stand and still be walked out by it - `departure_routes`' `reach`, one number for
both, so the entrance and the routes it must be passed by cannot disagree.

Research: dwelling served by a way - UNRESEARCHED: within 150 ft"""


def dwellings_joining(M: Any, track: Sequence[tuple[float, float]], houses: Sequence[tuple[float, float]]) -> list[tuple[float, float]]:
    """Where each dwelling whose nearest way is `track` itself joins it - the point of `track` nearest the house, for every
    house within `DWELLING_REACH_FT` of it and nearer it than to any other way (feature 291). A LINEAR village's roadside
    farm steps straight onto the track out with no lane of its own; found on Mizuguchi once it rolled linear: one farm
    joined the track about 200 ft out beyond the lanes' handover, so no seat by the handover was passed by its departure."""
    if len(track) < 2:
        return []
    others = [
        [(float(x), float(y)) for x, y in (ln.get("pts") or [])]
        for ln in (M.get("lanes") or [])
        if len(ln.get("pts") or []) >= 2 and [(float(x), float(y)) for x, y in ln["pts"]] not in (list(track), list(track)[::-1])
    ]
    out = []
    for hx, hy in houses:
        on = min((seg_closest(hx, hy, a, b) for a, b in zip(track, track[1:], strict=False)), key=lambda q: math.hypot(q[0] - hx, q[1] - hy))
        d = math.hypot(on[0] - hx, on[1] - hy)
        if d > DWELLING_REACH_FT:
            continue
        if any(seg_dist(hx, hy, a, b) < d for o in others for a, b in zip(o, o[1:], strict=False)):
            continue
        out.append(on)
    return out


def first_join(track: Sequence[tuple[float, float]], joins: Sequence[tuple[float, float] | None]) -> tuple[float, float] | None:
    """Of `joins` (points on `track`, None skipped), the one met first walking `track` from its first vertex."""

    def along(q: tuple[float, float]) -> float:
        best, acc = (math.inf, 0.0), 0.0
        for a, b in zip(track, track[1:], strict=False):
            c = seg_closest(q[0], q[1], a, b)
            d = math.hypot(c[0] - q[0], c[1] - q[1])
            if d < best[0]:
                best = (d, acc + math.dist(a, c))
            acc += math.dist(a, b)
        return best[1]

    found = [q for q in joins if q is not None]
    return min(found, key=along) if found else None


def outermost_join(track: Sequence[tuple[float, float]], others: Sequence[Sequence[tuple[float, float]]], step: float = 5.0) -> tuple[float, float] | None:
    """The first point of `track`, walked from its first vertex, that another way comes within `KOSATSUBA_HANDOVER_PX` of -
    where the last way out joins it - or None when none does (feature 261).

    The other ways' segments are INDEXED once (feature 281, FR-004): each 5 ft sample walked every segment of every way -
    209,131 `seg_dist` on Sawada. A sample farther than the reach from a segment's box is farther than the reach from the
    segment, so the segments whose box widened by the reach holds the sample are every one the test can accept; the reach
    is padded by 1e-6 so a way at EXACTLY the reach, which the closed test accepts, stays inside its widened box."""
    index = seg_reach_index([(o, 0.0) for o in others], KOSATSUBA_HANDOVER_PX + 1e-6)
    for a, b in zip(track, track[1:], strict=False):
        n = max(1, int(math.dist(a, b) // step))
        for i in range(n + 1):
            q = (a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n)
            if any(x0 <= q[0] <= x1 and y0 <= q[1] <= y1 and seg_dist(q[0], q[1], c, d) <= KOSATSUBA_HANDOVER_PX for c, d, _r, x0, y0, x1, y1 in index.near(q[0], q[1])):
                return q
    return None


def kosatsuba_handover(M: Any) -> tuple[float, float] | None:
    """Where a hamlet's connector hands over to its lanes - the connector's end nearest the dwellings, when another way
    meets it there - or None (no connector, no dwellings, or a connector that runs on through the houses meeting none).

    Research:
        entrance is the handover - research/questions/0190-notice-boards-kosatsuba.html: the board at the village entrance, read as the last join on the way out
        a through track's handover - research/questions/0190-notice-boards-kosatsuba.html: the entrance placement's anchor (the center or the entrance is rolled per settlement by the `kosatsuba_seat` knob, `board_seat.resolve_seat`) - where both its ends are off the sheet, the lane end joining it nearest the houses' middle"""
    houses = [(float(h["x"]), float(h["y"])) for h in (M.get("houses") or []) if "x" in h]
    if not houses:
        return None
    _others = [[(float(x), float(y)) for x, y in (ln.get("pts") or [])] for ln in (M.get("lanes") or []) if not ln.get("connector")]
    for ln in M.get("lanes") or []:
        pts = [(float(x), float(y)) for x, y in (ln.get("pts") or [])]
        if not ln.get("connector") or ln.get("run_on") or len(pts) < 2:  # a row street's far run is the road going on, not the way in
            continue
        inner = min((pts[0], pts[-1]), key=lambda q: min(math.hypot(q[0] - h[0], q[1] - h[1]) for h in houses))
        # a way meets it at a shared vertex or anywhere along a segment - the router joins at either
        # ...OR THE TRACK STARTS AT THE GATE THE HOUSEHOLDS' WAYS WERE LAID TO (feature 320, `way_out_gate`): they join it along
        # its stretch by the cluster, none need meet its inner end, and the through-track branch below then took the join
        # nearest the houses - the innermost, which the ways joining farther out never pass (11 of 16 bookend runs lost
        # their entrance board, perf-audit 2026-10-04)
        if M.get("way_out_gate") or any(seg_dist(inner[0], inner[1], a, b) <= KOSATSUBA_HANDOVER_PX for o in _others for a, b in zip(o, o[1:], strict=False)):
            # ...AND THE ENTRANCE IS THE LAST JOIN ON THE WAY OUT, not the inner end (settlement-review of Inashiro, feature
            # 261): a household's own short lane met the track 190 ft below the inner end, so it left without passing a board
            # seated there. Walked in from the outer end, the first point a way meets is where every departure has joined
            walk = pts if inner == pts[-1] else pts[::-1]
            return first_join(walk, [outermost_join(walk, _others), *dwellings_joining(M, walk, houses)]) or inner
        # ...AND A TRACK THAT RUNS THROUGH hands over where a lane's END meets it (settlement-review of Mizuguchi): both of
        # its ends are off the sheet, so its "inner end" meets nothing; the junction nearest the houses is where the lanes
        # reach the way out
        cx, cy = sum(h[0] for h in houses) / len(houses), sum(h[1] for h in houses) / len(houses)
        joins = [q for o in _others if len(o) >= 2 for q in (o[0], o[-1]) if any(seg_dist(q[0], q[1], a, b) <= KOSATSUBA_HANDOVER_PX for a, b in zip(pts, pts[1:], strict=False))]
        if joins:
            return min(joins, key=lambda q: math.hypot(q[0] - cx, q[1] - cy))
    return None


def kosatsuba_anchor(M: Any, placement: str) -> tuple[float, float] | None:
    """The point an anchored placement is measured to, or None when the placement is not anchored.

    `center` returns None ON PURPOSE, and that is the whole reason this function has a null case: the
    settlement center IS the traffic objective - *"the village center ... or the place where villagers
    assembled"* - which `place_kosatsuba` already computes by counting dwellings around each seat, far
    better than a centroid would. Returning the centroid here would replace a measure of where people
    ARE with a measure of where the middle IS, and on a crescent or a ribbon cluster those are not the
    same point. So `center` keeps today's behavior byte for byte, and only the two placements that
    need a landmark get one.

    `entrance` is where the connector hands over to the lanes (`kosatsuba_handover`, feature 261) - every departure
    passes that junction. Where the connector meets no other way, it is the MOUTH, not the nearest point: the approach
    is walked from its far end inward and the anchor is where it first reaches the cluster. Taking the nearest point instead would put the
    anchor at the deepest point of the track's run past the houses, i.e. inside the settlement, which
    is the opposite of an entrance.

    Research:
        board placements - research/questions/0190-notice-boards-kosatsuba.html: center, entrance, or the headman's gate (frontage)
        entrance anchor - research/questions/0190-notice-boards-kosatsuba.html: the handover, else where the approach first reaches a dwelling
        reaching the houses - UNRESEARCHED: the approach counts as reaching them within `KOSATSUBA_ENTRANCE_REACH_FT`, 100 ft of a dwelling
    """
    houses = [(float(h["x"]), float(h["y"])) for h in (M.get("houses") or []) if "x" in h]
    if not houses or placement == "center":
        return None
    if placement == "frontage":
        gate = next((h for h in (M.get("houses") or []) if h.get("role") == "headman" and "x" in h), None)
        return (float(gate["x"]), float(gate["y"])) if gate else None

    def _at_the_buildings(q: tuple[float, float]) -> bool:
        """Has the approach arrived? Measured to the nearest DWELLING, never to a centroid radius."""
        return min(math.hypot(q[0] - h[0], q[1] - h[1]) for h in houses) <= KOSATSUBA_ENTRANCE_REACH_FT

    # THE HANDOVER, WHERE THERE IS ONE (feature 261, settlement-review of Kashikawa and Sawada). A hamlet's connector is
    # its only way out, and it hands over to the lanes at its inner end: every departure passes that junction and no
    # other point. The first-arrival walk below anchored the board where the track first came within reach of a house,
    # and the board then stood on whichever lane was nearest THERE - on Kashikawa two households and on Sawada one left
    # by a lane that never passed it. So where the connector's inner end meets another way, that junction is the
    # entrance; a connector that meets nothing (a track running on through the houses) is still walked.
    _handover = kosatsuba_handover(M)
    if _handover is not None:
        return _handover
    runs: list[list[tuple[float, float]]] = []
    if M.get("road"):
        runs.append([(float(p[0]), float(p[1])) for p in M["road"]])
    runs += [[(float(p[0]), float(p[1])) for p in (r.get("pts") or [])] for r in (M.get("roads") or [])]
    runs += [[(float(x), float(y)) for x, y in (ln.get("pts") or [])] for ln in (M.get("lanes") or []) if ln.get("connector") and not ln.get("run_on")]
    best: tuple[float, tuple[float, float]] | None = None
    for run in runs:
        if len(run) < 2:
            continue
        # walk from whichever end is FURTHER out, so "first reach" means arriving rather than leaving
        _far = min(math.hypot(run[0][0] - h[0], run[0][1] - h[1]) for h in houses)
        _near = min(math.hypot(run[-1][0] - h[0], run[-1][1] - h[1]) for h in houses)
        walk = run if _far >= _near else run[::-1]
        # SAMPLED ALONG THE SEGMENTS, NOT AT THE VERTICES. A track is recorded with as few points as
        # its shape needs, so one that runs straight through the cluster can have no vertex inside it
        # at all - the first version of this tested vertices and returned "no entrance" for a
        # two-point track passing right through the houses, caught by its own unit test rather than by
        # a map, because the pool's connectors happen to be densely recorded.
        acc = 0.0
        for u, v in zip(walk, walk[1:], strict=False):
            seg = math.dist(u, v)
            steps = max(1, int(seg / 5.0))
            for k in range(1, steps + 1):
                q = (u[0] + (v[0] - u[0]) * k / steps, u[1] + (v[1] - u[1]) * k / steps)
                if _at_the_buildings(q) and (best is None or acc + seg * k / steps < best[0]):
                    best = (acc + seg * k / steps, q)
                    break
            if best is not None:
                break
            acc += seg
    if best is None and runs:
        # ...AND AN APPROACH THAT STOPS SHORT STILL HAS AN ENTRANCE (feature 261, settlement-review of Mizuguchi): a
        # connector that hands over to the lanes more than `KOSATSUBA_ENTRANCE_REACH_FT` from the nearest dwelling never
        # "arrives", and the entrance board fell back to the traffic objective and stood on a lane most departures never
        # use. Where the approach does not reach the buildings, its entrance is its point nearest them - the handover.
        _pts = [p for run in runs if len(run) >= 2 for p in run]
        if _pts:
            return min(_pts, key=lambda q: min(math.hypot(q[0] - h[0], q[1] - h[1]) for h in houses))
    return best[1] if best else None


def departure_routes(M: Any, step: float = 10.0, join: float = 7.0, reach: float = DWELLING_REACH_FT) -> list[list[tuple[float, float]]]:
    """Every household's way OUT, as the points it walks (feature 261 FR-015: an entrance board stands where every
    departure passes it). The drawn lanes are sampled every `step` into a graph whose samples within `join` of each other
    are one junction; each dwelling's nearest sample within `reach` walks the shortest route through them to the connector's
    OUTER end (settlement-review of Inashiro: routed to the handover first and then out, a lane that met the track below the
    handover was walked up to it and back, and every route passed a board there by construction). Empty when the map has
    no handover."""
    import heapq

    hand = kosatsuba_handover(M)
    if hand is None:
        return []
    nodes: list[tuple[float, float]] = []
    edges: dict[int, list[tuple[int, float]]] = {}
    for ln in M.get("lanes") or []:
        pts = [(float(x), float(y)) for x, y in (ln.get("pts") or [])]
        prev: int | None = None
        for a, b in zip(pts, pts[1:], strict=False):
            n = max(1, int(math.dist(a, b) // step))
            for i in range(n + 1):
                q = (a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n)
                nodes.append(q)
                j = len(nodes) - 1
                edges[j] = []
                if prev is not None:
                    d = math.dist(nodes[prev], q)
                    edges[prev].append((j, d))
                    edges[j].append((prev, d))
                prev = j
    grid: dict[tuple[int, int], list[int]] = {}
    for i, q in enumerate(nodes):
        grid.setdefault((int(q[0] // join), int(q[1] // join)), []).append(i)
    for i, q in enumerate(nodes):
        gx, gy = int(q[0] // join), int(q[1] // join)
        for j in (j for dx in (-1, 0, 1) for dy in (-1, 0, 1) for j in grid.get((gx + dx, gy + dy), ())):
            if j > i and math.dist(q, nodes[j]) < join:
                edges[i].append((j, 0.0))
                edges[j].append((i, 0.0))
    houses = [(float(h["x"]), float(h["y"])) for h in M.get("houses") or [] if "x" in h]
    ends = [
        q
        for ln in M.get("lanes") or []
        if ln.get("connector") and not ln.get("run_on") and len(ln.get("pts") or []) >= 2
        for q in ((float(ln["pts"][0][0]), float(ln["pts"][0][1])), (float(ln["pts"][-1][0]), float(ln["pts"][-1][1])))
    ]
    outer = max(ends, key=lambda q: min(math.dist(q, h) for h in houses)) if ends and houses else hand
    src = min(range(len(nodes)), key=lambda i: math.dist(nodes[i], outer))
    dist, back = {src: 0.0}, {src: -1}
    heap = [(0.0, src)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in edges[u]:
            if d + w < dist.get(v, math.inf):
                dist[v], back[v] = d + w, u
                heapq.heappush(heap, (d + w, v))
    routes: list[list[tuple[float, float]]] = []
    reached = list(dist)
    at = reached_at(nodes, reached)
    for h in M.get("houses") or []:
        s = nearest_of(nodes, reached, at, (float(h["x"]), float(h["y"])))
        if math.dist(nodes[s], (float(h["x"]), float(h["y"]))) > reach:
            continue
        path: list[tuple[float, float]] = []
        while s != -1:
            path.append(nodes[s])
            s = back[s]
        routes.append(path)
    return routes


def reached_at(nodes: Sequence[tuple[float, float]], among: Sequence[int]) -> Any:
    """The nodes `among` names, in its order, as one (n, 2) array for `nearest_of`.

    Research: plumbing - NONE: lane samples as an array"""
    import numpy as np

    return np.asarray([nodes[i] for i in among], dtype=float).reshape(-1, 2)


def nearest_of(nodes: Sequence[tuple[float, float]], among: Sequence[int], at: Any, q: tuple[float, float]) -> int:
    """The first of `among` (indices into `nodes`, in their order; `at` their points, `reached_at`) whose node lies nearest
    `q` by `math.dist` - what `min(among, key=...)` answers, the distances taken at once by numpy and only the near-ties
    (within 1e-6 ft of the least, far more than numpy's rounding) asked again exactly, so every node `math.dist` puts nearest
    is among them and the first is the same (the perf-audit of feature 328: 448,320 `math.dist` calls a 40-household knot
    step).

    Research: plumbing - NONE: a dwelling's nearest lane sample, the same answer"""
    import numpy as np

    d = np.hypot(at[:, 0] - q[0], at[:, 1] - q[1])
    near = np.flatnonzero(d <= d.min() + 1e-6)
    return min((among[int(k)] for k in near), key=lambda i: math.dist(nodes[i], q))


def routes_missed(routes: Sequence[Sequence[tuple[float, float]]], x: float, y: float, near: float) -> int:
    """How many of `routes` never come within `near` of (x, y) - the departures that do not pass a board there. A caller
    asking of many seats builds one `RouteReach` instead."""
    return RouteReach(routes).missed(x, y, near)


class RouteReach:
    """Every route's points filed ONCE, for asking of many candidate seats how many routes pass none of them within reach
    (feature 281, FR-004). `routes_missed` walked every point of every route per seat - 724,209 `hypot` on Sawada's
    notice board - though the routes do not change while the seats are scored. A point is filed by its own position, so
    `near(x, y, reach)` returns every point within the reach (and some beyond), and the same
    `math.hypot(q[0] - x, q[1] - y) <= near` decides which routes it reaches."""

    __slots__ = ("grid", "n")

    def __init__(self, routes: Sequence[Sequence[tuple[float, float]]]) -> None:
        self.n = len(routes)
        self.grid = PointGrid(cell=32.0)
        self.grid.extend((k, float(q[0]), float(q[1]), float(q[0]), float(q[1]), float(q[0]), float(q[1])) for k, r in enumerate(routes) for q in r)

    def missed(self, x: float, y: float, near: float) -> int:
        """`routes_missed(routes, x, y, near)`, exactly."""
        passed = {k for k, qx, qy, *_box in self.grid.near(x, y, near) if math.hypot(qx - x, qy - y) <= near}
        return self.n - len(passed)


CAPTION_HALO_FT = 1.5  # the caption's background halo, drawn past its box (`label()`'s stroke) - what notches a crown
"""Research: caption halo - CONVENTION: 1.5 ft"""


def quad_on_canopy(quad: Sequence[tuple[float, float]], near: Callable[[float, float, float], Any]) -> bool:
    """Does a caption DRAWN as `quad` - with its halo - lie on any tree crown? `near(x, y, pad)` returns the crowns (x, y,
    r, ...) whose boxes come within `pad` of a point (a `canopy_index` grid's `near`). The drawn shape against the drawn
    crowns (feature 261, settlement-review of Kuwabata): the old test asked whether the caption's CENTER stood within a
    radius of a crown, a stand-in for a 53 ft caption whose ends can lie in trees while its middle is clear.

    Research: caption off the canopy - CONVENTION: the drawn caption and halo against the drawn crowns"""
    from ..._geom import point_in_poly, seg_dist

    cx, cy = sum(p[0] for p in quad) / len(quad), sum(p[1] for p in quad) / len(quad)
    reach = max(math.dist((cx, cy), p) for p in quad) + CAPTION_HALO_FT
    for it in near(cx, cy, reach):
        x, y, r = float(it[0]), float(it[1]), float(it[2])
        if point_in_poly(x, y, list(quad)) or min(seg_dist(x, y, a, b) for a, b in zip(quad, [*quad[1:], quad[0]], strict=False)) < r + CAPTION_HALO_FT:
            return True
    return False
