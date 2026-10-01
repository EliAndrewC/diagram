"""THE ROW VILLAGE'S STREETS (feature 291 amendment 3, plan D17; research/homesteads/155 and 156) - each street the row
seating planned (`homesteads/rows.py`, `s._row_streets`) laid as ONE continuous way along its row, a rank wider than
the lanes off it, joined to the connector or to the street before it; and each row farm's way ending on its OWN street.

A layer between `serve` (the door paths) and `web` (the stage that calls it).
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, seg_closest, seg_dist

from ..consts import FOOTPATH_FABRIC_GAP, Poly, Pt
from .fabric import _crosses_fabric, _draw_web
from .route import _route
from .serve import door_path
from .settle import Lawful

STREET_WIDTH = 6
"""The street's tread: the connector's, a rank wider than the web's 3-5 lanes (FR-017)."""

_VERTEX_FT = 40.0
"""The street's vertex spacing once laid: the planned line is sampled every 8 ft; a worn way keeps a vertex every two
treads' lengths or so - a map drawing convention."""


def street_span(line: Sequence[Pt], houses: Sequence[Pt], reach: float, pad: float) -> list[Pt]:
    """The stretch of a planned street its farms stand along: from the first farm's projection less `pad` to the last's
    plus `pad`, over the farms within `reach` of the line; [] when no farm is. The line's own vertices are kept, thinned to
    `_VERTEX_FT`."""
    if len(line) < 2:
        return []
    arc = [0.0]
    for a, b in zip(line, line[1:], strict=False):
        arc.append(arc[-1] + math.dist(a, b))
    along: list[float] = []
    for h in houses:
        best = min(((seg_dist(h[0], h[1], a, b), i) for i, (a, b) in enumerate(zip(line, line[1:], strict=False))), key=lambda t: t[0])
        if best[0] > reach:
            continue
        i = best[1]
        q = seg_closest(h[0], h[1], line[i], line[i + 1])
        along.append(arc[i] + math.dist(line[i], q))
    if not along:
        return []
    lo, hi = max(0.0, min(along) - pad), min(arc[-1], max(along) + pad)
    idx = [i for i, u in enumerate(arc) if lo <= u <= hi]
    kept: list[int] = []
    for i in idx:
        if not kept or arc[i] - arc[kept[-1]] >= _VERTEX_FT:
            kept.append(i)
    if idx and kept[-1] != idx[-1]:
        kept.append(idx[-1])  # the stretch ends where its last farm does, not at the last whole vertex step
    return [line[i] for i in kept]


def thread(path: Sequence[Pt], walls: Sequence[Poly], hard: list[Poly], water: list[tuple[Pt, Pt]], half: float = STREET_WIDTH / 2 + 1.0) -> list[Pt]:
    """`path` with every leg whose TREAD - `half` either side of the line - meets a steading replaced by a route round it
    (`_route`, a footpath's gap) between the clear vertices either side; a vertex whose tread meets one is dropped. The
    street stays one way. (Tested at the centerline, a street grazed a grove band with its drawn tread - cohort seed 904.)"""
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
    steadings; unchanged when the network is empty, already touched, or no route is found."""
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


def lay_row_streets(s: Settlement, houses: Sequence[Mapping[str, Any]], hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]], reach: float, pad: float) -> int:
    """Lay each planned street of `s._row_streets` as one way: its farms' stretch (`street_span`), threaded round any
    steading in its way (`thread`), joined to the connector or a street already laid (`join_to`), drawn at the street's
    tread and recorded `street` with its index. Returns the streets drawn."""
    centers = [(float(h["x"]), float(h["y"])) for h in houses]
    # EACH STREET SPANS ITS OWN FARMS, as `seat_rows` seated them: spanned over every farm within reach, Mizuguchi's second
    # street, set out 238 ft behind the first row, took all twelve and ran 1,642 ft for the one farm of its own
    # (settlement-review, 2026-09-30)
    own = getattr(s, "_row_street_farms", None) or []
    n = 0
    for k, line in enumerate(getattr(s, "_row_streets", None) or []):
        path = thread(street_span(line, own[k] if k < len(own) else centers, reach, pad), walls, hard, water)
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
own (a map drawing convention: the road runs on from the street's end, `track.street_run_out`)."""


def meet_the_road(street: Sequence[Pt], road: Sequence[Pt], reach: float = MEET_THE_ROAD_FT) -> list[Pt]:
    """The row's first street carried on to the road's start where it ends within `reach` of it, so the two meet end to end as
    one way - else as it is. Joined by a lane of its own, the gap's join lay back along the road once a later pass carried the
    road's end onto it: the street ran on beside the road, a doubled tail no settle may cut, both being tree lanes (feature
    291 on 287, Kashikawa)."""
    if len(street) < 2 or len(road) < 2:
        return list(street)
    r0 = road[0]
    d0, d1 = math.dist(street[0], r0), math.dist(street[-1], r0)
    if min(d0, d1) < 1.0 or min(d0, d1) > reach:
        return list(street)
    return [r0, *street] if d0 < d1 else [*street, r0]


def unhooked_both(leg: Sequence[Pt]) -> list[Pt]:
    """`leg` with a hook taken off either end (`geom.door_unhooked`, asked of the leg and of it reversed)."""
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
    frame off its street), and the settle refuses a tree lane with a dangling end (feature 291 on 287, Mizuguchi)."""
    arc, at = joints_along(street, ends, touch)
    if not at:
        return list(street)
    lo, hi = min(at), max(at)
    return cut_between(street, arc, lo, hi)


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
    a street end the lane law calls dangling (`settle_dangling`)."""
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


def trim_streets(s: Settlement, touch: float) -> int:
    """Every planned street of a row (`street_index` set) cut to its joints (`to_its_joints`); returns the streets cut."""
    lanes = s.M.get("lanes") or []
    n = 0
    for i, ln in enumerate(lanes):
        if ln.get("street_index") is None or len(ln.get("pts") or []) < 2:
            continue
        pts = [(float(x), float(y)) for x, y in ln["pts"]]
        ends = [(float(o["pts"][e][0]), float(o["pts"][e][1])) for j, o in enumerate(lanes) if j != i and len(o.get("pts") or []) >= 2 for e in (0, -1)]
        cut = to_its_joints(pts, ends, touch)
        if len(cut) >= 2 and cut != pts and s.reshape_lane(ln, cut):
            s.reink_lane(i)
            n += 1
    return n
