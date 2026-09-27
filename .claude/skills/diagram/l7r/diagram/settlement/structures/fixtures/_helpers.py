"""Split from settlement/structures/fixtures.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
from collections.abc import Callable, Sequence
from typing import Any

from ..._geom import (
    seg_dist,
)

# The lane clearance `place_kosatsuba` asks of the caption room beside a candidate board seat - a SITING heuristic
# (is there room for a caption here?), not a caption seat: the caption itself is seated by the one placer
# (feature 266), which scores a lane crossed within the gate's 2 ft notch at Esri's way weight.
CAPTION_LANE_TARGET_FT = 3.0

# THE BOARD IS ROADSIDE (GM 2026-08-26, feature 133 T13: *"I would expect it to be essentially
# roadside ... puts it right next to one of the village lanes"*). Real feet from the tread's EDGE to
# the board's near edge. Research (research/urban-features.html): the kosatsu stood where traffic
# passed - the village entrance, the roadside, a crossroads, a bridgehead, the headman's gate - so a
# board 24 ft off its lane (Inashiro before this) is set back from the very thing it is for. The
# placer searched out to 60 ft and ranked caption clearance above nearness, which is how it walked
# out. Now: at the hamlet and village tiers only seats inside this band are eligible when any fits
# (the 60 ft band remains the fallback, and `kosatsuba_by_the_road` tightens to this band at those
# tiers); towns and cities keep the 60 ft rule until their pool maps are re-rolled at unlock.
KOSATSUBA_VERGE_FT = 6.0

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
a walker would say the hamlet begins, and it is the same measure the rest of the engine already makes."""

KOSATSUBA_ANCHOR_BAND_FT = 60.0
"""How far from the best seat at an anchored placement another seat may stand and still compete.

Not a new figure: it is `place_kosatsuba`'s own siting band, the ~60 real feet within which a board
counts as belonging to the way it stands on (`kosatsuba_by_the_road`'s fallback tolerance). Reused
here so an anchored placement admits the seats that genuinely front the entrance or the gate, and no
others, and then hands the choice to the caption and roadside preferences that already existed.
Making it TIGHTER would let a caption-blocked seat win on a foot of proximity; making it LOOSER would
let the traffic term drag the board off the anchor, which is the defect this feature exists to fix."""


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
(feature 261). 20 ft is the board's own verge off the tread plus a board's length either way along it."""


def outermost_join(track: Sequence[tuple[float, float]], others: Sequence[Sequence[tuple[float, float]]], step: float = 5.0) -> tuple[float, float] | None:
    """The first point of `track`, walked from its first vertex, that another way comes within `KOSATSUBA_HANDOVER_PX` of -
    where the last way out joins it - or None when none does (feature 261)."""
    for a, b in zip(track, track[1:], strict=False):
        n = max(1, int(math.dist(a, b) // step))
        for i in range(n + 1):
            q = (a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n)
            if any(seg_dist(q[0], q[1], c, d) <= KOSATSUBA_HANDOVER_PX for o in others for c, d in zip(o, o[1:], strict=False)):
                return q
    return None


def kosatsuba_handover(M: Any) -> tuple[float, float] | None:
    """Where a hamlet's connector hands over to its lanes - the connector's end nearest the dwellings, when another way
    meets it there - or None (no connector, no dwellings, or a connector that runs on through the houses meeting none)."""
    houses = [(float(h["x"]), float(h["y"])) for h in (M.get("houses") or []) if "x" in h]
    if not houses:
        return None
    _others = [[(float(x), float(y)) for x, y in (ln.get("pts") or [])] for ln in (M.get("lanes") or []) if not ln.get("connector")]
    for ln in M.get("lanes") or []:
        pts = [(float(x), float(y)) for x, y in (ln.get("pts") or [])]
        if not ln.get("connector") or len(pts) < 2:
            continue
        inner = min((pts[0], pts[-1]), key=lambda q: min(math.hypot(q[0] - h[0], q[1] - h[1]) for h in houses))
        # a way meets it at a shared vertex or anywhere along a segment - the router joins at either
        if any(seg_dist(inner[0], inner[1], a, b) <= KOSATSUBA_HANDOVER_PX for o in _others for a, b in zip(o, o[1:], strict=False)):
            # ...AND THE ENTRANCE IS THE LAST JOIN ON THE WAY OUT, not the inner end (settlement-review of Inashiro, feature
            # 261): a household's own short lane met the track 190 ft below the inner end, so it left without passing a board
            # seated there. Walked in from the outer end, the first point a way meets is where every departure has joined
            return outermost_join(pts if inner == pts[-1] else pts[::-1], _others) or inner
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

    `entrance` is the MOUTH, not the nearest point: the approach is walked from its far end inward and
    the anchor is where it first reaches the cluster. Taking the nearest point instead would put the
    anchor at the deepest point of the track's run past the houses, i.e. inside the settlement, which
    is the opposite of an entrance.
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
    runs += [[(float(x), float(y)) for x, y in (ln.get("pts") or [])] for ln in (M.get("lanes") or []) if ln.get("connector")]
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


def departure_routes(M: Any, step: float = 10.0, join: float = 7.0, reach: float = 150.0) -> list[list[tuple[float, float]]]:
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
        if ln.get("connector") and len(ln.get("pts") or []) >= 2
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
    for h in M.get("houses") or []:
        s = min(dist, key=lambda i: math.dist(nodes[i], (float(h["x"]), float(h["y"]))))
        if math.dist(nodes[s], (float(h["x"]), float(h["y"]))) > reach:
            continue
        path: list[tuple[float, float]] = []
        while s != -1:
            path.append(nodes[s])
            s = back[s]
        routes.append(path)
    return routes


def routes_missed(routes: Sequence[Sequence[tuple[float, float]]], x: float, y: float, near: float) -> int:
    """How many of `routes` never come within `near` of (x, y) - the departures that do not pass a board there."""
    return sum(1 for r in routes if not any(math.hypot(q[0] - x, q[1] - y) <= near for q in r))


CAPTION_HALO_FT = 1.5  # the caption's background halo, drawn past its box (`label()`'s stroke) - what notches a crown


def quad_on_canopy(quad: Sequence[tuple[float, float]], near: Callable[[float, float, float], Any]) -> bool:
    """Does a caption DRAWN as `quad` - with its halo - lie on any tree crown? `near(x, y, pad)` returns the crowns (x, y,
    r, ...) whose boxes come within `pad` of a point (a `canopy_index` grid's `near`). The drawn shape against the drawn
    crowns (feature 261, settlement-review of Kuwabata): the old test asked whether the caption's CENTER stood within a
    radius of a crown, a stand-in for a 53 ft caption whose ends can lie in trees while its middle is clear."""
    from ..._geom import point_in_poly, seg_dist

    cx, cy = sum(p[0] for p in quad) / len(quad), sum(p[1] for p in quad) / len(quad)
    reach = max(math.dist((cx, cy), p) for p in quad) + CAPTION_HALO_FT
    for it in near(cx, cy, reach):
        x, y, r = float(it[0]), float(it[1]), float(it[2])
        if point_in_poly(x, y, list(quad)) or min(seg_dist(x, y, a, b) for a, b in zip(quad, [*quad[1:], quad[0]], strict=False)) < r + CAPTION_HALO_FT:
            return True
    return False
