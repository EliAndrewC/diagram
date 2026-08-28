"""Town-tier ways and focal features - the market, the ancestral hall, the water mouth, alleys (feature 145: moved out of water_ways.py, which the hamlet path executes, so the module-level coverage floor judges only what a hamlet draws)."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import Settlement

import math
from typing import TYPE_CHECKING, Any


class TownWaysMixin:
    def ancestral_hall(self: Settlement, x: float, y: float, w: float = 110, h: float = 74) -> None:  # type: ignore[misc]
        """A lineage ANCESTRAL HALL (祠堂), a focal feature: the grandest civic building of a single-lineage
        village - broader than any house, a double-eave hall on the auspicious axis fronting the pond/water.
        Draws the hall, records M['ancestral_halls'] + the focal feature, reserves the footprint. Grounding
        (research.md D2): the ancestral hall was the ritual + governance center of a Huizhou/Hakka lineage
        village, its single most prominent structure - so a village that HAS one reads unmistakably by it."""
        pw, ph = self.px(w), self.px(h)
        self.add(f'<rect x="{x - pw / 2:.1f}" y="{y - ph / 2:.1f}" width="{pw:.1f}" height="{ph:.1f}" fill="#DDB87A" stroke="#5A3F1E" stroke-width="2.4" rx="2"/>')
        self.add(
            f'<rect x="{x - pw / 2 + self.px(5):.1f}" y="{y - ph / 2 + self.px(5):.1f}" width="{pw - self.px(10):.1f}" height="{ph - self.px(10):.1f}" fill="none" stroke="#6B4F2A" stroke-width="1.2"/>'
        )  # inner eave
        self.add(f'<rect x="{x - self.px(9):.1f}" y="{y + ph / 2 - self.px(4):.1f}" width="{self.px(18):.1f}" height="{self.px(6):.1f}" fill="#5A3F1E"/>')  # entry porch on the water side
        self.M.setdefault("ancestral_halls", []).append({"x": round(x, 1), "y": round(y, 1), "w": pw, "h": ph, "rot": 0})
        self.note_focal("ancestral_hall")
        self._focal_block(x, y, pw, ph)

    def water_mouth(self: Settlement, x: float, y: float, r: float = 22) -> None:  # type: ignore[misc]
        """A fengshui WATER-MOUTH complex (水口), a focal feature: the guarded outlet where the village stream
        leaves, marked by a small hexagonal pavilion (and, per the gen, a screening grove) to 'lock in' the qi
        of the departing water. Draws the pavilion, records M['water_mouths'] + the focal feature. Grounding:
        the shuikou was a standard focal ensemble of south-China lineage villages, sited at the stream exit."""
        pr = self.px(r)
        pts = " ".join(f"{x + pr * math.cos(a):.1f},{y + pr * math.sin(a):.1f}" for a in [math.pi / 6 + i * math.pi / 3 for i in range(6)])
        self.add(f'<polygon points="{pts}" fill="#C9876C" stroke="#6B2A18" stroke-width="2" stroke-linejoin="round"/>')
        self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{pr * 0.42:.1f}" fill="none" stroke="#6B2A18" stroke-width="1.2"/>')
        self.M.setdefault("water_mouths", []).append({"x": round(x, 1), "y": round(y, 1), "w": pr * 2, "h": pr * 2, "rot": 0})
        self.note_focal("water_mouth")
        self._focal_block(x, y, pr * 2, pr * 2)

    def market(self: Settlement, x: float, y: float, w: float = 120, h: float = 84) -> None:  # type: ignore[misc]
        """A village MARKET clearing (墟/市), a focal feature: an open packed-earth space with a few stalls
        where a periodic market gathers - a widening in the lane fabric, not a building. Draws the open court +
        a row of stall marks, records M['markets'] + the focal feature. Grounding: a market node is exactly
        where a `cross` lane skeleton reads as a market village rather than a plain farming one."""
        pw, ph = self.px(w), self.px(h)
        cid = self._cid("mkt")
        self.add(f'<clipPath id="{cid}"><rect x="{x - pw / 2:.1f}" y="{y - ph / 2:.1f}" width="{pw:.1f}" height="{ph:.1f}" rx="3"/></clipPath>')
        self.add(f'<rect x="{x - pw / 2:.1f}" y="{y - ph / 2:.1f}" width="{pw:.1f}" height="{ph:.1f}" fill="#D8C7A0" stroke="#9C7A40" stroke-width="1.6" stroke-dasharray="5 4" rx="3"/>')
        stalls = "".join(
            f'<rect x="{x - pw / 2 + self.px(10) + i * self.px(22):.1f}" y="{y - self.px(6):.1f}" width="{self.px(14):.1f}" height="{self.px(12):.1f}" fill="#C9A57A" stroke="#6B4F2A" stroke-width="1"/>'
            for i in range(max(1, int(w / 34)))
        )
        self.add(f'<g clip-path="url(#{cid})">{stalls}</g>')
        self.M.setdefault("markets", []).append({"x": round(x, 1), "y": round(y, 1), "w": pw, "h": ph, "rot": 0})
        self.note_focal("market")
        self._focal_block(x, y, pw, ph)

    def alley(self: Settlement, pts: Any, width: float | None = None) -> None:  # type: ignore[misc]
        """An UNPAVED interior lane (gravel / wood planks, not the dressed earth of a street) that
        threads the packed block cores: the poor reach their jammed interior housing by alleys,
        not the paved street frontage. Thinner than a street, drawn as a pale gravel path with a
        plank/speckle dash, and a NARROW no-build corridor so the dense core leaves a gap for it.
        Real width ~10 ft (a generous roji is 3-6 ft; ours carries the access for a whole block
        core) - at city scale that lands on the 4px linework floor, which is the doctrine: a roji
        is drawn at the minimum visible width, never to (invisible) true scale."""
        if width is None:
            width = self.lw(10)
        dd = 'M' + ' L'.join(f'{x},{y}' for x, y in pts)
        self.corridors.append((pts, width / 2 + 11))  # setback keeps building CORNERS off the lane, not just centers
        al = {"pts": [[x, y] for x, y in pts], "w": width, "z": None}
        self.M.setdefault("alleys", []).append(al)
        self._ground(
            width,
            al,
            "z",  # an unpaved gravel lane: its surface IS the bed (no curb/edge), plus a speckle
            bed=f'<path d="{dd}" fill="none" stroke="#C7BB9C" stroke-width="{width}" opacity="0.85" stroke-linejoin="round" stroke-linecap="round"/>',
            top=f'<path d="{dd}" fill="none" stroke="#9A8A68" stroke-width="1.4" stroke-dasharray="2,5" opacity="0.7"/>',
        )
