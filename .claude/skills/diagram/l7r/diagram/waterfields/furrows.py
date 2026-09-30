"""The dry hem's row directions, tract by tract (269 B06) - split out of `carve.py`, which `_dry_fields` calls it from."""

import math
import random
from collections.abc import Sequence
from typing import Any

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


SEAM_READS_RAD = 0.10
"""Two rows within ~6 deg read as ONE direction on the page, so a seam between tracts must turn by more than this, and two
plots of one tract may differ by no more than twice `TRACT_PLOT_TURN_RAD` (research fields/180; the gate's own figures)."""

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
    pair across tracts turned `SEAM_READS_RAD` or less. Both lists are named by the first plot's center, to the pixel."""
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


def settle_tract_seams(plots: list[dict[str, Any]]) -> None:
    """Hold every seam of a fan's dry hem to W35, in place, by turning whole tracts - never a plot's outline.

    `tract_ways` turns each tract off the ONE before it, which holds every seam along a straight hem; but a hem that
    bends round a canal elbow, and the fork triangle's second band laid against the first, set tracts side by side that
    were never compared. So every tract, in order, is compared with every earlier tract any of its plots neighbors - at
    the widest adjacency any later reading can take (`NEIGHBOR_REACH` of the LARGEST plot side, since the hem can only
    lose plots after this: the brook's band, a fan's wild middle) - and where a seam would read as one direction the
    tract is turned, all its plots together so its own rows still share one way, by the smallest turn that clears every
    such neighbor: first at the generator's own seam figure, `TRACT_SEAM_MIN_RAD` less the two plots' own turns, then at
    the rule's line. A furrow is modulo pi and each neighbor rules out a window, so only a tract hemmed in by more
    neighbors than fit round the half-circle has no such turn; it joins the neighbor whose rows it is closest to, taking
    that tract's number and heading - a larger tract, which the record allows (its sizes are open)."""
    ps = [p for p in plots if p.get("poly") and p.get("theta") is not None and p.get("tract") is not None]
    if len(ps) < 2:
        return
    radius = NEIGHBOR_REACH * max(_side(p) for p in ps)
    cents = [_center(p) for p in ps]
    near = [[j for j in range(len(ps)) if j != i and math.dist(cents[i], cents[j]) < radius] for i in range(len(ps))]
    order = sorted({p["tract"] for p in ps})
    shifts = [k * 0.025 * s for k in range(1, 64) for s in (1, -1)]
    for t in order:
        mine = [i for i, p in enumerate(ps) if p["tract"] == t]
        pairs = [(i, j) for i in mine for j in near[i] if ps[j]["tract"] != t and order.index(ps[j]["tract"]) < order.index(t)]
        floors = (TRACT_SEAM_MIN_RAD - 2 * TRACT_PLOT_TURN_RAD, SEAM_READS_RAD + THETA_ROUNDING_RAD)
        if _seams_clear(ps, pairs, 0.0, floors[0]):
            continue
        delta = next((d for floor in floors for d in shifts if _seams_clear(ps, pairs, d, floor)), None)
        if delta is not None:
            for i in mine:
                ps[i]["theta"] = float(ps[i]["theta"]) + delta
            continue
        host = min(pairs, key=lambda ij: furrow_turn(float(ps[ij[0]]["theta"]), float(ps[ij[1]]["theta"])))[1]
        for i in mine:
            ps[i]["tract"], ps[i]["theta"] = ps[host]["tract"], ps[host]["theta"]


def _seams_clear(ps: Sequence[dict[str, Any]], pairs: Sequence[tuple[int, int]], delta: float, floor: float) -> bool:
    """Whether turning the first plot of each pair by `delta` leaves every pair turned by more than `floor`."""
    return all(furrow_turn(float(ps[i]["theta"]) + delta, float(ps[j]["theta"])) > floor for i, j in pairs)
