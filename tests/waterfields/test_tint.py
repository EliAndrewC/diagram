"""`waterfields/tint.py` (feature 302): the low ground and the water tint - moved from the end of `close_seams`, its tests with it.

The collector runs along y = 1300 throughout (`_D`), as it did in the seam pass's own tests of the tint.
"""

from __future__ import annotations

import math

_D = [(100.0, 1300.0), (1300.0, 1300.0)]
GREEN = "#A6C398"


def _rect(x0: float, y0: float, x1: float, y1: float) -> list[tuple[float, float]]:
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def _segmented_wedge(apex_deg: float, cut: float, length: float, step: float, at: tuple[float, float]) -> list[tuple[float, float]]:
    """A wedge pointing -x with its tip cut `cut` ft from the apex, each long side stored as `step`-ft segments (glyph-check
    wet paddy on Sawada, feature 328 wave 40 round 2: plots at 18.8 and 22.8 deg behind 1.6-2.3 ft tips kept the tint)."""
    h = math.radians(apex_deg / 2)
    ds = [cut + k * step for k in range(int((length - cut) / step) + 1)]
    top = [(at[0] + d * math.cos(h), at[1] - d * math.sin(h)) for d in ds]
    bot = [(at[0] + d * math.cos(h), at[1] + d * math.sin(h)) for d in reversed(ds)]
    return [*top, *bot]


def test_a_plot_fronts_the_drain_only_along_a_real_length_of_it() -> None:
    """Feature 328 (glyph-check of Sawada; 0007: the plots whose foot lies on the drain): a plot meeting the drain only at a
    corner does not front it; one lying along it does."""
    from shapely.geometry import LineString, Polygon

    from l7r.diagram.waterfields.tint import fronts

    drain = LineString([(0.0, 0.0), (400.0, 0.0)])
    along = Polygon([(10.0, 2.0), (50.0, 2.0), (50.0, 30.0), (10.0, 30.0)])
    corner = Polygon([(405.0, 3.0), (440.0, 3.0), (440.0, 30.0), (405.0, 30.0)])  # past the drain's end
    assert fronts(along, drain, 32.0) and not fronts(corner, drain, 32.0)
    # glyph-check of Sawada round 2: a second-row plot with ONE vertex near a long drain, a green wedge between - a chord of
    # the drain's line near it passed the first cut
    diamond = Polygon([(300.0, 5.0), (320.0, 25.0), (300.0, 45.0), (280.0, 25.0)])
    assert not fronts(diamond, drain, 32.0), "a corner beside a long drain does not front it"
