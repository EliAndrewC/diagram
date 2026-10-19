"""Split from settlement/water_ways.py by feature 173 - see this package's CLAUDE.md for the index.

Research: ward and quarter records - NONE
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..core import Settlement


class WardsMixin:
    """Ward fences and declared city quarters.

    Research:
        ward fence stroke - CONVENTION: 5 px
        quarter zones and reserve kinds - UNRESEARCHED: a declared vocabulary; a reserve draws as a drill ground, a garden or farmland
    """

    _QUARTER_ZONES = ("residential", "civic", "mixed", "reserve", "castle", "samurai")
    # "castle" and "samurai" are CAPITAL vocabulary (feature 021): the citadel's own ground and
    # the senior-compound bands. Both are deliberately outside the residential density body
    # (a C_YASHIKI compound is ~0.24 dwellings/1000px^2, legitimately under the machi floor)
    # and outside the civic-openness and reserve-cap rules; the tiling check counts them like
    # any quarter, so the interior stays fully declared.
    _RESERVE_KINDS = ("drill_ground", "garden", "agricultural_district")

    def quarter(self: Settlement, poly: Any, zone: str, kind: Any = None, label: Any = None) -> None:  # type: ignore[misc]
        """Declare a city QUARTER as a first-class zoned region (feature 006). A walled city is a
        set of quarters tiling its interior, each with a ZONE - `residential`, `civic`, `mixed`, or
        `reserve` - so density is judged PER QUARTER (an empty block in a residential quarter is a
        defect; the same emptiness in a declared civic/reserve quarter is intentional). Purely
        DECLARATIVE: it records the region + zone into M['quarters'] and does NOT move or place any
        building. A `reserve` quarter also carries a `kind` and is DRAWN as that visible feature
        (so open ground reads as a deliberate drill ground / garden / farmland, not accidental
        emptiness). Declare reserves BEFORE the packs so the surface renders under later features
        (like fields and streets). `poly` is a list of (x, y); `label` is an optional map label."""
        if zone not in self._QUARTER_ZONES:
            raise ValueError(f"quarter zone must be one of {self._QUARTER_ZONES}, got {zone!r}")
        if zone == "reserve":
            if kind not in self._RESERVE_KINDS:
                raise ValueError(f"a reserve quarter needs kind in {self._RESERVE_KINDS}, got {kind!r}")
            self._draw_reserve(poly, kind)
        elif kind is not None:
            raise ValueError(f"only a reserve quarter may carry a kind (got zone={zone!r}, kind={kind!r})")
        self.M["quarters"].append({"poly": [[round(x, 1), round(y, 1)] for x, y in poly], "zone": zone, "kind": kind, "name": label})
        if label:
            xs = [p[0] for p in poly]
            ys = [p[1] for p in poly]
            self.label(sum(xs) / len(xs), sum(ys) / len(ys), label, 9, italic=True, color="#5A4326", ref=(min(xs), min(ys), max(xs), max(ys)))

    def _draw_reserve(self: Settlement, poly: Any, kind: str) -> None:  # type: ignore[misc]
        """Render a reserve quarter's ground as its declared kind. A drill_ground is bare packed
        earth with a dashed muster perimeter; a garden is a planted green sward. An
        agricultural_district draws NOTHING here (GM 2026-07-22): its own combs, farmhouses, and
        label ARE the rendering - the faint dashed boundary this used to add read as a stray dotted
        line cutting through the in-wall farmhouses and across the Imperial road above the burakumin
        neighborhood. The quarter stays DECLARED in M['quarters'] either way (recorded by quarter(),
        not here), so per-quarter density judging is unaffected.

        Research:
            reserve glyphs - CONVENTION: swept earth with a dashed perimeter for a drill ground, green rows for a garden
            farmland draws nothing - CONVENTION: its own fields are its rendering
        """
        if kind == "agricultural_district":
            return  # no boundary line - the generator's fields carry the whole visual
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in poly)
        if kind == "drill_ground":
            # a muster / archery field: flat swept earth, a dashed perimeter, a few faint rake lines
            self.add(f'<polygon points="{pts}" fill="#D6C79E" stroke="#A9925C" stroke-width="1.4" stroke-dasharray="6,4"/>')
            xs = [p[0] for p in poly]
            ys = [p[1] for p in poly]
            x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
            for k in range(1, 5):
                ry = y0 + (y1 - y0) * k / 5
                self.add(f'<line x1="{x0 + 6:.1f}" y1="{ry:.1f}" x2="{x1 - 6:.1f}" y2="{ry:.1f}" stroke="#BBA76E" stroke-width="0.8" opacity="0.6"/>')
        elif kind == "garden":
            # an ornamental / kitchen garden sward: soft green with planted rows
            self.add(f'<polygon points="{pts}" fill="#C4D3A0" stroke="#6E8A44" stroke-width="1.3"/>')
            xs = [p[0] for p in poly]
            ys = [p[1] for p in poly]
            x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
            for k in range(1, 4):
                ry = y0 + (y1 - y0) * k / 4
                self.add(f'<line x1="{x0 + 6:.1f}" y1="{ry:.1f}" x2="{x1 - 6:.1f}" y2="{ry:.1f}" stroke="#6E9A40" stroke-width="2.0" stroke-linecap="round" opacity="0.75"/>')
