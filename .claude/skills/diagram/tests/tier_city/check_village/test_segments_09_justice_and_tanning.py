"""tier city tests split out of `tests.check_village.test_segments_09_justice_and_tanning` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import WALL, _fall_map, _side_map, _ty_map, _wf_map, f_only


@pytest.mark.tiers("city")
def test_tanning_yard_outside_walls_fires_when_the_work_is_inside():
    M = _ty_map(
        meta={"scale": "city", "walled": True, "ftpx": 3},
        wall=WALL,
        tanning_yards=[{"x": 500, "y": 500, "w": 27, "h": 17, "rot": 0, "label": "tanning yard"}],
    )
    assert "tanning_yard_outside_walls" in f_only(M, "tanning_yard_outside_walls")


@pytest.mark.tiers("city")
def test_tanning_yard_outside_walls_passes_beyond_the_rampart():
    M = _ty_map(
        meta={"scale": "city", "walled": True, "ftpx": 3},
        wall=WALL,
        streams=[{"poly": [[500, 100], [500, 1300]], "w": 8}],
        tanning_yards=[{"x": 500, "y": 1100, "w": 27, "h": 17, "rot": 0, "label": "tanning yard"}],
    )
    assert "tanning_yard_outside_walls" not in f_only(M, "tanning_yard_outside_walls")


@pytest.mark.tiers("city")
def test_moat_declares_circulation_fires_on_a_moat_with_no_inlet_or_outlet():
    M = _wf_map(meta={"scale": "city", "walled": True, "ftpx": 3, "water_flow": 90}, wall=WALL, moat=WALL)
    assert "moat_declares_circulation" in f_only(M, "moat_declares_circulation")


@pytest.mark.tiers("city")
def test_settlement_has_tanning_yard_honors_the_declared_opt_out():
    # meta(tannery=False): a settlement with water but no legitimate site on it (Tango)
    M = _ty_map(meta={"scale": "city", "walled": False, "ftpx": 3, "tannery": False})
    M.pop("tanning_yards")
    assert "settlement_has_tanning_yard" not in f_only(M, "settlement_has_tanning_yard")


@pytest.mark.tiers("city")
def test_settlement_declares_a_land_fall_fires_when_nothing_declares_a_slope():
    # the hole that let both provincial cities skip every drainage-slope rule behind a green gate
    assert "settlement_declares_a_land_fall" in f_only(_fall_map(), "settlement_declares_a_land_fall")


@pytest.mark.tiers("city")
def test_tanning_yard_on_the_outcast_side_passes_when_far_but_on_the_same_side():
    """The Nagahara case: ~300px of separation is FINE as long as the bearing agrees - the rule is
    directional, and a metric rule here would condemn a correct city map."""
    assert "tanning_yard_on_the_outcast_side" not in f_only(_side_map([(380, 800), (420, 800)], [(200, 200), (240, 200)]), "tanning_yard_on_the_outcast_side")
