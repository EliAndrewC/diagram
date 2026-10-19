"""tier city tests split out of `tests.settlement.test_land` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram.settlement import Settlement


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
