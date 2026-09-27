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


def test_the_two_banks_of_the_brook_read_as_two_sides() -> None:
    """`bank_of` - which side of the brook a point stands on. Feature 261 retired the far-bank refusal it served (a
    hamlet may stand astride its brook now that ways cross it at a ford); it stays as the test of a farmstead's parts
    standing on their house's bank."""
    from l7r.diagram.hamletgen.homesteads.stages import bank_of

    brook = [(100.0, 0.0), (100.0, 200.0), (100.0, 400.0)]  # straight down the map at x = 100
    assert bank_of(40.0, 200.0, brook) != bank_of(300.0, 220.0, brook)
    assert bank_of(40.0, 200.0, brook) == bank_of(60.0, 300.0, brook)
