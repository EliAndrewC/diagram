"""gate tests split out of `tests.settlement.test_rolling` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram.pipeline import rollcache
from l7r.diagram.settlement import Settlement

# SERVED FROM THE ROLL CACHE (feature 135): nothing here patches the engine, so the knobs and manifest are served
# while every function the roll executed is unchanged, and rolled for real when one moves.


@pytest.mark.rolls_map
def test_roll_village_stream_fed_with_a_pinned_water_source():
    # exercises the STREAM water path (a brook entering from a canvas edge) and a PINNED water_source_position
    # (edge_N is a legal stream source for a south-falling field). Covers the stream branches in roll_village +
    # draw_comb_field that the pond-fed demos do not.
    def produce():
        s = Settlement(W=2000, H=2600, seed=7)
        s.meta(name="Sr", scale="hamlet", ftpx=1, toscale=True, households=18, field_footbridges=True)
        s.pin_knob("water_source_position", "edge_N")
        return s.roll_village("Sr", households=18, down_deg=90, water_kind="stream", field_fall=1260), s.M

    (k, M), _how = rollcache.obtain("roll_village:stream:edge_N:seed7:hh18", produce)
    assert k["water_source_position"] == "edge_N" and M["meta"]["water_kind"] == "stream"
    assert M["houses"] and any(st for st in M["streams"])  # a stream source was drawn


@pytest.mark.rolls_map
def test_roll_village_honors_a_pinned_knob():
    # a pinned knob overrides the roll (US3 determinism surface, exercised through the roll entrypoint)
    def produce():
        s = Settlement(W=2000, H=2600, seed=7)
        s.meta(name="P", scale="hamlet", ftpx=1, toscale=True, households=18, field_footbridges=True)
        s.pin_knob("cluster_shape", "elongated")
        s.pin_knob("lane_skeleton", "spine")
        return s.roll_village("P", households=18, down_deg=90, water_kind="pond", field_fall=1260)

    k, _how = rollcache.obtain("roll_village:pond:pins:elongated+spine:seed7:hh18", produce)
    assert k["cluster_shape"] == "elongated" and k["lane_skeleton"] == "spine"
