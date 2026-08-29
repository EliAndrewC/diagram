"""tier town tests split out of `tests.check_village.test_segments_01_city_frame_and_yards` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    bldg,
    f_only,
    manifest,
    yard,
)


@pytest.mark.tiers("town")
def test_structures_clear_of_trees_fires_when_a_crown_is_drawn_over_a_building():
    # a tree drawn on a roof erases the building - no drawn crown may overlap any ROOFED footprint,
    # and a ROTATED building is covered conservatively by its half-diagonal (as at placement).
    base = manifest(meta={"scale": "town"}, houses=[bldg(300, 300, "laborer")])
    assert "structures_clear_of_trees" in f_only({**base, "buildings": [bldg(600, 600, "servant")], "tree_crowns": [618, 600, 8]}, "structures_clear_of_trees")
    assert "structures_clear_of_trees" not in f_only({**base, "buildings": [bldg(600, 600, "servant")], "tree_crowns": [660, 600, 8]}, "structures_clear_of_trees")
    # ... every roofed kind counts, not just dwellings (here a storehouse), and a crown that only
    # reaches the OPEN yard beside a building is fine - yards have their own sun rules
    assert "structures_clear_of_trees" in f_only({**base, "storehouses": [{"x": 800, "y": 800, "w": 40, "h": 30, "rot": 0}], "tree_crowns": [822, 800, 6]}, "structures_clear_of_trees")
    assert "structures_clear_of_trees" not in f_only({**base, "threshing_yards": [yard(800, 800, of=(300, 300))], "tree_crowns": [800, 800, 6]}, "structures_clear_of_trees")
