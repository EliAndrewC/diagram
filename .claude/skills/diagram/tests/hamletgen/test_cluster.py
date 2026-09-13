"""Unit tests for seating the settlement on the margin (`hamletgen/cluster.py`).

Split from test_hamletgen.py by feature 111; test bodies verbatim. See hamletgen/CLAUDE.md.
"""

import pytest

from l7r.diagram import hamletgen as hg

from ._builders import SQUARE, a_plan


def test_a_point_below_the_drain_is_recognized_as_wet_ground() -> None:
    drain = [(0.0, 1000.0), (2000.0, 1000.0)]  # runs east-west across a south-falling map
    assert hg.below_drain((1000.0, 1080.0), drain, 0.0, 1.0)  # downslope of it, in the toe band
    assert not hg.below_drain((1000.0, 900.0), drain, 0.0, 1.0)  # above it
    assert not hg.below_drain((1000.0, 1400.0), drain, 0.0, 1.0)  # past the toe band entirely


def test_ground_behind_a_margin_reports_how_much_of_it_is_crop() -> None:
    assert hg.back_fouled((700.0, 400.0), (0.0, -1.0), 100.0, []) == 0.0
    fouled = hg.back_fouled((700.0, 1000.0), (0.0, -1.0), 100.0, [SQUARE])  # normal points back INTO the square
    assert fouled > 0.5


def test_the_cluster_is_seated_outside_the_field() -> None:
    plan = a_plan()
    seat = hg.seat_cluster(plan)
    assert not hg.point_in_poly(seat["cx"], seat["cy"], SQUARE)
    assert seat["lat"] > 0 and seat["dep"] > 0


def test_the_cluster_is_never_seated_below_the_drain() -> None:
    """The wet toe is not building ground. Excluded outright rather than scored down, because a
    strong enough wind score will otherwise pull the settlement into the bog."""
    plan = a_plan()
    drain = [(300.0, 1000.0), (1100.0, 1000.0)]  # along the square's low (south) edge
    seat = hg.seat_cluster(plan, drain=drain)
    assert seat["cy"] < 1000.0


def test_a_margin_below_the_drain_is_excluded_outright() -> None:
    """HARD 1's own `continue`: a drain drawn INSIDE the low half puts the square's south margin
    genuinely on the wet side (mid 100 px past the line, within the 150 px toe band), so the seat
    scan must skip that margin - not merely score it down. (The sibling drain-along-the-edge test
    asserts the RESULT; the 2026-08-16 re-rolls left this branch reached by no pool map, and a
    branch no test reaches is the coverage form of the check that never runs.)"""
    plan = a_plan()
    drain = [(300.0, 900.0), (1100.0, 900.0)]
    seat = hg.seat_cluster(plan, drain=drain)
    assert seat["cy"] < 900.0


def test_the_cluster_avoids_a_margin_whose_back_is_under_the_hem() -> None:
    """A margin hemmed by dry crop is not a worse seat, it is not a seat: the cluster's own band and
    the windbreak behind it would stand in the barley."""
    plan = a_plan()
    hem = [(400.0, 100.0), (1000.0, 100.0), (1000.0, 395.0), (400.0, 395.0)]  # the whole north back
    assert hg.seat_cluster(plan, dry_plots=[hem])["cy"] > hg.seat_cluster(plan)["cy"]


def test_a_field_with_no_buildable_flank_is_a_loud_error() -> None:
    plan = a_plan()
    boxed = [[(200.0, 200.0), (1200.0, 200.0), (1200.0, 1200.0), (200.0, 1200.0)]]  # crop on every side
    with pytest.raises(ValueError, match="no buildable flank"):
        hg.seat_cluster(plan, dry_plots=boxed)


def test_arm_crossing_accidental_drops_an_open_ground_X_and_keeps_a_designed_one():
    # kept arm: a horizontal run. Candidate: crosses it mid-run at (50, 0).
    kept_arm = [(0.0, 0.0), (100.0, 0.0)]
    crossing = [(50.0, -40.0), (50.0, 40.0)]
    # raw pair never crossed (a Y's arms share only their hub) -> the clipped X is ACCIDENTAL
    raw_no_cross = [(200.0, -40.0), (200.0, 40.0)]
    assert hg._arm_crossing_accidental(crossing, raw_no_cross, [(kept_arm, kept_arm)])
    # raw pair crossed at the same spot (the 'cross' skeleton's bar over its spine) -> DESIGNED
    assert not hg._arm_crossing_accidental(crossing, crossing, [(kept_arm, kept_arm)])
    # raw pair crossed but 200 px away -> still accidental (location-aware, not existence)
    far_raw = [(250.0, -40.0), (250.0, 40.0)]
    far_kept_raw = [(200.0, 0.0), (300.0, 0.0)]
    assert hg._arm_crossing_accidental(crossing, far_raw, [(kept_arm, far_kept_raw)])
    # no crossing at all -> kept
    assert not hg._arm_crossing_accidental([(0.0, 10.0), (100.0, 10.0)], raw_no_cross, [(kept_arm, kept_arm)])


def test_fork_spur_truncates_at_the_lane_and_survives_degenerate_input():
    arm = [(0.0, 0.0), (100.0, 0.0)]
    # a spur starting on the far side of the arm gets truncated to fork AT the crossing
    spur = [(50.0, -30.0), (50.0, 60.0)]
    out = hg._fork_spur(spur, [(arm, arm)])
    assert abs(out[0][0] - 50.0) < 0.1 and abs(out[0][1]) < 0.1, out
    assert out[-1] == (50.0, 60.0)
    # a spur already forking from the arm is untouched
    clean = [(50.0, 0.0), (50.0, 60.0)]
    assert hg._fork_spur(clean, [(arm, arm)]) == clean
    # degenerate input passes through the bounded loop's guard unharmed
    assert hg._fork_spur([(1.0, 2.0)], [(arm, arm)]) == [(1.0, 2.0)]


def test_a_seat_centered_in_the_reed_fringe_is_refused_and_one_with_an_end_in_it_is_scored_down() -> None:
    """Feature 150 T50 (GM 2026-08-28): the reservoir's reed fringe is drawn before the seat is chosen but
    was never scored, so a cluster could be seated with one end in the reeds - the house placer then
    refused those seats and re-seated the displaced houses at the cluster's far ends, out of the web's
    reach (Kuwabata seed 21). Wet ground is scored like the dry-plot foul; a seat CENTERED in it is refused."""
    plan = a_plan()
    dry = hg.seat_cluster(plan)
    north = [(300.0, 200.0), (1100.0, 200.0), (1100.0, 395.0), (300.0, 395.0)]  # the whole north margin band
    wet = hg.seat_cluster(plan, wet=[north])
    assert not hg.point_in_poly(wet["cx"], wet["cy"], north), "the seat left the reeds"
    assert (wet["cx"], wet["cy"]) != (dry["cx"], dry["cy"])
    corner = [(300.0, 200.0), (520.0, 200.0), (520.0, 395.0), (300.0, 395.0)]  # only the band's west end
    scored = hg.seat_cluster(plan, wet=[corner])
    assert scored["dep"] > 0  # a seat is still found; the foul is a score, not a refusal


def test_a_margin_the_brook_divides_is_struck_out_and_the_strike_is_counted() -> None:
    """Feature 230: the brook runs past the fan now, so a margin can have a stream down the middle of it -
    and a cluster seated there stands in two halves with no crossing between them. The margin is struck
    out rather than scored down, and the roll COUNTS the strike, because `generate` has to know the brook
    steered this seat before it can judge whether that cost the map a household."""
    plan = a_plan()
    plain = hg.seat_cluster(plan)
    assert plan.seat_brook_steered == 0, "no brook, no steer"
    # a brook down the middle of the band the seater just chose, running across it
    ax, ay = plain["along"]
    brook = [(plain["cx"] - ax * 900.0, plain["cy"] - ay * 900.0), (plain["cx"] + ax * 900.0, plain["cy"] + ay * 900.0)]
    moved = hg.seat_cluster(plan, brook=brook)
    assert plan.seat_brook_steered > 0, "the brook had a say and the roll records it"
    assert (moved["cx"], moved["cy"]) != (plain["cx"], plain["cy"]), "the divided margin is not the seat"
    assert moved["divided"] is False, "and the one it took is not divided either"


def test_the_brook_has_no_say_in_the_seat_when_the_map_came_up_short() -> None:
    """Feature 230, the other half: the ground the brook rules out is ground the houses had, so when a roll
    seats fewer households than declared `generate` rolls again with `seat_ignores_brook` set. Then the
    penalty and the strike-out are both off and the seat is exactly the one a brook-free map would take -
    which is what makes the second roll worth trying at all."""
    plan = a_plan()
    plain = hg.seat_cluster(plan)
    ax, ay = plain["along"]
    brook = [(plain["cx"] - ax * 900.0, plain["cy"] - ay * 900.0), (plain["cx"] + ax * 900.0, plain["cy"] + ay * 900.0)]
    plan.seat_ignores_brook = True
    plan.seat_brook_steered = 0
    ignored = hg.seat_cluster(plan, brook=brook)
    assert plan.seat_brook_steered == 0, "the brook is not consulted, so nothing is counted"
    assert (ignored["cx"], ignored["cy"]) == (plain["cx"], plain["cy"])


def test_every_margin_divided_still_seats_the_hamlet() -> None:
    """A brook that divides every margin must not raise: the scored form decides among them, and the seat
    reports that it stands on one (`meta.seat_divided` carries it onto the map)."""
    plan = a_plan()
    # a course that runs out through all four margins and back - one polyline, drawn as a cross
    brook = [(-1300.0, 700.0), (2700.0, 700.0), (700.0, 700.0), (700.0, -1300.0), (700.0, 2700.0)]
    seat = hg.seat_cluster(plan, brook=brook)
    assert seat["divided"] is True
    assert not hg.point_in_poly(seat["cx"], seat["cy"], SQUARE), "still outside the field"
