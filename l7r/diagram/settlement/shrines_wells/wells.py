"""The wellhead glyph, and the four passes that put wells on a map.

Split from settlement/shrines_wells.py by feature 116 - see settlement/shrines_wells/CLAUDE.md for the index.

Research: plumbing - NONE
"""

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any

from .._geom import (
    Pt,
    point_quad_dist,
    rot_rect,
)

if TYPE_CHECKING:
    from ..core import Settlement


WELL_AMONG_DWELLINGS_PX = 95.0
"""How far a well may stand from the nearest dwelling's WALL - `wells_among_dwellings`' bar, the figure the retired
finished-map test read, unchanged by feature 287 (whose clustered well pocket, refused past this bar, feature 374 wave 155
retired: a clustered hamlet's wells are all shared, off the farmstead). Its origin is not
recorded beside it; what the record gives is the reason for a bar at all - a well is dug among the doors it serves, the
dooryard well of the idiom 井戸端会議 (idobata kaigi, "well-side meeting"), not out in the commons. MOVED here from
`hamletgen/homesteads/wells.py` (feature 287, homes H09); the hamlet module imports it back.

Research: a well among the dwellings it serves - research/questions/0196-communal-wells-ido.drawing.html: 95 px from the nearest dwelling's wall
"""


def well_gap_to_dwellings(houses: Sequence[Mapping[str, Any]], x: float, y: float) -> float:
    """The gap from a well at (x, y) to the nearest dwelling's drawn wall - 0 inside one; abandoned houses are no dwelling.

    THE ONE PREDICATE of the among-the-dwellings rule (feature 287, FR-003, homes H09): every seat `place_wells` offers
    is held to `WELL_AMONG_DWELLINGS_PX` by it (the hamlet's `seat_wells` at its own nearer seat gap), and the
    finished-map test reads it. The two used to disagree: the placer's lattice asked for a house CENTER within 105-112 px,
    which admits a wall 99 px off beside a 26 px-deep house, while the test measured the gap to an unturned box. The
    test's reading is the right one, turned: a gap verdict reads the footprint, never the center (`dev/placement.md`,
    "CENTER vs FOOTPRINT"), and a well stands among the DOORS it serves, which are in the walls. Each house is measured on
    its drawn quad (`rot_rect` at its `rot`)."""
    return min(
        (point_quad_dist(x, y, rot_rect(h["x"], h["y"], h["w"], h["h"], h.get("rot", 0.0))) for h in houses if h.get("kind") != "abandoned"),
        default=float("inf"),
    )


class WellsMixin:
    def _well_vr(self: Settlement) -> float:  # type: ignore[misc]
        """The well-house ROOF square's half-size - a wellhead's full DRAWN extent (see well()).
        In FEET at this map's ftpx on a to-scale tier (a ~24.8 ft well-house); on the legacy tiers
        it scales with the urban glyph grain. Factored out of well() because PLACEMENT has to
        predict the glyph before it is drawn: the stable yard's dig-your-own-well fallback needs
        the head's size to keep it off a hitching rail or a neighboring yard's troughs
        (wellhead_quad / wells_troughs_rails_clear_of_each_other).

        Research:
            wellhead marker larger than life - research/questions/0196-communal-wells-ido.drawing.html: the curb `well()` draws at a 9.36 ft radius, about 19 ft across, is the page's marker
            the roof square round the curb - GUESS: searched, the record silent (feature 417 T36 pass P6, 2026-10-25) on a page - a well house and fence ran at most 12 sq m (Nakamori, late Edo, pass P6), 0196's 1.6; the marker is drawn larger than life; 12.376 ft half-size (24.75 ft across), 11.9 x bscale on the legacy tiers; the page (0196 drawing) gives no roof size
        """
        return self.px(12.376) if self._toscale() else 11.9 * self.bscale

    def well(self: Settlement, x: float, y: float, r: float = 8, shrine: bool = False, private: bool = False, kind: str | None = None) -> None:  # type: ignore[misc]
        """A public NEIGHBORHOOD WELL (井戸) - a stone curb under an open-sided well-house roof, the
        shared draw-point and social hub (the idobata, where a tenement block's gossip happened). One
        served a courtyard / cluster of ~10-20 households. SMALLER than a house and sits in a block
        INTERIOR off the lanes. Records M['wells'] and blocks placement so the quarter's houses flow
        around it - place BEFORE the quarter's pack. The underground end of a city's water system
        (aqueducts, cisterns, rain barrels feeding the shaft) stays off the map; only the head shows.

        Research:
            wellhead marker - research/questions/0196-communal-wells-ido.drawing.html: a round curb of 9.36 ft radius under a square roof on every well
            cistern-well on the aqueduct - research/questions/0141-the-capitals-aqueduct-josui.drawing.html: kind recorded when declared
            keep-clear margin - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P6, 2026-10-25); 8 px round the roof
        """
        # THE WELL IS A LOCATION MARKER, NOT A TO-SCALE FOOTPRINT (GM ruling 2026-07-21). A real stone
        # well curb is ~3-4 ft - sub-glyph at every map scale - so the wellhead denotes the well's
        # TO-SCALE LOCATION relative to its surroundings with a legible marker whose own pixels are NOT
        # claimed to be to scale. That places wells under the STROKE CONVENTION (same doctrine as the
        # linework floor, see SKILL.md "to scale"), not in violation of the everything-is-to-scale rule.
        # The marker SCALES WITH THE MAP GRAIN (bscale), exactly as the buildings do, so it keeps a
        # consistent ~0.55x a dwelling at every scale - fixed pixels would make it look right in the
        # dense city but far too small beside a village/town's larger houses. It stays SMALLER than a
        # house regardless of the larger COURTYARD footprint reserved for placement.
        vroof = self._well_vr()
        vcurb = self.px(9.36) if self._toscale() else 9.0 * self.bscale
        self.add(
            f'<rect x="{x - vroof:.1f}" y="{y - vroof:.1f}" width="{2 * vroof:.1f}" height="{2 * vroof:.1f}" rx="1.5" fill="#C7B084" stroke="#6B5836" stroke-width="1.1" opacity="0.55"/>', cls="well"
        )  # the well-house roof, light so the curb reads through
        self.add(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{vcurb:.1f}" fill="#9AA1A4" stroke="#43403A" stroke-width="1.1"/>', cls="well")  # stone curb
        self.add(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{vcurb * 0.47:.1f}" fill="#2E4C58"/>', cls="well")  # dark water in the shaft
        _wrec: dict[str, Any] = {"x": round(x, 1), "y": round(y, 1), "r": r, "vr": round(vroof, 1), "shrine": shrine, "private": private}
        if kind is not None:
            # a josui-ido CISTERN-WELL taps the buried aqueduct main (research 021 item 4);
            # recorded only when declared, so every existing manifest stays byte-identical
            _wrec["kind"] = kind
        self.M["wells"].append(_wrec)  # shrine=True marks an ablution (temizu) well - wells_sized_to_population counts only the communal household draw-wells
        # reserve only a TIGHT courtyard around the small wellhead (not a whole house-plot): houses ring
        # it closely, as in a real tenement court, so a well costs roughly its own footprint, not several
        # dwellings. (`r` stays the recorded clearance radius the checks use; the reserved block is small.)
        self.placed.append((x, y, 2 * vroof, 2 * vroof))
        bm = 8
        self.block_polys.append([(x - vroof - bm, y - vroof - bm), (x + vroof + bm, y - vroof - bm), (x + vroof + bm, y + vroof + bm), (x - vroof - bm, y + vroof + bm)])

    def well_at(self: Settlement, x: float, y: float, r: float = 8, shrine: bool = False) -> bool:  # type: ignore[misc]
        """Place ONE well at (x, y), but only if the spot is clear (a block interior off lanes,
        compounds, the bound, and other placed things - the same `_fits` test place_wells uses).
        Returns True if it placed. For hand-seeding wells into cramped, lane-laced quarters the grid
        scatter can't reach - pass a generous candidate list and the blocked ones simply no-op.
        A spot inside a scrub/pasture/coppice COVER poly is refused too (2026-07-24, caught by
        scrub_clear_of_urban_fabric when a torii-count ripple reseated three Hirameki farm wells
        into the grazing commons): a wellhead stands in worked dooryard/margin ground, never out
        in the grazed waste - and the cover scatter is drawn long before the farm wells, so the
        well must yield, not the commons.

        Research:
            wellhead off the commons - research/questions/0196-communal-wells-ido.drawing.html
            ground fit for a wellhead - research/questions/0196-communal-wells-ido.drawing.html: _well_ground_clear
            standing room demanded - GUESS: searched, the record silent (feature 417 T36 pass P6, 2026-10-25); a fixed 2r + 14 px box
        """
        if self._in_scrub_cover(x, y) or not self._well_ground_clear(x, y):
            return False
        # THE 30x30 IS A FIXED-PIXEL CONSTANT IN A SCALE-AWARE FAMILY, AND IT NO LONGER MEANS ONE
        # THING (measured 2026-08-08). `2 * r + 14` is 30px for the default r=8 REGARDLESS of ftpx,
        # while the head this reserves ground for is `_well_vr()` = px(12.376), which DOES scale. So
        # the ratio of reserved ground to drawn glyph is exactly ftpx, and every pool map disagrees:
        #
        #     ftpx=1  hamlets, towns   head 24.8px   reservation 30px   1.21x   (~30 real ft)
        #     ftpx=2  villages         head 12.4px   reservation 30px   2.42x   (~60 real ft)
        #     ftpx=3  cities           head  8.0px   reservation 30px   3.75x   (~90 real ft)
        #
        # Same ~24.8 ft well-house, three different answers: the placer demands 30 real ft of
        # standing room around it on a hamlet and 90 real ft on a city. The constant was DERIVED at
        # 1px=1ft, where it is a sensible ~2.6px margin a side, and was never re-derived when the
        # scale ladder added the 2 ft and 3 ft tiers - the exact trap `well()`'s own glyph comment
        # warns about ("fixed pixels would make it look right in the dense city but far too small
        # beside a village/town's larger houses"), running the other way.
        #
        # IT IS NOT A DELIBERATE DRAWING APRON, though the intent behind `_place_wells`' "modest
        # footprint" comment reads like one. An apron would be RESERVED as well as demanded, and it
        # is not: `well()` registers only `(x, y, 2 * vroof, 2 * vroof)` in `placed`, so on a city
        # map this asks 30px of clearance at placement and then occupies 8px, and later features
        # pack right up to the head. Over-restrictive going in, under-reserving once in - which is
        # skill CLAUDE.md's item 3 ("placement tests a DIFFERENT footprint than the one drawn")
        # wearing a different hat, not a fourth kind of defect.
        #
        # COST, for whoever fixes it: on Tango, testing the TRUE drawn head instead of this box
        # accepts ~5x the ground the box does around a boxed-in steading (157 seats vs 32 in the
        # east-fan sweep), and wells are 131 of the 767 seats that whole gen loses to geometry
        # error. LEFT AS IS deliberately - changing it re-seats wells on every map in the pool and
        # re-rolls the packs that flow around them, so it belongs with the item 2/item 3 pass and
        # its re-baseline, not in a drive-by. See `_place_wells`, which computes the same box.
        # ...AND THE REGISTRY OF WHAT STANDS ADMITS THE WELLHEAD AS IT WILL BE RECORDED (feature 287 M8): the overlap matrix (a
        # bed, a lane, a yard) and the seating's reservations (an access corridor, a household's wood seat) - cohort 1-60 dug
        # 44 wells on a corridor the web then had to draw round
        if self.admits("wells", {"x": round(x, 1), "y": round(y, 1), "r": r, "vr": round(self._well_vr(), 1)}) and self._fits(x, y, 2 * r + 14, 2 * r + 14):
            self.well(x, y, r, shrine=shrine)
            return True
        return False

    def place_wells(self: Settlement, bbox: Any, spacing: float, r: float = 8, near: Any = None, coverage: bool = True, kind: str | None = None) -> list[Pt]:  # type: ignore[misc]
        """Scatter neighborhood wells across a residential bbox on a grid at ~`spacing` px, keeping
        each in a block INTERIOR: a candidate is dropped if it falls on a lane corridor, outside the
        city bound, on an existing compound (temple/estate/pond), or too near another well (all via
        `_fits`). For each grid cell the cell center is tried first, then a few small offsets, so a
        cell still gets a well when its exact center happens to land on a lane or compound - this keeps
        coverage even in the lane-laced warren. One well per ~spacing px serves the courtyards around
        it. Call BEFORE the quarter's house pack so the houses flow around the wells. Returns the
        placed (x, y) list. Pass coverage=False to keep `near` as a PER-CANDIDATE gate only - the
        coverage pass sweeps ALL dwellings map-wide, which a district-scoped call must not do (it
        would drop wells beside the samurai compounds, which keep no public wells).

        Research: scoped well scatter - NONE: delegates to _place_wells
        """
        # SCOPED (2026-08-08): well siting jitters over a grid; keyed on the bbox it covers.
        with self.rng_scope("place_wells", *bbox), self.frozen_terrain():  # one well index for the whole scatter, not one revalidation per candidate seat
            return self._place_wells(bbox, spacing, r, near, coverage, kind)

    def _place_wells(self: Settlement, bbox: Any, spacing: float, r: float, near: Any, coverage: bool, kind: str | None = None) -> list[Pt]:  # type: ignore[misc]
        """The well scatter itself.

        Research:
            wells inside the blocks, off lanes and compounds - research/questions/0196-communal-wells-ido.drawing.html: a grid at the caller's spacing
            cell offsets - NONE: the center, then four at 0.26 of the spacing
            a dwelling within reach - research/questions/0196-communal-wells-ido.drawing.html: the caller's near
            no dwelling left without a well - research/questions/0196-communal-wells-ido.drawing.html: the coverage pass, six seats at 0.45 to 0.6 of near
            standing room demanded - GUESS: searched, the record silent (feature 417 T36 pass P6, 2026-10-25); a fixed 2r + 14 px box
        """
        x0, y0, x1, y1 = bbox
        # a modest footprint => wells sit in the courtyards, not crammed on a lane. The SAME box
        # `well_at` computes, and it carries the same caveat: 30px is fixed while the drawn head
        # scales with ftpx, so this reserves 1.21x the glyph on a hamlet and 3.75x on a city. Read
        # the note in `well_at` before touching it - the two must move together.
        probe = 2 * r + 14
        d = spacing * 0.26
        offsets = [(0, 0), (d, d), (-d, -d), (d, -d), (-d, d)]
        # `near`: only place a well that has a DWELLING within `near` px - a well serves the households
        # around it, so it must sit AMONG the buildings, never out in open countryside. Pass it when the
        # houses are already placed (the rural tiers: place_wells runs AFTER the field rings); a city's
        # pack runs after place_wells and fills in around the wells, so the city omits it.
        dwell = self.M.get("buildings", []) + self.M.get("houses", []) if near is not None else None
        out: list[Pt] = []
        yy = y0 + spacing / 2
        while yy <= y1:
            xx = x0 + spacing / 2
            while xx <= x1:
                for ox, oy in offsets:
                    cx, cy = xx + ox, yy + oy
                    if (
                        not self._in_scrub_cover(cx, cy)
                        and self._well_ground_clear(cx, cy)
                        and self._fits(cx, cy, probe, probe)
                        and (dwell is None or any((b["x"] - cx) ** 2 + (b["y"] - cy) ** 2 < near * near for b in dwell))
                    ):
                        self.well(cx, cy, r, kind=kind)
                        out.append((cx, cy))
                        break
                xx += spacing
            yy += spacing
        if dwell is not None and coverage:
            # COVERAGE pass: the grid can leave an edge / outlier dwelling in a gap. Guarantee none is left
            # well-less: any dwelling with no well within `spacing` gets one dropped in a clear spot beside it.
            for b in dwell:
                if all((b["x"] - wx) ** 2 + (b["y"] - wy) ** 2 > spacing * spacing for wx, wy in out):
                    # SIX SEATS, deliberately not a wider walk (tried 2026-07-27 and reverted): a
                    # 64-candidate ring walk does find a seat for a dwelling boxed in by refused
                    # ground, but on a CITY it also seats wells the block-interior rule rejects -
                    # over a ministry, on a lane - because `_fits` and `_well_ground_clear` are not
                    # the whole of what a city well must satisfy. A dwelling this cannot reach is
                    # better reported by farm_wells_within_reach and hand-seeded with `well_at`,
                    # which is what the gens already do for cramped quarters.
                    for ox, oy in ((0, near * 0.6), (near * 0.6, 0), (-near * 0.6, 0), (0, -near * 0.6), (near * 0.45, near * 0.45), (-near * 0.45, near * 0.45)):
                        cx, cy = b["x"] + ox, b["y"] + oy
                        if not self._in_scrub_cover(cx, cy) and self._well_ground_clear(cx, cy) and self._fits(cx, cy, probe, probe):
                            self.well(cx, cy, r)
                            out.append((cx, cy))
                            break
        return out
