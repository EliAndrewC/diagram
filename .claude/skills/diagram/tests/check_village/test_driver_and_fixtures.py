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


def test_a_waiver_excuses_its_check_and_is_recorded_as_used() -> None:
    """Feature 146: the WAIVE arm of `driver.check` - a map may break a rule in writing, and the driver
    records what was actually excused so a waiver whose defect is fixed can be reported stale."""
    from l7r.diagram import check_village

    M = manifest(meta={"scale": "hamlet", "households": 15, "toscale": True}, houses=[])
    M["meta"]["waivers"] = {"households_consistent": "a deliberate break, with a reason long enough to satisfy the minimum the gate demands of one"}
    fails = check_village.gate(M, verbose=False, only={"households_consistent"})
    assert "households_consistent" not in fails, "the waiver must excuse the check"
