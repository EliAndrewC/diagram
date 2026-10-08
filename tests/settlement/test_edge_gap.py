"""`edge_gap` and its neighbors - the ONE measurement any gap verdict uses.

WHY THIS FILE EXISTS (feature 174). `overlap/taxonomy.py` was 62% covered and `edge_gap` had no
unit test at all, despite being the most heavily documented rule in the engine and despite its
docstring recording THREE shipped defects that came from approximating it (an execution ground and a
boundary stone both sited inside the line they were supposed to be outside of). The rule was carried
entirely by whole-map checks; this file asserts it directly, in the arithmetic a reader can verify.

The project's rule, from CLAUDE.md: "Gap verdicts read footprints, never centers."
"""

from __future__ import annotations

import math

import pytest

from l7r.diagram.overlap.taxonomy import _gap_disc, _gap_reach, edge_gap, within_edge_gap


def _rect(x, y, w, h, rot=0.0):
    return {"x": x, "y": y, "w": w, "h": h, "rot": rot}


def test_the_gap_between_two_rects_is_the_distance_between_their_EDGES() -> None:
    """The whole point: 200 px apart at the centers, 100 px of building between them, so the gap a
    person could measure on the ground is 100 - not the 200 a center-to-center rule would report."""
    a = _rect(0.0, 0.0, 100.0, 40.0)
    b = _rect(200.0, 0.0, 100.0, 40.0)
    assert edge_gap(a, b) == pytest.approx(100.0)
    assert math.hypot(a["x"] - b["x"], a["y"] - b["y"]) == 200.0, "which is NOT the answer"


def test_two_footprints_that_touch_or_overlap_have_a_gap_of_ZERO_never_negative() -> None:
    """A negative gap would make "at least N apart" pass by arithmetic on an overlap."""
    a = _rect(0.0, 0.0, 100.0, 100.0)
    assert edge_gap(a, _rect(100.0, 0.0, 100.0, 100.0)) == 0.0, "edge to edge"
    assert edge_gap(a, _rect(50.0, 0.0, 100.0, 100.0)) == 0.0, "overlapping"
    assert edge_gap(a, _rect(0.0, 0.0, 20.0, 20.0)) == 0.0, "one wholly inside the other"


def test_the_HALF_DIAGONAL_approximation_the_docstring_rejects_would_give_a_different_answer() -> None:
    """The recorded error: the circumscribed radius exceeds the true half-extent by up to 41% on a
    square. Asserted as a real difference on a real pair, so this test fails if anyone re-introduces
    the approximation - which is the failure the docstring says shipped twice."""
    a = _rect(0.0, 0.0, 100.0, 100.0)
    b = _rect(300.0, 0.0, 100.0, 100.0)
    true_gap = edge_gap(a, b)
    half_diagonal = 0.5 * math.hypot(100.0, 100.0)
    approximation = 300.0 - 2 * half_diagonal
    assert true_gap == pytest.approx(200.0)
    assert approximation < true_gap - 40.0, "the half-diagonal understates the clearance by ~41 px here"


def test_a_ROTATED_footprint_is_measured_at_its_true_extent() -> None:
    """A square turned 45 degrees reaches further along the axis between the two, so the gap SHRINKS
    - which a rule reading w/h alone would miss entirely."""
    a = _rect(0.0, 0.0, 100.0, 100.0)
    far = _rect(300.0, 0.0, 100.0, 100.0)
    turned = _rect(300.0, 0.0, 100.0, 100.0, rot=45.0)
    assert edge_gap(a, turned) < edge_gap(a, far), "the corner now points at its neighbor"


def test_a_WELLHEAD_is_a_disc_and_measuring_it_as_a_rect_used_to_RAISE() -> None:
    """The 2026-07-27 case its docstring records: a wellhead records `r`/`vr` and NO w/h, so
    treating every feature as a rect raised KeyError - and a crashing gate prints no FAIL lines, so
    a pool scan grepping for FAIL read the crash as CLEAN.

    Disc-to-disc, disc-to-rect and rect-to-disc are all asserted, because they are three branches.
    """
    well = {"x": 0.0, "y": 0.0, "r": 20.0}
    other_well = {"x": 100.0, "y": 0.0, "r": 30.0}
    assert edge_gap(well, other_well) == pytest.approx(50.0), "100 apart, minus both radii"

    rect = _rect(200.0, 0.0, 100.0, 100.0)
    assert edge_gap(well, rect) == pytest.approx(130.0), "disc to rect: 150 to the near face, minus 20"
    assert edge_gap(rect, well) == pytest.approx(130.0), "and the same measured the other way round"


def test_a_wellhead_is_measured_by_its_DRAWN_head_not_its_clearance_ring() -> None:
    """`vr` over `r`, for the reason `_struct_rect` prefers vw/vh: a clearance rule is about the INK
    on the map, and the drawn head is what a reader sees."""
    assert _gap_disc({"x": 0.0, "y": 0.0, "r": 40.0, "vr": 10.0}) == (0.0, 0.0, 10.0)
    assert _gap_disc({"x": 0.0, "y": 0.0, "r": 40.0}) == (0.0, 0.0, 40.0), "and falls back to r when there is no drawn head"
    assert _gap_disc(_rect(0.0, 0.0, 10.0, 10.0)) is None, "anything with a w is a rect, not a disc"


def test_within_edge_gap_prefilters_GENEROUSLY_so_the_exact_test_decides() -> None:
    """The index-prunes-never-decides rule applied to a pair test: over-estimating an extent can
    only admit a pair the exact test then rejects, never exclude one it would have accepted.

    So a pair the prefilter admits may still be refused - asserted here on a pair whose centers are
    within the limit plus the circumscribed radii, but whose true gap is not.
    """
    a = _rect(0.0, 0.0, 100.0, 100.0)
    b = _rect(300.0, 0.0, 100.0, 100.0)
    assert edge_gap(a, b) == pytest.approx(200.0)
    assert within_edge_gap(a, b, 250.0) is True, "inside the limit"
    assert within_edge_gap(a, b, 150.0) is False, "outside it - and the exact test, not the prefilter, said so"
    assert within_edge_gap(a, _rect(5000.0, 0.0, 10.0, 10.0), 50.0) is False, "the prefilter rejects the far pair cheaply"


def test_gap_reach_uses_the_drawn_extent_where_a_feature_has_one() -> None:
    """`vw`/`vh` over `w`/`h`, the same ink-not-clearance rule as `_gap_disc`."""
    assert _gap_reach({"x": 0.0, "y": 0.0, "w": 100.0, "h": 0.0}) == pytest.approx(50.0)
    assert _gap_reach({"x": 0.0, "y": 0.0, "w": 100.0, "h": 0.0, "vw": 20.0, "vh": 0.0}) == pytest.approx(10.0)
    assert _gap_reach({"x": 0.0, "y": 0.0, "r": 15.0}) == 15.0, "a disc's reach is its radius"
