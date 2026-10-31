"""A comb fan's partition held to the ring rules AT CONSTRUCTION (feature 302): split, merge, or left bare.

`partition.cut` tiles the planted region with cells whose bunds are shared as laid; some cells break a rule a basin keeps - a
sliver at a ditch junction, a needle where a row meets a bank at an angle, a staircase, a cell under the area floor. Each is
resolved here the three ways the old repair resolved the rings it wrote (`seams/close.py` `hold_ring_rules`: "split, welded,
or left bare"), on a tiling that is still a tiling:

- the partition is SNAPPED to the recorded grid first (`GRID`, the 0.1 px the manifest rounds to): a sliver thinner than a
  recorded coordinate collapses, and a shared bund snaps the same way on both sides;
- each cell is judged ONCE (`verdict`: `ring_violations` and the toe discipline `_comb_toe_and_hem` dropped by);
- a staircase is split on its hops by the repair's own `_split_steps`;
- any other failing cell is merged into the neighbor across their longest shared bund whose union holds the rules - the union
  OPENED by `OPEN` px, so a sliver's hair spike does not ride into its neighbor's outline - and two failing cells may merge
  when the union's only fault is its size (`SIZE_ONLY`), so the cluster of scraps a ditch junction leaves grows into a basin;
- a merge never grows a cell past the partition's own recut bound (`partition.RECUT_OVER` design cells): the settle may not
  undo the lattice's backstop (glyph check, Inashiro: three ragged cells merged into one of 4.2 design cells);
- what neither makes lawful is LEFT BARE, as the repair left it ("the odd corner left unpaddied").

Research: settle plumbing - NONE: grid snapping, polygon cleanup, union and shared-length measures, the cell index
"""

from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any

from .banks import _TOE_MIN_APEX, _TOE_MIN_AREA, _TOE_MIN_THICKNESS, dedup_ring, is_chevron, pointed_ring
from .frame import Poly, _poly_area, _poly_perim
from .ring_rules import RingContext, ring_violations

SIZE_ONLY = frozenset({"area", "toe", "steps"})
"""The faults a union of two failing cells may still carry and be kept growing: its size, the toe discipline, a staircase.

Research: scraps grow into a basin - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html, research/questions/0014-bunds-between-the-paddies-aze.drawing.html: two failing cells may merge while the union's faults are only its size, the toe discipline (thin, pointed, an arrowhead) or a staircase - a union still growing, never kept on the map until it keeps every rule
"""


def ring_of(poly: Any) -> Poly:
    """A polygon's outer ring as recorded (rounded to the grid, the closing vertex dropped)."""
    import shapely

    # the coordinates in one call, not shapely's sequence iterated (feature 427 T09: its Python wrappers, 50k calls at 40 households)
    return [(round(x, 1), round(y, 1)) for x, y in shapely.get_coordinates(poly.exterior).tolist()[:-1]]


def verdict(poly: Any, ctx: RingContext, plot_across: float, cell: float) -> set[str]:
    """Every rule the cell breaks: `ring_violations`, and "toe" for the toe discipline - too thin (twice the area over the
    perimeter under `_TOE_MIN_THICKNESS` plot widths), under `_TOE_MIN_AREA` design cells, pointed under `_TOE_MIN_APEX`, or a
    chevron.

    Research:
        ring rules - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html, research/questions/0014-bunds-between-the-paddies-aze.drawing.html: every `ring_violations` rule
        toe discipline - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html, research/questions/0014-bunds-between-the-paddies-aze.drawing.html: too thin (0014: the thin strip takes the fan toe's least width), under the area floor, pointed under 25 deg, or an arrowhead
    """
    ring = ring_of(poly)
    found = set(ring_violations(ring, ctx))
    per, area = _poly_perim(ring), _poly_area(ring)
    if (
        per <= 0
        or 2 * area / per < _TOE_MIN_THICKNESS * plot_across
        or area < _TOE_MIN_AREA * cell
        or pointed_ring(dedup_ring([(float(p[0]), float(p[1])) for p in ring], 1.0), _TOE_MIN_APEX)
        or is_chevron(ring)
    ):
        found.add("toe")
    return found


def takes(union: Any, judged: Callable[[Any], set[str]], me: Any, neighbor: Any, neighbor_fails: bool, most: float = math.inf) -> set[str] | None:
    """The verdict on `union` if the merge of `me` into `neighbor` may be kept - lawful but for a staircase (split after it), or,
    where the neighbor fails too, growing with only its size short - else None. A union over `most` (the recut bound) is never
    kept.

    Research:
        merge kept when lawful - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a scrap taken into its neighbor where the union keeps the rules
        merge bounded - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: never past the recut bound of RECUT_OVER design cells
    """
    if union is None or union.geom_type != "Polygon" or len(union.interiors) or union.area > most:
        return None
    v = judged(union)
    if not (v - {"steps"}):
        return v
    if neighbor_fails and not (v - SIZE_ONLY) and union.area > max(me.area, neighbor.area):
        return v
    return None
