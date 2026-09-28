"""One shapely geometry per plot, and neighbors by spatial tree (feature 220, constitution X clause 15).

The seam passes rebuilt `Polygon(plot["poly"]).buffer(0)` on every look and found a basin's neighbors
by walking every plot with a bounds gate computed from its vertices - per trade, per absorption. On
the reference fan that was 35,000 polygon constructions and 268,000 bounds reads per build (specs/220
research R1). `PlotGeoms` builds a plot's geometry once and drops it when the plot's ring is REASSIGNED
(the passes never mutate a ring in place - they assign a new list, which is what the identity check
reads), and answers "which plots could touch this box" from an `STRtree` over the same vertex-extent
boxes the old gate compared, rebuilt lazily after any ring changes. `GeomTree` does the same for the
finished basins the pocket pass merges into.

Both are PREFILTERS in the engine's sense (`settlement/_geom/indexes.py`): the tree returns every plot
whose box touches the query box, exactly the set the strict `<`/`>` gate let through, and the exact
shapely tests that follow still decide - so the passes' verdicts, and the map, are unchanged."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # the names for the type checker; the runtime ones are bound by `_load_shapely`
    from shapely import STRtree, box
    from shapely.geometry import Polygon
    from shapely.geometry.base import BaseGeometry


_SHAPELY_LOADED = False


def _load_shapely() -> None:
    """Bind shapely's names into this module, on first use rather than at import (feature 237, FR-010).

    WHY. `import shapely` costs 16.3 MiB - it pulls numpy with it - and a module-level import here made every
    one of the ten gate workers pay that to COLLECT this package, whoever ran the geometry
    (`specs/237-lean-test-collection/research.md` R9). Only the worker that builds a map needs it.

    WHY NOT AN `import` INSIDE THE FUNCTIONS THAT USE IT. `geom()` and `near()` are called per plot and per
    query, and an `import` statement re-enters `__import__` on every call. Binding the real names into the
    module's globals once means every call site afterwards is the plain global lookup it was before, so the
    deferral costs nothing in steady state (spec D6). Called from the constructors: neither class can be
    used without one.
    """
    global _SHAPELY_LOADED, STRtree, box, Polygon  # binding the module-level names is the point
    if _SHAPELY_LOADED:
        return
    from shapely import STRtree, box
    from shapely.geometry import Polygon

    _SHAPELY_LOADED = True


def _vertex_box(ring: Any) -> tuple[float, float, float, float]:
    xs = [float(v[0]) for v in ring]
    ys = [float(v[1]) for v in ring]
    return min(xs), min(ys), max(xs), max(ys)


def ring_polygons(rings: list[Any], clean: bool = True) -> list[Any]:
    """`Polygon(ring).buffer(0)` (or, with `clean=False`, `Polygon(ring)`) for every ring of three or more vertices, and
    `None` for the rest - as two ARRAY calls rather than two calls per ring (feature 276, FR-004, plan D11/D12). The seam
    passes built this per plot in five places, 700 plots at a time. The coordinates are handed to GEOS as they stand, and
    a ring GEOS will not build as one batch (one already closed on itself, say) sends the whole list back through the
    per-ring constructor, so the answer is the per-ring answer either way."""
    _load_shapely()
    import numpy
    import shapely

    keep = [k for k, r in enumerate(rings) if len(r) >= 3]
    out: list[Any] = [None] * len(rings)
    if not keep:
        return out
    try:
        coords = numpy.asarray([(float(v[0]), float(v[1])) for k in keep for v in rings[k]], dtype=float)
        index = numpy.repeat(numpy.arange(len(keep)), [len(rings[k]) for k in keep])
        built = shapely.polygons(shapely.linearrings(coords, indices=index))
    except ValueError, shapely.errors.GEOSException:
        built = [Polygon(rings[k]) for k in keep]
    made: Any = shapely.buffer(built, 0) if clean else built
    for k, p in zip(keep, list(made), strict=True):
        out[k] = p
    return out


class PlotGeoms:
    """The plots of one seam pass: a geometry per plot on demand, neighbors by tree."""

    __slots__ = ("_built", "_geom", "_ring", "_tree", "_tree_ids", "plots")

    def __init__(self, plots: list[dict[str, Any]]) -> None:
        _load_shapely()
        self.plots = plots
        self._geom: dict[int, BaseGeometry] = {}
        self._ring: dict[int, Any] = {}
        self._tree: STRtree | None = None
        self._tree_ids: list[int] = []
        self._built: list[Any] = []

    def geom(self, k: int) -> BaseGeometry:
        """`Polygon(plots[k]["poly"]).buffer(0)`, built once per ring object."""
        ring = self.plots[k]["poly"]
        if self._ring.get(k) is not ring:
            self._geom[k] = Polygon(ring).buffer(0)
            self._ring[k] = ring
        return self._geom[k]

    def near(self, bounds: tuple[float, float, float, float], exclude: int = -1) -> list[int]:
        """Every plot index (ascending, `exclude` left out, rings under three vertices left out) whose
        vertex extent touches `bounds` - the set the passes' strict bounds gate admitted.

        THE TREE IS KEPT WHILE RINGS CHANGE, AND A CHANGED RING IS ASKED DIRECTLY (feature 276, FR-004, plan D12). It
        used to be rebuilt over every plot whenever any one ring had been reassigned since the last query - about
        twenty rebuilds of a 700-plot tree per build. Now a plot whose ring is no longer the one the tree was built
        over is left out of the tree's answer and tested against its CURRENT vertex extent, the way `GeomTree` does
        for a replaced basin; the tree is rebuilt only when the plot list changes length or the stale set grows past
        `_STALE_REBUILD`. The answer is the same set either way: every plot whose current extent touches `bounds`."""
        n = len(self.plots)
        stale = [k for k in range(n) if self.plots[k]["poly"] is not self._built[k]] if self._tree is not None and len(self._built) == n else None
        if stale is None or len(stale) > _STALE_REBUILD:
            self._built = [p["poly"] for p in self.plots]
            self._tree_ids = [k for k in range(n) if len(self._built[k]) >= 3]
            self._tree = STRtree([box(*_vertex_box(self._built[k])) for k in self._tree_ids])
            stale = []
        assert self._tree is not None
        gone = set(stale)
        hits = {k for k in (int(self._tree_ids[j]) for j in self._tree.query(box(*bounds))) if k not in gone}
        qx0, qy0, qx1, qy1 = bounds
        for k in stale:
            ring = self.plots[k]["poly"]
            if len(ring) >= 3:
                x0, y0, x1, y1 = _vertex_box(ring)
                if not (x1 < qx0 or x0 > qx1 or y1 < qy0 or y0 > qy1):
                    hits.add(k)
        return sorted(k for k in hits if k != exclude)


# PAST THIS MANY CHANGED RINGS THE TREE IS REBUILT (feature 276): each stale ring costs a direct extent test per query,
# a rebuild costs one box per plot; at 64 against a 700-plot field the two are the same order. A tuning figure, not a
# rule - the answer does not depend on it.
_STALE_REBUILD = 64


class GeomTree:
    """Neighbors among a list of finished basins that a pass replaces by index (`into[j] = merged`).

    The tree is built ONCE over the envelopes as they stood; a basin the pass has since replaced is
    remembered in `changed` and tested against its CURRENT envelope directly, so a merge that grew a
    basin past its old box is never missed and the tree is never rebuilt inside a round. Rebuilding
    it after every merge was measured first (specs/220 research R4): 101 rebuilds of a 600-basin tree
    cost more than the scan they replaced."""

    __slots__ = ("_n", "_tree", "changed", "geoms")

    def __init__(self, geoms: list[Polygon]) -> None:
        _load_shapely()
        self.geoms = geoms
        self._tree: STRtree | None = None
        self._n = -1
        self.changed: dict[int, tuple[float, float, float, float]] = {}

    def replaced(self, j: int) -> None:
        """`geoms[j]` has a new geometry: read its envelope directly from now on - taken here, once, rather than on every
        query that follows (feature 276, FR-004: a round's queries re-read up to a hundred changed envelopes each)."""
        self.changed[j] = self.geoms[j].bounds

    def near(self, bounds: tuple[float, float, float, float], pad: float = 0.0) -> list[int]:
        """Every index (ascending) whose CURRENT envelope touches `bounds` widened by `pad` on every side."""
        if self._tree is None or self._n != len(self.geoms):
            self._tree = STRtree(list(self.geoms))  # a tree over the geometries answers by their envelopes - the same boxes, unbuilt
            self._n = len(self.geoms)
            self.changed.clear()
        x0, y0, x1, y1 = bounds[0] - pad, bounds[1] - pad, bounds[2] + pad, bounds[3] + pad
        hits = {int(j) for j in self._tree.query(box(x0, y0, x1, y1)) if int(j) not in self.changed}
        for j, (gx0, gy0, gx1, gy1) in self.changed.items():
            if not (gx1 < x0 or gx0 > x1 or gy1 < y0 or gy0 > y1):
                hits.add(j)
        return sorted(hits)
