"""The dry hem's row directions, tract by tract (269 B06) - split out of `carve.py`, which `_dry_fields` calls it from.

Research: row-direction geometry - NONE: angle arithmetic, plot centers and sides, neighbor tests
"""

import math
from collections.abc import Sequence
from typing import Any

TRACT_PLOT_TURN_RAD = 0.05
"""Research: plot turn within a tract - GUESS: about 3 deg either way"""


def furrow_turn(a: float, b: float) -> float:
    """The angle between two row directions, in radians, 0 to pi/2: a furrow has no head and tail, so it is modulo pi."""
    d = abs(a - b) % math.pi
    return min(d, math.pi - d)


SEAM_READS_RAD = 0.10
"""Two rows within ~6 deg read as ONE direction on the page, so a seam between tracts must turn by more than this, and two
plots of one tract may differ by no more than twice `TRACT_PLOT_TURN_RAD` (research fields/180; the gate's own figures).

Research: one direction on the page - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: two rows within about 6 deg read as one direction
"""

THETA_ROUNDING_RAD = 0.002
"""The manifest records `theta` to 0.001 rad, so each pair's turn carries up to twice that of rounding."""

NEIGHBOR_REACH = 1.25
"""Two dry plots are neighbors when their centers lie within this many plot sides of each other - adjacency derived from
the plots, as a flat pixel radius once made the rule compare no pairs at all."""


def _center(p: dict[str, Any]) -> tuple[float, float]:
    return (sum(float(v[0]) for v in p["poly"]) / len(p["poly"]), sum(float(v[1]) for v in p["poly"]) / len(p["poly"]))


def _side(p: dict[str, Any]) -> float:
    pp = p["poly"]
    n = len(pp)
    return float(abs(sum(float(pp[i][0]) * float(pp[(i + 1) % n][1]) - float(pp[(i + 1) % n][0]) * float(pp[i][1]) for i in range(n))) / 2) ** 0.5


def tract_seams(plots: Sequence[dict[str, Any]], side: float | None = None) -> tuple[int, int, list[tuple[int, int]], list[tuple[int, int]]]:
    """The rule (water W35, `dry_plot_furrows_vary` re-scoped to tracts): over the dry plots that carry a row direction and
    a tract, `(pairs within a tract, pairs across a seam, tracts run apart, seams that do not turn)`. Neighbors are plots
    whose centers lie within `NEIGHBOR_REACH` sides - the plots' mean side, or `side` where the caller holds a wider one.
    A tract run apart is a pair of one tract turned more than twice `TRACT_PLOT_TURN_RAD`; a seam that does not turn is a
    pair across tracts turned `SEAM_READS_RAD` or less. Both lists are named by the first plot's center, to the pixel.

    Research: tracts and their seams - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: a tract's plots share one direction, a seam turns far enough to read
    """
    ps = [p for p in plots if p.get("poly") and p.get("theta") is not None and p.get("tract") is not None]
    if len(ps) < 2:
        return 0, 0, [], []
    cents = [_center(p) for p in ps]
    radius = NEIGHBOR_REACH * (side if side is not None else sum(_side(p) for p in ps) / len(ps))
    within, seams, split, blurred = 0, 0, [], []
    for a in range(len(ps)):
        for b in range(a + 1, len(ps)):
            if math.dist(cents[a], cents[b]) >= radius:
                continue
            turn = furrow_turn(float(ps[a]["theta"]), float(ps[b]["theta"]))
            where = (round(cents[a][0]), round(cents[a][1]))
            if ps[a]["tract"] == ps[b]["tract"]:
                within += 1
                if turn > 2 * TRACT_PLOT_TURN_RAD + THETA_ROUNDING_RAD:
                    split.append(where)
            else:
                seams += 1
                if turn <= SEAM_READS_RAD:
                    blurred.append(where)
    return within, seams, split, blurred
