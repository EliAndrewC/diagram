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
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union

from l7r.diagram.settlement._geom.indexes import PointGrid, RingIndex
from l7r.diagram.settlement._geom.primitives import FIELD_KEEPOUT_EPS, facing_chains, seg_dist

if TYPE_CHECKING:
    from l7r.diagram.settlement import Settlement

    from ..plan import SitePlan

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


def site_boundary(s: Settlement, seat: tuple[float, float]) -> tuple[list[list[Any]], tuple[list[Seg], list[Seg]], tuple[list[list[tuple[float, float]]], list[list[tuple[float, float]]]]]:
    """`(chains, (water, registered), (rings, holes))` for the homestead stage, from every geometry the bundle's fit test reads
    (spec FR-001): the area members unioned and reduced to the chains facing `seat`; the water obstacles and the
    registered corridors as two sets of `(a, b, clearance)` segments, each asked the way its own test asks today."""

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
    for dest, courses in ((water, [(poly, float(hw)) for poly, hw, _bbox in s._water_obstacles()]), (registered, [(pts, float(clr)) for pts, clr, *_ in s.corridors if len(pts) >= 2])):
        for pts, clr in courses:
            for k in range(len(pts) - 1):
                a, b = (float(pts[k][0]), float(pts[k][1])), (float(pts[k + 1][0]), float(pts[k + 1][1]))
                if covered is not None and covered.buffer(clr).covers(LineString([a, b])):
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

    __slots__ = ("center", "full", "holes", "rings")

    def __init__(self, corridors: tuple[list[Seg], list[Seg]], outline: tuple[list[list[tuple[float, float]]], list[list[tuple[float, float]]]] | None = None, cell: float = 128.0) -> None:
        water, registered = corridors
        rings, holes = outline if outline is not None else ([], [])
        self.full = PointGrid(cell)
        self.full.extend([(a, b, clr, min(a[0], b[0]) - clr, min(a[1], b[1]) - clr, max(a[0], b[0]) + clr, max(a[1], b[1]) + clr) for a, b, clr in water])
        self.center = PointGrid(cell)
        self.center.extend([(a, b, clr, min(a[0], b[0]) - clr, min(a[1], b[1]) - clr, max(a[0], b[0]) + clr, max(a[1], b[1]) + clr) for a, b, clr in registered])
        self.rings = PointGrid(cell)
        self.rings.extend([(RingIndex(r), min(p[0] for p in r), min(p[1] for p in r), max(p[0] for p in r), max(p[1] for p in r)) for r in rings if len(r) >= 3])
        self.holes = [RingIndex(h) for h in holes if len(h) >= 3]

    def _in_outline(self, x: float, y: float, ring: Any) -> bool:
        return ring.inside(x, y) and not any(h.inside(x, y) for h in self.holes)

    def hit_points(self, pts: Any) -> bool:
        if any(seg_dist(x, y, a, b) < clr for x, y in pts for a, b, clr, _x0, _y0, _x1, _y1 in self.full.near(x, y)):
            return True
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        rx0, ry0, rx1, ry1 = min(xs), min(ys), max(xs), max(ys)
        seen: set[int] = set()
        for x, y in pts:
            for ring, bx0, by0, bx1, by1 in self.rings.near(x, y):
                if id(ring) in seen or bx1 < rx0 or bx0 > rx1 or by1 < ry0 or by0 > ry1:
                    continue
                seen.add(id(ring))
                if any(self._in_outline(px, py, ring) for px, py in pts) or any(rx0 <= vx <= rx1 and ry0 <= vy <= ry1 for vx, vy in ring.ring):
                    return True
        return False

    def hit_center(self, x: float, y: float) -> bool:
        return any(seg_dist(x, y, a, b) < clr for a, b, clr, _x0, _y0, _x1, _y1 in self.center.near(x, y))


def install_site_boundary(s: Settlement, plan: SitePlan) -> None:
    """Compute the boundary for this roll's seat and set it on the settlement for the fit test (`_site_chains`,
    `_site_corridors`), recording it in the manifest for the gate and the measurement - no page element (FR-001)."""
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
    s.M["site_boundary"] = {
        "chords": [[[round(a[0], 1), round(a[1], 1)], [round(b[0], 1), round(b[1], 1)], [round(n[0], 4), round(n[1], 4)]] for ch in chains for a, b, n in ch],
        "water": [[[round(a[0], 1), round(a[1], 1)], [round(b[0], 1), round(b[1], 1)], round(clr, 1)] for a, b, clr in corridors[0]],
        "corridors": [[[round(a[0], 1), round(a[1], 1)], [round(b[0], 1), round(b[1], 1)], round(clr, 1)] for a, b, clr in corridors[1]],
        "rings": [[[round(x, 1), round(y, 1)] for x, y in r] for r in outline[0]],
        "holes": [[[round(x, 1), round(y, 1)] for x, y in h] for h in outline[1]],
    }
