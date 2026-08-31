"""Split from the 1,152-line `tests/settlement/test_structures.py` by feature 174 - see this
directory's CLAUDE.md for the index. Tests for `settlement/structures/compounds.py`."""

import pytest

from tests.settlement._builders import _estate_settlement, _town


def test_estate_wall_must_stand_on_dry_private_ground():
    """The municipal watch cannot be walled inside a private court, and the compound wall may not run
    through working water. Each refusal path asserted directly rather than left to map geometry."""
    s = _estate_settlement()
    assert s._estate_wall_clear(600, 600, 100, 80)  # clear ground
    s.M["fire_towers"] = [{"x": 600, "y": 600, "w": 10, "h": 10}]  # tower swallowed by the court
    assert not s._estate_wall_clear(600, 600, 100, 80)
    s2 = _estate_settlement()
    s2.M["fire_towers"] = [{"x": 650, "y": 600, "w": 10, "h": 10}]  # tower ON the wall line
    assert not s2._estate_wall_clear(600, 600, 100, 80)
    s3 = _estate_settlement()
    s3.M["canals"] = [{"poly": [(650, 400), (650, 800)], "w": 12}]  # canal crossing the wall
    assert not s3._estate_wall_clear(600, 600, 100, 80)
    s4 = _estate_settlement()
    s4.M["pond"] = (650, 600, 40, 40)  # pond under the wall
    assert not s4._estate_wall_clear(600, 600, 100, 80)


def test_merchant_estate_raises_when_no_clear_seat_exists():
    """Rather than draw a wall the gate will reject, an estate boxed in by water raises."""
    s = _estate_settlement()
    s.M["canals"] = [{"poly": [(x, 0), (x, 1200)], "w": 12} for x in range(400, 900, 40)]  # a thicket of canals
    with pytest.raises(ValueError, match="no seat within the slide fan"):
        s.merchant_estate(600, 600, 100, 80)


@pytest.mark.parametrize(
    ("key", "extra"),
    [
        ("moat", {"moat_width": 22}),
        ("road", {"road_width": 30}),
        ("ring_road", {"ring_road_width": 7}),
    ],
)
def test_a_compound_wall_may_not_stand_in_a_moat_a_road_or_the_ring_road(key: str, extra: dict) -> None:
    """`_estate_wall_clear` sweeps the whole street net and the whole water net, and each kind is its
    own branch reading its own width key. A test map that carries only streets and alleys leaves the
    rest of them unexercised - which is how a compound wall could have been laid down the middle of a
    ring road with every existing test green."""
    s = _town()
    through = [[100.0, 500.0], [900.0, 500.0]]
    assert s._estate_wall_clear(500.0, 500.0, 120.0, 90.0), "clear ground to begin with"
    s.M[key] = through
    s.M.update(extra)
    assert not s._estate_wall_clear(500.0, 500.0, 120.0, 90.0), f"a wall may line a {key}, never stand in its cleared band"
    assert s._estate_wall_clear(500.0, 200.0, 120.0, 90.0), "and a compound well clear of it is fine"


def test_a_compound_wall_may_not_stand_in_a_RIVER() -> None:
    """The river is recorded as a dict with its own `pts`/`w`, unlike the moat and the roads, so it is
    a separate branch and a separate test."""
    s = _town()
    assert s._estate_wall_clear(500.0, 500.0, 120.0, 90.0)
    s.M["river"] = {"pts": [[100.0, 500.0], [900.0, 500.0]], "w": 40.0}
    assert not s._estate_wall_clear(500.0, 500.0, 120.0, 90.0)
