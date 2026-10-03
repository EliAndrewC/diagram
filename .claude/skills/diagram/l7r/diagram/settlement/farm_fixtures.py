"""The small things on a farmstead: privy, wood shed, manure heap, bath room, chicken coop, the
household shrine, the persimmon (feature 133 T53-T59, GM 2026-08-27).

Sugiura 1973 counted 4.4 roofed outbuildings per Tōhoku farm household and the map drew one (the
kura) - the T52 pass listed the rest, and the GM chose these. Every one is drawn at TRUE size
(feedback: to-scale modes never inflate); the only legibility liberty is a bold stroke, and the
persimmon's fruit dots and the shrine's vermilion are RENDERING conventions, recorded as such in
research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.drawing.html. Research and sources:
research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.html and each fixture's own section. The PLACER is the scripted generator's (hamletgen/homesteads.py
`farmstead_fixtures`); this mixin only draws and records.

Research: fixture records and class names - NONE
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .core import Settlement

# Real feet (w along the house wall, h out from it). privy: the one-ken default here; the placer rolls each homestead's from
# the sixteen of the Kakimochi table (research/questions/0047-farm-privies-and-their-night-soil-benjo.html, feature 280) and passes it as `size_ft`. woodpile: the WOOD
# SHED, 4 x 2 ken, the common size in the Kakimochi count (research/questions/0043-firewood-stacks-and-sheds-kigoya.html and 720; the open stack under the eaves and
# the kizuma along the windbreak are modern-only and not drawn - feature 280). manure: a heap by the privy/stable (size
# GUESS). bath: a ROOM joined to the house, 6 ft out and 6-12 ft along it (research/homesteads/740, feature 280 M22 - the
# bath shed standing on its own is found only in the twentieth century); the placer passes its length. coop: a ground-level enclosure (Qimin Yaoshu 養雞), square in the
# Ming find (size GUESS). shrine: the one measured hokora is a 40 cm stone (READ); at 3 ft the GM could
# not tell what it was, so it is DRAWN at the small-shed size - vermilion, a torii mark in front - as a
# glyph rendering convention (GM 2026-08-27, T62; recorded as a map drawing convention in research/contents.json#homesteads).
# The interactive map's feature class per fixture kind (feature 134, spec FR-007) - the vocabulary
# is the `interactive/classes/` package; a kind missing here is a KeyError at draw time, never silent ink.
FIXTURE_CLASS = {"privy": "privy", "woodpile": "wood shed", "manure": "manure heap", "bath": "bath room", "coop": "hen coop", "shrine": "household shrine"}
# THE MANURE FIXTURE HAS TWO ATTESTED FORMS (feature 150, GM 2026-08-28 choosing audit A2): the HEAP by the
# privy or stable (Tohoku, Sugiura 1973) and the PIT - "pits made of earthenware, half buried in the ground at
# the back of the building" and lined along the road (Fei 1939, Lake Tai). Two forms -> a knob, rolled per
# hamlet (`MANURE_FORMS`); the record keeps `kind: manure` (one share, one seat table, every check unchanged)
# and carries `form: pit` when the pit is drawn. The pit is a ~3.5 ft jar mouth: a dark disc with a pale rim.
PIT_FT = 3.5
"""Research: manure pit - research/questions/0042-manure-heaps-and-compost-kyuhi.html: a jar mouth about 3.5 ft across"""
FIXTURE_CLASS_BY_FORM = {"pit": "manure pit"}

FIXTURE_FT: dict[str, tuple[float, float]] = {
    "privy": (6.0, 6.0),
    "woodpile": (24.0, 12.0),
    "manure": (8.0, 6.0),
    "bath": (6.0, 6.0),
    "coop": (5.0, 5.0),
    "shrine": (6.0, 6.0),  # DRAWN at the small-shed module, not the ~1.3 ft stone: a glyph convention (GM 2026-08-27, T62)
}
"""Each fixture's drawn size.

Research:
    privy size - research/questions/0047-farm-privies-and-their-night-soil-benjo.html: 6 x 6 ft, the one-ken default the placer overrides
    wood shed size - research/questions/0043-firewood-stacks-and-sheds-kigoya.html: 24 x 12 ft, 4 x 2 ken
    manure heap size - GUESS: 8 x 6 ft
    bath room size - research/questions/0044-baths-on-the-farm-furo.html: 6 x 6 ft, the placer passes its length
    hen coop size - GUESS: 5 x 5 ft
    household shrine size - CONVENTION: drawn at the 6 x 6 ft small-shed module, not the stone's 1.3 ft
"""
# radius: "a persimmon grows to about 12 m tall and 7 m across, a crown of about 23 ft" (research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.html, pfaf-kaki;
# 269 B14) - the full-grown size, which fits the "old giant persimmon in the dooryard" the record remembers. It was 9.0.
PERSIMMON_CROWN_FT = 11.5
"""Research: persimmon crown - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.html: 11.5 ft radius, a full-grown 23 ft crown"""

FIXTURE_KINDS = tuple(FIXTURE_FT)

#: THE STOREHOUSE ANNEX'S FOOTPRINT in its house's frame, as factors of the house's (w, h): (x, y, width, height). NORTH, a
#: wide block on the shaded back wall - 0.46 of the house's length by 0.45 of its depth, 1.67 to one, the Edo-period sheds'
#: proportion (feature 280 M18, research/questions/0052-farm-sheds-and-barns-naya.html), overlapping the back wall by 0.05 h so it reads as joined; WEST, a
#: tall block on the west wall (the dispersed farms). THE ONE TABLE the drawing (`Settlement.house`), the bundle's
#: reservation, the flush's side choice and the fixtures' wall list read: it was written out in four places, and feature
#: 280's new proportion reached two of them.
KURA_PARTS: dict[str, tuple[float, float, float, float]] = {"N": (0.0, -0.675, 0.46, 0.45), "W": (-0.64, 0.0, 0.32, 0.56)}
"""The annex footprints.

Research:
    north annex - research/questions/0052-farm-sheds-and-barns-naya.html: 0.46 of the house's length by 0.45 of its depth, on the back wall
    west annex - DEVIATION research/questions/0052-farm-sheds-and-barns-naya.html: 0.32 x 0.56 of the house (~15 x 16 ft on a 46 x 28 ft house), near square and attached to its west wall, for the dispersed farms, against a shed of 18 to 27 ft at 1.5 to 1.8 to one built apart
"""


#: THE NORTH ANNEX'S BAND (feature 280 M18, research/questions/0052-farm-sheds-and-barns-naya.html): the farm sheds dated to the end of the Edo period run
#: about 18 to 27 ft long and 1.5 to 1.8 times as long as deep (Hannan 3 x 2 ken; Nerima 8.17 x 4.54 m); the 1.8 to 2.4 of
#: the Meiji-Taisho barns is not drawn.
ANNEX_LENGTH_FT = (18.0, 27.0)
"""Research: annex length - research/questions/0052-farm-sheds-and-barns-naya.html: 18 to 27 ft"""
ANNEX_RATIO = (1.5, 1.8)
"""Research: annex proportion - research/questions/0052-farm-sheds-and-barns-naya.html: 1.5 to 1.8 times as long as deep"""


def kura_rect(w: float, h: float, side: str | None, ppf: float) -> tuple[float, float, float, float]:
    """The storehouse annex of a `w` x `h` house on `side` ("N", else the west), in the house's frame (`KURA_PARTS`), at
    `ppf` pixels per foot (`Settlement.px(1.0)`).

    THE NORTH ANNEX'S LENGTH IS HELD INSIDE ITS BAND (feature 293): 18 to 27 ft, and 1.5 to 1.8 times its depth. Once the
    annex went to the largest houses first, the shares alone drew it on the longest houses past 27 ft and at 1.9 to 2.3 to
    one, the barns' proportion (the settlement-reviews of the earlier 293 pass). An ordinary 46 x 28 ft minka is inside the
    band and unchanged, 21.2 x 12.6 ft; a 62 x 28 ft house draws 22.7 x 12.6 ft.

    THE DEPTH STAYS A SHARE, AND THE LENGTH GIVES (measured in that pass): held to the band by deepening instead - a long
    house's annex stopping at 27 ft and deepening to 1.8 to one, 27 x 15 ft - it moved every homestead that kept one, and
    the five pool hamlets re-packed with three finished-map checks failing. The length lies within the house's own width,
    so the bundle's reserved box moves only by the turn of its corner. Where the band cannot be met - a house under about
    22 ft deep - the 1.8 wins.

    THE SIZE IS A DELIBERATE DEVIATION: the record reads the annex as the kura (research/questions/0040-farm-storehouses-kura.html), and the kura read
    were about 15 by 18 ft, Kakimochi's two 12 by 18 - so the band's longer annexes are longer than a kura was. Kept: sizing
    it to the kura re-seats every scripted hamlet's houses, in a task that asked only which houses carry it; that resize is
    priced for the GM (specs/293-effort-level-experiment/outputs/I-port-handoff.md).

    Research:
        annex held in its band - research/questions/0052-farm-sheds-and-barns-naya.html: length 18 to 27 ft and 1.5 to 1.8 times its depth, the depth a share of the house
        annex larger than a kura - DEVIATION research/questions/0040-farm-storehouses-kura.html: the band's longer annexes exceed the 15 x 18 ft kura read
    """
    fx, fy, fw, fh = KURA_PARTS["N" if side == "N" else "W"]
    if side != "N":
        return (fx * w, fy * h, fw * w, fh * h)
    depth = fh * h
    lo, hi = max(ANNEX_LENGTH_FT[0] * ppf, ANNEX_RATIO[0] * depth), min(ANNEX_LENGTH_FT[1] * ppf, ANNEX_RATIO[1] * depth)
    return (fx * w, fy * h, min(max(fw * w, lo), hi), depth)


SHRINE_RED = "#A03020"  # the same vermilion as small_shrine's roof - the GM's "red marking" convention
"""Research: shrine vermilion - CONVENTION"""


class FarmFixturesMixin:
    def farm_fixture(self: Settlement, kind: str, cx: float, cy: float, rot: float = 0.0, of: Any = None, form: str | None = None, size_ft: tuple[float, float] | None = None) -> None:  # type: ignore[misc]
        """Draw and record one farmstead fixture of `kind` centered at (cx, cy), raked with its house. `form`
        picks an attested alternative glyph of the same kind (`manure` -> `pit`, feature 150). `size_ft` is the fixture's
        own size where the placer rolls one (the privy and the bath room, feature 280), else the kind's `FIXTURE_FT`.

        Research:
            the farmstead's fixtures - research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.html: privy, wood shed, manure, bath room, hen coop, household shrine
            manure heap or pit - research/questions/0042-manure-heaps-and-compost-kyuhi.html: the pit form drawn as a jar mouth
            fixture glyphs - CONVENTION: the privy's jar, the shed's log ends, the cauldron, the coop's slats, the shrine's torii
        """
        if kind not in FIXTURE_FT:
            raise ValueError(f"unknown farm fixture kind {kind!r}")
        if form is not None and (kind, form) != ("manure", "pit"):
            raise ValueError(f"no form {form!r} for fixture kind {kind!r}")
        _ft = (PIT_FT, PIT_FT) if form == "pit" else size_ft or FIXTURE_FT[kind]
        w, h = self.px(_ft[0]), self.px(_ft[1])
        x0, y0 = -w / 2, -h / 2
        edge = "#5A4326"
        g = [f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot:.2f})">']
        if kind == "privy":
            g.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" rx="1" fill="#8F7548" stroke="{edge}" stroke-width="1.1"/>')
            g.append(f'<line x1="{x0 + 1:.1f}" y1="0" x2="{-x0 - 1:.1f}" y2="0" stroke="#D8C08C" stroke-width="1"/>')
            # the night-soil jar at one end - hidden by the roof, so a MAP DRAWING CONVENTION naming what the building is: at the
            # rolled sizes (up to 24 x 12 ft, feature 280) a plain ridged roof read as the wood shed (settlement-review of Mizuguchi)
            g.append(f'<circle cx="{x0 + min(w, h) * 0.4:.1f}" cy="{h * 0.22:.1f}" r="{min(w, h) * 0.2:.1f}" fill="#3E2A12" stroke="#D8C08C" stroke-width="0.5"/>')
        elif kind == "woodpile":
            # the wood shed (feature 280 M21): a roof, and along its open front a band of log ends - which a roof would hide from above,
            # so the band is a MAP DRAWING CONVENTION naming what the shed holds, as the byre's stall mouth names its beast
            g.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" rx="1" fill="#9C7C4C" stroke="{edge}" stroke-width="1.1"/>')
            g.append(f'<line x1="{x0 + 1:.1f}" y1="{y0 + h * 0.3:.1f}" x2="{-x0 - 1:.1f}" y2="{y0 + h * 0.3:.1f}" stroke="#D8C08C" stroke-width="0.9"/>')  # the ridge
            n = max(3, int(w / 3.2))  # log ends large enough to read at the fit zoom (settlement-review of Mizuguchi, feature 280)
            for i in range(n):
                g.append(f'<circle cx="{x0 + (i + 0.5) * w / n:.1f}" cy="{-y0 - min(h, 4.0) * 0.4:.1f}" r="{min(h, 4.0) * 0.3:.1f}" fill="#E6CC96" stroke="#5A4326" stroke-width="0.4"/>')

        elif kind == "manure" and form == "pit":
            g.append(f'<circle cx="0" cy="0" r="{w / 2:.1f}" fill="#C9B384" stroke="#7A5A30" stroke-width="0.9"/>')  # the jar's rim, flush with the ground
            g.append(f'<circle cx="0" cy="0" r="{w / 2 - 1.1:.1f}" fill="#4A3418"/>')  # the dark mouth
        elif kind == "manure":
            # a plain mound with straw hatching - the dashed outline read as a crown's scallop, i.e. a bush (review at T99)
            g.append(f'<ellipse cx="0" cy="0" rx="{w / 2:.1f}" ry="{h / 2:.1f}" fill="#6B4F2A" stroke="#4A3418" stroke-width="0.7"/>')
            for k in (-0.5, -0.17, 0.17, 0.5):
                g.append(f'<line x1="{k * w * 0.8 - 0.9:.1f}" y1="{h * 0.22:.1f}" x2="{k * w * 0.8 + 0.9:.1f}" y2="{-h * 0.22:.1f}" stroke="#C9A874" stroke-width="0.6"/>')
        elif kind == "bath":
            g.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" rx="1" fill="#A98C58" stroke="{edge}" stroke-width="1.1"/>')
            g.append(f'<circle cx="0" cy="0" r="{min(w, h) * 0.24:.1f}" fill="#3E3E3E"/>')  # the iron cauldron
        elif kind == "coop":
            g.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#B9A070" stroke="{edge}" stroke-width="0.8"/>')
            for k in (-0.25, 0.0, 0.25):  # the slats/niches of the enclosure
                g.append(f'<line x1="{k * w:.1f}" y1="{y0 + 0.8:.1f}" x2="{k * w:.1f}" y2="{-y0 - 0.8:.1f}" stroke="{edge}" stroke-width="0.6"/>')
        else:  # shrine - the household hokora, in the religious red so a rare thing is seen (T58/T62)
            g.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" rx="0.8" fill="{SHRINE_RED}" stroke="#5A1A10" stroke-width="1.2"/>')
            g.append(f'<line x1="{x0 + 1:.1f}" y1="{y0 + h * 0.35:.1f}" x2="{-x0 - 1:.1f}" y2="{y0 + h * 0.35:.1f}" stroke="#F2C9B0" stroke-width="1"/>')  # the ridge
            ty = -y0 + 2.6  # a little torii standing before the door: two posts, a lintel wider than the hall, and the tie beam
            g.append(f'<line x1="{x0 - 1.5:.1f}" y1="{ty:.1f}" x2="{-x0 + 1.5:.1f}" y2="{ty:.1f}" stroke="{SHRINE_RED}" stroke-width="1.6"/>')
            # ...THE SECOND CROSSBAR (the nuki), below the lintel and just past the posts: with one bar the torii read as a small
            # bench on its own (glyph-check, feature 294); two bars are the torii, and the shrine mark (GM 2026-10-01). A clear
            # 0.6 ft of ground between the bars, and the posts run on below: at ty + 1.0 the two strokes overlapped into one slab
            # on stub feet, more a bench than before (glyph-check, the redraw's first round)
            g.append(f'<line x1="{x0 - 0.2:.1f}" y1="{ty + 1.8:.1f}" x2="{-x0 + 0.2:.1f}" y2="{ty + 1.8:.1f}" stroke="{SHRINE_RED}" stroke-width="0.8"/>')
            g.append(f'<line x1="{x0 + 0.6:.1f}" y1="{ty - 0.4:.1f}" x2="{x0 + 0.6:.1f}" y2="{ty + 3.2:.1f}" stroke="{SHRINE_RED}" stroke-width="1.1"/>')
            g.append(f'<line x1="{-x0 - 0.6:.1f}" y1="{ty - 0.4:.1f}" x2="{-x0 - 0.6:.1f}" y2="{ty + 3.2:.1f}" stroke="{SHRINE_RED}" stroke-width="1.1"/>')
        g.append("</g>")
        self.add_top("".join(g), cls=FIXTURE_CLASS_BY_FORM.get(form or "", FIXTURE_CLASS[kind]))  # feature 134: each kind (and form) is its own highlight class
        rec: dict[str, Any] = {"kind": kind, "x": round(cx, 1), "y": round(cy, 1), "w": round(w, 1), "h": round(h, 1), "rot": round(rot, 1)}
        if form is not None:
            rec["form"] = form
        if of is not None:
            rec["of"] = [round(float(of[0]), 1), round(float(of[1]), 1)]
        self.M.setdefault("farm_fixtures", []).append(rec)

    def persimmon(self: Settlement, cx: float, cy: float, of: Any = None) -> None:  # type: ignore[misc]
        """A yard persimmon: one crown, drawn a yellower green than the groves with four fruit dots -
        the fruit is the map's convention for "this one tree is the persimmon", not a season.

        Research:
            persimmon crown - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.html: one crown of PERSIMMON_CROWN_FT
            fruit dots - CONVENTION: four jittered orange dots
        """
        r = self.px(PERSIMMON_CROWN_FT)
        g = [f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="#94A23A" stroke="#5A6A26" stroke-width="0.8"/>']
        # THE FRUIT IS NOT A STENCIL (feature 152 T11, settlement-review 2026-08-29). The four dots sat at
        # exactly (+/-0.55r, +/-0.55r) at 45/135/225/315 degrees, identical on every tree on every map: a
        # rigid mirrored 2x2 of saturated marks, which is this project's own named strongest face-read
        # trigger, and the anti-twin problem in miniature - two hamlets' persimmons were pixel-identical.
        # Fruit does not hang in a square. Angle and radius are jittered off the tree's own position, so
        # the pattern is stable for a given tree and different between trees; the count stays four, which
        # is the convention that says "this one is the persimmon".
        _j = self._hjit(cx, cy, 107.0)
        for k in range(4):
            a = math.radians(45 + 90 * k + 34.0 * (self._hjit(cx + k * 13.0, cy - k * 7.0, 107.5) - 0.5))
            _rad = r * (0.44 + 0.24 * self._hjit(cx - k * 11.0, cy + k * 5.0, 107.9)) * (0.92 + 0.16 * _j)
            g.append(f'<circle cx="{cx + _rad * math.cos(a):.1f}" cy="{cy + _rad * math.sin(a):.1f}" r="{max(1.0, r * 0.14):.1f}" fill="#E07B22"/>')
        self.add_top("".join(g), cls="persimmon")
        self._record_crowns([(cx, cy, r)])
        rec: dict[str, Any] = {"x": round(cx, 1), "y": round(cy, 1), "r": round(r, 1)}
        if of is not None:
            rec["of"] = [round(float(of[0]), 1), round(float(of[1]), 1)]
        self.M.setdefault("persimmons", []).append(rec)


# ---- the stock a dike-pond hamlet keeps on its ponds (feature 150 A3/A4) ---------------------------

STY_FT = (8.0, 6.0)  # a simple pig shed on the dike, over the water's edge (FAO/NACA: "the simple pig shed constructed on the pond dyke")
"""Research: sty size - UNRESEARCHED: 8 x 6 ft (0025 gives no size for a sty)"""
# NO DUCK PEN (269 B32, the GM 2026-09-28): the fenced dry and wet run is a modern fish-cum-duck form, read only
# in the FAO/NACA manual, and a form attested only in modern sources is not drawn; premodern delta ducks were
# herded in the rice fields, not penned at the fish ponds (research/questions/0025-pigs-and-ducks-at-a-dike-pond-the-sty-on-the-pond-dike.html).
# NO PER-POND SLUICE (feature 280 M57, research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.html): a sluice through EACH pond's dike is defined only by the
# FAO training manual, so it is not drawn - and the sty's keep-clear of it (feature 233) went with it. The polder's own
# gates (the dou) stay.


class PondStockMixin:
    def pond_fixture_fits(self: Settlement, cx: float, cy: float, rot: float) -> bool:  # type: ignore[misc]
        """Room for a sty at this bank seat: clear of every placed footprint, every recorded sty, and the
        plank crossings; the bank itself is field ground, which the registries hold no structure off -
        that is what the seat is FOR.

        Research:
            sty on the bank - research/questions/0025-pigs-and-ducks-at-a-dike-pond-the-sty-on-the-pond-dike.html: the dike is field ground the sty may stand on
            sty clearance - UNRESEARCHED: its half-diagonal plus 2 ft from every placed structure and crossing
        """
        w, h = self.px(STY_FT[0]), self.px(STY_FT[1])
        half = math.hypot(w, h) / 2 + self.px(2.0)
        for key in ("pig_sties", "houses", "farm_sheds", "byres", "retirement_houses", "wells", "kosatsuba", "footbridges"):
            for o in self.M.get(key, []):
                if "x" in o and math.hypot(float(o["x"]) - cx, float(o["y"]) - cy) < half + math.hypot(float(o.get("w", 6)), float(o.get("h", 6))) / 2:
                    return False
        # ...and the registry of what stands admits the sty as `pig_sty` will record it (feature 287, water W53)
        return self.admits("pig_sties", {"x": round(cx, 1), "y": round(cy, 1), "w": round(w, 1), "h": round(h, 1), "rot": round(rot, 1)})

    def pig_sty(self: Settlement, cx: float, cy: float, rot: float = 0.0, pond: int | None = None) -> None:  # type: ignore[misc]
        """A pig shed on a pond dike: a small pitched shed with its pen rail, raked along the bank.

        Research:
            sty on the dike - research/questions/0025-pigs-and-ducks-at-a-dike-pond-the-sty-on-the-pond-dike.html: raked along the bank
            sty glyph - CONVENTION: a ridged shed on 0.62 of the length and a railed pen
        """
        w, h = self.px(STY_FT[0]), self.px(STY_FT[1])
        x0, y0 = -w / 2, -h / 2
        edge = "#5A4326"
        g = [
            f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot:.2f})">',
            f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w * 0.62:.1f}" height="{h:.1f}" rx="1" fill="#8F7548" stroke="{edge}" stroke-width="1.1"/>',  # the shed
            f'<line x1="{x0 + 1:.1f}" y1="0" x2="{x0 + w * 0.62 - 1:.1f}" y2="0" stroke="#D8C08C" stroke-width="1"/>',  # its ridge
            f'<rect x="{x0 + w * 0.62:.1f}" y="{y0:.1f}" width="{w * 0.38:.1f}" height="{h:.1f}" fill="none" stroke="{edge}" stroke-width="0.8" stroke-dasharray="1.2,1.2"/>',  # the railed pen
            "</g>",
        ]
        self.add_top("".join(g), cls="pig sty")
        rec: dict[str, Any] = {"x": round(cx, 1), "y": round(cy, 1), "w": round(w, 1), "h": round(h, 1), "rot": round(rot, 1)}
        if pond is not None:
            rec["pond"] = pond
        self.M.setdefault("pig_sties", []).append(rec)
