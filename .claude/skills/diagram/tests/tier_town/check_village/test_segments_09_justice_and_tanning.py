"""tier town tests split out of `tests.check_village.test_segments_09_justice_and_tanning` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import WALL, _dw, _justice_town, _tower, _ty_map, _wf_map, bldg, bstone, exground, f_only, house


@pytest.mark.tiers("town")
def test_streets_have_buildings_fires_when_building_fronts_the_other_street():
    M = {
        "meta": {"scale": "town", "walled": True},
        "wall": WALL,
        "town_streets": [
            {"pts": [[700, 380], [700, 620]], "w": 18},  # the lane (should read empty)
            {"pts": [[200, 500], [950, 500]], "w": 22, "main": True},  # the cross it actually fronts
        ],
        "buildings": [bldg(760, 500)],  # nearest the cross, not the lane
    }
    assert "streets_have_buildings" in f_only(M, "streets_have_buildings")


@pytest.mark.tiers("town")
def test_streets_have_buildings_passes_when_a_building_fronts_the_street():
    M = {
        "meta": {"scale": "town", "walled": True},
        "wall": WALL,
        "town_streets": [{"pts": [[700, 400], [700, 600]], "w": 18, "main": True}],
        "buildings": [bldg(720, 500)],  # nearest THIS street, covers its short length
    }
    assert "streets_have_buildings" not in f_only(M, "streets_have_buildings")


@pytest.mark.tiers("town")
def test_wall_hugs_the_town_fires_on_empty_corner_space():
    M = {"meta": {"scale": "town", "walled": True}, "wall": WALL, "buildings": [bldg(120, 120)]}  # one building, far from the right/bottom faces
    assert "wall_hugs_the_town" in f_only(M, "wall_hugs_the_town")


@pytest.mark.tiers("town")
def test_wall_hugs_the_town_passes_when_buildings_line_every_face():
    near = [bldg(x, y) for x in (120, 500, 880) for y in (120, 500, 880)]  # a 3x3 grid hugging all faces
    M = {"meta": {"scale": "town", "walled": True}, "wall": WALL, "buildings": near}
    assert "wall_hugs_the_town" not in f_only(M, "wall_hugs_the_town")


@pytest.mark.tiers("town")
def test_walled_town_has_gate_market_fires_when_no_market_outside():
    # the only business sits INSIDE the wall, so there is no extramural market at the gate
    M = {"meta": {"scale": "town", "walled": True}, "wall": WALL, "gate": [500, 950], "buildings": [bldg(500, 500, kind="merchant")]}
    assert "walled_town_has_gate_market" in f_only(M, "walled_town_has_gate_market")


@pytest.mark.tiers("town")
def test_walled_town_gate_market_opt_out_suppresses_the_check():
    # meta(gate_market=False) - a purely military or suppressed gate - skips the requirement
    M = {"meta": {"scale": "town", "walled": True, "gate_market": False}, "wall": WALL, "gate": [500, 950], "buildings": [bldg(500, 500, kind="merchant")]}
    assert "walled_town_has_gate_market" not in f_only(M, "walled_town_has_gate_market")


@pytest.mark.tiers("town")
def test_walled_town_commoners_inside_walls_fires_on_an_outside_laborer():
    M = {
        "meta": {"scale": "town", "walled": True},
        "wall": [[300, 300], [700, 300], [700, 700], [300, 700]],
        "gate": [500, 700],
        "buildings": [_dw(900, 500, "laborer")],
        "fire_towers": [_tower(500, 500)],
    }
    assert "walled_town_commoners_inside_walls" in f_only(M, "walled_town_commoners_inside_walls")


@pytest.mark.tiers("town")
def test_walled_town_commoners_inside_walls_allows_burakumin_and_gate_merchants():
    M = {
        "meta": {"scale": "town", "walled": True},
        "wall": [[300, 300], [700, 300], [700, 700], [300, 700]],
        "gate": [500, 700],
        "buildings": [_dw(900, 500, "burakumin"), _dw(520, 780, "merchant"), _dw(500, 500, "laborer")],
        "fire_towers": [_tower(500, 500)],
    }
    assert "walled_town_commoners_inside_walls" not in f_only(M, "walled_town_commoners_inside_walls")


@pytest.mark.tiers("town")
def test_water_flow_declared_fires_when_a_watered_map_declares_no_bearing():
    M = _wf_map(meta={"scale": "town", "walled": False, "ftpx": 1, "down_deg": 90})
    assert "water_flow_declared" in f_only(M, "water_flow_declared")


@pytest.mark.tiers("town")
def test_water_flow_consistent_with_slope_fires_when_water_would_run_uphill():
    # 90 deg or more off the fall = a net uphill component, which gravity forbids
    M = _wf_map(meta={"scale": "town", "walled": False, "ftpx": 1, "down_deg": 90, "water_flow": 270})
    assert "water_flow_consistent_with_slope" in f_only(M, "water_flow_consistent_with_slope")


@pytest.mark.tiers("town")
def test_water_flow_consistent_with_slope_passes_a_near_contour_divergence():
    # 85 deg off the fall is a CONTOUR work (a canal is built near-parallel to the contours),
    # realistic and must not be flagged - only crossing 90 is impossible
    M = _wf_map(meta={"scale": "town", "walled": False, "ftpx": 1, "down_deg": 90, "water_flow": 5})
    assert "water_flow_consistent_with_slope" not in f_only(M, "water_flow_consistent_with_slope")


@pytest.mark.tiers("town")
def test_tanning_yard_below_every_intake_ignores_an_intake_on_a_DIFFERENT_course():
    # Hoshizora's real situation: the town's intakes are on a watercourse the yard's water never
    # reaches, so they must not be charged against it
    M = _ty_map(channels=[{"poly": [[100, 700], [180, 720]], "frm": {"kind": "stream"}, "to": {"kind": "field", "name": "f1"}, "w": 2.5}])
    assert "tanning_yard_below_every_intake" not in f_only(M, "tanning_yard_below_every_intake")


@pytest.mark.tiers("town")
def test_town_has_punishment_spot_fires_when_the_seat_keeps_none():
    assert "town_has_punishment_spot" in f_only(_justice_town(punishment_spots=[]), "town_has_punishment_spot")


@pytest.mark.tiers("town")
def test_town_has_punishment_spot_can_be_opted_out():
    M = _justice_town(punishment_spots=[])
    M["meta"] = {**M["meta"], "punishment_spot": False}
    assert "town_has_punishment_spot" not in f_only(M, "town_has_punishment_spot")


@pytest.mark.tiers("town")
def test_town_has_execution_ground_fires_when_the_seat_keeps_none():
    assert "town_has_execution_ground" in f_only(_justice_town(execution_grounds=[]), "town_has_execution_ground")


@pytest.mark.tiers("town")
def test_town_has_execution_ground_can_be_opted_out():
    M = _justice_town(execution_grounds=[])
    M["meta"] = {**M["meta"], "execution_ground": False}
    assert "town_has_execution_ground" not in f_only(M, "town_has_execution_ground")


@pytest.mark.tiers("town")
def test_execution_ground_on_the_outcast_side_fires_on_the_opposite_side():
    # West of the core while the burakumin quarter lies east - pollution runs ONE way out of a town.
    M = _justice_town(execution_grounds=[exground(-600, 1060)], boundary_markers=[bstone(0, 1020)])
    assert "execution_ground_on_the_outcast_side" in f_only(M, "execution_ground_on_the_outcast_side")


@pytest.mark.tiers("town")
def test_execution_ground_no_nearer_the_houses_than_its_stone_fires_when_the_ground_is_further_in():
    """The GM's formulation, 2026-07-27: the stone should be closer to the town's edge than the
    ground. The between-ness test above cannot see this - it compares two distances to the core
    CENTROID, which orders the pair radially about one point while a settlement is not a disc. Here
    the ground keeps its 126 px of kegare clearance and is still 10 px further IN than the stone that
    is supposed to bound it, so both of the older rules are satisfied and the map is still wrong."""
    M = _justice_town(boundary_markers=[bstone(1160, 1010)], execution_grounds=[exground(1500, 1060)], houses=[house(440 + 30 * i, 940) for i in range(6)] + [house(1500, 1230)])
    assert "execution_ground_past_the_boundary_marker" not in f_only(M, "execution_ground_past_the_boundary_marker")  # the centroid arithmetic is satisfied...
    assert "execution_ground_no_nearer_the_houses_than_its_stone" in f_only(M, "execution_ground_no_nearer_the_houses_than_its_stone")  # ...and the ground is still inside the line


@pytest.mark.tiers("city", "town")
def test_execution_ground_no_nearer_the_houses_than_its_stone_measures_a_walled_seat_to_its_RAMPART():
    """And the settlement edge is the WALL where there is one. Measuring a walled city to its
    nearest dwelling lets an isolated farmstead in the hinterland stand for the town - Tango's
    ground sits in the extramural fields with a farmhouse further out than itself, which read as
    'nearer the town' than a stone plainly between the city and it."""
    M = _justice_town(wall=WALL, boundary_markers=[bstone(1000, 1010)], execution_grounds=[exground(1500, 1060)], houses=[house(440 + 30 * i, 940) for i in range(6)] + [house(1620, 1060)])
    assert "execution_ground_no_nearer_the_houses_than_its_stone" not in f_only(M, "execution_ground_no_nearer_the_houses_than_its_stone")
