"""tier city tests split out of `tests.check_village.test_segments_01_city_frame_and_yards` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram import check_village
from tests.check_village._builders import (
    _CITY_WALL,
    _CITY_WALL_SMALL,
    _FULL_Q,
    _capital_manifest,
    _diamond_city,
    _dwell_grid,
    _farrier_map,
    _fuel_map,
    _gate_parts,
    _kiln_map,
    _pop_city,
    _qcity,
    bldg,
    f,
    f_only,
    house,
    manifest,
)


@pytest.mark.tiers("city")
def test_guard_box_on_the_ward_fence_is_a_defect_though_the_gateway_on_it_is_not():
    # GM 2026-07-27: "ward gates seem to sometimes overlap with neighborhood walls". The GATEWAY
    # stands on the fence - the gate IS the opening. The guard box is a building on the verge and
    # rides no such permission, so a fence drawn through it is a defect.
    thru_gateway = {"meta": {"scale": "city"}, "kido": [_gate_parts()], "wards": [{"name": "samurai", "boundary": [[400, 300], [400, 700]]}]}
    assert not [v for v in check_village.matrix_violations(thru_gateway) if "kido_guard_box" in (v[0], v[1])]
    thru_box = {"meta": {"scale": "city"}, "kido": [_gate_parts()], "wards": [{"name": "samurai", "boundary": [[300, 520], [700, 520]]}]}
    assert [v for v in check_village.matrix_violations(thru_box) if "kido_guard_box" in (v[0], v[1])]
    assert "features_do_not_overlap" in f_only(thru_box, "features_do_not_overlap")


@pytest.mark.tiers("city")
def test_stable_troughs_beside_well_fires_when_the_cluster_is_far_from_every_well():
    # the pre-fix Nagahara defect: a trough cluster a real bucket-CARRY (>40 real ft) from every
    # well - watering is a relay at the wellhead, the bucket poured straight into the trough
    M = {
        "meta": {"scale": "city", "W": 1000, "H": 1000, "ftpx": 3},
        "stable_yards": [{"x": 500, "y": 500, "r": 72.0, "of": [500, 500], "troughs": 2, "troughs_at": [530.0, 500.0]}],
        "wells": [{"x": 700, "y": 500, "r": 8, "vr": 4.0}],  # 170 px = 510 real ft from the cluster
    }
    assert "stable_troughs_beside_well" in f_only(M, "stable_troughs_beside_well")


@pytest.mark.tiers("city")
def test_stable_troughs_beside_well_fires_when_the_cluster_went_unrecorded():
    # troughs > 0 with no troughs_at: the anchor is part of the record's contract - an
    # unrecorded cluster cannot be validated, so it fails rather than passing silently
    M = {
        "meta": {"scale": "city", "W": 1000, "H": 1000, "ftpx": 3},
        "stable_yards": [{"x": 500, "y": 500, "r": 72.0, "of": [500, 500], "troughs": 2}],
        "wells": [{"x": 505, "y": 500, "r": 8, "vr": 4.0}],
    }
    assert "stable_troughs_beside_well" in f_only(M, "stable_troughs_beside_well")


@pytest.mark.tiers("city")
def test_stable_troughs_beside_well_passes_beside_a_well_and_skips_troughless_yards():
    # a cluster hugging a wellhead (~24 real ft, the placement's own offset) passes; a yard that
    # drew no troughs (fully blocked ground) has nothing to anchor and is skipped
    M = {
        "meta": {"scale": "city", "W": 1000, "H": 1000, "ftpx": 3},
        "stable_yards": [
            {"x": 500, "y": 500, "r": 72.0, "of": [500, 500], "troughs": 2, "troughs_at": [492.1, 500.0], "troughs_box": [489.8, 497.2, 494.4, 502.8]},
            {"x": 800, "y": 800, "r": 60.0, "of": [800, 800], "troughs": 0},
        ],
        "wells": [{"x": 500, "y": 500, "r": 8, "vr": 4.0}],  # 7.9 px = 24 real ft from the cluster
    }
    fails = f(M)
    assert "stable_troughs_beside_well" not in fails
    assert "stable_troughs_clear_of_buildings" not in fails  # box clear of the roof square too


@pytest.mark.tiers("city")
def test_stable_troughs_clear_of_buildings_fires_when_a_trough_clips_a_well_roof():
    # the Tango caravan-ground defect: a 3-trough stack hugging its well on a near-vertical ray -
    # the box bottom reaches into the well-house roof square
    M = {
        "meta": {"scale": "city", "W": 1000, "H": 1000, "ftpx": 3},
        "stable_yards": [{"x": 500, "y": 500, "r": 80.0, "of": [500, 500], "troughs": 3, "troughs_at": [502.0, 492.4], "troughs_box": [499.7, 487.8, 504.3, 497.0]}],
        "wells": [{"x": 500, "y": 500, "r": 8, "vr": 4.0}],  # roof top edge at y=496 < box bottom 497
    }
    assert "stable_troughs_clear_of_buildings" in f_only(M, "stable_troughs_clear_of_buildings")


@pytest.mark.tiers("city")
def test_stable_troughs_clear_of_buildings_fires_when_a_trough_clips_a_building():
    # the cluster is a bucket-pour from its well, but the drawn rects land on a building footprint
    M = {
        "meta": {"scale": "city", "W": 1000, "H": 1000, "ftpx": 3},
        "stable_yards": [{"x": 500, "y": 500, "r": 72.0, "of": [500, 500], "troughs": 2, "troughs_at": [502.0, 492.4], "troughs_box": [499.7, 489.6, 504.3, 495.2]}],
        "wells": [{"x": 510, "y": 492, "r": 8, "vr": 4.0}],  # beside_well is satisfied
        "buildings": [{"x": 500, "y": 486, "w": 20, "h": 8}],  # footprint bottom at y=490 > box top 489.6
    }
    assert "stable_troughs_clear_of_buildings" in f_only(M, "stable_troughs_clear_of_buildings")


@pytest.mark.tiers("city")
def test_stable_troughs_clear_of_buildings_fires_when_the_box_went_unrecorded():
    # troughs > 0 with no troughs_box: the drawn extent is part of the record's contract
    M = {
        "meta": {"scale": "city", "W": 1000, "H": 1000, "ftpx": 3},
        "stable_yards": [{"x": 500, "y": 500, "r": 72.0, "of": [500, 500], "troughs": 2, "troughs_at": [492.1, 500.0]}],
        "wells": [{"x": 500, "y": 500, "r": 8, "vr": 4.0}],
    }
    assert "stable_troughs_clear_of_buildings" in f_only(M, "stable_troughs_clear_of_buildings")


@pytest.mark.tiers("city")
def test_stable_yard_furniture_fires_when_a_rail_tip_reaches_the_road():
    # the center-only placement bug (GM 2026-07-24): rail center 12px off the road centerline
    # clears the ~4.3px tread, but the 18px rail's tip (len/2 + 2.4 post reach = 11.4) lands on it
    M = {
        "meta": {"scale": "city", "W": 1000, "H": 1000, "ftpx": 3},
        "road": [[500, 0], [500, 1000]],
        "road_width": 8.667,
        "stable_yards": [
            {
                "x": 560,
                "y": 500,
                "r": 72.0,
                "of": [560, 500],
                "troughs": 0,
                "rails": [{"x": 512, "y": 500, "tx": 1.0, "ty": 0.0, "len": 18.0, "reach": 2.4}],
                "dung_heaps": [],
            }
        ],
    }
    assert "stable_yard_furniture_clear_of_roads_walls" in f_only(M, "stable_yard_furniture_clear_of_roads_walls")


@pytest.mark.tiers("city")
def test_stable_yard_furniture_fires_when_a_dung_heap_lies_against_the_wall():
    # a heap whose drawn edge (rx 2.5) reaches inside the rampart's ~5px clearance stroke
    M = {
        "meta": {"scale": "city", "W": 1000, "H": 1000, "ftpx": 3},
        "wall": [[100, 100], [900, 100], [900, 900], [100, 900]],
        "stable_yards": [
            {
                "x": 500,
                "y": 160,
                "r": 72.0,
                "of": [500, 160],
                "troughs": 0,
                "rails": [],
                "dung_heaps": [{"x": 500, "y": 106, "rx": 2.5, "ry": 1.8}],
            }
        ],
    }
    assert "stable_yard_furniture_clear_of_roads_walls" in f_only(M, "stable_yard_furniture_clear_of_roads_walls")


@pytest.mark.tiers("city")
def test_stable_yard_furniture_passes_clear_and_skips_unrecorded_legacy_yards():
    # a rail 30px off the road and a heap in open ground pass; a legacy yard record with no
    # rails/dung_heaps keys (the pre-2026-07-24 pinned fixtures) is skipped, never retro-failed
    M = {
        "meta": {"scale": "city", "W": 1000, "H": 1000, "ftpx": 3},
        "road": [[500, 0], [500, 1000]],
        "road_width": 8.667,
        "stable_yards": [
            {
                "x": 560,
                "y": 500,
                "r": 72.0,
                "of": [560, 500],
                "troughs": 0,
                "rails": [{"x": 530, "y": 500, "tx": 0.0, "ty": 1.0, "len": 18.0, "reach": 2.4}],
                "dung_heaps": [{"x": 585, "y": 520, "rx": 2.5, "ry": 1.8}],
            },
            {"x": 300, "y": 300, "r": 60.0, "of": [300, 300], "troughs": 0},
        ],
    }
    assert "stable_yard_furniture_clear_of_roads_walls" not in f_only(M, "stable_yard_furniture_clear_of_roads_walls")


@pytest.mark.tiers("city")
def test_dung_heaps_clear_of_hitch_rails_fires_across_yards_within_24px():
    # round 2 (GM 2026-07-25): the heap sits 20px from a NEIGHBORING yard's rail - inside the
    # 24px floor, yet round 1's same-yard-only pairing (and its 14px floor) passed exactly this
    # shape (the real Nagahara round-2 capture: 16.4px same-yard, 22.5px cross-yard)
    M = {
        "meta": {"scale": "city", "W": 1000, "H": 1000, "ftpx": 3},
        "stable_yards": [
            {
                "x": 400,
                "y": 500,
                "r": 72.0,
                "of": [400, 500],
                "troughs": 0,
                "rails": [],
                "dung_heaps": [{"x": 480, "y": 500, "rx": 2.5, "ry": 1.8}],
            },
            {
                "x": 560,
                "y": 500,
                "r": 72.0,
                "of": [560, 500],
                "troughs": 0,
                "rails": [{"x": 500, "y": 500, "tx": 0.0, "ty": 1.0, "len": 18.0, "reach": 2.4}],
                "dung_heaps": [],
            },
        ],
    }
    assert "dung_heaps_clear_of_hitch_rails" in f_only(M, "dung_heaps_clear_of_hitch_rails")


@pytest.mark.tiers("city")
def test_dung_heaps_clear_of_hitch_rails_passes_at_24px_or_more():
    # the muck pile belongs NEAR the yard's working edge - 30px off the rail line is fine
    M = {
        "meta": {"scale": "city", "W": 1000, "H": 1000, "ftpx": 3},
        "stable_yards": [
            {
                "x": 500,
                "y": 500,
                "r": 72.0,
                "of": [500, 500],
                "troughs": 0,
                "rails": [{"x": 500, "y": 500, "tx": 0.0, "ty": 1.0, "len": 18.0, "reach": 2.4}],
                "dung_heaps": [{"x": 530, "y": 500, "rx": 2.5, "ry": 1.8}],
            }
        ],
    }
    assert "dung_heaps_clear_of_hitch_rails" not in f_only(M, "dung_heaps_clear_of_hitch_rails")


@pytest.mark.tiers("city")
def test_city_has_farrier_fires_on_a_city_with_no_shoeing_forge():
    # a provincial city's gate caravan yard concentrates enough horses to keep a dedicated forge
    M = _farrier_map(320, 200, scale="city", walled=True)
    M["farriers"] = []
    M["wall"] = [[100, 100], [900, 100], [900, 900], [100, 900]]
    M["gates"] = [[500, 100]]
    assert "city_has_farrier" in f_only(M, "city_has_farrier")


@pytest.mark.tiers("city")
def test_city_capacity_too_small_when_wall_cannot_hold_target():
    # a 400px diamond holds ~200 well-packed; declaring 3000 (target 600) is far too small.
    rep = check_village.city_capacity(_diamond_city(3000))
    assert rep["verdict"] == "enlarge"
    assert rep["suggested_wall_scale"] > 1  # enlarge
    # and the gate check surfaces it
    assert "city_wall_sized_to_population" in f_only(_diamond_city(3000), "city_wall_sized_to_population")


@pytest.mark.tiers("city")
def test_city_capacity_too_big_when_wall_dwarfs_target():
    rep = check_village.city_capacity(_diamond_city(100))  # target 20, inherent ~200
    assert rep["verdict"] == "shrink"
    assert rep["suggested_wall_scale"] < 1  # shrink
    assert "city_wall_sized_to_population" in f_only(_diamond_city(100), "city_wall_sized_to_population")


@pytest.mark.tiers("city")
def test_city_capacity_underpacked_when_wall_right_but_placement_sparse():
    # target 100 (pop 500) sits inside the inherent band (~118 at RHO 1.49/1000), but only 10
    # dwellings placed -> the WALL is fine, the PLACEMENT is sparse (below the 7% population
    # line). Not a resize.
    rep = check_village.city_capacity(_diamond_city(500, dwellings=10))
    assert rep["verdict"] == "densify"
    # underpacked is NOT a wall-size fault, so the gate check stays silent
    assert "city_wall_sized_to_population" not in f_only(_diamond_city(500, dwellings=10), "city_wall_sized_to_population")


@pytest.mark.tiers("city")
def test_city_capacity_about_right_when_sized_and_packed():
    rep = check_village.city_capacity(_diamond_city(500, dwellings=95))
    assert rep["verdict"] == "sized_and_packed"
    assert "city_wall_sized_to_population" not in f_only(_diamond_city(500, dwellings=95), "city_wall_sized_to_population")


@pytest.mark.tiers("city")
def test_city_commoner_dwellings_inside_walls_fires_on_a_spilled_commoner():
    inside = [bldg(300 + (i % 10) * 20, 300, "laborer") for i in range(20)]
    assert "city_commoner_dwellings_inside_walls" not in f_only(_pop_city(inside), "city_commoner_dwellings_inside_walls")
    # one laborer outside the wall -> fires (hard zero)
    leaky = inside + [bldg(50, 500, "laborer")]
    assert "city_commoner_dwellings_inside_walls" in f_only(_pop_city(leaky), "city_commoner_dwellings_inside_walls")


@pytest.mark.tiers("city")
def test_city_commoner_dwellings_exempts_samurai_and_shops_outside():
    # samurai country estate + a gate-market shop OUTSIDE the wall are legitimate; not flagged.
    inside = [bldg(300 + (i % 10) * 20, 300, "laborer") for i in range(20)]
    exempt_outside = inside + [bldg(50, 300, "samurai"), bldg(50, 400, "samurai_large"), bldg(900, 500, "shop")]
    assert "city_commoner_dwellings_inside_walls" not in f_only(_pop_city(exempt_outside), "city_commoner_dwellings_inside_walls")


@pytest.mark.tiers("city")
def test_city_quarters_declared_fires_when_absent_passes_when_present():
    assert "city_quarters_declared" in f_only({"meta": {"scale": "city"}, "wall": _CITY_WALL_SMALL, "buildings": []}, "city_quarters_declared")
    ok = _qcity([{"poly": _FULL_Q, "zone": "residential", "kind": None, "name": "q"}])
    assert "city_quarters_declared" not in f_only(ok, "city_quarters_declared")


@pytest.mark.tiers("city")
def test_city_quarters_tile_interior_passes_on_a_clean_two_half_tiling():
    left = {"poly": [[200, 200], [500, 200], [500, 800], [200, 800]], "zone": "residential", "kind": None, "name": "L"}
    right = {"poly": [[500, 200], [800, 200], [800, 800], [500, 800]], "zone": "residential", "kind": None, "name": "R"}
    # both packed enough to pass density, so we isolate the tiling result
    b = _dwell_grid(230, 470, 230, 770, 12) + _dwell_grid(530, 770, 230, 770, 12)
    assert "city_quarters_tile_interior" not in f_only(_qcity([left, right], b), "city_quarters_tile_interior")


@pytest.mark.tiers("city")
def test_city_quarters_tile_interior_fires_on_gap_overlap_and_spill():
    half = {"poly": [[200, 200], [500, 200], [500, 800], [200, 800]], "zone": "civic", "kind": None, "name": "half"}
    assert "city_quarters_tile_interior" in f_only(_qcity([half]), "city_quarters_tile_interior")  # only half covered -> gap
    dup = {"poly": _FULL_Q, "zone": "civic", "kind": None, "name": "a"}
    dup2 = {"poly": _FULL_Q, "zone": "civic", "kind": None, "name": "b"}
    assert "city_quarters_tile_interior" in f_only(_qcity([dup, dup2]), "city_quarters_tile_interior")  # doubled -> overlap
    spill = {"poly": [[50, 200], [800, 200], [800, 800], [50, 800]], "zone": "civic", "kind": None, "name": "s"}
    assert "city_quarters_tile_interior" in f_only(_qcity([spill]), "city_quarters_tile_interior")  # extends past the wall


@pytest.mark.tiers("city")
def test_city_residential_density_passes_in_band():
    q = {"poly": _FULL_Q, "zone": "residential", "kind": None, "name": "warren"}
    b = _dwell_grid(210, 790, 210, 790, 17)  # 289 dwellings evenly spread -> in band, no dead zone
    assert "city_residential_quarters_dense_enough" not in f_only(_qcity([q], b), "city_residential_quarters_dense_enough")


@pytest.mark.tiers("city")
def test_city_residential_density_fires_below_floor_and_above_ceil():
    q = {"poly": _FULL_Q, "zone": "residential", "kind": None, "name": "warren"}
    sparse = _dwell_grid(210, 790, 210, 790, 6)  # 36 dwellings -> below floor
    assert "city_residential_quarters_dense_enough" in f_only(_qcity([q], sparse), "city_residential_quarters_dense_enough")
    crammed = _dwell_grid(210, 790, 210, 790, 30)  # 900 dwellings -> above ceil
    assert "city_residential_quarters_dense_enough" in f_only(_qcity([q], crammed), "city_residential_quarters_dense_enough")


@pytest.mark.tiers("city")
def test_city_residential_density_fires_on_a_dead_zone_despite_a_good_average():
    # in-band average, but every dwelling is jammed into one corner - the far half is a dead zone.
    q = {"poly": _FULL_Q, "zone": "residential", "kind": None, "name": "lopsided"}
    corner = _dwell_grid(210, 400, 210, 400, 16)  # ~256 dwellings, density over the whole quarter in band
    assert "city_residential_quarters_dense_enough" in f_only(_qcity([q], corner), "city_residential_quarters_dense_enough")


@pytest.mark.tiers("city")
def test_city_civic_quarter_passes_with_a_compound_fires_when_bare():
    civic = {"poly": _FULL_Q, "zone": "civic", "kind": None, "name": "yamen precinct"}
    with_compound = _qcity([civic], governor_mansion={"x": 500, "y": 500, "w": 400, "h": 300, "rot": 0})
    assert "city_civic_quarter_not_mostly_open" not in f_only(with_compound, "city_civic_quarter_not_mostly_open")
    bare = _qcity([civic], ministries=[{"x": 500, "y": 500, "w": 130, "h": 90, "rot": 0}])  # tiny building in a big quarter
    assert "city_civic_quarter_not_mostly_open" in f_only(bare, "city_civic_quarter_not_mostly_open")


@pytest.mark.tiers("city")
def test_city_reserve_within_cap_passes_under_and_fires_over():
    small = {"poly": [[250, 250], [500, 250], [500, 500], [250, 500]], "zone": "reserve", "kind": "drill_ground", "name": "drill"}
    assert "city_reserve_within_cap" not in f_only(_qcity([small]), "city_reserve_within_cap")  # 62500/360000 = 17% <= 20%
    big = {"poly": [[250, 250], [550, 250], [550, 550], [250, 550]], "zone": "reserve", "kind": "drill_ground", "name": "drill"}
    assert "city_reserve_within_cap" in f_only(_qcity([big]), "city_reserve_within_cap")  # 90000/360000 = 25% > 20%


@pytest.mark.tiers("city")
def test_city_capacity_shrinks_when_reserve_over_cap():
    # a city whose empty ground is declared reserve beyond the cap reads SHRINK, never sized_and_packed
    over = {"poly": [[250, 250], [560, 250], [560, 560], [250, 560]], "zone": "reserve", "kind": "drill_ground", "name": "drill"}
    b = _dwell_grid(210, 790, 210, 790, 17)
    M = _pop_city(b, population=400, quarters=[over])
    rep = check_village.city_capacity(M)
    assert rep["verdict"] == "shrink"  # reserve_frac over the 20% cap forces shrink
    assert rep["reserve_frac"] > check_village.RESERVE_CAP_FRAC
    # and the gate check surfaces it
    assert "city_wall_sized_to_population" in f_only(M, "city_wall_sized_to_population")


@pytest.mark.tiers("city")
def test_quarter_checks_skip_a_degenerate_zero_area_quarter():
    # collinear (zero-area) quarters are skipped by the residential-density and civic-open loops
    # rather than dividing by zero.
    good = {"poly": _FULL_Q, "zone": "residential", "kind": None, "name": "warren"}
    degen_res = {"poly": [[400, 400], [500, 400], [600, 400]], "zone": "residential", "kind": None, "name": "res-sliver"}
    degen_civ = {"poly": [[400, 500], [500, 500], [600, 500]], "zone": "civic", "kind": None, "name": "civ-sliver"}
    b = _dwell_grid(210, 790, 210, 790, 17)
    M = _pop_city(b, population=400, quarters=[good, degen_res, degen_civ])
    fails = f(M)
    assert "city_residential_quarters_dense_enough" not in fails  # good quarter passes; degenerate skipped
    assert "city_civic_quarter_not_mostly_open" not in fails  # zero-area civic quarter skipped, no crash
    check_village.city_capacity(M)  # does not crash on a degenerate quarter


@pytest.mark.tiers("city")
def test_city_geometry_within_canvas_fires_on_a_stray_vertex():
    good = _qcity([{"poly": _FULL_Q, "zone": "residential", "kind": None, "name": "q"}], meta={"scale": "city", "W": 3200, "H": 2700})
    assert "city_geometry_within_canvas" not in f_only(good, "city_geometry_within_canvas")
    bad = {
        "meta": {"scale": "city", "W": 3200, "H": 2700},
        "wall": _CITY_WALL_SMALL + [[9_000_000, 9_000_000]],
        "quarters": [{"poly": _FULL_Q, "zone": "residential", "kind": None, "name": "q"}],
        "buildings": [],
    }
    assert "city_geometry_within_canvas" in f_only(bad, "city_geometry_within_canvas")  # a vertex millions of px off is flagged


@pytest.mark.tiers("city")
def test_gate_does_not_hang_on_a_runaway_quarter_vertex():
    # the sweeps must terminate on garbage geometry (the whole point of sweep_hi) - if this test
    # runs to completion at all, the sweep did not loop forever.
    M = {
        "meta": {"scale": "city", "walled": True, "population": 3000, "W": 3200, "H": 2700},
        "wall": _CITY_WALL,
        "buildings": [bldg(300 + (i % 10) * 20, 300, "laborer") for i in range(20)],
        "quarters": [{"poly": [[200, 200], [9_000_000, 200], [9_000_000, 9_000_000], [200, 9_000_000]], "zone": "residential", "kind": None, "name": "runaway"}],
    }
    fails = f(M)
    assert "city_geometry_within_canvas" in fails


@pytest.mark.tiers("city")
def test_charcoal_yard_keeps_fire_gap_measures_in_REAL_feet_not_pixels():
    """The threshold converts through meta.ftpx, so 30 ft means the same distance at every tier -
    a pixel constant would silently become 90 ft on a 3 ft/px city sheet."""
    M = _fuel_map(houses=[house(500, 500 + 29 + 14 + 20)])
    M["meta"]["ftpx"] = 3  # the same PIXEL gap is now 60 real ft, which clears
    assert "charcoal_yard_keeps_fire_gap" not in f_only(M, "charcoal_yard_keeps_fire_gap")


@pytest.mark.tiers("city")
def test_kiln_keeps_fire_gap_measures_in_REAL_feet_not_pixels():
    """The threshold converts through meta.ftpx, so 60 ft means the same distance at every tier
    rather than silently becoming 180 ft on a 3 ft/px city sheet."""
    M = _kiln_map(quarters=((500.0, 470 + 8 + 20 + 9),), ftpx=3)  # the same PIXEL gap is now 60 real ft
    assert "kiln_keeps_fire_gap" not in f_only(M, "kiln_keeps_fire_gap")


@pytest.mark.tiers("capital")
def test_population_consistency_runs_at_capital_and_counts_terrace_units():
    """T006: the housing battery binds the capital too - and a terrace range houses `units`
    households under its one roof, so units count as dwellings toward the declared figure."""
    M = _capital_manifest()
    M["meta"]["population"] = 100
    assert "population_consistent_with_housing" in f_only(M, "population_consistent_with_housing")  # zero dwellings vs 100 declared
    M["terraces"] = [
        {"x": 300, "y": 300, "w": 108, "h": 7, "rot": 0, "units": 10, "z": 1},
        {"x": 600, "y": 300, "w": 108, "h": 7, "rot": 0, "units": 10, "z": 1},
    ]
    M["districts"] = [{"name": "castle foot", "kind": "terrace", "rank_band": "terrace", "poly": [[0, 0], [1000, 0], [1000, 1000], [0, 1000]]}]
    assert "population_consistent_with_housing" not in f_only(M, "population_consistent_with_housing")  # 20 units x 5 = 100


@pytest.mark.tiers("capital", "city")
def test_capital_population_counts_yashiki_manors_and_outwall_samurai():
    """T006 arithmetic: the capital's declared figure covers the WHOLE cohort - yashiki-band
    households are manors (not buildings), and the out-wall 15% of the samurai cohort
    (CAPITAL_SAMURAI_INWALL_FRAC) are the capital's people too, unlike a provincial city's
    estate samurai (the Tango rule counts those rural)."""
    M = _capital_manifest()
    M["meta"]["population"] = 30
    M["districts"] = [{"name": "castle foot", "kind": "yashiki", "rank_band": "yashiki", "poly": [[0, 0], [1000, 0], [1000, 1000], [0, 1000]]}]
    M["manors"] = [{"x": 300, "y": 300, "w": 60, "h": 40, "label": "Hazama Estate"}, {"x": 500, "y": 300, "w": 60, "h": 40, "label": "Utsuro Estate"}]
    M["buildings"] = [
        {"x": 700, "y": 700, "w": 15, "h": 10, "kind": "samurai", "rot": 0},
        {"x": 1500, "y": 500, "w": 15, "h": 10, "kind": "samurai", "rot": 0},
        {"x": 720, "y": 740, "w": 12, "h": 9, "kind": "laborer", "rot": 0},
        {"x": 1500, "y": 900, "w": 12, "h": 9, "kind": "laborer", "rot": 0},
    ]
    M["terraces"] = [{"x": 400, "y": 700, "w": 36, "h": 7, "rot": 0, "units": 2, "z": 1}]
    # the capital census counts the WHOLE cohort, suburbs included: 2 manors + 2 samurai +
    # 2 laborers + 2 terrace units = 8 dwellings = 40 people (WHERE the out-wall pair may
    # stand is city_commoner_dwellings_inside_walls' business, not the census's):
    assert "population_consistent_with_housing" in f_only(M, "population_consistent_with_housing")  # declared 30 - off by two houses
    M["meta"]["population"] = 40  # ...and 40 closes the arithmetic exactly
    assert "population_consistent_with_housing" not in f_only(M, "population_consistent_with_housing")


@pytest.mark.tiers("capital", "city")
def test_capital_civic_quarter_tolerates_ceremonial_breadth():
    """Research 021: the Corridor of a Thousand Steps is a vast open axis flanked by office
    files - a capital's civic band legitimately runs to 90% open where a provincial yamen
    precinct keeps 70%. Same manifest, city fires, capital does not."""
    base = {
        "wall": [[0, 0], [1000, 0], [1000, 1000], [0, 1000]],
        "quarters": [
            {"poly": [[100, 100], [400, 100], [400, 500], [100, 500]], "zone": "civic", "name": "civic quarter"},
            {"poly": [[400, 100], [900, 100], [900, 900], [100, 900], [100, 500], [400, 500]], "zone": "mixed"},
        ],
        "ministries": [{"x": 250, "y": 300, "w": 100, "h": 170, "name": "Ministry of Rites"}],  # ~14% built - clear of the capital tolerance, inside the city one
    }
    Mc = _capital_manifest()
    Mc.update({k: v for k, v in base.items()})
    assert "city_civic_quarter_not_mostly_open" not in f_only(Mc, "city_civic_quarter_not_mostly_open")
    Mp = _capital_manifest(scale="city")
    Mp.update({k: v for k, v in base.items()})
    assert "city_civic_quarter_not_mostly_open" in f_only(Mp, "city_civic_quarter_not_mostly_open")


@pytest.mark.tiers("city")
def test_commoner_dwellings_at_the_wharf_suburb_are_exempt():
    """021, the kashi form: a bank-quay city keeps its landing OUTSIDE the wall and the
    brokers/warehouse folk live at it - a commoner dwelling within ~300px of the wharf works
    (jetty, dock, quay granaries) is the wharf suburb, not a defect. Beyond that reach the
    hard-zero rule stands."""
    M = _capital_manifest()
    M["buildings"] = [{"x": 1500, "y": 500, "w": 12, "h": 9, "kind": "merchant", "rot": 0}]
    assert "city_commoner_dwellings_inside_walls" in f_only(M, "city_commoner_dwellings_inside_walls")  # extramural, no wharf near
    M["jetties"] = [{"x": 1520, "y": 560, "rot": 0, "len": 13, "z": 1}]
    assert "city_commoner_dwellings_inside_walls" not in f_only(M, "city_commoner_dwellings_inside_walls")  # the same house IS the quay suburb


@pytest.mark.tiers("capital")
def test_placement_runs_meet_their_ask_fires_on_a_run_that_landed_short():
    """A placer that drops most of what it was asked for is authored-vs-landed drift, and the
    record _shortfall writes is only worth writing if something reads it back (the capital drew
    129 of 283 requested frontage seats behind a green gate)."""
    M = manifest()
    M["shortfalls"] = [{"by": "frontage", "at": [10, 10, 200, 10], "placed": 3, "wanted": 20, "dropped": "shop x17"}]
    assert "placement_runs_meet_their_ask" in check_village.gate(M, verbose=False)
