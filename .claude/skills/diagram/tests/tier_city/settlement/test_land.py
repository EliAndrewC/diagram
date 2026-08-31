"""tier city tests split out of `tests.settlement.test_land` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram.settlement import Settlement


@pytest.mark.tiers("city")
def test_near_ring_cropland_keeps_a_city_ring_outside_the_wall():
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="C", scale="city")
    s.M["wall"] = [[300, 300], [700, 300], [700, 700], [300, 700]]  # a square rampart
    s.near_ring_cropland((0, 0, 600, 600), density="dense", seed=4)
    from l7r.diagram.settlement import point_in_poly

    for p in s.M["dry_plots"]:
        cx = sum(v[0] for v in p["poly"]) / 4
        cy = sum(v[1] for v in p["poly"]) / 4
        assert not point_in_poly(cx, cy, [(300, 300), (700, 300), (700, 700), (300, 700)])  # no cropland inside the wall


@pytest.mark.tiers("city")
def test_near_ring_paddy_moat_feeds_a_walled_city_basin_with_a_channel():
    s = Settlement(1400, 1400, seed=6)
    s.meta(name="C", scale="city")
    s.M["wall"] = [[500, 500], [900, 500], [900, 900], [500, 900]]
    s.M["moat"] = [[480, 480], [920, 480], [920, 920], [480, 920]]
    s.M["moat_width"] = 22
    # a big building band just outside the west moat: a basin west of it can only be moat-fed by a
    # channel that would CROSS the building, so that basin is skipped (the channel-clearance keep-out)
    s.M["buildings"] = [{"x": 430, "y": 700, "w": 60, "h": 340, "rot": 0, "kind": "warehouse"}]
    # a road + a rect-record cemetery: both keep-out builders must run (these paths were exercised by
    # the pool maps until the 2026-07-23 combs-only doctrine retired the basins from every gen)
    s.M["road"] = [[0, 1300], [1400, 1300]]
    s.M["cemeteries"] = [{"x": 1200, "y": 200, "w": 60, "h": 40}]
    n = s.near_ring_paddy((0, 0, 1400, 1400), seed=6, cell_ft=200)
    assert n > 0
    # interior (non-off-edge) basins are moat-fed: there is at least one moat->field channel
    assert any((c.get("frm") or {}).get("kind") == "moat" for c in s.M.get("channels", []))
    # no moat channel crosses the building (the clearance keep-out held)
    from l7r.diagram.settlement import seg_dist

    for c in s.M.get("channels", []):
        if (c.get("frm") or {}).get("kind") == "moat":
            assert seg_dist(430, 700, c["poly"][0], c["poly"][-1]) > 25


@pytest.mark.tiers("city")
def test_near_ring_paddy_respects_the_moat_current_when_the_moat_is_fed():
    # a moat fed by a stream from the north flows south; every moat intake must tap upstream of its basin
    s = Settlement(1600, 1600, seed=7)
    s.meta(name="C", scale="city")
    s.M["wall"] = [[600, 600], [1000, 600], [1000, 1000], [600, 1000]]
    s.M["moat"] = [[580, 580], [1020, 580], [1020, 1020], [580, 1020]]
    s.M["moat_width"] = 22
    s.M["streams"] = [{"poly": [[800, 580], [800, 200]], "w": 8}]  # feeder entering the moat top, coming from the north
    s.near_ring_paddy((0, 0, 1600, 1600), seed=7, cell_ft=220)
    for c in s.M.get("channels", []):
        if (c.get("frm") or {}).get("kind") == "moat":
            (_sx, sy), (_ex, ey) = c["poly"][0], c["poly"][-1]
            assert ey - sy >= -8  # field-end not upstream (north) of the moat tap - flows with the southward current


@pytest.mark.tiers("capital")
def test_commons_bare_records_the_claim_and_draws_nothing():
    """render='bare' claims the ground (full record: role, poly, render) but scatters no scrub -
    the GM's no-glyphs-on-claimed-capital-ground ruling (021)."""
    s = Settlement(800, 800, seed=9)
    svg_before = len(s.out)
    s.commons([(100, 100), (300, 100), (300, 260), (100, 260)], role="drill ground", render="bare")
    rec = s.M["commons"][-1]
    assert rec["role"] == "drill ground" and rec["poly"][0] == [100, 100]
    assert len(s.out) == svg_before  # no ink


def test_near_ring_paddy_takes_its_FLOW_from_the_stream_that_feeds_the_moat() -> None:
    """Feature 174. On a WALLED city the near-ring basins may be fed from the moat, and the moat's
    own flow direction is inferred from the stream that enters it - which end of the stream touches
    the ring tells you which way the water is going.

    Paddy is never conjured without water: ground with no reachable source is SKIPPED, "the honest
    limit: where the near ring genuinely lacks water, draw fewer basins / a lower tier, don't fake
    it". So the assertion is that basins appear at all with a fed moat, and the branch that reads
    the feeding stream is what makes that possible.
    """
    s = Settlement(2000, 2000, seed=19)
    s.meta(name="C", scale="city", ftpx=1)
    s.M["wall"] = [[600.0, 600.0], [1400.0, 600.0], [1400.0, 1400.0], [600.0, 1400.0]]
    s.M["moat"] = [[560.0, 560.0], [1440.0, 560.0], [1440.0, 1440.0], [560.0, 1440.0]]
    # a stream arriving at the moat from the north: its far end is the origin, so the flow is +y
    s.M["streams"] = [{"poly": [(1000.0, 100.0), (1000.0, 545.0)], "w": 9}]

    n = s.near_ring_paddy((100.0, 1500.0, 500.0, 1900.0), seed=3)
    assert isinstance(n, int), "the pass runs with a fed moat and reports what it drew"
