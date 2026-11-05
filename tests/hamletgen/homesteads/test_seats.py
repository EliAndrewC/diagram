"""The seat placers (`hamletgen/homesteads/seats.py`) on stub settlements - no roll."""

from __future__ import annotations


def test_the_two_banks_of_the_brook_read_as_two_sides() -> None:
    """`bank_of` - which side of the brook a point stands on. Feature 261 retired the far-bank refusal it served (a
    hamlet may stand astride its brook now that ways cross it at a ford); it stays as the test of a farmstead's parts
    standing on their house's bank."""
    from l7r.diagram.hamletgen.homesteads.stages import bank_of

    brook = [(100.0, 0.0), (100.0, 200.0), (100.0, 400.0)]  # straight down the map at x = 100
    assert bank_of(40.0, 200.0, brook) != bank_of(300.0, 220.0, brook)
    assert bank_of(40.0, 200.0, brook) == bank_of(60.0, 300.0, brook)
