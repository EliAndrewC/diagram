"""tier town tests split out of `tests.settlement.test_water_ways` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram.settlement import Settlement
from tests.settlement._builders import _town


@pytest.mark.tiers("town")
def test_ward_kido_squares_to_the_lane_it_bars_and_keeps_its_box_off_the_roadbed():
    # GM 2026-07-26: the gate shuts a WAY. A 45deg fence crossed by a HORIZONTAL street gets a
    # gate square to the street (90deg), not to the fence - and the watch box stands on the verge.
    s = Settlement(1000, 1000, seed=1)
    s.street([(100, 450), (900, 450)])
    s.ward("slant", [(300, 300), (600, 600)], gates=[(450, 450)])
    k = s.M["kido"][-1]
    assert abs(k["rot"] - 90.0) < 0.5  # square across the street, NOT the fence's 45deg
    st = s.M["town_streets"][-1]
    half = st["w"] / 2
    assert all(abs(cy - 450) > half for _, cy in k["guard"])  # the box is beside the roadbed, not in it


@pytest.mark.tiers("town")
def test_street_default_width_falls_back_to_the_ft_scale():
    # street() with no explicit width uses a real 24 ft, converted at the map's ftpx and linework-floored
    s = _town()
    s.street([(100, 200), (900, 200)])  # no width -> the lw(24) default branch
    assert s.M["town_streets"][0]["w"] == s.lw(24)


@pytest.mark.tiers("town")
def test_pack_core_skips_the_street_facing_band():
    # face_streets="core" leaves the near-street band for shop frontage: dwellings pack only
    # the deep block interior
    s = Settlement(1000, 1000, seed=2)
    s.meta(name="T", scale="town")
    s.street([(100, 500), (900, 500)], width=24)
    s.pack((150, 300, 850, 700), ["laborer"] * 30, step=40, face_streets="core")
    import math as _m

    for b in s.M["buildings"]:
        assert _m.hypot(0, b["y"] - 500) > 76 or not (100 <= b["x"] <= 900)
