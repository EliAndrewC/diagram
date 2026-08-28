"""Feature 139 T52 (GM 2026-08-28): the polder's ring canal CLOSES - every toe collector ends ON the trunk it meets."""

from __future__ import annotations

import math

from l7r.diagram.waterfields import build_polder
from l7r.diagram.waterfields.polder import _onto_poly


def _d(pt: tuple[float, float], poly: list[tuple[float, float]]) -> float:
    q = _onto_poly(pt, poly)
    return math.hypot(q[0] - pt[0], q[1] - pt[1])


def test_onto_poly_is_the_nearest_point_of_the_polyline() -> None:
    poly = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0)]
    assert _onto_poly((50.0, 7.0), poly) == (50.0, 0.0)
    assert _onto_poly((130.0, 50.0), poly) == (100.0, 50.0)
    assert _onto_poly((-10.0, -10.0), poly) == (0.0, 0.0)  # clamped to the first vertex


def test_both_toe_collectors_end_on_the_feeder_and_the_drain() -> None:
    """The corner rounding sweeps each trunk's corner inside the lattice node the toes were laid to, so a
    toe's end stood 9 ft off the feeder's swept bend (the gap the GM pointed at, top-left of the ring).
    Each toe END now snaps onto the NEARER trunk - the east toe runs feeder -> drain, the west toe is the
    block's fourth side and runs drain -> feeder, so 'start onto the feeder' would throw it across the block."""
    for seed, wander in ((3, 0.0), (7, 0.3), (11, 0.15)):
        net = build_polder(2400, 2400, (300.0, 300.0), seed=seed, edge_wander=wander)
        trunks = {c["seg"]: c["pts"] for c in net["channels"] if c.get("seg") in ("feeder", "drain")}
        assert set(trunks) == {"feeder", "drain"}
        toes = [c for c in net["channels"] if c.get("seg") in ("e_toe", "w_toe")]
        assert len(toes) == 2
        for toe in toes:
            for end in (toe["pts"][0], toe["pts"][-1]):
                assert min(_d(end, trunks["feeder"]), _d(end, trunks["drain"])) < 0.6, (seed, toe["seg"], end)
            assert math.dist(toe["pts"][0], toe["pts"][-1]) > 500, "a toe still spans the block - it was not thrown across it"
