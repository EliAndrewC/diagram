"""THE SWEEP (feature 254, spec FR-004): every Mode A sheet in the live pool, through every registered
check that applies to its declared type - the shared layer and the type's own.

WHY IT IS HERE AND NOT IN `gate/`. It parses a few small SVGs: milliseconds, no roll, no tooling, so
by `tests/CLAUDE.md`'s rule it is a quick-tree test and `make quick` sweeps the pool on every change -
which is what the GM asked for when they said a hand-authored diagram should still have "automated
checks that we run on them". Before this test the audit ran only when a session remembered to run it,
and the pool had never been swept: the drafts had no scale bar and drew their walls where the checks
could not read them, and one hand-drawn sheet sat below a band the record itself called "in-band".

A failure names the sheet, the check and the compliant fix, in that order, because that is what the
session fixing it needs first. A sheet whose tier has no declaration is NOT swept silently: the pool
classifier's ratchet in `test_villages.py` refuses it as `unknown` first.
"""

from __future__ import annotations

import os
import subprocess
import sys

import pytest

from l7r.diagram.buildings import types as bt
from l7r.diagram.pipeline import poolmaps
from l7r.diagram.tools import pack_audit as pa
from l7r.diagram.tools.pack_audit import registry as R

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _sheet(b: poolmaps.MapBundle) -> str:
    """The bundle's svg, generating a declared generated exception's when it is absent (a fresh
    checkout has none: a draft's svg is gitignored, and its gen writes it in a fraction of a second)."""
    svg = b.path(".svg")
    btype = bt.by_tier(b.tier)
    if not os.path.isfile(svg) and btype is not None and b.stem in btype.generated_exceptions:
        subprocess.run([sys.executable, b.gen], check=True, env={**os.environ, "DIAGRAM_SKIP_RENDER": "1"}, cwd=SKILL)
    return svg


def _bundles() -> list[poolmaps.MapBundle]:
    return [b for b in poolmaps.bundles(trees=(poolmaps.LIVE_TREE,), kinds={"compound"}, skill_dir=SKILL) if b.tier in bt.tiers()]


@pytest.mark.parametrize("bundle", _bundles(), ids=lambda b: b.stem)
def test_every_mode_a_sheet_passes_its_checks(bundle: poolmaps.MapBundle) -> None:
    svg = _sheet(bundle)
    assert os.path.isfile(svg), f"{bundle.tier}/{bundle.stem}: no svg on disk and it is not a declared generated exception"
    with open(svg, encoding="utf-8") as fh:
        text = fh.read()
    ctx = R.Context(pa.parse_svg(text), text, bt.by_tier(bundle.tier), pa.read_form(svg))
    failures = [f"{bundle.stem}: {ch.name}: {f} - fix: {ch.fix}" for ch, found in R.run_checks(ctx, bundle.tier) for f in found]
    assert not failures, "\n".join(failures)


def test_the_sweep_covers_every_declared_tier_that_has_a_sheet() -> None:
    """A declared tier with a folder is swept; a declared tier with no folder yet is the exemplar's to fill."""
    swept = {b.tier for b in _bundles()}
    live = os.path.join(SKILL, "pool")
    for tier in bt.tiers():
        if os.path.isdir(os.path.join(live, tier)):
            assert tier in swept, f"{tier} has a pool folder but no bundle reached the sweep"
    assert "magistracies" in swept
