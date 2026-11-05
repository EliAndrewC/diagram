"""Feature 287, plan M3's seat half (homes H16, ways W01): the access-corridor tree reserved at seating."""

from __future__ import annotations

import pytest

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.rolling import access
from l7r.diagram.settlement.rolling.access import AccessTree, _seg_box_gap, doors_of, fixtures_clear, house_clear, house_gap, parts_clear, reserve, standing_clear
from tests.settlement._builders import seed_tree


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


def test_a_reserved_corridor_joins_the_tree_and_the_manifest_records_it() -> None:
    s = _open()
    tree = seed_tree(s, (100.0, 100.0), (0.0, 1.0), 50.0)
    assert s._access is tree and tree.segs == [((100.0, 100.0), (100.0, 150.0))] and s.M["access_corridors"] == []
    reserve(s, ((0.0, 0.0), (100.0, 100.0)))
    assert len(tree.segs) == 2 and s.M["access_corridors"] == [{"pts": [[0.0, 0.0], [100.0, 100.0]]}]
    reserve(s, ((1.0, 1.0), (2.0, 2.0)), of=(5.0, 5.0))
    assert s.M["access_corridors"][-1] == {"pts": [[1.0, 1.0], [2.0, 2.0]], "of": [5.0, 5.0]}


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


def corridor_clear(s, a, b, own):  # type: ignore[no-untyped-def]
    """The corridor test the shared search replaced (`access.corridor_clear` until feature 444 T30 deleted it with the Python
    seating): the strip clear of every homestead but its own, its fixtures, its parts and what stands - the plain search's oracle."""
    return house_clear(a, b, own, house_gap(s)) and fixtures_clear(s, a, b, own) and parts_clear(s, a, b, own) and standing_clear(s, a, b)


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


def test_a_corridor_keeps_off_its_own_well_pocket_and_its_own_fixtures() -> None:
    """`access.fixtures_clear` (feature 318, cohort Audit-24): the wellhead laid in the household's own homestead is drawn as a
    well, which the registry keeps every corridor off - so the corridor is held off its own pocket by the wellhead's box,
    as off its own privy; a household with no pocket is asked of its fixtures alone."""
    s = _open()
    seed_tree(s, (700.0, 700.0), (1.0, 0.0), 300.0)
    vr = float(s._well_vr())
    own = {"well": (300.0, 300.0), "boxes": {"fixtures": {"privy": (500.0, 300.0, 10.0, 8.0)}}}
    assert not access.fixtures_clear(s, (200.0, 300.0 + vr), (400.0, 300.0 + vr), own), "past the wellhead within the corridor's half"
    assert access.fixtures_clear(s, (200.0, 360.0), (400.0, 360.0), own), "well clear of it"
    assert not access.fixtures_clear(s, (450.0, 300.0), (550.0, 300.0), own), "through its own privy"
    assert access.fixtures_clear(s, (200.0, 300.0), (400.0, 300.0), {"boxes": {}}), "no pocket, no fixtures"


def test_a_point_is_clear_of_the_boxes_as_the_line_tests_judge_it() -> None:
    """Feature 427 T07: `point_clear(q, gaps)` is `not seg_box_within(q, q, box, t)` for every `(box, t)` - inside a box,
    beside it, off a corner, and at no gap at all."""
    import random

    from l7r.diagram.settlement.rolling.access import point_clear, seg_box_within

    rng = random.Random(5)
    for _ in range(3000):
        box = (rng.uniform(0, 50), rng.uniform(0, 50), rng.uniform(1, 20), rng.uniform(1, 20))
        t = rng.choice([0.0, rng.uniform(0.1, 10.0)])
        q = (rng.uniform(-20, 70), rng.uniform(-20, 70))
        assert point_clear(q, [(box, t)]) == (not seg_box_within(q, q, box, t)), (q, box, t)
    assert point_clear((0.0, 0.0), [])


def _old_seg_box_gap(a, b, box):  # the construction `_seg_box_gap` replaced (feature 417 T54), kept as its oracle
    from l7r.diagram.settlement import seg_dist, segments_cross

    cx, cy, w, h = box
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    if any(x0 <= p[0] <= x1 and y0 <= p[1] <= y1 for p in (a, b)):
        return 0.0
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    if any(segments_cross(a, b, corners[k], corners[(k + 1) % 4]) for k in range(4)):
        return 0.0
    return min(min(seg_dist(c[0], c[1], a, b) for c in corners), min(seg_dist(p[0], p[1], corners[k], corners[(k + 1) % 4]) for p in (a, b) for k in range(4)))


def test_the_written_out_segment_to_box_gap_is_the_old_constructions() -> None:
    """Feature 417 T54: the clip and the squared sums give the gap the four crossings and twelve distances gave, on random
    segments and boxes, a point-segment among them."""
    import random

    rng = random.Random(54)
    for _ in range(3000):
        box = (rng.uniform(-50, 50), rng.uniform(-50, 50), rng.uniform(1, 40), rng.uniform(1, 40))
        a = (rng.uniform(-100, 100), rng.uniform(-100, 100))
        b = a if rng.random() < 0.05 else (rng.uniform(-100, 100), rng.uniform(-100, 100))
        assert abs(_seg_box_gap(a, b, box) - _old_seg_box_gap(a, b, box)) < 1e-9, (a, b, box)
    assert _seg_box_gap((0.0, 30.0), (0.0, 40.0), (0.0, 0.0, 10.0, 10.0)) == 25.0, "a vertical segment past the box"


def test_a_walk_is_barred_and_a_margin_with_no_lawful_bearing_has_no_way_out(monkeypatch: pytest.MonkeyPatch) -> None:
    s = _open()
    tree = seed_tree(s, (100.0, 100.0), (0.0, 1.0), 50.0)
    tree.bar((0.0, 0.0), (10.0, 0.0))
    assert tree.bars.n == 1 and [b[:2] for b in tree.bars.near(5.0, 0.0)] == [((0.0, 0.0), (10.0, 0.0))], "a passage's walk kept clear"
    monkeypatch.setattr(access, "lawful_ground", lambda *a: False)
    assert access.exit_bearing(s, (100.0, 100.0), (0.0, 1.0), 300.0) is None, "no turn off the bearing stands on lawful ground"


def test_a_strip_the_site_raster_refuses_is_not_clear(monkeypatch: pytest.MonkeyPatch) -> None:
    s = _open()
    seed_tree(s, (100.0, 100.0), (0.0, 1.0), 50.0)
    monkeypatch.setattr(access, "site_edge_samples", lambda *a: None)
    assert not standing_clear(s, (0.0, 0.0), (40.0, 0.0))
