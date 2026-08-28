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
