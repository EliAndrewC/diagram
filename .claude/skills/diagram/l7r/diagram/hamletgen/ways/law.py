"""The lane law: every rule a finished lane web must keep, each as ONE predicate (feature 287, M1).

A LIFT, NOT A RE-DERIVATION. Each predicate below is the body a finished-map test asserts - `tests/gate/test_lane_network.py`,
`tests/gate/test_cohort_lane_rules.py`, `tests/gate/test_crossings_and_cover.py` and the ways rows of
`tests/hamletgen/test_pool_261.py` - moved into the engine, and those tests now call it. The placer that owns a rule
(`settle_the_web`, the ways phase of feature 287) will call the same predicate, which is the skill's standing rule
("placement and its check must read the SAME source") made structural: there is one body per rule, so the two cannot
drift. The acceptance sweep (M9) runs `violations` over every finished map, so this module is the registry of the rules.

Every predicate answers with what VIOLATES the rule - an empty list (or zero, or False) is a pass - so a test states the
found thing in its failure message and a placer knows where to cut.

WHERE THE PLACER AND ITS TEST READ A RULE DIFFERENTLY TODAY, the predicate is the TEST's reading (feature 287's brief for
P1: predicates only, no placer change); the ways phase moves each placer onto it:

- the BEND (`bends_badly`): the tests sum the path between two 50 degree turns; `clearance._bends_badly`, which the web's
  passes ask, tests two turns separated by ONE segment - a lattice step of two short legs passes it and fails the test.
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

from l7r.diagram.settlement import seg_dist, seg_intersect, segments_cross
from l7r.diagram.settlement._knobs import bridge_carried_ways, bridge_crossed_waters
from l7r.diagram.settlement.city.bridges import crossing_deck
from l7r.diagram.settlement.structures.fixtures._helpers import departure_routes

from ..consts import FORD_HALF, Poly, Pt
from .checks import FORD_SQUARE_TOL_DEG, unreached_houses
from .clearance import _HAIRPIN_DEG, _ZIGZAG_DEG, _ZIGZAG_RUN_FT
from .fabric import _crosses_fabric, house_hit
from .geom import _TOUCH_GAP, _components, _turn_deg, end_serves, steading_footprints, worked_ground
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

DECK_SPAN_DEFAULT_FT = 20.0
"""A deck that records no span is read as this long when asking whether it covers a crossing (the test's default)."""

DECK_NEAR_FT = 40.0
"""A deck this near a recorded watercourse is over it, and is judged against that course's width."""

PLANK_DITCH_FT = 24.0
"""A footplank this near a recorded field ditch is on that ditch; farther, it crosses no recorded ditch at all."""

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
    turns, not one segment."""
    p = list(pts)
    bad: list[tuple[str, int, int]] = []
    if len(p) < 3:
        return bad
    turns: list[int] = []
    for k in range(1, len(p) - 1):
        v1 = (p[k][0] - p[k - 1][0], p[k][1] - p[k - 1][1])
        v2 = (p[k + 1][0] - p[k][0], p[k + 1][1] - p[k][1])
        if math.hypot(*v1) < 1e-6 or math.hypot(*v2) < 1e-6:
            continue
        deg = _turn_deg(p[k - 1], p[k], p[k + 1])
        if deg >= DOUBLE_BACK_DEG:
            bad.append(("doubles back", round(p[k][0]), round(p[k][1])))
        elif deg >= KINK_DEG:
            turns.append(k)
    for ka, kb in zip(turns, turns[1:], strict=False):
        if sum(math.dist(p[j], p[j + 1]) for j in range(ka, kb)) <= BEND_RUN_FT:
            bad.append(("kinks", round(p[ka][0]), round(p[ka][1])))
    return bad


def bends_badly(pts: Sequence[Pt]) -> bool:
    """Does this run fail to bend like a path (`kinks`)?"""
    return bool(kinks(pts))


def lanes_that_kink(M: Mapping[str, Any]) -> list[tuple[str, int, int]]:
    """`kinks` over every lane but the connector (`lanes_bend_like_paths`)."""
    return [k for ln in (M.get("lanes") or []) if not ln.get("connector") for k in kinks(lane_pts(ln))]


def hooks(pts: Sequence[Pt]) -> list[tuple[int, int]]:
    """The vertex before each hooked end: a first or last leg of `_HOOK_FT` or less turning `_HOOK_DEG` or more."""
    p = list(pts)
    if len(p) < 3:
        return []
    return [(round(q[-2][0]), round(q[-2][1])) for q in (p, p[::-1]) if math.dist(q[-2], q[-1]) <= _HOOK_FT and _turn_deg(q[-3], q[-2], q[-1]) >= _HOOK_DEG]


def hooked_ends(M: Mapping[str, Any]) -> list[tuple[int, int]]:
    """`hooks` over EVERY lane, the connector included."""
    return [h for ln in (M.get("lanes") or []) for h in hooks(lane_pts(ln))]


def husks(M: Mapping[str, Any]) -> list[int]:
    """The lane records that draw nothing: under two points, or under 1 ft long."""
    return [i for i, p in enumerate(_ways(M)) if len(p) < 2 or sum(math.dist(a, b) for a, b in zip(p, p[1:], strict=False)) < 1.0]


# ---- where lanes meet ----------------------------------------------------------------------------------------------


def folded_joints(lanes: Lanes) -> list[tuple[int, int]]:
    """Where two lanes meeting end to end - one way to the walker (`joints`) - turn `DOUBLE_BACK_DEG` or more at the joint."""
    out = []
    for i, ei, j, ej in joints(lanes):
        x, y = oriented(lanes, i, ei, j, ej)
        if _turn_deg(x[-2], x[-1], y[1]) >= DOUBLE_BACK_DEG:
            out.append((round(x[-1][0]), round(x[-1][1])))
    return out


def connector_hairpins(lanes: Lanes) -> list[tuple[int, int]]:
    """Where a lane's short last leg meets the connector's start and the two double back (`hairpin_over_a_short_leg`)."""
    out = []
    for co in lanes:
        cp = lane_pts(co)
        if not co.get("connector") or len(cp) < 2:
            continue
        for ln in lanes:
            p = lane_pts(ln)
            if ln.get("connector") or len(p) < 3:
                continue
            for seq in (p, p[::-1]):
                a, b, j = seq[-3], seq[-2], seq[-1]
                if math.dist(j, cp[0]) <= CONNECTOR_START_FT and hairpin_over_a_short_leg(a, b, j, cp[1]):
                    out.append((round(j[0]), round(j[1])))
    return out


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


def needle_joins(lanes: Lanes) -> list[tuple[int, int]]:
    """Where a lane's last leg, longer than `NEEDLE_FT`, meets another way's tread (within `JOIN_TOL`) and runs back along
    it at under `NEEDLE_DEG` - a needle rather than a T. A leg carrying straight on from a way's END is not a needle: the
    tread it meets does not run back beside it."""
    ways = [lane_pts(ln) for ln in lanes]
    out = []
    for i, ln in enumerate(lanes):
        p = ways[i]
        if ln.get("connector") or len(p) < 2:
            continue
        for q, b in ((p[-1], p[-2]), (p[0], p[1])):
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
                        out.append((round(q[0]), round(q[1])))
    return sorted(set(out))


def doubled_tails(M: Mapping[str, Any]) -> list[int]:
    """The lanes (the connector aside) whose end runs on beside another way, at `_DOUBLED_DEG` (`along_tail`), whatever the
    two ways' widths."""
    ways = _ways(M)
    lanes = M.get("lanes") or []
    return [
        i for i, p in enumerate(ways) if not lanes[i].get("connector") and len(p) >= 2 and any(j != i and len(o) >= 2 and along_tail(p, o, deg=_DOUBLED_DEG) is not None for j, o in enumerate(ways))
    ]


def lane_networks(M: Mapping[str, Any]) -> int:
    """How many networks the drawn lanes fall into at the ink tolerance (`JOIN_TOL`): one, or you cannot walk between
    them."""
    ways = [p for p in _ways(M) if len(p) >= 2]
    return len(set(_components(ways, JOIN_TOL)))


# ---- where lanes end -----------------------------------------------------------------------------------------------


def dangling_ends(M: Mapping[str, Any]) -> list[tuple[int, int]]:
    """Every internal lane end that reaches nothing (`end_serves`) other than the way its own far end stands on: the other
    ways' segments are asked, less those within `_TOUCH_GAP` of the lane's far end."""
    ways = _ways(M)
    centers = [(float(h["x"]), float(h["y"])) for h in M.get("houses") or []]
    steadings = steading_footprints(M)
    ground = worked_ground(M)
    out = []
    for i, ln in enumerate(M.get("lanes") or []):
        p = ways[i]
        if ln.get("connector") or len(p) < 2:
            continue
        others = [sg for k, o in enumerate(ways) if k != i and len(o) >= 2 for sg in zip(o, o[1:], strict=False)]
        for end, far in ((p[-1], p[0]), (p[0], p[-1])):
            segs = [sg for sg in others if seg_dist(far[0], far[1], sg[0], sg[1]) > _TOUCH_GAP]
            if not end_serves(end, segs, centers, ground, steadings):
                out.append((round(end[0]), round(end[1])))
    return sorted(set(out))


def fronted_ends(M: Mapping[str, Any]) -> dict[int, int]:
    """How many free lane ends (the connector's aside; an end within `JOIN_TOL` of another way is discharged by the
    junction) each farmhouse discharges - an end whose nearest farmhouse center is within `DOORSTEP_FT`."""
    ways = _ways(M)
    houses = M.get("houses") or []
    fronted: dict[int, int] = {}
    if not houses:
        return fronted
    for i, ln in enumerate(M.get("lanes") or []):
        p = ways[i]
        if ln.get("connector") or len(p) < 2:
            continue
        for end in (p[0], p[-1]):
            if min((_min_dist(end, o) for k, o in enumerate(ways) if k != i and len(o) >= 2), default=1e9) <= JOIN_TOL:
                continue
            best = min(range(len(houses)), key=lambda h: math.hypot(end[0] - houses[h]["x"], end[1] - houses[h]["y"]))
            if math.hypot(end[0] - houses[best]["x"], end[1] - houses[best]["y"]) <= DOORSTEP_FT:
                fronted[best] = fronted.get(best, 0) + 1
    return fronted


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
    """On a brook map, no way of the hamlet's own comes within `FIELD_REACH_FT` of its field."""
    return bool(_brooks(M)) and field_reach_ft(M) > FIELD_REACH_FT


# ---- the fabric ----------------------------------------------------------------------------------------------------


def solid_boxes(M: Mapping[str, Any]) -> list[tuple[float, float, float, float]]:
    """The axis boxes of the buildings a lane may not run through: houses, farm sheds and byres."""
    solid = []
    for key in ("houses", "farm_sheds", "byres"):
        for r in M.get(key) or []:
            if "x" in r and "w" in r:
                hw, hh = r["w"] / 2, r["h"] / 2
                solid.append((r["x"] - hw, r["y"] - hh, r["x"] + hw, r["y"] + hh))
    return solid


def breaks_mid_run(M: Mapping[str, Any]) -> list[tuple[int, int]]:
    """The midpoints of lane segments longer than `BREAK_SPAN_FT` that stand inside a building's box (`solid_boxes`)."""
    solid = solid_boxes(M)
    gaps = []
    for p in _ways(M):
        for i in range(len(p) - 1):
            if math.dist(p[i], p[i + 1]) <= BREAK_SPAN_FT:
                continue
            mid = ((p[i][0] + p[i + 1][0]) / 2, (p[i][1] + p[i + 1][1]) / 2)
            if any(x0 <= mid[0] <= x1 and y0 <= mid[1] <= y1 for x0, y0, x1, y1 in solid):
                gaps.append((round(mid[0]), round(mid[1])))
    return gaps


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
    return [x for a, b in zip(p, p[1:], strict=False) for c, d in zip(course, course[1:], strict=False) if segments_cross(a, b, c, d) and (x := seg_intersect(a, b, c, d)) is not None]


def over_and_back(M: Mapping[str, Any]) -> list[tuple[int, int]]:
    """(lane index, crossings) for every lane crossing one brook twice or more - out and home, two planks for nothing."""
    ways = _ways(M)
    return [(i, n) for brook in _brooks(M) for i, p in enumerate(ways) if (n := len(_crossings(p, brook))) >= 2]


def off_ford_crossings(M: Mapping[str, Any], reach: float = FORD_HALF) -> list[tuple[int, int]]:
    """Every crossing of the brook by a lane that stands farther than `reach` from every recorded ford
    (`meta.brook_fords`) - ONE constant with the router's ford gap."""
    fords = [(float(f[0]), float(f[1])) for f in (M.get("meta") or {}).get("brook_fords") or []]
    return [(round(x[0]), round(x[1])) for brook in _brooks(M) for p in _ways(M) for x in _crossings(p, brook) if min((math.dist(x, f) for f in fords), default=math.inf) > reach]


def oblique_crossings(M: Mapping[str, Any], water: str = "brook") -> list[tuple[int, int, float]]:
    """(x, y, degrees off square) for every lane crossing more than `FORD_SQUARE_TOL_DEG` off square - of the brook
    (`water="brook"`, the streams) or of a drawn channel (`water="channel"`, `drawn_channels`)."""
    courses = _brooks(M) if water == "brook" else [[(float(q[0]), float(q[1])) for q in c["pts"]] for c in M.get("drawn_channels") or []]
    out = []
    for course in courses:
        for p in _ways(M):
            for a, b in zip(p, p[1:], strict=False):
                for u, v in zip(course, course[1:], strict=False):
                    if segments_cross(a, b, u, v):
                        t = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]) - math.atan2(v[1] - u[1], v[0] - u[0])) % 180.0
                        if abs(90.0 - t) > FORD_SQUARE_TOL_DEG:
                            x = seg_intersect(a, b, u, v) or a
                            out.append((round(x[0]), round(x[1]), round(abs(90.0 - t), 1)))
    return out


def deck_covers(deck: Mapping[str, Any], x: float, y: float) -> bool:
    """Does this deck's own span reach the point (x, y)?"""
    return math.hypot(float(deck["x"]) - x, float(deck["y"]) - y) <= float(deck.get("span", DECK_SPAN_DEFAULT_FT))


def unbridged_crossings(M: Mapping[str, Any]) -> list[tuple[int, int]]:
    """Every crossing of the brook by a lane that no drawn deck covers (`deck_covers`)."""
    decks = M.get("bridges") or []
    return [(round(x[0]), round(x[1])) for brook in _brooks(M) for p in _ways(M) for x in _crossings(p, brook) if not any(deck_covers(d, x[0], x[1]) for d in decks)]


def deck_seats(pts: Poly, width: float, waters: Sequence[tuple[Any, float]], ftpx: float = 1.0) -> list[tuple[int, int]]:
    """Every crossing of `waters` (`bridge_crossed_waters`) by a way along `pts` where no deck seats: `crossing_deck`, the
    very solve `bridges()` makes - grown, then skewed toward square, until every corner clears the whole crossed course
    (`_deck_corners_clear`)."""
    out = []
    for ra, rb in zip(pts, pts[1:], strict=False):
        for wpts, ww in waters:
            wp = [(float(q[0]), float(q[1])) for q in wpts]
            for wa, wb in zip(wp, wp[1:], strict=False):
                if segments_cross(ra, rb, wa, wb):
                    p, _rot, _span, seated = crossing_deck(ra, rb, width, wa, wb, float(ww), wp, ftpx)
                    if not seated:
                        out.append((round(p[0]), round(p[1])))
    return out


def undeckable_crossings(M: Mapping[str, Any]) -> list[tuple[int, int]]:
    """`deck_seats` over every carried way of the map (`bridge_carried_ways`) against every watercourse it may cross."""
    ftpx = float((M.get("meta") or {}).get("ftpx") or 1.0)
    waters = bridge_crossed_waters(M)
    return [x for rpts, rw in bridge_carried_ways(M) for x in deck_seats([(float(q[0]), float(q[1])) for q in rpts], float(rw), waters, ftpx)]


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
    nearest ditch is not a supply ditch (a main or a branch) - the collector, the drain or the feeder."""
    supply = [([(float(p[0]), float(p[1])) for p in d["poly"]], d.get("role")) for d in (M.get("field_ditches") or [])]
    stranded, on_drain = [], []
    for b in M.get("bridges") or []:
        if not b.get("foot"):
            continue
        pt = (float(b["x"]), float(b["y"]))
        near = min(((_min_dist(pt, poly), role) for poly, role in supply if len(poly) >= 2), key=lambda t: t[0], default=(math.inf, None))
        if near[0] >= PLANK_DITCH_FT:
            stranded.append((round(pt[0]), round(pt[1])))
        elif near[1] not in ("main", "branch"):
            on_drain.append((round(pt[0]), round(pt[1]), str(near[1])))
    return stranded, on_drain


# ---- the ways out --------------------------------------------------------------------------------------------------


def way_outs_crossing(M: Mapping[str, Any], routes: Sequence[Sequence[Pt]] | None = None) -> list[tuple[int, int, int]]:
    """(x, y, crossings) for every household's way out (`departure_routes`) that crosses one brook more than once."""
    routes = departure_routes(M) if routes is None else routes
    out = []
    for brook in _brooks(M):
        for r in routes:
            n = sum(1 for a, b in zip(r, r[1:], strict=False) for c, d in zip(brook, brook[1:], strict=False) if segments_cross(a, b, c, d))
            if n > 1:
                out.append((round(r[0][0]), round(r[0][1]), n))
    return out


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
    "dangling_ends": dangling_ends,
    "doorstep_ends": doorstep_ends,
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
}
"""Every lane rule a finished map is asked, by name - the acceptance sweep's (M9) reading of this module. A rule's value is
falsy when the map keeps it. `fouls_fabric` and `deck_seats` are asked of one candidate way, not of a manifest, and are
reached here through `breaks_mid_run` and `undeckable_crossings`."""


def violations(M: Mapping[str, Any]) -> dict[str, Any]:
    """Every rule of `LAW` this map breaks, with what breaks it."""
    return {name: v for name, rule in LAW.items() if (v := rule(M))}
