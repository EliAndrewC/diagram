"""gate tests split out of `tests.hamletgen.test_water` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram import hamletgen as hg
from tests.gate import _pool

# THE POLDER TESTS LEFT FOR THE SOAK TIER (feature 219): the gate rolls no spec of its own - Kuwabata below is the
# POOL's map, read through `tests/gate/_pool.py`; the polder-grid assertions roll Polder 12 in tests/soak/test_polder_fall_0.py.


@pytest.mark.rolls_map
def test_a_dike_pond_hamlet_is_ponds_in_a_diked_block_with_wet_flanks() -> None:
    """THE THIRD FIELD ARCHETYPE (feature 150, Kuwabata): the polder carried to the wholesale
    dike-pond conversion. Asserts what the archetype is responsible for beyond the polder: the
    overlay record, the dike-pond parcels, the declared arrangement, and the waterward fringe
    (declared AND wet, so `polder_waterward_flanks_wet` has teeth rather than skipping)."""
    # THE KUWABATA SPEC, SHARED WITH THE THREE GATE FILES THAT ALREADY ROLL IT (2026-08-31). This test
    # was a spec of its own differing only in leaving `dike_crop` to roll (seed 21 gives sugarcane), and
    # it asserts nothing about the crop. Measured: Kuwabata's map carries every assertion below.
    plan, M = _pool.rolled_map(hg.HamletSpec(name="Kuwabata", seed=21, households=16, down_deg=90, field_archetype="mulberry_dike_fishpond", pond_layout="mosaic", dike_crop="mulberry"))
    m = M["meta"]
    assert m["field_archetype"] == "mulberry_dike_fishpond" and m["pond_layout"] == "mosaic"
    assert any(r["overlay"] == "mulberry_fishpond" and r["count"] >= 20 for r in M["land_use"])
    assert M.get("dikeponds"), "the ponds are recorded as dike-ponds"
    assert 1 <= sum(1 for d in M["dikeponds"] if d.get("kind") == "fry") <= 3, "a few of the smallest parcels are fry nursery ponds (feature 150 A5)"
    assert M.get("pig_sties") and M.get("duck_pens"), "the stock on the ponds (feature 150 A3/A4)"
    assert all(d.get("wet") for d in M["duck_pens"]), "every duck pen fences a wet run into its pond"
    assert plan.placed == plan.spec.households
    assert set(m["waterward"]) and set(m["waterward"]) <= {"N", "E", "S", "W"}
    assert sum(1 for q in M["marshes"] if q.get("role") == "waterside") == len(m["waterward"])
    # no threshing yards on a no-rice hamlet (feature 150 T41, GM 2026-08-28) - declared and drawn so
    assert m["work_yards"] is False and M["threshing_yards"] and all(y.get("kind") == "forecourt" for y in M["threshing_yards"])
