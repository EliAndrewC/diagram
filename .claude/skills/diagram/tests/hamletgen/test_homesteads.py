"""Unit tests for the houses, their appurtenances, and the wells (`hamletgen/homesteads.py`).

Split from test_hamletgen.py by feature 111; test bodies verbatim. See hamletgen/CLAUDE.md.
"""

import math

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen.homesteads.fixtures import nearer_own_house
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


def test_a_house_beside_open_water_needs_no_rescue_well() -> None:
    """`place_wells`' rescue pass exists for a household the grid left dry, and it skips any house
    already watered by a stream, channel or pond - the check's own verdict, so the rescue cannot
    plant a well the gate never asked for. The companion of the `M={}` case above, which has no
    surface water and so takes the other branch."""
    from types import SimpleNamespace

    houses = [{"x": 500, "y": 500}, {"x": 2000, "y": 2000}]  # the second sits far outside the first well's reach...
    s = SimpleNamespace(well_at=lambda x, y: math.hypot(x - 500, y - 500) < 60.0, M={"streams": [{"poly": [[1900, 1900], [2100, 2100]], "w": 9}]})  # ...but a stream runs right past it
    plan = SimpleNamespace(spec=SimpleNamespace(households=6), ftpx=1.0)
    assert hg.place_wells(s, plan, houses) == 1, "the watered house is skipped by the rescue, so only the first well is sited"  # type: ignore[arg-type]


def test_a_seat_on_forbidden_ground_is_refused() -> None:
    """`generate` re-rolls a stranding map with the offending ground passed as `avoid`; the seat loops
    honour it through `_seat_allowed`. Half a bundle pitch is the radius - enough to clear the pocket,
    not so much that the retry merely nudges the same steading along it."""

    class _S:
        pass

    s = _S()
    assert hg.homesteads._seat_allowed(s, 100.0, 100.0) is True  # nothing forbidden yet
    s._avoid_seats = [(100.0, 100.0)]
    assert hg.homesteads._seat_allowed(s, 100.0, 100.0) is False  # dead on the forbidden seat
    assert hg.homesteads._seat_allowed(s, 140.0, 100.0) is False  # inside half a bundle pitch
    assert hg.homesteads._seat_allowed(s, 400.0, 400.0) is True  # well clear


def test_farmstead_fixtures_roll_a_share_in_each_band_and_seat_one_of_a_kind_per_house() -> None:
    """Feature 133 T53-T59: the shares are rolled once per map inside the researched bands and declared
    for the gate; each house keeps at most one of a kind, every fixture names its house, and the
    shrine count never exceeds the share (the GM: "very rare, but notable")."""
    from l7r.diagram.hamletgen.homesteads import FIXTURE_BANDS, farmstead_fixtures
    from l7r.diagram.settlement import Settlement

    s = Settlement(W=900, H=700, seed=7)
    s.meta(name="T", scale="hamlet", ftpx=1)
    houses = [{"x": 200.0 + 110 * i, "y": 300.0 + 90 * (i % 2), "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "N"} for i in range(6)]
    for h in houses:
        s.M["houses"].append(dict(h))
        s.placed.append((h["x"], h["y"], h["w"], h["h"]))
    n = farmstead_fixtures(s, a_plan(), houses)
    shares = s.M["meta"]["farm_fixtures"]
    assert set(shares) == set(FIXTURE_BANDS) and all(lo <= shares[k] <= hi for k, (lo, hi) in FIXTURE_BANDS.items())
    recs = s.M["farm_fixtures"]
    assert n == len(recs) + len(s.M["persimmons"]) and n > 0
    owners = {(r["kind"], tuple(r["of"])) for r in recs}
    assert len(owners) == len(recs), "one of a kind per house"
    assert sum(r["kind"] == "shrine" for r in recs) <= max(1, round(shares["shrine"] * len(houses)))
    assert all(tuple(r["of"]) in {(h["x"], h["y"]) for h in houses} for r in recs)
    assert len(s.placed) == len(houses) + n, "every seated fixture reserves its ground"


def test_farmstead_fixtures_honor_the_spec_floor() -> None:
    """Feature 133 T61 (GM 2026-08-27: "a min number of something which may or may not appear"): a spec'd
    floor forces the kind onto houses that lack it after the rolled pass, and declares itself in meta."""
    from l7r.diagram.hamletgen.homesteads import farmstead_fixtures
    from l7r.diagram.settlement import Settlement

    s = Settlement(W=900, H=700, seed=7)
    s.meta(name="T", scale="hamlet", ftpx=1)
    houses = [{"x": 200.0 + 110 * i, "y": 300.0 + 90 * (i % 2), "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "N"} for i in range(6)]
    for h in houses:
        s.M["houses"].append(dict(h))
        s.placed.append((h["x"], h["y"], h["w"], h["h"]))
    plan = a_plan()
    plan.fixtures_min = {"shrine": 2, "bath": 3}
    farmstead_fixtures(s, plan, houses)
    kinds = [r["kind"] for r in s.M["farm_fixtures"]]
    assert kinds.count("shrine") >= 2 and kinds.count("bath") >= 3
    assert s.M["meta"]["farm_fixtures_min"] == {"shrine": 2, "bath": 3}
    owners = {(r["kind"], tuple(r["of"])) for r in s.M["farm_fixtures"]}
    assert len(owners) == len(s.M["farm_fixtures"]), "the floor never doubles a house"


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


def test_trunk_blocked_refuses_the_canvas_edge_and_a_record_without_a_footprint() -> None:
    """Feature 146: two arms of the trunk test - a trunk hanging off the canvas, and a record in one of the
    scanned lists that carries no `x` at all (a synthetic entry another check keeps), which is skipped
    rather than raising."""
    s, _plan = _strip_settlement()
    blocked = hg.homesteads._trunk_blocked
    assert blocked(s, 20, 500, 10, [], [], None, []) is True, "over the canvas edge"
    s.M["persimmons"] = [{"note": "a record with no footprint at all"}]
    assert blocked(s, 500, 500, 10, [], [], None, []) is False, "the footprint-less record is skipped"
    s.M["persimmons"].append({"x": 500.0, "y": 500.0, "w": 20.0, "h": 20.0})
    assert blocked(s, 500, 500, 10, [], [], None, []) is True, "and a real one blocks"


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


def test_a_woodpile_stacks_against_the_kura_when_the_shed_is_not_on_the_north_side() -> None:
    """The stack stands against whichever wall is free. Which wall that is depends on `shed_side`, and
    every live hamlet rolls the same side - so the other seat list had never been built."""
    from l7r.diagram.hamletgen.homesteads import farmstead_fixtures

    plan = a_plan()
    s = Settlement(1400, 1400, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=6, down_deg=90, water_flow=90)
    houses = [{"x": 700.0, "y": 700.0, "w": 46.0, "h": 28.0, "rot": 0.0, "kind": "plain", "shed_side": "S", "wealth": 1.0}]
    farmstead_fixtures(s, plan, houses)
    assert s.M["farm_fixtures"], "the steading's fixtures are seated round it"
    assert all(abs(f["x"] - 700.0) < 200 and abs(f["y"] - 700.0) < 200 for f in s.M["farm_fixtures"])


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


def test_nearer_own_house_with_no_other_houses_is_unambiguously_its_owners() -> None:
    """Feature 174: the no-neighbors branch, lifted out to take two tuples rather than a settlement.

    Its own docstring says that is why it exists. With nobody else to be nearer to, the seat scores
    rank 0 and a NEGATIVE margin - the sign convention the sort depends on - so the margin's sign is
    asserted, not just the rank.
    """
    rank, dmine, margin = nearer_own_house((30.0, 40.0, 0.0, 0.0), 0.0, 0.0, 1.0, 0.0, ())
    assert rank == 0
    assert dmine == pytest.approx(50.0), "3-4-5 from its own house"
    assert margin == pytest.approx(-50.0), "negative: unambiguously this house's"


def test_a_trunk_on_a_stream_is_refused_by_the_water_arm_alone() -> None:
    """`_trunk_blocked`'s water arm reached through `Footing` (feature 220), on a sheet that carries NOTHING but the
    stream - so no earlier arm (a paddy ring, a dry plot, a lane) can be the one that refused it."""
    from l7r.diagram.hamletgen.homesteads import _trunk_blocked
    from l7r.diagram.settlement import Settlement

    s = Settlement(1400, 1400, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1, down_deg=90)
    s.M["streams"] = [{"poly": [[100.0, 700.0], [1300.0, 700.0]], "w": 60}]
    assert _trunk_blocked(s, 700.0, 700.0, 20.0, [], [], None, []) is True
    assert _trunk_blocked(s, 700.0, 200.0, 20.0, [], [], None, []) is False
    # ...and the DRY-PLOT arm the same way: a trunk corner standing in a dry plot, nothing else on the sheet
    s.M["streams"] = []
    s.M["dry_plots"] = [{"poly": [(650.0, 150.0), (750.0, 150.0), (750.0, 250.0), (650.0, 250.0)]}]
    assert _trunk_blocked(s, 700.0, 200.0, 20.0, [], [], None, []) is True
    assert _trunk_blocked(s, 700.0, 700.0, 20.0, [], [], None, []) is False


def test_the_shrine_budget_refuses_a_second_house_that_rolls_one(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """`farmstead_fixtures`: the shrine share is a CEILING - "very rare, but notable" - so once the budget the share
    allows is spent, a later house that rolls a shrine gets none, whatever its roll says."""
    from l7r.diagram.hamletgen.homesteads import fixtures as fx
    from l7r.diagram.settlement import Settlement

    monkeypatch.setitem(fx.FIXTURE_BANDS, "shrine", (0.5, 0.5))
    s = Settlement(W=1200, H=700, seed=7)
    s.meta(name="T", scale="hamlet", ftpx=1)
    passing = [(x, y) for x in range(150, 1100, 110) for y in (250.0, 400.0) if s._hjit(float(x), y, fx._SALT["shrine"]) < 0.5]
    assert len(passing) >= 3
    houses = [{"x": float(x), "y": float(y), "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "N"} for x, y in passing[:3]] + [
        {"x": 1150.0, "y": 600.0, "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "N"}
    ]
    for h in houses:
        s.M["houses"].append(dict(h))
        s.placed.append((h["x"], h["y"], h["w"], h["h"]))
    fx.farmstead_fixtures(s, a_plan(), houses)
    shrines = [r for r in s.M["farm_fixtures"] if r["kind"] == "shrine"]
    assert len(shrines) == 2, "the share allows two of four; the third house that rolled one is refused"


def _toy_hamlet(households: int, seed: int = 3):  # type: ignore[no-untyped-def]
    """The linear toy's setup, for the stage's own branches: a square field, a seat band, the connector."""
    plan = a_plan(households=households)
    plan.seat = hg.seat_cluster(plan)
    plan.settlement_form = "nucleated"
    s = Settlement(1400, 1400, seed=seed)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=households, down_deg=90, water_flow=90, nucleated=True)
    s.field_polys.append(list(plan.envelope))
    cx_, cy_ = float(plan.seat["cx"]), float(plan.seat["cy"])
    s.M["lanes"] = [{"pts": [[cx_ - 400, cy_], [cx_ + 400, cy_]], "w": 6, "connector": True}]
    return s, plan


def test_the_front_row_stops_at_its_share_and_the_ranks_seat_the_rest() -> None:
    """Feature 227 D8: the row takes about sqrt(N x A) houses - here fewer than the chain could seat - and stops;
    the ranks behind seat the rest."""
    from l7r.diagram.hamletgen.consts import CLUSTER_DRAWN_ASPECT
    from l7r.diagram.hamletgen.homesteads import stage_homesteads

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

    s, plan = _toy_hamlet(20)
    # the ground beyond 260 ft of the seat is no-build, so the ranks run out of room and the rescue's wider cloud
    # throws seeds the band refuses
    cx_, cy_ = float(plan.seat["cx"]), float(plan.seat["cy"])
    s.block_polys.append([(cx_ - 2000.0, cy_ - 2000.0), (cx_ + 2000.0, cy_ - 2000.0), (cx_ + 2000.0, cy_ - 260.0), (cx_ - 2000.0, cy_ - 260.0)])
    s.block_polys.append([(cx_ - 2000.0, cy_ + 260.0), (cx_ + 2000.0, cy_ + 260.0), (cx_ + 2000.0, cy_ + 2000.0), (cx_ - 2000.0, cy_ + 2000.0)])
    stage_homesteads(s, plan)
    ss = s.M["meta"]["seat_search"]
    assert ss["rounds"] >= 5, "the rescue ran"
    assert len(s.M["houses"]) < 20, "...and the quota stayed short: the ground, not the search, was the limit"


def test_a_cluster_standing_off_its_field_gets_the_spur_to_it() -> None:
    """`stage_track`'s field spur is laid when the path from the cluster's edge to the field is longer than 20 ft; the
    pool's clusters front the paddy at the wall rule now (feature 227), so no shipped map lays one - a cluster seated
    three hundred feet back does."""
    from l7r.diagram.hamletgen.ways import stage_track

    s, plan = _toy_hamlet(10)
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
    stage_homesteads(s, plan)
    ss = s.M["meta"]["seat_search"]
    assert ss["rounds"] >= 1, "the ranks ran"
    assert len(s.M["houses"]) > ss["front"], "the only seats left were the ends, and the cluster took them"
