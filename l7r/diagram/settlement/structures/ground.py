"""Unbuilt GROUND SURFACES that reserve placement rather than structures that occupy it.

Split from settlement/structures.py by feature 114 - see settlement/structures/CLAUDE.md for the index.

Research: ground surface glyphs and captions - CONVENTION
"""

from typing import TYPE_CHECKING

from ...labels import Subject

if TYPE_CHECKING:
    from ..core import Settlement


#: the trunk road's default real width, feet - 5 ken (the 1604 Tokaido standard) drawn at 30 (feature 144)
ROAD_W_FT = 30.0
"""Research: trunk road width - research/questions/0137-domain-capitals-the-daimyos-castle-town-jokamachi.drawing.html: 30 ft, the Tokaido's 5 ken"""


class GroundMixin:
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
