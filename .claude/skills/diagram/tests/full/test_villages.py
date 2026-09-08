"""THE FULL TREE (feature 135, GM 2026-08-27): the pool sweep and the three-roll immunity ratchet. Collected by
`make done FULL=1` and the AWS check only - never by `make quick` or `make done` (tests/CLAUDE.md: the directory
decides when a test runs). Helpers stay in `tests.test_villages`, whose cheap tests run in the quick tree."""

import json
import os

import pytest

from l7r.diagram.pipeline import rollcache
from tests import rolls
from tests.gate import _pool
from tests.test_villages import GENERATORS, _channels_under_plots, _regen_and_gate, _typical_cell_acres


@pytest.mark.rolls_map  # ONE real roll: the reference PERTURBED, in a child (feature 215); the clean side is the pool's committed manifest
def test_a_map_is_immune_to_an_upstream_change_in_the_number_of_random_draws():
    """THE RATCHET for positional/scoped randomness (GM 2026-08-08).

    Generate one map twice - the second time with ONE extra `random.random()` consumed at `meta()`,
    which is what any upstream change that draws differently amounts to - and demand a byte-identical
    manifest. Before the discipline landed this moved 13 of a town's 71 manifest keys, including
    houses, wells, gardens, groves and 2,754 tree crowns; the visible cost was a farm shed drawn on a
    garden 700 px from anything that had changed.

    THE SUBJECT IS THE REFERENCE (feature 215, D5 - reversing 214's D3). It was a hand-authored TOWN until the
    2026-08-16 legacy freeze, then the largest scripted hamlet (Kashikawa: 20 households, fall 315, the off-map
    sink) for the mechanisms a large map exercises. The GM asked for the roster at the packing record's floor,
    and Kashikawa was a spec that existed only to be perturbed; the reference holds the same mechanisms -
    position-seeded attributes, the farmstead, well and grove scopes - on the map every gate test reads. What
    this no longer proves, stated (spec FR-006 c): the immunity of the off-map sink and fall-315 stages, which
    the pool sweep's Kashikawa child still covers but no longer perturbs. When the town tier converts to
    scripted generation, move the subject to a scripted town.

    THE CLEAN SIDE IS THE POOL'S COMMITTED MANIFEST - the GM's own statement of the rule (2026-08-30): "we are
    essentially using a cache, but we are building the cache as part of the test run in order to ensure that
    the process that builds the cache is part of what's being tested." The sweep rolls it cold in its coverage
    child and serves it warm; either way it is a clean roll of exactly this code. The PERTURBED side is the
    experiment and is never served: a child roll of the reference with the extra draw applied inside it
    (`rollcache._perturbed_manifest`), the one roll of the reference a gate makes."""
    clean_path = _pool.obtain(_pool.gen_of(rolls.REFERENCE))
    with open(clean_path, encoding="utf-8") as fh:
        clean = json.load(fh)
    perturbed, _deps = rollcache._in_child("l7r.diagram.pipeline.rollcache:_perturbed_manifest", rolls.REFERENCE)
    assert json.dumps(perturbed, sort_keys=True) == json.dumps(clean, sort_keys=True), (
        "an upstream change in the number of random draws re-rolled the map - see CLAUDE.md 'RANDOMNESS IS POSITIONAL OR SCOPED'. "
        "(The clean side is the pool's committed manifest through the gen cache; if you believe it is merely STALE rather than the draw "
        "order wrong, re-run with GATE_NO_CACHE=1, which forces the sweep to roll it for real.)"
    )


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
