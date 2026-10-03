"""THE SITE BOUNDARY (feature 226, GM 2026-09-12): the ground a homestead may stand on, computed ONCE.

The GM, after the per-house profile of the homesteads stage: *"Why not draw a section of cords which literally
separate the area in which we are placing our homesteads from literally everything? ... then you just have a few,
which is to say a relatively small number of line segments that you were checking."* At the moment the homesteads
are seated everything the map holds is fixed and everything placed later is placed around the houses, so the fit
test's five ground scans - the no-build polygons (every hem plot, a mosaic's ponds), the paddy's chords, the water
courses, the hard ground (every plot again, every marsh, every ditch segment as a quad) and the keep-out
ellipses, each walked per rectangle per candidate - collapse into two outlines asked two ways: the paddy's facing chains (feature 140's, asked by side, as
today) and ONE union outline of everything else - the hem, the marshes, the ponds, the no-build ground - with its
holes, asked by containment as today's overlap tests ask; plus the water courses and the registered corridors as a
few segments each with the clearance its own test applied. A candidate then asks its corners of ten to thirty chords and a few dozen
corridor segments. Every member enters at the pad its retired test held it to - zero on the bundle path - so no
placement rule moves here (spec D2); the house's own wall rule (`_wall_on_the_bund`) stays its own test.

Measured before (specs/226 research R1): 1,090-2,755 rectangles per house each walked ~150-200 polygons by
bounding box; 7,778-13,075 chord tests and 66,000-99,000 segment distances per house.

Research: site boundary - NONE: the ground tests indexed once, every member at the pad its own test held it to; no placement rule moves here
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # shapely's names for the type checker; `_load_shapely` binds the runtime ones
    from shapely.geometry import LineString, Polygon
    from shapely.ops import unary_union

from l7r.diagram.settlement._geom.indexes import PointGrid, RingIndex
from l7r.diagram.settlement._geom.primitives import FIELD_KEEPOUT_EPS, facing_chains, seg_dist
from l7r.diagram.settlement.land.wet import marsh_ground
from l7r.diagram.sitegen.geom import crop_polys

from ..consts import WEB_HARD_GAP, WEB_REACH_FT

if TYPE_CHECKING:
    from l7r.diagram.settlement import Settlement

    from ..plan import SitePlan

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
    """
    global _SHAPELY_LOADED, LineString, Polygon, unary_union  # binding this module's own names is the point
    if _SHAPELY_LOADED:
        return
    from shapely.geometry import LineString, Polygon
    from shapely.ops import unary_union

    _SHAPELY_LOADED = True


#: a keep-out ellipse becomes this many-sided polygon in the union; 24 keeps a pond's outline within ~1% of its radius
ELLIPSE_SIDES = 24
#: a blob member under this area (px^2) is noise from a degenerate quad and is dropped
MIN_MEMBER_AREA = 1.0
#: `_hard_clear` inflated the RECTANGLE to the swept extent of the farmhouse's +/-5 degree tilt before testing it; the
#: hard ground's members are grown by this instead - the house footprint's long side, 46 ft x sin 5 deg, halved, at
#: 1 ft/px - so the blob refuses what `_hard_clear` refused within a pixel for every rectangle (spec FR-001, D2)
TILT_ALLOWANCE_PX = 2.0


def _ellipse_poly(cx: float, cy: float, rx: float, ry: float) -> list[tuple[float, float]]:
    return [(cx + rx * math.cos(2 * math.pi * k / ELLIPSE_SIDES), cy + ry * math.sin(2 * math.pi * k / ELLIPSE_SIDES)) for k in range(ELLIPSE_SIDES)]


Seg = tuple[tuple[float, float], tuple[float, float], float]


def _prepare(geom: Any) -> None:
    import shapely

    shapely.prepare(geom)


def site_boundary(s: Settlement, seat: tuple[float, float]) -> tuple[list[list[Any]], tuple[list[Seg], list[Seg]], tuple[list[list[tuple[float, float]]], list[list[tuple[float, float]]]]]:
    """`(chains, (water, registered), (rings, holes))` for the homestead stage, from every geometry the bundle's fit test reads
    (spec FR-001): the area members unioned and reduced to the chains facing `seat`; the water obstacles and the
    registered corridors as two sets of `(a, b, clearance)` segments, each asked the way its own test asks today."""
    _load_shapely()

    def member(poly: Any, grow: float = 0.0) -> Polygon | None:
        if len(poly) < 3:
            return None
        q = Polygon([(float(v[0]), float(v[1])) for v in poly])
        if not q.is_valid:
            q = q.buffer(0)
        if grow:
            q = q.buffer(grow)
        return q if q.area >= MIN_MEMBER_AREA else None

    # TWO OUTLINES, NOT ONE, because they are asked two different questions (spec FR-002 and the first two cuts):
    #   - the FIELD polygons become facing chains, asked by SIDE (`chain_violated`), exactly as `_field_blocks_rect` asks
    #     today: the ground behind the paddy from the seat's view is refused, as it always was;
    #   - everything else - the no-build polygons, the hard ground's polygons (grown by the tilt allowance), the ellipses -
    #     is unioned into ONE outline with holes and asked by CONTAINMENT, exactly as `_rect_hits`, `_hard_clear` and the
    #     ellipses loop ask today: the ground between two ponds of a dike mosaic, or in a pocket among the hem's plots, is
    #     still buildable. A first cut put the paddy and everything else into one facing blob, and the mosaic's far chords
    #     refused the ground behind them: Kuwabata seated 11 of 16 households.
    chains: list[list[Any]] = []
    for poly in s.field_polys:
        if len(poly) >= 4:
            chains += facing_chains([(float(v[0]), float(v[1])) for v in poly], seat, FIELD_KEEPOUT_EPS)
    members: list[Polygon] = []
    for poly in s.block_polys:
        q = member(poly)
        if q is not None:
            members.append(q)
    hard_area = (
        [list(s.hard_polys)[i] for i in range(len(s.hard_polys))]
        + [list(wp) for wp in s.wet_polys if len(wp) >= 3]
        + [[(v[0], v[1]) for v in d["poly"]] for d in (s.M.get("dry_plots", []) or []) if d.get("poly") and len(d["poly"]) >= 3]
    )  # (the reed-marsh toe is among `hard_polys` by the time this runs - `install_site_boundary` registers it)
    for poly in hard_area:
        q = member(poly, TILT_ALLOWANCE_PX * s.bscale)
        if q is not None:
            members.append(q)
    for cx, cy, rx, ry in s.ellipses:
        if rx > 0 and ry > 0:
            members.append(Polygon(_ellipse_poly(float(cx), float(cy), float(rx), float(ry))))
    blob = unary_union(members) if members else None
    rings: list[list[tuple[float, float]]] = []  # each (exterior, holes) flattened: the exterior ring, then its holes, tagged below
    holes: list[list[tuple[float, float]]] = []
    if blob is not None and not blob.is_empty:
        parts = [g for g in (list(blob.geoms) if hasattr(blob, "geoms") else [blob]) if isinstance(g, Polygon)]
        for part in parts:
            rings.append([(float(x), float(y)) for x, y in part.exterior.coords[:-1]])
            for hole in part.interiors:
                holes.append([(float(x), float(y)) for x, y in hole.coords[:-1]])
    # THE LINE MEMBERS, two sets with the points and clearance their tests apply today (spec FR-001): the water obstacles at
    # half-width + 5, asked at the rectangle's corners and center (`_rect_on_water`); the registered corridors at their
    # registered clearance, asked at the center only (`_near_corridor` - a footprint test of that clearance was tried and
    # reverted). A segment the blob covers at its clearance refuses nothing the chains do not, and is dropped.
    water: list[tuple[tuple[float, float], tuple[float, float], float]] = []
    registered: list[tuple[tuple[float, float], tuple[float, float], float]] = []
    # a segment the CULTIVATED ground covers - the field's polygons and the others' outline together - refuses nothing the
    # chains and the outline do not: the ditches inside the paddy lie behind its chains, and dropping them is what keeps
    # this set a few dozen segments rather than a hundred
    fields = [Polygon([(float(v[0]), float(v[1])) for v in poly]) for poly in s.field_polys if len(poly) >= 3]
    fields = [f if f.is_valid else f.buffer(0) for f in fields]
    covered = unary_union([*fields, *([blob] if blob is not None and not blob.is_empty else [])]) if fields or (blob is not None and not blob.is_empty) else None
    # the cultivated ground grown by a clearance is built ONCE per clearance, prepared, and asked of every segment kept at
    # it (seed 44: 6,702 buffers of the whole union, one per segment, for a handful of clearances)
    grown: dict[float, Any] = {}
    for dest, courses in ((water, [(poly, float(hw)) for poly, hw, _bbox in s._water_obstacles()]), (registered, [(pts, float(clr)) for pts, clr, *_ in s.corridors if len(pts) >= 2])):
        for pts, clr in courses:
            for k in range(len(pts) - 1):
                a, b = (float(pts[k][0]), float(pts[k][1])), (float(pts[k + 1][0]), float(pts[k + 1][1]))
                if covered is not None:
                    if clr not in grown:
                        grown[clr] = covered.buffer(clr)
                        _prepare(grown[clr])
                    if grown[clr].covers(LineString([a, b])):
                        continue
                dest.append((a, b, clr))
    corridors = (water, registered)
    return chains, corridors, (rings, holes)


class SiteCorridors:
    """The two corridor sets in `PointGrid`s by their clearance-inflated boxes, and the OTHERS' outline as rings with
    holes by their boxes. `hit_points` asks the WATER set at every point handed in (a rectangle's corners and
    center, as `_rect_on_water`) and the rings by containment - a point inside an exterior ring and inside none of
    its holes, or a ring vertex inside the rectangle (the `_rect_hits` arms); `hit_center` asks the REGISTERED set
    at one point (the center, as `_near_corridor`)."""

    __slots__ = ("center", "full", "hole_grid", "holes", "rings", "ring_pts", "water")

    def __init__(self, corridors: tuple[list[Seg], list[Seg]], outline: tuple[list[list[tuple[float, float]]], list[list[tuple[float, float]]]] | None = None, cell: float = 128.0) -> None:
        self.ring_pts: list[list[tuple[float, float]]] = [list(r) for r in (outline[0] if outline else [])]  # the rings as points, for the front row's ground push (feature 227)
        water, registered = corridors
        self.water = list(water)  # the water courses as segments with their clearance, for the front row's push across a brook (feature 261)
        rings, holes = outline if outline is not None else ([], [])
        self.full = PointGrid(cell)
        self.full.extend([(a, b, clr, min(a[0], b[0]) - clr, min(a[1], b[1]) - clr, max(a[0], b[0]) + clr, max(a[1], b[1]) + clr) for a, b, clr in water])
        self.center = PointGrid(cell)
        self.center.extend([(a, b, clr, min(a[0], b[0]) - clr, min(a[1], b[1]) - clr, max(a[0], b[0]) + clr, max(a[1], b[1]) + clr) for a, b, clr in registered])
        # EACH RING CARRIES A GRID OF ITS OWN VERTICES, AND THE HOLES A GRID OF THEIR BOXES (feature 276, FR-003): the
        # vertex-in-rectangle arm walked every vertex of each nearby ring - the union outline runs to thousands - and
        # `_in_outline` walked every hole, for every one of the nine points of every candidate. The grids return every
        # vertex a query box could hold and every hole whose box could hold a point; the same tests decide.
        self.rings = PointGrid(cell)
        self.rings.extend([(RingIndex(r), _vertex_grid(r), min(p[0] for p in r), min(p[1] for p in r), max(p[0] for p in r), max(p[1] for p in r)) for r in rings if len(r) >= 3])
        self.holes = [RingIndex(h) for h in holes if len(h) >= 3]
        self.hole_grid = PointGrid(cell)
        self.hole_grid.extend([(h, min(p[0] for p in h.ring), min(p[1] for p in h.ring), max(p[0] for p in h.ring), max(p[1] for p in h.ring)) for h in self.holes])

    def _in_outline(self, x: float, y: float, ring: Any) -> bool:
        return ring.inside(x, y) and not any(bx0 <= x <= bx1 and by0 <= y <= by1 and h.inside(x, y) for h, bx0, by0, bx1, by1 in self.hole_grid.near(x, y))

    def hit_points(self, pts: Any) -> bool:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        rx0, ry0, rx1, ry1 = min(xs), min(ys), max(xs), max(ys)
        cx_, cy_, pad = (rx0 + rx1) / 2, (ry0 + ry1) / 2, max(rx1 - rx0, ry1 - ry0) / 2
        # ONE LOOKUP FOR ALL THE POINTS (feature 276): every point lies in the points' own box, so the items the grid returns
        # for that box include every item near any one of them - nine lookups a rectangle were 320,469 on the rescue
        # scenario. The same distance and containment tests decide.
        # ...and a point outside an item's box, widened by its clearance, stands farther than the clearance: it is passed
        # without the distance (feature 287 perf: 138,229 distances on the reference seed 4's seating, most of them points
        # the box already answers for)
        if any(x0 <= x <= x1 and y0 <= y <= y1 and seg_dist(x, y, a, b) < clr for a, b, clr, x0, y0, x1, y1 in self.full.near(cx_, cy_, pad) for x, y in pts):
            return True
        seen: set[int] = set()
        for ring, verts, bx0, by0, bx1, by1 in self.rings.near(cx_, cy_, pad):
            if id(ring) in seen or bx1 < rx0 or bx0 > rx1 or by1 < ry0 or by0 > ry1:
                continue
            seen.add(id(ring))
            if any(self._in_outline(px, py, ring) for px, py in pts) or any(rx0 <= vx <= rx1 and ry0 <= vy <= ry1 for vx, vy, *_ in verts.near(cx_, cy_, pad)):
                return True
        return False

    def hit_center(self, x: float, y: float) -> bool:
        return any(seg_dist(x, y, a, b) < clr for a, b, clr, _x0, _y0, _x1, _y1 in self.center.near(x, y))


def _vertex_grid(ring: Any) -> PointGrid:
    """A ring's vertices, each filed at its own point, for "which vertices lie in this box" (feature 276)."""
    grid = PointGrid(32.0)
    grid.extend([(float(x), float(y), float(x), float(y), float(x), float(y)) for x, y in ring])
    return grid


#: The side of a block of `FreeGround` cells asked as one box before its cells are (`FreeGround.__init__`), in cells.
_BLOCK_CELLS = 8


class EdgeSamples:
    """A line's samples the raster left to be asked (`FreeGround.lines_edge_points`), kept as arrays and turned into points
    only when they are asked: most corridors are refused by something else first."""

    __slots__ = ("xs", "ys")

    def __init__(self, xs: Any, ys: Any) -> None:
        self.xs, self.ys = xs, ys

    def __iter__(self) -> Any:
        return zip(self.xs.tolist(), self.ys.tolist(), strict=True)

    def __len__(self) -> int:
        return len(self.xs)


class FreeGround:
    """The site's STATIC ground a homestead may not take, as a raster of SURELY TAKEN cells (feature 276, FR-003, plan D9).

    A cell is surely taken only when EVERY point of it is refused by the nine-point ground test `_site_blocks_rect`
    applies: it lies inside the union of the paddy chords' field-side strips (a point there projects onto the chord and
    stands on its field side - `chain_violated` at gap 0), the outline's rings less their holes (`hit_points`'
    containment arm), and the water corridors inflated by their clearance (its distance arm) - that union shrunk by half
    a pixel, so a point ON its boundary, where the strict tests may pass it, is never claimed. So a candidate with one of
    its sample points in such a cell is refused by the test it would have received, and dropping it unasked is exact.
    The registered corridors are left out (the fit test asks them at the center only), which only prunes less.

    Where no site boundary is installed there is no FreeGround (the placer asks the placed-box index alone)."""

    __slots__ = ("_state", "cell", "clear", "nx", "ny", "taken", "x0", "y0")

    def __init__(self, chains: Any, corridors: Any, outline: Any, bounds: tuple[float, float, float, float], cell: float = 8.0) -> None:
        _load_shapely()
        import shapely

        x0, y0, x1, y1 = bounds
        self.cell, self.x0, self.y0 = cell, x0, y0
        depth = 2.0 * math.hypot(x1 - x0, y1 - y0)
        parts: list[Any] = []
        for chain in chains:
            for (ax, ay), (bx, by), (nx, ny) in chain:
                if (bx - ax) ** 2 + (by - ay) ** 2 <= 1e-12:
                    continue
                parts.append(Polygon([(ax, ay), (bx, by), (bx - nx * depth, by - ny * depth), (ax - nx * depth, ay - ny * depth)]).buffer(0))
        rings, holes = outline if outline is not None else ([], [])
        ring_union = unary_union([Polygon(r).buffer(0) for r in rings if len(r) >= 3]) if rings else None
        if ring_union is not None and holes:
            ring_union = ring_union.difference(unary_union([Polygon(h).buffer(0) for h in holes if len(h) >= 3]))
        if ring_union is not None:
            parts.append(ring_union)
        water, _registered = corridors
        parts += [LineString([a, b]).buffer(clr) for a, b, clr in water if clr > 0]
        self.taken: set[tuple[int, int]] = set()
        nx_, ny_ = int((x1 - x0) // cell) + 1, int((y1 - y0) // cell) + 1
        self.nx, self.ny = nx_, ny_
        self._state: Any = None
        # ...AND THE SURELY CLEAR CELLS (feature 287): a cell no point of which the same union, GROWN by half a pixel,
        # reaches - every test of `_site_blocks_rect`'s points passes a point there. The seating's corridors are sampled
        # every 8 px against the same tests (`access.on_site_ground`, seed 44: 6.7 million points), and a sample in a
        # clear cell or a taken one needs no test; only a sample in a cell the union's edge crosses is asked.
        self.clear: set[tuple[int, int]] = set()
        if not parts:
            self.clear = {(i, j) for i in range(nx_) for j in range(ny_)}
            return
        union = unary_union(parts)
        grown = union.buffer(0.5)
        shapely.prepare(grown)
        region = union.buffer(-0.5)
        if not region.is_empty:
            shapely.prepare(region)
        # BLOCKS OF CELLS FIRST (feature 287): a block the grown union misses holds only clear cells, and a block the
        # shrunk union contains only taken ones - so only the cells of a block the union's edge crosses are asked one by
        # one. The same two tests decide every cell; a block only answers for cells inside it (seed 44: four boundaries of
        # 100,000-odd cells each, asked every cell twice).
        blk = _BLOCK_CELLS
        ni, nj = (nx_ + blk - 1) // blk, (ny_ + blk - 1) // blk
        bkeys = [(bi, bj) for bi in range(ni) for bj in range(nj)]
        bw = blk * cell
        blocks = shapely.box([x0 + bi * bw for bi, _ in bkeys], [y0 + bj * bw for _, bj in bkeys], [x0 + (bi + 1) * bw for bi, _ in bkeys], [y0 + (bj + 1) * bw for _, bj in bkeys])
        missed = shapely.disjoint(grown, blocks).tolist()
        held = shapely.contains(region, blocks).tolist() if not region.is_empty else [False] * len(bkeys)
        ask: list[tuple[int, int]] = []
        for (bi, bj), m, h in zip(bkeys, missed, held, strict=True):
            inner = [(i, j) for i in range(bi * blk, min(nx_, (bi + 1) * blk)) for j in range(bj * blk, min(ny_, (bj + 1) * blk))]
            if m:
                self.clear.update(inner)
            elif h:
                self.taken.update(inner)
            else:
                ask += inner
        if not ask:
            return
        cells = shapely.box([x0 + i * cell for i, _ in ask], [y0 + j * cell for _, j in ask], [x0 + (i + 1) * cell for i, _ in ask], [y0 + (j + 1) * cell for _, j in ask])
        self.clear.update(k for k, t in zip(ask, shapely.disjoint(grown, cells).tolist(), strict=True) if t)
        if not region.is_empty:
            self.taken.update(k for k, t in zip(ask, shapely.contains(region, cells).tolist(), strict=True) if t)

    def point_taken(self, x: float, y: float) -> bool:
        return (int((x - self.x0) // self.cell), int((y - self.y0) // self.cell)) in self.taken

    def point_clear(self, x: float, y: float) -> bool:
        """Does (x, y) stand in a cell every point of which the site's ground tests pass?"""
        return (int((x - self.x0) // self.cell), int((y - self.y0) // self.cell)) in self.clear

    def lines_edge_points(self, lines: Any) -> list[EdgeSamples | None]:
        """For each line `(a, b, n)`, its `n + 1` points `a + (b - a) * k / n`: None where one stands in a surely taken
        cell, else those standing in neither a taken nor a clear cell - the only ones the ground tests must still be asked
        of. Every line asked of the raster in one array: the seating asks a homestead's whole corridor search at once
        (seed 44: 130,000 lines of up to a hundred samples each, each asked alone)."""
        import numpy as np

        if self._state is None:
            state = np.zeros((self.nx, self.ny), dtype=np.int8)  # 0: the edge's cells, and any outside the grid
            for i, j in self.clear:
                state[i, j] = 2
            for i, j in self.taken:
                state[i, j] = 1
            self._state = state
        if not lines:
            return []
        ax, ay, bx, by, nf0 = np.array([(a[0], a[1], b[0], b[1], n) for a, b, n in lines], dtype=np.float64).T
        dx, dy, ns = bx - ax, by - ay, nf0.astype(np.int64)
        # EVERY FOURTH SAMPLE FIRST: a refused corridor crosses taken ground for samples running, and the lines it refuses
        # are left out of the whole count below (the samples are the same points, `a + (b - a) * k / n`)
        line, xs, ys, st = self._samples(np, ax, ay, dx, dy, ns, np.arange(len(lines)), 4)
        refused = np.bincount(line[st == 1], minlength=len(lines)) > 0
        line, xs, ys, st = self._samples(np, ax, ay, dx, dy, ns, np.nonzero(~refused)[0], 1)
        refused |= np.bincount(line[st == 1], minlength=len(lines)) > 0
        edge = np.nonzero(st == 0)[0]
        ex, ey = xs[edge], ys[edge]
        cut = np.searchsorted(line[edge], np.arange(len(lines) + 1)).tolist()  # the samples are in line order
        return [None if r else EdgeSamples(ex[cut[n] : cut[n + 1]], ey[cut[n] : cut[n + 1]]) for n, r in enumerate(refused.tolist())]

    def _samples(self, np: Any, ax: Any, ay: Any, dx: Any, dy: Any, ns: Any, which: Any, step: int) -> tuple[Any, Any, Any, Any]:
        """The samples `k = 0, step, 2 step, ...` (up to `n`) of the lines `which`: (their line, x, y, raster state)."""
        counts = ns[which] // step + 1
        line = np.repeat(which, counts)
        k = ((np.arange(len(line)) - np.repeat(np.cumsum(counts) - counts, counts)) * step).astype(np.float64)
        nf = ns.astype(np.float64)[line]
        xs = ax[line] + dx[line] * k / nf
        ys = ay[line] + dy[line] * k / nf
        i = np.floor_divide(xs - self.x0, self.cell).astype(np.int64)
        j = np.floor_divide(ys - self.y0, self.cell).astype(np.int64)
        inside = (i >= 0) & (i < self.nx) & (j >= 0) & (j < self.ny)
        st = np.zeros(len(line), dtype=np.int8)
        st[inside] = self._state[i[inside], j[inside]]
        return line, xs, ys, st

    def rect_refused(self, rect: Any) -> bool:
        """Is one of the nine points `_site_blocks_rect` asks of this (cx, cy, w, h) rectangle in a surely-taken cell?"""
        cx, cy, w, h = rect
        x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
        return any(self.point_taken(px, py) for px, py in ((x0, y0), (x1, y0), (x1, y1), (x0, y1), (cx, y0), (x1, cy), (cx, y1), (x0, cy), (cx, cy)))


class UnreachableGround:
    """The ground where a farmhouse would stand beyond any way's reach (feature 278, FR-005).

    A WAY CANNOT BE DRAWN ON THE WEB'S HARD GROUND. `stage_web` hands its router `hard = [plan.envelope, *crops, toe,
    *wet]` (`ways/web.py`) and every web lane keeps `WEB_HARD_GAP` off it; the track's `PathChecker` keeps off the same
    crop. So a house whose center stands more than `WEB_REACH_FT` inside that ground, inflated by the gap, has no way
    within `WEB_REACH_FT` of it - and `unreached_houses`, a distance test at `WEB_REACH_FT` against the served lanes, is
    certain to fail it. That is Sawada's first roll: a farmhouse seated in a bare pocket inside the paddy field, 157.1 px
    deep, stranded on every roll and re-rolled every time (research R3). "Deeper than the reach" is the ground ERODED
    by the reach - built once, asked per seat with one point test - and eroded a pixel further, so the polygonal
    approximation of the erosion can only refuse less than the rule, never more.

    THIS REFUSES ONLY THE SEATS UNREACHABLE BY CONSTRUCTION, and records the narrowing: a seat the web cannot reach for any
    other reason (hemmed in by other steadings' fabric) is still found by the roll's self-report after the build, because
    reach is not measurable at seating in general - three seat-time tests were built and all three failed
    (`hamletgen/driver.py`, the re-roll's note). Measured before choosing (observed 2026-09-28, method: `build()` of the five
    pool hamlets): no house on any pool map stands inside this ground but Sawada's stranded one."""

    __slots__ = ("_contains", "deep")

    def __init__(self, hard: list[Any], gap: float = WEB_HARD_GAP, reach: float = WEB_REACH_FT) -> None:
        _load_shapely()
        import shapely

        self._contains = shapely.contains_xy
        self.deep: Any = None
        polys = [Polygon(p).buffer(0) for p in hard if len(p) >= 3]
        if polys:
            core = unary_union(polys).buffer(gap).buffer(-(reach + 1.0))
            if not core.is_empty:
                shapely.prepare(core)
                self.deep = core

    def refuses(self, x: float, y: float) -> bool:
        return self.deep is not None and bool(self._contains(self.deep, x, y))


def web_hard_ground(s: Settlement, plan: SitePlan) -> list[Any]:
    """The ground `stage_web` hands its router as hard (`ways/web.py`), as far as it is drawn at seating: the field
    envelope, the crops, the toe band (asked before it is drawn), the wet ground. A marsh drawn later is simply absent,
    which only refuses less."""
    toe = [(float(a), float(b)) for a, b in (s.toe_band() or [])]
    wet = marsh_ground(s.M, but=("defense",))
    env = list(getattr(plan, "envelope", None) or [])  # a plan with no field envelope contributes none
    return [*([env] if len(env) >= 3 else []), *crop_polys(s), *([toe] if len(toe) >= 3 else []), *wet]


def install_site_boundary(s: Settlement, plan: SitePlan) -> None:
    """Compute the boundary for this roll's seat and set it on the settlement for the fit test (`_site_chains`,
    `_site_corridors`), recording it in the manifest for the gate and the measurement - no page element (FR-001).

    Research: no house on the toe marsh - research/questions/0058-ground-too-wet-to-build-on.drawing.html: the reed toe hard ground before it is drawn
    """
    seat = (float(plan.seat["cx"]), float(plan.seat["cy"]))
    # THE REED-MARSH TOE IS HARD GROUND FROM HERE ON, ASKED BEFORE IT IS DRAWN (settlement-review of this feature,
    # 2026-09-12). `hinterland()` lays the toe marsh after the structures, so `wet_polys` does not hold it at seat time -
    # and the review found three maps whose manifest put a farmhouse, a threshing floor and a byre inside the toe polygon
    # (Kashikawa's house 10 wholly, 46 px deep). The ways already ask `toe_band()` for the same reason (`ways/track.py`,
    # `ways/web.py`). Registered ONCE among `hard_polys` rather than added to the blob alone, so the boundary (which reads
    # `hard_polys`) and every placer after this stage (`_hard_clear`: the byres, the sheds, the wells) refuse it alike -
    # a first cut put it in the blob only, and Inashiro's byre 2 stood 28 px into the reeds.
    _toe = [(float(a), float(b)) for a, b in (s.toe_band() or [])]
    if len(_toe) >= 3 and _toe not in s.hard_polys:
        s.hard_polys.append(_toe)
    chains, corridors, outline = site_boundary(s, seat)
    s._site_chains = chains
    s._site_corridors = SiteCorridors(corridors, outline)
    s._free_ground = FreeGround(chains, corridors, outline, (0.0, 0.0, float(s.W), float(s.H)))
    s._unreachable = UnreachableGround(web_hard_ground(s, plan))
    s.M["site_boundary"] = {
        "chords": [[[round(a[0], 1), round(a[1], 1)], [round(b[0], 1), round(b[1], 1)], [round(n[0], 4), round(n[1], 4)]] for ch in chains for a, b, n in ch],
        "water": [[[round(a[0], 1), round(a[1], 1)], [round(b[0], 1), round(b[1], 1)], round(clr, 1)] for a, b, clr in corridors[0]],
        "corridors": [[[round(a[0], 1), round(a[1], 1)], [round(b[0], 1), round(b[1], 1)], round(clr, 1)] for a, b, clr in corridors[1]],
        "rings": [[[round(x, 1), round(y, 1)] for x, y in r] for r in outline[0]],
        "holes": [[[round(x, 1), round(y, 1)] for x, y in h] for h in outline[1]],
    }
