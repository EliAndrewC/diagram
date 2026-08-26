"""tier city tests split out of `tests.check_village.test_segments_02_capital_and_walls` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram import check_village
from tests.check_village._builders import (
    WALL,
    WALLSQ,
    _agri_city,
    _budget_city,
    _cap_gov,
    _cap_water,
    _capital_manifest,
    _door_city,
    _fort_city,
    _ring_towers,
    _scaled_city,
    bldg,
    f,
    f_only,
)


@pytest.mark.tiers("city")
def test_city_interior_fields_farmhouse_density_passes_when_densely_ringed():
    # a dense ring wrapping the WHOLE perimeter (top, bottom, both sides) - a worked in-wall field
    houses = (
        [{"x": x, "y": 330} for x in range(360, 545, 30)]
        + [{"x": x, "y": 570} for x in range(360, 545, 30)]
        + [{"y": y, "x": 330} for y in range(380, 525, 30)]
        + [{"y": y, "x": 570} for y in range(380, 525, 30)]
    )
    M = _agri_city(houses)
    assert "city_interior_fields_farmhouse_density" not in f_only(M, "city_interior_fields_farmhouse_density")


@pytest.mark.tiers("city")
def test_city_interior_fields_farmhouse_density_skipped_without_agricultural_district():
    # an ordinary city (no in-wall farming declared) is not held to the rule even if a field strays inside
    M = _agri_city([], agri=False)
    assert "city_interior_fields_farmhouse_density" not in f_only(M, "city_interior_fields_farmhouse_density")


@pytest.mark.tiers("city")
def test_city_interior_fields_farmhouse_density_skips_a_tiny_field_sliver():
    # an in-wall field too small to merit its own farmhouse ring (edge < 120px) is skipped, not flagged
    tiny = {"name": "tiny", "kind": "paddy", "bbox": [480, 480, 505, 505], "outline": [[480, 480], [505, 480], [505, 505], [480, 505]]}  # ~100px perimeter
    M = {"meta": {"scale": "city", "walled": True, "agricultural_district": True, "W": 1000, "H": 1000}, "wall": WALLSQ, "gates": [[500, 200], [500, 800]], "fields": [tiny], "houses": []}
    assert "city_interior_fields_farmhouse_density" not in f_only(M, "city_interior_fields_farmhouse_density")


@pytest.mark.tiers("city")
def test_city_wall_tower_coverage_exempts_the_kido_keepclear_band():
    # a 300px tower hole in a dense 30px ring on the west curtain: mid-hole, points lose their 2nd tower
    # (garrison R ~121: the 2nd comes from 30px beyond a hole edge, so the thin band is y~441-559) and the
    # check fires - unless the hole is a recorded ward-junction keep-clear (wall_tower_keepclears), the
    # band placement itself refuses to tower (the kido chokepoint; check keep-outs mirror placement
    # keep-outs, same as the water-gate exemption)
    tw = [t for t in _ring_towers(30) if not (t["x"] == 200 and 350 < t["y"] < 650)]
    assert "city_wall_tower_coverage" in f_only(_fort_city(wall_towers=tw), "city_wall_tower_coverage")
    assert "city_wall_tower_coverage" not in f_only(_fort_city(wall_towers=tw, wall_tower_keepclears=[[200, 500]]), "city_wall_tower_coverage")


@pytest.mark.tiers("city")
def test_city_wall_tower_coverage_fires_when_sparse():
    # only the 2 gate towers: the whole curtain between them sits out of flanking range of a 2nd tower
    M = _fort_city(wall_towers=[{"x": 500, "y": 200}, {"x": 500, "y": 800}])
    assert "city_wall_tower_coverage" in f_only(M, "city_wall_tower_coverage")


@pytest.mark.tiers("city")
def test_city_wall_tower_coverage_passes_when_densely_ringed():
    # a 60px-spaced ring keeps every curtain point within garrison range (328 ft / ~121 px) of >= 2 towers
    assert "city_wall_tower_coverage" not in f_only(_fort_city(wall_towers=_ring_towers(60)), "city_wall_tower_coverage")


@pytest.mark.tiers("city")
def test_city_wall_tower_coverage_siege_tier_demands_more_than_garrison():
    # the SAME 100px-spaced ring passes garrison (R~121) but fails siege (R~78, still >=2): the tier tightens it
    ring = _ring_towers(100)
    assert "city_wall_tower_coverage" not in f_only(_fort_city(wall_towers=ring), "city_wall_tower_coverage")
    siege = _fort_city(wall_towers=ring)
    siege["meta"] = {**siege["meta"], "wall_defense": "siege"}
    assert "city_wall_tower_coverage" in f_only(siege, "city_wall_tower_coverage")


@pytest.mark.tiers("city")
def test_wells_troughs_rails_clear_of_each_other_fires_on_nagaharas_rail_across_its_well():
    # the real GM-caught defect (2026-07-25), verbatim geometry: an 18px rail laid straight over a
    # wellhead roof square AND over the trough cluster hugging it - three glyphs on one spot
    M = {
        "meta": {"scale": "city", "W": 2000, "H": 2000, "ftpx": 3},
        "stable_yards": [
            {
                "x": 1390,
                "y": 1020,
                "r": 72.0,
                "of": [1390, 1020],
                "troughs": 2,
                "troughs_at": [1388.8, 1018.7],
                "troughs_box": [1386.5, 1015.9, 1391.1, 1021.5],
                "rails": [{"x": 1386.0, "y": 1016.2, "tx": 1.0, "ty": 0.0, "len": 18.0, "reach": 2.4}],
            }
        ],
        "wells": [{"x": 1381.0, "y": 1019.0, "r": 8, "vr": 4.0}],
    }
    fails = f(M)
    assert "wells_troughs_rails_clear_of_each_other" in fails


@pytest.mark.tiers("city")
def test_wells_troughs_rails_clear_of_each_other_fires_when_a_rail_reaches_a_NEIGHBOR_yards_troughs():
    # the cross-yard hole the dung-heap rule had to be widened for twice: two yards sit close
    # enough that yard A's rail lies over yard B's trough cluster - a pair no within-one-yard
    # loop would ever measure. Rail spans x 491-509; B's cluster starts at 503.7.
    M = {
        "meta": {"scale": "city", "W": 1000, "H": 1000, "ftpx": 3},
        "stable_yards": [
            {"x": 480, "y": 500, "r": 72.0, "of": [480, 500], "troughs": 0, "rails": [{"x": 500, "y": 500, "tx": 1.0, "ty": 0.0, "len": 18.0, "reach": 2.4}]},
            {"x": 560, "y": 500, "r": 72.0, "of": [560, 500], "troughs": 2, "troughs_at": [506.0, 500.0], "troughs_box": [503.7, 497.2, 508.3, 502.8], "rails": []},
        ],
        "wells": [{"x": 512, "y": 500, "r": 8, "vr": 4.0}],
    }
    assert "wells_troughs_rails_clear_of_each_other" in f_only(M, "wells_troughs_rails_clear_of_each_other")


@pytest.mark.tiers("city")
def test_wells_troughs_rails_clear_of_each_other_fires_on_two_wellheads_sunk_on_one_spot():
    # wells are placed by machinery that predates the yards entirely, so the rule has to cover the
    # well/well pair too - two roof squares 5px apart are one unreadable blob
    M = {
        "meta": {"scale": "city", "W": 1000, "H": 1000, "ftpx": 3},
        "wells": [{"x": 800, "y": 800, "r": 8, "vr": 4.0}, {"x": 805, "y": 803, "r": 8, "vr": 4.0}],
    }
    assert "wells_troughs_rails_clear_of_each_other" in f_only(M, "wells_troughs_rails_clear_of_each_other")


@pytest.mark.tiers("city")
def test_wells_troughs_rails_clear_of_each_other_passes_when_the_three_stand_side_by_side():
    # the rule is GLYPH-level, not a working clearance: the troughs are SUPPOSED to hug their well
    # (the bucket-pour relay) and animals stand between rail and trough, so a cluster 1.6px off the
    # roof square and a rail a short walk away are all correct. Near is right; on top of is not.
    M = {
        "meta": {"scale": "city", "W": 1000, "H": 1000, "ftpx": 3},
        "stable_yards": [
            {
                "x": 500,
                "y": 500,
                "r": 72.0,
                "of": [500, 500],
                "troughs": 2,
                "troughs_at": [492.1, 500.0],
                "troughs_box": [489.8, 497.2, 494.4, 502.8],
                "rails": [{"x": 500, "y": 540, "tx": 1.0, "ty": 0.0, "len": 18.0, "reach": 2.4}],
                "dung_heaps": [],
            }
        ],
        "wells": [{"x": 500, "y": 500, "r": 8, "vr": 4.0}, {"x": 470, "y": 500, "r": 8, "vr": 4.0}],
    }
    assert "wells_troughs_rails_clear_of_each_other" not in f_only(M, "wells_troughs_rails_clear_of_each_other")


@pytest.mark.tiers("city")
def test_vegetable_tracts_skip_the_farmstead_ring_checks():
    # kind="vegetable" in-wall garden tracts are worked by the surrounding quarters (well/
    # night-soil fed urban plots), so neither field_ringed nor the in-wall agricultural
    # farmhouse-density ring applies to them - only paddy carries farmsteads
    M = {
        "meta": {"scale": "city", "walled": True, "agricultural_district": True, "ftpx": 3, "W": 1000, "H": 1000},
        "wall": WALL + [WALL[0]],
        "fields": [{"name": "vg1", "kind": "vegetable", "bbox": [400, 400, 600, 600], "outline": [[400, 400], [600, 400], [600, 600], [400, 600]]}],
        "houses": [],
    }
    fails = f(M)
    assert "field_ringed[vg1]" not in fails
    assert "city_interior_fields_farmhouse_density" not in fails


@pytest.mark.tiers("city")
def test_city_wall_matches_budget_fires_when_no_budget_is_declared():
    # budget-first is the city workflow: a walled city without meta.budget is unsized by construction
    assert "city_wall_matches_budget" in f_only(_budget_city(), "city_wall_matches_budget")


@pytest.mark.tiers("city")
def test_city_wall_matches_budget_fires_on_over_enclosure():
    # required 300k, enclosed 360k = +20% - the empty-space defect (unjustified open ground)
    assert "city_wall_matches_budget" in f_only(_budget_city({"required_interior_px2": 300_000.0}), "city_wall_matches_budget")


@pytest.mark.tiers("city")
def test_city_wall_matches_budget_fires_on_under_enclosure():
    # required 400k, enclosed 360k = -10% - the wall cannot hold the program
    assert "city_wall_matches_budget" in f_only(_budget_city({"required_interior_px2": 400_000.0}), "city_wall_matches_budget")


@pytest.mark.tiers("city")
def test_city_wall_matches_budget_passes_within_tolerance():
    # required 350k, enclosed 360k = +2.9% - inside +8%/-5%
    assert "city_wall_matches_budget" not in f_only(_budget_city({"required_interior_px2": 350_000.0}), "city_wall_matches_budget")


@pytest.mark.tiers("city")
def test_city_house_doors_unblocked_fires_when_a_door_opens_into_a_back_wall():
    # two rot=0 rows 1.5px apart (an eave gap): the TOP row's door (facing down) opens straight
    # into the bottom row's back wall - the defect the GM flagged on the shipped cities
    top = [bldg(300 + i * 41, 300, "laborer", w=40, h=24) for i in range(3)]
    bot = [bldg(300 + i * 41, 300 + 24 + 1.5, "laborer", w=40, h=24) for i in range(3)]
    assert "city_house_doors_unblocked" in f_only(_door_city(top + bot), "city_house_doors_unblocked")


@pytest.mark.tiers("city")
def test_city_house_doors_unblocked_passes_back_to_back_pair_facing_outward():
    # the SAME two rows with the top row rotated 180 (door up, into open ground): a proper
    # back-to-back nagaya pair - both doors open outward
    top = [bldg(300 + i * 41, 300, "laborer", rot=180, w=40, h=24) for i in range(3)]
    bot = [bldg(300 + i * 41, 300 + 24 + 1.5, "laborer", w=40, h=24) for i in range(3)]
    assert "city_house_doors_unblocked" not in f_only(_door_city(top + bot), "city_house_doors_unblocked")


@pytest.mark.tiers("city")
def test_city_house_doors_unblocked_passes_across_a_walkable_roji():
    # facing rows separated by a walkable lane (>= ~10 real ft): doors open onto the roji, fine
    top = [bldg(300 + i * 41, 300, "laborer", w=40, h=24) for i in range(3)]  # door down
    bot = [bldg(300 + i * 41, 300 + 24 + 5.0, "laborer", rot=180, w=40, h=24) for i in range(3)]  # door up
    assert "city_house_doors_unblocked" not in f_only(_door_city(top + bot), "city_house_doors_unblocked")


@pytest.mark.tiers("city")
def test_city_house_doors_unblocked_respects_rotation_axes():
    # a west-facing house (rot=90: door toward -x) with a neighbor tight on its WEST is blocked;
    # the same neighbor on its EAST, facing EAST itself (rot=270), is a proper back-to-back
    # partner - fine (both doors outward on the E-W axis)
    house = bldg(300, 300, "laborer", rot=90, w=40, h=24)
    west = bldg(300 - 24 / 2 - 1.5 - 12, 300, "laborer", rot=90, w=40, h=24)
    east = bldg(300 + 24 / 2 + 1.5 + 12, 300, "laborer", rot=270, w=40, h=24)
    assert "city_house_doors_unblocked" in f_only(_door_city([house, west]), "city_house_doors_unblocked")
    assert "city_house_doors_unblocked" not in f_only(_door_city([house, east]), "city_house_doors_unblocked")


@pytest.mark.tiers("city")
def test_city_rows_max_two_deep_fires_on_a_three_deep_stack():
    # three eave-gapped rows: the middle row has walls hard against BOTH long faces - trapped
    rows = []
    for r in range(3):
        rows += [bldg(300 + i * 41, 300 + r * (24 + 1.5), "laborer", rot=(180 if r == 0 else 0), w=40, h=24) for i in range(3)]
    assert "city_rows_max_two_deep" in f_only(_door_city(rows), "city_rows_max_two_deep")


@pytest.mark.tiers("city")
def test_city_rows_max_two_deep_passes_pairs_split_by_roji():
    # 2 rows + walkable gap + 2 rows: nobody is trapped (the canonical pair cadence)
    rows = []
    y = 300.0
    for r in range(4):
        rows += [bldg(300 + i * 41, y, "laborer", rot=(180 if r % 2 == 0 else 0), w=40, h=24) for i in range(3)]
        y += 24 + (5.0 if r % 2 else 1.5)
    assert "city_rows_max_two_deep" not in f_only(_door_city(rows), "city_rows_max_two_deep")


@pytest.mark.tiers("city")
def test_city_rows_max_two_deep_ignores_side_by_side_terraces():
    # a long terrace of party-wall units (touching along w) is the doctrine, not a violation
    row = [bldg(300 + i * 40.4, 300, "laborer", w=40, h=24) for i in range(8)]
    assert "city_rows_max_two_deep" not in f_only(_door_city(row), "city_rows_max_two_deep")


@pytest.mark.tiers("city")
def test_merchant_estate_wall_checks_skip_maps_without_estates():
    assert "merchant_estate_wall_clear_of_water" not in f_only({"meta": {"scale": "city"}, "docks": [{"x": 540, "y": 490, "w": 54, "h": 34, "rot": 0}]}, "merchant_estate_wall_clear_of_water")


@pytest.mark.tiers("city")
def test_cremation_ground_to_scale_fires_oversized_passes_in_band():
    # the old fixed 116x80px glyph at 3 ft/px = 348x240 ft - bigger than the crematory serving metropolitan Edo
    assert "cremation_ground_to_scale" in f_only(_scaled_city(cremation_grounds=[{"x": 500, "y": 500, "w": 116, "h": 80, "rot": 0}]), "cremation_ground_to_scale")
    # a 129x90 ft city ground (43x30px) is inside the 80-160 ft city band
    assert "cremation_ground_to_scale" not in f_only(_scaled_city(cremation_grounds=[{"x": 500, "y": 500, "w": 43, "h": 30, "rot": 0}]), "cremation_ground_to_scale")


@pytest.mark.tiers("city")
def test_ossuary_to_scale_fires_oversized_passes_in_band():
    # the old fixed mound = 276x180 ft - kofun-sized; a pauper bone mound is 10-30 ft. The band top is
    # 32 ft (tightened 2026-07-21): the earlier legibility-sized glyph (9px floor -> 54 real ft at city
    # scale, w=18px) must now FIRE; the true-size glyph (4.5px floor -> 27 ft, w=9px) passes.
    assert "ossuary_to_scale" in f_only(_scaled_city(ossuaries=[{"x": 500, "y": 500, "w": 92, "h": 60, "rot": 0}]), "ossuary_to_scale")
    assert "ossuary_to_scale" in f_only(_scaled_city(ossuaries=[{"x": 500, "y": 500, "w": 18, "h": 12, "rot": 0}]), "ossuary_to_scale")
    assert "ossuary_to_scale" not in f_only(_scaled_city(ossuaries=[{"x": 500, "y": 500, "w": 9, "h": 5.6, "rot": 0}]), "ossuary_to_scale")


@pytest.mark.tiers("city")
def test_burial_grounds_sized_to_population_passes_the_city_split():
    # ~1.8 acres split across common ground + parish yards is inside the 0.4-2.2 acre city band
    M = _scaled_city(cemeteries=[{"x": 500, "y": 500, "w": 90, "h": 64, "rot": 0}, {"x": 800, "y": 500, "w": 44, "h": 32, "rot": 0}, {"x": 900, "y": 700, "w": 44, "h": 32, "rot": 0}])
    assert "burial_grounds_sized_to_population" not in f_only(M, "burial_grounds_sized_to_population")


@pytest.mark.parametrize(
    "frac,fires",
    [
        (1.00, False),  # exactly on budget
        (1.07, False),  # inside the +8% tolerance
        (0.96, False),  # inside the -5% tolerance
        (1.20, True),  # over-enclosed: the empty-space defect
        (0.80, True),  # the wall cannot hold the program
    ],
)
@pytest.mark.tiers("capital")
def test_capital_wall_matches_budget_fires_only_outside_the_declared_tolerances(frac, fires):
    fired = "capital_wall_matches_budget" in check_village.gate(_capital_manifest(interior_frac=frac))
    assert fired is fires


@pytest.mark.tiers("capital", "city")
def test_capital_wall_matches_budget_reuses_the_provincial_tolerances():
    """Inherited deliberately - they are pinned by the shipped-Tango / rejected-Nagahara pair, and
    nothing about a capital argues for different slack."""
    assert check_village.BUDGET_TOL_OVER == 0.08
    assert check_village.BUDGET_TOL_UNDER == 0.05


@pytest.mark.tiers("capital")
def test_a_capital_that_declares_no_budget_FAILS_rather_than_skipping_the_conformance_check():
    """The FR-015 ratchet. Without it the map would skip capital_wall_matches_budget entirely and
    show green - and a check that never RUNS looks exactly like a check that passes."""
    failures = check_village.gate(_capital_manifest(budget=False))
    assert "capital_declares_a_budget" in failures
    assert "capital_wall_matches_budget" not in failures  # it has nothing to compare against


@pytest.mark.tiers("capital")
def test_a_capital_that_declares_a_budget_passes_the_ratchet():
    assert "capital_declares_a_budget" not in check_village.gate(_capital_manifest())


@pytest.mark.parametrize("scale", ["village", "town", "city"])
@pytest.mark.tiers("capital")
def test_neither_capital_check_runs_on_any_other_scale(scale):
    failures = check_village.gate(_capital_manifest(budget=False, scale=scale))
    assert "capital_declares_a_budget" not in failures
    assert "capital_wall_matches_budget" not in failures


@pytest.mark.tiers("capital")
def test_capital_has_six_ministries_fires_when_one_is_missing():
    M = _cap_gov()
    M["ministries"] = [m for m in M["ministries"] if m["name"] != "Ministry of War"]
    assert "capital_has_six_ministries" in f_only(M, "capital_has_six_ministries")


@pytest.mark.tiers("capital")
def test_capital_school_check_fires_when_absent():
    M = _cap_gov()
    M["ministries"] = [m for m in M["ministries"] if m["name"].startswith("Ministry of")]
    assert "capital_has_domain_school" in f_only(M, "capital_has_domain_school")


@pytest.mark.tiers("capital")
def test_capital_chancellery_fires_when_a_compound_is_drawn():
    """The council of lineage representatives meets IN the castle (GM 2026-08-09, researched:
    Edo's Hyojosho/Roju within the castle, China's Grand Secretariat inside the palace) - a
    chancellery compound outside is the defect, not the requirement."""
    M = _cap_gov()
    M["ministries"].append({"x": 435, "y": 800, "w": 70, "h": 48, "name": "House Chancellery"})
    assert "capital_chancellery_meets_in_the_castle" in f_only(M, "capital_chancellery_meets_in_the_castle")


@pytest.mark.tiers("capital")
def test_capital_domain_school_may_be_the_hanko_record():
    M = _cap_gov()
    M["ministries"] = [m for m in M["ministries"] if m["name"] != "Domain School"]
    M["martial_halls"] = [{"x": 565, "y": 800, "w": 80, "h": 50, "rot": 0, "label": "Domain School", "range_ft": 100, "kind": "hanko"}]
    fails = f(M)
    assert "capital_has_domain_school" not in fails
    assert "capital_school_on_the_axis" not in fails


@pytest.mark.tiers("capital")
def test_capital_castle_approach_fires_when_no_way_leaves_the_castle_gate():
    M = _cap_gov()
    M["roads"] = [{"pts": [[500, 700], [500, 1000]], "w": 26}]
    fails = f(M)
    assert "capital_castle_has_approach_avenue" in fails
    # ...and the checks that need the avenue SKIP rather than crash or misfire
    assert "capital_ministries_front_the_avenue" not in fails


@pytest.mark.tiers("capital")
def test_capital_ministries_front_the_avenue_fires_on_a_strayed_ministry():
    M = _cap_gov()
    war = next(m for m in M["ministries"] if m["name"] == "Ministry of War")
    war["x"], war["y"] = 850, 700  # off in the samurai ground, nowhere near the ote-suji
    assert "capital_ministries_front_the_avenue" in f_only(M, "capital_ministries_front_the_avenue")


@pytest.mark.tiers("capital")
def test_capital_school_on_the_axis_fires_when_it_strays():
    M = _cap_gov()
    sc = next(m for m in M["ministries"] if m["name"] == "Domain School")
    sc["x"] = 200  # far off the avenue's extended line
    assert "capital_school_on_the_axis" in f_only(M, "capital_school_on_the_axis")


@pytest.mark.tiers("capital")
def test_capital_government_offices_dont_abut_fires_on_touching_offices():
    M = _cap_gov()
    works = next(m for m in M["ministries"] if m["name"] == "Ministry of Works")
    works["y"] = 455  # 5px above War's footprint - inside the 14px standoff
    assert "capital_government_offices_dont_abut" in f_only(M, "capital_government_offices_dont_abut")


@pytest.mark.tiers("capital")
def test_capital_declares_lineages_fires_when_the_declaration_is_missing():
    """The FR-015 ratchet again: without the declaration every lineage check would SKIP while
    showing green, so the missing declaration is itself the failure."""
    M = _cap_gov()
    del M["meta"]["lineages"]
    fails = f(M)
    assert "capital_declares_lineages" in fails
    assert "capital_lineage_compounds_labeled" not in fails
    assert "capital_lineage_bands_visibly_distinct" not in fails


@pytest.mark.tiers("capital")
def test_capital_lineage_compounds_labeled_fires_on_a_missing_lineage():
    M = _cap_gov()
    M["manors"] = [m for m in M["manors"] if m.get("lineage") != "kurogi"]
    assert "capital_lineage_compounds_labeled" in f_only(M, "capital_lineage_compounds_labeled")


@pytest.mark.tiers("capital")
def test_capital_lineage_compounds_labeled_fires_on_an_unlabeled_compound():
    M = _cap_gov()
    M["manors"][0]["label"] = ""  # the compound stands but nothing names it
    assert "capital_lineage_compounds_labeled" in f_only(M, "capital_lineage_compounds_labeled")


@pytest.mark.tiers("capital")
def test_capital_ruling_lineage_gets_no_compound():
    M = _cap_gov()
    M["manors"][3]["lineage"] = "daika"
    M["manors"][3]["label"] = "Daika Estate"
    assert "capital_ruling_lineage_seat_is_the_castle" in f_only(M, "capital_ruling_lineage_seat_is_the_castle")


@pytest.mark.tiers("capital")
def test_capital_castle_without_a_gate_record_is_skipped_by_the_avenue_scan():
    M = _cap_gov()
    del M["castles"][0]["gate"]
    assert "capital_castle_has_approach_avenue" in f_only(M, "capital_castle_has_approach_avenue")  # no gate to anchor an avenue on


@pytest.mark.tiers("capital")
def test_capital_ruling_lineage_may_be_declared_in_the_band_map():
    """A gen may declare all nine lineages with bands, the ruling one among them - it is skipped
    rather than demanded a compound (its seat is the castle)."""
    M = _cap_gov()
    M["meta"]["lineages"] = {**M["meta"]["lineages"], "daika": "grand"}
    fails = f(M)
    assert "capital_lineage_compounds_labeled" not in fails
    assert "capital_ruling_lineage_seat_is_the_castle" not in fails


@pytest.mark.tiers("capital")
def test_capital_aqueduct_with_no_recorded_channel_is_skipped():
    M = _cap_water()
    M["aqueducts"] = [{"poly": [], "w": 8}]  # an empty channel - nothing to judge
    assert "capital_aqueduct_terminates_at_a_gate" not in f_only(M, "capital_aqueduct_terminates_at_a_gate")


@pytest.mark.tiers("capital", "city")
def test_capital_estate_labels_inside_fires_on_an_outside_caption():
    """A city estate's caption lives INSIDE its blank court (GM 2026-08-09) - hung outside it
    sits where 021's fabric must flow."""
    M = _cap_gov()
    M["labels"] = [[80, 120, 220, 136, 5, "Hazama Estate"]]  # above the walls, the old convention
    assert "capital_estate_labels_inside" in f_only(M, "capital_estate_labels_inside")
    M["labels"] = [[110, 195, 190, 209, 5, "Hazama Estate"]]  # within the court
    assert "capital_estate_labels_inside" not in f_only(M, "capital_estate_labels_inside")


@pytest.mark.tiers("capital")
def test_capital_lineage_bands_visibly_distinct_fires_on_a_band_size_collision():
    M = _cap_gov()
    kurogi = next(m for m in M["manors"] if m["lineage"] == "kurogi")
    kurogi["w"], kurogi["h"] = 145, 114  # numerically below the grand band, visually identical
    assert "capital_lineage_bands_visibly_distinct" in f_only(M, "capital_lineage_bands_visibly_distinct")


@pytest.mark.tiers("capital")
def test_capital_waterfront_checks_pass_on_the_fixture():
    fails = f(_cap_water())
    for c in ("capital_has_aqueduct", "capital_aqueduct_terminates_at_a_gate", "capital_aqueduct_stays_outside_the_wall", "capital_no_road_parallels_river"):
        assert c not in fails, c


@pytest.mark.tiers("capital")
def test_capital_has_aqueduct_fires_when_absent():
    M = _cap_water()
    M["aqueducts"] = []
    assert "capital_has_aqueduct" in f_only(M, "capital_has_aqueduct")


@pytest.mark.tiers("capital")
def test_capital_aqueduct_terminates_at_a_gate_fires_far_from_any_gate():
    M = _cap_water()
    M["aqueducts"][0]["poly"][-1] = [1030, 800]
    assert "capital_aqueduct_terminates_at_a_gate" in f_only(M, "capital_aqueduct_terminates_at_a_gate")


@pytest.mark.tiers("capital")
def test_capital_aqueduct_stays_outside_the_wall_fires_on_an_interior_channel():
    M = _cap_water()
    M["aqueducts"][0]["poly"].append([500, 500])  # an open cut through the walled interior
    assert "capital_aqueduct_stays_outside_the_wall" in f_only(M, "capital_aqueduct_stays_outside_the_wall")


@pytest.mark.tiers("capital")
def test_capital_no_road_parallels_river_fires_on_a_shadowing_road():
    M = _cap_water()
    M["roads"] = [{"pts": [[1180, 0], [1180, 1000]], "w": 26}]  # a trunk road hugging the bank end to end
    assert "capital_no_road_parallels_river" in f_only(M, "capital_no_road_parallels_river")


@pytest.mark.tiers("capital")
def test_capital_no_road_parallels_river_passes_a_bridged_crossing():
    M = _cap_water()
    M["roads"] = [{"pts": [[900, 500], [1400, 500]], "w": 26}]  # ACROSS the river, not along it
    M["bridges"] = [{"x": 1200, "y": 500, "rot": 0, "span": 68, "w": 26}]
    assert "capital_no_road_parallels_river" not in f_only(M, "capital_no_road_parallels_river")
