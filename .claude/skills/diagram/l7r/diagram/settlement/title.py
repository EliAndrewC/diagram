"""The map's title placard - its size, where it goes, the band grown for it, and the tests of its seat. Split out of `finish.py`
by feature 319, when the placard's text was set for reading (1.5x) and `finish.py` crossed the 1,000-line bar; see
settlement/CLAUDE.md for the index.

Research: map finishing - CONVENTION: the title placard and its band; geometry - NONE"""

from typing import TYPE_CHECKING, Any

from l7r.diagram.interactive.classes import PLACE

from ._geom import BoxObstacles, Pt
from .finish import band_keeps_the_strips

if TYPE_CHECKING:
    from .core import Settlement

#: THE PLACARD'S TEXT IS SET FOR READING (GM 2026-10-03, feature 319: *"my eyes are not great ... I end up using my browser's
#: resize to blow everything up to 150% ... I think we could probably do the same thing with the title card as well. At least
#: the text on it - obviously the map scale of one pixel per foot will not change"*). The name and the scale bar's two captions
#: are drawn 1.5 times the size they were (30, 12 and 10 px); the card grows around them, and the bar keeps its 100 map-px.
PLACARD_TEXT_SCALE = 1.5
"""Research: placard text size - CONVENTION: map furniture sized for the GM's reading; the scale bar's length is unchanged"""
#: the placard's padding around its text block, before the text scale (it scales with it, so the card keeps its proportions)
PLACARD_PAD = 12.0
"""Research: placard padding - CONVENTION: map furniture"""


def placard_height(fs: float = 30) -> float:
    """The title placard's height for a name drawn at `fs` before `PLACARD_TEXT_SCALE` - the name's line, the scale bar with its
    two captions, and the padding. It does not depend on the name; the width does (`FinishMixin.placard_size`). The hamlet's
    title band allowance and pocket rise are derived from it (`hamletgen/hinterland/frame.py`), so the card cannot outgrow them.
    Research: placard size - CONVENTION: map furniture, sized from its measured text"""
    k = PLACARD_TEXT_SCALE
    return fs * k * 1.2 + 46 * k + 2 * PLACARD_PAD * k


class TitleMixin:
    """The title placard's mixin (feature 319 split it out of `FinishMixin`)."""

    def placard_size(self: Settlement, name: str, fs: float = 30) -> tuple[float, float, float, float, float]:  # type: ignore[misc]
        """(text width, text height, card width, card height, padding) of the title placard for `name` - THE one statement of
        its size, which `title()` draws and the hamlet's title pocket reserves (`hamletgen/hinterland/frame.py`). The pocket
        restated the formula by hand until feature 319, so a change to the card's text size would have left the two apart.
        `fs` is the name's size before `PLACARD_TEXT_SCALE`.
        Research: placard size - CONVENTION: map furniture, sized from its measured text"""
        k = PLACARD_TEXT_SCALE
        tw, th = self._text_width(name, fs * k) + 4, fs * k * 1.2  # MEASURED text box (+4 breathing room) - see _text_width
        pad = PLACARD_PAD * k
        return tw, th, max(tw, 100.0) + 2 * pad, placard_height(fs), pad

    def title(self: Settlement, name: str, fs: float = 30, prefer: tuple[float, float, float, float] | None = None) -> None:  # type: ignore[misc]
        """Place the map title (the bold place name plus a scale bar under it) over BLANK space: scan the
        rendered window for a spot where the box clears every feature (buildings, fields, water, groves,
        the pond), scanning top-first so the title lands high when it can. Records the placed box in M['title']
        so `title_clear_of_features` can verify it. Call AFTER crop_to_content, so the search runs over the
        framed window. Where the map is too full to find any gap, a corner that hides nothing but cover, and failing
        that a band grown on the sheet for it (`_title_band`) - over nothing, never over a feature (feature 287, L14).

        SCALE BAR (GM 2026-07-20: every settlement map shows its scale, matching the Mode A compound
        sheets): the bar spans 100 map-px, which is a round real distance at every rung of the GM's
        scale ladder - 100 ft at hamlet/town (1 ft/px), 200 ft at village (2 ft/px), 300 ft at
        provincial city (3 ft/px) - drawn in the Mode A furniture style (end ticks + mid tick, the
        distance under the bar, a fine-print '(1 px = N ft)' line). The searched AND recorded box
        covers the title + bar together, so `title_clear_of_features` gates the bar's placement too.

        PLACARD (GM 2026-07-21): the title + scale bar sit on a stylized parchment CARD - a cream
        cartouche (lighter than the #EFE3C2 ground, double-line brown border) drawn under the text -
        so the block stays legible no matter what ground cover it lands over (the satoyama ring put
        scrub speckle nearly everywhere a title can sit, and ink-on-scrub was hard to read). The
        searched and recorded box is the PLACARD's extent, so the clearance check gates the whole
        card; `title_has_placard` gates its presence (a manifest without one predates the card)."""
        k = PLACARD_TEXT_SCALE  # the name and the bar's captions drawn for reading (GM 2026-10-03); the bar stays 100 map-px
        tw, th, bw, bh, PAD = self.placard_size(name, fs)  # the searched box: the whole placard
        fs = fs * k
        bar_px, bar_ft = 100.0, round(100 * self.ftpx)
        vx0, vy0, vw, vh = self.view if self.view else (0, 0, self.W, self.H)
        # THE RESERVED POCKET FIRST (feature 150): the scripted tier holds a pocket of blank ground for the
        # title before the coppice and the belt are seated, and DENTS the windbreak around it - so a title
        # that then lands in another corner leaves the dent as a hole in the belt (Kuwabata, a 40-50 ft bare
        # run). If the caller names its pocket and the placard fits there clear of every obstacle, that is
        # where it goes; main's blank-then-cover scan (feature 137 T06) is the fallback beneath it.
        spot = None
        if prefer is not None:
            # WITHIN the pocket, not only at its corner (settlement-review, feature 230 pass 12). The reservation is
            # cut a little larger than the placard, and this took the top-left of it and gave up if anything at all
            # stood there - so one byre seated in a corner of the pocket AFTER it was reserved sent the title out to
            # the cover rung and onto the windbreak, with the rest of the reserved ground standing empty. The scan is
            # the same one the fallback uses, bounded to the rectangle that was held for this.
            spot = self._blank_label_spot(prefer[0], prefer[1], prefer[2] - prefer[0], prefer[3] - prefer[1], bw, bh, margin=2.0, step=8.0)
        if spot is None:
            spot = self._blank_label_spot(vx0, vy0, vw, vh, bw, bh) or self._blank_label_spot(
                vx0, vy0, vw, vh, bw, bh, cover_ok=True
            )  # blank first; cover (a belt, a wood) as the last resort before the corner (feature 137 T06)
        if spot:
            px0, py0 = spot
        else:
            # MAP TOO FULL: the four corners, first one that hides nothing but cover (feature 137 T06 - seed 13's top-left
            # corner was a dry plot while its bottom-right was scrub). A map with no view is framed by its whole canvas -
            # a town canvas IS its view (Hirameki) - and takes the same rungs; the old canvas-center fallback set the
            # placard over whatever stood there (feature 287, labels L14)
            obs = self._title_obstacles(cover_ok=True)
            corners = [(vx0 + 30, vy0 + 16), (vx0 + vw - bw - 30, vy0 + 16), (vx0 + 30, vy0 + vh - bh - 16), (vx0 + vw - bw - 30, vy0 + vh - bh - 16)]
            clean = next(((cx, cy) for cx, cy in corners if self._box_clear(cx, cy, cx + bw, cy + bh, obs)), None)
            px0, py0 = clean if clean is not None else self._title_band(vx0, vy0, vw, vh, bw, bh, obs)
        y = py0 + PAD  # the text block's top, inside the card
        pcx = px0 + bw / 2  # the placard's axis: the name AND the scale bar center on it (GM 2026-07-21)
        self.M["title"] = {
            "name": name,
            "bbox": [round(px0, 1), round(py0, 1), round(px0 + bw, 1), round(py0 + bh, 1)],
            "placard": [round(px0, 1), round(py0, 1), round(px0 + bw, 1), round(py0 + bh, 1)],
        }
        # OPAQUE, not 0.94 (settlement-review 2026-08-29, Kashikawa): at 0.94 the ground cover showed
        # through - 6,900 of 79,772 interior pixels, 8.65%, with grass, brush dots and two whole pine
        # glyphs legible at native resolution - and the placard read as a decal laid on the field rather
        # than a card. This is the SAME defect, and the same fix, as the field grave on that map eight
        # days earlier ("painted at 0.9 opacity over an intact lattice ... it is opaque now"); one was
        # fixed for that reason and this one was left translucent with nothing recorded either way.
        # THE PLACARD IS THE PLACE (feature 156, GM 2026-08-29): "I would like to be able to click on
        # the title card for a settlement and then pull up an explanation of the type of settlement
        # that this is." It was ruled map furniture on 2026-08-27 and that ruling is OVERTURNED - the
        # card and its name now carry the reserved class `place` (`interactive/classes/` PLACE, with
        # the overturning recorded beside the ruling it replaces), so hovering lights the card and
        # clicking opens the settlement's own overview. THE SCALE BAR BELOW KEEPS `cls="-"`: it is
        # still furniture, and it has nothing to tell a reader that the card does not.
        self.add_label(  # the card FIRST, so every text draws over it (add_label draws in call order)
            f'<g><rect x="{px0:.0f}" y="{py0:.0f}" width="{bw:.0f}" height="{bh:.0f}" rx="7" fill="#F7F0DC" stroke="#8C7A55" stroke-width="1.6"/>'
            f'<rect x="{px0 + 3.5:.0f}" y="{py0 + 3.5:.0f}" width="{bw - 7:.0f}" height="{bh - 7:.0f}" rx="5" fill="none" stroke="#BCAA7E" stroke-width="0.8"/></g>',
            cls=PLACE,
        )
        self.add_label(f'<text x="{pcx:.0f}" y="{y + fs:.0f}" text-anchor="middle" font-size="{fs}" font-weight="bold" fill="#2D2A24">{name}</text>', cls=PLACE)
        bx0, bx1, by = pcx - bar_px / 2, pcx + bar_px / 2, y + th + 12 * k  # bar CENTERED under the name, on the placard's axis
        # THE BOX IS THE INK, not the placard's foot (settlement-review 2026-08-29, Kashikawa). The bottom
        # was `y + bh` - the placard's own base - which over-claimed 26 px, 41% of the box's height, and
        # reached 12 px BELOW the placard that contains it. Nothing keeps out of this box (the two checks
        # that read `scalebar` test its `ft` against the declared scale and skip its geometry), so the
        # over-claim bought nothing and cost the interactive map, which highlights the recorded box. The
        # last ink is the "(1 px = N ft)" caption at baseline `by + 31`, 10 pt, so its descender ends ~2 px
        # under that.
        self.M["scalebar"] = {"ft": bar_ft, "ftpx": self.ftpx, "bbox": [round(bx0, 1), round(by - 5, 1), round(bx1, 1), round(by + 33 * k, 1)]}
        self.add_label(
            # `class="scale"` is a NAME for the page's stylesheet, not a hover target (feature 203, GM 2026-09-07: the
            # lit scrub was painting over the card in raster mode): the placard is vector in both modes, its card
            # is opaque, so the bar drawn on it must be vector too - the ruling above stands, `cls="-"` stays
            f'<g class="scale" stroke="#3A2E1C" stroke-width="2">'
            f'<line x1="{bx0:.0f}" y1="{by:.0f}" x2="{bx1:.0f}" y2="{by:.0f}"/>'
            f'<line x1="{bx0:.0f}" y1="{by - 5:.0f}" x2="{bx0:.0f}" y2="{by + 5:.0f}"/>'
            f'<line x1="{bx1:.0f}" y1="{by - 5:.0f}" x2="{bx1:.0f}" y2="{by + 5:.0f}"/>'
            f'<line x1="{(bx0 + bx1) / 2:.0f}" y1="{by - 3:.0f}" x2="{(bx0 + bx1) / 2:.0f}" y2="{by + 3:.0f}" stroke-width="1"/>'
            f'</g>',
            cls="-",
        )
        self.add_label(f'<text x="{(bx0 + bx1) / 2:.0f}" y="{by + 17 * k:.0f}" text-anchor="middle" font-size="{12 * k:g}" fill="#3A2E1C">{bar_ft} ft</text>', cls="-")
        self.add_label(
            f'<text x="{(bx0 + bx1) / 2:.0f}" y="{by + 31 * k:.0f}" text-anchor="middle" font-size="{10 * k:g}" font-style="italic" fill="#5C4830">(1 px = {self.ftpx:g} ft)</text>', cls="-"
        )

    def _title_band(self: Settlement, vx0: float, vy0: float, vw: float, vh: float, bw: float, bh: float, obs: BoxObstacles) -> Pt:  # type: ignore[misc]
        """THE TITLE BAND, the last rung (feature 137 T06; feature 287, labels L14): every corner hides a plot (seed 13's
        dry hem rings the whole view). The title is not a feature of the place and owes it no ground, so the sheet grows
        a band sized to the placard - declared in meta (`title_band`, `title_band_side`), so the manifest says how much of
        the view is sheet rather than map - and the placard
        sits in it OVER NOTHING. The band shows the canvas past the frame, where a lane or a stream running off the map
        still draws, so the placard's x is SCANNED along the band with the test every other rung uses (`_box_clear`); then
        the band under the map; and where a way crosses the whole of both, the map's ink is clipped at the frame it had
        (`meta.neatline`: a title panel outside the map's neatline - a map drawing convention), which leaves the band
        blank by construction. A band inside the map is map, and its bare ground is clothed as the view's was
        (`refill_the_view`) - cover the placard may stand on, as on every other rung. Returns the placard's top-left."""
        band = bh + 32
        for north in (True, False):
            # ...NEVER ON A FLANK A WATERWARD REED STRIP RUNS OFF (feature 287, water W43): the band there would show ground past
            # the strip's end inside the frame - a lake with a ruled edge - so that flank is not taken; the other is, or the
            # neatline below, which leaves the map (the strip's view) the frame it had
            if not band_keeps_the_strips(self.M, (vx0, vy0, vw, vh), (vx0, vy0 - band if north else vy0, vw, vh + band)):
                continue
            y = vy0 - band + 16 if north else vy0 + vh + 16
            x = vx0 + 30
            while x + bw <= vx0 + vw - 30:
                if self._box_clear(x, y, x + bw, y + bh, obs):
                    self.set_view(vx0, vy0 - band if north else vy0, vw, vh + band)
                    self.M["meta"]["title_band"] = round(band, 1)
                    if not north:
                        self.M["meta"]["title_band_side"] = "south"
                    # ...and the band is map, so it is clothed as the view was (feature 287, woods W11): the holes are
                    # filled over the view as it ends, not the one the hinterland filled (`refill_the_view`)
                    self.refill_the_view()
                    return (x, y)
                x += 8
        self.M["meta"]["neatline"] = [round(v, 1) for v in (vx0, vy0, vw, vh)]
        self.set_view(vx0, vy0 - band, vw, vh + band)
        self.M["meta"]["title_band"] = round(band, 1)
        return (vx0 + 30, vy0 - band + 16)

    def title_clear(self: Settlement) -> bool:  # type: ignore[misc]
        """THE ONE PREDICATE of `title_clear_of_features` (feature 287, labels L14): the placard clears every feature it may
        not cover (`_title_obstacles(cover_ok=True)`) - or stands wholly outside the neatline the map's ink is clipped at."""
        x0, y0, x1, y1 = self.M["title"]["placard"]
        neat = self.M["meta"].get("neatline")
        if neat and (y1 <= neat[1] or y0 >= neat[1] + neat[3] or x1 <= neat[0] or x0 >= neat[0] + neat[2]):
            return True
        return self._box_clear(x0, y0, x1, y1, self._title_obstacles(cover_ok=True))

    def _title_obstacles(self: Settlement, cover_ok: bool = False, planned: Any = ()) -> BoxObstacles:  # type: ignore[misc]
        """Feature footprints a title must clear, indexed for box queries (feature 222) from (rects, polys, lines). Solid buildings/plots -> rects;
        the fields, groves, and commons -> polygons (so the title can sit in the empty corners around a diagonal
        field); the pond -> a rect; water lines + lanes -> polylines (a title must not cross a road or stream).

        `planned` is ground a LATER stage will fill and that is not on the map yet - the windbreak's band while the
        title's pocket is being RESERVED (settlement-review, feature 230 pass 12). Reserving blank ground that the
        belt is about to be planted on is a reservation that costs the belt rather than the title: on Kuwabata it
        took the pocket out of the belt's windward third and cut 34 of its 87 clumps, to hold ground that was empty
        only because the trees had not been drawn yet. It is empty for the RESERVATION and not for the title's own
        search, which runs after the belt and reads the clumps themselves."""
        rects: list[Any] = []
        polys: list[Any] = []
        lines: list[Any] = []
        for k in (
            "houses",
            "gardens",
            "threshing_yards",
            "groves",
            "dry_plots",
            "buildings",
            "manors",
            "religious",
            "shrines",
            "flophouses",
            "storehouses",
            "merchant_estates",
            "cemeteries",
            "mausoleums",
            "cremation_grounds",
            "ossuaries",
            "ministries",
            # the homestead's own small buildings and fixtures (the 269 landing's review of Mizuguchi: the title placard
            # covered a woodpile whole - none of these keys was here, so a title could sit on any of them on any map)
            "farm_fixtures",
            "byres",
            "farm_sheds",
            "retirement_houses",
        ):
            for o in self.M.get(k, []):
                if o.get("poly"):
                    xs = [p[0] for p in o["poly"]]
                    ys = [p[1] for p in o["poly"]]
                    rects.append((min(xs), min(ys), max(xs), max(ys)))
                elif "w" in o and "h" in o:
                    rects.append((o["x"] - o["w"] / 2, o["y"] - o["h"] / 2, o["x"] + o["w"] / 2, o["y"] + o["h"] / 2))
        for lb in self.M.get("labels", []):  # placed LABEL boxes: a title must never cover a label
            rects.append((lb[0], lb[1], lb[2], lb[3]))  # (caught 2026-07-23: the Tango content crop landed the
            #                                             placard on the 'pauper ossuary mound' label)
        # NOT the scrub commons: it is sparse GROUND COVER (a feathered scatter of grass tufts on open ground),
        # not a feature with a footprint, and a bold place name reads perfectly well over it. Treating it as an
        # obstacle only worked while some ground was left bare - once the commons properly clothes the field's
        # voids too, scrub covers nearly the whole map and a title could find nowhere at all to sit. The grove
        # (dense closed canopy) and the marsh (a distinct wetland) stay obstacles.
        # ...and a WOODLAND commons is dense canopy too, so it is an obstacle by the same test the
        # paragraph above applies (2026-08-17). The exclusion above is for the SCRUB commons - a
        # feathered scatter of grass tufts that a bold place name reads perfectly well over - and a
        # `role="woodland"` parcel is not that: it is a stand of tree crowns, the same closed canopy
        # as a grove. Left out, the placard printed over 64-68% of one of Sawada's two woodland
        # parcels, with a dozen crown circles ghosting up through the title card: one of the map's
        # two woods two-thirds invisible, and the title reading as smudged. The grazing parcels stay
        # excluded, which is what keeps a title from having nowhere to sit.
        polys += [[tuple(q) for q in ring] for ring in planned]
        _woodland = [c for c in self.M.get("commons", []) if c.get("role") == "woodland" and c.get("poly")]
        _cover = [] if cover_ok else self.M.get("bamboo_stands", []) + _woodland
        for o in _cover + self.M.get("marshes", []):
            polys.append([tuple(p) for p in o["poly"]])
        # A GROVE BLOCKS WHERE ITS TREES ARE, NOT WHERE ITS OUTLINE IS (settlement-review, feature 230 pass 12).
        # The belt was an obstacle by its recorded POLYGON, and that polygon is the band the clumps were seated
        # in rather than the canopy they drew: a hamlet that holds a pocket of bare ground for its own name
        # inside that band - which is exactly what `title_pocket` and the belt's dent arrange - had the title
        # refuse its own reservation, fall through to the cover rung, and print over the belt somewhere else.
        # Measured on Kuwabata: the placard hid 174 ft of a 440 ft belt and 28 of its clumps while the pocket it
        # had reserved stood empty. The clumps ARE the ink, so they are what a title must miss.
        if not cover_ok:
            for g in self.M.get("village_groves", []):
                _gr = float(g.get("r") or 0.0)
                rects += [(float(c[0]) - _gr, float(c[1]) - _gr, float(c[0]) + _gr, float(c[1]) + _gr) for c in (g.get("clumps") or [])]
        # ...and the WELLS and the NOTICE BOARD (feature 150, settlement-review of Kuwabata: the placard sat on the
        # east public well, its glyph showing through the card's edge). Both are traffic-sited fixtures with no
        # w/h - a well records its drawn radius `vr`, the board its `w`/`h` - and neither was in the list above.
        for o in self.M.get("wells", []):
            _wr = float(o.get("vr", o.get("r", 8.0))) + 4.0
            rects.append((o["x"] - _wr, o["y"] - _wr, o["x"] + _wr, o["y"] + _wr))
        for o in self.M.get("kosatsuba", []):
            _kw, _kh = float(o.get("w", 14.0)) / 2 + 4.0, float(o.get("h", 8.0)) / 2 + 4.0
            rects.append((o["x"] - _kw, o["y"] - _kh, o["x"] + _kw, o["y"] + _kh))
        # ONE BLOCK, NOT TWO (feature 222, Principle XIV). A second copy of the labels loop and an UNCONDITIONAL
        # loop over the groves, the bamboo stands, the marshes and the woodland stood here from feature 137 T06
        # until 2026-09-11, so `cover_ok=True` - the cover rung of the title ladder - never excluded anything
        # and every title that missed blank ground fell straight to a corner or the band. The rung works now;
        # which pool titles it moved is in specs/222 research R2.
        for fd in self.M.get("fields", []):
            polys.append([tuple(p) for p in fd["outline"]])
        if self.M.get("pond"):
            cx, cy, rx, ry = self.M["pond"]
            rects.append((cx - rx, cy - ry, cx + rx, cy + ry))
        for o in self.M.get("streams", []) + self.M.get("channels", []):
            lines.append([tuple(p) for p in o["poly"]])
        for ln in self.M.get("lanes", []):
            lines.append([tuple(p) for p in ln["pts"]])
        # CITY barriers + arteries (caught 2026-07-23, the aggressive Tango content crop): with no blank
        # corner left, the placard landed straddling the rampart/moat band - the wall, moat, ring road,
        # and the through-road are obstacles too (crossing the centerline is what the box test catches;
        # the placard is taller than the wall-moat gap, so it cannot hide between them).
        for key in ("wall", "moat", "ring_road", "road"):
            pl = self.M.get(key)
            if pl and len(pl) >= 2:
                lines.append([tuple(p) for p in pl])
        return BoxObstacles(rects, polys, lines)

    def _box_clear(self: Settlement, bx0: float, by0: float, bx1: float, by1: float, obs: BoxObstacles) -> bool:  # type: ignore[misc]
        """Whether the axis-aligned box clears every obstacle - asked of the index `_title_obstacles` built
        (feature 222); the linear scan this was is `_geom.box_clear_brute`, the oracle its tests hold it to."""
        return obs.clear(bx0, by0, bx1, by1)

    def _blank_label_spot(  # type: ignore[misc]
        self: Settlement, vx0: float, vy0: float, vw: float, vh: float, tw: float, th: float, margin: float = 22, step: float = 24, cover_ok: bool = False, planned: Any = ()
    ) -> Pt | None:
        """Scan the window (top-to-bottom, left-to-right) for the first box of size (tw, th) that clears every
        feature; returns its (x, y) top-left, or None if the map is too full. With `cover_ok` the belt, the
        bamboo and the woodland commons are not obstacles (the placard may sit on cover, never on a
        building, a plot, a field, water, a lane or a label - `title_clear_of_features`, feature 137)."""
        obs = self._title_obstacles(cover_ok=cover_ok, planned=planned)
        y = vy0 + margin
        while y + th <= vy0 + vh - margin:
            x = vx0 + margin
            while x + tw <= vx0 + vw - margin:
                if self._box_clear(x, y, x + tw, y + th, obs):
                    return (x, y)
                x += step
            y += step
        return None
