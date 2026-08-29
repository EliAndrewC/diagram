"""Split from settlement.py by feature 025 - see settlement/CLAUDE.md for the index."""

import itertools
import json
import os
import shutil
import subprocess
import sys
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from l7r.diagram.interactive.classes import PLACE
from l7r.diagram.interactive.page import ink_census, unregistered_classes, write_html
from l7r.diagram.interactive.tags import ClsTag

from ._geom import LAND, Poly, Pt, label_quad, label_tilt, linear_tilt, linear_tilt_full, point_in_poly, rects_overlap, segments_cross

if TYPE_CHECKING:
    from .core import Settlement


class FinishMixin:
    # ---- annotation

    def _record_label(  # type: ignore[misc]
        self: Settlement, x: float, y: float, text: str, size: float, anchor: str, z: int, ref: Sequence[float] | None = None, rot: float = 0.0, box: tuple[float, float, float, float] | None = None
    ) -> None:
        w = len(text) * size * 0.55  # rough serif advance; slightly generous so near-misses flag
        x0 = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
        # record the TEXT (element [5]) too, so the gate can verify a zone/neighborhood label actually
        # sits with the cluster it names (same side of the wall, among its buildings)
        # `box` is the WRAPPED caption's block (T39) - narrower and taller than the one-line box;
        # a one-line caption passes none and records exactly what it always did.
        bx0, by0, bx1, by1 = box if box is not None else (x0, y - size * 0.8, x0 + w, y + size * 0.25)
        rec: list[Any] = [round(bx0, 1), round(by0, 1), round(bx1, 1), round(by1, 1), z, text]
        if ref is not None or rot:
            # element [6]: the box of the ONE feature this caption names, recorded only by the
            # standoff-ladder path (`place_caption` / the road label). A district caption names an
            # AREA, not a thing, so it carries no referent and `label_hugs_its_referent` skips it.
            # (Recorded as null when only a tilt follows - the elements are positional.)
            rec.append([round(float(v), 1) for v in ref] if ref is not None else None)
        if rot:
            # element [7]: the caption's TILT in degrees (see label_tilt) - present ONLY when
            # nonzero, so every level caption's record stays byte-identical to the pre-tilt
            # format (the 695-manifest regression corpus reads unchanged). Elements [0..3] stay
            # the UNROTATED box; label_quad / label_aabb derive the drawn geometry from it.
            rec.append(rot)
        self.M["labels"].append(rec)

    def label(  # type: ignore[misc]
        self: Settlement,
        x: float,
        y: float,
        text: str,
        size: float = 12,
        anchor: str = "middle",
        italic: bool = False,
        weight: str = "normal",
        color: str = "#2D2A24",
        ref: Sequence[float] | None = None,
        rot: float = 0.0,
        linear: bool = False,
        full_tilt: bool = False,
        wrap: bool = True,
        cls: ClsTag = None,
    ) -> None:
        # `cls` is the class of the FEATURE the caption names (feature 134 FR-006): the label and its
        # subject share one class, so hovering either highlights both and a click on either opens the
        # subject's explanation. A caption with no subject class inherits the enclosing feature() scope.
        esc = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        st = ' font-style="italic"' if italic else ''
        # `rot` is the SUBJECT's rotation; the fold turns it into the caption's tilt (0 for any
        # square rotation, so nothing changes for level callers). A tilted caption rotates about
        # its recorded box's CENTER, so label_quad reads the drawn glyph run straight off the
        # record (GM 2026-08-02, angled-building labels).
        #
        # `linear=True` says the subject is a LINE, not a box - a road, a street, a frontage row
        # laid along one - and takes `linear_tilt`'s CLAMP instead of `label_tilt`'s FOLD (GM
        # 2026-08-08). The two are not interchangeable: the fold would send a 72-degree road's
        # caption to -18 degrees, an angle nothing on the map is drawn at.
        # `full_tilt=True` (linear subjects only) takes linear_tilt_full's unclamped angle - the
        # GM's 2026-08-09 extension for along-row captions like the wharf granary rows
        tilt = (linear_tilt_full(rot) if full_tilt else linear_tilt(rot)) if linear else label_tilt(rot)
        # A CAPTION WRAPS WHEN THAT IS WHAT CLEARS IT (GM 2026-08-27, feature 133 T39): *"if the label
        # was split across multiple lines, and that caused it to not overlap with anything, then we
        # should do that. If running the label on one line caused it to not overlap with anything,
        # then we should do that. If both things cause the label to overlap with something, then we
        # can just pick one."* One line first; then two, then three, each tested as its rotated block
        # against every footprint and every caption already on the sheet; the first clear layout is
        # drawn, and when none is clear the one-liner is. See `_caption_lines` for how a label is cut.
        lines = self._caption_lines(text, x, y, size, anchor, tilt) if wrap else [text]
        n = len(lines)
        lh = size * 1.15  # line pitch: the one-line box is 1.05 em tall, and a hair of lead between lines
        w_ = max(len(ln) for ln in lines) * size * 0.55
        x0_ = x - w_ / 2 if anchor == "middle" else (x - w_ if anchor == "end" else x)
        cx_, cy_ = x0_ + w_ / 2, y - size * 0.275  # the one-line box's center; a wrapped block keeps it
        box = (x0_, cy_ - (size * 1.05 + (n - 1) * lh) / 2, x0_ + w_, cy_ + (size * 1.05 + (n - 1) * lh) / 2)
        tr = f' transform="rotate({tilt:.1f} {cx_:.1f} {cy_:.1f})"' if tilt else ''
        # labels live in the topmost LABEL layer so nothing - not a road, not a wall, not a kido or torii
        # - ever paints over the text (a label must always be fully readable)
        if n == 1:
            body = esc
            y_first = y
        else:
            y_first = y - (n - 1) * lh / 2
            body = "".join(f'<tspan x="{x:.0f}" dy="{0 if i == 0 else lh:.1f}">{ln.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}</tspan>' for i, ln in enumerate(lines))
        z = self.add_label(
            f'<text x="{x:.0f}" y="{y_first:.0f}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}"{st}{tr} fill="{color}" paint-order="stroke" stroke="{LAND}" stroke-width="3">{body}</text>',
            cls=cls,
        )
        self._record_label(x, y, text, size, anchor, z, ref, tilt, box=box if n > 1 else None)

    def _caption_lines(self: Settlement, text: str, x: float, y: float, size: float, anchor: str, tilt: float) -> list[str]:  # type: ignore[misc]
        """The lines a caption is set on: one if that clears the sheet, else the first of two or three
        that does, else one (feature 133 T39 - the rule is in `label`).

        HOW A LABEL IS CUT. Words are never broken; a cut is a split of the word list into contiguous
        lines. Among the splits into `n` lines the one with the SHORTEST longest line wins (the block
        is as narrow as it can be), ties broken toward even lengths. A line that is only one short
        word - "of", "the", "to", anything of three letters or fewer - is refused whenever the label
        has more words than lines, so "Shrine of Benten" is cut as "Shrine of / Benten" or
        "Shrine / of Benten", never with "of" alone (the GM: *"put it on whichever line had fewer
        letters otherwise"*). Three lines are tried only after two, and only for three words or more.

        WHAT COUNTS AS OVERLAP: the caption's block, rotated about its center by `tilt` exactly as
        the SVG is, against `label_blockers()` - every recorded footprint (rotation-aware AABBs) and
        every caption already on the sheet - with the separating-axis test, so a tilted block is
        judged by its true quad rather than by a bounding box that would wrap for nothing."""
        words = text.split()
        if len(words) < 2:
            return [text]
        blockers: list[Poly] = self.label_blocker_quads() + [label_quad(lb) for lb in self.M["labels"] if len(lb) > 3]
        lh = size * 1.15

        def _clear(lines: list[str]) -> bool:
            n = len(lines)
            w_ = max(len(ln) for ln in lines) * size * 0.55
            x0_ = x - w_ / 2 if anchor == "middle" else (x - w_ if anchor == "end" else x)
            h_ = size * 1.05 + (n - 1) * lh
            cy_ = y - size * 0.275
            quad = label_quad([x0_, cy_ - h_ / 2, x0_ + w_, cy_ + h_ / 2, 0, text, None, tilt])
            return not any(rects_overlap(quad, b) for b in blockers)

        def _cut(n: int) -> list[str] | None:
            best: tuple[tuple[int, int], list[str]] | None = None
            for cuts in itertools.combinations(range(1, len(words)), n - 1):
                bounds = (0, *cuts, len(words))
                lines = [" ".join(words[a:b]) for a, b in zip(bounds, bounds[1:], strict=False)]
                if len(words) > n and any(len(ln) <= 3 for ln in lines):
                    continue  # a short word never stands alone
                score = (max(len(ln) for ln in lines), max(len(ln) for ln in lines) - min(len(ln) for ln in lines))
                if best is None or score < best[0]:
                    best = (score, lines)
            return best[1] if best else None

        if _clear([text]):
            return [text]
        for n in (2, 3):
            if n > len(words):
                break
            lines = _cut(n)
            if lines and _clear(lines):
                return lines
        return [text]

    def _text_width(self: Settlement, s: str, fs: float) -> float:  # type: ignore[misc]
        """Measured pixel width of bold `s` at font-size `fs` in the RENDER font (DejaVu Serif Bold -
        what resvg substitutes for 'serif'), via PIL; falls back to a calibrated estimate when PIL or
        the font is absent. WHY (GM 2026-07-21): the em/char estimates under-measured wide lowercase
        names - 'Akagahara' measured 180px against a 167px estimate, and the missing 14px ran the
        name off its placard's right edge. Measuring the actual glyphs makes the padding true.

        The layout engine is PINNED to BASIC, and that pin is load-bearing (2026-07-25). PIL picks its
        engine at runtime - RAQM when libraqm happens to be installed, BASIC when it is not - and the
        two disagree: BASIC sums integer-rounded glyph advances, RAQM sums true subpixel ones, so the
        same name measures 110.00 vs 110.59 ('Honda') or 103.95 vs 101.70 ('Tango'). That fraction of
        a pixel sizes the title placard, which is recorded in the manifest, so a container that merely
        HAS libraqm regenerates every titled map to different bytes: a laptop crash and a container
        rebuild dirtied all 16 tracked pool manifests at once, with no code change behind it. Which
        engine is not the point (both are within a pixel of what resvg draws, under 12px of padding) -
        being a pure function of the font FILE is, so the pool stays byte-reproducible on any
        container. `test_text_width_is_pinned_to_the_basic_layout_engine` holds the pin."""
        try:
            from PIL import ImageFont

            f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", int(round(fs)), layout_engine=ImageFont.Layout.BASIC)
            return float(f.getlength(s))
        except Exception:  # PIL / font absent: the engine stays standalone on a generous estimate
            return len(s) * fs * 0.62

    def title(self: Settlement, name: str, fs: float = 30, prefer: tuple[float, float, float, float] | None = None) -> None:  # type: ignore[misc]
        """Place the map title (the bold place name plus a scale bar under it) over BLANK space: scan the
        rendered window for a spot where the box clears every feature (buildings, fields, water, groves,
        the pond), scanning top-first so the title lands high when it can. Records the placed box in M['title']
        so `title_clear_of_features` can verify it. Call AFTER crop_to_content, so the search runs over the
        framed window. Falls back to the top-left of the view (or the canvas center) only if the map is too full
        to find any gap.

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
        tw, th = self._text_width(name, fs) + 4, fs * 1.2  # MEASURED text box (+4 breathing room) - see _text_width; symmetric placard padding follows for free
        bar_px, bar_ft = 100.0, round(100 * self.ftpx)
        PAD = 12  # placard padding around the text block
        bw, bh = max(tw, bar_px) + 2 * PAD, th + 46 + 2 * PAD  # the searched box: the whole placard
        vx0, vy0, vw, vh = self.view if self.view else (0, 0, self.W, self.H)
        # THE RESERVED POCKET FIRST (feature 150): the scripted tier holds a pocket of blank ground for the
        # title before the coppice and the belt are seated, and DENTS the windbreak around it - so a title
        # that then lands in another corner leaves the dent as a hole in the belt (Kuwabata, a 40-50 ft bare
        # run). If the caller names its pocket and the placard fits there clear of every obstacle, that is
        # where it goes; main's blank-then-cover scan (feature 137 T06) is the fallback beneath it.
        spot = None
        if prefer is not None:
            _px, _py = prefer[0] + 6.0, prefer[1] + 6.0
            if _px + bw <= prefer[2] and _py + bh <= prefer[3] and self._box_clear(_px, _py, _px + bw, _py + bh, self._title_obstacles()):
                spot = (_px, _py)
        if spot is None:
            spot = self._blank_label_spot(vx0, vy0, vw, vh, bw, bh) or self._blank_label_spot(
                vx0, vy0, vw, vh, bw, bh, cover_ok=True
            )  # blank first; cover (a belt, a wood) as the last resort before the corner (feature 137 T06)
        if spot:
            px0, py0 = spot
        elif self.view:
            # MAP TOO FULL: the four corners, first one that hides nothing but cover, else the top-left
            # (feature 137 T06 - seed 13's top-left corner was a dry plot while its bottom-right was scrub)
            obs = self._title_obstacles(cover_ok=True)
            corners = [(vx0 + 30, vy0 + 16), (vx0 + vw - bw - 30, vy0 + 16), (vx0 + 30, vy0 + vh - bh - 16), (vx0 + vw - bw - 30, vy0 + vh - bh - 16)]
            clean = next(((cx, cy) for cx, cy in corners if self._box_clear(cx, cy, cx + bw, cy + bh, obs)), None)
            if clean is not None:
                px0, py0 = clean
            else:
                # THE TITLE BAND, the last rung (feature 137 T06): every corner hides a plot (seed 13's dry hem
                # rings the whole view). The title is not a feature of the place and owes it no ground, so
                # the sheet grows a band above the map sized to the placard, declared in meta so
                # `crop_hugs_content` allows exactly that much on the north edge, and the placard sits in
                # it - over nothing, unless a feature runs off the frame there, which the check still reports.
                band = bh + 32
                vy0 -= band
                vh += band
                self.set_view(vx0, vy0, vw, vh)
                self.M["meta"]["title_band"] = round(band, 1)
                px0, py0 = vx0 + 30, vy0 + 16
        else:
            px0, py0 = self.W / 2 - bw / 2, 22
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
        # THE PLACARD IS THE PLACE (feature 154, GM 2026-08-29): "I would like to be able to click on
        # the title card for a settlement and then pull up an explanation of the type of settlement
        # that this is." It was ruled map furniture on 2026-08-27 and that ruling is OVERTURNED - the
        # card and its name now carry the reserved class `place` (`interactive/classes.py` PLACE, with
        # the overturning recorded beside the ruling it replaces), so hovering lights the card and
        # clicking opens the settlement's own overview. THE SCALE BAR BELOW KEEPS `cls="-"`: it is
        # still furniture, and it has nothing to tell a reader that the card does not.
        self.add_label(  # the card FIRST, so every text draws over it (add_label draws in call order)
            f'<g><rect x="{px0:.0f}" y="{py0:.0f}" width="{bw:.0f}" height="{bh:.0f}" rx="7" fill="#F7F0DC" stroke="#8C7A55" stroke-width="1.6"/>'
            f'<rect x="{px0 + 3.5:.0f}" y="{py0 + 3.5:.0f}" width="{bw - 7:.0f}" height="{bh - 7:.0f}" rx="5" fill="none" stroke="#BCAA7E" stroke-width="0.8"/></g>',
            cls=PLACE,
        )
        self.add_label(f'<text x="{pcx:.0f}" y="{y + fs:.0f}" text-anchor="middle" font-size="{fs}" font-weight="bold" fill="#2D2A24">{name}</text>', cls=PLACE)
        bx0, bx1, by = pcx - bar_px / 2, pcx + bar_px / 2, y + th + 12  # bar CENTERED under the name, on the placard's axis
        # THE BOX IS THE INK, not the placard's foot (settlement-review 2026-08-29, Kashikawa). The bottom
        # was `y + bh` - the placard's own base - which over-claimed 26 px, 41% of the box's height, and
        # reached 12 px BELOW the placard that contains it. Nothing keeps out of this box (the two checks
        # that read `scalebar` test its `ft` against the declared scale and skip its geometry), so the
        # over-claim bought nothing and cost the interactive map, which highlights the recorded box. The
        # last ink is the "(1 px = N ft)" caption at baseline `by + 31`, 10 pt, so its descender ends ~2 px
        # under that.
        self.M["scalebar"] = {"ft": bar_ft, "ftpx": self.ftpx, "bbox": [round(bx0, 1), round(by - 5, 1), round(bx1, 1), round(by + 33, 1)]}
        self.add_label(
            f'<g stroke="#3A2E1C" stroke-width="2">'
            f'<line x1="{bx0:.0f}" y1="{by:.0f}" x2="{bx1:.0f}" y2="{by:.0f}"/>'
            f'<line x1="{bx0:.0f}" y1="{by - 5:.0f}" x2="{bx0:.0f}" y2="{by + 5:.0f}"/>'
            f'<line x1="{bx1:.0f}" y1="{by - 5:.0f}" x2="{bx1:.0f}" y2="{by + 5:.0f}"/>'
            f'<line x1="{(bx0 + bx1) / 2:.0f}" y1="{by - 3:.0f}" x2="{(bx0 + bx1) / 2:.0f}" y2="{by + 3:.0f}" stroke-width="1"/>'
            f'</g>',
            cls="-",
        )
        self.add_label(f'<text x="{(bx0 + bx1) / 2:.0f}" y="{by + 17:.0f}" text-anchor="middle" font-size="12" fill="#3A2E1C">{bar_ft} ft</text>', cls="-")
        self.add_label(f'<text x="{(bx0 + bx1) / 2:.0f}" y="{by + 31:.0f}" text-anchor="middle" font-size="10" font-style="italic" fill="#5C4830">(1 px = {self.ftpx:g} ft)</text>', cls="-")

    def _title_obstacles(self: Settlement, cover_ok: bool = False) -> tuple[list[Any], list[Any], list[Any]]:  # type: ignore[misc]
        """Feature footprints a title must clear, as (rects, polys, lines). Solid buildings/plots -> rects;
        the fields, groves, and commons -> polygons (so the title can sit in the empty corners around a diagonal
        field); the pond -> a rect; water lines + lanes -> polylines (a title must not cross a road or stream)."""
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
        _woodland = [c for c in self.M.get("commons", []) if c.get("role") == "woodland" and c.get("poly")]
        _cover = [] if cover_ok else self.M.get("village_groves", []) + self.M.get("bamboo_stands", []) + _woodland
        for o in _cover + self.M.get("marshes", []):
            polys.append([tuple(p) for p in o["poly"]])
        # ...and the WELLS and the NOTICE BOARD (feature 150, settlement-review of Kuwabata: the placard sat on the
        # east public well, its glyph showing through the card's edge). Both are traffic-sited fixtures with no
        # w/h - a well records its drawn radius `vr`, the board its `w`/`h` - and neither was in the list above.
        for o in self.M.get("wells", []):
            _wr = float(o.get("vr", o.get("r", 8.0))) + 4.0
            rects.append((o["x"] - _wr, o["y"] - _wr, o["x"] + _wr, o["y"] + _wr))
        for o in self.M.get("kosatsuba", []):
            _kw, _kh = float(o.get("w", 14.0)) / 2 + 4.0, float(o.get("h", 8.0)) / 2 + 4.0
            rects.append((o["x"] - _kw, o["y"] - _kh, o["x"] + _kw, o["y"] + _kh))
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
        _woodland = [c for c in self.M.get("commons", []) if c.get("role") == "woodland" and c.get("poly")]
        for o in self.M.get("village_groves", []) + self.M.get("bamboo_stands", []) + self.M.get("marshes", []) + _woodland:
            polys.append([tuple(p) for p in o["poly"]])
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
        return rects, polys, lines

    def _box_clear(self: Settlement, bx0: float, by0: float, bx1: float, by1: float, obs: Any) -> bool:  # type: ignore[misc]
        """Whether the axis-aligned box clears every obstacle in (rects, polys, lines)."""
        rects, polys, lines = obs
        for ox0, oy0, ox1, oy1 in rects:
            if not (bx1 < ox0 or bx0 > ox1 or by1 < oy0 or by0 > oy1):
                return False
        corners = [(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)]
        for poly in polys:
            n = len(poly)
            if (
                any(point_in_poly(cx, cy, poly) for cx, cy in corners)
                or any(bx0 <= vx <= bx1 and by0 <= vy <= by1 for vx, vy in poly)
                or any(segments_cross(corners[e], corners[(e + 1) % 4], poly[k], poly[(k + 1) % n]) for e in range(4) for k in range(n))
            ):
                return False
        for poly in lines:
            if any(bx0 <= vx <= bx1 and by0 <= vy <= by1 for vx, vy in poly) or any(
                segments_cross(corners[e], corners[(e + 1) % 4], poly[k], poly[k + 1]) for e in range(4) for k in range(len(poly) - 1)
            ):
                return False
        return True

    def _blank_label_spot(self: Settlement, vx0: float, vy0: float, vw: float, vh: float, tw: float, th: float, margin: float = 22, step: float = 24, cover_ok: bool = False) -> Pt | None:  # type: ignore[misc]
        """Scan the window (top-to-bottom, left-to-right) for the first box of size (tw, th) that clears every
        feature; returns its (x, y) top-left, or None if the map is too full. With `cover_ok` the belt, the
        bamboo and the woodland commons are not obstacles (the placard may sit on cover, never on a
        building, a plot, a field, water, a lane or a label - `title_clear_of_features`, feature 137)."""
        obs = self._title_obstacles(cover_ok=cover_ok)
        y = vy0 + margin
        while y + th <= vy0 + vh - margin:
            x = vx0 + margin
            while x + tw <= vx0 + vw - margin:
                if self._box_clear(x, y, x + tw, y + th, obs):
                    return (x, y)
                x += step
            y += step
        return None

    def finish(self: Settlement, basepath: str, render: bool = True, png_width: int = 2600) -> int:  # type: ignore[misc]
        # BACKSTOP for the deferred canopy: crop_to_content / crop_city normally flush it, but a map
        # that frames to the bare canvas never calls either (Hoshizora), and a queued stand that is
        # never flushed is a wood with no trees. Idempotent, so the usual crop-time flush still wins.
        self.flush_tree_stands()
        # THE FIELD'S CHORDS FOR THE GATE (feature 140): `houses_clear_of_paddies` measures the same few chords the
        # placer measured (`rolling/fit.py::_field_chains`) - open chains facing the planned seat when there is one
        # (`keepout_chains`, each chord with its outward normal), a closed simplified ring (`keepout`) when not.
        from l7r.diagram.settlement._geom.primitives import FIELD_KEEPOUT_EPS, facing_chains, keepout_ring  # noqa: PLC0415 - finish-time only

        _face = getattr(self, "field_face", None)
        if _face is not None and self.field_polys:
            # THE PLACER'S OWN CHAINS, recorded flat: `houses_clear_of_paddies` must measure the very chords placement
            # measured, or a seat can pass one and fail the other (Mizuguchi did, 2026-08-28, when the gate rebuilt
            # chains from the manifest's rounded outline instead).
            _chains, _rings = self._field_chains()
            self.M["field_chains"] = [[[[round(_a[0], 1), round(_a[1], 1)], [round(_b[0], 1), round(_b[1], 1)], [round(_n[0], 4), round(_n[1], 4)]] for _a, _b, _n in _ch] for _ch in _chains]
        for _fld in self.M.get("fields") or []:
            _ol = [(float(_x), float(_y)) for _x, _y in (_fld.get("outline") or [])]
            if len(_ol) < 4 or "keepout" in _fld or "keepout_chords" in _fld:
                continue
            if _face is not None:
                _fld["keepout_chords"] = sum(len(_ch) for _ch in facing_chains(_ol, _face, FIELD_KEEPOUT_EPS))  # the count the record reports; the gate reads M["field_chains"]
            else:
                _keep, _chords = keepout_ring(_ol, _ol, FIELD_KEEPOUT_EPS, filled=True)
                _fld["keepout"] = [[round(_p[0], 1), round(_p[1], 1)] for _p in _keep]
                _fld["keepout_chords"] = len(_chords)
        # Deferred place_caption() seats, in call order, against the FINISHED map - and BEFORE the
        # road caption, which goes last because it has by far the most room to move: its subject is
        # a whole road segment with a wide slide set, where a market row's caption has one short
        # stretch of frontage to sit against. Most-constrained-first; the road yields.
        for _tx, _bx, _sz, _it, _wt, _co, _hi, _sl, _ro in self._captions:
            _lx, _ly = self._best_label_spot(_bx, _tx, _sz, hint=_hi, slides=_sl, tilt=_ro)
            self.label(_lx, _ly, _tx, _sz, italic=_it, weight=_wt, color=_co, ref=_bx, rot=_ro)
        self._captions: list[tuple[Any, ...]] = []
        if getattr(self, "_road_label", None):
            self._finish_road_label()  # feature 145: the Imperial-road caption, a town/city feature, lives in structures/ground.py
            self._road_label: Any = None  # declared Any at structures/ground.py; re-declared for the checker (the attribute is conditional)
        # Every block below is built as TWO aligned lists - the strings, and their feature classes
        # (feature 134): the string block is spliced into `self.out` exactly as before, the class
        # block into `self.out_cls` at the same index, so the side-list stays index-aligned with the
        # SVG through every splice. The `<g opacity>` wrappers carry no class (they draw no ink).
        splices: list[Any] = []  # (placeholder_idx, block, block_cls) - spliced high-index-first below
        if self._ground_idx is not None:  # the ordered linear-ground block (alley<street<road)
            feats = sorted(self.ground, key=lambda g: (g["zpri"], g["seq"]))
            block: list[Any] = []
            bcls: list[ClsTag] = []
            edge_zs: list[Any] = []
            bed_zs: list[Any] = []
            for g in feats:  # EDGES first (the dark borders), bottom of the block
                if g["edge"] is not None:
                    edge_zs.append(self._ground_idx + len(block))
                    block.append(g["edge"])
                    bcls.append(g["cls"])
            for g in feats:  # then BEDS (paved surfaces) - they merge at crossings
                if g["bed"] is not None:
                    g["rec"][g["zkey"]] = self._ground_idx + len(block)  # recorded z = the bed's draw position
                    bed_zs.append(self._ground_idx + len(block))
                    block.append(g["bed"])
                    bcls.append(g["cls"])
            for g in feats:  # then TOP marks (center dashes / gravel speckle)
                if g["top"] is not None:
                    block.append(g["top"])
                    bcls.append(g["cls"])
            if edge_zs:  # every edge sits below every bed -> clean crossroads
                self.M["ground_edge_zmax"] = max(edge_zs)
            if bed_zs:
                self.M["ground_bed_zmin"] = min(bed_zs)
            splices.append((self._ground_idx, block, bcls))
        # Does a LATE-block channel JOIN the pond? Then the pond's FILL + SHEEN must RELOCATE into
        # the late block (GM 2026-07-23, Tango's in-wall tank): the late block draws after the whole
        # shared block, so an early fill can never cover a late mouth's inside-the-rim overshoot -
        # the channel's round end-cap rode ON TOP of the open water and read as intersecting the
        # pond. The rim EDGE stays early (below every bed, so the mouth still covers it); only the
        # fill and sheen move, re-emitted LAST among the late beds - restoring exactly the covering
        # order the shared block gives an early feeder. Gated by pond_fill_covers_channel_mouths.
        # ONE WATER BLOCK (feature 150 T53, GM 2026-08-28: "when a stream meets a irrigated channel or where an
        # irrigated channel or a ditch meets a pond ... it clearly looks like one is rendered on top of the
        # other ... water just flows"). There were TWO blocks - the early one (streams, the pond, a moat) at
        # the first water call and the LATE one (a comb's ditch net) after the field's plots - each its own
        # opacity group, so where a ditch met a brook the two 0.85 groups stacked into a darker seam, and a
        # sheen in one block rode over a bed in the other. Every watercourse now composites in ONE block at
        # the late position when a late block exists (else the early one): all RIMS first, then every bed in
        # one shared-opacity group with the pond's fill last (so a feeder's overshoot inside the rim is
        # painted over), then every sheen. A pond's rim is therefore under every bed that reaches it - the
        # dark outline stops where the channel enters, which is the GM's "continuous flow of water".
        _entries = list(self.water) + list(self.late_water)
        _widx = self._late_water_idx if self._late_water_idx is not None else self._water_idx
        if _entries and _widx is not None:
            for w in self.water:  # a pond-anchored feeder is snapped to the rim now that the pond is known
                w["_bed"], w["_sheen"] = w["bed"], w["sheen"]
                if w.get("clip") is not None and self.M.get("pond"):
                    cp = self._clip_to_pond(w["clip"]["pts"])
                    dd = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in cp)
                    w["_bed"] = w["clip"]["bed_t"].format(dd=dd)
                    if w["clip"]["sheen_t"] is not None:
                        w["_sheen"] = w["clip"]["sheen_t"].format(dd=dd)
            for w in self.late_water:
                w["_bed"], w["_sheen"] = w["bed"], w["sheen"]
            wblock: list[Any] = []
            wcls: list[ClsTag] = []
            bedzs: list[Any] = []
            sheenzs: list[Any] = []
            for w in _entries:  # rims below every bed
                if w.get("edge") is not None:
                    wblock.append(w["edge"])
                    wcls.append(w["cls"])
            wblock.append('<g opacity="0.85">')
            wcls.append(None)
            for w in sorted(_entries, key=lambda w: bool(w.get("pond_fill"))):  # the pond FILL last (stable)
                w["rec"]["bedz"] = _widx + len(wblock)
                bedzs.append(_widx + len(wblock))
                wblock.append(w["_bed"])
                wcls.append(w["cls"])
            wblock.append('</g>')
            wcls.append(None)
            wblock.append('<g opacity="0.55">')
            wcls.append(None)
            for w in _entries:
                if w["_sheen"] is not None:
                    w["rec"]["sheenz"] = _widx + len(wblock)
                    sheenzs.append(_widx + len(wblock))
                    wblock.append(w["_sheen"])
                    wcls.append(w["cls"])
            wblock.append('</g>')
            wcls.append(None)
            if bedzs:
                self.M["water_bed_zmax"] = max(bedzs)
            if sheenzs:
                self.M["water_sheen_zmin"] = min(sheenzs)
            if self._pond_entry is not None:
                self._pond_entry["rec"]["late"] = self._late_water_idx is not None  # the fill lives in the late block when one exists
            splices.append((_widx, wblock, wcls))
            if self._late_water_idx is not None and self._water_idx is not None:
                splices.append((self._water_idx, [""], [None]))  # the early placeholder empties; nothing renders there
        for idx, block, bcls_ in sorted(splices, key=lambda s: -s[0]):  # high index first so the lower stays valid
            self.out[idx : idx + 1] = block
            self.out_cls[idx : idx + 1] = bcls_
        if self.view:  # crop the viewBox to the requested window
            ox, oy, vw, vh = self.view
            self.out[0] = self.out[0].replace(f'viewBox="0 0 {self.W} {self.H}"', f'viewBox="{ox} {oy} {vw} {vh}"')
        body = self.out + self.walls + self.top + self.toplabels + ['</svg>']  # WALLS over lanes; TOP furniture; LABEL text topmost
        body_cls: list[ClsTag] = self.out_cls + self.walls_cls + self.top_cls + self.toplabels_cls + [None]
        if len(body_cls) != len(body):  # the side-list drifted from the stream - a stream write that bypassed add()
            raise RuntimeError(f"feature-class side list out of step with the record streams: {len(body_cls)} tags for {len(body)} strings")
        with open(basepath + '.svg', 'w') as f:
            f.write('\n'.join(body))
        # THE INTERACTIVE PAGE (feature 134): the same primitives, each wrapped by its class, with the
        # explanations of the classes present. Written beside the SVG whenever the SVG is - a string
        # pass, so DIAGRAM_SKIP_RENDER (which spares only the raster) does not skip it. The census
        # goes into the manifest FIRST so the gate can read it (`all_ink_is_ruled_on`, FR-009).
        self.M["ink_classes"], self.M["unclassed_ink"] = ink_census(body, body_cls)
        self.M["unregistered_classes"] = unregistered_classes(self.M["ink_classes"])
        write_html(basepath + '.html', body, body_cls, name=str(self.M["meta"].get("name") or os.path.basename(basepath)), meta=self.M["meta"], manifest=self.M)
        with open(basepath + '.json', 'w') as f:
            json.dump(self.M, f)
        # Two env knobs make iteration cheap without changing committed output (see SKILL.md
        # 'Render pipeline'; since the resvg switch the raster is ~0.6s even for the biggest map,
        # so these mostly save the render when nothing will look at the PNG):
        #   DIAGRAM_SKIP_RENDER  - skip the raster entirely; the gate reads the JSON, so tests set this and
        #                          never pay to render a PNG no test looks at.
        #   DIAGRAM_PNG_WIDTH=N  - render at N px instead of 2600; unset for the full-res committed PNG.
        if render and not os.environ.get("DIAGRAM_SKIP_RENDER"):
            env_w = os.environ.get("DIAGRAM_PNG_WIDTH")
            self.render_png(basepath, int(env_w) if env_w else png_width)  # keep the .png paired with the .svg
        return len(self.placed)

    def render_png(self: Settlement, basepath: str, width: int = 2600) -> None:  # type: ignore[misc]
        """Rasterize basepath.svg -> basepath.png via resvg.

        Called from finish() so the PNG can never drift from the SVG: there is no way to
        regenerate a map's SVG (by hand or via the test harness, which re-runs every gen)
        without also refreshing its PNG. Settlement maps need ~2600px for the small labels.

        resvg, not rsvg-convert (and deliberately NO fallback - resvg is required, see the
        SKILL.md skill-load install check): profiling Tango (2026-07) showed rsvg-convert
        spent ~16s at 2600px, ~2/3 of it on foliage circles lying entirely outside the
        cropped city viewBox; resvg culls off-view geometry properly and rasterizes the
        same SVG in ~0.6s with visually identical output. Two font requirements for that
        "identical": resvg's generic-family defaults name MS fonts, so 'serif' must be
        mapped to DejaVu Serif explicitly (--serif-family), and resvg does not synthesize
        oblique, so the real italic faces (fonts-dejavu-extra) must be installed or every
        italic label silently renders upright.
        A no-op (with a warning) when resvg is absent - the skill cannot render at all
        without it, so that is a host-setup problem, not a generation bug."""
        exe = shutil.which('resvg')
        if not exe:  # pragma: no cover - depends on the host toolchain, not on any code path
            sys.stderr.write(f'warning: resvg not found (sudo apt-get install -y resvg fonts-dejavu-extra); {basepath}.png not refreshed\n')
            return
        subprocess.run([exe, '--width', str(width), '--serif-family', 'DejaVu Serif', basepath + '.svg', basepath + '.png'], check=True)
