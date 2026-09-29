"""Every rule a finished paddy ring must keep, as ONE predicate per rule (feature 287, M1 / FR-003).

WHY ONE MODULE. A rule used to live twice: once as the placer's own guard, at a margin stricter than the
gate's, and once as a test that re-measured the finished map. The two drifted - the needle test read the raw
ring while the tint guard read the deduped one, the supply test walked edges at 3 px while the carve tested
quads - so a map could pass the placer and fail the test, and nothing but a re-roll reconciled them. Here each
rule is written once, at the GATE's own threshold: the finished-map test calls it, and a placer that writes a
ring (the seam pass, water design W16-W28) refuses any candidate for which `ring_violations` is non-empty.

EACH BODY IS THE TEST BODY IT REPLACES, thresholds and all (`tests/gate/test_paddy_fabric.py`,
`tests/gate/test_bunds_and_dikes.py`, `tests/gate/test_water_junctions.py`). The rules no finished-map test asserts
yet - the arrowhead (W25) and the grave island (W28) - are written from the water design's mechanism.

TWO RULES ARE WRITTEN DOWN AND NOT ENFORCED: the working width (W26) and the dart (W27). Their research pass (feature
287, T13, 2026-09-29) read `research/fields/` and found the record CONTRADICTS both rather than being silent - see
`BASIN_MIN_WIDTH_FT` and `DART_MIN_APEX` for the passages. A rule the research contradicts is recorded, not enforced
(the lead's ruling for T13), so `ring_violations` does not ask `narrow` or `dart`; each stays a named predicate here,
tested, so the measurement is one call away if the GM rules otherwise.

Rings are judged AS RECORDED: the manifest rounds to 0.1 px, and a caller that judges a candidate ring rounds it
the same way first, so the placer and the manifest see one ring.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from l7r.diagram.settlement._geom.primitives import ring_meets_ellipse

from .banks import (
    _GATE_CHEVRON_APEX,
    _GATE_CHEVRON_SOLIDITY,
    _GATE_MIN_APEX,
    _GATE_MIN_AREA,
    StrokeIndex,
    dedup_ring,
    is_chevron,
    jog_vertices,
    pointed_ring,
    polyline_cum,
)
from .frame import BANK_MARGIN, Poly, Pt, _pip, _poly_area

NEEDLE_DEG = _GATE_MIN_APEX
"""The needle line, 15 deg. The carve demotes a ring tapering below 25 deg; the rule fires at 15, so a borderline
plot the carve deliberately allowed cannot be read as a failure (see `_GATE_MIN_APEX` in banks.py)."""

AREA_FLOOR = _GATE_MIN_AREA
"""The smallest basin, 0.20 of the fan's OWN design cell - a ratio, never an absolute floor (see `_GATE_MIN_AREA`)."""

OVERCOUNT_CEILING = 0.04
"""`plot_rings` is a paint-order STACK, not a partition - a later basin paints out the stretch of bund it laps,
which is what makes the pair read as the single shared wall a real fan has. So the ring areas double-count the
lapped ground, and this is a CEILING on that over-count rather than a ban on the lap. Measured over the four
scripted hamlets and a 48-seed cohort in 2026-08-17: 0.53-1.06% on the pool, cohort median ~0.9%, tail to 2.49%.
4% is ~1.6x the worst live map and fires on a doubling of it."""

MAX_STEPS = 1
"""A STAIRCASE is more than one sideways step on a ring; a single step is one awkward corner where a scrap had
exactly one home (see `test_a_bund_does_not_build_a_flight_of_steps` for the GM's report and the measurement)."""

STROKE_SAMPLE_PX = 3.0
"""Each ring edge is walked at 3 px against a supply stroke: a junction wedge can keep every CORNER dry while its
two long edges converge THROUGH the canal (settlement-review, Sawada 2026-08-15)."""

STROKE_ROUNDING_PX = 0.15
"""The manifest's rounding slack on the supply bar (halfw + BANK_MARGIN - 0.15): vertex and stroke point are each
rounded to 0.1 px, so a bund that abuts exactly cannot be read as inside the water."""

COLLECTOR_REACH = 0.5
"""An edge runs ACROSS the collector when both its ends lie within half the stroke's half-width of the centerline
and the edge is longer than the stroke is wide - it starts one side of the drain and ends the other."""

BASIN_MIN_WIDTH_FT = 12.0
"""NOT ENFORCED - the research contradicts the rule (water W26; decision class: deliberate deviation from the design row,
recorded here, in `ring_violations` and in the feature's report). The number is still a GUESS: the settlement-review on
Kashikawa (future-work 'the paddy area floor cannot see WIDTH') put a line 'somewhere in the 12-16 ft band' after a 5.9 ft
basin drew as a doubled bund, and 12 ft is that band's lower edge.

THE RESEARCH PASS (T13, 2026-09-29) searched `research/fields/` for a stated basin width. It found no width floor, and two
entries that argue against one: fields/023 ('A basin never tapers to a point') - "So the rule is deliberately NOT a minimum
plot width - that would have been the obvious rule and it would have been wrong", on the strength of Shiroyone Senmaida's
basins (about 18 m2 each, the smallest half a meter square) and terrace beds "usually 2-6 m in width" - and fields/024
('Minimum basin SIZE'), which prices and declines an absolute floor "in the same way and for the same reason that a
minimum plot WIDTH is the wrong rule for a fan toe". A 12 ft floor would condemn a 2 m (6.6 ft) terrace bed the record
calls usual. What the review saw - two bunds a few feet apart - is the doubled bund, which `_shed_necks` and
`_visible_parts` already open at half the width floor; that stays the fabric's answer."""

DART_MAX_CELL = 0.75
"""NOT ENFORCED, with `DART_MIN_APEX` (water W27): a basin under ~0.75 of its design cell carrying a tip under
`DART_MIN_APEX` would read as a dart. A GUESS from the review's measurements (future-work 'A tip-angle companion to the
area floor'): Mizuguchi's arrowhead at 0.69 cell, and sharp tips on basins of 0.55-0.72 cell."""

DART_MIN_APEX = 30.0
"""NOT ENFORCED - the research contradicts the rule (water W27; deliberate deviation from the design row, recorded). The
review measured 27.4 / 27.6 / 30.4 deg tips and asked for a floor of ~25-30 deg; 30 is the top of that band (GUESS).

THE RESEARCH PASS (T13, 2026-09-29) found the record answers it: fields/023 sets where a taper stops being workable -
"at a 7.5 degree apex a plot is 5 ft wide 40 ft back from its point ... At 25 degrees the same wedge is 17 ft wide 40 ft
back, which is a workable bunded strip" - so a 27-30 deg tip is inside what the record calls workable, and the carve
already refuses under 25 (`_TOE_MIN_APEX`). And fields/025 ('The arrowhead') records the review's own request for a
tip-angle floor on the motivating Mizuguchi ring and that "the measurement said no" (min apex 38.3 deg raw, solidity
0.878: "an ordinary irregular basin - which is what the fabric is supposed to be full of"); the shape the review meant
is the arrowhead, pointed AND notched, which `arrowhead` below enforces (W25)."""

CHEVRON_APEX = _GATE_CHEVRON_APEX
CHEVRON_SOLIDITY = _GATE_CHEVRON_SOLIDITY
"""The arrowhead's gate line, 35 deg AND 0.85 solidity - caught at 40/0.90 by the weld, gated here (banks.py)."""


def ring_area(ring: Sequence[Sequence[float]]) -> float:
    """A ring's area by the shoelace, from its vertices as recorded."""
    return _poly_area([(float(p[0]), float(p[1])) for p in ring])


def _pts(ring: Sequence[Sequence[float]]) -> Poly:
    return [(float(p[0]), float(p[1])) for p in ring]


# SHAPELY ON FIRST USE, NOT AT IMPORT (feature 237): the import costs 16.3 MiB per gate worker, and only the three
# rules below that need a polygon's validity, union or minimum rectangle pay it.
_SHAPELY: Any = None


def _shapely() -> Any:
    global _SHAPELY  # the cached (Polygon, unary_union) pair is this module's own
    if _SHAPELY is None:
        from shapely.geometry import Polygon
        from shapely.ops import unary_union

        _SHAPELY = (Polygon, unary_union)
    return _SHAPELY


def needle(ring: Sequence[Sequence[float]]) -> bool:
    """W18/W20 - the basin tapers to a point: an interior angle under `NEEDLE_DEG` on the ring as recorded.

    A paddy is a level, bunded, puddled unit; narrowness and radial convergence are authentic, but no real basin
    tapers to ZERO - the last yards of a 7.5 deg wedge are two bunds with no floor between them."""
    return pointed_ring(_pts(ring), NEEDLE_DEG)


def too_small(ring: Sequence[Sequence[float]], cell: float) -> bool:
    """W21 - the basin is under `AREA_FLOOR` of the fan's design cell, too small to be worth its own bund."""
    return ring_area(ring) / float(cell) < AREA_FLOOR


def staircase(ring: Sequence[Sequence[float]], g: float) -> bool:
    """W23 - the ring's bund steps sideways more than `MAX_STEPS` times: a flight of steps, not a nudge.

    `g` is the engine's grain, `2 / ftpx` - the same conversion `jog_vertices` documents."""
    return len(jog_vertices(_pts(ring), g)) > MAX_STEPS


def self_crossing(ring: Sequence[Sequence[float]]) -> bool:
    """W24 - the ring (of three or more vertices) is not a simple polygon, so it is not a basin."""
    if len(ring) < 3:
        return False
    Polygon, _union = _shapely()
    return not Polygon(_pts(ring)).is_valid


def overcount(rings: Sequence[Sequence[Sequence[float]]]) -> float:
    """W22 - how far the ring areas over-count their union: (sum of areas - union) / union.

    The rule is `overcount(rings) < OVERCOUNT_CEILING`; a stack that unions to nothing has no denominator, so it
    raises rather than answering."""
    Polygon, unary_union = _shapely()
    polys = [Polygon(_pts(r)).buffer(0) for r in rings]
    union = unary_union(polys)
    if union.area <= 0:
        raise ValueError("the rings union to nothing, so the over-count has no denominator")
    return float((sum(p.area for p in polys) - union.area) / union.area)


def working_width(ring: Sequence[Sequence[float]]) -> float:
    """A basin's working width, px: its area over the longer side of its minimum rotated rectangle."""
    Polygon, _union = _shapely()
    poly = Polygon(_pts(ring)).buffer(0)
    rect = list(poly.minimum_rotated_rectangle.exterior.coords) if poly.area > 0 else []
    longest = max((math.dist(rect[i], rect[i + 1]) for i in range(len(rect) - 1)), default=0.0)
    return poly.area / longest if longest > 0 else 0.0


def narrow(ring: Sequence[Sequence[float]], g: float) -> bool:
    """W26 - the basin is narrower than `BASIN_MIN_WIDTH_FT` (converted at `g / 2` px per foot)."""
    return working_width(ring) < BASIN_MIN_WIDTH_FT * g / 2.0


def dart(ring: Sequence[Sequence[float]], cell: float) -> bool:
    """W27 - a small basin (under `DART_MAX_CELL`) with a tip under `DART_MIN_APEX`, on the raw or the deduped ring."""
    if ring_area(ring) / float(cell) >= DART_MAX_CELL:
        return False
    raw = _pts(ring)
    deduped = dedup_ring(raw, 1.0)
    return pointed_ring(raw, DART_MIN_APEX) or (len(deduped) >= 3 and pointed_ring(deduped, DART_MIN_APEX))


def arrowhead(ring: Sequence[Sequence[float]]) -> bool:
    """W25 - the basin reads as an arrowhead: pointed AND notched at the gate line (`is_chevron` at 35 / 0.85)."""
    return is_chevron(_pts(ring), CHEVRON_APEX, CHEVRON_SOLIDITY)


@dataclass(frozen=True)
class SupplyStroke:
    """One supply canal or delivery ditch as the bank rule reads it: centerline, head and tail widths, arc lengths,
    the bounding box grown by the stroke's reach (a prefilter that prunes and decides nothing), and its segment grid
    (`banks.StrokeIndex`, which answers `supply_bank_clearance` to the bit wherever the rule can act)."""

    pts: Poly
    w0: float
    w1: float
    cum: list[float]
    box: tuple[float, float, float, float]
    index: StrokeIndex


def supply_strokes(ditches: Sequence[dict[str, Any]]) -> list[SupplyStroke]:
    """The supply strokes of a fan from its recorded ditches (`poly`, `w`, `w_tail`); a stroke of under two points
    has no centerline and is skipped."""
    out = []
    for fd in ditches:
        pts = [(float(p[0]), float(p[1])) for p in (fd.get("poly") or [])]
        if len(pts) < 2:
            continue
        w0 = float(fd.get("w", 2.0))
        w1 = float(fd.get("w_tail", w0))
        reach = max(w0, w1) / 2 + BANK_MARGIN + 1.0
        box = (min(p[0] for p in pts) - reach, max(p[0] for p in pts) + reach, min(p[1] for p in pts) - reach, max(p[1] for p in pts) + reach)
        cum = polyline_cum(pts)
        out.append(SupplyStroke(pts, w0, w1, cum, box, StrokeIndex(pts, w0, w1, cum, reach)))
    return out


def supply_intrusions(ring: Sequence[Sequence[float]], strokes: Sequence[SupplyStroke]) -> list[tuple[int, int]]:
    """W16 - the points where the ring's bund stands inside a supply stroke: per stroke and edge, the first 3 px
    sample closer to the centerline than the stroke's local half-width plus `BANK_MARGIN` (less the rounding slack),
    rounded to the pixel. Samples projecting past a stroke's ENDS are not governed by it.

    THE BAR IS THE BAND PLUS THE ABUTMENT, NOT THE CENTERLINE: a bund and a ditch ABUT at the bank, and a rule that
    only forbade crossing the centerline would pass a bund drawn down the inside of the water (GM 2026-08-15)."""
    out: list[tuple[int, int]] = []
    n = len(ring)
    for s in strokes:
        x0, x1, y0, y1 = s.box
        for i in range(n):
            ax, ay = float(ring[i][0]), float(ring[i][1])
            bx, by = float(ring[(i + 1) % n][0]), float(ring[(i + 1) % n][1])
            if max(ax, bx) < x0 or min(ax, bx) > x1 or max(ay, by) < y0 or min(ay, by) > y1:
                continue
            steps = max(1, int(math.hypot(bx - ax, by - ay) / STROKE_SAMPLE_PX))
            for k in range(steps + 1):
                t = k / steps
                x, y = ax + t * (bx - ax), ay + t * (by - ay)
                # `supply_bank_clearance`, from the stroke's segment grid: exact wherever the verdict below can fire,
                # since that needs a gap under the reach the grid was built for (`StrokeIndex`'s own argument)
                gap, halfw, past, _foot, _nrm = s.index.clearance((x, y), exact=False)
                if not past and gap < halfw + BANK_MARGIN - STROKE_ROUNDING_PX:
                    out.append((round(x), round(y)))
                    break
    return out


def _seg_dist(p: Pt, a: Pt, b: Pt) -> float:
    vx, vy = b[0] - a[0], b[1] - a[1]
    L2 = vx * vx + vy * vy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / L2))
    return math.hypot(p[0] - (a[0] + t * vx), p[1] - (a[1] + t * vy))


def collector_strokes(drains: Sequence[dict[str, Any]]) -> list[tuple[Poly, float]]:
    """Each recorded collector as (centerline, half its widest width)."""
    return [([(float(p[0]), float(p[1])) for p in d["poly"]], max(float(d.get("w", 3.0)), float(d.get("w_tail", 3.0))) / 2.0) for d in drains]


def collector_crossings(ring: Sequence[Sequence[float]], drains: Sequence[tuple[Poly, float]]) -> list[tuple[int, int]]:
    """W17 - the start of every ring edge that runs ACROSS a collector rather than along it: both ends within
    `COLLECTOR_REACH` of the half-width from its centerline, and the edge longer than the stroke is wide. A paddy's
    low bund is the collector's bank; a bund across it would dam the thing that drains the field."""
    out: list[tuple[int, int]] = []
    n = len(ring)
    for pts, half in drains:
        # A PREFILTER THAT DECIDES NOTHING (constitution X clause 15): an edge end within `half * COLLECTOR_REACH` of the
        # centerline lies inside the centerline's box grown by that reach, so an edge with either end outside it is skipped.
        reach = half * COLLECTOR_REACH
        x0, x1 = min(p[0] for p in pts) - reach, max(p[0] for p in pts) + reach
        y0, y1 = min(p[1] for p in pts) - reach, max(p[1] for p in pts) + reach
        for k in range(n):
            a = (float(ring[k][0]), float(ring[k][1]))
            b = (float(ring[(k + 1) % n][0]), float(ring[(k + 1) % n][1]))
            if not (x0 <= a[0] <= x1 and y0 <= a[1] <= y1 and x0 <= b[0] <= x1 and y0 <= b[1] <= y1):
                continue
            if (
                min(_seg_dist(a, pts[i], pts[i + 1]) for i in range(len(pts) - 1)) < half * COLLECTOR_REACH
                and min(_seg_dist(b, pts[i], pts[i + 1]) for i in range(len(pts) - 1)) < half * COLLECTOR_REACH
                and math.dist(a, b) > 2 * half
            ):
                out.append((round(a[0]), round(a[1])))
    return out


def crosses_pond_rim(ring: Sequence[Sequence[float]], pond: Sequence[float]) -> bool:
    """W29 - a ring edge meets a field pond (`pond` = cx, cy, rx, ry): it crosses the rim, chords it, or stands in the
    water. A field pond is a low pocket dug INTO one basin; a bund through it reads as a flood. The body is
    `settlement._geom.ring_meets_ellipse`, the one predicate `_plot_pond` shrinks the pond against (feature 287, T04):
    the vertex-parity test this replaced missed a bund chording the pond between two outside vertices."""
    return ring_meets_ellipse(ring, float(pond[0]), float(pond[1]), float(pond[2]), float(pond[3]))


def under_island(ring: Sequence[Sequence[float]], disc: Sequence[float]) -> bool:
    """W28 - the ring runs under a grave island's mound (`disc` = cx, cy, r): a bund edge passes within the radius of
    its center, or the basin's floor lies under it. The flat paddy tiles AROUND an in-field grave."""
    cx, cy, r = float(disc[0]), float(disc[1]), float(disc[2])
    pts = _pts(ring)
    n = len(pts)
    return any(_seg_dist((cx, cy), pts[k], pts[(k + 1) % n]) < r for k in range(n)) or _pip(cx, cy, pts)


@dataclass
class RingContext:
    """What a ring is judged against: the fan's design cell, the grain, its supply strokes and collectors, and the
    field ponds and grave islands seated in it. A rule whose input is absent is not asked."""

    cell: float | None = None
    g: float | None = None
    supplies: list[SupplyStroke] = field(default_factory=list)
    drains: list[tuple[Poly, float]] = field(default_factory=list)
    ponds: list[tuple[float, float, float, float]] = field(default_factory=list)
    graves: list[tuple[float, float, float]] = field(default_factory=list)
    _supply_reach: Any = field(default=None, repr=False, compare=False)

    def near_supply(self, ring: Sequence[Sequence[float]]) -> bool:
        """Whether `ring`'s bund comes within reach of any supply stroke - a PREFILTER that decides nothing (constitution
        X clause 15). A bund point the stroke rule flags is nearer the centerline than the local half-width plus
        `BANK_MARGIN`, and the local half-width never exceeds the wider end's, so every such point lies inside the union
        of the strokes buffered by that much (plus a pixel of slack); a ring whose outline misses the union has none.
        The union is built once per context and prepared, so each ring asks it in one call - measured on a 911-plot
        hamlet fan, the stroke rule's 3 px walk over every ring cost 0.86 s and this answers the far ones for nearly none."""
        if not self.supplies:
            return False
        import shapely
        from shapely.geometry import LineString

        if self._supply_reach is None:
            self._supply_reach = shapely.union_all([LineString(s.pts).buffer(max(s.w0, s.w1) / 2 + BANK_MARGIN + 1.0) for s in self.supplies])
            shapely.prepare(self._supply_reach)
        pts = [(float(p[0]), float(p[1])) for p in ring]
        return bool(self._supply_reach.intersects(LineString([*pts, *pts[:1]])))


def fan_context(
    channels: Sequence[dict[str, Any]],
    g: float | None,
    cell: float | None,
    ponds: Sequence[Sequence[float]] = (),
    graves: Sequence[Sequence[float]] = (),
) -> RingContext:
    """The context a fan's rings are judged in, built from the ENGINE's channels (`pts`, `w`, `w_tail`, `role`) exactly
    as `_comb_record_ditches` will record them - points and widths rounded to 0.1 px, a point repeating its predecessor
    dropped - and the design cell as `_comb_record_field` records it. So the placer's context and the gate's (which
    reads the recorded `field_ditches` and `cell`) are one: supply strokes are every channel but the drain, and the
    collector is the drain."""

    def recorded(c: dict[str, Any]) -> dict[str, Any]:
        pts = [q for i, q in enumerate(c["pts"]) if i == 0 or math.dist(q, c["pts"][i - 1]) > 0.05]
        return {"poly": [(round(float(x), 1), round(float(y), 1)) for x, y in pts], "w": round(float(c["w"]), 1), "w_tail": round(float(c["w_tail"] if "w_tail" in c else c["w"]), 1)}

    supplies = [recorded(c) for c in channels if c.get("role") in ("main", "branch")]
    drains = [recorded(c) for c in channels if c.get("role") == "drain" and len(c.get("pts") or ()) >= 2]
    return RingContext(
        cell=round(float(cell), 1) if cell else None,
        g=g,
        supplies=supply_strokes(supplies),
        drains=collector_strokes(drains),
        ponds=[(float(p[0]), float(p[1]), float(p[2]), float(p[3])) for p in ponds],
        graves=[(float(d[0]), float(d[1]), float(d[2])) for d in graves],
    )


def as_recorded(ring: Sequence[Sequence[float]]) -> Poly:
    """`ring` as the manifest records it (`plot_rings`): every vertex rounded to 0.1 px, nothing else changed."""
    return [(round(float(p[0]), 1), round(float(p[1]), 1)) for p in ring]


def ring_violations(ring: Sequence[Sequence[float]], ctx: RingContext) -> set[str]:
    """Every rule `ring` breaks, by name - empty for a ring a placer may write.

    NOT ASKED: `narrow` (W26) and `dart` (W27) - the research contradicts both (see `BASIN_MIN_WIDTH_FT` and
    `DART_MIN_APEX`), so they are recorded rules, not enforced ones."""
    out = set()
    if needle(ring):
        out.add("needle")
    if self_crossing(ring):
        out.add("crossing")
    if arrowhead(ring):
        out.add("arrowhead")
    if ctx.cell and too_small(ring, ctx.cell):
        out.add("area")
    if ctx.g and staircase(ring, ctx.g):
        out.add("steps")
    if ctx.near_supply(ring) and supply_intrusions(ring, ctx.supplies):
        out.add("stroke")
    if collector_crossings(ring, ctx.drains):
        out.add("collector")
    if any(crosses_pond_rim(ring, p) for p in ctx.ponds):
        out.add("pond")
    if any(under_island(ring, d) for d in ctx.graves):
        out.add("grave")
    return out
