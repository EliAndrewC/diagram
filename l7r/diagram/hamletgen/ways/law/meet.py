"""the lane law where lanes MEET: folded joints, hairpins, needles, doubled tails, joins that stop short, slivers, fragments, width steps, one network (split from `law.py` at the 1,000-line bar, feature 417 T54).

Research: plumbing and wrappers - NONE: each rule is claimed at the predicate that decides it
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import seg_closest, seg_dist, segments_cross
from l7r.diagram.settlement._knobs import bridge_crossed_waters
from l7r.diagram.settlement.city.bridges import DECK_SPAN_DEFAULT_FT as DECK_SPAN_DEFAULT_FT
from l7r.diagram.settlement.city.bridges import PLANK_DITCH_FT as PLANK_DITCH_FT
from l7r.diagram.settlement.city.bridges import deck_covers as deck_covers
from l7r.diagram.settlement.city.bridges import undeckable_at as undeckable_at
from l7r.diagram.settlement.rolling.access import TREAD_HALF_FT
from l7r.diagram.work_counts import OPS

from ...consts import WEB_FABRIC_GAP, Poly, Pt
from ..clearance import kink_spans
from ..fabric import _crosses_fabric, house_hit
from ..forced import Blocked, forced_meeting, forced_turn
from ..geom import _components, _seg_cross, _turn_deg, polyline_len
from ..joints import at_rank, hairpin_over_a_short_leg, joints, oriented
from ..law_water import (
    _bbox as _bbox,
)
from ..law_water import (
    _min_dist as _min_dist,
)
from ..law_water import (
    _ways as _ways,
)
from ..law_water import (
    boxes_meet as boxes_meet,
)
from ..law_water import (
    lane_pts as lane_pts,
)
from ..tails import tail_doubled
from .shape import (
    AIM_DEG,
    CONNECTOR_START_FT,
    DOUBLE_BACK_DEG,
    JOIN_REACH_FT,
    JOIN_TOL,
    NEEDLE_DEG,
    NEEDLE_FT,
    Lanes,
    hooked,
)

# ---- where lanes meet ----------------------------------------------------------------------------------------------


def folded_joint_pairs(lanes: Lanes, blocked: Blocked | None = None) -> list[tuple[int, int, int, int]]:
    """The joints (`joints`: `(i, end_i, j, end_j)`) where two lanes meeting end to end - one way to the walker - turn
    more than `DOUBLE_BACK_DEG`.
    Research:
        lanes met end to end are one - research/questions/0081-village-lanes.drawing.html: no hairpin at the joint
        a forced turn is lawful - research/questions/0081-village-lanes.drawing.html: "A turn the ground forces is drawn as walked" - a fold whose chord the ground blocks is excused"""
    out = []
    for i, ei, j, ej in joints(lanes):
        x, y = oriented(lanes, i, ei, j, ej)
        if _turn_deg(x[-2], x[-1], y[1]) >= DOUBLE_BACK_DEG and not forced_turn(blocked, x[-2], y[1], float(lanes[i].get("w") or 3.0)):
            out.append((i, ei, j, ej))
    return out


def folded_joints(lanes: Lanes, blocked: Blocked | None = None) -> list[tuple[int, int]]:
    """Where two lanes meeting end to end turn `DOUBLE_BACK_DEG` or more at the joint (`folded_joint_pairs`)."""
    out = []
    for i, ei, j, ej in folded_joint_pairs(lanes, blocked):
        x, _y = oriented(lanes, i, ei, j, ej)
        out.append((round(x[-1][0]), round(x[-1][1])))
    return out


def connector_hairpin_ends(lanes: Lanes, blocked: Blocked | None = None) -> list[tuple[int, int, int]]:
    """(connector index, lane index, end) wherever a lane's short last leg meets the connector's start and the two double
    back (`hairpin_over_a_short_leg`); the end is -1 (the lane's last point) or 0 (its first).
    Research:
        no hairpin at the track - research/questions/0081-village-lanes.drawing.html: over a returning leg under 40 ft
        a forced turn is lawful - research/questions/0081-village-lanes.drawing.html: "A turn the ground forces is drawn as walked" - a hairpin at the track whose chord the ground blocks is excused"""
    out = []
    for ci, co in enumerate(lanes):
        cp = lane_pts(co)
        if not co.get("connector") or len(cp) < 2:
            continue
        for i, ln in enumerate(lanes):
            p = lane_pts(ln)
            if ln.get("connector") or len(p) < 3:
                continue
            for end, seq in ((-1, p), (0, p[::-1])):
                a, b, j = seq[-3], seq[-2], seq[-1]
                if math.dist(j, cp[0]) <= CONNECTOR_START_FT and hairpin_over_a_short_leg(a, b, j, cp[1]) and not forced_turn(blocked, b, cp[1], float(ln.get("w") or 3.0)):
                    out.append((ci, i, end))
    return out


def connector_hairpins(lanes: Lanes, blocked: Blocked | None = None) -> list[tuple[int, int]]:
    """Where a lane's short last leg meets the connector's start and the two double back (`connector_hairpin_ends`)."""
    return [(round(lane_pts(lanes[i])[end][0]), round(lane_pts(lanes[i])[end][1])) for _ci, i, end in connector_hairpin_ends(lanes, blocked)]


def _tread_bearings(q: Pt, u: Pt, v: Pt) -> list[Pt]:
    """The unit directions a tread u-v runs from the point on it nearest `q` - toward each end it still extends to."""
    L2 = (v[0] - u[0]) ** 2 + (v[1] - u[1]) ** 2
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((q[0] - u[0]) * (v[0] - u[0]) + (q[1] - u[1]) * (v[1] - u[1])) / L2))
    foot = (u[0] + t * (v[0] - u[0]), u[1] + t * (v[1] - u[1]))
    out = []
    for e in (u, v):
        d = math.dist(foot, e)
        if d >= 1.0:
            out.append(((e[0] - foot[0]) / d, (e[1] - foot[1]) / d))
    return out


def needle_ends(lanes: Lanes, blocked: Blocked | None = None) -> list[tuple[int, int, int, Pt, Pt]]:
    """(lane index, end, tread lane index, u, v) wherever a lane's end leg, longer than `NEEDLE_FT`, meets another way's tread `u`-`v`
    (within `JOIN_TOL`) and runs back along it at under `NEEDLE_DEG` - a needle rather than a T. A leg carrying straight on
    from a way's END is not a needle: the tread it meets does not run back beside it. The end is -1 (last) or 0 (first).
    Research:
        a lane meets another as a T - research/questions/0081-village-lanes.drawing.html: never a needle
        a forced turn is lawful - research/questions/0081-village-lanes.drawing.html: "A turn the ground forces is drawn as walked" - a needle whose sliver the ground blocks is excused
        needle leg - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A2, 2026-10-25); only an end leg over NEEDLE_FT, 20 ft, can be a needle; shorter is the approach to the junction"""
    ways = [lane_pts(ln) for ln in lanes]
    out = []
    for i, ln in enumerate(lanes):
        p = ways[i]
        if ln.get("connector") or len(p) < 2:
            continue
        for end, q, b in ((-1, p[-1], p[-2]), (0, p[0], p[1])):
            leg = math.dist(q, b)
            if leg <= NEEDLE_FT:
                continue
            back = ((b[0] - q[0]) / leg, (b[1] - q[1]) / leg)
            for k, o in enumerate(ways):
                if k == i or len(o) < 2:
                    continue
                for u, v in zip(o, o[1:], strict=False):
                    # ...each tread leg by its box first (feature 417 T06): one whose box stands beyond the tolerance is beyond it,
                    # the same verdict (every end against every leg of every way: 246,213 `seg_dist` on seed 39 at 40 households)
                    if (
                        (u[0] - JOIN_TOL > q[0] and v[0] - JOIN_TOL > q[0])
                        or (u[0] + JOIN_TOL < q[0] and v[0] + JOIN_TOL < q[0])
                        or (u[1] - JOIN_TOL > q[1] and v[1] - JOIN_TOL > q[1])
                        or (u[1] + JOIN_TOL < q[1] and v[1] + JOIN_TOL < q[1])
                    ):
                        continue
                    if seg_dist(q[0], q[1], u, v) > JOIN_TOL:
                        continue
                    if any(math.degrees(math.acos(max(-1.0, min(1.0, back[0] * d[0] + back[1] * d[1])))) < NEEDLE_DEG for d in _tread_bearings(q, u, v)) and not forced_meeting(
                        blocked, q, b, u, v, float(ln.get("w") or 3.0)
                    ):
                        out.append((i, end, k, u, v))
    return out


def shallow_crossing_at(lanes: Lanes) -> list[tuple[int, int, int, Pt]]:
    """(lane, its segment, other way, the crossing point) wherever two ways cross each other at under `NEEDLE_DEG` - two
    paths side by side, the one wandering over the other, which a walker would wear into one (feature 385 T01, plan D4:
    cohort seed 10 under the wave 155 re-deal, a household's way crossing the field way at about 19 degrees and running on
    beside it to the field way's start). Each crossing is named once, at the lower-numbered lane of the two. A crossing on an
    end is a meeting, not a crossing (`needle_ends` reads it).
    Research: two paths side by side become one - research/questions/0081-village-lanes.drawing.html: "Two paths running side by side are drawn as one" - a lane wandering over another way at under NEEDLE_DEG"""
    ways = [lane_pts(ln) for ln in lanes]
    out = []
    for i, p in enumerate(ways):
        for k in range(i + 1, len(ways)):
            o = ways[k]
            if not boxes_meet(p, o, 0.0):  # ...two ways whose boxes do not meet cannot cross
                continue
            for n, (a, b) in enumerate(zip(p, p[1:], strict=False)):
                for c, d in zip(o, o[1:], strict=False):
                    if (x := _seg_cross(a, b, c, d)) is None or _seg_cross(c, d, a, b) is None:
                        continue
                    u, v = (b[0] - a[0], b[1] - a[1]), (d[0] - c[0], d[1] - c[1])
                    cos = abs(u[0] * v[0] + u[1] * v[1]) / ((math.hypot(*u) * math.hypot(*v)) or 1.0)
                    if math.degrees(math.acos(min(1.0, cos))) < NEEDLE_DEG:
                        out.append((i, n, k, x))
    return out


def shallow_crossings(M: Mapping[str, Any]) -> list[tuple[int, int]]:
    """Where two ways cross at under `NEEDLE_DEG` (`shallow_crossing_at`)."""
    return [(round(x[0]), round(x[1])) for _i, _n, _k, x in shallow_crossing_at(M.get("lanes") or [])]


def needle_joins(lanes: Lanes, blocked: Blocked | None = None) -> list[tuple[int, int]]:
    """Where a lane's end leg meets another way's tread as a needle rather than a T (`needle_ends`)."""
    return sorted({(round(lane_pts(lanes[i])[end][0]), round(lane_pts(lanes[i])[end][1])) for i, end, _k, _u, _v in needle_ends(lanes, blocked)})


def doubled_tails(M: Mapping[str, Any], only: int | None = None) -> list[int]:
    """The lanes (the connector aside) whose end - EITHER end - runs on beside another way, at `_DOUBLED_DEG` (`along_tail`,
    asked of the lane and of it reversed), whatever the two ways' widths. `along_tail` walks in from a lane's last point, and
    asked only that way it never saw a first end doubled: Mizuguchi's field spur left its street and ran 10-12 ft beside it
    for 210 ft before it turned for the field (feature 293 on 291, the pool's side-by-side test). `only`, a lane's index,
    asks that lane alone - the same verdict on it (a candidate at lay, `lay.laid_lawfully`, feature 417 T06).
    Research: no doubled tail - research/questions/0081-village-lanes.drawing.html: an end running back along another way under 20 degrees is refused, cut where it comes alongside - asked at `_DOUBLED_DEG`, 15, a known gap carried to 405 T101"""
    ways = _ways(M)
    lanes = M.get("lanes") or []
    asked = range(len(ways)) if only is None else [only]
    return [i for i in asked if not lanes[i].get("connector") and len(ways[i]) >= 2 and any(j != i and tail_doubled(ways[i], o) for j, o in enumerate(ways))]


def free_end(ways: Sequence[Poly], i: int, q: Pt, boxes: Sequence[tuple[float, float, float, float] | None] | None = None) -> bool:
    """Does the end `q` of way `i` touch no other way (within `JOIN_TOL`)? `boxes` (each way's `_bbox`), where the caller
    has them, pass over a way whose box lies beyond the tolerance (`box_gap`) - the same answer, without its segments."""
    if __debug__:
        OPS["seg_test@free_end"] += max(len(ways) - 1, 0)
    return all(
        len(o) < 2 or (boxes is not None and box_gap(q, boxes[k]) > JOIN_TOL) or min(seg_dist(q[0], q[1], u, v) for u, v in zip(o, o[1:], strict=False)) > JOIN_TOL
        for k, o in enumerate(ways)
        if k != i
    )


def box_gap(q: Pt, box: tuple[float, float, float, float] | None) -> float:
    """How far `q` lies from the box `(x0, y0, x1, y1)` (0 inside it; infinite from no box) - never more than its distance to
    anything in the box, so a box beyond a reach puts all it holds beyond it."""
    if __debug__:
        OPS["dist@box_gap"] += 1
    if box is None:
        return math.inf
    return math.hypot(max(box[0] - q[0], 0.0, q[0] - box[2]), max(box[1] - q[1], 0.0, q[1] - box[3]))


def span_walkable(M: Mapping[str, Any], p: Pt, q: Pt, skip: Sequence[int] = ()) -> bool:
    """May a short span of tread be laid from `p` to `q`: across no water (`bridge_crossed_waters`), no crop or marsh, no
    farmhouse (`house_hit`), no household's yard or garden, and not along another way (its middle within `JOIN_TOL` of a
    way other than the lanes `skip` - a span that doubles a tread rather than meeting it)?
    Research:
        a walkable span - research/questions/0081-village-lanes.drawing.html, research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: off water, crop, marsh and houses, its line 7 ft (`WEB_FABRIC_GAP`) off a garden fence
        a span off a threshing yard - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a track passing outside the cluster keeps 7 ft off every part of a homestead, a threshing yard among them, and the walk across a neighbor's yard is not drawn as a lane - extended here to a span inside the cluster
        a defense marsh too - research/questions/0081-village-lanes.drawing.html: no map draws a causeway, so a span crosses no reeds, a defense belt's
            included (405 T121)
        no span along another way - research/questions/0081-village-lanes.drawing.html: "Two paths running side by side are drawn as one" - a span whose middle runs within `JOIN_TOL` (4 ft) along another way would draw one tread twice
        a span off a farmhouse - research/questions/0081-village-lanes.drawing.html: its line a footpath's half-tread (`TREAD_HALF_FT`) and the 3 ft a lane's tread keeps off a farmhouse wall (`TREAD_WALL_FT`) off a house"""
    for wpts, _w in bridge_crossed_waters(M):
        wp = [(float(a[0]), float(a[1])) for a in wpts]
        if any(segments_cross(p, q, u, v) for u, v in zip(wp, wp[1:], strict=False)):
            return False
    rings = [[(float(a), float(b)) for a, b in f["outline"]] for f in M.get("fields") or [] if f.get("outline")]
    rings += [[(float(a), float(b)) for a, b in d["poly"]] for d in M.get("dry_plots") or [] if d.get("poly")]
    rings += [[(float(a), float(b)) for a, b in m["poly"]] for m in M.get("marshes") or [] if len(m.get("poly") or ()) >= 3]  # 405 T121: a defense belt too (0081)
    if any(segments_cross(p, q, r[k], r[(k + 1) % len(r)]) for r in rings for k in range(len(r))):
        return False
    if house_hit(
        [p, q], 2 * TREAD_HALF_FT, M.get("houses") or []
    ):  # a footpath's tread; `house_hit` keeps it 3 ft off every wall (405 T119: the sum was passed as a WIDTH, halved to 2.25 ft, and only corners were measured)
        return False
    yards = [[(float(a), float(b)) for a, b in rec["poly"]] for key in ("threshing_yards", "gardens") for rec in M.get(key) or [] if rec.get("poly")]
    if _crosses_fabric([p, q], yards, WEB_FABRIC_GAP):
        return False
    mid = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
    return math.dist(p, q) <= 2 * JOIN_TOL or all(k in skip or len(o) < 2 or _min_dist(mid, o) > JOIN_TOL for k, o in enumerate(_ways(M)))


def meets_clean(run: Poly, tread: Poly, connector: bool = False) -> bool:
    """Does the run's LAST end meet the way `tread` as the law asks - no needle, no hook, no fold at a joint, no hairpin at
    the connector's start? The law's own predicates, asked of the two ways alone (what `settle_the_web` re-lays an end to,
    and what a join that stops short would have to be)."""
    pair = [{"pts": run}, {"pts": tread, "connector": connector}]
    if -1 in hooked(run):
        return False
    if any(i == 0 and e == -1 for i, e, *_r in needle_ends(pair)):
        return False
    if any(i == 0 and e == -1 for _c, i, e in connector_hairpin_ends(pair)):
        return False
    return not any((i, ei) == (0, -1) or (j, ej) == (0, -1) for i, ei, j, ej in folded_joint_pairs(pair))


def near_misses(M: Mapping[str, Any]) -> list[tuple[int, int, Pt]]:
    """(lane index, end, the point it should meet) for every lane end that stops short of a way it is making for: a FREE
    end (`free_end`) with another way within `JOIN_REACH_FT`, the nearest point of which lies within `AIM_DEG` of the end's
    own heading, and a walkable span to it (`span_walkable`) that would meet the way cleanly and bend like a path
    (`meets_clean`, `kinks`). Such an end is a JOIN that stops short - a hole the eye reads in one way, or a T one clearance
    shy of its lane (homes H37, H38; the backlog's "one clearance short" (since closed) and 2c's corner hole). An end whose span is blocked, or would fold or kink, is not one: the two are separate ways, each ending at what it serves.
    Research:
        ends that nearly meet are joined - research/questions/0081-village-lanes.drawing.html: within 25 ft (`JOIN_REACH_FT`)
        which ends count - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A2, 2026-10-25); an end counts only where the way it nears lies within `AIM_DEG`, 60 deg, of its heading
        a door end is no short join - research/questions/0081-village-lanes.drawing.html: a household's path that leaves its own door and meets nothing there is left as drawn
            (a map drawing convention), never a join that stops short (405 T127)
        a blocked join is no short join - research/questions/0081-village-lanes.drawing.html: an end whose span would be blocked, fold or kink more than its own lane is not counted
        a connector's ends - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A2, 2026-10-25); never counted as joins that stop short"""
    ways = _ways(M)
    # EACH WAY'S BOX ONCE (feature 317): the seating asks this of every corridor it judges (`tree.as_joined`), and the
    # segment-by-segment search of every way from every free end was 1.26 s of a 40-household seating on seed 2 - 465,270
    # `seg_closest` - though most ways lie well beyond the reach. A way whose box is beyond it is passed over; same answers.
    boxes = [_bbox(o) for o in ways]
    out = []
    for i, ln in enumerate(M.get("lanes") or []):
        p = ways[i]
        if ln.get("connector") or len(p) < 2 or polyline_len(p) < 1.0:
            continue
        for end, q, b in ((-1, p[-1], p[-2]), (0, p[0], p[1])):
            if not free_end(ways, i, q, boxes) or math.dist(q, b) < 1e-6:
                continue
            if end == 0 and ln.get("of"):  # ...a household's own way's DOOR end serves its house (feature 318): not a join that stops short
                continue
            head = ((q[0] - b[0]) / math.dist(q, b), (q[1] - b[1]) / math.dist(q, b))
            best: tuple[float, int, Pt] | None = None
            for k, o in enumerate(ways):
                if k == i or len(o) < 2 or box_gap(q, boxes[k]) > JOIN_REACH_FT:
                    continue
                f = min((seg_closest(q[0], q[1], u, v) for u, v in zip(o, o[1:], strict=False)), key=lambda z: math.dist(q, z))
                d = math.dist(q, f)
                if d > JOIN_REACH_FT or (best is not None and d >= best[0]):
                    continue
                if (f[0] - q[0]) * head[0] + (f[1] - q[1]) * head[1] < d * math.cos(math.radians(AIM_DEG)):
                    continue
                best = (d, k, f)
            if best is None or not span_walkable(M, q, best[2], (i, best[1])):
                continue
            run = [*(p if end == -1 else p[::-1]), best[2]]
            if meets_clean(run, ways[best[1]], bool((M.get("lanes") or [])[best[1]].get("connector"))) and len(kink_spans(run)) <= len(kink_spans(p)):
                out.append((i, end, best[2]))
    return out


NEEDLE_LOOP_FT = 20.0
"""A face of the lane web whose mean width (twice its area over its perimeter) is under this is a NEEDLE OF GRASS: the same
way drawn twice, forking and rejoining round nothing (homes H39; the backlog's 2c (since closed), two
settlement-reviews: Sawada's triangle 110 ft long and 37.7 ft at its widest, mean width 16 ft, "reading as a street that
forks and rejoins around nothing"). A village block holds a steading and is five times as wide. A map drawing convention.
Research: needle of grass - CONVENTION: a web face under 20 ft mean width"""

NODING_SPECK_FT = 1.0
"""A web face whose whole perimeter is under this is no ground at all: three lanes meeting at one point, noded a hair apart,
polygonize into a speck (Kashikawa under feature 374 wave 119: two door paths ending on the skeleton at the point it bent,
a face 0.09 ft round, measured 2026-10-11 from the face the reroll's refusal named, and the last resort refused the map for a
needle it could not cut). A real needle - the same way drawn twice, or forking round nothing - runs the length of the ways
that bound it. The bound is the 1 ft below which `needle_loops` already drops a way itself.

Research: noding speck - NONE"""


def needle_loops(M: Mapping[str, Any]) -> list[tuple[Any, list[int]]]:
    """(face, the lanes bounding it) for every face of the drawn lane web (the treads noded where they cross, then
    polygonized) whose mean width is under `NEEDLE_LOOP_FT` - two ways laid round a sliver of ground, or along the same ground (a face of no area at all)."""
    lines = web_lines(M)
    out = []
    for face in web_faces(lines):
        if not is_needle(face):
            continue
        edge = face.exterior.buffer(0.5)
        out.append((face, sorted(i for i, ln in lines.items() if ln.intersection(edge).length > 1.0)))
    return out


def web_lines(M: Mapping[str, Any]) -> dict[int, Any]:
    """The web's treads as lines, by lane: each lane of two points or more and 1 ft long or more (`needle_loops`' own cut).

    Research: plumbing - NONE"""
    from shapely.geometry import LineString

    return {i: LineString(p) for i, p in enumerate(_ways(M)) if len(p) >= 2 and polyline_len(p) >= 1.0}


def web_faces(lines: Mapping[int, Any]) -> list[Any]:
    """Every face of the web's treads noded where they cross, then polygonized (none under two lines).

    Research: plumbing - NONE"""
    from shapely.ops import polygonize, unary_union

    if len(lines) < 2:
        return []
    return list(polygonize(unary_union(list(lines.values()))))


def is_needle(face: Any) -> bool:
    """Is a face of the web a needle - longer than a noding speck, its mean width under `NEEDLE_LOOP_FT`?

    Research: plumbing - NONE: `needle_loops`' own test, one face at a time (feature 387)"""
    return not (face.length < NODING_SPECK_FT or 2.0 * face.area / face.length >= NEEDLE_LOOP_FT)


def width_steps(lanes: Lanes) -> list[tuple[int, int]]:
    """The joints (`joints`: two lane ends meeting, no third way there) where one way changes width - a back lane halving
    its tread where nothing happens (homes H42); a lane at its rank meeting another way is where one rank meets the next (`at_rank`).
    Research: one width a way - research/questions/0081-village-lanes.drawing.html: no step at a bare joint, each way at its rank's width"""
    return [(i, j) for i, _ei, j, _ej in joints(lanes) if float(lanes[i].get("w") or 3.0) != float(lanes[j].get("w") or 3.0) and not (at_rank(lanes[i]) or at_rank(lanes[j]))]


def lane_networks(M: Mapping[str, Any]) -> int:
    """How many networks the drawn lanes fall into at the ink tolerance (`JOIN_TOL`): one, or you cannot walk between
    them.
    Research: one network - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: joined at 4 ft"""
    ways = [p for p in _ways(M) if len(p) >= 2]
    return len(set(_components(ways, JOIN_TOL)))
