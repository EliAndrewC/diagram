"""Town-tier ways and focal features - the market, the ancestral hall, the water mouth, alleys (feature 145: moved out of water_ways.py, which the hamlet path executes, so the module-level coverage floor judges only what a hamlet draws).

Research: town ways plumbing - NONE
"""

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
        village, its single most prominent structure - so a village that HAS one reads unmistakably by it.

        Research:
            hall size - research/questions/0050-ancestral-halls-in-south-china-villages-citang.html, research/questions/0050-ancestral-halls-in-south-china-villages-citang.drawing.html: 110 x 74 ft by default
            porch on the water side - research/questions/0050-ancestral-halls-in-south-china-villages-citang.drawing.html: the entry porch faces +y, the water
            hall glyph - CONVENTION: an inner eave line and a dark porch block
            focal keep-out - UNRESEARCHED: the footprint plus 6 px is reserved
        """
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
        the shuikou was a standard focal ensemble of south-China lineage villages, sited at the stream exit.

        Research:
            water-mouth seat - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.html: at the stream's exit, where the caller seats it
            a pavilion at the water mouth - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.html: a pavilion drawn (the page attests a grove there, no pavilion)
            pavilion size - UNRESEARCHED: a hexagon of 22 ft radius
            pavilion glyph - CONVENTION: a hexagon with an inner ring
        """
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
        where a `cross` lane skeleton reads as a market village rather than a plain farming one.

        Research:
            market ground - research/questions/0130-market-days-and-the-market-ground-ichi.drawing.html: an open court 120 x 84 ft by default
            stalls drawn - research/questions/0130-market-days-and-the-market-ground-ichi.drawing.html: a row of 14 x 12 ft stalls, one per 34 ft of width
            market glyph - CONVENTION: a dashed packed-earth court
        """
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
        """An UNPAVED interior lane (a roji) that threads the packed block cores: the poor reach their
        jammed interior housing by alleys, not the paved street frontage. Thinner than a street, with a
        NARROW no-build corridor so the dense core leaves a gap for it. Real width ~10 ft (a generous
        roji is 3-6 ft; ours carries the access for a whole block core) - at city scale that lands on
        the 4px linework floor, which is the doctrine: a roji is drawn at the minimum visible width,
        never to (invisible) true scale.

        Surface (research/contents.json#urban-fabric, "How our maps zone a city's lots"): a line of drain
        boards down the middle over a small ditch - HISTORICALLY ACCURATE, drawn as a dark center line of
        board-length dashes; the ground either side of the boards is read nowhere - a GUESS, drawn as
        plain beaten earth (the hamlet lane's tread color), no longer the gravel the maps once gave it.

        Research:
            alley width - research/questions/0136-town-streets-side-lanes-and-back-alleys-roji.drawing.html: 10 ft, floored at the 4 px linework minimum
            drain-board line - research/questions/0159-shops-on-the-street-tenements-behind-how-a-city-is-zoned-omotedana-uradana.html, research/questions/0159-shops-on-the-street-tenements-behind-how-a-city-is-zoned-omotedana-uradana.drawing.html: boards down the middle over a ditch
            ground beside the boards - GUESS: plain beaten earth
            board dashes - CONVENTION: long dashes with a hairline gap at each joint
            alley setback - UNRESEARCHED: buildings keep the half-width plus 11 px off the alley
        """
        if width is None:
            width = self.lw(10)
        dd = 'M' + ' L'.join(f'{x},{y}' for x, y in pts)
        self.corridors.append((pts, width / 2 + 11))  # setback keeps building CORNERS off the lane, not just centers
        al = {"pts": [[x, y] for x, y in pts], "w": width, "z": None}
        self.M.setdefault("alleys", []).append(al)
        self._ground(
            width,
            al,
            "z",  # an unpaved earth lane: its surface IS the bed (no curb/edge), plus the drain-board line (fabric/160)
            bed=f'<path d="{dd}" fill="none" stroke="#C9AE79" stroke-width="{width}" opacity="0.85" stroke-linejoin="round" stroke-linecap="round"/>',
            # the boards: butted planks over the ditch, so long dashes with a hairline gap at each joint (a map convention)
            top=f'<path d="{dd}" fill="none" stroke="#6B4F2A" stroke-width="1.6" stroke-dasharray="7,1.2" opacity="0.8"/>',
        )
