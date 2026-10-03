"""Ground given over to the dead: where a settlement buries, entombs, burns and stores its bones.

Split from settlement/civic_grounds.py by feature 115 - see settlement/civic_grounds/CLAUDE.md for the index.

Research: plumbing - NONE
"""

import math
import random
from typing import TYPE_CHECKING, Any

from .._geom import (
    HALL_CAPTION_FS,
    Pt,
    point_in_poly,
    smooth_closed,
)
from .._knobs import CITY_TIER_SCALES

if TYPE_CHECKING:
    from ..core import Settlement

# THE ROOFED FIRE BED IS THE MINORITY (feature 280 M70, research/questions/0238-cremation-grounds-and-bone-mounds-kasoba.html 'Cremation grounds and bone mounds (kasoba)'): most cremation grounds were
# open-air to the end of Edo, the four-post roofed bed and the snow-country hut coming in around mid-Edo. How many were
# roofed no page says - a GUESS, rolled off the ground's own seat.
ROOFED_SHARE = 0.25
"""The share of cremation grounds whose fire bed is roofed.

Research:
    roofed bed the minority - research/questions/0238-cremation-grounds-and-bone-mounds-kasoba.drawing.html
    the share - GUESS: 0.25
"""


def cremation_outline(cx: float, cy: float, rx: float, ry: float, n: int, jitter: float, rnd: random.Random) -> str:
    """An SVG points string for a worn, ragged oval: n vertices round (cx, cy), each radius scaled by a factor
    drawn from 1 +/- jitter - the cremation ground's cleared edge, its burned ground and its ash bed (feature 272).

    Research: worn ragged outline - CONVENTION
    """
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n
        f = 1 + rnd.uniform(-jitter, jitter)
        pts.append(f"{cx + rx * f * math.cos(a):.1f},{cy + ry * f * math.sin(a):.1f}")
    return " ".join(pts)


class FuneraryGroundsMixin:
    def cemetery(  # type: ignore[misc]
        self: Settlement,
        cx: float,
        cy: float,
        w: float,
        h: float,
        rot: float = 0,
        label: Any = None,
        label_above: bool = False,
        parish: bool = True,
        organic: bool | None = None,
        label_xy: Pt | None = None,
    ) -> None:
        """A BURIAL GROUND - rows of grave markers (sotoba / stone stelae) with a couple of taller
        memorial stupas. Every settlement above a hamlet buries its dead: a Buddhist danka PARISH
        ground sits in a TEMPLE / MONASTERY precinct (death is the Buddhist clergy's business), while
        a Shinto SHRINE keeps death-pollution (kegare) at arm's length - so a graveyard sits well
        clear of any shrine. parish=False marks a NON-parish burial ground (a village-style plot not
        attached to a temple, e.g. one serving an in-wall farm quarter) - exempt from the temple-precinct
        rule. organic=True draws an IRREGULAR earthen plot; organic=None (the default) DERIVES it from
        parish: every non-parish COMMON ground is organic, parish precinct plots stay ruled rectangles.
        Historical grounding (researched 2026-07-23, written up in research/questions/0235-village-burial-grounds-bochi.html ('shape of the common
        ground'): Japan's commoner burial grounds - Kyoto's burial fields, village sanmai, Edo's packed
        temple yards - were unplotted and terrain-following, never surveyed; Song China's state pauper
        cemeteries (louzeyuan, 1104 on) WERE surveyed walled compounds with numbered rowed plots, so a
        specific ordered city may pass organic=False to draw that Chinese form deliberately. Rokugan
        defaults to the Japanese mode (GM decision). The recorded bbox + the no-build block stay the
        w x h rectangle either way, so the placement/clearance checks are unaffected - only the DRAWN
        ground and the markers within it follow the blob. Records M['cemeteries'] and blocks placement.
        label_above puts the label over the plot (for a cramped intramural ground whose label would otherwise spill onto its temple).

        Research:
            unplotted ground for a common burial ground - research/questions/0235-village-burial-grounds-bochi.html, research/questions/0235-village-burial-grounds-bochi.drawing.html: organic unless parish
            parish plot ruled - UNRESEARCHED: a rectangle in the temple precinct
            rows of low markers - research/questions/0235-village-burial-grounds-bochi.drawing.html: 9 px apart, each wholly inside the ground
            marker heights - CONVENTION: 6 to 8 px
            a taller memorial stone or two - research/questions/0235-village-burial-grounds-bochi.drawing.html: two stupas
            no cleared band round the ground - research/questions/0224-ground-swept-clear-around-shrines-and-graves.drawing.html
            keep-clear margin - UNRESEARCHED: 8 px
            caption - CONVENTION
        """
        if organic is None:
            organic = not parish
        st = random.getstate()
        random.seed(int(abs(cx) + abs(cy) * 3 + w))
        g = [f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot:.1f})">']
        if organic:  # a jittered blob INSCRIBED in the w x h footprint - star-shaped from the center
            blob = [(math.cos(a) * (w / 2) * jr, math.sin(a) * (h / 2) * jr) for a, jr in ((2 * math.pi * i / 14, random.uniform(0.74, 1.0)) for i in range(14))]
            g.append(f'<path d="{smooth_closed(blob)}" fill="#CFC6B4" stroke="#8C8470" stroke-width="1.3" opacity="0.75"/>')
        else:
            blob = None
            g.append(f'<rect x="{-w / 2:.1f}" y="{-h / 2:.1f}" width="{w:.0f}" height="{h:.0f}" rx="3" fill="#CFC6B4" stroke="#8C8470" stroke-width="1.3" opacity="0.75"/>')
        yy = -h / 2 + 9
        while yy < h / 2 - 5:  # rows of small upright grave markers (kept inside the blob)
            xx = -w / 2 + 8
            while xx < w / 2 - 5:
                if blob is None or point_in_poly(xx, yy, blob):
                    mh = random.choice([6, 7, 8])
                    # its TOP inside the blob too (feature 273, settlement-review on Kuwabata): a marker is drawn
                    # upward from its base, and on a small ground a base just inside the rim put its top 5 ft out
                    if blob is not None and not point_in_poly(xx, yy - mh, blob):
                        xx += 9
                        continue
                    g.append(f'<rect x="{xx - 1.4:.1f}" y="{yy - mh:.1f}" width="2.8" height="{mh}" rx="1" fill="#9AA1A4" stroke="#5A584F" stroke-width="0.5"/>')
                xx += 9
            yy += 9
        stupas = (
            [(-w * 0.24, -h * 0.22), (w * 0.24, -h * 0.22)]
            if organic  # interior anchors (always inside the blob)
            else [(-w / 2 + 13, -h / 2 + 1), (w / 2 - 13, -h / 2 + 1)]
        )  # a couple of taller memorial stupas
        for sxp, syp in stupas:
            g.append(f'<rect x="{sxp - 2.2:.1f}" y="{syp:.1f}" width="4.4" height="13" rx="1.5" fill="#B7B0A0" stroke="#5A584F" stroke-width="0.7"/>')
            g.append(f'<circle cx="{sxp:.1f}" cy="{syp:.1f}" r="2.4" fill="#B7B0A0" stroke="#5A584F" stroke-width="0.7"/>')
        random.setstate(st)
        g.append('</g>')
        self.add(''.join(g))
        self.M.setdefault("cemeteries", []).append({"x": round(cx, 1), "y": round(cy, 1), "w": w, "h": h, "rot": round(rot, 1), "parish": parish})
        self.placed.append((cx, cy, w, h))
        bm = 8
        self.block_polys.append([(cx - w / 2 - bm, cy - h / 2 - bm), (cx + w / 2 + bm, cy - h / 2 - bm), (cx + w / 2 + bm, cy + h / 2 + bm), (cx - w / 2 - bm, cy + h / 2 + bm)])
        # THE GROUND CLEARS ONLY ITSELF (feature 280 M66, research/questions/0224-ground-swept-clear-around-shrines-and-graves.html): the grave itself was weeded and
        # topped up at Qingming in 1630s Beijing, but no cleared band round a graveyard is attested in any period - the
        # 30 px collar it had is gone, and the waste around it stays scrubby to its edge
        self._clear_ground(cx, cy, w, h, 0)
        if label:
            ly = cy - h / 2 - 8 if label_above else cy + h / 2 + 14
            # label_xy slides the caption ALONG the plot it names (it must still hug it) - a parish
            # graveyard often sits shoulder to shoulder with its temple, and the two captions can meet
            _lx, _ly = label_xy if label_xy else (cx, ly)
            self.label(_lx, _ly, label, 11, italic=True, color="#6B5A3C", ref=(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))

    def _ward_fence_cap(self: Settlement, a: Any, b: Any, tol: float = 16) -> int | None:  # type: ignore[misc]
        """If the axis-aligned wall segment a-b runs ALONG a neighborhood (ward) fence, re-stamp the
        fence stroke over it so the FENCE renders ON TOP - the compound's own wall runs underneath, and
        the fence IS that side of the compound (no doubled, clashing parallel walls). Mirrors how a
        ward's own ends run under the city rampart. Returns the cap's z if it stamped one, else None.

        Research: fence drawn over the compound wall - CONVENTION
        """
        ax, ay = a
        bx, by = b
        horiz = abs(ax - bx) >= abs(ay - by)
        for w in self.M.get("wards", []):
            bnd = w["boundary"]
            for i in range(len(bnd) - 1):
                px, py = bnd[i]
                qx, qy = bnd[i + 1]
                if (abs(px - qx) >= abs(py - qy)) != horiz:  # fence segment must run the same way
                    continue
                if horiz:
                    if abs(py - ay) > tol:
                        continue
                    lo, hi = max(min(ax, bx), min(px, qx)), min(max(ax, bx), max(px, qx))
                    if hi - lo < 10:
                        continue
                    dd = f'M{lo:.0f},{ay:.0f} L{hi:.0f},{ay:.0f}'
                else:
                    if abs(px - ax) > tol:
                        continue
                    lo, hi = max(min(ay, by), min(py, qy)), min(max(ay, by), max(py, qy))
                    if hi - lo < 10:
                        continue
                    dd = f'M{ax:.0f},{lo:.0f} L{ax:.0f},{hi:.0f}'
                self.add(f'<path d="{dd}" fill="none" stroke="#9C8A5E" stroke-width="5" opacity="0.9" stroke-linecap="round"/>')
                z = self.add(f'<path d="{dd}" fill="none" stroke="#4A3A22" stroke-width="1.3" stroke-dasharray="2,7" opacity="0.85"/>')  # palisade dash
                return z
        return None

    def mausoleum(self: Settlement, cx: float, cy: float, w: float, h: float, label: str = "Ancestral Mausoleum", gate_dir: str = "south", label_below: bool = False) -> None:  # type: ignore[misc]
        """A walled CRYPT PRECINCT - the ruling clan's ancestral mausoleum, where important samurai are
        interred in crypts and stone monuments after cremation. A prestige ground sited by the SAMURAI /
        government quarter (ancestor veneration is central to samurai identity), religiously staffed but a
        martial-clan monument distinct from the commoner temple graveyards. A walled court (like a manor)
        holding a stone crypt hall and a few tall memorial stupas. Records M['mausoleums']; blocks placement.

        Research:
            clan mausoleum by the samurai quarter - research/questions/0226-shrines-temples-and-graves-in-each-size-of-settlement.drawing.html: the caller's seat
            walled court with a crypt hall and stupas - research/questions/0238-cremation-grounds-and-bone-mounds-kasoba.html
            gate opening - UNRESEARCHED: 12 ft
            precinct wall - UNRESEARCHED: 2 ft, floored at 2 px
            crypt hall size - UNRESEARCHED: 0.42 x 0.34 of the court, at most 86 x 52 px
            keep-clear margin - UNRESEARCHED: 30 px at the grain
            caption - CONVENTION: the hall caption size
        """
        x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
        self.add(f'<rect x="{x0:.0f}" y="{y0:.0f}" width="{w}" height="{h}" fill="#E7DDC4"/>')  # the swept precinct court
        wall = '#3A352C'
        sides = {"north": ((x0, y0), (x1, y0), cx, y0), "south": ((x0, y1), (x1, y1), cx, y1), "west": ((x0, y0), (x0, y1), x0, cy), "east": ((x1, y0), (x1, y1), x1, cy)}
        mgg = max(self.px(12) / 2, 2.0)  # ceremonial gate: ~12 real ft opening (half-gap), floored
        mww = max(self.px(2), 2.0)  # precinct wall ~2 ft, 2px cartographic floor (GM 2026-07-19 to-scale rule)
        for name, (a, b, gx, gy) in sides.items():
            if name != gate_dir:
                self.add(f'<line x1="{a[0]:.0f}" y1="{a[1]:.0f}" x2="{b[0]:.0f}" y2="{b[1]:.0f}" stroke="{wall}" stroke-width="{mww:.1f}"/>')
            elif name in ("west", "east"):  # vertical wall - gap in y
                self.add(f'<line x1="{a[0]:.0f}" y1="{a[1]:.0f}" x2="{a[0]:.0f}" y2="{gy - mgg:.1f}" stroke="{wall}" stroke-width="{mww:.1f}"/>')
                self.add(f'<line x1="{b[0]:.0f}" y1="{gy + mgg:.1f}" x2="{b[0]:.0f}" y2="{b[1]:.0f}" stroke="{wall}" stroke-width="{mww:.1f}"/>')
            else:  # horizontal wall - gap in x
                self.add(f'<line x1="{a[0]:.0f}" y1="{a[1]:.0f}" x2="{gx - mgg:.1f}" y2="{a[1]:.0f}" stroke="{wall}" stroke-width="{mww:.1f}"/>')
                self.add(f'<line x1="{gx + mgg:.1f}" y1="{b[1]:.0f}" x2="{b[0]:.0f}" y2="{b[1]:.0f}" stroke="{wall}" stroke-width="{mww:.1f}"/>')
        # a wall that ABUTS a neighborhood (ward) fence yields to it: the fence is re-stamped over our
        # own wall there, so it renders ON TOP and IS that side of the precinct (recorded for the gate)
        ward_walls = [name for name, (a, b, gx, gy) in sides.items() if name != gate_dir and self._ward_fence_cap(a, b) is not None]
        hw, hh = min(w * 0.42, 86), min(h * 0.34, 52)  # the stone crypt hall, centered
        self.add(f'<rect x="{cx - hw / 2:.0f}" y="{cy - hh / 2:.0f}" width="{hw:.0f}" height="{hh:.0f}" rx="2" fill="#C9C0AE" stroke="#5A584F" stroke-width="2"/>')
        self.add(f'<rect x="{cx - hw / 2:.0f}" y="{cy - hh / 2:.0f}" width="{hw:.0f}" height="8" fill="#7A5A30"/>')  # the hall's roof band
        for sx in (x0 + 16, x1 - 16):  # tall memorial stupas flanking the hall
            self.add(f'<rect x="{sx - 3:.0f}" y="{cy - 9:.0f}" width="6" height="18" rx="2" fill="#B7B0A0" stroke="#5A584F" stroke-width="0.8"/>')
            self.add(f'<circle cx="{sx:.0f}" cy="{cy - 9:.0f}" r="3.4" fill="#B7B0A0" stroke="#5A584F" stroke-width="0.8"/>')
        self.M["mausoleums"].append({"x": cx, "y": cy, "w": w, "h": h, "rot": 0, "label": label, "gate_dir": gate_dir, "ward_walls": ward_walls, "gate_w": round(2 * mgg, 2), "wall_w": round(mww, 2)})
        self._assert_walls_clear_of_torii("the mausoleum wall")
        self.placed.append((cx, cy, w, h))
        m = 30 * self.bscale  # a building-half margin at the map's grain
        self.block_polys.append([(x0 - m, y0 - m), (x1 + m, y0 - m), (x1 + m, y1 + m), (x0 - m, y1 + m)])
        if label:
            ly = y1 + 14 if label_below else y0 - 12
            # HALL_CAPTION_FS, not a rank size: a clan crypt's glyph is a hall-class walled compound
            # (Minami's is 132x96 real ft against a temple hall's 130x84), so it takes the hall's
            # caption. At its old 12pt it came out the LOUDEST body text on a city sheet once the
            # temple halls dropped to 9 - above the governor's yamen at 11, whose compound is 525x300
            # ft - which is the size-by-rank ladder the whole change exists to remove.
            self.label(cx, ly, label, HALL_CAPTION_FS, weight="bold", italic=True, color="#3A352C", ref=(x0, y0, x1, y1))

    def cremation_ground(self: Settlement, cx: float, cy: float, label: str = "cremation ground", label_above: bool = False, jizo: bool = False) -> None:  # type: ignore[misc]
        """The CREMATORY (kasoba) - where the dead are burned before their bones are interred. Smoke, fire
        risk, and death-pollution put it OUTSIDE the walls; monks officiate with burakumin assistants (a
        religious order stands outside the caste system, so handling the dead does not pollute its caste).
        A cleared, scorched ground with its fire bed - a stone-framed trench on the leveled ground, open to the sky on most
        grounds and under a roof on four posts on a few (`roofed`). Records M['cremation_grounds']; blocks placement.

        THE FORMS BEFORE MODERN TIMES (feature 280 M70, research/questions/0238-cremation-grounds-and-bone-mounds-kasoba.html 'Cremation grounds and bone mounds (kasoba)'): the open pyre, the stone-framed
        trench beside a burial ground, and the four-post roofed bed and the snow-country hut dated to around mid-Edo - with
        most grounds open-air to the end of Edo. So the roof is the minority (`ROOFED_SHARE`, a GUESS), and no raised stone
        pyre platform or officiants' hut is drawn: neither is attested. A roof stands on four posts a few feet out from the
        bed, about 11 ft square. SIX JIZO (`jizo`) stand at a BURIAL ground's entrance (feature 280 M71, 700): a caller
        passes them only for a cremation ground beside a burial ground; one standing on its own has none.

        Research:
            cleared ground size - research/questions/0238-cremation-grounds-and-bone-mounds-kasoba.drawing.html: 75 ft at a village or town, 130 ft at a city
            fire bed - research/questions/0238-cremation-grounds-and-bone-mounds-kasoba.drawing.html: a stone-framed trench about 12 x 8 ft
            roofed bed the minority - research/questions/0238-cremation-grounds-and-bone-mounds-kasoba.drawing.html: ROOFED_SHARE off the seat
            roof size - research/questions/0238-cremation-grounds-and-bone-mounds-kasoba.drawing.html: about 11 ft square on four posts
            six jizo at a burial ground's entrance - research/questions/0238-cremation-grounds-and-bone-mounds-kasoba.drawing.html, research/questions/0235-village-burial-grounds-bochi.html
            jizo drawn size - CONVENTION: at least 2.4 x 3.2 px
            ragged outline, bed off center - CONVENTION
            keep-clear margin - UNRESEARCHED: 8 px
        """
        # TO SCALE (GM 2026-07-19; anchors in research/questions/0238-cremation-grounds-and-bone-mounds-kasoba.drawing.html): a sanmai's cleared working core is
        # 30-80 real ft for a village/town (a GUESS: the only sizes are 1922 and later - 202), ~80-160 ft for a provincial
        # city (Edo's Yoyogi crematory, 900 tsubo, ~180 ft square, the one premodern extent); the fire bed ~12x8 ft. The old
        # glyph was FIXED-PIXEL (116x80px) and silently tripled at city scale.
        across = 130.0 if self.M["meta"].get("scale") in CITY_TIER_SCALES else 75.0
        crx, cry = max(self.px(across) / 2, 14.0), max(self.px(across * 0.7) / 2, 10.0)
        # A WORN, RAGGED ground with its fire bed OFF CENTER (feature 272, settlement-review 2026-09-27 on
        # Hoshigaoka): a ruled ellipse with a centered dark ellipse and a centered dark block read as an eye or a
        # pit at fit zoom, and it was the only ruled ground on maps whose clearings are drawn ragged. The jitter
        # is seeded from the seat, so a map redraws the same ground every time.
        rnd = random.Random(f"cremation:{cx:.1f},{cy:.1f}")
        self.add(
            f'<polygon points="{cremation_outline(cx, cy, crx, cry, 22, 0.09, rnd)}" fill="#C9BCA0" stroke="#8C7A56" stroke-width="1.5" stroke-linejoin="round" opacity="0.85"/>'
        )  # cleared scorched ground
        fx = cx + crx * 0.08  # the fire bed a little east of center; the shelter keeps the east rim
        self.add(f'<polygon points="{cremation_outline(fx + crx * 0.05, cy + cry * 0.07, crx * 0.52, cry * 0.5, 14, 0.2, rnd)}" fill="#9A8A6A" opacity="0.5"/>')  # the burned ground
        abw, abh = max(self.px(12), 5.0), max(self.px(8), 3.6)  # the fire bed (~12x8 ft burn area), a trench in the leveled ground
        self.add(
            f'<rect x="{fx - abw / 2 - 0.8:.1f}" y="{cy - abh / 2 - 0.8:.1f}" width="{abw + 1.6:.1f}" height="{abh + 1.6:.1f}" rx="0.8" fill="none" stroke="#8C8470" stroke-width="1.2"/>'
        )  # its stone frame
        self.add(f'<polygon points="{cremation_outline(fx, cy, abw / 2, abh / 2, 9, 0.25, rnd)}" fill="#5A463A"/>')  # the ash bed, irregular
        roofed = self._hjit(cx, cy, 202.0) < ROOFED_SHARE
        if roofed:  # a roof on four posts a few feet out from the bed (~11 ft square), drawn as its outline and its posts
            rw = max(self.px(11), 6.0)
            self.add(f'<rect x="{fx - rw / 2:.1f}" y="{cy - rw / 2:.1f}" width="{rw:.1f}" height="{rw:.1f}" fill="#CDB890" fill-opacity="0.35" stroke="#5A4326" stroke-width="1.0"/>')
            self.add("".join(f'<circle cx="{fx + sx * (rw / 2 - 0.8):.1f}" cy="{cy + sy * (rw / 2 - 0.8):.1f}" r="0.9" fill="#5A4326"/>' for sx in (-1, 1) for sy in (-1, 1)))
        rec: dict[str, Any] = {"x": round(cx, 1), "y": round(cy, 1), "w": round(2 * crx, 1), "h": round(2 * cry, 1), "rot": 0, "roofed": roofed}
        if jizo:
            # SIX STONE JIZO in a row on the ground's upper rim - the entrance of the burial ground this cremation ground
            # stands beside (research 0235 'Village burial grounds (bochi)', feature 280 M71: dated at graveyards, 1678-1797; at a
            # cremation ground on its own only one undated modern page puts them). A stone jizo is about 2 ft; drawn at least 2.4 x 3.2 px - a map drawing convention, so
            # they can be seen (the hand-drawn Hoshigaoka ground's size, feature 272).
            jw, jh = max(self.px(2.0), 2.4), max(self.px(2.7), 3.2)
            pitch = jw * 1.4
            stones = [(round(cx - 2.5 * pitch + k * pitch, 1), round(cy - cry - jh, 1)) for k in range(6)]
            for jx, jy in stones:
                self.add(f'<rect x="{jx - jw / 2:.1f}" y="{jy - jh / 2:.1f}" width="{jw:.1f}" height="{jh:.1f}" rx="{jw * 0.45:.1f}" fill="#A8A294" stroke="#4A463C" stroke-width="0.5"/>')
            rec["jizo"] = [list(p) for p in stones]
        self.M["cremation_grounds"].append(rec)
        self.placed.append((cx, cy, 2 * crx, 2 * cry))
        m = 8
        self.block_polys.append([(cx - crx - m, cy - cry - m), (cx + crx + m, cy - cry - m), (cx + crx + m, cy + cry + m), (cx - crx - m, cy + cry + m)])
        if label:
            self.label(cx, cy - cry - 8 if label_above else cy + cry + 14, label, 11, italic=True, color="#6B5A3C", ref=(cx - crx, cy - cry, cx + crx, cy + cry))

    def ossuary(self: Settlement, cx: float, cy: float, label: str = "pauper ossuary mound") -> None:  # type: ignore[misc]
        """A PAUPER OSSUARY MOUND - a communal earthen mound where the bones of the poor and the
        'unconnected dead' (muenbotoke - those with no family or temple to inter them) are gathered, by
        the cremation ground outside the walls. A low rounded mound with a single weathered marker stupa.
        Records M['ossuaries']; blocks placement.

        Research:
            pauper mound - research/questions/0237-burial-grounds-of-towns-and-cities-and-paupers-grounds-yizhong.drawing.html, research/questions/0238-cremation-grounds-and-bone-mounds-kasoba.drawing.html: one mound by the cremation ground
            mound size - research/questions/0237-burial-grounds-of-towns-and-cities-and-paupers-grounds-yizhong.drawing.html: 22 ft, floored at 4.5 px
            marker stupa - UNRESEARCHED: one
            keep-clear margin - UNRESEARCHED: 8 px
        """
        # TO SCALE (GM 2026-07-19, tightened 2026-07-21): a muenzuka is a 10-30 real-ft mound
        # (cremated, consolidated bone takes almost no volume; Kyoto's monumental Mimizuka, a state
        # monument, is ~50 ft at the base). Drawn at ~22 ft, mid-band. History of this constant: the
        # original glyph was FIXED-PIXEL (92x60px = a 276 ft kofun at city scale); the first fix drew
        # ~40 ft with a 9px floor, which STILL rendered 54 real ft at city scale - the floor, not the
        # size, controlled. The floor is now 4.5px (27 ft at city, inside the band) - a stroke-
        # convention minimum for visibility, never a size license.
        orx = max(self.px(22) / 2, 4.5)
        ory = orx * 0.62
        self.add(f'<ellipse cx="{cx}" cy="{cy + ory * 0.2:.1f}" rx="{orx:.1f}" ry="{ory:.1f}" fill="#BCA878" stroke="#8C7A52" stroke-width="1.5"/>')  # the earthen mound
        self.add(f'<ellipse cx="{cx}" cy="{cy - ory * 0.1:.1f}" rx="{orx * 0.64:.1f}" ry="{ory * 0.55:.1f}" fill="#C8B584" opacity="0.7"/>')  # the crown (shading)
        self.add(f'<rect x="{cx - 2:.0f}" y="{cy - ory - 8:.1f}" width="4" height="9" rx="1.5" fill="#A8A294" stroke="#5A584F" stroke-width="0.8"/>')  # a weathered marker stupa
        self.add(f'<circle cx="{cx:.0f}" cy="{cy - ory - 8:.1f}" r="2.6" fill="#A8A294" stroke="#5A584F" stroke-width="0.8"/>')
        self.M["ossuaries"].append({"x": round(cx, 1), "y": round(cy, 1), "w": round(2 * orx, 1), "h": round(2 * ory, 1), "rot": 0})
        self.placed.append((cx, cy, 2 * orx, 2 * ory))
        m = 8
        self.block_polys.append([(cx - orx - m, cy - ory - m), (cx + orx + m, cy - ory - m), (cx + orx + m, cy + ory + m), (cx - orx - m, cy + ory + m)])
        if label:
            self.label(cx, cy + ory + 12, label, 11, italic=True, color="#6B5A3C", ref=(cx - orx, cy - ory, cx + orx, cy + ory))
