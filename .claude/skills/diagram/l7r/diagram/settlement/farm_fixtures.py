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
from typing import TYPE_CHECKING, Any

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
    def farm_fixture(self: Settlement, kind: str, cx: float, cy: float, rot: float = 0.0, of: Any = None) -> None:  # type: ignore[misc]
        """Draw and record one farmstead fixture of `kind` centered at (cx, cy), raked with its house."""
        if kind not in FIXTURE_FT:
            raise ValueError(f"unknown farm fixture kind {kind!r}")
        w, h = self.px(FIXTURE_FT[kind][0]), self.px(FIXTURE_FT[kind][1])
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
        self.add_top("".join(g))
        rec: dict[str, Any] = {"kind": kind, "x": round(cx, 1), "y": round(cy, 1), "w": round(w, 1), "h": round(h, 1), "rot": round(rot, 1)}
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
        self.add_top("".join(g))
        self._record_crowns([(cx, cy, r)])
        rec: dict[str, Any] = {"x": round(cx, 1), "y": round(cy, 1), "r": round(r, 1)}
        if of is not None:
            rec["of"] = [round(float(of[0]), 1), round(float(of[1]), 1)]
        self.M.setdefault("persimmons", []).append(rec)
