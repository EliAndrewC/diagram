"""The drain-bank hem as one array computation (feature 297, FR-007): every vertex's verdict is the scalar predicate's."""

import math
import random

from l7r.diagram.waterfields.banks import drain_bank_clearance, drain_bank_clearance_many, hem_rings_to_bank, hem_to_bank, polyline_cum


def test_the_array_verdict_is_the_scalar_verdict_per_vertex():
    rng = random.Random(11)
    for _ in range(40):
        n = rng.randint(2, 9)
        drain = [(100.0 + 60.0 * k + rng.uniform(-15, 15), 300.0 + rng.uniform(-40, 40)) for k in range(n)]
        if rng.random() < 0.2:
            drain.insert(1, drain[0])  # a zero-length segment
        down = rng.uniform(0, 360)
        dv = (math.cos(math.radians(down)), math.sin(math.radians(down)))
        cum = polyline_cum(drain)
        ring = [(rng.uniform(40, 700), rng.uniform(200, 400)) for _ in range(rng.randint(3, 12))]
        g, need, lean, past = drain_bank_clearance_many(ring, drain, dv, 2.0, 7.0, cum)
        for k, q in enumerate(ring):
            sg, sn, sl, sp = drain_bank_clearance(q, drain, dv, 2.0, 7.0, cum)
            assert math.isclose(g[k], sg, abs_tol=1e-9) and math.isclose(need[k], sn, abs_tol=1e-9)
            assert math.isclose(lean[k], sl, abs_tol=1e-9) and past[k] == sp


def test_the_hem_lifts_a_vertex_in_the_drain_and_keeps_the_rest():
    drain = [(0.0, 100.0), (400.0, 100.0)]
    ring = [(50.0, 20.0), (150.0, 20.0), (150.0, 101.0), (50.0, 101.0)]
    out = hem_to_bank(ring, drain, 90.0, 4.0, 4.0)  # the fall runs +y, toward the drain
    assert out[:2] == ring[:2]
    assert out[2][1] < 100.0 - 2.0 and out[3][1] < 100.0 - 2.0
    assert hem_to_bank([], drain, 90.0, 4.0, 4.0) == []
    other = [(200.0, 40.0), (260.0, 40.0), (260.0, 104.0)]
    assert hem_rings_to_bank([ring, other], drain, 90.0, 4.0, 4.0) == [out, hem_to_bank(other, drain, 90.0, 4.0, 4.0)], "every ring at once, as one at a time"
    assert hem_rings_to_bank([ring], [(0.0, 0.0)], 90.0, 4.0, 4.0) == [ring] and hem_rings_to_bank([], drain, 90.0, 4.0, 4.0) == []


def test_a_vertex_in_a_drain_running_with_the_fall_steps_off_at_right_angles() -> None:
    """Feature 328 wave 79 (0055: a bund abuts the ditch and never stands in its water): lifting up the fall buys nothing
    against a collector running WITH the fall, which used to leave such a vertex in the water. It now steps off at right
    angles onto its own side's bank, the scalar and the array walk alike; a vertex already clear is not moved."""
    from l7r.diagram.waterfields.banks import BANK_MARGIN, hem_rings_to_bank, hem_to_bank, off_with_the_fall

    drain = [(100.0, 0.0), (100.0, 400.0)]  # straight down the fall (down_deg 90: the fall is +y)
    need = 6.0 / 2 + BANK_MARGIN
    ring = [(101.0, 200.0), (98.0, 210.0), (150.0, 220.0)]
    moved = hem_to_bank(ring, drain, 90.0, 6.0, 6.0)
    assert moved == [(round(100.0 + need, 1), 200.0), (round(100.0 - need, 1), 210.0), (150.0, 220.0)]
    assert hem_rings_to_bank([ring], drain, 90.0, 6.0, 6.0) == [moved], "the array walk agrees with the scalar"
    assert off_with_the_fall((100.0, 50.0), drain, 0.0, need) == (round(100.0 - need, 1), 50.0), "on the line: the segment's left (-x for a segment running +y)"


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
