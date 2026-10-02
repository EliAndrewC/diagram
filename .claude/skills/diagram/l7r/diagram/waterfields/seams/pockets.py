"""Split from waterfields/seams.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # shapely's names for the type checker; `_load_shapely` binds the runtime ones
    from shapely.geometry import LineString, Point, Polygon
    from shapely.geometry.base import BaseGeometry
    from shapely.ops import unary_union

from ..banks import (
    polyline_cum,
)
from ..frame import BANK_MARGIN, Poly, _f_at_u, _Frame, taper_w

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
    discs close them without the over-claim a round CAP would add past the head and tail, where
    `supply_bank_clearance` reports `past` and the stroke governs nothing anyway."""
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


def _band(F: _Frame, us: list[float], fs: list[float], f_far: float) -> Polygon:
    """The region between the sampled curve f(u) and a constant fall far outside the fan."""
    _load_shapely()
    pts = [F.to_xy(u, f) for u, f in zip(us, fs, strict=True)]
    pts += [F.to_xy(us[-1], f_far), F.to_xy(us[0], f_far)]
    return Polygon(pts).buffer(0)


def _outside_command(F: _Frame, a_pts: Poly, dpts: Poly, field: Polygon, g: float, bank: Callable[[float], float]) -> BaseGeometry:
    """Ground the fan cannot command: below the collector, or upslope of the supply canal.

    The collector is extended LEVEL beyond both drawn ends (the same clamp `_fill_wedges` used and
    `floor_overhang` states): the command area's low boundary conceptually continues past the
    drawn water, so a low-u fork wedge still counts as commanded while the floating-diamond ground
    past the outfall does not. Where the canal does not reach a given u there is nothing upslope to
    exclude, so that sample falls back to a bound outside the fan entirely."""
    _load_shapely()
    x0, y0, x1, y1 = field.bounds
    corners = [F.to_uf(x0, y0), F.to_uf(x1, y0), F.to_uf(x1, y1), F.to_uf(x0, y1)]
    ulo, uhi = min(u for u, _ in corners), max(u for u, _ in corners)
    flo, fhi = min(f for _, f in corners), max(f for _, f in corners)
    span = (uhi - ulo) + (fhi - flo) + 1.0
    # SAMPLE THE CURVES FINELY. The band is a polygon through sampled points, so between samples
    # its edge is a CHORD - and a chord across a bend in a wandering collector cuts inside the
    # curve, admitting ground the fan may not plant. A fixed 64 samples is ~23 px apart on a hamlet
    # fan, which was enough to put a new basin's bund in the collector on 4 of 24 cohort seeds. One
    # sample every 6 px is finer than the drain's own jitter, and the whole band costs one polyline
    # scan per sample.
    _n_u = max(64, int((uhi - ulo) / 6.0))
    us = [ulo + (uhi - ulo) * k / _n_u for k in range(_n_u + 1)]
    dus = [F.to_uf(*p)[0] for p in dpts]
    du_lo, du_hi = min(dus), max(dus)

    def drain_f(u: float) -> float:
        fd = _f_at_u(F, dpts, u)
        if fd is not None:
            return fd
        end = dpts[0] if abs(u - du_lo) < abs(u - du_hi) else dpts[-1]
        return F.to_uf(*end)[1]

    def canal_f(u: float) -> float:
        fc = _f_at_u(F, a_pts, u)
        return flo - span if fc is None else fc + 4 * g

    # The low bound is the collector's BANK IN FALL - `_drain_bank`, the very function `_carve`
    # hems its closing rank onto - not a flat margin. `_fill_wedges` used a flat 3 * grain, which
    # is neither: too much where the collector is narrow (it left the last residue of doubled bunds
    # along the fan's toe, wedges this pass was forbidden to reach) and too little downstream,
    # where the drain widens to DRAIN_FT[1] and `paddy_bunds_clear_the_collector` measures a
    # slope-leaned set-back that a flat margin does not cover. Same predicate as the placer, so
    # ground this pass plants is ground the carve would have been allowed to plant.
    below = _band(F, us, [drain_f(u) - bank(u) for u in us], fhi + span)
    above = _band(F, us, [canal_f(u) for u in us], flo - span)
    return unary_union([below, above])
