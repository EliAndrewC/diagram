"""tier town tests split out of `tests.check_village.test_segments_08_kosatsuba_and_basins` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    _kosatsuba,
    f,
    f_only,
)


@pytest.mark.tiers("town")
def test_kosatsuba_at_a_junction_may_face_either_way():
    # ANY route segment inside the siting band counts, not merely the nearest: a board at a
    # crossing legitimately fronts one of the two ways that meet there (the real case -
    # Nagahara's north-ward board sits nearer a cross street than the ward street it fronts)
    M = {
        "meta": {"scale": "town"},
        "kosatsuba": [dict(_kosatsuba(500, 480), rot=90)],
        "town_streets": [{"pts": [[0, 500], [1000, 500]], "w": 28}, {"pts": [[540, 0], [540, 1000]], "w": 28}],
    }
    assert "kosatsuba_faces_the_road" not in f_only(M, "kosatsuba_faces_the_road")


@pytest.mark.tiers("city", "town")
def test_city_kosatsuba_siting_threshold_is_scale_aware():
    # the ~60 ft siting limit is REAL feet: 30 px off the road passes at town grain (30 ft)
    # but fires at city grain (1 px = 3 ft -> 90 ft)
    road = [[0, 500], [1000, 500]]
    assert "kosatsuba_by_the_road" not in f_only({"meta": {"scale": "town"}, "kosatsuba": [_kosatsuba(500, 530)], "road": road}, "kosatsuba_by_the_road")
    assert "kosatsuba_by_the_road" in f_only({"meta": {"scale": "city", "ftpx": 3}, "kosatsuba": [_kosatsuba(500, 530)], "road": road}, "kosatsuba_by_the_road")
    ok = f({"meta": {"scale": "city", "ftpx": 3}, "kosatsuba": [_kosatsuba(500, 515)], "road": road})
    assert "kosatsuba_by_the_road" not in ok and "city_has_kosatsuba" not in ok
