"""Split from waterfields/seams.py by feature 173 - see this package's CLAUDE.md for the index.

Research: pocket plumbing - NONE: lazy shapely binding, polygon parts and recorded rings
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # shapely's names for the type checker; `_load_shapely` binds the runtime ones
    from shapely.geometry import LineString, Point, Polygon
    from shapely.geometry.base import BaseGeometry
    from shapely.ops import unary_union

from ..banks import (
    polyline_cum,
)
from ..frame import BANK_MARGIN, Poly, taper_w

_SHAPELY_LOADED = False


def _load_shapely() -> None:
    """Bind shapely's names into this module, on first use rather than at import (feature 237, FR-010).

    WHY. `import shapely` costs 16.3 MiB of resident memory - it pulls numpy in with it - and a module-level
    import here made all ten gate workers pay that merely to COLLECT this package, whichever one of them ran
    the geometry (`specs/237-lean-test-collection/research.md` R9). Only a worker that builds a map needs it.

    WHY NOT AN `import` INSIDE THE FUNCTIONS THEMSELVES. Several of them run per plot, per seam or per
    candidate, and an `import` statement re-enters `__import__` on every call. Binding the names into this
    module's own globals ONCE leaves every call site the plain global lookup it already was, so the deferral
    costs nothing in steady state (spec D6); the sentinel makes a repeat call two bytecodes. An increase on
    any seed is not waiverable for this item - the bookends are `make perf LABEL=237-start|-end`.

    A MEASURED DEAD END, recorded so nobody pulls the lever again: checking the sentinel INLINE at each call
    site - `if not _SHAPELY_LOADED: _load_shapely()`, to save the call itself - bought nothing measurable (the
    bookend's slow seed stayed at +3.6%, because what it pays is the 0.244 s import, not the call) and cost the
    100% floor, since with several call sites per module only the first one to run ever executes its
    `_load_shapely()` line and the rest are unreachable.
    """
    global _SHAPELY_LOADED, LineString, Point, Polygon, unary_union  # binding this module's own names is the point
    if _SHAPELY_LOADED:
        return
    from shapely.geometry import LineString, Point, Polygon
    from shapely.ops import unary_union

    _SHAPELY_LOADED = True


def _parts(geom: BaseGeometry) -> list[Polygon]:
    """Simple polygons of `geom`, in a deterministic order (shapely does not promise one)."""
    _load_shapely()
    out = [g for g in getattr(geom, "geoms", [geom]) if isinstance(g, Polygon) and not g.is_empty and g.is_valid]
    return sorted(out, key=lambda g: (round(g.bounds[0], 1), round(g.bounds[1], 1)))


def _ring(poly: Polygon) -> Poly:
    """A plot ring as the manifest records it: 1dp, no repeated closing vertex, and no vertex
    that rounding has collapsed onto its predecessor (a boolean result carries plenty)."""
    _load_shapely()
    out: Poly = []
    for x, y in list(poly.exterior.coords)[:-1]:
        pt = (round(float(x), 1), round(float(y), 1))
        if not out or pt != out[-1]:
            out.append(pt)
    while len(out) > 3 and out[0] == out[-1]:
        out.pop()
    return out


def _water(channels: list[dict[str, Any]], g: float) -> BaseGeometry:
    """Every drawn course plus its BANK - the ground a bund may abut but never stand in.

    Buffered per SEGMENT at the local width, because the supply canals taper hard (14 px head to a
    couple at the tail): one buffer at the widest half-width would claim bank the fan really does
    plant, and re-open exactly the kind of strip this pass exists to close.

    AND A DISC AT EVERY INTERIOR VERTEX, which is not optional. Flat-capped segment buffers are
    rectangles, so two of them meeting at a bend leave a WEDGE of uncovered ground on the outside
    of the turn. Ten of Inashiro's new basins came out with a bund inside a delivery ditch through
    exactly those notches - the ground looked bare to this pass and was water to the gate. The
    discs close them without the over-claim a round CAP would add past the head and tail, past
    the stroke's ends, where it governs nothing anyway.

    Research:
        bund abuts the water - research/questions/0055-where-a-field-meets-its-ditch-the-bank-the-bund-and-the-inlet-mizuguchi.drawing.html: each course's local half-width plus half a bund is ground no bund stands in
        width along the run - research/questions/0069-how-our-maps-draw-a-channel-narrowing-along-its-run.drawing.html: the half-width read from the shared taper law
    """
    _load_shapely()
    strokes: list[tuple[str, BaseGeometry, float]] = []
    for c in channels:
        pts = [(float(q[0]), float(q[1])) for q in c.get("pts") or []]
        if len(pts) < 2:
            continue
        w0 = float(c["w"])
        w1 = float(c.get("w_tail", w0))
        cum = polyline_cum(pts)
        tot = cum[-1] or 1.0

        def half(k: int, w0: float = w0, w1: float = w1, cum: list[float] = cum, tot: float = tot) -> float:
            return taper_w(w0, w1, cum[k] / tot) / 2 + BANK_MARGIN * g

        for i in range(len(pts) - 1):
            strokes.append(("seg", LineString([pts[i], pts[i + 1]]), half(i)))
        for i in range(1, len(pts) - 1):
            strokes.append(("disc", Point(pts[i]), half(i)))
    if not strokes:
        return Polygon()
    import shapely

    # BUFFERED AS TWO ARRAY CALLS, one for the segments and one for the discs, then put back in the order they were
    # listed (feature 276, FR-004): the same buffers, a few hundred calls fewer.
    segs = [k for k, st in enumerate(strokes) if st[0] == "seg"]
    discs = [k for k, st in enumerate(strokes) if st[0] == "disc"]
    shapes: list[Any] = [None] * len(strokes)
    for idx, made in (
        (segs, shapely.buffer([strokes[k][1] for k in segs], [strokes[k][2] for k in segs], cap_style="flat") if segs else []),
        (discs, shapely.buffer([strokes[k][1] for k in discs], [strokes[k][2] for k in discs]) if discs else []),
    ):
        for k, geom in zip(idx, list(made), strict=True):
            shapes[k] = geom
    return unary_union(shapes)
