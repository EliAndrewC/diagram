"""tier city tests split out of `tests.check_village.test_common_overlap_policy` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram import check_village
from tests.check_village._builders import _gate_parts, bldg


@pytest.mark.tiers("city")
def test_matrix_extracts_a_ward_gates_parts_and_splits_off_the_guard_box():
    got = [k for k, *_ in check_village.matrix_extents({"meta": {"scale": "city"}, "kido": [_gate_parts()]})]
    assert sorted(got) == ["kido", "kido_guard_box"]
    # a gate that records no `guard` degrades to all-gateway rather than crashing, and a degenerate
    # part (fewer than 3 corners) is skipped
    bare = {"x": 400, "y": 500, "rot": 0, "parts": [[[380, 490], [420, 490], [420, 510], [380, 510]], [[1, 1], [2, 2]]]}
    assert [k for k, *_ in check_village.matrix_extents({"meta": {"scale": "city"}, "kido": [bare]})] == ["kido"]


@pytest.mark.tiers("city")
def test_the_parts_of_one_gate_do_not_accuse_each_other():
    # every part shares one object id, so the annex-on-its-own-parent test spares the glyph's pieces
    assert not [v for v in check_village.matrix_violations({"meta": {"scale": "city"}, "kido": [_gate_parts()]}) if "kido" in (v[0], v[1])]


@pytest.mark.tiers("city")
def test_matrix_sees_the_multi_road_list_and_a_flower_beds_outline():
    # `roads` (the multi-road list) and `flower_fields` (which stores its ring as `outline`, not
    # `poly`) were the other two classified-but-never-extracted keys found by the same audit
    on_road = {"meta": {"scale": "city"}, "roads": [{"pts": [[300, 500], [700, 500]], "w": 26}], "buildings": [bldg(500, 500, kind="merchant_house")]}
    assert ("roads", "buildings") in {(a, b) for a, b, _, _ in check_village.matrix_violations(on_road)} or ("buildings", "roads") in {
        (a, b) for a, b, _, _ in check_village.matrix_violations(on_road)
    }
    bed = {"meta": {"scale": "city"}, "flower_fields": [{"kind": "chrysanthemum", "outline": [[400, 400], [600, 400], [600, 600], [400, 600]]}], "buildings": [bldg(500, 500, kind="merchant_house")]}
    assert [v for v in check_village.matrix_violations(bed) if "flower_fields" in (v[0], v[1])]


@pytest.mark.tiers("capital")
def test_matrix_extracts_the_feature_020_linear_keys():
    """A record with no extents is invisible to every matrix check in both directions - feature
    019's blindness. The towpath records 'pts' and the aqueduct 'poly'; both must extract as
    STROKES via _MX_LINE_W (the aqueduct's open polyline must NOT fall through to the area-ring
    branch, which closes it into a sliver polygon)."""
    M = {"meta": {"scale": "capital"}, "towpaths": [{"pts": [[0, 0], [100, 0]], "w": 2.4}], "aqueducts": [{"poly": [[0, 50], [100, 50]], "w": 4.0, "intake": [0, 50], "to": [100, 50]}]}
    ks = [k for k, *_ in check_village.matrix_extents(M)]
    assert ks.count("towpaths") == 1 and ks.count("aqueducts") == 1
