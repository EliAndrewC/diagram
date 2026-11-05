"""A seated cluster's DRAWN ASPECT (`cluster_aspect`), read on its own axis; split from hamletgen/homesteads.py by feature 173. The
front row and the lane frontage that lived here are the Rust's since feature 444 T30 (`rust/phases/src/homesteads/grove_seat.rs`).

Research: seat geometry - NONE: a measure; the units that decide carry their own claims
"""

from __future__ import annotations

import math

from ..consts import BUNDLE_PITCH

# A pixel of margin and the rounding of a turn keyed on a 4 px cell (`bearing.KEY_CELL_PX`). It was the +/-5 degree rake's
# reach past the axis-aligned box; since 269 B18 a house may turn 30 degrees or a quarter turn, and the stage measures that
# reach per seat (`turn_the_seat`) instead of carrying it here as slack.

# ---- STAGE 5: the homesteads --------------------------------------------------------------------


# `_FIELD_RING_FLOOR` and `_FRONT_ROW_LANE_CAP` lived here and are GONE (feature 126). They were the
# two halves of a rule that judged a front-row seat by its distance to a drawn lane, and they existed
# only because the lanes were drawn BEFORE the houses. Now that the internal lanes are worn
# afterwards, a seat has no lane to be near and the rule had nothing left to mean.
#
# DO NOT REINTRODUCE A DISTANCE-TO-LANE TEST IN THIS STAGE. That is the inversion the whole feature
# removes: a farmhouse is sited by the field it works and the ground it can stand on. Two earlier
# attempts to TUNE this cap are recorded in the git history as dead ends; a third would be worse than
# either, because the thing it measures is no longer on the map when it runs.


def cluster_aspect(xs: list[float], ys: list[float]) -> float:
    """The house cloud's long:short ratio measured on ITS OWN principal axis - rotation-invariant.

    The observable `CLUSTER_DRAWN_ASPECT` is stated in, and the quantity a reader gets by laying a
    ruler along the cluster rather than along the page. A page-axis bbox ratio is not that quantity:
    it tends to 1.0 for any band on a diagonal, and is maximally blind at 45 degrees.

    Principal axis by second moments (a 2x2 covariance eigenvector, closed form via atan2), then the
    EXTENT along and across it. Extent rather than the eigenvalue ratio on purpose - a ruler measures
    the cloud's span, not its variance, and the two differ for an uneven rank (Sawada 3.02 by extent,
    2.72 by PCA sd). Mirrored in the gate; `tests/hamletgen/test_cluster_shape.py` pins the two equal
    by evaluating both on the same point sets, not by comparing source."""
    _n = len(xs)
    if _n < 2:
        return 1.0
    _mx, _my = sum(xs) / _n, sum(ys) / _n
    _sxx = sum((x - _mx) ** 2 for x in xs) / _n
    _syy = sum((y - _my) ** 2 for y in ys) / _n
    _sxy = sum((x - _mx) * (y - _my) for x, y in zip(xs, ys, strict=True)) / _n
    _th = 0.5 * math.atan2(2.0 * _sxy, _sxx - _syy)
    _c, _s = math.cos(_th), math.sin(_th)
    _along = [x * _c + y * _s for x, y in zip(xs, ys, strict=True)]
    _across = [-x * _s + y * _c for x, y in zip(xs, ys, strict=True)]
    _du = max(_along) - min(_along)
    _dv = max(_across) - min(_across)
    # A ROW IS ONE HOMESTEAD DEEP, NOT ZERO DEEP (the GM, 2026-10-01: tripwire seed 33 fixed). The extents are of the
    # houses' CENTERS, so a perfectly straight single row - ten houses fronting one straight field margin - measured
    # about 0.2 ft across and drew 2,345:1, past every shape's band, and `seat_every_household` refused every margin of
    # the site. A reader's ruler laid across that row reads the homesteads' own depth, so the short side is floored
    # at the along-row span (`BUNDLE_PITCH`, 100 ft): the row reads about n:1, a string. The floor reaches
    # only a near-straight row - every exhibit the bands were calibrated on (`CLUSTER_DRAWN_ASPECT`) is far deeper. The
    # long side takes the same floor, so a cloud smaller than one homestead each way reads 1:1, never under it.
    return max(BUNDLE_PITCH, _du, _dv) / max(BUNDLE_PITCH, min(_du, _dv))
