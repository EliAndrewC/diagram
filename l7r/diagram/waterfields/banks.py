"""A tapered channel cut a piece a segment (`taper_pieces`), and the bank clearances and swept bends the drawing reads.

Research: bank geometry - NONE: arc lengths, nearest segments, the stroke index, rounding slack
"""

import math
from typing import Any

from .frame import BANK_MARGIN, Poly, Pt, _seg_d, _seg_x, taper_w

_PAST_EPS = 0.25  # arc slack at a supply stroke's ends: covers the 0.1-px manifest rounding of vertex + stroke point together (see supply_bank_clearance)


def polyline_cum(pts: Poly) -> list[float]:
    """Cumulative arc length at each vertex - hoisted so a caller testing many points against one
    collector pays for it once."""
    cum = [0.0]
    for i in range(len(pts) - 1):
        cum.append(cum[-1] + math.dist(pts[i], pts[i + 1]))
    return cum


def taper_pieces(pts: Poly, w0: float, w1: float) -> list[tuple[Poly, float]]:
    """A tapering stroke split into drawable pieces, each carrying its ARC-CORRECT local width.

    PARAMETERIZED BY ARC LENGTH, NEVER BY VERTEX INDEX - which is the bug this replaced
    (settlement-review 2026-08-17). `field_channel` used to cut the polyline into 7 equal slices of
    the INDEX range and give slice k the width at `(k + 0.5) / 7`, which is only the width at that
    point of the run if the vertices are evenly spaced along it. The carve's are not: measured on
    Inashiro, one delivery ditch's seven slices covered 7.0 / 9.2 / 3.2 / 4.2 / 15.9 / 27.5 / 33.0%
    of its length, so the drawn width missed the law by up to 1.94 px (24-44% of the local width),
    the last third of the ditch was drawn at a FLAT minimum - the very "reaches the minimum and just
    stops" reading the taper work set out to fix - and a 2-point stub had six empty slices and was
    drawn end to end at its TAIL width, 3.6 px where its own record declared a 7.2 px head.

    Per SEGMENT rather than in buckets, for two reasons beyond correctness: a bucket boundary is a
    visible step (1.84 px in one place on the collector), and `banks.py`, `seams.py` and `carve.py`
    already take their local width at the arc fraction - so drawing per segment makes the INK agree
    with the bank geometry the bunds are laid against and the gate re-measures, rather than merely
    coming close to it.

    ONE definition, shared by the renderer (`field_channel`) and the keep-out corridor
    (`_watercourse_segs`), which used to build this ladder separately and identically - two copies
    of one ladder is how the drawn stroke and the corridor that protects it drift apart.

    KNOWN BOUND, measured rather than assumed (settlement-review 2026-08-17). The ink is piecewise
    constant per segment, while the two bank clearances below and `close_seams`' buffer evaluate the
    CONTINUOUS law at the query point - so the drawn edge and the geometry the bunds are laid
    against differ by up to half the step between neighboring pieces. On Inashiro that is 0.11-0.14
    px on most strokes, 0.21-0.23 on the two coarse-tailed deliveries, 0.52 on the collector, and
    **1.19 px on the 2-point stub**, where one piece has to stand for a run whose law goes 7.2 ->
    3.2; the stub's nearest plot ring ends up +0.25 px clear of the drawn edge against a designed
    `BANK_MARGIN` of 0.75. Nothing crosses on any shipped map, so this is a shrunken abutment, not a
    bund in the water. IF IT IS EVER WORTH CLOSING: have `drain_bank_clearance` /
    `supply_bank_clearance` / the `half` closure in `seams.py` take `t` at the arc midpoint of the
    segment they already identify as nearest, instead of at the query point's own arc fraction -
    they each compute that segment's index and `arc` already, so it is a few lines each. It re-rolls
    every scripted map, so it wants its own pass with a `settlement-review` per map. The alternative
    fix - densifying the polylines before stroking - would also close the collector's residual 1.64
    px step notch at (1521.7, 1540.7), which the per-segment split did not remove because that
    stroke has only 10 vertices over 1240 px.

    Research: drawn taper - research/questions/0069-how-our-maps-draw-a-channel-narrowing-along-its-run.drawing.html: each segment inked at the taper law's width at its arc midpoint
    """
    if len(pts) < 2:
        return []
    cum = polyline_cum(pts)
    tot = cum[-1] or 1.0
    return [([pts[i], pts[i + 1]], taper_w(w0, w1, (cum[i] + cum[i + 1]) / 2 / tot)) for i in range(len(pts) - 1)]


def drain_bank_clearance(q: Pt, dpts: Poly, dv: Pt, w0: float, w1: float, cum: list[float]) -> tuple[float, float, float, bool]:
    """How one point stands against a drainage collector: `(gap, need, lean, past)`.

    - `gap` - SIGNED perpendicular offset from the nearest segment, positive on the FIELD's side of
      the ditch (the side the fall comes from), negative once the point is across the centerline.
    - `need` - the bank: half the collector's DRAWN width at that point (it tapers `w0` -> `w1`
      along its length) plus `BANK_MARGIN`, so a bund's own stroke abuts the ditch's rather than
      overlapping it.
    - `lean` - how much clearance one unit of UP-FALL travel buys. It is ~0 for a collector running
      with the fall, where "lift it up-fall" is not a move that helps.
    - `past` - the point projects beyond the collector's head or tail. That ground drains somewhere
      else (the next fan, the map edge), so this collector does not govern it.

    ONE predicate, shared by the generator (`hem_to_bank`) and by the gate
    (`paddy_bunds_clear_the_collector`), because a placer and a checker that classify the same
    ground from two separate formulas drift apart - the trap the diagram CLAUDE.md records under
    'Placement and its check must read the SAME manifest source'.

    Research: bank of the collector - research/questions/0055-where-a-field-meets-its-ditch-the-bank-the-bund-and-the-inlet-mizuguchi.drawing.html: half the drain's drawn width there plus half a bund
        its salts, guards and sentinels - NONE: they decide nothing about the place - 1e+09 (sentinel starting distance)
    """
    off, cx, cy, arc, past, nrm = 1e9, 0.0, 0.0, 0.0, False, (0.0, 0.0)
    for i in range(len(dpts) - 1):
        ax, ay = dpts[i]
        vx, vy = dpts[i + 1][0] - ax, dpts[i + 1][1] - ay
        t = ((q[0] - ax) * vx + (q[1] - ay) * vy) / ((vx * vx + vy * vy) or 1.0)
        tc = max(0.0, min(1.0, t))
        sx, sy = ax + tc * vx, ay + tc * vy
        d = math.hypot(q[0] - sx, q[1] - sy)
        if d < off:
            off, cx, cy = d, sx, sy
            arc = cum[i] + tc * math.hypot(vx, vy)
            past = (i == 0 and t < 0.0) or (i == len(dpts) - 2 and t > 1.0)
            nl = math.hypot(vx, vy) or 1.0
            nx, ny = -vy / nl, vx / nl
            nrm = (nx, ny) if nx * dv[0] + ny * dv[1] < 0 else (-nx, -ny)  # points UP-fall, off the ditch
    gap = (q[0] - cx) * nrm[0] + (q[1] - cy) * nrm[1]
    need = taper_w(w0, w1, arc / (cum[-1] or 1.0)) / 2 + BANK_MARGIN
    return gap, need, -(dv[0] * nrm[0] + dv[1] * nrm[1]), past


def supply_bank_clearance(q: Pt, pts: Poly, w0: float, w1: float, cum: list[float]) -> tuple[float, float, bool, Pt, Pt]:
    """How one point stands against a SUPPLY channel's drawn stroke: `(gap, halfw, past, foot, nrm)`.

    The supply half of `drain_bank_clearance`, and simpler for a reason: a drain-side bund is held
    off IN FALL (the hem climbs up its own column, so that verdict needs the fall geometry), while
    a supply-side bund runs ALONGSIDE its channel and is held off PERPENDICULAR - the bund is the
    channel's bank wherever the channel goes, which is also what makes the bordering bund run
    parallel to the water (GM 2026-08-15).

    - `gap` - unsigned perpendicular distance from `q` to the nearest stroke segment.
    - `halfw` - half the stroke's DRAWN width at that point (`w0` -> `w1` taper along its arc).
    - `past` - `q` projects beyond the stroke's head or tail; ground beyond the span is not
      governed by this stroke (a delivery ditch's takeoff sits on its parent canal, which governs).
    - `foot` - the nearest point on the centerline.
    - `nrm` - the nearest segment's unit normal, side arbitrary; the caller orients it.

    ONE predicate, shared by the placer (`_carve`'s `clear_supply`) and by the gate
    (`paddy_bunds_clear_the_supply_channels`), for the same reason `drain_bank_clearance` is: a
    placer and a checker that classify the same ground from two formulas drift into disagreeing
    about which side of a ditch a point is on.

    Research: bund runs along the supply channel - research/questions/0055-where-a-field-meets-its-ditch-the-bank-the-bund-and-the-inlet-mizuguchi.drawing.html: held off perpendicular by the stroke's local half-width
    """
    return _stroke_verdict(q, pts, w0, w1, cum, _nearest_segment(q, pts, cum, range(len(pts) - 1)))


def _nearest_segment(q: Pt, pts: Poly, cum: list[float], which: Any) -> tuple[float, Pt, float, bool, Pt]:
    """The nearest of the segments `which` names (indices into `pts`, in order - ties go to the first,
    as the full walk always resolved them): `(gap, foot, arc, past, nrm)`. ONE body for the full walk
    and the indexed walk (`StrokeIndex`), so the two cannot drift.

    Research:
        its salts, guards and sentinels - NONE: they decide nothing about the place - 1e+09 (sentinel)
    """
    off, foot, arc, past, nrm = 1e9, (0.0, 0.0), 0.0, False, (0.0, 1.0)
    last = len(pts) - 2
    for i in which:
        ax, ay = pts[i]
        vx, vy = pts[i + 1][0] - ax, pts[i + 1][1] - ay
        t = ((q[0] - ax) * vx + (q[1] - ay) * vy) / ((vx * vx + vy * vy) or 1.0)
        tc = max(0.0, min(1.0, t))
        sx, sy = ax + tc * vx, ay + tc * vy
        d = math.hypot(q[0] - sx, q[1] - sy)
        if d < off:
            off, foot = d, (sx, sy)
            arc = cum[i] + tc * math.hypot(vx, vy)
            past = (i == 0 and t < 0.0) or (i == last and t > 1.0)
            nl = math.hypot(vx, vy) or 1.0
            nrm = (-vy / nl, vx / nl)
    return off, foot, arc, past, nrm


def _stroke_verdict(q: Pt, pts: Poly, w0: float, w1: float, cum: list[float], nearest: tuple[float, Pt, float, bool, Pt]) -> tuple[float, float, bool, Pt, Pt]:
    """`supply_bank_clearance`'s answer from the nearest segment: the drawn half-width at that arc, and
    the `past` reading with its manifest-rounding slack."""
    off, foot, arc, past, nrm = nearest
    halfw = taper_w(w0, w1, arc / (cum[-1] or 1.0)) / 2
    # `past` IS ROBUST AT THE MANIFEST ROUNDING SCALE (the seed-25 hairline, 2026-08-16): the
    # placer works in unrounded floats and exempted a carved corner projecting epsilon PAST the
    # branch tail; the manifest rounds both the corner and the stroke poly to 0.1 px, which
    # collapsed them onto the same coordinates - the gate then computed t = 1.0 exactly, `past`
    # came back False, and the check fired at gap 0 on a corner the placer had legally exempted.
    # One predicate, two verdicts, split by the round-trip. So ground within _PAST_EPS of either
    # end of the stroke's arc counts as past on BOTH sides of the rounding (same class as the
    # gate's 0.15 gap slack).
    past = past or arc <= _PAST_EPS or arc >= (cum[-1] or 1.0) - _PAST_EPS
    return off, halfw, past, foot, nrm


class StrokeIndex:
    """`supply_bank_clearance` for ONE stroke, answered from a grid of its segments (feature 220,
    constitution X clause 15). The carve asked it 86,000 times per roll and every call walked every
    segment of the stroke - the three callers (`_clear_supply` per carved corner, `_quad_in_supply`
    per 3 px step along every plot edge near a stroke, the hem's `_bank`) all want the nearest
    segment, and all decide on whether the gap is under a reach of a few px (half-width + margin).

    EXACT, by this argument: if any segment lies within `reach` of the point, the true nearest lies
    within `reach` too, so it is among the segments whose box the cells within `reach` hold, and the
    walk over those - in index order, so a tie resolves as the full walk resolved it - returns the
    same tuple. If the nearest of those is itself beyond `reach`, the true nearest may be a segment
    the cells did not hold, and the full walk runs instead: the callers only ever act on a gap under
    the reach, so that fallback is rare (a point inside the stroke's box but far from its line) and
    costs what every call used to cost. `test_strokes.py` proves tuple equality on random points."""

    __slots__ = ("cell", "cells", "cum", "pts", "reach", "w0", "w1")

    def __init__(self, pts: Poly, w0: float, w1: float, cum: list[float], reach: float, cell: float = 64.0) -> None:
        """Research:
        its salts, guards and sentinels - NONE: they decide nothing about the place - 64 (spatial-index cell)
        """
        self.pts, self.w0, self.w1, self.cum, self.reach, self.cell = pts, w0, w1, cum, reach, cell
        self.cells: dict[tuple[int, int], list[int]] = {}
        for i in range(len(pts) - 1):
            (ax, ay), (bx, by) = pts[i], pts[i + 1]
            for cx in range(int(min(ax, bx) // cell), int(max(ax, bx) // cell) + 1):
                for cy in range(int(min(ay, by) // cell), int(max(ay, by) // cell) + 1):
                    self.cells.setdefault((cx, cy), []).append(i)

    BEYOND: tuple[float, float, bool, Pt, Pt] = (1e9, 0.0, False, (0.0, 0.0), (0.0, 1.0))  # "no segment within reach", for a caller that decides only under the reach

    def clearance(self, q: Pt, exact: bool = True) -> tuple[float, float, bool, Pt, Pt]:
        """`supply_bank_clearance(q, pts, w0, w1, cum)`, to the bit - or, with `exact=False`, `BEYOND` when
        no segment lies within the reach. A caller that acts only on `gap < need` with `need <= reach`
        (`_clear_supply`, `_quad_in_supply`) reads the same verdict from `BEYOND` as from the true far
        gap, and skips the full walk that a point inside the stroke's box but off its line used to cost -
        a third of all calls on the reference fan, and the reason the first cut of this index bought
        nothing (specs/220 research R3). The hem's `_bank` reads the nearest half-width wherever the
        point stands, so it keeps `exact=True`."""
        c, r = self.cell, self.reach
        near: set[int] = set()
        for cx in range(int((q[0] - r) // c), int((q[0] + r) // c) + 1):
            for cy in range(int((q[1] - r) // c), int((q[1] + r) // c) + 1):
                hit = self.cells.get((cx, cy))
                if hit:
                    near.update(hit)
        nearest = _nearest_segment(q, self.pts, self.cum, sorted(near)) if near else None
        if nearest is None or nearest[0] > r:
            if not exact:
                return self.BEYOND
            nearest = _nearest_segment(q, self.pts, self.cum, range(len(self.pts) - 1))  # beyond the reach: the full walk, as before
        return _stroke_verdict(q, self.pts, self.w0, self.w1, self.cum, nearest)

    def edge_beyond(self, a: Pt, b: Pt, slack: float) -> bool:
        """Does every segment of the stroke lie farther from the edge a-b than its own drawn half-width plus `slack`, with
        a hair past rounding? Where it does, no point of the edge has a gap under `halfw + slack` (`_edge_in_supply`'s
        test) - a point's gap is its distance to its nearest segment, never under that segment's distance to the edge, and
        the half-width at its foot is at most the larger of the two at that segment's ends (`taper_w` runs one way along
        the stroke) - so the edge's walk sample by sample can be skipped (feature 287 perf). `slack` must keep the test
        under the index's reach, where every segment it could concern is filed in a cell the edge's box so grown meets."""
        c, r = self.cell, self.reach
        near: set[int] = set()
        for cx in range(int((min(a[0], b[0]) - r) // c), int((max(a[0], b[0]) + r) // c) + 1):
            for cy in range(int((min(a[1], b[1]) - r) // c), int((max(a[1], b[1]) + r) // c) + 1):
                hit = self.cells.get((cx, cy))
                if hit:
                    near.update(hit)
        tot = self.cum[-1] or 1.0
        for i in near:
            p, q = self.pts[i], self.pts[i + 1]
            thr = max(taper_w(self.w0, self.w1, self.cum[i] / tot), taper_w(self.w0, self.w1, self.cum[i + 1] / tot)) / 2 + slack + _EDGE_EPS
            if _seg_x(a, b, p, q) is not None or min(_seg_d(a[0], a[1], p, q), _seg_d(b[0], b[1], p, q), _seg_d(p[0], p[1], a, b), _seg_d(q[0], q[1], a, b)) <= thr:
                return False
        return True


_EDGE_EPS = 1e-6  # px: past any rounding between an edge's distance to a segment and its samples' gaps (`edge_beyond`)


def hem_to_bank(ring: Poly, dpts: Poly, down_deg: float, w0: float, w1: float) -> Poly:
    """Lift any vertex of `ring` that lies inside the collector's drawn stroke - or past its
    centerline - up-fall (at right angles, beside a drain running with the fall) onto the ditch's BANK. Returns a new ring; vertices already clear are
    returned untouched.

    The comb builder needs none of this: it hems onto the bank BY CONSTRUCTION (see `_drain_bank`). The
    other three field engines lay their parcels against a drain they build afterwards, so they have
    no such handle, and the check that caught the comb's defect caught the same class in all three
    (2026-08-08). Each was a different flavor of the one error:

      - TERRACES: the last terrace's toe is a WIGGLY contour (amp + phase) while the collector along
        the foot is a STRAIGHT descending line, so the two cross. Tanada's toe bund - the thick
        retaining lip, drawn separately from the plots - ran ~8 px below the ditch, which is the
        defect at its most visible: a retaining wall standing in the drain.
      - RIBBON: the bands end exactly AT the foot, i.e. on the drain's centerline (measured offset
        0.00 px on every flagged vertex), so the field's bottom bund is drawn under the ditch.
      - POLDER: the collector IS the polder's bottom side, so the parcels front it directly and
        float error alone put a vertex a half-pixel past.

    This is a terminal pass rather than a construction change in three engines, and that is a
    deliberate trade: it enforces one physical invariant (a basin's wall cannot stand in the ditch)
    on geometry those engines have finished with, in the same spirit as the comb's own terminal
    thin-plot drop. The move is along the FALL, so a lifted vertex slides up its own column and the
    parcel keeps its shape - except against a collector running WITH the fall (lean under 0.2), where up-fall buys nothing and
    the vertex steps off at right angles instead (`off_with_the_fall`).

    Research:
        no wall in the ditch - research/questions/0055-where-a-field-meets-its-ditch-the-bank-the-bund-and-the-inlet-mizuguchi.drawing.html: a vertex inside the collector's bank lifted up the fall onto it
        drain with the fall - research/questions/0055-where-a-field-meets-its-ditch-the-bank-the-bund-and-the-inlet-mizuguchi.drawing.html: a vertex in a collector running within ~12 deg of the fall (lean under 0.2) stepped off at right angles onto its own side's bank, never left in the water
    """
    dv = (math.cos(math.radians(down_deg)), math.sin(math.radians(down_deg)))
    cum = polyline_cum(dpts)
    out: Poly = []
    for q in ring:  # one ring: the scalar walk (a plot's few corners cost less than an array's fixed cost); many rings at once:
        # `hem_rings_to_bank` (feature 297)
        gap, need, lean, past = drain_bank_clearance(q, dpts, dv, w0, w1, cum)
        if past or gap >= need:  # clear, or off the collector's span
            out.append(q)
            continue
        if lean < 0.2:  # a drain running WITH the fall: up-fall buys nothing, so the vertex steps off at right angles - where it
            # is inside the bank on EITHER side (the up-fall side `gap` is signed toward does not exist for such a drain)
            out.append(off_with_the_fall(q, dpts, gap, need) if abs(gap) < need else q)
            continue
        shift = (need - gap) / lean
        out.append((round(q[0] - dv[0] * shift, 1), round(q[1] - dv[1] * shift, 1)))
    return out


def off_with_the_fall(q: Pt, dpts: Poly, gap: float, need: float) -> Pt:
    """`q`, inside the bank of a collector running with the fall, moved out at right angles to its nearest segment until it
    stands `need` off the centerline, on the side it already lies (`gap`'s sign; the segment's left where it lies on it).

    Research: off at right angles - research/questions/0055-where-a-field-meets-its-ditch-the-bank-the-bund-and-the-inlet-mizuguchi.drawing.html: a bund abuts the ditch and never stands in its water
        its salts, guards and sentinels - NONE: they decide nothing about the place - 1e+09 (sentinel)
    """
    best, foot, nrm = 1e9, (0.0, 0.0), (0.0, 1.0)
    for i in range(len(dpts) - 1):
        ax, ay = dpts[i]
        vx, vy = dpts[i + 1][0] - ax, dpts[i + 1][1] - ay
        t = max(0.0, min(1.0, ((q[0] - ax) * vx + (q[1] - ay) * vy) / ((vx * vx + vy * vy) or 1.0)))
        sx, sy = ax + t * vx, ay + t * vy
        d = math.hypot(q[0] - sx, q[1] - sy)
        if d < best:
            nl = math.hypot(vx, vy) or 1.0
            best, foot, nrm = d, (sx, sy), (-vy / nl, vx / nl)
    side = 1.0 if (q[0] - foot[0]) * nrm[0] + (q[1] - foot[1]) * nrm[1] >= 0 else -1.0
    step = need - abs(gap)
    return (round(q[0] + side * nrm[0] * step, 1), round(q[1] + side * nrm[1] * step, 1))


def swept_bend(P: Pt, u0: Pt, u1: Pt, interior: float, radius: float, run: float, steps: int) -> list[Pt]:
    """The arc that rounds a corner at `P` between the unit directions `u0` (back along the upstream run) and `u1` (on along the
    downstream run), meeting at `interior` radians: a CIRCULAR arc tangent to both runs, its radius `radius` capped at 35% of
    the shorter run `run` (0054), its cut-back from the corner radius x tan(turn / 2) for the turn the water makes (pi less the
    interior angle). A sharp turn's cut-back is also kept within 90% of the run - the arc must leave the run something to
    start from - by tightening the radius further. `steps + 1` points from the upstream tangent point to the downstream.

    Research:
        swept bends - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: a bend of about 2.5 channel widths' radius, the radius capped at 35% of the straight run on either side
        cut-back within its run - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P2b, 2026-10-25); a hairpin (a turn over ~137 deg) drawn tighter than the 2.5-width radius so its tangent point stays within 90% of its run; the 90% is this project's margin
        its figures from 0054 - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: 0.35 (bend radius capped at 35% of the run ("capped at 35% of the straight run"))
        its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N6, 2026-10-25) - 0.9 (a hairpin's tangent point kept within 90% of its run)
    """
    half = (math.pi - interior) / 2
    r = min(radius, 0.35 * run, 0.9 * run / math.tan(half))
    d = r * math.tan(half)
    a = (P[0] + u0[0] * d, P[1] + u0[1] * d)
    b = (P[0] + u1[0] * d, P[1] + u1[1] * d)
    bx, by = u0[0] + u1[0], u0[1] + u1[1]
    bl = math.hypot(bx, by) or 1.0
    reach = r / math.sin(interior / 2)
    c = (P[0] + bx / bl * reach, P[1] + by / bl * reach)
    t0, t1 = math.atan2(a[1] - c[1], a[0] - c[0]), math.atan2(b[1] - c[1], b[0] - c[0])
    sweep = (t1 - t0 + math.pi) % (2 * math.pi) - math.pi  # the short way round, the side the corner turns
    return [(round(c[0] + r * math.cos(t0 + sweep * s / steps), 1), round(c[1] + r * math.sin(t0 + sweep * s / steps), 1)) for s in range(steps + 1)]
