"""Unit tests for the houses, their appurtenances, and the wells (`hamletgen/homesteads.py`).

Split from test_hamletgen.py by feature 111; test bodies verbatim. See hamletgen/CLAUDE.md.
"""

import contextlib
import math

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen.homesteads.capacity import SiteRefused
from l7r.diagram.settlement import Settlement

from ._builders import SQUARE, a_plan


@pytest.mark.parametrize(("households", "wells"), [(10, 2), (12, 2), (15, 2), (20, 3)])
def test_wells_are_one_per_six_households_or_so(households: int, wells: int) -> None:
    """Inside `wells_sized_to_population`'s 2-20 households-per-well band at hamlet scale."""
    got = hg.well_target(households)
    assert got == wells
    assert 2 <= households / got <= 20


def test_a_tiny_hamlet_still_keeps_one_well() -> None:
    assert hg.well_target(1) == 1


# A 60 x 26 house at (1000, 1000), and two far houses that set the lattice's origin (min x 988, min y 988) so a
# lattice point falls 110 px due north of it - 13 px of its depth leaves that seat's wall gap at 97 px.
_WELL_HOUSES = [
    {"x": 1000.0, "y": 1000.0, "w": 60.0, "h": 26.0, "rot": 0.0},
    {"x": 988.0, "y": 1400.0, "w": 60.0, "h": 26.0, "rot": 0.0},
    {"x": 1400.0, "y": 988.0, "w": 60.0, "h": 26.0, "rot": 0.0},
]


def _only_seat(sx: float, sy: float, open_seat: tuple[float, float] | None = None) -> object:
    """A settlement whose engine allows a wellhead at (sx, sy) alone, and whose `open_seat` answers `open_seat`."""
    from types import SimpleNamespace

    return SimpleNamespace(well_at=lambda x, y: abs(x - sx) < 0.5 and abs(y - sy) < 0.5, open_seat=lambda *_a, **_k: open_seat, M={})


def test_a_well_is_held_to_the_wall_gap_the_test_reads_not_to_a_center_distance() -> None:
    """Feature 287 T04 (FR-003, homes H09): `place_wells` and the finished-map test read ONE predicate,
    `well_gap_to_dwellings` - the gap to the nearest dwelling's drawn wall, at most 95 px. The constructed case is where
    the two used to disagree: a lattice seat 110 px from a 26 px-deep house's CENTER, inside the old rungs' 112 px, but
    97 px from its wall. It is refused - on the lattice, by the rescue ring and at the last resort alike, which is
    handed the same seat - and the hamlet digs no well there. A seat the same center distance off the house's long
    end (wall 80 px off) is taken, and so is a last-resort seat among the doors."""
    from types import SimpleNamespace

    from l7r.diagram.hamletgen.homesteads.wells import WELL_AMONG_DWELLINGS_PX, well_gap_to_dwellings

    plan = SimpleNamespace(spec=SimpleNamespace(households=6), ftpx=1.0)
    north = (1000.0, 890.0)
    assert math.hypot(north[0] - 1000.0, north[1] - 1000.0) <= 112.0, "inside the old rungs' center distance"
    assert well_gap_to_dwellings(_WELL_HOUSES, *north) == pytest.approx(97.0), "and 97 px from its wall"
    assert WELL_AMONG_DWELLINGS_PX < 97.0, "past the wall gap"
    assert hg.place_wells(_only_seat(*north, open_seat=north), plan, _WELL_HOUSES) == 0  # type: ignore[arg-type]

    east = (1110.0, 1000.0)  # the same 110 px from the center, off the long end: the wall is 80 px away
    assert well_gap_to_dwellings(_WELL_HOUSES, *east) == pytest.approx(80.0)
    assert hg.place_wells(_only_seat(*east), plan, _WELL_HOUSES) == 1  # type: ignore[arg-type]

    door = (1001.5, 960.0)  # off the lattice: with no rescue and no last resort (feature 287, H10-H12), nothing seeks it
    assert hg.place_wells(_only_seat(*door, open_seat=door), plan, _WELL_HOUSES) == 0  # type: ignore[arg-type]
    pocketed = [{**_WELL_HOUSES[0], "well_pocket": [1000.0, 1040.0]}, *_WELL_HOUSES[1:]]
    wells: list[tuple[float, float]] = []
    fake = _only_seat(*door)
    fake.well = lambda x, y: wells.append((x, y))  # type: ignore[attr-defined]
    assert hg.place_wells(fake, plan, pocketed) == 1 and wells == [(1000.0, 1040.0)], "...but a pocket is always drawn"  # type: ignore[arg-type]


def test_the_well_gap_reads_the_turned_wall_and_passes_over_a_derelict() -> None:
    """The predicate measures each dwelling on its drawn quad (a house turned a quarter lies along the other axis) and
    reads no abandoned house as a dwelling; with no dwelling at all, no well stands among any."""
    from l7r.diagram.hamletgen.homesteads.wells import well_gap_to_dwellings

    turned = [{"x": 1000.0, "y": 1000.0, "w": 60.0, "h": 26.0, "rot": 90.0}]
    assert well_gap_to_dwellings(turned, 1000.0, 890.0) == pytest.approx(80.0), "turned, the house's long side faces north"
    assert well_gap_to_dwellings(turned, 1000.0, 1000.0) == 0.0, "inside the footprint"
    assert well_gap_to_dwellings([{**turned[0], "kind": "abandoned"}], 1000.0, 890.0) == math.inf


# ---- feature 145: the refusal branches of the fixture placer that no cohort seed took --------------


def _strip_settlement() -> tuple[object, object]:
    from l7r.diagram.settlement import Settlement

    s = Settlement(1000, 1000, seed=1)
    s.meta(name="S", scale="hamlet", ftpx=1, down_deg=90)
    return s, a_plan()


def test_strip_blocked_refuses_the_canvas_edge_a_crossing_lane_and_a_drawn_crown() -> None:
    s, _plan = _strip_settlement()
    blocked = hg.homesteads._strip_blocked
    assert blocked(s, 20, 500, 30, 20, 0, 0, [], [], None, []) is True, "over the canvas edge"
    assert blocked(s, 500, 500, 30, 20, 0, 0, [], [], None, []) is False, "open ground"
    lane = [([(500, 400), (500, 600)], 3.0)]  # a lane running THROUGH the strip, both ends outside it
    assert blocked(s, 500, 500, 30, 20, 0, 0, [], [], None, lane) is True
    s.M["tree_crowns"] = [500.0, 500.0, 12.0]
    assert blocked(s, 500, 500, 30, 20, 0, 0, [], [], None, []) is True, "a crown drawn two stages earlier"


def test_farmstead_fixtures_on_a_houseless_map_place_nothing() -> None:
    s, plan = _strip_settlement()
    assert hg.homesteads.farmstead_fixtures(s, plan, []) == 0


def test_roll_falls_through_to_the_last_weight() -> None:
    """A u past the weights' sum (floating-point slack) takes the last row rather than raising."""
    assert hg.homesteads._roll([("a", 0.3), ("b", 0.3)], 0.99) == "b"
    assert hg.homesteads._roll([("a", 0.3), ("b", 0.3)], 0.1) == "a"


def test_strip_blocked_refuses_a_lane_that_only_crosses_the_strip() -> None:
    """Feature 146: the crossing arm of `_strip_blocked` - a lane whose ENDS are both outside the strip but
    whose segment passes through it (the corner test above cannot see that one)."""
    s, _plan = _strip_settlement()
    blocked = hg.homesteads._strip_blocked
    across = [([(440.0, 500.0), (560.0, 500.0)], 1.0)]  # a hairline lane straight through, ends well clear
    assert blocked(s, 500, 500, 30, 20, 0, 0, [], [], None, across) is True
    beside = [([(440.0, 300.0), (560.0, 300.0)], 1.0)]
    assert blocked(s, 500, 500, 30, 20, 0, 0, [], [], None, beside) is False


def test_strip_blocked_refuses_a_dry_plot_and_a_watercourse(monkeypatch) -> None:
    """The two arms the unlock tripwire seed 47 added (a fixture on a dry plot, one on the stream) - reached by the
    cohort seeds until feature 214 packed them away, so asserted directly: a strip with a corner inside a dry hem
    plot is blocked, and so is one whose corner stands on a watercourse."""
    s, _plan = _strip_settlement()
    blocked = hg.homesteads._strip_blocked
    s.M["dry_plots"] = [{"poly": [(480.0, 480.0), (520.0, 480.0), (520.0, 520.0), (480.0, 520.0)]}]
    assert blocked(s, 500, 500, 30, 20, 0, 0, [], [], None, []) is True, "a corner inside a dry plot"
    s.M["dry_plots"] = []
    assert blocked(s, 500, 500, 30, 20, 0, 0, [], [], None, []) is False
    monkeypatch.setattr(s, "_on_watercourse", lambda x, y, pad=4.0, near=None: True)  # the footing passes its grid as `near` (feature 218)
    assert blocked(s, 500, 500, 30, 20, 0, 0, [], [], None, []) is True, "a corner on the stream"


def test_strip_blocked_sees_a_lane_that_crosses_the_strip_between_its_samples() -> None:
    """Five sample points on a 22 by 16 ft strip let a lane cross it DIAGONALLY between them (cohort
    seed 03), and `lanes_clear_of_bamboo` walks the tread's quarter-points, so the gate saw what the
    placer did not. The tread is therefore tested as a segment against the strip's own edges."""
    from l7r.diagram.hamletgen.homesteads import _strip_blocked

    s = Settlement(1000, 1000, seed=1)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    # The five samples are the four corners AND the center, so a tread through the middle is caught a
    # line earlier. This one clips the strip between them: 2.2 px from the nearest sample, well past
    # the tread's own half-width, and still straight through the strip.
    clipping = [([(480.0, 505.0), (520.0, 485.0)], 1.0)]
    assert _strip_blocked(s, 500.0, 500.0, 22.0, 16.0, 900.0, 900.0, [], [], None, clipping)
    assert not _strip_blocked(s, 200.0, 800.0, 22.0, 16.0, 900.0, 900.0, [], [], None, clipping)


def test_a_linear_hamlet_strings_its_houses_along_the_connector() -> None:
    """The `linear` settlement form is attested and implemented but pinned off (`SETTLEMENT_FORMS`), so
    the arm that fronts the CONNECTOR - the only way on the map that predates the houses - has never
    rolled. `lane_frontage` skips the connector for exactly the reason this form wants it: fronting it
    strings the hamlet along the road instead of nucleating it, which is this archetype."""
    from l7r.diagram.hamletgen.homesteads import stage_homesteads  # through the MODULE: a stage is not package surface

    # TEN HOUSEHOLDS, THE FLOOR OF THE HAMLET BAND (feature 158): the arm under test is the frontage
    # loop, which does not care how many houses it strings - and every household is a seat search.
    # Fifteen cost 4-5 s of every run in all three tiers; ten cost two thirds of that and prove the
    # same thing. (Nine is not available: `HamletSpec` refuses anything outside 10-20.)
    for form in ("nucleated", "linear"):
        plan = a_plan(households=10)
        plan.seat = hg.seat_cluster(plan)
        plan.settlement_form = form
        s = Settlement(1400, 1400, seed=3)
        s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=10, down_deg=90, water_flow=90, nucleated=True)
        s.field_polys.append(list(plan.envelope))
        # the connector has to BE there for the linear form to string anything along it - it is the one
        # way on the map that predates the houses, which is the whole premise of the archetype
        cx_, cy_ = float(plan.seat["cx"]), float(plan.seat["cy"])
        s.M["lanes"] = [{"pts": [[cx_ - 400, cy_], [cx_ + 400, cy_]], "w": 6, "connector": True}]
        stage_homesteads(s, plan)
        assert len(s.M["houses"]) == 10, f"{form}: every household seated"

    # ...and the frontage loop STOPS when the households run out rather than filling the whole
    # connector: the same plan, with the ask cut to three, seats three and leaves the rest of the
    # road bare. A row village is as long as its households, not as long as its road.
    spec = hg.HamletSpec(name="Row", seed=3, households=10, down_deg=90.0, windward="N")
    plan = hg.plan_site(spec)
    plan.envelope = list(SQUARE)
    plan.seat = hg.seat_cluster(plan)
    plan.settlement_form = "linear"
    s = Settlement(1400, 1400, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=10, down_deg=90, water_flow=90, nucleated=True)
    s.field_polys.append(list(plan.envelope))
    cx_, cy_ = float(plan.seat["cx"]), float(plan.seat["cy"])
    s.M["lanes"] = [{"pts": [[cx_ - 620, cy_], [cx_ + 620, cy_]], "w": 6, "connector": True}]
    stage_homesteads(s, plan)
    assert len(s.M["houses"]) == 10


def test_a_fixture_across_the_brook_from_its_house_is_across() -> None:
    """Feature 261 FR-013: the line from the house to a fixture's seat crossing a stream puts the seat on the far
    bank; a seat on the house's own bank, or a sheet with no stream, is not."""
    from l7r.diagram.hamletgen.homesteads.fixtures import across_the_brook

    s = Settlement(1400, 1400, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1, down_deg=90)
    assert across_the_brook(s, (700.0, 600.0), (700.0, 800.0)) is False
    s.M["streams"] = [{"poly": [[100.0, 700.0], [1300.0, 700.0]], "w": 9}]
    assert across_the_brook(s, (700.0, 600.0), (700.0, 800.0)) is True
    assert across_the_brook(s, (700.0, 600.0), (760.0, 640.0)) is False


def test_a_fixture_beyond_a_lane_from_its_house_is_across() -> None:
    """Settlement-review of Mizuguchi (feature 261): a lane between the house and the seat puts the seat outside the
    plot; a seat on the house's side of every lane is not across."""
    from l7r.diagram.hamletgen.homesteads.fixtures import across_a_lane

    lane = ([(100.0, 700.0), (500.0, 700.0), (1300.0, 700.0)], 4.5)
    assert across_a_lane([lane], (700.0, 600.0), (700.0, 720.0)) is True
    assert across_a_lane([lane], (700.0, 600.0), (740.0, 660.0)) is False
    assert across_a_lane([], (700.0, 600.0), (700.0, 720.0)) is False


def _toy_hamlet(households: int, seed: int = 3, east: bool = False):  # type: ignore[no-untyped-def]
    """The linear toy's setup, for the stage's own branches: a square field, a seat band, the connector. The seat is a
    margin's frame built directly - the north one, or with `east` the east one, which the twenty-household toy was seated
    on before feature 287 (as the off-wind fallback: the band would not fit north of the square). `seat_cluster` refuses
    both today (homes H30/H31); the stage's branches, not the seat's choice, are under test here."""
    from l7r.diagram.hamletgen.cluster import _seat_frame
    from l7r.diagram.hamletgen.plan import band_extent

    plan = a_plan(households=households)
    dep, lat = band_extent(households, plan.cluster_shape)
    anchor, out = ((1000.0, 700.0), (1.0, 0.0)) if east else ((700.0, 400.0), (0.0, -1.0))
    plan.seat = {**_seat_frame(anchor, out, lat, dep, plan.wind), "ladder": []}
    plan.settlement_form = "nucleated"
    s = Settlement(1400, 1400, seed=seed)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=households, down_deg=90, water_flow=90, nucleated=True)
    # THE PLACER'S OWN SWITCH, as the generator sets it (`hamletgen/water/skeleton.py`): `meta(nucleated=True)` only
    # RECORDS the form, and without this the toy's homesteads ran the DISPERSED spiral - a path no pool hamlet uses
    # (found by feature 276's plan review: the rescue scenario's grove rejections could only come from a dispersed bundle).
    s._nucleated = plan.settlement_form == "nucleated"
    s.field_polys.append(list(plan.envelope))
    cx_, cy_ = float(plan.seat["cx"]), float(plan.seat["cy"])
    s.M["lanes"] = [{"pts": [[cx_ - 400, cy_], [cx_ + 400, cy_]], "w": 6, "connector": True}]
    return s, plan


def test_the_front_row_stops_at_its_share_and_the_ranks_seat_the_rest(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 227 D8: the row takes about sqrt(N x A) houses - here fewer than the chain could seat - and stops;
    the ranks behind seat the rest. The toy's households keep no fixtures (homes H32): their corridors leave the yard
    round them, and the row's count is the thing under test. Nor a share of the wood floor (woods W25): the exit strip
    runs up the back of the toy's middle house, whose wood then spreads to its flanks and takes a row seat - measured,
    the row seats 4 - and the row's count, not the wood, is under test (`tests/settlement/test_wood_share.py` is the
    wood's)."""
    from l7r.diagram.hamletgen.consts import CLUSTER_DRAWN_ASPECT
    from l7r.diagram.hamletgen.homesteads import stage_homesteads
    from l7r.diagram.hamletgen.homesteads import stages as st

    monkeypatch.setattr(st, "fixture_quota", lambda *a: {})
    monkeypatch.setattr(st, "install_wood_shares", lambda *a: None)
    s, plan = _toy_hamlet(10)
    plan.cluster_shape = "round"  # the tightest band: the row's share is the floor of six, fewer than the chain could seat
    stage_homesteads(s, plan)
    lo, hi = CLUSTER_DRAWN_ASPECT["round"]
    cap = min(10, max(6, round(math.sqrt(10 * (lo + hi)))))
    assert cap == 6
    ss = s.M["meta"]["seat_search"]
    assert len(s.M["houses"]) == 10 and ss["front"] == cap and ss["rounds"] >= 1


def test_a_quota_the_ranks_cannot_seat_reaches_the_rescue_rounds() -> None:
    """The rescue rounds (five to seven) run only while the quota is short after four rounds of ranks; their cloud
    seeds a wider band and skips the seeds outside it. Twenty households on the toy's square field is such a quota."""
    from l7r.diagram.hamletgen.homesteads import stage_homesteads

    s, plan = _toy_hamlet(20, east=True)
    # the ground beyond 260 ft of the seat is no-build, so the ranks run out of room and the rescue's wider cloud
    # throws seeds the band refuses
    cx_, cy_ = float(plan.seat["cx"]), float(plan.seat["cy"])
    s.block_polys.append([(cx_ - 2000.0, cy_ - 2000.0), (cx_ + 2000.0, cy_ - 2000.0), (cx_ + 2000.0, cy_ - 260.0), (cx_ - 2000.0, cy_ - 260.0)])
    s.block_polys.append([(cx_ - 2000.0, cy_ + 260.0), (cx_ + 2000.0, cy_ + 260.0), (cx_ + 2000.0, cy_ + 2000.0), (cx_ - 2000.0, cy_ + 2000.0)])
    plan.seat["ladder"] = []  # this margin alone: the refusal below is the chosen margin's
    # ...AND A QUOTA THE GROUND CANNOT HOLD IS REFUSED, NEVER SHIPPED SHORT (feature 287, homes H14 and plan D2): the
    # rescue and then the exhaustive pass over every free point within reach ran, and still the ground was full
    with pytest.raises(SiteRefused, match="no margin seats all 20 households"):
        stage_homesteads(s, plan)
    assert s._seat_search["rounds"] >= 5, "the rescue ran"
    assert s._seat_search["exhaustive_offered"] > 0, "...and the exhaustive pass after it"
    assert len(s.M["houses"]) < 20, "the ground, not the search, was the limit"


def test_a_cluster_standing_off_its_field_gets_the_spur_to_it() -> None:
    """`stage_track`'s field spur is laid when the path from the cluster's edge to the field is longer than 20 ft; the
    pool's clusters front the paddy at the wall rule now (feature 227), so no shipped map lays one - a cluster seated
    three hundred feet back does."""
    from l7r.diagram.hamletgen.ways import stage_track

    s, plan = _toy_hamlet(10)
    # A DISPERSED cluster, said so (feature 276): the seats three hundred feet back fall off the toy's canvas, and it
    # was the dispersed spiral - which the toy ran by accident until `_toy_hamlet` set the placer's own switch -
    # that found room within reach of them. The spur is a property of the track, whatever form stands back there.
    s._nucleated = False
    cx_, cy_ = float(plan.seat["cx"]), float(plan.seat["cy"])
    ox, oy = plan.seat["out"]
    n = 0
    for k in range(-2, 3):
        ax, ay = plan.seat["along"]
        if s.try_place(cx_ + ax * 110 * k + ox * 300, cy_ + ay * 110 * k + oy * 300, "plain"):
            n += 1
    assert n >= 3
    stage_track(s, plan)
    spurs = [ln for ln in s.M["lanes"] if ln.get("w") == 5 and not ln.get("connector") and ln.get("worn")]
    assert spurs, "a worn width-5 way besides the connector: the spur to the field"


def test_a_rank_round_that_seats_nothing_grows_the_cluster_along_the_field() -> None:
    """Feature 227 D8: the seats a pitch beyond each end of the rank are offered ONLY in a round that seated nothing
    behind - so a cluster whose back is refused grows along the field instead of stopping. Here the ground more than
    40 px out from the row is no-build, so every seat at a rank's depth is refused and the ends are the only ones
    left; the houses past the front row's own count can therefore only have come from them."""
    from l7r.diagram.hamletgen.homesteads import stage_homesteads

    s, plan = _toy_hamlet(12)
    ax, ay = plan.seat["along"]
    ox, oy = plan.seat["out"]
    cx, cy = float(plan.seat["cx"]), float(plan.seat["cy"])
    back = [
        (cx + ox * 40 - ax * 5000, cy + oy * 40 - ay * 5000),
        (cx + ox * 40 + ax * 5000, cy + oy * 40 + ay * 5000),
        (cx + ox * 5000 + ax * 5000, cy + oy * 5000 + ay * 5000),
        (cx + ox * 5000 - ax * 5000, cy + oy * 5000 - ay * 5000),
    ]
    s.block_polys.append(back)
    with contextlib.suppress(SiteRefused):  # the strip holds fewer than twelve homesteads with their fixtures (homes H32)
        stage_homesteads(s, plan)
    ss = s._seat_search
    assert ss["rounds"] >= 1, "the ranks ran"
    assert len(s.M["houses"]) > ss["front"], "the only seats left were the ends, and the cluster took them"


def test_an_accretion_hamlets_ranks_stand_off_their_lines_and_a_planned_ones_do_not() -> None:
    """`stage_homesteads` (feature 261 D22): an `alleys` hamlet's rank seats take the depth jitter, so the ranks behind the
    front row are not all on one line; a `back_lane` hamlet seated the same way keeps its ranks exact. Both seat every
    household."""
    from l7r.diagram.hamletgen.homesteads import stage_homesteads

    seats = {}
    for form in ("alleys", "back_lane"):
        s, plan = _toy_hamlet(14)
        plan.lane_web = form
        stage_homesteads(s, plan)
        assert len(s.M["houses"]) == 14
        seats[form] = {(round(h["x"], 1), round(h["y"], 1)) for h in s.M["houses"]}
    moved = seats["alleys"] - seats["back_lane"]
    assert moved and len(moved) < 14, "the ranks' seats moved off their lines; the front row did not"


# ---- feature 276 FR-003 (plan D9): the free ground proposes, the fit test decides ----------------------------------


def _seats(s):  # type: ignore[no-untyped-def]
    return [(round(h["x"], 3), round(h["y"], 3), tuple(round(v, 3) for v in (h.get("geom") or {}).get("bbox", ()))) for h in s.M["houses"]]


def _rescue(form):  # type: ignore[no-untyped-def]
    s, plan = _toy_hamlet(20, east=True)
    s._nucleated = form == "nucleated"
    cx_, cy_ = float(plan.seat["cx"]), float(plan.seat["cy"])
    s.block_polys.append([(cx_ - 2000.0, cy_ - 2000.0), (cx_ + 2000.0, cy_ - 2000.0), (cx_ + 2000.0, cy_ - 260.0), (cx_ - 2000.0, cy_ - 260.0)])
    s.block_polys.append([(cx_ - 2000.0, cy_ + 260.0), (cx_ + 2000.0, cy_ + 260.0), (cx_ + 2000.0, cy_ + 2000.0), (cx_ - 2000.0, cy_ + 2000.0)])
    plan.seat["ladder"] = []  # the chosen margin alone, so its seats stand when the site is refused (feature 287, D2)
    return s, plan


@pytest.mark.parametrize("form", ["nucleated", "dispersed"])
@pytest.mark.parametrize("scenario", ["rescue", "open"])
def test_the_free_ground_changes_no_seat(form: str, scenario: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """The same houses, at the same seats, with the index asked first and with it switched off entirely."""
    from l7r.diagram.hamletgen.homesteads import boundary, stage_homesteads
    from l7r.diagram.settlement import Settlement

    def roll():  # type: ignore[no-untyped-def]
        s, plan = _rescue(form) if scenario == "rescue" else _toy_hamlet(15)
        s._nucleated = form == "nucleated"
        with contextlib.suppress(SiteRefused):  # the rescue ground cannot hold its quota (D2); the seats it took are compared all the same
            stage_homesteads(s, plan)
        return _seats(s)

    with_index = roll()
    monkeypatch.setattr(boundary.FreeGround, "rect_refused", lambda self, rect: False)
    monkeypatch.setattr(Settlement, "_seat_refused", lambda self, x, y, hw, hh: False)
    monkeypatch.setattr(Settlement, "_bundle_refused", lambda self, geom: False)
    without = roll()
    # the rescue's walled band, each homestead with its fixtures (homes H32) and its share of the wood floor (woods W25):
    # measured, 6 of the walled band's households seat with their wood where 8 did without it
    assert with_index == without and len(with_index) >= 6


def test_a_side_is_not_dropped_for_ground_the_loop_never_judges() -> None:
    """Plan review 2's case: on the nucleated path a side's own box is ground-tested only when the whole envelope was
    refused. With the envelope clear, an index claiming EVERY other box as taken - each side's own sample points
    included - must leave the seat exactly as it is with no index at all."""
    from l7r.diagram.settlement import Settlement

    class RefusesAllButTheEnvelope:
        def __init__(self, env):  # type: ignore[no-untyped-def]
            self.env = env

        def rect_refused(self, rect):  # type: ignore[no-untyped-def]
            return rect != self.env

    seated = 0
    for x, y in ((300.0, 300.0), (620.0, 410.0), (900.0, 760.0)):
        s = Settlement(1400, 1400, seed=5)
        s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=15, down_deg=90, water_flow=90, nucleated=True)
        s._nucleated = True
        plain = s._place_bundle_nucleated(x, y, 30.0, 20.0, False)
        assert s._envelope_blocked(s._bundle_envelope(x, y, 30.0, 20.0, False)) is None, "the case: the whole envelope clear"
        s._free_ground = RefusesAllButTheEnvelope(s._bundle_envelope(x, y, 30.0, 20.0, False))
        assert s._place_bundle_nucleated(x, y, 30.0, 20.0, False) == plain
        seated += plain is not None
    assert seated == 3, "non-vacuity: each seat was taken"


def test_every_surely_taken_cell_is_ground_the_fit_test_refuses() -> None:
    """FreeGround's exactness, asked of the real boundary on the toy: any point inside a taken cell is refused by the
    nine-point ground test itself (a zero-size rectangle there is nine copies of the point)."""
    import random

    from l7r.diagram.hamletgen.homesteads.boundary import install_site_boundary

    s, plan = _rescue("nucleated")
    install_site_boundary(s, plan)
    fg = s._free_ground
    assert len(fg.taken) > 100, "non-vacuity: the no-build walls and the field make taken ground"
    r = random.Random(276)
    for i, j in r.sample(sorted(fg.taken), 300):
        px, py = fg.x0 + (i + r.random()) * fg.cell, fg.y0 + (j + r.random()) * fg.cell
        assert s._site_blocks_rect((px, py, 0.0, 0.0)), (px, py)


def test_the_front_row_loop_stops_once_its_share_is_seated(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """`stage_homesteads`: the row's loop breaks when its share is placed, however many seats the chain still offers - here
    the chain's seats are offered twice over, and the row still takes exactly its share."""
    import math

    from l7r.diagram.hamletgen.consts import CLUSTER_DRAWN_ASPECT
    from l7r.diagram.hamletgen.homesteads import stage_homesteads
    from l7r.diagram.hamletgen.homesteads import stages as st

    monkeypatch.setattr(st, "fixture_quota", lambda *a: {})  # no fixtures: the row's count is under test (homes H32)
    monkeypatch.setattr(st, "install_wood_shares", lambda *a: None)  # ...nor wood shares (woods W25; see the test above)
    real = st.front_row
    monkeypatch.setattr(st, "front_row", lambda *a, **k: (lambda seats: seats + seats)(list(real(*a, **k))))
    s, plan = _toy_hamlet(10)
    plan.cluster_shape = "round"
    stage_homesteads(s, plan)
    lo, hi = CLUSTER_DRAWN_ASPECT["round"]
    assert s.M["meta"]["seat_search"]["front"] == min(10, max(6, round(math.sqrt(10 * (lo + hi)))))


def test_the_privy_seat_weights_are_rolled_per_hamlet_over_the_four_attested_seats() -> None:
    """269 B10 (research/homesteads/260): four attested seats, the weights re-rolled per hamlet from the seed and summing to one."""
    from l7r.diagram.hamletgen.homesteads.fixtures import _PRIVY_SEATS, privy_seat_weights

    a, b = privy_seat_weights(3), privy_seat_weights(4)
    assert [k for k, _ in a] == [k for k, _ in _PRIVY_SEATS] == ["yard", "front", "stable", "barn"]
    assert abs(sum(v for _, v in a) - 1.0) < 0.01 and a != b and a == privy_seat_weights(3)


def test_field_edge_seats_come_nearest_first_and_skip_an_edge_the_house_stands_within() -> None:
    """`field_edge_seats` (269 B11): a road's keep-out is added to the step, and an edge closer to the house than the
    step has no ground on the house's side to offer."""
    from l7r.diagram.hamletgen.homesteads.fixtures import edge_index, field_edge_seats

    idx = edge_index([[(100.0, 0.0), (200.0, 0.0), (200.0, 100.0), (100.0, 100.0)]], [([(0.0, 80.0), (60.0, 80.0)], 5.0), ([(0.0, 52.0), (60.0, 52.0)], 5.0)])
    pts = field_edge_seats(idx, 50.0, 50.0, 200.0, 10.0)
    assert pts[0][:2] == pytest.approx((50.0, 65.0)) and pts[1][:2] == pytest.approx((90.0, 50.0)), "the road, then the paddy"
    assert pts[0][2] is True and pts[1][2] is False, "each seat says whether its edge is a road"
    assert len(pts) == 2, "the road 2 px off the house leaves no ground between"


def test_kizuma_seats_keep_to_the_windward_edge_within_reach() -> None:
    """`kizuma_seats` (269 B15): the edge point nearest the house and a stack's length either way, each only to windward and
    within reach; nothing for a belt out of reach, and nothing where the house stands on the belt's own line."""
    from l7r.diagram.hamletgen.homesteads.fixtures import _WIND_VEC, belt_edge, kizuma_seats

    line = belt_edge([(330.0, 270.0), (470.0, 270.0), (470.0, 316.0), (330.0, 316.0)])
    got = kizuma_seats(line, 400.0, 350.0, 70.0, _WIND_VEC["NW"], 24.0, 2.0)
    assert len(got) == 2 and got[0][:2] == (pytest.approx(400.0), pytest.approx(318.0)), "the nearest point, and the one to the west"
    assert kizuma_seats(line, 400.0, 500.0, 70.0, _WIND_VEC["NW"], 24.0, 2.0) == []

    assert all(p[1] < 316.0 for p in kizuma_seats(line, 400.0, 316.0, 70.0, _WIND_VEC["N"], 24.0, 2.0)), "the house on the line is no seat"


def test_fixture_form_names_the_drawn_form() -> None:
    """`fixture_form` (feature 150, 269 B15): the pit, the woodshed, the kizuma, or the plain glyph."""
    from l7r.diagram.hamletgen.homesteads.fixtures import fixture_form

    assert fixture_form("manure", "pit", "eaves", False) == "pit" and fixture_form("manure", "heap", "eaves", False) is None
    assert fixture_form("woodpile", None, "kizuma", True) == "kizuma" and fixture_form("woodpile", None, "shed", False) == "shed"
    assert fixture_form("woodpile", None, "kizuma", False) is None and fixture_form("coop", "pit", "shed", False) is None


def test_strip_blocked_refuses_a_strip_standing_on_a_paddy() -> None:
    """A household strip whose corner stands in a paddy (or within 6 ft of its edge) is blocked - the branch the pool
    stopped reaching once Sawada's stranded field-house seat was refused (feature 278)."""
    s, _plan = _strip_settlement()
    paddy = [(480.0, 480.0), (700.0, 480.0), (700.0, 700.0), (480.0, 700.0)]
    assert hg.homesteads._strip_blocked(s, 500, 500, 30, 20, 0, 0, [paddy], [], None, []) is True
    assert hg.homesteads._strip_blocked(s, 300, 300, 30, 20, 0, 0, [paddy], [], None, []) is False


def test_a_front_seat_is_pushed_across_a_brook_by_the_waters_reach() -> None:
    """`water_push` (feature 261): a box whose near side a water course lies across moves along `n` past the course by its
    clearance; a course beside the box but beyond its lateral span, or one far off, moves nothing."""
    from l7r.diagram.hamletgen.homesteads.stages import water_push

    brook = [((-100.0, 10.0), (100.0, 10.0), 5.0)]  # across the box, 10 ft past its near edge at 0
    assert water_push(brook, (0.0, 20.0), (0.0, 1.0), 30.0, 0.0, 40.0) == 15.0
    assert water_push([((200.0, -50.0), (200.0, 90.0), 5.0)], (0.0, 20.0), (0.0, 1.0), 30.0, 0.0, 40.0) == 0.0
    assert water_push([((5000.0, 0.0), (5100.0, 0.0), 5.0)], (0.0, 20.0), (0.0, 1.0), 30.0, 0.0, 40.0) == 0.0


def test_the_drawn_forms_are_recorded_beside_the_rolled_knob() -> None:
    """`record_drawn_forms` (the 269 landing's reviews): the woodpiles by form - an unformed stack is the eaves stack - and
    the baths by whether a corridor joins them."""
    from l7r.diagram.hamletgen.homesteads.fixtures import record_drawn_forms

    m = {
        "meta": {},
        "farm_fixtures": [{"kind": "woodpile"}, {"kind": "woodpile", "form": "kizuma"}, {"kind": "woodpile"}, {"kind": "bath", "corridor": {"x": 1.0}}, {"kind": "bath"}, {"kind": "coop"}],
    }
    record_drawn_forms(m)
    assert m["meta"]["woodpile_forms_drawn"] == {"eaves": 2, "kizuma": 1} and m["meta"]["bath_seats_drawn"] == {"corridor": 1, "unjoined": 1}
