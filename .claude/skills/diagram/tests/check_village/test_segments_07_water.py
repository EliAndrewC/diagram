"""Split from test_checks.py by feature 025 - see tests/check_village/CLAUDE.md for the index."""

from tests.check_village._builders import (
    _bridge_map,
    _channel,
    _confluence,
    _drain_ditch,
    _field,
    _footbridge_map,
    _iw_manifest,
    _sink_channel,
    _water_map,
    f_only,
    house,
    manifest,
)


def test_channels_flow_downhill_fires_when_channel_runs_uphill():
    # downhill is south (+y); a channel whose field-end is NORTH of its stream-tap runs uphill
    M = {"meta": {"downhill": "south"}, "channels": [_channel([200, 500], [260, 320])]}
    assert "channels_flow_downhill" in f_only(M, "channels_flow_downhill")


def test_channels_flow_downhill_passes_when_channel_runs_downhill():
    M = {"meta": {"downhill": "south"}, "channels": [_channel([200, 320], [260, 500])]}
    assert "channels_flow_downhill" not in f_only(M, "channels_flow_downhill")


def test_channels_join_streams_at_confluence_fires_when_the_mouth_dies_short():
    # the stream runs N-S at x=400 (w 9 -> half-width 4.5); a culvert ending 20px from the
    # centerline passes the 30px anchor but never reaches the water - no confluence
    M = {"meta": {}, "streams": [{"poly": [[400, 100], [400, 900]], "w": 9}], "channels": [_sink_channel([380, 500])]}
    assert "channels_join_streams_at_confluence" in f_only(M, "channels_join_streams_at_confluence")


def test_channels_join_streams_at_confluence_passes_when_the_mouth_reaches_the_bed():
    M = {"meta": {}, "streams": [{"poly": [[400, 100], [400, 900]], "w": 9}], "channels": [_sink_channel([400, 500])]}
    assert "channels_join_streams_at_confluence" not in f_only(M, "channels_join_streams_at_confluence")


# ---- lanes: houses must FRONT a lane (not sit on it); a CONNECTOR must run off the edge -------
def test_houses_clear_of_lanes_fires_when_a_house_sits_on_the_tread():
    M = {"lanes": [{"pts": [[100, 500], [900, 500]], "worn": True, "w": 6, "connector": False}], "houses": [{"x": 500, "y": 500, "w": 23, "h": 14, "rot": 0, "kind": "plain"}]}  # centered ON the lane
    assert "houses_clear_of_lanes" in f_only(M, "houses_clear_of_lanes")


def test_houses_clear_of_lanes_reads_the_RAKE_the_house_is_drawn_at():
    """A farmhouse is drawn raked (`_house_rot`, +/-5 deg), and this check built its own
    axis-aligned corner list instead of using `rect_corners`, which has read `rot` all along
    (feature 121). So the gate measured a square-on rect while the map drew a raked one - and it
    disagreed with the PLACER, which is how a seat the placer had cleared came back from the gate
    as a house standing on a lane.

    The seat below is clear of the tread square-on and ON it once raked, so the axis-aligned
    version of this check cannot pass this test."""
    lane = {"pts": [[100, 500], [900, 500]], "worn": True, "w": 6, "connector": False}
    house = {"x": 500, "y": 521.5, "w": 62, "h": 30, "kind": "plain"}  # a LONG minka (the 1.35x length jitter)
    assert "houses_clear_of_lanes" not in f_only({"lanes": [lane], "houses": [{**house, "rot": 0}]}, "houses_clear_of_lanes"), "square-on it clears, so the rake is the only thing under test"
    assert "houses_clear_of_lanes" in f_only({"lanes": [lane], "houses": [{**house, "rot": -5}]}, "houses_clear_of_lanes"), "RAKED, the same house overhangs the tread and the gate must say so"


def test_houses_clear_of_lanes_passes_when_the_house_fronts_the_lane():
    M = {
        "lanes": [{"pts": [[100, 500], [900, 500]], "worn": True, "w": 6, "connector": False}],
        "houses": [{"x": 500, "y": 460, "w": 23, "h": 14, "rot": 0, "kind": "plain"}],
    }  # 40px off = fronting, clear
    assert "houses_clear_of_lanes" not in f_only(M, "houses_clear_of_lanes")


def test_groves_clear_of_lanes_fires_when_a_copse_sits_on_a_lane():
    M = {
        "lanes": [{"pts": [[300, 100], [300, 700]], "w": 6}],
        "village_groves": [{"role": "copse", "r": 11, "clumps": [[302, 400]], "poly": [[290, 390], [314, 390], [314, 410], [290, 410]]}],
    }  # clump ON the lane
    assert "groves_clear_of_lanes" in f_only(M, "groves_clear_of_lanes")


def test_groves_clear_of_lanes_passes_when_clumps_avoid_the_lane():
    M = {"lanes": [{"pts": [[300, 100], [300, 700]], "w": 6}], "village_groves": [{"role": "copse", "r": 11, "clumps": [[500, 400]], "poly": [[490, 390], [514, 390], [514, 410], [490, 410]]}]}
    assert "groves_clear_of_lanes" not in f_only(M, "groves_clear_of_lanes")


def test_groves_clear_of_lanes_fires_when_a_per_house_grove_sits_on_a_road():
    # covers the per-house grove (rect) branch AND the road corridor
    M = {"road": [[100, 400], [900, 400]], "road_width": 26, "groves": [{"x": 500, "y": 400, "w": 40, "h": 30, "rot": 0, "of": [500, 360]}]}
    assert "groves_clear_of_lanes" in f_only(M, "groves_clear_of_lanes")


def test_pond_fed_from_edge_fires_when_the_feeder_starts_mid_map():
    # a brook whose pond end is in the pond but whose FAR end sits mid-map (water out of nowhere)
    M = {"pond": [400, 300, 150, 90], "streams": [{"poly": [[600, 600], [420, 320]], "frm": {"kind": "offmap"}, "to": {"kind": "pond"}, "w": 9}]}
    assert "pond_fed_from_edge" in f_only(M, "pond_fed_from_edge")


def test_pond_fed_from_edge_passes_when_the_feeder_comes_from_the_edge():
    M = {"pond": [400, 300, 150, 90], "streams": [{"poly": [[10, 10], [420, 320]], "frm": {"kind": "offmap"}, "to": {"kind": "pond"}, "w": 9}]}
    assert "pond_fed_from_edge" not in f_only(M, "pond_fed_from_edge")


def test_fields_show_water_source_branches():
    abut = _field("a", 100, 100, 300, 300)  # abuts the stream at x95 -> watered
    ponded = {"name": "p", "kind": "paddy", "bbox": [680, 180, 720, 220], "outline": [[680, 180], [720, 180], [720, 220], [680, 220]]}  # over the pond -> watered
    dry = _field("d", 100, 600, 300, 800)  # no channel/stream/pond -> dry, fires
    M = {"fields": [abut, ponded, dry], "streams": [{"poly": [[95, 90], [95, 310]]}], "pond": [700, 200, 80, 60]}
    assert "fields_show_water_source" in f_only(M, "fields_show_water_source")


def test_long_ditches_have_a_footbridge_fires_when_a_long_ditch_is_planless():
    assert "long_ditches_have_a_footbridge" in f_only(_footbridge_map([]), "long_ditches_have_a_footbridge")
    assert "long_ditches_have_a_footbridge" not in f_only(_footbridge_map([{"x": 450, "y": 200, "rot": 90, "span": 20, "w": 5}]), "long_ditches_have_a_footbridge")


def test_long_ditches_footbridge_check_is_opt_in():
    # without meta.field_footbridges the check does not run at all (a planless ditch is fine)
    assert "long_ditches_have_a_footbridge" not in f_only(_footbridge_map([], footbridges=False), "long_ditches_have_a_footbridge")


def test_long_ditches_footbridge_exempts_a_margin_ditch():
    # a long ditch with cultivation on only ONE side (marsh/scrub the other) is not plankable -> no plank needed
    M = _footbridge_map([])
    M["fields"] = [{"name": "p", "kind": "paddy", "outline": [[50, 90], [850, 90], [850, 190], [50, 190]], "bbox": [50, 90, 850, 190]}]  # entirely N of the y=200 ditch
    assert "long_ditches_have_a_footbridge" not in f_only(M, "long_ditches_have_a_footbridge")


# ---- footbridges_reach_useful_ground: a standalone plank must land on field/village/dike both banks ----
def test_footbridges_reach_useful_ground_fires_when_a_plank_crosses_to_nothing():
    # a foot-tagged plank on the field's EDGE ditch: paddy on the N bank, bare ground (marsh/scrub) on the S
    M = _footbridge_map([{"x": 450, "y": 200, "rot": 90, "span": 11, "w": 2, "foot": True}])
    M["fields"] = [{"name": "p", "kind": "paddy", "outline": [[50, 90], [850, 90], [850, 190], [50, 190]], "bbox": [50, 90, 850, 190]}]  # only N of the ditch
    assert "footbridges_reach_useful_ground" in f_only(M, "footbridges_reach_useful_ground")


def test_footbridges_reach_useful_ground_passes_when_a_plank_reaches_field_both_banks():
    # the field straddles the ditch -> both banks cultivated -> the plank is useful
    assert "footbridges_reach_useful_ground" not in f_only(_footbridge_map([{"x": 450, "y": 200, "rot": 90, "span": 11, "w": 2, "foot": True}]), "footbridges_reach_useful_ground")


def test_footbridges_reach_useful_ground_exempts_untagged_lane_bridges():
    # a lane-carried crossing (no 'foot' tag) is exempt even with nothing on the far bank - a path leads to it
    M = _footbridge_map([{"x": 450, "y": 200, "rot": 90, "span": 11, "w": 5}])
    M["fields"] = [{"name": "p", "kind": "paddy", "outline": [[50, 90], [850, 90], [850, 190], [50, 190]], "bbox": [50, 90, 850, 190]}]
    assert "footbridges_reach_useful_ground" not in f_only(M, "footbridges_reach_useful_ground")


def test_waterways_merge_at_crossings_fires_when_bed_over_sheen():
    # the channel bed is drawn AFTER the stream sheen (the old per-course order) - an opaque bed cuts it
    assert "waterways_merge_at_crossings" in f_only(_confluence(25), "waterways_merge_at_crossings")


def test_waterways_merge_at_crossings_passes_when_beds_below_sheens():
    assert "waterways_merge_at_crossings" not in f_only(_confluence(11), "waterways_merge_at_crossings")


def test_waterways_merge_at_crossings_passes_when_no_crossing():
    M = _confluence(25)
    M["channels"][0]["poly"] = [[500, 100], [500, 300]]  # stops short, never reaches the stream
    assert "waterways_merge_at_crossings" not in f_only(M, "waterways_merge_at_crossings")


def test_waterways_merge_at_crossings_passes_when_neither_has_sheen():
    # two channels crossing - same-color beds merge regardless of order, no sheen to cut
    M = {
        "meta": {"scale": "village"},
        "channels": [
            {"poly": [[100, 500], [900, 500]], "frm": {"kind": "offmap"}, "to": {"kind": "offmap"}, "bedz": 30},
            {"poly": [[500, 100], [500, 900]], "frm": {"kind": "offmap"}, "to": {"kind": "offmap"}, "bedz": 10},
        ],
    }
    assert "waterways_merge_at_crossings" not in f_only(M, "waterways_merge_at_crossings")


def test_waterways_merge_at_crossings_fires_at_a_feeder_junction():
    # a channel FEEDS INTO a stream (its endpoint sits on it), drawn over the stream's sheen
    M = {
        "meta": {"scale": "village"},
        "streams": [{"poly": [[100, 500], [900, 500]], "frm": None, "to": None, "w": 9, "bedz": 10, "sheenz": 20}],
        "channels": [{"poly": [[500, 505], [500, 900]], "frm": {"kind": "offmap"}, "to": {"kind": "offmap"}, "bedz": 25}],
    }
    assert "waterways_merge_at_crossings" in f_only(M, "waterways_merge_at_crossings")


def test_waterways_merge_at_crossings_fires_when_stream_ends_on_a_channel():
    # the stream's own endpoint sits on a channel (the pa-endpoint junction branch)
    M = {
        "meta": {"scale": "village"},
        "streams": [{"poly": [[505, 500], [900, 500]], "frm": None, "to": None, "w": 9, "bedz": 25, "sheenz": 30}],
        "channels": [{"poly": [[500, 100], [500, 900]], "frm": {"kind": "offmap"}, "to": {"kind": "offmap"}, "bedz": 10, "sheenz": 5}],
    }
    assert "waterways_merge_at_crossings" in f_only(M, "waterways_merge_at_crossings")


# ---- shrine_halls_clear_of_lanes: a hall stands beside the road, torii may straddle it ----
def test_shrine_halls_clear_of_lanes_fires_on_a_hall_on_a_lane_exempts_torii():
    on = {
        "meta": {"scale": "village"},
        "religious": [{"x": 500, "y": 500, "w": 96, "h": 64, "kind": "shrine"}],
        "torii": [[500, 600, 1]],
        "lanes": [{"pts": [[500, 300], [500, 700]], "w": 6}],
    }  # lane threads through hall + torii
    assert "shrine_halls_clear_of_lanes" in f_only(on, "shrine_halls_clear_of_lanes")  # the HALL on the lane fires
    off = {**on, "religious": [{"x": 600, "y": 500, "w": 96, "h": 64, "kind": "shrine"}]}  # hall to the side, torii still ON the lane
    assert "shrine_halls_clear_of_lanes" not in f_only(off, "shrine_halls_clear_of_lanes")  # torii are exempt (road runs under the arch)


def test_shrine_halls_clear_of_lanes_fires_when_a_lane_ends_inside_the_hall():
    # a lane TERMINATING inside the hall footprint - exercises seg_to_rect_dist's endpoint-in-rect branch
    M = {"meta": {"scale": "village"}, "religious": [{"x": 500, "y": 500, "w": 96, "h": 64, "kind": "shrine"}], "lanes": [{"pts": [[500, 500], [500, 300]], "w": 6}]}
    assert "shrine_halls_clear_of_lanes" in f_only(M, "shrine_halls_clear_of_lanes")


def test_channels_join_streams_at_confluence_fires_when_the_intake_starts_short():
    # the SYMMETRIC (frm side) case: an intake declared frm={stream} starting 20px from the
    # centerline never actually taps the water - no confluence at the offtake either
    M = {"meta": {}, "streams": [{"poly": [[400, 100], [400, 900]], "w": 9}], "channels": [{"poly": [[380, 500], [440, 560]], "frm": {"kind": "stream"}, "to": {"kind": "field", "name": "x"}}]}
    assert "channels_join_streams_at_confluence" in f_only(M, "channels_join_streams_at_confluence")


def test_channels_join_streams_at_confluence_passes_when_the_intake_taps_the_bed():
    M = {"meta": {}, "streams": [{"poly": [[400, 100], [400, 900]], "w": 9}], "channels": [{"poly": [[400, 500], [460, 560]], "frm": {"kind": "stream"}, "to": {"kind": "field", "name": "x"}}]}
    assert "channels_join_streams_at_confluence" not in f_only(M, "channels_join_streams_at_confluence")


def test_watercourse_ends_reach_water_fires_when_the_collector_dangles():
    # the collector's east end stops 50px short of the stream, outside the planted bbox
    M = {
        "meta": {},
        "fields": [{"name": "f1", "kind": "paddy", "outline": [[100, 300], [300, 300], [300, 600], [100, 600]], "bbox": [100, 300, 300, 600], "vis_bbox": [100, 300, 300, 600]}],
        "streams": [{"poly": [[430, 100], [430, 900]], "w": 9}],
        "field_ditches": [_drain_ditch([[120, 590], [370, 610]])],
    }
    assert "watercourse_ends_reach_water" in f_only(M, "watercourse_ends_reach_water")


def test_watercourse_ends_reach_water_passes_when_a_culvert_carries_it_on():
    M = {
        "meta": {},
        "fields": [{"name": "f1", "kind": "paddy", "outline": [[100, 300], [300, 300], [300, 600], [100, 600]], "bbox": [100, 300, 300, 600], "vis_bbox": [100, 300, 300, 600]}],
        "streams": [{"poly": [[430, 100], [430, 900]], "w": 9}],
        "field_ditches": [_drain_ditch([[120, 590], [370, 610]])],
        "channels": [{"poly": [[370, 610], [430, 628]], "frm": {"kind": "drain"}, "to": {"kind": "stream"}, "w": 2.5}],
    }
    assert "watercourse_ends_reach_water" not in f_only(M, "watercourse_ends_reach_water")


def test_canopy_clear_of_watercourses_fires_on_a_clump_in_the_stream():
    M = {"meta": {}, "streams": [{"poly": [[400, 100], [400, 900]], "w": 9}], "village_groves": [{"x": 400, "y": 500, "w": 60, "h": 40, "role": "copse", "clumps": [[402, 500]]}]}
    assert "canopy_clear_of_watercourses" in f_only(M, "canopy_clear_of_watercourses")


def test_canopy_clear_of_watercourses_passes_beside_the_bank():
    M = {"meta": {}, "streams": [{"poly": [[400, 100], [400, 900]], "w": 9}], "village_groves": [{"x": 440, "y": 500, "w": 60, "h": 40, "role": "copse", "clumps": [[440, 500]]}]}
    assert "canopy_clear_of_watercourses" not in f_only(M, "canopy_clear_of_watercourses")


def test_watercourse_ends_reach_water_fires_on_a_dangling_main_canal():
    # a supply canal's free end far past the crop with no join - the hikari-east class
    M = {
        "meta": {},
        "fields": [{"name": "f1", "kind": "paddy", "outline": [[100, 300], [300, 300], [300, 600], [100, 600]], "bbox": [100, 300, 300, 600], "vis_bbox": [100, 300, 300, 600]}],
        "field_ditches": [{"poly": [[120, 310], [450, 340]], "role": "main", "field": "f1", "w": 6, "w_tail": 6}],
    }
    assert "watercourse_ends_reach_water" in f_only(M, "watercourse_ends_reach_water")


def test_watercourse_ends_reach_water_allows_a_canal_tail_at_the_crop_edge():
    M = {
        "meta": {},
        "fields": [{"name": "f1", "kind": "paddy", "outline": [[100, 300], [300, 300], [300, 600], [100, 600]], "bbox": [100, 300, 300, 600], "vis_bbox": [100, 300, 300, 600]}],
        "field_ditches": [{"poly": [[120, 310], [314, 330]], "role": "main", "field": "f1", "w": 6, "w_tail": 6}],
    }
    assert "watercourse_ends_reach_water" not in f_only(M, "watercourse_ends_reach_water")


# ---- near_ring_cultivated_fraction (feature 013): a well-sited town/city sits in packed farmland,
# so the flat, uncommitted near-ring ground must be CULTIVATED (paddy/veg fields, dry plots, gardens)
# to the near_ring_density tier's floor. Bare scrub on that ground counts against; the sub-100%
# threshold leaves room for the genuine fallow/margin scrub. Town + city only.


# ---- scrub_clear_of_urban_fabric (GM 2026-07-21, Hoshizora): settlement ground is CLEARED - a
# commons/pasture/coppice cover poly that CONTAINS an occupied structure or a wellhead is claiming
# grazed waste where the town stands. Scrub lives on the outskirts only; field barns are exempt
# (a hay barn stands in the grazed ground it serves).


def test_scrub_clear_of_urban_fabric_fires_on_a_farmhouse_in_the_scrub():
    # the check is order-blind and covers farmhouses: a house drawn after the cover fires too
    # (town scale - at village/hamlet scale dispersed farms legitimately stand on the marginal
    # scrub, so the check is scoped out there and only the engine halo applies)
    M = {
        "meta": {"scale": "town"},
        "commons": [{"x": 500, "y": 500, "w": 400, "h": 400, "rot": 0, "role": "pasture", "seq": 1, "poly": [[300, 300], [700, 300], [700, 700], [300, 700]]}],
        "houses": [{"x": 450, "y": 520, "w": 44, "h": 29, "rot": 0, "kind": "plain"}],
    }
    assert "scrub_clear_of_urban_fabric" in f_only(M, "scrub_clear_of_urban_fabric")


# ---- channels_join_water_not_cross (GM 2026-07-23): a channel/ditch never runs straight ACROSS the
# moat/river centerline - water joins water at a confluence (the mouth ends at the bank; the recorded
# topology ends ON the centerline, so first/last-segment touches at the crossed water segment are the
# sanctioned join).


def test_channels_join_water_not_cross_exempts_a_tap_ending_on_the_centerline():
    M = {
        "meta": {"scale": "town", "W": 500, "H": 500},
        "moat": [[50, 100], [450, 100], [450, 110]],
        "channels": [{"poly": [[100, 100], [100, 180]], "frm": {"kind": "moat"}, "to": {"kind": "offmap"}, "w": 2.5}],
    }
    assert "channels_join_water_not_cross" not in f_only(M, "channels_join_water_not_cross")


# ---- channel_gates_at_water_junctions (GM 2026-07-23): a moat/river tap hands off to the comb canal
# (and a field drain to its outfall culvert) through a visible sluice gate at the junction.
def test_channel_gates_at_water_junctions_fires_on_a_gateless_tap():
    M = {
        "meta": {"scale": "town", "W": 500, "H": 500},
        "moat": [[50, 100], [450, 100], [450, 110]],
        "channels": [{"poly": [[100, 100], [100, 140], [110, 200]], "frm": {"kind": "moat"}, "to": {"kind": "offmap"}, "w": 2.5}],
    }
    M["channels"][0]["to"] = {"kind": "field", "name": "f1"}
    M["fields"] = [{"name": "f1", "kind": "paddy", "outline": [[60, 160], [160, 160], [160, 260], [60, 260]], "bbox": [60, 160, 160, 260]}]
    assert "channel_gates_at_water_junctions" in f_only(M, "channel_gates_at_water_junctions")


def test_channel_gates_at_water_junctions_passes_with_a_gate_at_the_sluice():
    M = {
        "meta": {"scale": "town", "W": 500, "H": 500},
        "moat": [[50, 100], [450, 100], [450, 110]],
        "channels": [{"poly": [[100, 100], [100, 140], [110, 200]], "frm": {"kind": "moat"}, "to": {"kind": "field", "name": "f1"}, "w": 2.5}],
        "fields": [{"name": "f1", "kind": "paddy", "outline": [[60, 160], [160, 160], [160, 260], [60, 260]], "bbox": [60, 160, 160, 260]}],
        "sluice_gates": [{"x": 100, "y": 141, "rot": 90, "z": 1}],
    }
    assert "channel_gates_at_water_junctions" not in f_only(M, "channel_gates_at_water_junctions")


def test_channel_gates_at_water_junctions_fires_on_a_gateless_drain_culvert():
    M = {
        "meta": {"scale": "town", "W": 500, "H": 500},
        "moat": [[50, 100], [450, 100], [450, 110]],
        "channels": [{"poly": [[200, 300], [200, 105]], "frm": {"kind": "drain"}, "to": {"kind": "moat"}, "w": 3.2, "drawn": True}],
    }
    assert "channel_gates_at_water_junctions" in f_only(M, "channel_gates_at_water_junctions")


def test_channel_gates_at_water_junctions_exempts_an_underground_conduit():
    # an UNDROWN drain record is an implied underground conduit (Tango's in-wall nw1 drain drops
    # beneath the ring road, rampart and moat) - no visible seam, no gate demanded
    M = {
        "meta": {"scale": "town", "W": 500, "H": 500},
        "moat": [[50, 100], [450, 100], [450, 110]],
        "channels": [{"poly": [[200, 300], [200, 105]], "frm": {"kind": "drain"}, "to": {"kind": "moat"}, "w": 2.5}],
    }
    assert "channel_gates_at_water_junctions" not in f_only(M, "channel_gates_at_water_junctions")


# ---- pond_fill_covers_channel_mouths: the Tango in-wall tank (GM 2026-07-23) ----------------
# The comb head-race joined the pond from the LATE water block, whose beds draw after the whole
# shared block - so the pond fill could not cover the mouth's inside-the-rim overshoot and the
# channel's round end-cap rode ON TOP of the open water, reading as an intersection rather than
# a join. The check verifies the RECORDED z-order: pond fill above every joining bed.
def test_pond_fill_covers_channel_mouths_fires_when_a_joining_bed_draws_over_the_fill():
    # bedz values are block-relative offsets, so the LATE joining bed's raw number (8) is SMALLER
    # than the early fill's (9) even though it draws after - the (late, bedz) pair carries the
    # real order, and a raw-z comparison would falsely pass exactly this broken-engine shape
    M = {
        "meta": {"scale": "village"},
        "pond": [500, 500, 40, 25],
        "pond_layer": {"bedz": 9, "sheenz": 10, "late": False},
        "drawn_channels": [{"pts": [[462.5, 505.0], [380.0, 560.0]], "late": True, "bedz": 8}],  # mouth at the rim, bed ABOVE the fill
    }
    assert "pond_fill_covers_channel_mouths" in f_only(M, "pond_fill_covers_channel_mouths")


def test_pond_fill_covers_channel_mouths_fires_when_the_layering_is_unrecorded():
    # the pre-fix Tango shape (frozen in pool/regressions/): a comb ditch joins the pond but the
    # manifest carries no pond_layer / drawn_channels records - the uncovered cap, undetectable by
    # z-comparison, so the ABSENCE of the records must itself fire
    M = {
        "meta": {"scale": "village"},
        "pond": [500, 500, 40, 25],
        "field_ditches": [{"poly": [[462.5, 505.0], [380.0, 560.0]], "role": "main", "field": "f1", "w": 5.0}],
    }
    assert "pond_fill_covers_channel_mouths" in f_only(M, "pond_fill_covers_channel_mouths")


def test_pond_fill_covers_channel_mouths_fires_when_a_stroke_crosses_the_open_water():
    # mouths, not crossings (the pond sibling of channels_join_water_not_cross): a drawn stroke
    # whose INTERIOR vertex sits deep inside the pond runs straight through the open water
    M = {
        "meta": {"scale": "village"},
        "pond": [500, 500, 40, 25],
        "pond_layer": {"bedz": 300, "sheenz": 301},
        "drawn_channels": [{"pts": [[430.0, 460.0], [500.0, 500.0], [570.0, 540.0]], "late": False, "bedz": 100}],
    }
    assert "pond_fill_covers_channel_mouths" in f_only(M, "pond_fill_covers_channel_mouths")


def test_pond_fill_covers_channel_mouths_passes_when_the_fill_covers_the_mouth():
    # the fixed engine shape: a late channel joins, so the fill RELOCATED to the late block
    # (late: True) and draws above the joining bed within it
    M = {
        "meta": {"scale": "village"},
        "pond": [500, 500, 40, 25],
        "pond_layer": {"bedz": 300, "sheenz": 301, "late": True},
        "drawn_channels": [{"pts": [[462.5, 505.0], [380.0, 560.0]], "late": True, "bedz": 100}],
        "field_ditches": [{"poly": [[462.5, 505.0], [380.0, 560.0]], "role": "main", "field": "f1", "w": 5.0}],
    }
    assert "pond_fill_covers_channel_mouths" not in f_only(M, "pond_fill_covers_channel_mouths")


def test_inwall_drains_gated_at_cutoff_fires_when_the_cutoff_is_ungated():
    M = _iw_manifest([300, 300], stroke=[[500, 300], [300, 300]])  # ditch reaches the drop, road clear, NO gate
    assert "inwall_drains_gated_at_cutoff" in f_only(M, "inwall_drains_gated_at_cutoff")


def test_inwall_drains_gated_at_cutoff_fires_when_the_ditch_rides_the_ring_road():
    # cut point 5px off the ring centerline (< half width 4 + 4) and the stroke crosses it
    M = _iw_manifest([300, 95], stroke=[[300, 300], [300, 95]], gates=((300, 95),))
    assert "inwall_drains_gated_at_cutoff" in f_only(M, "inwall_drains_gated_at_cutoff")


def test_inwall_drains_gated_at_cutoff_fires_when_no_ditch_reaches_the_drop():
    M = _iw_manifest([300, 300], stroke=[[500, 300], [400, 300]], gates=((300, 300),))  # nearest stroke end 100px away
    assert "inwall_drains_gated_at_cutoff" in f_only(M, "inwall_drains_gated_at_cutoff")


def test_inwall_drains_gated_at_cutoff_passes_when_gated_and_clear():
    M = _iw_manifest([300, 300], stroke=[[500, 300], [300, 300]], gates=((302, 301),))
    assert "inwall_drains_gated_at_cutoff" not in f_only(M, "inwall_drains_gated_at_cutoff")


def test_inwall_drains_gated_at_cutoff_exempts_drawn_culverts_and_outside_conduits():
    # a DRAWN drain culvert is the outside-the-wall kind (gated at the drain handoff by
    # channel_gates_at_water_junctions), and an undrawn conduit STARTING outside the wall has
    # no rampart to pass under - neither is this check's business
    assert "inwall_drains_gated_at_cutoff" not in f_only(_iw_manifest([300, 300], drawn=True), "inwall_drains_gated_at_cutoff")
    outside = _iw_manifest([980, 500])
    assert "inwall_drains_gated_at_cutoff" not in f_only(outside, "inwall_drains_gated_at_cutoff")


# ---- one direction model, not three (GM 2026-07-25) -----------------------------------------
def test_channels_flow_downhill_runs_from_down_deg_without_the_legacy_downhill_tag():
    # it used to be gated on meta(downhill), which only 2 of 17 maps declared - so 15 maps, both
    # cities among them, skipped it entirely behind a green gate
    M = {
        "meta": {"scale": "town", "walled": False, "ftpx": 1, "W": 1200, "H": 1200, "down_deg": 90},
        "fields": [{"name": "f1", "kind": "paddy", "outline": [[100, 100], [500, 100], [500, 500], [100, 500]], "bbox": [100, 100, 500, 500], "vis_bbox": [100, 100, 500, 500]}],
        "channels": [{"poly": [[300, 600], [300, 300]], "frm": {"kind": "stream"}, "to": {"kind": "field", "name": "f1"}, "w": 2.5}],  # runs NORTH, i.e. uphill
    }
    assert "channels_flow_downhill" in f_only(M, "channels_flow_downhill")


def test_channels_flow_downhill_judges_a_channel_by_the_FIELD_it_feeds():
    # same channel, but this field's own fall is north - so the channel now runs downhill INTO it.
    # A settlement ringed by farmland drains several ways, so the target field is the authority.
    M = {
        "meta": {"scale": "town", "walled": False, "ftpx": 1, "W": 1200, "H": 1200, "down_deg": 90},
        "fields": [{"name": "f1", "kind": "paddy", "outline": [[100, 100], [500, 100], [500, 500], [100, 500]], "bbox": [100, 100, 500, 500], "vis_bbox": [100, 100, 500, 500], "down_deg": 270}],
        "channels": [{"poly": [[300, 600], [300, 300]], "frm": {"kind": "stream"}, "to": {"kind": "field", "name": "f1"}, "w": 2.5}],
    }
    assert "channels_flow_downhill" not in f_only(M, "channels_flow_downhill")


def test_towpath_hugs_the_bank():
    """GM 2026-08-10: the river was re-routed and the towpath kept its old seat, running 100+px
    inland. A towpath is the hauling line's bank walk - every vertex stays on the bank."""
    assert "towpath_hugs_the_bank" not in f_only(_water_map(towpaths=[{"pts": [[100, 522], [900, 524]], "w": 3}]), "towpath_hugs_the_bank")
    assert "towpath_hugs_the_bank" in f_only(_water_map(towpaths=[{"pts": [[100, 522], [900, 640]], "w": 3}]), "towpath_hugs_the_bank")


def test_sluice_gates_on_water():
    """A sluice regulates a flow it must stand in - one stood 245px from any water after the
    re-route (GM 2026-08-10)."""
    assert "sluice_gates_on_water" not in f_only(_water_map(sluice_gates=[{"x": 500, "y": 508, "rot": 0}]), "sluice_gates_on_water")
    assert "sluice_gates_on_water" in f_only(_water_map(sluice_gates=[{"x": 500, "y": 700, "rot": 0}]), "sluice_gates_on_water")


def test_tanning_yards_on_water():
    """Tanning is a wash trade - the yard stands at its water; one of two yards was beached
    189px inland (GM 2026-08-10)."""
    assert "tanning_yards_on_water" not in f_only(_water_map(tanning_yards=[{"x": 500, "y": 550, "w": 26, "h": 17, "rot": 0, "kind": "tanning yard"}]), "tanning_yards_on_water")
    assert "tanning_yards_on_water" in f_only(_water_map(tanning_yards=[{"x": 500, "y": 720, "w": 26, "h": 17, "rot": 0, "kind": "tanning yard"}]), "tanning_yards_on_water")


# ---- a lane must reach something (the internal counterpart of connector_lane_runs_off_edge) ----
def _lane_map(lanes, houses=(), gen="hamletgen"):
    return {"meta": {"scale": "hamlet", "ftpx": 1, "generated_by": gen}, "lanes": lanes, "houses": list(houses)}


def test_lanes_reach_something_fires_on_a_tread_that_stops_in_bare_grass():
    """A lane exists to be fronted. An internal arm ending far from every other way AND every
    farmhouse serves no house, reaches no field and connects to nothing - a blunt tread stopping in
    open ground. Measured before the fix: five such ends across the four scripted hamlets, because
    lanes are laid BEFORE the houses they serve and an arm meeting neither crop nor water had
    nothing to stop it."""
    M = _lane_map(
        [{"pts": [[500, 500], [500, 900]], "w": 5, "connector": False}],
        [{"x": 500, "y": 500, "w": 46, "h": 28, "rot": 0, "kind": "plain"}],  # serves the START only
    )
    assert "lanes_reach_something" in f_only(M, "lanes_reach_something")  # the far end is 400 ft from that house and there is no other way


def test_lanes_reach_something_passes_when_the_end_meets_another_way_or_a_house():
    served = _lane_map(
        [{"pts": [[500, 500], [500, 900]], "w": 5, "connector": False}],
        [{"x": 500, "y": 500, "w": 46, "h": 28, "rot": 0, "kind": "plain"}, {"x": 540, "y": 890, "w": 46, "h": 28, "rot": 0, "kind": "plain"}],
    )
    assert "lanes_reach_something" not in f_only(served, "lanes_reach_something"), "a house at the far end is something to reach"
    met = _lane_map(
        # the crossing lane is kept SHORT on purpose: a long one would dangle at its own far end and
        # the check would fire for that instead, which is the check being right and the fixture wrong
        [{"pts": [[500, 500], [500, 900]], "w": 5, "connector": False}, {"pts": [[480, 905], [560, 905]], "w": 5, "connector": False}],
        [{"x": 500, "y": 500, "w": 46, "h": 28, "rot": 0, "kind": "plain"}, {"x": 540, "y": 890, "w": 46, "h": 28, "rot": 0, "kind": "plain"}],
    )
    assert "lanes_reach_something" not in f_only(met, "lanes_reach_something"), "meeting another way is something to reach"


def test_lanes_reach_something_is_gated_on_generated_by():
    """The migration doctrine: the rule binds the scripted path, and a frozen hand-authored map
    inherits it at the moment it is CONVERTED rather than being retrofitted."""
    legacy = _lane_map([{"pts": [[500, 500], [500, 900]], "w": 5, "connector": False}], [{"x": 500, "y": 500, "w": 46, "h": 28, "rot": 0, "kind": "plain"}], gen=None)
    legacy["meta"].pop("generated_by")
    assert "lanes_reach_something" not in f_only(legacy, "lanes_reach_something")


# ---- every farmhouse is reached by a way (the converse of lanes_reach_something) ----------------
def test_farmhouses_reach_a_way_fires_on_a_house_the_web_does_not_touch():
    """The research is decisive that a house in a nucleated cluster is reached - "every house in the
    nucleated village is accessible via the interconnected system of narrow lanes and alleys". The
    earlier reading, that a back rank is walked to along unfigured footpaths, was defensible-sounding
    with nothing behind it, and it left 29 of the four pool hamlets' 66 farmhouses out of reach.

    Note this is the CONVERSE of `lanes_reach_something`, and a map can pass that one with every
    lane busy while still stranding a third of its houses - which is exactly what the pool did."""
    M = _lane_map(
        [{"pts": [[500, 500], [500, 900]], "w": 5, "connector": False}],
        [{"x": 500, "y": 600, "w": 46, "h": 28, "rot": 0, "kind": "plain"}, {"x": 900, "y": 700, "w": 46, "h": 28, "rot": 0, "kind": "plain"}],
    )
    assert "farmhouses_reach_a_way" in f_only(M, "farmhouses_reach_a_way"), "the second house is 400 ft from the only lane"


def test_farmhouses_reach_a_way_passes_when_every_house_is_within_a_bundle_pitch():
    """The threshold is one BUNDLE_PITCH - the ground a single homestead occupies, which is the
    distance at which a lane passes your own plot or your neighbor's. Derived rather than chosen:
    the number it replaced was flagged in future-work/ as one nobody had justified."""
    M = _lane_map(
        [{"pts": [[500, 500], [500, 900]], "w": 5, "connector": False}],
        [{"x": 560, "y": 600, "w": 46, "h": 28, "rot": 0, "kind": "plain"}, {"x": 440, "y": 800, "w": 46, "h": 28, "rot": 0, "kind": "plain"}],
    )
    assert "farmhouses_reach_a_way" not in f_only(M, "farmhouses_reach_a_way")


def test_farmhouses_reach_a_way_measures_from_the_house_CENTER():
    """x, y ARE the center in this manifest, not the top-left corner - `rect_corners` reads them
    that way. Measuring from x + w/2 instead shifts every house half its own size, which is a real
    mistake this check made before it was caught: it moved the baseline count by three."""
    M = _lane_map(
        [{"pts": [[500, 400], [500, 600]], "w": 5, "connector": False}],
        [{"x": 590, "y": 500, "w": 100, "h": 28, "rot": 0, "kind": "plain"}],
    )
    assert "farmhouses_reach_a_way" not in f_only(M, "farmhouses_reach_a_way"), "center is 90 ft off the lane; a corner-read would call it 140"


def test_farmhouses_reach_a_way_is_silent_on_a_map_with_no_ways_or_no_houses():
    """Scoped to scripted maps, and it makes no claim about a manifest that has nothing to measure."""
    assert "farmhouses_reach_a_way" not in f_only(_lane_map([], [{"x": 900, "y": 900, "w": 46, "h": 28, "rot": 0, "kind": "plain"}]), "farmhouses_reach_a_way")
    assert "farmhouses_reach_a_way" not in f_only(_lane_map([{"pts": [[500, 500], [500, 900]], "w": 5, "connector": False}], []), "farmhouses_reach_a_way")
    hand = _lane_map([{"pts": [[500, 500], [500, 900]], "w": 5, "connector": False}], [{"x": 2000, "y": 2000, "w": 46, "h": 28, "rot": 0, "kind": "plain"}], gen="")
    assert "farmhouses_reach_a_way" not in f_only(hand, "farmhouses_reach_a_way"), "hand-authored maps are not gated by this rule"


# ---- two lane ends may not front the same farmhouse from the same side --------------------------
def test_lane_ends_front_different_houses_fires_on_a_fan_of_blunt_tines():
    """A farmhouse discharges ONE lane end's obligation, not three. A settlement-review read three
    ways leaving one node within 23 degrees, two ending blunt and all three claiming the same house
    at 66.9 / 55.1 / 40.0 ft, as a broom at 3x zoom: not three ways, one way drawn three times with
    the ends fanned. `lanes_reach_something` was silent because each end could point at the house."""
    M = _lane_map(
        [
            {"pts": [[500, 500], [700, 505]], "w": 5, "connector": False},
            {"pts": [[500, 540], [700, 549]], "w": 5, "connector": False},
        ],
        [{"x": 740, "y": 525, "w": 46, "h": 28, "rot": 0, "kind": "plain"}],
    )
    assert "lane_ends_front_different_houses" in f_only(M, "lane_ends_front_different_houses")


def test_lane_ends_front_different_houses_allows_a_house_on_a_CORNER():
    """Two lanes reaching one house from OPPOSITE quarters is a corner - a real thing that reads as
    one. The bearing clause is what keeps that legal; without it the rule would flag most of a
    nucleated cluster's middle."""
    M = _lane_map(
        [
            {"pts": [[500, 525], [700, 525]], "w": 5, "connector": False},
            {"pts": [[980, 525], [780, 525]], "w": 5, "connector": False},
        ],
        [{"x": 740, "y": 525, "w": 46, "h": 28, "rot": 0, "kind": "plain"}],
    )
    assert "lane_ends_front_different_houses" not in f_only(M, "lane_ends_front_different_houses")


def test_lane_ends_front_different_houses_exempts_an_end_that_MET_a_way():
    """An end that crosses another way at a real angle is a junction, and a junction beside a
    junction is a crossroads however tightly they sit. Only a BLUNT end can be a tine."""
    M = _lane_map(
        [
            {"pts": [[500, 500], [700, 505]], "w": 5, "connector": False},
            {"pts": [[500, 540], [700, 549]], "w": 5, "connector": False},
            {"pts": [[700, 460], [700, 600]], "w": 5, "connector": False},  # crosses both, squarely
        ],
        [{"x": 740, "y": 525, "w": 46, "h": 28, "rot": 0, "kind": "plain"}],
    )
    assert "lane_ends_front_different_houses" not in f_only(M, "lane_ends_front_different_houses")


def test_lane_ends_front_different_houses_is_silent_without_lanes_or_houses():
    assert "lane_ends_front_different_houses" not in f_only(_lane_map([], []), "lane_ends_front_different_houses")
    assert "lane_ends_front_different_houses" not in f_only(_lane_map([{"pts": [[500, 500]], "w": 5, "connector": False}], []), "lane_ends_front_different_houses")


# ---- one way drawn as two --------------------------------------------------------------------
def test_lanes_do_not_break_mid_run_fires_on_a_hole_in_a_street():
    """Two ends pointing AT each other across empty ground are one street with a hole in it, and both
    read as a rounded cap dying in bare grass. `lanes_reach_something` passes them because it tests
    each end independently, and an end 83 ft from a house CENTRE counts as fronting it even when that
    is 55 ft from the wall - out past the dooryard."""
    M = _lane_map(
        [
            {"pts": [[500, 500], [700, 500]], "w": 5, "connector": False},
            {"pts": [[810, 500], [1010, 500]], "w": 5, "connector": False},
        ],
        [{"x": 600, "y": 560, "w": 46, "h": 28, "rot": 0, "kind": "plain"}],
    )
    assert "lanes_do_not_break_mid_run" in f_only(M, "lanes_do_not_break_mid_run")


def test_lanes_do_not_break_mid_run_allows_a_break_with_something_IN_it():
    """An interruption with a wellhead in it is honest - the way stops because something is there."""
    M = _lane_map(
        [
            {"pts": [[500, 500], [700, 500]], "w": 5, "connector": False},
            {"pts": [[810, 500], [1010, 500]], "w": 5, "connector": False},
        ],
        [{"x": 600, "y": 560, "w": 46, "h": 28, "rot": 0, "kind": "plain"}],
    )
    M["wells"] = [{"x": 755, "y": 500, "r": 9, "vr": 14}]
    assert "lanes_do_not_break_mid_run" not in f_only(M, "lanes_do_not_break_mid_run")


def test_lanes_do_not_break_mid_run_allows_a_gap_a_third_way_already_spans():
    """Closing a break leaves the two original ends where they were, joined THROUGH the new lane.
    Without this the check fires on the very repair that fixes it."""
    M = _lane_map(
        [
            {"pts": [[500, 500], [700, 500]], "w": 5, "connector": False},
            {"pts": [[810, 500], [1010, 500]], "w": 5, "connector": False},
            {"pts": [[700, 500], [810, 500]], "w": 5, "connector": False},
        ],
        [{"x": 600, "y": 560, "w": 46, "h": 28, "rot": 0, "kind": "plain"}],
    )
    assert "lanes_do_not_break_mid_run" not in f_only(M, "lanes_do_not_break_mid_run")


def test_lanes_do_not_break_mid_run_ignores_ends_that_do_not_point_at_each_other():
    """Two arms leaving a cluster in different directions are two arms, however near their tips."""
    M = _lane_map(
        [
            {"pts": [[500, 500], [700, 500]], "w": 5, "connector": False},
            {"pts": [[790, 620], [790, 820]], "w": 5, "connector": False},
        ],
        [{"x": 600, "y": 560, "w": 46, "h": 28, "rot": 0, "kind": "plain"}],
    )
    assert "lanes_do_not_break_mid_run" not in f_only(M, "lanes_do_not_break_mid_run")


def test_no_farmhouse_stands_on_a_lane_fires_on_a_house_the_lane_runs_over():
    """FIRES. The converse of `farmhouses_reach_a_way`, and NOT the same rule said twice: a map can
    serve every house and still have drawn a lane through one of them.

    This is a REGRESSION guard rather than a discovery. Under feature 128's order every lane is laid
    after the houses, so it passes by construction - which is the point. Feature 126 attempted the
    same reorder for the skeleton alone, left the connector and the spur reserving ground before any
    house was seated, and nothing measured it; the GM found it by reading the walk-through page five
    days later. This fails the moment a way is laid ahead of `stage_homesteads` again."""
    M = _lane_map(
        [{"pts": [[500, 500], [500, 900]], "w": 5, "connector": False}],
        [{"x": 505, "y": 700, "w": 46, "h": 28, "rot": 0, "kind": "plain"}],
    )
    assert "no_farmhouse_stands_on_a_lane" in f_only(M, "no_farmhouse_stands_on_a_lane"), "the house center is 5 px from the lane, well inside the 14 px bar"


def test_no_farmhouse_stands_on_a_lane_passes_when_the_lane_runs_past_them():
    """STAYS QUIET. A lane beside the houses is the normal, correct arrangement - the whole point of
    laying lanes after the houses is that they run past rather than through. A check that fired here
    would condemn every hamlet the generator makes."""
    M = _lane_map(
        [{"pts": [[500, 500], [500, 900]], "w": 5, "connector": False}],
        [{"x": 560, "y": 700, "w": 46, "h": 28, "rot": 0, "kind": "plain"}],
    )
    assert "no_farmhouse_stands_on_a_lane" not in f_only(M, "no_farmhouse_stands_on_a_lane"), "60 px clear of the tread is a house beside a lane, not on it"


def test_lanes_form_one_network_fires_and_passes():
    """Every lane touches the rest in ink (GM 2026-08-27, T31: "random scattered lanes ... does not
    really connect to anything on either end" - nine lanes in six components on Inashiro, joined only
    by the 30 ft tolerance). A 20 px gap fires; the same lanes touching pass."""
    gap = manifest(
        houses=[house(x=400, y=400)], lane=[[0, 500], [300, 500]], lanes=[{"pts": [[0, 500], [300, 500]], "w": 6, "connector": True}, {"pts": [[320, 500], [320, 700]], "w": 3, "connector": False}]
    )
    assert "lanes_form_one_network" in f_only(gap, "lanes_form_one_network"), "a 20 px gap between two lanes must fire"
    touch = manifest(
        houses=[house(x=400, y=400)], lane=[[0, 500], [300, 500]], lanes=[{"pts": [[0, 500], [300, 500]], "w": 6, "connector": True}, {"pts": [[300, 500], [300, 700]], "w": 3, "connector": False}]
    )
    assert "lanes_form_one_network" not in f_only(touch, "lanes_form_one_network"), "touching lanes are one network"


def test_lanes_bend_like_paths_fires_and_passes():
    """A lane bends the way feet wear a path (GM 2026-08-27, T32: "a loop-de-loop ... zig-zags ... for
    no apparent reason"): a hairpin (turn >= 140 deg) fires, a zigzag (two turns >= 50 deg within
    40 ft) fires, a gentle bend and a single corner pass."""
    hairpin = manifest(houses=[house(x=400, y=400)], lane=[[0, 500], [300, 500]], lanes=[{"pts": [[0, 500], [300, 500], [300, 700], [300, 690]], "w": 3}])
    assert "lanes_bend_like_paths" in f_only(hairpin, "lanes_bend_like_paths"), "an out-and-back arm must fire"
    zigzag = manifest(houses=[house(x=400, y=400)], lane=[[0, 500], [300, 500]], lanes=[{"pts": [[0, 500], [300, 500], [310, 520], [330, 505], [340, 700]], "w": 3}])
    assert "lanes_bend_like_paths" in f_only(zigzag, "lanes_bend_like_paths"), "two sharp turns inside 40 ft must fire"
    corner = manifest(houses=[house(x=400, y=400)], lane=[[0, 500], [300, 500]], lanes=[{"pts": [[0, 500], [300, 500], [300, 700], [420, 780]], "w": 3}])
    assert "lanes_bend_like_paths" not in f_only(corner, "lanes_bend_like_paths"), "a corner and a bend are how a lane runs"


def test_a_sluice_gate_on_a_drawn_channel_stroke_stands_in_water():
    """Feature 150 T51: the inlet sluice sits on the ring feeder's DRAWN bend; once the feeder stub reaches
    the reservoir rim the recorded hairline no longer passes within reach of it, so the drawn strokes
    count here as they do for `sluice_gates_centered_on_their_channel`."""
    drawn = [{"pts": [[400, 700], [600, 700]], "w0": 5.0, "w1": 4.0}]
    assert "sluice_gates_on_water" not in f_only(_water_map(sluice_gates=[{"x": 500, "y": 701, "rot": 0}], drawn_channels=drawn), "sluice_gates_on_water")
    assert "sluice_gates_on_water" in f_only(_water_map(sluice_gates=[{"x": 500, "y": 701, "rot": 0}]), "sluice_gates_on_water")


def test_lanes_bend_like_paths_steps_over_a_degenerate_vertex():
    """A lane record can carry the same point twice - a join that landed on its own endpoint, a rounding
    that collapsed a 0.04 px step. The turn at such a vertex is undefined (a zero-length arm has no
    bearing), so it is stepped over rather than measured; without that the angle would come out of an
    `acos` on a division by zero."""
    from tests.check_village._builders import f_only, manifest

    doubled = manifest(lanes=[{"pts": [[100, 100], [100, 100], [300, 100], [300, 300]], "w": 4}])
    assert "lanes_bend_like_paths" not in f_only(doubled, "lanes_bend_like_paths")
    # ...and a real hairpin at the same corner still fires, so the skip is not hiding anything
    hairpin = manifest(lanes=[{"pts": [[100, 100], [300, 100], [110, 104]], "w": 4}])
    assert "lanes_bend_like_paths" in f_only(hairpin, "lanes_bend_like_paths")


def test_pond_fill_covers_channel_mouths_reads_a_STREAM_that_joins_the_pond():
    """THREE RECORD KINDS JOIN A POND, and the stream one had no test. `drawn_channels` and
    `channels` were both exercised; `M["streams"]` - a natural watercourse recorded as a `poly`
    rather than `pts` - was not, so the arm of the check that reads it could have been deleted
    without a single test noticing.

    A stream carries no `late` flag (it is never in the late water block), so it is appended as
    `late=False`; what the check then wants is the same as for any other joining course - a
    recorded `pond_layer` saying where the fill sits. With the stream joining and no layer
    recorded, the check must fire."""
    M = {
        "meta": {"scale": "village"},
        "pond": [500, 500, 40, 25],
        "streams": [{"poly": [[462.5, 505.0], [380.0, 560.0]], "bedz": 8}],  # mouth inside the rim zone
    }
    assert "pond_fill_covers_channel_mouths" in f_only(M, "pond_fill_covers_channel_mouths")

    # ...and with the fill recorded ABOVE the stream's bed, the same geometry is clean
    ok = {**M, "pond_layer": {"bedz": 9, "sheenz": 10, "late": False}}
    assert "pond_fill_covers_channel_mouths" not in f_only(ok, "pond_fill_covers_channel_mouths")

    # a stream that ends well clear of the pond joins nothing and is not read at all
    away = {**M, "streams": [{"poly": [[100.0, 100.0], [120.0, 140.0]], "bedz": 8}]}
    assert "pond_fill_covers_channel_mouths" not in f_only(away, "pond_fill_covers_channel_mouths")


def test_bridges_span_their_water_fires_on_an_oblique_underspan():
    """An OBLIQUE crossing needs a longer deck - and the verdict is on the deck's CORNERS (GM
    2026-08-09): a span whose centerline ends cleared the banks still left a corner sitting AT
    the water's edge, structurally impossible for an abutment that must stand back from scour.
    A carried deck's corners need >= 6 ft of dry landing (the drawn LANDING_FT is 10)."""
    M = _bridge_map([{"x": 500, "y": 500, "rot": 45, "span": 8, "w": 6}])
    assert "bridges_span_their_water" in f_only(M, "bridges_span_their_water")
    M["bridges"] = [{"x": 500, "y": 500, "rot": 45, "span": 20, "w": 6}]  # ends clear, corners do not
    assert "bridges_span_their_water" in f_only(M, "bridges_span_their_water")
    M["bridges"] = [{"x": 500, "y": 500, "rot": 45, "span": 38, "w": 6}]
    assert "bridges_span_their_water" not in f_only(M, "bridges_span_their_water")


def test_footplanks_keep_their_short_abutment_but_a_flush_plank_fires():
    """A standalone footplank's SHORT abutment stands (GM 2026-07-22: PLANK_ABUTMENT, ~3px of
    bank rest per side) - so its floor is 2 ft, not the carried deck's 6 - but a plank whose
    corner sits at the water's edge still fires."""
    M = _bridge_map([{"x": 500, "y": 500, "rot": 0, "span": 15, "w": 2, "foot": True}])
    assert "bridges_span_their_water" not in f_only(M, "bridges_span_their_water")
    M["bridges"] = [{"x": 500, "y": 500, "rot": 0, "span": 10, "w": 2, "foot": True}]
    assert "bridges_span_their_water" in f_only(M, "bridges_span_their_water")
