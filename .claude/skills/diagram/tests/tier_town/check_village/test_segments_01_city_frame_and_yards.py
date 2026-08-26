"""tier town tests split out of `tests.check_village.test_segments_01_city_frame_and_yards` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram import check_village
from tests.check_village._builders import (
    _farrier_map,
    bldg,
    f_only,
    garden,
    house,
    manifest,
    yard,
)


@pytest.mark.tiers("town")
def test_imperial_road_town_farrier_is_gated_on_the_declaration():
    # the deliberate Hoshizora/Hirameki split: a relay/post town ON the Imperial Road works
    # courier and caravan horses hard enough to keep a forge; a market town off the road does not,
    # so the check is gated on meta(imperial_road=True) rather than on town scale alone
    M = _farrier_map(320, 200, imperial_road=True)
    M["farriers"] = []
    assert "imperial_road_town_has_farrier" in f_only(M, "imperial_road_town_has_farrier")
    off_road = _farrier_map(320, 200)
    off_road["farriers"] = []
    assert "imperial_road_town_has_farrier" not in f_only(off_road, "imperial_road_town_has_farrier")


@pytest.mark.tiers("town")
def test_population_consistent_with_housing_fires_when_dwellings_too_few():
    # population is dwellings x5, not total buildings x5; 10 dwellings imply ~50 residents, not 3000
    M = {"meta": {"scale": "town", "walled": False, "population": 3000}, "buildings": [bldg(120 + i * 60, 120, kind="laborer") for i in range(10)]}
    assert "population_consistent_with_housing" in f_only(M, "population_consistent_with_housing")


@pytest.mark.tiers("town")
def test_structures_clear_of_trees_fires_when_a_crown_is_drawn_over_a_building():
    # a tree drawn on a roof erases the building - no drawn crown may overlap any ROOFED footprint,
    # and a ROTATED building is covered conservatively by its half-diagonal (as at placement).
    base = manifest(meta={"scale": "town"}, houses=[bldg(300, 300, "laborer")])
    assert "structures_clear_of_trees" in f_only({**base, "buildings": [bldg(600, 600, "servant")], "tree_crowns": [618, 600, 8]}, "structures_clear_of_trees")
    assert "structures_clear_of_trees" not in f_only({**base, "buildings": [bldg(600, 600, "servant")], "tree_crowns": [660, 600, 8]}, "structures_clear_of_trees")
    # ... every roofed kind counts, not just dwellings (here a storehouse), and a crown that only
    # reaches the OPEN yard beside a building is fine - yards have their own sun rules
    assert "structures_clear_of_trees" in f_only({**base, "storehouses": [{"x": 800, "y": 800, "w": 40, "h": 30, "rot": 0}], "tree_crowns": [822, 800, 6]}, "structures_clear_of_trees")
    assert "structures_clear_of_trees" not in f_only({**base, "threshing_yards": [yard(800, 800, of=(300, 300))], "tree_crowns": [800, 800, 6]}, "structures_clear_of_trees")


@pytest.mark.tiers("town")
def test_settlement_has_charcoal_yard_fires_only_when_the_district_is_declared():
    """Opt-in, like meta(granary=True): an ordinary county seat declares nothing and is exempt."""
    M = manifest(meta={"scale": "town", "ftpx": 1, "W": 1000, "H": 1000, "charcoal_district": True})
    assert "settlement_has_charcoal_yard" in f_only(M, "settlement_has_charcoal_yard")
    del M["meta"]["charcoal_district"]
    assert "settlement_has_charcoal_yard" not in f_only(M, "settlement_has_charcoal_yard")


@pytest.mark.tiers("town")
def test_settlement_has_refining_forge_fires_only_when_the_district_is_declared():
    M = manifest(meta={"scale": "town", "ftpx": 1, "W": 1000, "H": 1000, "iron_district": True})
    assert "settlement_has_refining_forge" in f_only(M, "settlement_has_refining_forge")
    del M["meta"]["iron_district"]
    assert "settlement_has_refining_forge" not in f_only(M, "settlement_has_refining_forge")


@pytest.mark.tiers("town")
def test_manor_walls_clear_of_ways_fires_on_a_road_through_the_compound():
    """`manors` lives in _OVERLAP_TARGETS - the registry of things others must avoid - and never in
    _OVERLAP_STRUCTS, so the whole no_structure_on_* battery reads a manor as a hazard and nothing
    reads it as a candidate. The compound's own wall was ungoverned against the roadbed, and a trunk
    road ran 18 px inside a magistracy's south wall with the gate fully green."""
    M = manifest(meta={"scale": "town", "ftpx": 1, "W": 1200, "H": 1200})
    M["manors"] = [{"x": 600, "y": 300, "w": 290, "h": 200, "rot": 0, "label": "Magistrate's Manor"}]
    M["road"], M["road_width"] = [[0, 395], [1200, 395]], 26  # north edge 382, INSIDE the south wall at 400
    assert "manor_walls_clear_of_ways" in f_only(M, "manor_walls_clear_of_ways")
    M["road"] = [[0, 460], [1200, 460]]  # north edge 447, clear of it
    assert "manor_walls_clear_of_ways" not in f_only(M, "manor_walls_clear_of_ways")


@pytest.mark.tiers("town")
def test_structures_stay_on_their_side_of_a_border():
    """A border is overlap-EXEMPT so a frontier compound may stand its WALL on the line - but that
    is not licence to build ACROSS it. The test is on the CENTER, which is exactly what keeps the
    deliberate case legal while catching a garden that wandered onto the neighbor's ground."""

    def bmap(*extra_buildings, **kw):
        M = manifest(meta={"scale": "town", "ftpx": 1, "W": 1200, "H": 1200})
        M["borders"] = [{"poly": [[900, 0], [900, 1200]], "label": "the Fox border"}]
        M["houses"] = [house(400, 400), house(460, 400), house(400, 460)]  # the settlement is WEST
        M.update(kw)
        M["buildings"] = list(extra_buildings)
        return M

    assert "structures_stay_on_their_side_of_a_border" not in f_only(bmap(bldg(600, 400)), "structures_stay_on_their_side_of_a_border")
    assert "structures_stay_on_their_side_of_a_border" in f_only(bmap(bldg(1000, 400)), "structures_stay_on_their_side_of_a_border")  # over the line
    # a garden or a yard counts too - it is our ground being claimed, not just our roofs
    assert "structures_stay_on_their_side_of_a_border" in f_only(bmap(gardens=[garden(1020, 500)]), "structures_stay_on_their_side_of_a_border")
    # ...and a compound whose WALL sits on the line but whose CENTER is ours stays legal
    assert "structures_stay_on_their_side_of_a_border" not in f_only(bmap(manors=[{"x": 755, "y": 300, "w": 290, "h": 200, "rot": 0, "label": "M"}]), "structures_stay_on_their_side_of_a_border")


@pytest.mark.tiers("town")
def test_border_checks_abstain_when_there_is_no_border_or_no_housing():
    """A map with no drawn border has no side to be on, and one with no dwellings has no side to
    judge from - neither may raise a finding, and neither may crash."""
    M = manifest(meta={"scale": "town", "ftpx": 1, "W": 1200, "H": 1200}, buildings=[bldg(1000, 400)])
    assert "structures_stay_on_their_side_of_a_border" not in f_only(M, "structures_stay_on_their_side_of_a_border")
    M["borders"] = [{"poly": [[900, 0], [900, 1200]], "label": "b"}]
    M["buildings"] = []
    assert "structures_stay_on_their_side_of_a_border" not in f_only(M, "structures_stay_on_their_side_of_a_border")


@pytest.mark.tiers("town")
def test_farmsteads_reach_their_fields_unsevered_fires_across_a_road():
    # every reachable field vertex lies across the road from the house -> severed (hoshizora's
    # lone south-of-road farmhouse inside the merchant block, GM 2026-08-02)
    field = {"name": "f1", "kind": "paddy", "bbox": [300, 550, 450, 650], "outline": [[300, 550], [450, 550], [450, 650], [300, 650]]}
    M = {
        "meta": {"scale": "town", "ftpx": 1, "W": 1000, "H": 1000},
        "fields": [field],
        "roads": [{"pts": [[0, 675], [1000, 675]], "w": 26}],
        "houses": [house(500, 700)],
    }
    assert "farmsteads_reach_their_fields_unsevered" in f_only(M, "farmsteads_reach_their_fields_unsevered")
    # a second field on the house's own side of the road un-severs it
    M["fields"].append({"name": "f2", "kind": "paddy", "bbox": [600, 700, 750, 800], "outline": [[600, 700], [750, 700], [750, 800], [600, 800]]})
    assert "farmsteads_reach_their_fields_unsevered" not in f_only(M, "farmsteads_reach_their_fields_unsevered")


@pytest.mark.tiers("town")
def test_placement_runs_meet_their_ask_spares_a_run_that_missed_by_a_hair():
    """A row that seats all but a couple has met its ask - the two pool towns that record a
    shortfall at all (Ubame 21/23, Hirameki 13/14) are exactly this case and must stay green."""
    M = manifest()
    M["shortfalls"] = [{"by": "pack", "at": [10, 10, 200, 200], "placed": 21, "wanted": 23, "dropped": "servant x2"}]
    assert "placement_runs_meet_their_ask" not in check_village.gate(M, verbose=False)


@pytest.mark.tiers("capital", "town")
def test_roadside_works_stand_on_their_road():
    """A doss-house exists to catch travelers off a particular road, and a kiln carts its fuel
    along one - so both stand on that way and lie along it. Nine flophouses on the capital came out
    level while their roads ran at 138-167 degrees, and one sat ~300 ft off the road entirely."""
    M = manifest()
    M["town_streets"] = [{"pts": [[100, 100], [900, 100]], "w": 18}]
    M["flophouses"] = [{"x": 500, "y": 130, "w": 34, "h": 15, "rot": 90, "label": "flophouse"}]
    assert "roadside_works_stand_on_their_road" in check_village.gate(M, verbose=False)


@pytest.mark.tiers("town")
def test_roadside_work_lying_along_its_road_is_fine():
    M = manifest()
    M["town_streets"] = [{"pts": [[100, 100], [900, 100]], "w": 18}]
    M["flophouses"] = [{"x": 500, "y": 130, "w": 34, "h": 15, "rot": 0, "label": "flophouse"}]
    assert "roadside_works_stand_on_their_road" not in check_village.gate(M, verbose=False)


@pytest.mark.tiers("town")
def test_a_kiln_carries_no_distance_rule_only_an_angle():
    """A nuisance works belongs OUT of town by its nature - the rule for it is alignment, not
    proximity (the pool's kilns sit 482-1517 ft from the nearest way, correctly)."""
    M = manifest()
    M["town_streets"] = [{"pts": [[100, 100], [900, 100]], "w": 18}]
    M["kilns"] = [{"x": 500, "y": 900, "w": 46, "h": 40, "rot": 0, "label": "kiln works"}]
    assert "roadside_works_stand_on_their_road" not in check_village.gate(M, verbose=False)


@pytest.mark.tiers("town")
def test_manor_walls_fire_when_a_way_ENDS_inside_the_compound():
    """The _mw_gap helper returns 0.0 the moment a way SEGMENT ENDPOINT lies inside the wall
    rect - the crossing loop never runs. Before feature 022 this branch was only reached
    incidentally by regression fixtures' full-gate replays; the targeted replay no longer runs it
    there, so the branch gets the deterministic unit test it always deserved: a road DEAD-ENDING
    in the court is as illegal as one passing through."""
    M = manifest(meta={"scale": "town", "ftpx": 1, "W": 1200, "H": 1200})
    M["manors"] = [{"x": 600, "y": 300, "w": 290, "h": 200, "rot": 0, "label": "Magistrate's Manor"}]
    M["road"], M["road_width"] = [[0, 300], [600, 300]], 26  # terminates ON the manor center
    assert "manor_walls_clear_of_ways" in f_only(M, "manor_walls_clear_of_ways")
