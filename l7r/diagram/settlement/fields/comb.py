"""The comb-field builder, its base fill, its bund junctions, and its furrows.

Split from settlement/fields.py by feature 112 - see settlement/fields/CLAUDE.md for the index.

Research: plumbing - NONE: geometry, indexing, tolerances and manifest records
"""

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any

from l7r.diagram.work_counts import OPS

from .._geom import (
    Poly,
    Pt,
    point_in_poly,
    point_quad_dist,
    quad_hits_seg,
    seg_dist,
    seg_reach_index,
)
from .outfall import CURVE_LEG_PX as CURVE_LEG_PX
from .outfall import DOWNHILL_FRACTION as DOWNHILL_FRACTION
from .outfall import outfall_run as outfall_run
from .outfall import runs_downhill as runs_downhill

if TYPE_CHECKING:
    pass


class WetLines:
    """The `(polyline, half-width)` pairs `hem_on_water` asks, each segment filed once by its box widened by its half-width
    (`seg_reach_index`), so a plot asks only the segments whose widened box meets its own box (feature 287 perf: the
    coarse-grain top-up asks the whole wild middle, 558 plots on the reference seed 4, and each walked every ditch segment
    on the map - 35,000 `quad_hits_seg`). EXACT: a stroke that meets a plot has a point within its half-width of the
    plot, so its widened box meets the plot's box; a segment it skips could not have hit, and `any` does not care about
    order."""

    __slots__ = ("grid",)

    def __init__(self, wet: Sequence[tuple[Any, float]]) -> None:
        self.grid = seg_reach_index([([(float(q[0]), float(q[1])) for q in pl], float(hw)) for pl, hw in wet], 0.0)

    def hit(self, poly: Poly) -> bool:
        x0, y0 = min(q[0] for q in poly), min(q[1] for q in poly)
        x1, y1 = max(q[0] for q in poly), max(q[1] for q in poly)
        for a, b, hw, bx0, by0, bx1, by1 in self.grid.near((x0 + x1) / 2, (y0 + y1) / 2, max(x1 - x0, y1 - y0) / 2):
            if bx1 < x0 or bx0 > x1 or by1 < y0 or by0 > y1:
                continue
            if quad_hits_seg(poly, a, b, hw):
                return True
        return False


def hem_on_water(poly: Poly, wet: Sequence[tuple[Any, float]] | WetLines, pond: Any) -> bool:
    """Does this dry-hem plot lie across a watercourse or over the pond?

    LIFTED OUT OF `_comb_draw_hem` (feature 146, GM 2026-08-28 on inner functions and testability). The
    hem yields to standing water because the comb builder lays the fan from pure geometry and `draw_comb_field`
    used to render it blind - it was the ONLY placer that consulted nothing, so a hem plot could be drawn
    straight across a stream that had been authored earlier (Ubame's). The stream arm and the pond arm are
    different geometry and want asking separately, which through the method meant building a whole comb net.

    Research: hem off water - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: a dry plot across a watercourse or over the pond is not a field
    """
    if (wet if isinstance(wet, WetLines) else WetLines(wet)).hit(poly):  # a caller asking many plots hands the index in
        return True
    return bool(pond is not None and point_quad_dist(pond[0], pond[1], poly) < max(pond[2], pond[3]))


def channel_end_on_stream(end: Sequence[float], stream: Sequence[Sequence[float]], width: float) -> bool:
    """THE RULE (feature 287, labels L16; `channels_join_streams_at_confluence`): a channel end that declares a stream lies
    inside that stream's drawn `width` - within half of it of the centerline - so the mouth reaches INTO the water, never dying
    in the grass beside it (feature 328: it was a flat 13 px, wider than a 7 ft brook's whole bed). The intake that declares it
    and the test of it read this one predicate.

    Research: mouth reaches the water - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: a meeting is a junction when a channel's end lies inside the other's drawn width"""
    pts = [(float(q[0]), float(q[1])) for q in stream]
    return any(seg_dist(float(end[0]), float(end[1]), a, b) <= width / 2.0 for a, b in zip(pts, pts[1:], strict=False))


def feed_stub(race: Sequence[Sequence[float]], envelope: Sequence[Pt]) -> list[Sequence[float]]:
    """The drawn inlet stub of a pond-fed race (feature 294 B1): its points from the last one inside the crop's `envelope` - the
    ring's corner, where the feed meets the field - to its end on the reservoir's rim (`inlet_to_rim`). With no envelope to ask, or
    no point of the race inside it, the race's last leg."""
    for i in range(len(race) - 1, -1, -1):
        if len(envelope) >= 3 and point_in_poly(float(race[i][0]), float(race[i][1]), list(envelope)):
            return list(race[i:])
    return list(race[-2:])


def bead_drowned(q: Pt, water: Any, ellipses: Sequence[tuple[float, float, float, float]]) -> bool:
    """THE RULE (feature 287, water W33; `bund_beans_on_bunds`): an azemame bead stands on water paint - inside a pond's rim
    (`ellipses`, each grown by the rim stroke and a bead radius) or nearer than a ditch's or channel's half-width to its
    stroke (`water`, a `seg_reach_index` of (run, half) pairs). The bead drop and the test of it read this one predicate.

    Research: beads off water - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: no bean bead on a pond's rim or under a ditch's stroke"""
    if __debug__:
        OPS["candidate@bead_drowned"] += 1
    if any(((q[0] - ex) / erx) ** 2 + ((q[1] - ey) / ery) ** 2 <= 1.0 for ex, ey, erx, ery in ellipses):
        return True
    return any(x0 <= q[0] <= x1 and y0 <= q[1] <= y1 and seg_dist(q[0], q[1], a, b) < half for a, b, half, x0, y0, x1, y1 in water.near(q[0], q[1]))


def recorded_water(M: Mapping[str, Any]) -> Any:
    """Every recorded ditch and channel as the bead rule reads them: (run, half-width) filed once in a `seg_reach_index`.
    A ditch's half is its WIDEST - the tail of a tapered collector - since that is what the painter reaches."""
    runs = [([(float(q[0]), float(q[1])) for q in d["poly"]], max(float(d.get("w", 3.0)), float(d.get("w_tail", 3.0))) / 2.0) for d in (M.get("field_ditches") or []) if len(d.get("poly") or ()) >= 2]
    runs += [([(float(q[0]), float(q[1])) for q in c["poly"]], float(c.get("w", 3.0)) / 2.0) for c in (M.get("channels") or []) if len(c.get("poly") or ()) >= 2]
    return seg_reach_index(runs, 0.0)
