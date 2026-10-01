"""What a homestead BUNDLE is: house, threshing yard, dooryard garden beds, kura, grove arms. Pure geometry - it places nothing and draws nothing.

Split from settlement/rolling.py by feature 118 - see settlement/rolling/CLAUDE.md for the index.
"""

import math
from typing import TYPE_CHECKING, Any, cast

from ..homestead_parts.fixture_seats import FixtureForms, FixtureUnlaid, lay_fixtures
from ..homestead_parts.grove_sides import bundle_turn
from ..shrines_wells.byres import BYRE_FT, YARD_SHED_GAP_FT, byre_part
from ..shrines_wells.wells import WELL_AMONG_DWELLINGS_PX, well_gap_to_dwellings
from .dispersed import EAST_SHADE_REACH, LANE_ROOM_FT, SERVICE_STRIP_FT, THIN_BAND_FT, WAY_IN_FT, dispersed_layout
from .lot import kura_rect

if TYPE_CHECKING:
    from ..core import Settlement


def boxes_meet(a: Any, b: Any) -> bool:
    """Do two (cx, cy, w, h) boxes overlap - share more than an edge?"""
    return bool(abs(a[0] - b[0]) < (a[2] + b[2]) / 2 and abs(a[1] - b[1]) < (a[3] + b[3]) / 2)


def box_gap(a: Any, b: Any) -> float:
    """The edge gap between two (cx, cy, w, h) boxes: the larger of the two axes' clear distances, negative where they
    overlap on both (so `box_gap(a, b) < 0` is `boxes_meet(a, b)`, and 0 is a shared edge)."""
    return float(max(abs(a[0] - b[0]) - (a[2] + b[2]) / 2, abs(a[1] - b[1]) - (a[3] + b[3]) / 2))


class PocketUnlaid(ValueError):
    """A well pocket that can keep neither its gap from every bed nor its wall gap to its own dwelling - within
    `WELL_AMONG_DWELLINGS_PX` of the wall (`well_gap_to_dwellings`), its footprint clear of the house's (`box_gap`) - in
    this layout (feature 287, homes H09). The layout is then NOT the household's (`_lay_well_pocket` marks it `unlaid`
    and the fit refuses it, `_bundle_side_fits`), as a bath room with no seat is (`FixtureUnlaid`): another garden side
    or another seat is sought - never a well drawn out in the commons."""


def pocket_keeps_its_dwelling(box: tuple[float, float, float, float], house: tuple[float, float, float, float]) -> bool:
    """Does the pocket `box` keep the wall gap the wells rule reads to its own `house` (both (cx, cy, w, h), unturned in the
    house's frame, which the rake turns as one piece)? At most `WELL_AMONG_DWELLINGS_PX` from the wall, on the rule's own
    predicate (`well_gap_to_dwellings`, its center to the house's drawn quad), and its footprint - the wellhead and its
    margin - clear of the house's (`box_gap` at least 0: a shared edge, no overlap)."""
    hx, hy, hw, hh = house
    near = well_gap_to_dwellings([{"x": hx, "y": hy, "w": hw, "h": hh}], box[0], box[1]) <= WELL_AMONG_DWELLINGS_PX
    return near and box_gap(box, house) >= 0.0


def pocket_clear_of_beds(xs: Any, y: float, p: float, beds: Any, gap: float, house: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    """THE WELL POCKET NEVER ON A BED (feature 287 M8: the overlap matrix forbids a wellhead on a garden, its own household's
    too). The pocket, `p` square at height `y`, is offered at each flank in `xs` in turn (the flank away from the primary
    bed first); a bed split to flank the house on both walls (`_garden_beds`) can stand on either, and cohort 1-60 laid 8
    wells on a bed so. Where both flanks hold a bed, the pocket stands past the outermost bed of the first flank, `gap`
    beyond it - still beside the dooryard, on the same line.

    PUSHED, IT KEEPS THE GAP FROM EVERY BED (feature 287, homes H09): the push steps past each bed within `gap` of the
    pocket (`box_gap`), not only the beds it lies on, so a bed it clears by a hair - on the line, or beside it - is stepped
    past too, and the pocket it returns stands at least `gap` from every bed.

    ...AND ITS WALL GAP TO ITS OWN DWELLING (homes H09's other half, research R12): wherever it stands, the pocket keeps
    what the wells rule reads (`pocket_keeps_its_dwelling`) - a push past the beds walks it outward, so the push stops,
    refusing the layout (`PocketUnlaid`), the moment it is carried past the rule's reach; that also bounds the push."""
    for x in xs:
        box = (x, y, p, p)
        if not any(boxes_meet(box, b) for b in beds):
            return _kept(box, house)
    x = xs[0]
    side = 1.0 if x >= xs[-1] else -1.0
    while near := [b for b in beds if box_gap((x, y, p, p), b) < gap - 1e-9]:
        x = max(b[0] * side + b[2] / 2 for b in near) * side + side * (gap + p / 2)  # past the bed's outer edge on this flank
        _kept((x, y, p, p), house)  # every step walks it outward, so the first past the reach refuses (both flanks met a bed: one step at least)
    return (x, y, p, p)


def _kept(box: tuple[float, float, float, float], house: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    """`box`, if it keeps its dwelling (`pocket_keeps_its_dwelling`); else `PocketUnlaid`, naming the gap."""
    if not pocket_keeps_its_dwelling(box, house):
        wall = well_gap_to_dwellings([{"x": house[0], "y": house[1], "w": house[2], "h": house[3]}], box[0], box[1])
        raise PocketUnlaid(f"the well pocket at ({box[0]:.1f}, {box[1]:.1f}) stands {wall:.1f} px from its dwelling's wall, footprint gap {box_gap(box, house):.1f} px")
    return box


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
        fragment. Total bed area stays in the saien band (`garden_area_within_norms`). Returns (cx,cy,w,h) rects."""
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
        """The bundle at (hx, hy): its UNRAKED layout, built once per household and size (`_bundle_layout`), moved here
        and turned by this seat's rake (feature 276, FR-003, plan D10).

        WHY ONCE. The placer asks for this bundle at every candidate seat - the spiral's offsets, every 2 px of a
        slide, four garden sides - and rebuilt it each time (46,781 builds on the rescue scenario). A layout relative
        to its house center does not depend on the seat once its ROLLED parts - the yard's size, the garden's jitter,
        the bed split - are the household's rather than the seat's, so while a household's seat is sought
        (`_household_seat`, set by the placer) they are rolled at the seat it was sought from (the spec's Decisions
        Recorded: the same distributions, rolled per household). The RAKE stays the seat's, applied after the move, so
        the homestead still turns as one piece wherever it lands (GM 2026-09-26). Outside a seat search the rolls key
        on (hx, hy) as they always did. `rot` overrides the seat's turn (0.0: the unturned layout a caller measures).

        THE GROUND CLEARED IS THE GROUND DRAWN, AT ANY TURN (269 B18). The parts keep their true sizes - the drawing and
        the fixtures read a part in its house's frame - and `boxes` holds each part's axis-aligned box AS DRAWN, turned
        (`turned_box`); every fit rule reads the boxes, and the bundle's `bbox` is theirs. Under the old +/-5 degree
        rake the difference was two pixels and was let stand; a house turned 30 degrees, or a quarter turn, is not."""
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
            bool(getattr(self, "_household_well", False)),
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
        `grove_faces` beside it, when dispersed)."""
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
            # instead of all sitting east between houses. See research/homesteads.html 'Clustered and scattered villages (shūson, sanson)'.
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
            gw = min(gw * (1.0 + self._hjit(sx, sy, 3.0) * 0.25), self.px(48))  # garden [1.00,1.25]x, capped at 48 ft
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
            self._lay_well_pocket(base, hx, hy, hh, yh, gap)
            self._lay_fixtures(base, hx, hy, hw, hh, shed, seat)
            return base  # raked and boxed by `_bundle_geom`, per seat
        # DISPERSED farmstead: the farm's own GROVE round the ground it works, on the sides its settlement rolled
        # (feature 291, `grove_sides.py`). Laid out in the CANONICAL frame - the wind from the northwest, the deep bands
        # on the north and west, the yard on the south front, the garden on the east - then carried to the map's wind
        # by `dispersed_layout`'s turn. The multi-bed garden split is a NUCLEATED feature; a dispersed farm keeps one bed. Its
        # own well pocket is laid in the canonical frame (`canonical_farmstead`), turned with the rest - never `_lay_well_pocket`.
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
            sun_east=EAST_SHADE_REACH * self.bscale,
            way_in=self.px(WAY_IN_FT),
            pad=self.px(LANE_ROOM_FT) / 2.0,
            back=self.px(SERVICE_STRIP_FT),
            well=2.0 * self._well_vr() + self.px(6.0),  # the wellhead and a 3 ft margin, as `_lay_well_pocket`'s
        )
        # ...AND ITS FIXTURES, laid in the bundle as a nucleated household's are (feature 287, homes H32), clear of its own
        # grove (feature 291): the envelope admits the farm only with room for its privy, its wood shed and its bath room
        self._lay_fixtures(dispersed, hx, hy, hw, hh, False, seat, bands=dispersed["groves"])
        return dispersed

    def _lay_well_pocket(self: Settlement, base: dict[str, Any], hx: float, hy: float, hh: float, yh: float, gap: float) -> None:  # type: ignore[misc]
        """THE HOUSEHOLD'S WELL POCKET, a part of its homestead (feature 287, homes H09-H11): where the seating asked this
        household to carry one (`_household_well`), the wellhead's ground - its drawn well-house and a 3 ft margin - is
        laid beside the yard on the dooryard side, on the flank away from the garden (the side the byre takes, below it), so
        the envelope admits the household only with room for its well and the well stands among the doors it serves
        (within `WELL_AMONG_DWELLINGS_PX` of the wall: `pocket_clear_of_beds` refuses a pocket that would not be, and the
        layout is then marked `unlaid`, which the fit refuses). Beside the yard rather than before it, so the homestead
        reaches no deeper toward a paddy the yard faces than the yard does."""
        if not getattr(self, "_household_well", False):
            return
        p = 2.0 * self._well_vr() + self.px(6.0)
        yard = base["yard"]
        sx = -1.0 if base["garden"][0] > hx else 1.0  # away from the garden's side
        wy = hy + hh / 2 + gap + p / 2 + self.px(2.0)
        try:
            base["well"] = pocket_clear_of_beds([hx + sx * (yard[2] / 2 + gap + p / 2), hx - sx * (yard[2] / 2 + gap + p / 2)], wy, p, base["gardens"], gap, base["house"])
        except PocketUnlaid as refused:
            base["unlaid"] = str(refused)

    def _lay_fixtures(self: Settlement, base: dict[str, Any], hx: float, hy: float, hw: float, hh: float, shed: bool, seat: Any, bands: Any = ()) -> None:  # type: ignore[misc]
        """THE HOUSEHOLD'S FARMSTEAD FIXTURES, parts of its homestead (feature 287, homes H32, plan M5 and D9): the kinds its
        lot keeps (`_household_fixtures`, set by the seat search) laid beside the parts already laid - built ones a crown may
        not cover, the yard and the beds it may - in the house's frame (`homestead_parts/fixture_seats.py`), with the
        hamlet's rolled forms (`_fixture_forms`) and the household's own position roll. So the envelope admits a household
        only with room for its privy, its stack, its tree, and no later stage can take that room. A grove farm's `bands`
        (feature 291) are built ground too: no fixture stands in its own grove."""
        kinds = getattr(self, "_household_fixtures", None) or ()
        if not kinds:
            return
        sx, sy = seat

        def rel(r: Any) -> Any:
            return (r[0] - hx, r[1] - hy, r[2], r[3])

        roofs = [rel(r) for r in (base["house"], base.get("shed"), base.get("byre"), base.get("well"), *bands) if r is not None]
        ground = [rel(base["yard"]), *(rel(g) for g in base["gardens"])]
        forms = getattr(self, "_fixture_forms", None) or FixtureForms()
        annex = rel(base["byre"]) if base.get("byre") is not None else None
        notes: dict[str, Any] = {}
        try:
            laid = lay_fixtures(kinds, hw, hh, roofs, ground, rel(base["yard"]), shed, lambda salt: self._hjit(sx, sy, salt), forms, self.px, annex, notes)
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
        The grove arms are not moved: they are drawn unraked."""

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
