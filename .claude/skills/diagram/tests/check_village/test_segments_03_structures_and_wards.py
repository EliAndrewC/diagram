"""Split from test_checks.py by feature 025 - see tests/check_village/CLAUDE.md for the index."""

import math
import sys

from l7r.diagram import check_village
from tests.check_village._builders import (
    _CHAN,
    _STRM,
    FEAT,
    _farmhouse,
    _feature_overlap,
    _field,
    _label_map,
    _maus_ward,
    _paddy_field_rec,
    f_only,
    house,
    manifest,
)

# ---- a feature-footprint overlap check ----------------------------------------------------


# ---- a meta-driven scale rule -------------------------------------------------------------
def test_hamlet_has_no_headman_fires_when_a_hamlet_has_one():
    M = {"meta": {"scale": "hamlet"}, "houses": [{"x": 100, "y": 100, "w": 108, "h": 68, "kind": "big", "rot": 0, "role": "headman"}]}
    assert "hamlet_has_no_headman" in f_only(M, "hamlet_has_no_headman")


def test_no_structure_on_stream_branches():
    assert "no_structure_on_stream" in _feature_overlap({}, "streams", [{"poly": FEAT}])


# ---- town street-layout FAIL branches -----------------------------------------------------


def test_all_houses_field_adjacent_dispersed_fires_on_a_remote_house():
    M = {"meta": {"scale": "village"}, "fields": [_field("f", 100, 100, 400, 400)], "houses": [_farmhouse(430, 250), _farmhouse(1200, 250)]}
    assert "all_houses_field_adjacent" in f_only(M, "all_houses_field_adjacent")  # the x=1200 house is way off its fields


def test_all_houses_field_adjacent_dispersed_passes_when_close():
    M = {"meta": {"scale": "village"}, "fields": [_field("f", 100, 100, 400, 400)], "houses": [_farmhouse(430, 250), _farmhouse(60, 250)]}
    assert "all_houses_field_adjacent" not in f_only(M, "all_houses_field_adjacent")  # both within 165px of the field


def test_nucleated_cluster_abuts_fields_passes_with_interior_houses_set_back():
    # a tight cluster whose EAST edge touches the field; interior houses sit a cluster-span back (fine)
    houses = [_farmhouse(x, 250) for x in (60, 130, 200, 270, 340, 410)]
    M = {"meta": {"scale": "village", "nucleated": True}, "fields": [_field("f", 430, 150, 700, 400)], "houses": houses}
    assert "cluster_abuts_fields" not in f_only(M, "cluster_abuts_fields")
    assert "all_houses_field_adjacent" not in f_only(M, "all_houses_field_adjacent")  # the per-house check does NOT run for nucleated


def test_nucleated_cluster_abuts_fields_fires_when_the_village_floats_off_its_land():
    houses = [_farmhouse(x, 250) for x in (60, 130, 200, 270)]
    M = {"meta": {"scale": "village", "nucleated": True}, "fields": [_field("f", 1400, 150, 1700, 400)], "houses": houses}  # fields ~1000px from the whole cluster
    assert "cluster_abuts_fields" in f_only(M, "cluster_abuts_fields")


def test_irrigation_channels_hairline_fires_on_a_fat_ditch():
    M = {"channels": [{"poly": _CHAN, "frm": {"kind": "offmap"}, "to": {"kind": "field", "name": "f"}, "w": 4.2}]}
    assert "irrigation_channels_hairline" in f_only(M, "irrigation_channels_hairline")  # the OLD 4.2 px stout ditch must now trip


def test_irrigation_channels_hairline_passes_at_the_floor():
    M = {"channels": [{"poly": _CHAN, "frm": {"kind": "offmap"}, "to": {"kind": "field", "name": "f"}, "w": 2.5}]}
    assert "irrigation_channels_hairline" not in f_only(M, "irrigation_channels_hairline")


def test_irrigation_channels_hairline_still_fires_on_a_fat_drain_culvert():
    M = {"channels": [{"poly": _CHAN, "frm": {"kind": "drain"}, "to": {"kind": "moat"}, "w": 5.0}]}
    assert "irrigation_channels_hairline" in f_only(M, "irrigation_channels_hairline")


def test_watercourses_wider_than_ditches_fires_when_a_creek_reads_like_a_ditch():
    M = {
        "channels": [{"poly": _CHAN, "frm": {"kind": "offmap"}, "to": {"kind": "field", "name": "f"}, "w": 2.5}],
        "streams": [{"poly": _STRM, "frm": None, "to": None, "w": 5}],
    }  # 5 < 2.5x2.5 -> too close to the ditch
    assert "watercourses_wider_than_ditches" in f_only(M, "watercourses_wider_than_ditches")


def test_watercourses_wider_than_ditches_passes_for_a_proper_creek():
    M = {"channels": [{"poly": _CHAN, "frm": {"kind": "offmap"}, "to": {"kind": "field", "name": "f"}, "w": 2.5}], "streams": [{"poly": _STRM, "frm": None, "to": None, "w": 9}]}  # 9 >= 6.25
    assert "watercourses_wider_than_ditches" not in f_only(M, "watercourses_wider_than_ditches")


def test_shrine_clear_of_grove_trees_fires_when_a_clump_covers_the_hall():
    # a fengshui-grove tree clump whose center sits on the shrine hall's footprint reads as buried in the wood
    M = {
        "meta": {"scale": "village"},
        "religious": [{"kind": "shrine", "x": 500, "y": 500, "w": 30, "h": 24, "label": "Shrine"}],
        "village_groves": [{"role": "water_mouth", "r": 14, "clumps": [[502, 498]]}],
    }
    assert "shrine_clear_of_grove_trees" in f_only(M, "shrine_clear_of_grove_trees")


def test_shrine_clear_of_grove_trees_uses_the_canopy_radius_not_the_nominal_clump():
    # a clump 18px off the hall's east edge: its NOMINAL r=14 does not reach, but the drawn CANOPY (~1.7x = 24)
    # does - the check uses the canopy radius, so it fires (the crown overhang is what the eye sees overlapping)
    M = {
        "meta": {"scale": "village"},
        "religious": [{"kind": "shrine", "x": 500, "y": 500, "w": 30, "h": 24, "label": "Shrine"}],  # east edge x=515
        "village_groves": [{"role": "water_mouth", "r": 14, "clumps": [[533, 500]]}],
    }  # 18px off -> canopy overlaps
    assert "shrine_clear_of_grove_trees" in f_only(M, "shrine_clear_of_grove_trees")


def test_torii_clear_of_grove_trees_fires_when_a_clump_covers_the_arch():
    # a fengshui-grove tree clump sitting on a torii arch reads as the arch buried in the wood
    M = {"meta": {"scale": "village"}, "torii": [[500, 500, 1]], "village_groves": [{"role": "water_mouth", "r": 14, "clumps": [[505, 504]]}]}
    assert "torii_clear_of_grove_trees" in f_only(M, "torii_clear_of_grove_trees")


def test_dry_plots_clear_of_paddies_fires_on_a_hem_plot_in_the_rice():
    # a neighboring fan's hem quilt punched into this fan's envelope (the Tango fe2-into-fe1 incident)
    M = {"fields": [_field("p", 440, 440, 600, 600)], "dry_plots": [{"poly": [[560, 560], [640, 560], [640, 640], [560, 640]], "crop": "millet", "theta": 0.4}]}  # NW corner ~40px deep in the paddy
    assert "dry_plots_clear_of_paddies" in f_only(M, "dry_plots_clear_of_paddies")


def test_dry_plots_clear_of_paddies_passes_when_the_hem_abuts_the_bund():
    # a hem plot legitimately KISSES the envelope across the berm - only real interpenetration fires
    M = {
        "fields": [_field("p", 440, 440, 600, 600)],
        "dry_plots": [{"poly": [[440, 600], [600, 600], [600, 660], [440, 660]], "crop": "barley", "theta": 0.4}],
    }  # shares the paddy's south edge exactly
    assert "dry_plots_clear_of_paddies" not in f_only(M, "dry_plots_clear_of_paddies")


# --- no_label_overlaps (two body labels must not overlap) ---
def test_no_label_overlaps_fires_when_glyphs_cross():
    # two same-line labels whose boxes cross by >2px (x) and >4px (y) - the glyphs touch (the real
    # Hoshizora "cremation ground" / "Monastery of Bishamon" collision: 3px x, 10px y)
    M = {"meta": {}, "labels": [[40, 740, 143, 752, 1, "cremation ground"], [140, 736, 290, 750, 2, "Monastery of Bishamon"]]}
    assert "no_label_overlaps" in f_only(M, "no_label_overlaps")


def test_no_label_overlaps_passes_when_stacked_boxes_only_kiss():
    # two STACKED labels whose boxes merely kiss vertically (2.2px, the descender allowance) but are
    # cleanly separated lines (the real Tango "Mausoleum" / "Ministry of Works") - must NOT flag
    M = {"meta": {}, "labels": [[2216, 1580, 2276, 1593, 1, "Mausoleum"], [2168, 1591, 2252, 1600, 2, "Ministry of Works"]]}
    assert "no_label_overlaps" not in f_only(M, "no_label_overlaps")


def test_no_label_overlaps_passes_when_clear():
    M = {"meta": {}, "labels": [[40, 740, 130, 752, 1, "a"], [200, 740, 300, 752, 2, "b"]]}
    assert "no_label_overlaps" not in f_only(M, "no_label_overlaps")


# --- label_hugs_its_referent (a caption must sit against the feature it names) ---
# Element [6] of a label record is the subject box, written only by the standoff-ladder path. The
# real defect: Tango's "Imperial Road" 55px off the roadway with nothing but bare ground between,
# which the overlap-only scorer scored as perfect. Box heights below are ascent+descender = 1.05x
# the font size, which is how the check recovers the size to scale its cap.
def test_label_hugs_its_referent_fires_on_a_caption_adrift_in_empty_ground():
    M = {"meta": {}, "labels": [[400, 500, 486, 512.6, 1, "Imperial Road", [540, 400, 549, 700]]]}
    assert "label_hugs_its_referent" in f_only(M, "label_hugs_its_referent")


def test_label_hugs_its_referent_passes_a_caption_tucked_against_its_subject():
    M = {"meta": {}, "labels": [[400, 500, 486, 512.6, 1, "Imperial Road", [491, 400, 500, 700]]]}
    assert "label_hugs_its_referent" not in f_only(M, "label_hugs_its_referent")


def test_title_clear_of_features_passes_over_blank_space():
    M = {"meta": {"scale": "village"}, "houses": [{"x": 300, "y": 300, "w": 60, "h": 40, "rot": 0, "kind": "plain"}], "title": {"name": "V", "bbox": [800, 50, 900, 90]}}
    assert "title_clear_of_features" not in f_only(M, "title_clear_of_features")


def test_title_clear_of_features_fires_on_a_house():
    M = {"meta": {"scale": "village"}, "houses": [{"x": 300, "y": 300, "w": 60, "h": 40, "rot": 0, "kind": "plain"}], "title": {"name": "V", "bbox": [280, 285, 340, 315]}}  # box on the house
    assert "title_clear_of_features" in f_only(M, "title_clear_of_features")


def test_title_clear_of_features_fires_over_a_field():
    M = {"meta": {"scale": "village"}, "fields": [_field("p", 200, 200, 600, 600)], "title": {"name": "V", "bbox": [300, 300, 450, 340]}}
    assert "title_clear_of_features" in f_only(M, "title_clear_of_features")


def test_title_clear_of_features_tolerates_scrub_but_not_grove_or_marsh():
    # The scrub commons is sparse GROUND COVER (a feathered grass scatter), not a feature with a footprint, and
    # a bold place name reads fine over it - so it does NOT block a title. This changed when the commons began
    # clothing the field's interior voids too (GM, 2026-07): scrub then covers nearly the whole map, and
    # treating it as an obstacle would leave the title nowhere at all to sit. Must stay in step with
    # `Settlement._title_obstacles`.
    scrub = {"meta": {"scale": "village"}, "commons": [{"poly": [[200, 200], [400, 200], [400, 400], [200, 400]]}], "title": {"name": "V", "bbox": [250, 250, 350, 300]}}
    assert "title_clear_of_features" not in f_only(scrub, "title_clear_of_features")
    # the MARSH (a distinct wetland) still blocks it; the GROVE no longer does (feature 137 T06, 2026-08-28):
    # the placard is an opaque card and a strip of belt under it hides nothing a reader needs, while a tall
    # hamlet framed tight to its content often has no blank placard-sized ground at all (10 of 48 seeds).
    # The generator still takes blank ground first and cover only as the last resort before the corner.
    marsh = {"meta": {"scale": "village"}, "marshes": [{"poly": [[200, 200], [400, 200], [400, 400], [200, 400]]}], "title": {"name": "V", "bbox": [250, 250, 350, 300]}}
    assert "title_clear_of_features" in f_only(marsh, "title_clear_of_features")
    grove = {"meta": {"scale": "village"}, "village_groves": [{"poly": [[200, 200], [400, 200], [400, 400], [200, 400]]}], "title": {"name": "V", "bbox": [250, 250, 350, 300]}}
    assert "title_clear_of_features" not in f_only(grove, "title_clear_of_features")


def test_title_clear_of_features_fires_over_the_pond():
    M = {"meta": {"scale": "village"}, "pond": [400, 400, 100, 80], "title": {"name": "V", "bbox": [380, 380, 450, 420]}}
    assert "title_clear_of_features" in f_only(M, "title_clear_of_features")


def test_scalebar_matches_declared_scale_passes():
    M = {"meta": {"scale": "village", "ftpx": 2}, "title": {"name": "V", "bbox": [800, 50, 900, 132]}, "scalebar": {"ft": 200, "ftpx": 2, "bbox": [800, 93, 900, 132]}}
    assert "scalebar_matches_declared_scale" not in f_only(M, "scalebar_matches_declared_scale")


def test_scalebar_matches_declared_scale_fires_when_missing():
    # a manifest with a title but no scalebar predates the bar (GM 2026-07-20) - regenerate the map
    M = {"meta": {"scale": "village", "ftpx": 2}, "title": {"name": "V", "bbox": [800, 50, 900, 90]}}
    assert "scalebar_matches_declared_scale" in f_only(M, "scalebar_matches_declared_scale")


def test_scalebar_matches_declared_scale_fires_on_a_wrong_distance():
    # a village map (2 ft/px) whose bar claims the hamlet distance - the 100 map-px bar must read 200 ft
    M = {"meta": {"scale": "village", "ftpx": 2}, "title": {"name": "V", "bbox": [800, 50, 900, 132]}, "scalebar": {"ft": 100, "ftpx": 1, "bbox": [800, 93, 900, 132]}}
    assert "scalebar_matches_declared_scale" in f_only(M, "scalebar_matches_declared_scale")


def test_trees_clear_of_fengshui_ponds_fires_on_an_overhanging_clump():
    # Hoshigaoka's defect in miniature: a grove clump's canopy (1.7x nominal r) crossing the half-moon
    # pond's water fires; a clump standing clear passes. Pond poly = a simple half-disk stand-in.
    pond = {"cx": 300, "cy": 300, "r": 40, "facing": 270, "poly": [[340, 300], [300, 340], [260, 300]]}
    M = {
        "meta": {"scale": "village"},
        "crescent_ponds": [pond],
        "village_groves": [{"poly": [[200, 200], [400, 200], [400, 400], [200, 400]], "role": "windbreak", "r": 10, "clumps": [[310, 315]]}],
        "labels": [[270, 350, 340, 362, 1, "geomantic pond"]],
    }
    assert "trees_clear_of_fengshui_ponds" in f_only(M, "trees_clear_of_fengshui_ponds")
    M["village_groves"][0]["clumps"] = [[500, 500]]
    assert "trees_clear_of_fengshui_ponds" not in f_only(M, "trees_clear_of_fengshui_ponds")


def test_title_has_placard_fires_on_a_pre_placard_manifest():
    # the parchment card under the title + scale bar (GM 2026-07-21, legibility over scrub) is drawn
    # by s.title() - a manifest without the record predates the card and needs regeneration
    M = {"meta": {"scale": "village"}, "title": {"name": "V", "bbox": [800, 50, 900, 132]}}
    assert "title_has_placard" in f_only(M, "title_has_placard")
    M["title"]["placard"] = [800, 50, 900, 132]
    assert "title_has_placard" not in f_only(M, "title_has_placard")


# --- intersections_are_crossroads (lane beds merge, no edge line across a junction) ---


def test_every_feature_classified_for_overlap_fires_on_unknown_feature():
    # a new footprint feature nobody added to the _OVERLAP_* registry trips the completeness guard
    M = {"meta": {"scale": "village"}, "watchtowers": [{"x": 100, "y": 100, "w": 20, "h": 20, "rot": 0}]}
    assert "every_feature_classified_for_overlap" in f_only(M, "every_feature_classified_for_overlap")


def test_every_feature_classified_for_overlap_passes_for_known_features():
    M = {"meta": {"scale": "village"}, "houses": [{"x": 100, "y": 100, "w": 20, "h": 20, "rot": 0, "kind": "plain"}]}
    assert "every_feature_classified_for_overlap" not in f_only(M, "every_feature_classified_for_overlap")


def test_walled_structure_yields_to_ward_wall_fires_when_unyielded():
    # north wall abuts the fence but the compound drew its own wall there (not recorded)
    assert "walled_structure_yields_to_ward_wall" in f_only(_maus_ward([]), "walled_structure_yields_to_ward_wall")


def test_walled_structure_yields_to_ward_wall_passes_when_yielded():
    assert "walled_structure_yields_to_ward_wall" not in f_only(_maus_ward(["north"]), "walled_structure_yields_to_ward_wall")


def test_walled_structure_yields_to_ward_wall_passes_when_not_abutting():
    # the mausoleum sits well clear of the fence - nothing to yield
    assert "walled_structure_yields_to_ward_wall" not in f_only(_maus_ward([], maus_cy=2000), "walled_structure_yields_to_ward_wall")


def test_walled_structure_yields_to_ward_wall_skips_tilted_compounds():
    # a tilted compound is not axis-aligned to a fence, so the rule does not apply
    M = _maus_ward([])
    M["mausoleums"][0]["rot"] = 30
    assert "walled_structure_yields_to_ward_wall" not in f_only(M, "walled_structure_yields_to_ward_wall")


# ---- no_structure_on_canal: a canal VERTEX sitting inside a building footprint --------------
# The canal-vs-structure test catches not only a footprint corner near the water but also a
# canal polyline vertex landing INSIDE a (large) footprint while every corner stays clear of the
# thin canal segments. A merchant house straddling the canal's bend must fire.


def test_field_outline_matches_planting_fires_on_a_phantom_tail():
    # A DISPERSED map whose field OUTLINE runs 200px past the planted crop (`vis_bbox`) - the over-declared
    # `field_fall` defect. The point of the fixture: `all_houses_field_adjacent` PASSES on this manifest (the
    # farm hugs the phantom tail, so it measures as adjacent) while the farm sits out beyond the last rice.
    # That is the blindness the check exists to cover, so assert BOTH facts.
    base = {
        "meta": {"scale": "hamlet", "down_deg": 90},
        "fields": [{"name": "tail-test", "kind": "paddy", "outline": [[400, 400], [800, 400], [800, 800], [400, 800]], "bbox": [400, 400, 800, 800], "vis_bbox": [400, 400, 800, 600]}],
        "houses": [{"x": 600, "y": 760, "w": 46, "h": 28, "rot": 0, "kind": "plain"}],
    }
    assert "field_outline_matches_planting" in f_only(base, "field_outline_matches_planting")
    assert "all_houses_field_adjacent" not in f_only(base, "all_houses_field_adjacent")  # the old gate is blind here - that is the whole point
    # outline == planting: the honest field, no tail -> does NOT fire
    good = {**base, "fields": [{**base["fields"][0], "vis_bbox": [400, 400, 800, 800]}]}
    assert "field_outline_matches_planting" not in f_only(good, "field_outline_matches_planting")
    # a rounding-scale rim (smoothing over irregular plots) is tolerated -> does NOT fire
    rim = {**base, "fields": [{**base["fields"][0], "vis_bbox": [410, 420, 790, 760]}]}
    assert "field_outline_matches_planting" not in f_only(rim, "field_outline_matches_planting")
    # NUCLEATED is scoped OUT: the cluster never rides the envelope, so a tail is inert there
    nuc = {**base, "meta": {**base["meta"], "nucleated": True}}
    assert "field_outline_matches_planting" not in f_only(nuc, "field_outline_matches_planting")
    # a field with no vis_bbox recorded is skipped rather than crashing
    novis = {**base, "fields": [{k: v for k, v in base["fields"][0].items() if k != "vis_bbox"}]}
    assert "field_outline_matches_planting" not in f_only(novis, "field_outline_matches_planting")


def test_dwellings_above_field_drain_fires_on_a_toe_farm():
    # a DISPERSED map (no meta.nucleated), downhill = due S (down_deg=90); a drain runs cross-slope (E-W) at
    # the field's low edge. The first drain segment is DEGENERATE (a repeated point) to exercise that branch.
    base = {
        "meta": {"scale": "hamlet", "down_deg": 90},
        "field_ditches": [{"role": "drain", "field": "toe-test", "poly": [[400, 600], [400, 600], [800, 600]], "w": 4}],
        "fields": [{"name": "toe-test", "kind": "paddy", "outline": [[380, 560], [820, 560], [820, 640], [380, 640]], "bbox": [380, 560, 820, 640]}],
    }
    # a farm 110px DOWNSLOPE (S) of the drain, projecting onto the drain's interior -> in the wet toe -> FIRES
    bad = {**base, "houses": [{"x": 600, "y": 710, "w": 46, "h": 28, "rot": 0, "kind": "plain"}]}
    assert "dwellings_above_field_drain" in f_only(bad, "dwellings_above_field_drain")
    # the same farm UPSLOPE (N) of the drain is on dry ground -> does NOT fire
    good = {**base, "houses": [{"x": 600, "y": 490, "w": 46, "h": 28, "rot": 0, "kind": "plain"}]}
    assert "dwellings_above_field_drain" not in f_only(good, "dwellings_above_field_drain")
    # a flank farm off the drain's END (W of its start) is a legit homestead beside the field -> does NOT fire
    flank = {**base, "houses": [{"x": 250, "y": 710, "w": 46, "h": 28, "rot": 0, "kind": "plain"}]}
    assert "dwellings_above_field_drain" not in f_only(flank, "dwellings_above_field_drain")
    # a NUCLEATED cluster is scoped OUT (governed by cluster_abuts_fields), even sitting downslope
    nuc = {**base, "meta": {**base["meta"], "nucleated": True}, "houses": [{"x": 600, "y": 710, "w": 46, "h": 28, "rot": 0, "kind": "plain"}]}
    assert "dwellings_above_field_drain" not in f_only(nuc, "dwellings_above_field_drain")


def test_village_cluster_compact_fires_on_a_hollow_cluster():
    """A nucleated village whose houses ring a big HOLLOW hull (an over-wide cluster stranding houses far
    from the fields) must fire; the same houses packed into a compact blob must not. The teeth: it measures
    built COVERAGE of the house convex hull, which `cluster_abuts_fields` (a per-house span allowance) misses.
    Village scale + >=12 houses only."""

    base = {
        "meta": {"scale": "village", "nucleated": True},
        "fields": [{"name": "p", "kind": "paddy", "outline": [[0, 400], [800, 400], [800, 900], [0, 900]], "bbox": [0, 400, 800, 900]}],
    }
    ring = [{"x": 400 + 300 * math.cos(t), "y": 200 + 300 * math.sin(t), "w": 24, "h": 18, "rot": 0, "kind": "plain"} for t in [i * 2 * math.pi / 16 for i in range(16)]]
    assert "village_cluster_compact" in f_only({**base, "houses": ring}, "village_cluster_compact")
    grid = [{"x": 360 + 26 * (i % 4), "y": 160 + 26 * (i // 4), "w": 24, "h": 18, "rot": 0, "kind": "plain"} for i in range(16)]
    assert "village_cluster_compact" not in f_only({**base, "houses": grid}, "village_cluster_compact")
    # a HAMLET (or a small cluster) is legitimately loose - the check is village-scale + >=12 houses only
    assert "village_cluster_compact" not in f_only({**base, "meta": {"scale": "hamlet", "nucleated": True}, "houses": ring}, "village_cluster_compact")
    assert "village_cluster_compact" not in f_only({**base, "houses": ring[:8]}, "village_cluster_compact")


def test_no_structure_on_paddy_fires_when_a_farmhouse_sinks_a_corner_into_the_crop():
    # house center 10px outside the paddy edge, 44px wide -> its corner reaches ~12px inside
    M = {"meta": {}, "fields": [_paddy_field_rec()], "houses": [{"x": 290, "y": 500, "w": 44, "h": 29, "kind": "plain", "rot": 0}]}
    assert "no_structure_on_paddy" in f_only(M, "no_structure_on_paddy")


def test_no_structure_on_paddy_passes_when_the_farmhouse_abuts_the_bund():
    M = {"meta": {}, "fields": [_paddy_field_rec()], "houses": [{"x": 276, "y": 500, "w": 44, "h": 29, "kind": "plain", "rot": 0}]}
    assert "no_structure_on_paddy" not in f_only(M, "no_structure_on_paddy")


def test_every_solid_feature_classified_for_labels_fires_on_an_unclassified_key(monkeypatch):
    """The ratchet: a new solid feature must declare the caption group that may cover it, or be
    excused in _LABEL_EXEMPT. Without this, forgetting is silent - which is exactly how the list
    this replaced fell behind twice."""
    M = _label_map("Temple of Benten", "martial_halls")
    assert "every_solid_feature_classified_for_labels" not in f_only(M, "every_solid_feature_classified_for_labels")
    # since feature 024 the gate is a package: each submodule that imported _OVERLAP_STRUCTS holds
    # its own binding, so patch every holder, not just the package namespace
    _new = check_village._OVERLAP_STRUCTS + ("hawk_mews",)
    for _m in [m for m in list(sys.modules.values()) if getattr(m, "__name__", "").startswith("l7r.diagram.check_village") and hasattr(m, "_OVERLAP_STRUCTS")]:
        monkeypatch.setattr(_m, "_OVERLAP_STRUCTS", _new)
    assert "every_solid_feature_classified_for_labels" in f_only(M, "every_solid_feature_classified_for_labels")


# --- angled-building captions (GM 2026-08-02): tilted label records carry the tilt at [7] -------
def test_no_label_overlaps_judges_tilted_pairs_by_their_quads():
    # two captions along the same -30 deg lane: their AABBs cross massively, their glyph runs lie
    # parallel 14px apart - the box test would false-flag what the reader sees as two clean lines
    M = {"meta": {}, "labels": [[100, 100, 200, 110, 1, "a", None, -30.0], [100, 114, 200, 124, 2, "b", None, -30.0]]}
    assert "no_label_overlaps" not in f_only(M, "no_label_overlaps")


def test_no_label_overlaps_fires_when_tilted_glyphs_actually_cross():
    M = {"meta": {}, "labels": [[100, 100, 200, 110, 1, "a", None, -30.0], [100, 102, 200, 112, 2, "b", None, -30.0]]}
    assert "no_label_overlaps" in f_only(M, "no_label_overlaps")


def test_label_hugs_its_referent_measures_the_tilted_quad():
    # the tilted run's low corner dips to ~4px off the subject box - hugging - where its own
    # pre-tilt box floats 38px above the subject
    hug = [100, 100, 240, 112, 1, "gate market", [90, 150, 150, 190], -30.0]
    assert "label_hugs_its_referent" not in f_only({"meta": {}, "labels": [hug]}, "label_hugs_its_referent")
    adrift = [100, 100, 240, 112, 1, "gate market", [600, 600, 700, 650], -30.0]
    assert "label_hugs_its_referent" in f_only({"meta": {}, "labels": [adrift]}, "label_hugs_its_referent")


def test_labels_align_with_their_referent_fires_and_passes():
    """A caption lies at exactly the angle of the rotated feature it names (GM 2026-08-27, T38: "the
    notice board is at an angle, therefore, the notice board label should be at exactly the same
    angle"). A level caption on a board at -122.8 fires; one at 57.2 (the same line, right way up)
    passes; a caption with no referent box is not judged."""
    board = {"x": 500.0, "y": 500.0, "w": 12.0, "h": 5.0, "vw": 12.0, "vh": 5.0, "rot": -122.8, "z": 1, "label": "notice board"}
    ref = [494.0, 497.5, 506.0, 502.5]
    level = manifest(houses=[house(x=400, y=400)], kosatsuba=[board], labels=[[480.0, 512.0, 533.0, 520.0, 2, "notice board", ref]])
    assert "labels_align_with_their_referent" in f_only(level, "labels_align_with_their_referent"), "a level caption on a tilted board must fire"
    aligned = manifest(houses=[house(x=400, y=400)], kosatsuba=[board], labels=[[480.0, 512.0, 533.0, 520.0, 2, "notice board", ref, 57.2]])
    assert "labels_align_with_their_referent" not in f_only(aligned, "labels_align_with_their_referent"), "the board's own angle passes"
    noref = manifest(houses=[house(x=400, y=400)], kosatsuba=[board], labels=[[480.0, 512.0, 533.0, 520.0, 2, "notice board"]])
    assert "labels_align_with_their_referent" not in f_only(noref, "labels_align_with_their_referent"), "no referent, no judgment"
