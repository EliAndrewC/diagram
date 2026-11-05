"""May a bundle STAND here? Every keep-out and clearance predicate, plus the two spatial caches that make asking cheap.

Split from settlement/rolling.py by feature 118 - see settlement/rolling/CLAUDE.md for the index.

Research: keep-out geometry, index and cache plumbing - NONE
"""

from typing import TYPE_CHECKING, Any, cast

from .._geom import Indexed, Pt, edge_dist, point_in_poly, seg_dist, segments_cross
from .._geom.primitives import FIELD_KEEPOUT_EPS, chain_violated, facing_chains, keepout_ring
from ..farm_fixtures import PERSIMMON_CROWN_FT
from ..homestead_parts.tree_shade import CANOPY_SHADE_FT, crown_shades

if TYPE_CHECKING:
    from ..core import Settlement


from .fit_index import _extent_boxed, drop_persimmon, house_extent, houses_meeting, part_box  # noqa: E402,F401 - split at the bar (feature 315)


class BundleFitMixin:
    # WHAT A HAMLET'S SEATING INSTALLS for the fit test (feature 287, plan M3 and M5), None outside it: the access tree
    # (`rolling/access.py`), the households' lots and the byre form their bundles reserve a
    # stall for (`rolling/lot.py`), and - for the one household being sought a seat - which of those parts its bundle carries
    _access: Any = None
    _way_out_anchor: Any = None  # the seating's reach seed past the seat band (feature 320 D1, `stages._seat_households`)
    _way_out_bearing: Any = None  # ...and its lawful bearing out, the gate's (feature 320 D2)
    _lots: Any = None
    _byre_form: str | None = None
    _byre_pockets: Any = None  # the shared sheds' pockets the seating reserved (`detached_commons`, homes H06)
    _fixture_forms: Any = None  # the hamlet's rolled fixture forms, set by the seating (`FixtureForms`)
    _seat_region: Any = None  # the seat region the hamlet's seating offers from (feature 297, `hamletgen/homesteads/region.py`)
    _corridor_ground: Any = None  # the ways' test of a corridor's ground, installed by a hamlet's seating (`access.lawful_ground`)
    _wood: Any = None  # the households' shares of the wood floor (`homestead_parts/wood_share.py`, woods W25)

    def _rect_corners(self: Settlement, rect: Any) -> list[Pt]:  # type: ignore[misc]
        cx, cy, w, h = rect
        return [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)]

    def _poly_bboxes(self: Settlement, polys: Any) -> list[Any]:  # type: ignore[misc]
        """Cached (minx, miny, maxx, maxy) per polygon in `polys`. Rebuilt only when the list GROWS - the
        block-poly list accretes each placed homestead during the solve, but individual polys are never
        mutated - so a length change is a sufficient staleness signal. Lets _rect_hits reject a far polygon
        with 4 comparisons instead of the O(vertices) corner/segment tests. See `_bbox_cache`."""
        cached = self._bbox_cache.get(id(polys))
        if cached is None or cached[0] != len(polys):
            boxes: list[Any] = []
            for poly in polys:
                xs = [p[0] for p in poly]
                ys = [p[1] for p in poly]
                boxes.append((min(xs), min(ys), max(xs), max(ys)))
            cached = (len(polys), boxes)
            self._bbox_cache[id(polys)] = cached
        return cast(list[Any], cached[1])

    def _field_chains(self: Settlement) -> Any:  # type: ignore[misc]
        """THE FIELD EDGE AS A FEW OPEN CHORDS ON THE HOUSE SIDE (feature 140, GM 2026-08-28: *"49-73 verticies still
        sounds like a lot ... just a few line segments on one side of the field that you are checking that you are
        on the correct side of ... not forming a closed shape"*). When the engine has planned the cluster's seat
        (`field_face`, set by hamletgen's `stage_seat`), each field outline becomes the open chain(s) of its
        chords facing that seat - the reference hamlet's 73-vertex outline gives 5 chords - each pushed out by
        the tolerance so no drawn outline lies on the house side of it; a seat is judged by SIDE and by the
        rule's own gap (`chain_violated`). Where no seat is planned (the legacy village roll) a closed ring of
        the simplified outline stands in (`keepout` polygons, as before feature 140 but with a handful of
        vertices). Returns `(chains, rings)`: one of them empty. Cached by the registry's identity and length."""
        polys = self.field_polys
        face = getattr(self, "field_face", None)
        key = (id(polys), len(polys), face, getattr(self, "_fields_ringed", False))  # a scattered hamlet's line asks rings (385 T06)
        cached = getattr(self, "_field_chain_cache", None)
        if cached is None or cached[0] != key:
            if face is not None and not getattr(self, "_fields_ringed", False):
                chains = [c for p in polys if len(p) >= 4 for c in facing_chains(p, face, FIELD_KEEPOUT_EPS)]
                cached = (key, (chains, Indexed()))
            else:
                cached = (key, ([], Indexed([keepout_ring(p, p, FIELD_KEEPOUT_EPS, filled=True)[0] if len(p) >= 4 else list(p) for p in polys])))
            self._field_chain_cache = cached
        return cached[1]

    def _field_blocks_point(self: Settlement, x: float, y: float, gap: float) -> bool:  # type: ignore[misc]
        """Does a field's edge refuse the point (x, y) at `gap`? Chains where the seat is known, rings otherwise."""
        chains, rings = self._field_chains()
        if chains:
            return chain_violated(x, y, chains, gap)
        return any(point_in_poly(x, y, poly) or edge_dist(x, y, poly) < gap for poly, *_ in self._keepout_index(rings, "field_ring_keepout", gap).near(x, y))

    def _field_blocks_rect(self: Settlement, rect: Any) -> bool:  # type: ignore[misc]
        """Does a field's edge refuse this axis-aligned rect? Its four corners and center against the chains (any
        corner on the field side or within the tolerance fails), or the rings by overlap as before."""
        chains, rings = self._field_chains()
        if chains:
            cx, cy, w, h = rect
            return any(chain_violated(px, py, chains, 0.0) for px, py in ((cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2), (cx, cy)))
        return bool(self._rect_hits(rect, rings))

    def _rect_hits(self: Settlement, rect: Any, polys: Any) -> bool:  # type: ignore[misc]
        """Whether an axis-aligned rect overlaps any polygon in `polys` (corner-in, vertex-in, or edge-cross).
        Bbox pre-filters carry the cost: a polygon whose bbox is disjoint from the rect is skipped outright,
        and within an overlapping polygon each EDGE is bbox-tested before the crossing check (this matters for
        the one huge field-envelope polygon, where the rect only ever meets a couple of its many edges). (A
        spatial grid was tried on top of this and measured NOISE-identical: the bbox reject already makes the
        far-poly scan cheap, and the residual cost is the genuine near-overlap math on polys a grid returns
        anyway - so it was not worth the caching complexity.)"""
        cx, cy, w, h = rect
        rx0, ry0, rx1, ry1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
        gc = self._rect_corners(rect)
        for poly, (px0, py0, px1, py1) in zip(polys, self._poly_bboxes(polys), strict=False):
            if px1 < rx0 or px0 > rx1 or py1 < ry0 or py0 > ry1:
                continue  # bboxes disjoint -> cannot overlap
            n = len(poly)
            if any(point_in_poly(px, py, poly) for px, py in gc) or any(rx0 <= vx <= rx1 and ry0 <= vy <= ry1 and point_in_poly(vx, vy, gc) for vx, vy in poly):
                return True
            for k in range(n):  # edge-cross, each edge bbox-gated against the rect
                a, b = poly[k], poly[(k + 1) % n]
                if min(a[0], b[0]) > rx1 or max(a[0], b[0]) < rx0 or min(a[1], b[1]) > ry1 or max(a[1], b[1]) < ry0:
                    continue
                if any(segments_cross(gc[e], gc[(e + 1) % 4], a, b) for e in range(4)):
                    return True
        return False

    def _water_obstacles(self: Settlement) -> list[Any]:  # type: ignore[misc]
        """Cached (poly, keep-out half-width, bbox) for every irrigation LINE a solid bundle rect must avoid -
        feeder channels, in-field/drain ditches, streams. Rebuilt only when one of the three source lists
        changes length (all are laid before the homestead solve, then static). Lets _rect_on_water skip a
        whole course - and then an individual segment - whose neighborhood the rect cannot reach.

        Research: water line keep-out - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P3, 2026-10-25); half the line's width (channel 2.5, ditch 7, stream 9 px by default) plus 5 px"""
        chans = self.M.get("channels", [])
        ditches = self.M.get("field_ditches", [])
        streams = self.M.get("streams", [])
        key = (len(chans), len(ditches), len(streams))
        if self._water_obs_cache is None or self._water_obs_cache[0] != key:
            obs: list[Any] = []
            for lst, base in ((chans, 2.5), (ditches, 7.0), (streams, 9.0)):
                for f in lst:
                    poly = f["poly"]
                    if len(poly) < 2:
                        continue
                    hw = f.get("w", base) / 2 + 5
                    xs = [p[0] for p in poly]
                    ys = [p[1] for p in poly]
                    obs.append((poly, hw, (min(xs), min(ys), max(xs), max(ys))))
            self._water_obs_cache = (key, obs)
        return cast(list[Any], self._water_obs_cache[1])

    def _rect_on_water(self: Settlement, rect: Any) -> bool:  # type: ignore[misc]
        """Whether a SOLID bundle rect (house/yard/garden/shed) lands on an irrigation LINE - a feeder
        channel, an in-field/drain ditch, or a stream. These are dry-ground structures, so a garden or
        yard in a running ditch is wrong (gardens_clear_of_channels), and this keeps the homestead solver
        off the drain outfall that threads the village margin. A hair wider than the check's keep-out so
        the solver leaves room the check then confirms. The GROVE is exempt (it may hug a bund). Bbox
        pre-filters (per course, then per segment) skip the seg_dist / crossing math for anything far off.

        Research: solid parts off running water - research/questions/0035-villages-beside-their-stream-one-bank-or-both.html: a channel ran alongside the house (Harie) and into its grounds (0031), and houses stood on the water (0065) - solid parts are held off running water, a departure the code keeps until feature 417 T33; house, yard, garden and shed held off every irrigation line; the grove exempt"""
        cx, cy, w, h = rect
        gc = self._rect_corners(rect)
        pts = gc + [(cx, cy)]
        rx0, ry0, rx1, ry1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
        for poly, hw, (px0, py0, px1, py1) in self._water_obstacles():
            if px1 + hw < rx0 or px0 - hw > rx1 or py1 + hw < ry0 or py0 - hw > ry1:
                continue  # the whole course is out of reach
            for k in range(len(poly) - 1):
                a, b = poly[k], poly[k + 1]
                if min(a[0], b[0]) - hw > rx1 or max(a[0], b[0]) + hw < rx0 or min(a[1], b[1]) - hw > ry1 or max(a[1], b[1]) + hw < ry0:
                    continue  # this segment is out of reach
                if any(seg_dist(px, py, a, b) < hw for px, py in pts):
                    return True
                if any(segments_cross(a, b, gc[e], gc[(e + 1) % 4]) for e in range(4)):
                    return True
        return False

    def _site_blocks_rect(self: Settlement, rect: Any) -> bool:  # type: ignore[misc]
        """THE BOUNDARY PATH (feature 226, GM 2026-09-12: "a relatively small number of line segments that you were
        checking"): the five ground scans `_rect_blocked` makes below, answered by one outline computed once
        (`hamletgen/homesteads/boundary.py`). The rectangle is asked at NINE points - its corners, its edge midpoints
        and its center - against the site chains at gap 0 (so a member thinner than half a side cannot pass between two
        corners, which covers `_rect_hits`' edge-crossing arm) and against the water corridors at their clearance; its
        center alone against the registered corridors, as `_near_corridor` asks. Exact at the pads every rectangle is
        held to today (spec FR-002)."""
        self._seat_search["rects"] += 1
        cx, cy, w, h = rect
        x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
        pts = ((x0, y0), (x1, y0), (x1, y1), (x0, y1), (cx, y0), (x1, cy), (cx, y1), (x0, cy), (cx, cy))
        chains, corr = self._site_chains, self._site_corridors
        # a point in a cell the site's raster knows clear passes the chains (`FreeGround`, built from the same chains)
        fg = self._free_ground
        if any(chain_violated(px, py, chains, 0.0) for px, py in (pts if fg is None else [p for p in pts if not fg.point_clear(p[0], p[1])])):
            return True
        return bool(corr.hit_points(pts) or corr.hit_center(cx, cy))

    def _rect_blocked(self: Settlement, rect: Any, fields: bool) -> bool:  # type: ignore[misc]
        """Whether a bundle sub-rect lands on forbidden ground: no-build blocks, lanes, hill/pond ellipses,
        irrigation lines, and (only when `fields=True`, i.e. the SOLID house/yard/garden) the flooded
        paddies. The GROVE (fields=False) may HUG a paddy bund, so it is tested against everything BUT the
        fields and the water lines.

        Research: grove may hug a paddy bund - GUESS: searched, the record silent (feature 417 T36 pass P3, 2026-10-25); the grove tested against everything but the fields and the water lines"""
        if self._site_chains is not None:
            return self._site_blocks_rect(rect)  # feature 226: the one outline instead of the five scans below
        if self._rect_hits(rect, self.block_polys):
            return True
        if fields and self._field_blocks_rect(rect):
            return True
        if fields and self._rect_on_water(rect):
            return True
        if fields and not self._hard_clear(rect[0], rect[1], rect[2], rect[3]):
            return True  # HARD ground read from the manifest (crop plots + a field's own ditches)
        cx, cy, w, h = rect
        for px, py in self._rect_corners(rect) + [(cx, cy)]:
            for ex, ey, rx, ry in self.ellipses:
                if rx > 0 and ry > 0 and ((px - ex) / rx) ** 2 + ((py - ey) / ry) ** 2 <= 1:
                    return True
        return self._near_corridor(cx, cy)

    def sun_corridor(self: Settlement, feet: float) -> None:  # type: ignore[misc]
        """Ask the placer to keep `feet` of open ground SOUTH of every threshing yard (see
        `_sun_corridor_ok`). Off by default; a generator opts in.

        Research: hand-drawn maps exempt from the sun rule - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: off unless a generator opts in"""
        self._sun_corridor_ft = float(feet)

    def west_sun_lane(self: Settlement, feet: float) -> None:  # type: ignore[misc]
        """Ask the communal belt (`village_grove`, windbreak mix) to keep `feet` of open ground WEST
        and SOUTHWEST of every threshing yard and garden bed - the afternoon sun. Off by default; a
        generator opts in, exactly as with `sun_corridor` (feature 133 T10, GM 2026-08-25: "the
        windbreak forest ... is so close to the gardens ... that I do not believe that those gardens
        would get sufficient sunlight"). The number's derivation is in research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html.

        Research: windbreak off the plots' afternoon sun - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: `feet` clear west and southwest of every yard and bed"""
        self._west_sun_ft = float(feet)

    def _settle_persimmon(self: Settlement, geom: Any) -> bool:  # type: ignore[misc]
        """Drop this household's persimmon where, as laid, it stands in its own yard's or beds' sun or a standing neighbor's
        (feature 315); whether it was dropped. On the map that keeps the sun corridor.

        Research:
            persimmon out of the plots' sun - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: its own and a neighbor's, a crown's radius plus 1 ft
            no place, no persimmon - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html: dropped rather than moved"""
        tree = (geom.get("fixtures") or {}).get("persimmon")
        if tree is None or not getattr(self, "_sun_corridor_ft", 0.0):
            return False
        reach, r = self.px(CANOPY_SHADE_FT), self.px(PERSIMMON_CROWN_FT + 1.0)
        plots = [p for p in (part_box(geom, "yard"), *(part_box(geom, "gardens") or ())) if p is not None]
        if any(crown_shades(tree[0], tree[1], r, p, reach) for p in plots) or self._persimmon_shades_a_neighbor(geom, tree, r, reach):
            drop_persimmon(geom)
            return True
        return False

    def _persimmon_shades_a_neighbor(self: Settlement, geom: Any, tree: Any, r: float, reach: float) -> bool:  # type: ignore[misc]
        """Does `tree` (this household's persimmon) stand in a standing neighbor's yard's or bed's sun? From the houses index,
        by the crown's box grown by the reach (not to the south).

        Research: persimmon out of a neighbor's sun - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: `CANOPY_SHADE_FT` east, west and south"""
        box = (tree[0] - r - reach, tree[1] - r - reach, tree[0] + r + reach, tree[1] + r)
        for rec in houses_meeting(self.M["houses"], box):
            g = rec.get("geom")
            if not g or g is geom:
                continue
            if any(crown_shades(tree[0], tree[1], r, p, reach) for p in (part_box(g, "yard"), *(part_box(g, "gardens") or ())) if p is not None):
                return True
        return False
