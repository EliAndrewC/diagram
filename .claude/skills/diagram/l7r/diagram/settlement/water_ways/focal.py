"""Split from settlement/water_ways.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import Settlement


class FocalMixin:
    def note_focal(self: Settlement, kind: str) -> None:  # type: ignore[misc]
        """Record an optional FOCAL feature (feature 005 catalog) on the manifest so the twin-detector reads
        it as a distinctiveness axis (meta.focal_features). Call it for a focus DRAWN via an existing method -
        a secondary shrine via `shrine_hall(primary=False)`, an ancestral hall, a market clearing - as well as
        from the dedicated focal methods (`crescent_pond`, `mill`). Idempotent per kind."""
        foc = self.M["meta"].setdefault("focal_features", [])
        if kind not in foc:
            foc.append(kind)

    def mill(self: Settlement, x: float, y: float, wheel_side: str = "E", w: float = 30, h: float = 24) -> None:  # type: ignore[misc]
        """A water MILL (水磨 / 水車), a focal feature: a small mill house with an undershot WATERWHEEL on its
        watercourse side, for hulling/grinding. Place it BESIDE a watercourse with fall (a drain outfall or a
        stream), never on still pond water. `wheel_side` (N/E/S/W) is the side the wheel faces the water. Draws
        the house + wheel, records the footprint (M['mills']) + the `mill` focal feature, and reserves the
        footprint as a placement keep-out (call it before `farmsteads()` if the cluster could reach it)."""
        pw, ph = self.px(w), self.px(h)
        dx, dy = {"E": (1.0, 0.0), "W": (-1.0, 0.0), "N": (0.0, -1.0), "S": (0.0, 1.0)}[wheel_side]
        self.add(f'<rect x="{x - pw / 2:.1f}" y="{y - ph / 2:.1f}" width="{pw:.1f}" height="{ph:.1f}" fill="#C9A57A" stroke="#6B4F2A" stroke-width="2" rx="2"/>')
        self.add(f'<line x1="{x - pw / 2:.1f}" y1="{y:.1f}" x2="{x + pw / 2:.1f}" y2="{y:.1f}" stroke="#6B4F2A" stroke-width="1" opacity="0.6"/>')  # ridge line
        wx, wy = x + dx * (pw / 2 + self.px(5)), y + dy * (ph / 2 + self.px(5))  # waterwheel center, on the water side
        wr = self.px(9)
        spokes = "".join(
            f'<line x1="{wx:.1f}" y1="{wy:.1f}" x2="{wx + wr * math.cos(a):.1f}" y2="{wy + wr * math.sin(a):.1f}" stroke="#5A3F1E" stroke-width="1"/>' for a in [i * math.pi / 4 for i in range(8)]
        )
        self.add(f'<circle cx="{wx:.1f}" cy="{wy:.1f}" r="{wr:.1f}" fill="none" stroke="#5A3F1E" stroke-width="1.8"/>{spokes}')
        self.M.setdefault("mills", []).append({"x": round(x, 1), "y": round(y, 1), "w": pw, "h": ph, "rot": 0})
        self.note_focal("mill")
        self.placed.append((x, y, pw, ph))

    def _focal_block(self: Settlement, x: float, y: float, pw: float, ph: float) -> None:  # type: ignore[misc]
        """Reserve a focal footprint as a placement keep-out (so a later farmstead can never overlap it)."""
        self.placed.append((x, y, pw, ph))
        self.block_polys.append([(x - pw / 2 - 6, y - ph / 2 - 6), (x + pw / 2 + 6, y - ph / 2 - 6), (x + pw / 2 + 6, y + ph / 2 + 6), (x - pw / 2 - 6, y + ph / 2 + 6)])

    def secondary_shrine(self: Settlement, x: float, y: float, w_ft: float = 42, h_ft: float = 30) -> None:  # type: ignore[misc]
        """A SECONDARY tutelary/roadside shrine, a focal feature: a small second shrine besides the village's
        main one (a Benten by the pond, an Inari at a field corner). Records as a 'shrine' kind (so
        religious_matches_scale still sees only shrines) + the focal feature. Grounding: a village often kept a
        minor shrine in addition to its tutelary one; its PRESENCE + placement is a distinctiveness axis.
        TRUE SCALE: dimensions are real feet (a minor wayside hall ~42x30 ft, smaller than the tutelary)."""
        self.shrine(x, y, w_ft, h_ft, kind="shrine")
        self.note_focal("secondary_shrine")
