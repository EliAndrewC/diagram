"""The brook's placer guarantees (feature 287, water:W01-W04, W06-W09, W11): one engine predicate per rule, and the placer
tested on constructed inputs that include the violating case (FR-004)."""

import math
import random

import pytest

from l7r.diagram.hamletgen.consts import BROOK_TAP_RUN
from l7r.diagram.hamletgen.water import brook as wb
from l7r.diagram.hamletgen.water import brook_rules as br

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


# ---- the predicates ----------------------------------------------------------------------------------


def test_the_turn_is_read_once_and_a_zero_leg_turns_nothing() -> None:
    assert br.turn_deg((0.0, 0.0), (10.0, 0.0), (20.0, 0.0)) == pytest.approx(0.0)
    assert br.turn_deg((0.0, 0.0), (10.0, 0.0), (10.0, 10.0)) == pytest.approx(90.0)
    assert br.turn_deg((0.0, 0.0), (0.0, 0.0), (5.0, 5.0)) == 0.0
    assert br.max_turn_deg([(0.0, 0.0), (100.0, 0.0), (40.0, -20.0)]) > 150.0
    assert br.max_turn_deg([(0.0, 0.0), (1.0, 1.0)]) == 0.0


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


def test_the_ruled_run_is_judged_inside_the_view_against_ten_widths() -> None:
    """water:W03 (feature 444 T16, against 0054): no straight run past ten of the brook's drawn widths in view."""
    assert pytest.approx(10 * br.BROOK_DRAWN_W) == br.RULED_MAX_FT
    line = [(float(k * 10), 500.0) for k in range(101)]  # 1,000 ft dead straight
    assert not br.ruled_run_ok(line, (0.0, 0.0, 2000.0, 1000.0))
    assert br.ruled_run_ok(line, (0.0, 0.0, br.RULED_MAX_FT - 1.0, 1000.0)), "a run cut short by the view is judged as it shows"
    wavy = [(float(k * 20), 500.0 + (8.0 if k % 2 else 0.0)) for k in range(51)]
    assert br.ruled_run_ok(wavy, (0.0, 0.0, 2000.0, 1000.0))
    run, most, _a, _b = br.ruled_excess(line, 2000.0, 1000.0, (0.0, 0.0, 10.0, 10.0))
    assert run == pytest.approx(1000.0) and most == br.RULED_MAX_FT


def test_the_axis_rule_exempts_the_tap_run_and_short_chords_only() -> None:
    """water:W04 (named by the GM): a segment of a wander stride or more within 1.6 degrees of an axis is found; the two
    segments leaving the tap are the tap run and exempt; a chord under the stride is a curve's, not a run."""
    course = [(0.0, 0.0), (0.0, 100.0), (0.0, 170.0), (40.0, 260.0), (40.0, 400.0), (42.0, 405.0)]
    assert br.axis_segments(course, [(0.0, 100.0)]) == [0, 3]
    assert br.axis_segments(course, [(0.0, 0.0)]) == [3]
    assert br.tap_index(course, []) == 0, "no head race: the pool test's default"


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


# ---- the placer on constructed sites, violating case included -------------------------------------------------


def test_the_violations_name_each_rule() -> None:
    plan = a_plan()
    bad = [(700.0, 100.0), (700.0, 200.0), TAP, (700.0, 300.0 + BROOK_TAP_RUN), (700.0, 700.0), (1300.0, 700.0), (1300.0, 3000.0)]
    names = wb.brook_violations(bad, plan, TAP, [[(1200.0, 600.0), (1200.0, 800.0)]])
    assert {"source", "enters", "crosses", "axis"} <= set(names)


def test_a_straight_mid_leg_confluence_is_not_read_as_a_ruled_run() -> None:
    """Feature 302 (water:W03): a confluence held mid-leg adds a vertex on a straight line - it changes no stroke drawn, but the
    ruled rule's chord test, which leaves one straight leg alone, counted the leg as a three-vertex run. The rule reads the drawn
    course without such a vertex; a join on a bend, or off the line, is kept."""
    from l7r.diagram.hamletgen.water.brook_rules import without_straight_joins

    fin = [(0.0, 0.0), (100.0, 0.0), (300.0, 0.0), (300.0, 200.0)]
    assert without_straight_joins(fin, [(100.0, 0.0)], 1.0) == [(0.0, 0.0), (300.0, 0.0), (300.0, 200.0)], "the collinear join dropped"
    assert without_straight_joins(fin, [(300.0, 0.0)], 1.0) == fin, "a join on the bend is kept"
    assert without_straight_joins(fin, [], 1.0) == fin, "no join: the course as drawn"
    assert without_straight_joins(fin[:1], [(0.0, 0.0)], 1.0) == fin[:1] and without_straight_joins([], [], 1.0) == []
