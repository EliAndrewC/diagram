"""tier city tests split out of `tests.settlement.test_trades` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram.settlement import Settlement


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
