"""Split from test_ways.py by feature 173 - see this directory's CLAUDE.md."""

import math

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen.ways import serve as _serve

from ._builders import _StubSettlement


def test_the_shadow_measure_counts_the_near_points_and_the_longest_unbroken_stretch() -> None:
    """`shadow_measure` (lifted from `_lay_web_lane` by feature 293 so the pool's finished-map test reads the same
    measure): a way 18 ft beside another for 240 ft, then turning away, shadows it for 252 ft - the side-by-side pair a
    re-packed Sawada shipped - and one that leaves it square is near it only for its first 30 ft."""
    road = [((0.0, 0.0), (400.0, 0.0))]
    beside = [(float(x), 18.0) for x in range(0, 244, 4)] + [(240.0, 18.0 + d) for d in range(4, 64, 4)]  # every step 4 ft
    near, stretch = _serve.shadow_measure(beside, road)
    assert near == 63 and stretch == pytest.approx(252.0), "the 61 points at 18 ft and the first two of the turn, at 22 and 26"
    away = [(100.0, float(y)) for y in range(0, 200, 4)]
    assert _serve.shadow_measure(away, road) == (8, pytest.approx(32.0))


def test_a_way_shadowed_past_a_pitch_names_the_way_it_runs_beside() -> None:
    """`shadowed_by` (feature 293 on 291): way against way, the longest unbroken stretch within `WEB_SHADOW_FT` past a
    `BUNDLE_PITCH`; a way whose box stands off this one's is not measured, and a way of one point shadows nothing."""
    road = [(0.0, 0.0), (400.0, 0.0)]
    beside = [(0.0, 18.0), (240.0, 18.0), (240.0, 80.0)]
    short = [(0.0, 18.0), (60.0, 18.0)]
    far = [(0.0, 500.0), (400.0, 500.0)]
    ways = [road, beside, short, far, [(5.0, 5.0)]]
    assert _serve.shadowed_by(ways, 1) == 0
    assert _serve.shadowed_by(ways, 2) is None, "60 ft beside it is under a pitch"
    assert _serve.shadowed_by(ways, 3) is None, "a way 500 ft off is never measured"
    assert _serve.shadowed_by(ways, 4) is None
    assert _serve.sampled([(0.0, 0.0), (10.0, 0.0)]) == [(0.0, 0.0), (5.0, 0.0), (10.0, 0.0)]


def test_a_web_lane_may_not_run_the_length_of_a_shelter_belt() -> None:
    """Crossing a belt costs it a lane's width of wall, which is a fair price for a way with
    somewhere to be. Running ALONG it splits one wind wall into two thinner ones - measured, a back
    lane 237 of 237 ft inside the belt, having deleted 15 of its 169 clumps."""
    # Houses at both ends so the run is not trimmed back before the belt rule is reached - the trim
    # runs first on purpose (see `_trim_to_service`), and a run serving nothing is dropped for that
    # reason rather than this one.
    ends = [(20.0, 190.0), (285.0, 190.0)]
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]], houses=ends)
    belt = [(-50.0, 100.0), (400.0, 100.0), (400.0, 160.0), (-50.0, 160.0)]
    lengthwise = [(float(x), 130.0) for x in range(10, 300, 5)]
    assert hg.ways._lay_web_lane(s, lengthwise, [], [], [], belts=[belt], houses=ends) is False
    crossing = [(200.0, float(y)) for y in range(60, 205, 5)]
    assert hg.ways._lay_web_lane(s, crossing, [], [], [], belts=[belt], houses=[(200.0, 70.0), (200.0, 195.0)]) is True, "crossing the belt is allowed"


def test_a_web_lane_that_cannot_reach_the_network_draws_a_link_or_is_refused() -> None:
    """A run further off than the touch tolerance gets a link drawn to the network - and if the link
    cannot be drawn, the run is not drawn either. Refusing is the right answer: the alternative is
    ink that looks like a way and is not one."""
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]], houses=[(150.0, 200.0)])
    detached = [(120.0, float(y)) for y in range(150, 255, 5)]
    before = len(s.M["lanes"])
    assert hg.ways._lay_web_lane(s, detached, [], [], [], houses=[(150.0, 200.0)]) is True
    assert len(s.M["lanes"]) == before + 2, "the link and the run"

    walled = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]], houses=[(900.0, 200.0)])
    fence = [(300.0, -500.0), (320.0, -500.0), (320.0, 900.0), (300.0, 900.0)]
    far = [(880.0, float(y)) for y in range(150, 255, 5)]
    assert hg.ways._lay_web_lane(walled, far, [fence], [], [], houses=[(900.0, 200.0)]) is False
    assert len(walled.M["lanes"]) == 1, "nothing drawn when the link cannot be made"


def test_a_web_lane_is_refused_when_its_link_is_blocked_though_the_gap_is_short() -> None:
    """The gap is well inside the search radius, so the run is not rejected for distance - it is
    rejected because the ground between it and the network will not take a lane. Refusing is the
    point: ink that looks like a way and is not one is worse than a house left for the footpath
    pass."""
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]], houses=[(120.0, 200.0)])
    fence = [(40.0, -400.0), (60.0, -400.0), (60.0, 800.0), (40.0, 800.0)]
    run = [(120.0, float(y)) for y in range(150, 255, 5)]
    assert hg.ways._lay_web_lane(s, run, [fence], [], [], houses=[(120.0, 200.0)]) is False
    assert len(s.M["lanes"]) == 1, "neither the link nor the run is drawn"


def test_a_web_lane_snaps_its_end_onto_the_way_it_almost_meets() -> None:
    """A run that stops a few feet short of the way it aims at renders as a gap, whatever the gate
    thinks of it - acceptance tolerances are not ink tolerances. So an end within `_LANE_JOIN_FT` is
    extended onto the way it meets, but ONLY if the ground between is clear: adding those few feet
    blind put lane ink across houses and garden beds on every cohort seed the moment snapping went
    in. This pins both halves - the snap, and a run whose snap is not walkable refused whole (feature 328)."""
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]])
    before = len(s.M["lanes"])
    # SAMPLED like a real run: the shadow clause caps the longest UNBROKEN shadowed stretch at a
    # bundle pitch, and with only two vertices the sample step IS the whole run, so a two-point run
    # trips it on its joining end alone.
    run = [(200.0 - 182.0 * i / 10.0, 200.0) for i in range(11)]
    assert hg.ways._lay_web_lane(s, run, [], [], []) is True
    assert len(s.M["lanes"]) == before + 1
    drawn = [(round(x), round(y)) for x, y in s.M["lanes"][-1]["pts"]]
    assert (0, 200) in drawn, drawn
    # ...and the same run refused the snap when a steading stands in the gap
    s2 = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]])
    wall = [(2.0, 180.0), (16.0, 180.0), (16.0, 220.0), (2.0, 220.0)]
    # ...not drawn stopping short either (feature 328, 0081: ends within 25 ft are joined at a single point): refused
    assert hg.ways._lay_web_lane(s2, run, [], [wall], []) is False and len(s2.M["lanes"]) == 1


def test_a_web_lane_that_arrives_early_keeps_the_long_half() -> None:
    """The hairpin cure, on the side the existing test does not reach: when a run's closest approach
    to the network is an interior point, the SHORT half is the stub to drop - and which half is short
    is not always the tail. A run that touches the network 20 ft in and then travels 140 ft away is
    one lane arriving, not a lane with a tail; keeping the 20 ft head instead would delete the whole
    way and leave the houses it serves unserved."""
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]], houses=[(160.0, 230.0)])
    run = [(40.0, 200.0), (20.0, 200.0), (60.0, 200.0), (110.0, 200.0), (160.0, 200.0)]
    assert hg.ways._lay_web_lane(s, run, [], [], [], houses=[(160.0, 230.0)]) is True
    drawn = s.M["lanes"][-1]["pts"]
    assert [tuple(q) for q in drawn] == [(0.0, 200.0), *run[1:]], "the 20 ft head is dropped, the 140 ft body kept, its cut end carried onto the way (0081, feature 328)"


def test_a_web_lane_end_already_near_the_network_is_SNAPPED_onto_it() -> None:
    """The third arm of `_lay_web_lane`'s junction logic, and the only one with no test of its own: an
    end already inside `_LANE_JOIN_FT` is not linked and not refused - it is EXTENDED onto the way it
    meets, so the junction reads as a touch rather than a 12 ft gap. The snap is conditional on the
    ground between being walkable, because adding those few feet blind once put lane ink across houses
    and garden beds.

    Held here because its coverage was CACHE-DEPENDENT rather than absent (found 2026-08-19). The
    branch is exercised by regenerating a pool map, so a gate run that follows a `consts.py` change
    regenerates and covers it, while a gate run on an unchanged tree serves those maps from the gen
    cache and never executes the line. Same code, same seeds, coverage green or red depending on
    whether a cache happened to be warm - which is the flakiest kind of pass there is, and reads as a
    mystery regression when it flips."""
    lane = [(0.0, 0.0), (0.0, 400.0)]
    house = (160.0, 230.0)
    s = _StubSettlement(lanes=[lane], houses=[house])
    run = [(20.0, 200.0), (60.0, 200.0), (110.0, 200.0), (160.0, 200.0)]
    assert hg.ways._lay_web_lane(s, run, [], [], [], houses=[house]) is True
    drawn = [tuple(q) for q in s.M["lanes"][-1]["pts"]]
    assert drawn[0] == (0.0, 200.0), f"the near end should be snapped onto the lane, got {drawn[:2]}"
    assert drawn[1:] == run, "the rest of the run is unchanged - snapping adds a point, it does not re-route"


# ---- feature 126: ways split by provenance, and the settlement form ------------------------------


def test_the_form_roll_is_deterministic_and_covers_all_three_forms() -> None:
    """A seed must always produce the same form, and the cohort must actually exercise each one.

    The second half matters as much as the first: a form weighted so rarely that no cohort seed
    rolls it is a form nothing tests, and the whole point of the knob is that players can tell two
    settlements apart."""
    forms = {}
    for seed in range(48):
        plan = hg.plan_site(hg.HamletSpec(name=f"Roll-{seed}", seed=seed, households=12))
        again = hg.plan_site(hg.HamletSpec(name=f"Roll-{seed}", seed=seed, households=12))
        assert plan.settlement_form == again.settlement_form, f"seed {seed} rolled two different forms"
        forms[plan.settlement_form] = forms.get(plan.settlement_form, 0) + 1
    # ALL THREE FORMS ROLL AGAIN (feature 291): the per-house grove's four defects fixed at the seat, the forms back at
    # feature 126's 5 : 3 : 2. Every form must come up within these 48 seeds, and nucleated stays the commonest.
    assert set(forms) == {"nucleated", "dispersed", "linear"}, f"every form rolls; got {forms}"
    assert forms["nucleated"] > max(forms["dispersed"], forms["linear"]), forms


def test_an_explicit_form_on_the_spec_beats_the_roll() -> None:
    """A pool gen pins the form the way it pins every other knob."""
    plan = hg.plan_site(hg.HamletSpec(name="Pinned", seed=3, households=12, settlement_form="dispersed"))
    assert plan.settlement_form == "dispersed"


def test_a_web_lane_of_fewer_than_two_points_is_never_laid() -> None:
    """A run must be a LINE to be a lane. The guard fires twice - once on the run as offered, and
    again after `_trim_to_service` has cut it back, because trimming is what can reduce a real run to
    a single point. Both were excluded from coverage on the grounds that the callers never offer one;
    the function is the one that has to be sure, and it answers False rather than recording a lane
    with no length."""
    from l7r.diagram.hamletgen.ways.serve import _lay_web_lane
    from tests.hamletgen.ways._builders import _StubSettlement

    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]], houses=[(80.0, 200.0)])
    s.M.setdefault("meta", {"ftpx": 1})
    assert _lay_web_lane(s, [(50.0, 50.0)], [], [], []) is False, "a single point is not a run"
    assert _lay_web_lane(s, [], [], [], []) is False, "and neither is nothing at all"


def test_a_web_lane_that_shadows_the_network_for_most_of_its_length_is_refused() -> None:
    """A run lying within `WEB_SHADOW_FT` of an existing way for more than 60% of its points is the same
    way again - a second tread beside the first - and is refused before any join is attempted. The pool
    stopped reaching this branch when the homesteads re-seated (feature 226); the rule is unchanged."""
    ends = [(6.0, 60.0), (6.0, 340.0)]
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]], houses=ends)
    beside = [(6.0, float(y)) for y in range(50, 355, 5)]  # 6 ft east of the way, its whole length
    assert hg.ways._lay_web_lane(s, beside, [], [], [], houses=ends) is False
    assert len(s.M["lanes"]) == 1, "nothing was drawn"


def test_a_web_lane_that_shadows_the_network_for_a_whole_pitch_is_refused_even_when_most_of_it_is_clear() -> None:
    """The second shadow rule: a run mostly in open ground still counts as the same way again when one CONTIGUOUS
    stretch of it, longer than a bundle pitch, lies within `WEB_SHADOW_FT` of the network."""
    ends = [(6.0, 5.0), (306.0, 150.0)]
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 150.0)]], houses=ends)
    run = [(6.0, float(y)) for y in range(0, 155, 5)] + [(6.0 + 5.0 * k, 150.0) for k in range(1, 61)]  # 150 ft beside the way, then 300 ft away from it
    assert hg.ways._lay_web_lane(s, run, [], [], [], houses=ends) is False
    assert len(s.M["lanes"]) == 1


# ---- the late tidy-up, lifted to module level (feature 227) ----------------------------------------


def test_the_late_pass_pulls_back_an_end_that_still_reaches_nothing() -> None:
    """`tidy_lane_ends` is the last pass over every lane end, after the stragglers. Its shortening branch had no
    reader but the shipped rolls, and the moment the end rule learned to see a tread that had ARRIVED at a dooryard
    no pool map needed shortening - so the safety net went untested while still being the thing that catches the
    seed that needs it. Lifted out and driven here with a stub, per the GM's 2026-08-28 ruling on inner functions.

    The run below leaves its west end 900 ft from the house, the field and every other way."""
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]], houses=[(60.0, 200.0)])
    s.M["lanes"].append({"pts": [[-900.0, 200.0], [-100.0, 200.0], [20.0, 200.0]], "w": 3})
    hg.ways.tidy_lane_ends(s, [(200.0, 0.0), (600.0, 0.0), (600.0, 400.0), (200.0, 400.0)])
    kept = [(float(x), float(y)) for x, y in s.M["lanes"][-1]["pts"]]
    assert kept[0] != (-900.0, 200.0), "the 900 ft head into nothing is pulled back"
    assert kept[-1] == (20.0, 200.0), "and the end that stands at the house is kept"


def test_the_late_pass_leaves_a_lane_whose_ends_both_serve() -> None:
    """It only ever SHORTENS, and it shortens nothing when there is nothing to shorten - which is the state every
    shipped hamlet is in since the end rule started reading arrival."""
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]], houses=[(60.0, 200.0)])
    s.M["lanes"].append({"pts": [[10.0, 200.0], [60.0, 240.0]], "w": 3})
    before = [list(q) for q in s.M["lanes"][-1]["pts"]]
    hg.ways.tidy_lane_ends(s, [(200.0, 0.0), (600.0, 0.0), (600.0, 400.0), (200.0, 400.0)])
    assert [list(q) for q in s.M["lanes"][-1]["pts"]] == before


def test_the_late_pass_drops_a_lane_trimmed_to_a_nub() -> None:
    """A lane that serves nothing past the tread it leaves goes (feature 261, Kashikawa's field spur): trimmed to service it
    kept a stub shorter than a lane, and the pass used to leave such a lane whole - its head a plank to nothing."""
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]], houses=[(600.0, 600.0)])
    s.M["lanes"].append({"pts": [[0.0, 100.0], [-12.0, 100.0], [-400.0, 100.0]], "w": 3})
    hg.ways.tidy_lane_ends(s, [(200.0, 0.0), (600.0, 0.0), (600.0, 400.0), (200.0, 400.0)])
    assert len(s.M["lanes"]) == 1, "the nub is dropped"
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]], houses=[(-20.0, 700.0)])
    s.M["lanes"].append({"pts": [[0.0, 380.0], [-15.0, 395.0], [-20.0, 690.0]], "w": 3})
    hg.ways.tidy_lane_ends(s, [(200.0, 0.0), (600.0, 0.0), (600.0, 400.0), (200.0, 400.0)])
    assert len(s.M["lanes"]) == 2, "a lane that is some house's only way stays"


def test_a_web_lane_shadowing_another_for_a_bundles_pitch_is_refused() -> None:
    """`_lay_web_lane`'s second shadow clause. The fraction catches a short lane laid alongside another for all
    of its length; this one catches a LONG lane that eventually diverges - its unbroken shadowed stretch is
    capped at one bundle pitch, because a run that hugs an existing tread for that far is a doubled band
    whichever way it ends up going."""
    s = _StubSettlement(lanes=[[(0.0, 0.0), (600.0, 0.0)]], houses=[(600.0, 1200.0)])
    # a run that hugs the lane for its first 300 ft (well past a bundle pitch) and then leaves it, so the
    # FRACTION clause passes (most of the run is clear) while the unbroken shadowed stretch does not
    run = [(float(x), 2.0) for x in range(0, 320, 20)] + [
        (420.0, 400.0),
        (520.0, 900.0),
        (600.0, 1500.0),
        (640.0, 2100.0),
        (660.0, 2700.0),
        (680.0, 3300.0),
        (700.0, 3900.0),
        (720.0, 4500.0),
        (740.0, 5100.0),
        (760.0, 5700.0),
        (780.0, 6300.0),
        (800.0, 6900.0),
    ]
    assert not _serve._lay_web_lane(s, run, [], [], [], houses=[(600.0, 1200.0)])


def test_the_overrun_past_the_connector_is_cut_and_the_connector_left() -> None:
    """`cut_the_overruns` (feature 261, lifted from `stage_web`): a lane that met the way out and ran on past it to a loose
    end, under `_PAST_CONNECTOR_FT`, is cut where it met it; the connector itself is never cut, and a lane with nothing to
    cut is left as it is."""
    from l7r.diagram.hamletgen.ways.sweeps import _PAST_CONNECTOR_FT

    s = _StubSettlement(lanes=[[(0.0, 100.0), (400.0, 100.0)]])
    s.M["lanes"].append({"pts": [[0.0, 300.0], [0.0, 100.0 - (_PAST_CONNECTOR_FT - 8.0)]], "w": 3})
    s.M["lanes"].append({"pts": [[200.0, 400.0], [200.0, 100.0]], "w": 3})
    hg.ways.cut_the_overruns(s)
    assert s.M["lanes"][0]["pts"] == [[0.0, 100.0], [400.0, 100.0]], "the connector is left"
    end = s.M["lanes"][1]["pts"][-1]
    assert abs(end[1] - 100.0) <= 6.0, "the overrun is cut where it met the way"
    assert s.M["lanes"][2]["pts"] == [[200.0, 400.0], [200.0, 100.0]], "a lane ending on the way is left"


def test_the_late_pass_leaves_a_connector_that_starts_at_the_way_outs_gate() -> None:
    """Feature 287 wave 6 (cohort seeds 34 and 37), as feature 320 keeps it: a connector pulled back to service left the root
    the households' ways reach - 300 ft down the track on seed 34. Where the homesteads stage recorded the way out's gate
    (`way_out_gate`) the connector's start stands."""
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]], houses=[(60.0, 200.0)])
    s.M["way_out_gate"] = [0.0, 0.0]
    hg.ways.tidy_lane_ends(s, [(200.0, 0.0), (600.0, 0.0), (600.0, 400.0), (200.0, 400.0)])
    assert s.M["lanes"][0]["pts"][0] == [0.0, 0.0] or tuple(s.M["lanes"][0]["pts"][0]) == (0.0, 0.0)


def test_a_door_on_a_fixture_steps_along_the_front_until_clear() -> None:
    """`door_off_fixtures` (feature 291 on 287): a door clear stays; one on a trunk steps along the front (across the line
    from the house through it), nearest first; one boxed in along the whole front is None."""
    from l7r.diagram.hamletgen.ways.serve import door_off_fixtures

    house = (0.0, 0.0)
    trunk = [(-2.0, 48.0), (2.0, 48.0), (2.0, 52.0), (-2.0, 52.0)]
    assert door_off_fixtures((30.0, 50.0), house, [trunk], 5.0) == (30.0, 50.0)
    moved = door_off_fixtures((0.0, 50.0), house, [trunk], 5.0)
    assert moved is not None and abs(moved[1] - 50.0) < 1e-9 and abs(moved[0]) >= 7.0, "along the front, clear of the trunk"
    wall = [(-100.0, 45.0), (100.0, 45.0), (100.0, 55.0), (-100.0, 55.0)]
    assert door_off_fixtures((0.0, 50.0), house, [wall], 5.0) is None


def test_a_door_path_ends_where_it_first_arrives_at_its_way() -> None:
    """`to_first_arrival` (feature 291 on 287): the path is ended at the nearest point of the way where it first comes within
    the touch gap, so it never runs on beside it; a path that never arrives is as it was."""
    from l7r.diagram.hamletgen.ways.serve import to_first_arrival

    way = [((0.0, 0.0), (300.0, 0.0))]
    path = [(100.0, 60.0), (100.0, 3.0), (200.0, 3.0), (200.0, 0.0)]
    out = to_first_arrival(path, way, 4.0)
    assert out[0] == (100.0, 60.0) and out[-1][1] == 0.0 and 99.0 <= out[-1][0] <= 101.0 and len(out) == 2
    assert to_first_arrival([(0.0, 50.0), (10.0, 50.0)], way, 4.0) == [(0.0, 50.0), (10.0, 50.0)]
    slant = [(0.0, 60.0), (100.0, 0.0)]
    assert to_first_arrival(slant, way, 4.0, lambda a, b: True)[-1] == (0.0, 0.0), "square onto the way where that leg is clear"
    end = to_first_arrival(slant, way, 4.0, lambda a, b: False)[-1]
    assert end[1] == 0.0 and 90.0 < end[0] < 100.0, "else at the arrival itself, as the path came"


def test_a_routed_door_path_is_string_pulled_where_a_chord_is_clear() -> None:
    """`pulled` (feature 291 on 287): every jog a clear chord can cut is taken out; the ends are kept; a path of two points
    is as it was."""
    from l7r.diagram.hamletgen.ways.serve import pulled

    path = [(0.0, 0.0), (10.0, 1.0), (20.0, -1.0), (30.0, 0.0), (30.0, 40.0)]
    assert pulled(path, lambda a, b: True) == [(0.0, 0.0), (30.0, 40.0)]
    assert pulled(path, lambda a, b: abs(a[0] - b[0]) < 1e-9 or abs(a[1] - b[1]) < 2.0) == [(0.0, 0.0), (30.0, 0.0), (30.0, 40.0)]
    assert pulled(path[:2], lambda a, b: True) == path[:2]


def test_a_flank_door_faces_no_band_and_is_open_to_the_front() -> None:
    """`flank_doors` / `front_to_flank_open` (FR-019's exception, amendment 8): only a flank facing no band of the farm's own
    grove is offered; none without a yard; the ground from the front door to it is open unless the house or a band stands
    across it."""
    from l7r.diagram.hamletgen.ways.serve import flank_doors, front_to_flank_open

    geom = {"house": (0.0, 0.0, 40.0, 30.0), "yard": (0.0, 35.0, 30.0, 20.0), "grove_faces": [((0, -1), "deep"), ((-1, 0), "deep")], "groves": [(0.0, -60.0, 200.0, 40.0), (-80.0, 0.0, 40.0, 100.0)]}
    doors = flank_doors({"geom": geom})
    assert len(doors) == 1 and doors[0][0] > 0.0, "the east flank only: the west one faces the deep west band"
    assert flank_doors({"geom": {"house": (0.0, 0.0, 1.0, 1.0)}}) == []
    assert front_to_flank_open((0.0, 58.0), (30.0, 35.0), {"geom": geom})
    assert not front_to_flank_open((0.0, 58.0), (0.0, -30.0), {"geom": geom}), "across the house"


def test_a_farm_is_reached_from_a_flank_only_where_the_front_has_no_lawful_path(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """`lay_door_paths` (FR-019's exception, amendment 8): the front door first; where it has no lawful path, an open flank's
    path is drawn and recorded (`from_flank`, `meta.door_flanks`); a flank the house or a band walls off the front is not
    offered."""
    from l7r.diagram.hamletgen.ways import serve
    from l7r.diagram.settlement import Settlement

    def farm_and_street(open_front: bool):  # type: ignore[no-untyped-def]
        s = Settlement(600, 600, seed=1)
        s.meta(name="T", scale="hamlet", ftpx=1)
        s.lane([(0.0, 100.0), (600.0, 100.0)], width=6)
        s.M["lanes"][-1].update({"street": True, "street_index": 0})
        s.M["houses"].append({"x": 300.0, "y": 300.0, "w": 46.0, "h": 28.0, "geom": {}})
        monkeypatch.setattr(serve, "front_door", lambda h, clear: (300.0, 350.0))
        monkeypatch.setattr(serve, "flank_doors", lambda h: [(340.0, 320.0)])
        monkeypatch.setattr(serve, "door_off_fixtures", lambda d, house, quads, gap: d)
        monkeypatch.setattr(serve, "front_to_flank_open", lambda front, flank, h: open_front)
        monkeypatch.setattr(serve, "door_path", lambda s_, d, segs, *a: None if d == (300.0, 350.0) else [d, (340.0, 100.0)])
        return s

    s = farm_and_street(True)
    assert serve.lay_door_paths(s, [], [], []) == 1
    assert s.M["lanes"][-1].get("from_flank") and s.M["meta"]["door_flanks"] == [[300.0, 300.0]]
    s = farm_and_street(False)
    assert serve.lay_door_paths(s, [], [], []) == 0, "the flank walled off the front is not offered"


def test_a_boxed_in_door_routes_from_a_clear_step_out_of_it(monkeypatch: pytest.MonkeyPatch) -> None:
    """The router finds nothing from a door whose own cell has no free neighbor (Kashikawa under feature 302): the route is
    taken from a step a cell or two out, toward the target first and only where the step is clear, the door put back at its
    head; a door the router leaves is routed as it was, and one no step frees has no route."""
    from l7r.diagram.hamletgen.ways import serve

    door, q = (0.0, 0.0), (100.0, 0.0)
    asked: list[tuple[float, float]] = []

    def boxed(start, goal, *a, **k):  # type: ignore[no-untyped-def]
        asked.append(start)
        return [] if start == door else [start, goal]

    monkeypatch.setattr(serve, "_route", boxed)
    got = serve.route_from_door(door, q, [], [], [], lambda a, b: b[1] >= -1e-9)
    assert got[0] == door and got[1] == pytest.approx((10.0, 0.0)) and got[-1] == q, "the step toward the target, first"
    monkeypatch.setattr(serve, "_route", lambda start, goal, *a, **k: [start, goal])
    assert serve.route_from_door(door, q, [], [], [], lambda a, b: True) == [door, q]
    monkeypatch.setattr(serve, "_route", lambda *a, **k: [])
    assert serve.route_from_door(door, q, [], [], [], lambda a, b: True) == []
    assert serve.route_from_door(door, q, [], [], [], lambda a, b: False) == []


def test_a_row_farm_takes_no_door_path_only_where_its_street_already_arrives() -> None:
    """Off the network the reach alone is asked; on a row's own street, only where the street's point nearest the door is
    an end the lane law counts as serving the farm (`end_serves`) - Mizuguchi's east-end farm, its door 11 ft off the
    street but its house 77 ft and its yard 19, needed a path (2026-10-01)."""
    farm = {"x": 0.0, "y": 0.0}
    street = [((-100.0, 77.0), (100.0, 77.0))]
    yard = [[(-20.0, 20.0), (20.0, 20.0), (20.0, 58.0), (-20.0, 58.0)]]
    assert _serve.street_arrives(farm, (0.0, 66.0), street, None, yard), "off a row's street: the reach alone"
    assert not _serve.street_arrives(farm, (0.0, 66.0), street, 0, yard), "the street 19 ft off the yard and 77 off the house"
    near = [((-100.0, 66.0), (100.0, 66.0))]
    assert _serve.street_arrives(farm, (0.0, 60.0), near, 0, yard), "8 ft off the yard: it arrives"


def test_a_cut_end_that_cannot_be_carried_onto_the_way_is_refused_and_one_on_it_stays() -> None:
    """0081 (feature 328 wave 43): a run cut where it arrives early has its cut end carried onto the way - refused where a
    steading stands in that link, and left as it is where the cut end already lies on the way."""
    run = [(40.0, 200.0), (20.0, 200.0), (60.0, 200.0), (110.0, 200.0), (160.0, 200.0)]
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]], houses=[(160.0, 230.0)])
    wall = [(5.0, 190.0), (15.0, 190.0), (15.0, 210.0), (5.0, 210.0)]
    assert hg.ways._lay_web_lane(s, run, [], [wall], [], houses=[(160.0, 230.0)]) is False
    on = [(30.0, 200.0), (0.0, 200.0), (60.0, 200.0), (110.0, 200.0), (160.0, 200.0)]
    s2 = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]], houses=[(160.0, 230.0)])
    assert hg.ways._lay_web_lane(s2, on, [], [], [], houses=[(160.0, 230.0)]) is True
    assert [tuple(q) for q in s2.M["lanes"][-1]["pts"]][0] == (0.0, 200.0)


def test_joined_link_snaps_straight_falls_back_to_the_clear_run_or_refuses() -> None:
    """`joined_link` (feature 328 wave 44, 0081: ends within 25 ft are joined at a single point): no length is the point; a
    walkable straight join; where the straight join grazes a fence, the clear run of it the far branch lays; None where the
    link is blocked outright."""
    from l7r.diagram.hamletgen.ways.serve import joined_link

    segs = [((0.0, 0.0), (0.0, 400.0))]
    assert joined_link((0.0, 200.0), (0.0, 200.0), [], [], [], segs) == [(0.0, 200.0)]
    assert joined_link((20.0, 200.0), (0.0, 200.0), [], [], [], segs) == [(20.0, 200.0), (0.0, 200.0)]
    across = [(5.0, 190.0), (15.0, 190.0), (15.0, 210.0), (5.0, 210.0)]  # a steading astride the link
    assert joined_link((20.0, 200.0), (0.0, 200.0), [], [across], [], segs) is None
    graze = [(17.0, 205.0), (21.0, 205.0), (21.0, 209.0), (17.0, 209.0)]  # a post 5 ft off the link's first few feet
    link = joined_link((20.0, 200.0), (0.0, 200.0), [], [graze], [], segs)
    assert link is not None and link[-1] == (0.0, 200.0) and 0.0 < math.dist(link[0], (20.0, 200.0)) < 12.0, link


def test_a_run_kept_whole_takes_a_link_where_it_arrives() -> None:
    """A run whose nearest vertex comes within 25 ft of the network mid-run, both halves 40 ft or more, has that vertex snapped onto
    its foot on the way (it was drawn whole and left unjoined); refused where a new leg is not walkable."""
    run = [(160.0, 260.0), (110.0, 230.0), (20.0, 200.0), (110.0, 170.0), (160.0, 140.0)]
    homes = [(170.0, 270.0), (170.0, 130.0)]  # one at each end, so the run's service keeps it whole
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]], houses=homes)
    assert hg.ways._lay_web_lane(s, run, [], [], [], houses=homes) is True
    drawn = [tuple(q) for q in s.M["lanes"][-1]["pts"]]
    assert (0.0, 200.0) in drawn and (20.0, 200.0) not in drawn, drawn
    # a new leg blocked: the link `joined_link` finds is drawn as its own lane, if a lane can be (else the run is refused)
    walled = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]], houses=homes)
    walled.M["lanes"][0]["w"] = 5  # a cart way: the link takes its width (`join_width`)
    fence = [(40.0, 175.0), (60.0, 175.0), (60.0, 190.0), (40.0, 190.0)]  # on the snapped vertex's new leg out of (0, 200)
    assert hg.ways._lay_web_lane(walled, run, [], [fence], [], houses=homes) is True
    links = [ln for ln in walled.M["lanes"][1:] if {tuple(q) for q in ln["pts"]} == {(20.0, 200.0), (0.0, 200.0)}]
    assert links and float(links[0]["w"]) == 5.0, walled.M["lanes"]
    # the new legs AND the link blocked: not drawn
    shut = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]], houses=homes)
    post = [(5.0, 190.0), (15.0, 190.0), (15.0, 210.0), (5.0, 210.0)]  # astride the link (20, 200) -> (0, 200)
    assert hg.ways._lay_web_lane(shut, run, [], [fence, post], [], houses=homes) is False and len(shut.M["lanes"]) == 1


def test_carried_onto_splices_the_link_and_checks_the_leg_into_it() -> None:
    """`carried_onto` (feature 328 wave 44): no link, nothing; a point link leaves the run; a link from the end itself is spliced
    on; one starting past a foul is spliced only where the leg into it is walkable."""
    from l7r.diagram.hamletgen.ways.serve import carried_onto

    run = [(20.0, 200.0), (60.0, 200.0), (120.0, 200.0)]
    assert carried_onto(run, 0, None, [], [], []) is None
    assert carried_onto(run, 0, [(20.0, 200.0)], [], [], []) == run
    assert carried_onto(run, 0, [(20.0, 200.0), (0.0, 200.0)], [], [], []) == [(0.0, 200.0), (20.0, 200.0), (60.0, 200.0), (120.0, 200.0)]
    piece = [(14.0, 205.0), (0.0, 205.0)]  # a clear run that starts off the end
    assert carried_onto(run, 0, piece, [], [], [])[:2] == [(0.0, 205.0), (14.0, 205.0)]
    wall = [(30.0, 198.0), (40.0, 198.0), (40.0, 212.0), (30.0, 212.0)]  # on the leg from (60, 200) into the piece
    assert carried_onto(run, 0, piece, [], [wall], []) is None
    assert carried_onto(run[::-1], -1, piece, [], [], [])[-2:] == [(14.0, 205.0), (0.0, 205.0)]
