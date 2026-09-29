"""The dry hem's row directions, tract by tract (269 B06) - split out of `carve.py`, which `_dry_fields` calls it from."""

import math
import random

# HOW A TRACT IS DRAWN (269 B06, fields/180). The record gives the shape - tracts of neighboring plots, one direction
# each, a change of up to a right angle at the seam - and leaves the sizes open, so every figure here is a GUESS
# except where it says otherwise:
#   TRACT_COLUMNS         how many hem columns (each a strip of plots from the canal upslope) one tract holds.
#   TRACT_PLOT_TURN_RAD   how far a plot turns within its tract: ~3 deg either way, "a few degrees".
#   TRACT_LEAN_RAD        how far a tract's own ground turns its way off the pure contour or fall: ~17 deg.
#   TRACT_SEAM_MIN_RAD    the least change at a seam, ~20 deg - a map drawing convention: a seam must read as one, and
#                         the gate reads two rows within ~6 deg as one direction.
TRACT_COLUMNS = (2, 4)
TRACT_PLOT_TURN_RAD = 0.05
TRACT_LEAN_RAD = 0.30
TRACT_SEAM_MIN_RAD = 0.35
# Below this spread the hem is steep ground whose rows all converge on the contour (`furrows_vary`, comb.py): every tract
# runs the contour, turned no further than the spread allows, and no seam is required. Steep or terraced rows on the
# contour is the record's own inference, a GUESS (fields/180).
STEEP_SPREAD_RAD = 0.3


def furrow_turn(a: float, b: float) -> float:
    """The angle between two row directions, in radians, 0 to pi/2: a furrow has no head and tail, so it is modulo pi."""
    d = abs(a - b) % math.pi
    return min(d, math.pi - d)


def tract_ways(R: random.Random, ncols: int, theta0: float, spread: float) -> list[tuple[int, float]]:
    """Per hem column, `(tract index, the tract's row heading)`.

    The columns fall into runs of `TRACT_COLUMNS`; each run takes one of the two ways the record gives - along the
    contour (`theta0`) or down to its outfall (a right angle off it) - leaned by up to `TRACT_LEAN_RAD` for its own
    ground. A tract that would come out within `TRACT_SEAM_MIN_RAD` of the one before takes the other way, so every
    seam reads. On steep ground (`spread` under `STEEP_SPREAD_RAD`) every tract runs the contour, leaned no further than
    `spread`."""
    steep = spread < STEEP_SPREAD_RAD
    lean = min(TRACT_LEAN_RAD, spread)
    out: list[tuple[int, float]] = []
    prev: float | None = None
    tract = 0
    while len(out) < ncols:
        way = 0.0 if steep else R.choice((0.0, math.pi / 2))
        heading = theta0 + way + R.uniform(-lean, lean)
        if not steep and prev is not None and furrow_turn(heading, prev) < TRACT_SEAM_MIN_RAD:
            heading += math.pi / 2 if way == 0.0 else -math.pi / 2
        out += [(tract, heading)] * R.randint(*TRACT_COLUMNS)
        prev, tract = heading, tract + 1
    return out[:ncols]
