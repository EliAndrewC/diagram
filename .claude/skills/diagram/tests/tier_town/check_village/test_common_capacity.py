"""tier town tests split out of `tests.check_village.test_common_capacity` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram import check_village
from tests.check_village._builders import _diamond_city, bldg


@pytest.mark.tiers("city", "town")
def test_city_capacity_ascii_map_classes_every_cell_kind():
    # one manifest carrying a cell of each class, sampled fine enough to hit each branch.
    M = _diamond_city(
        185,
        dwellings=1,
        buildings=[
            bldg(200, 100, "laborer", w=34, h=34),  # D
            bldg(100, 220, "shop", w=34, h=34),
        ],  # C (civic list)
        canals=[{"poly": [[140, 300], [260, 300]], "w": 40}],  # ~ water
        fields=[{"outline": [[280, 180], [320, 180], [320, 220], [280, 220]], "bbox": [280, 180, 320, 220]}],  # F
        road=[[200, 140], [200, 260]],
        road_width=26,  # # trunk
        town_streets=[{"pts": [[120, 160], [180, 160]], "w": 12}],  # + res_st
    )
    rep = check_village.city_capacity(M, grid_step=20)
    flat = "".join(rep["grid"])
    for sym in "DC~F#+. ":  # every class incl. OPEN and OUTSIDE
        assert sym in flat, f"class {sym!r} never sampled"
    assert rep["grid_step"] == 20 and rep["grid_origin"] == (0, 0)
