"""Split from settlement.py by feature 025 - see settlement/CLAUDE.md for the index.

Research: civic drawing plumbing - NONE
"""

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from ..labels import Subject
from ..labels.geom import rect

if TYPE_CHECKING:
    from .core import Settlement


"""Research: honmaru size - research/questions/0139-the-castle-in-a-capital-where-it-sits-how-big-it-is-and-its-gates-shiro.drawing.html: about 2 ha (Nijo's honmaru about 150 m on a side, Hiroshima's upper honmaru about 2.2 ha)"""


"""Research: hall size - research/questions/0165-martial-training-grounds-and-dojo.drawing.html: one long building about 124 x 35 ft"""

"""Research: martial hall compound - UNRESEARCHED: 130 x 124 ft, the hall across its north, the master's house and the archery lane south of it"""


class CastleCivicMixin:
    """A hand-placed caption request and a freestanding wall - what is left of the castle and civic-building mixin after
    feature 392 retired the town and city drawing only the frozen legacy maps called.

    Research: mixin plumbing - NONE: the caption request and the wall carry their own claims
    """

    def place_caption(  # type: ignore[misc]
        self: Settlement,
        text: str,
        box: Sequence[float] | None,
        size: float = 9,
        italic: bool = True,
        weight: str = "normal",
        color: str = "#5A4326",
        rot: float = 0.0,
    ) -> None:
        """Caption the feature occupying `box` - seated in the label phase by the ONE placer (feature 266) as a POINT
        subject: the feature's box turned by `rot`, the caption beside it at the standard's first free ranked position.
        Use this instead of a hand-picked `s.label(x, y, ...)` whenever the caption names a specific feature. Records the
        subject box on the label so `label_hugs_its_referent` can measure the finished gap.

        `box` accepts None so `s.frontage_box` can be passed straight through; a None means the row placed nothing, and
        captioning an empty row is a gen-script bug, not something to draw.

        DEFERRED to the label phase: seating a caption at call time judges it against half a map (Tango's north gate
        market caption took the flank that later filled with the execution ground).

        Research: caption seat - CONVENTION: the one placer's ranked positions"""
        if box is None:
            raise ValueError(f"place_caption({text!r}) got no subject box - the feature it names placed nothing")
        x0, y0, x1, y1 = (float(v) for v in box)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        subject = Subject("point", tuple(rect(cx, cy, (x1 - x0) / 2, (y1 - y0) / 2, rot)), angle=rot)
        self._captions.append((text, subject, size, italic, weight, color))

    def wall(self: Settlement, pts: Any, gate: Any = None, label: Any = None, guardtower: bool = True) -> None:  # type: ignore[misc]
        """An irregular town rampart (thick polyline; may be an open arc anchored to a
        hill). gate=(x,y): a gap with posts, a guard station, and an optional guardtower.
        Recorded so the gate can check the wall and gate exist. No-build corridor.

        Research:
            a town rampart with a gate - research/questions/0125-town-walls-and-which-county-seats-had-one-chengqiang.html: an irregular thick line, gapped at the gate
            guard station and tower - research/questions/0147-city-and-town-gates-the-opening-the-gate-tower-and-the-crossing-of-the-moat-chengmen.drawing.html: a tower about 40 x 24 ft over the passage and a guard room about 12 x 18 ft inside; the code draws a 40 x 40 px tower beside the gate and a 96 x 46 px station
            rampart stroke - research/questions/0125-town-walls-and-which-county-seats-had-one-chengqiang.html, research/questions/0125-town-walls-and-which-county-seats-had-one-chengqiang.drawing.html: drawn 10 to 12 ft thick, 11 ft at the map's scale
            gate opening - research/questions/0147-city-and-town-gates-the-opening-the-gate-tower-and-the-crossing-of-the-moat-chengmen.drawing.html: a 13 ft passage
            gateposts - UNRESEARCHED: 14 x 48 px posts flanking the opening
            buildings kept off the rampart - research/questions/0125-town-walls-and-which-county-seats-had-one-chengqiang.drawing.html: a clear strip about 46 ft wide; the code keeps 46 px
            ground round the gate structures - research/questions/0147-city-and-town-gates-the-opening-the-gate-tower-and-the-crossing-of-the-moat-chengmen.drawing.html: about 36 ft clear around each
        """
        wc = '#3A352C'
        # the rampart renders in the WALL layer (over the ground lanes - a street running into it passes
        # UNDER it), with a genuine gap at the gate so the road shows through the opening
        go = self.px(13)  # the gate's 13 ft passage (0147)
        dd = self._gapped_ring(pts, [gate] if gate else [], go, closed=False)
        ww = self.M["wall_stroke"] = self.px(11)  # 10-12 ft at any grain (0125); recorded for the same reason as the city rampart's (see city_wall)
        self.M["wall_z"] = self.add_wall(f'<path d="{dd}" fill="none" stroke="{wc}" stroke-width="{ww:g}" stroke-linejoin="round" stroke-linecap="round"/>')
        self.add_wall(f'<path d="{dd}" fill="none" stroke="#6B5A3A" stroke-width="3" stroke-linejoin="round" opacity="0.5"/>')
        if gate:
            gx, gy = gate
            self.add_wall(f'<rect x="{gx - go / 2 - 14:.0f}" y="{gy - 24:.0f}" width="14" height="48" fill="{wc}"/>')  # gateposts (frame the opening)
            self.add_wall(f'<rect x="{gx + go / 2:.0f}" y="{gy - 24:.0f}" width="14" height="48" fill="{wc}"/>')
            # the gatehouse (guard station + tower) goes in the TOP layer: a street running
            # through the gate passes UNDER it, not over it
            gz = self.add_top(f'<rect x="{gx - 48:.0f}" y="{gy + 26:.0f}" width="96" height="46" rx="2" fill="#C9A57A" stroke="#5A4326" stroke-width="1.6"/>')  # guard station
            self.add_top(f'<line x1="{gx - 48:.0f}" y1="{gy + 49:.0f}" x2="{gx + 48:.0f}" y2="{gy + 49:.0f}" stroke="#5A4326" stroke-width="0.8"/>')
            self.M["gate_structs"] = [{"x": gx, "y": gy + 49, "w": 96, "h": 46, "z": gz}]  # guard station
            if guardtower:
                tz = self.add_top(f'<rect x="{gx + 50:.0f}" y="{gy - 44:.0f}" width="40" height="40" fill="#9C8A66" stroke="{wc}" stroke-width="2.4"/>')  # guardtower
                self.add_top(f'<rect x="{gx + 58:.0f}" y="{gy - 36:.0f}" width="24" height="24" fill="#6B5A3A"/>')
                self.M["gate_structs"].append({"x": gx + 70, "y": gy - 24, "w": 40, "h": 40, "z": tz})
            # block the guard station / tower from placement (rect + a building-half margin)
            for gs in self.M["gate_structs"]:
                bm = self.px(36)  # about 36 ft clear around each (0147)
                self.block_polys.append(
                    [
                        (gs["x"] - gs["w"] / 2 - bm, gs["y"] - gs["h"] / 2 - bm),
                        (gs["x"] + gs["w"] / 2 + bm, gs["y"] - gs["h"] / 2 - bm),
                        (gs["x"] + gs["w"] / 2 + bm, gs["y"] + gs["h"] / 2 + bm),
                        (gs["x"] - gs["w"] / 2 - bm, gs["y"] + gs["h"] / 2 + bm),
                    ]
                )
            self.M["gate"] = [gx, gy]
        self.M["wall"] = [[x, y] for x, y in pts]
        # no-build clearance kept wide enough that even a large building's CORNER (not
        # just its center) stays off the rampart stroke (half-diagonal of a 60x40 ~36)
        self.corridors.append(([(x, y) for x, y in pts], 46))
        if label:
            self.label(pts[0][0], pts[0][1] - 16, label, 12, italic=True, weight="bold", color=wc, ref=(min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)))
