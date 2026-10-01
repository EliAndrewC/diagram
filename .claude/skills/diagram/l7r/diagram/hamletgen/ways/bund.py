"""A way that makes for the field runs on to the bund (269 B04 and B17).

research/fields/290 ("Where does the path to the fields end? On a bund, which carries it on"): the field path runs from the
hamlet to the paddy's outer bund and joins it, however short that leaves the path; it never ends in open ground short of
the bund and never passes through a gap in it; where no path is left to draw, the hamlet's nearest lane runs on to the bund.
research/homesteads/310 ("How far does a village lane run past its last farmhouse?"): a lane ends at a dooryard, or runs on
to something a reader can see - a field path, a bund, another way. That the path joins the bund at the point nearest the
hamlet is the record's GUESS.

Two passes, both after the lanes are laid: `run_lanes_on_to_the_bund` carries every lane end that has reached nothing but
the field's neighborhood on to its edge (before the trims, which pull back an end that reaches nothing - `end_serves` counts
the bund, and no longer counts "within 60 ft of the field"); `a_way_onto_the_bund` makes sure the paddy is reached at all,
running the nearest lane end on, or a short field path off the nearest lane, where nothing else reaches it.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, point_in_poly, poly_gap, seg_dist, segments_cross
from l7r.diagram.settlement.land.wet import marsh_ground
from l7r.diagram.sitegen.geom import crop_polys

from ..consts import FOOTPATH_FABRIC_GAP, LANE_CLEARANCE, WAY_END_REACH_FT, Poly, Pt
from .checks import drawn_water_segs
from .fabric import _crosses_fabric, _hits_a_steading, _homestead_polys
from .geom import _TOUCH_GAP, BUND_REACH_FT, WorkedGround, end_serves, memo_ground, steading_footprints, stroke_quad, worked_ground

# The tip stops this far outside the worked ground's edge past its own half-tread, so the tread's rounded cap lies on the
# bund line rather than on the rice (a map drawing convention; inside `BUND_REACH_FT` for every lane width drawn here).
TIP_MARGIN_FT = 1.0
# How far an end that reaches nothing may be carried on to the bund: the gate's own reach to another way, the distance at
# which the old rule counted the field as reached - so an end the old rule passed as "near the field" is carried onto it.
RUN_ON_REACH_FT = WAY_END_REACH_FT
# A run-on may turn the path this far off the way it was walking, and no further: a path bends as it is walked, and a bund
# behind the end is not one it runs on to (a map drawing convention, well inside the 90 degree hook `joints.py` removes).
RUN_ON_TURN_DEG = 60.0
# The nearest lane is sampled every this many feet when a field path must branch off it (a map drawing convention).
BRANCH_STEP_FT = 8.0
# The branch is drawn at the field spur's own tread (`stage_track`: width 5, worn).
BRANCH_WIDTH = 5


def run_on_target(q: Pt, ground: WorkedGround, half_tread: float, reach: float = RUN_ON_REACH_FT) -> Pt | None:
    """Where an end at `q` is carried to: straight toward the nearest point of the worked ground's edge, stopped the
    half-tread and `TIP_MARGIN_FT` outside it. None for an end already on the bund or inside the ground, or further than
    `reach` from it. The open segment to a set's nearest point meets nothing of the set, so the run-on cannot cross a plot."""
    if ground.inside(q):
        return None
    p = ground.nearest(q)
    if p is None:
        return None
    d = math.dist(q, p)
    stop = half_tread + TIP_MARGIN_FT
    if d <= BUND_REACH_FT or d > reach:  # the arrival bar is past every stop: an end outside it is further off than its tread
        return None
    t = (d - stop) / d
    return (q[0] + (p[0] - q[0]) * t, q[1] + (p[1] - q[1]) * t)


def pulled_out_of_the_ground(pts: Sequence[Pt], ground: WorkedGround, half_tread: float) -> list[Pt]:
    """A path whose LAST point lies inside the worked ground, cut back along itself to the first point that stands the
    half-tread and `TIP_MARGIN_FT` clear of it - on the bund, not in the crop (Sawada's spur stopped 4 ft into the rice,
    and 19 ft inside the outline, measured). A path that is in the ground end to end comes back as one point."""
    out = [(float(p[0]), float(p[1])) for p in pts]
    stop = half_tread + TIP_MARGIN_FT
    if len(out) < 2 or not ground.inside(out[-1]):
        return out
    while len(out) >= 2:
        a, b = out[-2], out[-1]
        seg = math.dist(a, b)
        k = 1.0
        while k < seg:
            c = (b[0] + (a[0] - b[0]) * k / seg, b[1] + (a[1] - b[1]) * k / seg)
            if not ground.inside(c) and ground.dist(c) >= stop:
                out[-1] = c
                return out
            k += 1.0
        out.pop()
    return out


def turns_back(prev: Pt, end: Pt, tgt: Pt) -> bool:
    """Would carrying `end` on to `tgt` turn the path more than `RUN_ON_TURN_DEG` off the way it was walking? A bund that
    lies behind the end is not one the path runs ON to, and the turn draws a hook (`lanes_end_in_no_hook`)."""
    u, v = (end[0] - prev[0], end[1] - prev[1]), (tgt[0] - end[0], tgt[1] - end[1])
    nu, nv = math.hypot(*u), math.hypot(*v)
    if nu <= 1e-9 or nv <= 1e-9:
        return False
    return math.degrees(math.acos(max(-1.0, min(1.0, (u[0] * v[0] + u[1] * v[1]) / (nu * nv))))) > RUN_ON_TURN_DEG


def tip_onto_the_bund(pts: Sequence[Pt], ground: WorkedGround, half_tread: float, blocks: RunOnBlocks | None = None) -> list[Pt]:
    """A path's LAST point set on the bund: pulled back out of the worked ground where it ends inside it, carried on to it
    where it stops short and the way is clear, straight on (`run_on_target`, `turns_back`). Otherwise as it came."""
    out = [(float(p[0]), float(p[1])) for p in pts]
    if len(out) < 2:
        return out
    if ground.inside(out[-1]):
        return pulled_out_of_the_ground(out, ground, half_tread)
    tgt = run_on_target(out[-1], ground, half_tread)
    if tgt is not None and not turns_back(out[-2], out[-1], tgt) and (blocks is None or blocks.clear(out[-1], tgt, 2.0 * half_tread)):
        out.append(tgt)
    return out


class RunOnBlocks:
    """What a run-on may not cross, read once per pass: every drawn water course (a crossing between fords needs a plank
    this pass does not lay), the marsh and the wet toe, and the steadings' built ground at a footpath's clearance."""

    def __init__(self, s: Settlement) -> None:
        self.s = s
        self.water = drawn_water_segs(s)
        toe = s.toe_band()
        self.wet: list[Poly] = marsh_ground(s.M, but=("defense",))
        if toe:
            self.wet.append(list(toe))
        self.fabric = [poly for poly, _own, kind in _homestead_polys(s) if kind not in ("commons", "village_groves")]
        # THE DRY PLOTS TOO (feature 291, found by the cohort's matrix on seed 17): a run-on aims at the PADDY
        # (`paddy_ground`, which holds no dry plot) and `run_on_target` promises only that its segment meets nothing of
        # that set - so a way carried ~150 ft to the paddy ran straight across a buckwheat plot between, and nothing here
        # looked. A way runs on the baulk between plots, never through the crop (`lanes_clear_of_dry_plots`).
        self.crops = crop_polys(s)

    def clear(self, a: Pt, b: Pt, width: float, over_water: int = 0) -> bool:
        """Is the stretch a -> b clear - crossing no more than `over_water` water courses (a crossing the crossings stage
        squares and planks), no marsh, crop or steading?"""
        if sum(1 for c, d in self.water if segments_cross(a, b, c, d)) > over_water:
            return False
        for w in self.wet:
            if point_in_poly(b[0], b[1], w) or any(segments_cross(a, b, w[k], w[(k + 1) % len(w)]) for k in range(len(w))):
                return False
        # the new stretch alone, from a step off the end it grows from (that end may stand at its own dooryard's gap)
        start = (a[0] + (b[0] - a[0]) * min(1.0, 2.0 / max(math.dist(a, b), 1e-9)), a[1] + (b[1] - a[1]) * min(1.0, 2.0 / max(math.dist(a, b), 1e-9)))
        if self.crops and any(poly_gap(stroke_quad(start, b, width / 2.0), c) <= 0.0 for c in self.crops):
            return False  # the drawn tread, as the matrix reads it, on a dry plot
        return not _crosses_fabric([start, b], self.fabric, FOOTPATH_FABRIC_GAP) and not _hits_a_steading(self.s, [start, b], int(width))


def _segs_of(lanes: Sequence[Mapping[str, Any]], skip: int) -> list[tuple[Pt, Pt]]:
    return [((float(p[0]), float(p[1])), (float(q[0]), float(q[1]))) for k, ln in enumerate(lanes) if k != skip for p, q in zip(ln.get("pts") or [], (ln.get("pts") or [])[1:], strict=False)]


def run_lanes_on_to_the_bund(s: Settlement, ground: WorkedGround, blocks: RunOnBlocks | None = None) -> int:
    """Pull every lane end that stands IN the worked ground back out onto its bund, and carry on to the bund every lane end
    that reaches nothing - no way, no farmhouse, no dooryard (`end_serves`) - but
    stands within `RUN_ON_REACH_FT` of the worked ground (269 B17: "runs on to reach something a reader can see"), where the
    trims would otherwise pull it back. The connector is left alone - it leaves the map. Returns how many ends moved; each
    lane's ink is rewritten with its record."""
    lanes = s.M.get("lanes") or []
    steadings = steading_footprints(s.M)
    houses = [(float(h["x"]), float(h["y"])) for h in s.M.get("houses") or []]
    blocks = blocks or RunOnBlocks(s)
    moved = 0
    for i, ln in enumerate(lanes):
        pts = [(float(x), float(y)) for x, y in ln.get("pts") or []]
        if (ln.get("connector") or ln.get("street")) or len(pts) < 2:
            continue
        segs = _segs_of(lanes, i)
        changed = False
        half = float(ln.get("w") or 3) / 2.0
        for _ in range(2):  # each end in turn, as the last point of the path walked toward it
            if ground.inside(pts[-1]):
                out = pulled_out_of_the_ground(pts, ground, half)
                if len(out) >= 2:
                    pts, changed = out, True
            elif not end_serves(pts[-1], segs, houses, ground, steadings):
                tgt = run_on_target(pts[-1], ground, half)
                if tgt is not None and not turns_back(pts[-2], pts[-1], tgt) and blocks.clear(pts[-1], tgt, 2.0 * half):
                    pts, changed = [*pts, tgt], True
            pts.reverse()
        if changed and s.reshape_lane(ln, pts):  # asked of the overlap matrix (feature 287 M8)
            s.reink_lane(i)
            moved += 1
    return moved


def _build_paddy_ground(M: Mapping[str, Any]) -> WorkedGround:
    rings = [[(float(a), float(b)) for a, b in (f.get("outline") or [])] for f in (M.get("fields") or [])]
    rings += [[(float(a), float(b)) for a, b in r] for f in (M.get("fields") or []) for r in (f.get("plot_rings") or []) if len(r) >= 3]
    return WorkedGround(rings)


def paddy_ground(s: Settlement) -> WorkedGround:
    """The paddy itself - the fields' outlines and their drawn rice, without the dry plots: the bund a field path joins."""
    return memo_ground(s, "paddy", _build_paddy_ground)


def a_way_onto_the_bund(s: Settlement, blocks: RunOnBlocks | None = None) -> str:
    """Make sure some way JOINS the paddy's bund (269 B04, research/fields/290). Returns how it is reached, which the stage
    records as `meta.field_path`: "joined" where a lane end already stands on it; "run_on" where the lane end nearest the
    paddy is carried on to it; "branch" where a field path is drawn off the nearest point of the lanes; "none: ..." where
    every way to it crosses water or the marsh - the reason a reader needs, stated rather than swallowed."""
    paddy = paddy_ground(s)
    if paddy.edge is None:
        return "none: no paddy"
    lanes = s.M.get("lanes") or []
    live = [(i, ln) for i, ln in enumerate(lanes) if not (ln.get("connector") or ln.get("street")) and len(ln.get("pts") or []) >= 2]
    ends = [(i, e, (float(ln["pts"][e][0]), float(ln["pts"][e][1]))) for i, ln in live for e in (0, -1)]
    blocks = blocks or RunOnBlocks(s)
    # AN END AT THE BUND WITH WATER BETWEEN HAS NOT JOINED IT (settlement-review of Mizuguchi at the 269 landing): the field
    # path stopped on the outer bank of a supply canal 3 ft short of the bund and counted as joined, with no crossing. Such an
    # end is carried over the water on to the bund, and the crossings stage bridges it like any way over a channel.
    near = [(i, e, q, paddy.nearest(q)) for i, e, q in ends if paddy.dist(q) <= BUND_REACH_FT]
    if any(p is None or not water_between(q, p, blocks.water) for _i, _e, q, p in near):
        return "joined"
    for i, e, q, p in near:
        if p is not None:
            if not carry_on(s, i, e, q, over_the_water(q, p, blocks.water)):  # ...where the overlap matrix admits it (feature 287 M8)
                continue
            return "run_on"
    for i, e, q in sorted(ends, key=lambda t: paddy.dist(t[2])):
        # ...BUT NOT AN END THAT IS A JUNCTION (feature 293; Sawada in the earlier 293 pass): an end standing on another way's
        # tread carried on past it turns the T into a crossing, a crossing is not a join at the ink tolerance, and the hamlet's
        # ways came out two networks - the rule `run_lanes_on_to_the_bund` already keeps by moving only ends that reach
        # nothing. A free end is carried on, or the field path branches off the lanes below.
        if any(seg_dist(q[0], q[1], a, b) <= _TOUCH_GAP for a, b in _segs_of(lanes, i)):
            continue
        tgt = run_on_target(q, paddy, float(lanes[i].get("w") or 3) / 2.0, reach=float("inf"))
        prev = (float(lanes[i]["pts"][-2 if e == -1 else 1][0]), float(lanes[i]["pts"][-2 if e == -1 else 1][1]))
        if tgt is not None and not turns_back(prev, q, tgt) and blocks.clear(q, tgt, float(lanes[i].get("w") or 3)):
            if not carry_on(s, i, e, q, tgt):  # ...where the overlap matrix admits the run on (feature 287 M8)
                continue
            return "run_on"
    samples: list[Pt] = []
    for _i, ln in live:
        pts = [(float(x), float(y)) for x, y in ln["pts"]]
        for a, b in zip(pts, pts[1:], strict=False):
            n = max(1, int(math.dist(a, b) // BRANCH_STEP_FT))
            samples.extend((a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n))
    # ...AND WHERE THE WATER LIES BETWEEN, ACROSS IT ONCE: a row on the brook's far bank from its fields reaches them over a
    # plank, which the crossings stage squares and lays (Mizuguchi, settlement-review 2026-09-30: once its brook came on from
    # off the sheet no way reached the paddy, and the fallback refused every way across the water)
    for over in (0, 1):
        for q in sorted(samples, key=paddy.dist):
            tgt = run_on_target(q, paddy, BRANCH_WIDTH / 2.0, reach=float("inf"))
            if tgt is not None and blocks.clear(q, tgt, BRANCH_WIDTH, over_water=over) and s.admits_lane([q, tgt], BRANCH_WIDTH):  # ...and the matrix (M8)
                s.lane([q, tgt], width=BRANCH_WIDTH, clearance=LANE_CLEARANCE, worn=True, spur=True)
                return "branch"
    return "none: every straight way from the lanes to the paddy crosses water, the marsh or a steading"


SQUARE_APPROACH_FT = 12.0
"""How far before the water a step bends onto its square crossing (a map drawing convention: a few paces)."""


def squared_step(q: Pt, to: Pt, water: Sequence[tuple[Pt, Pt]], tol_deg: float = 10.0) -> list[Pt]:
    """The step from `q` to `to` (without `q`): straight where it crosses no water or crosses it within `tol_deg` of square;
    else bent onto a square crossing - to a point `SQUARE_APPROACH_FT` before the water on its normal, then across to the
    water's far side as far out as `to` stood (Kashikawa, settlement-review 2026-09-30: a field path's short step crossed
    the brook 45 degrees off square, too near its end for the crossings stage to square it)."""
    from l7r.diagram.settlement import seg_intersect

    hit = next(((c, d) for c, d in water if segments_cross(q, to, c, d)), None)
    if hit is None:
        return [to]
    c, d = hit
    x = seg_intersect(q, to, c, d) or to
    ln = math.dist(c, d) or 1.0
    nx, ny = -(d[1] - c[1]) / ln, (d[0] - c[0]) / ln
    if (to[0] - x[0]) * nx + (to[1] - x[1]) * ny < 0:
        nx, ny = -nx, -ny
    sx, sy = (to[0] - q[0]), (to[1] - q[1])
    sl = math.hypot(sx, sy) or 1.0
    if math.degrees(math.acos(min(1.0, abs(sx * nx + sy * ny) / sl))) <= tol_deg:
        return [to]
    beyond = max(3.5, (to[0] - x[0]) * nx + (to[1] - x[1]) * ny)
    return [(x[0] - nx * SQUARE_APPROACH_FT, x[1] - ny * SQUARE_APPROACH_FT), (x[0] + nx * beyond, x[1] + ny * beyond)]


def carry_on(s: Settlement, i: int, e: int, q: Pt, to: Pt) -> bool:
    """Carry lane `i`'s end `e` (at `q`) on to `to`: the lane is lengthened - unless that end is a JUNCTION, on another
    lane's tread, when the step is drawn as a field path of its own from `q` (feature 291: Mizuguchi's door path met its
    street there, was carried on over it to the bund, and the junction became a crossing - the web in two pieces at the
    4 ft its one-network rule joins at). Either way the overlap matrix is asked first (feature 287 M8): False, and
    nothing is drawn, where it refuses."""
    lanes = s.M.get("lanes") or []
    step = squared_step(q, to, drawn_water_segs(s))
    if any(seg_dist(q[0], q[1], a, b) <= _TOUCH_GAP for a, b in _segs_of(lanes, i)):
        if not s.admits_lane([q, *step], BRANCH_WIDTH):
            return False
        s.lane([q, *step], width=BRANCH_WIDTH, clearance=LANE_CLEARANCE, worn=True, spur=True)
        return True
    pts = [(float(x), float(y)) for x, y in lanes[i]["pts"]]
    pts = [*pts, *step] if e == -1 else [*step[::-1], *pts]
    if not s.reshape_lane(lanes[i], pts):
        return False
    s.reink_lane(i)
    return True


# ft past the centerline of the water crossed that a carried end stops, on the bund: a supply canal is ~4.5 ft wide and its
# outer bund stands 3-4 ft past the centerline (measured on Mizuguchi by the landing's round-3 review). A map drawing convention.
OVER_THE_WATER_FT = 3.5


def over_the_water(q: Pt, p: Pt, water: Sequence[tuple[Pt, Pt]]) -> Pt:
    """Where an end at `q` carried over the water toward the bund point `p` stops: straight across the first water course
    the step crosses, square to it, and `OVER_THE_WATER_FT` past its centerline, so the path ends ON the bund rather than
    on the canal's centerline where the paddy's outline runs (the round-3 review of Mizuguchi). The carried deck's
    paddy-side landing still runs onto the field - the gate's carried-way landing floor holds it; open in future-work.
    `p` itself where the step crosses nothing."""
    from l7r.diagram.settlement import seg_closest

    seg = next(((c, d) for c, d in water if segments_cross(q, p, c, d)), None)
    if seg is None:
        return p
    cx, cy = seg_closest(q[0], q[1], seg[0], seg[1])
    dx, dy = cx - q[0], cy - q[1]
    n = max(math.hypot(dx, dy), 1e-9)  # never zero: a step starting ON the water line does not strictly cross it
    return (cx + dx / n * OVER_THE_WATER_FT, cy + dy / n * OVER_THE_WATER_FT)


def water_between(q: Pt, p: Pt, water: Sequence[tuple[Pt, Pt]]) -> bool:
    """Does the straight step from a lane end `q` to the bund point `p` cross a drawn water course?"""
    return any(segments_cross(q, p, c, d) for c, d in water)


def worked_ground_of(s: Settlement, fallback: Poly) -> WorkedGround:
    """The worked ground of the map as it stands (`worked_ground`), or `fallback` (the plan's envelope) where the manifest
    records no field."""
    return memo_ground(s, "worked", worked_ground) if s.M.get("fields") or s.M.get("dry_plots") else WorkedGround([list(fallback)])


_PAST_JUNCTION_FT = 40.0  # ft: a free end's run past the junction it met, this short, is a stub (a map drawing convention)


def cut_past_the_junction(s: Settlement, touch: float = 4.0) -> int:
    """Cut a lane's FREE end back to the junction it met, where the run past the junction is short and serves nothing: no
    house within `HOUSE_SERVE_FT` of the end, and not on the worked ground's bund. Returns the lanes cut.

    FOUND AT THE 269 LANDING (settlement-review of Mizuguchi, rounds 1 and 2): the field spur began on the brook bank and
    ran 28 ft to the junction where another lane met it, then turned over the bridge - a stub reaching nothing, which the
    end rule counted as served because it stood within reach of the very lane it had just met, and which
    `trim_free_stub` misses because its corner is a single turn, not a kink (research/homesteads 310: a lane ends at the
    last house it serves)."""
    lanes = s.M.get("lanes") or []
    houses = [(float(h["x"]), float(h["y"])) for h in s.M.get("houses") or []]
    ground = worked_ground_of(s, []) if s.M.get("fields") or s.M.get("dry_plots") else WorkedGround([])
    cuts = 0
    for i, ln in enumerate(lanes):
        p = [(float(x), float(y)) for x, y in ln.get("pts") or []]
        if (ln.get("connector") or ln.get("street")) or len(p) < 3:
            continue
        others = _segs_of(lanes, i)
        q = cut_stub_ends(p, others, houses, ground, touch)
        if q != p:
            ln["pts"] = [[round(x, 1), round(y, 1)] for x, y in q]
            s.reink_lane(i)
            cuts += 1
    return cuts


def cut_stub_ends(p: list[Pt], others: Sequence[tuple[Pt, Pt]], houses: Sequence[Pt], ground: WorkedGround, touch: float = 4.0) -> list[Pt]:
    """`p` with each free end's short run past its first junction cut off (see `cut_past_the_junction`); plain inputs."""
    from l7r.diagram.settlement import seg_dist
    from l7r.diagram.settlement.water_ways._helpers import HOUSE_SERVE_FT

    def on_a_way(q: Pt) -> bool:
        return any(seg_dist(q[0], q[1], a, b) <= touch for a, b in others)

    out = list(p)
    for _end in range(2):
        k = next((k for k in range(1, len(out) - 1) if on_a_way(out[k])), None)
        end = out[0]
        if (
            k is not None
            and not on_a_way(end)
            and sum(math.dist(out[j], out[j + 1]) for j in range(k)) <= _PAST_JUNCTION_FT
            and all(math.dist(end, h) > HOUSE_SERVE_FT for h in houses)
            and ground.dist(end) > BUND_REACH_FT
        ):
            out = out[k:]
        out.reverse()
    return out
