"""tier city tests split out of `tests.check_village.test_segments_10_city_battery_c` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    f_only,
)


@pytest.mark.tiers("city")
def test_view_treats_the_crop_as_the_map_edge():
    # the Imperial road must run off the map edge through both gates. With a cropped city view,
    # "the edge" is the view, not the full canvas - a road that exits the view (but not the
    # canvas) counts as running through.
    base = {
        "meta": {"scale": "city", "walled": True, "W": 3000, "H": 2000},
        "wall": [[1300, 300], [1700, 300], [1700, 1700], [1300, 1700]],
        "gates": [[1500, 300], [1500, 1700]],
        "road": [[1500, 250], [1500, 1750]],
    }  # exits y250..1750, well inside the 0..2000 canvas
    assert "city_imperial_road_through" in f_only(base, "city_imperial_road_through")  # no view: road stops short of the canvas edge
    base["meta"]["view"] = [1250, 280, 500, 1440]  # crop to y280..1720
    assert "city_imperial_road_through" not in f_only(base, "city_imperial_road_through")  # road now exits the view -> runs through
