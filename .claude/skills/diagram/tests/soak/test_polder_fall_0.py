"""THE POLDER GRID, in the tier ABOVE the gate (feature 219, GM 2026-09-08; moved from tests/gate/).

Polder seed 12 was the gate's last roll of its own. Its three engine lines are unit tests now (`tests/hamletgen/
test_water.py`: the reservoir walk, the dike gaps at channels, `fit_polder`'s stop) and its five machinery lines are
tested on stubs, so under constitution VI the roll belongs here, where `make soak` makes it and no ordinary run does.
What these assert is BEHAVIOR on a real polder: the reservoir walking clear of the crop on the one seed that needs it,
the grid solved to its acreage with every household seated and the perimeter dike gated, the keep-outs containing what
they stand for, the lanes bending like paths, and the ratchet's seating and acreage. The pool ships no polder-grid map,
so until this tier runs these are proved by nothing - stated to the GM at the feature's landing.

SERVED FROM THE ROLL CACHE (feature 135): nothing here patches the engine, so `rollcache.hamlet` serves the plan and
finished manifest while every function the roll executed is unchanged, and rolls for real the moment one moves."""

import math

import pytest

from l7r.diagram.settlement import point_in_poly
from tests import rolls
from tests.gate import _pool
from tests.gate.test_cohort_lane_rules import _kinks


@pytest.mark.rolls_map
def test_a_polder_reservoir_backs_off_until_its_rim_clears_the_crop() -> None:
    """The seat is measured from the ring canal's HEAD, so anything that moves that head moves the
    reservoir - trimming the ring's doubling-back stub did exactly that and slid the pond onto the
    crop. A fixed stand-off from a moving anchor is the pinned-constant mistake in miniature, so the
    rim is tested and the pond walks uphill until it is clear.

    Seed 12 is chosen because it NEEDS the walk (one step at falls 0 and 180); seeds 3, 8, 19 and 22
    clear on the first try, so testing one of those would exercise nothing."""
    plan, M = _pool.rolled_map(rolls.POLDER_FALL_0)
    pond = M.get("pond")
    assert pond, "the polder's water source is its header reservoir"
    rim = [(pond[0] + pond[2] * math.cos(a), pond[1] + pond[3] * math.sin(a)) for a in (k * math.pi / 8 for k in range(16))]
    assert not any(point_in_poly(q[0], q[1], list(plan.envelope)) for q in rim), "no part of the rim may lie on the crop"
    # ...and it stays UPHILL of the field, which is the rule the walk must not trade away
    dx, dy = plan.fall
    assert pond[0] * dx + pond[1] * dy < min(p[0] * dx + p[1] * dy for p in plan.envelope), "the source sits above what it waters"


@pytest.mark.rolls_map
def test_a_polder_hamlet_draws_its_grid_dike_and_reservoir() -> None:
    """THE SECOND FIELD ARCHETYPE (GM 2026-08-13), pinned at what it currently guarantees.

    The polder is WORK IN PROGRESS - it has two named gate failures in `build_polder`'s own geometry
    (see hamletgen.md) - so this does not assert a clean gate, which would be a lie. It asserts the
    things the substrate is already responsible for and which no other test covers: that the grid is
    solved to the acreage the households imply, that every household is seated, that the defining
    perimeter dike exists, and that the header reservoir sits OUTSIDE the crop rather than in it,
    which two earlier versions of the siting got wrong in two different ways.

    SEED 19, SHARED WITH THE KEEP-OUT TEST BELOW (2026-08-31, GM: *"do there exist two or more hamlets
    ... which could be combined into a single hamlet while exercising all of the branches that all of
    the tests need"*). This test was rolled on seed 8 and asserts only what EVERY polder owes - the
    archetype declared, the grid solved to the acreage, every household seated, the perimeter dike, a
    gate at every cut, the reservoir outside the crop. None of that names a seed, so it does not need
    one of its own. Measured before the change: seed 19 carries all of these assertions, and seed 8 was
    the most expensive polder in the suite at 39.8 s.

    WHY SEED 12 BELOW IS NOT ALSO FOLDED IN, though it passes these same assertions: its value is that
    it NEEDS the reservoir walk, and an assertion that passes because the pond never had to move looks
    identical to one that passes because the walk worked. Merging on assertions alone would have made
    that test vacuous - the exact failure `tests/CLAUDE.md` warns about."""
    plan, M = _pool.rolled_map(rolls.POLDER_FALL_0)  # Polder 12 since feature 216: seed 19 reached no line of its own (215 R1), and these assertions hold on either
    assert plan.field_archetype == "polder_grid"
    assert M["meta"]["field_archetype"] == "polder_grid"
    assert abs(plan.acres - plan.target_acres) / plan.target_acres < 0.12, f"{plan.acres:.1f} acres against a {plan.target_acres:.1f} target"
    assert plan.placed == plan.spec.households
    assert M.get("dikes"), "a polder without its perimeter dike is not a polder"
    assert len(M.get("sluice_gates") or []) == len(M["dikes"][0]["gaps"]) >= 2, "a gate at every cut of the dike (feature 150 A7)"
    pond = M.get("pond")
    assert pond, "the header reservoir is the polder's water source"
    assert not point_in_poly(pond[0], pond[1], list(plan.envelope)), "the reservoir sits BESIDE the crop, never in it"


@pytest.mark.rolls_map
def test_the_polders_keep_outs_contain_what_they_stand_for() -> None:
    """Feature 139 on REAL geometry: the dike's few-chord keep-out contains every vertex of the drawn band, the
    field's facing chains never accept a point the outline refuses, and the counts are the GM's - a couple of
    dozen chords around the ring dike, under ten on the field's house side."""
    from l7r.diagram.settlement._geom.primitives import chain_violated

    _plan, M = _pool.rolled_map(rolls.POLDER_FALL_0)  # Polder 12 since feature 216: seed 19 reached no line of its own (215 R1), and these assertions hold on either
    dk = M["dikes"][0]
    assert dk["keepout_chords"] <= 24 and len(dk["keepout"]) <= 50  # the chord count is the GM's number; the vertex cap is its consequence - measured 48 on seed 19, 50 on seed 12 (feature 216)
    outside = [(x, y) for x, y in dk["outline"] if not point_in_poly(x, y, dk["keepout"])]
    assert not outside, f"{len(outside)} of {len(dk['outline'])} band vertices outside the keep-out, e.g. {outside[:3]}"
    fld = M["fields"][0]
    chains = [[((a[0], a[1]), (b[0], b[1]), (nv[0], nv[1])) for a, b, nv in ch] for ch in M["field_chains"]]
    assert 1 <= fld["keepout_chords"] <= 12 and chains
    from l7r.diagram.settlement._geom.primitives import FIELD_KEEPOUT_EPS, chain_distance

    assert all(
        chain_violated(x, y, chains, FIELD_KEEPOUT_EPS + 1e-6) for x, y in fld["outline"] if chain_distance(x, y, chains) <= FIELD_KEEPOUT_EPS + 1e-6
    )  # no vertex the chain reaches is on the house side


@pytest.mark.rolls_map
def test_the_polder_s_lanes_bend_like_paths() -> None:
    """The lane rules on the polder - the `Polder-12` member of the gate's cohort test until feature 219."""
    _plan, M = _pool.rolled_map(rolls.POLDER_FALL_0)
    assert M.get("lanes"), "the polder drew no lane, so this rule would judge nothing"
    assert not _kinks(M), _kinks(M)


@pytest.mark.rolls_map
def test_the_polder_seats_its_households_and_lands_its_acreage() -> None:
    """The ratchet's two unconditional claims on the polder (its member of `test_a_rolled_cohort_passes_the_whole_gate`
    until feature 219): the declared households are seated and the paddy acreage lands near the figure they imply."""
    report = _pool.rolled_report(rolls.POLDER_FALL_0)
    assert report.plan.placed >= round(0.85 * report.plan.spec.households), f"seated {report.plan.placed}/{report.plan.spec.households}"
    assert abs(report.plan.acres - report.plan.target_acres) / report.plan.target_acres < 0.15, f"{report.plan.acres:.1f} acres against {report.plan.target_acres:.1f}"
