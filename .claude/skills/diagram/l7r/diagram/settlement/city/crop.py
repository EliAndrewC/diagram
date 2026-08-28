"""The city crop (feature 145: moved out of core.py, which every map executes)."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import Settlement

from typing import TYPE_CHECKING


class CityCropMixin:
    def crop_city(self: Settlement, margin: float = 35, west: float | None = None, north: float | None = None, east: float | None = None, south: float | None = None) -> None:  # type: ignore[misc]
        """CITY content crop (GM 2026-07-23, replacing the hand-tuned wide MARGIN frames): frame the map to
        the moat ring + every KEPT satellite feature (gate markets, flophouses, funerary grounds, wharf
        stalls - the `_CROP_CITY` keys) + every placed LABEL box (labels_within_image demands containment),
        plus `margin`. The paddy fans, hems, farmhouses, and estates do NOT set the frame - they clip at
        the edge, reading as country that continues (the whole point of the wide-frame doctrine is kept by
        `margin`: ~100px past the moat still shows a working band of every fan that hugs the rim). Call
        AFTER every feature and label, BEFORE `title()` (the title drops into the framed window).
        Per-side margin overrides (west/north/east/south) keep a REPRESENTATIVE FARM BAND on a flank
        with no satellite to anchor the frame - e.g. Tango's west, where nothing but fans lies beyond
        the moat and the bare `margin` would re-create the pre-2026-07-23 sliver crop.
        THE AGGRESSIVE 35px MARGIN IS THE DEFAULT FOR ALL CITIES (GM 2026-07-23: "I would like the
        aggressive crop to be the default for all cities unless I state otherwise") - a new city gen
        calls `s.crop_city()` bare and adds only the farm-band override for its satellite-less flank
        (which flank that is varies by city; both current cities happen to use west=100)."""
        self.flush_stable_yards()  # yards draw HERE, seeing the complete map (GM 2026-07-24); their labels must exist before the frame is computed
        self.flush_tree_stands()  # ... and so does every wood's canopy, so no crown lands on a building placed after it
        _cboxes = self._crop_boxes(city=True)
        hx = [v for b in _cboxes for v in (b[0], b[1])]
        hy = [v for b in _cboxes for v in (b[2], b[3])]
        x0, y0 = max(0, min(hx) - (west if west is not None else margin)), max(0, min(hy) - (north if north is not None else margin))
        x1, y1 = min(self.W, max(hx) + (east if east is not None else margin)), min(self.H, max(hy) + (south if south is not None else margin))
        self.set_view(round(x0), round(y0), round(x1 - x0), round(y1 - y0))
