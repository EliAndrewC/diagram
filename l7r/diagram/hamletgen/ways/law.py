"""The lane law: every rule a finished lane web must keep, each as ONE predicate (feature 287, M1).

A LIFT, NOT A RE-DERIVATION. Each predicate below is the body a finished-map test asserted - the lane network, the
cohort's lane rules, the crossings and the ways rows of feature 261's pool tests - moved into the engine. The placer that
owns a rule (`settle.settle_the_web`, the web's last pass, and the connector's `track.connector_through`) calls the same
predicate, and so does the placer's unit test on the violating case (`tests/hamletgen/ways/`); the finished-map tests
those unit tests made unnecessary are retired, each listed with its placer test in feature 287's research R8. That is
the skill's standing rule ("placement and its check must read the SAME source") made structural: there is one body per
rule, so the two cannot drift. The acceptance sweep (M9) runs `violations` over every finished map, so this module is the
registry of the rules.

Every predicate answers with what VIOLATES the rule - an empty list (or zero, or False) is a pass - so a test states the
found thing in its failure message and a placer knows where to cut.

WHERE THE PLACER AND ITS TEST READ A RULE DIFFERENTLY, the predicate is the TEST's reading, and the placers were moved onto
it (the ways phase of feature 287):

- the BEND (`bends_badly`): the tests sum the path between two 50 degree turns; `clearance._bends_badly`, which the web's
  passes ask, tested two turns separated by ONE segment - a lattice step of two short legs passed it and failed the test.
  Both now read `clearance.kink_spans`.
- the FORD (`off_ford_crossings`): the test allowed 45 ft from a recorded ford; the router gaps the brook at `FORD_HALF`
  (30 ft). The 45 ft was slack for `round_the_brooks` moving the course after the fords were set; the pool passes at the
  one constant, so the predicate reads `FORD_HALF` and the slack is gone.
- the END (`dangling_ends`): `tidy_lane_ends` asks `end_serves` against every other way; the pool test asks it against the
  other ways MINUS those at the lane's own far end (a lane counted as arriving because it was still within reach of the way
  it left). The stronger set is the predicate, and it serves both tests.
- the HOOK (`hooked_ends`): one test asked every lane, the other skipped the connector; the stricter reading is taken.
Research: plumbing and wrappers - NONE: each rule is claimed at the predicate that decides it
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import point_in_poly, rot_rect, seg_closest, seg_dist, segments_cross
from l7r.diagram.settlement._geom.indexes import PointGrid
from l7r.diagram.settlement._knobs import bridge_crossed_waters
from l7r.diagram.settlement.city.bridges import DECK_SPAN_DEFAULT_FT as DECK_SPAN_DEFAULT_FT
from l7r.diagram.settlement.city.bridges import PLANK_DITCH_FT as PLANK_DITCH_FT
from l7r.diagram.settlement.city.bridges import deck_covers as deck_covers
from l7r.diagram.settlement.city.bridges import undeckable_at as undeckable_at
from l7r.diagram.settlement.homestead_parts.fixture_seats import TRUNK_FT
from l7r.diagram.settlement.structures.fixtures._helpers import departure_routes
from l7r.diagram.settlement.water_ways._helpers import BUND_REACH_FT
from l7r.diagram.settlement.water_ways.lanes import behind_house, reaches_dooryard

from ..consts import WAY_END_REACH_FT, WEB_FABRIC_GAP, Poly, Pt
from .checks import served_network, unreached_houses
from .clearance import _HAIRPIN_DEG, _ZIGZAG_DEG, _ZIGZAG_RUN_FT, kink_spans
from .fabric import _LANE_JOIN_FT, _WEB_MIN_FT, _crosses_fabric, house_hit
from .geom import _TOUCH_GAP, WorkedGround, _components, _turn_deg, end_serves, polyline_len, steading_footprints, worked_ground
from .joints import _HOOK_DEG, _HOOK_FT, at_rank, hairpin_over_a_short_leg, joints, oriented
from .law_water import (  # noqa: F401 - re-exported: the law's callers reach the water rules and the lane helpers here
    DECK_NEAR_FT as DECK_NEAR_FT,
)
from .law_water import (
    _bbox as _bbox,
)
from .law_water import (
    _brooks as _brooks,
)
from .law_water import (
    _crossings as _crossings,
)
from .law_water import (
    _min_dist as _min_dist,
)
from .law_water import (
    _ways as _ways,
)
from .law_water import (
    boxes_meet as boxes_meet,
)
from .law_water import (
    crossing_points as crossing_points,
)
from .law_water import (
    deck_seats as deck_seats,
)
from .law_water import (
    lane_pts as lane_pts,
)
from .law_water import (
    oblique_at as oblique_at,
)
from .law_water import (
    oblique_crossings as oblique_crossings,
)
from .law_water import (
    off_ford_at as off_ford_at,
)
from .law_water import (
    off_ford_crossings as off_ford_crossings,
)
from .law_water import (
    off_square as off_square,
)
from .law_water import (
    over_and_back as over_and_back,
)
from .law_water import (
    plank_faults as plank_faults,
)
from .law_water import (
    short_decks as short_decks,
)
from .law_water import (
    unbridged_crossings as unbridged_crossings,
)
from .law_water import (
    undeckable_crossings as undeckable_crossings,
)
from .law_water import (
    water_courses as water_courses,
)
from .tails import tail_doubled

Lanes = Sequence[Mapping[str, Any]]

# THE BEND. A turn this sharp is a path doubling back on itself - nobody walks that; two real turns closer together than
# the run is a kink rather than a bend: a walker rounding something takes one arc, not a zig and an immediate zag. The
# figures are `clearance`'s (`lanes_bend_like_paths`, the rule's own thresholds), named here as the rule reads them.
DOUBLE_BACK_DEG = _HAIRPIN_DEG
"""Research: hairpin - research/questions/0081-village-lanes.drawing.html: 140 degrees"""
KINK_DEG = _ZIGZAG_DEG
"""Research: zigzag turn - research/questions/0081-village-lanes.drawing.html: 50 degrees"""
BEND_RUN_FT = _ZIGZAG_RUN_FT
"""Research: zigzag run - research/questions/0081-village-lanes.drawing.html: 40 ft"""

JOIN_TOL = _TOUCH_GAP
"""How near a lane end must come to another lane before the two count as one network - the web's own join tolerance (the
ink's), which both network tests read; a looser bar would call a near-miss a junction."""

DOORSTEP_FT = 80.0
"""A free lane end this near a farmhouse's center is discharged by that house (`lane_ends_front_different_houses`).
Research: an end discharged by a house - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: within 80 ft of its center"""
DOORSTEP_MAX = 2
"""...and one farmhouse may absolve this many of them. Three reads as a fan of stubs pointing at one door (consts.py's
0611 ruling).
Research: ends one house may absolve - UNRESEARCHED: two"""

BREAK_SPAN_FT = 60.0
"""A lane segment longer than this whose midpoint stands in a building's box has run straight through it
(`lanes_do_not_break_mid_run`): the tread was drawn across the solid, or it vanished there and resumed beyond.
Research: no tread through a building - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a segment over 60 ft"""

FIELD_REACH_FT = 60.0
"""On a brook map one of the hamlet's own ways (not the track out) comes this near the field - its paddy or its dry hem -
the reach `lanes_reach_something` asks of the field (feature 261, FR-012).
Research: a way reaches the field - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: within 60 ft"""


CONNECTOR_START_FT = 1.5
"""A lane end this near the connector's first point meets the connector's START - `fold_the_connector_hairpin`'s own
figure, so the hairpin the fold repairs and the hairpin this law refuses are one set."""

# A NEEDLE JOIN - a lane's last leg meeting another way's tread at a shallow angle and running back along it, leaving a
# sliver of ground between two treads instead of a T (R3; Mizuguchi's 35 ft leg at 16 degrees, a ~250 sq ft needle).
# MAP DRAWING CONVENTION, not a finding: 20 degrees is where two treads 4-6 ft wide stop reading as a junction and start
# reading as one smudged wedge (Mizuguchi's 16 inside it with room), and a leg of 20 ft or less is the approach to the
# junction itself - under a quarter of the Mizuguchi leg, and short enough that the wedge it leaves is under the treads'
# own ink. No rule of the record states either figure; they are recorded here, at the constant.
NEEDLE_DEG = 20.0
"""Research: a needle, not a T - CONVENTION: under 20 degrees two treads read as one smudged wedge"""
NEEDLE_FT = 20.0
"""Research: needle leg - CONVENTION: a leg over 20 ft, shorter is the approach to the junction"""

JOIN_REACH_FT = _LANE_JOIN_FT
"""A free lane end this near another way, making for it, is a join that stops short (`near_misses`) - the web's own join
reach (`fabric._LANE_JOIN_FT`, 25 ft), ONE tolerance for the placer that draws a join and the rule that asks whether it
touched. Future-work 2c measured every stopped-short join in the pool inside it (16.7, 28.0, 28.1, 29.2, 29.6 ft) - the
dead band between the generator's then 30 ft and the ink's 4 ft that neither half owned.
Research: a join that stops short - research/questions/0081-village-lanes.drawing.html: ends within 25 ft of one another are joined"""

FRAGMENT_FT = _WEB_MIN_FT
"""A lane shorter than this that earns nothing is debris (`short_fragments`) - the web's own debris floor (`_WEB_MIN_FT`),
asked of the finished web rather than only when a run is drawn.
Research: shortest way - UNRESEARCHED: 30 ft"""

AIM_DEG = 60.0
"""...and "making for it" is the way standing within this many degrees of the end's own heading. MAP DRAWING CONVENTION: a
tread that stops pointing at a way within a turn of 60 degrees reads as meant to meet it; one pointing away from it, or past
it at a glance, is a lane that ends beside a way, not a broken join.
Research: making for a way - CONVENTION: within 60 degrees of the end's heading"""


def kinks(pts: Sequence[Pt]) -> list[tuple[str, int, int]]:
    """Where a lane fails to bend like a path: a turn of `DOUBLE_BACK_DEG` or more ("doubles back"), or two turns of
    `KINK_DEG` or more whose summed path between them is `BEND_RUN_FT` or less ("kinks") - the whole run between the two
    turns, not one segment. The body is `clearance.kink_spans`, which every web pass asks too (ways W18, FR-003).
    Research: bends like a path - research/questions/0081-village-lanes.drawing.html: no hairpin, no zigzag"""
    p = list(pts)
    return [(kind, round(p[ka][0]), round(p[ka][1])) for kind, ka, _kb in kink_spans(p)]


def bends_badly(pts: Sequence[Pt]) -> bool:
    """Does this run fail to bend like a path (`kinks`)?"""
    return bool(kinks(pts))


def lanes_that_kink(M: Mapping[str, Any]) -> list[tuple[str, int, int]]:
    """`kinks` over every lane but the connector (`lanes_bend_like_paths`).
    Research: bends like a path - research/questions/0081-village-lanes.drawing.html: every lane but the track out"""
    return [k for ln in (M.get("lanes") or []) if not ln.get("connector") for k in kinks(lane_pts(ln))]


def hooked(pts: Sequence[Pt]) -> list[int]:
    """Which ends of a run are hooked, as -1 (its last) and 0 (its first): a leg of `_HOOK_FT` or less turning `_HOOK_DEG` or more.
    Research: a lane's end loses its hook - research/questions/0081-village-lanes.drawing.html: 12 ft, 90 degrees"""
    p = list(pts)
    if len(p) < 3:
        return []
    return [end for end, q in ((-1, p), (0, p[::-1])) if math.dist(q[-2], q[-1]) <= _HOOK_FT and _turn_deg(q[-3], q[-2], q[-1]) >= _HOOK_DEG]


def hooks(pts: Sequence[Pt]) -> list[tuple[int, int]]:
    """The vertex before each hooked end (`hooked`)."""
    p = list(pts)
    return [(round(p[-2 if end == -1 else 1][0]), round(p[-2 if end == -1 else 1][1])) for end in hooked(p)]


def hooked_ends(M: Mapping[str, Any]) -> list[tuple[int, int]]:
    """`hooks` over EVERY lane, the connector included."""
    return [h for ln in (M.get("lanes") or []) for h in hooks(lane_pts(ln))]


def husks(M: Mapping[str, Any]) -> list[int]:
    """The lane records that draw nothing: under two points, or under 1 ft long."""
    return [i for i, p in enumerate(_ways(M)) if len(p) < 2 or sum(math.dist(a, b) for a, b in zip(p, p[1:], strict=False)) < 1.0]


# ---- where lanes meet ----------------------------------------------------------------------------------------------


def folded_joint_pairs(lanes: Lanes) -> list[tuple[int, int, int, int]]:
    """The joints (`joints`: `(i, end_i, j, end_j)`) where two lanes meeting end to end - one way to the walker - turn
    `DOUBLE_BACK_DEG` or more.
    Research: lanes met end to end are one - research/questions/0081-village-lanes.drawing.html: no hairpin at the joint"""
    out = []
    for i, ei, j, ej in joints(lanes):
        x, y = oriented(lanes, i, ei, j, ej)
        if _turn_deg(x[-2], x[-1], y[1]) >= DOUBLE_BACK_DEG:
            out.append((i, ei, j, ej))
    return out


def folded_joints(lanes: Lanes) -> list[tuple[int, int]]:
    """Where two lanes meeting end to end turn `DOUBLE_BACK_DEG` or more at the joint (`folded_joint_pairs`)."""
    out = []
    for i, ei, j, ej in folded_joint_pairs(lanes):
        x, _y = oriented(lanes, i, ei, j, ej)
        out.append((round(x[-1][0]), round(x[-1][1])))
    return out


def connector_hairpin_ends(lanes: Lanes) -> list[tuple[int, int, int]]:
    """(connector index, lane index, end) wherever a lane's short last leg meets the connector's start and the two double
    back (`hairpin_over_a_short_leg`); the end is -1 (the lane's last point) or 0 (its first).
    Research: no hairpin at the track - research/questions/0081-village-lanes.drawing.html: over a returning leg under 40 ft"""
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
                if math.dist(j, cp[0]) <= CONNECTOR_START_FT and hairpin_over_a_short_leg(a, b, j, cp[1]):
                    out.append((ci, i, end))
    return out


def connector_hairpins(lanes: Lanes) -> list[tuple[int, int]]:
    """Where a lane's short last leg meets the connector's start and the two double back (`connector_hairpin_ends`)."""
    return [(round(lane_pts(lanes[i])[end][0]), round(lane_pts(lanes[i])[end][1])) for _ci, i, end in connector_hairpin_ends(lanes)]


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


def needle_ends(lanes: Lanes) -> list[tuple[int, int, int, Pt, Pt]]:
    """(lane index, end, tread lane index, u, v) wherever a lane's end leg, longer than `NEEDLE_FT`, meets another way's tread `u`-`v`
    (within `JOIN_TOL`) and runs back along it at under `NEEDLE_DEG` - a needle rather than a T. A leg carrying straight on
    from a way's END is not a needle: the tread it meets does not run back beside it. The end is -1 (last) or 0 (first).
    Research: a lane meets another as a T - research/questions/0081-village-lanes.drawing.html: never a needle"""
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
                    if seg_dist(q[0], q[1], u, v) > JOIN_TOL:
                        continue
                    if any(math.degrees(math.acos(max(-1.0, min(1.0, back[0] * d[0] + back[1] * d[1])))) < NEEDLE_DEG for d in _tread_bearings(q, u, v)):
                        out.append((i, end, k, u, v))
    return out


def needle_joins(lanes: Lanes) -> list[tuple[int, int]]:
    """Where a lane's end leg meets another way's tread as a needle rather than a T (`needle_ends`)."""
    return sorted({(round(lane_pts(lanes[i])[end][0]), round(lane_pts(lanes[i])[end][1])) for i, end, _k, _u, _v in needle_ends(lanes)})


def doubled_tails(M: Mapping[str, Any]) -> list[int]:
    """The lanes (the connector aside) whose end - EITHER end - runs on beside another way, at `_DOUBLED_DEG` (`along_tail`,
    asked of the lane and of it reversed), whatever the two ways' widths. `along_tail` walks in from a lane's last point, and
    asked only that way it never saw a first end doubled: Mizuguchi's field spur left its street and ran 10-12 ft beside it
    for 210 ft before it turned for the field (feature 293 on 291, the pool's side-by-side test).
    Research: no doubled tail - UNRESEARCHED: an end running on beside another way within _DOUBLED_DEG, 15 deg, is refused; no page we read covers a way drawn twice"""
    ways = _ways(M)
    lanes = M.get("lanes") or []
    return [i for i, p in enumerate(ways) if not lanes[i].get("connector") and len(p) >= 2 and any(j != i and tail_doubled(p, o) for j, o in enumerate(ways))]


def free_end(ways: Sequence[Poly], i: int, q: Pt, boxes: Sequence[tuple[float, float, float, float] | None] | None = None) -> bool:
    """Does the end `q` of way `i` touch no other way (within `JOIN_TOL`)? `boxes` (each way's `_bbox`), where the caller
    has them, pass over a way whose box lies beyond the tolerance (`box_gap`) - the same answer, without its segments."""
    return all(
        len(o) < 2 or (boxes is not None and box_gap(q, boxes[k]) > JOIN_TOL) or min(seg_dist(q[0], q[1], u, v) for u, v in zip(o, o[1:], strict=False)) > JOIN_TOL
        for k, o in enumerate(ways)
        if k != i
    )


def box_gap(q: Pt, box: tuple[float, float, float, float] | None) -> float:
    """How far `q` lies from the box `(x0, y0, x1, y1)` (0 inside it; infinite from no box) - never more than its distance to
    anything in the box, so a box beyond a reach puts all it holds beyond it."""
    if box is None:
        return math.inf
    return math.hypot(max(box[0] - q[0], 0.0, q[0] - box[2]), max(box[1] - q[1], 0.0, q[1] - box[3]))


def span_walkable(M: Mapping[str, Any], p: Pt, q: Pt, skip: Sequence[int] = ()) -> bool:
    """May a short span of tread be laid from `p` to `q`: across no water (`bridge_crossed_waters`), no crop or marsh, no
    farmhouse (`house_hit`), no household's yard or garden, and not along another way (its middle within `JOIN_TOL` of a
    way other than the lanes `skip` - a span that doubles a tread rather than meeting it)?
    Research: a walkable span - research/questions/0081-village-lanes.drawing.html, research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: off water, crop, marsh and houses, its line 7 ft (`WEB_FABRIC_GAP`) off yards and gardens"""
    for wpts, _w in bridge_crossed_waters(M):
        wp = [(float(a[0]), float(a[1])) for a in wpts]
        if any(segments_cross(p, q, u, v) for u, v in zip(wp, wp[1:], strict=False)):
            return False
    rings = [[(float(a), float(b)) for a, b in f["outline"]] for f in M.get("fields") or [] if f.get("outline")]
    rings += [[(float(a), float(b)) for a, b in d["poly"]] for d in M.get("dry_plots") or [] if d.get("poly")]
    rings += [[(float(a), float(b)) for a, b in m["poly"]] for m in M.get("marshes") or [] if len(m.get("poly") or ()) >= 3 and m.get("role") != "defense"]
    if any(segments_cross(p, q, r[k], r[(k + 1) % len(r)]) for r in rings for k in range(len(r))):
        return False
    if house_hit([p, q], 3.0, M.get("houses") or []):
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
    shy of its lane (homes H37, H38; future-work's "one clearance short" and 2c's corner hole). An end whose span is blocked, or would fold or kink, is not one: the two are separate ways, each ending at what it serves.
    Research:
        ends that nearly meet are joined - research/questions/0081-village-lanes.drawing.html: within 25 ft (`JOIN_REACH_FT`)
        which ends count - UNRESEARCHED: an end counts only where the way it nears lies within `AIM_DEG`, 60 deg, of its heading
        a door end is no short join - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a household's way is laid from its dooryard, so its door end is where it starts, never a join that stops short
        a blocked join is no short join - UNRESEARCHED: an end whose span would be blocked, fold or kink more than its own lane is not counted
        a connector's ends - UNRESEARCHED: never counted as joins that stop short"""
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
way drawn twice, forking and rejoining round nothing (homes H39; future-work/farming-communities.md 2c, two
settlement-reviews: Sawada's triangle 110 ft long and 37.7 ft at its widest, mean width 16 ft, "reading as a street that
forks and rejoins around nothing"). A village block holds a steading and is five times as wide. A map drawing convention.
Research: needle of grass - CONVENTION: a web face under 20 ft mean width"""


def needle_loops(M: Mapping[str, Any]) -> list[tuple[Any, list[int]]]:
    """(face, the lanes bounding it) for every face of the drawn lane web (the treads noded where they cross, then
    polygonized) whose mean width is under `NEEDLE_LOOP_FT` - two ways laid round a sliver of ground, or along the same ground (a face of no area at all)."""
    from shapely.geometry import LineString
    from shapely.ops import polygonize, unary_union

    ways = _ways(M)
    lines = {i: LineString(p) for i, p in enumerate(ways) if len(p) >= 2 and polyline_len(p) >= 1.0}
    if len(lines) < 2:
        return []
    out = []
    for face in polygonize(unary_union(list(lines.values()))):
        if face.length <= 0 or 2.0 * face.area / face.length >= NEEDLE_LOOP_FT:
            continue
        edge = face.exterior.buffer(0.5)
        out.append((face, sorted(i for i, ln in lines.items() if ln.intersection(edge).length > 1.0)))
    return out


def short_fragments(M: Mapping[str, Any], ground: WorkedGround | None = None) -> list[int]:
    """The lanes shorter than `FRAGMENT_FT` (the connector and the field spur aside) that earn nothing: taking one away
    leaves no farmhouse newly unreached (`unreached_houses`) and the web in as many networks (`lane_networks`) - a fragment
    the passes whittled down and nothing re-asked (homes H40; future-work 2c's 4 ft fragment). A short run that is some
    house's way, or the link that joins two pieces, earns its place and is not one - and so does one whose removal leaves
    ANOTHER lane's end reaching nothing (`dangling_lane_ends`): a row farm's short door path holds the end of its street
    (feature 291 on 287; dropped, Mizuguchi's street ends dangled past their last farms and the settle refused the web).
    `ground` is the worked ground where the caller has it; it is built at most once here (the perf-audit of feature 308:
    each `dangling_lane_ends` built it again, though a lane taken away changes no ground - seven builds a web on seed 47 at
    20 households, the map byte-identical with one).
    Research:
        debris - UNRESEARCHED: a lane under 30 ft that earns no house, join, target or end
        a household's own way never debris - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: every other farmhouse is served by a lane of its own"""
    lanes = M.get("lanes") or []
    # ...NOR A HOUSEHOLD'S OWN WAY, however short (feature 318, FR-014): it is the lane its household is served by (`tree.owed`),
    # and dropped as earning nothing it was drawn again next round, until the settle refused the web (cohort seed 10)
    short = [i for i, ln in enumerate(lanes) if not ln.get("connector") and not ln.get("spur") and not ln.get("of") and len(ln.get("pts") or []) >= 2 and polyline_len(lane_pts(ln)) < FRAGMENT_FT]
    if not short:
        return []
    reached, nets, targets, field = len(unreached_houses(M)), lane_networks(M), len(unreached_targets(M)), field_unreached(M)
    dangling: int | None = None  # asked only of a lane that passes every other test
    out = []
    for i in short:
        without = {**M, "lanes": [ln for k, ln in enumerate(lanes) if k != i]}
        # ...nor a way target (a burial ground's edge) newly unreached, nor the field (feature 287: a short spur to the graves
        # or on to the bund earns its place as a house's door path does)
        if len(unreached_houses(without)) <= reached and lane_networks(without) <= nets and len(unreached_targets(without)) <= targets and field_unreached(without) <= field:
            ground = worked_ground(M) if ground is None else ground
            dangling = len(dangling_lane_ends(M, ground)) if dangling is None else dangling
            if len(dangling_lane_ends(without, ground)) <= dangling:  # ...nor another lane's end left reaching nothing
                out.append(i)
    return out


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


# ---- where lanes end -----------------------------------------------------------------------------------------------


def way_targets(M: Mapping[str, Any]) -> list[Pt]:
    """The points a way must reach (`meta.way_targets`: a burial ground's edge nearest the houses, homes H36)."""
    return [(float(t["at"][0]), float(t["at"][1])) for t in (M.get("meta") or {}).get("way_targets") or []]


TARGET_REACH_FT = 14.0
"""A way target is reached where the served network comes this near it: the spur drawn to it ends on it, and a lane passing
nearer than a doubled tread's distance (`sweeps._ALONG_FT`) stands at it. A map drawing convention.

Research: a way target reached - UNRESEARCHED: within 14 ft of the served network"""


def unreached_targets(M: Mapping[str, Any]) -> list[Pt]:
    """The way targets (`way_targets`) the served network (`served_network`) does not come within `TARGET_REACH_FT` of.
    Research: a path runs to the graves - UNRESEARCHED: within 14 ft of the burial ground's edge"""
    targets = way_targets(M)
    if not targets:
        return []
    segs = served_network(M.get("lanes") or [])
    return [t for t in targets if not any(seg_dist(t[0], t[1], a, b) <= TARGET_REACH_FT for a, b in segs)]


def _walked_to(end: Pt, far: Pt, sg: tuple[Pt, Pt]) -> bool:
    """Is the way segment `sg`'s nearest point to a lane's `end` nearer that end than the lane's `far` end - so the lane,
    walked from its far end, came toward it (`dangling_lane_ends`)?"""
    c = seg_closest(end[0], end[1], sg[0], sg[1])
    return math.dist(c, end) < math.dist(c, far)


def dangling_lane_ends(M: Mapping[str, Any], ground: WorkedGround | None = None) -> list[tuple[int, int]]:
    """(lane index, end) for every internal lane end that reaches nothing (`end_serves`) other than the way its own far
    end stands on: the other ways' segments are asked, less those within `_TOUCH_GAP` of the lane's far end. `ground` is the
    worked ground where the caller has it built already (`memo_ground`). A way target (`meta.way_targets`, a burial ground's
    near edge) is something worth walking to, as a farmhouse is (homes H36: a path runs to the graves).
    Research:
        an end reaches something seen - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: walked toward it
        a burial ground's edge a lane end's destination - UNRESEARCHED: a way target counts as a farmhouse does"""
    ways = _ways(M)
    centers = [(float(h["x"]), float(h["y"])) for h in M.get("houses") or []] + way_targets(M)
    steadings = steading_footprints(M)
    ground = worked_ground(M) if ground is None else ground
    out = []
    for i, ln in enumerate(M.get("lanes") or []):
        p = ways[i]
        if ln.get("connector") or len(p) < 2:
            continue
        others = [sg for k, o in enumerate(ways) if k != i and len(o) >= 2 for sg in zip(o, o[1:], strict=False)]
        for e, end, far in ((-1, p[-1], p[0]), (0, p[0], p[-1])):
            # ...AND A WAY IS REACHED ONLY WHERE THE END GOT NEARER TO IT THAN THE LANE'S FAR END ALREADY STOOD (feature 293, settlement-review of Inashiro): a 32 ft skeleton
            # stub left the connector at the entrance and ended in the windbreak, 58 ft from the exit strip's end at that same junction - inside `WAY_END_REACH_FT`, so it
            # "reached" the junction it had left. The nearest point of each other way is asked: nearer the far end than the end, the lane walked away from it, not to it.
            segs = [sg for sg in others if seg_dist(far[0], far[1], sg[0], sg[1]) > _TOUCH_GAP and _walked_to(end, far, sg)]
            if not end_serves(end, segs, centers, ground, steadings):
                out.append((i, e))
    return out


def dangling_ends(M: Mapping[str, Any]) -> list[tuple[int, int]]:
    """Every internal lane end that reaches nothing but the way it left (`dangling_lane_ends`), by where it stands."""
    ways = _ways(M)
    return sorted({(round(ways[i][e][0]), round(ways[i][e][1])) for i, e in dangling_lane_ends(M)})


def fronting_ends(M: Mapping[str, Any]) -> dict[int, list[tuple[int, int]]]:
    """The free lane ends each farmhouse discharges, as (lane index, end) - an end whose nearest farmhouse center is within `DOORSTEP_FT` (the connector's aside; an end within `JOIN_TOL` of another way is discharged by the junction).
    Research:
        an end discharged by a house - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: within DOORSTEP_FT, 80 ft of the nearest farmhouse's center
        an end discharged by a junction - NONE: an end within JOIN_TOL, the touch gap, of another way already meets it"""
    ways = _ways(M)
    houses = M.get("houses") or []
    fronted: dict[int, list[tuple[int, int]]] = {}
    if not houses:
        return fronted
    for i, ln in enumerate(M.get("lanes") or []):
        p = ways[i]
        if ln.get("connector") or len(p) < 2:
            continue
        for e, end in ((0, p[0]), (-1, p[-1])):
            if any(_min_dist(end, o) <= JOIN_TOL for k, o in enumerate(ways) if k != i and len(o) >= 2):  # the first junction answers
                continue
            best = min(range(len(houses)), key=lambda h: math.hypot(end[0] - houses[h]["x"], end[1] - houses[h]["y"]))
            if math.hypot(end[0] - houses[best]["x"], end[1] - houses[best]["y"]) <= DOORSTEP_FT:
                fronted.setdefault(best, []).append((i, e))
    return fronted


def fronted_ends(M: Mapping[str, Any]) -> dict[int, int]:
    """How many free lane ends each farmhouse discharges (`fronting_ends`)."""
    return {h: len(ends) for h, ends in fronting_ends(M).items()}


def ends_behind(M: Mapping[str, Any], ground: WorkedGround | None = None) -> list[tuple[int, int, int]]:
    """(lane index, end, house index) for every free lane end (the connector's aside; an end within `JOIN_TOL` of another
    way is a junction) that stands within `WAY_END_REACH_FT` of a farmhouse, BEHIND the nearest such house - past its back
    wall, abreast of it (`behind_house`) - and at no house's dooryard (`reaches_dooryard`), nor on the bund (water W57; 269
    B17, research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a lane that serves a farmhouse ends at its dooryard, and a lane end behind a house's back
    wall does not count as reaching it - Kuwabata's lane 5, 11 ft behind house 1 and 43 ft from its yard).
    Research: a lane ends at the dooryard - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: never behind the house"""
    ways = _ways(M)
    houses = M.get("houses") or []
    if not houses:
        return []
    ground = worked_ground(M) if ground is None else ground
    out = []
    for i, ln in enumerate(M.get("lanes") or []):
        p = ways[i]
        if ln.get("connector") or len(p) < 2:
            continue
        for e in (0, -1):
            q = p[e]
            near = [h for h in range(len(houses)) if math.hypot(q[0] - houses[h]["x"], q[1] - houses[h]["y"]) <= WAY_END_REACH_FT]
            if not near or not free_end(ways, i, q) or ground.dist(q) <= BUND_REACH_FT or any(reaches_dooryard(houses[h], q) for h in near):
                continue
            h = min(near, key=lambda k: math.hypot(q[0] - houses[k]["x"], q[1] - houses[k]["y"]))
            if behind_house(houses[h], q):
                out.append((i, e, h))
    return out


def doorstep_ends(M: Mapping[str, Any]) -> dict[int, int]:
    """The farmhouses that discharge more than `DOORSTEP_MAX` free lane ends apiece (`fronted_ends`).
    Research: no fan of stubs at a door - UNRESEARCHED: more than two free ends within 80 ft"""
    return {h: n for h, n in fronted_ends(M).items() if n > DOORSTEP_MAX}


def field_reach_ft(M: Mapping[str, Any]) -> float:
    """How near the hamlet's own ways (not the connector) come to the field - its paddy outlines and dry hem; infinite
    where there is no field or no way."""
    rings = [f["outline"] for f in M.get("fields") or [] if f.get("outline")] + [d["poly"] for d in M.get("dry_plots") or [] if d.get("poly")]
    pts = [(float(x), float(y)) for ln in (M.get("lanes") or []) if not ln.get("connector") for x, y in (ln.get("pts") or [])]
    return min((seg_dist(p[0], p[1], r[i], r[(i + 1) % len(r)]) for p in pts for r in rings for i in range(len(r))), default=math.inf)


def field_unreached(M: Mapping[str, Any]) -> bool:
    """On a brook map, no way of the hamlet's own comes within `FIELD_REACH_FT` of its field.

    `field_reach_ft(M) > FIELD_REACH_FT`, ASKED AS THE THRESHOLD IT IS (dev/performance.md, shape one): the measure walks
    every lane vertex against every edge of every paddy outline and dry plot, and the settle and the tree's pruning ask this
    once per round and per lane tried (cohort seed 44: 39,321 distances a roll). No vertex comes within the reach of an edge
    whose box, grown by the reach, does not hold it, so the edges are filed by that box once and a vertex asks only its
    cell's; the first within the reach answers, by the same `seg_dist`.
    Research: a way reaches the field - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: on brook maps"""
    if not _brooks(M):
        return False
    rings = [f["outline"] for f in M.get("fields") or [] if f.get("outline")] + [d["poly"] for d in M.get("dry_plots") or [] if d.get("poly")]
    grid = PointGrid(128.0)
    grid.extend(
        (a, b, min(a[0], b[0]) - FIELD_REACH_FT, min(a[1], b[1]) - FIELD_REACH_FT, max(a[0], b[0]) + FIELD_REACH_FT, max(a[1], b[1]) + FIELD_REACH_FT)
        for r in rings
        for a, b in ((r[i], r[(i + 1) % len(r)]) for i in range(len(r)))
    )
    pts = [(float(x), float(y)) for ln in (M.get("lanes") or []) if not ln.get("connector") for x, y in (ln.get("pts") or [])]
    return not any(seg_dist(p[0], p[1], a, b) <= FIELD_REACH_FT for p in pts for a, b, *_box in grid.near(p[0], p[1]))


# ---- the fabric ----------------------------------------------------------------------------------------------------


FIXTURE_PAD_FT = 0.5
"""How far a lane's tread keeps off a farmstead fixture beyond its own half-width: the ink's edge stroke - a tread that
touches the glyph reads as walking over it.
Research: fixture pad - CONVENTION: 0.5 ft past the half-tread"""


def fixture_quads(M: Mapping[str, Any]) -> list[Poly]:
    """Every farmstead fixture's drawn quad (`farm_fixtures`: privy, manure heap, bath, coop, hokora), turned as drawn, and
    every yard persimmon's TRUNK box (feature 287, homes H43: the persimmon is seated with its household before the web, so
    the web keeps its trunk off the tread as it keeps a privy - a lane may pass under the crown, never through the trunk;
    cohort seed 42 laid a straggler through a neighbor's persimmon). The box is the seating's own (`fixture_seats.TRUNK_FT`,
    which its own door corridor keeps off), so a tread clear of it is clear of the trunk (`stands.trunk_on_tread`).
    Research: under the crown, not the trunk - UNRESEARCHED: the persimmon's trunk box a wall, its crown not"""
    quads = [rot_rect(float(r["x"]), float(r["y"]), float(r["w"]), float(r["h"]), float(r.get("rot") or 0.0)) for r in M.get("farm_fixtures") or [] if all(k in r for k in ("x", "y", "w", "h"))]
    trunk = TRUNK_FT / float((M.get("meta") or {}).get("ftpx") or 1.0)
    return quads + [rot_rect(float(r["x"]), float(r["y"]), trunk, trunk, 0.0) for r in M.get("persimmons") or [] if "x" in r and "y" in r]


def over_a_fixture(pts: Sequence[Pt], width: float, quads: Sequence[Poly]) -> int | None:
    """The first segment of a lane along `pts`, drawn `width` wide, whose tread meets a farmstead fixture (`fixture_quads`) -
    crosses it, stands in it, or passes within its half-width and `FIXTURE_PAD_FT` of it; None where it meets none. THE ONE
    PREDICATE: the web's settle cuts what it names, a tree lane is refused by it, and the finished-map rule reads it.
    Research: off the fixtures - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: nothing stands on a tread"""
    gap = width / 2.0 + FIXTURE_PAD_FT
    for k, (a, b) in enumerate(zip(pts, pts[1:], strict=False)):
        for q in quads:
            if point_in_poly(a[0], a[1], q) or point_in_poly(b[0], b[1], q) or _crosses_fabric([a, b], [q], gap):
                return k
    return None


def lanes_over_fixtures(M: Mapping[str, Any]) -> list[tuple[int, int]]:
    """(lane, segment) for every lane whose tread meets a farmstead fixture (`over_a_fixture`)."""
    quads = fixture_quads(M)
    if not quads:
        return []
    out = []
    for i, ln in enumerate(M.get("lanes") or []):
        k = over_a_fixture(lane_pts(ln), float(ln.get("w") or 3.0), quads)
        if k is not None:
            out.append((i, k))
    return out


def solid_boxes(M: Mapping[str, Any]) -> list[tuple[float, float, float, float]]:
    """The axis boxes of the buildings a lane may not run through: houses, farm sheds and byres."""
    solid = []
    for key in ("houses", "farm_sheds", "byres"):
        for r in M.get(key) or []:
            if "x" in r and "w" in r:
                hw, hh = r["w"] / 2, r["h"] / 2
                solid.append((r["x"] - hw, r["y"] - hh, r["x"] + hw, r["y"] + hh))
    return solid


def solid_quads(M: Mapping[str, Any]) -> list[Poly]:
    """`solid_boxes` as polygons - the ground a placer that walls by polygon (the connector's sweep and its dry exit) keeps
    off, so it keeps off the very boxes `breaks_through` reads."""
    return [[(x0, y0), (x1, y0), (x1, y1), (x0, y1)] for x0, y0, x1, y1 in solid_boxes(M)]


def breaks_through(pts: Sequence[Pt], solid: Sequence[tuple[float, float, float, float]]) -> list[tuple[int, Pt]]:
    """(segment index, midpoint) for every segment of a run longer than `BREAK_SPAN_FT` whose midpoint stands inside one of
    the `solid` boxes (`solid_boxes`) - a tread drawn straight through a building. THE ONE PREDICATE of the rule: the
    finished-map reading (`breaks_mid_run`), the web's foul test (`settle.fouled_segment`) and the connector's placer
    (`track.connector_through`) all ask it.
    Research:
        no tread through a building - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html
        a leg long enough to break - UNRESEARCHED: only a leg over `BREAK_SPAN_FT` (60 ft) with its midpoint in a building counts"""
    out = []
    for k, (a, b) in enumerate(zip(pts, pts[1:], strict=False)):
        if math.dist(a, b) <= BREAK_SPAN_FT:
            continue
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        if any(x0 <= mid[0] <= x1 and y0 <= mid[1] <= y1 for x0, y0, x1, y1 in solid):
            out.append((k, mid))
    return out


def breaks_mid_run(M: Mapping[str, Any]) -> list[tuple[int, int]]:
    """The midpoints of lane segments longer than `BREAK_SPAN_FT` that stand inside a building's box (`breaks_through`)."""
    return [(round(mid[0]), round(mid[1])) for solid in (solid_boxes(M),) for p in _ways(M) for _k, mid in breaks_through(p, solid)]


def fouls_fabric(pts: Poly, width: float, houses: Sequence[Mapping[str, Any]], fabric: Sequence[tuple[Poly, Pt | None, str]], own: Pt | None = None) -> bool:
    """Does a lane of this width along `pts` put ink on a farmhouse (`house_hit`), or pass within `WEB_FABRIC_GAP` of another household's
    threshing yard or garden (`_crosses_fabric`)? `fabric`: `_homestead_polys`'; a door path is exempt from its OWN (`own`).
    Research:
        nothing built on a lane - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: no tread on another household's yard or bed
        foul margin - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the line within 7 ft of another's yard or bed"""
    if house_hit(pts, width, houses):
        return True
    theirs = [poly for poly, owner, kind in fabric if kind in ("threshing_yards", "gardens") and (own is None or owner != own)]
    return _crosses_fabric(pts, theirs, WEB_FABRIC_GAP)


# ---- water ---------------------------------------------------------------------------------------------------------


def way_outs_crossing(M: Mapping[str, Any], routes: Sequence[Sequence[Pt]] | None = None) -> list[tuple[int, int, int]]:
    """(x, y, crossings) for every household's way out (`departure_routes`) that crosses one brook more than once.
    Research: no way out over and back - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html"""
    routes = departure_routes(M) if routes is None else routes
    out = []
    for brook in _brooks(M):
        for r in routes:
            n = len(crossing_points(list(r), brook))
            if n > 1:
                out.append((round(r[0][0]), round(r[0][1]), n))
    return out


WAY_OUT_CARRY_FT = 12.0
"""How near a lane's own crossing of the brook must stand to a crossing of a household's way out for that lane to be the
one carrying it: a way out is walked over lane samples 10 ft apart (`departure_routes`), so its crossing lies within half a
sample, and a crossing of another lane is at least a ford's width away."""


def way_out_carriers(M: Mapping[str, Any], routes: Sequence[Sequence[Pt]] | None = None) -> list[tuple[int, int, Pt]]:
    """(lane index, segment index, point) for every crossing of a brook by a lane OTHER than the connector that carries a
    crossing of a household's way out crossing that brook more than once (`way_outs_crossing`), in the order the ways out
    meet them - the crossings the web may take away to hold the rule. The connector's are never among them: it crosses no
    brook more than once (`track.connector_through`), so a way out crossing twice always has a crossing on another lane."""
    routes = departure_routes(M) if routes is None else routes
    lanes = M.get("lanes") or []
    out: list[tuple[int, int, Pt]] = []
    for brook in _brooks(M):
        for r in routes:
            xs = [x for _k, x in crossing_points(list(r), brook)]
            if len(xs) <= 1:
                continue
            for x in xs:
                for i, ln in enumerate(lanes):
                    if ln.get("connector") or len(ln.get("pts") or []) < 2:
                        continue
                    out.extend((i, k, y) for k, y in crossing_points(lane_pts(ln), brook) if math.dist(x, y) <= WAY_OUT_CARRY_FT and (i, k, y) not in out)
    return out


def adds_a_way_out_crossing(M: Mapping[str, Any], run: Poly, width: float, lanes: Lanes | None = None) -> bool:
    """Would drawing `run` as a lane `width` wide beside `lanes` (the manifest's own by default) leave more households' ways
    out crossing a brook more than once (`way_outs_crossing`) than without it? A way out is a ROUTE, not a lane: a new lane
    that crosses nothing twice can still hand some household a shorter way out over the brook and back. THE ONE QUESTION the
    web asks before it lays a tree lane (`settle.Lawful`), which no repair takes away afterwards.
    Research: no way out over and back - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html"""
    if not _brooks(M):
        return False
    lanes = list(M.get("lanes") or []) if lanes is None else list(lanes)
    after = len(way_outs_crossing({**M, "lanes": [*lanes, {"pts": [list(q) for q in run], "w": width}]}))
    return after > 0 and after > len(way_outs_crossing({**M, "lanes": lanes}))  # the web without it walked only when it could matter


# ---- the registry --------------------------------------------------------------------------------------------------

LAW: dict[str, Callable[[Mapping[str, Any]], Any]] = {
    "bends": lanes_that_kink,
    "hooks": hooked_ends,
    "husks": husks,
    "folded_joints": lambda M: folded_joints(M.get("lanes") or []),
    "connector_hairpins": lambda M: connector_hairpins(M.get("lanes") or []),
    "needle_joins": lambda M: needle_joins(M.get("lanes") or []),
    "doubled_tails": doubled_tails,
    "networks": lambda M: max(0, lane_networks(M) - 1),
    "joins_short": near_misses,
    "fragments": short_fragments,
    "width_steps": lambda M: width_steps(M.get("lanes") or []),
    "dangling_ends": dangling_ends,
    "doorstep_ends": doorstep_ends,
    "ends_behind": ends_behind,
    "over_fixtures": lanes_over_fixtures,
    "needle_loops": lambda M: [[round(v) for v in face.centroid.coords[0]] for face, _lanes in needle_loops(M)],
    "field_unreached": field_unreached,
    "breaks_mid_run": breaks_mid_run,
    "over_and_back": over_and_back,
    "off_ford": off_ford_crossings,
    "oblique_brook": oblique_crossings,
    "oblique_channel": lambda M: oblique_crossings(M, "channel"),
    "unbridged": unbridged_crossings,
    "undeckable": undeckable_crossings,
    "short_decks": short_decks,
    "planks": lambda M: [x for part in plank_faults(M) for x in part],
    "way_outs": way_outs_crossing,
    "unreached_houses": unreached_houses,
    "unreached_targets": unreached_targets,
}
"""Every lane rule a finished map is asked, by name - the acceptance sweep's (M9) reading of this module. A rule's value is
falsy when the map keeps it. `fouls_fabric` and `deck_seats` are asked of one candidate way, not of a manifest, and are
reached here through `breaks_mid_run` and `undeckable_crossings`."""


def violations(M: Mapping[str, Any]) -> dict[str, Any]:
    """Every rule of `LAW` this map breaks, with what breaks it."""
    return {name: v for name, rule in LAW.items() if (v := rule(M))}
