"""Split from settlement/water_ways.py by feature 173 - see this package's CLAUDE.md for the index.

Research: lane geometry - NONE
"""

import math
from typing import TYPE_CHECKING, Any

from .._geom import (
    Pt,
    edge_dist,
    point_in_poly,
    rot_rect,
    seg_dist,
)

if TYPE_CHECKING:
    pass


_FRAY_DEG = 20.0  # below this the two ways are the same track fraying, not a junction (see trim_lane_stubs)
"""Research: fraying track - UNRESEARCHED: two ways meeting under 20 degrees are one track, not a junction"""


def _angle_between(run: Any, other: Any) -> float:
    """The acute angle in degrees between two segments, 0 = parallel (either direction)."""
    (ax, ay), (bx, by) = run
    (cx, cy), (dx, dy) = other
    u, v = (bx - ax, by - ay), (dx - cx, dy - cy)
    lu, lv = math.hypot(*u), math.hypot(*v)
    if lu < 1e-9 or lv < 1e-9:
        return 90.0
    cos = abs(u[0] * v[0] + u[1] * v[1]) / (lu * lv)
    return math.degrees(math.acos(max(0.0, min(1.0, cos))))


_LANE_MIN_FT = 71.0  # one homestead's frontage: below this a lane can front nobody (see trim_lane_stubs)
"""Research: shortest lane - UNRESEARCHED: an internal lane under 71 ft, one homestead's frontage, is dropped"""

# A LANE THAT SERVES A FARMHOUSE ENDS AT ITS DOORYARD (269 B17, research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html - "a lane that serves a farmhouse
# ends at that house's dooryard, or runs on to reach something a reader can see"; how close counts as serving is the
# record's GUESS). It was 90 ft to the house's CENTER here, which let an end run 60 ft past the last steading into the
# grass. The figure is hamletgen's `STEADING_ARRIVAL_FT`, derived there from the clip (a tread that reaches a plot records
# its last point 7-11 ft off it), and a test holds the two equal; the settlement engine cannot import the scripted tier.
DOORYARD_REACH_FT = 12.0
"""Research: dooryard reach - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: an end within 12 ft of the yard or beds serves the house"""
# ...or stands beside the house, within this of its center and not past it: the scripted tier's `WAY_END_REACH_FT`, the gate's
# own reach for an end (a test holds the two equal). It was 90 here, the looser figure feature 227 retired everywhere else.
HOUSE_SERVE_FT = 60.0
"""Research: beside-the-house reach - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: an end within 60 ft of the house's center, not past it, serves it"""
# An end has walked past a house when the foot of the perpendicular from the house falls more than this far back along
# its last segment - the 4 ft grain `_trim_to_service` walks in, and the `_stop_at_closest_approach` cut's own.
PAST_GRAIN_FT = 4.0
# ...OR RUNS ON TO THE BUND (269 B04/B17, research/questions/0014-bunds-between-the-paddies-aze.drawing.html - "the field path runs from the hamlet to the paddy's outer
# bund and joins it ... it never ends in open ground short of the bund"). An end has arrived when its centerline stops
# within a bund's width (~1.5 ft) and the widest lane's half-tread (3 ft) of the worked ground's edge, with a foot and a
# half of drawing margin: the cap of the tread then lies on the bund line. A map drawing convention.
BUND_REACH_FT = 6.0
"""Research: arrival at the bund - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: an end within 6 ft of the worked ground's edge has arrived"""


def walked_past(prev: Pt, q: Pt, house: Pt) -> bool:
    """Has a tread arriving at `q` from `prev` walked on past `house` - does the foot of the perpendicular from the house
    fall more than `PAST_GRAIN_FT` back from the end (269 B17)?"""
    dx, dy = q[0] - prev[0], q[1] - prev[1]
    d2 = dx * dx + dy * dy
    if d2 <= 0.0:
        return False
    t = ((house[0] - prev[0]) * dx + (house[1] - prev[1]) * dy) / d2
    return t < 1.0 and (1.0 - max(t, 0.0)) * math.sqrt(d2) > PAST_GRAIN_FT


def vertex_behind(q: Pt, pts: Any) -> Pt:
    """The vertex of `pts` a point `q` lying on it was walked to from: the start of the segment nearest `q`, the last such
    on a tie - so a pulled-back end is judged along the segment it now stands on, not the one it was cut from."""
    k = min(range(1, len(pts)), key=lambda j: (seg_dist(q[0], q[1], pts[j - 1], pts[j]), -j))
    return (float(pts[k - 1][0]), float(pts[k - 1][1]))


def dooryard_dist(house: Any, q: Pt) -> float:
    """How far `q` stands from a farmhouse's dooryard - its drawn footprint, its threshing yard and its garden beds, each
    turned with the house (the record's `geom`, 269 B18); zero inside one. A house with no bundle is its footprint alone.
    GAP VERDICT family: the drawn quads, never the center."""
    rot = float(house.get("rot") or 0.0)
    g = house.get("geom") or {}
    rects = [(house["x"], house["y"], house["w"], house["h"])] + [g[k] for k in ("yard", "shed") if g.get(k) is not None] + list(g.get("gardens") or ())
    best = float("inf")
    for r in rects:
        quad = rot_rect(float(r[0]), float(r[1]), float(r[2]), float(r[3]), rot)
        if point_in_poly(q[0], q[1], quad):
            return 0.0
        best = min(best, edge_dist(q[0], q[1], quad))
    return best


def _lane_len(pts: list[Pt]) -> float:
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:], strict=False))


def _pull_back(pts: list[Pt], reaches: Any, step: float = 8.0, min_len: float = 0.0) -> list[Pt]:
    """Shorten a polyline from its LAST vertex until that end reaches something, or the guard stops it.

    Walks the final segment inward in `step` px, dropping a whole vertex when one is consumed and
    more than two remain, as far as the end still reaches something - back to the last thing the lane
    serves (0246), however far that is - never past a junction (`min_len`) and never below two points.
    A lane whose whole run serves nothing is left whole: a siting problem, not something to delete -
    the map still needs the way it drew, and silently removing one would trade a visible stub for an
    invisible missing lane. (A 40% floor held the trim until feature 328 wave 66: it stopped a lane
    short of the last house it serves, where 0246 pulls it back to that house.)

    Research:
        end pulled back to what it serves - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: to the shortest end that still reaches something
        no trim floor - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: pulled back as far as the last house it serves, held only at a junction; a lane reaching nothing at all is left whole (no house to pull it back to)
    """
    # `min_len` is the one floor, the one a junction sets - see `_junction_floor`: a lane may not be trimmed past a way that
    # ties into it, whatever fraction of its length that leaves
    floor = min_len
    out = list(pts)
    best: list[Pt] | None = None  # the SHORTEST end seen that still reaches the last thing served
    served: Any = None  # what the end reached first, walking back - the last thing the lane serves
    while len(out) >= 2:
        a, b = out[-2], out[-1]
        seg = math.hypot(b[0] - a[0], b[1] - a[1])
        if seg <= step:
            if len(out) == 2:
                break
            out.pop()
            continue
        t = (seg - step) / seg
        cand = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        trial = [*out[:-1], cand]
        if sum(math.hypot(q[0] - r[0], q[1] - r[1]) for q, r in zip(trial, trial[1:], strict=False)) < floor:
            break
        out = trial
        # STOP AT THE LAST THING SERVED, not at the predicate's EDGE. Returning the first point that
        # reaches anything leaves the tread ending on the 90 ft radius of a farmhouse center - i.e.
        # ~60 ft clear of that homestead's own footprint, petering out in grass (both the Kashikawa
        # and Sawada reviews raised it independently). Walking on while it STILL reaches, and keeping
        # the shortest such point, ends the lane at the homestead instead - and where the end also
        # ran alongside a sibling arm, it shortens that parallel run by the same amount.
        got = reaches(cand)
        if got and (served is None or got == served):
            best, served = list(trial), (got if served is None else served)
        elif best is not None:
            # PAST THE LAST THING SERVED, walking back: the end stops there (0246) - not at whatever lies nearer the start,
            # and not at the next house along where reach zones chain (a predicate that NAMES what it reached is held to the
            # first thing named; one that answers only yes or no to any reaching run)
            break
    # NO REACHING END FOUND MEANS LEAVE THE LANE ALONE, not "return the floor-truncated one". `out`
    # at this point is the run cut back as far as the guard allowed, and its end reaches nothing by
    # construction - so returning it MANUFACTURES the exact defect `lanes_reach_something` exists to
    # catch: a tread stopping in bare grass. Measured on cohort seed 26, where an end that reached a
    # way at 31 ft and a house at 46 ft was pulled back (the fan rule: the house was a rival's to
    # claim) to a point 59 ft from any way and 156 ft from any house. The docstring already says a
    # lane serving nothing is "a siting problem, not something to delete"; shortening it to an
    # arbitrary floor is the same mistake as deleting it, only harder to see.
    return best if best is not None else list(pts)


def junction_floor(pts: list[Pt], lanes: Any, drop: Any, way_reach: float, me: int) -> float:
    """How much of a lane may NOT be trimmed away, because another way ties into it.

    AN END THAT CARRIES A JUNCTION IS NOT BLUNT - holding the network together is its own reason to
    exist. `_pull_back` keeps the SHORTEST end that reaches something, so without this it happily
    cuts past a tie point and orphans whatever was tied on. Measured on Mizuguchi: the trim cut 160 ft
    off a lane, taking its junction with it, the orphan-healer then re-laid the same alignment as a
    3 ft web path, and the street came out stroked 5 / 3 / 5 with a round-cap knuckle at the step - a
    repair scar in open ground, which a review read at 2x as a lollipop knob mid-street.

    Walking from the START, `keep` is the distance to the FURTHEST tie found, so everything up to the
    last junction is protected and anything past it may go.

    AND IT HAS TO BE A CROSSING, NOT A NEIGHBOR - the `_FRAY_DEG` rule again. Counting proximity alone
    made every point of a near-parallel arm look like a tie, so the floor came out at the full length
    and nothing could be trimmed at all. A CONTINUATION - two lanes meeting end to end at a shallow
    angle - is deliberately NOT protected here, though it is a real tie: protecting it was tried and it
    deadlocks against the fan rule on a map where the two tines of the fan are themselves a
    continuation - the arm cannot be trimmed without cutting the street, and the fan cannot be cleared
    without trimming the arm. The repair scar that motivated the attempt was a WIDTH problem, not a
    trim problem, and is fixed where the width is chosen instead.

    Lifted out of `trim_lane_stubs`'s closure so it can be asked with plain lists (GM 2026-08-28 on
    testability); the inner one delegates here, so there is ONE body.

    Research:
        junction kept - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: one network; a trim never cuts past a junction
        a crossing at 20 degrees - UNRESEARCHED: a way crossing the lane at 20 degrees or more counts as a junction
    """
    acc, keep = 0.0, 0.0
    for n in range(len(pts) - 1):
        acc += math.dist(pts[n], pts[n + 1])
        q = pts[n + 1]
        for k, o in enumerate(lanes):
            if k == me or k in drop or len(o["pts"]) < 2:
                continue
            op = [(float(x), float(y)) for x, y in o["pts"]]
            seg = min(zip(op, op[1:], strict=False), key=lambda ab, _q=q: seg_dist(_q[0], _q[1], ab[0], ab[1]))
            if seg_dist(q[0], q[1], seg[0], seg[1]) > way_reach:
                continue
            if _angle_between((pts[n], q), seg) >= _FRAY_DEG:
                keep = acc
                break
    return keep


def fan_rival(lanes: Any, q: Pt, bearing: float, house: Pt, mine: float, me: int, fan_spread: float, fan_bearing: float) -> bool:
    """Is another lane's end already fanning to this house on this bearing? A second stub arriving beside the
    first, within `fan_spread` of it and within `fan_bearing` degrees of the same heading, is the same
    approach drawn twice rather than two ways.

    LIFTED OUT OF `trim_lane_stubs` (feature 146, GM 2026-08-28 on making inner functions testable): it took
    only these values from the closure, and a test can now hand it two lane dicts instead of building a
    settlement whose web happens to fan.

    Research: one approach per house - UNRESEARCHED: a second end within the fan spread and bearing of another is the same approach drawn twice"""
    for k, other in enumerate(lanes):
        if k == me or len(other.get("pts") or []) < 2:
            continue
        op = [(float(x), float(y)) for x, y in other["pts"]]
        for tip, prev in ((op[0], op[1]), (op[-1], op[-2])):
            if math.dist(tip, q) > fan_spread or math.hypot(tip[0] - house[0], tip[1] - house[1]) >= mine:
                continue
            b = math.degrees(math.atan2(tip[1] - prev[1], tip[0] - prev[0]))
            if abs((bearing - b + 180.0) % 360.0 - 180.0) <= fan_bearing:
                return True
    return False
