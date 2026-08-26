"""tier city tests split out of `tests.settlement.test_core` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram.settlement import roll_merchant_estate_count, roll_torii_count
from tests.settlement._builders import _cap020, _castle_map, _city, _torii_city, _town


@pytest.mark.tiers("city")
def test_shrine_hall_rolls_torii_count_per_temple():
    # the 2026-07-23 full re-roll: torii=[...] is avenue GEOMETRY; the COUNT is a seeded
    # per-temple roll on the tier's TORII_WEIGHTS column, recorded on the religious rec
    import random as _rr

    expect = roll_torii_count("city", _rr.Random(9 * 977 + 600 * 31 + 500 * 57))
    s = _torii_city()
    assert s.M["religious"][-1]["torii_count"] == expect
    assert len(s.M["torii"]) == expect


@pytest.mark.tiers("city")
def test_roll_merchant_estate_count_distribution():
    # 30/40/30 for 1/2/3 at city scale - the granted-privilege distribution (MERCHANT_ESTATE_WEIGHTS)
    import collections
    import random as _rr

    from l7r.diagram.settlement import MERCHANT_ESTATE_WEIGHTS

    rng = _rr.Random(7)
    n = 6000
    c = collections.Counter(roll_merchant_estate_count("city", rng) for _ in range(n))
    assert set(c) == {1, 2, 3}
    for count, wt in MERCHANT_ESTATE_WEIGHTS["city"]:
        assert abs(c[count] / n - wt) < 0.03

    class _One:  # rng.random() lives in [0,1) so the exhaustion return is defensively dead - prove it anyway (the roll_torii_count precedent)
        def random(self):
            return 1.0

    assert roll_merchant_estate_count("city", _One()) == 3  # exhaustion falls to the last bucket


@pytest.mark.tiers("city")
def test_execution_ground_is_sized_and_screened_by_tier():
    t = _town()
    t.execution_ground(500, 500)
    e = t.M["execution_grounds"][0]
    assert (e["w"], e["h"]) == (60.0, 60.0)  # county tier: ~60x60 real ft
    assert e["screened"] is False  # a county ground is open to the road on every side
    c = _city()
    c.execution_ground(500, 500)
    ec = c.M["execution_grounds"][0]
    assert (ec["w"], ec["h"]) == (round(c.px(100), 1), round(c.px(60), 1))  # city tier: ~100x60 real ft
    assert ec["screened"] is True


@pytest.mark.tiers("capital")
def test_a_capital_declares_its_scale_and_takes_the_city_building_grain():
    s, _ = _castle_map()
    assert s.M["meta"]["scale"] == "capital"
    assert s.bscale == pytest.approx(1 / 3)


@pytest.mark.tiers("capital", "city")
def test_manor_ink_parameter_marks_foreign_sovereign_ground():
    """The Imperial Magistrate's compound is foreign sovereign ground and must not read as another
    domain office: the manor form, in its own ink (settlements/capitals.md, 'Compounds with no
    provincial equivalent')."""
    s1 = _cap020()
    s1.manor(700, 700, 240, 180, "Imperial Magistrate's Compound", gate_dir="west")
    assert "ink" not in s1.M["manors"][0]  # the default stays byte-identical for every old map
    s2 = _cap020()
    n0 = len(s2.out)
    s2.manor(700, 700, 240, 180, "Imperial Magistrate's Compound", gate_dir="west", ink="#274D3D")
    assert s2.M["manors"][0]["ink"] == "#274D3D"
    assert 'stroke="#274D3D"' in "".join(s2.out[n0:])
