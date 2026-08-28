"""Split from test_checks.py by feature 025 - see tests/check_village/CLAUDE.md for the index."""

import json
import pathlib

import pytest

from l7r.diagram import check_village, settlement
from tests.check_village._builders import (
    _CAP_GOV_CHECKS,
    _POND_OUTLIER,
    _cap_gov,
    _feature_022_manifest,
    _tv,
    bldg,
    bstone,
    exground,
    f,
    garden,
    grove,
    house,
    manifest,
    pspot,
    vgrove,
    well,
    yard,
)


def test_fixture_builders_survive_every_check():
    """The builders above must produce records EVERY check can read without a KeyError - that is
    the whole point of them. If a check starts indexing a new required key, this fails here once
    instead of ambushing the next person who writes a test."""
    M = manifest(
        houses=[house(300, 300)],
        buildings=[bldg(600, 600)],
        threshing_yards=[yard(300, 340, of=(300, 300))],
        gardens=[garden(340, 300, of=(300, 300))],
        wells=[well(500, 500)],
        groves=[grove(260, 260, of=(300, 300))],
        village_groves=[vgrove([(700, 700), (800, 700), (800, 800), (700, 800)])],
        tree_crowns=[900, 900, 6],
        punishment_spots=[pspot(400, 500)],
        execution_grounds=[exground(880, 200)],
        boundary_markers=[bstone(700, 350)],
    )
    f(M)  # must not raise; which checks FAIL is irrelevant here - only that they all ran


# ---- module-level helper branches (direct calls) ------------------------------------------
def test_helper_edge_branches():
    cv = check_village
    assert cv.sat_overlap([(0, 0), (10, 0), (10, 10), (0, 10)], [(5, 5), (15, 5), (15, 15), (5, 15)])
    assert not cv.sat_overlap([(0, 0), (10, 0), (10, 10), (0, 10)], [(20, 20), (30, 20), (30, 30), (20, 30)])
    assert cv.seg_closest(0, 0, (5, 5), (5, 5)) == (5, 5)  # degenerate (zero-length) segment
    assert cv.unit_dir(None) is None  # no slope declared
    assert cv.unit_dir("nonsense") is None  # unknown cardinal name
    assert cv.unit_dir([3, 4]) == (0.6, 0.8)  # raw vector, normalized
    assert cv.poly_dist(5, 5, [(0, 0), (10, 0), (10, 10), (0, 10)]) == 0.0  # point inside the polygon


def test_gate_crop_advisory_is_soft_not_a_failure():
    fails = check_village.gate(_POND_OUTLIER, verbose=True)  # prints the ADVISORY line but must NOT gate the map
    assert "crop_could_tighten" not in fails


def test_seg_intersect_returns_point_for_a_crossing_and_none_for_parallel():
    # the geometry helper that bridges() uses to find the crossing point
    p = settlement.seg_intersect((0, 0), (10, 0), (5, -5), (5, 5))
    assert p == (5.0, 0.0)
    assert settlement.seg_intersect((0, 0), (10, 0), (0, 4), (10, 4)) is None  # parallel - no crossing
    assert settlement.segments_cross((0, 0), (10, 0), (5, -5), (5, 5))
    assert not settlement.segments_cross((0, 0), (10, 0), (0, 4), (10, 4))


def test_mausoleum_draws_with_either_gate_orientation():
    # exercises both the horizontal-wall (south) and vertical-wall (west) gate branches + the default
    # (above) label position
    s = settlement.Settlement()
    s.mausoleum(900, 900, 120, 90, label="Mausoleum", gate_dir="south")
    s.mausoleum(600, 600, 120, 90, gate_dir="west")
    assert len(s.M["mausoleums"]) == 2


def test_twin_axes_geometric_fallbacks_no_meta_knobs():
    ax = check_village.twin_axes(_tv(meta={"name": "G"}))
    assert ax["cluster_region"] == "W"  # cluster sits W of the field center
    assert ax["cluster_shape"] == "tall"  # bbox 60 wide x 140 tall -> r < 0.7
    assert ax["headman_side"] == "N"  # headman N of the cluster centroid
    assert ax["water_source"] == "NW"  # pond NW of the field center
    assert ax["lane_skeleton"] is None  # no declared knob, no geometric fallback
    assert ax["focal_set"] == frozenset()
    assert isinstance(ax["grain_orient"], int)


def test_twin_axes_round_cluster_center_headman_and_dir8_deadzone():
    # a square cluster CENTERED on the field center: round shape, headman AT the centroid (center),
    # and cluster_region hits _dir8's zero-vector dead zone -> None
    houses = [
        {"x": 300, "y": 300, "role": "plain"},
        {"x": 400, "y": 300, "role": "plain"},
        {"x": 300, "y": 400, "role": "plain"},
        {"x": 400, "y": 400, "role": "plain"},
        {"x": 350, "y": 350, "role": "headman"},
    ]
    ax = check_village.twin_axes({"meta": {"name": "R", "down_deg": 45}, "houses": houses, "fields": [{"bbox": [0, 0, 700, 700]}]})
    assert ax["cluster_shape"] == "round"  # w == h
    assert ax["headman_side"] == "center"  # headman at the cluster center
    assert ax["cluster_region"] is None  # centroid == field center -> dead zone
    assert ax["water_source"] is None and ax["grain_orient"] is None  # no pond, no dry_plots


def test_twin_axes_wide_cluster_and_bare_manifest():
    wide = [{"x": 100, "y": 300, "role": "plain"}, {"x": 500, "y": 300, "role": "plain"}, {"x": 300, "y": 320, "role": "plain"}]
    axw = check_village.twin_axes({"meta": {"name": "W", "down_deg": 45}, "houses": wide, "fields": [{"bbox": [0, 0, 700, 700]}]})
    assert axw["cluster_shape"] == "wide"  # 400 wide x 20 tall -> r > 1.4
    # a bare manifest: every geometric axis is 'no evidence'
    ax = check_village.twin_axes({"meta": {"name": "bare", "down_deg": 45}})
    assert ax["cluster_region"] is None and ax["cluster_shape"] is None and ax["headman_side"] is None
    assert ax["water_source"] is None and ax["grain_orient"] is None and ax["focal_set"] == frozenset()


def test_twin_axes_pond_layout_distinguishes_mosaic_from_grid():
    # GM 2026-07-22: a mosaic dike-pond (桑基魚塘) and a surveyed grid polder (圩田) of the same water
    # direction are different KINDS of place; pond_layout is a twin axis so the detector counts the difference.
    assert "pond_layout" in check_village.TWIN_AXES
    assert check_village.twin_axes({"meta": {"name": "G", "down_deg": 45}})["pond_layout"] == "grid"  # default
    assert check_village.twin_axes({"meta": {"name": "M", "down_deg": 45, "pond_layout": "mosaic"}})["pond_layout"] == "mosaic"
    grid = check_village.twin_axes({"meta": {"name": "G", "down_deg": 45, "field_archetype": "polder_grid"}})
    mosaic = check_village.twin_axes({"meta": {"name": "M", "down_deg": 45, "pond_layout": "mosaic"}})
    assert check_village.twin_diff_count(grid, mosaic) >= 1  # they differ on at least the pond_layout axis


def test_twin_settlement_form_is_an_axis():
    # nucleated blob vs linear ribbon - the biggest structural read - is a twin-detector axis; it defaults
    # to 'nucleated' when a map does not declare it (so an undeclared map is not spuriously "different")
    assert "settlement_form" in check_village.TWIN_AXES
    a = _tv(meta={"name": "A", "settlement_form": "nucleated"})
    b = _tv(meta={"name": "B", "settlement_form": "linear"})
    ax, bx = check_village.twin_axes(a), check_village.twin_axes(b)
    assert ax["settlement_form"] == "nucleated" and bx["settlement_form"] == "linear"
    assert check_village.twin_axes(_tv(meta={"name": "C"}))["settlement_form"] == "nucleated"  # default
    assert check_village.twin_diff_count(ax, bx) == 1  # differ on settlement_form alone (otherwise identical)


def test_convex_hull_degenerate_point_clouds():
    """The hull helper returns <3 unique points as-is (a degenerate, zero-area hull) - the guard the pool
    maps never reach (the compactness check needs >=12 houses) but that must not crash on a stray call."""
    from l7r.diagram import check_village as cv

    assert cv.convex_hull([]) == []
    assert cv.convex_hull([(1.0, 2.0)]) == [(1.0, 2.0)]
    assert cv.convex_hull([(1.0, 2.0), (3.0, 4.0), (1.0, 2.0)]) == [(1.0, 2.0), (3.0, 4.0)]  # 2 unique
    assert cv.poly_area(cv.convex_hull([(0.0, 0.0), (1.0, 1.0)])) == 0.0


def test_the_new_trade_works_are_classified_in_both_registries():
    """The KEEP-CLEAR CONTRACT: registry membership alone gates a feature off every hazard and
    protects it from foreign captions. The border LINE is the deliberate exception - it is a line
    of law with no footprint, so it is exempt on both sides."""
    for key in ("charcoal_yards", "refining_forges"):
        assert key in check_village._OVERLAP_STRUCTS, key
        assert key in check_village._LABEL_GROUP, key
    assert "borders" in check_village._OVERLAP_EXEMPT
    assert "borders" in check_village._LABEL_EXEMPT


def test_a_border_line_under_a_compound_wall_trips_nothing():
    """A frontier magistracy stands its wall ON the line so the border runs across the parley-room
    floor (the Mode A ubame-magistracy sheet). Being overlapped is the arrangement, not a defect."""
    M = manifest(meta={"scale": "town", "ftpx": 1, "W": 1000, "H": 1000})
    M["borders"] = [{"poly": [[900, 0], [900, 1000]], "label": "the Fox border"}]
    M["manors"] = [{"x": 900, "y": 400, "w": 250, "h": 180, "rot": 0, "label": "Magistrate's Manor"}]
    assert not [c for c in f(M) if "border" in c]


def test_capital_government_ward_checks_pass_on_the_full_fixture():
    fails = f(_cap_gov())
    for c in _CAP_GOV_CHECKS:
        assert c not in fails, c


def test_feature_022_gate_refuses_an_unknown_check_name():
    with pytest.raises(ValueError, match="no_such_check_anywhere"):
        check_village.gate(_feature_022_manifest(), verbose=False, only={"no_such_check_anywhere"})


def test_feature_022_registry_base_names_match_the_frozen_legacy_set():
    frozen = json.loads((pathlib.Path(__file__).parent.parent / "fixtures" / "gate_check_names.json").read_text())
    registry = sorted({c for seg in check_village.GATE_SEGMENTS for c in seg.checks})
    assert registry == frozen
