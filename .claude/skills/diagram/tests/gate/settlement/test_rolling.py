"""gate tests split out of `tests.settlement.test_rolling` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram.settlement import Settlement


@pytest.mark.rolls_map
def test_roll_village_is_deterministic_and_seed_varies_the_combination():
    # US2 (SC-004): the same seed rolls the SAME combination (byte-identical), a different seed rolls a
    # DIFFERENT one, and a rolled map is populated with no hand-placed coordinates.
    def roll(seed):
        s = Settlement(W=2000, H=2600, seed=seed)
        s.meta(name="R", scale="hamlet", ftpx=1, toscale=True, households=18, field_footbridges=True)
        return s, s.roll_village("R", households=18, down_deg=90, water_kind="pond", field_fall=1260)

    s7a, k7a = roll(7)
    _s7b, k7b = roll(7)
    assert k7a == k7b  # same seed -> identical roll
    _s8, k8 = roll(8)
    combo = ("cluster_position", "cluster_shape", "lane_skeleton", "water_source_position")
    assert tuple(k7a[c] for c in combo) != tuple(k8[c] for c in combo)  # different seeds -> different combination
    assert 15 <= len(s7a.M["houses"]) <= 19 and s7a.M["fields"] and s7a.view  # a populated, framed map


@pytest.mark.rolls_map
def test_roll_village_stream_fed_with_a_pinned_water_source():
    # exercises the STREAM water path (a brook entering from a canvas edge) and a PINNED water_source_position
    # (edge_N is a legal stream source for a south-falling field). Covers the stream branches in roll_village +
    # draw_comb_field that the pond-fed demos do not.
    s = Settlement(W=2000, H=2600, seed=7)
    s.meta(name="Sr", scale="hamlet", ftpx=1, toscale=True, households=18, field_footbridges=True)
    s.pin_knob("water_source_position", "edge_N")
    k = s.roll_village("Sr", households=18, down_deg=90, water_kind="stream", field_fall=1260)
    assert k["water_source_position"] == "edge_N" and s.M["meta"]["water_kind"] == "stream"
    assert s.M["houses"] and any(st for st in s.M["streams"])  # a stream source was drawn


@pytest.mark.rolls_map
def test_roll_village_honors_a_pinned_knob():
    # a pinned knob overrides the roll (US3 determinism surface, exercised through the roll entrypoint)
    s = Settlement(W=2000, H=2600, seed=7)
    s.meta(name="P", scale="hamlet", ftpx=1, toscale=True, households=18, field_footbridges=True)
    s.pin_knob("cluster_shape", "elongated")
    s.pin_knob("lane_skeleton", "spine")
    k = s.roll_village("P", households=18, down_deg=90, water_kind="pond", field_fall=1260)
    assert k["cluster_shape"] == "elongated" and k["lane_skeleton"] == "spine"


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
