"""tier city tests split out of `tests.settlement.test_water_ways` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram.settlement import Settlement
from tests.settlement._builders import _crop_settlement


@pytest.mark.tiers("capital")
def test_quarter_accepts_the_capital_zones():
    """021: "castle" and "samurai" are legal quarter zones (capital vocabulary) - the citadel
    and the senior bands tile the interior without entering the residential density body."""
    s = _crop_settlement()
    s.quarter([(100, 100), (400, 100), (400, 400), (100, 400)], "castle")
    s.quarter([(400, 100), (700, 100), (700, 400), (400, 400)], "samurai")
    assert [q["zone"] for q in s.M["quarters"]] == ["castle", "samurai"]


@pytest.mark.tiers("capital")
def test_kido_mesh_reserves_and_gates_every_machi_mouth():
    """kido_mesh derives its gates from the SAME machi_mouths source the validator reads and
    reserves each gate's ground before the packs (021; the wip capital was its only exerciser)."""
    s = Settlement(1000, 1000, seed=3)
    s.street([(200, 500), (800, 500)])
    s.district("test machi", "machi", [(300, 400), (700, 400), (700, 600), (300, 600)], rank_band=None)
    before = len(s.block_polys)
    n = s.kido_mesh()
    assert n == len(s.M.get("kido", []))
    if n:
        assert len(s.block_polys) > before  # each kido reserved its ground
