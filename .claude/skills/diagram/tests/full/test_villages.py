"""THE FULL TREE (feature 135, GM 2026-08-27): the pool sweep (the three-roll immunity ratchet was retired by the GM on 2026-09-08, feature 219). Collected by
`make done FULL=1` and the AWS check only - never by `make quick` or `make done` (tests/CLAUDE.md: the directory
decides when a test runs). Helpers stay in `tests.test_villages`, whose cheap tests run in the quick tree."""

import json
import os

import pytest

from tests.test_villages import GENERATORS, _regen_and_gate, _typical_cell_acres


@pytest.mark.rolls_map
@pytest.mark.parametrize("gen", GENERATORS, ids=[os.path.basename(g) for g in GENERATORS])
def test_village_passes_gate(gen):
    assert _regen_and_gate(gen), f"{os.path.basename(gen)} failed the gate"
    svg = gen[: -len(".gen.py")] + ".svg"
    # (THE CHANNEL UNDER A LATER PLOT clause retired with feature 287: the finish lifts every plot under the water block and
    # the comb sends its channels to the late block - `settlement/finish.py`, `fields/comb.py`, unit-tested in
    # `tests/settlement/test_field_guarantees.py`; specs/287-placer-guarantees/research.md R8.)
    # PADDY CELL SIZE stays in the calibrated real-feet band (GM 2026-07-22). Every valley-paddy comb map
    # (all villages + cities) and the two HILL-RICE archetype demos - contour_terraces (Tanada) and
    # ribbon_valley (Yatsuda), whose steps/bands are now split into leveled cells - hold to it; the band
    # spans plot_texture's small_irregular->large_block knobs (~0.036-0.0675) plus slop and, above all,
    # catches a regression back to the old hand-set ~0.13 ac (or the old field-wide terrace/ribbon bands).
    # The polder / dike-pond archetypes are DELIBERATELY larger (Buck's ~1 mu parcels, 0.4-0.6 ha ponds -
    # true-scale per research/settlements.html, the scale entry), so they are excluded, not held to the leveled-cell target.
    # KEPT through feature 287 as the village and city tier's guard: the band is that tier's calibration, a RECORDED DROP on
    # the hamlet path (the hamlet keeps the GM's pixel grain - specs/287-placer-guarantees/research.md R7, water W39), and it
    # becomes a placer guarantee when the village tier converts to scripted generation. It judges no map the pool ships
    # today (all five are hamlets on a valley or dike-pond archetype).
    with open(gen[: -len(".gen.py")] + ".json") as _fh:
        manifest = json.load(_fh)
    meta = manifest.get("meta", {})
    _valley = meta.get("scale") in ("village", "city")
    _hill_rice = meta.get("field_archetype") in ("contour_terraces", "ribbon_valley")
    if _valley or _hill_rice:
        cell = _typical_cell_acres(svg, meta.get("ftpx") or 2)
        assert cell is not None and 0.030 <= cell <= 0.072, (
            f"{os.path.basename(gen)}: typical paddy cell {cell:.3f} ac is outside the calibrated 0.030-0.072 band (see research/fields.html 'Plot sizes, pond sizing and acreage from population')"
        )
