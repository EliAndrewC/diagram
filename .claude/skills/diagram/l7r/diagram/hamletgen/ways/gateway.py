"""The gateway walled in: where the connector's sweep from the cluster's gateway finds no dry way out of the frame (feature 315).

Split out of `track.py` at the 1,000-line bar; a layer above it - it sweeps with `track.connector_track` - and `stage_track`
imports it where it is called.

Research: gateway plumbing - NONE
"""

from __future__ import annotations

import contextlib
import math
from collections.abc import Mapping, Sequence

from l7r.diagram.settlement import Settlement

from ..consts import Poly, Pt
from ..plan import SitePlan
from .dry_exit import clear_of_bands
from .track import CONNECTOR_WIDTH, NoDryExit, _cluster_gateway, connector_track, gate_on_the_strip


def gateway_track(
    s: Settlement, plan: SitePlan, seat: Mapping[str, object], band_gate: Pt, gate: Pt, avoid: Sequence[Poly], wet: Sequence[Poly], waters: Sequence[tuple[Pt, Pt]], fabric: Sequence[Poly]
) -> Poly:
    """The connector's track from `gate`, swept (`connector_track`); and where that finds no dry way out - A GATEWAY WALLED IN
    (feature 315, cohort seed 19: walked out clear of every steading, it stopped in the corner of a farm's own grove, and every
    way out of the pocket was narrower than a track's gap) - out along the exit strip where the seating reserved one, else from
    the cloud's edge on a bearing turned off the downslope, the nearest turn first. The gateway is first stepped clear of what
    stands that a way may not run on (`clear_of_what_stands`).

    Research:
        track off the map - research/questions/0081-village-lanes.drawing.html: swept from the gateway to the frame
        a walled-in gateway - UNRESEARCHED: out along the exit strip, else from a gateway turned off the downslope"""
    gate = clear_of_what_stands(s, gate)
    try:
        return connector_track(plan, gate, avoid=avoid, wet=wet, waters=waters, fabric=fabric)
    except NoDryExit:
        if s.M.get("access_exit"):
            return track_from_the_strip_end(s, plan, gate, avoid, wet, waters, fabric)
        return turned_gateway_track(s, plan, seat, band_gate, avoid, wet, waters, fabric)


GATEWAY_TURNS_DEG = (30.0, -30.0, 60.0, -60.0, 90.0, -90.0)
"""The bearings off the downslope a walled-in gateway is sought on, nearest first (feature 315, `turned_gateway_track`).

Research: turned gateway bearings - UNRESEARCHED: 30, 60 then 90 degrees either side of the downslope"""


def turned_gateway_track(
    s: Settlement, plan: SitePlan, seat: Mapping[str, object], band_gate: Pt, avoid: Sequence[Poly], wet: Sequence[Poly], waters: Sequence[tuple[Pt, Pt]], fabric: Sequence[Poly]
) -> Poly:
    """The track from the first gateway, on a bearing turned off the downslope (`GATEWAY_TURNS_DEG`), whose sweep finds a dry way out
    of the frame; refused where none does, as the downslope gateway was.

    Research: the nearest turn first - UNRESEARCHED: the first bearing whose sweep finds a dry way out"""
    for deg in GATEWAY_TURNS_DEG:
        gate = gate_on_the_strip(s, plan.envelope, _cluster_gateway(s, seat, band_gate, deg))
        with contextlib.suppress(NoDryExit):
            return connector_track(plan, gate, avoid=avoid, wet=wet, waters=waters, fabric=fabric)
    raise NoDryExit("no dry way out of the frame from a gateway on any bearing off the cluster")


def track_from_the_strip_end(s: Settlement, plan: SitePlan, gate: Pt, avoid: Sequence[Poly], wet: Sequence[Poly], waters: Sequence[tuple[Pt, Pt]], fabric: Sequence[Poly]) -> Poly:
    """The track where the gateway itself is walled in (feature 315, cohort seed 19: a gateway seated in the corner of a farm's
    own grove): out along the exit strip the seating reserved, and swept from its outer end - the connector starts where the
    cluster ends (plan M3), as `connector_through`'s later fallbacks already have it. No strip, or none from its end: refused.

    Research: out along the exit strip - UNRESEARCHED: swept again from the strip's outer end"""
    strip = [(float(q[0]), float(q[1])) for q in s.M.get("access_exit") or []]
    if len(strip) < 2:
        raise NoDryExit(f"no dry way out of the frame from the gateway at ({gate[0]:.0f}, {gate[1]:.0f}), and no exit strip")
    out = connector_track(plan, strip[-1], avoid=avoid, wet=wet, waters=waters, fabric=fabric)
    return [gate, *([] if math.dist(gate, strip[-1]) < 1e-6 else [strip[-1]]), *out[1:]]


def clear_of_what_stands(s: Settlement, gate: Pt) -> Pt:
    """`gate` stepped out past half the connector's tread from every footprint the registry of what stands forbids a way on
    (feature 315, cohort seed 28: the gateway fell 9 px inside a farm's well, so every dry exit the fill sought started walled
    in, and the map was refused) - as the fill's start is stepped out of a grove band (`dry_exit.clear_of_bands`). A
    household's reserved wood seat is not a footprint: the way out may yet take one (`track.connector_through`).

    Research: nothing built on a lane - research/questions/0081-village-lanes.drawing.html: the gateway stepped half the connector's tread off every forbidden footprint"""
    st = getattr(s.M, "standing", None)
    if st is None:
        return gate
    return clear_of_bands(gate, [list(e[1]) for e in st.forbidding("lanes") if e[0] != "wood seat"], CONNECTOR_WIDTH / 2.0)
