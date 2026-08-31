"""Split from settlement/homestead_parts.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
from collections.abc import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


_BELT_GAP_FT = 30.0  # `village_windbreak_is_continuous`'s own bar - the fill closes what that check reads.
# THE NUMBER IS OURS; THE DIRECTION OF THE RULE IS THE RECORD'S (GM ruling 2026-08-29, "do whatever was
# historically true", research in settlements/vegetation.md). No source reached - Chinese or Japanese,
# historical or agronomic - gives a WIDTH for an opening in a shelter belt, so 30 ft is a rendering
# convention and is labelled one. What IS sourced is that a belt occupies one or two sides and is planted
# along them, that its ABSENT flank is not a gap (Honda 1915 defines yashikirin as the west and north
# sides), and that a bare run inside the planted stretch is not attested and funnels wind (Purdue NCR-191:
# an access crossing keeps the belt's own porosity rather than being left open). Hence: close holes WITHIN
# the run, never wrap the settlement.


def _belt_axis(pts: Sequence[tuple[float, float]]) -> tuple[float, float]:
    """The unit vector along a belt's own length, from the spread of its clumps.

    Taken from the seated points rather than from the wind, because what has to be walked in order is
    the run as DRAWN - a belt that bows around a plot is still one run, and sorting it by a wind-derived
    axis would interleave the two flanks of the bow."""
    n = len(pts)
    cx, cy = sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n
    sxx = sum((p[0] - cx) ** 2 for p in pts)
    syy = sum((p[1] - cy) ** 2 for p in pts)
    sxy = sum((p[0] - cx) * (p[1] - cy) for p in pts)
    th = 0.5 * math.atan2(2.0 * sxy, sxx - syy)  # the principal axis of the cloud
    return (math.cos(th), math.sin(th))
