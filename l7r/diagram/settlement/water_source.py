"""Where a field's water comes in: the gravity-feedable source positions (`water_sources_for`) and the sluice point a
named position resolves to (`water_source_anchor`). Lifted out of `houses.py` at the 1,000-line bar (feature 328) as its
own mixin, composed into `Settlement` in `core.py`.

Research: plumbing - NONE: the mixin that carries the two methods
"""

import math
from typing import TYPE_CHECKING

from ._geom import Pt

if TYPE_CHECKING:
    from .core import Settlement


class WaterSourceMixin:
    @staticmethod
    def water_sources_for(down_deg: float, water_kind: str) -> list[str]:
        """The `water_source_position` values that gravity-feed a field falling toward `down_deg` (the source
        must sit UPHILL of the field intake - water runs downhill through the comb). Pond kinds are the
        corner/mid/chain set; a stream enters from a canvas edge. A source on the downhill half is excluded
        (it could not feed the field), which is the gravity typing the knob's own `typing_rule` defers to
        placement. Used by the seed roll so an unpinned water source lands somewhere water can actually flow
        from.
        Research: water source above the field - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: only positions off the downhill half"""
        dx, dy = math.cos(math.radians(down_deg)), math.sin(math.radians(down_deg))
        # each candidate's outward direction from field center; keep those on the UPHILL half (dot with
        # downhill <= a small tolerance, so a cross-slope side counts as feedable)
        dirs = {
            "corner_NW": (-1, -1),
            "corner_NE": (1, -1),
            "corner_SW": (-1, 1),
            "corner_SE": (1, 1),
            "edge_N": (0, -1),
            "edge_E": (1, 0),
            "edge_S": (0, 1),
            "edge_W": (-1, 0),
            "mid_margin": (-dx, -dy),
            "chain": (-dx, -dy),  # the uphill margin itself
        }
        pond = ["corner_NW", "corner_NE", "corner_SW", "corner_SE", "mid_margin", "chain"]
        edge = ["edge_N", "edge_E", "edge_S", "edge_W"]
        names = edge if water_kind == "stream" else pond
        out = []
        for nm in names:
            vx, vy = dirs[nm]
            n = math.hypot(vx, vy) or 1.0
            if (vx / n) * dx + (vy / n) * dy <= 0.35:  # not on the downhill half (tolerance admits cross sides)
                out.append(nm)
        return out

    def water_source_anchor(self: Settlement, position: str, field_bbox: tuple[float, float, float, float], down_deg: float, pad: float = 90.0) -> Pt:  # type: ignore[misc]
        """Resolve `water_source_position` into the SLUICE / stream-entry point (where water reaches the field
        head), just off the field on the named margin. Pond positions (`corner_*` / `mid_margin` / `chain`) put
        the feed on that corner or margin; stream `edge_*` positions put it at that canvas-edge margin. RAISES
        if the resolved point is on the DOWNHILL half of the field (gravity: a source below the field cannot
        feed it) - so a historically-impossible pin is rejected here, and `water_sources_for` lists the legal
        set for a roll. Grounding: Chinese canal doctrine feeds a comb from its high end; the varied high-side
        entry (a corner pond, a mid-margin tank, a stepped chain, a stream off one edge) is the knob.
        Research: where the water comes in - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: a corner, a margin or a canvas edge, `pad` (90 px) off the field, never downhill"""
        if position not in ("corner_NW", "corner_NE", "corner_SW", "corner_SE", "mid_margin", "chain", "edge_N", "edge_E", "edge_S", "edge_W"):
            raise ValueError(f"unknown water_source_position {position!r}")
        fx0, fy0, fx1, fy1 = field_bbox
        fcx, fcy = (fx0 + fx1) / 2, (fy0 + fy1) / 2
        dx, dy = math.cos(math.radians(down_deg)), math.sin(math.radians(down_deg))
        corners = {"corner_NW": (fx0 - pad, fy0 - pad), "corner_NE": (fx1 + pad, fy0 - pad), "corner_SW": (fx0 - pad, fy1 + pad), "corner_SE": (fx1 + pad, fy1 + pad)}
        edges = {"edge_N": (fcx, fy0 - pad), "edge_S": (fcx, fy1 + pad), "edge_E": (fx1 + pad, fcy), "edge_W": (fx0 - pad, fcy)}
        if position in corners:
            sx, sy = corners[position]
        elif position in edges:
            sx, sy = edges[position]
        else:  # mid_margin / chain: the middle of the UPHILL margin (opposite the fall)
            sx, sy = fcx - dx * ((fx1 - fx0) / 2 + pad), fcy - dy * ((fy1 - fy0) / 2 + pad)
        if (sx - fcx) * dx + (sy - fcy) * dy > 0.35 * math.hypot(sx - fcx, sy - fcy):
            raise ValueError(f"water_source_position {position!r} sits downhill of a field falling to {down_deg} deg - it cannot gravity-feed it")
        return (round(sx, 1), round(sy, 1))
