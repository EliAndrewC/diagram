"""The small things on a farmstead: privy, woodpile, manure heap, bath shed, chicken coop, the
household shrine, the persimmon (feature 133 T53-T59, GM 2026-08-27).

Sugiura 1973 counted 4.4 roofed outbuildings per Tōhoku farm household and the map drew one (the
kura) - the T52 pass listed the rest, and the GM chose these. Every one is drawn at TRUE size
(feedback: to-scale modes never inflate); the only legibility liberty is a bold stroke, and the
persimmon's fruit dots and the shrine's vermilion are RENDERING conventions, recorded as such in
settlements/homesteads.md "Farmstead fixtures". Research and sources: research/homesteads.md
"The farmstead's fixtures". The PLACER is the scripted generator's (hamletgen/homesteads.py
`farmstead_fixtures`); this mixin only draws and records.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from ._geom import Pt

if TYPE_CHECKING:
    from .core import Settlement

# Real feet (w along the house wall, h out from it). privy: one ken square is the traditional
# module (research: "一坪" outhouses; the size is a GUESS within that module). woodpile: split logs
# ~35 cm long stacked ~1.5 m high, a row a few meters long (modern stacking practice; the object is
# unchanged). manure: a heap by the privy/stable (size GUESS). bath: a goemon-buro shed, one ken
# (GUESS within the ken module). coop: a ground-level enclosure (Qimin Yaoshu 養雞), square in the
# Ming find (size GUESS). shrine: the one measured hokora is a 40 cm stone (READ); at 3 ft the GM could
# not tell what it was, so it is DRAWN at the small-shed size - vermilion, a torii mark in front - as a
# glyph rendering convention (GM 2026-08-27, T62; recorded as a deviation in settlements/homesteads.md).
# The interactive map's feature class per fixture kind (feature 134, spec FR-007) - the vocabulary
# is `interactive/classes.py`; a kind missing here is a KeyError at draw time, never silent ink.
FIXTURE_CLASS = {"privy": "privy", "woodpile": "woodpile", "manure": "manure heap", "bath": "bathhouse", "coop": "hen coop", "shrine": "household shrine"}
# THE MANURE FIXTURE HAS TWO ATTESTED FORMS (feature 139, GM 2026-08-28 choosing audit A2): the HEAP by the
# privy or stable (Tohoku, Sugiura 1973) and the PIT - "pits made of earthenware, half buried in the ground at
# the back of the building" and lined along the road (Fei 1939, Lake Tai). Two forms -> a knob, rolled per
# hamlet (`MANURE_FORMS`); the record keeps `kind: manure` (one share, one seat table, every check unchanged)
# and carries `form: pit` when the pit is drawn. The pit is a ~3.5 ft jar mouth: a dark disc with a pale rim.
PIT_FT = 3.5
FIXTURE_CLASS_BY_FORM = {"pit": "manure pit"}

FIXTURE_FT: dict[str, tuple[float, float]] = {
    "privy": (6.0, 6.0),
    "woodpile": (10.0, 3.5),
    "manure": (8.0, 6.0),
    "bath": (6.0, 6.0),
    "coop": (5.0, 5.0),
    "shrine": (6.0, 6.0),  # DRAWN at the small-shed module, not the ~1.3 ft stone: a glyph convention (GM 2026-08-27, T62)
}
PERSIMMON_CROWN_FT = 9.0  # radius: a yard persimmon's crown runs ~5-6 m across (uekipedia: tree 5-10 m tall)
FIXTURE_KINDS = tuple(FIXTURE_FT)
SHRINE_RED = "#A03020"  # the same vermilion as small_shrine's roof - the GM's "red marking" convention


class FarmFixturesMixin:
    def farm_fixture(self: Settlement, kind: str, cx: float, cy: float, rot: float = 0.0, of: Any = None, form: str | None = None) -> None:  # type: ignore[misc]
        """Draw and record one farmstead fixture of `kind` centered at (cx, cy), raked with its house. `form`
        picks an attested alternative glyph of the same kind (`manure` -> `pit`, feature 139)."""
        if kind not in FIXTURE_FT:
            raise ValueError(f"unknown farm fixture kind {kind!r}")
        if form is not None and (kind, form) != ("manure", "pit"):
            raise ValueError(f"no form {form!r} for fixture kind {kind!r}")
        w, h = (self.px(PIT_FT), self.px(PIT_FT)) if form == "pit" else (self.px(FIXTURE_FT[kind][0]), self.px(FIXTURE_FT[kind][1]))
        x0, y0 = -w / 2, -h / 2
        edge = "#5A4326"
        g = [f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot:.2f})">']
        if kind == "privy":
            g.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" rx="1" fill="#8F7548" stroke="{edge}" stroke-width="1.1"/>')
            g.append(f'<line x1="{x0 + 1:.1f}" y1="0" x2="{-x0 - 1:.1f}" y2="0" stroke="#D8C08C" stroke-width="1"/>')
        elif kind == "woodpile":
            g.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#8B6A3E" stroke="{edge}" stroke-width="0.8"/>')
            n = max(3, int(w / 2.6))
            for i in range(n):  # the end grain of the split logs, the thing that makes a stack read as a stack
                g.append(f'<circle cx="{x0 + (i + 0.5) * w / n:.1f}" cy="0" r="{min(h, 2.6) * 0.34:.1f}" fill="#C9A874"/>')
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
            ty = -y0 + 2.6  # a little torii standing before the door: two posts and a lintel wider than the hall
            g.append(f'<line x1="{x0 - 1.5:.1f}" y1="{ty:.1f}" x2="{-x0 + 1.5:.1f}" y2="{ty:.1f}" stroke="{SHRINE_RED}" stroke-width="1.6"/>')
            g.append(f'<line x1="{x0 + 0.6:.1f}" y1="{ty - 0.4:.1f}" x2="{x0 + 0.6:.1f}" y2="{ty + 2.2:.1f}" stroke="{SHRINE_RED}" stroke-width="1.1"/>')
            g.append(f'<line x1="{-x0 - 0.6:.1f}" y1="{ty - 0.4:.1f}" x2="{-x0 - 0.6:.1f}" y2="{ty + 2.2:.1f}" stroke="{SHRINE_RED}" stroke-width="1.1"/>')
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
        the fruit is the map's convention for "this one tree is the persimmon", not a season."""
        r = self.px(PERSIMMON_CROWN_FT)
        g = [f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="#7C9A3E" stroke="#4E6A28" stroke-width="0.8"/>']
        for k in range(4):
            a = math.radians(45 + 90 * k)
            g.append(f'<circle cx="{cx + 0.55 * r * math.cos(a):.1f}" cy="{cy + 0.55 * r * math.sin(a):.1f}" r="{max(1.0, r * 0.14):.1f}" fill="#E07B22"/>')
        self.add_top("".join(g), cls="persimmon")
        self._record_crowns([(cx, cy, r)])
        rec: dict[str, Any] = {"x": round(cx, 1), "y": round(cy, 1), "r": round(r, 1)}
        if of is not None:
            rec["of"] = [round(float(of[0]), 1), round(float(of[1]), 1)]
        self.M.setdefault("persimmons", []).append(rec)


# ---- the stock a dike-pond hamlet keeps on its ponds (feature 139 A3/A4) ---------------------------

STY_FT = (8.0, 6.0)  # a simple pig shed on the dike, over the water's edge (FAO/NACA: "the simple pig shed constructed on the pond dyke")
PEN_FT = (10.0, 6.0)  # the fenced DRY RUN of a duck pen on the dike; its WET RUN is a fenced corner of the pond
PEN_WET_FT = 12.0  # how far the wet-run fence reaches into the water from the bank


class PondStockMixin:
    def pond_fixture_fits(self: Settlement, cx: float, cy: float, rot: float, kind: str) -> bool:  # type: ignore[misc]
        """Room for a sty or a pen at this bank seat: clear of every placed footprint, every recorded
        pond-stock fixture, and the plank crossings; the bank itself is field ground, which the
        registries hold no structure off - that is what the seat is FOR."""
        w, h = STY_FT if kind == "sty" else PEN_FT
        w, h = self.px(w), self.px(h)
        half = math.hypot(w, h) / 2 + self.px(2.0)
        for key in ("pig_sties", "duck_pens", "houses", "farm_sheds", "byres", "wells", "kosatsuba", "footbridges"):
            for o in self.M.get(key, []):
                if "x" in o and math.hypot(float(o["x"]) - cx, float(o["y"]) - cy) < half + math.hypot(float(o.get("w", 6)), float(o.get("h", 6))) / 2:
                    return False
        return True

    def pig_sty(self: Settlement, cx: float, cy: float, rot: float = 0.0, pond: int | None = None) -> None:  # type: ignore[misc]
        """A pig shed on a pond dike: a small pitched shed with its pen rail, raked along the bank."""
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

    def duck_pen(self: Settlement, cx: float, cy: float, rot: float = 0.0, pond: int | None = None, water: Sequence[Pt] = ()) -> None:  # type: ignore[misc]
        """A duck pen: a fenced dry run on the dike and a fenced wet run in the nearest corner of the pond
        (FAO/NACA fish-cum-duck: "the dikes ... are partly fenced to form a dry run and part of the water
        area or a corner of the pond is fenced ... to form a wet run")."""
        w, h = self.px(PEN_FT[0]), self.px(PEN_FT[1])
        x0, y0 = -w / 2, -h / 2
        fence = "#6B5A3C"
        g = [
            f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot:.2f})">',
            f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#D9CBA0" fill-opacity="0.55" stroke="{fence}" stroke-width="0.9" stroke-dasharray="1.6,1.2"/>',  # the dry run
            f'<rect x="{x0 + 1:.1f}" y="{y0 + 1:.1f}" width="{w * 0.3:.1f}" height="{h - 2:.1f}" fill="#A98C58" stroke="{fence}" stroke-width="0.7"/>',  # the duck house
            "</g>",
        ]
        # the WET RUN: a fence arc from the bank into the water toward the pond's nearest water point
        wet: list[list[float]] = []
        if water:
            wx, wy = min(water, key=lambda q: math.dist(q, (cx, cy)))
            vx, vy = wx - cx, wy - cy
            vl = math.hypot(vx, vy) or 1.0
            ux, uy = vx / vl, vy / vl
            reach = self.px(PEN_WET_FT)
            px_, py_ = -uy, ux
            arc = [(cx + ux * (vl - 1) + px_ * w / 2, cy + uy * (vl - 1) + py_ * w / 2)]
            for k in range(1, 6):
                t = k / 5
                ang = math.pi * t
                arc.append((cx + ux * (vl - 1 + reach * math.sin(ang) * 0.9) + px_ * (w / 2) * math.cos(ang), cy + uy * (vl - 1 + reach * math.sin(ang) * 0.9) + py_ * (w / 2) * math.cos(ang)))
            pts = " ".join(f"{a:.1f},{b:.1f}" for a, b in arc)
            g.append(f'<polyline points="{pts}" fill="none" stroke="{fence}" stroke-width="0.9" stroke-dasharray="1.6,1.2"/>')
            wet = [[round(a, 1), round(b, 1)] for a, b in arc]
        self.add_top("".join(g), cls="duck pen")
        rec: dict[str, Any] = {"x": round(cx, 1), "y": round(cy, 1), "w": round(w, 1), "h": round(h, 1), "rot": round(rot, 1), "wet": wet}
        if pond is not None:
            rec["pond"] = pond
        self.M.setdefault("duck_pens", []).append(rec)
