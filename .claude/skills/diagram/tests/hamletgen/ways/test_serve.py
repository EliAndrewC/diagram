"""Split from test_ways.py by feature 173 - see this directory's CLAUDE.md."""

from l7r.diagram import hamletgen as hg

from ._builders import _StubSettlement


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


def test_the_footpath_search_stops_looking_past_its_backstop_radius() -> None:
    """The directness bound is the real limit on a footpath; the radius is only a backstop against
    searching the whole map. A steading this far out is beyond any path worth drawing, and the loop
    must stop rather than test every way on the sheet."""

    class _Plan:
        envelope = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)]
        watercourses: list = []

    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 200.0)]], houses=[(4000.0, 4000.0)])
    before = len(s.M["lanes"])
    hg.ways._serve_stragglers(s, _Plan(), [], [], [])
    assert len(s.M["lanes"]) == before, "nothing drawn for a steading beyond the backstop"


def test_a_web_lane_snaps_its_end_onto_the_way_it_almost_meets() -> None:
    """A run that stops a few feet short of the way it aims at renders as a gap, whatever the gate
    thinks of it - acceptance tolerances are not ink tolerances. So an end within `_LANE_JOIN_FT` is
    extended onto the way it meets, but ONLY if the ground between is clear: adding those few feet
    blind put lane ink across houses and garden beds on every cohort seed the moment snapping went
    in. This pins both halves - the snap, and the refusal to snap through a steading."""
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
    hg.ways._lay_web_lane(s2, run, [], [wall], [])
    if len(s2.M["lanes"]) > 1:
        assert (0, 200) not in [(round(x), round(y)) for x, y in s2.M["lanes"][-1]["pts"]]


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
    assert [tuple(q) for q in drawn] == run[1:], "the 20 ft head is dropped, the 140 ft body is kept"


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
    # PINNED TO NUCLEATED for now - the knob is live and every other part of it is tested, but the
    # per-house grove path the other two forms need has four unfixed defects (see SETTLEMENT_FORMS
    # in hamletgen/consts.py for the measurements and the sketch). This asserts the CURRENT contract
    # rather than the intended one, so that turning the forms back on fails here loudly and the test
    # is updated deliberately instead of drifting.
    assert set(forms) == {"nucleated"}, f"forms are pinned to nucleated; got {forms}"


def test_an_explicit_form_on_the_spec_beats_the_roll() -> None:
    """A pool gen pins the form the way it pins every other knob."""
    plan = hg.plan_site(hg.HamletSpec(name="Pinned", seed=3, households=12, settlement_form="dispersed"))
    assert plan.settlement_form == "dispersed"
