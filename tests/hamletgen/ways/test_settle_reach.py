"""`hamletgen/ways/settle/`: the reach the web owes, drawn as tree lanes (step 4), the field way, and `Lawful` - the law asked
of a new lane - with the fabric's gaps (split from `test_settle.py` at the 1,000-line bar, 405 T107)."""

import math

import pytest

from l7r.diagram.hamletgen.ways import corridors as co
from l7r.diagram.hamletgen.ways import law, settle
from l7r.diagram.hamletgen.ways.last_resort import WebRefused
from l7r.diagram.settlement import segments_cross

from ._settle_builders import _GEN, _S, BROOK, CONN, _c, _pts


def test_a_stranded_house_is_reached_along_its_corridor_and_the_tree_is_never_cut() -> None:
    """Ways W01: the house the web left 360 ft off is served by the tree lane the seating judged - its corridor from its
    door to the track out (`tree.settle_tree`) - and a settle round after cuts nothing of it (`corridors.is_tree`)."""
    s = _S([_c((400.0, 0.0), (-1000.0, 0.0))], houses=[(300.0, 200.0)], meta=dict(_GEN), access_corridors=[{"pts": [[300.0, 180.0], [300.0, 0.0]], "of": [300.0, 200.0]}])
    s.M["houses"][0]["rot"] = 180.0  # the front faces the track: the door is in the dooryard
    assert law.unreached_houses(s.M)
    got = settle.settle_the_web(s)
    assert got["unreached_before"] == 1 and got["unreached_after"] == 0 and law.unreached_houses(s.M) == []
    assert [(ln.get("role"), ln.get("of")) for ln in s.M["lanes"][1:]] == [("access", [300.0, 200.0])], "no strip drawn"
    assert not law.violations(s.M)
    assert settle.settle_the_web(s)["changed"] == 0, "the tree lanes keep the law, so nothing is left to repair"
    assert settle.settle_reach(s) == 0, "nothing owed, nothing drawn"


def test_a_way_target_gets_its_spur() -> None:
    """Homes H36 (a path runs to the graves): the connector alone does not reach the burial ground's edge, so the settle lays
    the shortest lawful spur to it - a tree lane, drawn once."""
    meta = {**_GEN, "way_targets": [{"kind": "burial ground", "at": [-300.0, 80.0]}]}
    s = _S([CONN], meta=meta)
    assert law.unreached_targets(s.M) == [(-300.0, 80.0)]
    settle.settle_the_web(s)
    assert law.unreached_targets(s.M) == [] and [ln.get("role") for ln in s.M["lanes"]].count("way target") == 1
    assert settle.settle_targets(s, settle.Lawful(s)) == 0, "drawn once"


def test_a_target_no_lawful_run_reaches_is_left_unreached_not_drawn_least_bad(monkeypatch: pytest.MonkeyPatch) -> None:
    """FR-005: with no spur to a way target keeping the law, nothing is drawn - the report says what is still owed."""
    meta = {**_GEN, "way_targets": [{"kind": "burial ground", "at": [-300.0, 80.0]}]}
    s = _S([CONN], meta=meta)
    monkeypatch.setattr(settle.Lawful, "__call__", lambda self, run, width, skip=None: False)
    monkeypatch.setattr(settle.Lawful, "fault", lambda self, run, width, skip=None: "refused")
    got = settle.settle_the_web(s)
    assert got["targets_unreached"] == 1
    assert not any(ln.get("role") == "way target" for ln in s.M["lanes"])


def test_an_end_behind_a_house_reaches_it_and_is_left() -> None:
    """0246 (feature 328): an end within 60 ft of the house or 12 ft of its built ground reaches it, on any side - the end
    40 ft behind a farmhouse's back wall is left where it is (water W57 carried it round the gable or cut it, a rule on no page)."""
    lane = [(-100.0, 0.0), (-100.0, 100.0), (-100.0, 160.0)]
    s = _S([CONN, lane], houses=[(-100.0, 200.0)])
    settle.settle_ends(s)
    assert _pts(s, 1) == lane


def polyline(p):
    return sum(math.dist(a, b) for a, b in zip(p, p[1:], strict=False))


def test_lawful_refuses_each_rule_a_new_tree_lane_would_break() -> None:
    """`Lawful`: the one question asked before a tree lane is laid, since it is never cut afterwards."""
    s = _S(
        [CONN, [(-500.0, 0.0), (-500.0, 300.0)]], houses=[(-300.0, 300.0), (-460.0, 300.0)], streams=[BROOK], fields=[{"outline": [[-800.0, 400.0], [-700.0, 400.0], [-700.0, 500.0], [-800.0, 500.0]]}]
    )
    s.M["threshing_yards"] = [{"poly": [[-320.0, 100.0], [-280.0, 100.0], [-280.0, 120.0], [-320.0, 120.0]], "of": [-300.0, 300.0]}]
    ok = settle.Lawful(s)
    assert ok([(-240.0, 0.0), (-250.0, 290.0)], 3.0), "a clean spur off the connector, to a house"
    assert not ok([(-100.0, 0.0), (-100.0, 150.0)], 3.0), "a spur to nothing: its end dangles"
    assert not ok([(-100.0, 0.0)], 3.0) and not ok([(-100.0, 0.0), (-100.0, 150.0), (-90.0, 20.0)], 3.0), "too short; doubled back"
    assert not ok([(0.0, 50.0), (200.0, 50.0)], 3.0), "over the brook off any ford"
    assert not ok([(-300.0, 0.0), (-300.0, 160.0)], 3.0), "through a neighbor's threshing yard"
    assert not ok([(-750.0, 0.0), (-750.0, 450.0)], 3.0), "into the field"
    assert not ok([(-490.0, 0.0), (-490.0, 290.0)], 3.0), "doubling a way along its whole run"
    assert ok([(-500.0, 0.0), (-500.0, 300.0)], 3.0, skip=1), "the lane it would replace is not asked to meet it"
    assert not ok([(-340.0, 100.0), (-340.0, 250.0), (-300.0, 295.0)], 3.0), "into a house"
    quad = [(0.0, 0.0), (40.0, 0.0), (40.0, 28.0), (0.0, 28.0)]
    assert co.through_a_building([(20.0, -10.0), (20.0, 40.0)], [quad]), "clean through between the corners"
    assert co.through_a_building([(20.0, -10.0), (20.0, 10.0)], [quad]) and not co.through_a_building([(50.0, -10.0), (50.0, 40.0)], [quad])


def test_the_tree_is_left_alone_at_a_fold_and_behind_a_house_and_a_target_is_drawn_to_once() -> None:
    """The tree lanes (`corridors.is_tree`) are not the lanes a repair edits - but for a household's way at its FOOT, where
    two ways run side by side (feature 385 T01, plan D4): two household ways folded back on each other 80 ft side by side
    become one path, the one's foot re-aimed onto the other, both still drawn and joined. A tree lane ending behind a house
    is left as it is, and a target whose spur is drawn is not drawn to again."""
    folded = _S([CONN, [(-100.0, 0.0), (-100.0, 100.0)], [(-100.0, 100.0), (-95.0, 20.0)]])
    for ln in folded.M["lanes"][1:]:
        ln["role"] = "access"
    assert law.folded_joint_pairs(folded.M["lanes"]) and law.needle_ends(folded.M["lanes"]), "side by side, folded at the joint"
    assert settle.settle_ends(folded) == 1 and len(folded.M["lanes"]) == 3, "one foot re-aimed, no lane dropped"
    assert law.lane_networks(folded.M) == 1 and not law.needle_ends(folded.M["lanes"]), "one path, still one web"
    behind = _S([CONN, [(-100.0, 0.0), (-100.0, 100.0), (-100.0, 160.0)]], houses=[(-100.0, 200.0)])
    behind.M["lanes"][1]["role"] = "access"
    assert settle.settle_ends(behind) == 0
    drawn = _S([CONN, ([(-600.0, 0.0), (-600.0, 50.0)], {})], meta={**_GEN, "way_targets": [{"at": [-300.0, 80.0]}]})
    drawn.M["lanes"][1].update({"role": "way target", "to": [-300.0, 80.0]})
    assert settle.settle_targets(drawn, settle.Lawful(drawn)) == 0


def test_lawful_refuses_a_needle_or_a_hairpin_at_the_connectors_start() -> None:
    s = _S([CONN])
    ok = settle.Lawful(s)
    assert not ok([(-200.0, 30.0), (-100.0, 0.5)], 3.0), "meets the connector at a needle's angle"
    assert not ok([(-60.0, 10.0), (-5.0, 10.0), (0.0, 0.0)], 3.0), "doubles back over a short leg at the connector's start"


def test_a_field_way_no_straight_run_keeps_is_threaded_round_the_steadings() -> None:
    """Ways W03, cohort seed 13: every straight run from the network to the bund passed through a steading, so the field's
    corridor the seating reserves is threaded by the web's router (`field_router`, `routed_field_runs`) round it."""
    from l7r.diagram.hamletgen.ways.bund import BRANCH_WIDTH
    from l7r.diagram.hamletgen.ways.geom import WorkedGround

    field = [[300.0, -300.0], [500.0, -300.0], [500.0, 300.0], [300.0, 300.0]]
    far_brook = {"poly": [[1000.0, -500.0], [1000.0, 500.0]], "w": 6.0}
    s = _S([_c((0.0, 0.0), (-1000.0, 0.0))], houses=[(150.0, 0.0)], meta=dict(_GEN), streams=[far_brook], fields=[{"outline": field}])
    s.M["houses"][0].update({"w": 60.0, "h": 200.0})
    ground = WorkedGround([[(float(a), float(b)) for a, b in field]])
    runs = co.routed_field_runs([((0.0, 0.0), (-100.0, 0.0))], ground, BRANCH_WIDTH / 2.0, co.field_router(s, [(1000.0, -500.0), (1000.0, 500.0)]))
    assert runs and len(runs[0]) > 2 and not co.through_a_building(runs[0], co.building_quads(s.M)), "threaded round the house"


def _field_across_the_brook() -> _S:
    """A connector west of the brook at x = 100 and a paddy east of it: no way of the hamlet's own reaches the field."""
    field = [[300.0, -300.0], [500.0, -300.0], [500.0, 300.0], [300.0, 300.0]]
    return _S([CONN], meta={**_GEN, "brook_fords": [[100.0, 0.0]]}, streams=[BROOK], fields=[{"outline": field}])


def test_the_field_no_way_reaches_gets_the_field_way_drawn_once() -> None:
    """Feature 320 (FR-004): nothing reserved before the houses, the settle draws the field way where no way reaches the field
    - over the brook at its ford, a tree lane - and draws it once."""
    s = _field_across_the_brook()
    assert law.field_unreached(s.M)
    assert settle.settle_field(s, settle.Lawful(s, tree=True)) == 1
    assert not law.field_unreached(s.M) and s.M["lanes"][-1]["role"] == co.FIELD_ROLE and co.is_tree(s.M["lanes"][-1])
    assert settle.settle_field(s, settle.Lawful(s, tree=True)) == 0, "reached: nothing more drawn"


def test_a_field_no_lawful_run_reaches_draws_nothing_and_the_web_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    """FR-005: no candidate keeps the law, so nothing least-bad is drawn; and with no ground or no network, none is sought."""
    s = _field_across_the_brook()
    assert settle.settle_field(s, lambda run, width, skip=None: False) == 0 and not any(ln.get("role") == co.FIELD_ROLE for ln in s.M["lanes"])
    monkeypatch.setattr(settle.Lawful, "__call__", lambda self, run, width, skip=None: False)
    monkeypatch.setattr(settle.Lawful, "fault", lambda self, run, width, skip=None: "refused")
    with pytest.raises(WebRefused, match="the field is reached by no way"):
        settle.settle_the_web(_field_across_the_brook())
    bare = _S([CONN], meta=dict(_GEN), streams=[BROOK])
    assert law.field_unreached(bare.M) and settle.settle_field(bare, settle.Lawful(bare)) == 0, "no field: no ground to reach"
    lone = _field_across_the_brook()
    lone.M["lanes"] = []
    assert settle.settle_field(lone, settle.Lawful(lone)) == 0, "no network to leave from"


def test_a_routed_field_way_is_drawn_where_no_straight_run_keeps_the_law() -> None:
    """The router's runs are offered after the straight ones (`routed_field_runs`): the first lawful of them is drawn."""
    s = _field_across_the_brook()
    calls = []

    def law_(run, width, skip=None):
        calls.append(len(run))
        return len(calls) > 120

    assert settle.settle_field(s, law_) == 1 and len(calls) > 120, "every straight run refused, a routed one drawn"


def _strip_over_the_brook(start_y: float, ford_y: float) -> _S:
    """One house's corridor down to (300, 80), then west over the brook at x = 100 to the connector's start (0, `start_y`) - the
    run the exit strip took before feature 320 - a ford where it crosses."""
    brook = {"poly": [[100.0, -500.0], [100.0, 500.0]], "w": 7.0}
    s = _S(
        [_c((0.0, start_y), (-1000.0, start_y))],
        houses=[(300.0, 200.0)],
        meta={**_GEN, "brook_fords": [[100.0, ford_y]]},
        streams=[brook],
        fields=[{"outline": [[340.0, 60.0], [420.0, 60.0], [420.0, 140.0], [340.0, 140.0]]}],  # beside the house's way, reached by it
        access_corridors=[{"pts": [[300.0, 180.0], [300.0, 80.0]], "of": [300.0, 200.0]}, {"pts": [[300.0, 80.0], [0.0, start_y]]}],
    )
    s.M["houses"][0]["rot"] = 180.0
    return s


def test_seed_8_a_corridor_over_the_brook_at_its_ford_is_squared_and_drawn() -> None:
    """Cohort seed 8 (the coarse-grain knob reseated the cluster): the exit strip ran from the houses over the brook to the
    connector's start off square at a ford, the corridor was judged unsquared, refused, and three houses were stranded. The
    web squares a tree lane at its crossings (`square_run`) before it asks the law, as it squares every lane. Here 15
    degrees off: seed 8's own 38 is the case below, which the law refuses once the strip is drawn."""
    s = _strip_over_the_brook(0.0, 26.7)
    assert not settle.Lawful(s).on_lawful_ground([(300.0, 80.0), (0.0, 0.0)], 3.0), "unsquared, the strip crosses 15 degrees off"
    assert settle.corridor_on_lawful_ground(s.M, [(300.0, 80.0), (0.0, 0.0)]), "squared, the seating's own question admits it"
    settle.settle_the_web(s)
    assert law.unreached_houses(s.M) == [] and law.oblique_crossings(s.M) == [] and law.off_ford_crossings(s.M) == []
    # ...and the field way, since 405 T22: no lane here comes within 0014's 6 ft join of the field, so the settle draws one
    assert [ln["role"] for ln in s.M["lanes"] if ln.get("role")] == ["access", "field way"]
    assert settle.unsettled(s.M) == {}


def test_a_strip_squared_and_rejoined_bends_rather_than_kinks() -> None:
    """The same strip 38 degrees off square, as seed 8 drew it: the web draws it rejoined either side of the crossing and
    squared (`tree.rejoined`, `tree.lanes_of`). On the usual square leg its two elbows - 70 degrees each, 21 ft apart - were a
    kink the settle could only refuse; the squaring now takes a leg past 0081's 40 ft where the short one leaves a zigzag
    (`squaring.squared_against`, feature 328 wave 46), so the elbows are a bend and the strip keeps the law."""
    s = _strip_over_the_brook(-150.0, -73.3)
    assert settle.corridor_on_lawful_ground(s.M, [(300.0, 80.0), (0.0, -150.0)]), "squared without the rejoin, it keeps the law"
    settle.settle_the_web(s)
    assert not law.lanes_that_kink(s.M), "no kink at the crossing"


def _reference_lawful_ground(ok: settle.Lawful, run, width) -> bool:
    """`Lawful.on_lawful_ground` as it read before the ground was indexed: every registry walked whole."""
    if len(run) < 2 or law.hook_faults(run, width, ok.blocked) or law.kink_faults(run, width, ok.blocked):
        return False
    if settle._crossing_fault({**ok.M, "lanes": [{"pts": settle._rounded(run), "w": width}]}, 0, run, ok.wet) is not None:
        return False
    rings = settle.open_ground_rings(ok.M)
    crossed = any(segments_cross(p, q, r[k], r[(k + 1) % len(r)]) for p, q in zip(run, run[1:], strict=False) for r in rings for k in range(len(r)))
    return settle.fouled_segment(run, width, ok.houses, ok.yards, ok.solid, ok.fixtures) is None and not crossed and not co.through_a_building(run, ok.buildings)


def test_the_indexed_lawful_ground_answers_as_the_whole_registries_do() -> None:
    """The ground half of the law reads an index built once (`corridors.GroundIndex`, dev/performance.md): it only prunes, so
    over runs that cross the brook, a channel, a field, a dry plot and a marsh, pass a house, a yard, a byre and a fixture,
    each near and far, it gives the verdict every registry walked whole gives - and some of each."""
    import random

    s = _S(
        [CONN],
        houses=[(-300.0, 300.0), (-460.0, 300.0), (400.0, 200.0)],
        streams=[BROOK],
        drawn_channels=[{"pts": [[-900.0, 600.0], [900.0, 650.0]], "w0": 4.0}],
        fields=[{"outline": [[-800.0, 400.0], [-700.0, 400.0], [-700.0, 500.0], [-800.0, 500.0]]}],
        dry_plots=[{"poly": [[300.0, -300.0], [360.0, -300.0], [360.0, -240.0], [300.0, -240.0]]}],
        marshes=[{"poly": [[-200.0, -400.0], [-100.0, -400.0], [-150.0, -300.0]]}, {"poly": [[500.0, 500.0], [560.0, 500.0], [530.0, 560.0]], "role": "defense"}],
        byres=[{"x": 200.0, "y": 300.0, "w": 30.0, "h": 20.0}],
        farm_fixtures=[{"x": -250.0, "y": 200.0, "w": 8.0, "h": 8.0}],
    )
    s.M["meta"]["brook_fords"] = [[100.0, 100.0]]
    s.M["threshing_yards"] = [{"poly": [[-320.0, 100.0], [-280.0, 100.0], [-280.0, 120.0], [-320.0, 120.0]], "of": [-300.0, 300.0]}]
    ok = settle.Lawful(s)
    rng = random.Random(7)
    verdicts = []
    for _ in range(400):
        run = [(rng.uniform(-900.0, 900.0), rng.uniform(-600.0, 700.0))]
        for _leg in range(rng.choice((1, 1, 2))):
            run.append((run[-1][0] + rng.uniform(-300.0, 300.0), run[-1][1] + rng.uniform(-300.0, 300.0)))
        want = _reference_lawful_ground(ok, run, 3.0)
        assert ok.on_lawful_ground(run, 3.0) == want, run
        verdicts.append(want)
    assert 40 < sum(verdicts) < 360, "the runs drawn are admitted and refused both"
    assert ok.index is ok.index, "built once"


def test_a_run_is_squared_only_where_water_comes_within_the_squaring_reach() -> None:
    """`Lawful.squared` is `square_run` where water comes near the run, and the run itself where none does - where the
    squaring would change nothing."""
    s = _S([CONN], streams=[BROOK])
    ok = settle.Lawful(s)
    across = [(40.0, 100.0), (160.0, 160.0)]
    assert ok.squared(across) == settle.square_run(s.M, across) != across, "an oblique crossing is squared"
    far = [(300.0, 100.0), (320.0, 160.0), (400.0, 170.0)]
    assert ok.squared(far) == settle.square_run(s.M, far) == far


def test_an_ordinary_join_that_would_break_a_rule_against_the_tree_is_taken_back_instead(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 287 wave 6 (cohort seed 25 under the probes): a join closed onto the tree that the deference then cut again took
    turns with it until the rounds ran out - so an ordinary lane whose join would break a rule against a tree lane
    (`tree.tree_faults`) is taken back out of the join's reach instead; a tree lane's own join is made."""
    END = 200.0 - (law.JOIN_REACH_FT - 5.0)  # an end 5 ft inside the join reach of the way at y = 200
    s = _S([CONN, [(-100.0, 0.0), (-100.0, END)], [(-200.0, 200.0), (0.0, 200.0)]])
    assert [i for i, _e, _f in law.near_misses(s.M)] == [1]
    monkeypatch.setattr(settle.ends, "tree_faults", lambda M: [(1, (-100.0, 200.0))] if len(M["lanes"][1]["pts"]) > 2 else [])
    assert settle.settle_joins(s) == 1
    got = _pts(s, 1)
    assert got[0] == (-100.0, 0.0) and got[-1][1] == pytest.approx(END - law.JOIN_REACH_FT - settle.JOIN_BACK_PAD_FT), "taken back"
    t = _S([CONN, ([(-100.0, 0.0), (-100.0, END)], {}), [(-200.0, 200.0), (0.0, 200.0)]])
    t.M["lanes"][1]["role"] = co.ACCESS_ROLE
    assert settle.settle_joins(t) == 1 and _pts(t, 1)[-1] == (-100.0, 200.0), "a tree lane joins"


def test_an_ordinary_join_the_matrix_refuses_is_taken_back_instead() -> None:
    """Feature 318 (Kuwabata): the law called the span walkable (its centerline 4 ft off a garden) and the matrix refused the
    tread at the write, every round, until the web was refused - so an ordinary join the matrix refuses is taken back out of
    the join's reach, as one deferring to the tree is; a tree lane's join is never taken back."""
    END = 200.0 - (law.JOIN_REACH_FT - 5.0)  # an end 5 ft inside the join reach of the way at y = 200

    class _Refuses(_S):
        def admits(self, key, rec, ignore=None):
            return len(rec["pts"]) <= 2

    s = _Refuses([CONN, [(-100.0, 0.0), (-100.0, END)], [(-200.0, 200.0), (0.0, 200.0)]])
    assert [i for i, _e, _f in law.near_misses(s.M)] == [1]
    assert settle.settle_joins(s) == 1
    got = _pts(s, 1)
    assert got[-1][1] == pytest.approx(END - law.JOIN_REACH_FT - settle.JOIN_BACK_PAD_FT) and not law.near_misses(s.M), "taken back"
    t = _Refuses([CONN, ([(-100.0, 0.0), (-100.0, END)], {}), [(-200.0, 200.0), (0.0, 200.0)]])
    t.M["lanes"][1]["role"] = co.ACCESS_ROLE
    settle.settle_joins(t)
    assert _pts(t, 1)[:2] == [(-100.0, 0.0), (-100.0, END)], "a tree lane is never taken back (its join is left to the write)"


def test_a_house_crowded_with_ends_keeps_the_trees_and_loses_an_ordinary_one() -> None:
    """Homes H41 under the tree (feature 287 wave 6): a house discharging three free ends keeps the tree lane's - never cut -
    and the settle cuts the ordinary end that is farther than the nearer ordinary one; a violator the tree names is an
    ordinary lane (`last_resort.lane_violators` reads `tree.tree_faults`)."""
    # all three ends within 0246's 60 ft of the house's center (feature 328: the reach was 80 ft)
    s = _S([CONN, [(-300.0, 40.0), (-300.0, 170.0)], [(-200.0, 60.0), (-250.0, 190.0)], [(-400.0, 60.0), (-350.0, 190.0)]], houses=[(-300.0, 200.0)])
    s.M["lanes"][3]["role"] = co.ACCESS_ROLE
    assert len(law.fronting_ends(s.M)[0]) == 3
    settle.settle_ends(s)
    tree = [[tuple(q) for q in ln["pts"]] for ln in s.M["lanes"] if ln.get("role") == co.ACCESS_ROLE]
    assert tree == [[(-400.0, 60.0), (-350.0, 190.0)]], "the tree lane stands"
    assert len(s.M["lanes"]) < 4 or _pts(s, 1) != [(-300.0, 40.0), (-300.0, 170.0)] or _pts(s, 2) != [(-200.0, 60.0), (-250.0, 190.0)], "an ordinary end cut"
    assert len(law.fronting_ends(s.M).get(0, [])) <= law.DOORSTEP_MAX


def test_a_dangling_lane_its_trim_cannot_mend_goes_whole(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 297 (research R11): Inashiro's two-point skeleton lane dangled through every round - its trim gave it back
    unchanged - until the last resort dropped it. The docstring's promise, kept: it goes at the step."""
    s = _S([CONN, [(-50.0, 0.0), (-50.0, 300.0)]], houses=[(-50.0, 120.0)])
    monkeypatch.setattr(settle.ends, "_trim_to_service", lambda way, *a, **k: way)
    monkeypatch.setattr(settle.law, "dangling_lane_ends", lambda M, ground=None: [(1, -1)])
    assert settle.settle_dangling(s) == 1
    assert len(s.M["lanes"]) == 1 and s.M["lanes"][0].get("connector")


def test_a_household_way_wandering_over_a_way_at_a_needles_angle_is_cut_at_the_crossing() -> None:
    """Feature 385 T01 (plan D4): cohort seed 10 under the wave 155 re-deal - a household's way crossing the field way at
    about 19 degrees and running on beside it. The two are one path: the household's way is cut at the crossing, its
    door's side kept, and the end left on the way is a needle the next round re-aims as a T."""
    way = [(0.0, 0.0), (400.0, 0.0)]
    wander = [(300.0, 40.0), (100.0, -25.0)]  # ~18 degrees off the way, over it at x ~ 177
    s = _S([CONN, way, wander])
    s.M["lanes"][1]["role"], s.M["lanes"][2]["role"] = "field way", "access"
    assert [(i, n, k) for i, n, k, _x in law.shallow_crossing_at(s.M["lanes"])] == [(1, 0, 2)]
    assert law.shallow_crossings(s.M) and "shallow_crossings" in law.LAW
    piece, end = settle.cut_at_shallow_crossing(s.M["lanes"], 2, 1, [])
    assert end == -1 and piece[0] == (300.0, 40.0) and abs(piece[-1][1]) < 1e-6, "the door's side kept, ending on the way"
    assert settle.cut_at_shallow_crossing(s.M["lanes"], 1, 2, []) is None, "never a tree lane but a household's way"
    assert settle.settle_ends(s) == 1 and not law.shallow_crossings(s.M), "the crossing gone"
    ordinary = _S([CONN, way, [(300.0, 40.0), (100.0, -25.0)]])
    assert settle.cut_at_shallow_crossing(ordinary.M["lanes"], 1, 2, []) is None, "the way kept whole: its longer side would leave the connector (keeps_the_web)"
    square = _S([CONN, way, [(200.0, 100.0), (200.0, -100.0)]])
    assert not law.shallow_crossing_at(square.M["lanes"]), "a square crossing is a crossing"


def test_a_household_way_is_cut_only_onto_a_way_that_stays() -> None:
    """Feature 385 T01 (cohort seed 38, the change's first cohort): a household's way wandering over an ORDINARY lane is not
    cut onto it - a repair may cut or drop that lane and leave the household on nothing - and the ordinary lane is cut
    instead where that keeps the web."""
    way = [(0.0, 0.0), (400.0, 0.0)]
    s = _S([CONN, way, [(300.0, 40.0), (100.0, -25.0)]])
    s.M["lanes"][2]["role"] = "access"
    assert settle.cut_at_shallow_crossing(s.M["lanes"], 2, 1, []) is None, "lane 1 is ordinary: the household is not hung on it"
    s.M["lanes"][1]["role"] = "access"
    assert settle.cut_at_shallow_crossing(s.M["lanes"], 2, 1, []) is not None, "onto another household's way it is cut"
    assert settle.cut_at_shallow_crossing(s.M["lanes"], 0, 1, []) is None, "lane 0 (the connector) crosses nothing here, and is never cut"
    s.M["lanes"][0]["pts"] = [[300.0, 45.0], [100.0, -20.0]]
    assert settle.cut_at_shallow_crossing(s.M["lanes"], 0, 1, []) is None, "the connector crossing shallow is still never cut"


def test_lawful_names_the_first_rule_a_run_breaks() -> None:
    """Feature 385 T03, plan D16: `fault` and `ground_fault` name the rule that turned a run down - seed 17's refusal said only
    "the field is reached by no way", so where the ground refused could not be looked at."""
    s = _S(
        [CONN, [(-500.0, 0.0), (-500.0, 300.0)]], houses=[(-300.0, 300.0), (-460.0, 300.0)], streams=[BROOK], fields=[{"outline": [[-800.0, 400.0], [-700.0, 400.0], [-700.0, 500.0], [-800.0, 500.0]]}]
    )
    s.M["threshing_yards"] = [{"poly": [[-320.0, 100.0], [-280.0, 100.0], [-280.0, 120.0], [-320.0, 120.0]], "of": [-300.0, 300.0]}]
    s.M["houses"].append({"x": -150.0, "y": 600.0, "w": 40.0, "h": 28.0, "rot": 0.0})
    s.M["retirement_houses"] = [{"x": -150.0, "y": 900.0, "w": 40.0, "h": 28.0}]
    ok = settle.Lawful(s)
    assert ok.fault([(-240.0, 0.0), (-250.0, 290.0)], 3.0) is None
    assert ok.fault([(-100.0, 0.0)], 3.0) == "too short"
    assert ok.fault([(-100.0, 0.0), (-100.0, 150.0), (-90.0, 20.0)], 3.0) == "bends"
    assert ok.fault([(-300.0, 0.0), (-300.0, 160.0)], 3.0) == "fabric"
    assert ok.fault([(-750.0, 0.0), (-750.0, 450.0)], 3.0) == "off open ground"
    assert ok.fault([(-150.0, 850.0), (-150.0, 950.0)], 3.0) == "through a building"
    assert ok.fault([(0.0, 50.0), (200.0, 50.0)], 3.0) == "crossing"
    assert ok.fault([(-100.0, 0.0), (-100.0, 150.0)], 3.0) == "dangling_lane_ends"
    assert ok.fault([(-490.0, 0.0), (-490.0, 290.0)], 3.0) in ("doubled_tails", "needle_joins")
    bare = settle.Lawful(_S([CONN]))
    assert bare.fault([(-200.0, 30.0), (-100.0, 0.5)], 3.0) == "needle_joins"
    assert bare.fault([(-60.0, 10.0), (-5.0, 10.0), (0.0, 0.0)], 3.0) in ("connector_hairpins", "bends")


def test_a_field_way_refused_is_counted_by_rule_and_a_later_one_clears_the_count() -> None:
    s = _field_across_the_brook()

    class Turned:
        def __init__(self, why: str | None) -> None:
            self.why = why

        def fault(self, run, width):  # noqa: ANN001, ANN201
            return self.why

        def __call__(self, run, width, skip=None):  # noqa: ANN001, ANN201
            return self.why is None

    assert settle.settle_field(s, Turned("fabric")) == 0
    assert set(s.M["meta"]["field_refusals"]) == {"fabric"} and s.M["meta"]["field_refusals"]["fabric"] >= 1
    assert settle.settle_field(s, Turned(None)) == 1 and "field_refusals" not in s.M["meta"], "a later round that reaches the field leaves no tally"
    plain = _field_across_the_brook()
    assert settle.settle_field(plain, lambda run, width, skip=None: False) == 0 and plain.M["meta"]["field_refusals"]["refused"] >= 1, "a bare judge: refused, unnamed"


def test_a_bare_point_is_no_field_run_and_a_fold_is_named(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 385 T03: a one-point candidate is passed over, never judged; and a fold at a joint is named as one."""
    from l7r.diagram.hamletgen.ways import reach

    s = _field_across_the_brook()
    judged: list = []

    class Takes:
        def fault(self, run, width):  # noqa: ANN001, ANN201
            judged.append(run)

        def __call__(self, run, width, skip=None):  # noqa: ANN001, ANN201
            return True

    monkeypatch.setattr(reach, "field_runs", lambda *a: iter([[(0.0, 0.0)], [(0.0, 50.0), (300.0, 50.0)]]))
    assert settle.settle_field(s, Takes()) == 1 and judged == [[(0.0, 50.0), (300.0, 50.0)]], "the bare point never reached the judge"
    monkeypatch.setattr(settle.law, "needle_ends", lambda tl, blocked: [])
    monkeypatch.setattr(settle.law, "folded_joint_pairs", lambda tl, blocked: [(len(tl) - 1, 0, 0, 0)])
    assert settle.Lawful(_S([CONN])).fault([(-240.0, 0.0), (-250.0, 290.0)], 3.0) == "folded_joints"


def test_a_lane_keeps_the_gap_off_a_neighbor_s_garden_at_its_end() -> None:
    """405 T18 (D69): only a household's own way - its record names the household, `of` (a tree way) or `serves` (a door
    path) - may run beside its own garden; a back lane or cross lane is no household's own and keeps the gap off every
    garden, as 0246 keeps it off another household's."""
    from l7r.diagram.hamletgen.ways.geom import lane_owner
    from l7r.diagram.hamletgen.ways.settle import shapes

    yards = [([(0.0, 0.0)], (0.0, 0.0)), ([(50.0, 0.0)], (50.0, 0.0)), ([(9.0, 9.0)], None)]
    own_way = shapes.theirs(yards, lane_owner({"of": [0.0, 0.0]}))
    assert [(0.0, 0.0)] not in own_way and [(50.0, 0.0)] in own_way, "its own household's exempt, the neighbor's not"
    assert lane_owner({"serves": [50.0, 0.0]}) == (50.0, 0.0), "a door path's household"
    assert shapes.theirs(yards, lane_owner({"pts": []})) == [y for y, _o in yards], "a back lane: every garden keeps its gap"


def test_the_fence_gap_a_foul_is_judged_at_is_the_callers() -> None:
    """405 T107 (D83): `fouled_segment` keeps a run `gap` off another household's garden - 0246's 7 ft unless the caller (the
    knots step's second pass) passes 0081's crop clearance."""
    from l7r.diagram.hamletgen.consts import WEB_CROP_GAP
    from l7r.diagram.hamletgen.ways.settle import shapes

    yards = [([(0.0, 0.0), (20.0, 0.0), (20.0, 20.0), (0.0, 20.0)], (10.0, 10.0))]
    run = [(-5.0, -10.0), (-5.0, 30.0)]  # 5 ft off the fence
    assert shapes.fouled_segment(run, 3.0, [], yards, []) == 0, "inside 0246's 7 ft"
    assert shapes.fouled_segment(run, 3.0, [], yards, [], gap=WEB_CROP_GAP) is None, "clear at the crop clearance"
