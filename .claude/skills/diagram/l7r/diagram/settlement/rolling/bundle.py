"""What a homestead BUNDLE is: house, threshing yard, dooryard garden beds, kura, grove arms. Pure geometry - it places nothing and draws nothing.

Split from settlement/rolling.py by feature 118 - see settlement/rolling/CLAUDE.md for the index.
"""

from typing import TYPE_CHECKING, Any

from .._geom import turn_about
from ..homestead_parts.fixture_seats import FixtureForms, lay_fixtures
from ..shrines_wells.byres import BYRE_FT, YARD_SHED_GAP_FT, byre_part
from .bearing import turned_box

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
        seat = getattr(self, "_household_seat", None) or (hx, hy)
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

        def moved(r: Any) -> Any:
            return None if r is None else (r[0] + hx, r[1] + hy, r[2], r[3])

        base: dict[str, Any] = {k: ([moved(r) for r in v] if k == "gardens" else {f: moved(r) for f, r in v.items()} if k == "fixtures" else moved(v)) for k, v in tpl.items()}
        frame = base.pop("_frame", None)
        turn = self._turn_at(hx, hy) if rot is None else rot
        self._rake_parts(base, hx, hy, turn)
        boxes: dict[str, Any] = {k: (turned_box(base[k], turn) if base.get(k) is not None else None) for k in ("house", "yard", "shed", "byre", "well")}
        boxes["gardens"] = [turned_box(g, turn) for g in base["gardens"]]
        boxes["fixtures"] = {f: turned_box(r, turn) for f, r in (base.get("fixtures") or {}).items()}
        base["boxes"] = boxes
        if frame is None:  # nucleated: every part, as drawn
            rects = [r for r in (boxes["house"], boxes["yard"], *boxes["gardens"], boxes.get("shed"), boxes.get("byre"), boxes.get("well"), *boxes["fixtures"].values()) if r is not None]
            base["bbox"] = self._bbox_of(rects)
        else:  # dispersed: the grove's unraked frame with the turned yard and garden
            base["bbox"] = self._bbox_of([frame, boxes["yard"], boxes["gardens"][0], *([boxes["well"]] if boxes.get("well") else [])])
        return base

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
        windward GROVE as an L (an N band + a W band for the default NW wind), sized ~6x the house. The
        dooryard GARDEN tucks tight to the house's E (lee) wall, the threshing YARD sits on the sunny S
        front. Returns a dict of (cx, cy, w, h) rects keyed house/garden/yard (+ grove_n/grove_w when
        dispersed) plus the whole-bundle bbox. (NW windward; other winds are a later generalisation.)"""
        gap = self.px(3)  # 3 ft between a house and its yard/garden, at this map's ftpx
        gw, gh = 0.48 * hw, 0.85 * hh  # garden - tight to the house, scales with wealth
        sx, sy = seat  # the rolls key on the household's seat (see `_bundle_geom`)
        yw, yh = self._yard_dims(hw, hh, sx, sy)  # threshing/drying yard - the rolled area (homestead_parts._yard_area_ft2); the placer reserves exactly what gets drawn
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
        east = hx + hw / 2 + gap + gw
        south = hy + hh / 2 + gap + yh
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
            # instead of all sitting east between houses. See research/homesteads.html 'Does a hamlet have to be nucleated at all?'.
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
                base["shed"] = (hx, hy - 0.60 * hh, 0.46 * hw, 0.30 * hh)
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
        # DISPERSED farmstead (the shipped ring-village behavior): the windward GROVE as an L (an N
        # band + a W band, for the default NW wind), sized so the grove footprint is ~6x the house. The
        # multi-bed garden split is a NUCLEATED feature (clean E/W walls, no grove or shed in the way); a
        # dispersed farm keeps its single east garden (its west wall carries the windbreak grove).
        base["gardens"] = [base["garden"]]
        b = 1.57 * hh  # grove band depth -> grove ~= 6x house area
        west = hx - hw / 2 - gap - b
        north = hy - hh / 2 - gap - b
        base["grove_n"] = ((west + east) / 2, north + b / 2, east - west, b)
        base["grove_w"] = (west + b / 2, (north + b + south) / 2, b, south - (north + b))
        base["_frame"] = ((west + east) / 2, (north + south) / 2, east - west, south - north)  # the grove's frame, unraked
        self._lay_well_pocket(base, hx, hy, hh, yh, gap)
        return base

    def _lay_well_pocket(self: Settlement, base: dict[str, Any], hx: float, hy: float, hh: float, yh: float, gap: float) -> None:  # type: ignore[misc]
        """THE HOUSEHOLD'S WELL POCKET, a part of its homestead (feature 287, homes H09-H11): where the seating asked this
        household to carry one (`_household_well`), the wellhead's ground - its drawn well-house and a 3 ft margin - is
        laid beside the yard on the dooryard side, on the flank away from the garden (the side the byre takes, below it), so
        the envelope admits the household only with room for its well and the well stands among the doors it serves
        (within `WELL_AMONG_DWELLINGS_PX` of the wall, by construction). Beside the yard rather than before it, so the
        homestead reaches no deeper toward a paddy the yard faces than the yard does."""
        if not getattr(self, "_household_well", False):
            return
        p = 2.0 * self._well_vr() + self.px(6.0)
        yard = base["yard"]
        sx = -1.0 if base["garden"][0] > hx else 1.0  # away from the garden's side
        base["well"] = (hx + sx * (yard[2] / 2 + gap + p / 2), hy + hh / 2 + gap + p / 2 + self.px(2.0), p, p)

    def _lay_fixtures(self: Settlement, base: dict[str, Any], hx: float, hy: float, hw: float, hh: float, shed: bool, seat: Any) -> None:  # type: ignore[misc]
        """THE HOUSEHOLD'S FARMSTEAD FIXTURES, parts of its homestead (feature 287, homes H32, plan M5 and D9): the kinds its
        lot keeps (`_household_fixtures`, set by the seat search) laid beside the parts already laid - built ones a crown may
        not cover, the yard and the beds it may - in the house's frame (`homestead_parts/fixture_seats.py`), with the
        hamlet's rolled forms (`_fixture_forms`) and the household's own position roll. So the envelope admits a household
        only with room for its privy, its stack, its tree, and no later stage can take that room."""
        kinds = getattr(self, "_household_fixtures", None) or ()
        if not kinds:
            return
        sx, sy = seat

        def rel(r: Any) -> Any:
            return (r[0] - hx, r[1] - hy, r[2], r[3])

        roofs = [rel(r) for r in (base["house"], base.get("shed"), base.get("byre"), base.get("well")) if r is not None]
        ground = [rel(base["yard"]), *(rel(g) for g in base["gardens"])]
        forms = getattr(self, "_fixture_forms", None) or FixtureForms()
        annex = rel(base["byre"]) if base.get("byre") is not None else None
        laid = lay_fixtures(kinds, hw, hh, roofs, ground, rel(base["yard"]), shed, lambda salt: self._hjit(sx, sy, salt), forms, self.px, annex)
        base["fixtures"] = {k: (hx + r[0], hy + r[1], r[2], r[3]) for k, r in laid.items()}

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

        def turned(r: Any) -> Any:
            ((x, y),) = turn_about([(r[0], r[1])], hx, hy, rot)
            return (x, y, r[2], r[3])

        if base.get("yard") is not None:
            base["yard"] = turned(base["yard"])
        base["gardens"] = [turned(g) for g in base["gardens"]]
        base["garden"] = base["gardens"][0]
        for part in ("shed", "byre", "well"):
            if part in base:
                base[part] = turned(base[part])
        if base.get("fixtures"):
            base["fixtures"] = {f: turned(r) for f, r in base["fixtures"].items()}
