"""Split from test_ways.py by feature 173 - see this directory's CLAUDE.md."""

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen.ways import _crosses_fabric, _nearest_seg, _reach, _route, _trim_to_service

from ._builders import _FOLD_BAR, _HAIRPIN, _LONG_HAIRPIN, _TIP_WAY, _StubWeb, _walled_settlement, _webbed


def test_a_point_in_the_crop_is_pushed_out_on_the_LOCAL_edge_normal() -> None:
    """The defect the GM reported: a way's tip stopped 28 px INSIDE the paddy because it was pulled
    back along one fixed map-wide direction. The way out is the nearest OUTLINE EDGE's normal - and
    the nearest edge, not the nearest vertex, since a point deep in a lobe can have its nearest
    vertex round the far side."""
    square = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    out = hg.push_out_of(square, (90.0, 50.0), 10.0)  # nearest edge is the right one, x=100
    assert out == pytest.approx((110.0, 50.0))
    assert hg.push_out_of(square, (50.0, 5.0), 10.0) == pytest.approx((50.0, -10.0)), "the bottom edge is nearer here"
    far = hg.push_out_of(square, (300.0, 50.0), 10.0)
    assert far == (300.0, 50.0), "a point already clear is returned untouched - this must never drag a way back in"


def test_reach_measures_the_nearest_point_of_a_path_not_its_ends() -> None:
    """The same measurement `farmhouses_reach_a_way` makes. Measuring to the ENDS would call a house
    beside the middle of a long lane unreached."""
    path = [(0.0, 0.0), (1000.0, 0.0)]
    assert _reach((500.0, 30.0), path) == pytest.approx(30.0)


def test_trim_to_service_pulls_an_end_back_to_what_it_serves() -> None:
    """A tread that stops in bare grass serves nobody. Trimming happens BEFORE the ink and before the
    join is computed - trimming afterwards moves the end out from under the link drawn to it."""
    run = [(0.0, 0.0), (50.0, 0.0), (100.0, 0.0), (900.0, 0.0)]
    segs = [((0.0, -20.0), (0.0, 20.0))]
    out = hg.ways._trim_to_service(run, segs, [(100.0, 30.0)])
    assert out[-1] == (100.0, 0.0), "the 800 ft tail into nothing is dropped"
    assert out[0] == (0.0, 0.0), "the end that meets a way is kept"


def test_trim_to_service_never_trims_below_two_points() -> None:
    run = [(5000.0, 5000.0), (5100.0, 5000.0), (5200.0, 5000.0)]
    assert len(hg.ways._trim_to_service(run, [], [])) == 2


def test_route_goes_around_an_obstacle_rather_than_through_it() -> None:
    wall = [(40.0, -60.0), (60.0, -60.0), (60.0, 60.0), (40.0, 60.0)]
    path = hg.ways._route((0.0, 0.0), (100.0, 0.0), [wall], [], [], cell=8.0)
    assert path, "there is a way round the end of the wall"
    assert hg.ways.polyline_len(path) > 100.0, "going round costs more than the straight line"
    assert max(abs(q[1]) for q in path) > 40.0, "and it leaves the straight line to do it"


def test_net_reach_measures_the_paths_VERTICES_against_the_network() -> None:
    """Vertex-to-segment, not segment-to-segment, and the asymmetry is worth knowing: a long straight
    run whose middle passes close to a way but whose vertices do not will read as further off than it
    looks. The web samples its runs every few feet, so in practice the vertices are the line - but a
    caller handing it a two-point polyline gets the corner distance, not the perpendicular."""
    assert hg.ways._net_reach([(0.0, 50.0), (100.0, 50.0)], [((50.0, 0.0), (60.0, 0.0))]) == pytest.approx(64.031242, abs=1e-4)
    dense = [(float(x), 50.0) for x in range(0, 101, 5)]
    assert hg.ways._net_reach(dense, [((50.0, 0.0), (60.0, 0.0))]) == pytest.approx(50.0)


def test_trim_to_service_trims_the_FRONT_end_too() -> None:
    """Both ends, not just the tail. This branch had no test of its own and was covered only because
    some pool map happened to lay a run whose head hung in bare grass - so a cluster-shape change
    that moved the houses took the coverage away with it, which is what a branch tested by luck
    looks like when the luck runs out."""
    run = [(-900.0, 0.0), (0.0, 0.0), (50.0, 0.0), (100.0, 0.0)]
    segs = [((100.0, -20.0), (100.0, 20.0))]
    out = hg.ways._trim_to_service(run, segs, [(0.0, 30.0)])
    assert out[0] == (0.0, 0.0), "the 900 ft head into nothing is dropped"
    assert out[-1] == (100.0, 0.0), "the end that meets a way is kept"


def test_nearest_seg_returns_the_distance_AND_the_segment_it_belongs_to() -> None:
    """One expression, one answer - a caller must not re-derive which segment was nearest."""
    segs = [((0.0, 0.0), (100.0, 0.0)), ((0.0, 200.0), (100.0, 200.0))]
    d, sg = _nearest_seg((50.0, 10.0), segs)
    assert round(d, 6) == 10.0
    assert sg == segs[0]
    assert _nearest_seg((0.0, 0.0), []) == (float("inf"), None)


def test_trim_to_service_counts_ARRIVING_AT_THE_FIELD_as_service() -> None:
    """The spur's whole purpose is the crop, which is neither a house nor another lane."""
    field = [(400.0, 0.0), (600.0, 0.0), (600.0, 200.0), (400.0, 200.0)]
    run = [(0.0, 100.0), (200.0, 100.0), (395.0, 100.0)]
    assert _trim_to_service(run, [], [(0.0, 100.0)], [field]) == run
    assert len(_trim_to_service(run, [], [(0.0, 100.0)], [])) == 2


# ---- the splice helpers (feature 137 T04) ---------------------------------------------------------


def test_unretrace_collapses_an_out_and_back_spur() -> None:
    """A join link prepended whole doubled back along the piece's own first segment (cohort seed 07):
    A -> B -> A' -> B -> C is A -> B -> C."""
    pts = [(0.0, 0.0), (20.0, 0.0), (0.5, 0.0), (20.0, 0.0), (60.0, 0.0)]
    assert hg.ways._unretrace(pts) == [(0.0, 0.0), (20.0, 0.0), (60.0, 0.0)]


def test_unretrace_keeps_a_polyline_that_would_fold_away_entirely() -> None:
    """A door path whose link ran back past the door is an ugly lane, not an empty one (seed 03)."""
    pts = [(0.0, 0.0), (20.0, 0.0), (0.0, 0.0)]
    assert hg.ways._unretrace(pts) == pts


def test_stop_at_network_cuts_a_link_where_it_crosses_the_way_it_was_sent_to() -> None:
    """Tripwire seed 27: the link touched a way at 20 ft and carried on to a `q` a trim later removed."""
    link = [(0.0, 0.0), (0.0, 30.0), (0.0, 60.0)]
    way = [((-20.0, 20.0), (20.0, 20.0))]
    assert hg.ways._stop_at_network(link, way) == [(0.0, 0.0), (0.0, 20.0)]


def test_stop_at_network_lands_on_the_way_it_stops_beside() -> None:
    """A vertex 3 ft off a way is a piece to the web's 4 ft join tolerance once rounded - the cut
    ends on the way's foot point, not beside it."""
    link = [(0.0, 0.0), (30.0, 3.0), (60.0, 3.0)]
    way = [((20.0, 0.0), (40.0, 0.0))]
    assert hg.ways._stop_at_network(link, way) == [(0.0, 0.0), (30.0, 3.0), (30.0, 0.0)]


def test_stop_at_network_leaves_a_link_that_meets_nothing_on_the_way() -> None:
    link = [(0.0, 0.0), (30.0, 0.0), (60.0, 0.0)]
    assert hg.ways._stop_at_network(link, []) == link
    assert hg.ways._stop_at_network(link, [((0.0, 50.0), (60.0, 50.0))]) == link


def test_thread_the_fabric_takes_a_detour_when_neither_the_route_nor_the_clip_clears() -> None:
    from l7r.diagram.hamletgen.ways import _homestead_polys, _thread_the_fabric

    s, plan = _walled_settlement()
    run = [(700.0, 200.0), (700.0, 1200.0)]  # straight through the middle house
    fabric = [poly for poly, _o, _k in _homestead_polys(s)]
    assert _crosses_fabric(run, fabric, 8.0), "the fixture must actually be blocked, or the fallback proves nothing"
    out = _thread_the_fabric(s, plan, run, gap=8.0)
    assert len(out) >= 2
    assert out != run, "the straight run was kept - the detour never ran"


def test_thread_the_fabric_returns_the_run_untouched_when_there_is_no_fabric() -> None:
    from l7r.diagram.hamletgen.ways import _thread_the_fabric
    from l7r.diagram.settlement import Settlement

    from .._builders import a_plan

    s = Settlement(800, 800, seed=1)
    s.meta(name="E", scale="hamlet", ftpx=1, down_deg=90)
    run = [(100.0, 100.0), (700.0, 700.0)]
    assert _thread_the_fabric(s, a_plan(), run) == run  # nothing standing: nothing to thread
    assert _thread_the_fabric(s, a_plan(), [(1.0, 1.0)]) == [(1.0, 1.0)]  # a one-point run is not a run


def test_smooth_web_cuts_the_SHORT_arm_off_a_hairpin() -> None:
    """Feature 146: `_smooth_web`'s hairpin ARM cut, both directions. A lane that doubles back is not a way
    feet wore. The un-jog pass gets first refusal and replaces the hairpin with its chord where the chord is
    clear; where it is BLOCKED (a steading in the way, as here) the short arm is cut off instead."""
    from l7r.diagram.hamletgen.ways import _smooth_web

    block = [[(690.0, 220.0), (790.0, 220.0), (790.0, 250.0), (690.0, 250.0)]]  # across every chord below

    # a short head (30 ft) doubling back into a longer tail: the HEAD goes
    s1 = _webbed([{"pts": [[700.0, 230.0], [700.0, 200.0], [704.0, 232.0]], "w": 5}])
    _smooth_web(s1, block, [], [])
    kept = s1.M["lanes"][0]["pts"]
    assert len(kept) == 2 and abs(kept[0][1] - 200.0) < 1e-6, kept

    # the mirror: a short TAIL doubling back off a longer head
    s2 = _webbed([{"pts": [[704.0, 232.0], [700.0, 200.0], [700.0, 230.0]], "w": 5}])
    _smooth_web(s2, block, [], [])
    kept2 = s2.M["lanes"][0]["pts"]
    assert len(kept2) == 2 and abs(kept2[-1][1] - 200.0) < 1e-6, kept2


def test_the_cluster_gateway_and_edge_fall_back_when_no_house_is_placed_yet() -> None:
    """Feature 146: both helpers take the cloud's own extent, and both keep a fallback for a caller that
    asks before any house is seated - which the shipped order does not do, and which this file's own comment
    says is the failure mode it has met repeatedly."""
    from l7r.diagram.hamletgen.ways import _cluster_edge_toward, _cluster_gateway
    from l7r.diagram.settlement import Settlement

    s = Settlement(1000, 1000, seed=1)
    s.meta(name="G", scale="hamlet", ftpx=1, down_deg=90)
    seat = {"cx": 500.0, "cy": 500.0, "along": (1.0, 0.0), "out": (0.0, 1.0), "half": 200.0, "depth": 80.0}
    fallback = (123.0, 456.0)
    assert _cluster_gateway(s, seat, fallback) == fallback
    assert _cluster_edge_toward(s, (900.0, 500.0), fallback) == fallback
    s.M["houses"].append({"x": 500.0, "y": 500.0, "w": 50.0, "h": 30.0})
    assert _cluster_gateway(s, seat, fallback) != fallback, "with a house placed it measures the cloud"
    assert _cluster_edge_toward(s, (900.0, 500.0), fallback) != fallback


def test_a_hairpin_arm_LONGER_than_the_cheap_cap_is_cut_once_the_cut_is_MEASURED() -> None:
    """The repair's threshold and the check's threshold were different numbers, and nothing compared them.

    `lanes_bend_like_paths` fails ANY turn past 140 degrees, while `_smooth_web` would only cut an arm
    under `_ARM_FT` (40 ft). Everything in the band between was drawn, failed, and could not be repaired
    by any pass - tripwire seed 47's lane 11 doubled back 62 ft. The cap was standing in for "do not
    destroy a lane doing real work", so `_arm_cuttable` measures that instead: the arm goes when no
    farmhouse loses its way and the tip left behind still reaches something."""
    from l7r.diagram.hamletgen.ways import _smooth_web, _turn_deg

    assert _turn_deg((620.0, 300.0), (702.0, 300.0), (630.0, 318.0)) >= 140.0, "the fixture really is a hairpin"
    s = _webbed([{"pts": [list(p) for p in _HAIRPIN], "w": 5}, dict(_TIP_WAY)])
    _smooth_web(s, _FOLD_BAR, [], [])
    kept = s.M["lanes"][0]["pts"]
    assert kept[0] == [702.0, 300.0], f"the 82 ft arm is cut and the apex becomes the end: {kept}"
    assert all(_turn_deg(tuple(kept[k - 1]), tuple(kept[k]), tuple(kept[k + 1])) < 140.0 for k in range(1, len(kept) - 1)), kept


def test_the_arm_is_KEPT_when_a_farmhouse_would_lose_its_only_way() -> None:
    """The measurement has to preserve what the cap was protecting. This house stands 95 ft off the
    arm and 113 ft from every other tread, so cutting would strand it; the lane keeps its hairpin and
    `lanes_bend_like_paths` then fires on it honestly, which is the visible, correct outcome."""
    from l7r.diagram.hamletgen.ways import _smooth_web

    s = _webbed([{"pts": [list(p) for p in _HAIRPIN], "w": 5}, dict(_TIP_WAY)])
    s.M["houses"].append({"x": 620.0, "y": 205.0, "w": 40.0, "h": 25.0})
    _smooth_web(s, _FOLD_BAR, [], [])
    assert s.M["lanes"][0]["pts"] == [list(p) for p in _HAIRPIN], "a farmhouse with no other way keeps the arm that serves it"


def test_the_arm_is_KEPT_when_the_tip_left_behind_would_reach_nothing() -> None:
    """The other half of the measurement, and the one that binds most often. After the cut the tip IS
    the lane's end, and an end owes `lanes_reach_something` a way within 40 ft or a farmhouse within
    90 ft - so a cut that would trade a bend failure for a reach failure is refused. Same fixture with
    the neighbouring way taken away."""
    from l7r.diagram.hamletgen.ways import _smooth_web

    s = _webbed([{"pts": [list(p) for p in _HAIRPIN], "w": 5}])
    _smooth_web(s, _FOLD_BAR, [], [])
    assert s.M["lanes"][0]["pts"] == [list(p) for p in _HAIRPIN], "nothing within reach of the tip, so the arm stays"


def test_an_arm_past_the_long_cap_is_a_lane_rather_than_an_arm() -> None:
    """`_LONG_ARM_FT` is the check's own farmhouse figure: past 90 ft the arm reaches ground the rest
    of the lane cannot, so it is a lane in its own right and is kept whatever the measurement says.
    The cap bounds how much of the picture one cut may change; it no longer decides the cut alone."""
    from l7r.diagram.hamletgen.ways import _smooth_web

    s = _webbed([{"pts": [list(p) for p in _LONG_HAIRPIN], "w": 5}, dict(_TIP_WAY)])
    _smooth_web(s, _FOLD_BAR, [], [])
    assert s.M["lanes"][0]["pts"] == [list(p) for p in _LONG_HAIRPIN], "a 100 ft arm is a lane, not an arm"


def test_a_lane_whittled_below_the_minimum_and_left_standing_alone_is_swept() -> None:
    """`draw_web_lane` refuses to draw anything under `_WEB_MIN_FT`, and that rule was asked ONCE, at
    draw time - while a trim, a hairpin cut and `_stop_at_network` all shorten lanes afterwards.
    Tripwire seed 27 shipped a 20.5 ft two-point stub standing 31 ft off the nearest lane, in a slot
    about 7 ft wide that no link the joiner may draw could reach. The husk goes with the ink (feature
    145's rule from a Sawada review), so the record is deleted rather than left empty."""
    from l7r.diagram.hamletgen.ways import _sweep_debris

    s = _webbed([{"pts": [[300.0, 300.0], [300.0, 500.0]], "w": 5}, {"pts": [[600.0, 300.0], [614.0, 315.0]], "w": 5}])
    assert _sweep_debris(s) == 1
    assert len(s.M["lanes"]) == 1, "the record is deleted with its ink, not left declaring a lane nothing draws"
    assert s.M["lanes"][0]["pts"][0] == [300.0, 300.0], "the real lane is untouched"
    assert s.M["meta"]["lane_fragments_dropped"] == 1


def test_the_sweep_spares_a_short_lane_that_MEETS_the_web_and_one_that_is_a_houses_only_way() -> None:
    """Two guards, both load-bearing: a short spur that joins the network is a real lane and not
    debris, and a stranded fragment that is some farmhouse's only way stays visibly broken rather
    than stranding the house - `farmhouses_reach_a_way` is the check that should speak in that case."""
    from l7r.diagram.hamletgen.ways import _sweep_debris

    joined = _webbed([{"pts": [[300.0, 300.0], [300.0, 500.0]], "w": 5}, {"pts": [[300.0, 400.0], [318.0, 404.0]], "w": 5}])
    assert _sweep_debris(joined) == 0, "a 20 ft spur that touches the web is a lane, not debris"
    assert len(joined.M["lanes"]) == 2

    only_way = _webbed([{"pts": [[300.0, 300.0], [300.0, 500.0]], "w": 5}, {"pts": [[900.0, 300.0], [914.0, 315.0]], "w": 5}])
    only_way.M["houses"].append({"x": 930.0, "y": 330.0, "w": 40.0, "h": 25.0})
    assert _sweep_debris(only_way) == 0, "the fragment is that house's only way"
    assert len(only_way.M["lanes"]) == 2


def test_a_FINER_lattice_walks_a_narrower_corridor_than_a_coarse_one() -> None:
    """`_route` plans on a lattice and inflates its clearance by half a cell's diagonal
    (`gap + cell * 0.71`) so that "this cell is free" means every point in it is clear. That is
    load-bearing - it is what stopped lanes planned at 7 ft from being drawn at 4 - but the cost is
    charged against the CORRIDOR and it is invisible at the call site: at cell 6 a `_TOUCH_GAP`
    route really demands 8.26 ft, and at cell 10 a fabric route 14.1 ft. Tripwire seed 27's only way
    out of a stranded stub was a gap about 7 ft wide, so every rung of the orphan joiner's ladder
    reported NO ROUTE for a journey that plainly existed, and the caller could only say the piece
    would not join. Planning the last rung at `_FINE_CELL` is what opens it.

    The relationship is measured rather than predicted: the narrowest gap each cell size can thread
    is searched for, so the test cannot be wrong about the router's internals - which an earlier
    version of it was, twice."""
    from l7r.diagram.hamletgen.ways import _FINE_CELL, _TOUCH_GAP

    def narrowest_passable(cell: float) -> float | None:
        """Best case over several wall CENTRES, because the lattice samples cell centres and a gap that
        happens to straddle a sampled column threads at a width one offset to the side does not - noise
        of up to half a cell, which is the same order as the effect being measured."""
        return min((_narrowest_at(cell, centre) for centre in (443.0, 444.0, 445.0, 446.0, 447.0)), default=None)

    def _narrowest_at(cell: float, centre: float) -> float:
        """The smallest half-gap this cell size can plan through, in a wall that seals the search box
        except for one opening OFFSET from the straight line - offset so the router cannot take its
        straight-line shortcut and must actually plan."""
        for half in range(3, 17):
            wall = [
                [(300.0, 480.0), (centre - half, 480.0), (centre - half, 520.0), (300.0, 520.0)],
                [(centre + half, 480.0), (700.0, 480.0), (700.0, 520.0), (centre + half, 520.0)],
            ]
            if _route((500.0, 470.0), (500.0, 530.0), wall, [], [], gap=_TOUCH_GAP, pad_mult=2.0, cell=cell):
                return float(half)
        return float("inf")

    # against the DETOUR rung's own cell 10, whose effective clearance is 14.1 ft to the fine rung's
    # 6.13 - a gap far wider than the half-cell of sampling noise, which cell 6 was not.
    fine, coarse = narrowest_passable(_FINE_CELL), narrowest_passable(10.0)
    assert fine is not None and coarse is not None and fine != float("inf"), (fine, coarse)
    assert fine + 2.0 <= coarse, f"a {_FINE_CELL} ft lattice threads a corridor the 10 ft one cannot: {fine} vs {coarse}"


def test_web_pieces_counts_connected_lanes_and_ignores_stubs() -> None:
    """Feature 146: `web_pieces` lifted out of `_smooth_web` so it can be asked directly. A lane of fewer
    than two points is not a piece; lanes that touch are one."""
    from l7r.diagram.hamletgen.ways import web_pieces

    touching = [{"pts": [[0.0, 0.0], [100.0, 0.0]]}, {"pts": [[100.0, 0.0], [100.0, 100.0]]}]
    apart = [{"pts": [[0.0, 0.0], [100.0, 0.0]]}, {"pts": [[900.0, 900.0], [999.0, 900.0]]}]
    assert web_pieces(touching) == 1
    assert web_pieces(apart) == 2
    assert web_pieces([*apart, {"pts": []}, {"pts": [[5.0, 5.0]]}]) == 2, "an empty or one-point lane is no piece"


def test_web_rejoinable_says_whether_the_touch_pass_will_close_a_new_piece() -> None:
    """Feature 146: `web_rejoinable` lifted out of the same closure. A stub whose end stands within the
    touch pass's reach of another piece, with a clear straight link, will be closed again - so a rewrite
    that made it is allowed. A stub out of reach will not, so the rewrite is refused."""
    from l7r.diagram.hamletgen.ways import _STUB_REACH_FT, web_rejoinable

    spine = {"pts": [[0.0, 0.0], [400.0, 0.0]], "connector": True}
    near = {"pts": [[200.0, _STUB_REACH_FT - 2.0], [300.0, _STUB_REACH_FT - 2.0]]}
    far = {"pts": [[200.0, 900.0], [300.0, 900.0]]}
    assert web_rejoinable([spine, near], [], [], []) is True
    assert web_rejoinable([spine, far], [], [], []) is False
    wall = [[(150.0, 2.0), (350.0, 2.0), (350.0, 8.0), (150.0, 8.0)]]  # between the stub and the spine
    assert web_rejoinable([spine, near], wall, [], []) is False, "in reach, but no clear link"
    assert web_rejoinable([spine], [], [], []) is True, "one piece has nothing to rejoin"


def test_touch_junctions_records_an_orphan_it_can_neither_link_nor_drop() -> None:
    """The LAST rung of the orphan ladder, and the one a rolled map almost never reaches.

    A piece too far to link (past `_ORPHAN_REACH` = 150 ft) is normally DROPPED - unless dropping it
    would strand a farmhouse, and then it is kept, visibly broken, with the count in `meta`. The
    comment at that line says why: deleting it once stranded a house, `farmhouses_reach_a_way` failed,
    and the driver silently re-rolled the whole map. So the arm has to keep working."""
    from l7r.diagram.hamletgen.ways import _touch_junctions

    s = _StubWeb(
        lanes=[
            {"pts": [[0.0, 0.0], [200.0, 0.0]], "w": 3, "connector": True},
            {"pts": [[0.0, 900.0], [120.0, 900.0]], "w": 3},  # far past _ORPHAN_REACH from the spine
        ],
        houses=[{"x": 60.0, "y": 905.0}],  # served by the orphan alone: 5 ft from it, 900 from the spine
    )
    _touch_junctions(s, [], [], [], only_orphans=False)  # type: ignore[arg-type]
    assert s.M["meta"].get("lane_orphans") == 1, "the piece is KEPT and counted, not deleted under the house"
    assert len(s.M["lanes"]) == 2, "nothing was dropped"


def test_touch_junctions_drops_an_unreachable_piece_that_strands_nobody() -> None:
    """The rung above: same geometry, no house depending on the fragment, so it goes - record and ink
    together (`lane_fragments_dropped`), because a lane record nothing draws is the defect."""
    from l7r.diagram.hamletgen.ways import _touch_junctions

    s = _StubWeb(
        lanes=[
            {"pts": [[0.0, 0.0], [200.0, 0.0]], "w": 3, "connector": True},
            {"pts": [[0.0, 900.0], [120.0, 900.0]], "w": 3},
        ],
        houses=[{"x": 60.0, "y": 5.0}],  # on the spine, not the fragment
    )
    _touch_junctions(s, [], [], [], only_orphans=False)  # type: ignore[arg-type]
    assert s.M["meta"].get("lane_fragments_dropped") == 1
    assert len(s.M["lanes"]) == 1, "the husk goes with the ink"


def test_join_piece_prepends_a_link_that_meets_the_piece_at_its_HEAD() -> None:
    """`_join_piece` appends when the link starts at the piece's tail and PREPENDS, reversed, when it
    starts at the head. Only the append arm is exercised by the live hamlets - which arm a roll takes
    is an accident of which end of a stranded stub happened to face the spine."""
    from l7r.diagram.hamletgen.ways import _join_piece

    piece = [(100.0, 100.0), (160.0, 100.0)]
    s = _StubWeb(lanes=[{"pts": [[100.0, 100.0], [160.0, 100.0]], "w": 3}])
    _join_piece(s, s.M["lanes"], 0, piece, (100.0, 100.0), [(100.0, 100.0), (40.0, 100.0)], [], [], [], [])  # type: ignore[arg-type]
    pts = s.M["lanes"][0]["pts"]
    assert s.reinked == [0]
    assert pts[0] == [40.0, 100.0], "the link is reversed onto the FRONT, so the lane still reads end to end"
    assert pts[-1] == [160.0, 100.0]


def test_commit_lane_puts_a_rewrite_back_when_it_breaks_the_web_beyond_repair() -> None:
    """The revert arm - the reason `commit_lane` exists (feature 137 T03) and the one a clean roll never
    enters. A cut that splits the web is allowed ONLY while the touch pass could close it again."""
    from l7r.diagram.hamletgen.ways import commit_lane

    lanes: list = [
        {"pts": [[0.0, 0.0], [400.0, 0.0]], "w": 3, "connector": True},
        {"pts": [[200.0, 0.0], [200.0, 60.0], [400.0, 60.0]], "w": 3},  # meets the spine at its head
    ]
    reinked: list[int] = []
    # cutting the second lane back to its far half strands it 200 ft from anything: one more piece,
    # and no end within the stub reach of another tread, so the touch pass could not mend it
    assert not commit_lane(lanes, 1, [[900.0, 900.0], [980.0, 900.0]], [], [], [], reinked.append)
    assert lanes[1]["pts"] == [[200.0, 0.0], [200.0, 60.0], [400.0, 60.0]], "put back exactly as it was"
    assert reinked == [], "and never re-inked"


def test_commit_lane_accepts_a_rewrite_that_keeps_the_web_whole() -> None:
    from l7r.diagram.hamletgen.ways import commit_lane

    lanes: list = [
        {"pts": [[0.0, 0.0], [400.0, 0.0]], "w": 3, "connector": True},
        {"pts": [[200.0, 0.0], [200.0, 60.0], [400.0, 60.0]], "w": 3},
    ]
    reinked: list[int] = []
    assert commit_lane(lanes, 1, [[200.0, 0.0], [200.0, 40.0]], [], [], [], reinked.append)
    assert reinked == [1]


def test_bowtie_cut_takes_the_short_tail_the_short_head_or_neither() -> None:
    """Which arm a roll takes is an accident of the direction the lane was recorded in, so both are asked
    directly. `_ARM_FT` is 40 ft: a stray tail past a crossing is cut back TO the crossing."""
    from l7r.diagram.hamletgen.ways import bowtie_cut

    pts = [(0.0, 0.0), (100.0, 0.0), (120.0, 0.0)]  # crossing inside segment 1, near its far end
    assert bowtie_cut(pts, 1, (95.0, 0.0)) == [(0.0, 0.0), (100.0, 0.0), (95.0, 0.0)][:2] + [(95.0, 0.0)]

    head = [(0.0, 0.0), (20.0, 0.0), (400.0, 0.0)]  # the crossing sits 5 ft into a 380 ft second leg
    assert bowtie_cut(head, 1, (25.0, 0.0)) == [(25.0, 0.0), (400.0, 0.0)], "the short HEAD is the stray"

    long_both = [(0.0, 0.0), (300.0, 0.0), (600.0, 0.0)]
    assert bowtie_cut(long_both, 1, (450.0, 0.0)) is None, "neither side is a stray tail; leave the lane alone"


def test_push_clear_of_fabric_returns_the_last_point_tried_when_the_cluster_rings_it_round() -> None:
    """The bound is what makes the last line a real branch: a gateway that cannot get clear is still
    drawn from, because a track has to start somewhere. No live hamlet is that crowded."""
    from l7r.diagram.hamletgen.ways import push_clear_of_fabric

    # a corridor the whole walk stays inside: every point tried is within 5 px of its long edges,
    # under the 16 px the track keeps, so all 24 steps are refused
    corridor = [(-100.0, -5.0), (5000.0, -5.0), (5000.0, 5.0), (-100.0, 5.0)]
    got = push_clear_of_fabric((0.0, 0.0), (1.0, 0.0), 10.0, [corridor])
    assert got == pytest.approx((10.0 + 24 * 6.0, 0.0)), "24 steps of 6 px, then hand back where it stopped"

    clear = push_clear_of_fabric((0.0, 0.0), (1.0, 0.0), 10.0, [])
    assert clear == pytest.approx((10.0, 0.0)), "nothing in the way: the first point tried"


def test_shadowing_lane_asks_whether_a_lane_goes_anywhere() -> None:
    """A structural yes-or-no, with no dial to leave set too low. Both ends on one way means the
    lane connects that way to itself."""
    parent = [(0.0, 0.0), (300.0, 0.0)]
    assert hg.ways.shadowing_lane([(100.0, 6.6), (144.0, 6.6)], [parent], 30.0) == 0
    assert hg.ways.shadowing_lane([(100.0, 0.0), (136.0, 11.4)], [parent], 30.0) == 0
    # a lane that goes somewhere: one end on the parent, the other out in the fields
    assert hg.ways.shadowing_lane([(100.0, 0.0), (100.0, 120.0)], [parent], 30.0) is None
    assert hg.ways.shadowing_lane([(0.0, 0.0)], [parent], 30.0) is None  # nothing is a lane
    assert hg.ways.shadowing_lane([(100.0, 6.6), (144.0, 6.6)], [[(0.0, 0.0)]], 30.0) is None  # nor is the other one
