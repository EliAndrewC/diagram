"""Unit tests for the spec a caller writes and the site plan derived from it (`hamletgen/plan.py`).

Split from test_hamletgen.py by feature 111; test bodies verbatim. See hamletgen/CLAUDE.md.
"""

import math

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen.consts import COPSE_SITINGS, KOSATSUBA_SITINGS

from ._builders import a_plan

# ---- the spec refuses what the tier cannot draw --------------------------------------------------


@pytest.mark.parametrize("households", [0, 9, 21, 400])
def test_a_household_count_outside_the_hamlet_band_is_refused(households: int) -> None:
    """Below the band the place is an outlying farmstead; above it, it is a village and needs a
    headman, a shrine and tax-free plots this generator deliberately does not draw. Silently
    generating one anyway would produce a map that fails the gate for reasons that look unrelated."""
    with pytest.raises(ValueError, match="hamlet band"):
        hg.HamletSpec(name="X", seed=1, households=households)


def test_a_nonsense_compass_quarter_is_refused() -> None:
    with pytest.raises(ValueError, match="compass quarter"):
        hg.HamletSpec(name="X", seed=1, windward="NNW")


def test_an_unknown_water_sink_is_refused() -> None:
    with pytest.raises(ValueError, match="water_sink"):
        hg.HamletSpec(name="X", seed=1, water_sink="river")


# ---- sizing -------------------------------------------------------------------------------------


def test_the_field_target_is_gross_acres_times_households() -> None:
    plan = hg.plan_site(hg.HamletSpec(name="X", seed=1, households=15))
    assert plan.target_acres == pytest.approx(15 * hg.GROSS_ACRES_PER_HOUSEHOLD)


def test_the_canvas_grows_with_the_field_it_has_to_hold() -> None:
    small = hg.canvas_for(13.0, 1.0)
    big = hg.canvas_for(26.0, 1.0)
    assert big[0] > small[0] and big[1] > small[1]
    # ...and it is comfortably larger than the field, so `build_comb` never clamps the fan
    assert small[0] * small[1] > 13.0 * hg.SQ_FT_PER_ACRE * 2


@pytest.mark.parametrize(("households", "expect_last"), [(10, 0.93), (15, 0.93), (20, 0.93)])
def test_the_last_offtake_sits_near_the_canal_end(households: int, expect_last: float) -> None:
    """A supply canal running far past its last delivery ditch leaves a tail that dies in bare
    ground - see OFFTAKE_LADDER. Ikegami's authored 0.66 is exactly that shape of number."""
    a, _b = hg.offtakes_for(households)
    assert a[-1] == expect_last


def test_the_offtake_ladder_covers_counts_past_its_last_rung() -> None:
    assert hg.offtakes_for(999) == (hg.OFFTAKE_LADDER[-1][1], hg.OFFTAKE_LADDER[-1][2])


# ---- the rolls ----------------------------------------------------------------------------------


def test_the_same_seed_plans_the_same_hamlet() -> None:
    one = hg.plan_site(hg.HamletSpec(name="X", seed=11, households=14))
    two = hg.plan_site(hg.HamletSpec(name="X", seed=11, households=14))
    assert (one.down_deg, one.windward, one.water_sink, one.cluster_shape, one.lane_skeleton) == (two.down_deg, two.windward, two.water_sink, two.cluster_shape, two.lane_skeleton)


def test_different_seeds_roll_different_hamlets() -> None:
    """The whole point of the knob layer: a cohort must not be twenty copies of one map."""
    combos = {(p.down_deg, p.water_sink, p.cluster_shape, p.lane_skeleton) for p in (hg.plan_site(hg.HamletSpec(name="X", seed=s, households=15)) for s in range(1, 21))}
    assert len(combos) >= 12


def test_every_declared_knob_is_honored_over_its_roll() -> None:
    plan = hg.plan_site(
        hg.HamletSpec(
            name="X",
            seed=5,
            households=13,
            down_deg=180.0,
            water_flow=95.0,
            windward="E",
            water_sink="offmap",
            cluster_shape="crescent",
            lane_skeleton="Y",
            plot_size="strip",
            grain_drift=12,
            woodland_patches=1,
        )
    )
    assert (plan.down_deg, plan.water_flow, plan.windward, plan.water_sink) == (180.0, 95.0, "E", "offmap")
    assert (plan.cluster_shape, plan.lane_skeleton, plan.plot_size, plan.grain_drift, plan.woodland_patches) == ("crescent", "Y", "strip", 12, 1)


def test_the_drainage_bearing_follows_the_fall_unless_declared() -> None:
    """A hamlet is one comb draining down one valley, so absent a declaration the two agree - but
    they stay separate fields, because at any larger tier they are genuinely different facts."""
    assert hg.plan_site(hg.HamletSpec(name="X", seed=2, down_deg=45.0)).water_flow == 45.0


@pytest.mark.parametrize("down_deg", [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0])
def test_the_cold_wind_comes_off_the_high_ground(down_deg: float) -> None:
    """Cold air drains downhill, so the wind a valley settlement shelters from blows from upslope
    (turned up to 45 deg). This is what makes 'back to the hill' and 'back to the wind' one fact
    rather than two, and rolling them apart put a cluster in the drainage ditch - see WIND_TURNS."""
    wx, wy = hg.WIND_VECTORS[hg.windward_for(down_deg, seed=4)]
    up = (-math.cos(math.radians(down_deg)), -math.sin(math.radians(down_deg)))
    assert wx * up[0] + wy * up[1] > 0.5  # within 60 deg of straight upslope


def test_a_nonsense_field_archetype_is_refused() -> None:
    with pytest.raises(ValueError, match="field_archetype"):
        hg.HamletSpec(name="X", seed=1, field_archetype="terraces")


def test_the_roll_only_offers_archetypes_that_gate_clean() -> None:
    """`polder_grid` is opt-in until its own cohort is green (see ROLLED_ARCHETYPES).

    A rolled archetype with known failures mixes them into the valley tier's 36/36 and destroys the
    one number that says the scripted process is consistent - which is exactly what happened the
    moment the polder was added to the roll. Pinning it is still honored; only the ROLL is held
    back, and this is the test that will fail (correctly) on the day someone promotes it."""
    assert set(hg.ROLLED_ARCHETYPES) <= set(hg.FIELD_ARCHETYPES)
    rolled = {hg.plan_site(hg.HamletSpec(name="X", seed=s, households=15)).field_archetype for s in range(1, 30)}
    assert rolled == set(hg.ROLLED_ARCHETYPES)


# ---- the dike-pond archetype (feature 150) ----------------------------------------------------------


def test_the_dike_pond_is_a_declared_archetype_laid_to_a_cardinal_fall() -> None:
    """`mulberry_dike_fishpond` is opt-in like the polder it is built on, and a polder is laid to
    the cardinal survey grid (see `plan_site`)."""
    for seed in range(1, 12):
        plan = hg.plan_site(hg.HamletSpec(name="X", seed=seed, households=16, field_archetype="mulberry_dike_fishpond"))
        assert plan.field_archetype == "mulberry_dike_fishpond"
        assert plan.down_deg in hg.CARDINAL_BEARINGS


def test_a_dike_pond_rolls_its_arrangement_and_a_rice_polder_is_the_grid() -> None:
    """Two attested forms roll (`POND_LAYOUTS`); the rice polder never rolls, so every polder_grid
    map is byte-identical to before the knob existed."""
    rolled = {hg.plan_site(hg.HamletSpec(name="X", seed=s, households=16, field_archetype="mulberry_dike_fishpond")).pond_layout for s in range(1, 40)}
    assert rolled == {"grid", "mosaic"}
    assert all(hg.plan_site(hg.HamletSpec(name="X", seed=s, households=16, field_archetype="polder_grid")).pond_layout == "grid" for s in range(1, 12))
    assert hg.plan_site(hg.HamletSpec(name="X", seed=3, households=16, field_archetype="mulberry_dike_fishpond", pond_layout="grid")).pond_layout == "grid"


def test_the_manure_form_rolls_both_ways_and_pins() -> None:
    """Two attested forms (feature 150 A2): heap (Tohoku) and pit (Lake Tai), rolled per hamlet."""
    rolled = {hg.plan_site(hg.HamletSpec(name="X", seed=s, households=15)).manure_form for s in range(1, 30)}
    assert rolled == {"heap", "pit"}
    assert hg.plan_site(hg.HamletSpec(name="X", seed=3, households=15, manure_form="pit")).manure_form == "pit"
    with pytest.raises(ValueError, match="manure_form"):
        hg.HamletSpec(name="X", seed=1, manure_form="lagoon")


def test_the_dike_crop_and_leftover_roll_on_the_dike_pond_and_pin_elsewhere() -> None:
    """Feature 150 A6/B2: a dike-pond hamlet rolls its dike type and its leftover form; every other archetype is
    mulberry/rice by definition (the knobs have no meaning there and must not re-roll anything)."""
    crops = {hg.plan_site(hg.HamletSpec(name="X", seed=s, households=16, field_archetype="mulberry_dike_fishpond")).dike_crop for s in range(1, 60)}
    assert crops == {"mulberry", "sugarcane", "banana", "fruit"}
    lefts = {hg.plan_site(hg.HamletSpec(name="X", seed=s, households=16, field_archetype="mulberry_dike_fishpond")).leftover for s in range(1, 40)}
    assert lefts == {"rice", "vegetables", "pond"}
    p = hg.plan_site(hg.HamletSpec(name="X", seed=3, households=15))
    assert (p.dike_crop, p.leftover) == ("mulberry", "rice")
    p = hg.plan_site(hg.HamletSpec(name="X", seed=3, households=16, field_archetype="mulberry_dike_fishpond", dike_crop="banana", leftover="pond"))
    assert (p.dike_crop, p.leftover) == ("banana", "pond")
    with pytest.raises(ValueError, match="dike_crop"):
        hg.HamletSpec(name="X", seed=1, dike_crop="tea")
    with pytest.raises(ValueError, match="leftover"):
        hg.HamletSpec(name="X", seed=1, leftover="wheat")


def test_pond_stock_is_a_no_op_off_the_dike_pond() -> None:
    """The stage draws nothing on a valley hamlet - it has no ponds to keep stock on (feature 150 A3/A4)."""
    from l7r.diagram.hamletgen.pondstock import stage_pond_stock
    from l7r.diagram.settlement import Settlement

    s = Settlement(W=400, H=400, seed=1)
    s.M["houses"] = [{"x": 100.0, "y": 100.0}]
    stage_pond_stock(s, a_plan())
    assert "pig_sties" not in s.M and "duck_pens" not in s.M


def test_a_nonsense_pond_layout_is_refused() -> None:
    with pytest.raises(ValueError, match="pond_layout"):
        hg.HamletSpec(name="X", seed=1, pond_layout="chessboard")


def test_the_polder_fabric_table_covers_every_polder_archetype() -> None:
    """A polder archetype without a fabric row would KeyError in `stage_polder`."""
    assert set(hg.POLDER_ARCHETYPES) == set(hg.POLDER_FABRIC)
    assert set(hg.POLDER_ARCHETYPES) <= set(hg.FIELD_ARCHETYPES)
    assert "mulberry_dike_fishpond" not in hg.ROLLED_ARCHETYPES  # opt-in until a cohort is green


def test_the_waterward_flanks_are_the_ones_the_village_does_not_stand_on() -> None:
    """Fall S, village seated E: the west flank and the south foot face the water - the
    hand-authored Kuwabata's `["W", "S"]`, derived. The head (N, the reservoir) is never a flank."""
    plan = a_plan(field_archetype="polder_grid")
    plan.seat = {"out": (1.0, 0.0)}
    assert hg.polder_flanks(plan) == {"head": "N", "foot": "S", "plus": "E", "minus": "W", "cluster": "E"}
    assert hg.waterward_flanks(plan) == ["W", "S"]
    assert hg.polder_crossing_caps(plan) == {"feeder": 0, "w_toe": 0, "drain": 0, "e_toe": 3, "lateral": 1}
    plan.seat = {"out": (-1.0, 0.0)}
    assert hg.waterward_flanks(plan) == ["E", "S"]
    assert hg.polder_crossing_caps(plan)["w_toe"] == 3 and hg.polder_crossing_caps(plan)["e_toe"] == 0
    plan.seat = {"out": (0.0, -1.0)}  # seated at the HEAD: the feeder is the village's collector
    assert hg.polder_crossing_caps(plan) == {"feeder": 3, "drain": 0, "e_toe": 1, "w_toe": 1, "lateral": 1}
    plan.seat = {"out": (0.0, 1.0)}  # at the foot: the drain
    assert hg.polder_crossing_caps(plan)["drain"] == 3 and hg.polder_crossing_caps(plan)["feeder"] == 0
    plan.seat = {}
    assert hg.polder_flanks(plan)["cluster"] == ""


def test_a_pond_whose_bank_cannot_hold_the_fixture_is_passed_over() -> None:
    """EACH POND TAKES AT MOST ONE FIXTURE, AND ONLY IF ITS BANK HAS ROOM. The seat is derived from the
    parcel and the house centroid, so it can land somewhere the fixture does not fit - on the water, off
    the canvas, or against something already standing. The pond is then skipped and the next one in the
    walk order is tried, rather than the fixture being forced or the whole run abandoned.

    Reaching this from a rolled map needs a dike-pond hamlet whose nearest pond happens to have a
    blocked bank, which none of the four in the pool does - so the branch is asked directly, with
    hand-built pond records: one whose bank seat is off the canvas entirely, and one with room."""
    from l7r.diagram.hamletgen.pondstock import stage_pond_stock
    from l7r.diagram.settlement import Settlement

    plan = hg.plan_site(hg.HamletSpec(name="X", seed=3, households=16, field_archetype="mulberry_dike_fishpond"))

    def _pond(x: float, y: float) -> dict:
        parcel = [(x - 60.0, y - 40.0), (x + 60.0, y - 40.0), (x + 60.0, y + 40.0), (x - 60.0, y + 40.0)]
        return {"parcel": parcel, "water": parcel, "kind": "growout"}

    s = Settlement(W=900, H=900, seed=1)
    s.meta(name="X", scale="hamlet")
    s.M["houses"] = [{"x": 450.0, "y": 450.0, "w": 46.0, "h": 28.0} for _ in range(4)]
    # one pond's bank seat lands on the houses themselves - `pond_fixture_fits` holds a fixture clear
    # of every placed footprint, so that pond can take nothing and the walk moves on to the next
    s.M["dikeponds"] = [_pond(450.0, 500.0), _pond(450.0, 250.0), _pond(450.0, 700.0)]
    stage_pond_stock(s, plan)

    declared = s.M["meta"]["pond_stock"]
    assert declared["sties"] >= 0 and declared["pens"] >= 0
    placed = len(s.M.get("pig_sties") or []) + len(s.M.get("duck_pens") or [])
    assert placed <= 2, "the pond whose bank is under the houses can hold nothing"
    for rec in (s.M.get("pig_sties") or []) + (s.M.get("duck_pens") or []):
        assert rec.get("pond") != 0, "the pond whose bank could not hold a fixture was skipped"


def test_the_copse_and_kosatsuba_sitings_pin_and_refuse_a_value_the_generator_cannot_draw() -> None:
    """Feature 174: the last two unvalidated-in-test knob validators on the spec.

    Both accept a legal value and refuse an illegal one. Asserting only the refusal would pass with
    the whole `if` inverted, which is the mirror-branch trap the peer session hit on `drop_end_nubs`
    the same day - so each pin is asserted beside its refusal.
    """
    for value in COPSE_SITINGS:
        assert hg.plan_site(hg.HamletSpec(name="X", seed=3, households=16, copse_siting=value)).copse_siting == value
    with pytest.raises(ValueError, match="copse_siting"):
        hg.HamletSpec(name="X", seed=1, copse_siting="in_the_paddy")

    for value in KOSATSUBA_SITINGS:
        assert hg.plan_site(hg.HamletSpec(name="X", seed=3, households=16, kosatsuba_siting=value)).kosatsuba_siting == value
    with pytest.raises(ValueError, match="kosatsuba_siting"):
        hg.HamletSpec(name="X", seed=1, kosatsuba_siting="on_the_shrine")
