"""Split from test_checks.py by feature 025 - see tests/check_village/CLAUDE.md for the index."""

from tests.check_village._builders import (
    _RING,
    _fort_city,
    _haz_base,
    _on_ring_bldg,
    f_only,
)


def test_kido_clear_of_buildings_fires_when_a_row_house_sits_under_the_guard_box():
    # GM 2026-07: both fence-end kido guard boxes had row houses under them - the packs run long
    # before s.ward draws the gates, so the gen must reserve each kido's ground up front
    M = _fort_city(kido=[{"x": 400, "y": 500, "horizontal": False, "bbox": [385, 480, 415, 520]}], buildings=[{"x": 390, "y": 505, "w": 20, "h": 14, "rot": 0, "kind": "samurai"}])
    assert "kido_clear_of_buildings" in f_only(M, "kido_clear_of_buildings")


def test_kido_clear_of_buildings_passes_when_the_gate_ground_is_open():
    M = _fort_city(kido=[{"x": 400, "y": 500, "horizontal": False, "bbox": [385, 480, 415, 520]}], buildings=[{"x": 390, "y": 560, "w": 20, "h": 14, "rot": 0, "kind": "samurai"}])
    assert "kido_clear_of_buildings" not in f_only(M, "kido_clear_of_buildings")


def test_ring_road_kept_clear_fires_on_a_building_on_the_ring():
    assert "ring_road_kept_clear" in f_only(_fort_city(ring_road=_RING, ring_road_width=15, buildings=[_on_ring_bldg()]), "ring_road_kept_clear")


def test_ring_road_kept_clear_fires_on_a_ministry_on_the_ring():
    M = _fort_city(ring_road=_RING, ring_road_width=15, ministries=[{"name": "Ministry of Rites", "x": 760, "y": 500, "w": 50, "h": 50}])
    assert "ring_road_kept_clear" in f_only(M, "ring_road_kept_clear")


def test_ring_road_kept_clear_fires_on_a_field_on_the_ring():
    field = {"name": "f1", "kind": "dry", "bbox": [220, 480, 260, 520], "outline": [[220, 480], [260, 480], [260, 520], [220, 520]]}  # straddles the west leg
    assert "ring_road_kept_clear" in f_only(_fort_city(ring_road=_RING, ring_road_width=15, fields=[field]), "ring_road_kept_clear")


def test_ring_road_kept_clear_passes_without_a_ring():
    assert "ring_road_kept_clear" not in f_only(_fort_city(buildings=[_on_ring_bldg()]), "ring_road_kept_clear")


# --- city_graveyard_clear_of_ring_road (burial grounds keep off the ring's FULL drawn width) ---


# ---- overlap rules (2026-07-13): gate towers, ward fence, kido on fence -------------------


def test_granary_stores_are_solid_structs_for_every_keep_clear_rule():
    """A granary's kura are solid buildings like any other, but the manifest nests them under
    M['granary']['stores'] instead of a top-level list key, so the _OVERLAP_STRUCTS loop cannot
    reach them - solid_structs splices them in by hand. This holds that splice: without it a
    tax granary could be built across the patrol road and nothing would say so."""
    M = _haz_base()
    M["ring_road"] = [[400, 500], [600, 500]]
    M["granary"] = {"x": 500, "y": 500, "w": 60, "h": 40, "stores": [{"x": 500, "y": 500, "w": 18, "h": 14, "rot": 0}]}
    assert "ring_road_kept_clear" in f_only(M, "ring_road_kept_clear")
    M["granary"]["stores"][0]["y"] = 300  # ...and off the lane it is fine
    assert "ring_road_kept_clear" not in f_only(M, "ring_road_kept_clear")
