"""Split from test_checks.py by feature 025 - see tests/check_village/CLAUDE.md for the index."""

from l7r.diagram import check_village
from tests.check_village._builders import (
    _crop_map,
    _farrier_map,
    _forge_map,
    _fuel_map,
    _kiln_map,
    _mx_map,
    _pop_city,
    bldg,
    f,
    f_only,
    garden,
    house,
    manifest,
    yard,
)


def test_a_paid_matrix_debt_fires_so_the_line_gets_deleted(monkeypatch):
    """An _MATRIX_OUTSTANDING line is WORK OWED. Once the defect is fixed the line does not just rot -
    it goes on tolerating that many real overlaps of that pair for ever. Minami's five were fixed
    while the entry recording them stayed behind."""
    monkeypatch.setitem(check_village._MATRIX_OUTSTANDING, "Nowhere", {("dry_plots", "manors"): 2})
    M = manifest(meta={"scale": "village", "ftpx": 1, "W": 1000, "H": 1000, "name": "Nowhere"})
    assert "matrix_debts_still_owed" in f_only(M, "matrix_debts_still_owed")  # the map draws neither, so the debt is paid


def test_an_unpaid_matrix_debt_stays_quiet(monkeypatch):
    monkeypatch.setitem(check_village._MATRIX_OUTSTANDING, "Nowhere", {})
    M = manifest(meta={"scale": "village", "ftpx": 1, "W": 1000, "H": 1000, "name": "Nowhere"})
    assert "matrix_debts_still_owed" not in f_only(M, "matrix_debts_still_owed")


def test_hard_features_within_frame_fires_on_a_feature_clipped_by_the_crop():
    # a set-apart graveyard placed past the tight WEST frame edge (its west edge x=310 < the view's x0=400).
    # the torii (list branch) and well (radius branch) sit INSIDE the frame - only the graveyard is clipped.
    M = {
        "meta": {"scale": "village", "view": [400, 100, 1000, 800]},
        "torii": [[500, 300, 1]],
        "wells": [{"x": 600, "y": 300, "r": 8}],
        "cemeteries": [{"x": 360, "y": 500, "w": 100, "h": 70, "rot": 0}],
    }
    assert "hard_features_within_frame" in f_only(M, "hard_features_within_frame")


def test_crop_hugs_content_fires_when_the_frame_is_held_open():
    # Kikuta's defect in miniature: the north view edge sits ~385px above the northernmost
    # frame-setting content because the crop was holding the windbreak grove fully in frame
    M = {
        "meta": {"scale": "village", "view": [150, -300, 120, 455]},
        "houses": [{"x": 200, "y": 100, "w": 40, "h": 30, "rot": 0, "kind": "plain"}],
        "village_groves": [{"poly": [[100, -290], [300, -290], [300, 60], [100, 60]], "role": "windbreak"}],
    }
    assert "crop_hugs_content" in f_only(M, "crop_hugs_content")


def test_crop_hugs_content_counts_the_windbreaks_inner_face_but_not_its_depth():
    """GM 2026-08-26 (feature 133 T10): the belt's inner FACE is frame-setting, the belt behind it is
    not - so a view opened 48 px past the front row of crowns passes, and one opened past the
    whole belt (Kikuta's defect) still fires."""
    belt = {"role": "windbreak", "r": 14, "clumps": [[x, y] for x in (150, 200, 250) for y in (-200, -150, -100, -50)], "poly": [[100, -220], [300, -220], [300, -30], [100, -30]]}
    house = {"x": 200, "y": 100, "w": 40, "h": 30, "rot": 0, "kind": "plain"}
    face = -50 + 14  # the southernmost clump row's crowns end here, facing the house
    snug = {"meta": {"scale": "village", "view": [150, face - 48, 120, 115 - (face - 48)]}, "houses": [house], "village_groves": [belt]}
    assert "crop_hugs_content" not in f_only(snug, "crop_hugs_content"), "48 px past the face is the margin, not slack"
    wide = {"meta": {"scale": "village", "view": [150, -300, 120, 415]}, "houses": [house], "village_groves": [belt]}
    assert "crop_hugs_content" in f_only(wide, "crop_hugs_content"), "the belt's depth still may not hold the frame open"


def test_crop_hugs_content_passes_on_a_snug_frame():
    M = {
        "meta": {"scale": "village", "view": [150, 45, 120, 110]},
        "houses": [{"x": 200, "y": 100, "w": 40, "h": 30, "rot": 0, "kind": "plain"}],
    }
    assert "crop_hugs_content" not in f_only(M, "crop_hugs_content")


def test_crop_hugs_content_reveals_only_a_band_of_a_canvas_filling_forest():
    # a wood drawn to the canvas edge is frame-setting only to FOREST_REVEAL_FT past its TREE LINE
    # (deeper in it is identical crowns), so a frame that stops there is snug, not "held open"...
    # (deeper in it is identical crowns), so a view opened 190px past the tree line is HELD OPEN
    M = {
        "meta": {"scale": "hamlet", "ftpx": 1, "W": 1000, "H": 500, "view": [150, 45, 550, 110]},
        "houses": [{"x": 200, "y": 100, "w": 40, "h": 30, "rot": 0, "kind": "plain"}],
        "forest": [[400, 0], [400, 500], [1000, 500], [1000, 0]],
        "forest_edge": [[400, 0], [400, 500]],
    }
    assert "crop_hugs_content" in f_only(M, "crop_hugs_content")
    assert "crop_hugs_content" not in f_only({**M, "meta": {**M["meta"], "view": [150, 45, 360, 110]}}, "crop_hugs_content")  # snug: the reveal band exactly
    # a wood recorded WITHOUT its tree line keeps the legacy rule - the whole clamped polygon is
    # frame-setting, so the same wide view reads as snug
    assert "crop_hugs_content" not in f_only({**M, "forest_edge": None}, "crop_hugs_content")


def test_crop_hugs_content_is_not_excused_by_a_forest_running_off_both_canvas_ends():
    # the wood's N-S tree line runs off BOTH ends of the canvas - it is running ALONG that axis, not
    # bounding anything, so it cannot excuse a frame held open to the canvas top (GM 2026-07-25: this
    # is what pinned Moritono's north edge 127px past the northernmost real content). The house is the
    # only vertical content, so a full-height view is loose and a snug one passes.
    M = {
        "meta": {"scale": "hamlet", "ftpx": 1, "W": 1000, "H": 500, "view": [150, 0, 360, 500]},
        "houses": [{"x": 200, "y": 300, "w": 40, "h": 30, "rot": 0, "kind": "plain"}],
        "forest": [[400, -10], [400, 510], [1000, 510], [1000, -10]],
        "forest_edge": [[400, -10], [400, 510]],
    }
    assert "crop_hugs_content" in f_only(M, "crop_hugs_content")
    assert "crop_hugs_content" not in f_only({**M, "meta": {**M["meta"], "view": [150, 255, 360, 90]}}, "crop_hugs_content")


def test_hard_features_within_frame_lets_the_windbreak_clip_but_not_vanish():
    # a windbreak POKING past the frame edge is fine (part visible = "the wood continues";
    # the crop no longer holds the frame open for it) ...
    M = {
        "meta": {"scale": "village", "view": [0, 0, 400, 300]},
        "village_groves": [{"poly": [[100, -200], [300, -200], [300, 80], [100, 80]], "role": "windbreak"}],
    }
    assert "hard_features_within_frame" not in f_only(M, "hard_features_within_frame")
    # ... but one ENTIRELY outside the view is a lost feature and still fires
    M2 = {
        "meta": {"scale": "village", "view": [0, 0, 400, 300]},
        "village_groves": [{"poly": [[100, -200], [300, -200], [300, -40], [100, -40]], "role": "windbreak"}],
    }
    assert "hard_features_within_frame" in f_only(M2, "hard_features_within_frame")


def test_farrier_serves_a_stables_fires_on_a_forge_with_no_stables_in_reach():
    # a shoeing forge earns its own premises ONLY where horses concentrate (settlements.md
    # "TRADE WORKS" -> FARRIERY): the ordinary smith who also shoes stays inside the shop rows,
    # so a forge on a random street corner is the European coaching-inn image, not a Rokugani seat
    assert "farrier_serves_a_stables" in f_only(_farrier_map(800, 800), "farrier_serves_a_stables")
    M = _farrier_map(800, 800)
    M["buildings"] = []  # ... and a map with NO stables at all fails the same way
    assert "farrier_serves_a_stables" in f_only(M, "farrier_serves_a_stables")


def test_farrier_serves_a_stables_passes_beside_the_caravan_yard():
    # 250 real ft is the reach; at ftpx=1 a forge 120px off its stables is well inside it
    assert "farrier_serves_a_stables" not in f_only(_farrier_map(320, 200), "farrier_serves_a_stables")


def test_farrier_keeps_fire_gap_fires_on_a_forge_against_the_stall_range():
    # an OPEN forge against a hay-and-timber stall range is the fire a stable yard does not
    # survive, so the smithy stands across the ground, never attached. Both an overlapping forge
    # and one merely crowding the wall are the same defect.
    assert "farrier_keeps_fire_gap" in f_only(_farrier_map(200, 200), "farrier_keeps_fire_gap")  # squarely on top of the stables
    assert "farrier_keeps_fire_gap" in f_only(_farrier_map(200, 240), "farrier_keeps_fire_gap")  # 5 ft of daylight - not enough


def test_farrier_keeps_fire_gap_passes_at_a_real_fire_gap():
    # ~6 real ft clear of every footprint (buildings.md's wooden-service fire gap) is the floor
    assert "farrier_keeps_fire_gap" not in f_only(_farrier_map(200, 250), "farrier_keeps_fire_gap")


def test_population_counts_only_in_wall_dwellings_for_a_walled_city():
    # 20 dwellings inside -> ~100 residents, passes.
    inside = [bldg(300 + (i % 10) * 20, 300, "laborer") for i in range(20)]
    assert "population_consistent_with_housing" not in f_only(_pop_city(inside), "population_consistent_with_housing")
    # 15 inside + 5 spilled OUTSIDE (x=50) = 20 total: the OLD count (all 20) would pass, but only
    # the 15 in-wall now count -> ~75 residents -> fails. The spill cannot rescue the figure.
    spilled = [bldg(300 + (i % 10) * 20, 300, "laborer") for i in range(15)] + [bldg(50, 300 + i * 20, "laborer") for i in range(5)]
    assert "population_consistent_with_housing" in f_only(_pop_city(spilled), "population_consistent_with_housing")


def test_crop_not_held_open_fires_on_a_lone_small_feature_far_out():
    # one 28px-tall building ~400px south of everything else: it alone makes the image taller
    M = _crop_map(buildings=[bldg(500, 500), bldg(540, 500), bldg(520, 900)])
    assert "crop_not_held_open_by_one_feature" in f_only(M, "crop_not_held_open_by_one_feature")


def test_crop_not_held_open_spares_a_LARGE_outlying_feature():
    # a pond out on its own is the outlying CONTENT - big, and meant to be there. This is the
    # case that made the rule a RATIO rather than a flat gap (ponds measured 1.03-1.35x in the pool)
    M = _crop_map(pond=[520, 900, 200, 200])
    assert "crop_not_held_open_by_one_feature" not in f_only(M, "crop_not_held_open_by_one_feature")


def test_crop_not_held_open_honors_the_declared_opt_out():
    M = _crop_map(buildings=[bldg(500, 500), bldg(540, 500), bldg(520, 900)])
    M["meta"]["crop_outlier_ok"] = True
    assert "crop_not_held_open_by_one_feature" not in f_only(M, "crop_not_held_open_by_one_feature")


def test_charcoal_yard_keeps_fire_gap_fires_on_a_crowded_yard():
    """Charcoal self-heats: freshly-made charcoal absorbs oxygen fast enough to raise its own
    temperature to ignition, worst of all as tightly-packed fines. The hazard is therefore an
    UNATTENDED ignition inside a large fuel mass, which is why the gap (30 real ft, about one
    flame-height off a fully-involved stack) is an order above the attended-forge figure and well
    below the crematory's smell-carried-on-air figure."""
    tight = _fuel_map(houses=[house(500, 500 + 29 + 14 + 20)])  # 20 real ft off the yard
    clear = _fuel_map(houses=[house(500, 500 + 29 + 14 + 60)])  # 60 real ft off it
    assert "charcoal_yard_keeps_fire_gap" in f_only(tight, "charcoal_yard_keeps_fire_gap")
    assert "charcoal_yard_keeps_fire_gap" not in f_only(clear, "charcoal_yard_keeps_fire_gap")


def test_charcoal_yard_has_cooling_ground_fires_on_a_covered_only_yard():
    """A yard with no open apron has nowhere to stand a fresh load apart from the conditioned
    stock, which is the documented handling rule (24 hours in the open; 8 days of air clears it).
    A roofed shed is equally required - the county's premium good is bought for a dry burn."""
    assert "charcoal_yard_has_cooling_ground" in f_only(
        _fuel_map(charcoal_yards=[{"x": 500, "y": 500, "w": 88, "h": 58, "rot": 0, "label": "charcoal yard", "sheds": 2}]), "charcoal_yard_has_cooling_ground"
    )
    assert "charcoal_yard_has_cooling_ground" in f_only(
        _fuel_map(charcoal_yards=[{"x": 500, "y": 500, "w": 88, "h": 58, "rot": 0, "label": "charcoal yard", "sheds": 0, "apron": [0, 0, 30, 20]}]), "charcoal_yard_has_cooling_ground"
    )
    assert "charcoal_yard_has_cooling_ground" not in f_only(_fuel_map(), "charcoal_yard_has_cooling_ground")


def test_refining_forge_stands_off_dwellings():
    """A fining hearth is an OPEN fire under a forced blast, worked with a rod while the iron is
    semi-molten - the sparks, noise and smoke are the process, not a side effect. 60 real ft: half
    the crematory's nuisance figure (this does not rot), double the fuel stack's (this one is a
    live ignition source, but somebody is standing at it)."""
    close = _forge_map(homes=[(500, 500 + 24 + 14 + 30)])
    clear = _forge_map(homes=[(500, 500 + 24 + 14 + 70)])
    assert "refining_forge_stands_off_dwellings" in f_only(close, "refining_forge_stands_off_dwellings")
    assert "refining_forge_stands_off_dwellings" not in f_only(clear, "refining_forge_stands_off_dwellings")


def test_refining_forge_downwind_reads_the_maps_own_windward_declaration():
    """SMOKE goes downwind, FILTH goes downstream - two separate axes. This is the first: keyed off
    meta(windward=...), so a map with a different exposure gets a different answer instead of a
    hardcoded corner. Under the default NW monsoon the forge belongs SE of the housing."""
    homes = [(300, 300), (360, 300), (300, 360)]
    assert "refining_forge_downwind" not in f_only(_forge_map(700, 700, homes), "refining_forge_downwind")  # SE of the housing
    assert "refining_forge_downwind" in f_only(_forge_map(60, 60, homes), "refining_forge_downwind")  # NW of it - straight upwind
    # ...and reversing the declared wind reverses the verdict, which is the whole point of the knob
    assert "refining_forge_downwind" in f_only(_forge_map(700, 700, homes, windward="SE"), "refining_forge_downwind")
    assert "refining_forge_downwind" not in f_only(_forge_map(60, 60, homes, windward="SE"), "refining_forge_downwind")


def test_refining_forge_downwind_abstains_when_the_map_has_no_dwellings():
    """Nothing to smoke over, nothing to judge - the rule must not divide by an empty centroid."""
    assert "refining_forge_downwind" not in f_only(_forge_map(60, 60, ()), "refining_forge_downwind")


def test_kiln_works_houses_its_workers_fires_on_a_lone_kiln():
    """The GM's question, 2026-07-27: "would whoever works the kiln also live next to it?" Yes, for
    three independent reasons - a firing is stoked in shifts for DAYS, the works stands at its CLAY
    rather than at its customers, and the trade was organized in kiln households living at their
    kilns (Song/Ming kiln districts first, Seto/Tokoname/Imado corroborating). So a kiln drawn as a
    lone glyph is recording a place nobody could work."""
    assert "kiln_works_houses_its_workers" in f_only(_kiln_map(quarters=()), "kiln_works_houses_its_workers")
    assert "kiln_works_houses_its_workers" not in f_only(_kiln_map(), "kiln_works_houses_its_workers")


def test_kiln_keeps_fire_gap_fires_on_a_cottage_against_the_kiln():
    """The housing is not banished with the work, but it does keep the ordinary gap. 60 real ft is
    the ATTENDED-fire rung of the separation ladder, shared with the refining forge: a firing is a
    very large fire, but somebody is stoking it, so it does not belong with the UNATTENDED charcoal
    stack at 30 ft nor with the 120 ft figures that defend against a smell carried on air."""
    # kiln body bottom edge is at 470 + 8; cottage half-height is 9
    tight = _kiln_map(quarters=((500.0, 470 + 8 + 20 + 9),))
    clear = _kiln_map(quarters=((500.0, 470 + 8 + 70 + 9),))
    assert "kiln_keeps_fire_gap" in f_only(tight, "kiln_keeps_fire_gap")
    assert "kiln_keeps_fire_gap" not in f_only(clear, "kiln_keeps_fire_gap")


def test_kiln_keeps_fire_gap_also_measures_the_settlements_own_structures():
    """Not just the works' own cottages - the gap is owed to every footprint on the map. A works
    whose own quarters stand clear but which crowds a neighbor's house is the same hazard."""
    assert "kiln_keeps_fire_gap" in f_only(_kiln_map(houses=[house(500, 470 - 8 - 20 - 9)]), "kiln_keeps_fire_gap")
    assert "kiln_keeps_fire_gap" not in f_only(_kiln_map(houses=[house(500, 470 - 8 - 70 - 9)]), "kiln_keeps_fire_gap")


def test_kiln_keeps_fire_gap_fails_a_record_that_cannot_be_measured():
    """A record with no `body` FAILS rather than skipping. This file's standing hazard is that a
    check which never runs looks exactly like a check that passes - and a kiln whose body is not
    recorded is precisely a fire gap nobody can measure, which is the worse of the two states."""
    assert "kiln_keeps_fire_gap" in f_only(_kiln_map(body=None), "kiln_keeps_fire_gap")


def test_kiln_keeps_fire_gap_is_measured_on_the_ROTATED_cottage():
    """The bug this guards: with the cottage recorded unrotated, a works turned on its side reports
    a gap that is wrong by the difference between the cottage's own width and height. Placed so the
    two readings straddle the 60 ft rule - the unrotated read passes and the true one fails."""
    # At rot=90 the body's drawn half-height is 23 (its 46 ft length now runs N-S), so its lower
    # edge is y=493; the cottage's is 14 read correctly and 9 read unrotated. y=564 therefore gives
    # a TRUE gap of 57 ft - which must fire - and a mis-read gap of 62 ft, which would not. Any
    # seat outside [562, 567) is read the same way by both and proves nothing; the first draft of
    # this test used one, passed under the revert, and was worthless.
    tight = _kiln_map(quarters=((500.0, 564.0),), rot=90.0)
    assert "kiln_keeps_fire_gap" in f_only(tight, "kiln_keeps_fire_gap")


# ---- found by the settlement-review agent, 2026-07-26 -------------------------------------------


def test_features_do_not_overlap_catches_a_crop_plot_in_a_watercourse():
    """The defect this feature was opened for, caught by the GENERAL rule with no pair-specific code."""
    plot = [[500, 500], [560, 500], [560, 560], [500, 560]]
    M = _mx_map(dry_plots=[{"poly": plot, "crop": "barley", "theta": 0}], streams=[{"poly": [[530, 400], [530, 700]], "w": 9}])
    assert "features_do_not_overlap" in f_only(M, "features_do_not_overlap")
    M["streams"] = [{"poly": [[900, 400], [900, 700]], "w": 9}]  # moved clear
    assert "features_do_not_overlap" not in f_only(M, "features_do_not_overlap")


def test_matrix_permits_an_annex_on_its_OWN_parent_only():
    """Strictly stronger than the blanket exemption it replaces: a kura behind its own shop is fine,
    the same kura drawn across a NEIGHBOR's building is a defect - which the blanket form could not
    express, and which the first pool run duly found twice."""
    own = _mx_map(buildings=[bldg(500, 500)], storehouses=[{"x": 500, "y": 512, "w": 20, "h": 14, "of": [500, 500]}])
    other = _mx_map(buildings=[bldg(500, 500), bldg(560, 500)], storehouses=[{"x": 556, "y": 500, "w": 20, "h": 14, "of": [500, 500]}])
    assert "features_do_not_overlap" not in f_only(own, "features_do_not_overlap")
    assert "features_do_not_overlap" in f_only(other, "features_do_not_overlap")


def test_matrix_permits_two_annexes_of_one_household_to_abut():
    M = _mx_map(
        houses=[house(500, 500)],
        threshing_yards=[yard(500, 540, of=(500, 500))],
        gardens=[garden(500, 552, of=(500, 500))],
    )
    assert "features_do_not_overlap" not in f_only(M, "features_do_not_overlap")


def test_matrix_permits_a_ditch_on_its_own_field_but_not_another():
    M = _mx_map(
        fields=[
            {
                "name": "west",
                "kind": "paddy",
                "outline": [[400, 400], [700, 400], [700, 700], [400, 700]],
                "bbox": [400, 400, 700, 700],
                "vis_bbox": [400, 400, 700, 700],
                "plots": [[60, 60, 550, 550, 4, 4]],
            }
        ],
        field_ditches=[{"poly": [[550, 400], [550, 700]], "w": 1.5, "field": "west", "role": "main"}],
        houses=[house(551, 480)],
    )
    fails = f(M)
    assert "features_do_not_overlap" in fails  # the HOUSE is on the ditch, and it is nobody's annex


def test_every_feature_classified_for_matrix_is_the_ratchet(monkeypatch):
    """A drawn key with no class must fail BY NAME - the whole promise is 'add one line and you are
    protected', which only holds if forgetting the line is loud."""
    M = _mx_map(houses=[house(500, 500)])
    assert "every_feature_classified_for_matrix" not in f_only(M, "every_feature_classified_for_matrix")
    monkeypatch.delitem(check_village.OVERLAP_CLASS, "houses")
    assert "every_feature_classified_for_matrix" in f_only(M, "every_feature_classified_for_matrix")


def test_matrix_reads_drawn_extents_not_envelopes():
    """A commons is an ENVELOPE around a sparse scatter and is permissive besides, so it is never
    even extracted; testing envelopes is what made the motivating survey over-report ~2x."""
    M = _mx_map(commons=[{"x": 500, "y": 500, "w": 400, "h": 400, "rot": 0, "role": "grazing", "poly": [[300, 300], [700, 300], [700, 700], [300, 700]]}], houses=[house(500, 500)])
    assert "features_do_not_overlap" not in f_only(M, "features_do_not_overlap")
    assert not [e for e in check_village.matrix_extents(M) if e[0] == "commons"]


def test_placement_runs_meet_their_ask_is_silent_when_the_ask_is_a_declared_budget():
    """fill=True means "place up to N" - the engine records no shortfall at all, so a district
    fill that seats a fraction of its budget is not drift and the check never sees it."""
    M = manifest()
    M["shortfalls"] = []
    assert "placement_runs_meet_their_ask" not in check_village.gate(M, verbose=False)


def test_waterworks_captions_stand_at_their_point():
    """A caption naming the intake weir, the settling basin or a sluice gate names a POINT the
    manifest records - so the check derives the subject instead of waiting for the gen to declare
    one. These captions are placed by hand with no referent, which is how they escaped both the
    standoff ladder and label_hugs_its_referent and ended up 195 and 348 ft from what they name."""
    M = manifest()
    M["aqueducts"] = [{"poly": [[100, 100], [300, 300]], "w": 3.0, "intake": [100, 100], "to": [300, 300]}]
    M["labels"] = [[900, 900, 980, 910, 5, "intake weir"]]
    assert "waterworks_captions_stand_at_their_point" in check_village.gate(M, verbose=False)


def test_waterworks_caption_beside_its_point_is_fine():
    """Beside it, not on it - a caption that touched its subject would read as part of the glyph."""
    M = manifest()
    M["aqueducts"] = [{"poly": [[100, 100], [300, 300]], "w": 3.0, "intake": [100, 100], "to": [300, 300]}]
    M["labels"] = [[104, 88, 170, 98, 5, "intake weir"]]
    assert "waterworks_captions_stand_at_their_point" not in check_village.gate(M, verbose=False)
