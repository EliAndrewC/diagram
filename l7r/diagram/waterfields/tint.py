"""A comb fan's low ground and its water tint (feature 302): which plots are `low`, which are painted FLOODED.

`low` is the TOPOGRAPHY; `fill` is only the PICTURE (feature 010). The carve used to set both as it cut the closing rank - `low`
on the bottom two levels, FLOODED on a random 45% of the level whose bottom edge lies on the collector - and `close_seams`
re-judged the tint at its end against every plot's final ring. With the plots laid as a partition (`partition.py`) there is no
closing rank to cut, so both are set here from where each plot lies, and the re-judgment - moved here verbatim from
`seams/close.py`, its clauses and its promotion - runs on the finished plots as it always did. Since feature 328 wave 40 the
clauses are 0007's alone: a needle, a pointed apex, a taper to a point.

Research: tint plumbing - NONE: ring rounding for the needle test
"""

from __future__ import annotations

from typing import Any

from .frame import Poly
from .ring_rules import needle


def _needle(poly: Poly) -> bool:
    """The flooded tint's needle rule on the ring AS RECORDED - `ring_rules.needle`, the test's own call, asked of the
    plot rounded to the manifest's 0.1 px (feature 287, T04), so the tint pass and the test judge one ring."""
    return needle([(round(float(q[0]), 1), round(float(q[1]), 1)) for q in poly])


FRONTAGE_SHARE = 0.5
"""Research: a real length along the drain - CONVENTION: half a plot's width of the plot's OWN edge within a quarter plot of the
drain (glyph-check of Sawada, round 2: a corner plot's edge near the drain measures 8-15 ft, a fronting plot's 19 ft or more)"""


def fronts(poly: Any, line: Any, plot_across: float) -> bool:
    """Does `poly` front `line` - half a plot's width of its own edge within a quarter plot of the line? Measuring the LINE near
    the plot instead (the first cut) is a distance test in disguise: a single corner near a long drain cuts a chord of it.

    Research: fronting the drain - research/questions/0007-wet-paddies-that-never-drain-shitsuden.drawing.html: the plots whose foot lies on the drain
        its figures from 0007 - research/questions/0007-wet-paddies-that-never-drain-shitsuden.drawing.html: 0.25 (the same test of fronting the drain)
    """
    return bool(poly.exterior.intersection(line.buffer(0.25 * plot_across)).length >= FRONTAGE_SHARE * plot_across)
