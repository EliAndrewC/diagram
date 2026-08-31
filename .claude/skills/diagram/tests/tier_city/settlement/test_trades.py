"""tier city tests split out of `tests.settlement.test_trades` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram.settlement import Settlement
from tests.settlement._builders import _city


@pytest.mark.tiers("city")
def test_bathhouses_roll_follows_the_population_formula():
    # GM formula 2026-07-24 (second refinement): 1 per full 2,000 population + a remainder-
    # fraction chance of one extra (2,500 -> 1 + 25%, 3,000 -> 1 + 50%, 4,000 -> exactly 2);
    # count= pins; too few seats is loud. Own Settlements with pinned seeds (the module has two
    # _city helpers and the later one shadows - a seed-3 assumption here failed on seed 1):
    # seed 2's dedicated roll is 0.670 (extra misses at 50%), seed 1's is 0.258 (extra lands).
    def city_(seed, pop):
        s_ = Settlement(1200, 1200, seed=seed)
        s_.meta(name="C", scale="city", ftpx=3)
        s_.M["meta"]["population"] = pop
        return s_

    s = city_(2, 2000)  # zero remainder: exactly 1, no roll can add
    assert s.bathhouses([(300, 300), (600, 600)]) == 1
    assert s.M["meta"]["bathhouse_roll"] == 1 and len(s.M["bathhouses"]) == 1
    s2 = city_(2, 4000)  # two full units, zero remainder: exactly 2
    assert s2.bathhouses([(300, 300), (600, 600)]) == 2
    assert len(s2.M["bathhouses"]) == 2
    assert city_(2, 3000).bathhouses([(300, 300), (600, 600)]) == 1  # roll 0.670 >= 0.50: no extra
    assert city_(1, 3000).bathhouses([(300, 300), (600, 600)]) == 2  # roll 0.258 < 0.50: extra lands
    assert city_(2, 3000).bathhouses([(300, 300), (600, 600)], count=2) == 2  # pin overrides the roll
    s4 = city_(2, 4000)
    with pytest.raises(ValueError, match="vetted seats"):
        s4.bathhouses([(300, 300)])  # a guaranteed 2 needs 2 seats


# ---- feature 174: the three trade works with no test at all ---------------------------------------
# `dye_yard`, `oil_press` and `pawnshop` are city works, and no scripted generator produces a city -
# so all three were unreached. Each records through the shared `_trade_record`, and what is worth
# pinning is the thing each one's docstring says makes it that trade: its GROUND, not its workshop.


def test_a_dye_yard_records_GROUND_larger_than_the_workshop_that_fits_a_shophouse() -> None:
    """Its docstring's own claim: "the workshop fits a shophouse - the GROUND does not", because the
    drying frames need open air. So the recorded footprint has to exceed a shophouse's, which is
    what stops a later pack from seating a house across the drying ground."""
    s = _city()
    s.dye_yard(600.0, 600.0)
    rec = s.M["dye_yards"][-1]
    assert rec["w"] > s.px(48) and rec["h"] > s.px(32), "the yard is bigger than the shopfront on it"
    assert not s._fits(600.0, 600.0, 10.0, 10.0), "and it blocks - the drying ground is not free ground"


def test_an_oil_press_reserves_the_beam_swing_beyond_its_barn() -> None:
    """The wedge-and-beam press is a massive timber machine whose working radius is part of the
    premises, so the recorded width exceeds the 54 ft barn it stands in."""
    s = _city()
    s.oil_press(700.0, 500.0)
    rec = s.M["oil_presses"][-1]
    assert rec["w"] > s.px(54), "the barn plus the swing, not the barn alone"
    assert rec["h"] == s.px(30)


def test_a_pawnshop_is_a_shopfront_whose_TELL_is_its_storage() -> None:
    """A pledge is bulky, so the depth behind the shopfront is the trade's signature - the recorded
    height exceeds the plain 32 ft shop depth while the frontage stays shop-sized."""
    s = _city()
    s.pawnshop(400.0, 400.0)
    rec = s.M["pawnshops"][-1]
    assert rec["h"] > s.px(32), "the storehouse behind the counter"
    assert rec["w"] < rec["h"] * 4, "but the frontage is still an ordinary shop's"
