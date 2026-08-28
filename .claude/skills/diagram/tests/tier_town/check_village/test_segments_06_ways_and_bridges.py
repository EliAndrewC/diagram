"""tier town tests split out of `tests.check_village.test_segments_06_ways_and_bridges` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import WALLSQ, f_only


@pytest.mark.tiers("city", "town")
def test_streets_reach_neighbors_catches_perpendicular_approaches():
    """GM 2026-08-10: "two city streets which approach each other... generally should
    intersect." The aligned-only test missed a street ending a short way off one it meets at a
    CORNER angle - and the first cut of the perpendicular test compared the end's bearing
    against the LINE OF SIGHT to the other street, which makes two parallel streets 60px apart
    look perpendicular. It must compare against the other street's own bearing."""
    base = {"meta": {"scale": "city", "walled": True, "W": 2000, "H": 2000, "ftpx": 3}, "wall": WALLSQ, "gates": [[500, 200]]}
    tee = {**base, "town_streets": [{"pts": [[400, 300], [400, 900]], "w": 10}, {"pts": [[470, 600], [900, 600]], "w": 10}]}
    assert "city_streets_reach_their_neighbors" in f_only(tee, "city_streets_reach_their_neighbors")  # the east street stops 70px off the north-south one
    joined = {**base, "town_streets": [{"pts": [[400, 300], [400, 900]], "w": 10}, {"pts": [[402, 600], [900, 600]], "w": 10}]}
    assert "city_streets_reach_their_neighbors" not in f_only(joined, "city_streets_reach_their_neighbors")
    parallel = {**base, "town_streets": [{"pts": [[400, 300], [400, 900]], "w": 10}, {"pts": [[460, 300], [460, 900]], "w": 10}]}
    assert "city_streets_reach_their_neighbors" not in f_only(parallel, "city_streets_reach_their_neighbors")  # 60px apart and PARALLEL - not a failed junction
