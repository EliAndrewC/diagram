"""THE ONE SOURCE both sides of the bridging rules read (feature 020), tested directly (feature 158).

`bridge_carried_ways` and `bridge_crossed_waters` exist so the generator's `bridges()` and the gate
cannot build the way / water sets separately and be wrong together - which is what happened before
them: both omitted `M["roads"]`, the river and a castle's own moat, agreed perfectly, and left four
of six crossings on the first capital unbridged with a GREEN gate.

They are tested here rather than through a gate segment because feature 158 retired
`bridges_align_with_their_way`, and its derivation (`_seg_0335` / `_seg_0336`) was the only thing in
the suite that called `bridge_carried_ways` at all. The doctrine for a hamlet-path module that loses
its exerciser is to bring it up BY TESTS, not to keep a retired check alive to run it - and a plain
function taking a dict is exactly the shape feature 146 says to prefer anyway.
"""

from __future__ import annotations

from typing import Any

from l7r.diagram.settlement import bridge_carried_ways, bridge_crossed_waters


def test_every_kind_of_way_a_bridge_may_have_to_carry_is_in_the_set() -> None:
    """Each branch, with the widths the manifest declares AND the defaults it omits - the defaults are
    the half that goes wrong silently, because a missing width reads as a way of no width at all."""
    M: dict[str, Any] = {
        "road": [[0, 0], [100, 0]],
        "road_width": 34,
        "roads": [{"pts": [[0, 50], [100, 50]], "w": 20}, {"pts": [[0, 60], [100, 60]]}],  # the second takes the default
        "ring_road": [[0, 100], [100, 100]],
        "town_streets": [{"pts": [[0, 150], [100, 150]], "w": 18}],
        "lanes": [{"pts": [[0, 200], [100, 200]], "w": 5}, {"pts": [[0, 210], [100, 210]]}],
    }
    widths = [w for _pts, w in bridge_carried_ways(M)]
    assert widths == [34, 20, 26, 8, 18, 5, 6], "the Imperial road, every other trunk road, the ring, the streets and the lanes, in that order"
    assert bridge_carried_ways({}) == [], "a manifest with no ways carries nothing"


def test_every_kind_of_water_a_way_may_have_to_be_carried_over_is_in_the_set() -> None:
    """Same for the water side, including the two cases the docstring calls out: an UNDRAWN channel is
    a buried conduit with no seam to bridge, and the river rides in `pts` rather than `poly`."""
    M: dict[str, Any] = {
        "streams": [{"poly": [[0, 0], [10, 0]], "w": 11}, {"poly": [[0, 5], [10, 5]]}],
        "channels": [{"poly": [[0, 10], [10, 10]], "w": 6}, {"poly": [[0, 15], [10, 15]], "drawn": False}],
        "field_ditches": [{"poly": [[0, 20], [10, 20]]}],
        "canals": [{"poly": [[0, 25], [10, 25]], "w": 14}],
        "moat": [[0, 30], [10, 30]],
        "moat_width": 24,
        "river": {"pts": [[0, 35], [10, 35]]},
        "castles": [{"moat": [[0, 40], [10, 40]]}, {}],  # the second castle has no moat of its own
        "aqueducts": [{"poly": [[0, 45], [10, 45]]}],
    }
    widths = [w for _pts, w in bridge_crossed_waters(M)]
    assert widths == [11, 9, 6, 4.2, 14, 24, 40, 26, 8], "the buried channel is absent; every default is its documented one"
    assert bridge_crossed_waters({}) == []


def test_a_river_recorded_only_as_a_poly_is_still_water() -> None:
    """The fallback arm. `s.river` writes `pts`, so `poly` never occurs in a real manifest - but the
    function reads both, and a branch nothing exercises is a branch nobody has seen work."""
    assert [w for _p, w in bridge_crossed_waters({"river": {"poly": [[0, 0], [9, 0]], "w": 33}})] == [33]
    assert bridge_crossed_waters({"river": {}}) == [], "a river record with no line is not water to bridge"
