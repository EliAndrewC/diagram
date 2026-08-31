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


# ---- feature 174: the four TOWN-tier ways and focal features --------------------------------------
# `town_ways.py` was 21% covered (30 of 38 statements) because feature 145 moved these OUT of the
# module every hamlet executes, precisely so a hamlet roll would not be judged on them - and then
# nothing else ran them. Each is a direct call, and each records a FOCAL feature or a corridor that
# later placement must respect, which is what these tests pin.


def test_an_ancestral_hall_records_itself_as_a_focal_feature_and_reserves_its_ground() -> None:
    """Research D2: the ancestral hall was the ritual and governance center of a Huizhou/Hakka
    lineage village, its single most prominent structure - so a village that HAS one reads
    unmistakably by it. That means it must both be recorded as focal and BLOCK, or a later pack
    would seat houses across the grandest building in the settlement."""
    s = _town()
    s.ancestral_hall(500.0, 500.0)
    assert s.M["ancestral_halls"], "recorded under its own key"
    assert "ancestral_hall" in s.M["meta"]["focal_features"], "and declared focal"
    assert not s._fits(500.0, 500.0, 12.0, 12.0), "its footprint is reserved"


def test_a_water_mouth_is_a_focal_pavilion_at_the_stream_exit() -> None:
    """The fengshui shuikou: the guarded outlet where the village stream leaves, marked by a small
    hexagonal pavilion to 'lock in' the qi of the departing water."""
    s = _town()
    s.water_mouth(300.0, 700.0)
    assert s.M["water_mouths"], "recorded under its own key"
    assert "water_mouth" in s.M["meta"]["focal_features"]


def test_a_market_is_an_OPEN_CLEARING_that_still_reserves_its_court() -> None:
    """ "a widening in the lane fabric, not a building" - so nothing is drawn as a solid hall, but
    the court is reserved all the same: a market nobody can stand in is not a market."""
    s = _town()
    s.market(600.0, 400.0)
    assert s.M["markets"], "recorded under its own key"
    assert "market" in s.M["meta"]["focal_features"]
    assert not s._fits(600.0, 400.0, 12.0, 12.0), "the clearing is held open against later packs"


def test_an_alley_is_drawn_at_the_LINEWORK_FLOOR_rather_than_to_true_scale() -> None:
    """The roji doctrine, stated in its own docstring: a real generous roji is 3-6 ft and ours
    carries a whole block core at ~10 ft, which at city scale lands on the 4 px linework floor - "a
    roji is drawn at the minimum visible width, never to (invisible) true scale"."""
    s = _town()
    before = len(s.M.get("alleys") or [])
    s.alley([(100.0, 100.0), (400.0, 100.0)])
    assert len(s.M["alleys"]) == before + 1
    assert s.M["alleys"][-1]["w"] == pytest.approx(s.lw(10)), "the linework floor decides, not the true 10 ft"
