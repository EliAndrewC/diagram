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
    hemmed = hg.seat_cluster(plan, dry_plots=[hem])
    assert hemmed["cy"] > hg.seat_cluster(plan)["cy"]
    # ...and with the one wind-facing margin gone, the seat is the last fallback and says so (feature 261)
    assert hemmed["offwind"] is True and hg.seat_cluster(plan)["offwind"] is False


@pytest.mark.parametrize("windward", sorted(hg.WIND_VECTORS))
@pytest.mark.parametrize("down_deg", [0.0, 90.0, 180.0, 270.0])
def test_the_seat_turns_its_back_to_the_wind_whatever_the_slope(windward: str, down_deg: float) -> None:
    """THE SEAT BENDS TO THE WIND (feature 261): whichever way the land falls, the settlement's back - the seat's
    outward normal - faces within 45 degrees of the windward bearing, so the belt behind it stands on the
    windward side instead of in the crop. Before feature 261 the wind was renamed after the seat instead."""
    spec = hg.HamletSpec(name="Test", seed=3, households=10, down_deg=down_deg, windward=windward)
    plan = hg.plan_site(spec)
    plan.envelope = [(400.0, 400.0), (700.0, 250.0), (1000.0, 400.0), (1150.0, 700.0), (1000.0, 1000.0), (700.0, 1150.0), (400.0, 1000.0), (250.0, 700.0)]
    seat = hg.seat_cluster(plan)
    wx, wy = plan.wind
    assert seat["out"][0] * wx + seat["out"][1] * wy >= hg.WIND_BACK_MIN_DOT
    assert seat["offwind"] is False


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


def test_a_margin_the_brook_runs_through_is_scored_not_struck_out() -> None:
    """Feature 261 (the GM 2026-09-27: "fix the placement algorithm instead"): a band the brook runs through was struck
    out only because no way could cross the brook; ways cross it at a ford now, so the seat keeps its wind-facing
    margin and the brook costs only the score of the sample points standing on the water."""
    plan = a_plan()
    plain = hg.seat_cluster(plan)
    ax, ay = plain["along"]
    brook = [(plain["cx"] - ax * 900.0, plain["cy"] - ay * 900.0), (plain["cx"] + ax * 900.0, plain["cy"] + ay * 900.0)]
    moved = hg.seat_cluster(plan, brook=brook)
    assert moved["offwind"] is False, "the one wind-facing margin still seats the hamlet"
    assert "divided" not in moved


def test_a_brook_across_every_margin_still_seats_the_hamlet_facing_the_wind() -> None:
    plan = a_plan()
    brook = [(-1300.0, 700.0), (2700.0, 700.0), (700.0, 700.0), (700.0, -1300.0), (700.0, 2700.0)]
    seat = hg.seat_cluster(plan, brook=brook)
    assert not hg.point_in_poly(seat["cx"], seat["cy"], SQUARE), "outside the field"
    assert seat["offwind"] is False
