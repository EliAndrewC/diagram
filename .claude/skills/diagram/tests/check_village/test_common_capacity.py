"""Split from test_checks.py by feature 025 - see tests/check_village/CLAUDE.md for the index."""


# ---- feature 006: reworked capacity verdict (usable residential ground + reserve) ------------


def test_poly_area_is_the_shoelace_and_ignores_winding() -> None:
    from l7r.diagram.check_village.common_03_capacity import _poly_area

    square = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
    assert abs(_poly_area(square) - 100.0) < 1e-9
    assert abs(_poly_area(list(reversed(square))) - 100.0) < 1e-9  # winding does not change an area
    assert _poly_area([(0.0, 0.0), (5.0, 5.0)]) == 0.0
