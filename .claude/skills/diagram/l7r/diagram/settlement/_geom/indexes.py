"""Prefilters and spatial indexes: how a per-candidate scan of static geometry stops being the
whole runtime of a gen.

PREFILTER FAMILY, all of it - the box or the grid PRUNES, the caller's exact test still DECIDES,
so a verdict is identical to a linear scan's and the pool regenerates byte-identical when a
caller switches over. That property is what separates indexing from coarsening, which this engine
does not do (skill CLAUDE.md, 'When a check is slow, INDEX it - do not coarsen it').

Split from settlement/_geom.py by feature 117 - see settlement/_geom/CLAUDE.md for the index.
"""

from collections.abc import Callable
from typing import Any, SupportsIndex, cast

from .base import Poly, Pt
from .primitives import edge_dist, point_in_poly, seg_dist, segments_cross


def boxed_polys(polys: Any, pad: float = 0.0) -> list[tuple[Poly, float, float, float, float]]:
    """Each polygon paired with its bounding box, expanded by `pad`, computed ONCE. Feed the result
    to `boxed_hit` - which is where the why is written down."""
    out: list[tuple[Poly, float, float, float, float]] = []
    for poly in polys:
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        out.append((poly, min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad))
    return out


def boxed_hit(px: float, py: float, boxed: Any, edge_pad: float = 0.0) -> bool:
    """Is (px, py) inside any pre-boxed polygon - or within `edge_pad` of one's edge?

    PREFILTER family (this skill's CLAUDE.md, "Centers, footprints, and aggregates"): the bbox
    PRUNES, the exact `point_in_poly` / `edge_dist` still DECIDES. The verdict is therefore
    identical to a bare scan, which is what lets the whole pool regenerate byte-identical when a
    caller switches over - and is why this is a prefilter rather than the forbidden "coarsen it"
    (CLAUDE.md, "When a check is slow, INDEX it - do not coarsen it").

    WHY IT EXISTS: the ground-cover scatters test every field poly, block poly and clearing PER
    SCATTER POINT, and a marshy village pushes hundreds of thousands of points through them -
    Kikuta burned 24.6M `point_in_poly` calls, 93% of its whole gen (profiled 2026-08-03). The
    PLACEMENT path had had this treatment for months (`_in_blocked`, via `_poly_bboxes`); the
    scatter path never got it. Build the boxes with the SAME pad you pass as `edge_pad`, or the
    prefilter can reject a point the edge test would have wanted."""
    return any(bx0 <= px <= bx1 and by0 <= py <= by1 and (point_in_poly(px, py, poly) or (edge_pad > 0 and edge_dist(px, py, poly) < edge_pad)) for poly, bx0, by0, bx1, by1 in boxed)


def boxed_segs(corridors: Any) -> list[tuple[Pt, Pt, float, float, float, float, float]]:
    """Every corridor segment with its clearance-expanded bbox, flattened and computed ONCE - the
    polyline companion of `boxed_polys`. Feed to `boxed_seg_hit`."""
    out: list[tuple[Pt, Pt, float, float, float, float, float]] = []
    for pl, hw in corridors:
        for i in range(len(pl) - 1):
            a, b = pl[i], pl[i + 1]
            out.append((a, b, hw, min(a[0], b[0]) - hw, min(a[1], b[1]) - hw, max(a[0], b[0]) + hw, max(a[1], b[1]) + hw))
    return out


def boxed_seg_hit(px: float, py: float, segs: Any) -> bool:
    """Is (px, py) within its clearance of any pre-boxed corridor segment? Prefilter family exactly
    as `boxed_hit` - and the same shape `_near_corridor` already uses on the placement side."""
    return any(bx0 <= px <= bx1 and by0 <= py <= by1 and seg_dist(px, py, a, b) < hw for a, b, hw, bx0, by0, bx1, by1 in segs)


class Indexed(list):  # type: ignore[type-arg]
    """A no-build registry that carries a VERSION, so an index built from it can be invalidated by
    the data itself rather than by a guess about the data.

    WHY NOT A CACHE KEY. Two attempts in this engine at "is my cached index still valid?" failed,
    both SILENTLY, both on 2026-08-03: an incremental index over `placed` missed the two sites that
    REBIND it to a filtered copy (Minami and Nagahara lost every garden), and a record-count
    fingerprint for the well grids missed an in-place replacement of a same-LENGTH ring (a wellhead
    cleared to stand in a paddy). Length, object identity and record counts are all guesses about
    CONTENT. A version the list bumps itself is not a guess - mutating is the only way content
    changes, and every mutator bumps.

    The cache lives on the list too (`cache`), keyed by consumer, so an index physically cannot be
    read against a different list than it was built from. That covers the one non-append pattern in
    the engine: `farm_wells` swaps `field_polys` for an empty list and swaps the ORIGINAL OBJECT
    back, which an identity- or length-keyed cache gets wrong and this cannot.

    `test_indexed_overrides_every_mutating_list_method` is the ratchet: it enumerates `list`'s
    mutators by introspection and fails if one is not overridden here, so a Python version adding a
    mutating method cannot open a silent staleness hole."""

    __slots__ = ("appends", "cache", "version")

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.version = 0
        self.appends = 0  # bumped ONLY by append/extend - see indexed_grid for why that distinction pays
        self.cache: dict[str, tuple[int, int, int, Any]] = {}

    def _bump(self) -> None:
        self.version += 1

    def append(self, item: Any) -> None:
        self.appends += 1
        self._bump()
        super().append(item)

    def extend(self, items: Any) -> None:
        self.appends += 1
        self._bump()
        super().extend(items)

    def insert(self, i: SupportsIndex, item: Any) -> None:
        self._bump()
        super().insert(i, item)

    def remove(self, item: Any) -> None:
        self._bump()
        super().remove(item)

    def pop(self, i: SupportsIndex = -1) -> Any:
        self._bump()
        return super().pop(i)

    def clear(self) -> None:
        self._bump()
        super().clear()

    def sort(self, **kw: Any) -> None:
        self._bump()
        super().sort(**kw)

    def reverse(self) -> None:
        self._bump()
        super().reverse()

    def __setitem__(self, i: Any, v: Any) -> None:
        self._bump()
        super().__setitem__(i, v)

    def __delitem__(self, i: Any) -> None:
        self._bump()
        super().__delitem__(i)

    def __iadd__(self, other: Any) -> Any:  # type: ignore[misc]  # same as __imul__ below: mypy checks this against list.__add__, which an in-place op on a subclass cannot satisfy; the override exists so `reg += xs` bumps the version
        self._bump()
        return super().__iadd__(other)

    def __imul__(self, n: Any) -> Any:  # type: ignore[misc]  # mypy compares __imul__ against list.__mul__, which cannot hold for an in-place op on a subclass; the override exists so `reg *= n` still bumps the version rather than silently invalidating an index
        self._bump()
        return super().__imul__(n)


def indexed_grid(lst: Any, key: str, build: Callable[[Any], PointGrid], add: Callable[[PointGrid, Any], None] | None = None) -> PointGrid:
    """The PointGrid `build` makes from `lst`, cached ON `lst` under `key` until `lst` mutates.

    A plain list (one a caller rebound out from under us) is handled by simply building fresh every
    time: slower, never wrong. That fallback is the whole reason this is safe to use on registries
    whose mutation pattern might change later."""
    if not isinstance(lst, Indexed):
        return build(lst)
    hit = lst.cache.get(key)
    if hit is not None:
        version, appends, count, grid = hit
        if version == lst.version:
            return cast(PointGrid, grid)
        # EVERY change since was an append (the version moved exactly as far as the append counter),
        # so the index is not stale - it is merely SHORT, and appending to a grid is exact. This is
        # what keeps an accreting registry cheap: `placed` grows ~1,000 times per city map with
        # queries interleaved, and rebuilding all of it per append would cost more than the scan
        # being replaced.
        if add is not None and lst.version - version == lst.appends - appends:
            add(cast(PointGrid, grid), lst[count:])
            lst.cache[key] = (lst.version, lst.appends, len(lst), grid)
            return cast(PointGrid, grid)
    fresh = build(lst)
    lst.cache[key] = (lst.version, lst.appends, len(lst), fresh)
    return fresh


def boxed_circles(circles: Any) -> list[tuple[float, float, float, float, float, float, float]]:
    """Each `(cx, cy, r)` circle with its bounding box, in the `(payload..., x0, y0, x1, y1)` shape
    `PointGrid` files (feature 218). A point inside the circle is inside the box, so a zero-pad
    query is exact - the occupancy keep-outs of a grove, the wellhead aprons of a scatter."""
    return [(cx, cy, r, cx - r, cy - r, cx + r, cy + r) for cx, cy, r in circles]


def circle_hit(px: float, py: float, near: Any) -> bool:
    """Is (px, py) STRICTLY inside any circle `near` returns? The expression a grove's keep-out ran
    (`< rr * rr`), so the verdict is bit-identical to its linear scan. A scatter's CLOSED halo test
    lives in `KeepoutGrid`, which files every family of one scatter together."""
    return any((px - cx) ** 2 + (py - cy) ** 2 < r * r for cx, cy, r, _x0, _y0, _x1, _y1 in near)


def boxed_rects(rects: Any) -> list[tuple[float, float, float, float, float, float, float, float]]:
    """Each `(x0, y0, x1, y1)` rectangle with itself as its box - the payload IS the extent."""
    return [(x0, y0, x1, y1, x0, y0, x1, y1) for x0, y0, x1, y1 in rects]


def rect_hit(px: float, py: float, near: Any) -> bool:
    """Is (px, py) STRICTLY inside any rectangle `near` returns - a grove's sun corridors and light
    lanes, written `a < q < b`? A scatter's closed halo test lives in `KeepoutGrid`."""
    return any(x0 < px < x1 and y0 < py < y1 for x0, y0, x1, y1, _bx0, _by0, _bx1, _by1 in near)


def boxed_grid(boxed: Any) -> PointGrid:
    """A PointGrid over already-boxed items, for a caller that builds its keep-outs ONCE per region
    and then queries them per scatter point. `boxed_hit`/`boxed_seg_hit` accept the narrowed list
    `near` returns, so switching a linear prefilter to an index is a two-line change at the call
    site and the exact tests underneath are untouched."""
    grid = PointGrid()
    grid.extend(boxed)
    return grid


class PointGrid:
    """A uniform-grid spatial index for POINT queries against many static extents.

    PREFILTER family, like `boxed_hit` one level up: the grid narrows the CANDIDATE LIST, the
    caller's exact test still DECIDES, so verdicts match a linear scan exactly - which is what lets
    the pool regenerate byte-identical when a caller switches over.

    WHY IT EXISTS. A bbox prefilter drops the cost per item but still visits EVERY item, and some
    of this engine's per-candidate scans are long: Minami's well siting probes ~133k seats against
    ~580 watercourse segments plus 927 paddy rings (~123M box comparisons, 74% of that gen), and
    `_fits` measures every candidate against every building already standing. `check_village.py`
    solved exactly this on the CHECKING side with `GridIndex` (whole-pool gate 34.1s -> 11.8s); the
    GENERATOR side had no equivalent until 2026-08-03.

    Items are `(payload..., x0, y0, x1, y1)` - the box is the LAST FOUR fields, the shape
    `boxed_polys` and `boxed_segs` already produce. Filing is INCREMENTAL (`extend` appends), which
    is exact for an append-only registry like `Settlement.placed`, so a growing list is indexed as
    it grows instead of rebuilt.

    A GRID BOX IS A COST, SO IT IS CLAMPED - the lesson recorded in this skill's CLAUDE.md, learned
    when a negative fixture's 9,000,000px vertex asked the checker's index for ~5.6 billion cells
    and the gate ate gigabytes. An item spanning more than `_MAX_SPAN` cells on either axis is
    filed as OVERSIZED and returned by every query. That makes a wild coordinate cheap rather than
    unbounded, and it cannot change a verdict: an oversized item is simply never pruned."""

    __slots__ = ("buckets", "cell", "n", "oversized")
    _MAX_SPAN = 64  # cells per axis before an item is oversized (64 * 128px = 8,192px - wider than any canvas we draw)

    def __init__(self, cell: float = 128.0) -> None:
        self.cell = cell
        self.buckets: dict[tuple[int, int], list[Any]] = {}
        self.oversized: list[Any] = []
        self.n = 0  # items filed so far - an append-only source hands in only the tail

    def extend(self, items: Any) -> None:
        c = self.cell
        for item in items:
            self.n += 1
            i0, j0 = int(item[-4] // c), int(item[-3] // c)
            i1, j1 = int(item[-2] // c), int(item[-1] // c)
            if i1 - i0 > self._MAX_SPAN or j1 - j0 > self._MAX_SPAN:
                self.oversized.append(item)
                continue
            for i in range(i0, i1 + 1):
                for j in range(j0, j1 + 1):
                    self.buckets.setdefault((i, j), []).append(item)

    def near(self, px: float, py: float, pad: float = 0.0) -> Any:
        """Every filed item whose box comes within `pad` of (px, py) - plus, harmlessly, some that
        do not, and possibly the same item twice (an item spanning several queried cells). It never
        OMITS one that does, which is the only property the callers' exactness rests on."""
        c = self.cell
        i0, j0 = int((px - pad) // c), int((py - pad) // c)
        i1, j1 = int((px + pad) // c), int((py + pad) // c)
        if i0 == i1 and j0 == j1 and not self.oversized:  # the common case - one cell, no copy
            return self.buckets.get((i0, j0)) or ()
        out: list[Any] = list(self.oversized)
        for i in range(i0, i1 + 1):
            for j in range(j0, j1 + 1):
                bucket = self.buckets.get((i, j))
                if bucket:
                    out.extend(bucket)
        return out


class RingIndex:
    """Point queries against ONE static ring - inside/outside and distance-to-edge - built once.

    WHY IT EXISTS (feature 145, GM 2026-08-28: *"What are we doing billions of computations on
    exactly?"*). The ground-cover scatters (`commons`, `marsh`) throw ~100k+ candidate points per
    hamlet and asked the outline two questions per point, each by walking EVERY edge: `point_in_poly`
    and `edge_dist` - 1.3M ray tests and 156k full-ring distance scans on the reference, ~60M segment
    operations, 13 of the stage's 20 profiled seconds, to place grass. Both answers only ever depend
    on the few edges near the point, so the edges are filed in a `PointGrid` once per ring and each
    query touches its own cell. Exact, like every index here: `inside` counts the same crossings
    against the same edges (only the edges whose y-span can contain the ray are visited, which is
    every edge the crossing formula could count), and `edge_within` returns the true distance when it
    is under the limit and None when it is not - the callers only use the distance INSIDE a feather
    band, so a point farther than the band from every edge needs no number at all. Verdicts match
    the linear scan; a map that moves under this index moved for another reason."""

    __slots__ = ("cell", "grid", "ring", "rows", "x0", "x1", "y0", "y1")

    def __init__(self, ring: Any, cell: float = 64.0) -> None:
        self.ring: Poly = [(float(p[0]), float(p[1])) for p in ring]
        self.cell = cell
        n = len(self.ring)
        edges = []
        self.rows: dict[int, list[tuple[float, float, float, float]]] = {}
        for i in range(n):
            (xi, yi), (xj, yj) = self.ring[i], self.ring[(i + 1) % n]
            edges.append(((xi, yi), (xj, yj), min(xi, xj), min(yi, yj), max(xi, xj), max(yi, yj)))
            # the ray test's own condition is `(yi > py) != (yj > py)`, so an edge can only count for
            # the rows its y-span covers; file it there and the crossing count is exact per row
            for r in range(int(min(yi, yj) // cell), int(max(yi, yj) // cell) + 1):
                self.rows.setdefault(r, []).append((xi, yi, xj, yj))
        self.grid = PointGrid(cell)
        self.grid.extend(edges)
        xs = [p[0] for p in self.ring]
        ys = [p[1] for p in self.ring]
        self.x0, self.x1, self.y0, self.y1 = min(xs), max(xs), min(ys), max(ys)

    def inside(self, px: float, py: float) -> bool:
        """`point_in_poly`, restricted to the edges whose y-span can cross the ray."""
        if not (self.x0 <= px <= self.x1 and self.y0 <= py <= self.y1):
            return False
        inside = False
        for xi, yi, xj, yj in self.rows.get(int(py // self.cell), ()):
            if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi + 1e-9) + xi):
                inside = not inside
        return inside

    def edge_within(self, px: float, py: float, limit: float) -> float | None:
        """The distance from (px, py) to the nearest edge if it is under `limit`, else None."""
        best = limit
        for a, b, bx0, by0, bx1, by1 in self.grid.near(px, py, limit):
            if bx0 - limit <= px <= bx1 + limit and by0 - limit <= py <= by1 + limit:
                d = seg_dist(px, py, a, b)
                if d < best:
                    best = d
        return best if best < limit else None


class KeepoutGrid:
    """EVERY static keep-out of one scatter in ONE grid, so a scatter point asks its cell ONCE
    (feature 218, GM 2026-09-08: *"something much, much simpler ... which would take a fraction of a
    second rather than the many seconds that we are spending now"*).

    The ground-cover scatters had indexed each keep-out family on its own since feature 145 - the
    crop rings, the corridors, the water, the halo rects and circles, the building footprints, the
    clearings, the avoid polygons, and for a marsh the mound crests and the pond banks - and asked
    every one of those grids per point: on the reference roll's 134,877 commons points that was
    1.33 million `near` calls and ten wrapper calls per point, most returning an empty cell. Filing
    every family in one grid turns that into one cell read and one loop over what the cell holds.

    The verdict is the linear scan's, item by item: a RING answers `inside or (pad > 0 and
    edge_within(pad))`, a SEG `seg_dist < reach`, a RECT and a CIRCLE the strict or closed test their
    caller wrote. A family whose pad or reach varies PER QUERY (the crop margin plus a glyph's lean;
    a marsh mark's mound pad) files its BASE and a `slot`, and `hit` takes the extras as a tuple
    indexed by slot - `None` in a slot skips that family for this query, which is how a marsh mark
    whose pad has no mound grid stays exempt from the mounds exactly as before. Boxes carry the base
    pad plus `reach`, the widest extra a query may add, so the prefilter never rejects an item the
    exact test would have refused on (`boxed_hit`'s contract). Filing order does not matter: every
    test is a pure predicate with no randomness, so `any` of them is the same in any order."""

    __slots__ = ("grid",)
    RING, SEG, RECT, CIRCLE = 0, 1, 2, 3

    def __init__(self) -> None:
        self.grid = PointGrid()

    def rings(self, polys: Any, pad: float = 0.0, slot: int = 0, reach: float = 0.0) -> None:
        """Rings refused inside or within `pad` (+ the query's extra for `slot`) of an edge."""
        items = []
        for poly in polys:
            idx = RingIndex(poly)
            r = pad + reach
            items.append((self.RING, idx, pad, slot, idx.x0 - r, idx.y0 - r, idx.x1 + r, idx.y1 + r))
        self.grid.extend(items)

    def segs(self, corridors: Any, slot: int = 0, reach: float = 0.0) -> None:
        """`(polyline, half-width)` pairs refused within the half-width (+ the query's extra)."""
        items = []
        for pl, hw in corridors:
            for i in range(len(pl) - 1):
                a, b = pl[i], pl[i + 1]
                r = hw + reach
                items.append((self.SEG, a, b, hw, slot, min(a[0], b[0]) - r, min(a[1], b[1]) - r, max(a[0], b[0]) + r, max(a[1], b[1]) + r))
        self.grid.extend(items)

    def rects(self, rects: Any, closed: bool = False) -> None:
        self.grid.extend([(self.RECT, x0, y0, x1, y1, closed, x0, y0, x1, y1) for x0, y0, x1, y1 in rects])

    def circles(self, circles: Any, closed: bool = False) -> None:
        self.grid.extend([(self.CIRCLE, cx, cy, r, closed, cx - r, cy - r, cx + r, cy + r) for cx, cy, r in circles])

    def hit(self, px: float, py: float, extra: tuple[float | None, ...] = (0.0,)) -> bool:
        """Is (px, py) refused by any keep-out its cell holds? `extra[slot]` widens a family's pad for
        this query; `None` there skips the family."""
        for item in self.grid.near(px, py):
            kind = item[0]
            if kind == 0:
                _k, idx, pad, slot, bx0, by0, bx1, by1 = item
                ex = extra[slot]
                if ex is None:
                    continue
                pad += ex
                if bx0 <= px <= bx1 and by0 <= py <= by1 and (idx.inside(px, py) or (pad > 0 and idx.edge_within(px, py, pad) is not None)):
                    return True
            elif kind == 1:
                _k, a, b, hw, slot, bx0, by0, bx1, by1 = item
                ex = extra[slot]
                if ex is None:
                    continue
                if bx0 <= px <= bx1 and by0 <= py <= by1 and seg_dist(px, py, a, b) < hw + ex:
                    return True
            elif kind == 2:
                _k, x0, y0, x1, y1, closed, _bx0, _by0, _bx1, _by1 = item
                if (x0 <= px <= x1 and y0 <= py <= y1) if closed else (x0 < px < x1 and y0 < py < y1):
                    return True
            else:
                _k, cx, cy, r, closed, _bx0, _by0, _bx1, _by1 = item
                d2 = (px - cx) ** 2 + (py - cy) ** 2
                if (d2 <= r * r) if closed else (d2 < r * r):
                    return True
        return False


def boxed_rings(polys: Any, pad: float = 0.0) -> list[tuple[RingIndex, float, float, float, float]]:
    """`boxed_polys` with each ring INDEXED (feature 145): the same `(payload, x0, y0, x1, y1)` shape
    `boxed_grid` files, but the payload is a `RingIndex`, so `boxed_ring_hit` answers the inside
    and edge-margin questions from the edges near the point instead of walking every vertex. The
    scatters' crop-margin test was the last whole-ring scan per candidate: `boxed_hit(..., edge_pad)`
    ran `edge_dist` over the full paddy ring for every point whose box it could not reject - 18k
    calls, 2.4 of the hinterland stage's 10 profiled seconds after the outline itself was indexed."""
    out: list[tuple[RingIndex, float, float, float, float]] = []
    for poly in polys:
        idx = RingIndex(poly)
        out.append((idx, idx.x0 - pad, idx.y0 - pad, idx.x1 + pad, idx.y1 + pad))
    return out


def boxed_ring_hit(px: float, py: float, boxed: Any, edge_pad: float = 0.0) -> bool:
    """`boxed_hit` over `boxed_rings` items - identical verdicts, indexed edges."""
    return any(bx0 <= px <= bx1 and by0 <= py <= by1 and (idx.inside(px, py) or (edge_pad > 0 and idx.edge_within(px, py, edge_pad) is not None)) for idx, bx0, by0, bx1, by1 in boxed)


def box_clear_brute(bx0: float, by0: float, bx1: float, by1: float, rects: Any, polys: Any, lines: Any) -> bool:
    """Whether the axis-aligned box clears every obstacle in (rects, polys, lines) - the linear scan that
    `Settlement._box_clear` was until feature 222, kept as the ORACLE for `BoxObstacles`' tests: every
    rect, every polygon (a box corner inside it, a vertex inside the box, or an edge crossing the box's
    edge), every polyline (a vertex inside the box or a segment crossing its edge)."""
    for ox0, oy0, ox1, oy1 in rects:
        if not (bx1 < ox0 or bx0 > ox1 or by1 < oy0 or by0 > oy1):
            return False
    corners = [(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)]
    for poly in polys:
        n = len(poly)
        if (
            any(point_in_poly(cx, cy, poly) for cx, cy in corners)
            or any(bx0 <= vx <= bx1 and by0 <= vy <= by1 for vx, vy in poly)
            or any(segments_cross(corners[e], corners[(e + 1) % 4], poly[k], poly[(k + 1) % n]) for e in range(4) for k in range(n))
        ):
            return False
    for poly in lines:
        if any(bx0 <= vx <= bx1 and by0 <= vy <= by1 for vx, vy in poly) or any(segments_cross(corners[e], corners[(e + 1) % 4], poly[k], poly[k + 1]) for e in range(4) for k in range(len(poly) - 1)):
            return False
    return True


class BoxObstacles:
    """Axis-aligned BOX queries against static obstacles - rects, polygons, polylines - built once (feature
    222, GM 2026-09-11: "the title pocket scan index"). The title's blank-box scan (`Settlement._blank_label_spot`)
    tried every 24 px box of the framed window, top to bottom, against every edge of every obstacle by
    `segments_cross`: on Kuwabata, whose obstacle list is every dike pond and every ditch, 4,027 boxes cost
    16.4 million segment pairs and 8.7 of the hinterland stage's 10 s (specs/222 research R1). The same
    PREFILTER family as everything else here: every polygon and polyline edge is filed in a `PointGrid`
    once, each polygon keeps its bounding box, and a query visits only the obstacles whose box meets the
    candidate and the edges the grid returns near it - by the same three tests `box_clear_brute` makes.
    The index prunes, the exact test decides, so every verdict is the linear scan's and no map moves.

    Exactness, test by test: a box corner inside a polygon lies inside that polygon's bounding box, so a
    polygon whose box misses the candidate cannot contain a corner; every vertex is an endpoint of an edge
    whose bounding box therefore meets any box containing the vertex, so the endpoint test over the grid's
    near edges finds every vertex the brute scan finds; and an edge crossing the box's edge meets the
    box, so its own bounding box does too. The grid returns a superset (and sometimes an item twice), which
    changes nothing an `any` can see."""

    __slots__ = ("grid", "polys", "rects")

    def __init__(self, rects: Any, polys: Any, lines: Any, cell: float = 128.0) -> None:
        self.rects = [(float(r[0]), float(r[1]), float(r[2]), float(r[3])) for r in rects]
        self.polys: list[tuple[Poly, float, float, float, float]] = []
        edges: list[tuple[Pt, Pt, float, float, float, float]] = []
        for poly in polys:
            ring = [(float(p[0]), float(p[1])) for p in poly]
            if not ring:
                continue
            xs = [p[0] for p in ring]
            ys = [p[1] for p in ring]
            self.polys.append((ring, min(xs), min(ys), max(xs), max(ys)))
            n = len(ring)
            for k in range(n):
                a, b = ring[k], ring[(k + 1) % n]
                edges.append((a, b, min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])))
        for line in lines:
            pts = [(float(p[0]), float(p[1])) for p in line]
            for k in range(len(pts) - 1):
                a, b = pts[k], pts[k + 1]
                edges.append((a, b, min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])))
        self.grid = PointGrid(cell)
        self.grid.extend(edges)

    def clear(self, bx0: float, by0: float, bx1: float, by1: float) -> bool:
        """`box_clear_brute` over the same obstacles, visiting only the ones that can matter."""
        for ox0, oy0, ox1, oy1 in self.rects:
            if not (bx1 < ox0 or bx0 > ox1 or by1 < oy0 or by0 > oy1):
                return False
        corners = [(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)]
        for ring, px0, py0, px1, py1 in self.polys:
            if px1 < bx0 or px0 > bx1 or py1 < by0 or py0 > by1:
                continue  # a corner inside the polygon would be inside its box
            if any(point_in_poly(cx, cy, ring) for cx, cy in corners):
                return False
        pad = max(bx1 - bx0, by1 - by0) / 2.0
        for a, b, ex0, ey0, ex1, ey1 in self.grid.near((bx0 + bx1) / 2.0, (by0 + by1) / 2.0, pad):
            if ex1 < bx0 or ex0 > bx1 or ey1 < by0 or ey0 > by1:
                continue  # neither endpoint in the box, no crossing possible
            if (bx0 <= a[0] <= bx1 and by0 <= a[1] <= by1) or (bx0 <= b[0] <= bx1 and by0 <= b[1] <= by1):
                return False
            if any(segments_cross(corners[e], corners[(e + 1) % 4], a, b) for e in range(4)):
                return False
        return True
