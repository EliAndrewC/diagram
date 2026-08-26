"""Split from test_checks.py by feature 025 - see tests/check_village/CLAUDE.md for the index."""

from l7r.diagram import check_village


def test_poly_gap_overlap_containment_edgecross_and_separated():
    # poly_gap: 0 when one contains the other, 0 when edges CROSS with no vertex inside, else the min distance.
    sq = [[0, 0], [10, 0], [10, 10], [0, 10]]
    assert check_village.poly_gap(sq, [[3, 3], [5, 3], [5, 5], [3, 5]]) == 0.0  # containment
    bar1 = [[0, 4], [10, 4], [10, 6], [0, 6]]  # a + cross: edges cross,
    bar2 = [[4, 0], [6, 0], [6, 10], [4, 10]]  # no vertex inside the other
    assert check_village.poly_gap(bar1, bar2) == 0.0
    assert check_village.poly_gap(sq, [[20, 0], [30, 0], [30, 10], [20, 10]]) == 10.0  # separated by 10


def test_clip_and_onmap_edge_handle_a_fully_offmap_field():
    # a field lying entirely outside the map rect clips to nothing and contributes no on-map edge
    poly = [[-500, -500], [-300, -500], [-300, -300], [-500, -300]]
    assert check_village.clip_poly_rect(poly, 0, 0, 1000, 1000) == []
    assert check_village.onmap_field_edge(poly, 0, 0, 1000, 1000) == 0.0


def test_water_setback_scales_with_waterway_width():
    assert check_village.water_setback(4) == 75  # any small open water -> the floor (graves flood out)
    assert check_village.water_setback(9) == 75  # a narrow stream still gets the full floor
    assert check_village.water_setback(22) == 110  # moat -> moderate/large
    assert check_village.water_setback(40) == 140  # river / canal -> capped
    assert check_village.water_setback(9) < check_village.water_setback(22)  # wider water, more set-back
