"""The brook's placer guarantees (feature 287, water:W01-W04, W06-W09, W11): one engine predicate per rule, and the placer
tested on constructed inputs that include the violating case (FR-004)."""

import math
import random

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen.consts import BROOK_MAX_TURN_DEG, BROOK_TAP_RUN
from l7r.diagram.hamletgen.water import brook as wb
from l7r.diagram.hamletgen.water import brook_rules as br
from l7r.diagram.settlement import Settlement

from ._builders import a_plan

TAP = (700.0, 300.0)


def _straightest_reference(pts: list[tuple[float, float]], tol: float) -> float:
    """The pool test's `_straightest`, verbatim - the body `straightest_run` replaces."""
    best = 0.0
    for i in range(len(pts)):
        for j in range(i + 2, len(pts)):
            a, b = pts[i], pts[j]
            span = math.dist(a, b)
            if span > best and all(abs((b[0] - a[0]) * (a[1] - q[1]) - (a[0] - q[0]) * (b[1] - a[1])) / span <= tol for q in pts[i : j + 1]):
                best = span
    return best


def _skirt_below(plan: hg.SitePlan) -> list[tuple[float, float]]:
    return hg.brook_skirt(plan, TAP, plan.brook_side)


# ---- the predicates ----------------------------------------------------------------------------------


def test_the_turn_is_read_once_and_a_zero_leg_turns_nothing() -> None:
    assert br.turn_deg((0.0, 0.0), (10.0, 0.0), (20.0, 0.0)) == pytest.approx(0.0)
    assert br.turn_deg((0.0, 0.0), (10.0, 0.0), (10.0, 10.0)) == pytest.approx(90.0)
    assert br.turn_deg((0.0, 0.0), (0.0, 0.0), (5.0, 5.0)) == 0.0
    assert br.max_turn_deg([(0.0, 0.0), (100.0, 0.0), (40.0, -20.0)]) > 150.0
    assert br.max_turn_deg([(0.0, 0.0), (1.0, 1.0)]) == 0.0


def test_unfold_never_drops_a_held_vertex_it_drops_the_one_before() -> None:
    """water:W01: a fold AT the tap takes out the approach's last point, not the tap the head race leaves from; a fold
    between two held vertices has nothing it may drop and stays for the placer to refuse."""
    folded = [(0.0, 0.0), (100.0, 0.0), (200.0, 0.0), (190.0, 10.0), (260.0, 200.0)]  # 135 degrees at the held (200, 0)
    out = wb.unfold(folded, 100.0, hold=[(200.0, 0.0)])
    assert out == [(0.0, 0.0), (200.0, 0.0), (260.0, 200.0)], "the vertex before the tap went first, then the one after"
    assert br.max_turn_deg(out) <= 100.0
    pinned = [(0.0, 0.0), (100.0, 0.0), (0.0, 5.0)]
    assert wb.unfold(pinned, 100.0, hold=[(100.0, 0.0)]) == pinned, "the fold's only interior vertex is held"
    # held and its neighbor held: the vertex after it goes
    after = [(0.0, 0.0), (50.0, 0.0), (100.0, 0.0), (20.0, 10.0), (20.0, 200.0)]
    assert wb.unfold(after, 100.0, hold=[(50.0, 0.0), (100.0, 0.0)]) == [(0.0, 0.0), (50.0, 0.0), (100.0, 0.0), (20.0, 200.0)]


def test_a_level_run_along_the_frame_is_found_as_the_pool_test_finds_it() -> None:
    """water:W02: 457 ft within 4 ft of one y, 40 ft under the view's top edge (Sawada), is a run; the same run 300 ft
    inside the view is not, unless nearness is waived; a run that wanders 5 ft is not a run at all."""
    level = [(100.0 + 50.0 * k, 140.0 + (k % 2) * 3.0) for k in range(11)]
    runs = br.level_runs_along_frame(level, (0.0, 100.0, 2000.0, 2000.0))
    assert runs and runs[0][0] == 1 and runs[0][3] == pytest.approx(math.dist(level[0], level[1]) * 10)
    deep = [(x, y + 300.0) for x, y in level]
    assert br.level_runs_along_frame(deep, (0.0, 100.0, 2000.0, 2000.0)) == []
    assert br.level_runs_along_frame(deep, (0.0, 100.0, 2000.0, 2000.0), near=math.inf)
    wander = [(100.0 + 50.0 * k, 140.0 + (k % 2) * 5.0) for k in range(11)]
    assert br.level_runs_along_frame(wander, (0.0, 100.0, 2000.0, 2000.0)) == []


def test_the_straightest_run_is_the_pool_tests_own_measure() -> None:
    """water:W03: `straightest_run` answers what the test's cubic `_straightest` answers, on random courses and on the
    edge cases - a straight line, a single bend, fewer than three points."""
    rng = random.Random(287)
    for _ in range(60):
        pts = [(0.0, 0.0)]
        for _k in range(rng.randint(2, 18)):
            pts.append((pts[-1][0] + rng.uniform(5.0, 60.0), pts[-1][1] + rng.uniform(-6.0, 6.0)))
        tol = rng.choice((0.5, 3.1, 8.0))
        assert br.straightest_run(pts, tol) == pytest.approx(_straightest_reference(pts, tol))
    line = [(float(k * 10), 0.0) for k in range(20)]
    assert br.straightest_run(line, 3.1) == pytest.approx(190.0)
    assert br.straightest_run([(0.0, 0.0), (10.0, 0.0)], 3.1) == 0.0
    run, i, j = br.straightest_chord(line, 3.1)
    assert (run, i, j) == (pytest.approx(190.0), 0, 19)
    # a course folding back on its own line: the chord's bearing is a LINE's, taken mod 180
    back = [(0.0, 0.0), (100.0, 0.0), (50.0, 0.5), (0.0, 1.0), (-50.0, 1.0)]
    assert br.straightest_run(back, 3.1) == pytest.approx(_straightest_reference(back, 3.1))


def test_the_ruled_share_is_judged_inside_the_view() -> None:
    line = [(float(k * 50), 500.0) for k in range(21)]  # 1,000 ft dead straight
    assert not br.ruled_share_ok(line, (0.0, 0.0, 2000.0, 1000.0))
    assert br.ruled_share_ok(line, (0.0, 0.0, 200.0, 1000.0)), "under 300 ft in the view: the rule does not apply"
    wavy = [(float(k * 50), 500.0 + (10.0 if k % 2 else 0.0)) for k in range(21)]
    assert br.ruled_share_ok(wavy, (0.0, 0.0, 2000.0, 1000.0))


def test_the_axis_rule_exempts_the_tap_run_and_short_chords_only() -> None:
    """water:W04 (named by the GM): a segment of a wander stride or more within 1.6 degrees of an axis is found; the two
    segments leaving the tap are the tap run and exempt; a chord under the stride is a curve's, not a run."""
    course = [(0.0, 0.0), (0.0, 100.0), (0.0, 170.0), (40.0, 260.0), (40.0, 400.0), (42.0, 405.0)]
    assert br.axis_segments(course, [(0.0, 100.0)]) == [0, 3]
    assert br.axis_segments(course, [(0.0, 0.0)]) == [3]
    assert br.tap_index(course, []) == 0, "no head race: the pool test's default"


def test_the_small_predicates() -> None:
    ring = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    assert br.course_enters([(-50.0, 50.0), (50.0, 50.0), (150.0, 50.0)], [ring])
    assert not br.course_enters([(50.0, 50.0), (150.0, 50.0), (250.0, 50.0)], [ring]), "an end inside is the intake, not a crossing"
    assert br.ends_off_canvas([(-5.0, 10.0), (50.0, 50.0)], 100.0, 100.0, ends=(0,))
    assert not br.ends_off_canvas([(-5.0, 10.0), (50.0, 50.0)], 100.0, 100.0)
    water = [(0.0, 50.0), (200.0, 50.0)]
    assert br.crosses_mid_run(water, [(100.0, 0.0), (100.0, 200.0)])
    assert not br.crosses_mid_run(water, [(100.0, 0.0), (100.0, 45.0), (100.0, 55.0)]), "an end at the water is a confluence"
    assert not br.crosses_mid_run(water, [(100.0, 0.0)]) and not br.crosses_mid_run([(0.0, 0.0)], [(1.0, 1.0), (2.0, 2.0)])
    assert br.monotone_down([(0.0, 0.0), (5.0, 10.0), (0.0, 20.0)], (0.0, 1.0))
    assert not br.monotone_down([(0.0, 0.0), (5.0, 10.0), (0.0, 5.0)], (0.0, 1.0))
    assert br.bar_on_race([(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)], [(5.0, -20.0), (5.0, 30.0)], 2.0) == pytest.approx(20.0)
    assert br.bar_on_race([(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)], [], 2.0) == 0.0
    assert br.to_edge((100.0, 100.0), (1.0, 0.0), 1000.0, 500.0) == pytest.approx(900.0)
    assert br.to_edge((100.0, 100.0), (0.0, -1.0), 1000.0, 500.0) == pytest.approx(100.0)
    assert br.to_edge((100.0, 100.0), (0.0, 0.0), 1000.0, 500.0) == 0.0


def test_the_reserved_box_holds_the_paddies_and_the_stations_beside_the_field_and_hem() -> None:
    """water:W03: every view holds the paddies' visible box and each station within the frame margin of the field or a
    hem plot the brook leaves standing; a hem plot the brook's band crosses is dropped when the hem is drawn, so it
    reserves nothing here either."""
    plan = a_plan()
    plan.net = {
        "plots": [{"poly": [(450.0, 450.0), (950.0, 450.0), (950.0, 950.0), (450.0, 950.0)]}],
        "dry_plots": [{"poly": [(1000.0, 1000.0), (1100.0, 1000.0), (1100.0, 1100.0), (1000.0, 1100.0)]}],
    }
    beside_hem = [(1140.0, 1140.0)]  # within the margin of the hem plot only
    box = br.reserved_box(beside_hem, plan)
    assert box[2] == pytest.approx(1140.0 + br.BROOK_DRAWN_W / 2) and box[0] == 450.0
    through_hem = [(1050.0, 900.0), (1050.0, 1200.0), (1140.0, 1140.0)]  # the brook crosses the hem plot: it is dropped
    assert br.reserved_box(through_hem, plan)[3] < box[3], "the hem the brook crosses reserves no station beside it"
    plan.net = {}
    far = br.reserved_box([(1140.0, 1140.0)], plan)
    assert far == (400.0, 400.0, 1000.0, 1000.0), "no net: the envelope, and a station beyond the margin reserves nothing"


def test_a_level_run_deep_inside_the_reserved_box_is_near_no_views_edge() -> None:
    fin = [(500.0 + 0.0 * k, 400.0 + 40.0 * k) for k in range(8)]  # dead level on x for 280 ft
    assert br.level_runs_any_view(fin, 2000.0, 2000.0, (100.0, 100.0, 1500.0, 1500.0)) == []
    assert br.level_runs_any_view(fin, 2000.0, 2000.0, (450.0, 100.0, 1500.0, 1500.0)), "within 80 ft of the box's edge"


# ---- the repair ----------------------------------------------------------------------------------------


def test_the_axis_pass_moves_the_leg_into_the_tap_by_its_near_end() -> None:
    """water:W04, Inashiro: the approach's last leg 1.2 degrees off vertical into the tap. The whole-course pass tilts it
    by moving the approach point, never the tap; the tap run is left on the fall."""
    tap = (500.0, 500.0)
    w3 = (500.0 + 49.0 * math.tan(math.radians(1.2)), 451.0)
    course = [(500.0, -100.0), (520.0, 200.0), (510.0, 400.0), w3, tap, (500.0, 530.0), (500.0, 570.0), (540.0, 700.0), (560.0, 900.0), (600.0, 1400.0)]
    assert 3 in br.axis_segments(course, [tap])
    out = wb.axes_off(course, (1.0, 0.0), tap, (0.0, 1.0))
    assert out[4] == tap and out[5] == (500.0, 530.0) and out[6] == (500.0, 570.0), "the tap and its run stay"
    assert out[3] != w3 and br.axis_segments(out, [tap]) == []
    # a segment lying ACROSS the fall is tilted down it, at whichever end leaves its neighbor still descending
    across = [(0.0, 0.0), (0.0, 50.0), (0.0, 80.0), (0.0, 120.0), (100.0, 120.2), (130.0, 300.0), (160.0, 900.0)]
    moved = wb.axes_off(across, (1.0, 0.0), (0.0, 50.0), (0.0, 1.0))
    assert moved[4][1] > across[4][1] and 3 not in br.axis_segments(moved, [(0.0, 50.0)])
    assert br.monotone_down(moved[1:], (0.0, 1.0))
    tight = [(0.0, 0.0), (0.0, 50.0), (0.0, 80.0), (0.0, 110.0), (0.0, 120.0), (100.0, 120.2), (130.0, 121.0), (160.0, 900.0)]
    moved = wb.axes_off(tight, (1.0, 0.0), (0.0, 50.0), (0.0, 1.0))
    assert moved[4][1] < 120.0 - 5.0 and moved[5] == tight[5], "no slack below: the near end rises"
    boxed = [(0.0, 0.0), (0.0, 50.0), (0.0, 80.0), (0.0, 120.0), (100.0, 120.2), (130.0, 121.0)]
    assert wb.axes_off(boxed, (1.0, 0.0), (0.0, 50.0), (0.0, 1.0))[3:5] == boxed[3:5], "pinned both ends: left to the judgment"


def test_a_bend_goes_on_the_longest_leg_of_the_run_and_off_the_field() -> None:
    course = [(0.0, 0.0), (0.0, 50.0), (0.0, 100.0), (0.0, 200.0), (0.0, 600.0), (0.0, 640.0)]
    span = [(0.0, 200.0), (0.0, 600.0)]
    need = wb.chord_offsets((0.0, 200.0), (0.0, 600.0), (1.0, 0.0))
    field = [(-100.0, 300.0), (-1.0, 300.0), (-1.0, 500.0), (-100.0, 500.0)]
    out = wb.bend_at(course, span, need, (1.0, 0.0), (0.0, 50.0), field)
    assert len(out) == len(course) + 1 and out[4][1] == pytest.approx(400.0) and abs(out[4][0]) == pytest.approx(br.RULED_TOL_FT + 1.5)
    wide = [(-100.0, 300.0), (100.0, 300.0), (100.0, 500.0), (-100.0, 500.0)]
    assert wb.bend_at(course, span, need, (1.0, 0.0), (0.0, 50.0), wide) == course, "both sides in the field: no bend"
    assert wb.bend_at(course, [(900.0, 900.0)], need, (1.0, 0.0), (0.0, 50.0), field) == course, "no leg along the run"
    lvl = wb.level_offsets(10.0, 0, (0.1, 1.0))
    assert lvl((10.0, 0.0)) == pytest.approx(((br.LEVEL_TOL_FT + 1.5) / 0.3, -(br.LEVEL_TOL_FT + 1.5) / 0.3))
    assert wb.chord_offsets((0.0, 0.0), (100.0, 0.0), (1.0, 0.0))((50.0, 0.0))[0] == pytest.approx((br.RULED_TOL_FT + 1.5) / 0.3)


def test_a_course_through_the_field_is_moved_out_across_the_fall() -> None:
    """water:W06: a cut point between two stations taking the course into a lobe (cohort seed 12) is stepped out across
    the fall until the leg clears; the tap run and the ends are not moved."""
    env = [(400.0, 400.0), (1000.0, 400.0), (1000.0, 1000.0), (400.0, 1000.0)]
    tap = (1100.0, 300.0)
    course = [(1100.0, -100.0), (1100.0, 200.0), tap, (1100.0, 330.0), (1100.0, 370.0), (990.0, 700.0), (1060.0, 1100.0), (1100.0, 1500.0)]
    out = wb.clear_of_field(course, env, (1.0, 0.0), tap)
    assert not any(hg.point_in_poly(p[0], p[1], env) for p in out) and not br.course_enters(out, [env])
    assert out[2:5] == course[2:5] and out[0] == course[0] and out[-1] == course[-1]
    assert all(out[k][1] == course[k][1] for k in range(len(out))), "across the fall only"


# ---- the placer on constructed sites, violating case included -------------------------------------------------


def test_the_brook_placer_judges_its_course_and_the_a_plan_brook_breaks_no_rule() -> None:
    plan = a_plan()
    course = wb.feed_brook(plan, TAP)
    assert TAP in course
    assert wb.brook_violations(course, plan, TAP) == []


def test_a_fold_at_the_tap_is_taken_out_and_the_tap_kept() -> None:
    """water:W01, the Sawada shape: the approach arrives, the skirt's first leg heads back across the fall - 123 degrees
    at the tap. The repair unfolds the whole course with the tap held."""
    plan = a_plan()
    skirt = _skirt_below(plan)
    approach = [(700.0, -500.0), (720.0, 0.0), (690.0, 200.0), (760.0, 420.0)]  # the last leg comes back UP into the tap
    course = [*approach, TAP, *skirt]
    assert br.max_turn_deg(wb.finished_course(course, br.BROOK_DRAWN_W, [TAP])) > BROOK_MAX_TURN_DEG, "the constructed fold"
    settled = wb.settle_course(course, plan, TAP)
    assert TAP in settled
    assert br.max_turn_deg(wb.finished_course(settled, br.BROOK_DRAWN_W, [TAP])) <= BROOK_MAX_TURN_DEG


def test_a_course_pinned_level_along_the_frame_is_bent_off_the_level() -> None:
    """water:W02: a course held dead level for 450 ft - the frame box's edge on Sawada - is bent until no view could read
    a level run along its edge."""
    plan = a_plan()
    tap = (300.0, 300.0)
    plan.envelope = [(400.0, 400.0), (1000.0, 400.0), (1000.0, 1000.0), (400.0, 1000.0)]
    course = [
        (300.0, -300.0),
        (310.0, 100.0),
        (300.0, 250.0),
        tap,
        (300.0, 330.0),
        (300.0, 370.0),
        (340.0, 380.0),
        *[(400.0 + 50.0 * k, 356.0 + (k % 2) * 2.0) for k in range(10)],
        (900.0, 500.0),
        (960.0, 1200.0),
        (1000.0, 2400.0),
    ]
    fin = wb.finished_course(course, br.BROOK_DRAWN_W, [tap])
    box = br.reserved_box(course, plan)
    assert br.level_runs_any_view(fin, plan.W, plan.H, box), "the constructed level run"
    settled = wb.settle_course(course, plan, tap)
    fin = wb.finished_course(settled, br.BROOK_DRAWN_W, [tap])
    assert br.level_runs_any_view(fin, plan.W, plan.H, br.reserved_box(settled, plan)) == []


def test_a_straight_skirt_is_bent_under_the_view_independent_bound() -> None:
    """water:W03 (plan D5), Kashikawa's shape: a skirt that follows one straight 900 ft margin. After the repair the
    straightest run on the canvas is within the bound every view is judged by, and three views pass the test's rule."""
    plan = a_plan()
    course = [
        (700.0, -300.0),
        (710.0, 100.0),
        (695.0, 250.0),
        TAP,
        (700.0, 330.0),
        (700.0, 370.0),
        (1040.0, 420.0),
        *[(1040.0 + 0.2 * k, 450.0 + 100.0 * k) for k in range(10)],
        (1060.0, 1500.0),
        (1100.0, 2900.0),
    ]
    fin = wb.finished_course(course, br.BROOK_DRAWN_W, [TAP])
    run, bound, _a, _b = br.ruled_excess(fin, plan.W, plan.H, br.reserved_box(course, plan))
    assert run > bound, "the constructed ruled run"
    settled = wb.settle_course(course, plan, TAP)
    fin = wb.finished_course(settled, br.BROOK_DRAWN_W, [TAP])
    run, bound, _a, _b = br.ruled_excess(fin, plan.W, plan.H, br.reserved_box(settled, plan))
    assert run <= bound
    for view in ((400.0, 400.0, 600.0, 600.0), (300.0, 250.0, 900.0, 900.0), (0.0, 0.0, plan.W, plan.H)):
        assert br.ruled_share_ok(fin, view)


def test_every_bearing_blocked_takes_the_route_round_the_field() -> None:
    """water:W06, the unreachable terminal made reachable: a lobe of the field over the tap blocks all fifteen approach
    bearings, and the last candidate walks round it - no vertex in the field, the tap still a vertex. The old terminal
    ran straight up the fall through the lobe."""
    plan = a_plan()
    plan.envelope = [(400.0, 1000.0), (400.0, 400.0), (450.0, 400.0), (450.0, 80.0), (950.0, 80.0), (950.0, 250.0), (480.0, 250.0), (480.0, 400.0), (1000.0, 400.0), (1000.0, 1000.0)]
    dx, dy = plan.fall
    base = math.degrees(math.atan2(-dy, -dx))
    assert all(wb.approach_legs(plan, TAP, math.radians(base + 10.0 * k), 420.0) is None for k in range(-7, 8)), "every bearing is blocked"
    course = wb.feed_brook(plan, TAP)
    assert TAP in course
    assert not br.course_enters(wb.finished_course(course, br.BROOK_DRAWN_W, [TAP]), [plan.envelope])


def test_the_source_is_off_the_canvas_however_wide_the_canvas() -> None:
    """water:W07: on a canvas wider than 420 ft to its edge the approach still starts off it."""
    plan = a_plan()
    plan.W, plan.H = 6000, 6000
    legs = wb.approach_legs(plan, TAP, math.radians(-90.0 + 70.0), 420.0)
    assert legs is not None and br.ends_off_canvas(legs, plan.W, plan.H, ends=(0,))
    course = wb.feed_brook(plan, TAP)
    assert "source" not in wb.brook_violations(course, plan, TAP)


def test_a_ditch_tail_on_the_brooks_flank_is_skirted_not_crossed() -> None:
    """water:W08: a collector end running 90 ft past the field on the brook's flank. The skirt as first laid crosses it
    mid-run; the placer lays it again round the ditches' outside stretches."""
    plan = a_plan()
    side = plan.brook_side
    px = -plan.fall[1] * side  # the flank's outward x (the fall is due south)
    edge = 1000.0 if px > 0 else 400.0
    tail = [(700.0, 700.0), (edge - px * 10.0, 700.0), (edge + px * 90.0, 705.0)]
    plan.net = {"channels": [{"pts": tail, "role": "drain", "w": 4.0}]}
    first = wb.finished_course([TAP, *_skirt_below(plan)], br.BROOK_DRAWN_W, [TAP])
    assert br.crosses_mid_run(first, tail), "the constructed crossing"
    course = wb.feed_brook(plan, TAP)
    assert not br.crosses_mid_run(wb.finished_course(course, br.BROOK_DRAWN_W, [TAP]), tail)
    assert wb.outside_stretches(plan, [tail]) == [[tail[1], tail[2]]]


def test_the_course_below_the_tap_runs_down_the_fall_past_a_margin_that_steps_back() -> None:
    """water:W11: a crop margin that steps back upslope (the fold case) still gets a course that never climbs."""
    plan = a_plan()
    step = [(1000.0, 600.0), (1150.0, 600.0), (1150.0, 700.0), (1000.0, 700.0)]
    course = wb.feed_brook(plan, TAP, crop=[step])
    fin = wb.finished_course(course, br.BROOK_DRAWN_W, [TAP])
    assert br.monotone_down(fin[br.tap_index(fin, [TAP]) :], plan.fall)
    assert "climbs" in wb.brook_violations([*course[: course.index(TAP) + 1], (700.0, 900.0), (700.0, 500.0), (700.0, 3000.0)], plan, TAP)


def test_the_weir_keys_into_the_bank_clear_of_the_race() -> None:
    """water:W09: a 9 ft race leaving at the offtake angle. The first seat below the mouth put the bar's bank end on the
    race; the bar steps down the brook to the first seat clear of it, the mouth still above the bar."""
    plan = a_plan()
    plan.intake = "weir"
    plan.brook = [(700.0, 100.0), TAP, (700.0, 600.0)]
    rx, ry = math.cos(math.radians(plan.head_deg)), math.sin(math.radians(plan.head_deg))
    race = [TAP, (TAP[0] + rx * 120.0, TAP[1] + ry * 120.0)]
    plan.net = {"channels": [{"pts": race, "role": "main", "w": 9.0}]}
    areas: list[float] = []
    real = br.bar_on_race

    def spy(bar, pts, w):  # type: ignore[no-untyped-def]
        areas.append(real(bar, pts, w))
        return areas[-1]

    s = Settlement(int(plan.W), int(plan.H))
    import unittest.mock as _mock

    with _mock.patch.object(wb, "bar_on_race", spy):
        hg.draw_intake(s, plan, TAP)
    assert areas[0] > 0.0, "the old seat lay on the race"
    ring = [(float(x), float(y)) for x, y in s.M["weirs"][0]["poly"]]
    assert br.bar_on_race(ring, race, 9.0) == 0.0
    assert min(q[1] for q in ring) > TAP[1], "below the mouth: the race draws from the pool the weir raises"


def test_the_violations_name_each_rule() -> None:
    plan = a_plan()
    bad = [(700.0, 100.0), (700.0, 200.0), TAP, (700.0, 300.0 + BROOK_TAP_RUN), (700.0, 700.0), (1300.0, 700.0), (1300.0, 3000.0)]
    names = wb.brook_violations(bad, plan, TAP, [[(1200.0, 600.0), (1200.0, 800.0)]])
    assert {"source", "enters", "crosses", "axis"} <= set(names)


def test_the_route_round_the_field_takes_the_intake_leg_and_the_shortest_way_round() -> None:
    """`around_the_field`: a start within an intake's length of the tap goes straight in; a tap the field closes round on
    every side has no course round it, and the straight course is handed to the placer's judgment."""
    env = [(400.0, 400.0), (1000.0, 400.0), (1000.0, 1000.0), (400.0, 1000.0)]
    assert wb.around_the_field(env, (700.0, 330.0), (700.0, 360.0)) == [(700.0, 330.0)]
    ring = [
        (0.0, 0.0),
        (2000.0, 0.0),
        (2000.0, 2000.0),
        (0.0, 2000.0),
        (0.0, 1000.0),
        (100.0, 1000.0),
        (100.0, 1900.0),
        (1900.0, 1900.0),
        (1900.0, 100.0),
        (100.0, 100.0),
        (100.0, 990.0),
        (0.0, 990.0),
    ]  # a slit too narrow for the brook's clearance: the tap inside is closed in
    assert wb.around_the_field(ring, (1000.0, -500.0), (1000.0, 1000.0)) == [(1000.0, -500.0)]
    path = wb.around_the_field(env, (700.0, -300.0), (700.0, 1100.0))
    assert path[0] == (700.0, -300.0) and len(path) >= 3 and not br.course_enters([*path, (700.0, 1100.0)], [env])


def test_a_level_run_no_leg_can_bend_is_left_for_the_judgment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Where no leg along a level run takes a bend (`bend_at` hands the course back), the repair stops rather than
    looping, and the placer's judgment refuses the candidate."""
    plan = a_plan()
    tap = (80.0, 300.0)
    course = [(0.0, -300.0), (50.0, 100.0), tap, (80.0, 330.0), (80.0, 370.0), *[(90.0 + 40.0 * k, 372.0) for k in range(7)], (600.0, 3000.0)]
    assert br.level_runs_any_view(course, plan.W, plan.H, br.reserved_box(course, plan)), "the constructed level run"
    calls: list[int] = []
    monkeypatch.setattr(wb, "bend_at", lambda c, *a: bool(calls.append(1)) or list(c))
    monkeypatch.setattr(wb, "ruled_excess", lambda *a: (0.0, 1.0, (0.0, 0.0), (0.0, 0.0)))  # the level loop alone
    assert wb.bend_runs(course, plan, tap, (0.0, 1.0)) == course and calls == [1]


def test_the_last_candidate_bows_a_clear_way_straight_up_the_fall(monkeypatch: pytest.MonkeyPatch) -> None:
    """Where every bearing is refused for a reason of its own and the way straight up the fall is clear of the field, the
    last candidate is that way bowed at its middle - a course with a leg dead on the fall's axis would be refused too."""
    plan = a_plan()
    monkeypatch.setattr(wb, "brook_violations", lambda *a: ["refused"])
    course = wb.feed_brook(plan, TAP)
    assert TAP in course and course[0][0] == pytest.approx(TAP[0])
    assert br.axis_segments(wb.finished_course(course, br.BROOK_DRAWN_W, [TAP]), [TAP]) == []
