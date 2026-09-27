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

import pytest

from l7r.diagram.buildings import types as bt
from l7r.diagram.pipeline import poolmaps
from l7r.diagram.tools import pack_audit as pa
from l7r.diagram.tools.pack_audit import registry as R
from tests import _sheets

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _sheet(b: poolmaps.MapBundle) -> str:
    """The bundle's svg, a declared generated exception's regenerated when it is absent OR stale (`tests/_sheets.py`:
    a draft's svg is gitignored, and a copy older than the engine once failed here as if it were a regression)."""
    btype = bt.by_tier(b.tier)
    return _sheets.fresh(b.path(".svg"), b.gen, btype is not None and b.stem in btype.generated_exceptions)


def _bundles() -> list[poolmaps.MapBundle]:
    return [b for b in poolmaps.bundles(trees=(poolmaps.LIVE_TREE,), kinds={"compound"}, skill_dir=SKILL) if b.tier in bt.tiers()]


@pytest.mark.parametrize("bundle", _bundles(), ids=lambda b: b.stem)
def test_every_mode_a_sheet_passes_its_checks(bundle: poolmaps.MapBundle) -> None:
    svg = _sheet(bundle)
    assert os.path.isfile(svg), f"{bundle.tier}/{bundle.stem}: no svg on disk and it is not a declared generated exception"
    with open(svg, encoding="utf-8") as fh:
        text = fh.read()
    ctx = R.Context(pa.parse_svg(text), text, bt.by_tier(bundle.tier), pa.read_form(svg), pa.read_on_map(svg))
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


def test_a_generated_sheet_is_regenerated_when_missing_or_stale_and_a_hand_drawn_one_never(tmp_path) -> None:
    """The stale-copy failure of 2026-09-26: a sheet older than its generator or the engine is written again."""
    svg, gen = tmp_path / "a.svg", tmp_path / "a.gen.py"
    gen.write_text("", encoding="utf-8")
    ran: list[list[str]] = []

    def run(cmd: list[str], **_kw: object) -> None:
        ran.append(cmd)
        svg.write_text("<svg/>", encoding="utf-8")

    assert _sheets.fresh(str(svg), str(gen), False, 0.0, run) == str(svg) and ran == [], "hand-drawn: never run"
    _sheets.fresh(str(svg), str(gen), True, 0.0, run)
    assert len(ran) == 1 and ran[0][-1] == str(gen), "missing: generated"
    _sheets.fresh(str(svg), str(gen), True, 0.0, run)
    assert len(ran) == 1, "fresh: left alone"
    os.utime(svg, (1, 1))
    _sheets.fresh(str(svg), str(gen), True, 0.0, run)
    assert len(ran) == 2, "older than its generator: generated again"
    assert _sheets.is_stale(str(svg), str(gen), os.path.getmtime(svg) + 10), "older than the engine is stale"
    assert _sheets.newest_engine_mtime() > 0
