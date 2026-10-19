"""The religious hall and shrine GLYPHS, the hill one may stand on, and the hall's caption.

Split from settlement/shrines_wells.py by feature 116 - see settlement/shrines_wells/CLAUDE.md for the index.

Research: plumbing - NONE
"""

import math
import random
from typing import TYPE_CHECKING

from .._geom import (
    Pt,
)

if TYPE_CHECKING:
    from ..core import Settlement


class ShrineHallsMixin:
    def hill(self: Settlement, cx: float, cy: float, rx: float, ry: float, steep: bool = False) -> Pt:  # type: ignore[misc]
        """A hill drawn as stepped rings with hachures and a few trees; returns the summit seat.

        Research:
            stepped rings and hachures - CONVENTION
            trees on the hill - research/questions/0080-how-thickly-trees-stood-in-a-wood-and-how-wide-their-crowns.drawing.html: every crown at real size and spacing, about 600 a hectare, 17 ft crowns; 15 seeded crowns of 4 to 6 px
            tree glyph - CONVENTION
            summit seat for the shrine - UNRESEARCHED: 40 px above the center
        """
        rings = [(cx, cy + 28, rx, ry), (cx, cy, rx * 0.76, ry * 0.76), (cx, cy - 26, rx * 0.52, ry * 0.52), (cx, cy - 44, rx * 0.30, ry * 0.32)]
        self.M["hill"] = [rings[0][0], rings[0][1], rings[0][2], rings[0][3]]
        self.M["summit"] = [rings[3][0], rings[3][1], rings[3][2], rings[3][3]]
        self.ellipses.append((rings[0][0], rings[0][1], rings[0][2], rings[0][3]))
        for (ax, ay, arx, ary), shade in zip(rings, ['#DFD0A2', '#D8C795', '#D0BD87', '#C8B37B'], strict=False):
            self.add(f'<ellipse cx="{ax:.0f}" cy="{ay:.0f}" rx="{arx:.0f}" ry="{ary:.0f}" fill="{shade}" stroke="#A8995F" stroke-width="1"/>')
        ocx, ocy, orx, ory = rings[0]
        for k in range(30):
            a = 2 * math.pi * k / 30
            ex, ey = ocx + math.cos(a) * orx, ocy + math.sin(a) * ory
            self.add(f'<line x1="{ex:.0f}" y1="{ey:.0f}" x2="{ex + math.cos(a) * 9:.0f}" y2="{ey + math.sin(a) * 9:.0f}" stroke="#A8995F" stroke-width="0.9"/>')
        if steep:
            # emphasized downslope hachures over the steep north back and upper flanks:
            # closely-spaced, longer ticks read as a steep, undefendable-on-foot slope
            n = 52
            for k in range(n + 1):
                ang = math.radians(195 + (345 - 195) * k / n)
                ex, ey = ocx + math.cos(ang) * orx, ocy + math.sin(ang) * ory
                ln = 19 + 5 * math.sin(math.radians(195 + (345 - 195) * k / n) - math.pi / 2)
                self.add(f'<line x1="{ex:.1f}" y1="{ey:.1f}" x2="{ex + math.cos(ang) * ln:.1f}" y2="{ey + math.sin(ang) * ln:.1f}" stroke="#8F7E48" stroke-width="1.0"/>')
        st = random.getstate()
        random.seed(4)
        for _ in range(15):
            a = random.uniform(0, 2 * math.pi)
            rr = random.uniform(0.4, 0.9)
            tx = cx + math.cos(a) * rx * rr
            ty = (cy + 12) + math.sin(a) * ry * rr
            self.add(f'<circle cx="{tx:.0f}" cy="{ty:.0f}" r="{random.uniform(4, 6):.1f}" fill="#7E9B5C" stroke="#52663C" stroke-width="0.8"/>')
            self.add(f'<circle cx="{tx - 1:.0f}" cy="{ty - 1:.0f}" r="1.6" fill="#9DB87A"/>')
        random.setstate(st)
        return (cx, cy - 40)  # summit point for the shrine

    def shrine(self: Settlement, x: float, y: float, w_ft: float = 62, h_ft: float = 42, kind: str = "shrine") -> None:  # type: ignore[misc]
        """The legacy simple shrine glyph (the civic_shrine roll path + secondary_shrine). TRUE SCALE
        (GM 2026-07-21): dimensions are REAL FEET, converted through px() - an ordinary village
        tutelary hall ~62x42 ft (~240 m2, inside the 600 m2 village ceiling). The old signature took
        fixed PIXELS (104x68 default), a latent footgun that would have drawn a 208x136 ft
        monastery-sized hall on any village that used the default civic_shrine path.

        Research:
            hall size - research/questions/0215-village-shrines-where-they-stand-and-how-big-their-grounds-are.drawing.html: 62 x 42 ft default
            vermilion hall glyph - CONVENTION
        """
        w, h = self.px(w_ft), self.px(h_ft)
        self.add(f'<rect x="{x - w / 2:.0f}" y="{y - h / 2:.0f}" width="{w}" height="{h}" rx="3" fill="#C9876C" stroke="#6B2A18" stroke-width="2"/>')
        self.add(f'<rect x="{x - w / 2:.0f}" y="{y - h / 2:.0f}" width="{w}" height="8" fill="#A03020"/>')
        self.add(f'<rect x="{x - w / 2:.0f}" y="{y + h / 2 - 8:.0f}" width="{w}" height="8" fill="#A03020"/>')
        self.add(f'<line x1="{x - w / 2:.0f}" y1="{y:.0f}" x2="{x + w / 2:.0f}" y2="{y:.0f}" stroke="#6B2A18" stroke-width="0.7"/>')
        self.M["shrine"] = [x - w / 2, y - h / 2, w, h]
        self.M["religious"].append({"kind": kind, "x": x, "y": y, "w": w, "h": h})
