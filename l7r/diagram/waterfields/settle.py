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
from .partition import RECUT_OVER
from .ring_rules import RingContext, ring_violations

GRID = 0.1
"""The recorded grid (px): the manifest rounds every ring to it, so the partition is snapped to it before it is judged."""

OPEN = 0.3
"""A merged union is opened by this many px (mitred): a spike under 0.6 px wide - six recorded coordinates - does not survive."""

SIMPLIFY = 0.25
"""The merged outline simplified by this many px: the opening's own collinear vertices, not a bund's course."""

PINHOLE = 1.0
"""A hole under this many px² in a merged union is the snapped grid's leftover, filled before the union is judged: no cell is
that small (the area floor is a fifth of a design cell, hundreds of px²).

Research: pinhole - NONE: grid hygiene
"""

ROUNDS = 6
"""The merge repeats until nothing merges, at most this many passes (a cluster of scraps grows one neighbor a pass)."""

SIZE_ONLY = frozenset({"area", "toe", "steps"})
"""The faults a union of two failing cells may still carry and be kept growing: its size, the toe discipline, a staircase.

Research: scraps grow into a basin - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html, research/questions/0014-bunds-between-the-paddies-aze.drawing.html: two failing cells may merge while the union's faults are only its size, the toe discipline (thin, pointed, an arrowhead) or a staircase - a union still growing, never kept on the map until it keeps every rule
"""


def ring_of(poly: Any) -> Poly:
    """A polygon's outer ring as recorded (rounded to the grid, the closing vertex dropped)."""
    return [(round(x, 1), round(y, 1)) for x, y in list(poly.exterior.coords)[:-1]]


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


def polygons(geom: Any) -> list[Any]:
    """The non-empty polygons of `geom`, of positive area."""
    import shapely

    return [p for p in shapely.get_parts(geom) if p.geom_type == "Polygon" and not p.is_empty and p.area > 0]


def valid(poly: Any) -> Any:
    """`poly`, or the largest polygon of its `buffer(0)` where it is invalid (a snapped cell can pinch)."""
    if poly.is_valid:
        return poly
    parts = polygons(poly.buffer(0))
    return max(parts, key=lambda q: q.area) if parts else poly


def opened_union(a: Any, b: Any) -> Any | None:
    """`a` and `b` merged, opened by `OPEN` and simplified by `SIMPLIFY` - or None where shapely refuses the geometry.

    A union that does not come out one polygon, or carries a hole under `PINHOLE`, is WELDED first (`welded`): two cells
    that touch along a hairline bund the snapping left unfused, or a sub-pixel hole no cell fills, are the grid's artifacts,
    not a gap between basins (feature 328 wave 77, spec-fidelity: Sawada's two bare scraps each had a lawful neighbor so
    refused). A union already one clean polygon is not touched, so every merge that held before holds the same.
    """
    import shapely

    try:
        u = shapely.union(a, b)
        if u.geom_type != "Polygon" or any(shapely.Polygon(r).area < PINHOLE for r in u.interiors):
            u = welded(u)
        return shapely.simplify(u.buffer(-OPEN, join_style="mitre").buffer(OPEN, join_style="mitre"), SIMPLIFY)
    except shapely.errors.GEOSException:
        return None


def welded(u: Any) -> Any:
    """`u` closed by `GRID` (a hairline between two touching cells fused) and rid of every hole under `PINHOLE` px².

    Research: welded union - NONE: the snapped grid's hairlines and pinholes closed before a merge is judged
    """
    import shapely

    c = u.buffer(GRID, join_style="mitre").buffer(-GRID, join_style="mitre")
    parts = [p for p in getattr(c, "geoms", [c]) if p.geom_type == "Polygon" and not p.is_empty]
    out = [shapely.Polygon(p.exterior, [r for r in p.interiors if shapely.Polygon(r).area >= PINHOLE]) for p in parts]
    return out[0] if len(out) == 1 else shapely.MultiPolygon(out)


def shared_length(a: Any, b: Any) -> float:
    """How much of `a`'s outline runs along `b` (within 0.2 px) - 0 where shapely refuses the geometry."""
    import shapely

    try:
        return float(a.boundary.intersection(b.buffer(0.2)).length)
    except shapely.errors.GEOSException:
        return 0.0


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


class Fabric:
    """The cells being settled, each with its verdict, and the index their neighbors are found in."""

    def __init__(self, cells: list[Any], ctx: RingContext, plot_across: float, cell: float) -> None:
        import shapely

        self.ctx, self.plot_across, self.cell = ctx, plot_across, cell
        self.alive: dict[int, Any] = {}
        self.fails: dict[int, set[str]] = {}
        self._next = 0
        for snapped in shapely.set_precision(cells, GRID):
            for q in polygons(snapped):
                self.add(q)
        for i in [k for k, v in self.fails.items() if "steps" in v]:
            self.split(i)
        self.ids = list(self.alive)
        self.tree = shapely.STRtree([self.alive[k] for k in self.ids])
        self.owner = {k: k for k in self.ids}

    def judge(self, poly: Any) -> set[str]:
        return verdict(poly, self.ctx, self.plot_across, self.cell)

    def add(self, poly: Any) -> int:
        poly = valid(poly)
        k = self._next
        self.alive[k], self.fails[k] = poly, self.judge(poly)
        self._next += 1
        return k

    def split(self, i: int) -> None:
        """A staircase split on its hops by the repair's own `_split_steps` (W23).

        Research: staircase split - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a bund that steps sideways is carried straight on instead
        """
        from .seams.close import _split_steps

        if not self.ctx.g or "steps" not in self.fails[i]:
            return
        parts = _split_steps(self.alive[i], self.ctx)
        if len(parts) > 1:
            del self.alive[i], self.fails[i]
            for q in parts:
                for r in polygons(q):
                    self.add(r)

    def find(self, k: int) -> int:
        while self.owner.get(k, k) != k:
            k = self.owner[k]
        return k

    def neighbors(self, i: int) -> list[int]:
        """The cells sharing a stretch of bund with cell `i`, the longest shared stretch first."""
        me = self.alive[i]
        scored = set()
        for jj in self.tree.query(me.buffer(0.2)):
            j = self.find(self.ids[int(jj)])
            if j != i and j in self.alive:
                shared = shared_length(me, self.alive[j])
                if shared > 0.0:
                    scored.add((shared, j))
        return [j for _s, j in sorted(scored, reverse=True)]

    def merge(self, i: int) -> bool:
        """Cell `i` merged into the first neighbor that may take it (`takes`); True if it was.

        Research: merge across the longest shared bund - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: the neighbors tried longest shared bund first
        """
        me = self.alive[i]
        for j in self.neighbors(i):
            u = opened_union(me, self.alive[j])
            v = takes(u, self.judge, me, self.alive[j], bool(self.fails[j]), RECUT_OVER * self.cell)
            if v is None:
                continue
            self.alive[j], self.fails[j] = u, v
            del self.alive[i], self.fails[i]
            self.owner[i] = j
            self.split(j)
            return True
        return False


def settle_cells(cells: list[Any], ctx: RingContext, plot_across: float, cell: float) -> tuple[list[Any], list[Any]]:
    """The partition's cells held to the rules: (the lawful cells, the scraps left bare). See the module docstring.

    Research: unlawful scraps left bare - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: a strip that would draw every basin it touches out to a needle point stays bare; every other scrap is taken into a neighbor
    """
    fab = Fabric(cells, ctx, plot_across, cell)
    for _round in range(ROUNDS):
        failing = sorted((k for k in fab.alive if fab.fails[k]), key=lambda k: fab.alive[k].area)
        if not sum(1 for i in failing if i in fab.alive and fab.fails[i] and fab.merge(i)):
            break
    scraps = [fab.alive[k] for k, v in fab.fails.items() if v]
    return [fab.alive[k] for k, v in fab.fails.items() if not v], scraps
