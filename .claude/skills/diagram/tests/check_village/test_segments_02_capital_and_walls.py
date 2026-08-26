"""Split from test_checks.py by feature 025 - see tests/check_village/CLAUDE.md for the index."""

from tests.check_village._builders import (
    _agri_city,
    _fort_city,
    _mest_city,
    _ring_towers,
    _scaled_city,
    bldg,
    f,
    f_only,
)


def test_city_interior_fields_farmhouse_density_fires_when_under_farmed():
    # a real in-wall field with a single token farmhouse beside it - far below village density
    M = _agri_city([{"x": 360, "y": 320, "w": 18, "h": 12, "rot": 0}])
    assert "city_interior_fields_farmhouse_density" in f_only(M, "city_interior_fields_farmhouse_density")


def test_wall_towers_evenly_spaced_fires_on_a_doubled_tower():
    # a remediation-style tower squeezed 40px from its 100px-rhythm neighbor (the Tango east-curtain artifact)
    tw = _ring_towers(100) + [{"x": 240, "y": 200}]
    assert "wall_towers_evenly_spaced" in f_only(_fort_city(wall_towers=tw), "wall_towers_evenly_spaced")


def test_wall_towers_evenly_spaced_passes_on_an_even_ring():
    assert "wall_towers_evenly_spaced" not in f_only(_fort_city(wall_towers=_ring_towers(100)), "wall_towers_evenly_spaced")


def test_outside_fields_farmhouse_density_fires_on_a_bare_shown_field():
    # a field showing a long on-map edge (fully inside the canvas) but with NO farmhouses beside it:
    # a worked field carries farmhouses at ~village density on its shown portion. This is the partial-
    # field gap - the old per-field ">=2 anywhere" let an on-map field edge sit bare.
    field = {"name": "f1", "kind": "paddy", "bbox": [300, 300, 700, 700], "outline": [[300, 300], [700, 300], [700, 700], [300, 700]]}
    M = {"meta": {"scale": "town", "W": 1000, "H": 1000}, "fields": [field], "houses": []}
    assert "outside_fields_farmhouse_density" in f_only(M, "outside_fields_farmhouse_density")


def test_city_house_doors_scope_excludes_villages_and_farmhouses():
    # villages/farmhouses keep the south-facing sunlight canon - out of scope entirely
    top = [bldg(300 + i * 41, 300, "laborer", w=40, h=24) for i in range(3)]
    bot = [bldg(300 + i * 41, 300 + 24 + 1.5, "laborer", w=40, h=24) for i in range(3)]
    assert "city_house_doors_unblocked" not in f_only({"meta": {"scale": "village"}, "buildings": top + bot}, "city_house_doors_unblocked")


def test_merchant_estate_wall_fires_on_a_dock_overlap():
    # dock basin footprint under the estate's east wall (the shipped-Nagahara defect)
    assert "merchant_estate_wall_clear_of_water" in f_only(_mest_city(docks=[{"x": 540, "y": 490, "w": 54, "h": 34, "rot": 0}]), "merchant_estate_wall_clear_of_water")


def test_merchant_estate_wall_fires_on_a_canal_crossing():
    # canal centerline passes through the north wall
    assert "merchant_estate_wall_clear_of_water" in f_only(_mest_city(canals=[{"poly": [[400, 477], [600, 477]], "w": 12.0}]), "merchant_estate_wall_clear_of_water")


def test_merchant_estate_wall_fires_on_a_pond_and_a_moat():
    assert "merchant_estate_wall_clear_of_water" in f_only(_mest_city(pond=[469, 500, 20, 14]), "merchant_estate_wall_clear_of_water")  # pond ellipse reaching the west wall
    assert "merchant_estate_wall_clear_of_water" in f_only(_mest_city(moat=[[531, 400], [531, 600]], moat_width=22.0), "merchant_estate_wall_clear_of_water")  # moat band over the east wall


def test_merchant_estate_wall_passes_with_water_at_a_distance():
    clear = _mest_city(
        docks=[{"x": 620, "y": 490, "w": 54, "h": 34, "rot": 0}],
        canals=[{"poly": [[400, 440], [600, 440]], "w": 12.0}],
        pond=[420, 500, 20, 14],
    )
    assert "merchant_estate_wall_clear_of_water" not in f_only(clear, "merchant_estate_wall_clear_of_water")


def test_merchant_estate_wall_fires_on_a_fire_tower_and_passes_when_clear():
    # tower footprint straddling the south wall (the shipped-Nagahara defect)
    on_wall = _mest_city(fire_towers=[{"x": 490, "y": 523, "w": 8.7, "h": 8.7, "rot": 0}])
    assert "merchant_estate_wall_clear_of_fire_towers" in f_only(on_wall, "merchant_estate_wall_clear_of_fire_towers")
    clear = _mest_city(fire_towers=[{"x": 490, "y": 545, "w": 8.7, "h": 8.7, "rot": 0}])
    assert "merchant_estate_wall_clear_of_fire_towers" not in f_only(clear, "merchant_estate_wall_clear_of_fire_towers")


def test_merchant_estate_fires_when_a_fire_tower_is_enclosed_in_the_court():
    # wall-line clear but the municipal tower trapped INSIDE the private court - same siting error
    inside = _mest_city(fire_towers=[{"x": 500, "y": 505, "w": 8.7, "h": 8.7, "rot": 0}])
    assert "merchant_estate_wall_clear_of_fire_towers" in f_only(inside, "merchant_estate_wall_clear_of_fire_towers")


def test_compound_gates_to_scale_fires_on_a_wall_wide_opening():
    # a 204 real-ft gate opening (the old fixed +-34px at 3 ft/px) - most of the wall missing
    m = {"x": 500, "y": 500, "w": 90, "h": 60, "rot": 0, "label": "", "gate_dir": "south", "gate": [500, 530], "gate_w": 68.0, "wall_w": 6.0}
    assert "compound_gates_to_scale" in f_only(_scaled_city(manors=[m]), "compound_gates_to_scale")


def test_compound_gates_to_scale_fires_when_gate_size_unrecorded():
    # a pre-doctrine manifest (no gate_w) cannot prove its gates - regenerate with the engine that records them
    m = {"x": 500, "y": 500, "w": 90, "h": 60, "rot": 0, "label": "", "gate_dir": "south", "gate": [500, 530]}
    assert "compound_gates_to_scale" in f_only(_scaled_city(manors=[m]), "compound_gates_to_scale")


def test_compound_gates_to_scale_passes_a_real_gate():
    # a 12 real-ft opening (4px at 3 ft/px) in a 2 ft wall drawn at the 2px legibility floor
    m = {"x": 500, "y": 500, "w": 90, "h": 60, "rot": 0, "label": "", "gate_dir": "south", "gate": [500, 530], "gate_w": 4.0, "wall_w": 2.0}
    gov = {"x": 800, "y": 500, "w": 150, "h": 100, "rot": 0, "gate_dir": "west", "gate": [725, 500], "gate_w": 6.0, "wall_w": 2.0}
    assert "compound_gates_to_scale" not in f_only(_scaled_city(manors=[m], governor_mansion=gov), "compound_gates_to_scale")


def test_burial_grounds_sized_to_population_fires_on_an_oversized_village_ground():
    # an ~800-person district drawing 0.64 acre (200x140 ft) - ~2x the 0.15-0.30 acre district band, larger than a town's
    M = {"meta": {"scale": "village", "ftpx": 2}, "cemeteries": [{"x": 500, "y": 500, "w": 100, "h": 70, "rot": 0}]}
    assert "burial_grounds_sized_to_population" in f_only(M, "burial_grounds_sized_to_population")
    # a 120x88 ft district ground (60x44px at 2 ft/px) = ~0.24 acre - in band
    ok = {"meta": {"scale": "village", "ftpx": 2}, "cemeteries": [{"x": 500, "y": 500, "w": 60, "h": 44, "rot": 0}]}
    assert "burial_grounds_sized_to_population" not in f_only(ok, "burial_grounds_sized_to_population")


def test_burial_grounds_sized_to_population_fires_on_a_village_only_undersized_ground():
    # 60x40 ft (30x20px) = ~0.055 acre - sized as if the central village's ~350 buried alone; the ground
    # serves the whole ~800-person district (hamlets carry their urns here), so the 0.12 floor flags it
    M = {"meta": {"scale": "village", "ftpx": 2}, "cemeteries": [{"x": 500, "y": 500, "w": 30, "h": 20, "rot": 0}]}
    assert "burial_grounds_sized_to_population" in f_only(M, "burial_grounds_sized_to_population")


def test_compound_gates_to_scale_fires_on_gate_fraction_and_wall_thickness():
    # an in-band 21 ft opening that still swallows over 40% of a tiny compound's wall side
    frac = {"x": 500, "y": 500, "w": 15, "h": 10, "rot": 0, "label": "", "gate_dir": "south", "gate": [500, 505], "gate_w": 7.0, "wall_w": 0.7}
    assert "compound_gates_to_scale" in f_only(_scaled_city(manors=[frac]), "compound_gates_to_scale")
    # a good gate in a 15 ft rampart-thick wall - a residence wall is ~2 ft, not fortress masonry
    thick = {"x": 500, "y": 500, "w": 90, "h": 60, "rot": 0, "label": "", "gate_dir": "south", "gate": [500, 530], "gate_w": 4.0, "wall_w": 5.0}
    assert "compound_gates_to_scale" in f_only(_scaled_city(manors=[thick]), "compound_gates_to_scale")


def test_paddy_fan_gapless_credits_ditches_and_fires_on_holes():
    """The white-spots gate: a bare strip inside the fan fires; the SAME gap over a recorded
    field ditch is covered ground (drawn water), and must not - that credit is what lets the
    plot tolerance sit at bund scale (6 real ft) without flagging delivery-ditch strips."""
    outline = [[0, 0], [400, 0], [400, 400], [0, 400]]
    plots = [[[0, 0], [180, 0], [180, 400], [0, 400]], [[220, 0], [400, 0], [400, 400], [220, 400]]]
    base = {"meta": {"scale": "village", "ftpx": 2}, "fields": [{"name": "t", "kind": "paddy", "outline": outline, "bbox": [0, 0, 400, 400], "plot_polys": plots}]}
    assert "paddy_fan_gapless" in f_only(base, "paddy_fan_gapless")
    ditched = {**base, "field_ditches": [{"field": "t", "poly": [[200, -10], [200, 410]], "w": 40, "role": "branch"}]}
    assert "paddy_fan_gapless" not in f_only(ditched, "paddy_fan_gapless")


def test_city_fan_heads_quilted_moat_exclusion_and_degenerate_segments():
    """Branch coverage for the head-band sampler: a duplicated main vertex (zero-length segment)
    is skipped, and flank samples inside the moat corridor are excluded rather than counted bare
    (the moat legitimately borders a city fan's head where the sluice taps it)."""
    M = {
        "meta": {"scale": "village", "ftpx": 2},
        "moat": [[100, -50], [100, 450]],
        "moat_width": 30,
        "fields": [{"name": "t", "kind": "paddy", "outline": [[0, 0], [400, 0], [400, 400], [0, 400]], "bbox": [0, 0, 400, 400], "plot_polys": [[[60, 0], [400, 0], [400, 400], [60, 400]]]}],
        "field_ditches": [{"field": "t", "poly": [[112, 0], [112, 200], [112, 200], [112, 400]], "w": 6, "role": "main"}],
    }
    f(M)  # execution is the point: west flank samples sit in the moat corridor, the duplicate vertex is skipped
