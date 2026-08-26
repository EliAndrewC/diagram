"""tier town tests split out of `tests.check_village.test_segments_05_supply_and_graveyards` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    _town_dead,
    f_only,
)


@pytest.mark.tiers("town")
def test_town_has_cremation_ground_fires_when_missing():
    assert "town_has_cremation_ground" in f_only(_town_dead([]), "town_has_cremation_ground")


@pytest.mark.tiers("town")
def test_town_has_cremation_ground_fires_when_among_dwellings():
    assert "town_has_cremation_ground" in f_only(_town_dead([(320, 300)]), "town_has_cremation_ground")


@pytest.mark.tiers("town")
def test_town_has_cremation_ground_passes_when_at_the_edge():
    assert "town_has_cremation_ground" not in f_only(_town_dead([(900, 900)]), "town_has_cremation_ground")


@pytest.mark.tiers("town")
def test_town_monasteries_have_graveyards_fires_when_unserved():
    M = {"meta": {"scale": "town"}, "religious": [{"x": 500, "y": 500, "w": 100, "h": 70, "kind": "monastery"}]}
    assert "town_monasteries_have_graveyards" in f_only(M, "town_monasteries_have_graveyards")


@pytest.mark.tiers("town")
def test_town_monasteries_have_graveyards_passes_with_precinct_ground_or_opt_out():
    M = {"meta": {"scale": "town"}, "religious": [{"x": 500, "y": 500, "w": 100, "h": 70, "kind": "monastery"}], "cemeteries": [{"x": 560, "y": 420, "w": 80, "h": 60, "rot": 0}]}
    assert "town_monasteries_have_graveyards" not in f_only(M, "town_monasteries_have_graveyards")
    M2 = {"meta": {"scale": "town"}, "religious": [{"x": 500, "y": 500, "w": 100, "h": 70, "kind": "monastery", "graveyard": False}]}
    assert "town_monasteries_have_graveyards" not in f_only(M2, "town_monasteries_have_graveyards")


@pytest.mark.tiers("town")
def test_town_has_ossuary_fires_when_missing():
    M = {"meta": {"scale": "town"}, "cremation_grounds": [{"x": 200, "y": 800, "w": 75, "h": 52, "rot": 0}]}
    assert "town_has_ossuary" in f_only(M, "town_has_ossuary")


@pytest.mark.tiers("town")
def test_town_has_ossuary_passes_beside_the_cremation_ground():
    M = {"meta": {"scale": "town"}, "cremation_grounds": [{"x": 200, "y": 800, "w": 75, "h": 52, "rot": 0}], "ossuaries": [{"x": 260, "y": 860, "w": 20, "h": 20, "rot": 0}]}
    assert "town_has_ossuary" not in f_only(M, "town_has_ossuary")


@pytest.mark.tiers("town")
def test_geometry_within_canvas_fires_on_a_stray_town_wall_vertex():
    M = {"meta": {"scale": "town", "W": 2000, "H": 1300}, "wall": [[300, 300], [9999999, 300], [700, 700]]}
    assert "geometry_within_canvas" in f_only(M, "geometry_within_canvas")


@pytest.mark.tiers("town")
def test_dry_plots_off_hill_fires_when_a_plot_sits_on_the_hill():
    M = {"meta": {"scale": "town"}, "hill": [500, 500, 200, 150], "dry_plots": [{"poly": [[480, 480], [520, 480], [520, 520], [480, 520]], "crop": "soy", "theta": 0.0}]}
    assert "dry_plots_off_hill" in f_only(M, "dry_plots_off_hill")


@pytest.mark.tiers("town")
def test_dry_plots_off_hill_passes_when_plots_avoid_the_hill():
    M = {"meta": {"scale": "town"}, "hill": [500, 500, 200, 150], "dry_plots": [{"poly": [[50, 50], [90, 50], [90, 90], [50, 90]], "crop": "soy", "theta": 0.0}]}
    assert "dry_plots_off_hill" not in f_only(M, "dry_plots_off_hill")
