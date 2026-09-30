"""Unit tests for the houses, their appurtenances, and the wells (`hamletgen/homesteads.py`).

Split from test_hamletgen.py by feature 111; test bodies verbatim. See hamletgen/CLAUDE.md.
"""

import contextlib
import math

import pytest

import l7r.diagram.settlement.rolling.access as access_mod
from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen.homesteads.capacity import SiteRefused
from l7r.diagram.settlement import Settlement

from ._builders import a_plan


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

    # `frozen_terrain` is the engine's one-index scope for the well ladder; this stand-in has no terrain to freeze
    return SimpleNamespace(
        well_at=lambda x, y: abs(x - sx) < 0.5 and abs(y - sy) < 0.5,
        open_seat=lambda *_a, **_k: open_seat,
        M={},
        frozen_terrain=contextlib.nullcontext,
    )


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


def test_strip_blocked_excuses_its_own_farmhouse_and_the_skipped_bundle_boxes_and_nothing_else() -> None:
    """A strip beside its OWN farmhouse is not blocked by it, nor by a reserved box the caller passes in `skip`
    (feature 261: the homestead bundle boxes, whose parts are each registered); any other placed box it touches blocks it."""
    from l7r.diagram.hamletgen.homesteads import _strip_blocked

    s = Settlement(1000, 1000, seed=1)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    s.placed.append((500.0, 500.0, 40.0, 30.0))  # its own farmhouse, under the strip's center
    assert not _strip_blocked(s, 500.0, 500.0, 22.0, 16.0, 500.0, 500.0, [], [], None, []), "its own house is not something"
    assert _strip_blocked(s, 500.0, 500.0, 22.0, 16.0, 900.0, 900.0, [], [], None, []), "a house not its own is"
    bundle = (515.0, 500.0, 20.0, 20.0)
    s.placed.append(bundle)
    assert _strip_blocked(s, 500.0, 500.0, 22.0, 16.0, 500.0, 500.0, [], [], None, []), "an unexcused box blocks it"
    assert not _strip_blocked(s, 500.0, 500.0, 22.0, 16.0, 500.0, 500.0, [], [], None, [], skip=frozenset({bundle})), "a skipped box does not"


def test_a_linear_hamlet_stands_in_rows_along_its_streets_and_never_in_ranks() -> None:
    """Feature 291 amendment 3 (research homesteads/155 and 156): a linear hamlet's farms stand in rows along the streets
    its row planned - `seat_rows` - and it takes no rank round; a nucleated hamlet on the same ground is seated by its front
    row and ranks as before. Both seat every household (feature 287 plan D2). (The connector-frontage pass this test used to
    hold is retired: the connector does not exist when the homesteads are seated.)"""
    from l7r.diagram.hamletgen.homesteads import stage_homesteads  # through the MODULE: a stage is not package surface

    for form in ("nucleated", "linear"):
        plan = a_plan(households=10, settlement_form=form)  # each form's own canvas (a row grows it, `LINEAR_CANVAS`)
        plan.seat = hg.seat_cluster(plan)
        s = Settlement(plan.W, plan.H, seed=3)  # the canvas the plan sized (feature 287's seat room on every side)
        s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=10, down_deg=90, water_flow=90, nucleated=True)
        s._nucleated = form == "nucleated"
        s.field_polys.append(list(plan.envelope))
        stage_homesteads(s, plan)
        if form == "nucleated":
            assert len(s.M["houses"]) == 10, "nucleated: every household seated"
        else:
            assert s.M.get("row_street_plans"), "the row planned its streets"
            assert s.M["meta"]["seat_search"].get("rounds", 0) == 0, "no rank round ran"
            assert len(s.M["houses"]) == 10, "linear: every household seated along the streets"


def test_a_row_village_whose_streets_cannot_hold_every_farm_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 287 plan D2 over 291's reported remainder (the GM, 2026-09-30): where no margin's streets hold every farm, the
    site is refused by name - never seated in ranks behind the row, and never shipped short."""
    from l7r.diagram.hamletgen.homesteads import capacity, rows
    from l7r.diagram.hamletgen.homesteads import stages as st

    plan = a_plan(households=10, settlement_form="linear")
    plan.seat = {**hg.seat_cluster(plan), "ladder": []}
    s = Settlement(2400, 1400, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=10, down_deg=90, water_flow=90, nucleated=False)
    s._nucleated = False
    s.field_polys.append(list(plan.envelope))
    monkeypatch.setattr(rows, "seat_rows", lambda s_, plan_, frame, allowed=None: 0)  # the streets hold nobody
    with pytest.raises(capacity.SiteRefused, match="no margin seats all 10"):
        st.stage_homesteads(s, plan)


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
    # the toy's bundles lay a bed or the well pocket where a flank door stands, and a corridor over its own parts is refused
    # since feature 287 M8 (`access.parts_clear`); the seating's count, not the parts, is under test here
    monkeypatch.setattr(access_mod, "parts_clear", lambda *a: True)
    _small_yards(monkeypatch)
    _no_tree(monkeypatch)
    s, plan = _toy_hamlet(10, seed=5)  # seed 5: feature 280 turned no house a quarter away (M26), and seed 3's chain seats five
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
    two hundred feet back does."""
    from l7r.diagram.hamletgen.ways import stage_track

    s, plan = _toy_hamlet(10)
    # NUCLEATED seats two hundred feet back, where they are asked (feature 291). Three hundred fell off the toy's canvas,
    # and the test leaned on the DISPERSED spiral finding room within reach of them (feature 276); a dispersed farm's
    # frame - its grove, the service strip and the lane's room - is over 200 ft across now, and the spiral found none. The
    # spur is a property of the track, whatever form stands back there.
    cx_, cy_ = float(plan.seat["cx"]), float(plan.seat["cy"])
    ox, oy = plan.seat["out"]
    n = 0
    for k in range(-2, 3):
        ax, ay = plan.seat["along"]
        if s.try_place(cx_ + ax * 110 * k + ox * 200, cy_ + ay * 110 * k + oy * 200, "plain"):
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
    from l7r.diagram.hamletgen.consts import BUNDLE_PITCH
    from l7r.diagram.hamletgen.homesteads import stage_homesteads

    s, plan = _toy_hamlet(13)  # 13: feature 280's geometry (M26, M18) fits twelve on the strip
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
    # ...AND A STRIP THAT CANNOT HOLD THE QUOTA IS REFUSED, NAMED (feature 287, homes H14 and H32: every household with its
    # fixtures, or the site refused) - asserted, not suppressed: the ends were offered and taken before the refusal
    plan.seat["ladder"] = []
    tried: list[tuple[float, float]] = []
    real = s.try_place

    def spy(x: float, y: float, *a: object, **kw: object) -> object:
        tried.append((x, y))
        return real(x, y, *a, **kw)

    s.try_place = spy  # type: ignore[method-assign]
    with pytest.raises(SiteRefused, match="no margin seats all 13 households"):
        stage_homesteads(s, plan)
    ss = s._seat_search
    assert ss["rounds"] >= 1, "the ranks ran"
    # ...AND THE SEATS OFFERED PAST THE RANK'S ENDS, along the field: whether one is TAKEN is the corridor's to say (feature
    # 287 M8 - here every run from an end to the access tree passes a front-row homestead's parts, which the overlap matrix
    # keeps a way off), and the rule under test is that they are offered once the back is refused
    row = [(float(h["x"]) - cx) * ax + (float(h["y"]) - cy) * ay for h in s.M["houses"]]
    reach = max(abs(u) for u in row) if row else 0.0
    along = [(x - cx) * ax + (y - cy) * ay for x, y in tried]
    assert any(abs(u) >= reach + BUNDLE_PITCH * 0.9 for u in along), "a seat a pitch past the rank's end was offered"


def test_an_accretion_hamlets_ranks_stand_off_their_lines_and_a_planned_ones_do_not(monkeypatch: pytest.MonkeyPatch) -> None:
    """`stage_homesteads` (feature 261 D22): an `alleys` hamlet's rank seats take the depth jitter, so the ranks behind the
    front row are not all on one line; a `back_lane` hamlet seated the same way keeps its ranks exact. Both seat every
    household."""
    from l7r.diagram.hamletgen.homesteads import stage_homesteads

    # the toy's bundles lay a bed or the well pocket where a flank door stands, and a corridor over its own parts is refused
    # since feature 287 M8 (`access.parts_clear`); the seating's count, not the parts, is under test here
    monkeypatch.setattr(access_mod, "parts_clear", lambda *a: True)

    _no_tree(monkeypatch)
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
@pytest.mark.parametrize("sides", [2, 4])
def test_the_free_ground_changes_no_seat(form: str, scenario: str, sides: int, monkeypatch: pytest.MonkeyPatch) -> None:
    """The same houses, at the same seats, with the index asked first and with it switched off entirely - for a farm
    grove on two sides and on four (feature 291: a dispersed bundle's grove takes its settlement's rolled sides)."""
    from l7r.diagram.hamletgen.homesteads import boundary, stage_homesteads
    from l7r.diagram.settlement import Settlement

    # the toy's bundles lay a bed or the well pocket where a flank door stands, and a corridor over its own parts is refused
    # since feature 287 M8 (`access.parts_clear`); the seating's count, not the parts, is under test here
    monkeypatch.setattr(access_mod, "parts_clear", lambda *a: True)

    def roll():  # type: ignore[no-untyped-def]
        s, plan = _rescue(form) if scenario == "rescue" else _toy_hamlet(15)
        s._nucleated = form == "nucleated"
        s.M["meta"]["grove_sides"] = sides
        if scenario == "rescue":  # the rescue ground cannot hold its quota (D2): refused, and the seats it took compared all the same
            with pytest.raises(SiteRefused):
                stage_homesteads(s, plan)
        elif form == "dispersed" and sides == 4:
            # ...and the open toy cannot hold fifteen ring farms since each carries its well pocket and fixtures (feature 291
            # on 287): refused, its seats compared all the same
            with pytest.raises(SiteRefused):
                stage_homesteads(s, plan)
        else:
            stage_homesteads(s, plan)
        return _seats(s)

    with_index = roll()
    monkeypatch.setattr(boundary.FreeGround, "rect_refused", lambda self, rect: False)
    monkeypatch.setattr(Settlement, "_seat_refused", lambda self, x, y, hw, hh: False)
    monkeypatch.setattr(Settlement, "_bundle_refused", lambda self, geom: False)
    without = roll()
    # the rescue's walled band, each homestead with its fixtures (homes H32) and its share of the wood floor (woods W25):
    # measured, 6 of the walled band's households seat with their wood where 8 did without it. A grove farm's frame - its
    # grove, the service strip on both windward sides and the lane's room - is some 200 ft across, and the 520 ft rescue strip
    # holds 4 two-sided farms and 1 ring (measured 2026-09-29, feature 291) - and 2 two-sided farms once each carries its own
    # well pocket and fixtures (feature 291 on 287, measured 2026-09-30); the open toy 12 rings of 15. The equivalence is
    # what the test is for.
    floor = {("dispersed", "rescue", 2): 2, ("dispersed", "rescue", 4): 1, ("dispersed", "open", 4): 12}.get((form, scenario, sides), 6)
    assert with_index == without
    assert len(with_index) >= floor, len(with_index)


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


def test_every_surely_clear_cell_is_ground_the_corridor_tests_pass() -> None:
    """FreeGround's clear cells (feature 287), asked of the real boundary on the toy: any point inside one passes the
    tests a corridor's samples are asked (`chain_violated` at gap 0 and `hit_points`) - and a corridor's verdict with the
    raster installed is its verdict without it, over corridors that cross clear, taken and edge cells."""
    import random

    from l7r.diagram.hamletgen.homesteads.boundary import install_site_boundary
    from l7r.diagram.settlement._geom.primitives import chain_violated
    from l7r.diagram.settlement.rolling.access import on_site_ground

    s, plan = _rescue("nucleated")
    install_site_boundary(s, plan)
    fg = s._free_ground
    assert len(fg.clear) > 100, "non-vacuity: open ground makes clear cells"
    r = random.Random(287)
    for i, j in r.sample(sorted(fg.clear), 300):
        px, py = fg.x0 + (i + r.random()) * fg.cell, fg.y0 + (j + r.random()) * fg.cell
        assert not chain_violated(px, py, s._site_chains, 0.0) and not s._site_corridors.hit_points([(px, py)]), (px, py)
    verdicts = []
    for i, j in r.sample(sorted(fg.clear), 200):
        a = (fg.x0 + (i + r.random()) * fg.cell, fg.y0 + (j + r.random()) * fg.cell)
        b = (a[0] + r.uniform(-120.0, 120.0), a[1] + r.uniform(-120.0, 120.0))
        with_raster = on_site_ground(s, a, b)
        s._free_ground = None
        assert on_site_ground(s, a, b) == with_raster, (a, b)
        s._free_ground = fg
        verdicts.append(with_raster)
    assert 10 < sum(verdicts) < 190, "non-vacuity: corridors admitted and refused"


def test_the_front_row_loop_stops_once_its_share_is_seated(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """`stage_homesteads`: the row's loop breaks when its share is placed, however many seats the chain still offers - here
    the chain's seats are offered twice over, and the row still takes exactly its share."""
    import math

    from l7r.diagram.hamletgen.consts import CLUSTER_DRAWN_ASPECT
    from l7r.diagram.hamletgen.homesteads import stage_homesteads
    from l7r.diagram.hamletgen.homesteads import stages as st

    monkeypatch.setattr(st, "fixture_quota", lambda *a: {})  # no fixtures: the row's count is under test (homes H32)
    monkeypatch.setattr(st, "install_wood_shares", lambda *a: None)  # ...nor wood shares (woods W25; see the test above)
    # the toy's bundles lay a bed or the well pocket where a flank door stands, and a corridor over its own parts is refused
    # since feature 287 M8 (`access.parts_clear`); the seating's count, not the parts, is under test here
    monkeypatch.setattr(access_mod, "parts_clear", lambda *a: True)
    real = st.front_row
    monkeypatch.setattr(st, "front_row", lambda *a, **k: (lambda seats: seats + seats)(list(real(*a, **k))))
    _small_yards(monkeypatch)
    _no_tree(monkeypatch)
    s, plan = _toy_hamlet(10, seed=5)  # seed 5, as above (feature 280 M26 moved seed 3's chain to five)
    plan.cluster_shape = "round"
    stage_homesteads(s, plan)
    lo, hi = CLUSTER_DRAWN_ASPECT["round"]
    assert s.M["meta"]["seat_search"]["front"] == min(10, max(6, round(math.sqrt(10 * (lo + hi)))))


def _no_tree(monkeypatch: pytest.MonkeyPatch) -> None:
    """The seating's question of the whole access tree (feature 287 wave 6, `ways/tree.admits`), stood aside for a test of
    the seating's COUNTS: on the toy's tight square band it refuses a corridor meeting its host at a needle or crossing a
    neighbor's (measured on the twelve-household toy: 65 needles, 3 crossings) and so moves the counts, which the tree's own
    tests (`tests/hamletgen/ways/test_tree.py`, `tests/settlement/test_access.py`) hold; the cohort seats as before."""
    from l7r.diagram.hamletgen.ways import tree as tree_mod

    monkeypatch.setattr(tree_mod, "seating_judge", lambda s: lambda corridor, geom: True)


def _small_yards(monkeypatch: pytest.MonkeyPatch) -> None:
    """The toy field's front chain seats six homesteads at the 18-tsubo yard median these loop tests were written against;
    at the 25 tsubo feature 280 set (research/homesteads/020) it seats five, below the row's share. The tests are about the
    loop stopping at its share, not the calibration, so they keep the smaller yards."""
    monkeypatch.setattr(Settlement, "YARD_MEDIAN_TSUBO", 18.0)


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


def test_bath_room_seats_abut_their_walls_the_hamlets_seat_first() -> None:
    """`bath_room_seats` (feature 280 M22): each seat's inner edge lies ON its wall; the rolled seat comes first."""
    from l7r.diagram.hamletgen.homesteads.fixtures import bath_room_seats

    seats = bath_room_seats("stable_end", 46.0, 28.0, 9.0, 6.0)
    assert seats[0] == ((-26.0, 0.0, 6.0, 9.0), "stable_end") and len(seats) == 8
    assert all(ly - d / 2 == pytest.approx(14.0) for (_lx, ly, _w, d), _n in seats if ly > 14.0), "the door seats on the front wall"
    assert bath_room_seats("floored_rooms", 46.0, 28.0, 9.0, 6.0)[0] == ((26.0, 0.0, 6.0, 9.0), "floored_rooms")
    door = [q for q, n in bath_room_seats("main_door", 46.0, 28.0, 9.0, 6.0) if n == "main_door"]
    assert len(door) == 2 and all(q[1] == 17.0 for q in door), "on the front wall, either side of the door"
    past = [q for q, n in bath_room_seats("main_door", 46.0, 28.0, 9.0, 6.0, (0.0, 10.0)) if n == "main_door"]
    assert [q[0] for q in past[2:]] == [17.5, -17.5], "then just past the yard's sides, on the front wall"
    assert len([q for q, n in bath_room_seats("main_door", 46.0, 28.0, 9.0, 6.0, (0.0, 20.0)) if n == "main_door"]) == 2, "past the wall's end: none"


def test_the_privy_and_the_bath_room_take_a_rolled_size_and_the_wood_shed_goes_to_the_larger_houses() -> None:
    """`fixture_ft` and the lots' `larger_first` (feature 280, research/homesteads/750, 740, 720; carried into feature 287's
    lots): the privy is one of the Kakimochi table's sixteen, the bath 6 ft out by 6-12 ft along - each rolled off the
    household's position roll - and the wood shed's quota goes to the larger houses first."""
    from l7r.diagram.hamletgen.homesteads import fixtures as fx
    from l7r.diagram.settlement.farm_fixtures import FIXTURE_FT
    from l7r.diagram.settlement.homestead_parts.fixture_seats import FixtureForms, fixture_ft
    from l7r.diagram.settlement.rolling.lot import HouseholdLots, quota_carriers

    s = Settlement(W=900, H=700, seed=7)
    forms = FixtureForms()
    sizes = {fixture_ft("privy", forms, lambda salt, k=k: s._hjit(10.0 * k, 3.0 * k, salt)) for k in range(80)}
    assert sizes <= set(fx.PRIVY_SIZES_FT) and len(sizes) > 6 and len(fx.PRIVY_SIZES_FT) == 16
    baths = [fixture_ft("bath", forms, lambda salt, k=k: s._hjit(10.0 * k, 3.0 * k, salt)) for k in range(40)]
    assert all(fx.BATH_LENGTH_FT[0] <= w <= fx.BATH_LENGTH_FT[1] and d == fx.BATH_DEPTH_FT for w, d in baths) and len({w for w, _d in baths}) > 3
    assert fixture_ft("coop", forms, lambda _salt: 0.5) == FIXTURE_FT["coop"] and fixture_ft("privy", forms) == FIXTURE_FT["privy"], "one size, or the default without a roll"
    lots = HouseholdLots(7, 12, fixture_shares={"woodpile": 0.4, "coop": 0.4})
    area = [lf * df for lf, df in lots.sizes]
    shed = [k for k in range(12) if lots.fixtures["woodpile"][k]]
    assert len(shed) == sum(quota_carriers(7, "fixture_woodpile", 12, 0.4)) == 5
    assert min(area[k] for k in shed) >= max(area[k] for k in range(12) if k not in shed), "the larger houses first"
    assert lots.fixtures["coop"] == quota_carriers(7, "fixture_coop", 12, 0.4), "every other kind by the shuffled quota"


def test_the_drawn_forms_are_recorded_beside_the_rolled_knob() -> None:
    """`record_drawn_forms` (the 269 landing's reviews; feature 280): the bath rooms by the wall each took."""
    from l7r.diagram.hamletgen.homesteads.fixtures import record_drawn_forms

    m = {"meta": {}, "farm_fixtures": [{"kind": "bath", "seat": "main_door"}, {"kind": "bath", "seat": "stable_end"}, {"kind": "bath", "seat": "main_door"}, {"kind": "coop"}]}
    record_drawn_forms(m)
    assert m["meta"]["bath_seats_drawn"] == {"main_door": 2, "stable_end": 1} and "woodpile_forms_drawn" not in m["meta"]


def test_fixture_form_names_the_drawn_form() -> None:
    """`fixture_form` (feature 150): the manure pit on a pit hamlet, else the plain glyph."""
    from l7r.diagram.hamletgen.homesteads.fixtures import fixture_form

    assert fixture_form("manure", "pit") == "pit" and fixture_form("manure", "heap") is None and fixture_form("woodpile", "pit") is None


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


def test_a_large_privy_s_sun_side_reach_keeps_its_near_edge_where_a_one_ken_privy_s_is() -> None:
    """Feature 280 (settlement-review of Sawada): a 24 x 12 ft privy never fitted the one-ken reach and fell to the north-east."""
    from l7r.diagram.hamletgen.homesteads.fixtures import PRIVY_SUN_MAX_FT, privy_sun_reach_ft

    assert privy_sun_reach_ft(6.0, 6.0) == PRIVY_SUN_MAX_FT == privy_sun_reach_ft(5.0, 5.0)
    assert privy_sun_reach_ft(24.0, 12.0) == PRIVY_SUN_MAX_FT + 9.0


def test_strip_blocked_refuses_another_farmhouse_as_drawn() -> None:
    """The every-other-farmhouse arm of `_strip_blocked` (feature 280: the re-packed pool rolls no longer reach it)."""
    s, _plan = _strip_settlement()
    s.M["houses"] = [{"x": 500.0, "y": 500.0, "w": 46.0, "h": 28.0, "rot": 0.0}]
    blocked = hg.homesteads._strip_blocked
    assert blocked(s, 500, 500, 30, 20, 300, 300, [], [], None, []) is True, "a neighbor's house"
    assert blocked(s, 500, 500, 30, 20, 500, 500, [], [], None, []) is False, "its own house is excused"


def test_a_household_strip_keeps_out_of_the_windbreak_belt() -> None:
    """Feature 280 (settlement-review of Inashiro): a strip seated in the belt painted its culms over the conifers."""
    from l7r.diagram.hamletgen.homesteads.bamboo import in_belt

    belt = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    assert in_belt(belt, 50.0, 50.0, 10.0, 10.0) and in_belt(belt, 104.0, 50.0, 10.0, 10.0), "inside, or a corner reaching in"
    assert not in_belt(belt, 200.0, 50.0, 10.0, 10.0) and not in_belt(None, 50.0, 50.0, 10.0, 10.0) and not in_belt([(0.0, 0.0)], 1, 1, 1, 1)
