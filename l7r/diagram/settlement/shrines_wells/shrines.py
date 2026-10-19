"""The shrine GLYPH (the hall, the hill and the hall's caption went with feature 392).

Split from settlement/shrines_wells.py by feature 116 - see settlement/shrines_wells/CLAUDE.md for the index.

Research: plumbing - NONE
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import Settlement


class ShrineHallsMixin:
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
