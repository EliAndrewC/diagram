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


def _vertex_box(ring: Any) -> tuple[float, float, float, float]:
    xs = [float(v[0]) for v in ring]
    ys = [float(v[1]) for v in ring]
    return min(xs), min(ys), max(xs), max(ys)


class PlotGeoms:
    """The plots of one seam pass: a geometry per plot on demand, neighbors by tree."""

    __slots__ = ("_geom", "_ring", "_tree", "_tree_ids", "_tree_rings", "plots")

    def __init__(self, plots: list[dict[str, Any]]) -> None:
        if not _SHAPELY_LOADED:
            _load_shapely()
        self.plots = plots
        self._geom: dict[int, BaseGeometry] = {}
        self._ring: dict[int, Any] = {}
        self._tree: STRtree | None = None
        self._tree_ids: list[int] = []
        self._tree_rings: list[Any] = []

    def geom(self, k: int) -> BaseGeometry:
        """`Polygon(plots[k]["poly"]).buffer(0)`, built once per ring object."""
        ring = self.plots[k]["poly"]
        if self._ring.get(k) is not ring:
            self._geom[k] = Polygon(ring).buffer(0)
            self._ring[k] = ring
        return self._geom[k]

    def _fresh(self) -> bool:
        return (
            self._tree is not None
            and len(self._tree_ids) == sum(1 for p in self.plots if len(p["poly"]) >= 3)
            and all(self.plots[k]["poly"] is r for k, r in zip(self._tree_ids, self._tree_rings, strict=True))
        )

    def near(self, bounds: tuple[float, float, float, float], exclude: int = -1) -> list[int]:
        """Every plot index (ascending, `exclude` left out, rings under three vertices left out) whose
        vertex extent touches `bounds` - the set the passes' strict bounds gate admitted."""
        if not self._fresh():
            self._tree_ids = [k for k, p in enumerate(self.plots) if len(p["poly"]) >= 3]
            self._tree_rings = [self.plots[k]["poly"] for k in self._tree_ids]
            self._tree = STRtree([box(*_vertex_box(r)) for r in self._tree_rings])
        assert self._tree is not None
        hits = sorted(int(self._tree_ids[j]) for j in self._tree.query(box(*bounds)))
        return [k for k in hits if k != exclude]


class GeomTree:
    """Neighbors among a list of finished basins that a pass replaces by index (`into[j] = merged`).

    The tree is built ONCE over the envelopes as they stood; a basin the pass has since replaced is
    remembered in `changed` and tested against its CURRENT envelope directly, so a merge that grew a
    basin past its old box is never missed and the tree is never rebuilt inside a round. Rebuilding
    it after every merge was measured first (specs/220 research R4): 101 rebuilds of a 600-basin tree
    cost more than the scan they replaced."""

    __slots__ = ("_n", "_tree", "changed", "geoms")

    def __init__(self, geoms: list[Polygon]) -> None:
        if not _SHAPELY_LOADED:
            _load_shapely()
        self.geoms = geoms
        self._tree: STRtree | None = None
        self._n = -1
        self.changed: set[int] = set()

    def replaced(self, j: int) -> None:
        """`geoms[j]` has a new geometry: read its envelope directly from now on."""
        self.changed.add(j)

    def near(self, bounds: tuple[float, float, float, float], pad: float = 0.0) -> list[int]:
        """Every index (ascending) whose CURRENT envelope touches `bounds` widened by `pad` on every side."""
        if self._tree is None or self._n != len(self.geoms):
            self._tree = STRtree([box(*g.bounds) for g in self.geoms])
            self._n = len(self.geoms)
            self.changed.clear()
        x0, y0, x1, y1 = bounds[0] - pad, bounds[1] - pad, bounds[2] + pad, bounds[3] + pad
        hits = {int(j) for j in self._tree.query(box(x0, y0, x1, y1)) if int(j) not in self.changed}
        for j in self.changed:
            gx0, gy0, gx1, gy1 = self.geoms[j].bounds
            if not (gx1 < x0 or gx0 > x1 or gy1 < y0 or gy0 > y1):
                hits.add(j)
        return sorted(hits)
