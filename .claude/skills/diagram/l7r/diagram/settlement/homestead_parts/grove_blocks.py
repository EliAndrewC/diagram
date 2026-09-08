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

    __slots__ = ("circles", "corr", "crop", "crop_pad", "dikes", "displacers", "dry", "dry_pad", "rects", "ring", "water")

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
    ) -> None:
        self.ring = RingIndex(outline)
        self.crop, self.crop_pad = boxed_grid(boxed_rings(crops, crop_pad)), crop_pad
        self.dry, self.dry_pad = boxed_grid(boxed_rings(dry, dry_pad)), dry_pad
        self.dikes = boxed_grid(boxed_rings(dikes))
        self.water = boxed_grid(boxed_segs(water))  # (polyline, reach) pairs, the reach already including the clump's radius
        self.corr = boxed_grid(boxed_segs(corridors))  # (polyline, buffer) pairs from `_corridor_buffers`
        self.circles = boxed_grid(boxed_circles(circles))
        self.displacers = boxed_grid(boxed_circles(displacers))
        self.rects = boxed_grid(boxed_rects(rects))

    def hard(self, x: float, y: float) -> bool:
        """The crop, open water, the dike bank: reasons moving a few feet does not change."""
        return (
            boxed_ring_hit(x, y, self.crop.near(x, y), self.crop_pad)
            or boxed_ring_hit(x, y, self.dry.near(x, y), self.dry_pad)
            or boxed_ring_hit(x, y, self.dikes.near(x, y))
            or boxed_seg_hit(x, y, self.water.near(x, y))
        )

    def lane(self, x: float, y: float) -> bool:
        return boxed_seg_hit(x, y, self.corr.near(x, y))

    def local(self, x: float, y: float) -> bool:
        """A house, a yard, a wellhead's keep-out, a shrine, a pond, the other grove, a sun corridor."""
        return circle_hit(x, y, self.circles.near(x, y)) or rect_hit(x, y, self.rects.near(x, y))

    def displaced(self, x: float, y: float) -> bool:
        """Standing under the OTHER grove's canopy - the one refusal a sparse grove re-seats for."""
        return circle_hit(x, y, self.displacers.near(x, y))

    def inside(self, x: float, y: float) -> bool:
        return self.ring.inside(x, y)

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
        self.grid = PointGrid()

    def add(self, x: float, y: float) -> None:
        r = self.reach
        self.grid.extend([(x, y, x - r, y - r, x + r, y + r)])

    def too_near(self, x: float, y: float) -> bool:
        r2 = self.r2
        return any((x - sx) ** 2 + (y - sy) ** 2 < r2 for sx, sy, _x0, _y0, _x1, _y1 in self.grid.near(x, y))
