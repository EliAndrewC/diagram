"""tier town tests split out of `tests.check_village.test_segments_06_ways_and_bridges` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import WALLSQ, _capital_manifest, f_only


@pytest.mark.tiers("town")
def test_cistern_wells_sit_on_the_buried_main():
    """Research 021 item 4: josui-ido tap the mokuhi mains that run UNDER THE STREETS from
    the settling basin at the gate - so a cistern-well stands within the band (~600 real ft
    of the terminus, the disclosed calibrated liberty) and beside a street. A dug draw-well
    (no kind) is untouched."""
    M = _capital_manifest()
    M["aqueducts"] = [{"poly": [[900, 100], [700, 300]], "w": 8, "intake": [900, 100], "to": [700, 300]}]
    M["town_streets"] = [{"pts": [[700, 300], [700, 700]], "w": 5}]
    M["wells"] = [{"x": 705, "y": 420, "r": 8, "vr": 6, "shrine": False, "private": False, "kind": "cistern"}]
    assert "cistern_wells_in_service_band" not in f_only(M, "cistern_wells_in_service_band")  # on the street, 120px from the basin
    M["wells"][0]["x"], M["wells"][0]["y"] = 705, 620  # 320px out - beyond the main's reach
    assert "cistern_wells_in_service_band" in f_only(M, "cistern_wells_in_service_band")
    M["wells"][0]["x"], M["wells"][0]["y"] = 760, 380  # in reach but 55px off any street
    assert "cistern_wells_in_service_band" in f_only(M, "cistern_wells_in_service_band")
    M["wells"][0].pop("kind")  # a dug draw-well may stand anywhere wells stand
    assert "cistern_wells_in_service_band" not in f_only(M, "cistern_wells_in_service_band")


@pytest.mark.tiers("town")
def test_kido_close_the_machi_mouths():
    """Research 021 item 6 (the ward MESH): every street mouth into a machi district gets its
    night-barred kido; a mouth without one fires. The mouths come from the SAME shared source
    the placer uses (settlement.machi_mouths), so the two sides cannot disagree."""
    M = _capital_manifest()
    M["districts"] = [{"name": "east machi", "kind": "machi", "poly": [[300, 300], [700, 300], [700, 700], [300, 700]]}]
    M["town_streets"] = [{"pts": [[100, 500], [900, 500]], "w": 5}]  # crosses at (300,500) and (700,500)
    assert "kido_close_the_machi_mouths" in f_only(M, "kido_close_the_machi_mouths")  # two mouths, no kido
    M["kido"] = [{"x": 312, "y": 500, "parts": [], "guard": None}, {"x": 688, "y": 500, "parts": [], "guard": None}]
    assert "kido_close_the_machi_mouths" not in f_only(M, "kido_close_the_machi_mouths")


@pytest.mark.tiers("city", "town")
def test_city_streets_serve_both_sides():
    """GM 2026-08-10: "several city streets extend out into empty space with nothing on either
    side of them and also not leading to anywhere... essentially a road to nowhere check."
    city_streets_have_buildings measures ONE side and excuses claimed open ground; this one
    fires when a long stretch is bare on BOTH."""
    base = {"meta": {"scale": "city", "walled": True, "W": 2000, "H": 2000, "ftpx": 3}, "wall": WALLSQ, "gates": [[500, 200], [500, 800]]}
    bare = {**base, "town_streets": [{"pts": [[300, 400], [900, 400]], "w": 18}]}
    assert "city_streets_serve_both_sides" in f_only(bare, "city_streets_serve_both_sides")
    lined = {
        **base,
        "town_streets": [{"pts": [[300, 400], [900, 400]], "w": 18}],
        "buildings": [{"x": 320 + 60 * i, "y": 360, "w": 14, "h": 10, "rot": 0, "kind": "laborer"} for i in range(11)],
    }
    assert "city_streets_serve_both_sides" not in f_only(lined, "city_streets_serve_both_sides")


@pytest.mark.tiers("city", "town")
def test_streets_reach_neighbors_catches_perpendicular_approaches():
    """GM 2026-08-10: "two city streets which approach each other... generally should
    intersect." The aligned-only test missed a street ending a short way off one it meets at a
    CORNER angle - and the first cut of the perpendicular test compared the end's bearing
    against the LINE OF SIGHT to the other street, which makes two parallel streets 60px apart
    look perpendicular. It must compare against the other street's own bearing."""
    base = {"meta": {"scale": "city", "walled": True, "W": 2000, "H": 2000, "ftpx": 3}, "wall": WALLSQ, "gates": [[500, 200]]}
    tee = {**base, "town_streets": [{"pts": [[400, 300], [400, 900]], "w": 10}, {"pts": [[470, 600], [900, 600]], "w": 10}]}
    assert "city_streets_reach_their_neighbors" in f_only(tee, "city_streets_reach_their_neighbors")  # the east street stops 70px off the north-south one
    joined = {**base, "town_streets": [{"pts": [[400, 300], [400, 900]], "w": 10}, {"pts": [[402, 600], [900, 600]], "w": 10}]}
    assert "city_streets_reach_their_neighbors" not in f_only(joined, "city_streets_reach_their_neighbors")
    parallel = {**base, "town_streets": [{"pts": [[400, 300], [400, 900]], "w": 10}, {"pts": [[460, 300], [460, 900]], "w": 10}]}
    assert "city_streets_reach_their_neighbors" not in f_only(parallel, "city_streets_reach_their_neighbors")  # 60px apart and PARALLEL - not a failed junction
