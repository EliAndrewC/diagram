"""Gate checks for field cover, cremation, streams and field ditches (test_segments_05_fields_and_funerary split by feature 122; tests verbatim)."""

from tests.check_village._builders import (
    _FORK_MAINS,
    _city_dead,
    _cross_M,
    _dryplot,
    _farmhouse,
    _field,
    _nuc_grid,
    _nuc_village_M,
    _tips_M,
    f_only,
)


# ---- field_ditches_reach_source_and_sink (role-aware: supply->source, drain->sink) ----------
def test_field_ditches_reach_source_and_sink_fires_when_ungrounded():
    # a supply ditch with no pond source AND a drain with no runoff sink - both dangle (the failure
    # path of the role-aware grounding). The GOOD case is covered by the real maps (kikuta passes with
    # its full pond->canal->cascade->drain->off-map network; the wip Hoshigaoka likewise).
    M = {"field_ditches": [{"poly": [[300, 300], [500, 300]], "role": "main", "field": "f"}, {"poly": [[300, 600], [500, 600]], "role": "drain", "field": "f"}]}
    assert "field_ditches_reach_source_and_sink" in f_only(M, "field_ditches_reach_source_and_sink")


def test_delivery_ditches_taper_fires_on_a_blunt_ditch():
    # a delivery ditch (role "branch") ending at nearly full width - it should have shed its water
    M = {"field_ditches": [{"poly": [[300, 300], [500, 500]], "role": "branch", "field": "f", "w": 4.0, "w_tail": 4.0}]}
    assert "delivery_ditches_taper" in f_only(M, "delivery_ditches_taper")


def test_delivery_ditches_taper_passes_when_it_narrows():
    M = {"field_ditches": [{"poly": [[300, 300], [500, 500]], "role": "branch", "field": "f", "w": 4.0, "w_tail": 1.5}]}
    assert "delivery_ditches_taper" not in f_only(M, "delivery_ditches_taper")


def test_delivery_ditches_taper_exempts_ditches_without_recorded_widths():
    # the older water_field engine records no head/tail width - nothing to judge, so it is skipped
    M = {"field_ditches": [{"poly": [[300, 300], [500, 500]], "role": "branch", "field": "f"}]}
    assert "delivery_ditches_taper" not in f_only(M, "delivery_ditches_taper")


def test_channels_join_not_cross_at_fork_fires_on_a_delivery_at_the_division():
    # a delivery (role "branch") taking off AT the fork - the 4-way star that reads as a crossroads
    M = {"field_ditches": _FORK_MAINS + [{"poly": [[100, 100], [140, 140]], "role": "branch", "field": "f", "w": 2.7, "w_tail": 1.0}]}
    assert "channels_join_not_cross_at_fork" in f_only(M, "channels_join_not_cross_at_fork")


def test_channels_join_not_cross_at_fork_passes_when_the_delivery_is_downstream():
    # the delivery branches off a supply canal 50px downstream of the fork - a clean offtake
    M = {"field_ditches": _FORK_MAINS + [{"poly": [[150, 100], [150, 145]], "role": "branch", "field": "f", "w": 2.7, "w_tail": 1.0}]}
    assert "channels_join_not_cross_at_fork" not in f_only(M, "channels_join_not_cross_at_fork")


def test_dry_plot_furrows_vary_fires_when_two_neighbours_share_an_angle():
    # 4 dry plots in a row; the first two are edge-adjacent AND run their furrows the same way -> fires
    dp = [_dryplot(300, 0.2), _dryplot(340, 0.2), _dryplot(380, 0.9), _dryplot(420, 0.4)]
    assert "dry_plot_furrows_vary" in f_only({"dry_plots": dp}, "dry_plot_furrows_vary")


def test_dry_plot_furrows_vary_passes_when_neighbours_differ():
    # adjacent plots alternate orientation, so no neighboring pair shares a row direction
    dp = [_dryplot(300, 0.2), _dryplot(340, 0.9), _dryplot(380, 0.2), _dryplot(420, 0.9)]
    assert "dry_plot_furrows_vary" not in f_only({"dry_plots": dp}, "dry_plot_furrows_vary")


def test_dry_plot_furrows_vary_skipped_for_a_contour_village():
    # a STEEP / terraced village declares contour furrows (meta.dry_furrows_vary=False) - the rows converge on
    # the contour for erosion control, so identical adjacent angles are CORRECT and the check does not fire
    dp = [_dryplot(300, 0.2), _dryplot(340, 0.2), _dryplot(380, 0.2), _dryplot(420, 0.2)]  # all aligned
    assert "dry_plot_furrows_vary" not in f_only({"meta": {"dry_furrows_vary": False}, "dry_plots": dp}, "dry_plot_furrows_vary")


# ---- dry_plot_seams_shared (hem seams are single straight lines both quads lie on) -----------


def test_field_ditch_tips_land_on_the_trunk_fires_on_a_tip_past_the_canal():
    # both tips 6px BEYOND the trunk centerline: inside near_any's 13px net (so field_ditches_terminate
    # is happy) but 3.5px outside the trunk's drawn band, so a stub shows through
    assert "field_ditch_tips_land_on_the_trunk" in f_only(_tips_M([[100, 256], [100, 94]]), "field_ditch_tips_land_on_the_trunk")


def test_field_ditch_tips_land_on_the_trunk_passes_on_a_tip_in_the_band():
    # tips 1px off the centerline - buried under the trunks' own strokes, a clean T at each end
    assert "field_ditch_tips_land_on_the_trunk" not in f_only(_tips_M([[100, 249], [100, 101]]), "field_ditch_tips_land_on_the_trunk")


def test_water_channels_join_not_cross_fires_on_a_stub_through_the_trunk():
    # the vertical stroke crosses the trunk and stops 6px past it; the trunk's own nearest end is
    # 100px away, so NEITHER tip is buried in the other's band -> it reads as a 4-way intersection.
    # The third stroke is far off in the corner (the bbox-reject path).
    M = _cross_M(
        {"pts": [[0, 100], [200, 100]], "w0": 5, "w1": 5},
        {"pts": [[100, 150], [100, 94]], "w0": 3, "w1": 3},
        {"pts": [[380, 380], [390, 390]], "w0": 3, "w1": 3},
    )
    assert "water_channels_join_not_cross" in f_only(M, "water_channels_join_not_cross")


def test_water_channels_join_not_cross_passes_on_a_shallow_offtake():
    # a delivery taking off at a shallow angle overruns the crossing along its OWN line by ~40px,
    # yet its tip stays 1px off the trunk centerline - under the ink, a clean Y. The second pair
    # (widths defaulted, bboxes overlapping but never crossing) exercises the no-crossing path.
    M = _cross_M(
        {"pts": [[0, 100], [200, 100]], "w0": 5, "w1": 5},
        {"pts": [[150, 140], [50, 99]], "w0": 3, "w1": 3},
        {"pts": [[10, 200], [190, 200]]},
    )
    assert "water_channels_join_not_cross" not in f_only(M, "water_channels_join_not_cross")


def test_streams_avoid_fields_fires():
    M = {"fields": [_field("f", 100, 100, 400, 400)], "streams": [{"poly": [[200, 200], [200, 500]]}]}  # first point sits inside the field
    assert "streams_avoid_fields" in f_only(M, "streams_avoid_fields")


def test_streams_avoid_fields_allows_a_drain_fed_brook():
    # a brook anchored to the field's DRAIN starts at the outfall (inside the envelope) and runs off-map - legit
    M = {"fields": [_field("f", 100, 100, 400, 400)], "streams": [{"poly": [[300, 380], [300, 550], [300, 700]], "frm": {"kind": "drain"}, "to": {"kind": "offmap"}}]}
    assert "streams_avoid_fields" not in f_only(M, "streams_avoid_fields")


def test_streams_avoid_fields_still_fires_when_a_drain_brook_reenters_the_field():
    # a drain-fed brook that leaves then CUTS BACK across the crop is still a defect
    M = {"fields": [_field("f", 100, 100, 400, 400)], "streams": [{"poly": [[300, 380], [300, 600], [250, 250]], "frm": {"kind": "drain"}, "to": {"kind": "offmap"}}]}  # last leg re-enters the field
    assert "streams_avoid_fields" in f_only(M, "streams_avoid_fields")


def test_streams_avoid_fields_allows_a_stream_that_ends_at_the_field():
    # a stream anchored INTO the field (to=field) ends inside it - the connection is legitimate
    M = {
        "fields": [_field("f", 100, 100, 400, 400)],
        "streams": [{"poly": [[300, 700], [300, 500], [300, 300]], "frm": {"kind": "offmap"}, "to": {"kind": "field", "name": "f"}}],
    }  # ends inside the field
    assert "streams_avoid_fields" not in f_only(M, "streams_avoid_fields")


def test_fields_clear_of_road_fires():
    M = {"fields": [_field("f", 100, 100, 400, 400)], "road": [[50, 250], [500, 250]], "road_width": 26}
    assert "fields_clear_of_road" in f_only(M, "fields_clear_of_road")


def test_commons_clear_of_paddies_fires_when_scrub_sits_in_a_field():
    # The check tests the DRAWN OUTCOME, not the patch's bbox CENTER (the scatter skips every paddy point by
    # construction, so a center-over-water test was only a proxy). It fires when a patch can clothe NOTHING:
    M = _nuc_village_M(_nuc_grid(), fields=[_field("p", 540, 540, 700, 700)])
    M["commons"] = [{"x": 600, "y": 600, "w": 60, "h": 60, "rot": 0, "poly": [[570, 570], [630, 570], [630, 630], [570, 630]]}]  # wholly inside the paddy -> draws nothing
    assert "commons_clear_of_paddies" in f_only(M, "commons_clear_of_paddies")
    # ...but an INTERIOR FILL - the patch that clothes the voids an irregular field leaves inside its own bbox -
    # legitimately has its CENTER on the crop while every glyph it draws lands in the open ground around it.
    # Scoring the center failed this correct patch, which is why the rule changed (GM, 2026-07: Akagahara's fan
    # void rendered as bare clay because nothing was allowed to cover it).
    fill = _nuc_village_M(_nuc_grid(), fields=[_field("p", 540, 540, 700, 700)])
    fill["commons"] = [{"x": 600, "y": 600, "w": 400, "h": 400, "rot": 0, "poly": [[400, 400], [800, 400], [800, 800], [400, 800]]}]
    assert "commons_clear_of_paddies" not in f_only(fill, "commons_clear_of_paddies")
    # a patch with no recorded polygon is skipped rather than crashing
    nopoly = _nuc_village_M(_nuc_grid(), fields=[_field("p", 540, 540, 700, 700)])
    nopoly["commons"] = [{"x": 600, "y": 600, "w": 60, "h": 60, "rot": 0}]
    assert "commons_clear_of_paddies" not in f_only(nopoly, "commons_clear_of_paddies")


def test_woodland_clear_of_crops_fires_on_overlap_and_shade_passes_when_set_back_north():
    # a managed-woodland patch must NOT overlap a crop NOR shade it from the sunny SOUTH side (trees cast
    # shadows north, maps are north-up); a patch set back to the NORTH is fine. Covers paddy + dry_plots.
    p = _field("p", 400, 400, 700, 600)
    base = {"meta": {"scale": "village"}, "fields": [p]}

    def wood(poly):
        cx = sum(v[0] for v in poly) / len(poly)
        cy = sum(v[1] for v in poly) / len(poly)
        return {"x": cx, "y": cy, "w": 100, "h": 100, "rot": 0, "role": "woodland", "poly": poly}

    over = {**base, "commons": [wood([[500, 450], [600, 450], [600, 550], [500, 550]])]}  # sits ON the paddy
    assert "woodland_clear_of_crops" in f_only(over, "woodland_clear_of_crops")
    shade = {**base, "commons": [wood([[500, 612], [640, 612], [640, 660], [500, 660]])]}  # just SOUTH -> shades it
    assert "woodland_clear_of_crops" in f_only(shade, "woodland_clear_of_crops")
    ok = {**base, "commons": [wood([[500, 300], [640, 300], [640, 344], [500, 344]])]}  # well NORTH -> clear
    assert "woodland_clear_of_crops" not in f_only(ok, "woodland_clear_of_crops")
    dry = {
        **base,
        "dry_plots": [{"poly": [[800, 400], [900, 400], [900, 500], [800, 500]], "crop": "soy", "theta": 0.0}],
        "commons": [wood([[840, 420], [940, 420], [940, 520], [840, 520]])],
    }  # overlaps a DRY plot
    assert "woodland_clear_of_crops" in f_only(dry, "woodland_clear_of_crops")


def test_woodland_clear_of_grove_fires_when_on_the_fengshui_grove():
    # a coppice woodland patch and the protected fengshui grove are DISTINCT woods - a patch sitting on a grove
    # clump fires; one on its own ground does not.
    p = _field("p", 400, 400, 700, 600)
    patch = {"x": 200, "y": 200, "w": 100, "h": 100, "rot": 0, "role": "woodland", "poly": [[150, 150], [250, 150], [250, 250], [150, 250]]}
    base = {"meta": {"scale": "village"}, "fields": [p], "commons": [patch]}
    on = {**base, "village_groves": [{"role": "windbreak", "x": 200, "y": 200, "r": 14, "clumps": [[200, 200]]}]}  # clump inside the patch
    assert "woodland_clear_of_grove" in f_only(on, "woodland_clear_of_grove")
    off = {**base, "village_groves": [{"role": "windbreak", "x": 900, "y": 900, "r": 14, "clumps": [[900, 900]]}]}  # grove far away
    assert "woodland_clear_of_grove" not in f_only(off, "woodland_clear_of_grove")


def test_farmhouse_sizes_vary_fires_when_flat():
    M = {"meta": {"scale": "village"}, "houses": [_farmhouse(300 + 60 * i, 300) for i in range(12)]}
    assert "farmhouse_sizes_vary" in f_only(M, "farmhouse_sizes_vary")  # _farmhouse has no wealth -> all at the baseline tier


def test_farmhouse_sizes_vary_passes_with_a_spread():
    houses = []
    for i in range(12):
        h = _farmhouse(300 + 60 * i, 300)
        h["wealth"] = 0.9 if i % 3 == 0 else (1.12 if i % 3 == 1 else 1.0)
        houses.append(h)
    assert "farmhouse_sizes_vary" not in f_only({"meta": {"scale": "village"}, "houses": houses}, "farmhouse_sizes_vary")


# --- labels_render_on_top (label text is never covered) ---


def test_funerary_clear_of_fields_fires_when_a_cremation_ground_sits_on_a_field():
    # GM 2026-07 (Nagahara): a cremation ground on the far-bank comb's crop + ditch
    field = [{"name": "fe1", "kind": "paddy", "outline": [[300, 300], [700, 300], [700, 700], [300, 700]], "bbox": [300, 300, 700, 700]}]
    fire = {"fields": field, "cremation_grounds": [{"x": 500, "y": 500, "w": 116, "h": 80, "rot": 0}]}
    assert "funerary_clear_of_fields" in f_only(fire, "funerary_clear_of_fields")
    ok = {"fields": field, "cremation_grounds": [{"x": 500, "y": 850, "w": 116, "h": 80, "rot": 0}]}
    assert "funerary_clear_of_fields" not in f_only(ok, "funerary_clear_of_fields")


def test_walled_graveyards_inside_and_outside_fires_when_all_inside():
    assert "walled_graveyards_inside_and_outside" in f_only(_city_dead(cems=[(300, 300), (700, 300)]), "walled_graveyards_inside_and_outside")
