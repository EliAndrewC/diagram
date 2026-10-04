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

from l7r.diagram.settlement import seg_dist
from l7r.diagram.settlement.homestead_parts.groves import crown_lift
from l7r.diagram.settlement.homestead_parts.stands import crown_reach
from l7r.diagram.settlement.homestead_parts.wood_share import COPSE_CLUMP_BS

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

ROOT_FT = 40.0
"""The first leg of the track out, from the gate along the bearing out: the stretch the households' ways are laid to and join
at a T, as they joined the exit strip before it (feature 318) - and the leg the track out is drawn along from the gate
(`track.with_the_root`). A single point gathered every way into a knot of needle joins and doubled tails (cohort seeds 9,
17, 21, feature 320).

Research: the ways gather at the gate - UNRESEARCHED: a 40 ft first leg, past the 25 ft a way joins within"""


def box_poly(b: Sequence[float]) -> Poly:
    """A homestead's box `(cx, cy, w, h)` as its four corners.

    Research: plumbing - NONE: a box's corners"""
    x0, y0, x1, y1 = b[0] - b[2] / 2, b[1] - b[3] / 2, b[0] + b[2] / 2, b[1] + b[3] / 2
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


GATE_STEP_PX = 6.0
"""The step the gate is walked out along the bearing until its first leg clears every household's wood seat
(`clear_of_the_seats`): `push_clear_of_fabric`'s own step.

Research: plumbing - NONE: a search step"""

GATE_STEPS = 40
"""How many steps the gate is walked at most before it is left where it stands (the connector's law then decides).

Research: plumbing - NONE: a search bound"""


def seat_walls(s: Settlement) -> tuple[list[Pt], float]:
    """Every household's reserved wood seats and the reach a lane keeps off each: the buffer the registry reserves them with
    (`stages.reserve_the_seating`) and half the track's tread.

    Research: the track off the wood seats - UNRESEARCHED: a lane kept off a household's copse seat by the crown's reach (or 0.45 of the clump and 4 ft) and 4 ft more; the record keeps the copse off the main road, not the reverse"""
    clump = COPSE_CLUMP_BS * s.bscale
    reach = max(clump * 0.45 + 4, crown_reach(clump, 0.0, lift=crown_lift(s.bscale))) + 4.0
    seats = [(float(p[0]), float(p[1])) for h in s.M.get("houses") or [] for p in (h.get("wood_share") or {}).get("seats") or ()]
    return seats, reach


def clear_of_the_seats(gate: Pt, bearing: Pt, length: float, seats: Sequence[Pt], reach: float) -> Pt:
    """`gate` walked out along `bearing` until its first leg (`length` on along the bearing) passes no wood seat within `reach`;
    at most `GATE_STEPS` steps of `GATE_STEP_PX`, then the last point tried.

    Research: the track off the wood seats - UNRESEARCHED: the gate walked out until the track's first leg clears every copse seat; the record keeps the copse off the main road, not the reverse"""
    n = math.hypot(*bearing) or 1.0
    ux, uy = bearing[0] / n, bearing[1] / n
    g = gate
    for _ in range(GATE_STEPS):
        end = (g[0] + ux * length, g[1] + uy * length)
        if all(seg_dist(p[0], p[1], g, end) > reach for p in seats):
            return g
        g = (g[0] + ux * GATE_STEP_PX, g[1] + uy * GATE_STEP_PX)
    return g


CANVAS_INSET_PX = 12.0
"""How far inside the canvas's edge the gate and its first leg are held (`on_the_canvas`): past two of the gap raster's cells,
so the households' search finds them on its grid.

Research: plumbing - NONE: the raster's own reach"""


def on_the_canvas(s: Settlement, p: Pt) -> Pt:
    """`p` held `CANVAS_INSET_PX` inside the canvas: a cluster by the edge with its bearing out over it sent the gate off the map,
    where no way could be searched to it (feature 320).

    Research: plumbing - NONE: kept on the canvas"""
    m = CANVAS_INSET_PX
    return (min(max(p[0], m), float(s.W) - m), min(max(p[1], m), float(s.H) - m))


def way_out_gate(s: Settlement, plan: SitePlan, bearing: Pt) -> Pt:
    """Where the track out leaves the cluster: from the houses' center along `bearing` (the seating's lawful bearing out),
    past the farthest homestead box by `GATE_CLEAR_FT`, clear of every box (`push_clear_of_fabric`), its first leg clear of
    every household's wood seat (`clear_of_the_seats`), and out of the field's envelope (`gate_out_of_the_field`) - decided
    from the homesteads as seated, before any is drawn.

    Research: the gate on the cluster's edge - research/questions/0081-village-lanes.drawing.html: the track out leaves the cluster once its houses stand"""
    boxes = list(getattr(s, "placed", None) or [])
    hs = s.M.get("houses") or []
    cx = sum(float(h["x"]) for h in hs) / max(1, len(hs))
    cy = sum(float(h["y"]) for h in hs) / max(1, len(hs))
    ux, uy = bearing
    reach = max([((x - cx) * ux + (y - cy) * uy) for b in boxes for x, y in box_poly(b)], default=0.0)
    gate = push_clear_of_fabric((cx, cy), (ux, uy), reach + s.px(GATE_CLEAR_FT), [box_poly(b) for b in boxes])
    seats, seat_reach = seat_walls(s)
    return on_the_canvas(s, gate_out_of_the_field(plan.envelope, clear_of_the_seats(gate, (ux, uy), s.px(ROOT_FT), seats, seat_reach)))


def root_at_the_gate(s: Settlement, gate: Pt, bearing: Pt) -> tuple[Pt, Pt]:
    """The stretch of the way out the households' ways join: `ROOT_FT` from the gate along `bearing`.

    Research: the ways gather at the gate - UNRESEARCHED: the first leg of the track out from the gate"""
    d = s.px(ROOT_FT)
    n = math.hypot(*bearing) or 1.0
    return gate, on_the_canvas(s, (gate[0] + bearing[0] / n * d, gate[1] + bearing[1] / n * d))
