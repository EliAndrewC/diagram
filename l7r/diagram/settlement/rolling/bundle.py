"""What a homestead BUNDLE is: house, threshing yard, dooryard garden beds, kura, grove arms. Pure geometry - it places nothing and draws nothing.

Split from settlement/rolling.py by feature 118 - see settlement/rolling/CLAUDE.md for the index.

Research: box and template plumbing - NONE
"""

import math
from typing import TYPE_CHECKING, Any, cast

from ..homestead_parts.fixture_seats import DOOR_OUT_FT, DOOR_ROOM_HALF_FT, FixtureForms, FixtureUnlaid, door_room, lay_fixtures, sun_turns, way_in_strip
from ..homestead_parts.grove_rules import EAST_REACH_FT
from ..homestead_parts.grove_sides import bundle_turn
from ..homestead_parts.tree_shade import CANOPY_SHADE_FT
from ..shrines_wells.byres import BYRE_FT, YARD_SHED_GAP_FT, byre_part
from .bearing import BEARING_SPREAD_DEG
from .dispersed import LANE_ROOM_FT, SERVICE_STRIP_FT, THIN_BAND_FT, WAY_IN_FT, YARD_SUN_STRIP, clear_east_of_beds, dispersed_layout
from .lot import kura_rect

if TYPE_CHECKING:
    from ..core import Settlement


class BundleGeomMixin:
    @staticmethod
    def _bbox_of(rects: Any) -> tuple[float, float, float, float]:
        """The axis-aligned (cx, cy, w, h) bounding box enclosing a list of (cx, cy, w, h) rects."""
        xs = [r[0] - r[2] / 2 for r in rects] + [r[0] + r[2] / 2 for r in rects]
        ys = [r[1] - r[3] / 2 for r in rects] + [r[1] + r[3] / 2 for r in rects]
        return ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, max(xs) - min(xs), max(ys) - min(ys))

    def _garden_beds(self: Settlement, hx: float, hy: float, hw: float, hh: float, gx: float, gy: float, gw: float, gh: float, side: str, gap: float, seat: Any = None) -> list[Any]:  # type: ignore[misc]
        """The dooryard garden BED(S) of one nucleated homestead. Usually ONE bed (the reserved plot at
        (gx, gy)). But ~1 in 4 households FRAGMENT the plot into two beds - soil and paths made a single
        clean plot impractical, so you work the good topsoil where it lies. Of the splits (all position-
        seeded, no RNG ripple): ~half FLANK the house on OPPOSITE walls (the E and W walls, or the two south
        corners) because the workable ground just fell on both sides; the rest share ONE side, either
        SIDE-BY-SIDE or - for a SOUTH garden, where the upper bed stays out of the house's shade - STACKED
        above/below. Every bed sits on a SUNNY band (never the cold north back), and because the beds are
        returned to `_bundle_geom` they are RESERVED and collision-checked as part of the whole bundle - so an
        opposite-side bed can never overlap a neighbor or a paddy. Splits only fire when each bed stays wide
        enough (~12 ft) to read as a real garden, so it is the larger (well-off / headman) plots that
        fragment. Total bed area stays in the saien band (`garden_area_within_norms`). Returns (cx,cy,w,h) rects.

        Research:
            bed split share - GUESS: searched, the record silent (feature 417 T36 pass P3, 2026-10-25); about one household in four splits its plot into two beds
            bed split forms - GUESS: searched, the record silent (feature 417 T36 pass P3, 2026-10-25) - 0039 has where a bed lay, nothing on splitting one; half flank the house on opposite walls, the rest stacked (south gardens) or side by side; each bed at least 6 ft (`bscale`) wide
            beds one household's garden - research/questions/0039-kitchen-gardens-beside-farmhouses-yashikibatake.drawing.html: the beds together held to the garden's size range
            beds on sunny sides - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: never the north back
            its figures against 0039 - research/questions/0039-kitchen-gardens-beside-farmhouses-yashikibatake.drawing.html: 0.26 (about 1 in 4 households split the garden); 0.55 (each flanking bed 0.55 of the garden, so the two pass the 1,507 sq ft ceiling) - a departure the code keeps until feature 417 T33
            its salts, guards and sentinels - NONE: they decide nothing about the place - 8 (jitter salt); 9 (jitter salt)
        """
        bs = self.bscale
        jx, jy = seat if seat is not None else (hx, hy)  # the household's seat when one is being sought (feature 276, D10)
        if self._hjit(jx, jy, 8.0) >= 0.26:  # the common case: one undivided plot
            return [(gx, gy, gw, gh)]
        south = side in ("SE", "SW")
        # OPPOSITE-SIDE (flanking) split: a bed on each of the E and W walls (or the two south corners for a
        # south garden), each ~half width, the house standing between them
        if self._hjit(jx, jy, 9.0) < 0.5 and gw * 0.55 >= 6 * bs:
            pw = gw * 0.55
            return [(hx + hw / 2 + gap + pw / 2, gy, pw, gh), (hx - hw / 2 - gap - pw / 2, gy, pw, gh)]
        # SAME-SIDE STACKED (above/below): only for a south garden, so the upper bed does not fall into shade
        if south and self._hjit(jx, jy, 10.0) < 0.5 and (gh - gap) / 2 >= 6 * bs:
            ph = (gh - gap) / 2
            return [(gx, gy - (gap + ph) / 2, gw, ph), (gx, gy + (gap + ph) / 2, gw, ph)]
        # SAME-SIDE SIDE-BY-SIDE (the default fragmentation), both beds on the primary wall
        if (gw - gap) / 2 >= 6 * bs:
            pw = (gw - gap) / 2
            return [(gx - (gap + pw) / 2, gy, pw, gh), (gx + (gap + pw) / 2, gy, pw, gh)]
        return [(gx, gy, gw, gh)]  # reserved plot too small to split cleanly

    def _bundle_envelope(self: Settlement, hx: float, hy: float, hw: float, hh: float, shed: bool = False) -> tuple[float, float, float, float]:  # type: ignore[misc]
        """The homestead's ENVELOPE (feature 227): the box around the LARGEST configuration a nucleated bundle can
        take at this seat - the union of the four garden sides' bundle boxes (house, yard, the garden on either
        side, the kura when reserved). Tested once before any part is laid; a part laid inside it never needs
        ground the envelope did not clear."""
        return self._bbox_of([self._bundle_geom(hx, hy, hw, hh, side, shed)["bbox"] for side in self._NUC_SIDES])

    def _bundle_geom(self: Settlement, hx: float, hy: float, hw: float, hh: float, garden_side: str = "E", shed: bool = False, rot: float | None = None) -> dict[str, Any]:  # type: ignore[misc]
        """The bundle at (hx, hy): its UNRAKED layout, built once per seat offered, size and garden side (`_bundle_template`,
        `_bundle_layout`), moved here and turned by this seat's rake (feature 276, FR-003, plan D10).

        WHY ONCE. The placer asks for this bundle at every candidate seat - the spiral's offsets, every 2 px of a
        slide, four garden sides - and rebuilt it each time (46,781 builds on the rescue scenario). A layout relative
        to its house center does not depend on the seat once its ROLLED parts - the yard's size, the garden's jitter,
        the bed split - are the household's rather than the seat's, so while a household's seat is sought
        (`_household_seat`, set by the placer) they are rolled at the seat it was sought from (the spec's Decisions
        Recorded: the same distributions, rolled per household). The RAKE stays the seat's, applied after the move, so
        the homestead still turns as one piece wherever it lands (GM 2026-09-26). Outside a seat search the rolls key
        on (hx, hy) as they always did. `rot` overrides the seat's turn (0.0: the unturned layout a caller measures).
        ONCE PER SEAT OFFERED, NOT PER HOUSEHOLD: each `_place_bundle` call is a seat offered and its own key - keying the rolls
        on the household was tried and withdrawn (feature 297, `place.py`) - so a household offered from many seats lays as
        many layouts (2,369 for 40 households at seed 25, measured 2026-10-27 by `make perf-profile`; feature 435 set down
        building them once per household on that ground, ask:435-bundle-once).

        THE GROUND CLEARED IS THE GROUND DRAWN, AT ANY TURN (269 B18). The parts keep their true sizes - the drawing and
        the fixtures read a part in its house's frame - and `boxes` holds each part's axis-aligned box AS DRAWN, turned
        (`turned_box`); every fit rule reads the boxes, and the bundle's `bbox` is theirs. Under the old +/-5 degree
        rake the difference was two pixels and was let stand; a house turned 30 degrees, or a quarter turn, is not.

        Research:
            homestead turns as one piece - research/questions/0029-farmhouses-minka.drawing.html: the yard and beds turn with the house about its center, the ground cleared as drawn
            grove cleared east of turned beds - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: a farm's grove, of any form, cut back 50 ft (`EAST_REACH_FT`) east of its turned beds (`clear_east_of_beds`)
        """
        tpl = self._bundle_template(hw, hh, garden_side, shed, getattr(self, "_household_seat", None) or (hx, hy))

        def moved(r: Any) -> Any:
            return None if r is None else (r[0] + hx, r[1] + hy, r[2], r[3])

        base: dict[str, Any] = {
            k: ([moved(r) for r in v] if k in ("gardens", "groves") else {f: moved(r) for f, r in v.items()} if k == "fixtures" else v if k in ("fixture_notes", "unlaid", "grove_faces") else moved(v))
            for k, v in tpl.items()
        }
        frame = base.pop("_frame", None)
        turn = self._turn_at(hx, hy) if rot is None else rot
        self._rake_parts(base, hx, hy, turn)
        if base.get("groves"):  # every form, not the dispersed alone: no band left standing in a bed's morning sun (feature 315 seed 906; 328 wave 59: a linear farm's thin east band, cohort seed 901)
            base["groves"] = clear_east_of_beds(list(base.get("groves") or ()), list(base["gardens"]), self.px(EAST_REACH_FT))
        base["turn"] = turn  # the parts' turn, so a reader of their true sizes (`access.doors_of`) measures them as drawn
        # `turned_box` for every part, its turn's cosine and sine taken once (the same arithmetic, part by part)
        _th = math.radians(turn)
        _c, _s = abs(math.cos(_th)), abs(math.sin(_th))

        def tbox(r: Any) -> tuple[float, float, float, float]:
            x, y, w, h = float(r[0]), float(r[1]), float(r[2]), float(r[3])
            return (x, y, w * _c + h * _s, w * _s + h * _c)

        boxes: dict[str, Any] = {k: (tbox(base[k]) if base.get(k) is not None else None) for k in ("house", "yard", "shed", "byre", "well")}
        boxes["gardens"] = [tbox(g) for g in base["gardens"]]
        boxes["fixtures"] = {f: tbox(r) for f, r in (base.get("fixtures") or {}).items()}
        base["boxes"] = boxes
        if frame is None:  # nucleated: every part, as drawn
            rects = [r for r in (boxes["house"], boxes["yard"], *boxes["gardens"], boxes.get("shed"), boxes.get("byre"), boxes.get("well"), *boxes["fixtures"].values()) if r is not None]
            base["bbox"] = self._bbox_of(rects)
        else:  # dispersed: the grove's unraked frame with the turned yard and garden
            base["bbox"] = self._bbox_of([frame, boxes["yard"], boxes["gardens"][0], *([boxes["well"]] if boxes.get("well") else []), *boxes["fixtures"].values()])
        # ...AND ITS PERSIMMON KEPT ONLY WHERE, AT THIS RAKE, IT SHADES NO PLOT - its own or a placed neighbor's (feature 315): decided
        # here, because the placer lays a seat's homestead afresh once it is chosen (`_place_bundle`), so a tree dropped by the
        # fit alone came back on the record (cohort seed 1: its own yard's sun)
        self._settle_persimmon(base)
        return base

    def _core_geom(self: Settlement, hx: float, hy: float, hw: float, hh: float, shed: bool = False) -> dict[str, Any]:  # type: ignore[misc]
        """The house and its yard at (hx, hy), as `_bundle_geom` lays and boxes them, without the rest of the layout (feature 297,
        FR-002): `house`, `yard`, `boxes` (the two turned boxes) and `turn` - what `doors_of` and the corridor search read. The
        house and the yard are the same for every garden side (research R6), so the first side's template serves."""
        tpl = self._bundle_template(hw, hh, self._NUC_SIDES[0], shed, getattr(self, "_household_seat", None) or (hx, hy))
        turn = self._turn_at(hx, hy)
        th = math.radians(turn or 0.0)
        c, sn = math.cos(th), math.sin(th)
        house = (tpl["house"][0] + hx, tpl["house"][1] + hy, tpl["house"][2], tpl["house"][3])
        yard = None
        if tpl.get("yard") is not None:
            px, py = tpl["yard"][0] + hx, tpl["yard"][1] + hy
            yard = (hx + (px - hx) * c - (py - hy) * sn, hy + (px - hx) * sn + (py - hy) * c, tpl["yard"][2], tpl["yard"][3])
        _c, _s = abs(c), abs(sn)

        def tbox(r: Any) -> tuple[float, float, float, float]:
            x, y, w, h = float(r[0]), float(r[1]), float(r[2]), float(r[3])
            return (x, y, w * _c + h * _s, w * _s + h * _c)

        return {"house": house, "yard": yard, "turn": turn, "boxes": {"house": tbox(house), "yard": tbox(yard) if yard is not None else None}}

    def _bundle_template(self: Settlement, hw: float, hh: float, garden_side: str, shed: bool, seat: Any) -> dict[str, Any]:  # type: ignore[misc]
        """The household's unraked layout at the origin for one garden side, its rolls drawn at `seat` (the household's point
        during a seat search, else the house's own position), built once per key (see `_bundle_geom`)."""
        key = (
            hw,
            hh,
            garden_side,
            shed,
            bool(getattr(self, "_nucleated", False)),
            seat,
            getattr(self, "_household_byre", None),
            tuple(getattr(self, "_household_fixtures", None) or ()),
        )
        cache = self.__dict__.setdefault("_bundle_templates", {})
        tpl = cache.get(key)
        if tpl is None:
            tpl = self._bundle_layout(0.0, 0.0, hw, hh, garden_side, shed, seat)
            cache[key] = tpl
        return cast("dict[str, Any]", tpl)

    def _turn_at(self: Settlement, hx: float, hy: float) -> float:  # type: ignore[misc]
        """`_house_rot(hx, hy)`, remembered for the last seat asked while the bearing it reads stands: the four garden sides
        of a seat, and the fit rules after them, ask the same seat (seed 44: 60,552 turns for 5,299 seats)."""
        key = (hx, hy, self._house_bearing, self._bearing_follow)
        got = self.__dict__.get("_turn_memo")
        if got is None or got[0][0] != hx or got[0][1] != hy or got[0][2] != key[2] or got[0][3] is not key[3]:
            got = self.__dict__["_turn_memo"] = (key, self._house_rot(hx, hy))
        return got[1]

    def _bundle_layout(self: Settlement, hx: float, hy: float, hw: float, hh: float, garden_side: str, shed: bool, seat: Any) -> dict[str, Any]:  # type: ignore[misc]
        """The metric layout of one homestead BUNDLE around a house centered at (hx, hy). TWO forms:
        NUCLEATED (self._nucleated) = house + lee GARDEN (E) + south YARD only, compact so a cluster can
        pack tight (no per-house grove - a nucleus shelters itself); DISPERSED (default) also carries the
        farm's own GROVE on the sides its settlement rolled, turned to the map's wind (`dispersed.dispersed_layout`,
        feature 291). Returns a dict of (cx, cy, w, h) rects keyed house/garden/yard (+ `groves`, a list, with
        `grove_faces` beside it, when dispersed).

        Research:
            house-to-part gap - GUESS: searched, the record silent (feature 417 T36 pass P3, 2026-10-25); 3 ft between the house and its yard and garden
            garden size - research/questions/0039-kitchen-gardens-beside-farmhouses-yashikibatake.drawing.html: 0.48 x 0.85 of the house, jittered up to 1.25x, capped at 44 x 34 ft (dispersed 42 x 30), under 0039's 1,507 sq ft
            yard before the south wall - research/questions/0037-threshing-and-drying-yards-at-farmhouses-niwa.drawing.html, research/questions/0029-farmhouses-minka.drawing.html: the rolled yard, centered on the front
            headman keeps an ordinary yard and garden - research/questions/0030-the-headmans-house-and-the-rich-farmers-homestead-shoya-gono.drawing.html: the caps hold a big house's parts to an ordinary farm's
            no grove of its own in a cluster - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html, research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: a nucleus shelters behind one village belt
            garden side - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: southeast, southwest, east or west of the house
            garden morning-sun reach - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: no grove band within 50 ft (`EAST_REACH_FT`) east of a garden across its height
            forecourt kept on a no-rice farm - research/questions/0039-kitchen-gardens-beside-farmhouses-yashikibatake.html: the drying yard was also the work yard, a fifth of the lot (Imabari 1924); no page ties the yard to rice alone; the yard's ground reserved where no threshing floor is drawn
            frame padded for a lane - GUESS research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: half `LANE_ROOM_FT` (16 ft) on every side, so neighbors' groves stand 32 ft apart
            service strip - GUESS research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: the windward stand `SERVICE_STRIP_FT` (24 ft) off the back and windward end walls, sized to seat a wood shed
            thin band - GUESS research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: a grove side away from the wind one tree deep, `THIN_BAND_FT` 17 ft (two 0080 mean crown radii)
            way in through a ring - GUESS research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: one `WAY_IN_FT` (36 ft) break at the front band's middle, sized so a lane can be routed through
            byre footprint - research/questions/0048-draft-oxen-and-horses-and-their-byres-umaya.drawing.html: `BYRE_FT`, 16.12 x 10.92 ft
            byre off the house - research/questions/0048-draft-oxen-and-horses-and-their-byres-umaya.drawing.html: `YARD_SHED_GAP_FT[0]`, 6 ft, off the house
            dispersed well pocket - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P3, 2026-10-25); the wellhead plus a 3 ft margin, `2 * _well_vr() + px(6.0)`
            south band off an unkept yard - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: the project's sun figures leave 39 ft open before a yard - the strip is 22 ft, a departure the code keeps until feature 417 T33; `YARD_SUN_STRIP`, 22, unscaled, where the map keeps no sun
            storehouse on the north wall - DEVIATION research/questions/0040-farm-storehouses-kura.drawing.html: a nucleated farm's annex on the shaded back wall, a convention the page records against the record
            storehouse seam - CONVENTION: the north-wall kura annex reserved 1 ft off the house wall
            byre beside the house - research/questions/0048-draft-oxen-and-horses-and-their-byres-umaya.drawing.html: the keeper's stall beside the house
            byre's flank - research/questions/0048-draft-oxen-and-horses-and-their-byres-umaya.html: in the Tono L-shaped house the stable joins the lower end and projects off the south side, both mirror forms recorded - the byre is set at the floored end when the garden is west or southwest, a departure the code keeps until feature 417 T33; away from the garden is ours; the flank away from the garden; the page attests the inner and outer stable, not the side
            outer stable off the wall - GUESS research/questions/0048-draft-oxen-and-horses-and-their-byres-umaya.drawing.html: the yard-shed byre set `YARD_SHED_GAP_FT[0]` (6 ft) off the house, the near end of the page's guessed 6 to 12 ft
            dispersed farm's grove - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: the farm's own grove on its rolled sides, turned to the wind
            south band kept off the yard's sun - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: on a sun-keeping map the south band stands `CANOPY_SHADE_FT` plus 1.7 x 1.15 crown radii beyond the yard
            its figures from 0039 - research/questions/0039-kitchen-gardens-beside-farmhouses-yashikibatake.drawing.html: 0.25 (garden depth jittered up to 1.25x)
        """
        gap = self.px(3)  # 3 ft between a house and its yard/garden, at this map's ftpx
        gw, gh = 0.48 * hw, 0.85 * hh  # garden - tight to the house, scales with wealth
        sx, sy = seat  # the rolls key on the household's seat (see `_bundle_geom`)
        # the yard is the household's, the same for the four garden sides of its seat: rolled once per (size, seat)
        _yk = (hw, hh, sx, sy)
        _ym = self.__dict__.get("_yard_memo")
        if _ym is None or _ym[0] != _yk:
            _ym = self.__dict__["_yard_memo"] = (_yk, self._yard_dims(hw, hh, sx, sy))
        yw, yh = _ym[1]  # threshing/drying yard - the rolled area (homestead_parts._yard_area_ft2); the placer reserves exactly what gets drawn
        if not getattr(self, "_nucleated", False):
            # CAP the DISPERSED appurtenances too, same doctrine as the nucleated branch below: a BIG house
            # (the 46x28 px headman) keeps an ORDINARY farm's garden/yard, not ones scaled to the grand
            # house. Found 2026-07-21 (Hikari, GM): the moment the dispersed headman started getting a real
            # bundle, its uncapped 0.48/0.85-scaled garden (~160+ m^2) breached garden_area_within_norms'
            # 140 m^2 ceiling. Garden caps sit BELOW the nucleated ones (42x30 ft vs 48x34) because this
            # path has no up-jitter to absorb - 21x15 px ~ 117 m^2 stays comfortably a garden. Plain
            # dispersed houses (garden ~11x12 px, yard ~25x14) sit far under every cap, so only the headman
            # is affected. Scoped OFF the nucleated path (which recomputes from these as inputs and applies
            # its own caps) so nucleated maps stay byte-identical - capping its inputs re-rolled
            # Hoshigaoka's packing and pushed its fixed-coordinate graveyard off-frame.
            gw, gh = min(gw, self.px(42)), min(gh, self.px(30))
            # the yard is ROLLED, not scaled off the house (feature 134 T49), so it needs no headman cap
        base: dict[str, Any] = {
            "house": (hx, hy, hw, hh),
            "garden": (hx + hw / 2 + gap + gw / 2, hy, gw, gh),
            "yard": (hx, hy + hh / 2 + gap + yh / 2, yw, yh),
        }
        if getattr(self, "_nucleated", False):
            # NUCLEATED cluster (China-leaning default, per Knapp - and the Japanese shuson): the
            # houses stand close and SHELTER EACH OTHER, so there is NO per-house windbreak grove
            # (a full yashikirin is the DISPERSED-farmstead feature; a tight cluster of grove-bundles
            # cannot nucleate at all). The windbreak becomes a VILLAGE-EDGE belt placed in the second
            # pass. The bundle is house + south yard + a garden on an ADAPTIVE sunny side (chosen by
            # the placer for fit + no shading), so it packs into a real nucleus and the gardens vary
            # instead of all sitting east between houses. See research/questions/0031-clustered-and-scattered-villages-shuson-sanson.html.
            # CAP the appurtenance dims so a big house (the headman) keeps an ORDINARY farm's yard/garden
            # (spanning ~its adjacent wall but not scaled up to the grand house - "not as tall / not as
            # wide"). A plain 23x14 house is well under these caps, so ordinary farms are unaffected.
            # SIZE variation (position-seeded, no RNG ripple): the garden's base is its MINIMUM (you need at
            # least this plot to feed a household) so it jitters UP - by a different amount in each dimension,
            # which also varies its proportions; the threshing yard's base is its MAXIMUM (a work apron sized
            # to the harvest) so it jitters DOWN. No two homesteads are identical. Both are CAPPED afterward so
            # the big headman still keeps an ordinary farm's yard/garden (the garden jitter can't breach it).
            # THE YARD KEEPS ITS ROLLED DIMS (feature 134 T49): the lognormal IS its variation, and
            # re-jittering it here would flatten the distribution the research fixed. The garden below
            # still jitters UP from its minimum - that rule is unchanged.
            gw = min(gw * (1.0 + self._hjit(sx, sy, 3.0) * 0.25), self.px(44))  # garden [1.00,1.25]x, capped at 44 ft (44 x 34 = 1,496 sq ft, under 0039's 1,507)
            gh = min(gh * (1.0 + self._hjit(sx, sy, 4.0) * 0.25), self.px(34))
            # THE FORECOURT IS RESERVED WHETHER OR NOT A THRESHING FLOOR IS DRAWN ON IT (feature 150, GM
            # 2026-08-28: "thrashing yards on a no-rice hamlet seem bad and should be eliminated"). A
            # dike-pond hamlet grows no rice, so `_attach_yard` draws and records no threshing floor
            # when the generator declares `work_yards=False` - but the open ground before the house
            # stays reserved here: a silk-and-fish farmstead still handles its leaf, cocoons and nets
            # somewhere, and (measured) dropping the reservation re-packed the cluster tightly enough
            # to break its lane web and its belt, which are not what the GM asked to change.
            base["yard"] = (hx, hy + hh / 2 + gap + yh / 2, yw, yh)
            if garden_side == "SE":  # tucked beside the south yard (sunny, tight)
                gx, gy = hx + hw / 2 + gap + gw / 2, hy + hh / 2 + gap + gh / 2
            elif garden_side == "SW":
                gx, gy = hx - hw / 2 - gap - gw / 2, hy + hh / 2 + gap + gh / 2
            elif garden_side == "W":  # windward wall, house mid-height
                gx, gy = hx - hw / 2 - gap - gw / 2, hy
            else:  # "E" - lee wall, house mid-height
                gx, gy = hx + hw / 2 + gap + gw / 2, hy
            beds = self._garden_beds(hx, hy, hw, hh, gx, gy, gw, gh, garden_side, gap, seat)
            base["gardens"] = beds  # 1 bed normally; 2 (flanking / stacked / side-by-side) when fragmented
            base["garden"] = beds[0]  # primary bed (kept for the shading score + back-compat)
            if shed:  # a north-wall kura, reserved so a neighbor never lands on it
                _kx, _ky, _kw, _kh = kura_rect(hw, hh, "N", self.px(1.0))  # the drawn annex (`house`), its length held in its band (feature 293)
                base["shed"] = (hx + _kx, hy + _ky, _kw, _kh)
            # THE HOUSEHOLD'S BEAST, a part of its homestead (feature 287, homes H06): a keeper's byre - the inner stable's
            # arm or the outer stable's shed, on the flank away from the garden - is laid in the bundle, so the envelope
            # admits the household only with room for it and no later stage can take that room (`byre_part`)
            form = getattr(self, "_household_byre", None)
            if form:
                bw, bh = self.px(BYRE_FT[0]), self.px(BYRE_FT[1])
                dx, dy, w, h, _turn = byre_part(hw, hh, bw, bh, garden_side, form, self.px(YARD_SHED_GAP_FT[0]))
                base["byre"] = (hx + dx, hy + dy, w, h)
            self._lay_fixtures(base, hx, hy, hw, hh, shed, seat)
            return base  # raked and boxed by `_bundle_geom`, per seat
        # DISPERSED farmstead: the farm's own GROVE round the ground it works, on the sides its settlement rolled
        # (feature 291, `grove_sides.py`). Laid out in the CANONICAL frame - the wind from the northwest, the deep bands
        # on the north and west, the yard on the south front, the garden on the east - then carried to the map's wind
        # by `dispersed_layout`'s turn. The multi-bed garden split is a NUCLEATED feature; a dispersed farm keeps one bed. Its
        # own well pocket is laid in the canonical frame (`canonical_farmstead`), turned with the rest (a clustered farmstead lays none: feature 374 wave 155).
        # THE THIN BANDS KEEP OUT OF THE PLOTS' SUN (feature 310, GM 2026-10-02: "no canopy trees should be exempt"): on a map that
        # keeps the sun, the garden stands beside the yard and the east band closes the house's east side only (`sun_band`,
        # `dispersed.canonical_farmstead`: the frontage stays inside the record's 240 ft), and a ring's south band stands the
        # canopy reach and a crown's radius beyond the yard, so it stands whole
        _sun = self.px(CANOPY_SHADE_FT) + self.px(self.CANOPY_R_FT) * 1.7 * 1.15 if getattr(self, "_sun_corridor_ft", 0.0) else 0.0
        dispersed = dispersed_layout(
            hx,
            hy,
            hw,
            hh,
            gap,
            (gw, gh),
            (yw, yh),
            sides=self._grove_sides(),
            turn=bundle_turn(self._windward(), self._grove_flank()),
            thin=self.px(THIN_BAND_FT),
            sun_east=self.px(EAST_REACH_FT),  # the garden's morning sun: no band within 50 ft east of a bed (0038)
            yard_sun=_sun if _sun else YARD_SUN_STRIP,
            sun_band=bool(_sun),
            way_in=self.px(WAY_IN_FT),
            pad=self.px(LANE_ROOM_FT) / 2.0,
            back=self.px(SERVICE_STRIP_FT),
            well=2.0 * self._well_vr() + self.px(6.0),  # the wellhead and a 3 ft margin
        )
        # ...AND ITS FIXTURES, laid in the bundle as a nucleated household's are (feature 287, homes H32), clear of its own
        # grove (feature 291): the envelope admits the farm only with room for its privy, its wood shed and its bath room
        self._lay_fixtures(dispersed, hx, hy, hw, hh, False, seat, bands=dispersed["groves"], faces=[f for f, _d in dispersed.get("grove_faces") or ()])
        return dispersed

    def _lay_fixtures(self: Settlement, base: dict[str, Any], hx: float, hy: float, hw: float, hh: float, shed: bool, seat: Any, bands: Any = (), faces: Any = ()) -> None:  # type: ignore[misc]
        """THE HOUSEHOLD'S FARMSTEAD FIXTURES, parts of its homestead (feature 287, homes H32, plan M5 and D9): the kinds its
        lot keeps (`_household_fixtures`, set by the seat search) laid beside the parts already laid - built ones a crown may
        not cover, the yard and the beds it may - in the house's frame (`homestead_parts/fixture_seats.py`), with the
        hamlet's rolled forms (`_fixture_forms`) and the household's own position roll. So the envelope admits a household
        only with room for its privy, its stack, its tree, and no later stage can take that room. A grove farm's `bands`
        (feature 291) are built ground too: no fixture stands in its own grove.

        Research:
            farmstead fixtures - research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.drawing.html: the kinds the household's lot keeps, laid in its own frame
            persimmon may stand in its own grove's bands - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html: fruit=bands, the persimmon is not held out of its own farm's grove bands
            persimmon out of the plots' sun - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: held 50 ft off yards and beds at the seat's own rake, re-checked as drawn (`fit._persimmon_sun_conflict`)
            a grove farm's way in kept clear - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: the way-in strip (`way_in_strip`) and the door's room (`door_room`, UNRESEARCHED in size) handed to the fixtures as `keep`
            the door's room past the yard - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P3, 2026-10-25); `DOOR_OUT_FT` (8 ft) past the yard's far edge, where the web's door path starts (`ways/serve.front_door`)
            its figures from 0029 - research/questions/0029-farmhouses-minka.drawing.html: 5 (+-5 degree rake where no hamlet bearing is set)
        """
        kinds = getattr(self, "_household_fixtures", None) or ()
        if not kinds:
            return
        sx, sy = seat

        def rel(r: Any) -> Any:
            return (r[0] - hx, r[1] - hy, r[2], r[3])

        # A GROVE FARM'S BANDS TAKE ITS PERSIMMON (feature 315): the traditional igune held "a few fruit trees" among its cedar and
        # pine (Sendai's replanting plan, research/questions/0075-bamboo-groves-chikurin.html), so the persimmon's trunk and crown may
        # stand in its own grove's bands - behind the house, within the dooryard - where no other fixture stands
        fruit = [rel(b) for b in bands]
        roofs = [rel(r) for r in (base["house"], base.get("shed"), base.get("byre"), base.get("well")) if r is not None]
        ground = [rel(base["yard"]), *(rel(g) for g in base["gardens"])]
        forms = getattr(self, "_fixture_forms", None) or FixtureForms()
        annex = rel(base["byre"]) if base.get("byre") is not None else None
        notes: dict[str, Any] = {}
        # THE PERSIMMON KEEPS OUT OF ITS OWN YARD'S AND BEDS' SUN (GM 2026-10-02, `CANOPY_SHADE_FT`), on the map that keeps
        # the sun corridor (the scripted path's opt-in, `sun_corridor`), at every rake the house may yet be drawn at: this
        # template serves every position, and the turn is the position's (`_house_rot`: the common bearing +-30, else +-5)
        # ...judged at the rake of the household's own seat (feature 315): the template no longer has to hold at every rake the house
        # might take, because the fit asks the tree again as drawn, at the house's own rake, and drops it there if it shades a
        # plot (`fit._persimmon_sun_conflict`); held at the whole 60-degree range, a grove farm found no dooryard seat at all
        bearing = getattr(self, "_house_bearing", None)
        lo, hi = (-5.0, 5.0) if bearing is None else (bearing - BEARING_SPREAD_DEG, bearing + BEARING_SPREAD_DEG)
        shade = self.px(CANOPY_SHADE_FT) if getattr(self, "_sun_corridor_ft", 0.0) else 0.0
        try:
            laid = lay_fixtures(
                kinds,
                hw,
                hh,
                roofs,
                ground,
                rel(base["yard"]),
                shed,
                lambda salt: self._hjit(sx, sy, salt),
                forms,
                self.px,
                annex,
                notes,
                shade,
                (self._turn_at(sx, sy),) if getattr(self, "_sun_corridor_ft", 0.0) else sun_turns(lo, hi),
                fruit,
                [
                    s_
                    for s_ in [way_in_strip(rel(base["house"]), fruit, faces), door_room(rel(base["house"]), rel(base["yard"]), self.px(DOOR_OUT_FT), self.px(DOOR_ROOM_HALF_FT)) if fruit else None]
                    if s_ is not None
                ],
            )
        except FixtureUnlaid as refused:  # a bath room or a wood shed with no seat in this layout: the fit refuses it (feature 280)
            base["unlaid"] = str(refused)
            return
        base["fixtures"] = {k: (hx + r[0], hy + r[1], r[2], r[3]) for k, r in laid.items()}
        base["fixture_notes"] = notes  # the rolled sizes and the bath room's wall (feature 280), for the record the drawing reads

    def _rake_parts(self: Settlement, base: dict[str, Any], hx: float, hy: float, rot: float) -> None:  # type: ignore[misc]
        """Carry the yard, the garden bed(s) and the kura round the house center by the house's rake, in place.

        THE HOMESTEAD TURNS AS ONE PIECE (GM 2026-09-26). The house is drawn raked by `_house_rot`; its parts are
        laid out square to the house, so their CENTERS must turn about the house's center with it, and each part is
        then drawn turned by the same rake about its own center (`_attach_yard`, `_attach_garden`). Turning a part
        only about its own center left it where the square layout put it - a yard 29 px south of the house slid up
        to 3 ft sideways along the front wall, the direction following the rake's sign, which the GM saw as more
        room at one end of the yard than the other. The rake is position-seeded, so it is known here, at seat
        time, and every fit test the placer runs reads the moved centers - the ground cleared is the ground drawn.
        The grove arms are not moved: they are drawn unraked.

        Research: homestead turns as one piece - research/questions/0029-farmhouses-minka.drawing.html: parts carried round the house center by its rake; the grove arms left unraked
        """

        # `turn_about` for every part, its turn's cosine and sine taken once (the same arithmetic, part by part)
        th = math.radians(rot or 0.0)
        c, sn = math.cos(th), math.sin(th)

        def turned(r: Any) -> Any:
            px, py = r[0], r[1]
            return (hx + (px - hx) * c - (py - hy) * sn, hy + (px - hx) * sn + (py - hy) * c, r[2], r[3])

        if base.get("yard") is not None:
            base["yard"] = turned(base["yard"])
        base["gardens"] = [turned(g) for g in base["gardens"]]
        base["garden"] = base["gardens"][0]
        for part in ("shed", "byre", "well"):
            if part in base:
                base[part] = turned(base[part])
        if base.get("fixtures"):
            base["fixtures"] = {f: turned(r) for f, r in base["fixtures"].items()}
