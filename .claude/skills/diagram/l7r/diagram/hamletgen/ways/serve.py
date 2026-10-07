"""Split from hamletgen/ways.py by feature 173 - see this package's CLAUDE.md for the index.

One web lane, laid (`_lay_web_lane`). The straggler footpath pass that also lived here was dropped by feature 287 (GM
2026-09-30): the access tree reserves every house's corridor at seating and the settle draws it for any house the web
leaves unreached (`tree.admits`, `settle.settle_the_web`, `last_resort`), so a second router pass had nothing left to
guarantee.

Research: plumbing - NONE"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, point_in_poly, rot_rect, seg_closest, seg_dist, segments_cross
from l7r.diagram.settlement._geom.primitives import seg_dists

from ..consts import (
    BUNDLE_PITCH,
    FOOTPATH_FABRIC_GAP,
    WEB_FABRIC_GAP,
    WEB_HARD_GAP,
    WEB_REACH_FT,
    WEB_SHADOW_FT,
    Poly,
    Pt,
)
from .clearance import _clear_link, clear_runs
from .fabric import _LANE_JOIN_FT, _crosses_fabric, _draw_web, _net_segs
from .geom import _TOUCH_GAP, _net_reach, _reach, _trim_to_service, door_unhooked, end_serves, polyline_len, steading_footprints
from .route import ROUTE_CELL, _route


def shadow_measure(run: Sequence[Pt], segs: Sequence[tuple[Pt, Pt]]) -> tuple[int, float]:
    """How much of `run` (points along a way) shadows the ways `segs`: the points within `WEB_SHADOW_FT` of them, and the
    longest unbroken stretch of such points in feet. `_lay_web_lane` refuses a run on it against the whole network as the
    run is laid; the pool's finished-map test reads it way against way (feature 293: a re-packed Sawada roll of the earlier
    293 pass shipped two lanes 244 ft side by side that no pass laying them had asked about)."""
    near_flags = [bool(f) for f in (seg_dists(run, segs).min(axis=1) < WEB_SHADOW_FT)] if run and segs else [False] * len(run)
    step_ft = polyline_len(list(run)) / max(len(run) - 1, 1)
    worst = cur = 0
    for f in near_flags:
        cur = cur + 1 if f else 0
        worst = max(worst, cur)
    return sum(near_flags), worst * step_ft


def sampled(p: Sequence[Pt], step: float = 4.0) -> list[Pt]:
    """A way's points every `step` ft - the spacing `clear_runs` gives a web run before `_lay_web_lane` judges it."""
    out: list[Pt] = []
    for a, b in zip(p, p[1:], strict=False):
        n = max(1, int(math.dist(a, b) // step))
        out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    return [*out, p[-1]]


def shadowed_by(ways: Sequence[Sequence[Pt]], i: int) -> int | None:
    """The first other way that way `i` runs beside - within `WEB_SHADOW_FT`, unbroken, for more than a `BUNDLE_PITCH`
    (`shadow_measure`, way against way) - or None: `_lay_web_lane`'s refusal, asked of a finished lane (`settle_shadows`).
    Only a way whose box comes within `WEB_SHADOW_FT` of this one's is measured.

    Research: no way drawn twice - UNRESEARCHED: refused beside another way, within `WEB_SHADOW_FT` (30 ft), unbroken for more than a bundle pitch"""
    p = ways[i]
    if len(p) < 2:
        return None
    run = sampled(p)
    return next((j for j, o in enumerate(ways) if j != i and runs_beside(p, run, o)), None)


def runs_beside(p: Sequence[Pt], run: Sequence[Pt], o: Sequence[Pt]) -> bool:
    """Does way `p` (`run`: its `sampled` points) run beside way `o` - within `WEB_SHADOW_FT`, unbroken, for more than a
    `BUNDLE_PITCH`? Only a way whose box comes within `WEB_SHADOW_FT` of `p`'s is measured. `shadowed_by`'s pair test, asked
    pair by pair by a caller that keeps the answers (`knots.WebMemo`).

    Research: no way drawn twice - UNRESEARCHED: within `WEB_SHADOW_FT` (30 ft), unbroken for more than a bundle pitch"""
    x0, y0 = min(q[0] for q in p) - WEB_SHADOW_FT, min(q[1] for q in p) - WEB_SHADOW_FT
    x1, y1 = max(q[0] for q in p) + WEB_SHADOW_FT, max(q[1] for q in p) + WEB_SHADOW_FT
    if len(o) < 2 or max(q[0] for q in o) < x0 or min(q[0] for q in o) > x1 or max(q[1] for q in o) < y0 or min(q[1] for q in o) > y1:
        return False
    return shadow_measure(run, list(zip(o, o[1:], strict=False)))[1] > BUNDLE_PITCH


def _lay_web_lane(s: Settlement, run: Poly, hard: list[Poly], walls: list[Poly], water: list[tuple[Pt, Pt]], belts: Sequence[Poly] = (), houses: Sequence[Pt] = ()) -> bool:
    """Draw one web lane - but ONLY if it joins the way network, and TOUCHING it where it joins.

    A WEB THAT DOES NOT JOIN UP IS NOT A WEB, and this is the rule that makes the name honest. Three
    settlement-reviews found the same defect independently on three different maps: the lanes reached
    the houses and reached nothing else. Sawada drew six web lanes of which four touched no other
    way, so seven of its nineteen houses were "served" by an island whose nearest real lane was still
    136-296 ft off - exactly where they had been before the feature. Inashiro came out as three
    separate components with a 110 ft gap between them. The research this feature cites is explicit
    that the thing being reproduced is "the INTERCONNECTED system of narrow lanes and alleys", so a
    lane that connects to nothing is not an alley, it is a yard path.

    Two distinct jobs, and both were missing:

      - JOIN. A run whose nearest end is already within `_LANE_JOIN_FT` counts as arriving; one that
        is further off gets a link drawn to the network, and if the link cannot be drawn the run is
        not drawn either. Refusing to draw is the right answer - the alternative is ink that looks
        like a way and is not one.
      - TOUCH. Acceptance and INK are different tolerances, and conflating them is what left Inashiro
        with a lane stopping 12.7 ft short of the junction it aimed at, a visible break of about 19
        px on the sheet. So the joining end is extended onto the way it meets. The gate reach can
        stay where it is; it is then satisfied by construction rather than by rounding.

    Also refuses a run that merely SHADOWS an existing way - Inashiro laid a back lane a median 10 ft
    from a skeleton lane for its whole length, which reads as one lane accidentally drawn twice.
    `MIN_WEB_GAP` keeps the web's own cuts apart; nothing was keeping a cut off the lanes already
    there.

    Research:
        a web lane joins the network - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: one network, or not drawn
        no way drawn twice - UNRESEARCHED: a run refused over 60% of it, or a bundle pitch unbroken, beside a way
        not along a shelter belt - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: a lane kept through a belt, not along it
        how far inside a belt - UNRESEARCHED: a run over 60 ft inside a belt refused
        a tail past the junction cut - research/questions/0081-village-lanes.drawing.html: under 40 ft
        link reach - UNRESEARCHED: a link up to 200 ft to the network
        a link takes its way's width - CONVENTION
        web lane width - research/questions/0081-village-lanes.drawing.html: a web lane drawn 3 ft wide, the footpath's tread"""
    segs = _net_segs(s)
    if len(run) < 2:
        return False
    # TRIM FIRST, JOIN SECOND. The join is computed from the run's ENDS, so trimming afterwards moves
    # the end out from under the link that was drawn to it - which left a 187 ft lane whose start
    # stood 178 ft from any way, the exact dangling tread `lanes_reach_something` exists to catch.
    # to the bar the GATE asks of a lane end, not the looser service reach: this runs at DRAW time, before
    # the settle, so a steading a shortened run stops serving still gets its reserved corridor drawn afterwards (feature 227;
    # the straggler footpaths that used to do this were dropped, feature 287).
    # ...and a tread that stops at a steading's own dooryard has ARRIVED there, which is the fourth clause of
    # `end_serves` at its own tight distance (`steading_footprints`, feature 227 D11).
    run = _trim_to_service(run, segs, houses, steadings=steading_footprints(s.M))
    if segs:
        # SHARING A CORRIDOR IS SHADOWING, whether the two lines are parallel or crossing. The test
        # was written against `MIN_WEB_GAP` (the room a lane needs to pass BETWEEN two steadings),
        # which is far too tight to describe two ways a reader sees as one: Inashiro laid a back lane
        # that crossed the connector mid-run and stayed within 30 ft of it for 91% of its length, and
        # the 18 ft test did not fire once. A reader reads them as one lane drawn twice, so the
        # threshold is what a reader can separate, not what a lane can squeeze through.
        # SHADOWING IS A LENGTH, NOT ONLY A FRACTION. A fraction alone lets a long run hide: a lane
        # that parallels the connector for 128 continuous feet at a median 16 ft measured 50%
        # shadowed against a 60% bar and was drawn. Doubled ink is doubled ink whether it is half the
        # run or four fifths of it, so the longest UNBROKEN shadowed stretch is capped at one bundle
        # pitch as well. Both clauses are needed - the fraction catches a short lane laid alongside
        # another for all of its length, the absolute catches a long one that eventually diverges.
        _near, _worst_ft = shadow_measure(run, segs)
        # ONE REFUSAL, BOTH CLAUSES: the fraction catches a short lane laid alongside another for all of its
        # length, the unbroken stretch a long one that eventually diverges. Written as one test because they are
        # one rule - a lane that shadows another is a doubled band - and because a separate line for the second
        # is a line only a particular map shape ever reaches.
        if _near > 0.6 * len(run) or _worst_ft > BUNDLE_PITCH:
            return False
        # ...AND A LANE DOES NOT RUN THE LENGTH OF A SHELTER BELT. Crossing one costs the belt a
        # lane's width of wall, which is a fair price for a way that has somewhere to be; running
        # ALONG it splits one wind wall into two thinner ones and opens a slot down the middle. A
        # review measured a back lane 237 of 237 ft inside the belt, having deleted 15 of its 169
        # clumps, on a map whose notes already record this belt being damaged the same way once.
        for belt in belts:
            inside = sum(1 for q in run if point_in_poly(q[0], q[1], list(belt)))
            if inside * (polyline_len(run) / max(len(run), 1)) > 60.0:
                return False
        # THE WHOLE RUN ARRIVES, NOT JUST ITS TWO ENDS. Measuring only the endpoints is how the snap
        # came to draw a hairpin: a run whose BODY already passes 2.75 ft from a lane, but whose end
        # wandered 23.8 ft beyond it, got a perpendicular drawn back to the foot - a needle-thin
        # triangular loop hanging off the junction, which a review found on all four hamlets (turn
        # deviations of 158, 178, 110 and 107 degrees, against a pre-web maximum of 7). If the run
        # has already arrived somewhere along its length there is nothing to snap; the only thing
        # worth doing is trimming the short tail that carried on past.
        vert = [min(seg_dist(v[0], v[1], a, b) for a, b in segs) for v in run]
        k = min(range(len(vert)), key=lambda i: vert[i])
        if 0 < k < len(run) - 1 and vert[k] <= _LANE_JOIN_FT:
            # THE SHORT HALF IS THE STUB, whichever half it is: a run that touches the network partway along is
            # one lane arriving with a tail, and which side carried on past is not always the same one. Written
            # as a choice rather than a pair of branches so neither side is a line only one map shape reaches.
            head, tail = polyline_len(run[: k + 1]), polyline_len(run[k:])
            run = run[: k + 1] if tail < 40.0 else (run[k:] if head < 40.0 else run)
            _draw_web(s, run, 3)
            return True
        d0, d1 = vert[0], vert[-1]
        end = 0 if d0 <= d1 else -1
        gap = min(d0, d1)
        p = run[end]
        q = min((seg_closest(p[0], p[1], a, b) for a, b in segs), key=lambda z: math.dist(p, z))
        if gap > _LANE_JOIN_FT:
            if math.dist(p, q) > WEB_REACH_FT * 2.0:
                return False
            link = [
                r for r in clear_runs([p, q], hard, WEB_HARD_GAP, step=4.0, lines=water, tight=walls, tight_margin=WEB_FABRIC_GAP, floor=12.0) if _reach(p, r) < 12.0 and _net_reach(r, segs) < 12.0
            ]
            if not link:
                return False
            # A HEALING LINK INHERITS THE WIDTH OF THE WAY IT JOINS. Laid at the web's own 3 ft
            # between two 5 ft lanes it renders as a neck with a round-cap knuckle at each step - a
            # review read it at 2x as a lollipop knob mid-street, and it is a repair scar rather than
            # a way. A link exists to make two lanes one; it should look like the lane it completes.
            _w = max(
                (
                    float(_l.get("w", 3))
                    for _l in s.M.get("lanes", [])
                    if _net_reach(link[0], list(zip([(float(x), float(y)) for x, y in _l["pts"]], [(float(x), float(y)) for x, y in _l["pts"]][1:], strict=False))) <= _LANE_JOIN_FT
                ),
                default=3.0,
            )
            _draw_web(s, link[0], int(_w))
        elif _clear_link(run[end], q, hard, walls, water):
            # SNAP ONLY IF THE GROUND BETWEEN IS CLEAR. Extending an end onto the way it meets is
            # what makes the junction read as a touch instead of a gap - but the few feet being
            # added are ground like any other, and adding them blind put lane ink across houses and
            # garden beds (`features_do_not_overlap`, `houses_clear_of_lanes` on every cohort seed
            # the moment snapping went in). If the gap is not walkable the lane simply ends where it
            # ended; a visible break is better than a lane through a wall.
            run = ([q, *run]) if end == 0 else ([*run, q])
    _draw_web(s, run, 3)
    return True


def front_door(h: Mapping[str, Any], clear: float) -> Pt | None:
    """Where a path to a farm with its own grove begins (feature 291): `clear` past the far edge of the farm's yard, straight
    out along the line from the house through the yard - the front, the side a grove leaves open (or breaks for the way
    in). None for a farm with no grove of its own, or no yard.

    Research:
        the way in at the front - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html:
            past the yard on the grove's open side, at the middle of a ring's break"""
    g = h.get("geom") or {}
    y = g.get("yard")
    if not g.get("groves") or y is None:
        return None
    # A RING'S DOOR LINES UP WITH ITS WAY IN: the yard turns with the house's rake and the bands do not, so "straight out
    # through the yard" can miss a gap 24 ft wide (cohort seed 12: three farms' doors walled on all four sides). The door
    # stays just past the yard - a door out in the gap itself, ~80 ft from the house, is past the reach a path's arrival
    # is judged by, and seed 12 then stranded 13 - but it takes the gap's middle across the front.
    faces = list(g.get("grove_faces") or ())
    split = [r for r, (face, _d) in zip(g["groves"], faces, strict=False) if sum(1 for f2, _d2 in faces if f2 == face) == 2]
    gap_mid: Pt | None = None
    if len(split) == 2:
        (ax, ay, aw, ah), (bx, by, bw, bh) = split
        if abs(ay - by) < 1e-6:  # a north or south front: the halves side by side along x
            lo, hi = sorted(((ax, aw), (bx, bw)))
            gap_mid = ((lo[0] + lo[1] / 2 + hi[0] - hi[1] / 2) / 2, ay)
        else:
            lo, hi = sorted(((ay, ah), (by, bh)))
            gap_mid = (ax, (lo[0] + lo[1] / 2 + hi[0] - hi[1] / 2) / 2)
    hx, hy = float(h["x"]), float(h["y"])
    fx, fy = float(y[0]) - hx, float(y[1]) - hy
    n = math.hypot(fx, fy)
    if n < 1e-9:
        return None
    fx, fy = fx / n, fy / n
    # the yard's reach along the front, unturned: where the ray from its middle leaves the box. It was the box's projected
    # half-width (|fx| w/2 + |fy| h/2), which overshoots the edge on any slant - Kashikawa's farm at (2268, 2144), its front
    # ten degrees off the box's side, took its door 12.4 ft past the yard, past the 12 ft a path's arrival is judged at
    half = min(float(y[2]) / 2 / abs(fx) if abs(fx) > 1e-9 else math.inf, float(y[3]) / 2 / abs(fy) if abs(fy) > 1e-9 else math.inf)
    door = (float(y[0]) + fx * (half + clear), float(y[1]) + fy * (half + clear))
    if gap_mid is None:
        return door
    # across the front, the gap's line; along it, just past the yard
    return (gap_mid[0], door[1]) if abs(split[0][1] - split[1][1]) < 1e-6 else (door[0], gap_mid[1])


DOOR_STEP_FT = 4.0
"""How far a door on a fixture is stepped along the front at a time (`door_off_fixtures`; a map drawing convention)."""


def door_off_fixtures(door: Pt, house: Pt, quads: Sequence[Poly], gap: float, step: float = DOOR_STEP_FT, tries: int = 8) -> Pt | None:
    """`door` moved along the front - across the line from the house through it - to the nearest point `gap` clear of every
    quad in `quads` (the walls a route keeps off, the fixtures among them; feature 291 on 287: the yard persimmon stands at
    the middle of the yard's front, where the door is, and Kashikawa's door paths began inside its trunk); the door itself
    where it is clear, None where no step within `tries` is.

    Research: no path from inside a fixture - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the door stepped along the front"""
    from l7r.diagram.settlement import edge_dist

    fx, fy = door[0] - house[0], door[1] - house[1]
    n = math.hypot(fx, fy) or 1.0
    ax, ay = -fy / n, fx / n  # along the front
    for k in range(tries + 1):
        for sgn in (1.0,) if k == 0 else (1.0, -1.0):
            q = (door[0] + sgn * ax * k * step, door[1] + sgn * ay * k * step)
            if not any(len(p) >= 3 and (point_in_poly(q[0], q[1], p) or edge_dist(q[0], q[1], p) < gap) for p in quads):
                return q
    return None


def pulled(path: Sequence[Pt], clear: Any) -> list[Pt]:
    """`path` string-pulled: from each kept point, on to the farthest later point a straight leg reaches where `clear(a, b)`
    says it may - the first and last points kept, every jog a clear chord can cut taken out."""
    pts = list(path)
    if len(pts) < 3:
        return pts
    out, k = [pts[0]], 0
    while k < len(pts) - 1:
        nxt = next((j for j in range(len(pts) - 1, k, -1) if j == k + 1 or clear(pts[k], pts[j])), k + 1)
        out.append(pts[nxt])
        k = nxt
    return out


def to_first_arrival(path: Sequence[Pt], segs: Sequence[tuple[Pt, Pt]], touch: float, clear: Any = None) -> list[Pt]:
    """A door path ended where it first arrives within `touch` of its way (`segs`) - square onto it, at the way's nearest point
    to the leg's start - so it never runs on beside the street it joins (feature 291 on 287: a door path is a tree lane the settle does not cut, and
    one of Kashikawa's routed along its street before meeting it, a doubled tail and a sliver of grass the settle refused).

    Research:
        a door path meets its way as a T - research/questions/0081-village-lanes.drawing.html, research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: joined at a T, ended square at its first arrival"""
    import numpy as np  # bound here, not at import (feature 237)

    pts = list(path)
    for k in range(1, len(pts) if segs else 0):
        a, b = pts[k - 1], pts[k]
        n = max(1, int(math.dist(a, b) // 2.0))
        qs = [(a[0] + (b[0] - a[0]) * j / n, a[1] + (b[1] - a[1]) * j / n) for j in range(1, n + 1)]
        # every sample of the leg against every segment at once (`seg_dists`); the first sample within `touch` arrives
        d = seg_dists(qs, segs)
        hit = np.flatnonzero(d.min(axis=1) <= touch)
        if hit.size:
            j = int(hit[0])
            q, best = qs[j], segs[int(d[j].argmin())]
            # ...SQUARE ONTO IT: the last leg runs from the vertex before the arrival to the way's nearest point to that
            # vertex, where the clear chord allows it - a leg arriving at a shallow slant ran on beside the street, and the
            # doubled-tail sweep cut it to a jog the law read as a kink (cohort seed 904)
            a0 = pts[k - 1]
            foot = min((seg_closest(a0[0], a0[1], u, v) for u, v in segs), key=lambda f: math.dist(f, a0))
            # ...where that square leg is clear (`clear`); else at the arrival itself, as the path came (cohort seeds 12 and
            # 901: a square leg across a neighbor's grove corner left three farms with no path at all)
            if clear is not None and not clear(a0, foot):
                foot = seg_closest(q[0], q[1], best[0], best[1])
            return [*pts[:k], foot]
    return pts


DOOR_REACH_FT = 60.0
"""How far a grove farm's front door may stand from the lane network before a footpath is laid to it (feature 291; the
settlement-review of Kashikawa: a farm whose only lane stopped against the outside of its east band, 89 ft from the door).
The front is the side the grove leaves open for the way in (research/homesteads/715), so the path arrives there; 60 ft is
the reach at which the lane page counts a way as reaching a farmhouse, itself a GUESS there (feature 328).

Research: a door reached - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: 60 ft from the network, the page's reach for a way reaching a farmhouse"""


def own_street(h: Mapping[str, Any], streets: Sequence[Sequence[tuple[Pt, Pt]]]) -> int | None:
    """The index of the street a row farm's way ends on - the nearest to its FRONT DOOR (its house where it has none) - or
    None where no street is laid. By the door, not the house: a farm between two streets faces the one its door is on
    (cohort seed 903: a door 36 ft from one street, its house nearer the other).

    Research: a row farm fronts its street - research/questions/0033-row-villages-resson.drawing.html: the nearest to its door"""
    if not streets:
        return None
    hx, hy = front_door(h, FOOTPATH_FABRIC_GAP + 4.0) or (float(h["x"]), float(h["y"]))
    return min(range(len(streets)), key=lambda k: min((seg_dist(hx, hy, a, b) for a, b in streets[k]), default=float("inf")))


def lay_door_paths(s: Settlement, hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]], reach: float = DOOR_REACH_FT) -> int:
    """A footpath from each grove farm's front door (`front_door`) to the ways, where the door stands more than `reach`
    from them: to the connected lane network, or - for a row farm (feature 291 plan D17) - to its OWN street (the nearest
    street laid, `own_street`), routed round the farm's grove when the street lies on its windward side. Each path records
    the farm it serves (`serves`); the nearest few points are tried, nearest first. Returns the paths drawn.

    Research:
        every grove farm reached at its door - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html:
            a 3 ft footpath where the door stands past the reach
        round the grove to the street - research/questions/0033-row-villages-resson.drawing.html: a path round the grove,
            a GUESS there
        off the fixtures and grove bands - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html, research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: walls to the path
        no path to a household reached across a yard - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: it shows no lane of its own
        a flank door only where the front has none - UNRESEARCHED: a door path leaves from a flank of the dooryard only where no lawful path leaves the front"""
    from .checks import served_network  # local: checks sits above serve in this package's layers
    from .law import fixture_quads  # local: the law sits above serve too
    from .settle import Lawful  # local: the settle sits above serve too

    # ...EACH AS LAWFUL AS A TREE LANE (feature 291 on 287): a door path is one (`corridors.is_tree`), which no settle repair
    # cuts, so a path the law refuses - a kink round a grove's corner (cohort seed 904), a needle onto a join (seed 23) - is
    # passed over for the next target rather than drawn and the web refused
    lawful = Lawful(s, tree=True)

    # ...ROUND EVERY FARMSTEAD FIXTURE (feature 291 on feature 287): a grove farm's fixtures are laid in its bundle and drawn
    # before the web, and the lane law cuts a way over one (`over_fixtures`) - Kashikawa's far-row paths each crossed their
    # own farm's wood shed or privy on their first leg, the settle cut them, and the farms were left unreached
    quads = fixture_quads(s.M)
    # ...AND EVERY GROVE BAND, the farm's own too: a ring's door stands in the way in through its front band, and a straight
    # step to the street ran off through the band's other half (cohort seed 901, `grove_rules.groves_crossed_by_lanes`)
    # - grown by a door path's half-tread and half a foot, since the rule strokes the tread, not the centerline
    grow = 2.0 * (1.5 + 0.5)
    bands = [
        rot_rect(float(g["x"]), float(g["y"]), float(g["w"]) + grow, float(g["h"]) + grow, float(g.get("rot") or 0.0)) for g in s.M.get("groves") or () if all(k in g for k in ("x", "y", "w", "h"))
    ]
    walls = [*walls, *quads, *bands]
    steadings = steading_footprints(s.M)
    n = 0
    for h in list(s.M.get("houses", [])):
        if h.get("reached_across"):
            continue  # reached across its neighbor's yard: a household with no way of its own (feature 317, `rolling/passage.py`)
        door = front_door(h, FOOTPATH_FABRIC_GAP + 4.0)
        if door is not None:
            # ...clear of everything the router keeps off, not the fixtures alone: stepped toward its own well, a door stood in
            # the router's gap off the wellhead and no route left it (Mizuguchi, three farms)
            door = door_off_fixtures(door, (float(h["x"]), float(h["y"])), [*walls, *hard], FOOTPATH_FABRIC_GAP + 1.0)
        streets = [
            [(tuple(a), tuple(b)) for a, b in zip(ln["pts"], ln["pts"][1:], strict=False)] for ln in s.M.get("lanes") or [] if ln.get("street") and ln.get("street_index") is not None
        ]  # a row's own street, not a join
        k = own_street(h, streets)  # type: ignore[arg-type]
        segs = streets[k] if k is not None else served_network(s.M.get("lanes") or [])
        if door is None or not segs or (min(seg_dist(door[0], door[1], a, b) for a, b in segs) <= reach and street_arrives(h, door, segs, k, steadings)):  # type: ignore[arg-type]
            continue
        # ...FROM THE FRONT DOOR, ELSE A FLANK OF THE DOORYARD (`access.doors_of`, the corridors' own doors): a far-row farm
        # fronts its holding, away from its street, and with its grove on the street's side the front had no way round it
        # the law would keep (cohort seed 904: two farms left unreached)
        doors = [door, *(door_off_fixtures(d, (float(h["x"]), float(h["y"])), [*walls, *hard], FOOTPATH_FABRIC_GAP + 1.0) for d in flank_doors(h))]
        # A FLANK ONLY AS THE FALLBACK (amendment 8; since amendment 9 a preference, FR-019's door clause dropped): the front first;
        # a flank facing no band of the farm's own grove, with open ground between it and the front door, only where no
        # lawful path leaves the front - recorded on the lane (`from_flank`) and on the map (`meta.door_flanks`)
        for k, d in enumerate(doors):
            if d is None or (k > 0 and not front_to_flank_open(door, d, h)):
                continue
            path = door_path(s, d, segs, hard, walls, water, quads, lawful)  # type: ignore[arg-type]
            if path is not None and _draw_web(s, path, 3, houses=[(float(h["x"]), float(h["y"]))], joins=True):
                s.M["lanes"][-1]["serves"] = [float(h["x"]), float(h["y"])]
                if k > 0:
                    s.M["lanes"][-1]["from_flank"] = True
                    s.M["meta"].setdefault("door_flanks", []).append([round(float(h["x"]), 1), round(float(h["y"]), 1)])
                n += 1
                break
    return n


def street_arrives(h: Mapping[str, Any], door: Pt, segs: Sequence[tuple[Pt, Pt]], street: int | None, steadings: Sequence[Poly]) -> bool:
    """Does a farm's way already arrive at it without a door path? Off the network, yes (the reach alone was asked, as
    ever). On a row's OWN street (`street` an index) only where the street's point nearest the door is an end the lane law
    counts as serving the farm (`end_serves`: within `WAY_END_REACH_FT` of the house, or `STEADING_ARRIVAL_FT` of its built
    ground) - the predicate the settle trims a street's end by. At the door's reach alone, Mizuguchi's east-end farm, its door
    11 ft off the street but its yard 19, took no path; the street's end past the last path then served nothing the law
    counts, the settle cut it back a frame, and the farm stood off every way (2026-10-01).

    Research:
        the street serves the farm - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: within 60 ft of the house or
            12 ft of its built ground"""
    if street is None:
        return True
    q = min((seg_closest(door[0], door[1], a, b) for a, b in segs), key=lambda p: math.dist(p, door))
    return end_serves(q, (), [(float(h["x"]), float(h["y"]))], None, steadings)


def flank_doors(h: Mapping[str, Any]) -> list[Pt]:
    """A farm's dooryard flanks that face NO BAND of its own grove (`rolling.access.doors_of`, beside the yard carried past
    the gable) - on the grove's open side, so in practice a two-sided grove's (spec-fidelity's condition on FR-019's
    exception, 2026-09-30) - or none without a yard of its own.

    Research: a flank door as fallback - UNRESEARCHED: a dooryard flank facing no grove band"""
    from l7r.diagram.settlement.rolling.access import doors_of

    g = h.get("geom") or {}
    if g.get("yard") is None or g.get("house") is None:
        return []
    yx, yy = float(g["yard"][0]), float(g["yard"][1])
    faces = [(float(f[0]), float(f[1])) for f, _depth in g.get("grove_faces") or ()]

    def open_side(d: Pt) -> bool:
        vx, vy = d[0] - yx, d[1] - yy
        n = math.hypot(vx, vy) or 1.0
        return not any((vx * fx + vy * fy) / n > 0.7 for fx, fy in faces)

    return [d for d in doors_of(g, 3.0)[2:] if open_side(d)]


def front_to_flank_open(front: Pt, flank: Pt, h: Mapping[str, Any]) -> bool:
    """Is the ground between a farm's front door and a flank door open - no building (its house) and no band of its grove
    across it (amendment 8's condition: open yard between the path's end and the front door)?"""
    g = h.get("geom") or {}
    boxes = [g.get("house"), *(g.get("groves") or ())]
    rings = [[(b[0] - b[2] / 2, b[1] - b[3] / 2), (b[0] + b[2] / 2, b[1] - b[3] / 2), (b[0] + b[2] / 2, b[1] + b[3] / 2), (b[0] - b[2] / 2, b[1] + b[3] / 2)] for b in boxes if b]
    return not _crosses_fabric([front, flank], rings, 0.0)


def route_from_door(door: Pt, q: Pt, hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]], ok: Any) -> list[Pt]:
    """The router's way from a door to `q` (`_route`, a footpath's gap) - or, where the door's own lattice cell has no free
    neighbor to leave by, from a step one or two cells out of it, toward `q` first, taken only where the step itself is
    clear (`ok`), the door put back at its head. The router plans its cells at the gap and most of a cell more, so a door
    close against its house wall and its own fixture was boxed in: Kashikawa's farm at (2473, 2937) under feature 302 found
    no route to any of its six targets, where a step of 6-11 px found one (the Diagram performance session, 2026-10-01).
    The law still judges the whole path (`door_path`)."""
    path = _route(door, q, hard, walls, water, gap=FOOTPATH_FABRIC_GAP)
    if len(path) >= 2:
        return path
    for r in (ROUTE_CELL, 2.0 * ROUTE_CELL):
        steps = [(door[0] + r * math.cos(k * math.pi / 4), door[1] + r * math.sin(k * math.pi / 4)) for k in range(8)]
        for st in sorted(steps, key=lambda p: math.dist(p, q)):
            if not ok(door, st):
                continue
            path = _route(st, q, hard, walls, water, gap=FOOTPATH_FABRIC_GAP)
            if len(path) >= 2:
                return [door, *path]
    return []


def door_path(s: Settlement, door: Pt, segs: Sequence[tuple[Pt, Pt]], hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]], quads: Sequence[Poly], lawful: Any) -> list[Pt] | None:
    """The door path from `door` to its way (`segs`) the law keeps, trying the way's six nearest points, nearest first: the
    straight step where it is clear (the router plans on a lattice and refused doors whose every neighboring cell stood in
    its gap of the yard, the well or a trunk - three Mizuguchi doors 35 ft from their street), else the routed way,
    string-pulled (the lattice's few-foot jogs are kinks to the law, cohort seed 904); ended square on the way at its first
    arrival (`to_first_arrival`); squared where it crosses water (`settle.square_run`, as the settle squares every lane
    first); and kept only where it crosses no wall and no fixture and the law would keep it as a tree lane (`lawful`).

    Research:
        a worn path takes the shortest way - research/questions/0081-village-lanes.drawing.html: straight where clear,
            else routed and pulled taut"""
    from l7r.diagram.overlap.registry import forbidden_segment

    from .law import over_a_fixture
    from .settle import square_run

    def ok(a: Pt, b: Pt) -> bool:
        # ...and clear of a fixture at the tread's half-width and the law's pad, and of what the overlap matrix forbids a way
        # on - what the law asks of the finished path: at a bare zero gap, cohort seed 23's straight steps skimmed a privy
        return (
            not _crosses_fabric([a, b], walls, 0.0)
            and not _crosses_fabric([a, b], hard, 0.0)
            and not any(segments_cross(a, b, c, d) for c, d in water)
            and over_a_fixture([a, b], 3.0, quads) is None
            and forbidden_segment(s.M, "lanes", [a, b], 3.0) is None
        )

    for q in sorted((seg_closest(door[0], door[1], a, b) for a, b in segs), key=lambda q: math.dist(q, door))[:6]:
        path = [door, q] if ok(door, q) else pulled(door_unhooked(route_from_door(door, q, hard, walls, water, ok), ok), ok)
        path = to_first_arrival(path, segs, _TOUCH_GAP, ok)
        path = square_run(s.M, path) if len(path) >= 2 else path
        if len(path) >= 2 and not _crosses_fabric(path, walls, 0.0) and over_a_fixture(path, 3.0, quads) is None and lawful(path, 3.0):
            return path
    return None
