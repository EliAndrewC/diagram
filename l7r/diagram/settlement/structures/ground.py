"""Unbuilt GROUND SURFACES that reserve placement rather than structures that occupy it.

Split from settlement/structures.py by feature 114 - see settlement/structures/CLAUDE.md for the index.

Research: ground surface glyphs and captions - CONVENTION
"""

from typing import TYPE_CHECKING, Any

from ...labels import Subject

if TYPE_CHECKING:
    from ..core import Settlement


#: the trunk road's default real width, feet - 5 ken (the 1604 Tokaido standard) drawn at 30 (feature 144)
ROAD_W_FT = 30.0
"""Research: trunk road width - research/questions/0137-domain-capitals-the-daimyos-castle-town-jokamachi.drawing.html: 30 ft, the Tokaido's 5 ken"""


class GroundMixin:
    def road(self: Settlement, pts: Any, label: Any = None, width: float | None = None, label_xy: Any = None) -> None:  # type: ignore[misc]
        """A major road (e.g. an Imperial road) - a bordered roadbed. No-build corridor.
        Default real width ROAD_W_FT = 30 ft (an Imperial trunk highway), converted at the
        map's ftpx and linework-floored. WHY 30 (GM 2026-08-28, feature 144): the Tokaido's
        width was standardized at 5 ken in 1604 ("街道の幅員を5間とし", ja.wikipedia 東海道 -
        `tokaido-jawiki` in research/sources/), 5 ken = 29.5 ft; drawn at the round 30 the
        GM asked for. The earlier 26 ft ("the Tokaido's own width") and the "~18-24 ft" this
        docstring once claimed were both unsourced - research/questions/0137-domain-capitals-the-daimyos-castle-town-jokamachi.drawing.html carries the read and the correction.
        label_xy overrides the label anchor (default: the polyline midpoint). For a city the
        midpoint is the city CENTER, but the road label names the *Imperial* road, which is an
        Imperial responsibility only OUTSIDE the walls - inside, the same roadway is a city
        street the city maintains - so a city must pass label_xy a point beyond the gates.

        Research:
            road width - research/questions/0137-domain-capitals-the-daimyos-castle-town-jokamachi.drawing.html: ROAD_W_FT by default
            building setback from the road - UNRESEARCHED: half-width plus 32 ft at the map's grain, floored at 17 px
            roadbed glyph - CONVENTION: bordered bed with a dashed center
            caption - CONVENTION: deferred to the label phase"""
        if width is None:
            width = self.lw(ROAD_W_FT)
        dd = 'M' + ' L'.join(f'{x},{y}' for x, y in pts)
        self.corridors.append((pts, width / 2 + max(32 * self.bscale, 17)))  # wide road -> larger building setback (at the map's grain, floored)
        if "road" not in self.M or self.M["road"] is None:
            self.M["road"] = [[x, y] for x, y in pts]  # the FIRST road stays the main road (back-compat
            self.M["road_width"] = width  # for the single-road checks/projections)
        self.M.setdefault("roads", []).append({"pts": [[x, y] for x, y in pts], "w": width})
        self.M["road_z"] = None
        self._ground(
            width,
            self.M,
            "road_z",
            edge=f'<path d="{dd}" fill="none" stroke="#9C7A40" stroke-width="{width}" opacity="0.9"/>',
            bed=f'<path d="{dd}" fill="none" stroke="#D8C49A" stroke-width="{width - 8}" opacity="1"/>',
            top=f'<path d="{dd}" fill="none" stroke="#8A6E3E" stroke-width="1.2" stroke-dasharray="12,10" opacity="0.6"/>',
        )
        if label:
            mid = pts[len(pts) // 2]
            lx, ly = label_xy if label_xy else (mid[0] + 46, mid[1] - 22)
            # DEFERRED to finish(): the label picks its side of the road by what is actually
            # built around it, and at road-draw time the map is still empty (GM label doctrine:
            # a label that can sit in empty ground, should; otherwise cover as little as possible)
            self._road_label: Any = (label, lx, ly)

    def _finish_road_label(self: Settlement) -> None:  # type: ignore[misc]
        """Seat and draw the Imperial road's caption in the label phase, by the ONE placer (feature 266): a LINE
        subject - the road's centerline at its drawn half-width - so the name runs along the road, above it before
        below it, never upside down, nearest the authored anchor first (psu-geog486-point-labels; research/contents.json#map-conventions,
        "Labels on maps (cartographic label placement)"). The anchor is a HINT for where along the road, never a distance."""
        text, lx, ly = self._road_label
        rd = [(float(p[0]), float(p[1])) for p in self.M.get("road") or []]
        half = float(self.M.get("road_width") or 26) / 2
        p = self._draw_seated_caption(text, Subject("line", tuple(rd), half_width=half, hint=(float(lx), float(ly))), 12, True, "bold", "#5A4326", None)
        self.M["road_label"] = [p.x, p.y]
