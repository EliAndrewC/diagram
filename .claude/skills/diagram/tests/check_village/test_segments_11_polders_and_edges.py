"""Split from test_checks.py by feature 025 - see tests/check_village/CLAUDE.md for the index."""

import math

import pytest

from l7r.diagram import check_village
from tests.check_village._builders import _WHY, _feature_022_manifest, _waived_map, f_only

# ---- dwellings must not sit in the WET low toe below the field's drainage ditch (feature 005 / GM 2026-07) ----


def test_polder_field_must_fill_its_bbox():
    # a field declared field_archetype=polder_grid must FILL its bounding box (a surveyed rectangle); a fan-shaped
    # outline covering only a fraction of its bbox fires.
    base = {"meta": {"scale": "hamlet", "field_archetype": "polder_grid"}}
    rect = {**base, "fields": [{"name": "p", "kind": "paddy", "outline": [[100, 100], [900, 100], [900, 1300], [100, 1300]], "bbox": [100, 100, 900, 1300]}]}
    assert "polder_fills_its_bbox" not in f_only(rect, "polder_fills_its_bbox")
    fan = {**base, "fields": [{"name": "p", "kind": "paddy", "outline": [[500, 100], [900, 1300], [100, 1300]], "bbox": [100, 100, 900, 1300]}]}  # a triangle covers ~half its bbox
    assert "polder_fills_its_bbox" in f_only(fan, "polder_fills_its_bbox")


def test_structures_clear_of_dike():
    # GM 2026-07-22: no farmhouse and no windbreak clump may sit ON the perimeter dike earthwork band.
    dike = [[100, 100], [900, 100], [900, 900], [100, 900]]
    base = {"meta": {"scale": "hamlet", "field_archetype": "polder_grid"}, "dikes": [{"outline": dike, "w_min": 14.0, "w_max": 38.0}]}
    assert "structures_clear_of_dike" in f_only({**base, "houses": [{"x": 500, "y": 500, "w": 40, "h": 26, "rot": 0, "kind": "plain"}]}, "structures_clear_of_dike")  # house on the dike
    assert "structures_clear_of_dike" in f_only({**base, "village_groves": [{"clumps": [[500, 500], [1200, 1200]]}]}, "structures_clear_of_dike")  # a clump on the dike
    assert "structures_clear_of_dike" not in f_only(
        {**base, "houses": [{"x": 1200, "y": 500, "w": 40, "h": 26, "rot": 0, "kind": "plain"}], "village_groves": [{"clumps": [[1200, 1200]]}]}, "structures_clear_of_dike"
    )
    # a non-polder map (no dike) never trips it
    assert "structures_clear_of_dike" not in f_only(
        {"meta": {"scale": "hamlet", "field_archetype": "valley_paddy"}, "houses": [{"x": 500, "y": 500, "w": 40, "h": 26, "rot": 0, "kind": "plain"}]}, "structures_clear_of_dike"
    )


def test_polder_channels_clear_of_dike():
    # GM 2026-07-22: the polder ring canal runs on the INNER TOE of the dike (field side); an irrigation
    # channel buried in the dike band fires (>4 points), a couple of sluice crossings are fine.
    dike = [[100, 100], [900, 100], [900, 900], [100, 900]]  # a simple square "band" outline
    base = {"meta": {"scale": "hamlet", "field_archetype": "polder_grid"}, "dikes": [{"outline": dike, "w_min": 14.0, "w_max": 38.0}]}
    inside = {"poly": [[200, 200], [300, 200], [400, 200], [500, 200], [600, 200], [700, 200]], "role": "main", "field": "p"}  # 6 pts in the band
    assert "polder_channels_clear_of_dike" in f_only({**base, "field_ditches": [inside]}, "polder_channels_clear_of_dike")
    outside = {"poly": [[200, 50], [500, 50], [800, 50], [200, 1000]], "role": "main", "field": "p"}  # all outside the band
    assert "polder_channels_clear_of_dike" not in f_only({**base, "field_ditches": [outside]}, "polder_channels_clear_of_dike")
    sluices = {"poly": [[200, 150], [500, 1000], [800, 150]], "role": "drain", "field": "p"}  # 2 crossings <= 4
    assert "polder_channels_clear_of_dike" not in f_only({**base, "field_ditches": [sluices]}, "polder_channels_clear_of_dike")
    # a non-polder archetype never trips it, and no dike -> polder_dike_is_earthwork owns that case
    assert "polder_channels_clear_of_dike" not in f_only(
        {"meta": {"scale": "hamlet", "field_archetype": "valley_paddy"}, "dikes": base["dikes"], "field_ditches": [inside]}, "polder_channels_clear_of_dike"
    )


def test_polder_edges_wander():
    # GM 2026-07-22 (issue 4): a polder's dikes must WANDER (a hand-dug fish-scale polder), not run axis-perfect.
    # A dead-straight axis-aligned outline fires; an outline that runs mostly off-axis passes.
    dike = [{"outline": [[100, 100], [900, 100], [900, 1300], [100, 1300]], "w_min": 14.0, "w_max": 38.0, "gaps": []}]
    base = {"meta": {"scale": "hamlet", "down_deg": 90, "field_archetype": "polder_grid"}, "dikes": dike}
    # an axis-aligned rectangle - with a leading ZERO-LENGTH segment the check skips - scores 0% off-axis
    rect = {**base, "fields": [{"name": "p", "kind": "paddy", "outline": [[100, 100], [100, 100], [900, 100], [900, 1300], [100, 1300], [100, 100]], "bbox": [100, 100, 900, 1300]}]}
    assert "polder_edges_wander" in f_only(rect, "polder_edges_wander")
    wavy = [(100 + 45 * math.sin(i / 3.0), 100 + i * 24) for i in range(50)] + [(900 + 45 * math.sin(i / 3.0), 1300 - i * 24) for i in range(50)]
    wavy.append(wavy[0])
    passd = {**base, "fields": [{"name": "p", "kind": "paddy", "outline": [[round(x, 1), round(y, 1)] for x, y in wavy], "bbox": [55, 100, 945, 1300]}]}
    assert "polder_edges_wander" not in f_only(passd, "polder_edges_wander")


def test_polder_dike_gapped_at_sluices():
    # GM 2026-07-22 (issue 1): a THROUGH-CROSSER (a water line running from the field, through the dike band,
    # to outside the field outline) must have a recorded dike gap near where it enters the band; no gap fires.
    band = [[100, 100], [900, 100], [900, 1300], [100, 1300]]
    outline = [[150, 150], [850, 150], [850, 1250], [150, 1250]]  # the field outline sits inside the band
    base = {"meta": {"scale": "hamlet", "field_archetype": "polder_grid"}, "fields": [{"name": "p", "kind": "paddy", "outline": outline, "bbox": [150, 150, 850, 1250]}]}
    crosser = {"poly": [[500, 700], [500, 120], [500, 50]], "role": "main", "field": "p"}  # field -> through band -> outside
    assert "polder_dike_gapped_at_sluices" in f_only({**base, "dikes": [{"outline": band, "w_min": 14.0, "w_max": 38.0, "gaps": []}], "field_ditches": [crosser]}, "polder_dike_gapped_at_sluices")
    assert "polder_dike_gapped_at_sluices" not in f_only(
        {**base, "dikes": [{"outline": band, "w_min": 14.0, "w_max": 38.0, "gaps": [[500, 110]]}], "field_ditches": [crosser]}, "polder_dike_gapped_at_sluices"
    )


def test_polder_floor_is_ring_interior():
    # GM 2026-07-22: the polder's green field floor must be the ring-canal INTERIOR (hug the outermost
    # channels), not the dike-boundary envelope. A floor vertex >8 px off the ring fires; a floor on the ring
    # passes. (No ring channels or no floor recorded -> the check is simply skipped.)
    ring = [
        {"poly": [[100, 100], [300, 100]], "role": "main", "seg": "feeder", "field": "p"},
        {"poly": [[300, 100], [300, 300]], "role": "lateral", "seg": "e_toe", "field": "p"},
        {"poly": [[300, 300], [100, 300]], "role": "drain", "seg": "drain", "field": "p"},
        {"poly": [[100, 300], [100, 100]], "role": "lateral", "seg": "w_toe", "field": "p"},
    ]
    base = {
        "meta": {"scale": "hamlet", "field_archetype": "polder_grid"},
        "field_ditches": ring,
        "dikes": [{"outline": [[90, 90], [310, 90], [310, 310], [90, 310]], "w_min": 14.0, "w_max": 38.0, "gaps": []}],
        "fields": [{"name": "p", "kind": "paddy", "outline": [[100, 100], [300, 100], [300, 300], [100, 300]], "bbox": [100, 100, 300, 300]}],
    }
    on_ring = {**base, "comb_floors": {"p": [[100, 100], [300, 100], [300, 300], [100, 300]]}}  # the floor IS the ring loop
    assert "polder_floor_is_ring_interior" not in f_only(on_ring, "polder_floor_is_ring_interior")
    off_ring = {**base, "comb_floors": {"p": [[50, 50], [350, 50], [350, 350], [50, 350]]}}  # the dike-boundary envelope, ~50 px out
    assert "polder_floor_is_ring_interior" in f_only(off_ring, "polder_floor_is_ring_interior")


def test_polder_dike_is_earthwork():
    # GM 2026-07-22: a polder/dike-pond map must record a perimeter-dike earthwork band of VARYING width;
    # a missing dike or a uniform-width one (the reverted post-1949 ruled rectangle) fires.
    base = {"meta": {"scale": "hamlet", "field_archetype": "polder_grid"}}
    assert "polder_dike_is_earthwork" in f_only(base, "polder_dike_is_earthwork")  # no dike recorded at all
    assert "polder_dike_is_earthwork" in f_only({**base, "dikes": [{"outline": [], "w_min": 20.0, "w_max": 22.0}]}, "polder_dike_is_earthwork")  # near-uniform width
    assert "polder_dike_is_earthwork" not in f_only({**base, "dikes": [{"outline": [], "w_min": 14.0, "w_max": 38.0}]}, "polder_dike_is_earthwork")
    assert "polder_dike_is_earthwork" in f_only({"meta": {"scale": "hamlet", "field_archetype": "mulberry_dike_fishpond"}}, "polder_dike_is_earthwork")
    # a non-polder archetype never trips it
    assert "polder_dike_is_earthwork" not in f_only({"meta": {"scale": "hamlet", "field_archetype": "valley_paddy"}}, "polder_dike_is_earthwork")


def test_the_waiver_meta_checks_cannot_themselves_be_waived():
    """Otherwise the hatch swallows its own guard: one waiver silencing waivers_are_live would let
    every other waiver rot unreported."""
    M = _waived_map({"waivers_are_live": _WHY, "tanning_yard_on_watr": _WHY})
    assert "waivers_are_live" in f_only(M, "waivers_are_live")


def test_feature_022_gate_refuses_a_meta_check_in_targeted_mode():
    # measured (census 2026-08-15): waivers_are_documented reads only the DECLARED waivers (pure
    # manifest input), so it is legitimately targetable; waivers_are_live reads what actually
    # FIRED this run and is the true meta-check.
    assert "waivers_are_live" in set(check_village.META_CHECKS)
    with pytest.raises(ValueError, match="waivers_are_live"):
        check_village.gate(_feature_022_manifest(), verbose=False, only={"waivers_are_live"})
