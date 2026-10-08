"""THE FULL TREE (feature 135, GM 2026-08-27): the `roll_village` pinned-knob DETERMINISM test. It must roll the same
seed twice for real - a second roll served from a cache would make "same seed, same bytes" vacuous - so it runs
where every roll is real. It EARNS its two village rolls: `make roll-audit` finds 15 lines of `settlement/rolling/roll.py`
that nothing else in the gate reaches (feature 221). Its sibling - "the same seed rolls the same combination, a different
seed a different one" - reached ONE line nothing else reached (`_geom/water_index.py`'s grid refusal, now a unit test in
`tests/settlement/test_geom.py`), so under feature 216's clause it moved to `tests/soak/test_village_determinism.py`.
The stream-fed and pinned-knob path tests stay at the gate, cached."""

import pytest

from l7r.diagram.settlement import Settlement


@pytest.mark.rolls_map
def test_pinned_knob_is_byte_identical_across_regens_and_rejects_incompatible_pins():
    # US3 (SC-006): a pinned knob is honored identically every regen; a pin outside the value space or one
    # that violates the geography typing rule is a LOUD error, never silently drawn.
    def build():
        s = Settlement(W=2000, H=2600, seed=11)
        s.meta(name="Pin", scale="village", ftpx=1, toscale=True, households=40, field_footbridges=True)
        s.pin_knob("cluster_shape", "split")  # split needs a village (typing rule) - legal here
        s.pin_knob("lane_skeleton", "cross")
        return s.roll_village("Pin", households=40, down_deg=90, water_kind="pond", field_fall=1400)

    k1 = build()
    k2 = build()
    assert k1 == k2 and k1["cluster_shape"] == "split" and k1["lane_skeleton"] == "cross"  # byte-identical, honored
    # a value outside the knob's space -> loud error
    s = Settlement(W=1800, H=1800, seed=1)
    s.meta(name="X", scale="village")
    s.pin_knob("cluster_shape", "octagon")
    with pytest.raises(ValueError):
        s.resolve("cluster_shape")
    # a value that VIOLATES the geography typing rule (split needs a village/town, not a hamlet) -> loud error
    s2 = Settlement(W=1800, H=1800, seed=1)
    s2.meta(name="Y", scale="hamlet")
    s2.pin_knob("cluster_shape", "split")
    with pytest.raises(ValueError):
        s2.resolve("cluster_shape")
