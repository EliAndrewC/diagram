"""THE FULL TREE (feature 135, GM 2026-08-27): the pool sweep and the three-roll immunity ratchet. Collected by
`make done FULL=1` and the AWS check only - never by `make quick` or `make done` (tests/CLAUDE.md: the directory
decides when a test runs). Helpers stay in `tests.test_villages`, whose cheap tests run in the quick tree."""

import json
import os
import runpy

import pytest

from tests.test_villages import GENERATORS, HERE, _channels_under_plots, _regen_and_gate, _typical_cell_acres


@pytest.mark.rolls_map  # three real Kashikawa rolls, 214 s (feature 135 R3) - un-marked until now because it rolls through runpy
def test_a_map_is_immune_to_an_upstream_change_in_the_number_of_random_draws():
    """THE RATCHET for positional/scoped randomness (GM 2026-08-08).

    Generate one map twice - the second time with ONE extra `random.random()` consumed at `meta()`,
    which is what any upstream change that draws differently amounts to - and demand a byte-identical
    manifest. Before the discipline landed this moved 13 of a town's 71 manifest keys, including
    houses, wells, gardens, groves and 2,754 tree crowns; the visible cost was a farm shed drawn on a
    garden 700 px from anything that had changed.

    The subject was a hand-authored TOWN (hoshizora) until the 2026-08-16 legacy freeze, because a
    town exercises both mechanisms at once: position-seeded attributes (a house's rake, its wall
    color, its kura) and scoped phases (ring, pack, frontage, pasture, grove, wells, farmsteads).
    Legacy gens are never run by the suite now, so the subject is a large SCRIPTED hamlet - it
    holds the attribute mechanism and the farmstead/well/grove scopes, but not the urban scopes
    (ring, pack, frontage). When the town tier converts to scripted generation, move the subject
    to a scripted town: a hamlet alone would not have held the original line.
    """
    import random

    from l7r.diagram import settlement

    gen = os.path.join(HERE, "pool", "hamlets", "kashikawa.gen.py")

    def once(perturb):
        orig = settlement.Settlement.meta

        def patched(self, *a, **kw):
            r = orig(self, *a, **kw)
            for _ in range(perturb):
                random.random()
            return r

        settlement.Settlement.meta = patched
        os.environ["DIAGRAM_SKIP_RENDER"] = "1"
        try:
            runpy.run_path(gen, run_name="__main__")
        finally:
            settlement.Settlement.meta = orig
            del os.environ["DIAGRAM_SKIP_RENDER"]
        with open(gen[: -len(".gen.py")] + ".json") as fh:
            return fh.read()

    clean = once(0)
    assert once(1) == clean, "an upstream change in the number of random draws re-rolled the map - see CLAUDE.md 'RANDOMNESS IS POSITIONAL OR SCOPED'"
    assert once(0) == clean  # ...and leave the committed manifest as the unperturbed run wrote it


@pytest.mark.rolls_map
@pytest.mark.parametrize("gen", GENERATORS, ids=[os.path.basename(g) for g in GENERATORS])
def test_village_passes_gate(gen):
    assert _regen_and_gate(gen), f"{os.path.basename(gen)} failed the gate"
    svg = gen[: -len(".gen.py")] + ".svg"
    covered = _channels_under_plots(svg)
    assert not covered, (
        f"{os.path.basename(gen)}: {len(covered)} field channel(s) painted UNDER a later plot at {covered[:5]} - route the comb net through the LATE water block (field_channel late=True; see settlement._water)"
    )
    # PADDY CELL SIZE stays in the calibrated real-feet band (GM 2026-07-22). Every valley-paddy comb map
    # (all villages + cities) and the two HILL-RICE archetype demos - contour_terraces (Tanada) and
    # ribbon_valley (Yatsuda), whose steps/bands are now split into leveled cells - hold to it; the band
    # spans plot_texture's small_irregular->large_block knobs (~0.036-0.0675) plus slop and, above all,
    # catches a regression back to the old hand-set ~0.13 ac (or the old field-wide terrace/ribbon bands).
    # The polder / dike-pond archetypes are DELIBERATELY larger (Buck's ~1 mu parcels, 0.4-0.6 ha ponds -
    # true-scale per settlements.md line ~102), so they are excluded, not held to the leveled-cell target.
    with open(gen[: -len(".gen.py")] + ".json") as _fh:
        manifest = json.load(_fh)
    meta = manifest.get("meta", {})
    _valley = meta.get("scale") in ("village", "city")
    _hill_rice = meta.get("field_archetype") in ("contour_terraces", "ribbon_valley")
    if _valley or _hill_rice:
        cell = _typical_cell_acres(svg, meta.get("ftpx") or 2)
        assert cell is not None and 0.030 <= cell <= 0.072, (
            f"{os.path.basename(gen)}: typical paddy cell {cell:.3f} ac is outside the calibrated 0.030-0.072 band (see settlements.md 'Paddy cell size')"
        )
