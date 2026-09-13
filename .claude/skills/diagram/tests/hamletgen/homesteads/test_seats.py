"""The seat placers (`hamletgen/homesteads/seats.py`) on stub settlements - no roll."""

from __future__ import annotations

from l7r.diagram.hamletgen.homesteads import seats


def test_lane_frontage_skips_web_lanes_and_lanes_of_the_other_kind() -> None:
    """`lane_frontage` offers verges along internal lanes only: a web lane is never fronted, and the connector is
    skipped unless the caller is siting a LINEAR hamlet along it (`connector=True`), when it is the only lane fronted.
    Feature 217: this skip was the one engine line the seatings' partial roll alone reached; a stub settlement asks the
    same question in a millisecond."""

    class _S:
        M = {
            "lanes": [
                {"pts": [[0.0, 0.0], [0.0, 500.0]], "connector": True},
                {"pts": [[1000.0, 0.0], [1000.0, 500.0]]},
                {"pts": [[2000.0, 0.0], [2000.0, 500.0]], "web": True},
            ]
        }

    seat = {"cx": 50.0, "cy": 250.0}
    internal = seats.lane_frontage(_S(), seat)  # type: ignore[arg-type]
    assert internal and all(abs(x - 1000.0) < seats.LANE_FRONTAGE_STANDOFF + 1 for x, _ in internal), "only the internal lane is fronted"
    along = seats.lane_frontage(_S(), seat, connector=True)  # type: ignore[arg-type]
    assert along and all(abs(x) < seats.LANE_FRONTAGE_STANDOFF + 1 for x, _ in along), "with connector=True only the connector is fronted"
    assert not any(abs(x - 2000.0) < seats.LANE_FRONTAGE_STANDOFF + 1 for x, _ in internal + along), "a web lane is never fronted"


def test_a_homestead_is_refused_on_the_far_bank_of_the_brook() -> None:
    """Feature 230. A hamlet stands on one bank of the stream that passes it, and `seat_cluster` keeping the BAND
    off a divided margin is not the same as keeping every HOUSE on one bank - Kashikawa shipped a farmstead 52 ft
    beyond the brook from the other nineteen, 133 ft from the lane web, with no bridge anywhere on the water.

    The rule takes BOTH tests, and the test names why: the side of the nearest reach alone flips where the course
    wraps the field's toe, and a crossing of the line between two houses alone is true of a brook that merely
    bends around them."""
    from l7r.diagram.hamletgen.homesteads.stages import bank_of, far_bank

    brook = [(100.0, 0.0), (100.0, 200.0), (100.0, 400.0)]  # straight down the map at x = 100
    west, east = [(40.0, 200.0), (50.0, 250.0)], (300.0, 220.0)
    assert bank_of(40.0, 200.0, brook) != bank_of(300.0, 220.0, brook), "the two banks read as two sides"
    assert far_bank(east[0], east[1], brook, west), "a candidate across the water from every placed house"
    assert not far_bank(60.0, 300.0, brook, west), "and one on the hamlet's own bank is free"
    assert not far_bank(east[0], east[1], brook, []), "the first house is free - there is no bank yet"
    assert not far_bank(east[0], east[1], [], west), "and a map with no brook has no far bank"
