"""Split from test_checks.py by feature 025 - see tests/check_village/CLAUDE.md for the index."""

from l7r.diagram import check_village
from tests.check_village._builders import (
    _feature_022_manifest,
    _field,
    _grove,
    _kiln_map,
    _nuc_grid,
    _nuc_village_M,
    _rural,
    _thin_belt_cluster,
    bldg,
    f,
    f_only,
    house,
    manifest,
    well,
)

# ---- the matrix debt register rots loudly ------------------------------------------------------


def test_gardens_clear_of_channels_fires_when_a_garden_sits_on_a_ditch():
    # a drain ditch runs straight through the garden's footprint - a raised-bed saien in a running ditch
    M = {
        "meta": {"scale": "village"},
        "houses": [{"x": 500, "y": 500, "w": 44, "h": 29, "kind": "plain", "rot": 0}],
        "gardens": [{"x": 540, "y": 500, "w": 24, "h": 16, "rot": 0, "of": [500, 500]}],
        "field_ditches": [{"poly": [[540, 480], [540, 520]], "role": "drain", "w": 6, "field": "f"}],
    }
    assert "gardens_clear_of_channels" in f_only(M, "gardens_clear_of_channels")


def test_farmhouses_shed_separately_passes_at_an_ordinary_nucleated_spacing():
    # The rule must not fire on a tight-but-honest nucleus: the scripted hamlets sit at 23-29 ft.
    far = {
        "meta": {"scale": "hamlet", "ftpx": 1},
        "houses": [{"x": 500, "y": 500, "w": 46, "h": 28, "kind": "plain", "rot": 0}, {"x": 570, "y": 500, "w": 46, "h": 28, "kind": "plain", "rot": 0}],
    }  # 24 ft apart
    assert "farmhouses_shed_separately" not in f_only(far, "farmhouses_shed_separately")


def test_farmhouses_shed_separately_measures_FEET_not_pixels():
    # The clearance is a physical distance, so it converts through meta.ftpx (FEET per pixel) rather
    # than being a raw pixel literal that would silently mean two different rules at two tiers.
    # The same 6 px wall gap is 6 ft at a hamlet (1 ft/px) - a merge - and 12 ft at a village
    # (2 ft/px), which is honest spacing. So the SAME geometry must fire at one tier and not the other.
    houses = [{"x": 500, "y": 500, "w": 23, "h": 14, "kind": "plain", "rot": 0}, {"x": 529, "y": 500, "w": 23, "h": 14, "kind": "plain", "rot": 0}]
    assert "farmhouses_shed_separately" in f_only({"meta": {"scale": "hamlet", "ftpx": 1}, "houses": houses}, "farmhouses_shed_separately"), "6 px = 6 ft at a hamlet: a merge"
    assert "farmhouses_shed_separately" not in f_only({"meta": {"scale": "village", "ftpx": 2}, "houses": houses}, "farmhouses_shed_separately"), "the same 6 px = 12 ft at a village: honest spacing"


def test_farmhouses_shed_separately_ignores_a_derelict():
    # A ruin has no roof left to shed, so it is not held to the drip-line rule - the placer skips it too.
    M = {
        "meta": {"scale": "hamlet", "ftpx": 1},
        "houses": [{"x": 500, "y": 500, "w": 46, "h": 28, "kind": "plain", "rot": 0}, {"x": 550, "y": 500, "w": 46, "h": 28, "kind": "abandoned", "rot": 0}],
    }
    assert "farmhouses_shed_separately" not in f_only(M, "farmhouses_shed_separately")


def test_village_windbreak_present_fires_when_a_nucleated_village_has_none():
    assert "village_windbreak_present" in f_only(_nuc_village_M(_nuc_grid(), []), "village_windbreak_present")


# --- labels_within_image (a label must not run off the edge of the rendered frame) ---
def test_labels_within_image_fires_when_a_label_runs_off_the_edge():
    # the default canvas is 1820x1180; this label pokes past the right edge
    M = {"meta": {}, "labels": [[1750, 500, 1900, 512, 1, "off the right edge"]]}
    assert "labels_within_image" in f_only(M, "labels_within_image")


def test_labels_within_image_passes_when_inside():
    M = {"meta": {}, "labels": [[100, 100, 300, 112, 1, "comfortably inside"]]}
    assert "labels_within_image" not in f_only(M, "labels_within_image")


def test_margins_form_continuous_ring_passes_when_the_frame_is_clothed():
    # one commons band + the field cover the whole (small) view - only feathered seams left
    M = {
        "meta": {"scale": "village", "view": [0, 0, 400, 300]},
        "fields": [_field("p", 0, 0, 400, 150)],
        "commons": [{"poly": [[0, 140], [400, 140], [400, 300], [0, 300]], "role": "grazing"}],
    }
    assert "margins_form_continuous_ring" not in f_only(M, "margins_form_continuous_ring")


def test_margins_form_continuous_ring_fires_on_bare_open_plain():
    # the real Ueda defect in miniature: the ring bands sit OFF-FRAME (west of the cropped view),
    # so the framed map is mostly bare open tan around a small field
    M = {
        "meta": {"scale": "village", "view": [500, 0, 400, 300]},
        "fields": [_field("p", 500, 0, 650, 150)],
        "commons": [{"poly": [[0, 0], [480, 0], [480, 300], [0, 300]], "role": "grazing"}],
    }
    assert "margins_form_continuous_ring" in f_only(M, "margins_form_continuous_ring")


def test_margins_form_continuous_ring_ignores_town_and_city_sheets():
    # urban sheets cover the ground with streets/wards/walls these feature sets do not model -
    # the satoyama-ring doctrine is village/hamlet scope only
    M = {"meta": {"scale": "town", "view": [0, 0, 400, 300]}}
    assert "margins_form_continuous_ring" not in f_only(M, "margins_form_continuous_ring")


def test_scatter_respects_swept_clearings_fires_on_cover_before_the_collar():
    # the real Ueda graveyard defect in miniature: the grazing band (seq 1) drew BEFORE the grave
    # collar was registered (clearing seq 1 = one cover already drawn), so tufts landed on swept ground
    M = {
        "meta": {"scale": "village"},
        "commons": [{"poly": [[50, 50], [400, 50], [400, 400], [50, 400]], "role": "grazing", "seq": 1}],
        "clearings": [{"poly": [[100, 100], [200, 100], [200, 200], [100, 200]], "seq": 1}],
    }
    assert "scatter_respects_swept_clearings" in f_only(M, "scatter_respects_swept_clearings")


def test_scatter_respects_swept_clearings_passes_when_the_ground_was_reserved():
    # the documented reserve_clearing pattern: the collar is reserved (seq 0, before any cover), the
    # band draws (seq 1, skips it), then the cemetery registers its own duplicate collar late (seq 1) -
    # harmless, because a pre-cover guard clearing already protected every point of it
    M = {
        "meta": {"scale": "village"},
        "commons": [{"poly": [[50, 50], [400, 50], [400, 400], [50, 400]], "role": "grazing", "seq": 1}],
        "clearings": [
            {"poly": [[100, 100], [200, 100], [200, 200], [100, 200]], "seq": 0},
            {"poly": [[100, 100], [200, 100], [200, 200], [100, 200]], "seq": 1},
        ],
    }
    assert "scatter_respects_swept_clearings" not in f_only(M, "scatter_respects_swept_clearings")


def test_scatter_respects_swept_clearings_passes_when_the_cover_draws_after():
    # normal order: clearing registered first (seq 0), the band draws after (seq 1) and skips it
    M = {
        "meta": {"scale": "village"},
        "commons": [{"poly": [[50, 50], [400, 50], [400, 400], [50, 400]], "role": "grazing", "seq": 1}],
        "clearings": [{"poly": [[100, 100], [200, 100], [200, 200], [100, 200]], "seq": 0}],
    }
    assert "scatter_respects_swept_clearings" not in f_only(M, "scatter_respects_swept_clearings")


def test_lanes_clear_of_dry_plots_fires_on_a_path_through_the_crop():
    # Hikari's defect in miniature (GM 2026-07-21): a lane crossing a dry plot's interior fires; a
    # lane running along the plot's edge (a path hugs the field margin by design) passes
    plot = {"poly": [[300, 300], [400, 300], [400, 400], [300, 400]], "crop": "barley", "theta": 0}
    M = {"meta": {"scale": "village"}, "dry_plots": [plot], "lanes": [{"pts": [[250, 350], [450, 350]], "width": 5}]}
    assert "lanes_clear_of_dry_plots" in f_only(M, "lanes_clear_of_dry_plots")
    M["lanes"] = [{"pts": [[250, 300], [450, 300]], "width": 5}]  # along the top edge - touching, not through
    assert "lanes_clear_of_dry_plots" not in f_only(M, "lanes_clear_of_dry_plots")
    M["lanes"] = [{"pts": [[250, 250], [450, 250]], "width": 5}]  # clear of the plot entirely
    assert "lanes_clear_of_dry_plots" not in f_only(M, "lanes_clear_of_dry_plots")


def test_labels_within_image_uses_the_cropped_view():
    # with a crop set, the frame is the viewBox - a label inside the full canvas but WEST of the crop
    # (a city map crops tight to the walls) is clipped and fires
    M = {"meta": {"view": [658, 448, 1884, 1764]}, "labels": [[300, 690, 500, 702, 1, "west of the crop"]]}
    assert "labels_within_image" in f_only(M, "labels_within_image")


def test_settlement_has_wells_fires_when_too_few():
    # 40 farm households, no wells at all
    assert "settlement_has_wells" in f_only(_rural("village", [(300 + i * 10, 300) for i in range(40)], []), "settlement_has_wells")


def test_settlement_dwellings_watered_fires_when_a_house_is_dry():
    # one house 600px from the only well, with no irrigation nearby
    assert "settlement_dwellings_watered" in f_only(_rural("village", [(300, 300), (300, 900)], [(300, 300)]), "settlement_dwellings_watered")


def test_settlement_dwellings_watered_passes_via_irrigation():
    # the far house has no well within reach but sits beside a stream
    M = _rural("hamlet", [(300, 900)], [(300, 300)], streams=[{"poly": [[200, 880], [400, 880]], "frm": None, "to": None, "w": 9}])
    assert "settlement_dwellings_watered" not in f_only(M, "settlement_dwellings_watered")


def test_remote_shrine_has_own_well_fires_when_a_set_apart_shrine_has_none():
    # the shrine sits far from the houses AND far from the one well -> it must keep its OWN well close by
    M = _rural("village", [(300, 300)], [(310, 305)], religious=[{"x": 1200, "y": 1200, "w": 30, "h": 24, "kind": "shrine"}])
    assert "remote_shrine_has_own_well" in f_only(M, "remote_shrine_has_own_well")


def test_remote_shrine_has_own_well_passes_with_a_well_close_by():
    M = _rural(
        "village",
        [(300, 300)],
        [(310, 305), (1210, 1205)],  # a second well right beside the remote shrine
        religious=[{"x": 1200, "y": 1200, "w": 30, "h": 24, "kind": "shrine"}],
    )
    assert "remote_shrine_has_own_well" not in f_only(M, "remote_shrine_has_own_well")


def test_remote_shrine_own_well_not_required_when_a_ditch_is_near():
    # a ditch/pond is NOT an ablution source - a set-apart shrine still needs its own WELL, so a nearby ditch does not save it
    M = _rural(
        "village",
        [(300, 300)],
        [(310, 305)],
        religious=[{"x": 1200, "y": 1200, "w": 30, "h": 24, "kind": "shrine"}],
        field_ditches=[{"poly": [[1180, 1180], [1220, 1220]], "w": 5, "role": "main", "field": "p"}],
    )
    assert "remote_shrine_has_own_well" in f_only(M, "remote_shrine_has_own_well")  # the ditch by the shrine does not count


def test_remote_shrine_among_the_houses_is_exempt():
    # a shrine near the dwellings shares the village wells - no own well required
    M = _rural("village", [(300, 300)], [(310, 305)], religious=[{"x": 360, "y": 340, "w": 30, "h": 24, "kind": "shrine"}])
    assert "remote_shrine_has_own_well" not in f_only(M, "remote_shrine_has_own_well")


def test_wells_among_dwellings_fires_on_a_stray_well():
    # a well far out in open country, no house beside it
    assert "wells_among_dwellings" in f_only(_rural("village", [(300, 300)], [(900, 900)]), "wells_among_dwellings")


def test_wells_among_dwellings_passes_when_beside_a_house():
    assert "wells_among_dwellings" not in f_only(_rural("village", [(300, 300)], [(340, 300)]), "wells_among_dwellings")


# ---- grove_clumps_clear_of_structures: a tree blob may abut but not overlap a farmstead ----


def test_wells_clear_of_trees_fires_on_grove_forest_woodland_grect_but_passes_when_clear():
    # a wellhead is a clean draw-point: it must not sit under ANY tree - the fengshui grove clumps, the
    # per-house grove rects, a forest, or a coppice-woodland patch. Each type fires; a well on open ground does not.
    base = {"meta": {"scale": "village"}, "houses": [bldg(300, 300, "laborer")]}
    well = {"x": 500, "y": 500, "r": 8, "vr": 12}
    on_grove = {**base, "wells": [well], "village_groves": [{"role": "windbreak", "x": 505, "y": 505, "r": 14, "clumps": [[505, 505]]}]}
    assert "wells_clear_of_trees" in f_only(on_grove, "wells_clear_of_trees")
    on_forest = {**base, "wells": [well], "forest": [[400, 400], [600, 400], [600, 600], [400, 600]]}
    assert "wells_clear_of_trees" in f_only(on_forest, "wells_clear_of_trees")
    on_wood = {**base, "wells": [well], "commons": [{"x": 500, "y": 500, "role": "woodland", "poly": [[440, 440], [560, 440], [560, 560], [440, 560]]}]}
    assert "wells_clear_of_trees" in f_only(on_wood, "wells_clear_of_trees")
    on_grect = {**base, "wells": [well], "groves": [{"x": 505, "y": 505, "w": 40, "h": 30, "of": [300, 300], "face": [0, -1]}]}
    assert "wells_clear_of_trees" in f_only(on_grect, "wells_clear_of_trees")
    clear = {**base, "wells": [well], "village_groves": [{"role": "windbreak", "x": 900, "y": 900, "r": 14, "clumps": [[900, 900]]}]}
    assert "wells_clear_of_trees" not in f_only(clear, "wells_clear_of_trees")


def test_wells_clear_of_trees_fires_on_a_drawn_crown_over_the_wellhead():
    # the reserved-area tests above are coarse (where trees MAY stand); tree_crowns is where they DO.
    # A crown drawn onto the wellhead fires even with no grove/forest record anywhere near it.
    base = manifest(houses=[bldg(300, 300, "laborer")])
    wl = well(500, 500)
    assert "wells_clear_of_trees" in f_only({**base, "wells": [wl], "tree_crowns": [508, 495, 9]}, "wells_clear_of_trees")
    assert "wells_clear_of_trees" not in f_only({**base, "wells": [wl], "tree_crowns": [540, 495, 9]}, "wells_clear_of_trees")


# ---- gardens_unshaded_from_east: a garden truly boxed in to the SOUTH by a bog is EXEMPT ----
# The east-shade relaxer only fires when a small SOUTHWARD nudge into OPEN ground would clear
# the morning-sun shadow. When every candidate shift lands the garden bed on a bog/marsh (or a
# field outline), no clear shift exists, so the garden is exempt and the check must NOT fire.
# This pins the field-outline / bog clause of the internal _bed_clear helper.


def test_village_windbreak_embraces_cluster_fires_on_far_corner_masses_only():
    # a substantial belt exists but stands 400px from the nearest farmhouse - decoration, not a wall
    houses = [{"x": 500 + i * 30, "y": 500, "w": 23, "h": 14, "kind": "plain", "rot": 0} for i in range(12)]
    far = {"x": 900, "y": 100, "w": 120, "h": 60, "role": "windbreak", "clumps": [[880 + j * 6, 100] for j in range(14)]}
    M = {"meta": {"scale": "village", "nucleated": True}, "houses": houses, "village_groves": [far]}
    assert "village_windbreak_embraces_cluster" in f_only(M, "village_windbreak_embraces_cluster")


def test_village_windbreak_embraces_cluster_passes_when_the_belt_nestles():
    houses = [{"x": 500 + i * 30, "y": 500, "w": 23, "h": 14, "kind": "plain", "rot": 0} for i in range(12)]
    belt = {"x": 590, "y": 420, "w": 300, "h": 50, "role": "windbreak", "clumps": [[470 + j * 22, 425] for j in range(14)]}
    M = {"meta": {"scale": "village", "nucleated": True}, "houses": houses, "village_groves": [belt]}
    assert "village_windbreak_embraces_cluster" not in f_only(M, "village_windbreak_embraces_cluster")


def test_village_windbreak_scales_with_cluster_fires_on_a_belt_too_thin_for_the_cluster():
    M = _thin_belt_cluster()
    fails = f(M)
    assert "village_windbreak_scales_with_cluster" in fails and "village_windbreak_embraces_cluster" not in fails


def test_village_windbreak_scales_with_cluster_counts_per_house_groves():
    # a map that ALSO groves its farmhouses (Hikari-no-Sato does both) banks those yashikirin footprints
    M = _thin_belt_cluster(groves=[_grove(500 + i * 30 - 18, 480, 500 + i * 30, 500, w=40, h=40) for i in range(12)])
    assert "village_windbreak_scales_with_cluster" not in f_only(M, "village_windbreak_scales_with_cluster")


def test_village_windbreak_forest_exempts_only_when_it_shelters_the_cluster():
    # a REAL FOREST standing at the cluster's windward (NW) back, within nestling reach, IS the wind wall
    near = _thin_belt_cluster(forest=[[400, 360], [420, 420], [400, 470]])
    assert "village_windbreak_scales_with_cluster" not in f_only(near, "village_windbreak_scales_with_cluster")
    # ... but a wood on the LEE side, half a map away, shelters nothing - no exemption (Moritono's Shirin
    # Forest, 1,089 ft east of the hamlet under an NW wind, GM 2026-07-25)
    far = _thin_belt_cluster(forest=[[1500, 200], [1520, 600], [1500, 900]])
    assert "village_windbreak_scales_with_cluster" in f_only(far, "village_windbreak_scales_with_cluster")
    # ... and neither does a wood that is CLOSE but downwind (the lee side of the same cluster)
    lee = _thin_belt_cluster(forest=[[900, 560], [940, 600], [900, 640]])
    assert "village_windbreak_scales_with_cluster" in f_only(lee, "village_windbreak_scales_with_cluster")


def test_wells_among_dwellings_counts_a_kiln_works_cottages():
    """The works' well stands among the houses it serves - they are simply recorded inside the kiln
    record rather than in M["houses"] (see s.kiln: every dwelling rule in the gate is written about
    the settlement's own housing stock, and a satellite works' cottages would be adjudicated by
    rules that were never about them). A check reading only that stock would call this well stray."""
    # a distant house so the map HAS a housing stock - the check deliberately abstains on a map
    # with no dwellings at all, which would make the negative half pass for the wrong reason
    M = _kiln_map(quarters=((500.0, 570.0),), houses=[house(100, 100)])
    M["wells"] = [well(500, 550)]
    assert "wells_among_dwellings" not in f_only(M, "wells_among_dwellings")
    M["kilns"][0]["quarters"] = []
    assert "wells_among_dwellings" in f_only(M, "wells_among_dwellings")


def test_labels_within_image_uses_the_tilted_reach():
    lvl = [100, 20, 240, 32, 1, "near the top edge"]
    assert "labels_within_image" not in f_only({"meta": {}, "labels": [lvl]}, "labels_within_image")
    # tilted -30, the run's high end pokes past the frame the level box sat inside
    assert "labels_within_image" in f_only({"meta": {}, "labels": [[*lvl[:6], None, -30.0]]}, "labels_within_image")


def test_feature_022_targeted_verdict_matches_the_full_gate():
    name = "settlement_has_wells"
    full = name in set(check_village.gate(_feature_022_manifest(), verbose=False))
    targ = name in set(check_village.gate(_feature_022_manifest(), verbose=False, only={name}))
    assert full == targ


# ---- settlement_records_cluster_seeding: a rolled knob must leave a trace ---------------------
def _seedrec_M(gen="hamletgen", nucleated=True, **meta):
    M = {"meta": {"scale": "hamlet", "W": 1200, "H": 1200}}
    if gen:
        M["meta"]["generated_by"] = gen
    if nucleated:
        M["meta"]["nucleated"] = True
    M["meta"].update(meta)
    return M


def _seedrec_f(M):
    return check_village.gate(M, verbose=False, only={"settlement_records_cluster_seeding"})


def test_cluster_seeding_fires_when_neither_trace_is_recorded():
    # the Kashikawa shape (2026-08-16): rows + frontage seated every house, the cloud never ran,
    # and the rolled cluster_shape knob vanished without a trace
    assert "settlement_records_cluster_seeding" in _seedrec_f(_seedrec_M())


def test_cluster_seeding_passes_when_the_cloud_recorded_the_knob():
    assert "settlement_records_cluster_seeding" not in _seedrec_f(_seedrec_M(cluster_shape="round"))


def test_cluster_seeding_passes_when_the_seeding_mode_is_recorded():
    assert "settlement_records_cluster_seeding" not in _seedrec_f(_seedrec_M(cluster_seeding="frontage"))


def test_cluster_seeding_skips_a_dispersed_settlement():
    # no nucleated cluster = no cluster knobs to trace
    assert "settlement_records_cluster_seeding" not in _seedrec_f(_seedrec_M(nucleated=False))


def test_cluster_seeding_skips_legacy_maps():
    assert "settlement_records_cluster_seeding" not in _seedrec_f(_seedrec_M(gen=None))


def test_captions_clear_the_ways_they_stand_on_fires_and_skips_a_malformed_record() -> None:
    """0617: a caption's 3 px halo must not notch the tread its subject stands on.

    Two assertions, and the SECOND is the one with no map behind it. A label record is a flat list
    `[x0, y0, x1, y1, z, text]`, and the check guards against a shorter one - no map in the pool or
    the cohort produces one, so that `continue` is a branch the corpus cannot reach and the coverage
    gate rightly refused it. The guard is worth keeping rather than deleting: the check reads four
    positional fields off a record whose shape nothing enforces, so a truncated entry would be an
    IndexError inside the GATE, which is the worst place to discover it."""
    lane = {"pts": [(0.0, 100.0), (400.0, 100.0)], "w": 6}
    meta = {"scale": "hamlet", "ftpx": 1, "W": 1000, "H": 1000, "generated_by": "test"}

    on_the_lane = manifest(meta=meta, lanes=[lane], labels=[[180.0, 96.0, 240.0, 104.0, 20000000, "notice board"]])
    assert "captions_clear_the_ways_they_stand_on" in check_village.gate(on_the_lane, verbose=False, only={"captions_clear_the_ways_they_stand_on"})

    well_clear = manifest(meta=meta, lanes=[lane], labels=[[180.0, 300.0, 240.0, 308.0, 20000000, "notice board"]])
    assert "captions_clear_the_ways_they_stand_on" not in check_village.gate(well_clear, verbose=False, only={"captions_clear_the_ways_they_stand_on"})

    # a truncated record is SKIPPED, not crashed on, even though it sits squarely on the lane
    malformed = manifest(meta=meta, lanes=[lane], labels=[[180.0, 96.0, 240.0, 104.0]])
    assert "captions_clear_the_ways_they_stand_on" not in check_village.gate(malformed, verbose=False, only={"captions_clear_the_ways_they_stand_on"})


def test_village_groves_visibly_stocked_fires_on_a_grove_that_was_never_drawn():
    """A DECLARED GROVE MUST HOLD TREES (gate 0618, settlement-review on Inashiro 2026-08-20).

    The motivating artifact: `village_groves[1]`, role copse, 255 x 741 px, holding exactly ONE
    clump - a grove the manifest declares and the sheet does not show. Every other grove rule asks
    where the clumps are relative to something ELSE (the belt, the paddies, the structures, the
    lanes), so a feature collapsing to nothing passed all of them.

    The three cases below are the floor's whole contract: the defect fires, a healthy scatter at the
    lowest density ever measured on a shipped map passes, and a zero-area record is skipped rather
    than dividing by zero."""
    meta = {"scale": "hamlet", "ftpx": 1, "W": 1000, "H": 1000, "generated_by": "test"}
    only = {"village_groves_visibly_stocked"}

    # 1 clump in 255x741 px = 0.53 per 100k - the Inashiro defect, to its own numbers
    starved = manifest(meta=meta, village_groves=[{"role": "copse", "w": 255.0, "h": 740.9, "r": 11.0, "clumps": [[500.0, 500.0]]}])
    assert "village_groves_visibly_stocked" in check_village.gate(starved, verbose=False, only=only)

    # 14 clumps in 538x667 = 3.90 per 100k - Sawada before the fix, the LOWEST healthy scatter
    # measured on any shipped map. The floor must clear it, or it is dictating density rather than
    # catching absence.
    healthy = manifest(meta=meta, village_groves=[{"role": "copse", "w": 538.0, "h": 667.0, "r": 11.0, "clumps": [[float(i) * 10, 500.0] for i in range(14)]}])
    assert "village_groves_visibly_stocked" not in check_village.gate(healthy, verbose=False, only=only)

    # a zero-area record is SKIPPED, not divided by (coverage: the `_area <= 0` branch)
    degenerate = manifest(meta=meta, village_groves=[{"role": "copse", "w": 0.0, "h": 0.0, "r": 11.0, "clumps": []}])
    assert "village_groves_visibly_stocked" not in check_village.gate(degenerate, verbose=False, only=only)


def test_bamboo_stands_clear_of_paddies_fires_and_passes():
    """A take-yabu stands on the dry margin, never in the rice (feature 133 T47)."""
    stand = {"x": 500.0, "y": 300.0, "w": 48.0, "h": 34.0, "rot": 0, "role": "homestead", "poly": [[476, 283], [524, 283], [524, 317], [476, 317]]}
    paddy = [_field("f", 500, 300, 900, 700)]  # the stand's south-east corner lies in it
    assert "bamboo_stands_clear_of_paddies" in f_only(manifest(houses=[house(x=400, y=400)], fields=paddy, bamboo_stands=[stand]), "bamboo_stands_clear_of_paddies")
    assert "bamboo_stands_clear_of_paddies" not in f_only(manifest(houses=[house(x=400, y=400)], fields=[_field("f", 600, 400, 900, 700)], bamboo_stands=[stand]), "bamboo_stands_clear_of_paddies")


def test_a_hilltop_shrine_needs_no_dug_well_of_its_own():
    """`remote_shrine_has_own_well`'s HILL arm (feature 158). A shrine set apart from the houses keeps
    its own draw-point for temizu - unless it stands on the hill, where it takes a spring or a rock
    basin and no one digs a well up a slope. The arm was reached only by frozen hand-era manifests.

    Both halves are asserted, because a `continue` that exempts everything looks exactly like one that
    exempts the right thing."""
    hall = {"x": 800, "y": 200, "w": 40, "h": 30, "kind": "shrine"}
    on_the_hill = manifest(religious=[hall], hill=[800, 200, 160, 120], houses=[house(200, 800)])
    assert "remote_shrine_has_own_well" not in f_only(on_the_hill, "remote_shrine_has_own_well")
    off_the_hill = manifest(religious=[hall], houses=[house(200, 800)])
    assert "remote_shrine_has_own_well" in f_only(off_the_hill, "remote_shrine_has_own_well"), "set apart, on flat ground, with no well: it owes one"
