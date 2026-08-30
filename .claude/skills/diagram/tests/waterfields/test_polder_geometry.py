"""The polder's geometric guarantees, at the code that builds them (feature 166).

Carries `polder_fills_its_bbox`, `polder_floor_is_ring_interior`, `polder_edges_wander` and
`polder_dike_gapped_at_sluices`, which the retired battery re-measured on every finished map.

A polder is not placed feature by feature - `build_polder` lays the whole block at once, so its rules are
properties of that one construction and belong beside it. It takes plain numbers and returns plain data,
which is why these need no settlement, no manifest and no roll.
"""

from __future__ import annotations

import math

import pytest

from l7r.diagram.waterfields import build_polder

SEEDS = (3, 7, 11, 19)


def _net(seed: int, wander: float = 0.15):
    return build_polder(2400, 2400, (300.0, 300.0), seed=seed, edge_wander=wander)


def _bbox(poly):
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    return min(xs), min(ys), max(xs), max(ys)


def _area(poly) -> float:
    return abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))) / 2.0


@pytest.mark.parametrize("seed", SEEDS)
def test_the_polder_fills_the_box_it_claims(seed: int) -> None:
    """`polder_fills_its_bbox`. A polder is reclaimed land inside a ring, and the ring is drawn around
    what was drained - so a block whose envelope claims far more ground than it encloses is drawing a
    boundary around emptiness. The floor of 0.82 is what a wandering edge can cost an honest block."""
    net = _net(seed)
    env = net["envelope"]
    x0, y0, x1, y1 = _bbox(env)
    box = (x1 - x0) * (y1 - y0)
    assert box > 0
    assert _area(env) / box >= 0.82, f"seed {seed}: the envelope fills {_area(env) / box:.2f} of its own box"


@pytest.mark.parametrize("seed", SEEDS)
def test_the_floor_lies_inside_the_ring(seed: int) -> None:
    """`polder_floor_is_ring_interior`. The floor is the drained interior; a floor vertex outside the
    envelope is land the ring does not enclose being drawn as though it were reclaimed."""
    net = _net(seed)
    ex0, ey0, ex1, ey1 = _bbox(net["envelope"])
    for x, y in net["floor"]:
        assert ex0 - 1.0 <= x <= ex1 + 1.0 and ey0 - 1.0 <= y <= ey1 + 1.0, f"seed {seed}: floor point ({x:.0f}, {y:.0f}) outside the ring's bounds"


@pytest.mark.parametrize("seed", SEEDS)
def test_the_edges_wander_rather_than_ruling_straight(seed: int) -> None:
    """`polder_edges_wander`. A reclaimed block follows the water it took the land from; a polder whose
    sides are ruled straight reads as a survey plan rather than as ground. The wander knob must actually
    reach the drawn envelope - a knob that does not bind is the defect this whole feature keeps finding."""
    straight = _net(seed, wander=0.0)
    wobbly = _net(seed, wander=0.45)
    assert _area(wobbly["envelope"]) != _area(straight["envelope"]), f"seed {seed}: the wander knob changed nothing"


@pytest.mark.parametrize("seed", SEEDS)
def test_every_sluice_sits_on_the_ring_it_gaps(seed: int) -> None:
    """`polder_dike_gapped_at_sluices`. Water crosses the dike only where a sluice lets it, so a sluice
    recorded away from the ring is a gap in nothing, and water crossing elsewhere is a breach."""
    net = _net(seed)
    env = net["envelope"]
    assert net["dike_sluices"], f"seed {seed}: a polder with no sluice cannot drain"
    for s in net["dike_sluices"]:
        sx, sy = (s["x"], s["y"]) if isinstance(s, dict) else (s[0], s[1])
        near = min(math.dist((sx, sy), p) for p in env)
        assert near < 120.0, f"seed {seed}: a sluice {near:.0f} px from the ring gaps nothing"
