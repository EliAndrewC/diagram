"""Split from settlement/structures/fixtures.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any

from ..._geom import (
    Pt,
    seg_dist,
)

# The lane clearance a notice-board caption must MEET before nearness decides the seat. See the long
# note beside `_pick` in `kosatsuba` for why this satisfices rather than maximizes, and why 5 ft.
CAPTION_LANE_TARGET_FT = 3.0

# THE RULE'S OWN FLOOR, as opposed to the target above it. `captions_clear_the_ways_they_stand_on`
# (gate 0617) requires 2 ft between a caption's box and a lane's tread edge; the 3 ft target keeps one
# foot of margin over it and no more. A board that can reach the target takes it; a board that cannot
# gives up the margin - never the two feet the rule actually asks for, and never its position beside
# the board it names. Feature 157: the rung between "the good seat" and the old unbounded fallback.
CAPTION_LANE_FLOOR_FT = 2.0

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

if TYPE_CHECKING:
    pass


def first_clear_seat(
    seats: Sequence[Any],
    hug: Callable[[Any], float],
    hug_cap: float,
    blocked: Callable[[Any], bool],
    clearance: Callable[[Any], float],
    want: float,
) -> Any:
    """ONE RUNG of the caption ladder: the first seat that clears the hug cap, is unblocked, and
    keeps at least `want` of clearance from the way it stands on.

    LIFTED OUT OF `_draw_board_caption` (feature 174, GM 2026-08-28: "If something is only available
    as an inner function in a closure, then you can move it out into its own function to make it
    more unit testable... Dropping the test is not one of the options"). The identical expression
    appeared FOUR times in that method - the tilted branch's target and floor rungs, and the level
    branch's two - and the rung that SUCCEEDS at the floor after failing at the target could not be
    reached by any of eight constructed map geometries, because the discriminator is a narrow band
    of clearance between the two thresholds. As one lifted body it is three lambdas to test.

    The four call sites now differ only in their seat list and their `want`, which is the whole of
    what the ladder is: the same question asked with a lower bar each time.
    """
    return next((q for q in seats if hug(q) <= hug_cap and not blocked(q) and clearance(q) >= want), None)


def pick_caption_seat(
    seats: Sequence[Pt],
    at: Pt,
    hug: Callable[[Pt], float],
    hug_cap: float,
    box_clearance: Callable[[Pt], float],
    lane_target: float,
    blocked: Callable[[Pt], bool] | None = None,
    gap: Callable[[Pt], float] | None = None,
) -> Pt:
    """The board's caption seat: the NEAREST seat that clears the ways by `lane_target`, and if none does,
    the legal seat that clears them best.

    LIFTED OUT OF `place_kosatsuba` (feature 146, GM 2026-08-28 on inner functions and testability). It took
    two closures and two numbers, all of which a test can hand it directly; reaching it through the placer
    meant building a settlement whose every seat was blocked. The tie-break is (distance, then ORDER), which
    is what keeps an unblocked board on its historical seat when a diagonal ties with it.
    """
    # `blocked` IS A THIRD LEGALITY TERM, and it degrades in the same direction as the other two
    # (feature 152 T12). The filter scored hug and lane clearance and NOTHING ELSE, so a caption could
    # be seated on top of a garden, or with a whole lane between it and the thing it names - Inashiro's
    # "notice board" stood with the full 6 ft width of lane 1 between the caption and its board, and a
    # shrine 22 ft away on the caption's own side, so the words read as naming the shrine. The comment
    # under the satisfice rule already knew the shape ("a copse clump through the text") and chose lane
    # clearance as the only bar anyway. If every seat is blocked the term is dropped rather than the map
    # left captionless, which is the same "or list(seats)" fallback the hug cap has always had.
    _hug_ok = [q for q in seats if hug(q) <= hug_cap] or list(seats)
    legal = _hug_ok
    # `blocked` REFINES AMONG SEATS THAT ALREADY CLEAR THE WAYS - it does not outrank the lane bar
    # (feature 152 T12). Applied as a filter over ALL legal seats it changed which seat the ladder fell
    # back to, and tripwire seed 33 came out with its caption standing on a way
    # (`captions_clear_the_ways_they_stand_on`) - trading the defect this term was written for against a
    # worse one. Lane clearance is the older and harder rule; the fabric and way-side terms pick BETWEEN
    # the seats that already satisfy it, and drop away entirely when none of them is unblocked.
    clear = [q for q in legal if box_clearance(q) >= lane_target]
    _unblocked = [q for q in clear if not (blocked and blocked(q))]
    # LEAST BAD, NOT ARBITRARY, WHEN EVERY SEAT IS BLOCKED (settlement-review of Kuwabata, 2026-09-12).
    # Dropping the term entirely is right in that it never leaves a map captionless, and wrong in what it
    # then chooses: Kuwabata's caption came to rest 0.02 px off a byre and 38.7 ft from the board it names,
    # because with every seat blocked the choice fell through to pure lane clearance and a seat touching a
    # roof scored as well as one in the open. `gap` is how far the caption's own quad stands from the
    # nearest solid feature, so the fallback degrades along the axis the term is about.
    clear = _unblocked or ([max(clear, key=gap)] if (gap and clear) else clear)
    if clear:
        ix = {id(q): i for i, q in enumerate(seats)}
        return min(clear, key=lambda q: (round((q[0] - at[0]) ** 2 + (q[1] - at[1]) ** 2, 3), ix[id(q)]))
    # ...AND THE FALLBACK REFINES BY IT TOO (settlement-review x3, feature 154). This returned
    # `max(legal, key=box_clearance)` and never consulted `blocked` at all - so on a board where NO
    # seat reaches the lane target, which is every board standing close beside a way, the whole
    # way-side term was silently skipped and the best-clearing seat won even with the tread between
    # the caption and its own board. Sawada shipped exactly that three passes running: board at -12.0
    # to -7.0 off the connector's axis, tread -3.0 to +3.0, caption +6.0 to +14.5, with the board's
    # own side measurably clear. A rule that cannot fire on the path most boards take looks exactly
    # like a rule that passes.
    #
    # Same degradation as above, deliberately: prefer the unblocked seats, and drop the term entirely
    # when none of them is - never leave the map captionless for it.
    _legal_unblocked = [q for q in legal if not (blocked and blocked(q))]
    if not _legal_unblocked and gap and legal:
        # the same graceful degradation as above, on the path most boards take
        return max(legal, key=gap)
    return max(_legal_unblocked or legal, key=box_clearance)


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
            return inner
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
    are one junction; each dwelling's nearest sample within `reach` walks the shortest route to the connector's handover,
    and every route then runs on out along the connector. Empty when the map has no handover."""
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
    src = min(range(len(nodes)), key=lambda i: math.dist(nodes[i], hand))
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
    out_along: list[tuple[float, float]] = []  # the approach, sampled at the same step as the lanes
    for ln in M.get("lanes") or []:
        cp = [(float(x), float(y)) for x, y in (ln.get("pts") or [])] if ln.get("connector") else []
        for a, b in zip(cp, cp[1:], strict=False):
            n = max(1, int(math.dist(a, b) // step))
            out_along += [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n + 1)]
    routes: list[list[tuple[float, float]]] = []
    for h in M.get("houses") or []:
        s = min(dist, key=lambda i: math.dist(nodes[i], (float(h["x"]), float(h["y"]))))
        if math.dist(nodes[s], (float(h["x"]), float(h["y"]))) > reach:
            continue
        path: list[tuple[float, float]] = []
        while s != -1:
            path.append(nodes[s])
            s = back[s]
        routes.append(path + out_along)
    return routes


def routes_missed(routes: Sequence[Sequence[tuple[float, float]]], x: float, y: float, near: float) -> int:
    """How many of `routes` never come within `near` of (x, y) - the departures that do not pass a board there."""
    return sum(1 for r in routes if not any(math.hypot(q[0] - x, q[1] - y) <= near for q in r))
