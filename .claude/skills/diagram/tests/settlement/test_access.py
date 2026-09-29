"""Feature 287, plan M3's seat half (homes H16, ways W01): the access-corridor tree reserved at seating."""

from __future__ import annotations

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.rolling import access
from l7r.diagram.settlement.rolling.access import AccessTree, _seg_box_gap, access_corridor, corridor_clear, doors_of, reserve, start_tree
from tests.hamletgen._builders import a_plan


def _open(W: float = 1400.0) -> Settlement:
    s = Settlement(W, W, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=10, down_deg=90, water_flow=90, nucleated=True)
    s._nucleated = True
    return s


def test_the_segment_box_gap_is_zero_where_they_meet_and_the_true_gap_elsewhere() -> None:
    box = (0.0, 0.0, 10.0, 10.0)
    assert _seg_box_gap((0.0, 0.0), (20.0, 0.0), box) == 0.0, "an end inside"
    assert _seg_box_gap((-20.0, 0.0), (20.0, 0.0), box) == 0.0, "a crossing"
    assert _seg_box_gap((10.0, -20.0), (10.0, 20.0), box) == 5.0
    assert _seg_box_gap((20.0, 20.0), (30.0, 30.0), box) == ((15**2) * 2) ** 0.5


def test_the_tree_covers_a_box_its_strip_meets_and_offers_its_nearest_points() -> None:
    tree = AccessTree(7.0)
    tree.add((0.0, 0.0), (100.0, 0.0))
    tree.add((0.0, 200.0), (100.0, 200.0))
    assert tree.covers_box((50.0, 10.0, 10.0, 8.0)), "the box's edge 6 px off the line: inside the 7 px strip"
    assert not tree.covers_box((50.0, 10.0, 10.0, 4.0)), "8 px off: clear"
    assert not tree.covers_box((50.0, 30.0, 10.0, 10.0))
    assert not tree.covers_box((500.0, 0.0, 10.0, 10.0)), "far along: the index returns nothing"
    got = tree.targets((50.0, 60.0))
    assert got[0] == (50.0, 0.0) and (50.0, 200.0) in got and (0.0, 0.0) in got, "the nearest point first, then the points along"


def test_a_homestead_leaves_by_its_dooryard_never_a_back_wall() -> None:
    """The forecourt, then the yard's far edge and its two flanks - every door in the dooryard (ways W57)."""
    doors = doors_of({"house": (0.0, 0.0, 40.0, 20.0), "yard": (0.0, 30.0, 30.0, 20.0)}, 7.0)
    assert doors == [(0.0, 30.0), (0.0, 40.0), (-28.0, 30.0), (28.0, 30.0)], "the flanks carried past the gable: 20 + 7 + 1"
    assert all(y > 10.0 for _x, y in doors), "none behind or beside the house"
    assert doors_of({"house": (0.0, 0.0, 10.0, 20.0), "yard": (0.0, 30.0, 30.0, 20.0)})[2] == (-15.0, 30.0), "a yard wider than its house"
    assert doors_of({"house": (0.0, 0.0, 40.0, 20.0), "yard": None}) == [(0.0, 12.0)], "no yard: a step off the front wall"


def test_a_turned_yards_far_edge_door_stands_on_its_drawn_edge_not_its_box() -> None:
    """Merge of features 280 and 287 (cohort seed 32): a turned yard's axis-aligned box reaches past the drawn yard, and a
    far-edge door set by the box stood 16 ft beyond it - an end the lane law reads as reaching nothing. With the bundle's
    turn the door is on the drawn edge: here a 50 x 28 yard turned 12 degrees, straight out along its own axis."""
    import math

    th = math.radians(12.0)
    u = (-math.sin(th), math.cos(th))  # the house's front normal, turned
    yard = (u[0] * 40.0, u[1] * 40.0, 50.0, 28.0)
    box = (yard[0], yard[1], 50.0 * math.cos(th) + 28.0 * math.sin(th), 50.0 * math.sin(th) + 28.0 * math.cos(th))
    geom = {"house": (0.0, 0.0, 46.0, 28.0), "yard": yard, "boxes": {"house": (0.0, 0.0, 46.0, 28.0), "yard": box}, "turn": 12.0}
    far = doors_of(geom)[1]
    assert math.dist(far, yard[:2]) == pytest.approx(14.0), "the yard's own half depth"
    del geom["turn"]
    assert math.dist(doors_of(geom)[1], yard[:2]) > 20.0, "the box alone overstates it"


def test_the_exit_strip_starts_the_tree_and_the_manifest_records_it() -> None:
    s = _open()
    tree = start_tree(s, (100.0, 100.0), (0.0, 1.0), 50.0)
    assert s._access is tree and tree.segs == [((100.0, 100.0), (100.0, 150.0))]
    assert s.M["access_exit"] == [[100.0, 100.0], [100.0, 150.0]] and s.M["access_corridors"] == []
    reserve(s, ((0.0, 0.0), (100.0, 100.0)))
    assert len(tree.segs) == 2 and s.M["access_corridors"] == [{"pts": [[0.0, 0.0], [100.0, 100.0]]}]
    reserve(s, ((1.0, 1.0), (2.0, 2.0)), of=(5.0, 5.0))
    assert s.M["access_corridors"][-1] == {"pts": [[1.0, 1.0], [2.0, 2.0]], "of": [5.0, 5.0]}


def test_a_corridor_through_another_homestead_or_its_own_house_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    """W01 (a): two placed homesteads close the only straight run to the tree; a seat with a clear run is admitted."""
    # the SE bed stands at the flank door the run round the neighbor leaves by; the corridor's own parts are
    # `test_a_corridor_over_its_own_bed_or_well_pocket_is_refused`'s (feature 287 M8)
    monkeypatch.setattr(access, "parts_clear", lambda *a: True)
    s = _open()
    start_tree(s, (700.0, 300.0), (1.0, 0.0), 300.0)
    s.placed.append((700.0, 500.0, 120.0, 60.0))  # a neighbor square across the direct run to the strip
    blocked = s._bundle_geom(700.0, 700.0, 46.0, 28.0, "SE", rot=0.0)
    assert not corridor_clear(s, doors_of(blocked)[0], (700.0, 300.0), blocked)
    assert not corridor_clear(s, (700.0, 740.0), (700.0, 650.0), blocked), "a run through its own house"
    got = access_corridor(s, blocked)
    assert got is not None and got[1][0] > 800.0, "...but a point further along the strip is reached round the neighbor"
    s.placed.append((640.0, 620.0, 120.0, 400.0))
    s.placed.append((760.0, 620.0, 120.0, 400.0))
    s.placed.append((700.0, 800.0, 400.0, 60.0))
    assert access_corridor(s, blocked) is None, "hemmed in on every side: refused"
    open_ = s._bundle_geom(1000.0, 300.0, 46.0, 28.0, "SE", rot=0.0)
    assert access_corridor(s, open_) is not None


def test_a_corridor_over_ground_the_boundary_refuses_is_refused() -> None:
    plan = a_plan(households=10)
    plan.seat = hg.seat_cluster(plan)
    s = _open()
    s.field_polys.append(list(plan.envelope))
    cx, cy = float(plan.seat["cx"]), float(plan.seat["cy"])
    s.block_polys.append([(cx + 150.0, cy - 40.0), (cx + 250.0, cy - 40.0), (cx + 250.0, cy + 40.0), (cx + 150.0, cy + 40.0)])  # no-build ground
    hg.homesteads.boundary.install_site_boundary(s, plan)
    start_tree(s, (cx, cy), plan.seat["out"], 100.0)
    geom = s._bundle_geom(cx, cy, 46.0, 28.0, "SE", rot=0.0)
    assert not corridor_clear(s, (cx, cy + 40.0), (700.0, 700.0), geom), "into the paddy: the field side of a chord"
    assert not corridor_clear(s, (cx + 60.0, cy), (cx + 300.0, cy), geom), "through the outline of the other ground"
    assert corridor_clear(s, (cx - 60.0, cy), (cx - 300.0, cy), geom), "open ground"


def test_no_tree_admits_no_corridor_and_the_placer_asks_none() -> None:
    s = _open()
    geom = s._bundle_geom(500.0, 500.0, 46.0, 28.0, "SE")
    assert access_corridor(s, geom) is None
    s._seat_search = {"candidates": 0, "placer_calls": 0, "positions": 0, "rects": 0, "rounds": 0}
    assert s._parts_fit(geom) and "access" not in geom


def test_the_placer_admits_a_seat_only_with_its_corridor_and_reserves_it() -> None:
    """The seat half end to end: `_parts_fit` refuses a boxed-in seat, admits an open one with its corridor on the geometry,
    `try_place` reserves the corridor, and the envelope of a later homestead on the corridor is refused."""
    s = _open()
    s._seat_search = {"candidates": 0, "placer_calls": 0, "positions": 0, "rects": 0, "rounds": 0}
    start_tree(s, (700.0, 300.0), (0.0, -1.0), 200.0)
    assert s.try_place(700.0, 520.0, "plain")
    assert len(s.M["access_corridors"]) == 1 and len(s._access.segs) == 2
    a, b = s._access.segs[1]
    mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    assert s._envelope_blocked((mid[0], mid[1], 20.0, 20.0)) is True, "no homestead on a reserved corridor"
    s.placed.extend([(640.0, 900.0, 60.0, 400.0), (760.0, 900.0, 60.0, 400.0), (700.0, 1120.0, 200.0, 60.0), (700.0, 760.0, 200.0, 40.0)])
    geom = s._bundle_geom(700.0, 900.0, 46.0, 28.0, "SE", rot=0.0)
    assert not s._parts_fit(geom), "boxed in: no corridor, no seat"
    assert access.TARGETS_TRIED >= 2


def test_a_corridor_the_ways_ground_test_refuses_is_refused_and_the_exit_strip_turns_off_it() -> None:
    """The ways' own ground test, installed by the hamlet's seating (`_corridor_ground`): a corridor it refuses is refused
    though the site boundary admits it; the exit strip is held to it, turned off its bearing where refused straight out,
    and a margin whose every turn is refused has no way out."""
    s = _open()
    start_tree(s, (100.0, 100.0), (0.0, 1.0), 50.0)
    geom = s._bundle_geom(1000.0, 1000.0, 46.0, 28.0, "SE", rot=0.0)
    assert corridor_clear(s, (500.0, 500.0), (500.0, 300.0), geom), "no test installed (a village roll): the boundary's alone"
    s._corridor_ground = lambda run: run[-1][0] <= 500.0  # a stand-in: ground east of x = 500 is unlawful
    assert corridor_clear(s, (500.0, 500.0), (500.0, 300.0), geom)
    assert not corridor_clear(s, (500.0, 500.0), (700.0, 300.0), geom), "the ground test refuses it"
    assert access.exit_bearing(s, (500.0, 500.0), (0.0, -1.0), 100.0) == (0.0, -1.0), "straight out"
    u = access.exit_bearing(s, (500.0, 500.0), (1.0, 0.0), 100.0)
    assert u is not None and u[0] < 1e-9 and abs(u[1]) == pytest.approx(1.0), "east refused: turned a quarter"
    s._corridor_ground = lambda run: False
    assert access.exit_bearing(s, (500.0, 500.0), (0.0, -1.0), 100.0) is None


def test_a_tree_behind_the_house_is_reached_round_the_gable_from_the_dooryard() -> None:
    """No straight run from the dooryard reaches a tree behind the house past its neighbors; a flank door carried back
    along the gable does, in two legs - and each leg is its own record, the first naming the house."""
    s = _open()
    start_tree(s, (720.0, 470.0), (0.0, -1.0), 20.0)  # the tree starts just behind the back wall: every straight run crosses the house
    geom = s._bundle_geom(720.0, 520.0, 46.0, 28.0, "SE", rot=0.0)
    got = access_corridor(s, geom)
    assert got is not None and len(got) == 3, "round the gable"
    door, turn, _q = got
    assert door[1] > 520.0 and turn[1] < 520.0 - 14.0 - 7.0, "leaves the dooryard, turns past the back wall"
    assert access.round_the_gable(geom, door, 7.0) == turn
    reserve(s, got, of=(720.0, 520.0))
    recs = s.M["access_corridors"]
    assert len(recs) == 2 and recs[0]["of"] == [720.0, 520.0] and "of" not in recs[1] and recs[0]["pts"][1] == recs[1]["pts"][0]
    assert access.legs(got) == [(door, turn), (turn, _q)]


def test_a_corridor_round_the_gable_never_doubles_back_to_a_tree_in_front(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 287, homes wave 5 (cohort seed 32): with every straight run from the dooryard refused, a flank door carried
    past the gable to a tree point back in FRONT of the house turns by more than the web's bend law allows (`doubles_back`,
    `HAIRPIN_DEG`, the ways' own `_HAIRPIN_DEG`) - the web could not draw it and left the house with no way. The seat is
    refused instead; the same search to a tree behind the house still goes round the gable."""
    from l7r.diagram.hamletgen.ways.clearance import _HAIRPIN_DEG

    assert access.HAIRPIN_DEG == _HAIRPIN_DEG
    assert access.doubles_back((0.0, 0.0), (0.0, -10.0), (1.0, 20.0)) and not access.doubles_back((0.0, 0.0), (0.0, -10.0), (20.0, -12.0))
    assert not access.doubles_back((0.0, 0.0), (0.0, 0.0), (1.0, 1.0)), "a leg of no length turns nowhere"
    turns: list[tuple[float, float]] = []
    real = access.round_the_gable

    def gable(geom, door, half):  # type: ignore[no-untyped-def]
        turns.append(turn := real(geom, door, half))
        return turn

    monkeypatch.setattr(access, "round_the_gable", gable)
    monkeypatch.setattr(access, "parts_clear", lambda *a: True)  # the SE bed at the flank door is not under test (M8)
    monkeypatch.setattr(access, "standing_clear", lambda s_, a, b, memo=None: any(access.math.dist(p, t) < 1e-6 for t in turns for p in (a, b)))

    def search(tree_at: tuple[float, float], out: tuple[float, float]) -> tuple[tuple[float, float], ...] | None:
        s = _open()
        turns.clear()
        start_tree(s, tree_at, out, 60.0)
        return access_corridor(s, s._bundle_geom(720.0, 520.0, 46.0, 28.0, "SE", rot=0.0))

    assert search((820.0, 750.0), (1.0, 0.0)) is None, "the tree in front, beside the house: only a hairpin reaches it"
    assert len(search((720.0, 400.0), (0.0, -1.0)) or ()) == 3, "the tree behind: round the gable"
    monkeypatch.setattr(access, "doubles_back", lambda a, b, c: False)
    got = search((820.0, 750.0), (1.0, 0.0))
    assert got is not None and len(got) == 3, "the refusal is the hairpin's: without it the gable run is taken"


def test_what_stands_is_asked_once_while_nothing_of_it_changes() -> None:
    s = _open()
    start_tree(s, (100.0, 100.0), (0.0, 1.0), 50.0)
    calls: list[int] = []
    s._corridor_ground = lambda run: calls.append(1) or True
    geom = s._bundle_geom(1000.0, 1000.0, 46.0, 28.0, "SE", rot=0.0)
    assert corridor_clear(s, (500.0, 500.0), (500.0, 300.0), geom) and corridor_clear(s, (500.0, 500.0), (500.0, 300.0), geom)
    assert len(calls) == 1, "remembered"
    s.placed.append((900.0, 900.0, 10.0, 10.0))
    assert corridor_clear(s, (500.0, 500.0), (500.0, 300.0), geom) and len(calls) == 2, "a box placed since: asked again"
    start_tree(s, (100.0, 100.0), (0.0, 1.0), 50.0)
    assert "_corridor_memo" not in s.__dict__, "a new seating forgets"


def test_the_bounded_gap_test_gives_the_exact_gaps_verdict() -> None:
    """`seg_box_within` decides by one distance where it can (a box beyond the segment's widened box, a center within the
    reach, a center past the reach by its half-diagonal) and by the exact gap otherwise - the same verdict as
    `_seg_box_gap(...) < t` on every segment and box, each branch among them."""
    import random

    from l7r.diagram.settlement.rolling.access import seg_box_within

    rng = random.Random(11)
    hits = 0
    for _ in range(3000):
        a, b = (rng.uniform(0, 200), rng.uniform(0, 200)), (rng.uniform(0, 200), rng.uniform(0, 200))
        box = (rng.uniform(0, 200), rng.uniform(0, 200), rng.uniform(1, 60), rng.uniform(1, 60))
        t = rng.uniform(0.5, 20.0)
        want = _seg_box_gap(a, b, box) < t
        assert seg_box_within(a, b, box, t) == want, (a, b, box, t)
        hits += want
    assert 300 < hits < 2700


def _plain_search(s, geom):  # type: ignore[no-untyped-def]
    """`access_corridor`'s search asked straight through, strip by strip - what the shared search must return."""
    tree = s._access
    doors = doors_of(geom, tree.half)
    for door in doors:
        for q in tree.targets(door):
            if access.math.dist(door, q) < 1e-6 or corridor_clear(s, door, q, geom):
                return access.drawn_corridor(s, (door, q), geom)
    for door in doors[2:]:
        turn = access.round_the_gable(geom, door, tree.half)
        if corridor_clear(s, door, turn, geom):
            for q in tree.targets(turn):
                if access.math.dist(turn, q) < 1e-6 or (not access.doubles_back(door, turn, q) and corridor_clear(s, turn, q, geom)):
                    return access.drawn_corridor(s, (door, turn, q), geom)
    return None


def test_the_homesteads_of_one_house_and_yard_share_the_search_and_each_gets_its_own_answer() -> None:
    """The four sides of a seat share one search (their house and yard), and each takes the first corridor its own
    fixtures leave clear: over fixtures laid across the first corridors, straight and round the gable, and a door on
    the tree itself, the shared search returns what the plain search returns - a refusal included."""
    import random

    rng = random.Random(3)
    got = []
    for center, tree_at, out in (((720.0, 520.0), (720.0, 470.0), (0.0, -1.0)), ((700.0, 700.0), (700.0, 300.0), (1.0, 0.0)), ((700.0, 700.0), (700.0, 735.0), (1.0, 0.0))):
        s = _open()
        start_tree(s, tree_at, out, 300.0 if out[0] else 20.0)
        base = s._bundle_geom(center[0], center[1], 46.0, 28.0, "SE", rot=0.0)
        for _ in range(12):
            geom = {**base, "boxes": {**base["boxes"], "fixtures": {f"f{k}": (center[0] + rng.uniform(-60, 60), center[1] + rng.uniform(-60, 60), 8.0, 8.0) for k in range(rng.randint(0, 3))}}}
            want = _plain_search(s, geom)
            assert access_corridor(s, geom) == want
            got.append(want)
    assert any(c is None for c in got) and any(c is not None and len(c) == 3 for c in got) and any(c is not None and len(c) == 2 for c in got)


def test_the_indexed_targets_are_the_nearest_of_every_point_of_the_tree_in_its_order() -> None:
    """`AccessTree.targets` reads the points along from an index; over trees of one to thirty corridors, small and large,
    it returns what sorting every point of the tree (each corridor's nearest point, then its points along) returns."""
    import math
    import random

    from l7r.diagram.settlement._geom import seg_closest

    def plain(tree, p):  # type: ignore[no-untyped-def]
        pts = []
        for a, b in tree.segs:
            pts.append(seg_closest(p[0], p[1], a, b))
            n = int(math.dist(a, b) // access.TARGET_STEP_PX)
            pts += [(a[0] + (b[0] - a[0]) * k / max(1, n), a[1] + (b[1] - a[1]) * k / max(1, n)) for k in range(n + 1)]
        pts.sort(key=lambda q: math.dist(p, q))
        return pts[: access.TARGETS_TRIED]

    rng = random.Random(4)
    for size in (1, 2, 5, 30):
        tree = AccessTree(7.0)
        for _ in range(size):
            a = (rng.uniform(0, 1400), rng.uniform(0, 1400))
            tree.add(a, (a[0] + rng.uniform(-400, 400), a[1] + rng.uniform(-400, 400)) if rng.random() < 0.8 else (a[0] + 20.0, a[1]))
        for _ in range(60):
            p = (round(rng.uniform(-200, 1600)), round(rng.uniform(-200, 1600)))
            assert tree.targets(p) == plain(tree, p), (size, p)
    tiny = AccessTree(7.0)
    tiny.add((0.0, 0.0), (10.0, 0.0))
    assert tiny.targets((5.0, 5.0)) == plain(tiny, (5.0, 5.0)) and len(tiny.targets((5.0, 5.0))) == 2, "a tree of fewer points than tried: every point"


def test_a_corridor_is_drawn_from_where_it_leaves_its_own_yard() -> None:
    """Feature 287 wave 6 (ways W01; cohort seed 39 under the probes: an 81-mat yard 76 x 53 ft, the door in its middle): the
    matrix forbids a way on a yard, its own household's too, so the corridor the seating reserves and the web draws starts
    where its tread leaves the yard for good - the yard read as the matrix reads it, turned with its house (`yard_quad`)."""
    geom = {"house": (0.0, 0.0, 40.0, 28.0), "yard": (0.0, 60.0, 80.0, 50.0), "turn": 0.0}
    quad = access.yard_quad(geom)
    assert quad is not None and sorted(round(q[1]) for q in quad) == [35, 35, 85, 85]
    turned = access.yard_quad({**geom, "turn": 90.0})
    assert turned is not None and sorted(round(q[0]) for q in turned) == [-25, -25, 25, 25], "turned with its house"
    assert access.yard_quad({"house": (0.0, 0.0, 1.0, 1.0), "yard": None}) is None
    run = [(0.0, 60.0), (0.0, 400.0)]
    past = access.past_the_yard(run, quad, access.TREAD_HALF_FT)
    assert past is not None and past[0] == (0.0, pytest.approx(85.0 + access.TREAD_HALF_FT + access.YARD_EXIT_PAD_FT)) and past[-1] == (0.0, 400.0)
    assert access.past_the_yard([(0.0, 300.0), (0.0, 400.0)], quad, 1.5) is None, "never near it"
    assert access.past_the_yard([(0.0, 400.0), (0.0, 60.0)], quad, 1.5) is None, "ending on it"
    bent = access.past_the_yard([(0.0, 60.0), (0.0, 60.0), (0.0, 100.0), (200.0, 100.0)], quad, 1.5)
    assert bent is not None and bent[0] == (0.0, pytest.approx(87.5)) and bent[-1] == (200.0, 100.0), "left along its first leg"
    s = _open()
    assert access.drawn_corridor(s, ((0.0, 60.0), (0.0, 400.0)), geom)[0][1] == pytest.approx(87.5)
    assert access.drawn_corridor(s, ((500.0, 60.0), (500.0, 400.0)), geom) == ((500.0, 60.0), (500.0, 400.0)), "away from its yard: as found"
    assert access.drawn_corridor(s, ((0.0, 60.0), (0.0, 400.0)), {**geom, "yard": None}) == ((0.0, 60.0), (0.0, 400.0))


def test_a_seat_whose_corridor_the_tree_cannot_take_lawfully_is_refused_at_seating() -> None:
    """Feature 287 wave 6 (ways W01): the seating asks the WHOLE tree, as lanes, of every corridor it would admit (the ways'
    own `tree.admits`, installed as `_corridor_tree`) - so a house whose every corridor would make the tree unlawful is
    refused there and the next seat tried, never found unreached when the web draws. Here the tree is a strip, and the
    house's only reachable point on it is the strip's inner end, which its corridor would meet folded back on the strip."""
    from l7r.diagram.hamletgen.ways.tree import seating_judge

    s = _open()
    s._seat_search = {"candidates": 0, "placer_calls": 0, "positions": 0, "rects": 0, "rounds": 0}
    start_tree(s, (700.0, 300.0), (0.0, -1.0), 200.0)
    geom = s._bundle_geom(700.0, 520.0, 46.0, 28.0, "SE", rot=0.0)
    admitted = access_corridor(s, geom)
    assert admitted is not None, "no tree judge installed: the strip is reached"
    s._corridor_tree = seating_judge(s)
    assert access.tree_admits(s, admitted, geom), "square onto the strip's inner end: the tree admits it"
    calls = []
    s._corridor_tree = lambda corridor, g: calls.append(corridor) or False
    s.__dict__.pop("_corridor_memo", None)
    assert access_corridor(s, geom) is None and calls, "every corridor the tree refuses: the seat has none"
    assert not s._parts_fit(geom), "and the seat is refused"
    n = len(calls)
    assert access.tree_admits(s, admitted, geom) is False and len(calls) == n, "asked once while nothing standing changes"
    s._corridor_tree = None
    assert access.tree_admits(s, admitted, geom), "no judge (a village roll): admitted"
