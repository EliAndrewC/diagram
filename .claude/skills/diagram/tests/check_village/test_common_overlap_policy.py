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


def test_polyline_len_and_in_ellipse() -> None:
    """Feature 146: the two small shared measures - a polyline's run, and a point inside a scaled ellipse."""
    from l7r.diagram.check_village.common_02_overlap_policy import in_ellipse, polyline_len

    assert abs(polyline_len([(0.0, 0.0), (3.0, 4.0), (3.0, 14.0)]) - 15.0) < 1e-9
    assert polyline_len([(1.0, 1.0)]) == 0.0
    e = (100.0, 100.0, 40.0, 20.0)
    assert in_ellipse(100.0, 100.0, e) is True
    assert in_ellipse(145.0, 100.0, e) is False
    assert in_ellipse(145.0, 100.0, e, scale=1.2) is True  # the scaled rim admits it


def test_forest_reveal_x_with_and_without_a_recorded_tree_line() -> None:
    """Feature 146: the frame reveals a shallow band of a canvas-filling wood - the tree line plus `reveal`
    px of canopy behind it. With no recorded tree line the whole clamped polygon sets the frame, as before."""
    from l7r.diagram.check_village.common_02_overlap_policy import forest_reveal_x

    forest = [(-40.0, 0.0), (500.0, 0.0), (500.0, 300.0)]
    assert forest_reveal_x(forest, w=400, edge=None, reveal=30) == [0, 400, 400]  # clamped, no tree line
    assert forest_reveal_x(forest, w=400, edge=[(-5.0, 0.0), (380.0, 0.0)], reveal=30) == [0, 380, 30, 400]


def test_matrix_violations_skips_a_box_wholly_off_the_canvas() -> None:
    """Feature 146: a feature whose clearance box lies wholly off the canvas can meet nothing on the map, so
    the overlap sweep skips it on both sides of the pair loop rather than measuring against it."""
    from l7r.diagram.check_village.common_02_overlap_policy import matrix_violations

    M = {
        "meta": {"scale": "hamlet", "ftpx": 1, "W": 1000, "H": 1000},
        "houses": [{"x": 500.0, "y": 500.0, "w": 50.0, "h": 30.0, "rot": 0}, {"x": -9000.0, "y": -9000.0, "w": 50.0, "h": 30.0, "rot": 0}],
    }
    out = matrix_violations(M)
    assert isinstance(out, list)
    assert not any("-9000" in str(v) for v in out), "the off-canvas house is not paired with anything"
