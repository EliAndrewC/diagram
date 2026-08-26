"""Split from test_checks.py by feature 025 - see tests/check_village/CLAUDE.md for the index."""

from tests.check_village._builders import (
    _fort_city,
    _merchant_city,
    bldg,
    f_only,
)


def test_merchant_estates_match_roll_fires_when_drawn_undershoots_the_grant():
    # the seeded roll granted 2 compounds but only 1 was drawn (a stale hand count / short seat list)
    M = _merchant_city([bldg(300, 300, kind="merchant_house")], estates=[{"x": 500, "y": 600, "w": 62, "h": 46}])
    M["meta"]["merchant_estate_roll"] = 2
    assert "merchant_estates_match_roll" in f_only(M, "merchant_estates_match_roll")


def test_merchant_estates_match_roll_passes_on_the_rolled_count_and_skips_unrolled_maps():
    M = _merchant_city([bldg(300, 300, kind="merchant_house")], estates=[{"x": 500, "y": 600, "w": 62, "h": 46}])
    M["meta"]["merchant_estate_roll"] = 1
    assert "merchant_estates_match_roll" not in f_only(M, "merchant_estates_match_roll")
    M2 = _merchant_city([bldg(300, 300, kind="merchant_house")], estates=[{"x": 500, "y": 600, "w": 62, "h": 46}])
    assert "merchant_estates_match_roll" not in f_only(M2, "merchant_estates_match_roll")  # no recorded roll (a hand-placed town) - skipped


def test_kido_aligned_with_ward_fence_fires_when_axis_aligned_on_a_slant_and_passes_when_rotated():
    # GM 2026-07-24 (live on both cities, frozen in pool/regressions/: Nagahara's ~159deg SW
    # ring-road kido, Tango's ~44deg S jog kido): the kido's roofed bar spans the gap IN the
    # fence, so it rotates with the local fence tangent; axis-aligned-on-a-slant is the defect.
    ward = [{"name": "w", "boundary": [[300, 300], [600, 600]], "z": 1, "wall_caps": []}]
    stamp = _fort_city(wards=ward, kido=[{"x": 450, "y": 450, "horizontal": True, "bbox": [430, 430, 470, 470]}])  # legacy flag: a 90deg gate on a 45deg fence
    assert "kido_aligned_with_ward_fence" in f_only(stamp, "kido_aligned_with_ward_fence")
    turned = _fort_city(wards=ward, kido=[{"x": 450, "y": 450, "rot": 45.0, "bbox": [430, 430, 470, 470]}])
    assert "kido_aligned_with_ward_fence" not in f_only(turned, "kido_aligned_with_ward_fence")
    free = _fort_city(wards=ward, kido=[{"x": 100, "y": 900, "horizontal": True, "bbox": [80, 880, 120, 920]}])  # far from any fence - nothing to align to
    assert "kido_aligned_with_ward_fence" not in f_only(free, "kido_aligned_with_ward_fence")


def test_kido_guard_box_clear_of_lanes_fires_when_the_watch_box_stands_in_the_roadbed():
    # GM 2026-07-26 (Tango's two ring-road ward gates): the gate's watch box is a small BUILDING on
    # the verge beside the way - the bar spans the road, the box does not stand in it. The whole
    # kido group is overlap-exempt (the bar must cross the lane and the fence), so this is the one
    # rule that protects the box, and it needs the box's own recorded footprint: the group bbox
    # cannot tell the bar from the shack.
    ward = [{"name": "w", "boundary": [[300, 450], [600, 450]], "z": 1, "wall_caps": []}]
    ring = [[200, 500], [800, 500]]
    inbed = _fort_city(wards=ward, ring_road=ring, ring_road_width=20, kido=[{"x": 450, "y": 450, "rot": 0.0, "bbox": [430, 430, 470, 510], "guard": [[440, 492], [460, 492], [460, 508], [440, 508]]}])
    assert "kido_guard_box_clear_of_lanes" in f_only(inbed, "kido_guard_box_clear_of_lanes")
    verge = _fort_city(wards=ward, ring_road=ring, ring_road_width=20, kido=[{"x": 450, "y": 450, "rot": 0.0, "bbox": [430, 430, 470, 470], "guard": [[440, 452], [460, 452], [460, 468], [440, 468]]}])
    assert "kido_guard_box_clear_of_lanes" not in f_only(verge, "kido_guard_box_clear_of_lanes")
    legacy = _fort_city(wards=ward, ring_road=ring, ring_road_width=20, kido=[{"x": 450, "y": 450, "rot": 0.0, "bbox": [430, 430, 470, 510]}])  # a manifest from before the box was recorded
    assert "kido_guard_box_clear_of_lanes" not in f_only(legacy, "kido_guard_box_clear_of_lanes")


def test_kido_clear_of_wall_towers_fires_when_a_ward_gate_hugs_a_tower():
    # GM 2026-07: the E ward-fence kido's guard box sat inside the mural tower at the wall vertex
    # below the samurai neighborhood gate (both classes are overlap-EXEMPT, so nothing caught it)
    M = _fort_city(kido=[{"x": 210, "y": 500, "horizontal": False, "bbox": [195, 480, 225, 520]}], wall_towers=[{"x": 205, "y": 505, "w": 38, "h": 38, "rot": 0}])
    assert "kido_clear_of_wall_towers" in f_only(M, "kido_clear_of_wall_towers")


def test_kido_clear_of_wall_towers_passes_when_the_tower_stands_off():
    M = _fort_city(kido=[{"x": 210, "y": 500, "horizontal": False, "bbox": [195, 480, 225, 520]}], wall_towers=[{"x": 205, "y": 570, "w": 38, "h": 38, "rot": 0}])
    assert "kido_clear_of_wall_towers" not in f_only(M, "kido_clear_of_wall_towers")


# --- city_civic_label_on_its_own_building (a named civic label may sit only on ITS OWN building) ---


# --- city_government_offices_dont_abut (a ministry / the yamen must stand clear of its neighbors) ---
