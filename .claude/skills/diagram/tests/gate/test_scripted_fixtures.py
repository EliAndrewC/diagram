"""SCRIPTED NEGATIVE FIXTURES (feature 141, GM 2026-08-28): a kept check is proved to fire on what the ENGINE
draws - a cached roll with one deliberate break - instead of on a frozen manifest from the hand-placement era.

The GM: *"If the thing which fixes the wrongness of the map is an update to our placement algorithm, then I
don't think that saving off that past map actually has value ... we can have one hundred percent unit test
coverage and have a unit test which asserts that things are now correct without saving off the old map."*
Here the roll is served from the roll cache (feature 135), the break is a few lines the reader can see, and
the check is run TARGETED (feature 022's `only=`), so each case costs milliseconds at the gate."""

from __future__ import annotations

import copy
from collections.abc import Callable
from typing import Any

import pytest

from l7r.diagram import check_village
from l7r.diagram import hamletgen as hg
from l7r.diagram.pipeline import rollcache

REFERENCE = hg.HamletSpec(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond")
POLDER = hg.HamletSpec(name="Polder", seed=19, households=16, field_archetype="polder_grid", down_deg=90)


def _fires(spec: hg.HamletSpec, check: str, mutate: Callable[[dict[str, Any]], None]) -> None:
    _plan, M = rollcache.hamlet(spec)
    M = copy.deepcopy(M)
    assert check not in check_village.gate(M, verbose=False, only={check}), f"{check} must be CLEAN on the unbroken roll, or the break proves nothing"
    mutate(M)
    assert check in check_village.gate(M, verbose=False, only={check}), f"{check} did not fire on the break"


@pytest.mark.rolls_map
def test_hamlet_has_kosatsuba_fires_when_the_board_is_gone() -> None:
    _fires(REFERENCE, "hamlet_has_kosatsuba", lambda M: M.__setitem__("kosatsuba", []))


@pytest.mark.rolls_map
def test_kosatsuba_by_the_road_fires_when_the_board_stands_in_the_paddy() -> None:
    def far_from_every_way(M: dict[str, Any]) -> None:
        fx0, fy0, fx1, fy1 = M["fields"][0]["bbox"]
        M["kosatsuba"][0]["x"], M["kosatsuba"][0]["y"] = (fx0 + fx1) / 2, (fy0 + fy1) / 2  # the middle of the paddy, no way within reach

    _fires(REFERENCE, "kosatsuba_by_the_road", far_from_every_way)


@pytest.mark.rolls_map
def test_structures_clear_of_dike_fires_when_a_house_stands_on_the_dike() -> None:
    def onto_the_dike(M: dict[str, Any]) -> None:
        crest = M["dikes"][0]["crest"]
        cx, cy = crest[len(crest) // 2]
        M["houses"][0]["x"], M["houses"][0]["y"] = float(cx), float(cy)

    _fires(POLDER, "structures_clear_of_dike", onto_the_dike)


@pytest.mark.rolls_map
def test_polder_dike_gapped_at_sluices_fires_when_the_gaps_are_forgotten() -> None:
    _fires(POLDER, "polder_dike_gapped_at_sluices", lambda M: M["dikes"][0].__setitem__("gaps", []))


# ---- feature 146: a check nobody has proved fires is a check nobody has proved ------------------------------
# One deliberate, targeted break per check, on a cached roll. Each `mutate` is the smallest edit that makes the
# map wrong in exactly the way the check names - so a reader can see what the check is for, and the check's own
# failure branch is exercised (which is what the hamlet-path coverage floor was reporting, feature 146 class 2).


@pytest.mark.rolls_map
def test_households_consistent_fires_when_half_the_houses_vanish() -> None:
    _fires(REFERENCE, "households_consistent", lambda M: M.__setitem__("houses", M["houses"][: len(M["houses"]) // 3]))


@pytest.mark.rolls_map
def test_cluster_abuts_fields_fires_when_a_house_is_flung_far_from_the_field() -> None:
    def far_away(M: dict[str, Any]) -> None:
        fx0, fy0, fx1, fy1 = M["fields"][0]["bbox"]
        span = max(fx1 - fx0, fy1 - fy0)
        for h in M["houses"]:  # the whole cluster, so the check's cluster-radius term cannot absorb it
            h["x"], h["y"] = h["x"] - 4 * span, h["y"]

    _fires(REFERENCE, "cluster_abuts_fields", far_away)


@pytest.mark.rolls_map
def test_wells_among_dwellings_fires_when_a_well_stands_out_in_the_country() -> None:
    def out_in_the_open(M: dict[str, Any]) -> None:
        M["wells"][0]["x"] = M["wells"][0]["x"] + 4000.0

    _fires(REFERENCE, "wells_among_dwellings", out_in_the_open)


@pytest.mark.rolls_map
def test_ways_cross_water_on_a_deck_fires_when_a_lane_is_laid_down_the_channel() -> None:
    """Emptying `bridges` does NOT fire it on the reference - the hamlet's ways do not cross water at all, its
    footbridges plank the field channels. So the break is a lane laid ALONG a drawn channel, with no deck."""

    def down_the_channel(M: dict[str, Any]) -> None:
        # ALONG A STREAM, which is what the check actually reads (feature 150, 2026-08-29). The break used
        # `drawn_channels[0]`, and `wd_waters` is built from `streams` + `canals` + the moat - never from
        # `drawn_channels` - so it only ever fired because that one channel happened to run alongside a
        # stream. It stopped firing the moment `_clip_to_stream` began pulling a channel's endpoint back by
        # its cap radius, which is a drawing fix with nothing to say about this check. A fixture that
        # depends on an incidental adjacency is not testing the rule it names.
        pts = M["streams"][0]["poly"]
        M["lanes"].append({"pts": [list(p) for p in pts], "w": 5, "worn": True, "connector": False})
        M["bridges"] = []

    _fires(REFERENCE, "ways_cross_water_on_a_deck", down_the_channel)


@pytest.mark.rolls_map
def test_scalebar_matches_declared_scale_fires_when_the_declared_scale_changes_under_it() -> None:
    _fires(REFERENCE, "scalebar_matches_declared_scale", lambda M: M["meta"].__setitem__("ftpx", 3.0))


@pytest.mark.rolls_map
def test_lanes_bend_like_paths_fires_on_a_hairpin() -> None:
    def hairpin(M: dict[str, Any]) -> None:
        x, y = M["houses"][0]["x"], M["houses"][0]["y"]
        M["lanes"].append({"pts": [[x, y - 200], [x, y - 100], [x + 4, y - 200]], "w": 5, "worn": True, "connector": False})  # out and straight back

    _fires(REFERENCE, "lanes_bend_like_paths", hairpin)


@pytest.mark.rolls_map
def test_woodland_commons_on_dry_ground_fires_when_a_coppice_is_laid_in_the_marsh() -> None:
    def into_the_bog(M: dict[str, Any]) -> None:
        poly = [[float(a), float(b)] for a, b in M["marshes"][0]["poly"][:4]]
        cx = sum(q[0] for q in poly) / len(poly)
        cy = sum(q[1] for q in poly) / len(poly)
        M["commons"].append(
            {"x": cx, "y": cy, "w": 120.0, "h": 120.0, "rot": 0, "role": "woodland", "seq": 99, "poly": [[cx - 60, cy - 60], [cx + 60, cy - 60], [cx + 60, cy + 60], [cx - 60, cy + 60]]}
        )

    _fires(REFERENCE, "woodland_commons_on_dry_ground", into_the_bog)


@pytest.mark.rolls_map
def test_map_frame_hugs_its_content_fires_when_the_frame_is_blown_out() -> None:
    def blow_out_the_frame(M: dict[str, Any]) -> None:
        v = list(M["meta"]["view"])
        M["meta"]["view"] = [v[0] - 900, v[1] - 900, v[2] + 1800, v[3] + 1800]

    _fires(REFERENCE, "map_frame_hugs_its_content", blow_out_the_frame)


@pytest.mark.rolls_map
def test_no_structure_on_paddy_fires_when_a_farmhouse_is_dropped_in_the_basins() -> None:
    def into_the_paddy(M: dict[str, Any]) -> None:
        fx0, fy0, fx1, fy1 = M["fields"][0]["bbox"]
        M["houses"][0]["x"], M["houses"][0]["y"] = (fx0 + fx1) / 2, (fy0 + fy1) / 2

    _fires(REFERENCE, "no_structure_on_paddy", into_the_paddy)


@pytest.mark.rolls_map
def test_hamlet_has_no_headman_fires_when_a_headman_house_appears() -> None:
    _fires(REFERENCE, "hamlet_has_no_headman", lambda M: M["houses"][0].__setitem__("role", "headman"))


@pytest.mark.rolls_map
def test_farmhouses_reach_a_way_fires_when_the_lanes_are_taken_away() -> None:
    def strand_them(M: dict[str, Any]) -> None:
        M["lanes"] = [ln for ln in M["lanes"] if ln.get("connector")]

    _fires(REFERENCE, "farmhouses_reach_a_way", strand_them)


@pytest.mark.rolls_map
def test_labels_within_image_fires_when_a_caption_is_flung_off_the_sheet() -> None:
    _fires(REFERENCE, "labels_within_image", lambda M: M["labels"][0].__setitem__(0, -5000.0))


@pytest.mark.rolls_map
def test_farmhouse_sizes_vary_fires_when_every_house_is_the_same_size() -> None:
    def all_alike(M: dict[str, Any]) -> None:
        w, h = M["houses"][0]["w"], M["houses"][0]["h"]
        for house in M["houses"]:
            house["w"], house["h"] = w, h

    _fires(REFERENCE, "farmhouse_sizes_vary", all_alike)


@pytest.mark.rolls_map
def test_houses_face_south_fires_when_a_farmhouse_is_turned_around() -> None:
    _fires(REFERENCE, "houses_face_south", lambda M: [h.__setitem__("rot", 180.0) for h in M["houses"]])


@pytest.mark.rolls_map
def test_no_label_overlaps_fires_when_a_caption_is_stacked_on_another() -> None:
    def stack_them(M: dict[str, Any]) -> None:
        first = list(M["labels"][0])
        M["labels"].append(first)

    _fires(REFERENCE, "no_label_overlaps", stack_them)


@pytest.mark.rolls_map
def test_features_do_not_overlap_fires_when_a_shed_is_moved_onto_its_house() -> None:
    def onto_the_house(M: dict[str, Any]) -> None:
        h = M["houses"][0]
        M["farm_sheds"][0]["x"], M["farm_sheds"][0]["y"] = float(h["x"]), float(h["y"])

    _fires(REFERENCE, "features_do_not_overlap", onto_the_house)


@pytest.mark.rolls_map
def test_commons_clear_of_paddies_fires_when_grazing_is_recorded_over_the_field() -> None:
    def onto_the_field(M: dict[str, Any]) -> None:
        fx0, fy0, fx1, fy1 = M["fields"][0]["bbox"]
        cx, cy = (fx0 + fx1) / 2, (fy0 + fy1) / 2
        for c in M["commons"]:  # every parcel, so a check reading the WHOLE list cannot find a clean one
            dx, dy = cx - float(c["x"]), cy - float(c["y"])
            c["x"], c["y"] = cx, cy
            if c.get("poly"):
                c["poly"] = [[float(a_) + dx, float(b_) + dy] for a_, b_ in c["poly"]]

    _fires(REFERENCE, "commons_clear_of_paddies", onto_the_field)


@pytest.mark.rolls_map
def test_lanes_form_one_network_fires_when_a_lane_is_set_adrift() -> None:
    def adrift(M: dict[str, Any]) -> None:
        M["lanes"].append({"pts": [[60.0, 60.0], [220.0, 60.0]], "w": 5, "worn": True, "connector": False})  # a lane in the far corner, touching nothing

    _fires(REFERENCE, "lanes_form_one_network", adrift)


@pytest.mark.rolls_map
def test_dry_plots_clear_of_paddies_fires_when_a_dry_plot_is_laid_on_the_rice() -> None:
    def onto_the_rice(M: dict[str, Any]) -> None:
        fx0, fy0, fx1, fy1 = M["fields"][0]["bbox"]
        cx, cy = (fx0 + fx1) / 2, (fy0 + fy1) / 2
        M["dry_plots"][0]["poly"] = [[cx - 40, cy - 40], [cx + 40, cy - 40], [cx + 40, cy + 40], [cx - 40, cy + 40]]

    _fires(REFERENCE, "dry_plots_clear_of_paddies", onto_the_rice)


@pytest.mark.rolls_map
def test_groves_clear_of_lanes_fires_when_a_belt_clump_is_dropped_on_a_lane() -> None:
    def onto_the_lane(M: dict[str, Any]) -> None:
        pts = next(ln["pts"] for ln in M["lanes"] if len(ln.get("pts") or []) >= 2)
        mid = pts[len(pts) // 2]
        M["village_groves"][0]["clumps"].append([float(mid[0]), float(mid[1])])

    _fires(REFERENCE, "groves_clear_of_lanes", onto_the_lane)


@pytest.mark.rolls_map
def test_houses_clear_of_lanes_fires_when_a_lane_is_run_through_a_farmhouse() -> None:
    def through_the_house(M: dict[str, Any]) -> None:
        h = M["houses"][0]
        M["lanes"].append({"pts": [[float(h["x"]) - 120, float(h["y"])], [float(h["x"]) + 120, float(h["y"])]], "w": 5, "worn": True, "connector": False})

    _fires(REFERENCE, "houses_clear_of_lanes", through_the_house)


@pytest.mark.rolls_map
def test_lanes_reach_something_fires_on_a_lane_that_serves_nothing() -> None:
    def to_nowhere(M: dict[str, Any]) -> None:
        pts = next(ln["pts"] for ln in M["lanes"] if len(ln.get("pts") or []) >= 2)
        a = pts[0]
        M["lanes"].append({"pts": [[float(a[0]), float(a[1])], [float(a[0]) + 300.0, float(a[1]) - 300.0]], "w": 5, "worn": True, "connector": False})

    _fires(REFERENCE, "lanes_reach_something", to_nowhere)


@pytest.mark.rolls_map
def test_village_windbreak_present_fires_when_the_belt_is_taken_away() -> None:
    _fires(REFERENCE, "village_windbreak_present", lambda M: M.__setitem__("village_groves", [g for g in M["village_groves"] if g.get("role") != "windbreak"]))


@pytest.mark.rolls_map
def test_village_windbreak_embraces_cluster_fires_when_the_belt_is_carried_off() -> None:
    def carry_it_off(M: dict[str, Any]) -> None:
        belt = next(g for g in M["village_groves"] if g.get("role") == "windbreak")
        belt["clumps"] = [[float(x) + 2200.0, float(y)] for x, y in belt["clumps"]]
        belt["x"] = float(belt["x"]) + 2200.0

    _fires(REFERENCE, "village_windbreak_embraces_cluster", carry_it_off)


@pytest.mark.rolls_map
def test_village_windbreak_scales_with_cluster_fires_when_the_belt_is_cut_to_a_stub() -> None:
    def cut_to_a_stub(M: dict[str, Any]) -> None:
        belt = next(g for g in M["village_groves"] if g.get("role") == "windbreak")
        belt["clumps"] = belt["clumps"][:2]

    _fires(REFERENCE, "village_windbreak_scales_with_cluster", cut_to_a_stub)


@pytest.mark.rolls_map
def test_no_structure_on_torii_fires_when_a_shed_is_set_under_the_arch() -> None:
    def under_the_arch(M: dict[str, Any]) -> None:
        M["torii"] = [[float(M["houses"][1]["x"]), float(M["houses"][1]["y"]), 0.0]]

    _fires(REFERENCE, "no_structure_on_torii", under_the_arch)


@pytest.mark.rolls_map
def test_wells_among_dwellings_fires_when_a_wellhead_stands_in_the_paddy() -> None:
    """The other arm of the well check: not merely far from the houses, but standing in the rice."""

    def into_the_rice(M: dict[str, Any]) -> None:
        fx0, fy0, fx1, fy1 = M["fields"][0]["bbox"]
        M["wells"][0]["x"], M["wells"][0]["y"] = (fx0 + fx1) / 2, (fy0 + fy1) / 2

    _fires(REFERENCE, "wells_among_dwellings", into_the_rice)


@pytest.mark.rolls_map
def test_byres_meet_their_target_fires_when_the_byres_are_taken_away() -> None:
    _fires(REFERENCE, "byres_meet_their_target", lambda M: M.__setitem__("byres", []))


@pytest.mark.rolls_map
def test_byre_form_declared_fires_when_the_declaration_is_missing() -> None:
    """The declaration itself, not its truth: a map that draws byres must SAY which form they are, so the
    form check has something to measure against."""
    _fires(REFERENCE, "byre_form_declared", lambda M: M["meta"].pop("byre_form", None))


@pytest.mark.rolls_map
def test_title_clear_of_features_fires_when_the_placard_is_dropped_on_a_farmhouse() -> None:
    def onto_a_house(M: dict[str, Any]) -> None:
        h = M["houses"][0]
        box = [float(h["x"]) - 90, float(h["y"]) - 34, float(h["x"]) + 90, float(h["y"]) + 34]
        M["title"] = {**M["title"], "bbox": box, "placard": list(box)}

    _fires(REFERENCE, "title_clear_of_features", onto_a_house)


@pytest.mark.rolls_map
def test_title_has_placard_fires_when_the_placard_is_dropped() -> None:
    _fires(REFERENCE, "title_has_placard", lambda M: M["title"].pop("placard", None))


@pytest.mark.rolls_map
def test_structures_clear_of_dike_fires_when_a_house_corner_reaches_the_bank() -> None:
    """The polder dike's keep-out is measured at the house's CORNERS, not its centre: a house whose corner
    reaches the bank fires even when its middle is clear. (A `dike_top` house is exempt and stays so.)"""

    def corner_onto_the_bank(M: dict[str, Any]) -> None:
        keep = M["dikes"][0].get("keepout") or M["dikes"][0]["crest"]
        cx, cy = keep[len(keep) // 2]
        h = M["houses"][0]
        h["x"], h["y"] = float(cx) + float(h["w"]) / 2 - 2.0, float(cy)
        h.pop("on_dike", None)

    _fires(POLDER, "structures_clear_of_dike", corner_onto_the_bank)


@pytest.mark.rolls_map
def test_the_gate_prints_a_waiver_it_honours() -> None:
    """Feature 146: the driver's WAIVE arm. A map may break a rule IN WRITING, and a verbose run says which
    rule was excused - which is what makes a stale waiver visible later."""
    _plan, M = rollcache.hamlet(REFERENCE)
    M = copy.deepcopy(M)
    M["houses"] = M["houses"][: len(M["houses"]) // 3]
    assert "households_consistent" in check_village.gate(M, verbose=False, only={"households_consistent"})
    M["meta"]["waivers"] = {"households_consistent": "a deliberate break with a reason long enough to satisfy the minimum the gate asks of one"}
    assert "households_consistent" not in check_village.gate(M, verbose=True, only={"households_consistent"})


@pytest.mark.rolls_map
def test_pond_fill_covers_channel_mouths_fires_when_a_stream_mouth_is_left_dry() -> None:
    """A watercourse ending inside the pond's rim must meet drawn fill, or the map shows a channel stopping
    in bare ground where the water should be."""

    def strand_a_mouth(M: dict[str, Any]) -> None:
        # THE BREAK IS A LATE DRAWN COURSE, NOT A STREAM (feature 150): the one water block paints the pond
        # fill LAST, so `pond_layer` is now always `late`, and the check reads a stream's flank as never-late
        # (`_pjz.append((pt, st.get("bedz"), False))`) - `(False, bz) >= (True, _pz)` cannot hold, so no
        # stream can strand a mouth any more and the old break proved nothing. What CAN still happen is the
        # defect the check was written for: a course drawn in the late block, after the fill, leaving its bed
        # lying on top of the open water. That is what is broken here.
        pond = M["pond"]
        M.setdefault("drawn_channels", []).append({"pts": [[float(pond[0]), float(pond[1])], [float(pond[0]) + 400.0, float(pond[1])]], "w0": 7.0, "w1": 7.0, "bedz": 99999, "late": True})

    _fires(REFERENCE, "pond_fill_covers_channel_mouths", strand_a_mouth)
