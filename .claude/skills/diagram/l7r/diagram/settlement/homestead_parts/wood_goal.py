"""THE HOMESTEADS' WOOD IS DRAWN AT ITS ROLL (feature 294 B9, the review's "drawn area against rolled area" class).

Each homestead's wood - its windward grove and its share of the copse together - is rolled within the 1684 register's range
(`HOMESTEAD_WOOD_FT2`, research/vegetation/210: a degree along a continuum, calibrated liberty). The copse used to be filled
TOWARD that roll and left short wherever the ground could not hold it, so the map recorded one size and drew another: Sawada
rolled 17,692 sq ft a homestead and drew 10,672 (60%), Kuwabata 14,686 and 11,809, and Inashiro, whose belt alone holds more
than its roll, drew 14,023 against 12,136. Now the roll is taken within the part of the register's range THIS ground can
hold - no less than the belt and the farm groves already give, no more than the belt, the groves and the fullest copse the
ground takes - and the copse is filled to the ground's capacity and trimmed back to the roll. The rolled size is then the
drawn size, and it is still inside the register's range: the range is the rule the record gives (the attainable bound is a
map drawing convention; the roll's log-uniform shape is the existing GUESS).

Research: plumbing - NONE
"""

from __future__ import annotations

from collections.abc import Sequence

from .._geom import CanopyArea
from .groves import HOMESTEAD_WOOD_FT2


def attainable_band(given_ft2: float, capacity_ft2: float) -> tuple[float, float]:
    """The part of the register's range one homestead's wood can be drawn at: no less than what the belt and the farm groves
    already give it (`given_ft2`), no more than the most the ground holds (`capacity_ft2`), within `HOMESTEAD_WOOD_FT2`. Where
    the ground gives more than the register's largest wood, the band is that one value (the wood drawn is the wood given).

    Research:
        homestead wood range - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: within
            6,000-28,000 sq ft
        held to what the ground holds - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: the
            roll's floor what already stands, its ceiling the fullest copse the ground takes
    """
    lo = max(HOMESTEAD_WOOD_FT2[0], given_ft2)
    hi = max(lo, min(HOMESTEAD_WOOD_FT2[1], capacity_ft2))
    return lo, hi


def rolled_wood(u: float, band: tuple[float, float]) -> float:
    """One homestead's wood from its positional roll `u` in [0, 1), log-uniform over `band` - the shape the register's own
    roll has (`homestead_wood_ft2`), taken over the attainable part of the range.

    Research:
        log-uniform roll - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: each doubling
            as likely as the next
    """
    lo, hi = band
    return float(lo * (hi / lo) ** u)


def copse_goal(rolls: Sequence[float], given_px2: float, kept_px2: float, capacity_px2: float, px2_per_ft2: float) -> tuple[float, float]:
    """(the copse's goal in px^2, the mean rolled wood a homestead in sq ft): every homestead's wood rolled within the
    attainable band, their sum less what the belt and the groves already give. The band's floor counts what always stands -
    the belt, the groves and the households' reserved copse seats (`kept_px2`, never trimmed); its ceiling, the copse at its
    fullest (`capacity_px2`).

    Research:
        copse makes up the wood - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: the
            rolled woods less what the belt and the groves give
    """
    n = len(rolls)
    if not n:
        return 0.0, 0.0
    band = attainable_band((given_px2 + kept_px2) / px2_per_ft2 / n, (given_px2 + max(kept_px2, capacity_px2)) / px2_per_ft2 / n)
    total_ft2 = sum(rolled_wood(u, band) for u in rolls)
    return max(0.0, total_ft2 * px2_per_ft2 - given_px2), total_ft2 / n


def canopy_of(seats: Sequence[tuple[float, float]], r: float, cell: float) -> float:
    """The ground (px^2) the crowns of radius `r` at `seats` cover, on `CanopyArea`'s raster of `cell`."""
    canopy = CanopyArea(cell)
    for x, y in seats:
        canopy.add(x, y, r)
    return canopy.area


def trim_to_goal(seats: Sequence[tuple[float, float]], kept: frozenset[tuple[float, float]], r: float, cell: float, goal: float) -> list[tuple[float, float]]:
    """The copse's seats trimmed back to `goal` (px^2): the households' reserved seats (`kept`) always stand; of the rest, the
    shortest run in seating order whose canopy reaches the goal - or, where one clump fewer lands nearer it, that. The canopy
    of a run only grows with its length, so the run is found by bisection."""
    base = [p for p in seats if p in kept]
    rest = [p for p in seats if p not in kept]
    lo, hi = 0, len(rest)
    while lo < hi:
        mid = (lo + hi) // 2
        if canopy_of(base + rest[:mid], r, cell) >= goal:
            hi = mid
        else:
            lo = mid + 1
    if lo > 0 and abs(canopy_of(base + rest[: lo - 1], r, cell) - goal) < abs(canopy_of(base + rest[:lo], r, cell) - goal):
        lo -= 1
    keep = set(base + rest[:lo])
    return [p for p in seats if p in keep]
