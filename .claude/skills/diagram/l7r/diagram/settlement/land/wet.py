"""WET GROUND: the reed marsh, the contour band that decides where it lies, the trim that keeps a
way out of it, and the package's one surface-water distance predicate.


The BAND is the load-bearing idea. Wet ground is defined by HEIGHT, so `toe_band` returns a CONTOUR
band perpendicular to the fall rather than an axis-aligned box - a rectangle is only an honest
contour at a 0/90/180/270 fall, and at a diagonal it slices across the slope. Its WIDTH comes from
the ground the fan waters, never from the canvas: an alluvial fan's spring line follows the FAN's
toe, and a floodplain's backswamp is bounded by its natural levees, so wet ground is FEATURE-bounded
in both landforms (research/water.html, 'The wet toe is as wide as the FAN'). Both corrections are
argued at length in the members themselves; read them before changing either.

`surface_water_dist` is module-level rather than a mixin method: it takes a MANIFEST, not a
Settlement, and it is the ONE predicate shared by the gate's `settlement_dwellings_watered` and by
`hamletgen.place_wells` - written that way because the two had drifted into separate definitions of
"needs a well". It lives in this module because it is this package's water-distance question.
`settlement/__init__.py` re-exports it, so consumers import it from `settlement` and never from
here.

Split from settlement/land.py by feature 120 - see settlement/land/CLAUDE.md for the index.
"""

import math
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # shapely's names for the type checker; `_load_shapely` binds the runtime ones
    from shapely.errors import GEOSException
    from shapely.geometry import Polygon as ShapelyPolygon
    from shapely.ops import unary_union

# THE REEDS ARE A TILE (feature 298): the marsh's tint, glints and reed tufts, thrown one by one until then, are the reed tile
# (`land.tiles`) filling the drawn ground less what the tufts were kept off (`Cover`, `Settlement.flush_covers`).
from .._geom import KeepoutGrid, Pt, point_in_poly, seg_dist
from .._knobs import scope_seed
from .outline import natural_outline
from .tiles import Cover

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
    global _SHAPELY_LOADED, GEOSException, ShapelyPolygon, unary_union  # binding this module's own names is the point
    if _SHAPELY_LOADED:
        return
    from shapely.errors import GEOSException
    from shapely.geometry import Polygon as ShapelyPolygon
    from shapely.ops import unary_union

    _SHAPELY_LOADED = True


MARSH_TINT_R = 28.0  # the widest wet-tint circle's radius (x bscale) - also the keep-off a mound owes the tint (feature 150 T54)
MARSH_TUFT_R = 7.0  # the tallest reed blade / widest glint (x bscale) - the same keep-off for the tufts


def pond_fringe_ring(cx: float, cy: float, rx: float, ry: float, margin: float, n: int = 16) -> list[tuple[float, float]]:
    """The reedy MARGIN of a pond, as the polygon `marsh(role="pond_fringe")` scatters (feature 151).

    One helper because there are two call sites and they diverged: the sink's tameike keeps 44 px of fringe,
    a comb source pond 40, and each built the ring by hand. The margins still differ - a tameike is dug and
    its shallows are wider - but the difference is an ARGUMENT now rather than two literals a reader has to
    notice.

    TWO ORDERING RULES BOTH CALLERS OWE, both learned by getting them wrong on 2026-08-29:

    1. Scatter the fringe only AFTER the water it must keep off is recorded. `draw_comb_field` drew it
       before the field's channels existed, so the reed keep-out had nothing to keep off and three blades
       were drawn across the inlet hairline.
    2. Let the pond's own no-build rect (`block_polys`) follow the fringe, never precede it. The reed
       scatter reads `block_polys`, which exists to stop BUILDINGS standing on water; appended first it
       covers the shore band and costs 45% of the annulus - 32 of 54 tufts, measured.
    """
    return [(cx + (rx + margin) * math.cos(a), cy + (ry + margin) * math.sin(a)) for a in [i * math.pi / (n / 2) for i in range(n)]]


MARSH_FEATHER_BS = 46  # the reeds thin to nothing over this band (x bscale) inside the polygon; `commons` thins its scrub INTO the marsh over the same band

if TYPE_CHECKING:
    from ..core import Settlement


def _ellipse(pond: Any, n: int = 64) -> Any:
    """The open water as a polygon: `M['pond']` is (cx, cy, rx, ry)."""
    _load_shapely()
    cx, cy, rx, ry = (float(v) for v in pond[:4])
    return ShapelyPolygon([(cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)])


def _filled(ring: Any) -> Any:
    """A ring as a SOLID - its outline with everything inside it, holes included.

    `buffer(0)` on a self-intersecting outline returns a MultiPolygon (a field outline that pinches or
    crosses itself does), so each part is re-made from its own exterior and the parts unioned. Filling is
    the point: subtracting a dike BAND left the ground it encloses standing, which is the bug this
    function's caller was written to fix."""
    _load_shapely()
    g = ShapelyPolygon([(float(a), float(b)) for a, b in ring]).buffer(0)
    return unary_union([ShapelyPolygon(part.exterior) for part in getattr(g, "geoms", [g]) if part.geom_type == "Polygon" and not part.is_empty])


def _clipped_to_open_ground(poly: Any, dikes: Any, fields: Any = (), pond: Any = None) -> Any:
    """A waterside/toe marsh outline with the DIKED GROUND taken out of it (settlement-review 2026-08-29).

    THREE THINGS ARE SUBTRACTED, and each is ground the scatter already refuses (settlement-review
    2026-08-29, Kuwabata and then Inashiro - the reference hamlet). The keep-out refactor made `wet_polys`
    NO-BUILD, which turned every over-claim in these outlines into a placement rule and into the answer
    the interactive map gives a reader: on Inashiro, **46.7% of the pond-fringe polygon lay inside the
    pond** - it is recorded as a filled disc CONTAINING the water rather than the annulus it draws - and
    the toe polygon covered **88,418 sq ft of the drawn rice fan**, with a field pond inside it. The ink
    was clean in both cases; the record was not. So a fringe loses the open water, and a toe or waterside
    loses the diked block and the fields, which is exactly what `_sparse` already refuses to scatter on.

    A polder's wet wild lies OUTSIDE its perimeter dike; the outline the caller hands in is a generous
    region that laps the dike and the ground it encloses. What is subtracted is the FILLED block - the
    dike band's outer ring taken as a solid - so the enclosed ground goes with it and every mulberry bank
    inside it goes too, which is the half of the GM's T54 complaint the scatter fix did not reach.

    THE FILLED RING, NOT THE BAND (settlement-review 2026-08-29). Subtracting `dk["outline"]` as given -
    a ring 119,693 sq ft in area with no interior - left the enclosed ground standing and got the right
    answer only because `max(parts, key=area)` happened to pick the outside piece: on Kuwabata the toe
    came apart into 1,079,925 sq ft outside and 65,325 sq ft inside the block, and the second was thrown
    away by a rule that was never checking where it was. Filling the ring makes the geometry do what this
    docstring says, rather than the tie-break doing it by luck.

    Returns the largest remaining piece's exterior. Records carry ONE ring, so several pieces cannot all
    be kept; with the block filled, a second piece can only arise where a single `marsh()` call wraps the
    block on two flanks and is cut in half by it, and each flank is its own call.

    NEVER THE INPUT (feature 287, woods W07). This used to hand the outline back whenever shapely returned nothing usable,
    "so a degenerate outline cannot lose a feature" - which drew and recorded the marsh OVER the block and the fields it
    exists to be subtracted from. Now an invalid outline or cut is repaired (`make_valid`) and the difference taken again;
    a marsh with no open ground left, or one no repair can clip, is None - no marsh here - and the caller draws and records
    nothing (`meta.marsh_dropped`)."""
    _load_shapely()
    rings = [list(dk["outline"]) for dk in dikes if len(dk.get("outline") or []) >= 3]
    rings += [list(f) for f in fields if len(f) >= 3]
    if not rings and not pond:
        return poly
    out = None
    for repair in (False, True):
        try:
            keep = ShapelyPolygon([(float(a), float(b)) for a, b in poly]).buffer(0)
            cuts = [_filled(r) for r in rings]
            if pond:
                cuts.append(_ellipse(pond))
            if repair:  # the second try: every piece made valid, the way `buffer(0)` cannot always
                from shapely import make_valid  # noqa: PLC0415 - the repair path only

                keep, cuts = make_valid(keep), [make_valid(c) for c in cuts]
            out = keep.difference(unary_union(cuts))
            break
        except ValueError, GEOSException:
            continue
    if out is None:
        return None
    parts = [g for g in getattr(out, "geoms", [out]) if not g.is_empty and g.geom_type == "Polygon"]
    if not parts:
        return None
    best = max(parts, key=lambda g: g.area)
    return _keyholed(best)


def _signed_area(ring: Any) -> float:
    """Twice a ring's signed area - positive one way round, negative the other. Orientation only."""
    return sum(ring[k][0] * ring[(k + 1) % len(ring)][1] - ring[(k + 1) % len(ring)][0] * ring[k][1] for k in range(len(ring)))


def _keyholed(g: Any) -> Any:
    """A polygon as ONE ring, holes spliced in on a seam.

    A record carries a single ring, and `best.exterior` throws every hole away - which is exactly what
    made the first version of this clip a silent no-op for a pond fringe (settlement-review 2026-08-29,
    Inashiro): the fringe is a filled disc, subtracting the pond turns it into an ANNULUS, and taking the
    exterior handed the disc straight back, still claiming 46.7% of it was the open water it had just been
    clipped off. The earlier docstring predicted a hole "cannot arise here" and was wrong the moment the
    pond became one of the things subtracted.

    A keyhole is the standard answer: cut from the outer ring to the inner one at their closest pair of
    vertices, walk the hole the opposite way round, and come back along the same cut. The seam is
    zero-width, so every point-in-polygon consumer - the keep-out, the checks, the interactive hit test -
    reads the annulus correctly."""
    ring = [(float(x), float(y)) for x, y in g.exterior.coords[:-1]]
    for hole in g.interiors:
        pts = [(float(x), float(y)) for x, y in hole.coords[:-1]]
        if len(pts) < 3 or len(ring) < 3:
            continue
        i, j = min(((a, b) for a in range(len(ring)) for b in range(len(pts))), key=lambda ab: math.dist(ring[ab[0]], pts[ab[1]]))
        loop = pts[j:] + pts[:j]  # the hole, starting at its closest vertex
        if _signed_area(loop) * _signed_area(ring) > 0:
            loop.reverse()  # ...walked the OPPOSITE way round the outer ring, so the seam subtracts
        ring = ring[: i + 1] + loop + [loop[0], ring[i]] + ring[i + 1 :]
    return ring


def pond_cut(blocks: Any, pond: Any, slack: float = 25.0) -> list[Any]:
    """`blocks` with the pond's own no-build box - a block holding the pond's ellipse and reaching no more than `slack` past
    its box on any side - replaced by the ellipse itself (feature 299): the box keeps buildings off the water, and a marsh
    cut by it showed a rectangle round an oval pond. Every other block is kept as it is."""
    if not pond:
        return list(blocks)
    cx, cy, rx, ry = (float(v) for v in pond[:4])
    out: list[Any] = []
    swapped = False
    for b in blocks:
        xs, ys = [float(q[0]) for q in b], [float(q[1]) for q in b]
        if (
            xs
            and min(xs) <= cx - rx
            and max(xs) >= cx + rx
            and min(ys) <= cy - ry
            and max(ys) >= cy + ry
            and min(xs) >= cx - rx - slack
            and max(xs) <= cx + rx + slack
            and min(ys) >= cy - ry - slack
            and max(ys) <= cy + ry + slack
        ):
            swapped = True
            continue
        out.append(b)
    return [*out, ellipse_ring(cx, cy, rx, ry)] if swapped else out


def drawn_ground(poly: Any, fields: Any = (), blocks: Any = (), clearings: Any = (), avoid: Any = (), field_pad: float = 10.0) -> list[Pt] | None:
    """The ground a marsh's reeds are ACTUALLY drawn on: its outline with the scatter's AREA keep-outs taken out, as one
    keyholed ring - or None where nothing is left (feature 287, M7; woods W08).

    THE RECORD WAS THE UNCLIPPED RING (future-work/farming-communities.md, "The toe marsh's recorded outline is not the
    drawn marsh"). The scatter refuses a mark in a paddy (padded `field_pad`), on a building or any other no-build block,
    in a swept clearing and in the caller's `avoid` set, while `M['marshes']` kept the whole outline - so every reader
    asking "is this in the marsh" was told yes about dry, cleared ground: Sawada's belt lost 68 of 179 crowns to an
    outline that ran under the settlement's own cleared ground. These are the SAME rings, pads and families the
    scatter's `KeepoutGrid` holds; the corridors and the mounds are threads and margins, not ground, and stay.

    A record carries one ring, so where a keep-out cuts the marsh in two the largest piece is the marsh - and the scatter
    is then run on that ring (`marsh`), so no reed is drawn on a piece the record does not hold."""
    _load_shapely()
    pts = [(float(a), float(b)) for a, b in poly]
    if len(pts) < 3:
        return None
    try:
        keep = ShapelyPolygon(pts).buffer(0)
        x0, y0, x1, y1 = keep.bounds
        cuts = []
        for ring, pad in [*((f, field_pad) for f in fields), *((r, 0.0) for fam in (blocks, clearings, avoid) for r in fam)]:
            rp = [(float(q[0]), float(q[1])) for q in ring]
            if len(rp) < 3 or min(q[0] for q in rp) - pad > x1 or max(q[0] for q in rp) + pad < x0 or min(q[1] for q in rp) - pad > y1 or max(q[1] for q in rp) + pad < y0:
                continue  # a keep-out beyond the marsh's reach cuts nothing
            g = ShapelyPolygon(rp).buffer(0)
            cuts.append(g.buffer(pad) if pad else g)
        out = keep.difference(unary_union(cuts)) if cuts else keep
    except ValueError, GEOSException:  # pragma: no cover - buffer(0) repairs every ring a placer records [287: a degenerate outline keeps the drop honest]
        return None
    if keep.area > 0.0 and out.area >= keep.area - 1e-6:
        return pts  # nothing the scatter refuses lies in it: the outline IS the drawn ground, vertex for vertex
    parts = [g for g in getattr(out, "geoms", [out]) if not g.is_empty and g.geom_type == "Polygon" and g.area > 0.0]
    if not parts:
        return None
    return _keyholed(max(parts, key=lambda g: g.area))


def marsh_ground(M: Any, only: Any = None, but: Any = ()) -> list[list[Pt]]:
    """Every recorded marsh ring - the ONE reading of "is this in the marsh" (feature 287, M7; woods S3).

    Since M7 a marsh's record IS the ground its reeds are drawn on (`drawn_ground`), so this is the drawn marsh. `only`
    names the roles to read (None: every role), `but` the roles to leave out - the ways leave out the `defense` belt, whose
    approach is a causeway, and the belt's alder reads the toe and the waterside only. Rings of under three points are
    not ground and are skipped."""
    out: list[list[Pt]] = []
    for m in M.get("marshes") or []:
        role = m.get("role")
        if (only is not None and role not in only) or role in but:
            continue
        ring = [(float(q[0]), float(q[1])) for q in m.get("poly") or []]
        if len(ring) >= 3:
            out.append(ring)
    return out


def ellipse_ring(cx: float, cy: float, rx: float, ry: float, n: int = 32) -> list[tuple[float, float]]:
    """An ellipse as an `n`-gon through its rim (feature 297): how a round keep-out - a crescent pond, the pond's water - is filed
    into a `KeepoutGrid` as a ring, its pad the query's own."""
    return [(cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]


def bank_rings(dikeponds: Any, near: Any) -> list[list[tuple[float, float]]]:
    """Every fish pond's mulberry bank near the marsh, WHOLE - each ring as drawn, never thinned (feature 281; the reason is
    at the call in `marsh`). Lifted to module level so a test can hold the whole ring without a scatter to throw into it."""
    return [[(float(mx), float(my)) for mx, my in dp["bank"]] for dp in dikeponds if dp.get("bank") and near(dp["bank"])]


class WetGroundMixin:
    def marsh(self: Settlement, poly: Any, role: str = "toe", avoid: Any = ()) -> None:  # type: ignore[misc]
        """REED MARSH / WET MEADOW - wet reed ground drawn WET and SPARSE, FEATHERED to nothing at the margin like
        the commons (no hard fill edge): a faint blue-green wet tint (soft translucent patches), reed / sedge tufts,
        and a few standing-water glints - a distinctly WET palette, unlike the dry tan scrub commons. Points falling
        IN a paddy or ON the open pond water are skipped, so a generous region ABUTS the field's low edge (the polder
        embankment) or the pond's shore and only fills the wet ground beyond. `role`: 'toe' (default) = the LOW,
        undrained valley toe below the managed paddy, where wet-rice cultivation stops (wet rice is reclaimed FROM
        marsh - polders diked out into marsh/lake; where reclamation stops it stays reed wetland; `marsh_on_low_ground`
        checks this sits downhill); 'pond_fringe' = the reedy shallow MARGIN of a pond (a water-edge fringe, exempt
        from the low-ground rule); 'defense' = an ENGINEERED defensive wet belt maintained outside a fortified
        perimeter (Song Hebei frontier marsh belt, numajiro "marsh castles", the flooded-paddy glacis) - it hugs
        the wall/moat wherever the circuit runs, so it is exempt from the low-ground rule and from
        `roads_clear_of_marsh` (an approach road through the belt is a CAUSEWAY - the corridor skip keeps its
        tread bare - and few, constricted approaches are the belt's military purpose); `defense_marsh_girds_the_walls`
        owns its placement instead; 'waterside' = the un-reclaimed wet WILD outside a polder's perimeter dike on its
        WATERWARD flanks (the fluctuating lake/creek/marsh the dike holds back - exempt from the low-ground rule
        because a polder floor sits BELOW the outside water level, so the wet fringe surrounds it regardless of the
        fall direction; `polder_waterward_flanks_wet` owns its placement, driven by `meta.waterward`). WHY:
        research/water.html 'What ground is too wet to build on?' + 'Defensive marshland - the engineered wet belt' + research/archetypes.html 'Polder siting - full enclosure, fluctuating water and where the village sits'. Recorded M['marshes']."""
        if role not in ("toe", "pond_fringe", "defense", "waterside"):
            raise ValueError(f"unknown marsh role {role!r}; expected 'toe', 'pond_fringe', 'defense', or 'waterside'")
        # THE RECORD SAYS WHAT THE INK SAYS (feature 150 T54 residue, settlement-review 2026-08-29). The
        # scatter keeps reeds off the mounds (see the keep-out below) but the POLYGON was recorded raw, so
        # the interactive map's hit area still answered "marsh" for ground drawn as mulberry dike and pond
        # bank: measured on Kuwabata, 5.2% of the toe polygon - about 61,000 sq ft - lay inside the polder
        # block, covering 5 of 26 bank rings. Clipping the outline to the same ground the marks are allowed
        # is what makes the two agree, and it is done ONCE here so `wet_polys`, `M['marshes']` and the hit
        # polygon are all the same shape. Only the OUTSIDE roles are clipped: a `pond_fringe` is a shore and
        # a `defense` belt hugs its wall, and neither has a polder block to be outside of.
        # ...SHAPED FIRST (feature 299): the laid strips' corners rounded and their edges waved, before the cut-outs below, so where
        # the marsh meets a paddy, a dike or the pond it still follows that feature's edge; a pond's fringe is a narrow ring the
        # shaping would break, and is left as laid. The shaping only takes ground away (`land.outline`).
        if role != "pond_fringe" and len(poly) >= 3:
            poly = natural_outline(poly, scope_seed(self.seed, "marsh_outline", (role, round(float(poly[0][0])), round(float(poly[0][1])))), self.bscale)
        _outside = role in ("toe", "waterside")
        poly = _clipped_to_open_ground(
            poly,
            self.M.get("dikes", ()) if _outside else (),
            self.field_polys if _outside else (),
            self.M.get("pond") if role == "pond_fringe" else None,
        )
        if poly is None:  # no open ground outside the block, the fields and the water: no marsh here (woods W07)
            self.M["meta"].setdefault("marsh_dropped", []).append({"role": role, "why": "no open ground left"})
            return
        # ...AND THE RECORD IS THE GROUND THE REEDS ARE DRAWN ON (feature 287, M7): the outline less every area the scatter
        # below refuses - the padded paddies, the no-build blocks, the swept clearings, `avoid` - one ring (`drawn_ground`).
        # The reed tile fills this ring (feature 298), so the ink and the record are one shape. Nothing left: nothing is drawn
        # or recorded.
        # ...WITH THE POND CUT AS THE POND (feature 299, plan review): the pond's no-build block is a box round its ellipse, kept
        # to stop BUILDINGS standing on water (`pond_fringe_ring`'s note), and cut from the marsh it left a pale rectangle round
        # the oval pond; the marsh is cut by the water itself, the ellipse - its reed fringe stands round it
        _blocks = pond_cut(self.block_polys, self.M.get("pond"))
        # ...AND THE PADDY CUT AT ITS EDGE (GM 2026-10-01, after feature 300: the drains at the foot of the paddy "also appear to
        # have a similar clearance ... fixed in the same way"): the 10 ft a thrown reed kept off a paddy's outline left a bare strip
        # outside the collector drain that runs along it; the marsh meets the paddy, and the drain - a watercourse - is lined by
        # the bank band (`flush_covers`) like any other
        _ground = drawn_ground(poly, self.field_polys, _blocks, self.clearings, avoid, field_pad=0.0)
        if _ground is None:
            self.M["meta"].setdefault("marsh_dropped", []).append({"role": role, "why": "no open ground left"})
            return
        drawn = [(round(px, 1), round(py, 1)) for px, py in _ground]  # at the record's grain, so the scatter keeps a mark in exactly what is recorded
        self.wet_polys.append(list(drawn))
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        bs = self.bscale
        pond = self.M.get("pond")
        halo_rects, halo_circles = self._urban_keepouts((x0, y0, x1, y1))  # the urban-clearance halo (see _urban_keepouts): reeds no more belong in a dooryard than scrub does
        corridors = self._corridor_buffers(3 * bs)  # every trodden tread (lane/street/road), not just lanes
        # PRE-BOX every static keep-out ONCE (see boxed_hit) - the field boxes carry the SAME 10px
        # pad as the edge test below, so the prefilter can never reject a point that test wanted
        # ONE GRID FOR EVERY STATIC KEEP-OUT (feature 218; `KeepoutGrid` carries the argument). The
        # field rings carry the same 10 px pad as the old edge test; the building footprints, the
        # sacred verge and the avoid set are footprints; every trodden tread is a corridor (a
        # causeway/path/road through the marsh stays bare, not reeded over); the urban halo is the
        # closed test it always was. Three families take the MARK'S OWN PAD per query, by slot:
        # REEDS KEEP OFF THE EARTHEN MOUNDS (feature 150 T54, GM 2026-08-28: "the hazy blue that
        # denotes the marsh is clearly overlaid on top of the greenery of the earthen mounds"). A
        # perimeter dike and a fish pond's mulberry bank are raised, maintained, PLANTED earth; reeds
        # root in the shallow standing water OUTSIDE the embankment, so wet ground abuts a mound and
        # never crosses it. The dike band is tested as its CREST plus half of `w_max` rather than its
        # 2,880-point ribbon - the ribbon's bbox covers the whole block, so it pruned nothing and cost
        # 21.7 s of a roll; the trade is one-directional (a pinched stretch keeps reeds a few feet
        # further back, never a mark ON the mound). Both sets are pruned to this polygon's own reach
        # first: a waterward strip lies outside the block, so none of the pond banks can touch it.
        # Slot 1 is the crests, and a mark whose pad is not one of the two mound pads (a narrow
        # fringe's smaller tint) is exempt from them, as it always was; slot 2 the pond banks, by the
        # mark's reach; slot 3 the drawn water - a stream, an irrigation channel, a comb lateral - at
        # its drawn half-width + 2 px + the mark's pad (a pond fringe's reeds keep the 2 px only;
        # settlement-review 2026-08-29: reeds grow AT a ditch's edge, the tuft's own reach against a
        # 2.5 ft inlet cut a bare lane through the fringe).
        _pads = {MARSH_TINT_R * bs, MARSH_TUFT_R * bs}
        _reach = max(_pads) + 40.0
        _near_box = lambda pts: not (min(q[0] for q in pts) - _reach > x1 or max(q[0] for q in pts) + _reach < x0 or min(q[1] for q in pts) - _reach > y1 or max(q[1] for q in pts) + _reach < y0)  # noqa: E731
        _crests = [
            ([(float(mx), float(my)) for mx, my in dk["crest"]], float(dk.get("w_max", 0.0)) / 2) for dk in self.M.get("dikes", []) if len(dk.get("crest") or []) >= 2 and _near_box(dk["crest"])
        ]
        # THE WHOLE BANK, NOT EVERY 16TH OF IT (feature 281). Feature 139 thinned each bank to 16 points ("16 points hold
        # its shape for a keep-out") while every bank was asked per scatter point; the keep-out grid indexes each ring now,
        # so the whole ring costs a cell read. The thinned ring cut every corner of a rectangular bank with a chord, and a
        # reed based 0.8 ft inside a drawn corner passed the keep-out - found when feature 281 moved the marsh's throws
        # (a change it then withdrew, having bought no time: specs/281 Amendment 1).
        _banks = bank_rings(self.M.get("dikeponds", []), _near_box)
        keep = KeepoutGrid()
        keep.rings(self.field_polys, pad=0.0)  # at the paddy's edge (GM 2026-10-01; the note at `drawn_ground` above)
        keep.rings(_blocks)  # the pond as its ellipse, not its building box (`pond_cut`, feature 299)
        keep.rings(self.clearings)
        keep.rings(avoid)
        keep.segs(corridors)
        keep.rects(halo_rects, closed=True)
        keep.circles(halo_circles, closed=True)
        keep.segs(_crests, slot=1, reach=max(_pads))
        keep.rings(_banks, slot=2, reach=max(_pads))
        keep.segs(self._watercourse_segs(0.0), slot=3, reach=max(_pads) + 2.0)
        crescents = self.M.get("crescent_ponds", [])  # read once (feature 218)  # base = the drawn half-width; the query adds 2 px + the mark's pad in the SAME association the linear scan used

        # THE MARSH'S WHOLE REGION IN ONE KEEP-OUT GRID (feature 297, FR-004, plan B2): the crescent ponds and the pond's ellipse -
        # asked point by point beside the grid until now - are filed into it as rings (slot 4 the crescents at the mark's pad,
        # slot 5 the pond grown by the mark's lateral pad, slot 6 the pond moved up by a tuft's blade so no tip crosses its rim),
        # so the ground the reed tile leaves bare is one shape (`KeepoutGrid.shape`, feature 298)
        if crescents:
            keep.rings([ellipse_ring(cp["cx"], cp["cy"], cp["r"], cp["r"]) for cp in crescents], slot=4, reach=2.0 + max(_pads))
        if pond:
            keep.rings([ellipse_ring(pond[0], pond[1], pond[2], pond[3])], slot=5, reach=max(_pads))
            keep.rings([ellipse_ring(pond[0], pond[1] + MARSH_TUFT_R * bs, pond[2], pond[3])], slot=6)

        # THE REEDS ARE A TILE (feature 298, the GM 2026-10-01: "instead of then drawing individual glyphs within that ... some
        # tiled pattern"): the drawn ground is recorded with the ground its tufts were kept off - every keep-out the grid files,
        # at the tuft's own pads (the mounds, the banks, the water, the crescents, the pond) - and `flush_covers` fills the rest
        # with the reed tile (tint, glints and reeds) at the bottom of the stack. Nothing is thrown, so nothing is thrown again
        # once the view is decided (the re-throw of feature 287, M6, is gone with the throw).
        pad = MARSH_TUFT_R * bs
        pond_pad = 2.0 if role == "pond_fringe" else 2.0 + pad
        # (slot 6, the pond moved up a blade so no thrown tip crossed its rim, is a thrown reed's alone: a tile has none, and it left
        # a bare crescent under the pond)
        # (slot 3, the watercourses, at their drawn width alone - feature 300: the 2 ft and a tuft's reach a thrown reed kept
        # off the water left a bare strip down both banks; the reeds stand at the water's edge, and the bank band lines it)
        bare = keep.shape((0.0, pad, pad, 0.0, pond_pad, min(pad, 1.5), None), (x0, y0, x1, y1))
        self._covers.append(Cover("reed", "marsh", [(float(q[0]), float(q[1])) for q in drawn], [bare] if bare is not None else []))
        self._cover_n += 1
        dx0, dx1, dy0, dy1 = min(q[0] for q in drawn), max(q[0] for q in drawn), min(q[1] for q in drawn), max(q[1] for q in drawn)
        self.M["marshes"].append(
            {
                "x": round((dx0 + dx1) / 2, 1),
                "y": round((dy0 + dy1) / 2, 1),
                "w": round(dx1 - dx0, 1),
                "h": round(dy1 - dy0, 1),
                "rot": 0,
                "role": role,
                "seq": self._cover_n,
                "poly": [[round(px, 1), round(py, 1)] for px, py in drawn],  # the drawn ground (feature 287, M7)
            }
        )
        if role != "pond_fringe":  # the wet valley TOE (and the defensive belt) is UNBUILDABLE: register it as a no-build keep-out
            blk = [(round(px, 1), round(py, 1)) for px, py in drawn]
            self.block_polys.append(blk)  # so nothing is placed/dug on a bog (a thin pond-fringe shore ring is exempt)
            self.marsh_blocks.append(blk)  # ...and the scrub scatter treats it as the marsh it is (soft), not as a building (hard)

    def shrink_marshes_off(self: Settlement, ring: Any) -> None:  # type: ignore[misc]
        """A CLEARING SWEPT AFTER THE MARSH TAKES ITS GROUND OUT OF THE MARSH'S RECORD TOO (feature 287, woods W08). The reeds
        inside a clearing swept later - a household shrine seated after the toe was laid - are culled at the sweep
        (`_cull_cover_in`), and the record kept the whole ring, so "is this in the marsh" said yes about the swept verge. Each
        marsh the clearing reaches is recorded again as `drawn_ground` of its own ring less the clearing - the one predicate
        the marsh was first recorded by - and its no-build block and drawn-wet ring with it; a marsh the clearing takes whole
        is dropped as a marsh with no open ground is (`marsh_dropped`)."""
        xs, ys = [float(q[0]) for q in ring], [float(q[1]) for q in ring]
        cx0, cy0, cx1, cy1 = min(xs), min(ys), max(xs), max(ys)
        for rec in list(self.M.get("marshes") or []):
            old = [(float(q[0]), float(q[1])) for q in rec.get("poly") or []]
            if len(old) < 3 or min(q[0] for q in old) > cx1 or max(q[0] for q in old) < cx0 or min(q[1] for q in old) > cy1 or max(q[1] for q in old) < cy0:
                continue
            _load_shapely()
            swept = ShapelyPolygon([(float(q[0]), float(q[1])) for q in ring]).buffer(0)
            # a hundredth of the clearing: a record already cut round it, rounded to a tenth of a pixel, still laps it by a
            # few square pixels along its edge (6 px2 of a 17,400 px2 verge, measured) - that is the record's grain, not ground
            if ShapelyPolygon(old).buffer(0).intersection(swept).area < 0.01 * swept.area:
                continue  # the clearing's box reached the marsh's, its ground did not (or the marsh was laid round it already)
            ground = drawn_ground(old, clearings=[ring])
            new = [(round(float(x), 1), round(float(y), 1)) for x, y in ground] if ground is not None else None
            for fam in (self.block_polys, self.wet_polys):
                for blk in fam:
                    if [(float(q[0]), float(q[1])) for q in blk] == old:
                        blk[:] = new or []  # IN PLACE: the no-build block is the same list in `marsh_blocks` (read by identity)
            self.block_polys[:] = [b for b in self.block_polys if len(b) >= 3]
            self.marsh_blocks[:] = [b for b in self.marsh_blocks if len(b) >= 3]
            self.wet_polys[:] = [b for b in self.wet_polys if len(b) >= 3]
            self._hard_cache_key: tuple[int, ...] | None = None  # the hard ground reads `wet_polys` and is cached on counts only
            if new is None:
                self.M["marshes"].remove(rec)
                self.M["meta"].setdefault("marsh_dropped", []).append({"role": rec.get("role"), "why": "swept clear"})
                continue
            nx, ny = [q[0] for q in new], [q[1] for q in new]
            rec.update(
                poly=[[x, y] for x, y in new],
                x=round((min(nx) + max(nx)) / 2, 1),
                y=round((min(ny) + max(ny)) / 2, 1),
                w=round(max(nx) - min(nx), 1),
                h=round(max(ny) - min(ny), 1),
            )

    def trim_off_marsh(self: Settlement, pts: Any, margin: float = 6.0) -> Any:  # type: ignore[misc]
        """Shorten a way so neither END stands on drawn marshland (GM 2026-08-12).

        A path does not run into a reed bed: it stops on the dry side of it. Only the ENDS are
        walked back, because a way whose MIDDLE crosses wet ground has a routing problem that
        trimming cannot fix - that one has to be re-routed, and `roads_clear_of_marsh` says so.
        Marsh drawn so far is what is checked, so this only helps a way laid AFTER its water; the
        `defense` belt is exempt for the same reason it is exempt from the check (its approach IS a
        causeway, and few constricted approaches are the point of it)."""
        wet = marsh_ground(self.M, but=("defense",))
        if not wet or len(pts) < 2:  # a caller may hand over an already-clipped stub; there is nothing to walk back
            return pts
        out = [(float(q[0]), float(q[1])) for q in pts]

        def soaked(q: Pt) -> bool:
            return any(point_in_poly(q[0], q[1], r) or min(seg_dist(q[0], q[1], r[k], r[(k + 1) % len(r)]) for k in range(len(r))) < margin for r in wet)

        # A skeleton arm is a TWO-point polyline, so the walk must be able to shorten the last leg
        # itself rather than only drop vertices - guarding on `len(out) > 2` trimmed nothing at all
        # on the very map this was written for.
        # ...AND WALKED BACK UNTIL IT IS DRY, not for a fixed count (feature 287, woods W09): sixty 24 px steps stopped a wet leg
        # longer than ~1,440 px with its end still in the reeds. Every pass pops a vertex, returns, or shortens the last leg
        # by 24 px while it is over 30 px long, so the walk ends.
        for _ in range(2):  # once from each end
            while soaked(out[-1]):
                a, b = out[-2], out[-1]
                d = math.hypot(b[0] - a[0], b[1] - a[1])
                if d <= 30.0:  # this whole leg is wet: drop it
                    if len(out) > 2:
                        out.pop()
                        continue
                    # ...AND A WAY WHOLLY IN THE REEDS IS NO WAY (feature 287, woods W09): with its last leg wet and nothing
                    # left to drop, it used to ship the soaked end - the one thing this function exists to prevent. The
                    # caller's own no-way path runs instead (an arm or a spur of fewer than two points is not drawn).
                    return []
                out[-1] = (b[0] - (b[0] - a[0]) / d * 24.0, b[1] - (b[1] - a[1]) / d * 24.0)
            out.reverse()
        return out

    def toe_band(self: Settlement, down_deg: Any = None, pad: float = 90.0) -> list[Pt]:  # type: ignore[misc]
        """The reed-marsh TOE: the contour band below the crop's lowest point, in canvas coordinates.

        FACTORED OUT so it can be asked for BEFORE it is drawn (2026-08-12). `hinterland()` lays the
        marsh late, after the structures, but a WAY has to be routed early - and the GM's rule is
        that a path does not pass through marshland, so the router has to know where the wet ground
        will be while it still has a choice. Deriving it in two places is the trap this skill's notes
        call "placement and its check must read the SAME source", so there is one derivation and both
        callers use it.

        It is a CONTOUR band, not a bbox: wet ground is defined by HEIGHT, so the inner edge is
        perpendicular to the `down_deg` vector like every other height-resolved feature here. An
        axis-aligned rectangle is only an honest contour at a 0/90/180/270 fall, and at a diagonal it
        slices across the slope - which is the bug this shape was given to fix."""
        if down_deg is None:
            down_deg = self.M.get("meta", {}).get("down_deg", 90)
        polys = self.field_polys
        if not polys:
            return []
        dx, dy = math.cos(math.radians(down_deg)), math.sin(math.radians(down_deg))
        ux, uy = -dy, dx  # cross-slope unit vector (the contour direction)
        # ...not a HOMESTEAD field (feature 261): those are laid after the ways, so counting them moved the toe after the seat
        # and the router had been handed it, and Sawada's marsh came out over the connector's handover
        # ...nor a row farm's HOLDING (feature 291), drawn after the seat for the same reason
        cult = [p for poly in polys for p in poly] + [p for dp in self.M.get("dry_plots", []) if not dp.get("homestead") and dp.get("holding") is None for p in dp["poly"]]
        v_in = max(p[0] * dx + p[1] * dy for p in cult) - pad  # inner edge: `pad` ABOVE the crop's lowest point, so the reeds still tuck under the crop
        bleed = 120.0
        corners = [(-bleed, -bleed), (self.W + bleed, -bleed), (self.W + bleed, self.H + bleed), (-bleed, self.H + bleed)]
        v_out = max(c[0] * dx + c[1] * dy for c in corners)  # far enough downhill to leave the canvas
        # THE BAND IS AS WIDE AS THE GROUND THE FAN WATERS, not as wide as the canvas (GM 2026-08-12;
        # researched, see research/water.html 'The wet toe is as wide as the fan, not as wide as the
        # valley'). The cross-slope extent used to come from the CANVAS CORNERS, which drew the
        # valley wet from edge to edge - so a map falling toward its own frame had no dry exit
        # anywhere and every connector had to turn away over the settlement's back. That width was
        # never a rule; it arrived with the 2026-07 fix that made the toe a contour band so it would
        # rotate with the fall, and the rotation was the point.
        #
        # Real wet toes are FEATURE-bounded. On an alluvial fan the water that sinks in the dry
        # mid-fan re-emerges in a spring line at the fan's toe (扇端の湧水帯), and that line follows
        # the fan's own geometry - it is where the permeable fan gravels meet the impermeable floor
        # beneath - not the width of the valley it sits in. Our comb fans ARE that landform. The
        # `pad` shoulder each side is the seepage spreading a little past the watered ground.
        us = [p[0] * ux + p[1] * uy for p in cult]
        u_lo, u_hi = min(us) - pad, max(us) + pad
        cu = [c[0] * ux + c[1] * uy for c in corners]
        u0, u1 = max(min(cu), u_lo), min(max(cu), u_hi)
        # THE INNER EDGE FOLLOWS THE FAN'S TOE, NOT ONE CONTOUR (GM 2026-08-26, feature 133 T30; researched -
        # research/water.html "the marsh follows the fan's toe"). It used to be a single contour through the
        # crop's lowest point anywhere, so on Inashiro the collector, which descends ~20 deg across the
        # contours to reach its pond, left a 324 px wedge of dry ground below its upper reach while the
        # reeds climbed above its lower end - and the boundary ran dead parallel to the frame, which the
        # GM read as a mistake. It was: wet ground at a fan's foot is the spring line where the fan's
        # seepage re-emerges, an ARC along the toe (the 2026-08-12 note already said "curving it would be
        # more faithful"), and MAFF's own drainage standard puts the field-toe interceptor drain (承水路)
        # nearly parallel to the contours - so in reality the toe drain and the wet edge run TOGETHER,
        # and our collector's 20 deg grade is the drawn legibility of a fall that is really ~0.1%.
        # Sampled across the slope: at each cross-slope station the edge sits `pad` above the LOCAL
        # lowest crop point (a window of `pad` each side), so the reeds still tuck under the crop and the
        # collector on every station. Smoothed by a running maximum over three stations so a fan corner
        # cannot notch the band.
        step = max(24.0, pad / 3)
        n = max(2, int((u1 - u0) / step) + 1)
        stations = [u0 + (u1 - u0) * k / (n - 1) for k in range(n)]
        # THE STATIONS READ THE FAN ONLY, never a dry plot (feature 137, cohort seed 14 at 20
        # households). The hem's dry plots are in `cult` so the band's WIDTH and its global floor
        # count them, but a station whose window held only a dry plot - one standing upslope of the
        # settlement, with no paddy within `pad` of that station - took that plot's foot as "the
        # crop's lowest point" and declared every foot of ground below it wet: a 30 ft column of
        # marsh from the plot, straight through two ranks of farmhouses, to the real toe 1,800 ft
        # further down. Nothing drew it (the marsh is inked from the field's foot), but the router
        # walls a path off wet ground, so eight steadings east of the column could not be reached.
        # The research this band encodes (research/water.html, "the wet toe is as wide as the fan")
        # is about the FAN's spring line; a dry plot is not a fan and has no toe.
        fan = [p for poly in polys for p in poly]
        us_fan = [p[0] * ux + p[1] * uy for p in fan]
        vs = [p[0] * dx + p[1] * dy for p in fan]
        local: list[float] = []
        for u in stations:
            near = [v for v, uu in zip(vs, us_fan, strict=True) if abs(uu - u) <= pad]
            local.append((max(near) if near else v_in + pad) - pad)
        edge = [max(local[max(0, k - 1) : k + 2]) for k in range(n)]
        inner = [(u * ux + v * dx, u * uy + v * dy) for u, v in zip(stations, edge, strict=True)]

        # THE LATERAL ENDS FLARE, they do not run ruled to the frame (settlement-review at the T99
        # acceptance, 2026-08-27: the west limit was a straight cross-slope line at u0 from the inner edge
        # to the frame - the same "parallel to the frame" defect T30 fixed on the inner edge, on the side).
        # Seepage at a fan's toe spreads DOWNSLOPE: the wet ground is narrowest where it leaves the
        # watered crop and widens toward the valley floor, so each side bows outward on a rising curve
        # from its inner end to `pad` * 1.5 past the shoulder at the frame. Five stations a side; the
        # closing edge lies beyond the bleed and is never drawn.
        def flank(u_end: float, v_end: float, sign: float) -> list[Pt]:
            return [(uu * ux + vv * dx, uu * uy + vv * dy) for t in (0.2, 0.4, 0.6, 0.8, 1.0) for uu, vv in [(u_end + sign * 1.5 * pad * t**1.6, v_end + (v_out - v_end) * t)]]

        return inner + flank(u1, edge[-1], 1.0) + list(reversed(flank(u0, edge[0], -1.0)))


def surface_water_dist(M: Any, x: float, y: float) -> float:
    """Distance from (x, y) to the nearest SURFACE water - irrigation channel, stream, or moat
    polyline, or the pond's rim - reading exactly the manifest records
    `settlement_dwellings_watered` reads. ONE predicate, shared by that gate check and by
    `hamletgen.place_wells` (known-open ledger 2026-08-16: the well minimax objective counted
    stream-watered houses as needing a well while the check already treated them as watered -
    the objective and the check read two definitions of "needs a well"). Wells are deliberately
    NOT included: the caller asking "does this house need a well" must not have the answer
    pre-empted by the wells it is deciding to dig."""
    # AN IRRIGATION DITCH IS NOT DOMESTIC WATER (ruled 2026-08-18; settlement-review, Sawada, found
    # the mechanism and did the research pass). This used to count `channels` too, and that made the
    # answer depend on WHICH MANIFEST KEY a watercourse happened to be recorded under rather than on
    # what kind of water it is: on a comb-field map `channels` holds one short intake stub while the
    # thirteen real watercourses live in `drawn_channels`, so Sawada counted 13 of 19 houses as
    # watered by a stub, and Mizuguchi's well objective had **zero** clients - it was optimizing
    # nothing at all, silently. Had `drawn_channels` been the key read instead, every house on every
    # comb map would have been "watered" and no hamlet would ever have dug a well.
    #
    # The research says the exclusion is right and only the mechanism was accidental: domestic water
    # came from a well or a spring, while ditch water served washing at a dedicated *kawado* stand -
    # a field ditch is seasonal, silty and fouled by the paddies it feeds, and nobody drank from it.
    # So the predicate now names the water it means. A STREAM is a living watercourse a household
    # draws from; a MOAT and a CANAL are the town/city equivalents, permanent and open; a POND is a
    # tameike. An irrigation channel is field infrastructure, whichever key it is recorded under.
    #
    # Measured cost, and it is the point rather than a side effect: the houses that actually need a
    # well go 5 -> 8 on Inashiro, 3 -> 9 on Kashikawa, 0 -> 5 on Mizuguchi and 6 -> 9 on Sawada, so
    # the minimax objective and the coverage pass finally have the clients the doctrine says they
    # have. The GM may reverse this; it is recorded in `future-work/`.
    d = 1e9
    for ln in [c["poly"] for c in M.get("canals", []) if c.get("poly")] + [st["poly"] for st in M.get("streams", [])] + ([M["moat"]] if M.get("moat") else []):
        for i in range(len(ln) - 1):
            d = min(d, seg_dist(x, y, ln[i], ln[i + 1]))
    pond = M.get("pond")
    if pond:
        d = min(d, abs(math.hypot(x - pond[0], y - pond[1]) - max(pond[2], pond[3])))
    return d
