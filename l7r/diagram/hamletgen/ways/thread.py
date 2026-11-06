"""THE TRACK THREADED THROUGH THE FABRIC: `_thread_the_fabric` and its fallbacks, the spur's fold and the connector's room off a
grove band - lifted out of `track.py` at the 1,000-line bar (feature 405 T09, as `cluster_edge.py` was by feature 316); `track`
re-exports every name, so no importer changes. A test patches `_route` or `_out_of_bands` HERE, where `_thread_the_fabric` looks
them up.

Research: track plumbing - NONE"""

from __future__ import annotations

import math

from ..consts import (
    GROVE_WORKING_ROOM_FT,
    Poly,
)

CONNECTOR_WIDTH = 6.0
"""The connector's tread, px: the cart track out to the wider world, drawn wider than the web's footpaths.

Research: connector width - research/questions/0081-village-lanes.drawing.html: 6 ft"""

CONNECTOR_BAND_GAP_FT = GROVE_WORKING_ROOM_FT + CONNECTOR_WIDTH / 2.0
"""How far the connector's line keeps off a farm's grove band (`connector_dry_exit`): 0036's working room off the trees and the
connector's half-width, 12.5 ft (feature 385 T98: it was a footpath's gap and the half-width, 7 ft at the 4 ft footpath, 10 at
7, never 0036's room). Dispersed farms' bands stand 32 ft apart (feature 291's measure), so the 25 ft it asks still passes.

Research: the connector off a grove band - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: some working room off the trees each side of the tread, 9.5 ft beyond the 6 ft connector's half-width"""


def _inner(run: Poly, d: float = 3.0) -> Poly:
    """`run` with each end drawn in `d` along its own leg (405 T09): a fallback's ends stand on the bund or at the field's edge,
    which a crossing test at 0 ft would read as crossing the field; a leg shorter than twice `d` is kept whole.

    Research: the ends drawn in - GUESS: 3 ft at each end, so a fallback whose end stands on the bund or at the field's edge is
    not read as crossing it; a crossing nearer an end than that goes untested"""
    out = list(run)
    for i, j in ((0, 1), (-1, -2)):
        n = math.dist(out[i], out[j])
        if n > 2 * d:
            out[i] = (out[i][0] + (out[j][0] - out[i][0]) * d / n, out[i][1] + (out[j][1] - out[i][1]) * d / n)
    return out
