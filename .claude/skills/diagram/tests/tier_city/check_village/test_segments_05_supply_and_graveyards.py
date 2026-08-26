"""tier city tests split out of `tests.check_village.test_segments_05_supply_and_graveyards` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    _MOAT,
    _city_dead,
    f_only,
)


@pytest.mark.tiers("city")
def test_funerary_set_back_inside_wall_grave_exempt_from_moat():
    # a graveyard just inside the wall is shielded from the (outside) moat by the rampart -> exempt
    WALLSQ = [[200, 200], [800, 200], [800, 800], [200, 800]]
    M = {"meta": {"scale": "city"}, "wall": WALLSQ, "moat": _MOAT, "moat_width": 22, "cemeteries": [{"x": 230, "y": 500, "w": 50, "h": 36, "rot": 0, "parish": True}]}
    assert "funerary_set_back_from_water" not in f_only(M, "funerary_set_back_from_water")


@pytest.mark.tiers("city")
def test_funerary_set_back_outside_wall_grave_subject_to_moat():
    WALLSQ = [[200, 200], [800, 200], [800, 800], [200, 800]]
    M = {"meta": {"scale": "city"}, "wall": WALLSQ, "moat": _MOAT, "moat_width": 22, "cemeteries": [{"x": 120, "y": 500, "w": 50, "h": 36, "rot": 0, "parish": True}]}
    assert "funerary_set_back_from_water" in f_only(M, "funerary_set_back_from_water")


@pytest.mark.tiers("city")
def test_city_temples_have_graveyards_fires_when_a_temple_unserved():
    assert "city_temples_have_graveyards" in f_only(_city_dead(temples=[(320, 320, "A", True), (680, 700, "B", True)]), "city_temples_have_graveyards")


@pytest.mark.tiers("city")
def test_city_temples_have_graveyards_exempts_a_flagged_temple():
    assert "city_temples_have_graveyards" not in f_only(_city_dead(temples=[(320, 320, "A", True), (680, 700, "B", False)]), "city_temples_have_graveyards")


@pytest.mark.tiers("city")
def test_city_has_mausoleum_fires_when_missing():
    assert "city_has_mausoleum" in f_only(_city_dead(maus=[]), "city_has_mausoleum")


@pytest.mark.tiers("city")
def test_city_has_mausoleum_fires_when_outside_walls():
    assert "city_has_mausoleum" in f_only(_city_dead(maus=[(100, 100)]), "city_has_mausoleum")


@pytest.mark.tiers("city")
def test_city_has_mausoleum_fires_when_far_from_quarter():
    assert "city_has_mausoleum" in f_only(_city_dead(maus=[(260, 740)], gov=(740, 260)), "city_has_mausoleum")


@pytest.mark.tiers("city")
def test_city_has_mausoleum_passes_when_by_quarter():
    assert "city_has_mausoleum" not in f_only(_city_dead(), "city_has_mausoleum")


@pytest.mark.tiers("city")
def test_city_has_cremation_ground_fires_when_inside_walls():
    assert "city_has_cremation_ground" in f_only(_city_dead(crem=[(500, 400)]), "city_has_cremation_ground")


@pytest.mark.tiers("city")
def test_city_has_cremation_ground_passes_when_outside():
    assert "city_has_cremation_ground" not in f_only(_city_dead(), "city_has_cremation_ground")


@pytest.mark.tiers("city")
def test_city_has_ossuary_fires_when_far_from_cremation():
    assert "city_has_ossuary" in f_only(_city_dead(oss=[(900, 100)]), "city_has_ossuary")


@pytest.mark.tiers("city")
def test_city_has_ossuary_passes_when_by_cremation():
    assert "city_has_ossuary" not in f_only(_city_dead(), "city_has_ossuary")
