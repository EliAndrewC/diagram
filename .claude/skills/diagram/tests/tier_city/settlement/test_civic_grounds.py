"""tier city tests split out of `tests.settlement.test_civic_grounds` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram.settlement import Settlement
from tests.settlement._builders import _cap020, _crop_settlement


@pytest.mark.tiers("city")
def test_cemetery_organic_false_keeps_the_louzeyuan_rectangle():
    # the deliberate per-city override: a plotted Chinese-style charity ground stays a ruled rectangle
    s = _crop_settlement()
    s.cemetery(300, 300, 100, 70, parish=False, organic=False)
    assert 'width="100"' in s.out[-1] and "<path" not in s.out[-1]


@pytest.mark.tiers("capital")
def test_granary_append_records_a_list_for_a_capital_with_two_granaries():
    """A capital holds its grain in TWO places for two reasons (the domain's working rice at the
    wharf, the Emperor's stores beside it) - the legacy single M['granary'] dict cannot carry
    both, so append=True records each store into the M['granaries'] LIST instead."""
    s = _cap020()
    s.granary(400, 400, n=3, w=20, h=12, gap=8, label="domain granary", append=True)
    s.granary(800, 300, n=2, w=20, h=12, gap=8, label="Imperial granaries", append=True)
    assert "granary" not in s.M  # the legacy dict is untouched
    assert len(s.M["granaries"]) == 5  # one record per store, so the matrix can see each
    assert {r["label"] for r in s.M["granaries"]} == {"domain granary", "Imperial granaries"}
    assert all("w" in r and "h" in r for r in s.M["granaries"])


# ---- feature 174: the two funerary works whose SIZE is a tier rule ---------------------------------
# Branch-coverage tests (GM 2026-08-31's division of labor): the end-to-end suite draws these on real
# maps, and these say what the tier branch is FOR. Both encode a recorded fixed-pixel defect.


def test_a_cremation_ground_is_sized_by_TIER_not_by_a_fixed_pixel_glyph() -> None:
    """GM 2026-07-19, anchors in settlements.md: a sanmai's cleared working core is 30-80 real ft for
    a village or town and ~80-160 ft for a provincial city - even metropolitan Edo's Yoyogi crematory
    was only ~180 ft square. The old glyph was FIXED-PIXEL (116x80 px) and silently TRIPLED at city
    scale, which is the defect this branch exists to prevent.

    So the branch is asserted by its consequence: a city's ground is drawn larger than a village's,
    at the same ftpx.
    """
    village = Settlement(1000, 1000, seed=2)
    village.meta(name="V", scale="village")
    village.cremation_ground(500.0, 500.0)

    city = Settlement(1000, 1000, seed=2)
    city.meta(name="C", scale="city")
    city.cremation_ground(500.0, 500.0)

    assert village.M["cremation_grounds"] and city.M["cremation_grounds"]
    v_w = village.M["cremation_grounds"][-1].get("w") or village.M["cremation_grounds"][-1].get("vw")
    c_w = city.M["cremation_grounds"][-1].get("w") or city.M["cremation_grounds"][-1].get("vw")
    assert c_w > v_w, f"a city crematory is bigger than a village's ({c_w} vs {v_w})"
    assert not village._fits(500.0, 500.0, 8.0, 8.0), "and it blocks - death-pollution ground is not free ground"


def test_a_pauper_ossuary_mound_stays_inside_its_researched_BAND_at_every_scale() -> None:
    """GM 2026-07-19, tightened 2026-07-21: a muenzuka is a 10-30 real-ft mound - cremated,
    consolidated bone takes almost no volume, and Kyoto's monumental Mimizuka, a STATE monument, is
    only ~50 ft at the base.

    The constant's own history is why this test exists: the original glyph was fixed-pixel (92x60 px
    = a 276 ft kofun at city scale); the first fix drew ~40 ft with a 9 px floor, which STILL
    rendered 54 real ft at city scale - the FLOOR, not the size, controlled. So the assertion is on
    real feet at a coarse scale, which is exactly where both earlier versions failed.
    """
    city = Settlement(2000, 2000, seed=2)
    city.meta(name="C", scale="city", ftpx=3)
    city.ossuary(1000.0, 1000.0)
    rec = city.M["ossuaries"][-1]
    drawn_px = rec.get("w") or rec.get("vw")
    real_ft = drawn_px * 3
    assert real_ft <= 40.0, f"inside the 10-30 ft band with a little slack for the stroke floor, not a 276 ft kofun ({real_ft:.0f} ft)"
