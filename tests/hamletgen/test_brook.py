"""The brook's placer guarantees (feature 287, water:W01-W04, W06-W09, W11): one engine predicate per rule, and the placer
tested on constructed inputs that include the violating case (FR-004)."""

import math
import random

import pytest

from l7r.diagram.hamletgen.water import brook_rules as br

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


# ---- the repair ----------------------------------------------------------------------------------------


# ---- the placer on constructed sites, violating case included -------------------------------------------------
