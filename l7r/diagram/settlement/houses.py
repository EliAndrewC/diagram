"""Split from settlement.py by feature 025 - see settlement/CLAUDE.md for the index.
Research: placement, index and corridor plumbing - NONE"""

import math
import random
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, cast

from ._geom import PointGrid, Pt, boxed_polys, drawn_extent, edge_dist, indexed_grid, point_in_poly, poly_seg_dist, rot_rect, seg_dist
from .rolling.access import LANE_MIDDLE_CLEAR_FT, TREAD_WALL_FT
from .rolling.bearing import house_rot
from .rolling.lot import FARMHOUSE_MAX_ASPECT, KURA_SHARE, household_parts, kura_rect, record_parts, seat_parts_done
from .rolling.passage import reserve_way

# HOW FAR A FARMHOUSE WALL STANDS OFF THE PADDY (researched 2026-08-27, feature 133 T41; the record
# in research/questions/0029-farmhouses-minka.drawing.html). The paddy's margin is
# a bund (aze) about 1.5 ft wide (a search-summary figure the session could not read - UNVERIFIED;
# the read source gives ~10 cm high) that is ALSO the working footpath: levees are "constructed and
# maintained to retain water ... and to allow the passage of people and transportation of tools"
# (read, PMC 7538448); a thatched farmhouse's eaves overhang its wall by about 3 ft (the figure
# `FARMHOUSE_EAVE_GAP_FT` already uses; unsourced here). A wall nearer than bund + path + eave puts the roof over the levee path and the drip
# line in the rice. 6 ft is that sum, rounded down: the floor a wall may never cross. A MINIMUM, not
# the norm - the seat band's own 12 px standoff puts the front row 10-13 ft off, which is "right up
# against the edge" as the GM expects. Real feet; `px()` scales it per tier. Held by the gate's
# `houses_clear_of_paddies`.
HOUSE_PADDY_GAP_FT = 6.0
"""Research: farmhouse wall off the paddy - research/questions/0029-farmhouses-minka.drawing.html: a 6 ft minimum, bund plus path plus eave"""
# THE STOREHOUSE ANNEX'S SHARE is `rolling/lot.py`'s `KURA_SHARE` (feature 280 M20: one farm in eight, the headman always),
# the lots' quota and the positional roll's threshold outside the lots alike.
STOREHOUSE_GRAY = "#9A968C"
"""Research: storehouse color - CONVENTION: solid gray, apart from the house's roof color"""

if TYPE_CHECKING:
    from .core import Settlement


class HousesMixin:
    # ---- houses
    def house(self: Settlement, cx: float, cy: float, w: float, h: float, kind: str = "plain", rot: float = 0, shed: bool = False, shed_side: str = "W") -> None:  # type: ignore[misc]
        """Research: farmhouse glyph - research/questions/0029-farmhouses-minka.drawing.html: one rectangle under a ridge line with a door mark, the big and abandoned variants
        farmhouse tones - CONVENTION: wall tones by position, the abandoned house's dashed outline, the gray annex's color
        big farmhouse wing - research/questions/0029-farmhouses-minka.drawing.html: the big house drawn with a wing (0.40 x 0.5 of the house) off its back corner
        ridge at 0.6 of the length - research/questions/0029-farmhouses-minka.drawing.html: the ridge drawn at 0.6 of the house's length, a hipped-roof reading
            its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 0.3 (ridge line); 0.4 (door mark); 0.16 (ruin mark); 0.04 (ruin mark); 0.2 (ruin mark); 0.42 (door mark)
        """
        # POSITION-SEEDED (2026-08-08). A house's wall color is a property of the house, and this
        # was the single most-executed stream draw in the engine - one per house, on every map - so
        # it moved the whole sequence for everything drawn afterwards.
        _plain = ('#C6AC76', '#BEA26C', '#C2A672', '#B89A62')
        pal = {
            "plain": (_plain[int(self._hjit(cx, cy, 13.0) * len(_plain))], '#A98C58', '#5A4326'),
            "big": ('#CFAB64', '#B08C4C', '#4E3A1E'),
            "abandoned": ('#B4AC96', '#9A917A', '#7A7058'),
        }
        light, dark, edge = pal[kind]
        ridge = '#E2CB98' if kind != "abandoned" else '#C7C0AA'
        x0, y0 = -w / 2, -h / 2
        # kura footprint (ox, oy center; sw, sh) in the house's local frame, per side. WEST = a tall block on the
        # west wall (dispersed farms, where the west is free); NORTH = a wide block on the shaded back wall
        # (nucleated farms, where the garden takes the sunnier walls). Shared by the draw + the record below.
        # THE NORTH ANNEX'S PROPORTIONS (feature 280 M18, research/homesteads/440): the sheds dated to the end of the Edo period
        # run about 18-27 ft long and 1.5-1.8 times as long as deep (Hannan 3 x 2 ken; Nerima 8.17 x 4.54 m) - 0.46 of an ordinary
        # 46 ft minka is 21 ft, and 0.45 of its 28 ft depth is 12.6 ft, 1.67 to one; the 1.8-2.4 of the Meiji-Taisho barns is not
        # drawn. It overlaps the back wall by 0.05 h, as before, so the annex reads as joined. `kura_rect` is the one table, and
        # holds the length inside the band (feature 293: on the largest houses the shares alone ran past it).
        _sox, _soy, _ssw, _ssh = kura_rect(w, h, shed_side, self.px(1.0))
        # EMIT WHAT WAS PLACED (feature 121, found by settlement-review on Sawada). This rounded the
        # center to whole pixels and the rake to whole DEGREES, while the placer clears and the gate
        # measure full floats - so after all of this feature's work the drawn quad was still not the
        # tested quad, by up to ~0.5 deg of rake plus ~0.7 px of center: about 0.95 ft at a long
        # minka's corner. Nothing was at risk on any current map (the tightest lane gap is 27 ft),
        # but LANE_CLEARANCE is now DERIVED to the foot, and handing an exact derivation to a
        # renderer that rounds is how the next tightening quietly stops being true. No check can see
        # this: every check reads the manifest, never the SVG.
        g = [f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot:.2f})">']
        if shed and kind == "plain":
            # THE SOLID GRAY STOREHOUSE (research/contents.json#homesteads, 'distinct from the solid gray storehouse'): drawn in the house's roof
            # color it read as a rear wing of an L-shaped farmhouse once feature 280 made it a block (settlement-review of Sawada)
            g.append(f'<rect x="{_sox - _ssw / 2:.1f}" y="{_soy - _ssh / 2:.1f}" width="{_ssw:.1f}" height="{_ssh:.1f}" rx="2" fill="{STOREHOUSE_GRAY}" stroke="{edge}" stroke-width="1.1"/>')
        g.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w}" height="{h / 2:.1f}" fill="{dark}"/>')
        g.append(f'<rect x="{x0:.1f}" y="0" width="{w}" height="{h / 2:.1f}" fill="{light}"/>')
        dash = ' stroke-dasharray="5,3"' if kind == "abandoned" else ''
        g.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w}" height="{h}" rx="3" fill="none" stroke="{edge}" stroke-width="1.5"{dash}/>')
        g.append(f'<line x1="{-w * 0.30:.1f}" y1="0" x2="{w * 0.30:.1f}" y2="0" stroke="{ridge}" stroke-width="2"/>')
        if kind == "big":
            g.append(f'<rect x="{x0 - 1:.1f}" y="{y0 - h * 0.42:.1f}" width="{w * 0.40:.1f}" height="{h * 0.5:.1f}" rx="3" fill="{light}" stroke="{edge}" stroke-width="1.3"/>')
        if kind == "abandoned":
            g.append(f'<polygon points="{-w * 0.16:.1f},{-h * 0.16:.1f} {w * 0.16:.1f},{-h * 0.04:.1f} {-w * 0.04:.1f},{h * 0.2:.1f}" fill="#6E6452" opacity="0.7"/>')
        else:
            g.append(f'<rect x="-3.5" y="{h / 2 - 2:.1f}" width="7" height="3.3" fill="{edge}" opacity="0.85"/>')
        g.append('</g>')
        # ONE string, TWO feature classes (feature 134): the shed rect (g[1] when drawn) is the
        # "storage shed", everything else the "farmhouse"; the shared <g transform> wrapper's opening
        # and closing tags carry no class. Joined byte-for-byte as before - see Settlement.add_parts.
        _shed_drawn = shed and kind == "plain"
        self.add_parts([(None, g[0])] + ([("storage shed", g[1])] if _shed_drawn else []) + [("farmhouse", "".join(g[2 if _shed_drawn else 1 : -1])), (None, g[-1])])
        if shed and kind == "plain":  # record the attached kura so it is first-class + checkable
            th = math.radians(rot)
            self.M.setdefault("farm_sheds", []).append(
                {
                    "x": round(cx + _sox * math.cos(th) - _soy * math.sin(th), 1),
                    "y": round(cy + _sox * math.sin(th) + _soy * math.cos(th), 1),
                    "w": round(_ssw, 1),
                    "h": round(_ssh, 1),
                    "rot": round(rot, 1),
                    "of": [round(cx, 1), round(cy, 1)],
                }
            )

    def _wall_on_the_bund(self: Settlement, x: float, y: float, w: float, h: float, rot: float) -> bool:  # type: ignore[misc]
        """Would any CORNER of this footprint stand nearer than `HOUSE_PADDY_GAP_FT` to a paddy?

        THE CENTER-vs-FOOTPRINT TRAP, found on the reference hamlet (GM 2026-08-27, feature 133 T41:
        *"One of the farmhouses ... appears to actually be touching the edge of the rice paddy
        fields ... actually touching looks wrong to me"*). `_in_blocked` holds the 14 px field
        set-back from the seat's CENTER, so a house 28 ft deep seated 14 px off the paddy stands with
        its wall on the bund - Inashiro had one corner 0.9 ft from the outline while every other
        house stood 10-13 ft off. This tests the rotated corners against the field outlines at the
        wall's own floor (`dev/placement.md`, "gap verdicts read footprints, never centers").
        Research: farmhouse wall off the paddy - research/questions/0029-farmhouses-minka.drawing.html: every rotated corner `HOUSE_PADDY_GAP_FT` plus 1 ft of rounding slack off the field"""
        # THE PLACER HOLDS THE GATE'S FIGURE PLUS THE ROUNDING (feature 137 T06, 2026-08-28): the check tests the
        # corners of the RECORDED footprint, whose center and rake are rounded to 0.1 (see `house()`), so a
        # seat held at exactly 6.0 ft came out at 5.6-5.9 on five of 48 cohort seeds. One foot of slack.
        gap = self.px(HOUSE_PADDY_GAP_FT + 1.0)
        return any(self._field_blocks_point(cx, cy, gap) for cx, cy in rot_rect(x, y, w, h, rot))  # the outline's chords on the house side (feature 140)

    def _in_blocked(self: Settlement, x: float, y: float) -> bool:  # type: ignore[misc]
        """Research: seat set-back from fields, dry plots and hills - research/questions/0029-farmhouses-minka.drawing.html: the center 14 px off a field
        seat set-back from dry plots and hills - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P7, 2026-10-25); the center 12 px off a dry plot or a hill or pond ellipse"""
        # bbox pre-filter (cached, same idea as _rect_hits): a point outside a polygon's bbox - expanded by
        # the 14px field set-back - can neither be inside it nor within 14px of an edge, so skip the O(vertices)
        # point_in_poly / edge_dist. Matters for the one big field envelope and a city's many block polys.
        # INDEXED (2026-08-03), replacing a bbox prefilter that still VISITED every polygon: 419k
        # calls and 12.9s of self time on Minami, whose block_polys accretes one entry per placed
        # homestead. Each grid's boxes carry that registry's own pad, so a zero-pad query is exact
        # and the tests below are the same ones, in the same order.
        if self._field_blocks_point(x, y, 14.0):  # the outline's chords on the house side, not the outline (feature 140)
            return True
        for poly, *_ in self._keepout_index(self.block_polys, "block_keepout", 0.0).near(x, y):
            if point_in_poly(x, y, poly):
                return True
        for poly, *_ in self._keepout_index(self.dry_polys, "dry_keepout", 12.0).near(x, y):
            if point_in_poly(x, y, poly) or edge_dist(x, y, poly) < 12:
                return True  # dry plots are cropland: a building's whole footprint stays off them
        return any(math.hypot((x - cx) / (rx + 12), (y - cy) / (ry + 12)) < 1.0 for cx, cy, rx, ry in self.ellipses)

    def _near_corridor(self: Settlement, x: float, y: float, skip: Any = None) -> bool:  # type: ignore[misc]
        # INDEXED (2026-08-03). This walked every segment of every corridor per candidate seat -
        # 230k calls and 22.6s of self time on Minami, the biggest single cost left in that gen
        # after the well grids. The per-segment bbox test below is unchanged; the grid only decides
        # which segments are worth testing, and each segment's box already carries its clearance,
        # so a zero-pad query is exact. `skip` still works: the index carries each segment's parent
        # polyline, so a frontage row can sit against the street it fronts.
        # `skip` is matched by IDENTITY: a corridor is skipped only when the caller passes the very polyline object it was
        # registered with. (The geometric match the dense frontage rows needed went with the town and city drawing code,
        # feature 392.)
        return any(poly is not skip and seg_dist(x, y, a, b) < clearance for poly, a, b, clearance, *_ in self._corridor_index().near(x, y))

    def _corridor_index(self: Settlement) -> PointGrid:  # type: ignore[misc]
        def build(lst: Any) -> PointGrid:
            grid = PointGrid()
            grid.extend(
                (poly, poly[k], poly[k + 1], cl, min(poly[k][0], poly[k + 1][0]) - cl, min(poly[k][1], poly[k + 1][1]) - cl, max(poly[k][0], poly[k + 1][0]) + cl, max(poly[k][1], poly[k + 1][1]) + cl)
                for poly, cl in lst
                for k in range(len(poly) - 1)
            )
            return grid

        return indexed_grid(self.corridors, "corridor_segs", build)

    def _keepout_index(self: Settlement, polys: Any, key: str, pad: float) -> PointGrid:  # type: ignore[misc]
        """The no-build polygons of `polys` indexed by their bbox, expanded by `pad` so a zero-pad
        query is exact for a rule that also tests `edge_dist(...) < pad`."""

        def build(lst: Any) -> PointGrid:
            grid = PointGrid()
            grid.extend(boxed_polys(lst, pad))
            return grid

        return indexed_grid(polys, key, build)

    def _record_tread(self: Settlement, pts: Any, half: float) -> None:  # type: ignore[misc]
        """Register a way's DRAWN tread, so `_fits` can keep whole footprints off it (see `_on_a_tread`).

        ONLY `lane` calls this today, and the scope is a deliberate decision rather than an oversight. WATER (streams,
        channels, canals, the moat, the aqueduct) is out because its keep-out is `hard_polys`, which is already
        footprint-tested, and so are the BARRIERS (wall, city wall, ward fence), whose corridors are a standoff rather than a
        surface anything is drawn on. The other TRAFFICKED ways - street, alley, road, ring road, towpath - were tried
        (2026-08-12) and reverted the same day: each of them already inflates its corridor by a half-diagonal's worth of
        margin precisely to cover this gap by hand, so the tread test changes no verdict they were getting wrong, and the
        extra tightening cost Tango a public well, tipping `city_well_density_sufficient` into the documented
        well-versus-collision-circle squeeze (this skill's CLAUDE.md, "The collision circle is now blocking FEATURES").
        Extending the registry is one `_record_tread` call per way plus a pool re-roll with a `settlement-review` per map - a
        job, not a side effect. Do it when the collision circle is replaced by a real footprint test, which frees the ground
        those wells need."""
        self.treads.append(([(float(q[0]), float(q[1])) for q in pts], float(half), pts))

    def _on_a_tread(self: Settlement, x: float, y: float, w: float, h: float, skip: Any = None, rot: float = 0.0) -> bool:  # type: ignore[misc]
        """Would a building of this size, at this spot, have any CORNER on a way's drawn tread?

        THE DEBT THIS PAYS (this skill's CLAUDE.md, "placement tests a different footprint than the one drawn"):
        `_near_corridor` tests a candidate's CENTER against a way's soft clearance, so a building whose drawn footprint is
        wider than the placer assumed can stand a legal distance off by its center and still put a corner on the road.
        Measured: a well-off farmhouse (the minka's length varies to 1.35x) ended 2.4 px from a track's centerline with its
        center a legal 34 px away, which `houses_clear_of_lanes` reports as a house standing in the lane.

        The two tests are kept SEPARATE on purpose. Footprint-testing the whole clearance was tried once for `block_polys` and
        reverted, because a clearance is slack that a footprint routinely overhangs by a few px; the TREAD is not slack. So
        the clearance keeps its center test and the tread gets an exact one, its edge `TREAD_WALL_FT` clear of the wall
        (feature 294; it was the 2 px hair `houses_clear_of_lanes` allows).

        `rot` IS THE FOOTPRINT (feature 121). This used to pass 0.0 unconditionally, which made the "exact" test axis-aligned -
        so it measured a square-on rect while the map drew a raked one, the very substitution the paragraph above is about.
        It defaults to 0.0 because most callers seat something genuinely unrotated; a caller that knows its rake passes it,
        and the bundle placer gets it from `_house_rot`. GAP VERDICT family (this skill's dev/placement.md, "CENTER vs
        FOOTPRINT"): real rotated corners, never a center, never a circumscribed radius.
        Research:
            no building corner on a lane - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html, research/questions/0081-village-lanes.drawing.html: nothing built on a lane (0246), the tread's edge `TREAD_WALL_FT`, 3 ft, clear of every wall (0081) - each wall measured whole, not its corners alone
            the lane middle's 7 ft - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: `LANE_MIDDLE_CLEAR_FT`, the 7 ft a lane's middle keeps off a garden fence
            a building's corners held to it - GUESS: every corner of a footprint `_fits` seats (a house's wall, a shed's) held 7 ft off a lane's middle, as the page holds a fence"""
        if not self.treads:
            return False
        quad = rot_rect(x, y, w, h, rot)
        # EACH WALL MEASURED WHOLE (feature 385 T07, impl-drift: the four corners and the center alone let a tread come within
        # the clearance of a long wall's middle, or cross a long house 10 ft off its center): `poly_seg_dist` is zero where a
        # tread crosses the footprint or lies inside it. The half-diagonal box test first passes over a tread segment too far off.
        reach = math.hypot(w, h) / 2
        # ...AND THE TREAD'S EDGE STANDS `TREAD_WALL_FT` CLEAR OF THE WALL (feature 294 B7, the review's "lane tread to house wall"
        # class: one tread ran 3.85 ft from a wall under the 2 ft hair `houses_clear_of_lanes` allowed)
        # ...AND EVERY CORNER `LANE_MIDDLE_CLEAR_FT` OFF THE LANE'S MIDDLE AT LEAST (feature 328 wave 48, 0246: "a lane's middle
        # keeps at least 7 ft clear of a garden fence") - the half-width and the hair held a narrow way's corners nearer
        hair, middle = self.px(TREAD_WALL_FT), self.px(LANE_MIDDLE_CLEAR_FT)
        return any(
            not self._tread_skipped(orig, skip)
            and any(seg_dist(x, y, tp[i], tp[i + 1]) < reach + max(half + hair, middle) and poly_seg_dist(quad, tp[i], tp[i + 1]) < max(half + hair, middle) for i in range(len(tp) - 1))
            for tp, half, orig in self.treads
        )

    def _tread_skipped(self: Settlement, poly: Any, skip: Any) -> bool:  # type: ignore[misc]
        """Is this tread the way the caller is FRONTING, and so exempt?

        `_near_corridor` has excused the fronted way since frontage rows existed, and its own notes
        record what happens when a skip is matched too narrowly: a frontage written as a fresh
        two-point list over a sub-stretch of a street stopped matching by identity and the street's
        own band refused the shops meant to line it - two thirds of the pool's commercial frontage,
        silently. So this matches the same way that one does: identity OR geometry, with either
        polyline allowed to contain the other, since a fronted stretch may be shorter than the way
        or span several of its segments."""
        if skip is None:
            return False
        nested = bool(len(skip)) and isinstance(skip[0], (list, tuple)) and len(skip[0]) == 2 and all(isinstance(v, (int, float)) for v in skip[0])
        for q in [skip] if nested else list(skip):
            if q is poly:
                return True
            if q is None or len(q) < 2 or len(poly) < 2:
                continue
            if all(min(seg_dist(pt[0], pt[1], q[k], q[k + 1]) for k in range(len(q) - 1)) <= 3.0 for pt in poly):
                return True
            if all(min(seg_dist(pt[0], pt[1], poly[k], poly[k + 1]) for k in range(len(poly) - 1)) <= 3.0 for pt in q):
                return True
        return False

    def _fits(  # type: ignore[misc]
        self: Settlement,
        x: float,
        y: float,
        w: float,
        h: float,
        skip: Any = None,
        corridors: bool = True,
        disc: bool = False,
        rot: float | None = None,
        top: float = 88.0,
    ) -> bool:
        """Research: building spacing - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P7, 2026-10-25); 4 px between collision circles (exact boxes where both are declared)
        its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 88 (top sheet margin); 55 (side and bottom sheet margins); 26 (side and bottom sheet margins)
        """
        if x < 55 or x > self.W - 55 or y < top or y > self.H - 26:
            return False
        if self.bound and not point_in_poly(x, y, self.bound):  # stay inside a bounding ring (city wall)
            return False
        if self._in_blocked(x, y) or (corridors and self._near_corridor(x, y, skip)):
            return False
        if self._wall_on_the_bund(x, y, w, h, rot or 0.0):
            return False
        if corridors and self._on_a_tread(x, y, w, h, skip):
            return False
        if not self._hard_clear(x, y, w, h):
            return False
        # INDEXED (2026-08-04), and the history is worth the paragraph. These two scans are
        # O(placed) per candidate seat - 58M hypot() calls on Minami - and indexing them was tried
        # on 2026-08-03 and REVERTED: an incremental index assumed `placed` was append-only, two
        # sites rebind it to a shorter filtered list (search for "lift own reservation" and "drop
        # the un-appurtenanced farmhouse"), and the stale index cost Minami and Nagahara every
        # garden and farm shed. What makes it safe now is `Indexed`, which was built for that
        # lesson: the registry versions ITSELF and carries its own index, so a rebind cannot be
        # missed - the filtered copies below are Indexed too, and each starts with an empty cache.
        # A WELLHEAD IS A DISC, so its own reach is its RADIUS, not the half-diagonal of the
        # probe box around it (2026-08-11). The circumscribed circle is the documented
        # over-restriction in this skill's CLAUDE.md ("CENTER vs FOOTPRINT" item 2); for a round
        # feature it is not an approximation anyone has to live with - min(w, h) / 2 is EXACT, and
        # for a 16 px probe that is 8 px of reach instead of 11.3. This is the one case that can be
        # made exact without first solving the rotated-footprint problem, and it is the case that
        # was blocking the capital: open_seat refused a wellhead at 12, 10 and 8 px in two blocks
        # that the well-density rule says need one.
        r = (min(w, h) / 2) if disc else (math.hypot(w, h) / 2)
        # THE CANDIDATE'S OWN DRAWN EXTENT, when the caller knows its rake (feature 121). `None`
        # means UNKNOWN, not "zero": a caller that does not say keeps the circumscribed circle,
        # because assuming axis-aligned for a candidate the map draws raked would under-state it.
        _cw, _ch = drawn_extent(w, h, rot) if rot is not None and not disc else (None, None)
        for px, py, pw, ph, _pw_drawn, _ph_drawn, *_ in self._reach_index(self.placed, "placed_reach").near(x, y, r):
            # EXACT BOX when BOTH sides have declared what they draw; the circumscribed circle
            # otherwise. The circle refuses seats nothing occupies - measured on a provincial city,
            # 38.7% of all refusals - but it is rotation-invariant, and that invariance is what has
            # been covering for placement dimensions that ignore rake, so it may only be given up
            # where the real extent is known on both sides.
            if _cw is not None and _pw_drawn is not None:
                if abs(x - px) < (_cw + _pw_drawn) / 2 + 4 and abs(y - py) < (_ch + _ph_drawn) / 2 + 4:
                    return False
            elif math.hypot(x - px, y - py) < r + math.hypot(pw, ph) / 2 + 4:
                return False
        return all(math.hypot(x - gx, y - gy) >= r + math.hypot(gw, gh) / 2 + 4 for gx, gy, gw, gh, *_ in self._reach_index(self.grove_rects, "grove_reach").near(x, y, r))

    @staticmethod
    def _reach_boxed(entries: Any) -> Iterator[Any]:
        """(x, y, w, h) footprints boxed by their COLLISION REACH - the half-diagonal `_fits`
        measures against, plus its 4px. Boxing by reach means a query pads by the CANDIDATE's own
        radius alone: anything that could collide has the query point inside its reach box widened
        by r, so it shares a cell with the query span and is never pruned away.

        THE REACH BOX KEEPS THE HALF-DIAGONAL even though the verdict no longer does (feature 121).
        It is a PREFILTER: over-stating an extent can only admit a pair the exact test then rejects,
        while under-stating one starts rejecting before the exact test runs - the index would be
        deciding. Tightening this to match `drawn_extent` would look like a tidy-up and would be a
        bug. (specs/121-placer-drawn-footprint/contracts/placement.md, C1.)

        AN ENTRY MAY DECLARE ITS DRAWN EXTENT, as a trailing `(ew, eh)`. Declaring it opts that
        entry into the exact box verdict; a plain 4-tuple keeps the circle, unchanged. That is
        deliberate rather than a migration half-done: an entry whose stored `w`/`h` is the UNROTATED
        size of a feature the map draws raked would silently under-state itself under a box test,
        and a 90-degree building is the case where that is worst. Opt-in means a site nobody has
        checked cannot become an overlap - it just keeps today's conservative circle.
        `PointGrid` reads the box as the LAST FOUR fields, so the declaration rides in front of it."""
        for px, py, pw, ph, *decl in entries:
            rr = math.hypot(pw, ph) / 2 + 4
            ew, eh = (decl[0], decl[1]) if len(decl) >= 2 else (None, None)
            yield (px, py, pw, ph, ew, eh, px - rr, py - rr, px + rr, py + rr)

    def _reach_index(self: Settlement, registry: Any, key: str) -> PointGrid:  # type: ignore[misc]
        def build(lst: Any) -> PointGrid:
            grid = PointGrid()
            grid.extend(self._reach_boxed(lst))
            return grid

        def add(grid: PointGrid, tail: Any) -> None:
            grid.extend(self._reach_boxed(tail))

        return indexed_grid(registry, key, build, add)

    @staticmethod
    def _hjit(x: float, y: float, salt: float) -> float:
        """Deterministic per-position pseudo-random in [0,1) from (x,y,salt) - jitters a homestead's parts
        (house aspect, garden/yard size + shape) WITHOUT a global RNG draw, so it never ripples other
        placement or household counts (position-seeded, exactly like the wealth tier). Real villages were
        never rows of copy-pasted identical farmsteads; this gives each one its own proportions.

        Research:
            its salts, guards and sentinels - NONE: they decide nothing about the place - 43758.5 (hash constants); 7.373 (hash constants); 12.9898 (hash constants); 4.1414 (hash constants)
        """
        v = math.sin(x * 12.9898 + y * 4.1414 + salt * 7.373) * 43758.5453
        return v - math.floor(v)

    def _house_rot(self: Settlement, cx: float, cy: float) -> float:  # type: ignore[misc]
        """The rake a farmhouse seated at (cx, cy) will be DRAWN at, in degrees.

        ONE DEFINITION, because the placer and the renderer must not each have their own (feature 121): the bundle
        placer once cleared an AXIS-ALIGNED rect and the map then drew the house raked (a corner 2.56 px outside the
        cleared rect on Inashiro), which was the whole of the drawn-versus-placed divergence.

        POSITION-SEEDED: a pure function of the seat's coordinates (see `_hjit`), so the placer knows the exact quad
        before it commits. A hamlet sets `_house_bearing` (269 B18, research/homesteads/400): the common bearing and the
        lane's turn (`rolling/bearing.py`); elsewhere the old +/-5 degree rake stands.
        Research: farmhouse rake - research/questions/0029-farmhouses-minka.drawing.html: the hamlet's bearing rule, else +-5 degrees by position
            its salts, guards and sentinels - NONE: they decide nothing about the place - 11 (salt)
        """
        if self._house_bearing is None:
            return self._hjit(cx, cy, 11.0) * 10.0 - 5.0
        return house_rot(self._hjit, cx, cy, self._house_bearing, self._bearing_follow)

    def _quad(self: Settlement, cx: float, cy: float, w: float, h: float, jit: float, salt: float, level: str | None = None) -> list[Pt]:  # type: ignore[misc]
        """A slightly-IRREGULAR 4-sided polygon INSCRIBED in the (cx,cy,w,h) rect: each corner is pulled
        INWARD by a deterministic, position-seeded fraction (0..jit of the half-span), so the footprint loses
        its perfect 90-degree corners while staying ENTIRELY within its reserved rect - so it can never create
        a new overlap the rect-based placement/checks didn't already clear. Real dooryard plots were bounded by
        paths, walls, and awkward soil, not surveyed to a clean rectangle. `jit` sets how irregular: a garden
        gets more (a hand-worked bed), a threshing yard less (a swept work surface stays near-square). Returns
        the 4 corners [NW, NE, SE, SW] as (x, y) tuples.

        `level` names ONE edge ("N", "E", "S" or "W") whose two corners share a single inward pull, so that edge
        stays straight and parallel to its frame (GM 2026-09-26, of the threshing yard: *"the northern edge
        should be parallel with the house"* - with each corner pulled on its own, the edge facing the house ran
        up to 3 degrees off the house's wall, and the gap read wider at one end). The other edges keep their
        irregularity.
        Research: hand-laid plot outlines - research/questions/0029-farmhouses-minka.drawing.html: corners pulled in by position, the edge toward the house straight and parallel
            its salts, guards and sentinels - NONE: they decide nothing about the place - 0.19 (salt step)
        """
        hw, hh = w / 2.0, h / 2.0
        pulls = [(self._hjit(cx, cy, salt + i * 0.19) * jit, self._hjit(cx, cy, salt + i * 0.19 + 0.5) * jit) for i in range(4)]  # each corner its own inward pull
        if level in ("N", "S"):
            a, b = (0, 1) if level == "N" else (3, 2)
            pulls[b] = (pulls[b][0], pulls[a][1])  # the edge's two corners at one depth
        elif level in ("E", "W"):
            a, b = (1, 2) if level == "E" else (0, 3)
            pulls[b] = (pulls[a][0], pulls[b][1])
        return [(cx + sx * hw * (1.0 - jx), cy + sy * hh * (1.0 - jy)) for (sx, sy), (jx, jy) in zip(((-1, -1), (1, -1), (1, 1), (-1, 1)), pulls, strict=True)]  # NW, NE, SE, SW

    def _toscale(self: Settlement) -> bool:  # type: ignore[misc]
        """Whether this map uses the to-scale HOMESTEAD BUNDLE (house + grove + yard + garden as one packed
        unit, dimensions in FEET drawn at the map's `ftpx`) vs the legacy house-first path + urban glyphs.
        Every VILLAGE does; a HAMLET opts in with `meta(toscale=True)` (village 2 ft/px, hamlet 1). Every POOL
        map is now to-scale (Moritono was the last legacy hamlet, redone water-first); the legacy house-first
        path is kept as a fallback, covered by `test_legacy_dispersed_farmstead_path_still_covered`
        in `tests/settlement/`. Kept as one predicate so every to-scale gate stays in sync."""
        m = self.M["meta"]
        return cast(bool, m.get("toscale", m.get("scale") == "village"))

    def try_place(self: Settlement, x: float, y: float, kind: str, role: Any = None, size: Any = None) -> bool:  # type: ignore[misc]
        """Place one farmhouse as a to-scale HOMESTEAD BUNDLE (house + grove/garden + yard, reserved and packed as ONE unit).
        `size=(w,h)` overrides the kind's default footprint (base FEET) so farmhouses can be individually sized. (The house-first
        path a map not drawn to scale took went with the frozen maps' code, feature 392.)"""
        return self._try_place_bundle(x, y, kind, role, size)

    def _try_place_bundle(self: Settlement, x: float, y: float, kind: str, role: Any = None, size: Any = None) -> bool:  # type: ignore[misc]
        """Seat one to-scale homestead bundle.
        Research:
            farmhouse size - research/questions/0029-farmhouses-minka.drawing.html: 46 x 28 ft base, by the lot's ladder or 0.85-1.35 x 0.90-1.10; dispersed 0.9 / 1.0 / 1.12 by position, big 64 x 40
            storehouse - research/questions/0040-farm-storehouses-kura.drawing.html: one farm in eight by count (else by position), the headman always, on the north wall
            a farmhouse no longer than 2.7:1 - research/questions/0029-farmhouses-minka.drawing.html: `FARMHOUSE_MAX_ASPECT`, the length and depth jitter's 1.3-2.7 bar; a caller's longer house is refused
            its salts, guards and sentinels - NONE: they decide nothing about the place - 0.2 (depth spread 0.90 to 1.10; the branch is dead (0029 would cite it)); 30 (0.9 / 1.0 / 1.12 tier split; the branch is dead); 53 (hash multipliers); 29 (hash multipliers); 80 (0.9 / 1.0 / 1.12 tier split; the branch is dead)
        """
        # a farmhouse shares the MAP'S building grain (bscale): at village/hamlet scale bscale is
        # 1.0 (full size), but a town/city compresses its urban buildings, and a peasant farmhouse
        # must not render LARGER than the samurai and merchant houses inside the walls - so it
        # scales down by the same factor.
        if kind == "abandoned":  # a lone derelict ruin - no homestead bundle
            w, h = self.px(46), self.px(28)  # the 46x28 ft minka, at this map's ft/px
            if not self._fits(x, y, w, h):
                return False
            self.placed.append((x, y, w, h))
            # POSITION-SEEDED, not a stream draw (2026-08-08): a farmhouse's rake is a property of
            # the house, not of how many houses preceded it. See _hjit - "so it never ripples other
            # placement or household counts" - which is the convention this line was missing.
            rec = {"x": x, "y": y, "w": w, "h": h, "kind": kind, "rot": self._house_rot(x, y), "role": role, "shed": False, "wealth": 1.0}
            self.M["houses"].append(rec)
            self._pending_farmsteads.append(rec)
            return True
        # TO-SCALE HOMESTEAD BUNDLE: an occupied farmstead is placed as ONE unit - house + windward grove +
        # threshing yard + dooryard garden - reserved and overlap-checked together so the grove always keeps
        # its ~6:1 room (the fix for groves never reaching target under end-reconciliation). Dimensions are in
        # FEET, drawn at this map's ftpx (village 2 ft/px, hamlet 1): the plain house is the 46x28 ft 8:5 minka
        # (px(46) = 23px at 2 ft/px). A modest, position-seeded wealth tier scales the whole bundle. See
        # research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.html ('How far is it across this map? The scale, tier by tier'.
        # THE HOUSEHOLD'S PARTS (feature 287, plan M5): its lot - the k-th plain household seated takes lot k, its size
        # rung, its kura and its beast, whatever seat it lands on (`rolling/lot.py`)
        _lot, _byre_form = household_parts(self, x, y, kind, role)
        if size is not None:  # explicit footprint in FEET (e.g. a larger headman)
            if max(size) > FARMHOUSE_MAX_ASPECT * min(size):  # a caller's input error, not a map check (homes H08)
                raise ValueError(f"a farmhouse of {size[0]} x {size[1]} ft runs past {FARMHOUSE_MAX_ASPECT}:1 - it would read as a shed")
            wf, hw, hh = 1.0, self.px(size[0]), self.px(size[1])
        elif _lot is not None:  # the size ladder (homes H17): the footprints spread by construction
            wf, hw, hh = 1.0, self.px(46) * _lot[0], self.px(28) * _lot[1]
        elif getattr(self, "_nucleated", False):
            # a minka grew by adding BAYS (ken) along the ridge, so a bigger farmhouse is LONGER far more
            # than it is wider (the roof span caps the depth) - vary length a lot, depth only a little, so
            # houses are individually proportioned (some long, some near-square) but always within the
            # ~1.3-2.5:1 minka norm, never uniformly scaled copies. Position-seeded (no RNG ripple).
            wf = 1.0
            hw = self.px(46) * (0.85 + self._hjit(x, y, 1.0) * 0.5)  # length factor [0.85, 1.35]
            hh = self.px(28) * (0.90 + self._hjit(x, y, 2.0) * 0.2)  # depth factor  [0.90, 1.10]
        else:
            bw, bh = (64, 40) if kind == "big" else (46, 28)  # base minka in FEET
            t = int(abs(x) * 53 + abs(y) * 29) % 100
            wf = 1.0 if kind == "big" else (0.9 if t < 30 else (1.12 if t >= 80 else 1.0))
            hw, hh = self.px(bw) * wf, self.px(bh) * wf
        # a fireproof KURA storehouse is a WEALTH MARKER, not universal - it attaches to the house on about ONE FARM IN EIGHT
        # (feature 280 M20, research/homesteads/720: Kakimochi's count, 2 of 16 households, both powerful; the ~30% it was drawn
        # at came from Sugiura's 1972 count, modern) of
        # plain farms (position-seeded off the SEED spot, no RNG ripple; a ruin has none). The HEADMAN always
        # has one (GM 2026-07-21): the shoya/nanushi is by definition among the village's most prosperous
        # farmers - historically the land-opening family - AND the office needs one functionally: the headman
        # kept the village's tax ledgers, land registers, and tax rice awaiting collection, exactly what
        # fireproof kura storage is for. Leaving him on the ~30% dice let all four pool headmen roll bare
        # (chance masquerading as doctrine); headman_has_kura gates it now. It goes on the
        # NORTH (back) wall of a nucleated house: the cluster hugs the field to the EAST so a house's garden takes
        # the west/sunny walls but never the shaded NORTH, so a north kura is clear of it - and its footprint is
        # RESERVED in the homestead bundle so a neighbor never lands on it. Drawn + recorded in farmsteads() so
        # it always moves WITH the house (farm_sheds_attached guards it).
        # ...A COUNT, NOT A PER-SEAT ROLL, where the household carries a lot (homes H45): exactly round(n x `KURA_SHARE`) of n
        # seated households keep one, where the positional roll aliased along a row and under-delivered 2.2x.
        _shed = kind == "plain" and (role == "headman" or (_lot[2] if _lot is not None else self._hjit(x, y, 3.0) < KURA_SHARE))
        try:  # a keeper's byre and a well pocket are parts of the bundle: the envelope is sought with them in it (H06, H10)
            spot = self._place_bundle(x, y, hw, hh, shed=_shed)  # pack the bundle (incl. the reserved kura) near (x,y)
        finally:
            seat_parts_done(self)
        if spot is None:
            return False
        cx, cy, geom = spot
        self.placed.append(geom["bbox"])  # reserve the whole homestead footprint as one rect
        rec = {
            "x": cx,
            "y": cy,
            "w": hw,
            "h": hh,
            "kind": kind,
            "rot": self._house_rot(cx, cy),
            "role": role,
            "shed": _shed,
            "shed_side": "N",
            "wealth": wf,
            "geom": geom,
        }  # rot position-seeded, like _shed above
        reserve_way(self, rec, geom, (cx, cy))  # its corridor reserved (feature 287, plan M3), or its walk across a yard (feature 317)
        record_parts(self, rec, geom, _byre_form)  # the reserved stall and well pocket, on the record
        self.M["houses"].append(rec)
        self._pending_farmsteads.append(rec)
        return True

    def cluster_seeds(self: Settlement, shape: str, cx: float, cy: float, ex: float, ey: float, n: int, rng: random.Random, record: bool = True) -> list[Pt]:  # type: ignore[misc]
        """Generate `n` house-seed positions for a nucleated cluster of the given SHAPE (feature 005
        `cluster_shape` knob), to feed to `try_place` (the bundle solver then hugs each homestead to the field
        edge). Records `meta.cluster_shape` when `record=True`. Shapes (grounding: research.md D2 - cluster
        shape followed the available dry ground):
          - `round`     - a filled ellipse (a knoll): the classic disk.
          - `elongated` - a long narrow ellipse (a levee / ridge string): stretched along the margin (the ey axis).
          - `crescent`  - positions hugging a shallow arc (a field-edge crescent), concave toward the field.
          - `split`     - two sub-hamlets on either flank (two dry patches flanking the arable).
        Off the flood toe / field-adjacency are enforced downstream by `try_place` (each candidate that is not
        field-adjacent or lands on a blocker is simply rejected), so this only has to SHAPE the seed cloud.
        Research: cluster shape - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: round, elongated, crescent or split, with this method's proportions
            its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N12, 2026-10-25) - 0.55 (elongated seed cloud; the record attests the levee string but gives no ratio, and the placer sets the drawn width); 1.4 (elongated seed cloud; the record attests the levee string but gives no ratio, and the placer sets the drawn width)
            its figures guessed on 0031 - GUESS research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: 0.22 (crescent spread); 0.95 (crescent depth); 0.42 (split sub-clusters); 0.82 (split sub-clusters); 0.62 (split sub-clusters)
        """
        if shape not in ("round", "elongated", "crescent", "split"):
            raise ValueError(f"unknown cluster_shape {shape!r}; expected round / elongated / crescent / split")
        if record:
            self.M["meta"]["cluster_shape"] = shape
        out: list[Pt] = []
        for _ in range(n):
            a = rng.uniform(0, 2 * math.pi)
            r = rng.random() ** 0.5
            if shape == "round":
                out.append((cx + math.cos(a) * r * ex, cy + math.sin(a) * r * ey))
            elif shape == "elongated":  # narrow across the margin, long along it
                out.append((cx + math.cos(a) * r * ex * 0.55, cy + math.sin(a) * r * ey * 1.4))
            elif shape == "crescent":  # a curved band, concave toward the field, NARROW across the margin.
                # The old form spread wide (x1.15 lateral) with the horns curved hard back, so the placer -
                # which pulls every house to hug the paddy and packs ALONG it - strung them into a wide, hollow
                # arc that stranded the horns far from the crops (Kikuta: 55 houses over a hull filled ~20%, NE
                # horn ~400px from any field; see village_cluster_compact / research/questions/0032-how-our-maps-pack-a-clustered-villages-houses.drawing.html).
                # WIDTH is what the placer amplifies, so keep the lateral reach narrow (a nucleated village is a
                # deep blob, not a wide ribbon) and let the depth carry the frontage, with a gentle concave bow.
                t = rng.uniform(-1.0, 1.0)
                depth = rng.random() ** 0.5
                bx = cx + t * ex * 0.5 + math.cos(a) * ex * 0.22 * depth
                by = cy + (t * t - 0.5) * ey * 0.5 + math.sin(a) * ey * 0.95 * depth
                out.append((bx, by))
            else:  # split: two sub-disks on the flanks
                side = -1.0 if rng.random() < 0.5 else 1.0
                out.append((cx + side * ex * 0.62 + math.cos(a) * r * ex * 0.42, cy + math.sin(a) * r * ey * 0.82))
        return out

    def cluster_anchor(  # type: ignore[misc]
        self: Settlement, position: str, field_bbox: tuple[float, float, float, float], down_deg: float, lateral_frac: float = 0.6, depth_frac: float = 0.34
    ) -> tuple[float, float, float, float]:
        """Resolve the `cluster_position` knob into a cluster ANCHOR `(cx, cy, ex, ey)` to feed `cluster_seeds`.
        The knob says WHERE on its field's dry margin a nucleated village sits; this reads that against the
        field's bbox and its `down_deg` fall line and returns a center just OFF the paddy plus screen-axis
        half-extents (`ex`, `ey`) oriented so the cluster runs ALONG that margin. (Field-adjacency + off-the-toe
        are still enforced downstream: `try_place` rejects any seeded house that is not field-adjacent or lands
        on the flood toe / a blocker, so this only has to aim the cloud at the right dry ground.)

        Grounding (research.md D2 - villages took the best DRY ground beside their paddy, 背山面水 'mountain
        behind, water in front'; which dry ground was available varied, and that variation is the knob):
          - `high_margin`  - the upslope (high) edge, centered: the classic back-to-the-hill seat. DEFAULT.
          - `valley_head`  - the high edge but tucked to one cross-slope corner (a head terrace by the intake).
          - `mid_margin`   - the high edge, offset the other way along the margin (partway along, not centered).
          - `flank`        - a cross-slope SIDE margin (a side levee / valley wall), off to one flank.
          - `valley_mouth` - down by the low end where the valley opens, but pulled to the dry lateral shoulder
                             (NEVER straight down into the wet central toe below the drain).
          - `on_rise`      - a dry knoll off a high corner (a rise standing a little out of the plain).
        Research: cluster position - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: six margins of the field, the cluster along the margin, depth capped at 118 px
            its salts, guards and sentinels - NONE: they decide nothing about the place - 0.6 (lateral and depth fractions (no caller)); 0.34 (lateral and depth fractions (no caller)); 22 (clearance (no caller)); 0.3 (lateral offsets (no caller)); 0.45 (valley-mouth offset (no caller))
        """
        if position not in ("high_margin", "valley_head", "mid_margin", "flank", "valley_mouth", "on_rise"):
            raise ValueError(f"unknown cluster_position {position!r}")
        fx0, fy0, fx1, fy1 = field_bbox
        fcx, fcy = (fx0 + fx1) / 2, (fy0 + fy1) / 2
        hw, hh = (fx1 - fx0) / 2, (fy1 - fy0) / 2
        dx, dy = math.cos(math.radians(down_deg)), math.sin(math.radians(down_deg))  # downhill unit
        ux, uy = -dy, dx  # cross-slope (lateral / along-margin) unit
        ad = abs(dx) * hw + abs(dy) * hh  # field half-extent along the fall
        au = abs(ux) * hw + abs(uy) * hh  # field half-extent across the fall (the margin's run)
        lat = au * lateral_frac  # the cluster runs ALONG the margin (lateral)...
        dep = min(
            max(ad, au) * depth_frac, 118.0
        )  # ...but stays fairly shallow: the near rows ring the field (field_ringed), the back rows are a legit cluster-span back (cluster_abuts_fields allows it for a nucleated seat)
        clr = dep + 22.0  # the along-slope clearance: the cluster's near edge sits `pad`-ish off the paddy, whole cluster clear
        # (along-slope offset s: -ve = uphill of center; lateral offset t along +u)
        # high-margin lateral offsets stay MODEST (a fan field is narrow at its head, so the bbox overstates
        # how far a high-corner cluster can slide and still sit over the paddy) - the flank/mouth positions push
        # fully out to a cross-slope side where the field is at full width.
        if position == "high_margin":
            s, t = -(ad + clr), 0.0
        elif position == "valley_head":
            s, t = -(ad + clr), -au * 0.3
        elif position == "mid_margin":
            s, t = -(ad + clr), au * 0.3
        elif position == "flank":
            s, t = 0.0, au + clr
        elif position == "valley_mouth":
            s, t = ad * 0.45, au + clr  # low-ish AND pushed to the dry lateral shoulder, never the central toe
        else:  # on_rise: a dry knoll at a HIGH CORNER (up, and a little laterally) - still hugging the high margin
            s, t = -(ad + clr), au * 0.3
        cx = fcx + dx * s + ux * t
        cy = fcy + dy * s + uy * t
        ex = abs(ux) * lat + abs(dx) * dep  # project the lateral+depth extents back onto screen x / y
        ey = abs(uy) * lat + abs(dy) * dep
        return (cx, cy, ex, ey)

    def plot_texture(self: Settlement, plot_size: str = "medium", plot_regularity: str = "organic", record: bool = True) -> tuple[float, tuple[float, float]]:  # type: ignore[misc]
        """Resolve the `plot_size` + `plot_regularity` knobs into `carve_comb`'s `(plot_across, row_step)` levers
        so they actually change the paddy grain. `plot_across` sets how many bunded plots tile across each canal
        reach (small = many small paddies, large_block = few big ones, strip = narrow but long); `row_step` is
        the along-canal row spacing, and its SPREAD is the regularity: a WIDE spread reads organic/old-grown, a
        TIGHT spread reads as a planned/surveyed grid. Records the two knobs on the manifest. Grounding: old
        wet-rice terraces grew as small irregular paddies fitted to the microtopography; large regular blocks or
        long strips signal a later planned reclamation/allotment (which is why `grid` is typing-gated to a
        planned field origin). Returns `(plot_across, row_step)` to pass straight into `carve_comb`.

        SIZED IN REAL FEET at ftpx >= 2 (GM 2026-07-22): for a village or provincial city each `plot_size`
        picks a real-feet CELL-AREA target (acres) and an aspect, and `waterfields.paddy_grain` converts that to
        px at THIS map's `ftpx` - so the paddy grain is the same real size at every scale (see
        waterfields.PADDY_CELL_ACRES / research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.html). The targets bracket the calibrated
        norm: `small_irregular` below it, `medium` at it, `large_block` above, `strip` at the norm's area but
        long-and-narrow (aspect > 1). The ft/px=1 HAMLETS (the only maps that reach this at that scale, via
        the scripted hamlet's `stage_field`) stay on the LEGACY px grain: they already render in-band (~0.02-0.06 acre) and the GM
        asked to leave them untouched, so recalibrating them would only reshuffle vetted maps for no gain.
        Research: paddy plot size and regularity - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html, research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.drawing.html, research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html, research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: 0.72 / 1.0 / 1.35 of the plot norm or a strip, a grid only narrowing the row spread; no jori grid is drawn
            its salts, guards and sentinels - NONE: they decide nothing about the place - 0.66 (basin aspect at ftpx >= 2 (unreached)); 1.9 (strip aspect (unreached)); 32 (hamlet strip (never rolled or fixed)); 46 (hamlet strip (never rolled or fixed)); 66 (hamlet strip (never rolled or fixed))
            its figures guessed on 0005 - GUESS research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: 34 (small_irregular basin); 20 (small_irregular basin); 40 (small_irregular basin)
            its figures from 0005 - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: 48 (medium basin); 70 (large_block basin); 26 (medium basin); 36 (medium basin); 30 (large_block basin); 44 (large_block basin)
        """
        from l7r.diagram.waterfields import PADDY_CELL_ACRES, paddy_grain

        if plot_size not in ("small_irregular", "medium", "large_block", "strip"):
            raise ValueError(f"unknown plot_size {plot_size!r}")
        if plot_regularity not in ("organic", "grid"):
            raise ValueError(f"unknown plot_regularity {plot_regularity!r}")
        if self.ftpx >= 2:  # village / city: the real-feet calibration
            # (target_acres, aspect = along/across): small below the norm, large above, strip = norm area but elongated
            tgt_acres, aspect = {
                "small_irregular": (PADDY_CELL_ACRES * 0.72, 0.66),
                "medium": (PADDY_CELL_ACRES, 0.66),
                "large_block": (PADDY_CELL_ACRES * 1.35, 0.72),
                "strip": (PADDY_CELL_ACRES, 1.9),
            }[plot_size]
            across, step = paddy_grain(self.ftpx, target_acres=tgt_acres, aspect=aspect)
        else:  # ft/px=1 hamlet: the legacy px grain (already in-band; left untouched by GM request)
            across, step = {
                "small_irregular": (34.0, (20.0, 40.0)),
                "medium": (48.0, (26.0, 36.0)),
                "large_block": (70.0, (30.0, 44.0)),
                "strip": (32.0, (46.0, 66.0)),
            }[plot_size]
        if plot_regularity == "grid":  # collapse the row-step spread toward its mean -> even, surveyed rows
            mid = (step[0] + step[1]) / 2
            step = (mid - 3.0, mid + 3.0)
        if record:
            self.M["meta"]["plot_size"] = plot_size
            self.M["meta"]["plot_regularity"] = plot_regularity
        return across, step
