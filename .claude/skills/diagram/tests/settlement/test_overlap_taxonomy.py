"""The overlap taxonomy's policy engine and its geometry helpers.

Feature 174: `overlap/taxonomy.py` sat at 61% with its whole policy layer untested - the function
that decides whether two features may lie on each other was exercised only through whole-map checks,
and feature 166 deleted the battery that ran them. These are pure functions of two strings or a
record dict, so they take direct tests.
"""

from __future__ import annotations

import json

import pytest

from l7r.diagram.overlap.matrix import (
    GridIndex,
    edge_dist,
    forest_reveal_x,
    matrix_extents,
    matrix_violations,
    poly_gap,
    polyline_len,
    torii_halfbox,
)
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
    seg_closest,
    seg_dist,
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


# ---- feature 174: the matrix module's index and its mirrored geometry ----------------------------


def test_the_grid_index_PRUNES_and_never_decides() -> None:
    """Its contract, in its own words: a query returns "a superset of the true neighbors, so the
    caller still runs its exact test - the index prunes, it never decides".

    Profiled 2026-07-25 after a feature spent an hour and the gate was suspected: `city_fan_heads_quilted`
    was testing ~3,000 sample points against every plot on the map, 14M segment-distance calls and
    ~58% of Tango's 17 s gate.

    The property that matters is the SUPERSET one, so it is asserted from both sides: everything
    near is returned, and something merely in the same cell is returned too (which is why the caller
    must still run the exact test).
    """
    idx = GridIndex(100.0)
    idx.add(0.0, 0.0, 10.0, 10.0, "corner")
    idx.add(90.0, 90.0, 95.0, 95.0, "same cell, far side")
    idx.add(5000.0, 5000.0, 5010.0, 5010.0, "elsewhere")

    got = idx.near(5.0, 5.0)
    assert "corner" in got, "the item at the query point is returned"
    assert "same cell, far side" in got, "and so is one merely sharing its cell - the caller decides"
    assert "elsewhere" not in got, "but a far item is pruned"


def test_an_item_spanning_cells_is_found_from_every_cell_it_touches() -> None:
    """ "Each item is inserted under every cell its influence bbox touches" - a long wall found only
    from its own corner would be an index that decides by omission."""
    idx = GridIndex(50.0)
    idx.add(0.0, 0.0, 500.0, 10.0, "a long wall")
    assert "a long wall" in idx.near(10.0, 5.0)
    assert "a long wall" in idx.near(480.0, 5.0), "found from the far end too"
    assert idx.near(10.0, 400.0) == [], "and not from a cell it never reaches"


def test_near_rect_returns_each_item_ONCE_however_many_cells_it_shares() -> None:
    """Its docstring's own promise. A duplicate would make any caller that COUNTS its results wrong,
    which is exactly the shape of the checks this index was built for."""
    idx = GridIndex(50.0)
    idx.add(0.0, 0.0, 500.0, 500.0, "one big thing")
    got = idx.near_rect(0.0, 0.0, 400.0, 400.0)
    assert got.count("one big thing") == 1, f"spans many cells, returned once: {got}"


def test_a_canvas_filling_forest_reveals_only_its_TREE_LINE_to_the_crop() -> None:
    """The crop rule: a wood is drawn to the canvas edge, but holding the frame open for identical
    crowns deeper in is wasted image - so only the tree line plus `reveal` px counts.

    `crop_hugs_content` gates how tight the crop is and must measure by exactly this rule, which is
    why the function exists rather than each caller doing its own thing.
    """
    forest = [(0.0, 0.0), (900.0, 0.0), (900.0, 900.0), (0.0, 900.0)]
    edge = [(300.0, 100.0), (320.0, 500.0)]
    xs = forest_reveal_x(forest, edge, 40.0, 1000.0)
    assert max(xs) == pytest.approx(360.0), "the tree line plus the reveal, not the canvas edge"
    assert max(forest_reveal_x(forest, [], 40.0, 1000.0)) == pytest.approx(900.0), "with no tree line, the wood's own extent"


def test_a_torii_halfbox_is_derived_from_the_SPAN_at_the_maps_scale() -> None:
    """It replaced a legacy fixed +/-19 px box - the pre-true-scale glyph, ~5x oversized. So the
    box must move with ftpx, which a fixed box could not do."""
    fine = torii_halfbox(1.0)
    coarse = torii_halfbox(2.0)
    assert fine[0] > coarse[0], "the same 16 ft arch is fewer pixels on a coarser map"
    assert fine[2] > fine[1], "and it reaches further DOWN than up - the glyph is not centered"


def test_poly_gap_is_zero_for_every_way_two_polygons_can_meet() -> None:
    """Overlap, containment and a bare edge crossing are three separate clauses, and a shape can
    meet another by the third with no vertex of either inside the other."""
    square = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    assert poly_gap(square, [(200.0, 0.0), (300.0, 0.0), (300.0, 100.0), (200.0, 100.0)]) == pytest.approx(100.0)
    assert poly_gap(square, [(50.0, 50.0), (150.0, 50.0), (150.0, 150.0), (50.0, 150.0)]) == 0.0, "overlapping"
    assert poly_gap(square, [(40.0, 40.0), (60.0, 40.0), (60.0, 60.0), (40.0, 60.0)]) == 0.0, "contained"
    assert poly_gap(square, [(-10.0, 40.0), (110.0, 40.0), (110.0, 60.0), (-10.0, 60.0)]) == 0.0, "a band crossing it"


def test_edge_dist_and_polyline_len() -> None:
    square = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
    assert edge_dist(5.0, 25.0, square) == pytest.approx(15.0), "to the nearest EDGE, inside or out"
    assert edge_dist(5.0, 5.0, square) == pytest.approx(5.0), "a point inside still measures to the wall"
    assert polyline_len([(0.0, 0.0), (3.0, 4.0), (3.0, 14.0)]) == pytest.approx(15.0)
    assert polyline_len([(1.0, 1.0)]) == 0.0, "a single point has no length"


def test_matrix_violations_reports_a_forbidden_overlap_and_says_WHERE() -> None:
    """Two SOLID features on the same ground is the case the whole matrix exists for. The answer
    carries the point, because a reader needs to find it on the sheet."""
    M = {
        "meta": {"W": 1000, "H": 1000},
        "houses": [{"x": 200.0, "y": 200.0, "w": 100.0, "h": 60.0, "rot": 0.0}],
        "storehouses": [{"x": 220.0, "y": 210.0, "w": 100.0, "h": 60.0, "rot": 0.0}],
    }
    bad = matrix_violations(M)
    assert bad, "two solids on the same ground is forbidden"
    ka, kb, x, y = bad[0]
    assert {ka, kb} == {"houses", "storehouses"}
    assert 150 < x < 300 and 150 < y < 300, f"and it says where to look: {(x, y)}"


def test_an_annex_may_lie_on_its_OWN_parent_and_only_its_own() -> None:
    """The conditional permission that cannot live in `matrix_policy`, because it depends on the two
    RECORDS rather than their classes: a garden belongs to a house, so it may lie on THAT house -
    and on no other. Both halves asserted, since the permission is worthless if it is unconditional.

    The parent is carried in the key `_MATRIX_PARENT_FIELD` names for that record type - `of` for a
    garden - not in a generic "parent". A test using the wrong spelling gets `parent_id = None` and
    silently exercises the FORBIDDEN path while claiming to test the permitted one.
    """
    house = {"x": 200.0, "y": 200.0, "w": 100.0, "h": 60.0, "rot": 0.0}
    stranger = {"x": 600.0, "y": 600.0, "w": 100.0, "h": 60.0, "rot": 0.0}

    own = {
        "meta": {"W": 1000, "H": 1000},
        "houses": [house],
        "gardens": [{"x": 210.0, "y": 205.0, "w": 40.0, "h": 30.0, "rot": 0.0, "of": [200.0, 200.0]}],
    }
    assert matrix_violations(own) == [], "a garden on its own house is by design"

    foreign = {
        "meta": {"W": 1000, "H": 1000},
        "houses": [house, stranger],
        "gardens": [{"x": 210.0, "y": 205.0, "w": 40.0, "h": 30.0, "rot": 0.0, "of": [600.0, 600.0]}],
    }
    assert matrix_violations(foreign), "...but a garden on SOMEONE ELSE's house is a defect"


def test_matrix_extents_reads_a_records_DRAWN_extent() -> None:
    """The distinction the gate test's own header calls out: drawn extents, not recorded envelopes.
    A record carrying `vw`/`vh` is measured by the ink a reader sees."""
    M = {"meta": {"W": 1000, "H": 1000}, "houses": [{"x": 100.0, "y": 100.0, "w": 200.0, "h": 100.0, "rot": 0.0, "vw": 20.0, "vh": 10.0}]}
    ext = matrix_extents(M)
    assert ext, "the house is extracted"
    poly = ext[0][1]
    assert max(p[0] for p in poly) - min(p[0] for p in poly) == pytest.approx(20.0), "the DRAWN width, not the recorded one"


def test_matrix_extents_extracts_each_feature_family_in_ITS_OWN_vocabulary() -> None:
    """Feature 174. `matrix_extents` is a dispatch over how each key records its shape, and a family
    it cannot read is INVISIBLE to the matrix in both directions - the recurring trap this file's
    own docstrings record. Four shapes, four branches, all asserted here:

      - a WARD is a fence LINE, stroked at a hair's width (2.5), because a fence is thin and a
        generous stroke "would manufacture defects out of houses that merely front it";
      - a KIDO records `parts`, and its GUARD BOX is separated out under its own key so it excuses
        nothing but its own glyph;
      - a TORII is a glyph box derived from the span at the map's scale (`torii_halfbox`);
      - a LINEAR feature (road, moat, ring road, wall, lane) is stroked at its recorded width.
    """
    M = {
        "meta": {"W": 2000, "H": 2000, "ftpx": 1},
        "wards": [{"name": "n", "boundary": [(100.0, 100.0), (500.0, 100.0), (500.0, 400.0)]}],
        "torii": [(800.0, 800.0)],
        "road": [(0.0, 1200.0), (2000.0, 1200.0)],
        "road_width": 30.0,
    }
    got = {k for k, _p, _i, _pa in matrix_extents(M)}
    assert "wards" in got, "a ward's fence line is extracted"
    assert "torii" in got, "an arch's glyph box is extracted"
    assert "road" in got, "and a road is stroked at its recorded width"

    road_quads = [p for k, p, _i, _pa in matrix_extents(M) if k == "road"]
    spread = max(q[1] for quad in road_quads for q in quad) - min(q[1] for quad in road_quads for q in quad)
    assert spread == pytest.approx(30.0), "the road's full width, from its half-width stroke"


def test_a_kido_GUARD_BOX_is_extracted_under_its_own_key() -> None:
    """ "so it excuses nothing but its own glyph" - the guard box is a separate feature for the
    matrix's purposes, and giving it the kido's key would let it inherit the kido's permissions."""
    guard = [(500.0, 500.0), (520.0, 500.0), (520.0, 520.0), (500.0, 520.0)]
    other = [(600.0, 500.0), (640.0, 500.0), (640.0, 508.0), (600.0, 508.0)]
    M = {"meta": {"W": 2000, "H": 2000, "ftpx": 1}, "kido": [{"x": 510.0, "y": 510.0, "guard": guard, "parts": [guard, other]}]}
    keys = [k for k, _p, _i, _pa in matrix_extents(M)]
    assert "kido_guard_box" in keys, "the guard box is its own feature"
    assert "kido" in keys, "and the bar itself is still the kido"


def test_a_feature_wholly_off_the_canvas_meets_nothing() -> None:
    """The index box is clamped to the canvas, so a record drawn entirely outside it collapses to an
    empty box - and nothing on the map can meet it. Without the skip it would be indexed at a
    degenerate box and compared against everything."""
    M = {
        "meta": {"W": 1000, "H": 1000},
        "houses": [{"x": 500.0, "y": 500.0, "w": 40.0, "h": 30.0, "rot": 0.0}],
        "storehouses": [{"x": -5000.0, "y": -5000.0, "w": 40.0, "h": 30.0, "rot": 0.0}],
    }
    assert matrix_violations(M) == [], "the off-canvas record accuses nobody"


def test_two_annexes_of_ONE_household_may_abut_and_two_of_different_ones_may_not() -> None:
    """The second conditional permission that cannot live in `matrix_policy` (gardens/gardens is
    FORBIDDEN there - asserted below, because the permission would be vacuous if the class pair
    already allowed it). A household's shed and its garden crowd each other inside one yard; two
    households' do not, because that is a boundary being crossed."""
    assert matrix_policy("gardens", "gardens") is None, "the CLASS pair is forbidden - the permission is per-record"
    house = {"x": 200.0, "y": 200.0, "w": 100.0, "h": 60.0, "rot": 0.0}
    neighbor = {"x": 600.0, "y": 600.0, "w": 100.0, "h": 60.0, "rot": 0.0}
    a = {"x": 230.0, "y": 205.0, "w": 40.0, "h": 30.0, "rot": 0.0, "of": [200.0, 200.0]}

    one = {"meta": {"W": 1000, "H": 1000}, "houses": [house], "gardens": [a, {**a, "x": 240.0}]}
    assert matrix_violations(one) == [], "one household's two annexes may abut"

    two = {"meta": {"W": 1000, "H": 1000}, "houses": [house, neighbor], "gardens": [a, {**a, "x": 240.0, "of": [600.0, 600.0]}]}
    assert ("gardens", "gardens") in {(ka, kb) for ka, kb, _x, _y in matrix_violations(two)}, "two households' may not"


def test_a_PRIVATE_well_stands_inside_its_own_court_and_a_public_one_does_not() -> None:
    """A trade work's own well is sunk in its court, so it lies on the work that owns it; a well on
    the common ground is a well in the middle of somebody's building. The `private` flag is the
    whole difference, so both halves are asserted from the same geometry."""
    house = {"x": 200.0, "y": 200.0, "w": 100.0, "h": 60.0, "rot": 0.0}
    on_the_house = {"x": 210.0, "y": 205.0}
    assert matrix_violations({"meta": {"W": 1000, "H": 1000}, "houses": [house], "wells": [{**on_the_house, "private": True}]}) == []
    assert matrix_violations({"meta": {"W": 1000, "H": 1000}, "houses": [house], "wells": [on_the_house]}), "a public well may not"


def test_a_DEGENERATE_segment_is_its_own_closest_point() -> None:
    """`seg_closest` divides by the segment's squared length, so a segment whose two ends coincide -
    a way pinched to one point by an earlier pass - would raise. It answers the point itself."""
    assert seg_closest(50.0, 90.0, (10.0, 10.0), (10.0, 10.0)) == (10.0, 10.0)
    assert seg_dist(13.0, 14.0, (10.0, 10.0), (10.0, 10.0)) == pytest.approx(5.0)
