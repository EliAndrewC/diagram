"""Split from test_checks.py by feature 025 - see tests/check_village/CLAUDE.md for the index."""

from tests.check_village._builders import (
    _agri_city,
    _fort_city,
    _mest_city,
    _ring_towers,
    f,
    f_only,
)


def test_city_interior_fields_farmhouse_density_fires_when_under_farmed():
    # a real in-wall field with a single token farmhouse beside it - far below village density
    M = _agri_city([{"x": 360, "y": 320, "w": 18, "h": 12, "rot": 0}])
    assert "city_interior_fields_farmhouse_density" in f_only(M, "city_interior_fields_farmhouse_density")


def test_wall_towers_evenly_spaced_fires_on_a_doubled_tower():
    # a remediation-style tower squeezed 40px from its 100px-rhythm neighbor (the Tango east-curtain artifact)
    tw = _ring_towers(100) + [{"x": 240, "y": 200}]
    assert "wall_towers_evenly_spaced" in f_only(_fort_city(wall_towers=tw), "wall_towers_evenly_spaced")


def test_wall_towers_evenly_spaced_passes_on_an_even_ring():
    assert "wall_towers_evenly_spaced" not in f_only(_fort_city(wall_towers=_ring_towers(100)), "wall_towers_evenly_spaced")


def test_merchant_estate_wall_fires_on_a_dock_overlap():
    # dock basin footprint under the estate's east wall (the shipped-Nagahara defect)
    assert "merchant_estate_wall_clear_of_water" in f_only(_mest_city(docks=[{"x": 540, "y": 490, "w": 54, "h": 34, "rot": 0}]), "merchant_estate_wall_clear_of_water")


def test_merchant_estate_wall_fires_on_a_canal_crossing():
    # canal centerline passes through the north wall
    assert "merchant_estate_wall_clear_of_water" in f_only(_mest_city(canals=[{"poly": [[400, 477], [600, 477]], "w": 12.0}]), "merchant_estate_wall_clear_of_water")


def test_merchant_estate_wall_fires_on_a_pond_and_a_moat():
    assert "merchant_estate_wall_clear_of_water" in f_only(_mest_city(pond=[469, 500, 20, 14]), "merchant_estate_wall_clear_of_water")  # pond ellipse reaching the west wall
    assert "merchant_estate_wall_clear_of_water" in f_only(_mest_city(moat=[[531, 400], [531, 600]], moat_width=22.0), "merchant_estate_wall_clear_of_water")  # moat band over the east wall


def test_merchant_estate_wall_passes_with_water_at_a_distance():
    clear = _mest_city(
        docks=[{"x": 620, "y": 490, "w": 54, "h": 34, "rot": 0}],
        canals=[{"poly": [[400, 440], [600, 440]], "w": 12.0}],
        pond=[420, 500, 20, 14],
    )
    assert "merchant_estate_wall_clear_of_water" not in f_only(clear, "merchant_estate_wall_clear_of_water")


def test_merchant_estate_wall_fires_on_a_fire_tower_and_passes_when_clear():
    # tower footprint straddling the south wall (the shipped-Nagahara defect)
    on_wall = _mest_city(fire_towers=[{"x": 490, "y": 523, "w": 8.7, "h": 8.7, "rot": 0}])
    assert "merchant_estate_wall_clear_of_fire_towers" in f_only(on_wall, "merchant_estate_wall_clear_of_fire_towers")
    clear = _mest_city(fire_towers=[{"x": 490, "y": 545, "w": 8.7, "h": 8.7, "rot": 0}])
    assert "merchant_estate_wall_clear_of_fire_towers" not in f_only(clear, "merchant_estate_wall_clear_of_fire_towers")


def test_merchant_estate_fires_when_a_fire_tower_is_enclosed_in_the_court():
    # wall-line clear but the municipal tower trapped INSIDE the private court - same siting error
    inside = _mest_city(fire_towers=[{"x": 500, "y": 505, "w": 8.7, "h": 8.7, "rot": 0}])
    assert "merchant_estate_wall_clear_of_fire_towers" in f_only(inside, "merchant_estate_wall_clear_of_fire_towers")


def test_city_fan_heads_quilted_moat_exclusion_and_degenerate_segments():
    """Branch coverage for the head-band sampler: a duplicated main vertex (zero-length segment)
    is skipped, and flank samples inside the moat corridor are excluded rather than counted bare
    (the moat legitimately borders a city fan's head where the sluice taps it)."""
    M = {
        "meta": {"scale": "village", "ftpx": 2},
        "moat": [[100, -50], [100, 450]],
        "moat_width": 30,
        "fields": [{"name": "t", "kind": "paddy", "outline": [[0, 0], [400, 0], [400, 400], [0, 400]], "bbox": [0, 0, 400, 400], "plot_polys": [[[60, 0], [400, 0], [400, 400], [60, 400]]]}],
        "field_ditches": [{"field": "t", "poly": [[112, 0], [112, 200], [112, 200], [112, 400]], "w": 6, "role": "main"}],
    }
    f(M)  # execution is the point: west flank samples sit in the moat corridor, the duplicate vertex is skipped
