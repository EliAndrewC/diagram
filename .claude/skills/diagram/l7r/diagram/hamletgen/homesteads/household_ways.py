"""THE WAY OUT'S GATE, DECIDED ONCE THE LAST HOUSE STANDS, AND THE HOUSEHOLDS' WAYS LAID TO IT (feature 320, plan D2).

The GM, 2026-10-04, of the exit strip and the field's corridor the seating used to reserve before any house: *"we should
eliminate both ... because the space we've already allocated can serve the same function"*. So nothing of a way is laid or
reserved while the farmhouses are seated - the lane's room between neighbors (feature 318) is what keeps a way possible.
Once the last house stands, the GATE is decided: the point on the cluster's edge, on the bearing out the seating found
lawful, where the track out will leave. Each household's way is laid in the gaps to it (`gap_ways.lay_the_ways`), before the
farmsteads are drawn, and the track out is drawn from it (`stage_track`).

Research: houses before lanes - research/questions/0081-village-lanes.drawing.html: every farmhouse seated before any way is laid; the track out leaves from the cluster's edge and each household's way joins it
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import TYPE_CHECKING

from ..consts import Poly, Pt
from ..ways.cluster_edge import gate_out_of_the_field
from ..ways.geom import push_clear_of_fabric

if TYPE_CHECKING:
    from l7r.diagram.settlement import Settlement

    from ..plan import SitePlan

GATE_CLEAR_FT = 24.0
"""How far past the farthest homestead box, along the bearing out, the gate stands: the track's own gap off the steadings
(`track.TRACK_FABRIC_GAP`, 16 ft) and the 8 ft the gateway has always been walked past it (`_cluster_gateway`).

Research: gate clear of the homesteads - UNRESEARCHED: 16 ft and 8 ft past the farthest homestead box"""

ROOT_FT = 1.0
"""The stretch of the way out from the gate the households' ways may end on while it is the only way on the map: a foot, so
the first way ends where the track out starts (`stage_track` draws it from the gate) and every later way joins one laid
before it or the gate - a longer stretch along the bearing out was not drawn when the track left the gate on another.

Research: the ways gather at the gate - NONE: the gate itself, a foot long so the search has a leg to end on"""


def box_poly(b: Sequence[float]) -> Poly:
    """A homestead's box `(cx, cy, w, h)` as its four corners.

    Research: plumbing - NONE: a box's corners"""
    x0, y0, x1, y1 = b[0] - b[2] / 2, b[1] - b[3] / 2, b[0] + b[2] / 2, b[1] + b[3] / 2
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def way_out_gate(s: Settlement, plan: SitePlan, bearing: Pt) -> Pt:
    """Where the track out leaves the cluster: from the houses' center along `bearing` (the seating's lawful bearing out),
    past the farthest homestead box by `GATE_CLEAR_FT`, clear of every box (`push_clear_of_fabric`), and out of the field's
    envelope (`gate_out_of_the_field`) - decided from the homesteads as seated, before any is drawn.

    Research: the gate on the cluster's edge - research/questions/0081-village-lanes.drawing.html: the track out leaves the cluster once its houses stand"""
    boxes = list(getattr(s, "placed", None) or [])
    hs = s.M.get("houses") or []
    cx = sum(float(h["x"]) for h in hs) / max(1, len(hs))
    cy = sum(float(h["y"]) for h in hs) / max(1, len(hs))
    ux, uy = bearing
    reach = max([((x - cx) * ux + (y - cy) * uy) for b in boxes for x, y in box_poly(b)], default=0.0)
    gate = push_clear_of_fabric((cx, cy), (ux, uy), reach + s.px(GATE_CLEAR_FT), [box_poly(b) for b in boxes])
    return gate_out_of_the_field(plan.envelope, gate)


def root_at_the_gate(s: Settlement, gate: Pt, bearing: Pt) -> tuple[Pt, Pt]:
    """The stretch of the way out the households' ways join: `ROOT_FT` from the gate along `bearing`.

    Research: the ways gather at the gate - UNRESEARCHED: the first leg of the track out from the gate"""
    d = s.px(ROOT_FT)
    n = math.hypot(*bearing) or 1.0
    return gate, (gate[0] + bearing[0] / n * d, gate[1] + bearing[1] / n * d)
