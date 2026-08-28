"""tier city tests split out of `tests.check_village.test_segments_03_structures_and_wards` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    _CHAN,
    WALL,
    f_only,
)


@pytest.mark.tiers("city")
def test_irrigation_channels_hairline_allows_a_drain_outfall_culvert_at_four():
    # a drain-outfall culvert carries the fan's whole runoff and matches the drain's outfall width
    # (4.0 at the city grain) - it is not a field ditch, so its ceiling is 4.5 (GM 2026-07-23)
    M = {"channels": [{"poly": _CHAN, "frm": {"kind": "drain"}, "to": {"kind": "moat"}, "w": 4.0}]}
    assert "irrigation_channels_hairline" not in f_only(M, "irrigation_channels_hairline")


@pytest.mark.tiers("city")
def test_torii_and_religious_clear_of_works_and_ring():
    # GM placement rules (2026-07-21, caught on Tango): torii keep clear of halls/towers/the ring
    # road; religious footprints keep clear of towers/the ring road. An ordinary street through a
    # torii stays legal (only the RING corridor counts), so no street data appears here.
    base = {"meta": {"scale": "city", "ftpx": 3}, "ring_road": [[100, 900], [900, 900]], "ring_road_width": 8, "wall_towers": [{"x": 500, "y": 500, "w": 38, "h": 38}]}
    hall = {"kind": "temple", "x": 300, "y": 300, "w": 43, "h": 28, "label": "Temple of Ebisu"}
    # torii: on the hall / on the tower / on the ring -> fire; standing clear -> pass
    assert "torii_clear_of_halls_towers_ring" in f_only({**base, "religious": [hall], "torii": [[305, 310, 9]]}, "torii_clear_of_halls_towers_ring")
    assert "torii_clear_of_halls_towers_ring" in f_only({**base, "religious": [hall], "torii": [[505, 512, 9]]}, "torii_clear_of_halls_towers_ring")
    assert "torii_clear_of_halls_towers_ring" in f_only({**base, "religious": [hall], "torii": [[400, 902, 9]]}, "torii_clear_of_halls_towers_ring")
    assert "torii_clear_of_halls_towers_ring" not in f_only({**base, "religious": [hall], "torii": [[300, 380, 9]]}, "torii_clear_of_halls_towers_ring")
    # religious: the Tango defect (shrine on a wall tower) and a hall on the ring -> fire; clear -> pass
    shrine_on_tower = {"kind": "small_shrine", "x": 521, "y": 509, "w": 11, "h": 8}
    assert "religious_clear_of_ring_and_towers" in f_only({**base, "religious": [shrine_on_tower]}, "religious_clear_of_ring_and_towers")
    assert "religious_clear_of_ring_and_towers" in f_only({**base, "religious": [{**hall, "y": 890}]}, "religious_clear_of_ring_and_towers")
    # ...and a hall standing ON THE EDGE of the roadbed without crossing its centerline: entirely
    # south of y=900 but lapping the bed's 896-904 span. Crossing and proximity are separate
    # branches of the corridor test and this is the one only proximity catches.
    assert "religious_clear_of_ring_and_towers" in f_only({**base, "religious": [{**hall, "y": 916}]}, "religious_clear_of_ring_and_towers")
    assert "religious_clear_of_ring_and_towers" not in f_only({**base, "religious": [hall]}, "religious_clear_of_ring_and_towers")


@pytest.mark.tiers("city")
def test_torii_clear_of_walls():
    # GM 2026-07-25, caught on Nagahara: the 7th arch of the Ebisu sando stood IN the samurai ward
    # fence. A torii is a FREESTANDING gateway and a wall is a continuous barrier, so an arch never
    # stands in one - a way through a wall is a GATE. Every wall counts: the city rampart, a ward
    # fence (and its wall-cap), and the perimeter of a walled compound.
    base = {"meta": {"scale": "city", "ftpx": 3}}
    fence = {"name": "samurai", "boundary": [[300, 700], [900, 700]], "z": 10, "wall_caps": []}
    manor = {"x": 400, "y": 400, "w": 60, "h": 40, "rot": 0, "wall_w": 2}
    assert "torii_clear_of_walls" in f_only({**base, "wards": [fence], "torii": [[600, 699, 9]]}, "torii_clear_of_walls")  # the Nagahara defect
    assert "torii_clear_of_walls" not in f_only({**base, "wards": [fence], "torii": [[600, 680, 9]]}, "torii_clear_of_walls")  # the sando stops short
    assert "torii_clear_of_walls" in f_only({**base, "wall": WALL, "torii": [[500, 52, 9]]}, "torii_clear_of_walls")  # standing in the rampart
    assert "torii_clear_of_walls" in f_only(
        {**base, "wards": [{**fence, "wall_caps": [{"x": 300, "y": 700, "z": 3, "pts": [[290, 690], [290, 760]]}]}], "torii": [[290, 730, 9]]}, "torii_clear_of_walls"
    )
    assert "torii_clear_of_walls" in f_only({**base, "manors": [manor], "torii": [[400, 420, 9]]}, "torii_clear_of_walls")  # in a compound wall
    assert "torii_clear_of_walls" not in f_only({**base, "manors": [manor], "torii": [[400, 460, 9]]}, "torii_clear_of_walls")
    assert "torii_clear_of_walls" in f_only({**base, "governor_mansion": {**manor, "x": 700}, "torii": [[700, 420, 9]]}, "torii_clear_of_walls")
    assert "torii_clear_of_walls" in f_only({**base, "merchant_estates": [{**manor, "y": 200}], "torii": [[430, 200, 9]]}, "torii_clear_of_walls")
    assert "torii_clear_of_walls" in f_only({**base, "mausoleums": [{**manor, "y": 900}], "torii": [[370, 900, 9]]}, "torii_clear_of_walls")
    # a run that ENDS inside the arch box, crossing none of its edges, still counts as standing in it
    assert "torii_clear_of_walls" in f_only({**base, "wards": [{**fence, "boundary": [[599, 700], [601, 701]]}], "torii": [[600, 700, 9]]}, "torii_clear_of_walls")
