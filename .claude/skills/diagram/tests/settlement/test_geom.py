"""Split from test_settlement.py by feature 025 - see tests/settlement/CLAUDE.md for the index."""

import ast
import collections
import math
import pathlib
import random

import pytest

from l7r.diagram import settlement
from l7r.diagram.settlement import Settlement, seg_dist
from l7r.diagram.settlement._geom.primitives import convex_hull, edge_dist, point_in_poly
from l7r.diagram.settlement._geom.walls import _box_hits_run, torii_wall_conflicts, wall_runs
from tests.settlement._builders import _IDX_POLY, _cap020, _ladder_map, _max_turn_deg, _memo_city, _ward_city_with_samurai


def test_stroke_quads_makes_one_quad_per_segment():
    qs = settlement.stroke_quads([(0, 0), (100, 0), (100, 100)], 5.0)
    assert len(qs) == 2 and all(len(q) == 4 for q in qs)
    assert settlement.stroke_quads([(0, 0)], 5.0) == []
    assert settlement.stroke_quads([(7, 7), (7, 7)], 5.0)  # a degenerate segment still yields a quad rather than dividing by zero


def test_way_beds_carries_the_lane_network_lane_runs_does_not():
    # the AVOIDANCE list for a verge-hugging feature: lane_runs' roads/streets/alleys/ring road
    # PLUS the village lane network. Each siter used to build its own partial list, which is how a
    # punishment ground came to clip an alley (reported by another session, Tango 2026-07-27).
    M = {"road": [[0, 100], [500, 100]], "alleys": [{"pts": [[0, 300], [500, 300]], "w": 6}], "lane": [[0, 500], [500, 500]], "lanes": [{"pts": [[0, 700], [500, 700]], "w": 8}]}
    beds = settlement.way_beds(M)
    # THREE, not four: `M["lane"]` is NOT a way of its own. `Settlement.lane()` sets it on every
    # call, so it holds whichever lane was drawn LAST and is always already present in `M["lanes"]`
    # - counting it again double-listed one lane at a wrong half-width (4.0 rather than its own
    # w/2). It is honored ONLY when `lanes` is absent, which is the case for six hand-built
    # regression fixtures and for nothing the engine generates. See `street_runs`.
    assert len(beds) == 3 and len(settlement.lane_runs(M)) == 2
    assert sorted(round(b[0][0][1]) for b in beds) == [100, 300, 700]
    # ...and with no `lanes`, the legacy key still carries the lane, so a fixture cannot rot silently
    legacy = {"road": [[0, 100], [500, 100]], "lane": [[0, 500], [500, 500]]}
    assert sorted(round(b[0][0][1]) for b in settlement.way_beds(legacy)) == [100, 500]


def test_seg_closest_degenerate_segment():
    assert settlement.seg_closest(0, 0, (5, 5), (5, 5)) == (5, 5)


def test_indexed_overrides_every_mutating_list_method():
    """Every way a list's CONTENT can change must bump the version, or an index cached against it
    goes stale silently - the exact failure that cost this engine two silent bugs in one day
    (a stale `placed` index, a stale well-geometry fingerprint).

    The mutator set is discovered by INTROSPECTION rather than hand-listed, so a future Python
    adding a mutating list method fails this test instead of opening a hole nobody notices.
    """
    non_mutating = {"copy", "__reversed__", "__init__", "__new__", "__class_getitem__", "__getitem__"}
    candidates = (set(dir(list)) - set(dir(tuple))) - non_mutating
    ops = {
        "append": lambda r: r.append(_IDX_POLY),
        "extend": lambda r: r.extend([_IDX_POLY]),
        "insert": lambda r: r.insert(0, _IDX_POLY),
        "remove": lambda r: r.remove(_IDX_POLY),
        "pop": lambda r: r.pop(),
        "clear": lambda r: r.clear(),
        "sort": lambda r: r.sort(),
        "reverse": lambda r: r.reverse(),
        "__setitem__": lambda r: r.__setitem__(0, _IDX_POLY),
        "__delitem__": lambda r: r.__delitem__(0),
        "__iadd__": lambda r: r.__iadd__([_IDX_POLY]),
        "__imul__": lambda r: r.__imul__(2),
    }
    assert set(ops) == candidates, f"the mutator table is out of step with list's API: {set(ops) ^ candidates}"
    for name, op in ops.items():
        assert name in settlement.Indexed.__dict__, f"Indexed does not override {name}"
        reg = settlement.Indexed([_IDX_POLY])
        before, before_appends = reg.version, reg.appends
        op(reg)
        assert reg.version > before, f"{name} changed the list without bumping the version"
        # `indexed_grid` extends a cached index instead of rebuilding it when version and appends
        # moved together, i.e. when every change was an append. That inference is only sound if
        # `appends` counts APPENDS AND NOTHING ELSE - a non-appending mutator that bumped it would
        # let a stale index survive a removal, which is the 2026-08-03 `placed` bug exactly.
        grew = name in {"append", "extend", "__iadd__", "__imul__", "insert"}
        assert (reg.appends > before_appends) == (name in {"append", "extend"}), f"{name} must {'' if grew else 'not '}bump appends"


def test_point_grid_never_omits_an_item_a_linear_scan_would_find():
    """The one property every PointGrid caller's exactness rests on: `near` may return extra items
    (or an item twice), but it must never OMIT one whose box comes within `pad` of the query.

    Includes the OVERSIZED path - a wildly-spanning box, which is what a negative fixture's
    9,000,000px vertex looks like - because that clamp is the difference between a cheap query and
    the gigabytes-of-RAM incident recorded in this skill's CLAUDE.md.
    """
    rng = random.Random(11)
    items = [(f"i{k}", *(lambda a, b, w, h: (a, b, a + w, b + h))(rng.uniform(0, 900), rng.uniform(0, 900), rng.uniform(1, 300), rng.uniform(1, 300))) for k in range(120)]
    items.append(("huge", -9_000_000.0, -9_000_000.0, 9_000_000.0, 9_000_000.0))  # the clamp case
    grid = settlement.PointGrid()
    grid.extend(items)
    assert grid.n == len(items) and grid.oversized, "the wild box must be filed as oversized, not as billions of cells"
    for pad in (0.0, 5.0, 140.0):  # 140 > cell, so the query spans several cells
        for _ in range(400):
            px, py = rng.uniform(-100, 1000), rng.uniform(-100, 1000)
            want = {it[0] for it in items if it[1] - pad <= px <= it[3] + pad and it[2] - pad <= py <= it[4] + pad}
            got = {it[0] for it in grid.near(px, py, pad)}
            assert want <= got, f"grid OMITTED {want - got} at ({px:.1f}, {py:.1f}) pad={pad}"


def test_boxed_prefilters_agree_exactly_with_the_bare_scan():
    """The bbox PRUNES, the exact test DECIDES - so the prefiltered answer must equal the naive
    one at EVERY point, especially in the near-edge band the pad exists for.

    This is the ratchet behind "the pool regenerates byte-identical" (2026-08-03): the tempting
    way to speed a scatter up is to COARSEN it - a tighter pad, a bbox-only answer, fewer sample
    points - and the loss would show up not here but as silently-moved ground cover on some map
    nobody re-renders for a month. Coarsening fails this test instead.
    """
    polys = [
        [(100.0, 100.0), (200.0, 100.0), (200.0, 180.0), (100.0, 180.0)],
        [(220.0, 40.0), (300.0, 90.0), (250.0, 160.0)],  # a triangle: bbox and shape differ a lot
    ]
    corr = [([(0.0, 0.0), (400.0, 300.0)], 9.0), ([(50.0, 250.0), (350.0, 250.0)], 4.0)]
    boxed0, boxed10 = settlement.boxed_polys(polys), settlement.boxed_polys(polys, 10.0)
    segs = settlement.boxed_segs(corr)
    rng = random.Random(7)
    hits = 0
    for _ in range(4000):
        px, py = rng.uniform(-20, 420), rng.uniform(-20, 320)
        naive_in = any(settlement.point_in_poly(px, py, p) for p in polys)
        naive_pad = any(settlement.point_in_poly(px, py, p) or settlement.edge_dist(px, py, p) < 10.0 for p in polys)
        naive_seg = any(any(seg_dist(px, py, pl[i], pl[i + 1]) < hw for i in range(len(pl) - 1)) for pl, hw in corr)
        assert settlement.boxed_hit(px, py, boxed0) == naive_in, (px, py)
        assert settlement.boxed_hit(px, py, boxed10, 10.0) == naive_pad, (px, py)
        assert settlement.boxed_seg_hit(px, py, segs) == naive_seg, (px, py)
        hits += naive_in or naive_pad or naive_seg
    assert 200 < hits < 3800, f"the sample must straddle both answers to have teeth, got {hits}/4000"


def test_union_area_empty_and_overlapping_spans():
    # empty (or all-degenerate) rects -> zero area; and a rect fully shadowed by a taller one in the
    # same x-slab must be counted ONCE (the y1 <= cy skip), not double-counted.
    assert settlement._union_area([]) == 0.0
    assert settlement._union_area([(0, 0, 2, 2)]) == 4.0  # single rect
    assert settlement._union_area([(0, 0, 10, 10), (0, 2, 10, 5)]) == 100.0  # inner rect adds nothing


def test_main_tree_guard_blocks_main_allows_clones_and_gm_override(monkeypatch, tmp_path):
    # MAIN IS THE TREE THAT CONTAINS .clones/ (feature 131): no path is hardcoded, so the fixture is
    # a checkout with a .clones/ directory, whatever it is called and wherever it is mounted.
    monkeypatch.delenv("GM_ASSISTANT_ALLOW_MAIN", raising=False)
    main = tmp_path / "anything"
    (main / ".git").mkdir(parents=True)
    (main / ".clones" / "x" / ".claude").mkdir(parents=True)
    (main / ".claude").mkdir()
    # running from the MAIN integration tree aborts with the CLAUDE.md reminder
    with pytest.raises(SystemExit, match="Session clones"):
        settlement._assert_not_main_tree(str(main / ".claude" / "settlement.py"))
    # a session clone under .clones/ is the sanctioned workspace
    settlement._assert_not_main_tree(str(main / ".clones" / "x" / ".claude" / "settlement.py"))
    # a checkout with no .clones/ (a detached worktree, the GM's laptop clone) is not main
    other = tmp_path / "worktree"
    (other / ".git").mkdir(parents=True)
    settlement._assert_not_main_tree(str(other / "settlement.py"))
    # a path under no checkout at all is not main
    settlement._assert_not_main_tree(str(tmp_path / "loose.py"))
    # the GM's deliberate override opens main
    monkeypatch.setenv("GM_ASSISTANT_ALLOW_MAIN", "1")
    settlement._assert_not_main_tree(str(main / ".claude" / "settlement.py"))


def test_fillet_polyline_rounds_a_square_corner_into_a_sweep():
    # a right-angle elbow becomes a swept bend: no vertex still turns anywhere near 90 degrees, the
    # ends are untouched (a snapped pond/moat mouth must stay exactly where it was), and the corner
    # itself is gone from the line
    pts = [(0.0, 0.0), (200.0, 0.0), (200.0, 200.0)]
    out = settlement.fillet_polyline(pts, 25.0)
    assert out[0] == (0.0, 0.0) and out[-1] == (200.0, 200.0)
    assert (200.0, 0.0) not in out
    assert _max_turn_deg(out) < 20  # was 90
    assert len(out) == 9  # the two ends plus the arc's 7 samples


def test_fillet_polyline_caps_the_bend_on_short_segments():
    # the cut-back never exceeds 35% of either leg, so two corners cannot eat the segment between
    # them and a short stub keeps its shape (radius 500 asked for on 100px legs)
    out = settlement.fillet_polyline([(0.0, 0.0), (100.0, 0.0), (100.0, 100.0)], 500.0)
    assert min(x for x, _ in out[1:-1]) >= 64.9  # 100 - 35% of the leg
    assert max(y for _, y in out[:-1]) <= 35.1


def test_fillet_polyline_leaves_gentle_bends_and_degenerate_input_alone():
    gentle = [(0.0, 0.0), (100.0, 2.0), (200.0, 4.0)]  # ~0 degrees of turn: nothing to round
    assert settlement.fillet_polyline(gentle, 25.0) == gentle
    assert settlement.fillet_polyline([(0.0, 0.0), (10.0, 0.0)], 25.0) == [(0.0, 0.0), (10.0, 0.0)]  # too few points
    assert settlement.fillet_polyline([(0.0, 0.0), (10.0, 0.0), (20.0, 0.0)], 0.0) == [(0.0, 0.0), (10.0, 0.0), (20.0, 0.0)]  # no radius
    dup = [(0.0, 0.0), (100.0, 0.0), (100.0, 0.0), (100.0, 100.0)]  # a repeated vertex bends nothing
    assert settlement.fillet_polyline(dup, 25.0)[0] == (0.0, 0.0)


def test_region_blocked_catches_a_keepout_against_a_cell_EDGE():
    """The bug this exists to stop: a keep-out sitting against the middle of a cell EDGE touches
    neither the center nor any corner, so center-plus-corner sampling passes it. That is how a
    wellhead ended up 1 px inside a hatake plot with every sample point clear."""
    cell = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    assert not settlement.region_blocked(cell, [], [], [], [])
    # a small circle hugging the middle of the LEFT edge - no corner is near it, the center is 50 away
    assert settlement.region_blocked(cell, [], [(-4.0, 50.0, 6.0)], [], [])
    assert not settlement.region_blocked(cell, [], [(-40.0, 50.0, 6.0)], [], [])
    assert settlement.region_blocked(cell, [(-4.0, 50.0, 6.0)], [], [], [])  # same, as a pond
    # a ditch threading across the cell's middle, touching no corner
    assert settlement.region_blocked(cell, [], [], [([(-20.0, 50.0), (120.0, 50.0)], 1.0)], [])
    assert not settlement.region_blocked(cell, [], [], [([(-20.0, 300.0), (120.0, 300.0)], 1.0)], [])
    # a polygon overlapping a corner
    assert settlement.region_blocked(cell, [], [], [], [[(90.0, 90.0), (150.0, 90.0), (150.0, 150.0), (90.0, 150.0)]])
    assert not settlement.region_blocked(cell, [], [], [], [[(300.0, 300.0), (350.0, 300.0), (350.0, 350.0), (300.0, 350.0)]])


def test_quad_hits_seg_covers_all_three_ways_a_line_can_meet_a_cell():
    """A stroked line meets a cell in three distinct ways, and each needs its own test: an ENDPOINT
    lying in (or near) the cell, the line CROSSING an edge, and the line merely GRAZING a corner
    without crossing anything. The third is the one that point sampling misses."""
    cell = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    assert settlement.quad_hits_seg(cell, (50.0, 50.0), (300.0, 50.0), 1.0)  # endpoint INSIDE
    assert settlement.quad_hits_seg(cell, (-50.0, 50.0), (150.0, 50.0), 1.0)  # CROSSES both edges
    assert settlement.quad_hits_seg(cell, (-50.0, -5.0), (150.0, -5.0), 8.0)  # GRAZES the top corners
    assert not settlement.quad_hits_seg(cell, (-50.0, -5.0), (150.0, -5.0), 2.0)  # ...same line, too thin to reach
    assert not settlement.quad_hits_seg(cell, (-50.0, 500.0), (150.0, 500.0), 8.0)  # nowhere near


def test_point_quad_dist_is_zero_inside_and_grows_outside():
    cell = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
    assert settlement.point_quad_dist(5, 5, cell) == 0.0
    assert 2.9 < settlement.point_quad_dist(-3, 5, cell) < 3.1


def test_ward_interior_returns_none_on_a_zero_perimeter_wall():
    # a "ring" of coincident points has zero perimeter - nothing to walk an arc along
    assert settlement.ward_interior([(400, 945), (400, 400)], [(7, 7), (7, 7), (7, 7)]) is None


# ---- angled-building captions (GM 2026-08-02): a label tilts with the feature it names ----------
def test_label_tilt_is_the_subjects_own_angle():
    """GM 2026-08-27 (feature 133 T38), the general rule: a caption lies at exactly the angle of the
    thing it names, normalized to [-90, 90) so it never reads upside down. The 2026-08-02 mod-90 fold
    is superseded - a 102-degree yard's caption ran at 12 degrees, aligned with an edge, not the thing."""
    assert [settlement.label_tilt(r) for r in (0, 90, 180, 270, -90, 360)] == [0.0] * 6  # a square rotation has a horizontal edge: level IS aligned
    assert settlement.label_tilt(-16) == -16.0
    assert settlement.label_tilt(150) == -30.0  # the same line of text, read the right way up
    assert settlement.label_tilt(102) == -78.0  # was 12.0 under the fold
    assert settlement.label_tilt(67.1) == 67.1
    assert settlement.label_tilt(-104) == 76.0
    assert settlement.label_tilt(180.02) == 0.0  # float noise snaps level
    assert settlement.label_tilt(-122.8) == 57.2  # Inashiro's notice board


def test_linear_tilt_is_the_same_rule_as_label_tilt():
    """The 45-degree clamp (GM 2026-08-08: a north-south road keeps a level caption) is superseded by
    the general alignment rule (GM 2026-08-27, T38); a line and a box caption follow one function."""
    assert settlement.linear_tilt(0) == 0.0
    assert settlement.linear_tilt(-26.6) == -26.6  # Hoshizora's Imperial Road
    assert settlement.linear_tilt(153.4) == -26.6  # ...the same line stored the other way round
    assert settlement.linear_tilt(72) == 72.0  # Nagahara's approach now tilts with the road
    assert settlement.linear_tilt(45.1) == 45.1
    assert settlement.linear_tilt(180.02) == 0.0  # float noise snaps level
    assert settlement.linear_tilt(72) == settlement.label_tilt(72) == settlement.aligned_tilt(72)


def test_label_ladder_seats_a_tilted_caption_by_its_THICKNESS_not_its_rotated_aabb():
    # The defect this pins (GM 2026-08-08): probing the rotated AABB made a diagonal caption reach
    # by most of its own LENGTH in the one direction it does not extend, so "Imperial Road" seated
    # 64px off a clear roadbed. The support is exact in every direction, so a tilted caption tucks
    # in at the same LABEL_MIN_AIR a level one gets.
    s = _ladder_map()
    box = (400.0, 480.0, 600.0, 520.0)
    seat = s._best_label_spot(box, "Imperial Road", 12, tilt=-26.6)
    quad = settlement.label_quad([*s._label_box(*seat, "Imperial Road", 12), 0, "Imperial Road", None, -26.6])
    corners = [(box[0], box[1]), (box[2], box[1]), (box[2], box[3]), (box[0], box[3])]
    assert settlement.poly_gap(quad, corners) < settlement.LABEL_MIN_AIR + 1


def test_label_quad_and_aabb_rotate_the_record_about_its_center():
    lvl = [0.0, 0.0, 100.0, 10.0, 1, "x"]
    assert settlement.label_quad(lvl) == [(0.0, 0.0), (100.0, 0.0), (100.0, 10.0), (0.0, 10.0)]
    assert settlement.label_aabb([*lvl, None]) == (0.0, 0.0, 100.0, 10.0)  # a ref-carrying level record reads the same
    tl = [*lvl, None, 30.0]
    q = settlement.label_quad(tl)
    c30, s30 = math.cos(math.radians(30)), math.sin(math.radians(30))
    assert q[0] == pytest.approx((50 - 50 * c30 + 5 * s30, 5 - 50 * s30 - 5 * c30))
    a = settlement.label_aabb(tl)
    assert a[3] - a[1] > 10 and a[2] - a[0] < 100  # taller and narrower, as a tilted run must be


def test_tilt_caption_seat_picks_the_perpendicular_half_extent_by_fold_family():
    a = math.radians(-30.0)
    # rot=150 folds to -30 with the footprint's LOCAL h perpendicular to the baseline
    assert settlement.tilt_caption_seat(0, 0, 150, -30.0, 50, 10, 11) == pytest.approx((-math.sin(a) * 21, math.cos(a) * 21))
    # rot=102 folds to 12: the other family - the local w lies perpendicular
    b = math.radians(12.0)
    assert settlement.tilt_caption_seat(0, 0, 102, 12.0, 50, 10, 11) == pytest.approx((-math.sin(b) * 61, math.cos(b) * 61))
    # above=True mirrors the seat to the upper edge
    assert settlement.tilt_caption_seat(0, 0, 150, -30.0, 50, 10, 11, above=True) == pytest.approx((math.sin(a) * 21, -math.cos(a) * 21))


def test_servant_ranges_keeps_every_range_inside_the_fence():
    # a house hard against the ward fence must not be ranged out through it
    s = _ward_city_with_samurai((412, 600, "samurai", 0.0))
    s.servant_ranges()
    for r in [b for b in s.M["buildings"] if b["kind"] == "servant"]:
        assert settlement.point_in_poly(r["x"], r["y"], s._samurai_ward_interiors[0])
        assert min(settlement.seg_dist(r["x"], r["y"], (400, 795), (400, 400)), settlement.seg_dist(r["x"], r["y"], (400, 400), (795, 400))) > s._WARD_STROKE


def test_poly_gap_measures_true_clearance_and_zero_on_overlap():
    # the exact vertex-to-edge minimum, and 0.0 the moment two quads intersect - the measurement
    # servant_ranges uses to refuse a seat that touches a non-host more closely than its own host
    a = settlement.rot_rect(0, 0, 10, 10, 0)
    assert settlement.poly_gap(a, settlement.rot_rect(20, 0, 10, 10, 0)) == pytest.approx(10.0)
    assert settlement.poly_gap(a, settlement.rot_rect(10, 0, 10, 10, 0)) == pytest.approx(0.0)  # touching
    assert settlement.poly_gap(a, settlement.rot_rect(5, 0, 10, 10, 0)) == 0.0  # overlapping


def test_seat_memo_forgets_when_a_registry_is_rebound_or_truncated():
    # `placed` is rebound to a filtered copy in two places in this engine, and that is precisely
    # what defeated the previous attempt at an incremental index over it
    s, memo = _memo_city()
    memo.level("laborer", 10, 6, 7).add((100.0, 200.0))
    s.placed = settlement.Indexed()
    memo.sync()
    assert (100.0, 200.0) not in memo.level("laborer", 10, 6, 7)

    s2, memo2 = _memo_city()
    s2.M["buildings"].append({"x": 1, "y": 2, "w": 3, "h": 4, "kind": "laborer"})
    memo2.sync()
    memo2.level("laborer", 10, 6, 7).add((100.0, 200.0))
    s2.M["buildings"].clear()  # a plain list has only identity + length as a witness; length is enough here
    memo2.sync()
    assert (100.0, 200.0) not in memo2.level("laborer", 10, 6, 7)


def test_full_tilt_lays_a_row_caption_along_the_row():
    """GM 2026-08-09: linear subjects may carry the FULL tilt (linear_tilt_full), past the
    45-degree go-level clamp the road captions keep - a -54 deg granary row's caption lies
    along the row, and a bearing and its reverse caption identically."""
    assert settlement.linear_tilt_full(-54) == -54.0
    assert settlement.linear_tilt_full(126) == -54.0
    assert settlement.linear_tilt_full(0) == 0.0
    s = _cap020()
    s.granary(700, 700, n=3, w=20, h=12, gap=8, label="domain granaries", append=True, rot=-54)
    assert "rotate(-54" in "".join(s.out)  # the caption carries the row's own angle


def test_a_rolled_cluster_band_is_sized_in_REAL_FEET_at_the_map_s_grain():
    """THE RATCHET for the other half of that fix (see `roll_village`).

    A cluster band is sized per homestead BUNDLE - house plus its yard and dooryard garden, ~92 ft
    of pitch once the placer's collision circles are paid for - and that is a REAL-FEET quantity, so
    the band must shrink with the map's grain. It used to convert through `bscale`, which every tier
    pins to 1/ftpx except villages, which pin it to 1.0 for legacy reasons; a village band was
    therefore asked for twice the ground its (half-size) bundles occupy and strung its cluster thin
    over a hollow hull. The failure mode of the ORIGINAL 56 ft figure is nastier and is why this is
    pinned: too small does not show up as a shortfall, because the caller keeps seeding until the
    quota is met - it shows up as a cluster too solid to seat a wellhead in."""
    hamlet, village = Settlement(900, 900, seed=1), Settlement(900, 900, seed=1)
    hamlet.meta(scale="hamlet", ftpx=1)
    village.meta(scale="village", ftpx=2)
    assert hamlet.px(settlement.BUNDLE_PITCH_FT) == pytest.approx(settlement.BUNDLE_PITCH_FT)
    assert village.px(settlement.BUNDLE_PITCH_FT) == pytest.approx(settlement.BUNDLE_PITCH_FT / 2)


# ---- THE PACKAGE SURFACE (feature 117) --------------------------------------------------------
# _geom was one 1,303-line module until feature 117 cut it into eleven submodules behind a
# star-import re-export (specs/117-geom-package/contracts/surface.md). Two properties hold that
# design up and NEITHER is visible to ruff, to mypy --strict, or to any other test in this suite:
#
#   - the whole pre-split surface still resolving (a dropped member gives a package that imports
#     cleanly and fails only when whichever caller needs it happens to run - and 12 of these names
#     have no test of their own, several reachable only from the frozen city wing);
#   - no public name bound in two submodules. This one is new to 117: the mixin splits (025,
#     112-116) composed an MRO, which at least keeps a duplicate reachable, while
#     `from .a import *` followed by `from .b import *` silently keeps b's binding and leaves a's
#     implementation dead. Python, ruff and mypy all report nothing.
#
# Principle X clause 14's bargain, exactly: the roster is DERIVED (the stars), so the roster's
# safety property moves into a guard proven to fire. Both halves were demonstrated red before they
# were trusted - see specs/117-geom-package/tasks.md T014/T015 for the observed failure text.

# The 89 module-level names of settlement/_geom.py as it stood at the split, by AST census. A
# FROZEN literal, deliberately: its whole job is to remember a state that no longer exists.
_PRE_SPLIT_GEOM_SURFACE = (
    'BUNDLE_PITCH_FT', 'CARRIED_LANDING_FLOOR_FT', 'FLOODED_SHADES', 'GOVERNOR_CAPTION_FS', 'HALL_CAPTION_FS', 'Indexed', 'LABEL_AIR_CAP', 'LABEL_AIR_RINGS', 'LABEL_AIR_STEP', 'LABEL_MIN_AIR',
    'LAND', 'LANDING_FT', 'LANE_CROSSES_MIN_DEG', 'LANE_THROUGH_TOL', 'Manifest', 'PADDY_SHADES', 'PLANK_ABUTMENT', 'PLANK_BANK_REACH', 'PLANK_VILLAGE_REACH', 'PointGrid', 'Poly', 'Pt',
    'RICE_GREENS', 'RIPE_SHADES', 'SeatMemo', 'TORII_PITCH_FT', 'TORII_PITCH_MAX_SPANS', 'WARD_BARRED_KINDS', 'YARD_GLYPH_SLACK', '_VILLAGE_POP_DIST', '_aabb_gap', '_assert_not_main_tree',
    '_box_hits_run', '_rect_ring', '_signed_area', '_union_area', 'box_gap', 'boxed_grid', 'boxed_hit', 'boxed_polys', 'boxed_seg_hit', 'boxed_segs', 'edge_dist', 'fillet_polyline',
    'forest_frame_span', 'forest_reveal_x', 'indexed_grid', 'kido_bar_deg', 'label_aabb', 'label_quad', 'label_tilt', 'lane_runs', 'lane_through_gate', 'linear_tilt', 'linear_tilt_full',
    'organic_bbox', 'organic_poly', 'paddy_wet_rings', 'point_in_poly', 'point_quad_dist', 'poly_gap', 'quad_hits_poly', 'quad_hits_seg', 'rail_quad', 'rects_overlap', 'region_blocked',
    'ring_touches', 'rot_rect', 'sat_overlap', 'seg_closest', 'seg_dist', 'seg_in_ellipse_core', 'seg_intersect', 'segments_cross', 'smooth_closed', 'smooth_points', 'stroke_quads',
    'tilt_caption_seat', 'torii_halfbox', 'torii_seat_on_wall', 'torii_wall_conflicts', 'tower_quad', 'trough_quad', 'village_population', 'wall_runs', 'ward_interior', 'way_beds',
    'wellhead_quad', 'winding'
)  # fmt: skip


def _geom_submodule_members() -> dict[str, list[str]]:
    """Every top-level name each `settlement/_geom/` submodule DEFINES, by AST.

    By AST rather than by `vars(module)`, for two reasons a runtime census gets wrong: a submodule's
    namespace also holds the names it IMPORTS (overlap.py imports `point_in_poly`), and filtering
    those out by `__module__` would drop every module-level CONSTANT - which is most of `labels.py`
    and `ways.py`, and exactly the population a duplicate could hide in."""
    out: dict[str, list[str]] = {}
    for path in sorted(pathlib.Path(settlement._geom.__path__[0]).glob("*.py")):
        if path.name == "__init__.py":
            continue
        names: list[str] = []
        for node in ast.parse(path.read_text()).body:
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
                names.append(node.name)
            elif isinstance(node, ast.Assign):
                names += [t.id for t in node.targets if isinstance(t, ast.Name)]
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                names.append(node.target.id)
        out[path.stem] = names
    return out


def test_the_geom_package_surface_still_carries_every_pre_split_name():
    """A SUBSET assertion, so a helper added later needs no bookkeeping here - only a name that
    LEAVES is a defect. Underscore names are in the census on purpose: `import *` does not carry
    them, so they exist on the surface only through the aliased block in `__init__.py`, and that
    block is the thing most likely to be forgotten when a member moves between submodules."""
    missing = [n for n in _PRE_SPLIT_GEOM_SURFACE if not hasattr(settlement._geom, n)]
    assert missing == [], f"the _geom package no longer exposes: {missing}"


def test_no_public_geom_name_is_bound_in_two_submodules():
    """The star-import shadowing guard - see the bank above for why nothing else catches this.

    Private names are checked too: a duplicated `_helper` is shadowed just as silently, and the
    aliased block in `__init__.py` would then re-export whichever one the import order happened to
    keep."""
    owners = collections.defaultdict(list)
    for mod, names in _geom_submodule_members().items():
        for name in names:
            owners[name].append(mod)
    clashes = {name: mods for name, mods in owners.items() if len(mods) > 1}
    assert clashes == {}, f"a name is defined in more than one _geom submodule (the later star import silently wins): {clashes}"


def test_the_import_time_main_tree_guard_survived_the_split():
    """The guard's CALL is the one unnamed top-level statement in the pre-split file, so it is the
    one member a name-keyed partition can drop - and its failure mode is silence, because every test
    already runs inside a session clone. Read for the call rather than trusting the move; the
    `_assert_not_main_tree` tests above exercise the FUNCTION and would pass with the call gone."""
    base = pathlib.Path(settlement._geom.__path__[0]) / "base.py"
    assert "\n_assert_not_main_tree()\n" in base.read_text()
    assert settlement._assert_not_main_tree is settlement._geom.base._assert_not_main_tree


def test_ring_index_matches_the_linear_scan_exactly() -> None:
    """RingIndex (feature 145) is a prefilter: inside/outside and the feather-band distance must
    equal point_in_poly / edge_dist on every point - concave rings, points on the bbox edge, points
    outside, points far from every edge (None) and points inside the band (the true distance)."""
    import random as _r

    from l7r.diagram.settlement._geom import RingIndex, edge_dist, point_in_poly

    rng = _r.Random(144)
    rings = [
        [(0, 0), (300, 0), (300, 200), (150, 80), (0, 200)],  # a concave notch
        [(50, 50), (400, 60), (420, 300), (200, 350), (180, 180), (40, 320)],  # irregular, six edges
        [(0, 0), (1000, 0), (1000, 1000), (0, 1000)],  # spans many cells
    ]
    for ring in rings:
        idx = RingIndex(ring, cell=64.0)
        for _ in range(3000):
            px, py = rng.uniform(-100, 1100), rng.uniform(-100, 1100)
            assert idx.inside(px, py) == point_in_poly(px, py, ring), (ring, px, py)
            for limit in (10.0, 42.0, 200.0):
                exact = edge_dist(px, py, ring)
                got = idx.edge_within(px, py, limit)
                if exact < limit:
                    assert got is not None and abs(got - exact) < 1e-9, (ring, px, py, limit)
                else:
                    assert got is None, (ring, px, py, limit)


def test_boxed_rings_match_boxed_polys() -> None:
    """`boxed_ring_hit` over `boxed_rings` (feature 145) gives `boxed_hit`'s verdict on every point,
    with and without an edge pad - the box pad is the edge pad, as the contract requires."""
    import random as _r

    from l7r.diagram.settlement._geom import boxed_hit, boxed_polys, boxed_ring_hit, boxed_rings

    rng = _r.Random(1440)
    polys = [[(0, 0), (120, 0), (120, 90), (60, 40), (0, 90)], [(300, 300), (500, 320), (480, 520), (320, 480)]]
    for pad in (0.0, 12.0):
        a, b = boxed_polys(polys, pad), boxed_rings(polys, pad)
        for _ in range(4000):
            px, py = rng.uniform(-50, 600), rng.uniform(-50, 600)
            assert boxed_ring_hit(px, py, b, pad) == boxed_hit(px, py, a, pad), (px, py, pad)


# ---- feature 145: the branches the hamlet-path floor found no test reaching ---------------------------------


def test_keepout_ring_and_facing_chains_degenerate_and_all_facing() -> None:
    from l7r.diagram.settlement._geom.primitives import chain_distance, chain_violated, facing_chains, keepout_ring

    line = [(0.0, 0.0), (100.0, 0.0)]  # two points simplify to fewer than three chords
    assert keepout_ring(line, line, 3.0) == (line, line)
    assert facing_chains(line, (50.0, 50.0), 3.0) == []
    square = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    assert facing_chains(square, (50.0, 50.0), 1.0) == []  # a seat INSIDE the ring faces no outward normal
    # a seat far outside faces two edges; every chord faces it only when the ring is a sliver seen end-on
    sliver = [(0.0, 0.0), (100.0, 0.0), (100.0, 1.0), (0.0, 1.0)]
    chains = facing_chains(sliver, (50.0, -500.0), 0.1)
    assert chains and all(len(ch) >= 1 for ch in chains)
    # a zero-length chord is skipped by both walkers
    zero = [[((0.0, 0.0), (0.0, 0.0), (0.0, -1.0)), ((0.0, 0.0), (10.0, 0.0), (0.0, -1.0))]]
    assert chain_violated(5.0, 3.0, zero, 2.0) is True  # on the field side of the live chord
    assert chain_distance(5.0, -4.0, zero) == 4.0


def test_aabb_gap_forest_reveal_organic_bbox_flat_edge() -> None:
    from l7r.diagram.settlement._geom.curves import organic_bbox
    from l7r.diagram.settlement._geom.extents import forest_reveal_x
    from l7r.diagram.settlement._geom.overlap import _aabb_gap

    assert _aabb_gap([(0, 0), (10, 0), (10, 10), (0, 10)], [(13, 14), (20, 14), (20, 20), (13, 20)]) == 5.0
    assert forest_reveal_x([(0, 0), (500, 0)], w=400, edge=[(-5, 0), (380, 0)], reveal=30) == [0, 380, 30, 400]
    pts = organic_bbox((0.0, 0.0, 100.0, 50.0), 6.0, flat_edges=(0,))
    assert [p for p in pts[:4]] == [(0.0, 0.0), (25.0, 0.0), (50.0, 0.0), (75.0, 0.0)]  # the flat top edge is exact


def test_water_index_wide_fixture_wall_runs_skip_and_lane_alongside_a_fence() -> None:
    from l7r.diagram.settlement._geom.walls import wall_runs
    from l7r.diagram.settlement._geom.water_index import SLACK, WaterIndex
    from l7r.diagram.settlement._geom.ways import lane_through_gate

    M = {"streams": [{"pts": [[0, 100], [400, 100]], "w": 8}]}
    idx = WaterIndex(M)
    assert idx.clear(200.0, 300.0, SLACK + 10.0) is True and idx.clear(200.0, 110.0, SLACK + 10.0) is False
    runs = wall_runs({"manors": [{"name": "a fixture compound with no footprint"}]})
    assert runs == []
    alongside = {"lanes": [{"pts": [[0, 0], [100, 0]], "w": 6}]}
    assert lane_through_gate(alongside, 50.0, 2.0, fence_deg=0.0) is None  # parallel to the fence, not through it


def test_lane_runs_includes_the_ring_road_and_the_alleys() -> None:
    """Feature 146: `lane_runs` gathers every trodden run a gate rule measures against, the city's included."""
    from l7r.diagram.settlement._geom.ways import lane_runs

    M = {"lanes": [{"pts": [[0, 0], [10, 0]], "w": 5}], "alleys": [{"pts": [[0, 20], [10, 20]], "w": 6}], "ring_road": [[0, 40], [10, 40]], "ring_road_width": 20}
    halves = sorted(round(h, 1) for _pts, h in lane_runs(M))
    assert 3.0 in halves and 10.0 in halves, halves  # the alley at w 6 and the ring road at w 20


def test_lane_through_gate_skips_a_far_lane_and_one_running_alongside_the_fence() -> None:
    """Feature 146: two of the gate probe's skips - a lane too far to be the crossing, and one running ALONG
    the fence, which the gate deliberately does not bar (only a lane THROUGH the gate counts)."""
    from l7r.diagram.settlement._geom.ways import lane_through_gate

    # `lane_runs` gathers the TRAVELED ways - roads, town streets, alleys, the ring road - so the probe is
    # fed a street here; a hamlet's `lanes` are not among them, which is itself worth pinning.
    far = {"town_streets": [{"pts": [[0, 400], [200, 400]], "w": 6}]}
    assert lane_through_gate(far, 100.0, 0.0, fence_deg=0.0) is None, "400 px away is not this gate's way"
    alongside = {"town_streets": [{"pts": [[0, 2], [200, 2]], "w": 6}]}
    assert lane_through_gate(alongside, 100.0, 0.0, fence_deg=0.0) is None, "parallel to the fence"
    across = {"town_streets": [{"pts": [[100, -60], [100, 60]], "w": 6}]}
    assert lane_through_gate(across, 100.0, 0.0, fence_deg=0.0) is not None, "square through the gate"
    assert lane_through_gate({"lanes": [{"pts": [[100, -60], [100, 60]], "w": 6}]}, 100.0, 0.0, fence_deg=0.0) is None


def test_facing_chains_returns_one_run_when_every_chord_faces_the_seat() -> None:
    """Feature 146: the two run-splitting arms. A seat far off one side of a long sliver faces EVERY chord,
    which is the single-run case; a seat beside a wide ring faces only some, which splits into runs."""
    from l7r.diagram.settlement._geom import facing_chains

    sliver = [(0.0, 0.0), (400.0, 0.0), (400.0, 2.0), (0.0, 2.0)]
    one = facing_chains(sliver, (200.0, -4000.0), 0.5)
    assert len(one) == 1, one

    square = [(0.0, 0.0), (400.0, 0.0), (400.0, 400.0), (0.0, 400.0)]
    some = facing_chains(square, (200.0, -600.0), 1.0)
    assert some and len(some) >= 1
    assert sum(len(c) for c in some) < 4, "not every chord of a square faces a seat off one side"


def test_street_runs_honors_a_manifest_that_carries_only_the_singular_lane() -> None:
    """The fallback the docstring exists for. Six frozen regression fixtures are hand-built manifests
    carrying `lane` and no `lanes`, so a fixture that stops firing because the code stopped reading
    its key is a fixture that has silently rotted. `lanes` wins where it exists; `lane` is honored
    where it is all there is; nothing at all is an empty list, not a crash."""
    from l7r.diagram.settlement import street_runs

    both = {"lanes": [{"pts": [(0, 0), (10, 0)]}], "lane": [(50, 50), (60, 60)]}
    assert street_runs(both) == [[(0.0, 0.0), (10.0, 0.0)]], "the plural wins where it exists"
    assert street_runs({"lane": [(50, 50), (60, 60)]}) == [[(50.0, 50.0), (60.0, 60.0)]]
    assert street_runs({}) == []
    assert street_runs({"lanes": [{"pts": []}]}) == [], "a lane record with no points is not a run"


# ---- feature 174: convex_hull, the last unreached function in this module -------------------------
# It is re-exported by `overlap/taxonomy.py` and, since feature 166 deleted the check battery that
# used it, called by nothing a roll executes - so all 16 of its statements sat uncovered in the
# 2026-08-31 baseline. A pure function of a point list is the cheapest thing in this repository to
# test (GM 2026-08-28: "unit tests be much simpler if you're just calling functions that take simple
# inputs and outputs"), so it gets tests rather than a roll or an exemption.


def test_convex_hull_returns_the_extreme_points_and_drops_the_interior_ones() -> None:
    pts = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0), (5.0, 5.0), (2.0, 3.0)]
    hull = convex_hull(pts)
    assert set(hull) == {(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)}, "the two interior points are not on the hull"
    assert len(hull) == 4, "a corner is not repeated and the ring is not closed"


def test_convex_hull_encloses_every_input_point() -> None:
    """The property that matters to its consumer, asserted rather than the vertex order."""
    pts = [(1.0, 2.0), (4.0, 0.0), (9.0, 3.0), (7.0, 8.0), (2.0, 7.0), (5.0, 4.0), (3.0, 3.0)]
    hull = convex_hull(pts)
    for p in pts:
        assert point_in_poly(p[0], p[1], hull) or edge_dist(p[0], p[1], hull) < 1e-6, f"{p} fell outside its own hull"


def test_convex_hull_of_fewer_than_three_unique_points_returns_them_as_is() -> None:
    """The documented degenerate case - a hull of zero area, returned rather than refused."""
    assert convex_hull([(1.0, 1.0)]) == [(1.0, 1.0)]
    assert convex_hull([(2.0, 2.0), (1.0, 1.0)]) == [(1.0, 1.0), (2.0, 2.0)], "sorted, and both kept"
    assert convex_hull([(1.0, 1.0), (1.0, 1.0), (1.0, 1.0)]) == [(1.0, 1.0)], "duplicates are one point"
    assert convex_hull([]) == []


def test_convex_hull_rounds_to_the_millimetre_before_deduplicating() -> None:
    """`round(x, 3)` is what makes two points from different float paths the same point."""
    assert convex_hull([(1.0, 1.0), (1.0000001, 1.0000001)]) == [(1.0, 1.0)]


def test_convex_hull_of_collinear_points_keeps_only_the_ends() -> None:
    """The `cross(...) <= 0` pop is what drops a point that adds no area - both loops exercise it."""
    hull = convex_hull([(0.0, 0.0), (1.0, 1.0), (2.0, 2.0), (3.0, 3.0)])
    assert set(hull) == {(0.0, 0.0), (3.0, 3.0)}, "the two interior collinear points carry no area"


# ---- feature 174: the five unreached statements in _geom/walls.py --------------------------------


def test_wall_runs_walls_the_governors_mansion() -> None:
    """A city-tier compound: the key is read like a manor's, and no hamlet records one."""
    runs = wall_runs({"governor_mansion": {"x": 100.0, "y": 100.0, "w": 60.0, "h": 40.0}})
    labels = [lbl for lbl, _, _ in runs]
    assert "the governor's mansion wall" in labels
    assert not wall_runs({"governor_mansion": {"x": 1.0, "y": 1.0}}), "a compound with no footprint carries no wall"


def test_box_hits_run_catches_a_run_that_ENDS_inside_the_box_crossing_no_edge() -> None:
    """The docstring's own case: "a run that merely ends inside the box (crossing no edge) counts".

    Its sibling - a run that crosses an edge - is exercised by every walled map; this vertex-inside
    branch is not, and a test asserting only the crossing would pass with this branch deleted.
    """
    box = (0.0, 0.0, 10.0, 10.0)
    assert _box_hits_run(box, [(5.0, 5.0), (50.0, 50.0)], 0.5), "the first vertex sits inside the box"
    assert not _box_hits_run(box, [(50.0, 50.0), (60.0, 60.0)], 0.5), "a run wholly outside is not a hit"


def test_torii_wall_conflicts_names_the_wall_an_arch_is_standing_in() -> None:
    """The whole-manifest form. Its empty answer is exercised by every clean map; the branch that
    REPORTS one is not, so the conflict is built on purpose - a manor wall with an arch on it."""
    M = {"meta": {"ftpx": 1}, "manors": [{"x": 100.0, "y": 100.0, "w": 60.0, "h": 40.0}], "torii": [(70.0, 100.0)]}
    bad = torii_wall_conflicts(M)
    assert bad and bad[0][0] == 70.0 and bad[0][1] == 100.0, "the arch's own coordinates, rounded"
    assert "manor" in bad[0][2], "and the label of the wall it stands in"
    assert torii_wall_conflicts({"meta": {"ftpx": 1}, "manors": M["manors"], "torii": [(400.0, 400.0)]}) == [], "an arch clear of every wall is not a conflict"
