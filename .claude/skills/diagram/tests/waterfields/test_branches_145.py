"""Feature 145: the branches of banks.py and palette.py the hamlet-path floor found no test reaching."""

from __future__ import annotations

from l7r.diagram.waterfields.banks import ring_solidity
from l7r.diagram.waterfields.palette import organic_parcel


def test_ring_solidity_degenerate_rings_score_one() -> None:
    assert ring_solidity([(0.0, 0.0), (1.0, 1.0)]) == 1.0  # fewer than three distinct points
    assert ring_solidity([(0.0, 0.0), (1.0, 1.0), (2.0, 2.0), (3.0, 3.0)]) == 1.0  # collinear: no hull
    assert abs(ring_solidity([(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]) - 1.0) < 1e-9


def test_organic_parcel_leaves_a_degenerate_polygon_alone() -> None:
    import random

    assert organic_parcel([(0.0, 0.0), (1.0, 0.0)], random.Random(1), 4.0, 0.05, 6.0) == [(0.0, 0.0), (1.0, 0.0)]
