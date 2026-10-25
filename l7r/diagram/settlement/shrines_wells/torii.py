"""The torii arch and the whole approach engine: the gen authors the LINE, the engine owns the count, the stride, the threshold and the wall clearance.

Split from settlement/shrines_wells.py by feature 116 - see settlement/shrines_wells/CLAUDE.md for the index.

Research: plumbing - NONE
"""

import math
from typing import TYPE_CHECKING, Any, cast

from .._geom import (
    Pt,
    torii_glyph_dims,
    torii_seat_on_wall,
)

if TYPE_CHECKING:
    from ..core import Settlement


def torii_plan_svg(tx: float, ty: float, ftpx: float, span_ft: float = 16.0) -> str:
    """The plan-view arch at (tx, ty): the beam as a bar across the approach, the two posts as squares on
    it (`torii_glyph_dims`). A module function so the wayside shrine's small arch draws the same thing.

    Research:
        arch drawn in plan - CONVENTION: beam bar, posts proud of it
        default span - research/questions/0220-shrine-gateways-and-the-approach-to-the-hall-torii-sando.html: from about 8 ft between the posts at a country shrine to about 18 ft at a shrine of the city of Sendai, on the three stone arches found measured; pass P6), the order of this size; 16 ft
    """
    s2, beam, post, p2 = torii_glyph_dims(ftpx, span_ft)
    return (
        f'<g transform="translate({tx:.0f},{ty:.0f})">'
        f'<line x1="{-s2:.1f}" y1="0" x2="{s2:.1f}" y2="0" stroke="#A03020" stroke-width="{beam:.2f}"/>'
        f'<rect x="{-p2 - post / 2:.2f}" y="{-post / 2:.2f}" width="{post:.2f}" height="{post:.2f}" fill="#7A2418"/>'
        f'<rect x="{p2 - post / 2:.2f}" y="{-post / 2:.2f}" width="{post:.2f}" height="{post:.2f}" fill="#7A2418"/></g>'
    )


class ToriiAvenueMixin:
    def _torii(self: Settlement, tx: float, ty: float, span_ft: float = 16.0) -> int:  # type: ignore[misc]
        """Draw ONE torii arch TRUE SCALE (GM 2026-07-21), IN PLAN (feature 268, D3), and record it in
        M['torii']; returns the z-handle. `span_ft` is the TOP-BEAM span in real feet: a standard
        shrine/approach torii runs ~10-16 ft between its beam ends (grand landmark torii reach 30-50 ft,
        but none of our maps draws one). Seen from above an arch is its top beam across the approach with
        its two posts under it - `torii_glyph_dims` gives the sizes, the posts marked just proud of the
        beam (a drawing convention; real posts hide under it). The elevation glyph it replaces stood
        about 10 ft deep on paper and could not stand at the 12 ft pitch. STROKES keep a legibility floor
        (stroke convention - see SKILL.md "to scale"), never a footprint license.

        Research:
            arch span - research/questions/0220-shrine-gateways-and-the-approach-to-the-hall-torii-sando.html: from about 8 ft between the posts at a country shrine to about 18 ft at a shrine of the city of Sendai, on the three stone arches found measured; pass P6), the order of this size; 16 ft default
            arch in plan - CONVENTION
            never in a barrier - research/questions/0220-shrine-gateways-and-the-approach-to-the-hall-torii-sando.html: a torii can be built into a sacred fence, the tamagaki (the Encyclopedia of Shinto) - a torii is refused in a barrier, a departure the code keeps until feature 417 T35; raises
        """
        wall = torii_seat_on_wall(self.M, tx, ty, self.ftpx)  # an arch never stands IN a barrier - see the wall_runs block
        if wall:
            raise ValueError(
                f"torii at ({tx:.0f},{ty:.0f}) would stand in {wall} - a torii is a freestanding gateway on open "
                f"ground, never set into a barrier (a way through a wall is a GATE). Move the arch clear; a shrine_hall "
                f"avenue shortens itself to fit, so a hand-placed arch is what lands here."
            )
        tz = self.add_top(torii_plan_svg(tx, ty, self.ftpx, span_ft))  # over any street it crosses
        self.M["torii"].append([round(tx, 1), round(ty, 1), tz])
        return tz

    def torii_path(self: Settlement, ascent: Any) -> None:  # type: ignore[misc]
        """Place one torii at each interior vertex of the ascent polyline; draw the
        winding path. Count is village-specific - pass as many points as torii+ends.

        Research:
            arch count - research/questions/0220-shrine-gateways-and-the-approach-to-the-hall-torii-sando.drawing.html: one at each interior vertex the caller gives
            arch spacing on the path - research/questions/0220-shrine-gateways-and-the-approach-to-the-hall-torii-sando.drawing.html: 12 ft apart, the innermost 12 ft off the hall; set by the caller's vertices instead
            ascent path width - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P6, 2026-10-25); an 8 px stroke, about 24 ft at a city's 3 ft/px
            ascent path centerline - CONVENTION: a dashed centerline and its color
        """
        dstr = 'M' + ' L'.join(f'{x},{y}' for x, y in ascent)
        self.add(f'<path d="{dstr}" fill="none" stroke="#B89A6A" stroke-width="8" opacity="0.7"/>')
        self.add(f'<path d="{dstr}" fill="none" stroke="#6B4F2A" stroke-width="1" stroke-dasharray="3,5"/>')
        for tx, ty in ascent[1:-1]:
            self._torii(tx, ty)

    def torii_even(self: Settlement, ascent: Any, count: int) -> None:  # type: ignore[misc]
        """Spread `count` torii by arc-length along an ascent polyline (Kikuta style).

        Research:
            arch count - research/questions/0220-shrine-gateways-and-the-approach-to-the-hall-torii-sando.drawing.html: the caller's count
            arches spread over the ascent - DEVIATION research/questions/0220-shrine-gateways-and-the-approach-to-the-hall-torii-sando.drawing.html: from 6% to 86% of its length, not 12 ft apart nor 12 ft off the hall
            ascent path width - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P6, 2026-10-25); an 8 px stroke, about 24 ft at a city's 3 ft/px
            ascent path centerline - CONVENTION: a dashed centerline and its color
            its figures against 0220 - research/questions/0220-shrine-gateways-and-the-approach-to-the-hall-torii-sando.drawing.html: 0.06 (arches spread from 6% to 86% of the ascent); 0.8 (arches spread from 6% to 86% of the ascent) - a departure the code keeps until feature 417 T35
        """
        seg = [math.hypot(ascent[i + 1][0] - ascent[i][0], ascent[i + 1][1] - ascent[i][1]) for i in range(len(ascent) - 1)]
        tot = sum(seg)

        def along(t: float) -> Pt:
            target = t * tot
            acc: float = 0
            for i, sl in enumerate(seg):
                if acc + sl >= target:
                    f = (target - acc) / sl
                    return (ascent[i][0] + (ascent[i + 1][0] - ascent[i][0]) * f, ascent[i][1] + (ascent[i + 1][1] - ascent[i][1]) * f)
                acc += sl
            return cast(Pt, ascent[-1])  # pragma: no cover - defensive: t is capped at 0.86, never past the last segment [174: KEPT, not deletable - a terminal return]

        dstr = 'M' + ' L'.join(f'{x},{y}' for x, y in ascent)
        self.add(f'<path d="{dstr}" fill="none" stroke="#B89A6A" stroke-width="8" opacity="0.7"/>')
        self.add(f'<path d="{dstr}" fill="none" stroke="#6B4F2A" stroke-width="1" stroke-dasharray="3,5"/>')
        for i in range(count):
            tx, ty = along(0.06 + 0.80 * i / max(count - 1, 1))  # one arch stands at the foot; `count - 1` divided by zero (found by the feature-316 audit)
            self._torii(tx, ty)
