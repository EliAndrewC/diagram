"""The DRY ground cover, the layout that lays it, and the swept verge it must skip.

`commons` is the feathered scatter - coarse grass and brush with a few scraggly pines, open grazing
grass, or a spaced coppice canopy, by `role`. `hinterland` is the COMPOSER: it decides which frame
sides carry scrub, which side is the downhill toe, and fills the interior voids an irregular field
leaves inside its own bbox; it asks wet.py for the toe band and hands it to `commons` as a keep-out
so the two never overlap. `_clear_ground` / `reserve_clearing` reserve the swept ground around a
sacred or funerary feature.

The verge belongs in THIS module rather than with the features it protects, because the scatters are
what must skip it: `clearings` is a keep-out registry this module both writes and reads, and a
clearing registered after its scatter has run does nothing at all (`scatter_respects_swept_
clearings` checks exactly that ordering).

NO SOLID FILL is the rule the scatters are built on. A filled polygon always has a crisp geometric
EDGE, so each land type is defined PURELY by cover that thins to nothing at its margin - the ground
has no boundary, just its cover petering out.

Split from settlement/land.py by feature 120 - see settlement/land/CLAUDE.md for the index.

Research: plumbing - NONE: footprints, the bare-ground grid, keep-out indexing and manifest records
"""

import math
import random
from typing import TYPE_CHECKING, Any

# THE GRASS IS A TILE (feature 298): the blades and brush dots this scatter threw one by one - 55-68% of four pool hamlets'
# SVGs once merged (features 222-225 merged and culled them) - are the grass tile (`land.tiles`), filling each zone less the
# ground its throws were kept off (`Cover`, `Settlement.flush_covers`). The scraggly pines and the woodland's crowns stay
# individual: the GM, 2026-10-01, drawing individual trees "serves a useful purpose".
from .._geom import CrownIndex, KeepoutGrid, Poly, RingIndex, convex_hull
from ..land.wet import MARSH_FEATHER_BS, marsh_ground
from .tiles import Cover

WOOD_FRINGE_FT = 8.0
"""How far grass reaches in under a wood's edge before the kept-clear floor (GM 2026-09-27, Inashiro: highlighting the
scrub showed "broad swaths of the forest with scrubland underneath" - "a tiny bit of overlap" at the edge is fine). The
record already said the grass fringe "thins out inside the first few paces" (research/contents.json#homesteads, the woodland-edge
mantle-and-fringe); the woods were handed the marsh's 46 ft reed feather instead, so blades ran 46 ft under the belt.
A few paces is the record's own figure, so this is ACCURATE as a degree; 8 ft is the calibration within it.

Research: grass under a wood's edge - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: 8 ft"""

if TYPE_CHECKING:
    from ..core import Settlement


FARMSTEAD_NEIGHBOR_FT = 140.0  # ft: two farmsteads this near share the ground between them - a lane, a gap a copse fills
"""Research: shared ground between farmsteads - UNRESEARCHED: two within 140 ft keep the ground between them clear of scrub"""


def farmstead_keepouts(M: Any, margin: float) -> list[Any]:
    """The settlement's scrub keep-out as rings: each farmstead's own outline - its house and the parts nearest it -
    grown by `margin`, and the outline of each pair of farmsteads within `FARMSTEAD_NEIGHBOR_FT` (feature 261).

    Research: no scrub among the farmsteads - UNRESEARCHED: each farmstead and its parts, and each near pair, grown by the margin"""
    hs = [(float(h["x"]), float(h["y"])) for h in M.get("houses") or [] if "x" in h]
    if not hs:
        return []
    groups: list[list[tuple[float, float]]] = [[h] for h in hs]
    for key in ("gardens", "threshing_yards", "farm_fixtures", "byres", "farm_sheds", "retirement_houses", "persimmons"):
        for r in M.get(key) or []:
            if "x" in r:
                hw, hh = float(r.get("w", 0.0)) / 2, float(r.get("h", 0.0)) / 2
                k = min(range(len(hs)), key=lambda i: math.dist(hs[i], (float(r["x"]), float(r["y"]))))
                groups[k] += [(float(r["x"]) + sx * hw, float(r["y"]) + sy * hh) for sx in (-1, 1) for sy in (-1, 1)]

    def grown(pts: list[tuple[float, float]]) -> Any:
        return convex_hull([(x + margin * math.cos(math.radians(a)), y + margin * math.sin(math.radians(a))) for x, y in pts for a in range(0, 360, 45)])

    rings = [grown(g) for g in groups]
    rings += [grown(groups[i] + groups[j]) for i in range(len(hs)) for j in range(i + 1, len(hs)) if math.dist(hs[i], hs[j]) <= FARMSTEAD_NEIGHBOR_FT]
    return rings


WOODLAND_MIN_CROWNS = 5
"""The fewest crowns a woodland commons may record (`test_a_woodland_commons_is_visibly_stocked`, feature 287 woods W13):
a parcel claiming a wood draws one - under five crowns it reads as a few trees on grass, not a worked wood. A map drawing
convention on legibility, the rule's own figure; the parcel's real stocking is `COMMONS_SPACING_FT`.

Research: stocked wood floor - CONVENTION: at least five crowns, so a wood reads as one"""
#: a scrub pine's crown for the sun rule (feature 310): its lowest, widest branch, drawn 3.6 bs out, and the stroke's slack
PINE_SPREAD_BS = 4.6
"""Research: pine crown reach - CONVENTION: 4.6 bs, the drawn pine's widest branch and its stroke"""

BARE_STEP = 25.0  # px between the samples `bare_cells` takes - the gate's own grid (`margins_form_continuous_ring`)
BARE_SHARE_CAP = 0.35
"""How much of the rendered view may be ground nothing covers (`margins_form_continuous_ring`). Above this the map has
holes in it - the margins are meant to form a continuous ring of worked and unworked ground, not islands with gaps.

Research: bare-ground cap - CONVENTION: a map-completeness threshold, no more than 0.35 of the view uncovered"""

#: The manifest's TREADS - a way or a watercourse is a polyline with a width, not a ring: (key, points key, width key).
BARE_TREADS = (("lanes", "pts", "w"), ("streams", "poly", "w"), ("channels", "poly", "w"), ("field_ditches", "poly", "w"), ("drawn_channels", "pts", "w0"))
#: Keys that record no ground: the page's furniture, the render's bookkeeping, a lone connector's raw points.
_BARE_SKIP = frozenset(
    {
        "meta",
        "labels",
        "title",
        "scalebar",
        "ink_classes",
        "site_boundary",
        "comb_floors",
        "pond_layer",
        "tree_crowns",
        "scrub_pines",
        "bamboo_marks",
        "planted_trees",
        "wet_plots",
        "flooded_plots",
        "field_chains",
        "lane",
    }
)


def ring_center(poly: Any) -> tuple[float, float]:
    """The point a commons record carries as its `x`, `y`: the middle of its ring's bounding box, at the record's grain.
    ONE body (feature 287, woods W04): `commons` records it and the woodland scan asks the row rule of it, so the point a
    reader of the record finds in a row is the point the placer refused a row for."""
    xs = [float(q[0]) for q in poly]
    ys = [float(q[1]) for q in poly]
    return (round((min(xs) + max(xs)) / 2, 1), round((min(ys) + max(ys)) / 2, 1))


def _footprint(o: Any) -> Any:
    """One manifest record as the shapely ground it covers, or None - a ring (`outline` / `poly`), a turned box (`x y w h rot`),
    a disc (`x y r`) or an ellipse (`x y rx ry`); a bare list of points is a ring too (a pasture, a forest patch)."""
    from shapely.geometry import Point, Polygon  # noqa: PLC0415 - shapely is loaded on first use (feature 237)

    from .._geom import rot_rect  # noqa: PLC0415 - kept beside its one use

    if isinstance(o, dict):
        ring = o.get("outline") or o.get("poly")
        if ring and len(ring) >= 3 and all(isinstance(q, (list, tuple)) and len(q) >= 2 for q in ring):
            return Polygon([(float(q[0]), float(q[1])) for q in ring]).buffer(0)
        if all(k in o for k in ("x", "y", "w", "h")):
            return Polygon(rot_rect(float(o["x"]), float(o["y"]), float(o["w"]), float(o["h"]), float(o.get("rot") or 0.0))).buffer(0)
        if all(k in o for k in ("x", "y", "r")):
            return Point(float(o["x"]), float(o["y"])).buffer(max(float(o["r"]), 0.5))
        if all(k in o for k in ("x", "y", "rx", "ry")):
            return _ellipse_ground(float(o["x"]), float(o["y"]), float(o["rx"]), float(o["ry"]))
        return None
    if isinstance(o, (list, tuple)) and len(o) >= 3 and all(isinstance(q, (list, tuple)) and len(q) >= 2 for q in o):
        return Polygon([(float(q[0]), float(q[1])) for q in o]).buffer(0)
    return None


def _ellipse_ground(cx: float, cy: float, rx: float, ry: float) -> Any:
    """An axis-aligned ellipse as shapely ground."""
    from shapely import affinity  # noqa: PLC0415 - shapely is loaded on first use (feature 237)
    from shapely.geometry import Point  # noqa: PLC0415

    return affinity.scale(Point(cx, cy).buffer(1.0), max(rx, 0.5), max(ry, 0.5))


def covered_ground(M: Any) -> Any:
    """Everything the manifest records as standing on the ground, as one shapely geometry: every footprint (cover,
    fields, buildings, yards, wells, clearings, the burial ground, ponds - every ring, box, disc and ellipse a record
    carries) and every tread (the ways and the watercourses at their drawn width).

    THE FR-003 CORRECTION (feature 287, plan D6; woods W11): the rule's own grounding is that a hole in the cover is "the
    map admitting it has not decided what is there", and a recorded lane, stream, well, clearing or burial ground is
    DECIDED ground - "margin grass, scrub, a grazing common, a marsh, a wood, a yard" are the rule's examples, not its
    list. The gate used to count those as bare, so a view that such features filled could fail however the cover lay."""
    from shapely.geometry import LineString  # noqa: PLC0415 - shapely is loaded on first use (feature 237)
    from shapely.ops import unary_union  # noqa: PLC0415

    parts: list[Any] = []
    treads = {k for k, _p, _w in BARE_TREADS}
    for key, recs in M.items():
        if key in _BARE_SKIP or key in treads or not isinstance(recs, list):
            continue
        parts += [g for g in (_footprint(o) for o in recs) if g is not None and not g.is_empty]
    for key, pk, wk in BARE_TREADS:
        for o in M.get(key) or []:
            pts = [(float(q[0]), float(q[1])) for q in (o.get(pk) or [])]
            if len(pts) >= 2:
                parts.append(LineString(pts).buffer(max(float(o.get(wk) or 1.0), 1.0) / 2.0))
    pond = M.get("pond")
    if pond and len(pond) >= 4:
        parts.append(_ellipse_ground(float(pond[0]), float(pond[1]), float(pond[2]), float(pond[3])))
    return unary_union(parts) if parts else None


def bare_cells(M: Any, view: Any, step: float = BARE_STEP) -> tuple[list[tuple[float, float]], int]:
    """The sample points of `view` (x, y, w, h) that stand on ground nothing covers, and how many points were sampled.

    ONE PREDICATE (feature 287, FR-003; woods W11): the grid is the gate's own - a point every `step` px from half a step
    in - and "covered" is `covered_ground`, which counts every recorded footprint and tread. The share is
    `len(bare) / total`; the rule holds it at `BARE_SHARE_CAP`."""
    from shapely import intersects_xy  # noqa: PLC0415 - shapely is loaded on first use (feature 237)

    vx0, vy0, vw, vh = (float(v) for v in view)
    xs: list[float] = []
    ys: list[float] = []
    y = vy0 + step / 2
    while y < vy0 + vh:
        x = vx0 + step / 2
        while x < vx0 + vw:
            xs.append(x)
            ys.append(y)
            x += step
        y += step
    ground = covered_ground(M)
    hit = intersects_xy(ground, xs, ys) if ground is not None else [False] * len(xs)
    return [(x, y) for x, y, h in zip(xs, ys, hit, strict=True) if not h], len(xs)


def map_window(M: Any) -> list[float]:
    """The part of the sheet that is MAP, as (x, y, w, h): the view, or the neatline where the map's ink is clipped at one
    (a title panel or a caption key outside it is sheet, not ground - `Settlement._title_band`). The window the bare-ground
    rule is judged over (`margins_form_continuous_ring`, feature 287 woods W11)."""
    meta = M.get("meta") or {}
    return [float(v) for v in (meta.get("neatline") or meta["view"])]


def bare_blocks(bare: list[tuple[float, float]], step: float = BARE_STEP) -> list[list[tuple[float, float]]]:
    """The bare sample points grouped into connected blocks (4-neighbors on the `step` grid), largest first."""
    if not bare:
        return []
    x0, y0 = min(p[0] for p in bare), min(p[1] for p in bare)
    at = {(round((x - x0) / step), round((y - y0) / step)): (x, y) for x, y in bare}  # grid indices: the points were accumulated in floats
    left = set(at)
    out: list[list[tuple[float, float]]] = []
    while left:
        seed = min(left)
        left.discard(seed)
        block, todo = [seed], [seed]
        while todo:
            i, j = todo.pop()
            for q in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                if q in left:
                    left.discard(q)
                    block.append(q)
                    todo.append(q)
        out.append([at[k] for k in block])
    return sorted(out, key=lambda b: (-len(b), min(b)))


def block_ring(block: list[tuple[float, float]], step: float = BARE_STEP) -> list[tuple[float, float]]:
    """A bare block as one ring: the outline of its cells (each sample point's `step` square), the largest piece's exterior
    - which holds every one of its sample points, since a cell's square holds its center."""
    from shapely.geometry import box
    from shapely.ops import unary_union

    h = step / 2.0
    g = unary_union([box(x - h, y - h, x + h, y + h) for x, y in block])
    part = max(getattr(g, "geoms", [g]), key=lambda p: p.area)
    return [(float(x), float(y)) for x, y in part.exterior.coords[:-1]]


class GroundCoverMixin:
    def fill_the_holes(self: Settlement, view: Any, planned: Any = ()) -> int:  # type: ignore[misc]
        """Lay rough grazing over the bare ground of `view` (x, y, w, h) until no more than `BARE_SHARE_CAP` of it is ground
        nothing covers (feature 287, woods W11 - `margins_form_continuous_ring`: between the fields and the settlement
        there is always something). `planned` is cover a later stage will record (the woodland parcels, the bamboo
        stands), counted as cover. The bare sample points (`bare_cells`, the rule's one predicate) are grouped into
        connected blocks and the largest are clothed first, each as one grazing commons over its cells - its record
        covers every one of its points, so the share falls by exactly the block and the fill ends. Returns the commons laid.
        Rough grazing is what the record puts on ground nothing else claims (research/questions/0078-grass-hills-and-fodder-meadows-kusayama-magusaba.drawing.html).

        Research: unclaimed ground grazed - research/questions/0078-grass-hills-and-fodder-meadows-kusayama-magusaba.drawing.html: the largest bare blocks laid as grazing until the cap holds"""
        vars(self)["_fills_holes"] = True  # ...and the view the finish grows for the title is clothed the same way (`refill_the_view`)
        probe = {**self.M, "_planned_cover": [[(float(q[0]), float(q[1])) for q in p] for p in planned]}
        bare, total = bare_cells(probe, view)
        laid = 0
        for block in bare_blocks(bare):
            if not total or len(bare) <= BARE_SHARE_CAP * total:
                break
            self.commons(block_ring(block), role="grazing")
            gone = set(block)
            bare = [p for p in bare if p not in gone]
            laid += 1
        return laid

    def refill_the_view(self: Settlement) -> int:  # type: ignore[misc]
        """THE VIEW AS IT ENDS, CLOTHED (feature 287, woods W11): the title's last rung grows the sheet a band past the view
        the holes were filled over (`Settlement._title_band`), and the band shows the map's canvas - blank ground the rule
        counts. So a map that filled its holes (`fill_the_holes`) has the final view filled again, over `map_window` - the
        view, or the neatline where the band lies outside the map. Returns the commons laid; 0 for a map that never asked."""
        if not vars(self).get("_fills_holes"):
            return 0
        return self.fill_the_holes(map_window(self.M))

    def _commons_keep(self: Settlement, box: tuple[float, float, float, float], avoid: Any = ()) -> Any:  # type: ignore[misc]
        """The commons' STATIC keep-outs over `box` (x0, y0, x1, y1), indexed once - lifted out of `commons` (feature 287, woods
        W13) so the woodland scan asks the very keep-outs a parcel's crowns will be thrown against (`woodland_room`).

        Research:
            off the crops - research/questions/0073-scrub-and-rough-grass-at-the-edges-of-fields-and-channels.drawing.html: every paddy and dry plot padded by the crop margin
            off the treads - UNRESEARCHED: 4 ft of bare verge along every lane, street and road
            off the channels - research/questions/0073-scrub-and-rough-grass-at-the-edges-of-fields-and-channels.drawing.html: the cut-bank margin off every irrigation channel, streams at their drawn width"""
        bs = self.bscale
        halo_rects, halo_circles = self._urban_keepouts(box)  # the urban-clearance halo (see _urban_keepouts)
        corridors = self._corridor_buffers(
            4 * bs
        )  # lanes AND town streets AND the road: every trodden/maintained tread stays bare (the old skip knew only lanes, so scrub drew on the Imperial Road bed - GM 2026-07-21, Hoshizora).
        # FOUR, BECAUSE THAT IS THE FIGURE THE RULE READS (feature 230). `groves_clear_of_lanes` forbids a
        # TRUNK within 4.0 ft of a lane's centerline, and this buffer was 3 - so a tree could be planted
        # 3.1 ft from a 3 ft footpath, off the tread and inside the rule, and the gate was right to say
        # so. A check and the code it checks must read the same number or they drift apart quietly; the
        # cost is one more foot of bare verge along every tread, which is what a walked path has anyway.
        # PRE-BOX every static keep-out ONCE (see boxed_hit): _sparse below runs per SCATTER POINT,
        # and these lists do not change while a region scatters
        # INDEXED (2026-08-04): boxing alone dropped the cost per keep-out but still VISITED every
        # one per scatter point - 948k boxed_hit calls iterating 25M items on Kikuta, whose gen was
        # still 81% ground cover. The grids narrow each point to its own cell; the exact tests below
        # are the same ones, run on what `near` returns.
        # CROP MARGIN (see _CROP_MARGIN_FT): the crop keep-out is every PADDY (field_polys) plus
        # every DRY PLOT (dry_polys - block_polys also carries them, but reading the crop registry
        # directly is what the grove/lane skips do, and it survives a gen that registers only one),
        # padded by the margin. Boxes carry the WORST-CASE pad - margin plus the tallest glyph's
        # drawn reach, a pine tip at 14*bs - because the bbox prefilter must never reject a point
        # the exact edge test wants (boxed_hit's contract); the exact test gets the per-glyph lean.
        crop_pad = self.px(self._CROP_MARGIN_FT)
        # ONE GRID FOR EVERY STATIC KEEP-OUT (feature 218; `KeepoutGrid` carries the argument):
        # the crop rings grow by the glyph's lean per query (slot 1, boxed for the tallest, a pine
        # tip at 14*bs); a marsh recorded BEFORE this pass sits in block_polys as a no-build bog
        # and is a SOFT keep-out below, so it is not filed here - or the feathered edge never
        # happens; the irrigation channels carry the cut-bank margin (_BANK_MARGIN_FT), streams
        # stay at drawn width so the brook's natural bank keeps its grass; the urban halo is the
        # closed test it always was
        keep = KeepoutGrid()
        keep.rings(list(self.field_polys) + list(self.dry_polys), pad=crop_pad, slot=1, reach=14 * bs)
        keep.rings([bp for bp in self.block_polys if not any(bp is mb for mb in self.marsh_blocks)])
        keep.rings(self.clearings)
        keep.rings(avoid)
        keep.segs(corridors)
        keep.segs(self._watercourse_segs(channel_margin=self.px(self._BANK_MARGIN_FT)))
        keep.rects(halo_rects, closed=True)
        keep.circles(halo_circles, closed=True)
        return keep

    def woodland_room(self: Settlement, poly: Any) -> list[tuple[float, float, float]]:  # type: ignore[misc]
        """The crowns a woodland parcel `poly` is SURE of, as (x, y, r): a grid at the stocking spacing
        (`COMMONS_SPACING_FT`) over the ring, each seat inside it, on dry ground (off every marsh), clear of every keep-out
        the commons' crowns are thrown against at the largest crown's lean (`_commons_keep`), off the pond and the fengshui
        pond, and under no crown already standing at the largest radius (feature 287, woods W13). Deterministic - no draw is
        made - so the scan that offers a parcel and the commons that stocks it read one answer: a parcel whose room is
        under `WOODLAND_MIN_CROWNS` is not offered, and a parcel whose throws seat fewer is stocked from its room.

        Research: coppice stocking grid - research/questions/0080-how-thickly-trees-stood-in-a-wood-and-how-wide-their-crowns.drawing.html: a crown every COMMONS_SPACING_FT on dry ground, none under another"""
        xs, ys = [float(q[0]) for q in poly], [float(q[1]) for q in poly]
        x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
        keep = self._commons_keep((x0, y0, x1, y1))
        ring = RingIndex(poly)
        wet = [RingIndex(m) for m in marsh_ground(self.M)]
        pond = self.M.get("pond")
        crescents = self.M.get("crescent_ponds", [])
        r = self.px(self.COMMONS_CROWN_R_FT[1])
        seated = CrownIndex(self._crowns_near(x0, y0, x1, y1))
        step = self.px(self.COMMONS_SPACING_FT)
        out: list[tuple[float, float, float]] = []
        y = y0 + step / 2
        while y < y1:
            x = x0 + step / 2
            while x < x1:
                if (
                    ring.inside(x, y)
                    and not keep.hit(x, y, (0.0, r))
                    and not any(w.inside(x, y) for w in wet)
                    and not (crescents and self._on_crescent_pond(x, y))
                    and not (pond and ((x - pond[0]) / pond[2]) ** 2 + ((y - pond[1]) / pond[3]) ** 2 <= 1.0)
                    and seated.clear(x, y, r)
                ):
                    seated.add(x, y, r)
                    out.append((x, y, r))
                x += step
            y += step
        return out

    def commons(self: Settlement, poly: Any, role: str = "commons", avoid: Any = (), render: str = "scrub", soft: Any = (), woods: Any = ()) -> None:  # type: ignore[misc]
        """FUEL-AND-FODDER COMMONS - the degraded open grazing/scrub on the far (upslope / windward) side,
        BEYOND the fengshui back-grove: coarse grass, low brush, and a FEW scattered SCRAGGLY pines, kept
        cropped bare by constant firewood + grass gathering. Deliberately drawn OPEN and SPARSE on drier,
        poorer ground so it is VISUALLY DISTINCT from the dense, dark, closed-canopy village grove - this is a
        COMMONS (not anyone's field), non-arable. WHY (south China's hills were stripped for fuel/timber over a
        millennium - open pine + grass + erosion; the protected grove is the green EXCEPTION; the back slope
        also carried the graves + dry hill-crops): research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.html / 'Grass hills and fodder meadows (kusayama, magusaba)'. Recorded
        in M['commons']. `role` picks the glyph (woodland / pasture / commons); `avoid` is a list of KEEP-OUT
        polygons (e.g. the hamlet cluster) the scatter stays out of, so ground-cover never creeps onto them.

        Research:
            commons beyond the grove - research/questions/0078-grass-hills-and-fodder-meadows-kusayama-magusaba.drawing.html: open scrub and rough grazing, not forest
            scrub ground color - research/questions/0078-grass-hills-and-fodder-meadows-kusayama-magusaba.drawing.html: the grass and brush drawn as one repeated block over the bare ground, no solid fill and no outline (`tiles.cover_path`: the pattern alone)
            grass ground forms - research/questions/0078-grass-hills-and-fodder-meadows-kusayama-magusaba.drawing.html: one form only, the scrub past the grove; the floodplain and the small grass plot beside one paddy are never drawn or rolled
            coppice stocking - research/questions/0080-how-thickly-trees-stood-in-a-wood-and-how-wide-their-crowns.drawing.html: one crown to COMMONS_SPACING_FT squared, COMMONS_CROWN_R_FT across
            no crown under another - research/questions/0080-how-thickly-trees-stood-in-a-wood-and-how-wide-their-crowns.drawing.html: a crown centered under one already seated is not drawn
            scrub pines - research/questions/0078-grass-hills-and-fodder-meadows-kusayama-magusaba.drawing.html: a few scraggly pines - one throw to 6,000 sq ft, at least two throws (a throw the keep-outs refuse seats none), none on pasture
            off the ponds' open water - UNRESEARCHED: no scrub, pine or coppice crown on a pond or a crescent pond (one water test, `_sparse`), the grass bare 2 ft past a crescent pond's rim
            marsh edge - research/questions/0074-reed-beds-and-the-marshs-edge-yoshihara.drawing.html: grass thins into the reeds, brush and pines stop at the marsh
            wood edge - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: no brush or pine in a wood, grass only WOOD_FRINGE_FT under its edge, thinning inward (its inner half at `WOOD_FRINGE_THIN_KEEP`)
            coppice stops at the marsh - research/questions/0074-reed-beds-and-the-marshs-edge-yoshihara.drawing.html: no woody growth inside a marsh but the belt's alder, so no coppice crown is seated in one
            crowns and pines clear of the crops - UNRESEARCHED: a crown held its largest radius, a pine its 14 bs tip, off every field, so no canopy or pine overhangs one
            a scrub pine's reach - UNRESEARCHED: `PINE_SPREAD_BS` (4.6 ft) as the pine's crown radius in the sun test
            edge feather - CONVENTION: the scatter thins over 42 bs at the parcel's edge
            crown and pine ink - CONVENTION: flat crown discs, a scraggly three-branch pine
            claimed but undrawn - CONVENTION: a bare render records the ground and draws nothing
            woodland no-build - UNRESEARCHED: a woodland parcel made no-build ground
            woodland stocked to read - CONVENTION: a woodland parcel carries at least `WOODLAND_MIN_CROWNS` (5) crowns, so it reads as a wood
            no crown in a yard's sun - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: no coppice crown or scrub pine in a yard's or bed's sun"""
        # EVERY RECORDED MARSH IS A KEEP-OUT FOR SCRUB (GM 2026-08-26, feature 133 T12: *"do we mean to
        # show ... small pine trees and such growing out of the marshland in exactly the same pattern as
        # ... outside of the marshland? my guess is that that is a mistake"*). It was: only the toe-side
        # strip was handed the toe band (2026-08-12), so the left/right ring strips, the interior fill
        # and every gen-placed patch scattered dry-ground scrub straight through the reeds, and none of
        # them knew the pond-fringe marsh recorded before them - Inashiro carried ~40k scrub bases
        # inside its marshes (the scatter audit (retired 2026-09-06, feature 193) adjudicated "marsh"). Reeds are the
        # marsh's own cover; scrub stops where the wet ground starts. Taken here, at the source, so a
        # caller cannot forget it; the toe band that is only computed later is passed in by hinterland.
        # A SOFT keep-out, not a hard one (settlement-review 2026-08-26, round 1): the marsh thins its
        # reeds to nothing over a 46 px feather INSIDE its polygon, so a hard cut at the polygon left a
        # ruled line and a ~40 ft bare strip on the toe's straight west edge. The scrub instead thins
        # INTO the marsh over that same band - kept with probability 1 at the edge, 0 at feather depth,
        # the complement of the reeds' ramp - so the two covers interleave into a wild edge.
        soft = [*soft, *marsh_ground(self.M)]
        # SCOPED (2026-08-08): the tuft/brush scatter is decoration keyed to the common it fills.
        if render == "bare":
            # CLAIMED but UNDRAWN ground (GM 2026-08-10, on the capital's ring bands reading as
            # weeds): the record still claims the ground for the empty-space detector and names
            # its role, but nothing is scattered - kept working ground reads as clean parchment,
            # not scrub. The default stays "scrub" so every village commons is byte-identical.
            xs0 = [q[0] for q in poly]
            ys0 = [q[1] for q in poly]
            self.M.setdefault("commons", []).append(
                {
                    "x": round(sum(xs0) / len(xs0), 1),
                    "y": round(sum(ys0) / len(ys0), 1),
                    "w": round(max(xs0) - min(xs0), 1),
                    "h": round(max(ys0) - min(ys0), 1),
                    "rot": 0,
                    "role": role,
                    "seq": len(self.M.get("commons", [])) + 1,
                    "poly": [list(q) for q in poly],
                }
            )
            return
        with self.rng_scope("commons", len(poly), poly[0][0], poly[0][1]):
            xs = [p[0] for p in poly]
            ys = [p[1] for p in poly]
            x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
            bs = self.bscale
            # THE POLYGON'S AREA, NOT ITS BOUNDING BOX. These were the same number for as long as
            # every commons was an axis-aligned rectangle, and stopped being the same the day
            # woodland parcels started rolling a bearing (2026-08-18): a rect rotated 45 deg has a
            # bbox 41% larger than itself, so a bbox-derived scatter target overshoots by that much
            # and the realized density then depends on the rotation ANGLE - measured 433 sq ft per
            # crown against the stated 540 on a parcel turned 7 deg. `_sparse` already refuses a
            # point outside the ring, so nothing was drawn out of bounds; the count was simply
            # computed against the wrong shape. Shoelace, so it is the ring the manifest records.
            area = abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))) / 2.0 or (x1 - x0) * (y1 - y0)
            st = random.getstate()
            random.seed(int(abs(x0) * 7 + abs(y0) * 3 + round(x1 - x0)))
            feather = 42 * bs  # scrub THINS toward the boundary (a soft, ragged edge, not a hard line)

            pond = self.M.get("pond")
            keep = self._commons_keep((x0, y0, x1, y1), avoid)  # every static keep-out, indexed once (the why is on the method)
            crescents = self.M.get("crescent_ponds", [])  # read once: the per-point test below costs a registry lookup per throw otherwise
            soft_polys = [[tuple(q) for q in sp] for sp in soft] + [[tuple(q) for q in wp] for wp in woods]
            # the marsh's own reed feather (wet.py), so the two ramps are complements - and a WOOD's much narrower one
            soft_feathers = [MARSH_FEATHER_BS * bs] * len(soft) + [WOOD_FRINGE_FT * bs] * len(woods)
            # THE RING IS INDEXED ONCE (feature 145): every throw below asked `point_in_poly` and
            # `edge_dist` to walk the whole outline - 1.3M ray tests and 156k full-ring scans per
            # reference roll, two thirds of the stage. `RingIndex` answers both from the edges near
            # the point, exactly (its docstring carries the argument).
            ring = RingIndex(poly)
            soft_idx = [RingIndex(sp) for sp in soft_polys]

            def _sparse(
                px: float, py: float, drop: float, lean: float = 0.0
            ) -> bool:  # skip a scatter point outside the poly, on/near a crop, on a corridor/water, in the urban halo, in a keep-out, or (probabilistically) near the edge; `lean` = the glyph's drawn reach, so a tall glyph stands its own height back from the crop margin
                if (
                    not ring.inside(px, py)
                    or keep.hit(px, py, (0.0, lean))  # off the crops (+ this glyph's lean), every tread, the water, the halo, every footprint, the verge, the avoid set - one cell read
                    or (crescents and self._on_crescent_pond(px, py))  # ... and the fengshui pond's open water
                    or (pond and ((px - pond[0]) / pond[2]) ** 2 + ((py - pond[1]) / pond[3]) ** 2 <= 1.0)  # ... and the pond (scrub never draws over open water)
                ):  # ... and OUT of any keep-out (the hamlet cluster stays clear of cover)
                    return True
                for si, sf in zip(soft_idx, soft_feathers, strict=True):  # ...and GRASS thins INTO a soft keep-out (a marsh, a wood) over its own feather
                    if si.inside(px, py):
                        sd = si.edge_within(px, py, sf)
                        return random.random() < (1.0 if sd is None else sd / sf)
                ed = ring.edge_within(px, py, feather)
                return ed is not None and random.random() > (ed / feather) ** drop

            def _in_soft(px: float, py: float) -> bool:
                """WOODY glyphs (brush dots, pines) are HARD-excluded from a marsh; only GRASS grades into it.
                Round 2 of the T12 fix let every family thin into the reeds over the 46 px band, and at fit
                zoom a 1,600 px seam of pines standing in the bog read as the very overlap the GM had
                asked to remove (GM 2026-08-26: *"it looks like it is still overlapping!"*). The ecology
                agrees: a bog's margin is sedge and grass grading into reeds; pine and brush stand on the
                dry ground above it. So blades keep the soft ramp (a wild edge, no ruled line) and the
                woody families stop dead at the polygon."""
                return any(si.inside(px, py) for si in soft_idx)

            # NO solid fill: a filled polygon always has a crisp geometric EDGE (that read as a rhombus). Each land
            # type is defined PURELY by its feathered scatter, which thins to nothing at the margin - so the ground
            # has no boundary at all, just its cover petering out onto the open slope. THREE distinct looks so land
            # types read apart at a glance (the GM's rule - grass and woods must NOT look the same):
            #   role="woodland"  -> a COPPICE WOOD: a thicket of small crowns whose neighbors just meet (8-9 ft on
            #                       ~8 ft centers, research/vegetation/230) - the hill wood the hamlet coppices. Clearly
            #                       TREES, lighter and finer-grained than the DARK big-crowned village grove (they stay distinct).
            #   role="pasture"   -> OPEN GRAZING GRASS: grass tufts + the odd brush dot, NO trees at all - reads as
            #                       open pasture, unmistakably NOT woodland.
            #   role="commons"/"grazing" (default) -> the cut-over fuel/fodder scrub: grass + a FEW scraggly pines.
            # The grass and brush are the grass tile (feature 298; the note at the imports); the pines keep their inline styles.
            g: list[str] = []
            marks: list[tuple[float, float, float, float, str]] = []  # (extent, string): the pines, culled to the frame at finish (feature 225); the woodland crowns stay in `g`
            _wd_crowns = 0
            _cover_bare: list[Any] = []  # the ground the grass tile leaves bare (feature 298): set where the grass would have been thrown
            _woods: list[Any] = []  # the woods the scrub keeps out of whole, and the grass-only band under each one's edge (wave 57)
            _fringe: list[Any] = []
            _fringe_in: list[Any] = []
            if role == "woodland":
                # A TARGET, NOT AN ATTEMPT COUNT (settlement-review x3, 2026-08-18 round 2 - Inashiro,
                # Sawada and Mizuguchi found it independently). `int(area / 540)` looks like a density
                # and is not: it is the number of THROWS, and `_sparse` rejects a share of them, so the
                # realized spacing depends on how much of a parcel lies near a keep-out. Small parcels
                # are proportionally more edge, so they came out both smaller AND thinner - measured
                # 691-768 sq ft per crown on the big stands against 981 on Sawada's and 1101 on
                # Inashiro's smallest, which at ~31% canopy reads as scattered trees on grass rather
                # than a wood. The size-variance work made that worse rather than better: growing
                # Sawada's parcel 125 -> 136 ft added no crowns at all, so the sparsest object on the
                # sheet got sparser.
                #
                # A coppice is a worked thicket cut on rotation, and the sources describe the SMALL
                # parcels near a settlement as the intensively worked ones - so density must not fall
                # away with size. Throwing until the target is MET (capped, so a parcel that genuinely
                # cannot hold its quota still terminates) makes the realized density the stated one on
                # every parcel. The draws stay inside this function's `random.setstate` scope, so the
                # extra throws cannot ripple into anything drawn later.
                # THE COMMONS' OWN STOCKING (269 B28; research/vegetation/230): one crown to `COMMONS_SPACING_FT`
                # squared (~63 sq ft, 1,700 stems/ha), each 8-9 ft across so neighbors just meet. It was one crown to
                # 540 sq ft at 13-23 ft across, the hill wood's figures (0080) that no page gave for a coppice.
                _wd_target = int(area / self.px(self.COMMONS_SPACING_FT) ** 2)
                _r_lo, _r_hi = (self.px(v) for v in self.COMMONS_CROWN_R_FT)
                # ...AND NO CROWN IN A YARD'S OR BED'S SUN (feature 310, GM 2026-10-02: "no canopy trees should be exempt"), throws and
                # the room's grid alike: the commons are laid after every plot, so the keep-out is whole here
                _wd_sun = self._sun_keepouts(
                    (x0 - _r_hi - self.CANOPY_PAD, y0 - _r_hi - self.CANOPY_PAD, x1 + _r_hi + self.CANOPY_PAD, y1 + _r_hi + self.CANOPY_PAD)
                )  # the reach the crown test asks: radius AND pad
                # no crown under another's, this wood's or a neighbor's (GM 2026-08-28; woods._crown_seat_clear) -
                # asked of an index, because a coppice at its real stocking seats hundreds of crowns (dev/performance.md)
                _wd_seated = CrownIndex(self._crowns_near(min(q[0] for q in poly), min(q[1] for q in poly), max(q[0] for q in poly), max(q[1] for q in poly)))
                _tc0, _g0 = len(self.M["tree_crowns"]), len(g)  # where this wood's crowns start, for the stocking below
                for _ in range(_wd_target * 6):
                    if _wd_crowns >= _wd_target:
                        break
                    cx, cy = random.uniform(x0, x1), random.uniform(y0, y1)
                    if _sparse(cx, cy, 0.6, _r_hi):  # lean = the largest crown radius, so no canopy overhangs a crop
                        continue
                    # ...AND NONE IN A MARSH (feature 328 wave 57, impl-drift; 0074: woody growth stops at the marsh's edge, the
                    # trees standing in one are the belt's alder): the coppice's crowns thinned 46 ft into it over the grass's ramp
                    if any(si.inside(cx, cy) for si in soft_idx[: len(soft)]):
                        continue
                    r = random.uniform(_r_lo, _r_hi)
                    if self._crown_covers(cx, cy, r, _wd_sun, (), self.CANOPY_PAD):
                        continue
                    col = random.choice(("#6E8B4A", "#7C9856", "#87A45C"))
                    # RECORD the crown (known-open ledger 2026-08-16, both review rounds
                    # independently): these used to be SVG ink only, so no manifest check could
                    # count a stand's canopy - which is how a zero-crown "woodland" parcel could
                    # ship green. Same flat [x, y, r] run the homestead groves use.
                    if not _wd_seated.clear(cx, cy, r):
                        continue  # centered under an already-seated crown: an understory stem, not canopy
                    _wd_seated.add(cx, cy, r)
                    self.M["tree_crowns"] += [round(cx, 1), round(cy, 1), round(r, 1)]
                    _wd_crowns += 1
                    # ONE FLAT DISC PER CROWN (GM 2026-09-28), as in groves.py and woods.py. A pale "sun highlight"
                    # disc inside each crown and a soft ground shadow under it were a shading convention that
                    # the GM read as a second tree or a trunk, worse under the page's highlighting; color alone
                    # tells one kind of tree from another.
                    g.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{col}" stroke="#4C6234" stroke-width="0.7"/>')
                # ...AND NEVER UNDER-STOCKED (feature 287, woods W13): where the throws seat fewer than `WOODLAND_MIN_CROWNS` -
                # a parcel mostly over the padded crop, most throws refused - they are taken back and the parcel is stocked
                # from its room instead (`woodland_room`, the grid the scan asked before offering it), so a parcel the scan
                # offered always records at least the floor it was offered at
                if _wd_crowns < WOODLAND_MIN_CROWNS:
                    del self.M["tree_crowns"][_tc0:]
                    del g[_g0:]
                    room = [t for t in self.woodland_room(poly) if not self._crown_covers(t[0], t[1], t[2], _wd_sun, (), self.CANOPY_PAD)][: max(_wd_target, WOODLAND_MIN_CROWNS)]
                    for cx, cy, r in room:
                        self.M["tree_crowns"] += [round(cx, 1), round(cy, 1), round(r, 1)]
                        g.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="#7C9856" stroke="#4C6234" stroke-width="0.7"/>')
                    _wd_crowns = len(room)
            else:
                # A THROW OUTSIDE THE PREDICTED FRAME COSTS ITS TWO DRAWS AND NOTHING ELSE (feature 224): ~90% of a hamlet's
                # throws land where the frame will clip them, and each used to pay the keep-out test and its marks' draws
                # before finish culled the result. The count is the parcel's own (D3), so the in-frame density is unchanged;
                # the in-frame texture re-rolls (D1, the GM's 2026-09-08 ruling). `_scatter_frame` is None outside a hamlet.
                _fr = self._scatter_frame
                if _fr is not None:
                    self._scatter_frames.append((_fr, (x0, y0, x1, y1)))  # for finish()'s breach record: the frame, and the ground this throw covered
                # THE GRASS AND BRUSH ARE A TILE NOW (feature 298, the GM 2026-10-01: "instead of then drawing individual glyphs
                # within that ... some tiled pattern"): the zone is recorded with the ground its scatter kept bare - every keep-out
                # the throw was tested against, every marsh, the crescent ponds and the pond - and `flush_covers` fills the rest
                # with the grass tile at the bottom of the stack, so whatever stands in it draws over it
                import shapely.affinity  # bound here, not at import (feature 237)
                from shapely.geometry import Point, Polygon

                _cover_bare += [g for g in (keep.shape((0.0, 0.0), (x0, y0, x1, y1)),) if g is not None]
                _cover_bare += [Polygon(m).buffer(0) for m in soft]  # every marsh (and what the caller hands as soft): no grass in the reeds
                # ...and every wood but its fringe: grass runs a few paces in under a wood's edge (`WOOD_FRINGE_FT`, the GM
                # 2026-09-27: not "broad swaths of it under the windbreak")
                # ...and every wood WHOLE: the scrub tile carries brush, and no brush stands in a wood (0077); the fringe a few
                # paces in under its edge is drawn with the grass-only tile instead (`wood_fringe_tile`, feature 328 wave 57)
                _woods = [Polygon(w).buffer(0) for w in woods]
                _cover_bare += _woods
                # ...in two steps, the grass THINNING inward (0077: "thinning out over the first few paces under the crowns"):
                # the outer half at the tile's density, the inner half at `WOOD_FRINGE_THIN_KEEP` of it
                _fringe = [wd.difference(wd.buffer(-WOOD_FRINGE_FT * bs / 2.0)) for wd in _woods]
                _fringe_in = [wd.buffer(-WOOD_FRINGE_FT * bs / 2.0).difference(wd.buffer(-WOOD_FRINGE_FT * bs)) for wd in _woods]
                _cover_bare += [Point(cp["cx"], cp["cy"]).buffer(cp["r"] + 2.0) for cp in crescents]
                if pond:
                    _cover_bare.append(shapely.affinity.scale(Point(pond[0], pond[1]).buffer(1.0), pond[2], pond[3]))
                if role != "pasture":  # the SCRAGGLY pines belong to cut-over scrub, NOT to open pasture
                    # the plots' sun ground near this throw, gathered ONCE: nothing seats a yard or bed during the scatter, and a
                    # box beyond a pine's reach never meets its crown (the perf-audit, feature 310: it was re-read per pine)
                    _pr = PINE_SPREAD_BS * bs
                    _ps = _pr + self.CANOPY_PAD  # the reach `_crown_covers` asks - the crown AND its pad (a margin of the radius alone missed a box in the pad)
                    _pine_sun = self._sun_keepouts((x0 - _ps, y0 - _ps, x1 + _ps, y1 + _ps))
                    for _ in range(max(2, int(area / (6000 * bs * bs)))):  # a few SCRAGGLY hill pines (sparse, individual, open)
                        px, py = random.uniform(x0 + 6, x1 - 6), random.uniform(y0 + 6, y1 - 6)
                        if _fr is not None and not (_fr[0] <= px <= _fr[2] and _fr[1] <= py <= _fr[3]):
                            continue
                        if _sparse(px, py, 0.5, 14 * bs) or _in_soft(px, py):  # lean = the tallest pine's tip reach, so no pine leans over a crop; and never in the bog
                            continue
                        # ...NOR IN A YARD'S OR BED'S SUN (feature 310): a pine is a tree, its crown its widest branch's reach; recorded
                        # apart (`scrub_pines`) so the map's check sees it, since `tree_crowns` is read as canopy discs elsewhere
                        if self._crown_covers(px, py, _pr, _pine_sun, (), self.CANOPY_PAD):
                            continue
                        self.M.setdefault("scrub_pines", []).append([round(px, 1), round(py, 1), round(_pr, 1)])
                        th = random.uniform(9, 14) * bs
                        marks.append(
                            (px - bs, py - th - bs, px + bs, py + bs, f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{px:.1f}" y2="{py - th:.1f}" stroke="#7A6A48" stroke-width="{1.1 * bs:.1f}"/>')
                        )  # thin trunk; the extents carry a stroke's slack (settlement-review 2026-09-11)
                        for k in range(3):  # sparse open branches - a scraggly wind-cropped pine, NOT a dense crown
                            ly, sp = py - th * (0.45 + 0.25 * k), (3.6 - k) * bs
                            marks.append(
                                (
                                    px - sp - bs,
                                    ly - bs,
                                    px + bs,
                                    ly + 3 * bs,
                                    f'<line x1="{px:.1f}" y1="{ly:.1f}" x2="{px - sp:.1f}" y2="{ly + 2 * bs:.1f}" stroke="#6E8452" stroke-width="{1.0 * bs:.1f}"/>',
                                )
                            )
                            marks.append(
                                (
                                    px - bs,
                                    ly - bs,
                                    px + sp + bs,
                                    ly + 3 * bs,
                                    f'<line x1="{px:.1f}" y1="{ly:.1f}" x2="{px + sp:.1f}" y2="{ly + 2 * bs:.1f}" stroke="#6E8452" stroke-width="{1.0 * bs:.1f}"/>',
                                )
                            )
            # feature 134: the commons' highlight class follows its ROLE; a role the vocabulary does not
            # name yet (pasture) stays unclassed so the census reports it rather than misfiling it
            _ccls = {"woodland": "woodland commons", "grazing": "scrub and rough grazing", "commons": "scrub and rough grazing"}.get(role)
            self._mark_groups.append((self.add(''.join(g), cls=_ccls), marks))  # the crowns now, the dots and pines at finish, into one slot
            random.setstate(st)
            self._cover_n += 1
            if role == "woodland":
                # ...and the parcel is a KEEP-OUT placers actually honor (the Sawada merged-roll
                # review's placer-side ask): nothing packs after the woodland today, but a future
                # placer reading crown records rather than the commons poly would otherwise seat
                # a structure under this canopy with nothing firing. Center-tested by _fits like
                # every block poly.
                self.block_polys.append([(float(px0), float(py0)) for px0, py0 in poly])
            _rx, _ry = ring_center(poly)
            self.M["commons"].append(
                {
                    "x": _rx,
                    "y": _ry,
                    "w": round(x1 - x0, 1),
                    "h": round(y1 - y0, 1),
                    "rot": 0,
                    "role": role,
                    "seq": self._cover_n,
                    **({"crowns": _wd_crowns} if role == "woodland" else {}),
                    "poly": [[round(px, 1), round(py, 1)] for px, py in poly],
                }
            )
            if role != "woodland":
                self._covers.append(Cover("grass", _ccls, [(float(a), float(b)) for a, b in poly], _cover_bare, self.M["commons"][-1]))
                if _fringe:  # the grass under each wood's edge: the zone bare but for the fringe bands, and their own bare ground
                    from shapely.geometry import Polygon as _Poly
                    from shapely.ops import unary_union

                    _rest = [g for g in _cover_bare if not any(g is wd for wd in _woods)]
                    _zone = _Poly([(float(a), float(b)) for a, b in poly]).buffer(0)
                    for _kind, _band in (("wood-fringe", _fringe), ("wood-fringe-thin", _fringe_in)):
                        _outside = _zone.difference(unary_union(_band))
                        self._covers.append(Cover(_kind, _ccls, [(float(a), float(b)) for a, b in poly], [*_rest, _outside], self.M["commons"][-1]))

    def hinterland(  # type: ignore[misc]
        self: Settlement,
        down_deg: Any = None,
        *,
        marsh: bool = True,
        commons: bool = True,
        interior_fill: bool = True,
        pad: float = 90,
        marsh_role: str = "toe",
        scrub_role: str = "grazing",
        skip_sides: Any = (),
        soft_extra: Any = (),
    ) -> None:
        """Lay out a settlement's non-arable HINTERLAND: a reed MARSH at the downhill TOE (below the paddy's
        drainage line, where wet-rice reclamation stops and the valley floor stays reed wetland) and the
        cut-over SCRUB commons (coarse grass + a few scraggly pines) filling the surrounding non-arable margins.
        CHINA-FIRST: the south-China rice hills were stripped for fuel/timber over ~1,000 years, so the DOMINANT
        cover past the settlement is denuded scrub/rough grazing, NOT forest - the protected fengshui grove is
        the green exception, and the managed WOODLAND (coppice / bamboo / tung / tea-oil 'economic forest') is a
        FEW discrete PATCHES the gen adds by hand on the higher / farther ground (`s.commons([...],
        role='woodland')`), set back from the sun-needing crops by the scrub between. So hinterland lays the
        scrub + marsh; the woodland patches are per-map. The scrub bands are frame-margin strips OUTSIDE the
        CULTIVATED bbox (paddy + dry hatake), so each recorded centroid clears the paddy (`commons_clear_of_
        paddies` is a centroid test). All scatters skip fields/pond/lanes/buildings AND a **hamlet keep-out**
        (each farmstead's own grown outline on a nucleated hamlet, so no cover creeps among the houses), and NONE is a
        crop anchor (`_CROP_HARD`), so
        they BLEED off the frame and the crop stays tight. Call AFTER fields + cluster + pond + dry fields,
        BEFORE crop_to_content. `down_deg` (defaults to meta's) picks which frame side the scrub ring OMITS
        (the toe side) AND orients the marsh itself: the toe is a CONTOUR BAND perpendicular to the fall, so it
        rotates with the map like every other feature (see the comment at the marsh block); the scrub ring is
        radial. A comb-FAN field leaves the opposite bbox corner open; the interior fill (`interior_fill`) clothes the
        voids, and the woodland patches are drawn over them. See research/questions/0078-grass-hills-and-fodder-meadows-kusayama-magusaba.drawing.html.

        Research:
            marsh at the toe - research/questions/0057-marshes-and-wetlands-shitchi.drawing.html: the reed marsh on the downhill toe band
            scrub ring - research/questions/0078-grass-hills-and-fodder-meadows-kusayama-magusaba.drawing.html: scrub on the frame strips round the cultivated ground and the toe's flank
            interior voids grazed - research/questions/0078-grass-hills-and-fodder-meadows-kusayama-magusaba.drawing.html: the ground a fan leaves inside its own box clothed as rough grazing
            no cover among the houses - UNRESEARCHED: 44 px round each farmstead, or each homestead on a dispersed map
            woodland per map - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: the coppice patches added by the generator, not here"""
        if down_deg is None:
            down_deg = self.M.get("meta", {}).get("down_deg", 90)
        polys = self.field_polys
        if not polys:
            return
        xs = [p[0] for poly in polys for p in poly]
        ys = [p[1] for poly in polys for p in poly]
        for dp in self.M.get("dry_plots", []):  # the CULTIVATED extent includes the dry hatake plots
            xs += [p[0] for p in dp["poly"]]
            ys += [p[1] for p in dp["poly"]]
        fx0, fx1, fy0, fy1 = min(xs), max(xs), min(ys), max(ys)
        W, H = self.W, self.H
        dx, dy = math.cos(math.radians(down_deg)), math.sin(math.radians(down_deg))
        # SETTLEMENT KEEP-OUT, so cover never scatters among the dwellings. Its SHAPE depends on the form:
        avoid: list[Any] = []
        hs = self.M.get("houses", [])
        m = 44
        if hs and self.M.get("meta", {}).get("nucleated", True):
            # NUCLEATED: the houses are one blob, so the HULL of their positions, grown by the margin, is the built
            # footprint. It was the axis-aligned BBOX, which is the same thing only for a round cluster: on a diagonal
            # ribbon (Sawada, drawn aspect 4) the bbox took in open ground far off the houses and the scrub stopped
            # along ruler-straight north-south and east-west lines round an empty rectangle (settlement-review,
            # feature 261: 0 blade bases in a 50 ft band against 219 just beyond it). Each house point is grown by
            # the margin in eight directions before the hull is taken, so the keep-out clears every house by `m`.
            # ...AND EVERY PART OF THE FARMSTEADS, NOT ONLY THE HOUSES (settlement-review of Kuwabata, feature 261): a hull of
            # house centers left a fringe farmstead's privy, heap and garden outside it, with scrub on three sides of the
            # privy - where the record puts them in the homestead's own work yard. Each part's footprint corners join the
            # house points, grown by the same margin.
            # ...AND NOT ONE HULL ROUND THEM ALL (settlement-review of Kuwabata, feature 261): a single convex hull took in open
            # ground more than a dooryard from any house, where the copse may not stand either, and left a bare wedge 240 x
            # 270 ft with a straight 430 ft edge inside the cluster. Each farmstead's own grown outline is kept clear, and so
            # is the ground between two farmsteads near enough to share it (`FARMSTEAD_NEIGHBOR_FT`); wider open ground
            # carries the scrub the rest of the map does.
            avoid += farmstead_keepouts(self.M, m)
        elif hs:
            # DISPERSED: the farmsteads RING the settlement, so a bbox of their positions is not their footprint
            # - it is the WHOLE MAP, and using it forbids ground cover everywhere inside the ring. That is what
            # left Akagahara's fan void as bare clay (GM: "a ton of empty space between the ditch and the
            # marsh"): the void fell inside this blanket, so neither the scrub ring nor anything else could
            # clothe it. Keep out each HOMESTEAD individually instead - house plus its bundle (yard, garden,
            # grove) - so the open ground BETWEEN the strewn farms is free to carry rough grazing, as it should.
            for key in ("houses", "gardens", "threshing_yards", "groves"):
                for r in self.M.get(key, []):
                    hw, hh = r.get("w", 40) / 2 + m, r.get("h", 30) / 2 + m
                    avoid.append([(r["x"] - hw, r["y"] - hh), (r["x"] + hw, r["y"] - hh), (r["x"] + hw, r["y"] + hh), (r["x"] - hw, r["y"] + hh)])
        # which frame side is the downhill TOE (marsh) - the other three carry the scrub commons
        toe_side = ("bottom" if dy >= 0 else "top") if abs(dy) >= abs(dx) else ("right" if dx >= 0 else "left")

        BLEED = 120  # a band reaches the canvas edge + this bleed, NOT `outer` beyond it
        # (clamping the OUTER extent to the canvas avoids scattering a huge off-canvas apron of scrub that only
        #  bloats the SVG node count - the frame clips it anyway; the on-canvas cover is unchanged)

        def ring(inner: float, outer: float) -> list[Any]:
            """The four picture-frame side-strips between the cultivated bbox grown by `inner` and by `outer`
            (outer clamped to the canvas + bleed), MINUS the toe side (marsh) and any `skip_sides` (e.g. a forest
            flank). Each strip lies outside the bbox -> centroid clears the paddy."""
            ox0, oy0 = max(-BLEED, fx0 - outer), max(-BLEED, fy0 - outer)
            ox1, oy1 = min(W + BLEED, fx1 + outer), min(H + BLEED, fy1 + outer)
            ix0, iy0, ix1, iy1 = fx0 - inner, fy0 - inner, fx1 + inner, fy1 + inner
            sides = {
                "top": [(ox0, oy0), (ox1, oy0), (ox1, iy0), (ox0, iy0)],
                "bottom": [(ox0, iy1), (ox1, iy1), (ox1, oy1), (ox0, oy1)],
                "left": [(ox0, iy0), (ix0, iy0), (ix0, iy1), (ox0, iy1)],
                "right": [(ix1, iy0), (ox1, iy0), (ox1, iy1), (ix1, iy1)],
            }
            return [v for k, v in sides.items() if k != toe_side and k not in skip_sides]

        def toe_strip(inner: float, outer: float) -> list[Any]:
            """The one strip `ring` leaves out - the toe side - for the scrub that flanks the reeds."""
            ox0, oy0 = max(-BLEED, fx0 - outer), max(-BLEED, fy0 - outer)
            ox1, oy1 = min(W + BLEED, fx1 + outer), min(H + BLEED, fy1 + outer)
            ix0, iy0, ix1, iy1 = fx0 - inner, fy0 - inner, fx1 + inner, fy1 + inner
            return {
                "top": [(ox0, oy0), (ox1, oy0), (ox1, iy0), (ox0, iy0)],
                "bottom": [(ox0, iy1), (ox1, iy1), (ox1, oy1), (ox0, oy1)],
                "left": [(ox0, iy0), (ix0, iy0), (ix0, iy1), (ox0, iy1)],
                "right": [(ix1, iy0), (ox1, iy0), (ox1, iy1), (ix1, iy1)],
            }[toe_side]

        # THE TOE SIDE IS NOT ALL MARSH ANY MORE, so the scrub has to finish the job (settlement-review,
        # 2026-08-12). `ring()` drops the whole toe-side strip, which was right while the toe ran edge
        # to edge - the reeds covered every inch below the crop. Now the band is only as wide as the
        # ground the fan waters, so the ground past its lateral ends was covered by NEITHER, and
        # Ikegami shipped a ~267 x 193 ft corner of blank parchment with the connector crossing it
        # (measured 2.2% ink against 23.7% in the scrub band immediately above). Rough grazing is
        # exactly what stands on a dry footslope beside a reed flat, so the toe side gets the same
        # scrub as the other three - handed the marsh as a keep-out, so it stops where the reeds start
        # and the two never overlap. Computed BEFORE the commons pass for that reason.
        # The toe is computed whether or not the marsh is DRAWN on this call: the scrub needs it as a
        # soft keep-out either way, and the hamlet generator draws the marsh and the scrub in two
        # calls (T35) so the coppice scan can run between them.
        toe_poly = self.toe_band(down_deg, pad)
        # ...and EVERY scrub pass gets it, not just the toe strip (GM 2026-08-26, T12): the ring's side
        # strips and the interior fill reach into the toe band too, and the marsh is drawn AFTER them,
        # so `commons()`'s own marsh keep-out cannot see it yet - it has to be handed in.
        # As a SOFT keep-out (see `commons`), and NEVER folded into `avoid`: the marsh call below takes
        # `avoid` too, and a marsh handed its own band draws no reeds at all (measured on the first
        # cut of this fix - the toe went bare).
        # SOFT keep-outs: grass grades into them over the reed feather, woody glyphs stop at the line
        # (`commons` `_in_soft`). The toe marsh (T12), and whatever the caller adds - the hamlet
        # generator passes the WINDBREAK BELT (feature 133 T34, GM 2026-08-27: "Should scrubland
        # overlap with forests? ... it seems like it shouldn't"). Researched: a managed village wood's
        # floor was kept CLEAR - litter raked and undergrowth cut for fuel and paddy fertilizer - with
        # a grass fringe at the edge (the woodland-edge mantle-and-fringe), so brush and pine never
        # stand under the crowns and grass thins out inside the first few paces. The belt is drawn
        # two stages later, so without this the scrub could not see it: Inashiro carried 2,688
        # blades, 158 brush dots and 11 pines inside the belt polygon.
        # ...BUT ONCE A MARSH IS DRAWN, ITS OWN GROUND IS THE KEEP-OUT, NOT THE BAND IT WAS LAID IN (feature 299): the marsh's
        # outline is shaped inside the band (`land.outline`), and the ground it gives up is dry ground the scrub fills -
        # handed the laid band, the scrub left a bare strip between the two. `commons` reads every recorded marsh itself.
        soft = [toe_poly] if toe_poly and not marsh_ground(self.M) else []
        woods = [[tuple(q) for q in sp] for sp in soft_extra]  # every wood: grass reaches only WOOD_FRINGE_FT under its edge
        if commons:
            for p in ring(0, max(W, H)):  # the cut-over SCRUB commons: the DOMINANT denuded-hill cover
                self.commons(p, role=scrub_role, avoid=avoid, soft=soft, woods=woods)  # (managed woodland is added as a FEW patches by the gen)
            if toe_poly and toe_side not in skip_sides:
                self.commons(toe_strip(0, max(W, H)), role=scrub_role, avoid=avoid, soft=soft, woods=woods)
            # ...and the INTERIOR. The ring lays strips only OUTSIDE the cultivated bbox, but an irregular field
            # (a comb FAN) does not fill its own bbox: it leaves open VOIDS INSIDE it that nothing else clothes
            # - the strips are outside them and the marsh is a contour band below them - so they render as BARE
            # ground, the only uncovered land on the map. That is what read as "empty space" on Akagahara. This
            # patch covers the cultivated bbox; since the scatter already skips every field, lane, watercourse,
            # building and keep-out, it can only land in those voids, clothing them as the rough grazing they
            # are. Ground the crop does not use is still ground, and it is grazed. A SOLID field (a polder grid
            # fills its whole bbox, no voids) has nothing to clothe here, so `interior_fill=False` skips it.
            if interior_fill:
                self.commons([(fx0, fy0), (fx1, fy0), (fx1, fy1), (fx0, fy1)], role=scrub_role, avoid=avoid, soft=soft, woods=woods)
        if marsh:
            # The toe is a CONTOUR BAND, not an axis-aligned box. Wet ground is defined by HEIGHT, and every
            # other feature here (field, comb, drain, the marsh_on_low_ground check) resolves height by
            # projecting onto the `down_deg` vector - so the marsh's inner edge must be PERPENDICULAR to that
            # vector too. It was previously a bbox-keyed rectangle, which is only an honest contour when the
            # fall is axis-aligned (0/90/180/270); it was the ONE feature that did not rotate with the map.
            # At a diagonal fall that rectangle slices across the slope: on Kikuta/Hoshigaoka (down=45) its
            # inner edge spanned 205/219px of height and its uphill corner reached ABOVE their entire drain,
            # so it swallowed the ditch and painted reeds over ground that is still at rice height. That made
            # the reeds appear to abut the collector on the diagonal maps but not on due-S Akagahara - a pure
            # artifact of the rotation, which read as a real difference between the maps (GM, 2026-07).
            # Since EVERY collector descends ~19-20 degrees across the contours to reach its tameike, there is
            # genuinely ground below the ditch that is still crop-height on every map; the band now shows that
            # consistently instead of hiding it on two maps out of three.
            self.marsh(toe_poly, role=marsh_role, avoid=avoid)  # reed wetland: the low, undrained downhill toe

    def _clear_ground(self: Settlement, x: float, y: float, w: float, h: float, extra: float) -> None:  # type: ignore[misc]
        """Reserve a swept verge around a sacred/funerary feature: the w x h footprint grown by `extra`,
        added to `self.clearings` so the loose hinterland scatter (commons scrub, marsh reeds) skips it.
        Scaled by the map grain (bscale), so the cleared collar reads at the same real size on any scale.
        The verge's OUTLINE is ORGANIC (irregular bays carved into the padded rectangle), never the
        rectangle itself (GM 2026-07-23): swept ground is PRODUCED by tending - brooms, feet, the sando's
        traffic - radiating from the feature, and its edge sits wherever the tending peters out into the
        scrub; a surveyed straight line belongs to walls and paddy bunds, never to clearage (research/questions/0224-ground-swept-clear-around-shrines-and-graves.drawing.html). The bays are INWARD-ONLY, so the blob always
        stays INSIDE the old padded rect: a collar is a maintenance CLAIM, and making it irregular means
        the sweeping falls short of the surveyed ideal - it never annexes ground (an outward lobe could
        newly overlap a cover that legitimately predates the clearing and flip
        scatter_respects_swept_clearings on a previously-clean map). A bay cuts at most ~55% of the collar,
        so the verge still generously CONTAINS its feature. The blob is seeded from the footprint (the
        saved RNG state keeps the map's stream untouched, so only collar shapes changed pool-wide), and a
        SAME-CENTER duplicate registration (within 4px: the reserve_clearing-then-feature pattern) REUSES
        the first blob verbatim, so guard and late collar can never disagree. Also recorded in
        M['clearings'] with the current cover ordinal, so the checks can verify ORDER: a scatter only
        skips clearings that exist when it runs (scatter_respects_swept_clearings).

        Research:
            swept verge - research/questions/0224-ground-swept-clear-around-shrines-and-graves.drawing.html: a collar of `extra` round a sacred or funerary feature kept clear of scrub
            ragged edge - research/questions/0224-ground-swept-clear-around-shrines-and-graves.drawing.html: inward-only bays up to 0.55 of the collar"""

        def record(poly: Poly) -> None:
            self.M.setdefault("clearings", []).append({"poly": [[round(px, 1), round(py, 1)] for px, py in poly], "seq": self._cover_n})
            self._cull_cover_in(poly)

        for (ocx, ocy), opoly in zip(self._verge_centers, self.clearings, strict=True):
            if abs(ocx - x) <= 4 and abs(ocy - y) <= 4:  # the documented duplicate-registration pattern: reuse the reserved blob
                self.clearings.append(opoly)
                self._verge_centers.append((x, y))
                record(opoly)
                return
        e = extra * self.bscale
        st = random.getstate()
        random.seed(int(abs(x) * 3 + abs(y) * 7 + w * 11 + h * 13 + e))
        x0, y0, x1, y1 = x - w / 2 - e, y - h / 2 - e, x + w / 2 + e, y + h / 2 + e
        amp = 0.55 * e
        edges = [((x0, y0), (x1, y0), (0, 1)), ((x1, y0), (x1, y1), (-1, 0)), ((x1, y1), (x0, y1), (0, -1)), ((x0, y1), (x0, y0), (1, 0))]  # normals point INWARD
        verge = []
        for sa, sb, (nx, ny) in edges:
            for i in range(4):
                t = i / 4
                bx, by = sa[0] + (sb[0] - sa[0]) * t, sa[1] + (sb[1] - sa[1]) * t
                off = random.uniform(0.05, 1.0) * amp * (0.35 if i == 0 else 1.0)  # inward-only bay; damped at the corner so the collar keeps its reach there
                jt = random.uniform(-0.18, 0.18) * amp  # tangential jitter (along the edge)
                vx, vy = bx + nx * off + jt * (1 - abs(nx)), by + ny * off + jt * (1 - abs(ny))
                verge.append(
                    (min(max(vx, x0), x1), min(max(vy, y0), y1))
                )  # clamp: corner-sample jitter must not poke past the padded rect (the blob-is-a-subset guarantee is what makes this pool-safe)
        random.setstate(st)
        self.clearings.append(verge)
        self._verge_centers.append((x, y))
        record(verge)

    def _cull_cover_in(self: Settlement, ring: Poly) -> None:  # type: ignore[misc]
        """Take out of every cover still waiting for the finish (`_covers`) the swept clearing `ring` - its tile leaves the
        ground bare (feature 298) - and out of every scatter (`_mark_groups`) each pine stroke whose extent's middle lies
        inside it (feature 287, woods W10). The scatter skips the clearings that exist when it runs; a clearing swept after it - a household
        shrine seated after the scrub - was dotted over. Its marks are deferred to the finish, so the ground is cleared
        here, where the clearing is made, and the order the two were placed in cannot matter. The clearing is bare, which
        is what it is; no feature moves."""
        xs, ys = [float(q[0]) for q in ring], [float(q[1]) for q in ring]
        x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
        idx = RingIndex(ring)

        def swept(px: float, py: float) -> bool:
            return x0 <= px <= x1 and y0 <= py <= y1 and idx.inside(px, py)

        if len(ring) >= 3:
            from shapely.geometry import Polygon  # bound here, not at import (feature 237)

            swept_ground = Polygon(ring).buffer(0)
            for cover in self._covers:
                cover.bare.append(swept_ground)
        for k, (z, marks) in enumerate(self._mark_groups):
            left = [mk for mk in marks if not swept((mk[0] + mk[2]) / 2.0, (mk[1] + mk[3]) / 2.0)]
            if len(left) != len(marks):
                self._mark_groups[k] = (z, left)
        self.shrink_marshes_off(ring)  # ...and a marsh's reeds culled here leave its record too (woods W08)

    def reserve_clearing(self: Settlement, x: float, y: float, w: float, h: float, extra: float = 46) -> None:  # type: ignore[misc]
        """Pre-register a swept-ground clearing for a sacred/funerary feature a gen draws LATER (e.g. a
        precinct dropped in after crop_to_content, or placed after the hinterland scatter). The scrub/marsh
        scatter only skips clearings that already exist when it runs, so a late precinct must reserve its
        ground FIRST or the scrub covers it. The later shrine_hall/cemetery registers its own clearing too;
        the overlap is harmless. Pass roughly the footprint you will draw (a slightly generous `extra` is
        fine - over-clearing by a few px reads the same).

        Research: cleared collar - research/questions/0224-ground-swept-clear-around-shrines-and-graves.drawing.html: 46 ft cleared round the footprint by default"""
        self._clear_ground(x, y, w, h, extra)
