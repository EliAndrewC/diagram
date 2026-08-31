"""The hill-rice field engines (`waterfields/hill.py`) - contour terraces and the ribbon valley.

WHY THIS FILE EXISTS (feature 174). These two builders had NO test and 7% coverage, and this session
first called them dead code. That was wrong: `legacy-hand-authored-pool/hamlets/tanada` calls
`build_terraces` and `.../yatsuda` calls `build_ribbon`, and `migration-plan.md` lists both
archetypes as "NOT STARTED | engine builder exists" - they are pending conversion work with two
frozen exhibit maps demonstrating them. The spec then proposed asking the GM whether to cover or
exempt them; `spec-fidelity` round 2 ruled that the request forecloses a carve-out and 99 statements
of unit tests are cheap, so they are covered like any other engine module.

The calls below are the frozen exhibits' own, verbatim, so these tests exercise the builders exactly
as the two maps that depend on them do.
"""

from __future__ import annotations

import pytest

from l7r.diagram.waterfields.hill import build_ribbon, build_terraces
from l7r.diagram.waterfields.palette import PADDY_CELL_ACRES

TOP = (1000.0, 200.0)
SEED = 7


def _terraces(**kw):
    """Tanada's own call (tanada.gen.py:35), shrunk only where a test says so."""
    args = dict(down_deg=90, n_terraces=32, cross_width=760, fall=1400, ftpx=1)
    return build_terraces(2000, 2000, TOP, SEED, **{**args, **kw})


def _ribbon(**kw):
    """Yatsuda's own call (yatsuda.gen.py:38)."""
    args = dict(down_deg=90, length=1400, width=300, n_bands=48, ftpx=1)
    return build_ribbon(2000, 2000, TOP, SEED, **{**args, **kw})


def test_a_terrace_STEP_is_split_along_the_contour_into_many_small_cells() -> None:
    """THE LEVELED-CELL PRINCIPLE, and the defect it fixed (GM 2026-07-22, settlements/fields.md).

    Both engines used to draw each terrace STEP as ONE plot spanning the full width - ~1.4 acres,
    far over the leveled-cell size a paddy can hold water at. Each step is split ALONG the contour
    now, so a step reads as a ROW of small paddies rather than one band.

    Asserted as the RULE rather than a count: there are many more plots than terraces, which is only
    true if each step was split.
    """
    net = _terraces()
    assert len(net["plots"]) > 32 * 4, f"32 steps split along the contour, not 32 bands: {len(net['plots'])} plots"
    assert net["acres"] > 0
    per_cell = net["acres"] / len(net["plots"])
    assert per_cell < 1.0, f"a leveled cell, not a field-wide band ({per_cell:.2f} ac)"


def test_a_ribbon_valley_is_LONG_AND_NARROW_which_is_what_makes_it_that_archetype() -> None:
    """Its own grounding: "a long, NARROW paddy strung along a MEANDERING valley floor, the field
    archetype for a confined valley where the flat ground is only a thin winding ribbon beside the
    brook". The retired validator was named `ribbon_is_long_and_narrow` and read the OUTLINE, so the
    cell split stayed transparent to it - the same quantity is asserted here."""
    net = _ribbon()
    xs = [p[0] for p in net["envelope"]]
    ys = [p[1] for p in net["envelope"]]
    span_along, span_across = max(ys) - min(ys), max(xs) - min(xs)
    assert span_along > span_across * 1.5, f"long down the valley, narrow across it ({span_along:.0f} x {span_across:.0f})"
    assert len(net["plots"]) > 48, "and the bands are split ACROSS the valley into cells, not left as sheets"


def test_both_engines_carry_the_water_a_hill_field_needs() -> None:
    """A paddy that cannot be filled or drained is not a paddy. Both return build_comb-compatible
    keys, and both owe the same three: a supply channel, a drain, and the brook the valley runs on."""
    for name, net in (("terraces", _terraces()), ("ribbon", _ribbon())):
        assert net["channels"], f"{name}: a supply channel cascades terrace-to-terrace"
        assert net["drain"], f"{name}: and a foot drain takes the water away"
        assert net["plots"] and net["envelope"], f"{name}: with a field to serve"


def test_the_cell_size_is_TUNABLE_and_smaller_cells_mean_more_of_them() -> None:
    """`cell_acres` defaults to `PADDY_CELL_ACRES`. Asserted by moving it: a smaller leveled cell
    must yield MORE plots over the same ground, which a hard-coded split would not do."""
    assert PADDY_CELL_ACRES == 0.05
    coarse = _terraces(cell_acres=0.20)
    fine = _terraces(cell_acres=0.02)
    assert len(fine["plots"]) > len(coarse["plots"]), "a finer cell splits the same hillside further"
    assert coarse["acres"] == pytest.approx(fine["acres"], rel=0.05), "the hillside itself is the same size either way"


def test_the_fall_direction_turns_the_whole_field() -> None:
    """`down_deg` is which way the hill falls. Turning it must turn the field, or the archetype
    could only ever be drawn on a north-facing slope."""
    south = _terraces(down_deg=90)
    east = _terraces(down_deg=0)
    sx = [p[0] for p in south["envelope"]]
    ex = [p[0] for p in east["envelope"]]
    assert (max(ex) - min(ex)) != (max(sx) - min(sx)), "the field's extent follows the fall it was given"
