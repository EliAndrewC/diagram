"""Unit tests for seating the settlement on the margin (`hamletgen/cluster.py`).

Split from test_hamletgen.py by feature 111; test bodies verbatim. See hamletgen/CLAUDE.md.
"""

import math

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen.cluster import BELT_ROOM_MAX_OFF, SeatRefused, belt_off_canvas
from l7r.diagram.hamletgen.consts import CLUSTER_SHAPES, FALL_BEARINGS
from l7r.diagram.hamletgen.plan import BELT_REACH, FAN_OVERHANG, SEAT_STANDOFF, band_extent, fall_backs_the_wind, seat_room

from ._builders import CROWN, SQUARE, a_plan

D = 300.0  # the square moved this far in from the canvas's top and left for a seat test
SEATED = [(x + D, y + D) for x, y in SQUARE]


def a_seat_plan() -> hg.SitePlan:
    """`a_plan` with its square moved `D` in from the canvas's top and left: `seat_cluster` holds the seat center a whole
    band half-length (`lat`) inside the frame (feature 328), and at 400 px `SQUARE`'s north seat stood nearer the top."""
    plan = a_plan()
    plan.envelope = list(SEATED)
    _dep, lat = band_extent(plan.spec.households, plan.cluster_shape)
    assert lat <= SEATED[0][1] - _dep - SEAT_STANDOFF, "the fixture's premise: the north band fits on the canvas"
    return plan


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
    plan = a_seat_plan()
    seat = hg.seat_cluster(plan)
    assert not hg.point_in_poly(seat["cx"], seat["cy"], SEATED)
    assert seat["lat"] > 0 and seat["dep"] > 0


def test_the_cluster_is_never_seated_below_the_drain() -> None:
    """The wet toe is not building ground. Excluded outright rather than scored down, because a
    strong enough wind score will otherwise pull the settlement into the bog."""
    plan = a_seat_plan()
    drain = [(300.0 + D, 1000.0 + D), (1100.0 + D, 1000.0 + D)]  # along the square's low (south) edge
    seat = hg.seat_cluster(plan, drain=drain)
    assert seat["cy"] < 1000.0 + D


def test_a_margin_below_the_drain_is_excluded_outright() -> None:
    """HARD 1's own `continue`: a drain drawn INSIDE the low half puts the square's south margin
    genuinely on the wet side (mid 100 px past the line, within the 150 px toe band), so the seat
    scan must skip that margin - not merely score it down. (The sibling drain-along-the-edge test
    asserts the RESULT; the 2026-08-16 re-rolls left this branch reached by no pool map, and a
    branch no test reaches is the coverage form of the check that never runs.)"""
    plan = a_seat_plan()
    drain = [(300.0 + D, 900.0 + D), (1100.0 + D, 900.0 + D)]
    seat = hg.seat_cluster(plan, drain=drain)
    assert seat["cy"] < 900.0 + D


def test_the_cluster_avoids_a_margin_whose_back_is_under_the_hem() -> None:
    """A margin hemmed by dry crop is not a worse seat, it is not a seat: the cluster's own band and
    the windbreak behind it would stand in the barley."""
    plan = a_seat_plan()
    hem = [(x + D, y + D) for x, y in [(400.0, 100.0), (1000.0, 100.0), (1000.0, 395.0), (400.0, 395.0)]]  # the whole north back
    assert hg.seat_cluster(plan)["offwind"] is False
    # ...and with the one wind-facing margin gone the site is REFUSED, naming it - never seated off the wind (feature 287,
    # homes H30: the off-wind fallback feature 261 kept is gone)
    with pytest.raises(SeatRefused, match="Test .seed 3.: no field margin turns its back to the N wind"):
        hg.seat_cluster(plan, dry_plots=[hem])


@pytest.mark.parametrize("windward", sorted(hg.WIND_VECTORS))
@pytest.mark.parametrize("down_deg", [0.0, 90.0, 180.0, 270.0])
def test_the_seat_turns_its_back_to_the_wind_whatever_the_slope(windward: str, down_deg: float) -> None:
    """THE SEAT BENDS TO THE WIND (feature 261): whichever way the land falls, the settlement's back - the seat's
    outward normal - faces within 45 degrees of the windward bearing, so the belt behind it stands on the
    windward side instead of in the crop. Before feature 261 the wind was renamed after the seat instead."""
    spec = hg.HamletSpec(name="Test", seed=3, households=10, down_deg=down_deg, windward=windward)
    plan = hg.plan_site(spec)
    d = plan.W / 2.0 - 700.0  # the field in the canvas middle, where `head_sluice` lays it (the canvas holds the seat's room round it)
    plan.envelope = [(x + d, y + d) for x, y in [(400.0, 400.0), (700.0, 250.0), (1000.0, 400.0), (1150.0, 700.0), (1000.0, 1000.0), (700.0, 1150.0), (400.0, 1000.0), (250.0, 700.0)]]
    seat = hg.seat_cluster(plan)
    wx, wy = plan.wind
    assert seat["out"][0] * wx + seat["out"][1] * wy >= hg.WIND_BACK_MIN_DOT
    assert seat["offwind"] is False


def test_a_field_with_no_buildable_flank_is_a_loud_error() -> None:
    plan = a_plan()
    boxed = [[(200.0, 200.0), (1200.0, 200.0), (1200.0, 1200.0), (200.0, 1200.0)]]  # crop on every side
    with pytest.raises(SeatRefused, match="the site has no seat"):
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
    plan.envelope = list(CROWN)
    dry = hg.seat_cluster(plan)
    top = [(500.0, 450.0), (900.0, 450.0), (900.0, 715.0), (500.0, 715.0)]  # round the crown's top seat
    wet = hg.seat_cluster(plan, wet=[top])
    assert not hg.point_in_poly(wet["cx"], wet["cy"], top), "the seat left the reeds"
    assert (wet["cx"], wet["cy"]) != (dry["cx"], dry["cy"])
    corner = [(300.0, 500.0), (620.0, 500.0), (620.0, 715.0), (300.0, 715.0)]  # only the top band's west end
    scored = hg.seat_cluster(plan, wet=[corner])
    assert scored["dep"] > 0  # a seat is still found; the foul is a score, not a refusal


def test_a_margin_the_brook_runs_through_is_scored_not_struck_out() -> None:
    """Feature 261 (the GM 2026-09-27: "fix the placement algorithm instead"): a band the brook runs through was struck
    out only because no way could cross the brook; ways cross it at a ford now, so the seat keeps its wind-facing
    margin and the brook costs only the score of the sample points standing on the water."""
    plan = a_seat_plan()
    plain = hg.seat_cluster(plan)
    ax, ay = plain["along"]
    brook = [(plain["cx"] - ax * 900.0, plain["cy"] - ay * 900.0), (plain["cx"] + ax * 900.0, plain["cy"] + ay * 900.0)]
    moved = hg.seat_cluster(plan, brook=brook)
    assert moved["offwind"] is False, "the one wind-facing margin still seats the hamlet"
    assert "divided" not in moved


def test_a_brook_across_every_margin_still_seats_the_hamlet_facing_the_wind() -> None:
    plan = a_seat_plan()
    brook = [(x + D, y + D) for x, y in [(-1300.0, 700.0), (2700.0, 700.0), (700.0, 700.0), (700.0, -1300.0), (700.0, 2700.0)]]
    seat = hg.seat_cluster(plan, brook=brook)
    assert not hg.point_in_poly(seat["cx"], seat["cy"], SEATED), "outside the field"
    assert seat["offwind"] is False


def test_a_seat_whose_belt_would_fall_off_the_canvas_is_measured() -> None:
    """Feature 261 (settlement-review of Mizuguchi): the share of the windbreak's band behind a seat that the canvas
    cannot hold."""
    from l7r.diagram.hamletgen.cluster import belt_off_canvas

    inside = belt_off_canvas((1300.0, 1300.0), (0.0, 1.0), (-1.0, 0.0), 300.0, 150.0, (-1.0, 0.0), 2600.0, 2600.0)
    at_edge = belt_off_canvas((120.0, 1300.0), (0.0, 1.0), (-1.0, 0.0), 300.0, 150.0, (-1.0, 0.0), 2600.0, 2600.0)
    assert inside == 0.0 and at_edge == 1.0


# ---- the seat's back to the wind, by construction (feature 287, homes H30/H31, plan D3) ----------


@pytest.mark.parametrize("windward", sorted(hg.WIND_VECTORS))
def test_a_rolled_fall_always_leaves_a_margin_whose_back_faces_the_wind(windward: str) -> None:
    """The roll's value space is the falls `fall_backs_the_wind` admits: over 200 seeds no rolled fall runs within 90
    degrees of the wind's quarter (the fan's flanks lean uphill, so a fall 45 degrees off the wind leaves only the toe's
    corner facing it - cohort seed 24), and every value that remains is rolled."""
    falls = {hg.plan_site(hg.HamletSpec(name="X", seed=s, households=10, windward=windward)).down_deg for s in range(1, 201)}
    assert falls == {f for f in FALL_BEARINGS if fall_backs_the_wind(f, windward)}
    assert len(falls) == 5


def test_a_rolled_fall_backs_the_wind_and_a_declared_one_is_taken_as_written() -> None:
    """Plan D3: the roll is narrowed to falls square to the wind or away from it; a declared fall is the GM's fact, taken
    as written - into the wind included - and its site is judged by the seat alone."""
    assert not fall_backs_the_wind(225.0, "NW") and not fall_backs_the_wind(180.0, "NW")
    assert fall_backs_the_wind(135.0, "NW") and fall_backs_the_wind(45.0, "NW")
    assert hg.plan_site(hg.HamletSpec(name="Sawada", seed=24, households=19, down_deg=225)).down_deg == 225


def test_a_flank_offers_its_back_turned_to_the_wind_after_every_margin_facing_it() -> None:
    """Homes H30, plan D3: a margin 45 to 90 degrees off the wind offers a seat whose back is turned just past the bar
    toward the wind (tier 1), after every margin that faces it (tier 0); a margin facing away offers none."""
    from l7r.diagram.hamletgen.cluster import margin_candidates

    square = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    wind = (-0.5, -math.sqrt(0.75))  # 30 degrees west of north: the north edge faces it, the west edge is 60 degrees off
    got = {m: (o, t) for m, o, t in margin_candidates(square, (50.0, 50.0), wind)}
    assert set(got) == {(50.0, 0.0), (0.0, 50.0)}, "south and east face away and offer nothing"
    assert got[(50.0, 0.0)] == ((0.0, -1.0), 0)
    west, tier = got[(0.0, 50.0)]
    assert tier == 1 and west[0] * wind[0] + west[1] * wind[1] > hg.WIND_BACK_MIN_DOT and -west[0] > math.cos(math.radians(45.0)), "turned just past the bar, under 45 degrees off its normal"
    plan = a_plan()
    plan.windward = "NW"
    plan.envelope = [(x + 600.0, y + 600.0) for x, y in SQUARE]
    seat = hg.seat_cluster(plan)
    assert seat["out"][0] * -0.7071 + seat["out"][1] * -0.7071 >= hg.WIND_BACK_MIN_DOT and seat["offwind"] is False


@pytest.mark.parametrize("shape", sorted(CLUSTER_SHAPES))
@pytest.mark.parametrize("windward", sorted(hg.WIND_VECTORS))
def test_the_canvas_holds_the_seat_and_its_belt_on_the_windward_side(windward: str, shape: str) -> None:
    """H31: the canvas is the field's square grown by the fan's overhang and the seat's room on every side, so a field
    pushed as far toward the wind as a fan stands past its square still has a wind-facing margin whose band and belt
    stand on the canvas - the largest hamlet, every shape, every wind."""
    wx, wy = hg.WIND_VECTORS[windward]
    down = next(f for f in FALL_BEARINGS if fall_backs_the_wind(f, windward))
    plan = hg.plan_site(hg.HamletSpec(name="X", seed=1, households=20, windward=windward, down_deg=down, cluster_shape=shape))
    c, reach = plan.W / 2.0, plan.field_span * (0.5 + FAN_OVERHANG)
    side = plan.field_span * 0.5
    x0 = c - reach if wx < 0 else (c + reach - side if wx > 0 else c - side / 2)
    y0 = c - reach if wy < 0 else (c + reach - side if wy > 0 else c - side / 2)
    plan.envelope = [(x0, y0), (x0 + side, y0), (x0 + side, y0 + side), (x0, y0 + side)]
    seat = hg.seat_cluster(plan)
    assert seat["out"][0] * wx + seat["out"][1] * wy >= hg.WIND_BACK_MIN_DOT
    off = belt_off_canvas((seat["cx"], seat["cy"]), seat["along"], seat["out"], seat["lat"], seat["dep"], (wx, wy), plan.W, plan.H)
    assert off <= BELT_ROOM_MAX_OFF


def test_a_canvas_with_no_room_for_the_belt_refuses_the_site() -> None:
    """The input `plan_site` never produces: both wind-facing margins with their bands on the canvas (HARD 3 passes, the
    seat center a whole `lat` inside the frame - feature 328) but their belts, thrown out diagonally by a northwest
    wind, off the corner - each cramped margin is refused (no longer a fallback), and so is the site. Moved in by the
    seat's room (`seat_room`), the same field seats. (A wind square to the frame cannot reach the refusal now: past
    HARD 3's whole `lat` the belt's 146 ft row stands on the canvas for every band `band_extent` gives.)"""
    plan = a_plan(households=10, cluster_shape="round")
    plan.windward = "NW"
    dep, lat = band_extent(10, "round")
    corner = lat + dep + SEAT_STANDOFF + 10.0  # each margin's seat center a whole `lat` (and 10 px) inside its frame edge
    plan.envelope = [(x - 400.0 + corner, y - 400.0 + corner) for x, y in SQUARE]
    north, west = (corner + 300.0, lat + 10.0), (lat + 10.0, corner + 300.0)
    assert belt_off_canvas(north, (1.0, 0.0), (0.0, -1.0), lat, dep, plan.wind, plan.W, plan.H) > BELT_ROOM_MAX_OFF, "the premise: the band fits, its belt does not"
    assert belt_off_canvas(west, (0.0, 1.0), (-1.0, 0.0), lat, dep, plan.wind, plan.W, plan.H) > BELT_ROOM_MAX_OFF
    with pytest.raises(SeatRefused):
        hg.seat_cluster(plan)
    room = seat_room(10, "round")
    plan.envelope = [(x - 400.0 + room + 1.0, y - 400.0 + room + 1.0) for x, y in SQUARE]
    assert hg.seat_cluster(plan)["out"] in ((0.0, -1.0), (-1.0, 0.0))


def test_the_band_and_the_seat_room_are_one_derivation() -> None:
    dep, lat = band_extent(20, "elongated")
    assert dep < 120.0 and lat > 500.0
    assert seat_room(20, "elongated") == pytest.approx(dep + SEAT_STANDOFF + hg.WIND_BACK_MIN_DOT * lat + dep + BELT_REACH)
    assert seat_room(10, "round") < seat_room(20, "round")


def _boxed_in(cx: float, cy: float, r: float) -> list[list[tuple[float, float]]]:
    """Four marsh strips walling a square of half-side `r` round (cx, cy) - no dry way out of it."""
    t = 20.0
    return [
        [(cx - r - t, cy - r - t), (cx + r + t, cy - r - t), (cx + r + t, cy - r), (cx - r - t, cy - r)],
        [(cx - r - t, cy + r), (cx + r + t, cy + r), (cx + r + t, cy + r + t), (cx - r - t, cy + r + t)],
        [(cx - r - t, cy - r), (cx - r, cy - r), (cx - r, cy + r), (cx - r - t, cy + r)],
        [(cx + r, cy - r), (cx + r + t, cy - r), (cx + r + t, cy + r), (cx + r, cy + r)],
    ]


def test_a_seat_walled_in_by_the_wet_has_no_dry_exit_and_is_refused() -> None:
    """Feature 287, ways W23 at the seat: the connector raises `NoDryExit` where the gateway is walled in, so the seat
    asks the same flood fill (`dry_exit`) first. The crown's top seat boxed in by marsh: the seat moves to a shoulder;
    every wind-facing seat boxed in: the site is refused, naming it."""
    from l7r.diagram.hamletgen.cluster import seat_has_dry_exit

    plan = a_plan()
    plan.envelope = list(CROWN)
    free = hg.seat_cluster(plan)
    assert seat_has_dry_exit(plan, (free["cx"], free["cy"]))
    box = _boxed_in(free["cx"], free["cy"], 60.0)
    assert not seat_has_dry_exit(plan, (free["cx"], free["cy"]), wet=box)
    moved = hg.seat_cluster(plan, wet=box)
    assert (moved["cx"], moved["cy"]) != (free["cx"], free["cy"])
    assert (free["cx"], free["cy"]) not in [(r["cx"], r["cy"]) for r in moved["ladder"]], "a walled seat is no rung either"
    everywhere = [p for q in [free, *free["ladder"]] for p in _boxed_in(q["cx"], q["cy"], 60.0)]
    with pytest.raises(SeatRefused):
        hg.seat_cluster(plan, wet=everywhere)
    plan.sink_pond = (700.0, 2000.0, 60.0, 40.0)  # the tameike's disc is a wall too, far from here
    plan.sink_brook = [(0.0, 1900.0), (1400.0, 1900.0)]
    assert seat_has_dry_exit(plan, (free["cx"], free["cy"]))


def test_each_refusal_of_a_wind_facing_margin_turns_it_away() -> None:
    """Every HARD refusal met on a margin whose back faces the wind (homes H30 put the wind first): the band standing in
    the field's own arm, the drain, the canvas edge, the wet toe - each leaves no seat here - and a dry hem that only
    scores a surviving margin down."""
    from l7r.diagram.hamletgen.cluster import SeatRefused

    plan = a_plan(households=20, cluster_shape="elongated")
    # the L stands 700 px in from the canvas's left, so its arm's seat clears the frame by the band's half-length (587 ft)
    plan.envelope = [(700.0, 1000.0), (800.0, 1000.0), (800.0, 1300.0), (1300.0, 1300.0), (1300.0, 1600.0), (700.0, 1600.0)]
    seat = hg.seat_cluster(plan)  # the L's long top edge is refused (its band stands in the arm); the arm's own top seats it
    assert seat["out"] == (0.0, -1.0) and seat["anchor"][0] < 800.0
    south = a_seat_plan()
    south.windward = "S"
    with pytest.raises(SeatRefused):
        hg.seat_cluster(south, drain=[(300.0 + D, 950.0 + D), (1100.0 + D, 950.0 + D)])  # the south margin is below the drain
    east = a_seat_plan()
    east.windward = "E"
    east.W = east.H = int(1050 + D)
    with pytest.raises(SeatRefused):
        hg.seat_cluster(east)  # the east margin's band center stands off the canvas
    toe = [(0.0, 0.0), (3000.0, 0.0), (3000.0, 395.0 + D), (0.0, 395.0 + D)]
    with pytest.raises(SeatRefused):
        hg.seat_cluster(a_seat_plan(), toe=toe)
    plan = a_plan()
    plan.envelope = list(CROWN)
    far = [[(600.0, 1500.0), (700.0, 1500.0), (700.0, 1600.0), (600.0, 1600.0)]]
    assert hg.seat_cluster(plan, dry_plots=far)["out"][1] < 0.0, "a far hem scores; the seat stands"


def test_a_straight_run_off_the_canvas_is_a_dry_exit_and_the_fill_decides_the_rest(monkeypatch: pytest.MonkeyPatch) -> None:
    """`straight_exit`, the flood fill's fast path: a clear straight run off the canvas answers yes at once; a seat walled
    on every bearing goes to the fill, which still finds the way out a straight run cannot."""
    from l7r.diagram.hamletgen import cluster

    walls = [([(0.0, -100.0), (100.0, -100.0), (100.0, 100.0), (0.0, 100.0)], 0.0)]
    assert cluster.straight_exit((1000.0, 1000.0), walls, [], 2000.0, 2000.0, 20.0)
    ringed = [(p, 0.0) for p in _boxed_in(1000.0, 1000.0, 200.0)]
    assert not cluster.straight_exit((1000.0, 1000.0), ringed, [], 2000.0, 2000.0, 20.0)
    assert not cluster.straight_exit(
        (1000.0, 1000.0), [], [((900.0, 0.0), (900.0, 2000.0)), ((1100.0, 0.0), (1100.0, 2000.0)), ((0.0, 900.0), (2000.0, 900.0)), ((0.0, 1100.0), (2000.0, 1100.0))], 2000.0, 2000.0, 20.0
    )
    plan = a_plan()
    plan.envelope = list(CROWN)
    seat = hg.seat_cluster(plan)
    monkeypatch.setattr(cluster, "straight_exit", lambda *a: False)
    assert cluster.seat_has_dry_exit(plan, (seat["cx"], seat["cy"])), "the fill finds it"
