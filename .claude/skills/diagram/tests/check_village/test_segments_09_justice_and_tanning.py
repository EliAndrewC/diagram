"""Split from test_checks.py by feature 025 - see tests/check_village/CLAUDE.md for the index."""

from l7r.diagram import check_village
from tests.check_village._builders import _TY_DIAG, _WHY, WALL, _fall_map, _justice_town, _side_map, _ty_map, _waived_map, _wf_map, bldg, bstone, exground, f_only, pspot

# ---- streets_have_buildings: the case that motivated this file ----------------------------
# A building beside a north-south lane but FRONTING the east-west cross-street (it is nearer
# the cross) must NOT count as serving the lane - so a lane with only such neighbors reads as
# empty. The old proximity-only check missed this; this fixture pins the fix.


# ---- wall_hugs_the_town: a wall that encloses large empty corner space ---------------------
# Walls are expensive; one should hug the built town. A single building tucked in one corner of
# a big square enclosure leaves three faces running over empty space - that must fire. A town
# whose buildings sit near every face must NOT. (The hill, when present, counts as occupancy -
# a wall may legitimately climb/skirt terrain rather than leveling it.)


def test_settlement_has_tanning_yard_fires_when_a_watered_town_keeps_none():
    M = _ty_map()
    M.pop("tanning_yards")
    assert "settlement_has_tanning_yard" in f_only(M, "settlement_has_tanning_yard")


def test_settlement_has_tanning_yard_passes_when_the_settlement_has_no_water():
    M = _ty_map(streams=[])  # no watercourse -> no tannery is CORRECT, not a defect
    M.pop("tanning_yards")
    assert "settlement_has_tanning_yard" not in f_only(M, "settlement_has_tanning_yard")


def test_settlement_has_tanning_yard_passes_when_there_is_no_burakumin_quarter():
    M = _ty_map(buildings=[bldg(200, 200)])
    M.pop("tanning_yards")
    assert "settlement_has_tanning_yard" not in f_only(M, "settlement_has_tanning_yard")


def test_tanning_yard_on_water_fires_when_the_yard_sits_on_dry_ground():
    M = _ty_map(tanning_yards=[{"x": 180, "y": 500, "w": 58, "h": 41, "rot": 0, "label": "tanning yard"}])
    assert "tanning_yard_on_water" in f_only(M, "tanning_yard_on_water")


def test_tanning_yard_on_water_passes_on_the_bank():
    assert "tanning_yard_on_water" not in f_only(_ty_map(), "tanning_yard_on_water")


def test_tanning_yard_clear_of_dwellings_fires_when_a_house_stands_beside_it():
    M = _ty_map(buildings=[bldg(200, 200, kind="burakumin"), bldg(466, 560)])  # a merchant 60 ft away
    assert "tanning_yard_clear_of_dwellings" in f_only(M, "tanning_yard_clear_of_dwellings")


def test_tanning_yard_clear_of_dwellings_exempts_the_burakumin_quarter():
    # the same 60 ft gap, but the neighbor is burakumin: they live on the ground they work
    M = _ty_map(buildings=[bldg(466, 560, kind="burakumin")])
    assert "tanning_yard_clear_of_dwellings" not in f_only(M, "tanning_yard_clear_of_dwellings")


def test_tanning_yard_clear_of_water_fires_when_the_ground_crosses_the_bank():
    # the yard edge 10 px past the stream's drawn edge - the real Tango defect: the tamped
    # ground read as a platform over the water
    M = _ty_map(tanning_yards=[{"x": 476, "y": 500, "w": 58, "h": 41, "rot": 0, "label": "tanning yard"}])
    assert "tanning_yard_clear_of_water" in f_only(M, "tanning_yard_clear_of_water")


def test_tanning_yard_clear_of_water_fires_when_a_ditch_threads_under_the_rect():
    # a thin field drain crossing UNDER the yard between its corners - the real Hoshizora
    # defect; corner-sampling cannot see this, seg_to_rect_dist can
    M = _ty_map(field_ditches=[{"poly": [[400, 300], [466, 500], [530, 700]], "role": "drain", "field": "t-ne", "w": 2.2, "w_tail": 2.2}])
    assert "tanning_yard_clear_of_water" in f_only(M, "tanning_yard_clear_of_water")


def test_tanning_yard_clear_of_water_fires_when_the_yard_sits_in_the_pond():
    M = _ty_map(pond=[466, 530, 30, 20])
    assert "tanning_yard_clear_of_water" in f_only(M, "tanning_yard_clear_of_water")


def test_tanning_yard_clear_of_water_fires_when_the_river_swallows_a_corner():
    # tested at the river's REAL half-width (the lumber-yard lesson): a 60 px river's edge reaches
    # 30 px out and swallows the yard's corner while its CENTERLINE stands 23 px clear of the
    # ground - far past the generic ~6 px stroke the village checks assume
    M = _ty_map(river={"pts": [[510, 100], [510, 900]], "w": 60})
    assert "tanning_yard_clear_of_water" in f_only(M, "tanning_yard_clear_of_water")


def test_tanning_yard_clear_of_water_passes_on_the_bank():
    # the baseline yard abuts the stream's edge with the frames overhanging - the design
    assert "tanning_yard_clear_of_water" not in f_only(_ty_map(), "tanning_yard_clear_of_water")


def test_tanning_yard_clear_of_fields_fires_on_a_paddy():
    M = _ty_map(fields=[{"name": "t-ne", "kind": "paddy", "outline": [[300, 400], [480, 400], [480, 600], [300, 600]], "bbox": [300, 400, 480, 600]}])
    assert "tanning_yard_clear_of_fields" in f_only(M, "tanning_yard_clear_of_fields")


def test_tanning_yard_clear_of_fields_fires_on_a_dry_plot():
    M = _ty_map(dry_plots=[{"poly": [[430, 480], [470, 480], [470, 520], [430, 520]], "crop": "millet"}])
    assert "tanning_yard_clear_of_fields" in f_only(M, "tanning_yard_clear_of_fields")


def test_tanning_yard_clear_of_fields_fires_when_the_yard_engulfs_a_flower_patch():
    # the poly entirely inside the rect: no edges cross, only the vertex-in-rect test sees it
    M = _ty_map(flower_fields=[{"kind": "chrysanthemum", "outline": [[460, 495], [470, 495], [470, 505], [460, 505]]}])
    assert "tanning_yard_clear_of_fields" in f_only(M, "tanning_yard_clear_of_fields")


def test_tanning_yard_clear_of_fields_passes_beside_the_field():
    # abutting cropland is fine - marginal bank ground borders the fields; only OVERLAP fires
    M = _ty_map(fields=[{"name": "t-ne", "kind": "paddy", "outline": [[300, 400], [430, 400], [430, 600], [300, 600]], "bbox": [300, 400, 430, 600]}])
    assert "tanning_yard_clear_of_fields" not in f_only(M, "tanning_yard_clear_of_fields")


def test_tanning_yard_square_to_its_water_fires_on_an_axis_aligned_yard_on_a_diagonal_bank():
    M = _ty_map(
        streams=[{"poly": _TY_DIAG, "w": 8, "flow": "forward", "flow_deg": 56.3, "frm": {"kind": "offmap"}, "to": {"kind": "offmap"}}],
        tanning_yards=[{"x": 466, "y": 473, "w": 58, "h": 41, "rot": 0, "label": "tanning yard"}],
    )
    assert "tanning_yard_square_to_its_water" in f_only(M, "tanning_yard_square_to_its_water")


def test_tanning_yard_square_to_its_water_passes_when_the_yard_follows_the_bank():
    M = _ty_map(
        streams=[{"poly": _TY_DIAG, "w": 8, "flow": "forward", "flow_deg": 56.3, "frm": {"kind": "offmap"}, "to": {"kind": "offmap"}}],
        tanning_yards=[{"x": 476, "y": 466, "w": 58, "h": 41, "rot": 56.3, "label": "tanning yard"}],
    )
    assert "tanning_yard_square_to_its_water" not in f_only(M, "tanning_yard_square_to_its_water")


def test_tanning_yard_square_to_its_water_accepts_a_180_degree_flip():
    # the same ground with the water side on the other long edge is the same alignment
    M = _ty_map(
        streams=[{"poly": _TY_DIAG, "w": 8, "flow": "forward", "flow_deg": 56.3, "frm": {"kind": "offmap"}, "to": {"kind": "offmap"}}],
        tanning_yards=[{"x": 476, "y": 466, "w": 58, "h": 41, "rot": 236.3, "label": "tanning yard"}],
    )
    assert "tanning_yard_square_to_its_water" not in f_only(M, "tanning_yard_square_to_its_water")


def test_tanning_yard_square_to_its_water_passes_at_a_confluence_when_square_to_either_course():
    # the yard follows the vertical stream; the 40 deg course also runs past it, and being 50 deg
    # off THAT one is not a defect - a yard on two banks legitimately lies along one of them
    M = _ty_map(
        streams=[
            {"poly": [[500, 100], [500, 900]], "w": 8, "flow": "forward", "flow_deg": 90.0, "frm": {"kind": "offmap"}, "to": {"kind": "offmap"}},
            {"poly": [[361, 470], [552, 630]], "w": 8, "flow": "forward", "flow_deg": 39.9, "frm": {"kind": "offmap"}, "to": {"kind": "offmap"}},
        ],
        tanning_yards=[{"x": 466, "y": 500, "w": 58, "h": 41, "rot": 90, "label": "tanning yard"}],
    )
    assert "tanning_yard_square_to_its_water" not in f_only(M, "tanning_yard_square_to_its_water")


def test_tanning_yard_square_to_its_water_abstains_when_no_bank_is_in_reach():
    # a yard on dry ground is tanning_yard_on_water's defect; do not report it twice
    M = _ty_map(tanning_yards=[{"x": 180, "y": 500, "w": 58, "h": 41, "rot": 0, "label": "tanning yard"}])
    assert "tanning_yard_on_water" in f_only(M, "tanning_yard_on_water")
    assert "tanning_yard_square_to_its_water" not in f_only(M, "tanning_yard_square_to_its_water")


def test_tanning_yard_square_to_its_water_measures_a_wide_course_from_its_BANK():
    # a 80 ft river's centerline is 50 px from this yard - out of the 20 ft reach - but its bank is
    # 10 px away, which is the edge the yard actually works. Read from the centerline the check
    # would abstain here; read from the bank it catches the yard sitting 56 deg across it.
    M = _ty_map(
        river={"poly": [[216, 342], [354, 550]], "w": 80},
        tanning_yards=[{"x": 200, "y": 473, "w": 58, "h": 41, "rot": 0, "label": "tanning yard"}],
    )
    assert "tanning_yard_square_to_its_water" in f_only(M, "tanning_yard_square_to_its_water")


def test_tanning_yard_square_to_its_water_ignores_a_repeated_polyline_point():
    # a duplicated vertex has no bearing - read as 0 deg it would wave this axis-aligned yard
    # through, since the point itself is the nearest bit of water to the rect
    M = _ty_map(
        streams=[{"poly": [[400, 300], [500, 450], [500, 450], [600, 600]], "w": 8, "flow": "forward", "flow_deg": 56.3, "frm": {"kind": "offmap"}, "to": {"kind": "offmap"}}],
        tanning_yards=[{"x": 466, "y": 473, "w": 58, "h": 41, "rot": 0, "label": "tanning yard"}],
    )
    assert "tanning_yard_square_to_its_water" in f_only(M, "tanning_yard_square_to_its_water")


def test_watercourses_declare_flow_fires_on_an_untagged_course():
    M = _wf_map(streams=[{"poly": [[500, 100], [500, 900]], "w": 8}])
    assert "watercourses_declare_flow" in f_only(M, "watercourses_declare_flow")


def test_watercourses_declare_flow_accepts_a_level_canal():
    M = _wf_map(canals=[{"poly": [[100, 500], [900, 500]], "w": 12, "flow": "level", "flow_deg": None}])
    assert "watercourses_declare_flow" not in f_only(M, "watercourses_declare_flow")


def test_watercourses_flow_downstream_fires_on_a_course_running_against_the_bearing():
    M = _wf_map(streams=[{"poly": [[500, 900], [500, 100]], "w": 8, "flow": "forward", "flow_deg": 270.0}])
    assert "watercourses_flow_downstream" in f_only(M, "watercourses_flow_downstream")


def test_watercourses_flow_downstream_exempts_the_level_canal():
    # Nagahara's cargo canal runs against the drainage and is CORRECT - it is a navigation cut
    M = _wf_map(canals=[{"poly": [[900, 500], [100, 500]], "w": 12, "flow": "level", "flow_deg": None}])
    assert "watercourses_flow_downstream" not in f_only(M, "watercourses_flow_downstream")


def test_tanning_yard_discharges_to_nothing_drawn_from_fires_on_a_course_feeding_a_pond():
    M = _ty_map(streams=[{"poly": [[500, 100], [500, 900]], "w": 8, "flow": "forward", "flow_deg": 90.0, "frm": {"kind": "offmap"}, "to": {"kind": "pond"}}])
    assert "tanning_yard_discharges_to_nothing_drawn_from" in f_only(M, "tanning_yard_discharges_to_nothing_drawn_from")


def test_tanning_yard_discharges_to_nothing_drawn_from_passes_when_it_ends_off_map():
    assert "tanning_yard_discharges_to_nothing_drawn_from" not in f_only(_ty_map(), "tanning_yard_discharges_to_nothing_drawn_from")


def test_tanning_yard_discharges_reads_the_sink_by_FLOW_not_polyline_order():
    # stored downstream-first: frm is the SINK. Reading frm/to by position would call this clean.
    M = _ty_map(streams=[{"poly": [[500, 900], [500, 100]], "w": 8, "flow": "reverse", "flow_deg": 270.0, "frm": {"kind": "pond"}, "to": {"kind": "offmap"}}])
    assert "tanning_yard_discharges_to_nothing_drawn_from" in f_only(M, "tanning_yard_discharges_to_nothing_drawn_from")


def test_tanning_yard_below_every_intake_fires_on_a_tap_downstream_of_the_yard():
    # the real Tango defect: a field taps the yard's own course BELOW it
    M = _ty_map(channels=[{"poly": [[500, 700], [700, 720]], "frm": {"kind": "stream"}, "to": {"kind": "field", "name": "f1"}, "w": 2.5}])
    assert "tanning_yard_below_every_intake" in f_only(M, "tanning_yard_below_every_intake")


def test_tanning_yard_below_every_intake_passes_when_the_tap_is_upstream():
    M = _ty_map(channels=[{"poly": [[500, 300], [700, 320]], "frm": {"kind": "stream"}, "to": {"kind": "field", "name": "f1"}, "w": 2.5}])
    assert "tanning_yard_below_every_intake" not in f_only(M, "tanning_yard_below_every_intake")


def test_tanning_yard_downstream_checks_skip_a_yard_with_no_watercourse_at_all():
    # degenerate but the guard is real: no course to reason about means no downstream verdict
    M = _ty_map(streams=[])
    assert "tanning_yard_discharges_to_nothing_drawn_from" not in f_only(M, "tanning_yard_discharges_to_nothing_drawn_from")
    assert "tanning_yard_below_every_intake" not in f_only(M, "tanning_yard_below_every_intake")


def test_settlement_declares_a_land_fall_accepts_a_map_level_bearing():
    M = _fall_map()
    M["meta"]["down_deg"] = 90
    assert "settlement_declares_a_land_fall" not in f_only(M, "settlement_declares_a_land_fall")


def test_settlement_declares_a_land_fall_accepts_per_field_falls_with_no_map_bearing():
    # what a settlement ringed by farmland needs: its fans drain several ways, so no single bearing
    M = _fall_map()
    M["fields"][0]["down_deg"] = 90
    assert "settlement_declares_a_land_fall" not in f_only(M, "settlement_declares_a_land_fall")


def test_settlement_declares_a_land_fall_is_not_satisfied_by_water_flow_alone():
    # water_flow is where the water GOES; down_deg is how the land LIES. Different facts.
    M = _fall_map()
    M["meta"]["water_flow"] = 90
    assert "settlement_declares_a_land_fall" in f_only(M, "settlement_declares_a_land_fall")


def test_punishment_spot_in_the_core_fires_on_a_spot_out_in_the_fields():
    # Out by the execution ground, where nobody passes it - a display nobody sees is not a display.
    assert "punishment_spot_in_the_core" in f_only(_justice_town(punishment_spots=[pspot(1600, 1300)]), "punishment_spot_in_the_core")


def test_punishment_spot_in_the_core_fires_outside_a_rampart():
    M = _justice_town(wall=WALL, punishment_spots=[pspot(520, 1020)])
    assert "punishment_spot_in_the_core" in f_only(M, "punishment_spot_in_the_core")  # the core sits outside this fixture's square wall


def test_punishment_spot_by_the_traffic_fires_on_a_spot_off_the_street():
    # In among the houses but ~150 ft back from the road: shaming is sited on foot traffic.
    assert "punishment_spot_by_the_traffic" in f_only(_justice_town(punishment_spots=[pspot(520, 850)]), "punishment_spot_by_the_traffic")


def test_execution_ground_outside_the_settlement_fires_on_a_ground_among_the_dwellings():
    assert "execution_ground_outside_the_settlement" in f_only(_justice_town(execution_grounds=[exground(520, 1000)]), "execution_ground_outside_the_settlement")


def test_execution_ground_outside_the_settlement_fires_inside_a_wall():
    M = _justice_town(wall=WALL, execution_grounds=[exground(500, 500)], boundary_markers=[bstone(480, 480)])
    assert "execution_ground_outside_the_settlement" in f_only(M, "execution_ground_outside_the_settlement")


def test_execution_ground_by_the_road_fires_on_a_ground_hidden_off_the_highway():
    # The posts are meant to be read from the road; 400 ft back into a field deters nobody.
    M = _justice_town(execution_grounds=[exground(1500, 1400)], boundary_markers=[bstone(1100, 1200)])
    assert "execution_ground_by_the_road" in f_only(M, "execution_ground_by_the_road")


def test_execution_ground_past_the_boundary_marker_fires_when_the_stone_is_missing():
    assert "execution_ground_past_the_boundary_marker" in f_only(_justice_town(boundary_markers=[]), "execution_ground_past_the_boundary_marker")


def test_execution_ground_past_the_boundary_marker_fires_when_the_stone_is_beyond_the_ground():
    # A stone further out than the ground marks nothing - the ground would sit INSIDE the boundary.
    assert "execution_ground_past_the_boundary_marker" in f_only(_justice_town(boundary_markers=[bstone(1800, 1060)]), "execution_ground_past_the_boundary_marker")


def test_execution_ground_past_the_boundary_marker_fires_when_the_stone_is_off_the_road():
    # Between the settlement and the ground, but sitting in open field 300 ft off the highway. The
    # between-ness arithmetic alone accepted this and it is still wrong: sae blocks pollution where
    # the ROAD leaves clean ground, so a stone that marks no road marks nothing. (Found by eye on a
    # rendered Nagahara while every check was green - hence this fixture.)
    assert "execution_ground_past_the_boundary_marker" in f_only(_justice_town(boundary_markers=[bstone(1100, 1300)]), "execution_ground_past_the_boundary_marker")


def test_execution_ground_past_the_boundary_marker_fires_when_the_stone_stands_among_the_dwellings():
    # On the road and correctly between core and ground, but 67 real ft from the nearest house - a
    # dosojin inside the built edge marks nothing, exactly like one inside a rampart. This is the
    # UNWALLED case, and it is the one that shipped: "outside" was tested as `not _inwall_j(...)`,
    # which is False for every point on a map with no wall, so the clause passed anything at all and
    # Ubame's stone stood among the west-end shops with a green gate (GM, 2026-07-26).
    assert "execution_ground_past_the_boundary_marker" in f_only(_justice_town(boundary_markers=[bstone(620, 1000)]), "execution_ground_past_the_boundary_marker")


def test_execution_ground_past_the_boundary_marker_accepts_a_walled_towns_stone_beside_the_suburb():
    # The deliberate divergence from the GROUND's version of "outside", pinned so nobody unifies
    # them: where there is a rampart the wall IS the edge, so a stone beyond it is past the line
    # even with roadside suburb against it (Hirameki's stands 104 ft from an extramural laborer
    # row). The ground keeps both clauses because kegare is a separation from people wherever they
    # live; the stone only has to say where clean ground ends.
    M = _justice_town(wall=WALL, buildings=[bldg(1000, 1010, kind="burakumin"), bldg(1210, 1010, kind="laborer")])
    assert "execution_ground_past_the_boundary_marker" not in f_only(M, "execution_ground_past_the_boundary_marker")


def test_execution_ground_clear_of_the_dead_fires_beside_the_burial_ground():
    M = _justice_town(cemeteries=[{"x": 1560, "y": 1060, "w": 100, "h": 80, "rot": 0, "parish": False}])
    assert "execution_ground_clear_of_the_dead" in f_only(M, "execution_ground_clear_of_the_dead")


def test_execution_ground_clear_of_the_dead_fires_beside_a_cremation_ground():
    # The rule covers the whole funerary family, not the cemetery alone.
    M = _justice_town(cremation_grounds=[{"x": 1540, "y": 1100, "w": 75, "h": 52, "rot": 0}])
    assert "execution_ground_clear_of_the_dead" in f_only(M, "execution_ground_clear_of_the_dead")


def test_execution_ground_off_the_farmland_fires_on_a_ground_in_a_paddy():
    M = _justice_town(fields=[{"name": "north", "kind": "paddy", "outline": [[1400, 960], [1700, 960], [1700, 1200], [1400, 1200]], "bbox": [1400, 960, 1700, 1200], "plots": [], "down_deg": 90}])
    assert "execution_ground_off_the_farmland" in f_only(M, "execution_ground_off_the_farmland")


def test_execution_ground_on_the_outcast_side_is_skipped_without_a_quarter():
    # A settlement with no burakumin dwellings has no outcast side to measure against.
    M = _justice_town(buildings=[], execution_grounds=[exground(-600, 1060)], boundary_markers=[bstone(0, 1020)])
    assert "execution_ground_on_the_outcast_side" not in f_only(M, "execution_ground_on_the_outcast_side")


def test_tanning_yard_on_the_outcast_side_fires_when_the_yard_faces_the_other_way():
    # core ~(290,410) sits BETWEEN the quarter (northwest) and the yard at (466,500) to the southeast
    assert "tanning_yard_on_the_outcast_side" in f_only(_side_map([(200, 200), (240, 200)], [(360, 620), (360, 620)]), "tanning_yard_on_the_outcast_side")


def test_tanning_yard_on_the_outcast_side_abstains_with_no_ordinary_dwellings():
    """All-burakumin fixture: the core lands ON the quarter, so no bearing exists and the rule has
    nothing to say. It must abstain rather than fire on a degenerate zero-length vector."""
    assert "tanning_yard_on_the_outcast_side" not in f_only(_ty_map(), "tanning_yard_on_the_outcast_side")


def test_a_waiver_excuses_the_named_check():
    assert "tanning_yard_on_the_outcast_side" not in f_only(_waived_map({"tanning_yard_on_the_outcast_side": _WHY}), "tanning_yard_on_the_outcast_side")


def test_waivers_are_documented_fires_on_a_reason_too_thin_to_be_one():
    assert "waivers_are_documented" in f_only(_waived_map({"tanning_yard_on_the_outcast_side": "by design"}), "waivers_are_documented")


def test_waivers_are_documented_fires_when_the_reason_is_not_even_text():
    assert "waivers_are_documented" in f_only(_waived_map({"tanning_yard_on_the_outcast_side": True}), "waivers_are_documented")


def test_waivers_are_live_fires_on_a_waiver_whose_check_now_passes():
    """The rot this prevents: a map keeps collecting waivers for defects it no longer has, and ends
    up exempt from rules nobody remembers it was ever breaking."""
    M = _waived_map({"tanning_yard_on_the_outcast_side": _WHY, "tanning_yard_on_water": _WHY})
    assert "waivers_are_live" in f_only(M, "waivers_are_live")


def test_waivers_are_live_fires_on_a_name_no_check_has():
    assert "waivers_are_live" in f_only(_waived_map({"tanning_yard_on_the_outcast_side": _WHY, "tanning_yard_on_watr": _WHY}), "waivers_are_live")


def test_a_waived_check_prints_WAIVE_and_a_closing_summary(capsys):
    """A waiver must never read as a PASS in the gate output - the whole point is that the override
    is visible to whoever runs it."""
    check_village.gate(_waived_map({"tanning_yard_on_the_outcast_side": _WHY}), verbose=True)
    out = capsys.readouterr().out
    assert "WAIVE tanning_yard_on_the_outcast_side" in out
    assert "WAIVED tanning_yard_on_the_outcast_side: The Emperor lies southeast" in out
