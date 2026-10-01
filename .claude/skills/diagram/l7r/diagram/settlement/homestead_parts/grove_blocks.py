"""The keep-outs of ONE grove fill, indexed once and asked per candidate clump (feature 218).

WHY THIS EXISTS (GM 2026-09-08, on a 7.3 s windbreak stage: *"Is that because we are doing some kind
of overlap check every time we place an individual tree? ... suppose that we were to Start by drawing
the outline of where the Windbreak Forest is going to be, and then we lay down all of the trees within
that outline"*). `village_grove` walks a jittered grid over the grove's footprint and asks, per
candidate, whether a clump may stand there. Before this module every one of those questions was a
linear walk: `_hard_blocked` ran `edge_dist` over EVERY crop polygon and `seg_dist` over EVERY
watercourse segment, `_lane_blocked` over every corridor segment, and the re-seat search re-asked all
of it eight times per ring. Measured on the reference hamlet (specs/218 research R1): 37,490 candidate
positions x 25 crop polygons = 936,709 `edge_dist` calls and 7.19 million `seg_dist` calls, 77% of
the stage, to keep 150 clumps. The trees never test against each other - a dense belt overlaps its
clumps on purpose - so the whole cost was the carving of the outline, done again per tree.

This is the engine's PREFILTER pattern (`_geom/indexes.py`): every keep-out that does not change
during the fill is filed in a `PointGrid` (rings as `RingIndex`, polylines as boxed segments, circles
and open rectangles with their boxes) ONCE, and each candidate asks the cell it stands in. The index
PRUNES; the caller's exact test - the same `inside` / `edge_within` / `seg_dist` / squared-distance
expression the linear scan ran - still DECIDES, so every verdict is identical and the pool regenerates
byte-identical (the oracle `dev/performance.md` prescribes for this shape). Nothing is coarsened.

Module-level and built from plain lists (feature 146: an inner function that is hard to test gets
lifted out), so `tests/settlement/test_homestead_parts.py` can prove the verdicts equal the linear
expressions on a synthetic layout without rolling a settlement.
"""

from __future__ import annotations

import math
from typing import Any

from .._geom import PointGrid, RingIndex, boxed_circles, boxed_grid, boxed_rects, boxed_ring_hit, boxed_rings, boxed_seg_hit, boxed_segs, circle_hit, rect_hit


class GroveBlocks:
    """Every static keep-out of one `village_grove` fill, indexed once.

    `hard` is what `_hard_blocked` was: the crop rings within `crop_pad` of an edge (or inside), the
    dry plots within `dry_pad`, the dike outlines (inside only), and the watercourses within their
    reach - the edges a belt STOPS at, so a clump refused here is dropped. `lane` is what
    `_lane_blocked` was, and `local` what `_local_blocked` was (the occupancy circles, then the open
    sun-corridor rectangles) - a local obstacle a dense belt plants AROUND, so a clump refused there
    re-seats. `displaced` is the other grove's canopy alone, the one blocker a SPARSE grove re-seats
    for. `inside` and `rim_within` are the grove's own outline."""

    __slots__ = ("_clear", "_fams", "_inside", "_last", "_raw", "_region", "crop_pad", "dike_pad", "displacers", "dry_pad", "ring", "static")

    def __init__(
        self,
        *,
        outline: Any,
        crops: Any,
        crop_pad: float,
        dry: Any,
        dry_pad: float,
        dikes: Any,
        water: Any,
        corridors: Any,
        circles: Any,
        displacers: Any,
        rects: Any,
        dike_pad: float = 0.0,
    ) -> None:
        self.ring = RingIndex(outline)
        self.crop_pad, self.dry_pad = crop_pad, dry_pad
        # the dike and marsh outlines refuse a point inside them; `dike_pad` also refuses one within it of their edge - a
        # placer held a hair stricter than the planting (the reserved seats, `wood_share.BAR_MARGIN_PX`: a seat left on the
        # toe marsh's rounded edge, feature 287 M8)
        self.dike_pad = dike_pad
        # ONE GRID FOR EVERY STATIC FAMILY (feature 278, FR-010; 218's "one grid per scatter, not one per family", never
        # applied to the grove). The seven families were seven grids and a candidate asked up to seven of them - 1.09
        # million `near` calls on Kashikawa's belts. Filed together, tagged by family, in cells of the same size, a point's
        # cell holds exactly the items each family's own grid held there; the first question about a point splits them by
        # family and the rest reuse that split (`hard`, `local` and `lane` are asked of the same candidate in turn). Each
        # family's own hit test still decides, so no verdict changes.
        families = (
            boxed_rings(crops, crop_pad),
            boxed_rings(dry, dry_pad),
            boxed_rings(dikes, dike_pad),
            boxed_segs(water),  # (polyline, reach) pairs, the reach already including the clump's radius
            boxed_segs(corridors),  # (polyline, buffer) pairs from `_corridor_buffers`
            boxed_circles(circles),
            boxed_rects(rects),
        )
        self.static = PointGrid()
        self.static.extend((tag, it, *it[-4:]) for tag, fam in enumerate(families) for it in fam)
        self.displacers = boxed_grid(boxed_circles(displacers))
        self._last: tuple[float, float] | None = None
        self._fams: tuple[list[Any], ...] = ()
        self._inside: dict[tuple[float, float], bool] = {}
        self._clear: dict[tuple[float, float], bool] = {}
        self._raw = (outline, crops, crop_pad, dry, dry_pad, dikes, dike_pad, water, corridors, circles, rects)
        self._region: Any = None

    def _at(self, x: float, y: float) -> tuple[list[Any], ...]:
        """The static items in (x, y)'s cell, split by family: crops, dry, dikes, water, corridors, circles, rects."""
        if self._last != (x, y):
            fams: tuple[list[Any], ...] = ([], [], [], [], [], [], [])
            for tag, it, *_box in self.static.near(x, y):
                fams[tag].append(it)
            self._last, self._fams = (x, y), fams
        return self._fams

    def hard(self, x: float, y: float) -> bool:
        """The crop, open water, the dike bank: reasons moving a few feet does not change."""
        crop, dry, dikes, water, _corr, _circles, _rects = self._at(x, y)
        return boxed_ring_hit(x, y, crop, self.crop_pad) or boxed_ring_hit(x, y, dry, self.dry_pad) or boxed_ring_hit(x, y, dikes, self.dike_pad) or boxed_seg_hit(x, y, water)

    def lane(self, x: float, y: float) -> bool:
        return boxed_seg_hit(x, y, self._at(x, y)[4])

    def local(self, x: float, y: float) -> bool:
        """A house, a yard, a wellhead's keep-out, a shrine, a pond, the other grove, a sun corridor."""
        fams = self._at(x, y)
        return circle_hit(x, y, fams[5]) or rect_hit(x, y, fams[6])

    def displaced(self, x: float, y: float) -> bool:
        """Standing under the OTHER grove's canopy - the one refusal a sparse grove re-seats for."""
        return circle_hit(x, y, self.displacers.near(x, y))

    def inside(self, x: float, y: float) -> bool:
        """The outline's own test, remembered per point (feature 278, FR-010): the gap fill offers the SAME points on
        every round it runs - its depth search is deterministic - and the outline does not change during the fill."""
        hit = self._inside.get((x, y))
        if hit is None:
            hit = self._inside[(x, y)] = self.ring.inside(x, y)
        return hit

    def region(self) -> Any:
        """EVERY STATIC KEEP-OUT OF THE FILL PAINTED ONCE (feature 297, FR-004, plan B3 - the GM: "drawing a box and then filling it
        in"): the crops and the dry plots grown by their pads, the dikes and the marsh, the watercourses and the corridors at their
        reach, the occupancy circles and the sun rectangles, in one `Region` over the outline's box grown by the widest reach, at a
        cell of two pixels. Conservative (every shape grown by `region.GROW` cells), so ground it calls clear is clear of every
        family - a clump at a family's very margin may be lost, never one seated on a keep-out."""
        if self._region is None:
            from .._geom.region import Region

            outline, crops, crop_pad, dry, dry_pad, dikes, dike_pad, water, corridors, circles, rects = self._raw
            reach = max([crop_pad, dry_pad, dike_pad] + [float(r) for _pl, r in list(water) + list(corridors)] + [float(c[2]) for c in circles] + [0.0])
            xs, ys = [float(q[0]) for q in outline], [float(q[1]) for q in outline]
            region = Region((min(xs) - reach - 40.0, min(ys) - reach - 40.0, max(xs) + reach + 40.0, max(ys) + reach + 40.0), 2.0)
            for ring_ in crops:
                region.poly(ring_, crop_pad)
            for ring_ in dry:
                region.poly(ring_, dry_pad)
            for ring_ in dikes:
                region.poly(ring_, dike_pad)
            for pl, r in list(water) + list(corridors):
                region.line(pl, float(r))
            for cx, cy, r in circles:
                region.circle(float(cx), float(cy), float(r))
            for x0, y0, x1, y1 in rects:
                region.rect(float(x0), float(y0), float(x1), float(y1))
            self._region = region
        return self._region

    def static_clear(self, x: float, y: float) -> bool:
        """`not (hard or local or lane)`, read off the fill's one region (feature 297, plan B3): where the region holds the point
        clear it is clear of all three; where it does not, the families decide, as before, remembered per point (feature 281)."""
        hit = self._clear.get((x, y))
        if hit is None:
            hit = self._clear[(x, y)] = (not self.region().taken(x, y)) or not (self.hard(x, y) or self.local(x, y) or self.lane(x, y))
        return hit

    def static_clear_many(self, xs: Any, ys: Any) -> Any:
        """Which of the points the fill's region holds clear, at once (a boolean array): a True is clear of every static family;
        a False is still to be asked of them (`hard`, `local`, `lane`)."""
        return ~self.region().taken_many(xs, ys)

    def rim_within(self, x: float, y: float, limit: float) -> bool:
        """`edge_dist(x, y, outline) <= limit`, exactly: `edge_within` answers strictly-under, so the
        limit is nudged by an epsilon and the closed inequality re-asked on the distance it returns."""
        d = self.ring.edge_within(x, y, limit + 1e-9)
        return d is not None and d <= limit


class Seats:
    """The clumps seated so far, filed as they land, for the two "not on top of a neighbor" tests.

    Incremental on purpose: the list GROWS during the fill, and `PointGrid.extend` files the tail
    exactly. `too_near` runs the linear scan's own expression on the cell's occupants."""

    __slots__ = ("grid", "r2", "reach")

    def __init__(self, reach: float) -> None:
        self.reach = reach
        self.r2 = reach**2  # `(step * 0.55) ** 2` and `(clump * 0.5) ** 2` were the originals - the same power, once
        # A CELL THE SIZE OF THE REACH (feature 278, FR-010). At the default 128 px a query read every clump seated in a
        # 128 px square - dozens of a dense belt's - to find the few within a ~10 px reach: 4.5 million distance tests over
        # Kashikawa and Sawada's belts. At twice the reach a seat is filed in at most four cells and a query reads one.
        self.grid = PointGrid(cell=max(16.0, 2.0 * reach))

    def add(self, x: float, y: float) -> None:
        r = self.reach
        self.grid.extend([(x, y, x - r, y - r, x + r, y + r)])

    def too_near(self, x: float, y: float) -> bool:
        r2 = self.r2
        return any((x - sx) ** 2 + (y - sy) ** 2 < r2 for sx, sy, _x0, _y0, _x1, _y1 in self.grid.near(x, y))


class BankNear:
    """`near`'s index when the points have a BANK (feature 261, settlement-review of Kashikawa): a clump is near a point
    only within `reach` of it AND on its side of `barriers` - three dooryard-copse clumps stood 79-86 ft from a house as
    the crow flies, across the brook from every farmhouse, where the copse is the trees "in the gaps between the houses".
    Asked per clump like `Seats.too_near`."""

    def __init__(self, points: Any, reach: float, barriers: Any) -> None:
        from .._geom import PointGrid

        self.reach = reach
        self.points = PointGrid(max(reach, 1.0))
        self.points.extend([((float(p[0]), float(p[1])), float(p[0]), float(p[1]), float(p[0]), float(p[1])) for p in points])
        self.barriers = [((float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) for a, b in barriers]
        # ...each barrier filed once by its box (feature 287 perf: every clump walked every brook segment for every point near
        # it, 381,637 crossing tests on the reference seed 4's belt). EXACT: two segments `segments_cross` finds crossing
        # meet, so their boxes meet; a barrier whose box misses the line's by more than `_BOX_EPS` cannot cross it, and
        # `any` does not care about order.
        self.bars = PointGrid(max(reach, 1.0))
        self.bars.extend([(a, b, min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])) for a, b in self.barriers])

    _BOX_EPS = 1e-6  # px: far beyond the rounding of a crossing test on this canvas, far below anything drawn

    def too_near(self, x: float, y: float) -> bool:
        from .._geom import segments_cross

        e = self._BOX_EPS
        bars = None
        for it in self.points.near(x, y, self.reach):
            if math.dist((x, y), it[0]) > self.reach:
                continue
            if bars is None:
                bars = self.bars.near(x, y, self.reach + e)  # every barrier whose box comes within reach: a superset for each line
            px, py = it[0]
            lx0, ly0, lx1, ly1 = min(x, px) - e, min(y, py) - e, max(x, px) + e, max(y, py) + e
            if not any(bx1 >= lx0 and bx0 <= lx1 and by1 >= ly0 and by0 <= ly1 and segments_cross((x, y), it[0], a, b) for a, b, bx0, by0, bx1, by1 in bars):
                return True
        return False
