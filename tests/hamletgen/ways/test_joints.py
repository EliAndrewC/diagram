"""`hamletgen/ways/joints.py`: two lanes meeting end to end are one way to the walker (GM 2026-09-26)."""

import math

import pytest

from l7r.diagram.hamletgen.ways.joints import as_walked, joints, keeps_the_web, oriented, pulled, straighten_joints, tee, unhooked

from ._builders import _webbed


def _lanes(s):
    return [ln["pts"] for ln in s.M["lanes"] if ln.get("pts")]


def test_a_fold_at_a_joint_becomes_a_t() -> None:
    # Inashiro's bamboo stand: lane 8 comes down, turns back west to where lane 7 begins, and lane 7 runs back east
    s = _webbed([{"pts": [[100.0, 100.0], [200.0, 100.0], [200.0, 140.0], [160.0, 150.0]], "w": 3}, {"pts": [[160.0, 150.0], [300.0, 160.0]], "w": 3}])
    assert joints(s.M["lanes"]) == [(0, -1, 1, 0)]
    assert straighten_joints(s, [], [], []) == 1
    stem, bar = s.M["lanes"][0]["pts"], s.M["lanes"][1]["pts"]
    assert stem[-2] == [200.0, 140.0] and abs(stem[-1][0] - 199.1) < 0.2, "the stem drops from its last vertex to the bar's side"
    assert bar == [[160.0, 150.0], [300.0, 160.0]], "the bar keeps the ground it served"


def test_a_jog_across_a_chain_of_joints_is_pulled_straight() -> None:
    # Inashiro's northeast lane: three records, one line, a 3 ft step in the middle one
    s = _webbed([{"pts": [[100.0, 300.0], [300.0, 300.0]], "w": 3}, {"pts": [[300.0, 300.0], [310.0, 303.0], [320.0, 300.0]], "w": 3}, {"pts": [[320.0, 300.0], [500.0, 300.0]], "w": 3}])
    assert straighten_joints(s, [], [], []) == 2
    assert _lanes(s) == [[[100.0, 300.0], [500.0, 300.0]]]


def test_a_cart_route_and_a_footpath_meeting_end_to_end_are_pulled_straight_and_stay_two_ways() -> None:
    """0081 (feature 328): a jog across the meeting point is pulled straight like any other; the two records keep their widths."""
    s = _webbed([{"pts": [[100.0, 500.0], [300.0, 500.0]], "w": 5}, {"pts": [[300.0, 500.0], [310.0, 503.0], [500.0, 500.0]], "w": 3}])
    assert straighten_joints(s, [], [], []) == 1
    assert [ln["w"] for ln in s.M["lanes"]] == [5, 3], "two records, two widths"
    assert all(p[1] == 500.0 for ln in s.M["lanes"] for p in ln["pts"]), "the jog pulled straight"


def test_a_joint_with_nothing_to_straighten_is_left_alone() -> None:
    s = _webbed([{"pts": [[100.0, 700.0], [300.0, 700.0]], "w": 3}, {"pts": [[300.0, 700.0], [300.0, 900.0]], "w": 3}])
    wall = [[(190.0, 790.0), (210.0, 790.0), (210.0, 810.0), (190.0, 810.0)]]  # across the corner's chord
    assert straighten_joints(s, wall, [], []) == 0


def test_a_fold_no_t_can_mend_is_left_for_the_bends_check() -> None:
    # a lane doubling straight back along the next: both T links cross the same block
    s = _webbed([{"pts": [[100.0, 1000.0], [200.0, 1000.0]], "w": 3}, {"pts": [[200.0, 1000.0], [100.0, 1010.0]], "w": 3}])
    block = [[(90.0, 1003.0), (110.0, 1003.0), (110.0, 1007.0), (90.0, 1007.0)]]
    assert joints(s.M["lanes"]) == [(0, -1, 1, 0)]
    assert straighten_joints(s, block, [], []) == 0


def test_joints_skip_a_loop_a_third_way_and_the_connector() -> None:
    loop = [{"pts": [[0.0, 0.0], [50.0, 0.0]]}, {"pts": [[50.0, 0.0], [0.0, 0.0]]}]
    assert joints(loop) == []
    crossed = [{"pts": [[0.0, 0.0], [50.0, 0.0]]}, {"pts": [[50.0, 0.0], [90.0, 0.0]]}, {"pts": [[50.0, -30.0], [50.0, 30.0]]}]
    assert joints(crossed) == []
    assert joints([{"pts": [[0.0, 0.0], [50.0, 0.0]], "connector": True}, {"pts": [[50.0, 0.0], [90.0, 0.0]]}]) == []
    x, y = oriented([{"pts": [[50.0, 0.0], [0.0, 0.0]]}, {"pts": [[90.0, 0.0], [50.0, 0.0]]}], 0, 0, 1, -1)
    assert x[-1] == y[0] == (50.0, 0.0)


def test_tee_refuses_what_it_cannot_improve() -> None:
    assert tee([(0.0, 0.0), (10.0, 0.0)], [(10.0, 0.0), (10.0, 10.0)], [], [], []) is None, "the foot is the joint"
    y = [(10.0, 0.0), (-10.0, 0.0)]
    assert tee([(0.0, 2.0), (10.0, 0.0)], y, [], [], []) is None, "already touching, and nothing left to keep"
    assert tee([(-5.0, 30.0), (0.0, 2.0), (10.0, 0.0)], y, [], [], []) == [(-5.0, 30.0), (0.0, 2.0)], "already touching: it stops there"
    assert tee([(0.0, 0.0), (100.0, 0.0), (60.0, 10.0)], [(60.0, 10.0), (60.0, -40.0)], [], [], []) is None, "the new last turn is itself a hairpin"
    hard = [[(98.0, 10.0), (104.0, 10.0), (104.0, 30.0), (98.0, 30.0)]]
    assert tee([(0.0, 0.0), (100.0, 0.0), (130.0, 45.0)], [(130.0, 45.0), (40.0, 50.0)], hard, [], []) is None, "the link is not walkable"


def test_pulled_takes_the_furthest_chord_allowed() -> None:
    pts = [(0.0, 0.0), (1.0, 1.0), (2.0, 0.0), (3.0, 1.0)]
    assert pulled(pts, lambda a, b: True) == [(0.0, 0.0), (3.0, 1.0)]
    assert pulled(pts, lambda a, b: b == a + 1) == pts


def test_keeps_the_web_refuses_a_lost_junction_a_split_and_a_stranded_house() -> None:
    other = {"pts": [[50.0, 3.0], [50.0, 60.0]]}
    lanes = [{"pts": [[0.0, 0.0], [100.0, 0.0]]}, other]
    old = [(0.0, 0.0), (100.0, 0.0)]
    assert keeps_the_web(lanes, {0}, old, [(0.0, 0.0), (0.0, 50.0)], []) is False, "the other lane's end no longer meets a way"
    tee_web = [{"pts": [[0.0, 0.0], [98.0, 0.0]]}, {"pts": [[100.0, -50.0], [100.0, 50.0]]}]
    assert keeps_the_web(tee_web, {0}, [(0.0, 0.0), (98.0, 0.0)], [(0.0, 0.0), (50.0, 0.0)], []) is False, "the web would fall into two pieces"
    assert keeps_the_web(lanes, {0}, old, [(0.0, 0.0), (100.0, 0.0), (100.0, 1.0)], [(50.0, 90.0)]) is True
    assert keeps_the_web([{"pts": [[0.0, 0.0], [100.0, 0.0]]}], {0}, old, [(0.0, 400.0), (100.0, 400.0)], [(50.0, 10.0)]) is False, "a farmhouse loses its way"


def test_unhooked_takes_the_hook_off_a_lane_end() -> None:
    assert unhooked([(0.0, 0.0), (100.0, 0.0), (130.0, 5.0)], []) is None, "a long last leg is a route, not a hook"
    assert unhooked([(0.0, 0.0), (100.0, 0.0), (108.0, 6.0)], []) is None, "a shallow last turn is a bend"
    assert unhooked([(0.0, 0.0), (100.0, 0.0), (92.0, 6.0)], []) == [(0.0, 0.0), (100.0, 0.0)], "a nub reaching nothing"
    # Kashikawa: the vertex before the hook already stands on a way the hook met
    on = [(98.0, -40.0), (98.0, 40.0)]
    assert unhooked([(0.0, 0.0), (100.0, 0.0), (94.0, 8.0)], [on]) == [(0.0, 0.0), (100.0, 0.0)]
    # the leg before overshoots the way it joins: cut where it crosses
    o = [(210.0, 650.0), (210.0, 720.0)]
    assert unhooked([(100.0, 700.0), (220.0, 700.0), (212.0, 694.0)], [o]) == [(100.0, 700.0), (210.0, 700.0)]
    assert unhooked([(100.0, 700.0), (220.0, 700.0), (212.0, 694.0)], [o, [(212.0, 690.0), (212.0, 600.0)]]) is None, "two ways met: no single cut"
    assert unhooked([(100.0, 700.0), (220.0, 700.0), (212.0, 694.0)], [[(212.0, 690.0), (260.0, 600.0)]]) is None, "the leg never reaches the way"


def test_the_pass_takes_hooks_off_both_ends() -> None:
    s = _webbed([{"pts": [[108.0, 1206.0], [100.0, 1200.0], [300.0, 1200.0], [292.0, 1206.0]], "w": 3}, {"pts": [[500.0, 1200.0], [600.0, 1200.0], [592.0, 1206.0]], "w": 3}])
    s.M["lanes"][1]["connector"] = True  # the route out's far end is never re-shaped here, hook or no hook
    assert straighten_joints(s, [], [], []) == 2
    assert s.M["lanes"][0]["pts"] == [[100.0, 1200.0], [300.0, 1200.0]]
    assert math.isclose(s.M["lanes"][1]["pts"][-1][0], 592.0)


def test_a_connector_start_that_overshoots_a_lane_and_hooks_back_is_cut_where_it_crosses() -> None:
    """Kashikawa (feature 280): the connector's start ran 7.6 ft past a 3 ft lane and hooked back onto it."""
    s = _webbed([{"pts": [[200.0, 1100.0], [200.0, 1300.0]], "w": 3}, {"pts": [[200.0, 1206.0], [193.0, 1200.0], [600.0, 1200.0]], "w": 6}])
    s.M["lanes"][1]["connector"] = True

    assert straighten_joints(s, [], [], []) == 1
    assert s.M["lanes"][1]["pts"] == [[200.0, 1200.0], [600.0, 1200.0]]


def test_an_end_on_another_lanes_tread_is_set_on_its_centerline() -> None:
    """GM 2026-09-27: a branch ending 2 ft off the through lane's centerline showed its round cap past the far edge."""
    from l7r.diagram.hamletgen.ways.joints import center_lane_ends, centered_end

    through = [((0.0, 0.0), (100.0, 0.0), 3.0)]
    assert centered_end((50.0, 2.0), (50.0, 40.0), 3.0, through) == (50.0, 0.0), "a T end 2 ft short moves onto the line"
    assert centered_end((50.0, -1.0), (50.0, 40.0), 3.0, through) == (50.0, 0.0), "...and one 1 ft past it comes back"
    oblique = centered_end((52.0, 2.0), (92.0, 42.0), 3.0, through)
    assert oblique is not None and oblique[1] == 0.0 and oblique[0] == 50.0, "it slides along its own leg, not sideways"
    assert centered_end((50.0, 0.05), (50.0, 40.0), 3.0, through) is None, "already on the line"
    assert centered_end((50.0, 9.0), (50.0, 40.0), 3.0, through) is None, "past the touch gap is not a junction"
    assert centered_end((50.0, 2.0), (0.0, 2.0), 3.0, through) is None, "a leg running along the lane has no slide"
    assert centered_end((50.0, 2.0), (50.0, 0.0), 3.0, through) is None, "a leg starting ON the lane has no side"
    assert centered_end((50.0, 2.0), (50.0, 40.0), 3.0, [((50.0, 1.0), (50.0, 1.0), 3.0)]) is None, "a point is not a lane"
    wide = centered_end((50.0, 0.5), (50.0, 40.0), 6.0, through)
    assert wide == (50.0, 1.5), "a 6 ft track stops 1.5 ft short, its cap on the 3 ft lane's far edge"
    tip = [((0.0, 0.0), (50.0, 0.0), 3.0)]
    assert centered_end((50.0, 0.0), (80.0, 30.0), 6.0, tip) is None, "end to end at the tip: sliding back would leave it"
    s = _webbed([{"pts": [[0.0, 300.0], [200.0, 300.0]], "w": 3}, {"pts": [[100.0, 402.0], [100.0, 302.5]], "w": 3}])
    s.M["lanes"].append({"pts": [], "w": 3})  # a dropped lane's husk is passed over
    assert center_lane_ends(s) == 1
    assert s.M["lanes"][1]["pts"] == [[100.0, 402.0], [100.0, 300.0]], "the record moves, the far end stays"
    assert "100.0,300.0" in s.ground[s._lane_ink[1][0]]["bed"], "and the ink with it"
    assert center_lane_ends(s) == 0, "a second pass finds nothing to move"


def test_a_lane_is_cut_where_it_crosses_another_and_each_half_ends_on_the_crossing() -> None:
    """`split_at_crossings` (the 269 landing): an X crossing becomes two records meeting the other lane there; an end
    already at a crossing, and the connector, are not cut."""
    from l7r.diagram.hamletgen.ways.joints import split_at_crossings

    from ._builders import _StubSettlement

    s = _StubSettlement(lanes=[[(0.0, 500.0), (1000.0, 500.0)], [(100.0, 0.0), (100.0, 300.0)], [(300.0, 400.0), (300.0, 600.0)], [(600.0, 400.0), (600.0, 502.0)]])
    s.M["lanes"][2]["role"] = "skeleton"
    assert split_at_crossings(s) == 1, "the connector (lane 0) is never cut; the lane ending on it (3) is a junction already"
    pts = [ln["pts"] for ln in s.M["lanes"]]
    assert pts[2] == [[300.0, 400.0], [300.0, 500.0]] and pts[4] == [[300.0, 500.0], [300.0, 600.0]]
    assert s.M["lanes"][4].get("role") == "skeleton", "the cut half keeps its provenance"
    assert pts[1] == [[100.0, 0.0], [100.0, 300.0]] and pts[3] == [[600.0, 400.0], [600.0, 502.0]]


def test_a_lane_and_the_connector_doubling_back_over_a_short_leg_meet_as_a_t() -> None:
    """`fold_the_connector_hairpin` (the 269 landing's review of Kuwabata): 79 + 90 degrees across a 15 ft leg is one
    hairpin; the connector starts at the lane's vertex before the leg and the leg goes. A long leg is no hairpin."""
    from l7r.diagram.hamletgen.ways.joints import fold_the_connector_hairpin, hairpin_over_a_short_leg

    from ._builders import _StubSettlement

    assert hairpin_over_a_short_leg((1929.1, 56.4), (2054.3, 40.0), (2055.3, 25.3), (1408.0, -20.4))
    assert not hairpin_over_a_short_leg((1929.1, 56.4), (2054.3, 40.0), (2055.3, -25.3), (1408.0, -80.4)), "a 65 ft leg"
    assert not hairpin_over_a_short_leg((0.0, 0.0), (100.0, 0.0), (110.0, 0.0), (200.0, 0.0)), "straight on"
    s = _StubSettlement(lanes=[[(2055.3, 25.3), (1408.0, -20.4)], [(1929.1, 56.4), (2054.3, 40.0), (2055.3, 25.3)]])
    assert fold_the_connector_hairpin(s) == 1
    assert s.M["lanes"][0]["pts"][0] == [2054.3, 40.0] and s.M["lanes"][1]["pts"] == [[1929.1, 56.4], [2054.3, 40.0]]
    rev = _StubSettlement(lanes=[[(2055.3, 25.3), (1408.0, -20.4)], [(2055.3, 25.3), (2054.3, 40.0), (1929.1, 56.4)]])
    assert fold_the_connector_hairpin(rev) == 1 and rev.M["lanes"][1]["pts"] == [[2054.3, 40.0], [1929.1, 56.4]]


def test_a_connector_fold_that_would_crowd_the_fabric_is_refused() -> None:
    """`fold_the_connector_hairpin` asks `may_write`: a moved connector nearer a homestead than the old one is not written
    (Kuwabata at the 269 landing, recorded in future-work)."""
    from l7r.diagram.hamletgen.ways.joints import fold_the_connector_hairpin

    from ._builders import _StubSettlement

    s = _StubSettlement(lanes=[[(2055.3, 25.3), (1408.0, -20.4)], [(1929.1, 56.4), (2054.3, 40.0), (2055.3, 25.3)]])
    yard = [(1990.0, 30.0), (2010.0, 30.0), (2010.0, 42.0), (1990.0, 42.0)]  # a steading just below the old connector
    assert fold_the_connector_hairpin(s, [yard]) == 0 and s.M["lanes"][0]["pts"][0] == [2055.3, 25.3]


def test_a_connector_fold_whose_new_first_leg_runs_through_a_building_is_refused() -> None:
    """`fold_the_connector_hairpin` asks the lane law too (`law.breaks_through`): the connector started at the lane's vertex
    would run its first long leg through a byre's box, so the fold is not made and the connector stays as placed."""
    from l7r.diagram.hamletgen.ways import law
    from l7r.diagram.hamletgen.ways.joints import fold_the_connector_hairpin

    from ._builders import _StubSettlement

    s = _StubSettlement(lanes=[[(2055.3, 25.3), (1408.0, -20.4)], [(1929.1, 56.4), (2054.3, 40.0), (2055.3, 25.3)]])
    s.M["byres"] = [{"x": 1731.0, "y": 10.0, "w": 10.0, "h": 8.0}]  # on the middle of the leg the fold would draw, off the old one's
    assert law.breaks_mid_run(s.M) == [], "the connector as placed runs through nothing"
    assert fold_the_connector_hairpin(s) == 0 and s.M["lanes"][0]["pts"][0] == [2055.3, 25.3]


def test_a_connector_starting_at_the_way_outs_gate_is_not_moved_off_it_by_a_hairpin_fold() -> None:
    """Feature 287 wave 6 (cohort seed 37), as feature 320 keeps it: the households' ways reach the root at the connector's
    start, and a fold that started the connector at a lane's vertex would leave them ending off it - where the homesteads
    stage recorded the way out's gate the connector stands, and the settle re-aims the lane's end instead
    (`law.connector_hairpin_ends`)."""
    from l7r.diagram.hamletgen.ways.joints import fold_the_connector_hairpin

    from ._builders import _StubSettlement

    s = _StubSettlement(lanes=[[(2055.3, 25.3), (1408.0, -20.4)], [(1929.1, 56.4), (2054.3, 40.0), (2055.3, 25.3)]])
    s.M["way_out_gate"] = [2055.3, 25.3]
    assert fold_the_connector_hairpin(s) == 0 and s.M["lanes"][0]["pts"][0] == [2055.3, 25.3]


def test_a_joint_moved_back_drops_its_own_vertex_from_either_side() -> None:
    from l7r.diagram.hamletgen.ways.joints import moved_back

    x, y = [(0.0, 0.0), (10.0, 0.0), (12.0, 5.0)], [(12.0, 5.0), (20.0, 0.0), (30.0, 0.0)]
    assert moved_back(x, y) == [([(0.0, 0.0), (10.0, 0.0)], [(10.0, 0.0), (20.0, 0.0), (30.0, 0.0)]), ([(0.0, 0.0), (10.0, 0.0), (20.0, 0.0)], [(20.0, 0.0), (30.0, 0.0)])]
    assert moved_back(x[1:], y[1:]) == [], "two-point lanes give nothing up"


def test_a_z_across_a_joint_is_mended_by_moving_the_joint_back_or_left_where_nothing_is_clear(monkeypatch: pytest.MonkeyPatch) -> None:
    """`_joint_moved_back` (feature 308): the first clear move that keeps the web is committed to both records, in their own
    orientation; a second record refused puts the first back; nothing clear, nothing changed."""
    from l7r.diagram.hamletgen.ways import joints as J

    x, y = [(0.0, 0.0), (10.0, 0.0), (12.0, 5.0)], [(12.0, 5.0), (20.0, 0.0), (30.0, 0.0)]
    lanes = [{"pts": [list(q) for q in x[::-1]]}, {"pts": [list(q) for q in y]}]  # lane 0 recorded from the joint out (end 0)
    commits: list[tuple[int, list]] = []
    refuse = {"lane": None}

    def commit(lanes_, m, pts, *a, **k):  # type: ignore[no-untyped-def]
        commits.append((m, pts))
        return refuse["lane"] != m

    class S:
        def reink_lane(self, i: int) -> None: ...

    monkeypatch.setattr(J, "commit_lane", commit)
    monkeypatch.setattr(J, "admits_lane", lambda s: None)
    monkeypatch.setattr(J, "keeps_the_web", lambda *a: True)
    monkeypatch.setattr(J, "_clear_link", lambda *a: True)
    assert J._joint_moved_back(S(), lanes, (0, 0, 1, 0), x, y, [], [], [], [])  # type: ignore[arg-type]
    assert commits[0][0] == 0 and commits[0][1] == [[10.0, 0.0], [0.0, 0.0]], "lane 0 shortened, in its own orientation"
    assert commits[1] == (1, [[10.0, 0.0], [20.0, 0.0], [30.0, 0.0]]), "lane 1 started from lane 0's new end"
    commits.clear()
    refuse["lane"] = 1
    assert not J._joint_moved_back(S(), lanes, (0, 0, 1, 0), x, y, [], [], [], [])  # type: ignore[arg-type]
    assert [m for m, _ in commits].count(0) >= 2, "the first record put back when the second is refused"
    commits.clear()
    refuse["lane"] = 0
    assert not J._joint_moved_back(S(), lanes, (0, 0, 1, 0), x, y, [], [], [], [])  # type: ignore[arg-type]
    monkeypatch.setattr(J, "keeps_the_web", lambda *a: False)
    assert not J._joint_moved_back(S(), lanes, (0, 0, 1, -1), x, y, [], [], [], [])  # type: ignore[arg-type]
    monkeypatch.setattr(J, "_bends_badly", lambda pts: True)
    assert not J._joint_moved_back(S(), lanes, (0, -1, 1, 0), x, y, [], [], [], []), "a walk still bent: not moved"  # type: ignore[arg-type]
    monkeypatch.setattr(J, "_clear_link", lambda *a: False)
    assert not J._joint_moved_back(S(), lanes, (0, -1, 1, 0), x, y, [], [], [], []), "nothing clear: nothing changed"  # type: ignore[arg-type]


def test_a_z_no_t_mends_is_mended_by_moving_the_joint_back(monkeypatch: pytest.MonkeyPatch) -> None:
    """`_one_joint` (feature 308): a Z across a joint - each record clean, their walk bent - that no T mends is handed to
    `_joint_moved_back`, and the joint pass reports the rewrite."""
    from l7r.diagram.hamletgen.ways import joints as J

    s = _webbed([{"pts": [[0.0, 0.0], [100.0, 0.0], [104.0, 10.0]], "w": 3}, {"pts": [[104.0, 10.0], [200.0, 0.0], [300.0, 0.0]], "w": 3}])
    monkeypatch.setattr(J, "tee", lambda *a: None)
    monkeypatch.setattr(J, "_bends_badly", lambda pts: len(pts) > 3)
    moved: list[tuple[int, int, int, int]] = []
    monkeypatch.setattr(J, "_joint_moved_back", lambda s_, lanes, joint, *a: moved.append(joint) or True)
    assert J._one_joint(s, s.M["lanes"], [], [], [], [])  # type: ignore[arg-type]
    assert moved == [(0, -1, 1, 0)], "the Z's joint moved back"


def test_two_lanes_meeting_end_to_end_are_never_pulled_into_a_kink(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 317 (seed 47 at 20 households): a corridor hung from another's start at a door, the pair met end to end; pulled
    taut as one round the map's walls, the run lost the vertex of its bend and kinked at the next - a tree lane no settle may
    cut. A pull that makes a kink the two did not have is not taken (the walls' pull stood in for by the seed's own result)."""
    from l7r.diagram.hamletgen.ways import joints as J
    from l7r.diagram.hamletgen.ways import law

    x = [[657.0, 328.0], [648.0, 420.0]]
    y = [[648.0, 420.0], [669.0, 446.0], [669.0, 458.0], [657.0, 482.0], [490.0, 473.0]]
    assert not law.kinks([tuple(p) for p in [*x, *y[1:]]]), "the two as one: no kink"
    seeds_pull = [(657.0, 328.0), (648.0, 420.0), (669.0, 458.0), (657.0, 482.0), (490.0, 473.0)]
    assert law.kinks(seeds_pull), "...the seed's pull: a kink"
    monkeypatch.setattr(J, "pulled", lambda pts, ok: list(seeds_pull))
    s = _webbed([{"pts": x, "w": 3}, {"pts": y, "w": 3}])
    straighten_joints(s, [], [], [])
    assert len(_lanes(s)) == 2 and all(not law.kinks([tuple(p) for p in pts]) for pts in _lanes(s)), "not taken: no kink made"


def test_lanes_met_end_to_end_are_walked_as_one_way() -> None:
    """`as_walked` (feature 318): two records meeting end to end at a joint are one way, in walking order whichever way each
    was drawn; a lane a third way touches at its end, and a lane of one point, stand alone."""
    lanes = [
        {"pts": [[0.0, 0.0], [100.0, 0.0]]},
        {"pts": [[200.0, 0.0], [100.0, 0.0]]},  # drawn backwards, met end to end at (100, 0)
        {"pts": [[500.0, 0.0], [600.0, 0.0]]},
        {"pts": [[600.0, 0.0], [700.0, 0.0]]},
        {"pts": [[600.0, -50.0], [600.0, 50.0]]},  # a third way through the second joint: no joint there
        {"pts": [[900.0, 900.0]]},
    ]
    ways, owner = as_walked(lanes)
    assert owner[0] == owner[1] and ways[owner[0]] in ([(0.0, 0.0), (100.0, 0.0), (200.0, 0.0)], [(200.0, 0.0), (100.0, 0.0), (0.0, 0.0)])
    assert len({owner[2], owner[3], owner[4]}) == 3, "a joint a third way touches is no joint"
    assert ways[owner[5]] == [(900.0, 900.0)] and len(ways) == 5
    loop = [{"pts": [[0.0, 0.0], [100.0, 0.0], [100.0, 100.0]]}, {"pts": [[100.0, 100.0], [0.0, 100.0], [0.0, 0.0]]}]
    ways, owner = as_walked(loop)
    assert len(ways) == 2 and owner == [0, 1], "two lanes meeting at both ends are a loop, not a joint"


def test_a_chain_met_at_its_first_lane_s_start_is_walked_back_to_its_true_first_lane() -> None:
    """`as_walked` (feature 320): a walk starting at a lane whose START is a joint walks back along the chain to the lane
    with a free end first, so the chain reads as ONE way from that free end, both records mapped to it."""
    lanes = [{"pts": [[10.0, 0.0], [20.0, 0.0]]}, {"pts": [[0.0, 0.0], [10.0, 0.0]]}]
    assert joints(lanes) == [(0, 0, 1, -1)]
    ways, owner = as_walked(lanes)
    assert owner == [0, 0] and ways == [[(0.0, 0.0), (10.0, 0.0), (20.0, 0.0)]], "one way, walked from lane 1's free end"


def test_a_pulled_walk_is_split_at_the_old_joint_and_written_back_as_its_two_records(monkeypatch: pytest.MonkeyPatch) -> None:
    """`split_at` cuts at the walk's point nearest the joint (a vertex there is not doubled); `_split_committed` writes both
    records in their own orientation, puts the first back when the second is refused, and writes nothing for a point part."""
    from l7r.diagram.hamletgen.ways import joints as J

    assert J.split_at([(0.0, 0.0), (100.0, 0.0)], (40.0, 3.0)) == ([(0.0, 0.0), (40.0, 0.0)], [(40.0, 0.0), (100.0, 0.0)])
    assert J.split_at([(0.0, 0.0), (40.0, 0.0), (100.0, 0.0)], (40.0, 0.0)) == ([(0.0, 0.0), (40.0, 0.0)], [(40.0, 0.0), (100.0, 0.0)])
    assert not J._split_committed(None, [{"pts": [[40.0, 0.0], [0.0, 0.0]]}, {"pts": [[40.0, 0.0], [100.0, 0.0]]}], (0, 0, 1, 0), [(0.0, 0.0), (100.0, 0.0)], (40.0, 0.0), [], [], []), (
        "already split so: nothing to do"
    )  # type: ignore[arg-type]
    lanes = [{"pts": [[40.0, 3.0], [0.0, 0.0]]}, {"pts": [[40.0, 3.0], [100.0, 0.0]]}]
    commits: list[tuple[int, list]] = []
    refuse = {"lane": None}

    def commit(lanes_, m, pts, *a, **k):  # type: ignore[no-untyped-def]
        commits.append((m, pts))
        return refuse["lane"] != m

    class S:
        def reink_lane(self, i: int) -> None: ...

    monkeypatch.setattr(J, "commit_lane", commit)
    monkeypatch.setattr(J, "admits_lane", lambda s: None)
    walk = [(0.0, 0.0), (100.0, 0.0)]
    assert J._split_committed(S(), lanes, (0, 0, 1, 0), walk, (40.0, 0.0), [], [], [])  # type: ignore[arg-type]
    assert commits[0] == (0, [[40.0, 0.0], [0.0, 0.0]]) and commits[1] == (1, [[40.0, 0.0], [100.0, 0.0]])
    commits.clear()
    refuse["lane"] = 1
    assert not J._split_committed(S(), lanes, (0, -1, 1, -1), walk, (40.0, 0.0), [], [], [])  # type: ignore[arg-type]
    assert commits[-1][0] == 0, "the first record put back"
    refuse["lane"] = 0
    assert not J._split_committed(S(), lanes, (0, -1, 1, 0), walk, (40.0, 0.0), [], [], [])  # type: ignore[arg-type]
    assert not J._split_committed(S(), lanes, (0, -1, 1, 0), walk, (0.0, 0.0), [], [], [])  # type: ignore[arg-type]
