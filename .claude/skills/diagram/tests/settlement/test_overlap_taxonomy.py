"""The overlap taxonomy's policy engine and its geometry helpers.

Feature 174: `overlap/taxonomy.py` sat at 61% with its whole policy layer untested - the function
that decides whether two features may lie on each other was exercised only through whole-map checks,
and feature 166 deleted the battery that ran them. These are pure functions of two strings or a
record dict, so they take direct tests.
"""

from __future__ import annotations

import json
import math

import pytest

from l7r.diagram.overlap.taxonomy import (
    OVERLAP_CLASS,
    _box_hits_poly,
    _mx_rect,
    _mx_same,
    _mx_stroke,
    load,
    matrix_policy,
    poly_area,
    poly_dist,
    seg_intersect,
    segments_cross,
)


def test_two_SOLID_features_may_never_overlap_and_the_answer_is_None() -> None:
    """None is FORBIDDEN. Two buildings cannot occupy the same ground, and the taxonomy says so
    without needing a reason string."""
    assert matrix_policy("houses", "terraces") is None


def test_an_UNCLASSIFIED_key_abstains_rather_than_permitting_or_forbidding() -> None:
    """A key nobody has classified must not silently become "allowed" - it is reported by the
    ratchet check instead, which is the mechanism that stops a new feature type from being invisible
    to the matrix in both directions."""
    assert matrix_policy("a_key_nobody_registered", "houses") == "unclassified"
    assert matrix_policy("houses", "a_key_nobody_registered") == "unclassified"


def test_a_FIXTURE_may_overlap_only_what_it_declares_itself_mounted_on() -> None:
    """A bridge sits on the water it spans BY DESIGN, and says so; the permission is not a blanket
    class. The reason string is the record of why, which is what a reader of the interactive map
    eventually sees."""
    why = matrix_policy("bridges", "streams")
    assert why and "mounted on" in why, why
    assert matrix_policy("streams", "bridges") == why, "the answer cannot depend on argument order"


def test_ANNEX_x_ANNEX_resolves_to_None_ON_PURPOSE() -> None:
    """Its docstring's own case: the permission is conditional on a SHARED PARENT, which only the
    caller can test - so the matrix abstains rather than guessing. A garden may lie on ITS OWN
    house's threshing yard, not on any threshing yard."""
    assert matrix_policy("gardens", "threshing_yards") is None


def test_mx_same_matches_a_parent_reference_across_INDEPENDENT_ROUNDING() -> None:
    """A parent is stored as a rounded coordinate pair and the child's own id is rounded separately,
    so exact equality would miss real parents. The tolerance is 1.5 px - asserted on both sides of
    it, since a tolerance tested only from inside is a tolerance that could be infinite."""
    assert _mx_same([100.0, 200.0], [100.4, 200.4]) is True, "the same parent, rounded twice"
    assert _mx_same([100.0, 200.0], [104.0, 200.0]) is False, "a different parent"
    assert _mx_same(None, [1.0, 2.0]) is False and _mx_same([1.0, 2.0], None) is False
    assert _mx_same("headman", "headman") is True, "a non-coordinate id compares exactly"


def test_mx_rect_reads_the_DRAWN_box_and_turns_with_the_record() -> None:
    """`vw`/`vh` where a marker draws above its true size - the ink is what a reader sees."""
    plain = _mx_rect({"x": 0.0, "y": 0.0, "w": 100.0, "h": 50.0})
    assert max(p[0] for p in plain) == pytest.approx(50.0)

    drawn = _mx_rect({"x": 0.0, "y": 0.0, "w": 100.0, "h": 50.0, "vw": 20.0, "vh": 10.0})
    assert max(p[0] for p in drawn) == pytest.approx(10.0), "the drawn box wins over the true one"

    turned = _mx_rect({"x": 0.0, "y": 0.0, "w": 100.0, "h": 50.0, "rot": 90.0})
    assert max(p[1] for p in turned) == pytest.approx(50.0), "a quarter turn puts the long axis on y"


def test_mx_stroke_uses_the_TRUE_half_width_never_the_ink_width() -> None:
    """ "a hairline stroke floor draws a 1 ft ditch 4 px wide and that slop must not manufacture a
    defect" - so a linear feature's quads are built at what it IS, not at what it is drawn as."""
    quads = _mx_stroke([(0.0, 0.0), (100.0, 0.0), (100.0, 100.0)], 5.0)
    assert len(quads) == 2, "one quad per segment"
    ys = [p[1] for p in quads[0]]
    assert max(ys) - min(ys) == pytest.approx(10.0), "the full width is twice the half-width given"
    assert _mx_stroke([(0.0, 0.0)], 5.0) == [], "a single point is no segment at all"


def test_box_hits_poly_catches_all_three_ways_a_box_can_touch_a_polygon() -> None:
    """Corner-in, vertex-in, and edge-cross are three separate clauses, and a box can hit by any one
    of them alone - a cross-shaped overlap has no corner or vertex inside the other."""
    diamond = [(50.0, 0.0), (100.0, 50.0), (50.0, 100.0), (0.0, 50.0)]
    assert _box_hits_poly((40.0, 40.0, 60.0, 60.0), diamond), "the box's corners lie inside"
    assert _box_hits_poly((-10.0, -10.0, 200.0, 200.0), diamond), "the polygon's vertices lie inside"
    assert _box_hits_poly((-10.0, 45.0, 200.0, 55.0), diamond), "a band crossing it: no corner or vertex inside either"
    assert not _box_hits_poly((500.0, 500.0, 510.0, 510.0), diamond), "and a box well clear is clear"


def test_poly_area_is_the_shoelace_and_is_never_signed() -> None:
    """Winding order must not decide an area - a ring recorded clockwise is the same field."""
    ccw = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
    assert poly_area(ccw) == pytest.approx(100.0)
    assert poly_area(list(reversed(ccw))) == pytest.approx(100.0), "the same ring, wound the other way"


def test_poly_dist_and_the_segment_predicates() -> None:
    square = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
    assert poly_dist(5.0, 20.0, square) == pytest.approx(10.0), "to the nearest EDGE"
    assert poly_dist(5.0, 5.0, square) == 0.0, "a point inside is at zero"

    assert segments_cross((0.0, 0.0), (10.0, 0.0), (5.0, -5.0), (5.0, 5.0)) is True
    assert segments_cross((0.0, 0.0), (10.0, 0.0), (0.0, 5.0), (10.0, 5.0)) is False, "parallel lines never meet"

    hit = seg_intersect((0.0, 0.0), (10.0, 0.0), (5.0, -5.0), (5.0, 5.0))
    assert hit is not None and hit[0] == pytest.approx(5.0) and hit[1] == pytest.approx(0.0)
    assert seg_intersect((0.0, 0.0), (10.0, 0.0), (0.0, 5.0), (10.0, 5.0)) is None


def test_load_reads_a_manifest_from_disk(tmp_path) -> None:
    """The module's one I/O function, used by every audit that reads a finished map."""
    p = tmp_path / "m.json"
    p.write_text(json.dumps({"houses": [{"x": 1, "y": 2}]}))
    assert load(str(p))["houses"][0]["x"] == 1


def test_every_class_in_the_taxonomy_is_one_the_policy_engine_can_decide() -> None:
    """A guard rather than a coverage test. A class added to `OVERLAP_CLASS` with no branch in
    `matrix_policy` would make every pair involving it abstain silently, which reads exactly like a
    permission. The roster is DERIVED from the registry, so this pins the count rather than a
    hand-written list - and a new class trips it, which is the point.
    """
    classes = sorted(set(OVERLAP_CLASS.values()))
    assert classes == ['ANNEX', 'BARRIER', 'COVER', 'FIXTURE', 'GROUND', 'OVERLAY', 'PADDY_RECONSTRUCTED', 'RECORD', 'RING_ROAD', 'SOLID', 'VEGETATION', 'WATER', 'WAY'], (
        "a new overlap class needs a matrix_policy branch (and this line updated)"
    )
    for cls in classes:
        key = next(k for k, v in OVERLAP_CLASS.items() if v == cls)
        assert matrix_policy(key, "houses") != "unclassified", f"{cls} is classified, so it must not abstain"
