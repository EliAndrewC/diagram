"""tier town tests split out of `tests.settlement.test_land` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram.settlement import Settlement


@pytest.mark.tiers("town")
def test_near_ring_paddy_skips_interior_ground_with_no_reachable_water():
    # a town (no moat) with a big frame: interior basins far from the edge have no water -> skipped;
    # only the off-edge band is filled. So no placed basin sits deep in the middle.
    s = Settlement(1600, 1600, seed=3)
    s.meta(name="T", scale="town")
    s.near_ring_paddy((0, 0, 1600, 1600), seed=3, cell_ft=150)
    for fld in s.M["fields"]:
        if fld["name"].startswith("nrp_"):
            b = fld["bbox"]
            touches_edge = b[0] < 60 or b[1] < 60 or b[2] > 1540 or b[3] > 1540
            assert touches_edge  # only edge-watered basins were placed


@pytest.mark.tiers("town")
def test_near_ring_paddy_waters_a_basin_from_a_pond_ring():
    # an INTERIOR bbox (never touches the frame edge, no moat) - so a basin can ONLY be watered by the pond ring
    s = Settlement(1400, 1400, seed=5)
    s.meta(name="T", scale="town")
    s.M["pond"] = [700, 700, 190, 190]
    n = s.near_ring_paddy((450, 450, 950, 950), seed=5, cell_ft=120)
    assert n > 0 and any(fld["name"].startswith("nrp_") for fld in s.M["fields"])


@pytest.mark.tiers("town")
def test_near_ring_paddy_keeps_basins_off_streams_and_the_hill():
    s = Settlement(1400, 1400, seed=4)
    s.meta(name="T", scale="town")
    s.M["hill"] = [700, 200, 200, 140]
    s.M["streams"] = [{"poly": [[700, 0], [700, 1400]], "w": 8}]  # a stream down the middle
    s.near_ring_paddy((0, 0, 1400, 1400), seed=4, cell_ft=150)
    from l7r.diagram.settlement import seg_dist

    for fld in s.M["fields"]:
        if fld["name"].startswith("nrp_"):
            for vx, vy in fld["outline"]:
                assert min(seg_dist(vx, vy, (700, 0), (700, 1400)), 999) > 14  # off the stream
                assert not (((vx - 700) / (200 * 1.35)) ** 2 + ((vy - 200) / (140 * 1.35)) ** 2 <= 1.0)  # off the hill
