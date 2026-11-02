"""A tapered channel cut a piece a segment (`taper_pieces`), and the bank clearances and swept bends the drawing reads.

Research: bank geometry - NONE: arc lengths, nearest segments, the stroke index, rounding slack
"""

import math

from .frame import Poly, taper_w


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
    margin of 0.75 grains. Nothing crosses on any shipped map, so this is a shrunken abutment, not a
    bund in the water. IF IT IS EVER WORTH CLOSING: have each reader of a band's width take `t` at the arc midpoint of the
    segment it identifies as nearest, instead of at the query point's own arc fraction (the Python field's
    bank clearances that did this read were deleted by feature 444 T16). It re-rolls
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
