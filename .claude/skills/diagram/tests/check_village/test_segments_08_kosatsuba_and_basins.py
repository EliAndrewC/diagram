"""Gate checks for kosatsuba, punishment spots, paddy plot seams and basins (test_segments_08_town_and_fire split by feature 122; tests verbatim)."""

from l7r.diagram import check_village
from tests.check_village._builders import (
    _BB_FILLER,
    _BB_HOST,
    _bb_M,
    _drain_map,
    _field,
    _kosatsuba,
    f,
    f_only,
    manifest,
)


def test_village_and_hamlet_have_kosatsuba():
    # the ofuregaki reached the peasantry through the village/hamlet board via the literate
    # headman (GM 2026-07-24); siting works off the LANE network at these tiers
    assert "village_has_kosatsuba" in f_only({"meta": {"scale": "village"}}, "village_has_kosatsuba")
    assert "hamlet_has_kosatsuba" in f_only({"meta": {"scale": "hamlet"}}, "hamlet_has_kosatsuba")
    assert "hamlet_has_kosatsuba" not in f_only({"meta": {"scale": "hamlet", "kosatsuba": False}}, "hamlet_has_kosatsuba")
    # ...and stands ROADSIDE: 5 px = 10 ft off the lane at village grain (24 ft, the pre-2026-08-26 fixture, now fires - see test_hamlet_and_village_boards_must_be_roadside)
    ok = f({"meta": {"scale": "village", "ftpx": 2}, "kosatsuba": [_kosatsuba(500, 505)], "lanes": [{"pts": [[0, 500], [1000, 500]], "w": 5}]})
    assert "village_has_kosatsuba" not in ok and "kosatsuba_by_the_road" not in ok
    marooned = f({"meta": {"scale": "hamlet"}, "kosatsuba": [_kosatsuba(500, 700)], "lane": [[0, 500], [1000, 500]]})
    assert "kosatsuba_by_the_road" in marooned


# ---- households_consistent: the LEGACY (extended-family) band on an off-scale tier -----------
# On a to-scale tier (village/hamlet, or meta.toscale) the map depicts ~every household 1:1
# (~0.85-1.05x). A tier that is NOT to-scale (a town/city carrying a `households` meta, or an
# explicit toscale:False) falls to the legacy ~0.68-0.9x extended-family band. This pins that
# branch: a town declaring 100 households but depicting zero farmhouses is out of even the
# looser legacy band and must fire.
def test_households_consistent_uses_legacy_band_when_not_to_scale():
    M = {"meta": {"scale": "town", "households": 100}}  # town => scale != "village", no toscale => legacy band
    assert "households_consistent" in f_only(M, "households_consistent")


# ---- defense_marsh_girds_the_walls (the engineered defensive wet belt, GM 2026-07-23) ----------


def test_marsh_on_low_ground_exempts_the_waterside_fringe():
    # a polder's waterside fringe surrounds the dike regardless of the fall direction (the polder floor
    # sits BELOW the outside water level) - only the valley-toe role must lie downhill of the paddy.
    base = {
        "meta": {"scale": "hamlet", "down_deg": 90},
        "fields": [{"name": "p", "kind": "paddy", "outline": [[300, 300], [1100, 300], [1100, 1100], [300, 1100]], "bbox": [300, 300, 1100, 1100]}],
    }
    west_fringe = {**base, "marshes": [{"x": 200, "y": 700, "w": 200, "h": 900, "rot": 0, "role": "waterside", "poly": [[100, 250], [300, 250], [300, 1150], [100, 1150]]}]}
    assert "marsh_on_low_ground" not in f_only(west_fringe, "marsh_on_low_ground")  # same fall as the field centroid - exempt
    uphill_toe = {**base, "marshes": [{"x": 700, "y": 200, "w": 800, "h": 200, "rot": 0, "role": "toe", "poly": [[300, 100], [1100, 100], [1100, 300], [300, 300]]}]}
    assert "marsh_on_low_ground" in f_only(uphill_toe, "marsh_on_low_ground")  # a TOE marsh uphill of the paddy still fires


def test_drain_runs_cross_slope_fires_on_a_drain_running_with_the_fall():
    assert "drain_runs_cross_slope" in f_only(_drain_map(), "drain_runs_cross_slope")


def test_drain_runs_cross_slope_exempts_a_trimmed_inwall_drain():
    # an in-wall drain is cut short of the patrol ring and sluice-gated into a conduit to the moat,
    # so what remains is the last leg to the outfall - a stub, not a contour collector
    M = _drain_map()
    M["field_ditches"][0]["trimmed"] = True
    assert "drain_runs_cross_slope" not in f_only(M, "drain_runs_cross_slope")


def test_drain_flows_downhill_reads_the_NAMED_discharge_channel_over_an_uphill_edge():
    # Nagahara's fnn2 exactly: the drain's HEAD sits inside the 32px at_edge tolerance of the frame's
    # TOP (upslope), so the edge signal alone called the high end the outfall and reported the water
    # running backwards. A discharge channel NAMING this field puts the real outfall at the tail, and
    # pooling the evidence and taking the LOWEST end resolves it.
    M = _drain_map(
        field_ditches=[{"role": "drain", "field": "f1", "poly": [[400, 20], [700, 300]], "w": 1.5}],
        channels=[{"poly": [[700, 300], [780, 360]], "frm": {"kind": "drain", "name": "f1"}, "to": {"kind": "offmap"}, "w": 2.5}],
    )
    assert "drain_flows_downhill" not in f_only(M, "drain_flows_downhill")


def test_drain_flows_downhill_ignores_a_discharge_channel_naming_ANOTHER_field():
    # the whole point of naming: Hirameki carries seven discharge channels and several sit on top of
    # a different field's drain, so proximity matching mis-attributed them
    M = _drain_map(
        field_ditches=[{"role": "drain", "field": "f1", "poly": [[400, 20], [700, 300]], "w": 1.5}],
        channels=[{"poly": [[700, 300], [780, 360]], "frm": {"kind": "drain", "name": "SOMEWHERE-ELSE"}, "to": {"kind": "offmap"}, "w": 2.5}],
    )
    assert "drain_flows_downhill" in f_only(M, "drain_flows_downhill")


def test_drain_flows_downhill_still_fires_on_a_genuinely_backwards_drain():
    # outfall on a stream at the HIGH end: the evidence is a real sink, so the check must still bite
    M = _drain_map(
        streams=[{"poly": [[300, 250], [900, 250]], "w": 8, "flow": "forward", "flow_deg": 0.0, "frm": {"kind": "offmap"}, "to": {"kind": "offmap"}}],
        field_ditches=[{"role": "drain", "field": "f1", "poly": [[400, 260], [430, 800]], "w": 1.5}],
    )
    assert "drain_flows_downhill" in f_only(M, "drain_flows_downhill")


def test_bund_beans_on_bunds_fires_on_a_bead_buried_by_a_later_plot():
    # a bead on the host's east bund (x=400) sits 100px inside the filler, which paints after
    # its host - the bund stroke under it is not visible ground on the finished map
    assert "bund_beans_on_bunds" in f_only(_bb_M([[400, 300]], [_BB_HOST, _BB_FILLER]), "bund_beans_on_bunds")


def test_bund_beans_on_bunds_fires_on_a_bead_in_open_ground():
    # a bead near no bund at all (the bare fan floor)
    assert "bund_beans_on_bunds" in f_only(_bb_M([[700, 700]], [_BB_HOST, _BB_FILLER]), "bund_beans_on_bunds")


def test_bund_beans_on_bunds_passes_beads_on_visible_bunds():
    # the host's west bund (x=200) stands clear of the filler; and a bead on the FILLER's own
    # west bund (x=300), though it lies deep inside the host, is legal - the filler paints
    # last, so its stroke is the visible one and the bead reads as sitting on that seam
    assert "bund_beans_on_bunds" not in f_only(_bb_M([[200, 300], [300, 300]], [_BB_HOST, _BB_FILLER]), "bund_beans_on_bunds")


def test_bund_beans_on_bunds_skips_manifests_without_the_recording():
    # pre-2026-08-15 manifests record no plot_rings; regeneration adds them (the recording is
    # unconditional at the one draw site - see test_draw_comb_field_records_rings_and_beads)
    assert "bund_beans_on_bunds" not in f_only(_bb_M([[400, 300]], []), "bund_beans_on_bunds")


def test_bund_beans_on_bunds_survives_geometry_far_off_the_canvas():
    # negative fixtures carry deliberately insane geometry; the index box is clamped to the
    # canvas on insert, so an off-map ring is skipped (it is not visible ground - a bead
    # claiming to sit on it still fires) instead of allocating billions of grid cells
    assert "bund_beans_on_bunds" in f_only(_bb_M([[9000000, 300]], [[[8999900, 200], [9000100, 200], [9000100, 400], [8999900, 400]]]), "bund_beans_on_bunds")


def test_bund_beans_on_bunds_fires_on_a_bead_under_the_ditch_nets_stroke():
    # the ditch net draws LATE - over bund and bead alike - so a bead inside a late stroke's
    # drawn band is buried ink: the record attests a bead nobody can see
    M = {**_bb_M([[200, 300]], [_BB_HOST]), "drawn_channels": [{"pts": [[200, 180], [200, 420]], "late": True, "w0": 8.0, "w1": 8.0}]}
    assert "bund_beans_on_bunds" in f_only(M, "bund_beans_on_bunds")


def test_bund_beans_on_bunds_ignores_early_water_and_the_banks():
    # a non-late stroke composites UNDER the plots, so it cannot bury a bead; a 1-point stroke
    # is unpaintable; and a bead 5px off an 8px stroke's centerline rides the BANK, not the water
    M = {
        **_bb_M([[200, 300]], [_BB_HOST]),
        "drawn_channels": [
            {"pts": [[200, 180], [200, 420]], "late": False, "w0": 8.0, "w1": 8.0},
            {"pts": [[205, 180]], "late": True, "w0": 8.0, "w1": 8.0},
            {"pts": [[205, 180], [205, 420]], "late": True, "w0": 8.0, "w1": 8.0},
        ],
    }
    assert "bund_beans_on_bunds" not in f_only(M, "bund_beans_on_bunds")


def test_bund_beans_on_bunds_fires_on_a_bead_in_pond_water():
    # the source pond and a pocket pond both paint water over the bead's ground; a degenerate
    # pond thinner than the tolerance cannot bury anything (the guard, not a verdict)
    assert "bund_beans_on_bunds" in f_only({**_bb_M([[200, 300]], [_BB_HOST]), "pond": [200, 300, 30, 20]}, "bund_beans_on_bunds")
    assert "bund_beans_on_bunds" in f_only({**_bb_M([[200, 300]], [_BB_HOST]), "field_ponds": [{"x": 200, "y": 300, "rx": 30, "ry": 20}]}, "bund_beans_on_bunds")
    assert "bund_beans_on_bunds" not in f_only({**_bb_M([[200, 300]], [_BB_HOST]), "pond": [200, 300, 1.5, 1.5]}, "bund_beans_on_bunds")


# ---- comb_floor_ends_at_the_collector: floor past the (flat-extended) drain line -------------
def _floor_M(outline, dd=90.0, fork=(400.0, 200.0), drain=None, gen="hamletgen"):
    """Fall straight down-screen (dd=90): u = x, f = y; the collector crosses the low side at
    y=800 (thin head at x=300, outfall at x=700), plus a main channel so the role filter is
    exercised on every run."""
    M = {
        "meta": {"scale": "hamlet", "down_deg": 90, "W": 1200, "H": 1200},
        "fields": [{**_field("f", 200, 200, 900, 900), "outline": outline, "down_deg": dd, "plot_rings": []}],
        "field_ditches": [
            {"poly": [[200, 250], [900, 250]], "role": "main", "field": "f", "w": 8.0, "w_tail": 3.0},
            drain or {"poly": [[300, 800], [700, 800]], "role": "drain", "field": "f", "w": 3.0, "w_tail": 12.0},
        ],
    }
    if fork:
        M["fields"][0]["fork"] = list(fork)
    if gen:
        M["meta"]["generated_by"] = gen
    return M


def _floor_f(M):
    return check_village.gate(M, verbose=False, only={"comb_floor_ends_at_the_collector"})


def test_comb_floor_fires_on_an_outline_vertex_below_the_collector_line():
    # inside the drain's u-span, 30 px down-fall of the interpolated line
    assert "comb_floor_ends_at_the_collector" in _floor_f(_floor_M([[300, 300], [700, 300], [500, 830]]))


def test_comb_floor_fires_on_the_needle_beyond_the_drains_thin_head():
    # the Mizuguchi shape: past the head end the boundary continues LEVEL, and the outline
    # dips 100 px below it - a bare needle no plot can ever occupy
    assert "comb_floor_ends_at_the_collector" in _floor_f(_floor_M([[250, 900], [700, 300], [300, 300]]))


def test_comb_floor_passes_when_the_outline_hugs_the_collector():
    assert "comb_floor_ends_at_the_collector" not in _floor_f(_floor_M([[300, 300], [700, 300], [700, 800], [300, 800]]))


def test_comb_floor_tolerates_the_drawn_water_width():
    # 12 px past the centerline is inside the 16 px tolerance (max drain halfw 6 + slack): the
    # outline's low edge IS the drain polyline, so near-line vertices must never fire
    assert "comb_floor_ends_at_the_collector" not in _floor_f(_floor_M([[300, 300], [700, 300], [500, 812]]))


def test_comb_floor_only_governs_comb_fans():
    # no `fork` = not a build_comb fan: a polder's floor legitimately runs past its inner ring
    # drain to the dike, so the rule cannot bind there
    assert "comb_floor_ends_at_the_collector" not in _floor_f(_floor_M([[300, 300], [700, 300], [500, 900]], fork=None))


def test_comb_floor_skips_a_field_with_no_outline():
    M = _floor_M([[300, 300], [700, 300], [500, 900]])
    del M["fields"][0]["outline"]
    assert "comb_floor_ends_at_the_collector" not in _floor_f(M)


def test_comb_floor_skips_legacy_maps():
    # no meta.generated_by = a legacy comb; it inherits the rule when converted (migration doctrine)
    assert "comb_floor_ends_at_the_collector" not in _floor_f(_floor_M([[300, 300], [700, 300], [500, 900]], gen=None))


def test_comb_floor_skips_a_degenerate_drain_poly():
    M = _floor_M([[300, 300], [700, 300], [500, 900]], drain={"poly": [[300, 800]], "role": "drain", "field": "f", "w": 3.0, "w_tail": 12.0})
    assert "comb_floor_ends_at_the_collector" not in _floor_f(M)


def test_comb_floor_ignores_another_fields_drain():
    M = _floor_M([[300, 300], [700, 300], [500, 900]])
    M["field_ditches"][1]["field"] = "other"
    assert "comb_floor_ends_at_the_collector" not in _floor_f(M)


def test_comb_floor_reads_the_map_fall_when_the_field_has_none():
    M = _floor_M([[300, 300], [700, 300], [500, 830]])
    del M["fields"][0]["down_deg"]
    assert "comb_floor_ends_at_the_collector" in _floor_f(M)


# ---- flooded_plots_read_as_basins: a pointed blue sliver reads as a pond -----------------------
def _basin_M(rings, flooded, gen="hamletgen"):
    M = {
        "meta": {"scale": "hamlet", "down_deg": 90, "W": 1200, "H": 1200},
        "fields": [{**_field("f", 200, 200, 900, 900), "plot_rings": rings}],
        "flooded_plots": flooded,
    }
    if gen:
        M["meta"]["generated_by"] = gen
    return M


def _basin_f(M):
    return check_village.gate(M, verbose=False, only={"flooded_plots_read_as_basins"})


_NEEDLE = [[300, 300], [500, 308], [500, 300]]  # ~2.3 deg apex
_STRIP = [[300, 400], [500, 400], [500, 418], [300, 418]]  # a bunded rectangle


def _cent(r):
    return [sum(p[0] for p in r) / len(r), sum(p[1] for p in r) / len(r)]


def test_flooded_basins_fires_on_a_pointed_blue_sliver():
    # the Sawada fan-seam capture: a needle apex carrying the water tint reads as a tiny pond
    assert "flooded_plots_read_as_basins" in _basin_f(_basin_M([_NEEDLE, _STRIP], [_cent(_NEEDLE)]))


def test_flooded_basins_passes_a_rectangular_flooded_strip():
    assert "flooded_plots_read_as_basins" not in _basin_f(_basin_M([_NEEDLE, _STRIP], [_cent(_STRIP)]))


def test_flooded_basins_gives_the_carve_its_borderline_band():
    # ~19.8 deg apex: demoted by the carve at 25 deg, but the gate holds its fire at 15 - a
    # borderline plot the carve let through must not false-fire
    mid = [[300, 500], [500, 572], [500, 500]]
    assert "flooded_plots_read_as_basins" not in _basin_f(_basin_M([mid], [_cent(mid)]))


def test_flooded_basins_skips_an_unmatched_centroid():
    # a tint record with no ring near it (a fill path with no recorded ring) is not judgeable
    assert "flooded_plots_read_as_basins" not in _basin_f(_basin_M([_STRIP], [[50.0, 50.0]]))


def test_flooded_basins_skips_a_manifest_with_no_tint_record():
    M = _basin_M([_NEEDLE], [_cent(_NEEDLE)])
    del M["flooded_plots"]
    assert "flooded_plots_read_as_basins" not in _basin_f(M)


def test_flooded_basins_skips_legacy_maps():
    assert "flooded_plots_read_as_basins" not in _basin_f(_basin_M([_NEEDLE], [_cent(_NEEDLE)], gen=None))


# --- paddy_plot_seams_shared -------------------------------------------------------------
# TWO ADJACENT BASINS SHARE ONE BUND (GM 2026-08-17). The two faults, and every way the rule is
# allowed NOT to fire - each of the exemptions below was a false positive the check shipped with
# before it was calibrated against the real fan.


def _seam_M(rings, ditches=(), ponds=(), gen="hamletgen"):
    M = manifest(
        meta={"scale": "hamlet", "W": 600, "H": 400, "ftpx": 1.0, "down_deg": 90, **({"generated_by": gen} if gen else {})},
        fields=[{"name": "sf", "kind": "paddy", "outline": [[0, 0], [600, 0], [600, 400], [0, 400]], "bbox": [0, 0, 600, 400], "plot_rings": [list(r) for r in rings]}],
        field_ditches=[dict(d, field="sf") for d in ditches],
        field_ponds=list(ponds),
    )
    return M


def _seam_f(M):
    return check_village.gate(M, only={"paddy_plot_seams_shared"}, verbose=False)


def _box(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def test_paddy_seams_fires_on_a_bare_strip_between_two_basins():
    # the GM's report: two walls with unplanted floor between them where one wall belongs
    assert "paddy_plot_seams_shared" in _seam_f(_seam_M([_box(10, 10, 110, 110), _box(122, 10, 222, 110)]))


def test_paddy_seams_fires_on_a_bund_ring_drawn_inside_a_basin():
    # the standalone rectangle: a whole ring sitting in the middle of somebody else's paddy
    assert "paddy_plot_seams_shared" in _seam_f(_seam_M([_box(10, 10, 210, 210), _box(60, 60, 160, 160)]))


def test_paddy_seams_stands_aside_for_a_dike_pond_block():
    # feature 139: two ponds a dike apart are the 桑基魚塘 fabric, not a doubled aze - the ~22 ft
    # strip between the rings IS the planted dike. The same rings fire on a paddy field.
    rings = [_box(10, 10, 110, 110), _box(132, 10, 232, 110)]
    assert "paddy_plot_seams_shared" in _seam_f(_seam_M(rings))
    M = _seam_M(rings)
    M["meta"]["field_archetype"] = "mulberry_dike_fishpond"
    assert "paddy_plot_seams_shared" not in _seam_f(M)


def test_paddy_seams_passes_basins_that_share_their_bund_exactly():
    assert "paddy_plot_seams_shared" not in _seam_f(_seam_M([_box(10, 10, 110, 110), _box(110, 10, 210, 110)]))


def test_paddy_seams_passes_a_strip_a_delivery_ditch_runs_down():
    # the carve holds each bank's bund off the water on purpose - two basins parted by a ditch are
    # correct, and this is the one honest reason for a gap
    ditch = {"poly": [[116, 0], [116, 400]], "role": "branch", "w": 10.0, "w_tail": 10.0}
    assert "paddy_plot_seams_shared" not in _seam_f(_seam_M([_box(10, 10, 110, 110), _box(122, 10, 222, 110)], ditches=[ditch]))


def test_paddy_seams_passes_a_strip_a_field_pond_sits_in():
    pond = {"x": 116.0, "y": 60.0, "rx": 8.0, "ry": 52.0}
    assert "paddy_plot_seams_shared" not in _seam_f(_seam_M([_box(10, 10, 110, 110), _box(122, 10, 222, 110)], ponds=[pond]))


def test_paddy_seams_passes_the_edge_of_the_planted_block():
    # a lone basin's outer wall faces the fan's rim, not another basin - nothing to share with
    assert "paddy_plot_seams_shared" not in _seam_f(_seam_M([_box(10, 10, 110, 110)]))


def test_paddy_seams_passes_a_bund_running_away_from_a_corner_neighbour():
    # at a T-junction the far end of a wall recedes from the basin it corners on, with nothing
    # wrong: the crossing to that neighbor runs ALONG this wall, not across it
    assert "paddy_plot_seams_shared" not in _seam_f(_seam_M([_box(10, 10, 110, 110), _box(110, 10, 210, 110), _box(10, 110, 210, 210)]))


def test_paddy_seams_passes_a_gap_measured_across_the_basins_own_ground():
    # the fan toe laps its closing-rank plots, so a wall can have another basin's wall 20 px off
    # ACROSS ITS OWN GROUND. There is no second wall to remove there and nothing bare between them
    # - the later plot simply paints over the stretch it covers - so the rule must hold its fire.
    assert "paddy_plot_seams_shared" not in _seam_f(_seam_M([_box(10, 10, 200, 110), _box(150, 30, 320, 160)]))


def test_paddy_seams_skips_legacy_maps():
    assert "paddy_plot_seams_shared" not in _seam_f(_seam_M([_box(10, 10, 110, 110), _box(122, 10, 222, 110)], gen=None))


def test_paddy_seams_skips_a_field_that_records_no_plot_rings():
    M = _seam_M([_box(10, 10, 110, 110), _box(122, 10, 222, 110)])
    del M["fields"][0]["plot_rings"]
    assert "paddy_plot_seams_shared" not in _seam_f(M)


# --- paddy_plot_rings_overcount_stays_marginal --------------------------------------------
# The record is a PAINT-ORDER STACK by decision, and this rule is the ceiling that keeps the
# accepted approximation small enough for the contract in comb.py's record comment to stay true.
# Its teeth are HERE, deliberately, not in a frozen fixture: the pre-close_seams Inashiro scores
# 2.58% against a worst live cohort seed of 2.49%, so a map-wide lap fraction does not separate
# that defect from ordinary fabric (paddy_plot_seams_shared is the rule that does). This one
# catches DRIFT, and drift is what a synthetic break models.


def _lap_f(M):
    return check_village.gate(M, only={"paddy_plot_rings_overcount_stays_marginal"}, verbose=False)


def test_paddy_ring_overcount_fires_when_a_ring_is_painted_over_its_neighbour():
    # half of one basin laid over the next: 25% of the recorded fabric counted twice
    assert "paddy_plot_rings_overcount_stays_marginal" in _lap_f(_seam_M([_box(10, 10, 110, 110), _box(60, 10, 160, 110)]))


def test_paddy_ring_overcount_passes_a_shallow_lap():
    # a filler lapping a couple of feet onto its neighbor is correct ink - the later plot simply
    # paints out the stretch of bund it covers, and the pair reads as one shared aze
    assert "paddy_plot_rings_overcount_stays_marginal" not in _lap_f(_seam_M([_box(10, 10, 110, 110), _box(108, 10, 208, 110)]))


def test_paddy_ring_overcount_passes_basins_that_share_their_bund_exactly():
    assert "paddy_plot_rings_overcount_stays_marginal" not in _lap_f(_seam_M([_box(10, 10, 110, 110), _box(110, 10, 210, 110)]))


def test_paddy_ring_overcount_skips_legacy_maps():
    assert "paddy_plot_rings_overcount_stays_marginal" not in _lap_f(_seam_M([_box(10, 10, 110, 110), _box(60, 10, 160, 110)], gen=None))


def test_paddy_ring_overcount_skips_a_field_that_records_no_plot_rings():
    M = _seam_M([_box(10, 10, 110, 110), _box(60, 10, 160, 110)])
    del M["fields"][0]["plot_rings"]
    assert "paddy_plot_rings_overcount_stays_marginal" not in _lap_f(M)


def _worth_M(rings, cell=1488.0, gen="hamletgen"):
    """A generated comb fan recording its design `cell` - what the size floor measures against."""
    return manifest(
        meta={"scale": "hamlet", "W": 1000, "H": 1000, "ftpx": 1.0, "generated_by": gen},
        fields=[{**_field("f", 10, 10, 900, 900), "cell": cell, "plot_rings": rings}],
    )


def test_paddy_basins_are_worth_their_bund_fires_on_a_fragment_of_the_design_cell():
    # 0.20 of a 1,488 sq ft cell is 298; a 15 x 15 basin is 225, a 40 x 40 one is 1,600.
    assert "paddy_basins_are_worth_their_bund" in f_only(_worth_M([_box(100, 100, 140, 140), _box(300, 300, 315, 315)]), "paddy_basins_are_worth_their_bund")
    assert "paddy_basins_are_worth_their_bund" not in f_only(_worth_M([_box(100, 100, 140, 140), _box(300, 300, 340, 340)]), "paddy_basins_are_worth_their_bund")


def test_paddy_basins_are_worth_their_bund_skips_a_field_recording_no_design_cell():
    # A terrace, ribbon or polder fan records no `cell` and is deliberately exempt - hill rice is
    # where the real micro-basins are (research/fields.md, "Minimum basin SIZE"). With no comb fan
    # on the map the check does not run at all rather than passing vacuously.
    M = _worth_M([_box(300, 300, 315, 315)])
    del M["fields"][0]["cell"]
    assert "paddy_basins_are_worth_their_bund" not in f_only(M, "paddy_basins_are_worth_their_bund")


def test_paddy_basins_are_worth_their_bund_ignores_a_degenerate_ring():
    # A ring with fewer than three vertices encloses nothing, so its area is 0 and it would trip a
    # floor stated as an area - but it is not a basin at all and there is nothing to absorb. The
    # guard is defensive (no shipped manifest carries one), which is exactly why it needs a test:
    # without one the branch is unreachable and a later edit could invert it unnoticed.
    assert "paddy_basins_are_worth_their_bund" not in f_only(_worth_M([_box(100, 100, 140, 140), [[500, 500], [520, 500]]]), "paddy_basins_are_worth_their_bund")


def test_paddy_basins_are_worth_their_bund_is_off_for_a_legacy_map():
    # no meta.generated_by = a legacy comb map; it inherits the rule at conversion (migration doctrine)
    assert "paddy_basins_are_worth_their_bund" not in f_only(_worth_M([_box(300, 300, 315, 315)], gen=None), "paddy_basins_are_worth_their_bund")


def _stag_M(rings, gen="hamletgen", ftpx=1.0):
    """A generated comb fan whose plot rings are the thing under test."""
    return manifest(
        meta={"scale": "hamlet", "W": 1000, "H": 1000, "ftpx": ftpx, "generated_by": gen},
        fields=[{**_field("f", 10, 10, 900, 900), "cell": 1488.0, "plot_rings": rings}],
    )


# A wall running north at x=100, hopping 9 ft east, carrying on north, hopping 9 ft east again and
# carrying on - the staircase the GM reported. One hop on its own is the SINGLE step the rule allows.
_STAIR = [[100, 0], [100, 60], [109, 60], [109, 120], [118, 120], [118, 300], [300, 300], [300, 0]]
_ONE_STEP = [[100, 0], [100, 60], [109, 60], [109, 300], [300, 300], [300, 0]]
_STRAIGHT = [[100, 0], [100, 300], [300, 300], [300, 0]]


def test_paddy_bunds_do_not_stagger_fires_on_a_flight_of_steps():
    assert "paddy_bunds_do_not_stagger" in f_only(_stag_M([_STAIR]), "paddy_bunds_do_not_stagger")


def test_paddy_bunds_do_not_stagger_allows_a_single_nudge():
    # ONE step is an awkward corner where a scrap of ground had one home; a FLIGHT of them is a weld
    # pitch out of register with the fabric. The absolute rule lives in tools/jogs.py.
    assert "paddy_bunds_do_not_stagger" not in f_only(_stag_M([_ONE_STEP]), "paddy_bunds_do_not_stagger")
    assert "paddy_bunds_do_not_stagger" not in f_only(_stag_M([_STRAIGHT]), "paddy_bunds_do_not_stagger")


def test_paddy_bunds_do_not_stagger_passes_steps_too_small_to_see():
    # 2 ft is under the 3 ft floor `paddy_plot_seams_shared` reasons to from AZE_FT: two bunds this
    # close draw as one line.
    tiny = [[100, 0], [100, 60], [102, 60], [102, 120], [104, 120], [104, 300], [300, 300], [300, 0]]
    assert "paddy_bunds_do_not_stagger" not in f_only(_stag_M([tiny]), "paddy_bunds_do_not_stagger")


def test_paddy_bunds_do_not_stagger_passes_long_limbs():
    # a 40 ft hop is not a step in a wall, it is a LIMB - the honest odd shape reclamation leaves
    limbs = [[100, 0], [100, 60], [140, 60], [140, 120], [180, 120], [180, 300], [400, 300], [400, 0]]
    assert "paddy_bunds_do_not_stagger" not in f_only(_stag_M([limbs]), "paddy_bunds_do_not_stagger")


def test_paddy_bunds_do_not_stagger_passes_a_gently_curving_bund():
    # THE CLAUSE THIS HOLDS: a curve sampled into segments is a run, a link and a run resuming
    # near-parallel, with a few feet of offset coming purely from the bend. Kuwabata's long curved
    # parcels reported 57 steps on 43 rings without the corner test and 0 with it.
    curve = [[0, 0]] + [[30 * k, 7 * k + 1.5 * k * k] for k in range(1, 9)] + [[240, 500], [0, 500]]
    assert "paddy_bunds_do_not_stagger" not in f_only(_stag_M([curve]), "paddy_bunds_do_not_stagger")


def test_paddy_bunds_do_not_stagger_passes_a_narrow_basin_on_its_own_end_wall():
    # THE REASON HEADINGS ARE COMPARED OVER THE FULL CIRCLE. A thin rectangle is two long parallel
    # runs a short link apart, which modulo 180 deg is indistinguishable from a step.
    assert "paddy_bunds_do_not_stagger" not in f_only(_stag_M([[[100, 100], [100, 112], [400, 112], [400, 100]]]), "paddy_bunds_do_not_stagger")


def test_paddy_bunds_do_not_stagger_reads_the_step_in_feet_at_city_scale():
    # The thresholds are stated in FEET and divided by ftpx, so the same drawn shape is judged the
    # same way at every tier: at ftpx 3 a 1 px hop is 3 real ft and on the floor, 0.6 px is under it.
    big = [[100, 0], [100, 20], [101, 20], [101, 40], [102, 40], [102, 100], [200, 100], [200, 0]]
    small = [[100, 0], [100, 20], [100.6, 20], [100.6, 40], [101.2, 40], [101.2, 100], [200, 100], [200, 0]]
    assert "paddy_bunds_do_not_stagger" in f_only(_stag_M([big], ftpx=3.0), "paddy_bunds_do_not_stagger")
    assert "paddy_bunds_do_not_stagger" not in f_only(_stag_M([small], ftpx=3.0), "paddy_bunds_do_not_stagger")


def test_paddy_bunds_do_not_stagger_ignores_a_quad():
    # a four-vertex ring has no room for a run, a hop and the run resuming
    assert "paddy_bunds_do_not_stagger" not in f_only(_stag_M([[[100, 100], [100, 200], [200, 205], [200, 100]]]), "paddy_bunds_do_not_stagger")


def test_paddy_bunds_do_not_stagger_is_off_for_a_legacy_map():
    # no meta.generated_by = a legacy comb map; it inherits the rule at conversion (migration doctrine)
    assert "paddy_bunds_do_not_stagger" not in f_only(_stag_M([_STAIR], gen=None), "paddy_bunds_do_not_stagger")


def test_hamlet_and_village_boards_must_be_roadside():
    # GM 2026-08-26 (feature 133 T13): at the lane tiers the board stands within ~12 ft
    # (center to lane centerline) - 24 ft off, Inashiro's old seat, fires; 10 ft passes.
    # Towns keep the 60 ft rule until their maps re-roll.
    lane = [[0, 500], [1000, 500]]
    assert "kosatsuba_by_the_road" in f_only({"meta": {"scale": "hamlet", "ftpx": 1}, "kosatsuba": [_kosatsuba(500, 524)], "lane": lane}, "kosatsuba_by_the_road")
    assert "kosatsuba_by_the_road" not in f_only({"meta": {"scale": "village", "ftpx": 2}, "kosatsuba": [_kosatsuba(500, 505)], "lane": lane}, "kosatsuba_by_the_road")
    assert "kosatsuba_by_the_road" not in f_only({"meta": {"scale": "town"}, "kosatsuba": [_kosatsuba(500, 524)], "road": lane}, "kosatsuba_by_the_road")


def _scripted(**over):
    """A hamletgen-shaped manifest: the census keys `finish()` writes (feature 139)."""
    m = manifest(**over)
    m["meta"]["generated_by"] = "hamletgen"
    m.setdefault("ink_classes", {"-": 3, "farmhouse": 2})
    m.setdefault("unclassed_ink", [])
    m.setdefault("unregistered_classes", [])
    return m


def test_all_ink_is_ruled_on_fires_and_passes():
    """On a scripted hamlet every drawn element is in a feature class or ruled not highlighted, and
    every class used is registered (feature 139 FR-009; the GM: "judgment calls to make about what
    things get highlighted and which things do not" - unclassed ink is an unmade decision)."""
    bad = _scripted(unclassed_ink=['<rect> <rect x="1" y="1" width="2" height="2"/>'])
    assert "all_ink_is_ruled_on" in f_only(bad, "all_ink_is_ruled_on"), "ink nobody ruled on must fire"
    unregistered = _scripted(unregistered_classes=["flying castle"])
    assert "all_ink_is_ruled_on" in f_only(unregistered, "all_ink_is_ruled_on"), "a class the registry does not know must fire"
    good = _scripted(ink_classes={"-": 3, "farmhouse": 2, "paddy": 40})
    assert "all_ink_is_ruled_on" not in f_only(good, "all_ink_is_ruled_on"), "ruled-out ink (the `-` class) never fires"
    hand = manifest(unclassed_ink=["<rect> x"])  # no generated_by: a hand-authored tier, its vocabulary is later work
    assert "all_ink_is_ruled_on" not in f_only(hand, "all_ink_is_ruled_on")
