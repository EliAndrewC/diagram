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
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import point_in_poly, rot_rect, seg_closest, seg_dist, seg_intersect, segments_cross
from l7r.diagram.settlement._geom.indexes import PointGrid
from l7r.diagram.settlement._knobs import bridge_carried_ways, bridge_crossed_waters
from l7r.diagram.settlement.city.bridges import DECK_SPAN_DEFAULT_FT as DECK_SPAN_DEFAULT_FT
from l7r.diagram.settlement.city.bridges import PLANK_DITCH_FT as PLANK_DITCH_FT
from l7r.diagram.settlement.city.bridges import deck_covers as deck_covers
from l7r.diagram.settlement.city.bridges import flooded_ground, plank_ditch, plank_on_supply
from l7r.diagram.settlement.city.bridges import undeckable_at as undeckable_at
from l7r.diagram.settlement.homestead_parts.fixture_seats import TRUNK_FT
from l7r.diagram.settlement.structures.fixtures._helpers import departure_routes
from l7r.diagram.settlement.water_ways._helpers import BUND_REACH_FT
from l7r.diagram.settlement.water_ways.lanes import behind_house, reaches_dooryard

from ..consts import FORD_HALF, WAY_END_REACH_FT, Poly, Pt
from .checks import FORD_SQUARE_TOL_DEG, served_network, unreached_houses
from .clearance import _HAIRPIN_DEG, _ZIGZAG_DEG, _ZIGZAG_RUN_FT, kink_spans
from .fabric import _LANE_JOIN_FT, _WEB_MIN_FT, _crosses_fabric, house_hit
from .geom import _TOUCH_GAP, WorkedGround, _components, _turn_deg, end_serves, polyline_len, steading_footprints, worked_ground
from .joints import _HOOK_DEG, _HOOK_FT, hairpin_over_a_short_leg, joints, oriented
from .sweeps import _DOUBLED_DEG, along_tail

Lanes = Sequence[Mapping[str, Any]]

# THE BEND. A turn this sharp is a path doubling back on itself - nobody walks that; two real turns closer together than
# the run is a kink rather than a bend: a walker rounding something takes one arc, not a zig and an immediate zag. The
# figures are `clearance`'s (`lanes_bend_like_paths`, the rule's own thresholds), named here as the rule reads them.
DOUBLE_BACK_DEG = _HAIRPIN_DEG
KINK_DEG = _ZIGZAG_DEG
BEND_RUN_FT = _ZIGZAG_RUN_FT

JOIN_TOL = _TOUCH_GAP
"""How near a lane end must come to another lane before the two count as one network - the web's own join tolerance (the
ink's), which both network tests read; a looser bar would call a near-miss a junction."""

DOORSTEP_FT = 80.0
"""A free lane end this near a farmhouse's center is discharged by that house (`lane_ends_front_different_houses`)."""
DOORSTEP_MAX = 2
"""...and one farmhouse may absolve this many of them. Three reads as a fan of stubs pointing at one door (consts.py's
0611 ruling)."""

BREAK_SPAN_FT = 60.0
"""A lane segment longer than this whose midpoint stands in a building's box has run straight through it
(`lanes_do_not_break_mid_run`): the tread was drawn across the solid, or it vanished there and resumed beyond."""

FIELD_REACH_FT = 60.0
"""On a brook map one of the hamlet's own ways (not the track out) comes this near the field - its paddy or its dry hem -
the reach `lanes_reach_something` asks of the field (feature 261, FR-012)."""

DECK_NEAR_FT = 40.0
"""A deck this near a recorded watercourse is over it, and is judged against that course's width."""

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
NEEDLE_FT = 20.0

JOIN_REACH_FT = _LANE_JOIN_FT
"""A free lane end this near another way, making for it, is a join that stops short (`near_misses`) - the web's own join
reach (`fabric._LANE_JOIN_FT`, 30 ft), ONE tolerance for the placer that draws a join and the rule that asks whether it
touched. Future-work 2c measured every stopped-short join in the pool inside it (16.7, 28.0, 28.1, 29.2, 29.6 ft) - the
dead band between the generator's 30 ft and the ink's 4 ft that neither half owned."""

FRAGMENT_FT = _WEB_MIN_FT
"""A lane shorter than this that earns nothing is debris (`short_fragments`) - the web's own debris floor (`_WEB_MIN_FT`),
asked of the finished web rather than only when a run is drawn."""

AIM_DEG = 60.0
"""...and "making for it" is the way standing within this many degrees of the end's own heading. MAP DRAWING CONVENTION: a
tread that stops pointing at a way within a turn of 60 degrees reads as meant to meet it; one pointing away from it, or past
it at a glance, is a lane that ends beside a way, not a broken join."""


def lane_pts(ln: Mapping[str, Any]) -> Poly:
    """A lane record's points as float tuples."""
    return [(float(x), float(y)) for x, y in (ln.get("pts") or [])]


def _ways(M: Mapping[str, Any]) -> list[Poly]:
    return [lane_pts(ln) for ln in (M.get("lanes") or [])]


def _brooks(M: Mapping[str, Any]) -> list[Poly]:
    return [[(float(p[0]), float(p[1])) for p in s["poly"]] for s in (M.get("streams") or []) if len(s.get("poly", ())) >= 2]


def _min_dist(pt: Pt, poly: Poly) -> float:
    return min(seg_dist(pt[0], pt[1], poly[i], poly[i + 1]) for i in range(len(poly) - 1))


# ---- a lane's own shape --------------------------------------------------------------------------------------------


def kinks(pts: Sequence[Pt]) -> list[tuple[str, int, int]]:
    """Where a lane fails to bend like a path: a turn of `DOUBLE_BACK_DEG` or more ("doubles back"), or two turns of
    `KINK_DEG` or more whose summed path between them is `BEND_RUN_FT` or less ("kinks") - the whole run between the two
    turns, not one segment. The body is `clearance.kink_spans`, which every web pass asks too (ways W18, FR-003)."""
    p = list(pts)
    return [(kind, round(p[ka][0]), round(p[ka][1])) for kind, ka, _kb in kink_spans(p)]


def bends_badly(pts: Sequence[Pt]) -> bool:
    """Does this run fail to bend like a path (`kinks`)?"""
    return bool(kinks(pts))


def lanes_that_kink(M: Mapping[str, Any]) -> list[tuple[str, int, int]]:
    """`kinks` over every lane but the connector (`lanes_bend_like_paths`)."""
    return [k for ln in (M.get("lanes") or []) if not ln.get("connector") for k in kinks(lane_pts(ln))]


def hooked(pts: Sequence[Pt]) -> list[int]:
    """Which ends of a run are hooked, as -1 (its last) and 0 (its first): a leg of `_HOOK_FT` or less turning `_HOOK_DEG`
    or more."""
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
    `DOUBLE_BACK_DEG` or more."""
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
    back (`hairpin_over_a_short_leg`); the end is -1 (the lane's last point) or 0 (its first)."""
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
    from a way's END is not a needle: the tread it meets does not run back beside it. The end is -1 (last) or 0 (first)."""
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
    """The lanes (the connector aside) whose end runs on beside another way, at `_DOUBLED_DEG` (`along_tail`), whatever the
    two ways' widths."""
    ways = _ways(M)
    lanes = M.get("lanes") or []
    return [
        i for i, p in enumerate(ways) if not lanes[i].get("connector") and len(p) >= 2 and any(j != i and len(o) >= 2 and along_tail(p, o, deg=_DOUBLED_DEG) is not None for j, o in enumerate(ways))
    ]


def free_end(ways: Sequence[Poly], i: int, q: Pt) -> bool:
    """Does the end `q` of way `i` touch no other way (within `JOIN_TOL`)?"""
    return all(len(o) < 2 or min(seg_dist(q[0], q[1], u, v) for u, v in zip(o, o[1:], strict=False)) > JOIN_TOL for k, o in enumerate(ways) if k != i)


def span_walkable(M: Mapping[str, Any], p: Pt, q: Pt, skip: Sequence[int] = ()) -> bool:
    """May a short span of tread be laid from `p` to `q`: across no water (`bridge_crossed_waters`), no crop or marsh, no
    farmhouse (`house_hit`), no household's yard or garden, and not along another way (its middle within `JOIN_TOL` of a
    way other than the lanes `skip` - a span that doubles a tread rather than meeting it)?"""
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
    if _crosses_fabric([p, q], yards, _TOUCH_GAP):
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
    shy of its lane (homes H37, H38; future-work's "one clearance short" and 2c's corner hole). An end whose span is blocked,
    or would fold or kink, is not one: the two are separate ways, each ending at what it serves."""
    ways = _ways(M)
    out = []
    for i, ln in enumerate(M.get("lanes") or []):
        p = ways[i]
        if ln.get("connector") or len(p) < 2 or polyline_len(p) < 1.0:
            continue
        for end, q, b in ((-1, p[-1], p[-2]), (0, p[0], p[1])):
            if not free_end(ways, i, q) or math.dist(q, b) < 1e-6:
                continue
            head = ((q[0] - b[0]) / math.dist(q, b), (q[1] - b[1]) / math.dist(q, b))
            best: tuple[float, int, Pt] | None = None
            for k, o in enumerate(ways):
                if k == i or len(o) < 2:
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
forks and rejoins around nothing"). A village block holds a steading and is five times as wide. A map drawing convention."""


def needle_loops(M: Mapping[str, Any]) -> list[tuple[Any, list[int]]]:
    """(face, the lanes bounding it) for every face of the drawn lane web (the treads noded where they cross, then
    polygonized) whose mean width is under `NEEDLE_LOOP_FT` - two ways laid round a sliver of ground, or along the same
    ground (a face of no area at all)."""
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


def short_fragments(M: Mapping[str, Any]) -> list[int]:
    """The lanes shorter than `FRAGMENT_FT` (the connector and the field spur aside) that earn nothing: taking one away
    leaves no farmhouse newly unreached (`unreached_houses`) and the web in as many networks (`lane_networks`) - a fragment
    the passes whittled down and nothing re-asked (homes H40; future-work 2c's 4 ft fragment). A short run that is some
    house's way, or the link that joins two pieces, earns its place and is not one."""
    lanes = M.get("lanes") or []
    short = [i for i, ln in enumerate(lanes) if not ln.get("connector") and not ln.get("spur") and len(ln.get("pts") or []) >= 2 and polyline_len(lane_pts(ln)) < FRAGMENT_FT]
    if not short:
        return []
    reached, nets, targets, field = len(unreached_houses(M)), lane_networks(M), len(unreached_targets(M)), field_unreached(M)
    out = []
    for i in short:
        without = {**M, "lanes": [ln for k, ln in enumerate(lanes) if k != i]}
        # ...nor a way target (a burial ground's edge) newly unreached, nor the field (feature 287: a short spur to the graves
        # or on to the bund earns its place as a house's door path does)
        if len(unreached_houses(without)) <= reached and lane_networks(without) <= nets and len(unreached_targets(without)) <= targets and field_unreached(without) <= field:
            out.append(i)
    return out


def width_steps(lanes: Lanes) -> list[tuple[int, int]]:
    """The joints (`joints`: two lane ends meeting, no third way there) where one way changes width - a back lane halving
    its tread where nothing happens (homes H42, future-work "THE WIDTH STEP"): (lane, lane) for each."""
    return [(i, j) for i, _ei, j, _ej in joints(lanes) if float(lanes[i].get("w") or 3.0) != float(lanes[j].get("w") or 3.0)]


def lane_networks(M: Mapping[str, Any]) -> int:
    """How many networks the drawn lanes fall into at the ink tolerance (`JOIN_TOL`): one, or you cannot walk between
    them."""
    ways = [p for p in _ways(M) if len(p) >= 2]
    return len(set(_components(ways, JOIN_TOL)))


# ---- where lanes end -----------------------------------------------------------------------------------------------


def way_targets(M: Mapping[str, Any]) -> list[Pt]:
    """The points a way must reach (`meta.way_targets`: a burial ground's edge nearest the houses, homes H36)."""
    return [(float(t["at"][0]), float(t["at"][1])) for t in (M.get("meta") or {}).get("way_targets") or []]


TARGET_REACH_FT = 14.0
"""A way target is reached where the served network comes this near it: the spur drawn to it ends on it, and a lane passing
nearer than a doubled tread's distance (`sweeps._ALONG_FT`) stands at it. A map drawing convention."""


def unreached_targets(M: Mapping[str, Any]) -> list[Pt]:
    """The way targets (`way_targets`) the served network (`served_network`) does not come within `TARGET_REACH_FT` of."""
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
    near edge) is something worth walking to, as a farmhouse is (homes H36: a path runs to the graves)."""
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
            # ...AND A WAY IS REACHED ONLY WHERE THE END GOT NEARER TO IT THAN THE LANE'S FAR END ALREADY STOOD (feature 293,
            # settlement-review of Inashiro): a 32 ft skeleton stub left the connector at the entrance and ended in the
            # windbreak, 58 ft from the exit strip's end at that same junction - inside `WAY_END_REACH_FT`, so it "reached" the
            # junction it had left. The nearest point of each other way is asked: nearer the far end than the end, the lane
            # walked away from it, not to it.
            segs = [sg for sg in others if seg_dist(far[0], far[1], sg[0], sg[1]) > _TOUCH_GAP and _walked_to(end, far, sg)]
            if not end_serves(end, segs, centers, ground, steadings):
                out.append((i, e))
    return out


def dangling_ends(M: Mapping[str, Any]) -> list[tuple[int, int]]:
    """Every internal lane end that reaches nothing but the way it left (`dangling_lane_ends`), by where it stands."""
    ways = _ways(M)
    return sorted({(round(ways[i][e][0]), round(ways[i][e][1])) for i, e in dangling_lane_ends(M)})


def fronting_ends(M: Mapping[str, Any]) -> dict[int, list[tuple[int, int]]]:
    """The free lane ends (the connector's aside; an end within `JOIN_TOL` of another way is discharged by the junction)
    each farmhouse discharges, as (lane index, end) - an end whose nearest farmhouse center is within `DOORSTEP_FT`."""
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
            if min((_min_dist(end, o) for k, o in enumerate(ways) if k != i and len(o) >= 2), default=1e9) <= JOIN_TOL:
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
    B17, research/homesteads/310: a lane that serves a farmhouse ends at its dooryard, and a lane end behind a house's back
    wall does not count as reaching it - Kuwabata's lane 5, 11 ft behind house 1 and 43 ft from its yard)."""
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
    """The farmhouses that discharge more than `DOORSTEP_MAX` free lane ends apiece (`fronted_ends`)."""
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
    cell's; the first within the reach answers, by the same `seg_dist`."""
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
touches the glyph reads as walking over it."""


def fixture_quads(M: Mapping[str, Any]) -> list[Poly]:
    """Every farmstead fixture's drawn quad (`farm_fixtures`: privy, manure heap, bath, coop, hokora), turned as drawn, and
    every yard persimmon's TRUNK box (feature 287, homes H43: the persimmon is seated with its household before the web, so
    the web keeps its trunk off the tread as it keeps a privy - a lane may pass under the crown, never through the trunk;
    cohort seed 42 laid a straggler through a neighbor's persimmon). The box is the seating's own (`fixture_seats.TRUNK_FT`,
    which its own door corridor keeps off), so a tread clear of it is clear of the trunk (`stands.trunk_on_tread`)."""
    quads = [rot_rect(float(r["x"]), float(r["y"]), float(r["w"]), float(r["h"]), float(r.get("rot") or 0.0)) for r in M.get("farm_fixtures") or [] if all(k in r for k in ("x", "y", "w", "h"))]
    trunk = TRUNK_FT / float((M.get("meta") or {}).get("ftpx") or 1.0)
    return quads + [rot_rect(float(r["x"]), float(r["y"]), trunk, trunk, 0.0) for r in M.get("persimmons") or [] if "x" in r and "y" in r]


def over_a_fixture(pts: Sequence[Pt], width: float, quads: Sequence[Poly]) -> int | None:
    """The first segment of a lane along `pts`, drawn `width` wide, whose tread meets a farmstead fixture (`fixture_quads`) -
    crosses it, stands in it, or passes within its half-width and `FIXTURE_PAD_FT` of it; None where it meets none. THE ONE
    PREDICATE: the web's settle cuts what it names, a tree lane is refused by it, and the finished-map rule reads it."""
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
    (`track.connector_through`) all ask it."""
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
    solid = solid_boxes(M)
    return [(round(mid[0]), round(mid[1])) for p in _ways(M) for _k, mid in breaks_through(p, solid)]


def fouls_fabric(pts: Poly, width: float, houses: Sequence[Mapping[str, Any]], fabric: Sequence[tuple[Poly, Pt | None, str]], own: Pt | None = None) -> bool:
    """Does a lane of this width along `pts` put ink on a farmhouse (`house_hit`), or pass within `_TOUCH_GAP` of another
    household's threshing yard or garden (`_crosses_fabric`)? `fabric` is `_homestead_polys`' (polygon, owner, kind); a door
    path is exempt only from its OWN steading's yard and garden (`own`, its house's center)."""
    if house_hit(pts, width, houses):
        return True
    theirs = [poly for poly, owner, kind in fabric if kind in ("threshing_yards", "gardens") and (own is None or owner != own)]
    return _crosses_fabric(pts, theirs, _TOUCH_GAP)


# ---- water ---------------------------------------------------------------------------------------------------------


def _crossings(p: Poly, course: Poly) -> list[Pt]:
    return [x for _k, x in crossing_points(p, course)]


def over_and_back(M: Mapping[str, Any]) -> list[tuple[int, int]]:
    """(lane index, crossings) for every lane crossing one brook twice or more - out and home, two planks for nothing."""
    ways = _ways(M)
    return [(i, n) for brook in _brooks(M) for i, p in enumerate(ways) if (n := len(_crossings(p, brook))) >= 2]


def crossing_points(p: Poly, course: Poly) -> list[tuple[int, Pt]]:
    """(segment index, point) for every crossing of `course` by the run `p`, in the run's order.

    THE COURSE INDEXED ONCE (constitution X clause 15): a household's way out is sampled every 10 ft and a brook runs to
    hundreds of segments, so every pair was millions of tests a map (`settle_the_web`'s way-out step, 4.3 s of Kashikawa's
    5.0). The grid only prunes - a course segment whose box cannot meet the run segment's cannot cross it - and the same
    test decides, in the same order."""
    grid = PointGrid(64.0)
    grid.extend((j, c, d, min(c[0], d[0]), min(c[1], d[1]), max(c[0], d[0]), max(c[1], d[1])) for j, (c, d) in enumerate(zip(course, course[1:], strict=False)))
    out = []
    for k, (a, b) in enumerate(zip(p, p[1:], strict=False)):
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        near = {item[0]: item for item in grid.near(mx, my, math.dist(a, b) / 2 + 1.0)}
        for j in sorted(near):
            _j, c, d, *_box = near[j]
            if segments_cross(a, b, c, d) and (x := seg_intersect(a, b, c, d)) is not None:
                out.append((k, x))
    return out


def off_ford_at(M: Mapping[str, Any], reach: float = FORD_HALF) -> list[tuple[int, int, Pt]]:
    """(lane index, segment index, point) for every crossing of the brook by a lane farther than `reach` from every
    recorded ford (`meta.brook_fords`)."""
    fords = [(float(f[0]), float(f[1])) for f in (M.get("meta") or {}).get("brook_fords") or []]
    return [(i, k, x) for brook in _brooks(M) for i, p in enumerate(_ways(M)) for k, x in crossing_points(p, brook) if min((math.dist(x, f) for f in fords), default=math.inf) > reach]


def off_ford_crossings(M: Mapping[str, Any], reach: float = FORD_HALF) -> list[tuple[int, int]]:
    """Every crossing of the brook by a lane that stands farther than `reach` from every recorded ford
    (`meta.brook_fords`) - ONE constant with the router's ford gap (`off_ford_at`)."""
    return [(round(x[0]), round(x[1])) for _i, _k, x in off_ford_at(M, reach)]


def water_courses(M: Mapping[str, Any], water: str = "brook") -> list[Poly]:
    """The brook's courses (`water="brook"`, the streams) or the drawn channels' (`water="channel"`)."""
    return _brooks(M) if water == "brook" else [[(float(q[0]), float(q[1])) for q in c["pts"]] for c in M.get("drawn_channels") or []]


def off_square(a: Pt, b: Pt, u: Pt, v: Pt) -> float:
    """How many degrees the run `a`-`b` crosses the course `u`-`v` off square."""
    t = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]) - math.atan2(v[1] - u[1], v[0] - u[0])) % 180.0
    return abs(90.0 - t)


def oblique_at(M: Mapping[str, Any], water: str = "brook") -> list[tuple[int, int, Pt, float]]:
    """(lane index, segment index, point, degrees off square) for every lane crossing of the brook or a drawn channel
    (`water_courses`) more than `FORD_SQUARE_TOL_DEG` off square."""
    out = []
    for course in water_courses(M, water):
        for i, p in enumerate(_ways(M)):
            for k, (a, b) in enumerate(zip(p, p[1:], strict=False)):
                for u, v in zip(course, course[1:], strict=False):
                    if segments_cross(a, b, u, v) and (off := off_square(a, b, u, v)) > FORD_SQUARE_TOL_DEG:
                        out.append((i, k, seg_intersect(a, b, u, v) or a, off))
    return out


def oblique_crossings(M: Mapping[str, Any], water: str = "brook") -> list[tuple[int, int, float]]:
    """(x, y, degrees off square) for every lane crossing more than `FORD_SQUARE_TOL_DEG` off square - of the brook
    (`water="brook"`, the streams) or of a drawn channel (`water="channel"`, `drawn_channels`) (`oblique_at`)."""
    return [(round(x[0]), round(x[1]), round(off, 1)) for _i, _k, x, off in oblique_at(M, water)]


def unbridged_crossings(M: Mapping[str, Any]) -> list[tuple[int, int]]:
    """Every crossing of water by a lane that no drawn deck covers (`deck_covers`): the brook, and every other course a way
    may have to be carried over (`bridge_crossed_waters`) - a drawn channel, a field ditch, the polder's drain (feature
    287: the drain takes no footplank, `plank_on_supply`, so a way over it is carried on the deck `bridges()` lays where
    the web's last pass left a crossing it can deck, and cut where it could not - never walked through the water)."""
    decks = M.get("bridges") or []
    waters = [*_brooks(M), *([(float(q[0]), float(q[1])) for q in wpts] for wpts, _w in bridge_crossed_waters(M) if len(wpts) >= 2)]
    hits = {(round(x[0]), round(x[1])) for course in waters for p in _ways(M) for x in _crossings(p, course) if not any(deck_covers(d, x[0], x[1]) for d in decks)}
    return sorted(hits)


def deck_seats(pts: Poly, width: float, waters: Sequence[tuple[Any, float]], ftpx: float = 1.0, wet: Sequence[Poly] = (), M: Any = None) -> list[tuple[int, int]]:
    """Every crossing of `waters` (`bridge_crossed_waters`) by a way along `pts` where no deck seats: `crossing_deck`, the
    very solve `bridges()` makes - grown, then skewed toward square, until every corner clears the whole crossed course
    (`_deck_corners_clear`) and lands off the flooded rice (`wet`, `flooded_ground`) (`undeckable_at`)."""
    return [(round(p[0]), round(p[1])) for _k, p in undeckable_at(pts, width, waters, ftpx, wet, M)]


def undeckable_crossings(M: Mapping[str, Any]) -> list[tuple[int, int]]:
    """`deck_seats` over every carried way of the map (`bridge_carried_ways`) against every watercourse it may cross."""
    ftpx = float((M.get("meta") or {}).get("ftpx") or 1.0)
    waters = bridge_crossed_waters(M)
    wet = flooded_ground(M)
    return [x for rpts, rw in bridge_carried_ways(M) for x in deck_seats([(float(q[0]), float(q[1])) for q in rpts], float(rw), waters, ftpx, wet, M)]


def short_decks(M: Mapping[str, Any]) -> list[tuple[int, int, float, float]]:
    """(x, y, span, water width) for every deck over a recorded watercourse (within `DECK_NEAR_FT` of it) shorter than that
    course's full width - its abutment stands in the water (`bridges_span_their_water`)."""
    courses = [([(float(p[0]), float(p[1])) for p in d["poly"]], max(float(d.get("w", 3.0)), float(d.get("w_tail", 3.0)))) for d in (M.get("field_ditches") or [])]
    courses += [([(float(p[0]), float(p[1])) for p in c["poly"]], float(c.get("w", 3.0))) for c in (M.get("channels") or [])]
    courses += [([(float(p[0]), float(p[1])) for p in s["poly"]], float(s.get("w", 6.0))) for s in (M.get("streams") or [])]
    short = []
    for b in M.get("bridges") or []:
        bx, by, span = float(b["x"]), float(b["y"]), float(b["span"])
        near = min(((_min_dist((bx, by), poly), w) for poly, w in courses if len(poly) >= 2), key=lambda t: t[0], default=(math.inf, 0.0))
        if near[0] <= DECK_NEAR_FT and span < near[1]:
            short.append((round(bx), round(by), round(span, 1), round(near[1], 1)))
    return short


def plank_faults(M: Mapping[str, Any]) -> tuple[list[tuple[int, int]], list[tuple[int, int, str]]]:
    """(stranded, on the drain): footplanks farther than `PLANK_DITCH_FT` from every recorded field ditch, and planks whose
    nearest ditch is not a supply ditch (`SUPPLY_ROLES`: a main, a branch or a lateral) - the collector, the drain or the
    feeder. `plank_ditch` and `plank_on_supply` are the placer's own (`channel_footbridges`, ways W14).

    THE LATERAL IS A SUPPLY DITCH (feature 287; Kuwabata's six planks). The test this was lifted from read the comb's two roles
    only, and so named every plank on a polder's laterals and settlement-side ring canal - which record the role `lateral` -
    as laid on a drain. The record answers it: a plank is laid where a bund path meets an IRRIGATION ditch (research/ways/030),
    and the polder's inner ring canal and its field ditches are its distribution water (research/archetypes/110)."""
    ditches = M.get("field_ditches") or []
    stranded, on_drain = [], []
    for b in M.get("bridges") or []:
        if not b.get("foot"):
            continue
        pt = (float(b["x"]), float(b["y"]))
        dist, role = plank_ditch(pt, ditches)
        if dist >= PLANK_DITCH_FT:
            stranded.append((round(pt[0]), round(pt[1])))
        elif not plank_on_supply(pt, ditches):
            on_drain.append((round(pt[0]), round(pt[1]), str(role)))
    return stranded, on_drain


# ---- the ways out --------------------------------------------------------------------------------------------------


def way_outs_crossing(M: Mapping[str, Any], routes: Sequence[Sequence[Pt]] | None = None) -> list[tuple[int, int, int]]:
    """(x, y, crossings) for every household's way out (`departure_routes`) that crosses one brook more than once."""
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
    web asks before it lays a tree lane (`settle.Lawful`), which no repair takes away afterwards."""
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
