"""The drain-bank hem as one array computation (feature 297, FR-007): every vertex's verdict is the scalar predicate's."""

import math


def test_a_swept_bend_is_a_circular_arc_of_its_radius_cut_back_by_the_turn() -> None:
    """Feature 328 wave 80 (0054: a bend of about 2.5 channel widths' radius, capped at 35% of each run): the cut-back is
    radius * tan(turn / 2) - the radius at a right angle, far less at a gentle turn - and every point of the arc stands one
    radius from its center; a cap tightens the radius rather than flattening the curve."""
    from l7r.diagram.waterfields.banks import swept_bend

    P = (100.0, 100.0)
    arc = swept_bend(P, (-1.0, 0.0), (0.0, 1.0), math.pi / 2, 10.0, 1e9, 6)  # in from the west, out to the south: a right angle
    assert arc[0] == (90.0, 100.0) and arc[-1] == (100.0, 110.0), "tangent points one radius back along each run"
    assert all(abs(math.dist(q, (90.0, 110.0)) - 10.0) < 0.15 for q in arc), "every point one radius from the center"
    turn20 = math.radians(160.0)  # a 20-degree turn: the runs meet at 160 degrees
    gentle = swept_bend(P, (-1.0, 0.0), (math.cos(math.radians(20.0)), math.sin(math.radians(20.0))), turn20, 10.0, 1e9, 6)
    assert abs(math.dist(gentle[0], P) - 10.0 * math.tan(math.radians(10.0))) < 0.1, "a gentle turn cuts back ~1.8, not 10"
    capped = swept_bend(P, (-1.0, 0.0), (0.0, 1.0), math.pi / 2, 10.0, 4.0 / 0.35, 6)  # a run of 11.4: radius capped at 4
    assert capped[0] == (96.0, 100.0) and all(abs(math.dist(q, (96.0, 104.0)) - 4.0) < 0.15 for q in capped), "the RADIUS is capped at 35% of the run"
    shallow = swept_bend(P, (-1.0, 0.0), (math.cos(math.radians(20.0)), math.sin(math.radians(20.0))), turn20, 10.0, 10.0, 6)
    assert abs(math.dist(shallow[0], P) - 3.5 * math.tan(math.radians(10.0))) < 0.1, "a shallow turn on a 10 ft run: radius 3.5, not 10"
    sharp = swept_bend(P, (-1.0, 0.0), (-math.cos(math.radians(20.0)), math.sin(math.radians(20.0))), math.radians(20.0), 10.0, 10.0, 6)
    assert math.dist(sharp[0], P) <= 9.0 + 0.1, "a hairpin's cut-back stays within its run"
