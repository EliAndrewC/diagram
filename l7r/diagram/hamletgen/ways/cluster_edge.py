"""Where a way leaves the placed cluster: the connector's gateway, its start on the exit strip, and the spur's origin facing
the field.

Lifted out of `track.py` at the 1,000-line bar (feature 316, when the research claims were carried over feature 315's merge);
`track` re-exports all four, which `gateway.py`, `ways/__init__.py` and the tests name there. A leaf: nothing here reads a
name the tests monkeypatch on `track`.

Research: plumbing - NONE: each placement rule is claimed at its function
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import cast

from l7r.diagram.settlement import Settlement

from ..consts import SPUR_SETBACK, TRACK_FABRIC_GAP, Poly, Pt
from .fabric import _homestead_polys
from .geom import push_clear_of_fabric, push_out_of


def _cluster_gateway(s: Settlement, seat: Mapping[str, object], fallback: Pt, turn_deg: float = 0.0) -> Pt:
    """Where a track leaves the settlement - measured from the PLACED houses, not the predicted band.

    FR-002, and feature 126's unfinished task T009. Until now the gateway came from
    `skeleton_layout(plan.lane_skeleton, 0, 0, seat["lat"], seat["dep"])` - a pure function of the
    rolled knob and the SEAT BAND, which is where the cluster was PREDICTED to go. The houses land
    where they land, and the two disagree; that mismatch is the recorded root of the
    `farmhouses_reach_a_way` defect that survived seventeen attempts.

    It also had a concrete cost the moment the track moved after the houses: a band-derived gateway
    can sit INSIDE the house cloud, and a track starting there has to leave through the settlement.
    One house on the reference hamlet ended up within 14 px of the connector's centerline - the
    threshold the retired `houses_off_corridors` check measured - and no amount of routing around the fabric fixed it,
    because the route's own start was in the middle of it.

    So: take the cloud's own extent along the seat axes and put the gateway on its DOWNSLOPE edge, clear of the last house. The fallback is the old band point, for the case where no house has been
    placed yet - which cannot happen in the shipped order, but a helper that assumes its caller is
    the failure mode this file has met repeatedly.

    Research:
        track leaves downslope - research/questions/0081-village-lanes.drawing.html: from the cluster's downslope edge (or a bearing turned off it)
        gateway clear of what stands - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a track passing outside the cluster keeps 7 ft off every part of a homestead - the gateway is walked out from the house centers (8 px its first step) until it clears all that stands by that gap (`push_clear_of_fabric`)
    """
    hs = s.M.get("houses") or []
    if not hs:
        return fallback
    ax, ay = cast(Pt, seat["along"])
    ox, oy = cast(Pt, seat["out"])
    if turn_deg:  # a bearing turned off the downslope (`stage_track`, where the downslope gateway has no dry way out)
        c, sn = math.cos(math.radians(turn_deg)), math.sin(math.radians(turn_deg))
        ox, oy, ax, ay = ox * c - oy * sn, ox * sn + oy * c, ax * c - ay * sn, ax * sn + ay * c
    xs = [float(h["x"]) for h in hs]
    ys = [float(h["y"]) for h in hs]
    cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
    # how far the cloud actually reaches, along each seat axis
    out_reach = max((x - cx) * ox + (y - cy) * oy for x, y in zip(xs, ys, strict=False))
    along_mid = sum((x - cx) * ax + (y - cy) * ay for x, y in zip(xs, ys, strict=False)) / len(xs)
    # THE CLOUD IS NOT ONLY THE HOUSES. Wells, byres, sheds and yards are seated in
    # `stage_appurtenances`, which runs BEFORE the track, and some of them stand outside the house
    # extent. A gateway measured from houses alone landed 3.6 px from a well on the reference hamlet
    # and the connector drew straight over it - `features_do_not_overlap`, wells x lanes.
    #
    # So walk outward until the gateway clears every standing thing by the track's own gap. Stepping
    # rather than solving: the fabric is an arbitrary set of polygons, the step is cheap, and a
    # bounded walk cannot fail to terminate the way a solve can.
    fabric = [poly for poly, _owner, _kind in _homestead_polys(s)]
    return push_clear_of_fabric((cx + ax * along_mid, cy + ay * along_mid), (ox, oy), out_reach + TRACK_FABRIC_GAP + 8.0, fabric)


def gate_out_of_the_field(envelope: Poly, gate: Pt) -> Pt:
    """The connector's start: `gate` pushed out of the field's `envelope` (`push_out_of`, the rule the track has always kept).

    Research:
        connector starts off the crop - research/questions/0081-village-lanes.drawing.html: the start pushed out of the field envelope
        setback from the field - research/questions/0081-village-lanes.drawing.html, research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a lane may touch a plot's boundary and the field path runs onto the outer bund - the way out is set 17 ft back from the field, a departure the code keeps until feature 417 T32; `SPUR_SETBACK` 17 ft clear of the field envelope"""
    return push_out_of(envelope, gate, SPUR_SETBACK)
