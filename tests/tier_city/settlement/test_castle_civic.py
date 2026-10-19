"""tier city tests split out of `tests.settlement.test_castle_civic` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

from l7r.diagram.settlement import Settlement

# ---- feature 174: the private dojos, whose COUNT is a GM formula ----------------------------------


def test_a_town_rampart_gate_puts_its_guard_station_on_the_TOP_layer() -> None:
    """ "a street running through the gate passes UNDER it, not over it" - so the gatehouse is drawn
    on the top layer rather than with the wall, and the guard station is recorded so a later check
    can find it.

    The guardtower is optional and both ways are asserted: a gate without one must still record its
    station, or the wall would appear ungarrisoned.
    """
    s = Settlement(1400, 1400, seed=7)
    s.meta(name="C", scale="city")
    s.wall([(200.0, 200.0), (1200.0, 200.0), (1200.0, 1200.0)], gate=(700.0, 200.0))
    assert s.M["gate_structs"], "the guard station is recorded"
    assert s.M["gate_structs"][0]["z"] > 0, "and drawn on the top layer, so a street passes under it"

    plain = Settlement(1400, 1400, seed=7)
    plain.meta(name="C", scale="city")
    plain.wall([(200.0, 200.0), (1200.0, 200.0)], gate=(700.0, 200.0), guardtower=False)
    assert plain.M["gate_structs"], "a gate with no tower still has its station"
    # the gate's furniture goes to the WALL and TOP streams, not `out` - a street passes under the
    # gatehouse, which is what `add_top` is for
    assert len(plain.top) < len(s.top), "and puts less on the top layer than one with a tower"
    assert s.walls, "the rampart itself is on the wall stream"
