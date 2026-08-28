"""tier town tests split out of `tests.check_village.test_segments_10_city_battery_a` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    _fort_city,
    _well_city,
    f_only,
)


@pytest.mark.tiers("town")
def test_kido_aligned_squares_to_the_lane_it_bars_not_the_oblique_fence_it_hangs_in():
    # GM 2026-07-26: a kido shuts a WAY, so where a lane runs through the seat the bar stands
    # SQUARE ACROSS THE LANE, and the fence meets it at whatever angle the fence runs. Tango's SW
    # ring-road gate followed its ~44deg fence jog while the road it barred ran at ~172deg - 38deg
    # off square to its own roadbed. Here: a 45deg fence, a HORIZONTAL street through the gate, so
    # the bar wants 90deg (vertical, across the street), NOT the fence's 45.
    ward = [{"name": "w", "boundary": [[300, 300], [600, 600]], "z": 1, "wall_caps": []}]
    street = [{"pts": [[300, 450], [600, 450]], "w": 18}]
    fenced = _fort_city(wards=ward, town_streets=street, kido=[{"x": 450, "y": 450, "rot": 45.0, "bbox": [430, 430, 470, 470]}])
    assert "kido_aligned_with_ward_fence" in f_only(fenced, "kido_aligned_with_ward_fence")  # square to the FENCE is now the defect, because a lane runs through
    squared = _fort_city(wards=ward, town_streets=street, kido=[{"x": 450, "y": 450, "rot": 90.0, "bbox": [430, 430, 470, 470]}])
    assert "kido_aligned_with_ward_fence" not in f_only(squared, "kido_aligned_with_ward_fence")
    # a street laid ALONGSIDE the fence is not something the gate bars, so it must not be what the
    # gate squares to - the fence tangent still rules there
    along = _fort_city(wards=ward, town_streets=[{"pts": [[300, 290], [600, 590]], "w": 18}], kido=[{"x": 450, "y": 450, "rot": 45.0, "bbox": [430, 430, 470, 470]}])
    assert "kido_aligned_with_ward_fence" not in f_only(along, "kido_aligned_with_ward_fence")


@pytest.mark.tiers("city", "town")
def test_city_wells_in_block_interiors_fires_on_a_lane():
    M = _well_city(town_streets=[{"pts": [[400, 500], [600, 500]], "w": 18}])
    assert "city_wells_in_block_interiors" in f_only(M, "city_wells_in_block_interiors")
