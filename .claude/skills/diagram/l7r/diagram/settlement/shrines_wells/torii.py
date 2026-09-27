"""The torii arch and the whole approach engine: the gen authors the LINE, the engine owns the count, the stride, the threshold and the wall clearance.

Split from settlement/shrines_wells.py by feature 116 - see settlement/shrines_wells/CLAUDE.md for the index.
"""

import math
from typing import TYPE_CHECKING, Any, cast

from .._geom import (
    TORII_PITCH_FT,
    Pt,
    segments_cross,
    torii_glyph_dims,
    torii_seat_on_wall,
    torii_wall_conflicts,
    wall_runs,
)

if TYPE_CHECKING:
    from ..core import Settlement


def avenue_along(seats: list[Pt], gaps: list[float], dist: float) -> Pt:
    """The point `dist` along the authored avenue line, measured by ARC LENGTH.

    LIFTED OUT OF `_avenue_pitch`'s closure (GM 2026-08-28, feature 146). The walk that steps past a
    segment - `d -= gaps[i]` - only runs for an avenue of three or more seats whose stride outruns the
    first gap, and reaching that through a whole shrine placement meant it was a branch no test could
    name. Here it is three lists and a float.
    """
    d = dist
    for i in range(len(seats) - 1):
        if d <= gaps[i] or i == len(seats) - 2:  # the last segment also carries any run PAST the authored line
            t = d / gaps[i] if gaps[i] else 0.0
            return (seats[i][0] + (seats[i + 1][0] - seats[i][0]) * t, seats[i][1] + (seats[i + 1][1] - seats[i][1]) * t)
        d -= gaps[i]  # this segment is wholly behind us - carry the remainder into the next
    return seats[-1]


def torii_plan_svg(tx: float, ty: float, ftpx: float, span_ft: float = 16.0) -> str:
    """The plan-view arch at (tx, ty): the beam as a bar across the approach, the two posts as squares on
    it (`torii_glyph_dims`). A module function so the wayside shrine's small arch draws the same thing."""
    s2, beam, post, p2 = torii_glyph_dims(ftpx, span_ft)
    return (
        f'<g transform="translate({tx:.0f},{ty:.0f})">'
        f'<line x1="{-s2:.1f}" y1="0" x2="{s2:.1f}" y2="0" stroke="#A03020" stroke-width="{beam:.2f}"/>'
        f'<rect x="{-p2 - post / 2:.2f}" y="{-post / 2:.2f}" width="{post:.2f}" height="{post:.2f}" fill="#7A2418"/>'
        f'<rect x="{p2 - post / 2:.2f}" y="{-post / 2:.2f}" width="{post:.2f}" height="{post:.2f}" fill="#7A2418"/></g>'
    )


class ToriiAvenueMixin:
    def _assert_walls_clear_of_torii(self: Settlement, what: str) -> None:  # type: ignore[misc]
        """Re-ask the torii/wall question the moment a WALL is on the page. A wall drawn AFTER an
        arch cannot be dodged by the arch (see CLAUDE.md "DRAW ORDER"), and neither feature can move
        once drawn - so the honest response is to fail the generator and let the author resite the
        geometry, exactly as the merchant-estate wall does when its slide fan runs out."""
        bad = torii_wall_conflicts(self.M)
        if bad:
            raise ValueError(
                f"{what} runs through torii arch(es) at {[(x, y) for x, y, _ in bad]} (in {bad[0][2]}) - a wall is a "
                f"continuous barrier and a torii is a freestanding gateway, so an arch never stands in one (a way "
                f"through a wall is a GATE: the city gate, a ward kido). Move the arch or the wall - or draw the wall "
                f"BEFORE the hall, and shrine_hall shortens its avenue to stop short of it automatically."
            )

    def _avenue_pitch(self: Settlement, seats: list[Pt]) -> list[Pt]:  # type: ignore[misc]
        """Lay a torii avenue at the PITCH (see TORII_PITCH_FT). The gen authors the avenue's LINE; the
        engine owns its stride, the same division of labor as the COUNT (rolled, not authored). EVERY
        avenue is re-laid at the pitch (feature 268, GM 2026-09-27: "All maps, ~10-13 ft"), resampled by
        arc length ALONG the authored line - so it keeps its direction and its curve, and its innermost
        arch keeps the seat the gen chose at the hall's threshold; only the stride changes. The old
        cap-and-band rule, which left an avenue inside the band alone, is retired with the band."""
        if len(seats) < 2:
            return seats
        gaps = [math.hypot(seats[i + 1][0] - seats[i][0], seats[i + 1][1] - seats[i][1]) for i in range(len(seats) - 1)]
        step = self.px(TORII_PITCH_FT)
        return [avenue_along(seats, gaps, step * i) for i in range(len(seats))]

    def _avenue_at_threshold(self: Settlement, x: float, y: float, w: float, h: float, seats: list[Pt]) -> list[Pt]:  # type: ignore[misc]
        """Seat a sando's INNERMOST arch ONE PITCH off the hall's front, sliding the whole run in along
        the face it approaches. The gen authors the avenue's LINE; the engine already owned its COUNT
        (the tier roll) and its STRIDE (`_avenue_pitch`), and this hands it the THRESHOLD too.

        WHY (GM 2026-07-27): "torii arches appear to be a sensible distance apart from each other but
        appear to start a huge distance away from city temples. The distance from the front of the
        temple should be the same as the distance between each torii arch." The gens had been
        authoring the whole run by hand, and once `_avenue_pitch` took over the stride the two numbers
        stopped agreeing: Tango's Bishamon sando stood 139 ft off its hall with 20 ft between arches -
        three arches marooned up a street past a flophouse, reading as marks beside an unrelated
        building - and Nagahara's Ebisu avenue began 120 ft south of its temple, in the middle of a
        housing block with the caption and two rows of houses between hall and first gate. An approach
        that does not TOUCH its hall is not an approach.

        The correction is a TRANSLATION, never a re-shaping: the run keeps its direction, its curve and
        its stride, and only its distance from the hall changes. It slides along the outward normal from
        the hall's FOOTPRINT to the innermost arch (point-to-rotated-rect geometry, per CLAUDE.md's "Gap VERDICT
        reads footprints, never centers") - so a run authored square in front of the hall walks straight
        in down its own axis, while one authored off to the side is pulled onto the flank it actually
        stands off, which is what makes the beside-the-hall gates read as that hall's. A run authored
        THROUGH the hall is left alone: that is `torii_clear_of_shrine`'s defect to report, not this
        method's to paper over."""
        if not seats:
            return seats
        pitch = math.hypot(seats[1][0] - seats[0][0], seats[1][1] - seats[0][1]) if len(seats) > 1 else self.px(TORII_PITCH_FT)
        nx = min(max(seats[0][0], x - w / 2), x + w / 2)  # the nearest point of the hall's footprint: the FRONT it stands off
        ny = min(max(seats[0][1], y - h / 2), y + h / 2)
        gap = math.hypot(seats[0][0] - nx, seats[0][1] - ny)
        if gap < 1e-6:  # the innermost arch is ON the hall - torii_clear_of_shrine's business
            return seats
        ux, uy, shift = (seats[0][0] - nx) / gap, (seats[0][1] - ny) / gap, pitch - gap
        return [(sx + ux * shift, sy + uy * shift) for sx, sy in seats]

    def _avenue_short_of_walls(self: Settlement, seats: list[Pt]) -> list[Pt]:  # type: ignore[misc]
        """Shorten a torii avenue so it stops SHORT of any wall (see wall_runs) - neither standing an
        arch in one nor marching the run across one, since a sando is a single approach and cannot
        continue on the far side of a barrier. It is a LINE of arches walking away from its hall, so
        the honest correction is to pull the whole run BACK - scale every seat's offset from the first
        arch by the largest factor that keeps the run clear - rather than shove one arch out of step
        with its neighbors (which would just straddle the wall). The first arch (nearest the hall)
        never moves, and the search floors out once the stride would close to one rail-span, since
        arches that touch are no avenue at all. Only walls ALREADY DRAWN are visible here (see
        CLAUDE.md "DRAW ORDER"); a wall laid later ACROSS an arch is caught by the wall methods'
        _assert_walls_clear_of_torii, and at the manifest by torii_clear_of_walls."""
        runs = wall_runs(self.M)

        def fit(f: float) -> list[Pt] | None:
            moved = [(seats[0][0] + (sx - seats[0][0]) * f, seats[0][1] + (sy - seats[0][1]) * f) for sx, sy in seats]
            if any(torii_seat_on_wall(self.M, mx, my, self.ftpx, runs) is not None for mx, my in moved):
                return None
            for _lbl, pts, _half in runs:  # ... and the WALK the arches stand on stays on ONE side of every wall
                if any(segments_cross(moved[i], moved[i + 1], pts[j], pts[j + 1]) for i in range(len(moved) - 1) for j in range(len(pts) - 1)):
                    return None
            return moved

        if not runs:
            return seats
        whole = fit(1.0)
        if whole is not None:
            return whole
        span = math.hypot(seats[-1][0] - seats[0][0], seats[-1][1] - seats[0][1])
        # The stride may tighten to the arch's drawn DEPTH plus one px (feature 268, D4) - the plan-view
        # glyph's post side - and never past it, so neighbors never touch. (The old floor was one rail-span,
        # which belonged to the elevation glyph; a floor above the 12 ft pitch would forbid any shortening.)
        floor_f = (torii_glyph_dims(self.ftpx)[2] + 1.0) * (len(seats) - 1) / span if span else 1.0
        f = 1.0
        while f - 0.02 > floor_f:
            f -= 0.02
            if (short := fit(f)) is not None:
                return short
        raise ValueError(
            f"the torii avenue from ({seats[0][0]:.0f},{seats[0][1]:.0f}) cannot be shortened clear of "
            f"{torii_seat_on_wall(self.M, seats[0][0], seats[0][1], self.ftpx, runs) or 'a wall'} without closing the "
            f"arches up on each other - resite the hall or its approach in the gen so the sando has open ground to run in."
        )

    def _torii(self: Settlement, tx: float, ty: float, span_ft: float = 16.0) -> int:  # type: ignore[misc]
        """Draw ONE torii arch TRUE SCALE (GM 2026-07-21), IN PLAN (feature 268, D3), and record it in
        M['torii']; returns the z-handle. `span_ft` is the TOP-BEAM span in real feet: a standard
        shrine/approach torii runs ~10-16 ft between its beam ends (grand landmark torii reach 30-50 ft,
        but none of our maps draws one). Seen from above an arch is its top beam across the approach with
        its two posts under it - `torii_glyph_dims` gives the sizes, the posts marked just proud of the
        beam (a drawing convention; real posts hide under it). The elevation glyph it replaces stood
        about 10 ft deep on paper and could not stand at the 12 ft pitch. STROKES keep a legibility floor
        (stroke convention - see SKILL.md "to scale"), never a footprint license."""
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
        winding path. Count is village-specific - pass as many points as torii+ends."""
        dstr = 'M' + ' L'.join(f'{x},{y}' for x, y in ascent)
        self.add(f'<path d="{dstr}" fill="none" stroke="#B89A6A" stroke-width="8" opacity="0.7"/>')
        self.add(f'<path d="{dstr}" fill="none" stroke="#6B4F2A" stroke-width="1" stroke-dasharray="3,5"/>')
        for tx, ty in ascent[1:-1]:
            self._torii(tx, ty)

    def torii_even(self: Settlement, ascent: Any, count: int) -> None:  # type: ignore[misc]
        """Spread `count` torii by arc-length along an ascent polyline (Kikuta style)."""
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
            tx, ty = along(0.06 + 0.80 * i / (count - 1))
            self._torii(tx, ty)
