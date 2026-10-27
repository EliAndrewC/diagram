"""the lane law where lanes END, the fabric they keep off and the water they cross (split from `law.py` at the 1,000-line bar, feature 417 T54).

Research: plumbing and wrappers - NONE: each rule is claimed at the predicate that decides it
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import point_in_poly, rot_rect, seg_closest, seg_dist
from l7r.diagram.settlement._geom.indexes import PointGrid
from l7r.diagram.settlement.city.bridges import DECK_SPAN_DEFAULT_FT as DECK_SPAN_DEFAULT_FT
from l7r.diagram.settlement.city.bridges import PLANK_DITCH_FT as PLANK_DITCH_FT
from l7r.diagram.settlement.city.bridges import deck_covers as deck_covers
from l7r.diagram.settlement.city.bridges import undeckable_at as undeckable_at
from l7r.diagram.settlement.homestead_parts.fixture_seats import TRUNK_FT
from l7r.diagram.settlement.structures.fixtures._helpers import departure_routes

from ...consts import WAY_END_REACH_FT, Poly, Pt
from ..checks import served_network, unreached_houses
from ..fabric import _crosses_fabric
from ..geom import _TOUCH_GAP, WorkedGround, end_serves, polyline_len, steading_footprints, worked_ground
from ..law_water import _bbox
from ..law_water import (
    _brooks as _brooks,
)
from ..law_water import (
    _min_dist as _min_dist,
)
from ..law_water import (
    _ways as _ways,
)
from ..law_water import (
    crossing_points as crossing_points,
)
from ..law_water import (
    lane_pts as lane_pts,
)
from .meet import free_end, lane_networks
from .shape import (
    BREAK_SPAN_FT,
    DOORSTEP_MAX,
    FIELD_REACH_FT,
    FRAGMENT_FT,
    Lanes,
    reach_to_steading,
)

# ---- where lanes end -----------------------------------------------------------------------------------------------


def way_targets(M: Mapping[str, Any]) -> list[Pt]:
    """The points a way must reach (`meta.way_targets`: a burial ground's edge nearest the houses, homes H36)."""
    return [(float(t["at"][0]), float(t["at"][1])) for t in (M.get("meta") or {}).get("way_targets") or []]


TARGET_REACH_FT = 14.0
"""A way target is reached where the served network comes this near it: the spur drawn to it ends on it, and a lane passing
nearer than a doubled tread's distance (`sweeps._ALONG_FT`) stands at it. A map drawing convention.

Research: a way target reached - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A2, 2026-10-25); within 14 ft of the served network"""


def unreached_targets(M: Mapping[str, Any]) -> list[Pt]:
    """The way targets (`way_targets`) the served network (`served_network`) does not come within `TARGET_REACH_FT` of.
    Research: a path runs to the graves - GUESS: searched, no page draws a path to the graves (feature 417 T29 pass A1, 2026-10-25) - 0224's notes have the graves and their paths cleaned in a modern account"""
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


def dangling_lane_ends(M: Mapping[str, Any], ground: WorkedGround | None = None, only: int | None = None) -> list[tuple[int, int]]:
    """(lane index, end) for every internal lane end that reaches nothing (`end_serves`) other than the way its own far
    end stands on: the other ways' segments are asked, less those within `_TOUCH_GAP` of the lane's far end. `ground` is the
    worked ground where the caller has it built already (`memo_ground`). A way target (`meta.way_targets`, a burial ground's
    near edge) is something worth walking to, as a farmhouse is (homes H36: a path runs to the graves). `only`, a lane's
    index, asks that lane's ends alone - the same verdict on it (a candidate at lay, `lay.laid_lawfully`, feature 417 T06).
    Research:
        an end reaches something seen - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: walked toward it
        a burial ground's edge a lane end's destination - GUESS: searched, the record silent (feature 417 T29 pass A2, 2026-10-25) on where a lane ends at the graves - 0224 has paths to the graves; a way target counts as a farmhouse does
        the connector exempt - research/questions/0081-village-lanes.drawing.html: the track out runs off the map, so its ends are not asked
        a way reached only where the lane walked to it - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A2, 2026-10-25); a way counts as reached only where the lane's end lies nearer it than
            its far end does (`_walked_to`) (405 T127)"""
    ways = _ways(M)
    centers = [(float(h["x"]), float(h["y"])) for h in M.get("houses") or []] + way_targets(M)
    steadings = steading_footprints(M)
    ground = worked_ground(M) if ground is None else ground
    out = []
    for i, ln in enumerate(M.get("lanes") or []):
        p = ways[i]
        if ln.get("connector") or len(p) < 2 or (only is not None and i != only):
            continue
        others = [sg for k, o in enumerate(ways) if k != i and len(o) >= 2 for sg in zip(o, o[1:], strict=False)]
        for e, end, far in ((-1, p[-1], p[0]), (0, p[0], p[-1])):
            # ...AND A WAY IS REACHED ONLY WHERE THE END GOT NEARER TO IT THAN THE LANE'S FAR END ALREADY STOOD (feature 293, settlement-review of Inashiro): a 32 ft skeleton
            # stub left the connector at the entrance and ended in the windbreak, 58 ft from the exit strip's end at that same junction - inside `WAY_END_REACH_FT`, so it
            # "reached" the junction it had left. The nearest point of each other way is asked: nearer the far end than the end, the lane walked away from it, not to it.
            # ...ONLY A LEG WITHIN THE END'S REACH CAN SERVE IT (`end_serves`), so the far end and the walk are asked of those alone
            # (feature 417 T06: every leg was asked both, 165,659 `seg_dist` on seed 39 at 40 households) - the same verdict
            ex, ey, r = end[0], end[1], WAY_END_REACH_FT
            near = [
                sg
                for sg in others
                if not (
                    (sg[0][0] - r > ex and sg[1][0] - r > ex) or (sg[0][0] + r < ex and sg[1][0] + r < ex) or (sg[0][1] - r > ey and sg[1][1] - r > ey) or (sg[0][1] + r < ey and sg[1][1] + r < ey)
                )
            ]
            segs = [sg for sg in near if seg_dist(far[0], far[1], sg[0], sg[1]) > _TOUCH_GAP and _walked_to(end, far, sg)]
            if not end_serves(end, segs, centers, ground, steadings):
                out.append((i, e))
    return out


def dangling_ends(M: Mapping[str, Any]) -> list[tuple[int, int]]:
    """Every internal lane end that reaches nothing but the way it left (`dangling_lane_ends`), by where it stands."""
    ways = _ways(M)
    return sorted({(round(ways[i][e][0]), round(ways[i][e][1])) for i, e in dangling_lane_ends(M)})


def fronting_ends(M: Mapping[str, Any]) -> dict[int, list[tuple[int, int]]]:
    """The free lane ends each farmhouse discharges, as (lane index, end) - an end that reaches its nearest farmhouse as 0246
    measures it (`reach_to_steading`) (the connector's aside; an end within `JOIN_TOL` of another way is discharged by the junction).
    Research:
        an end discharged by a house - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: within 60 ft of the nearest farmhouse or 12 ft of its steading's built ground
        an end discharged by a junction - NONE: an end within JOIN_TOL, the touch gap, of another way already meets it"""
    ways = _ways(M)
    houses = M.get("houses") or []
    fronted: dict[int, list[tuple[int, int]]] = {}
    if not houses:
        return fronted
    boxes = [_bbox(o) for o in ways]  # ...each way's box once: `free_end` passes over a way beyond the tolerance (feature 417 T06)
    for i, ln in enumerate(M.get("lanes") or []):
        p = ways[i]
        if ln.get("connector") or len(p) < 2:
            continue
        for e, end in ((0, p[0]), (-1, p[-1])):
            if not free_end(ways, i, end, boxes):  # the first junction answers
                continue
            best = min(range(len(houses)), key=lambda h: math.hypot(end[0] - houses[h]["x"], end[1] - houses[h]["y"]))
            if reach_to_steading(end, houses[best], M):  # 0246's reach (feature 328: it was DOORSTEP_FT from the center)
                fronted.setdefault(best, []).append((i, e))
    return fronted


def fronted_ends(M: Mapping[str, Any]) -> dict[int, int]:
    """How many free lane ends each farmhouse discharges (`fronting_ends`)."""
    return {h: len(ends) for h, ends in fronting_ends(M).items()}


def doorstep_ends(M: Mapping[str, Any]) -> dict[int, int]:
    """The farmhouses that discharge more than `DOORSTEP_MAX` free lane ends apiece (`fronted_ends`).
    Research: no fan of stubs at a door - GUESS: searched, the record silent (feature 417 T29 pass A2, 2026-10-25) - one main door served a minka's household (JAANUS, Edo period, pass A2); no page gives how many ends meet at one; more than two free ends within 80 ft"""
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
    Research:
        a way reaches the field - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: on brook maps
        asked on brook maps only - DEVIATION research/questions/0014-bunds-between-the-paddies-aze.drawing.html: every hamlet's field path runs onto the outer bund - asked here only where a brook runs (405 T127), a departure the code keeps until feature 417 T60
        the track out is no way to the field - GUESS: no source could speak to it, a value of ours (feature 417 T60); the `connector` lane, which only the track out carries (`track.stage_track` lays it), is the way off the map, not the hamlet's own way to its field
        its salts, guards and sentinels - NONE: they decide nothing about the place - 128 (spatial-index cell)
    """
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
    Research: under the crown, not the trunk - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass C, 2026-10-25); the persimmon's trunk box a wall, its crown not"""
    quads = [rot_rect(float(r["x"]), float(r["y"]), float(r["w"]), float(r["h"]), float(r.get("rot") or 0.0)) for r in M.get("farm_fixtures") or [] if all(k in r for k in ("x", "y", "w", "h"))]
    trunk = TRUNK_FT / float((M.get("meta") or {}).get("ftpx") or 1.0)
    return quads + [rot_rect(float(r["x"]), float(r["y"]), trunk, trunk, 0.0) for r in M.get("persimmons") or [] if "x" in r and "y" in r]


def over_a_fixture(pts: Sequence[Pt], width: float, quads: Sequence[Poly]) -> int | None:
    """The first segment of a lane along `pts`, drawn `width` wide, whose tread meets a farmstead fixture (`fixture_quads`) -
    crosses it, stands in it, or passes within its half-width and `FIXTURE_PAD_FT` of it; None where it meets none. THE ONE
    PREDICATE: the web's settle cuts what it names, a tree lane is refused by it, and the finished-map rule reads it.
    Research: off the fixtures - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: nothing stands on a tread"""
    gap = width / 2.0 + FIXTURE_PAD_FT
    # ...EACH FIXTURE'S BOX FIRST (feature 417 T06): a segment meets a fixture only where its box, grown by the gap, meets the
    # fixture's - the rest are passed over unasked, the same verdict (the finished web's rule asked every fixture of every
    # segment: 619,222 calls, half the settle's exit question on seed 39 at 40 households, measured 2026-10-27)
    boxes = [(min(v[0] for v in q), min(v[1] for v in q), max(v[0] for v in q), max(v[1] for v in q)) for q in quads]
    for k, (a, b) in enumerate(zip(pts, pts[1:], strict=False)):
        sx0, sx1 = (a[0], b[0]) if a[0] <= b[0] else (b[0], a[0])
        sy0, sy1 = (a[1], b[1]) if a[1] <= b[1] else (b[1], a[1])
        for q, (qx0, qy0, qx1, qy1) in zip(quads, boxes, strict=True):
            if qx0 - gap > sx1 or qx1 + gap < sx0 or qy0 - gap > sy1 or qy1 + gap < sy0:
                continue
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
        a leg long enough to break - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A2, 2026-10-25); only a leg over `BREAK_SPAN_FT` (60 ft) with its midpoint in a building counts"""
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


def short_fragments(M: Mapping[str, Any], ground: WorkedGround | None = None) -> list[int]:
    """The lanes shorter than `FRAGMENT_FT` (the connector and the field spur aside) that earn nothing: taking one away
    leaves no farmhouse newly unreached (`unreached_houses`) and the web in as many networks (`lane_networks`) - a fragment
    the passes whittled down and nothing re-asked (homes H40; the backlog's 2c's (since closed) 4 ft fragment). A short run that is some
    house's way, or the link that joins two pieces, earns its place and is not one - and so does one whose removal leaves
    ANOTHER lane's end reaching nothing (`dangling_lane_ends`): a row farm's short door path holds the end of its street
    (feature 291 on 287; dropped, Mizuguchi's street ends dangled past their last farms and the settle refused the web).
    `ground` is the worked ground where the caller has it; it is built at most once here (the perf-audit of feature 308:
    each `dangling_lane_ends` built it again, though a lane taken away changes no ground - seven builds a web on seed 47 at
    20 households, the map byte-identical with one).
    Research:
        debris - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A2, 2026-10-25); a lane under 30 ft that earns no house, join, target or end
        a household's own way never debris - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: every other farmhouse is served by a lane of its own, a household's way (`of`) or a farm's door path (`serves`)"""
    lanes = M.get("lanes") or []
    # ...NOR A HOUSEHOLD'S OWN WAY, however short (feature 318, FR-014): it is the lane its household is served by (`tree.owed`),
    # and dropped as earning nothing it was drawn again next round, until the settle refused the web (cohort seed 10)
    # ...NOR A FARM'S DOOR PATH (feature 385 T97, D125): it records `serves` where a household's way records `of`, and seed 904's
    # four row farms lost theirs as earning nothing, the farms being within the 100 ft back-lane reach - but 0246 serves a farm
    # by a lane of its own from its dooryard, not by that reach
    short = [
        i
        for i, ln in enumerate(lanes)
        if not (ln.get("connector") or ln.get("spur") or ln.get("of") or ln.get("serves")) and len(ln.get("pts") or []) >= 2 and polyline_len(lane_pts(ln)) < FRAGMENT_FT
    ]
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
