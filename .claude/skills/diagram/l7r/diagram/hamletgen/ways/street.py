"""THE ROW VILLAGE'S STREETS (feature 291 amendment 3, plan D17; research/questions/0033-row-villages-resson.html) - each street the row
seating planned (`homesteads/rows.py`, `s._row_streets`) laid as ONE continuous way along its row, a rank wider than
the lanes off it, joined to the connector or to the street before it; and each row farm's way ending on its OWN street.

A layer between `serve` (the door paths) and `web` (the stage that calls it).

Research: street plumbing - NONE
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, seg_closest, seg_dist

from ..consts import BUNDLE_PITCH, FOOTPATH_FABRIC_GAP, Poly, Pt
from . import law
from .corridors import FORD_LANDING_FT
from .fabric import _crosses_fabric, _draw_web
from .route import _route
from .serve import door_path
from .settle import Lawful

STREET_WIDTH = 6
"""The street's tread: the connector's, a rank wider than the web's 3-5 lanes (FR-017).

Research: street width - research/questions/0033-row-villages-resson.drawing.html: 6 ft"""

_VERTEX_FT = 40.0
"""The street's vertex spacing once laid: the planned line is sampled every 8 ft; a worn way keeps a vertex every two
treads' lengths or so - a map drawing convention.

Research: street vertex spacing - CONVENTION: a vertex every 40 ft"""


def row_reach(houses: Sequence[Mapping[str, Any]]) -> tuple[float, float]:
    """How far off a planned street a farm may stand and still be its own (1.5 frames), and how far the street runs past its
    end farms (half a frame) - the widest farm's frame (`geom.bbox`), or the nucleated pitch where none is recorded.

    Research:
        a farm's own street - UNRESEARCHED: a farm within 1.5 frames of the street is its own
        street run past its end farms - UNRESEARCHED: half a frame"""
    fw = max((max(float(b[2]), float(b[3])) for b in (((h.get("geom") or {}).get("bbox")) for h in houses) if b), default=BUNDLE_PITCH)
    return 1.5 * fw, fw / 2


def drawn_span(s: Settlement, k: int, houses: Sequence[Mapping[str, Any]], brook: Sequence[Pt] = ()) -> list[Pt]:
    """The stretch of planned street `k` the web will lay (`lay_row_streets`): its own farms' span (`street_span`) at the
    farms' own reach (`row_reach`), short of the `brook` past its end farms. The road reads it too (`track.stage_track`),
    with the same brook, so it runs out from the street as drawn."""
    lines = getattr(s, "_row_streets", None) or []
    if k >= len(lines):
        return []
    own = getattr(s, "_row_street_farms", None) or []
    centers = [(float(h["x"]), float(h["y"])) for h in houses]
    reach, pad = row_reach(houses)
    return street_span(lines[k], own[k] if k < len(own) else centers, reach, pad, brook)


def street_run_out(street: Sequence[Pt], width: float, height: float, beyond: float = 60.0) -> list[Pt]:
    """The road a row's street runs on as (feature 291 plan D17): from the street's end nearer the sheet's edge, straight on
    along its last leg until `beyond` past the edge. The end chosen is the one whose run to the edge is shorter. (Here, beside
    the street's span, since feature 304 took `track.py` over the 1,000-line bar; `track.stage_track` calls it.)

    Research: street runs on as the road - research/questions/0033-row-villages-resson.drawing.html, research/questions/0081-village-lanes.drawing.html: straight on along its last leg off the nearer sheet edge"""

    def run(end: Pt, prev: Pt) -> tuple[float, list[Pt]]:
        dx, dy = end[0] - prev[0], end[1] - prev[1]
        m = math.hypot(dx, dy) or 1.0
        ux, uy = dx / m, dy / m
        tx = (-end[0]) / ux if ux < 0 else (width - end[0]) / ux if ux > 0 else math.inf
        ty = (-end[1]) / uy if uy < 0 else (height - end[1]) / uy if uy > 0 else math.inf
        t = max(0.0, min(tx, ty))
        return t, [end, (end[0] + ux * (t + beyond), end[1] + uy * (t + beyond))]

    a = run(street[0], street[min(8, len(street) - 1)])
    b = run(street[-1], street[max(-9, -len(street))])
    return a[1] if a[0] <= b[0] else b[1]


_CHUNK = 16
"""Segments per box in `_line_chunks`: a planned line sampled every 8 ft is a few hundred segments, so a few dozen boxes -
measured on the pool's four streets against a `PointGrid` of the segments, which cost more to file each call than the
scan it saved (18.0 ms against the scan's 15.6 ms, feature 306)."""

_BOX_SLACK = 1e-6
"""A box's gap is a lower bound on any segment in it, but `seg_dist` rounds; a box is passed over only when its gap
exceeds the bound by more than this, so a rounding can never prune the segment that decides (feature 306)."""


def _line_chunks(line: Sequence[Pt]) -> list[tuple[int, int, float, float, float, float]]:
    """`line`'s segments in runs of `_CHUNK`, each as `(first, end, x0, y0, x1, y1)` - its segment indices `first..end-1` and
    the box of their vertices (feature 306)."""
    out = []
    for k0 in range(0, len(line) - 1, _CHUNK):
        k1 = min(k0 + _CHUNK, len(line) - 1)
        xs, ys = [p[0] for p in line[k0 : k1 + 1]], [p[1] for p in line[k0 : k1 + 1]]
        out.append((k0, k1, min(xs), min(ys), max(xs), max(ys)))
    return out


def _nearest_within(h: Pt, line: Sequence[Pt], chunks: Sequence[tuple[int, int, float, float, float, float]], reach: float) -> tuple[float, int]:
    """`(distance, index)` of the segment of `line` nearest `h`, the lower index on a tie as `min` over the whole line
    returned; where none is within `reach`, a distance over it - `(inf, -1)` when no box is near (feature 306). The boxes of `chunks` are read nearest first and
    one farther off than the best distance so far (or than `reach`) is passed over: no segment in it can be nearer, so
    none that decides is missed."""
    hx, hy = h
    gaps = []
    for k0, k1, x0, y0, x1, y1 in chunks:
        gap = math.hypot(max(x0 - hx, 0.0, hx - x1), max(y0 - hy, 0.0, hy - y1))
        if gap - _BOX_SLACK <= reach:
            gaps.append((gap, k0, k1))
    best = (math.inf, -1)
    for gap, k0, k1 in sorted(gaps):
        if gap - _BOX_SLACK > best[0]:
            break
        for i in range(k0, k1):
            best = min(best, (seg_dist(hx, hy, line[i], line[i + 1]), i))
    return best


def street_span(line: Sequence[Pt], houses: Sequence[Pt], reach: float, pad: float, brook: Sequence[Pt] = ()) -> list[Pt]:
    """The stretch of a planned street its farms stand along: from the first farm's projection less `pad` to the last's
    plus `pad`, over the farms within `reach` of the line, its run past an end farm stopped a ford's landing short of where
    the line crosses the `brook` (`brook_bounds`); [] when no farm is. The line's own vertices are kept, thinned to
    `_VERTEX_FT`.

    Research: street spans its farms - research/questions/0033-row-villages-resson.drawing.html, research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: from its first farm to its last, plus the run past them"""
    if len(line) < 2:
        return []
    arc = [0.0]
    for a, b in zip(line, line[1:], strict=False):
        arc.append(arc[-1] + math.dist(a, b))
    # EACH FARM ASKS ONLY THE STRETCH OF LINE NEAR IT (feature 306): it measured every segment of a line sampled every 8 ft -
    # 6,394 distances a call on the pool - when only the nearest within `reach` is kept. The line is boxed once in runs of
    # segments (`_line_chunks`) and a farm measures only the runs whose box could hold its nearest (`_nearest_within`). The
    # nearest is chosen as before, the lower index on a tie, so the pool's manifests regenerate byte-identical
    # (`tests/hamletgen/ways/test_street.py` holds it to the old scan).
    chunks = _line_chunks(line)
    along: list[float] = []
    for h in houses:
        best = _nearest_within(h, line, chunks, reach)
        if best[0] > reach:
            continue
        i = best[1]
        q = seg_closest(h[0], h[1], line[i], line[i + 1])
        along.append(arc[i] + math.dist(line[i], q))
    if not along:
        return []
    lo, hi = brook_bounds(line, arc, min(along), max(along), max(0.0, min(along) - pad), min(arc[-1], max(along) + pad), brook)
    idx = [i for i, u in enumerate(arc) if lo <= u <= hi]
    kept: list[int] = []
    for i in idx:
        if not kept or arc[i] - arc[kept[-1]] >= _VERTEX_FT:
            kept.append(i)
    if idx and kept[-1] != idx[-1]:
        kept.append(idx[-1])  # the stretch ends where its last farm does, not at the last whole vertex step
    return [line[i] for i in kept]


def brook_bounds(line: Sequence[Pt], arc: Sequence[float], first: float, last: float, lo: float, hi: float, brook: Sequence[Pt]) -> tuple[float, float]:
    """`lo` and `hi` (arc lengths along `line`, its cumulative lengths `arc`) drawn in to `FORD_LANDING_FT` short of the
    nearest crossing of `brook` beyond the end farms' projections `first` and `last` - never past those projections
    themselves, so the street still spans its farms.

    WHY. A planned street is a straight line fitted to the hard ground's edge, and its run past the end farm (`pad`, half a
    frame) is drawn wherever that line goes. Along a brook it went OVER the brook: on cohort seed 11 the line ran 11 degrees
    off the brook's course, the last farm's projection stood 12 ft short of the crossing, and the half frame past it took the
    street across 46 ft from the nearest ford. A street is a tree lane no settle may cut, so the crossing was squared in
    place (`checks.square_crossings`) into two 80 degree turns 21 ft apart - a kink - still off the ford, and the web was
    refused (`WebRefused`: bends, off_ford). A run past the last farm serves nothing over the water, so it stops a ford's
    landing short of the crossing along the line (a map drawing convention: the one figure the ways already keep between a
    way's turn and the brook), or at the end farm where the crossing is nearer than that (seed 11: 12 ft past it) - and the
    road runs out from there (`track.stage_track` reads the same span), over the brook at a ford as every way crosses it.
    A crossing BETWEEN farms is left to the street: its farms stand on both banks.

    Research: street end short of the brook - UNRESEARCHED: the run past an end farm stops a ford's landing short of a brook crossing"""
    if len(brook) < 2 or len(line) < 2:
        return lo, hi
    at = [arc[k] + math.dist(line[k], x) for k, x in law.crossing_points([(float(p[0]), float(p[1])) for p in line], [(float(p[0]), float(p[1])) for p in brook])]
    if beyond := [u for u in at if u >= last]:
        hi = max(last, min(hi, min(beyond) - FORD_LANDING_FT))
    if before := [u for u in at if u <= first]:
        lo = min(first, max(lo, max(before) + FORD_LANDING_FT))
    return lo, hi


def thread(path: Sequence[Pt], walls: Sequence[Poly], hard: list[Poly], water: list[tuple[Pt, Pt]], half: float = STREET_WIDTH / 2 + 1.0) -> list[Pt]:
    """`path` with every leg whose TREAD - `half` either side of the line - meets a steading replaced by a route round it
    (`_route`, a footpath's gap) between the clear vertices either side; a vertex whose tread meets one is dropped. The
    street stays one way. (Tested at the centerline, a street grazed a grove band with its drawn tread - cohort seed 904.)

    Research: street threaded round the steadings - research/questions/0081-village-lanes.drawing.html: nothing is built on a lane"""
    clear = [p for p in path if not _crosses_fabric([p, p], walls, half)]
    if len(clear) < 2:
        return list(clear)
    out: list[Pt] = [clear[0]]
    for a, b in zip(clear, clear[1:], strict=False):
        if _crosses_fabric([a, b], walls, half):
            # routed at the STREET's gap, not a footpath's: a detour at 4 ft ran 3 ft off a grove band, inside the 6 ft tread
            # (cohort seed 23); a leg still grazing is routed once more a foot wider
            leg = _route(a, b, hard, walls, water, gap=half + 1.0)
            if len(leg) >= 2 and _crosses_fabric(leg, walls, half):
                leg = _route(a, b, hard, walls, water, gap=half + 3.0)
            out += leg[1:] if len(leg) >= 2 else [b]
        else:
            out.append(b)
    return out


def join_to(path: list[Pt], network: Sequence[tuple[Pt, Pt]], hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]]) -> list[Pt]:
    """`path` extended from whichever of its ends is nearer the `network` to the nearest point on it, routed round the
    steadings; unchanged when the network is empty, already touched, or no route is found.

    Research: street joined to the network - research/questions/0081-village-lanes.drawing.html: one network"""
    if len(path) < 2 or not network:
        return path

    def near(p: Pt) -> tuple[float, Pt]:
        return min(((seg_dist(p[0], p[1], a, b), seg_closest(p[0], p[1], a, b)) for a, b in network), key=lambda t: t[0])

    (d0, q0), (d1, q1) = near(path[0]), near(path[-1])
    if min(d0, d1) < 1.0:
        return path
    if d0 <= d1:
        leg = _route(q0, path[0], hard, walls, water, gap=FOOTPATH_FABRIC_GAP)
        return (leg[:-1] + path) if len(leg) >= 2 else path
    leg = _route(path[-1], q1, hard, walls, water, gap=FOOTPATH_FABRIC_GAP)
    return (path + leg[1:]) if len(leg) >= 2 else path


def lay_row_streets(s: Settlement, houses: Sequence[Mapping[str, Any]], hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]], brook: Sequence[Pt] = ()) -> int:
    """Lay each planned street of `s._row_streets` as one way: its farms' stretch (`street_span`, short of the `brook` past
    its end farms), threaded round any steading in its way (`thread`), joined to the connector or a street already laid (`join_to`), drawn at the street's
    tread and recorded `street` with its index. Returns the streets drawn.

    Research:
        one street per planned row - research/questions/0033-row-villages-resson.drawing.html: further streets laid beside the first
        further street joins the streets - UNRESEARCHED: only the first street takes the road, a further one joins a street laid
        street join width - UNRESEARCHED: the join is drawn at the street's 6 ft tread
        street join unhooked - research/questions/0081-village-lanes.drawing.html: a lane's end loses its hook"""
    centers = [(float(h["x"]), float(h["y"])) for h in houses]
    # EACH STREET SPANS ITS OWN FARMS, as `seat_rows` seated them: spanned over every farm within reach, Mizuguchi's second
    # street, set out 238 ft behind the first row, took all twelve and ran 1,642 ft for the one farm of its own
    # (settlement-review, 2026-09-30)
    n = 0
    for k, _line in enumerate(getattr(s, "_row_streets", None) or []):
        path = thread(drawn_span(s, k, houses, brook), walls, hard, water)
        # A FURTHER STREET JOINS THE ROW'S STREETS, NOT THE ROAD: joined to the nearest of either, Mizuguchi's second street
        # met the connector at its head, 96 ft past the entrance board, and two of its farms left without passing the board
        # (settlement-review, 2026-09-30); only the first street takes the road
        laid = [ln for ln in s.M.get("lanes", []) if ln.get("street")]
        if not laid:
            road = next(([(float(x), float(y)) for x, y in ln["pts"]] for ln in s.M.get("lanes", []) if ln.get("connector")), [])
            path = meet_the_road(path, road)
        net = [(tuple(a), tuple(b)) for ln in (laid or [ln for ln in s.M.get("lanes", []) if ln.get("connector")]) for a, b in zip(ln["pts"], ln["pts"][1:], strict=False)]
        joined = join_to(path, net, hard, walls, water)  # type: ignore[arg-type]
        if len(path) >= 2 and _draw_web(s, path, STREET_WIDTH, houses=centers):
            s.M["lanes"][-1]["street"] = True
            s.M["lanes"][-1]["street_index"] = k
            n += 1
            # ...AND ITS JOIN TO THE NETWORK IS A WAY OF ITS OWN, the road's rank but no row's street (`street_index` None):
            # drawn as part of the street, a 600 ft link from a second street's end across the first row counted as that
            # street, and a first-row farm beside it was judged to stand behind the second row's farms (cohort seed 904)
            # ...WITHOUT A HOOK AT EITHER END, and only where the law would keep it: the join is a tree lane no settle repair
            # cuts, and one that left the street by a 7 ft leg turning back was a hook and a needle the web was refused for
            # (feature 291 on 287, cohort seed 901)
            leg = unhooked_both(join_leg(path, joined))
            lawful = Lawful(s, tree=True)
            if len(leg) < 2 or not lawful(leg, STREET_WIDTH):
                # ...ELSE THE LAWFUL JOIN FROM EITHER END, searched as a door path is (`serve.door_path`): a second street of one
                # farm whose nearest join the law refused was left unjoined and its farm unreached (cohort seed 904)
                leg = next((j for e in (path[-1], path[0]) if (j := door_path(s, e, net, hard, walls, water, [], lawful)) is not None), [])  # type: ignore[arg-type]
            if len(leg) >= 2 and _draw_web(s, leg, STREET_WIDTH, houses=centers, joins=True):
                s.M["lanes"][-1]["street"] = True
                s.M["lanes"][-1]["street_index"] = None
    return n


MEET_THE_ROAD_FT = 60.0
"""How far short of the road's start a row's first street may end and be carried on to it rather than joined by a lane of its
own (a map drawing convention: the road runs on from the street's end, `street.street_run_out`).

Research: street carried on to the road - research/questions/0033-row-villages-resson.drawing.html: within 60 ft of the road's start"""


def meet_the_road(street: Sequence[Pt], road: Sequence[Pt], reach: float = MEET_THE_ROAD_FT) -> list[Pt]:
    """The row's first street carried on to the road's start where it ends within `reach` of it, so the two meet end to end as
    one way - else as it is. Joined by a lane of its own, the gap's join lay back along the road once a later pass carried the
    road's end onto it: the street ran on beside the road, a doubled tail no settle may cut, both being tree lanes (feature
    291 on 287, Kashikawa).

    Research: street and road meet end to end - research/questions/0033-row-villages-resson.drawing.html: the street runs on as the road"""
    if len(street) < 2 or len(road) < 2:
        return list(street)
    r0 = road[0]
    d0, d1 = math.dist(street[0], r0), math.dist(street[-1], r0)
    if min(d0, d1) < 1.0 or min(d0, d1) > reach:
        return list(street)
    return [r0, *street] if d0 < d1 else [*street, r0]


def unhooked_both(leg: Sequence[Pt]) -> list[Pt]:
    """`leg` with a hook taken off either end (`geom.door_unhooked`, asked of the leg and of it reversed).

    Research: lane end loses its hook - research/questions/0081-village-lanes.drawing.html"""
    from .geom import door_unhooked

    out = door_unhooked(list(leg), lambda a, b: True)  # every straightened leg is the join's own ground: judged whole after
    return door_unhooked(out[::-1], lambda a, b: True)[::-1] if len(out) >= 2 else out


def join_leg(path: Sequence[Pt], joined: Sequence[Pt]) -> list[Pt]:
    """The leg `join_to` added to `path` (at whichever end), from the street's end to the network; [] where none was."""
    if len(joined) <= len(path):
        return []
    if list(joined[: len(path)]) == list(path):
        return list(joined[len(path) - 1 :])
    return list(joined[: len(joined) - len(path) + 1])


def to_its_joints(street: Sequence[Pt], ends: Sequence[Pt], touch: float) -> list[Pt]:
    """A street cut back to the stretch between its outermost joints - the points on it nearest each other lane end within
    `touch` of it (a farm's door path, the join, the road run on from it) - or as it is where fewer than one joint stands on
    it. Past its last farm's path a street serves nothing the lane law counts (`end_serves`: a farmhouse stands most of a
    frame off its street), and the settle refuses a tree lane with a dangling end (feature 291 on 287, Mizuguchi).

    Research: street cut to its outermost joints - research/questions/0081-village-lanes.drawing.html: an end reaching nothing is pulled back"""
    arc, at = joints_along(street, ends, touch)
    if not at:
        return list(street)
    lo, hi = min(at), max(at)
    return cut_between(street, arc, lo, hi)


def nearest_on(line: Sequence[Pt], p: Pt) -> Pt | None:
    """The point of the polyline `line` nearest `p`; None for a line of fewer than two points."""
    if len(line) < 2:
        return None
    return min((seg_closest(p[0], p[1], a, b) for a, b in zip(line, line[1:], strict=False)), key=lambda q: math.dist(q, p))


def joints_along(street: Sequence[Pt], ends: Sequence[Pt], touch: float) -> tuple[list[float], list[float]]:
    """The street's cumulative lengths, and the arc length along it of each lane end in `ends` within `touch` of it."""
    arc = [0.0]
    for a, b in zip(street, street[1:], strict=False):
        arc.append(arc[-1] + math.dist(a, b))
    at: list[float] = []
    for e in ends:
        best = min(((seg_dist(e[0], e[1], a, b), k) for k, (a, b) in enumerate(zip(street, street[1:], strict=False))), default=(math.inf, 0))
        if best[0] <= touch:
            a, b = street[best[1]], street[best[1] + 1]
            q = seg_closest(e[0], e[1], a, b)
            at.append(arc[best[1]] + math.dist(a, q))
    return arc, at


def end_to_its_joint(street: Sequence[Pt], ends: Sequence[Pt], touch: float, end: int) -> list[Pt]:
    """The street's `end` (-1 its last point, 0 its first) cut back to the joint nearest it (`to_its_joints`' outermost
    joint on that side), the other end left as it is; the street as it is where no joint stands on it. The settle asks it of
    a street end the lane law calls dangling (`settle_dangling`).

    Research: street end cut to its joint - research/questions/0081-village-lanes.drawing.html: an end reaching nothing is pulled back"""
    arc, at = joints_along(street, ends, touch)
    if not at:
        return list(street)
    return cut_between(street, arc, 0.0, max(at)) if end == -1 else cut_between(street, arc, min(at), arc[-1])


def cut_between(pts: Sequence[Pt], arc: Sequence[float], lo: float, hi: float) -> list[Pt]:
    """The polyline `pts` (its cumulative lengths `arc`) from arc length `lo` to `hi`."""

    def at(u: float) -> Pt:
        k = max(0, min(len(pts) - 2, next((j for j in range(len(pts) - 1) if arc[j + 1] >= u), len(pts) - 2)))
        seg = arc[k + 1] - arc[k] or 1.0
        f = (u - arc[k]) / seg
        return (pts[k][0] + (pts[k + 1][0] - pts[k][0]) * f, pts[k][1] + (pts[k + 1][1] - pts[k][1]) * f)

    inner = [p for p, u in zip(pts, arc, strict=True) if lo < u < hi]
    return [at(lo), *inner, at(hi)]


def trim_streets(s: Settlement, touch: float, doors: Sequence[Pt] = (), reach: float = 0.0) -> int:
    """Every planned street of a row (`street_index` set) cut to its joints (`to_its_joints`) - and to the nearest point of
    each front door in `doors` within `reach` of it, a farm the street serves without a path of its own (`lay_door_paths`
    lays none within that reach): cut to its paths' joints alone, Mizuguchi's street stopped a frame short of its end farm,
    whose door stood 12 ft off it, and the farm was left off every way (2026-10-01). Returns the streets cut.

    Research: street cut to its joints - research/questions/0081-village-lanes.drawing.html: pulled back to the last way or door it serves"""
    lanes = s.M.get("lanes") or []
    n = 0
    for i, ln in enumerate(lanes):
        if ln.get("street_index") is None or len(ln.get("pts") or []) < 2:
            continue
        pts = [(float(x), float(y)) for x, y in ln["pts"]]
        ends = [(float(o["pts"][e][0]), float(o["pts"][e][1])) for j, o in enumerate(lanes) if j != i and len(o.get("pts") or []) >= 2 for e in (0, -1)]
        ends += [q for d in doors if (q := nearest_on(pts, d)) is not None and math.dist(q, d) <= reach]
        cut = to_its_joints(pts, ends, touch)
        if len(cut) >= 2 and cut != pts and s.reshape_lane(ln, cut):
            s.reink_lane(i)
            n += 1
    return n
