"""The check registry (feature 254, D5): every registered check has a red fixture it FIRES on and stays
quiet on every pool sheet of a tier it covers; a declaration names only registered checks; the
shared layer is what every tier gets.

The fixture assertion is the test with teeth: coverage of a check function proves it runs, and only a
recorded red-then-green proves it catches the defect it is for (buildings.md, "Tuning a check").
"""

from __future__ import annotations

import os

import pytest

from l7r.diagram.buildings import types as bt
from l7r.diagram.pipeline import poolmaps
from l7r.diagram.tools import pack_audit as pa
from l7r.diagram.tools.pack_audit import registry as R

SKILL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIX = os.path.join(SKILL, "tests", "fixtures")


def _ctx(path: str) -> R.Context:
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    return R.Context(pa.parse_svg(text), text)


@pytest.mark.parametrize("check", R.CHECKS, ids=[c.name for c in R.CHECKS])
def test_every_check_fires_on_its_red_fixture(check: R.Check) -> None:
    path = os.path.join(FIX, check.fixture)
    assert os.path.isfile(path), f"{check.name}: its red fixture {check.fixture} is missing - a check without one is not merged (spec 254 FR-005)"
    assert check.run(_ctx(path)), f"{check.name} did not fire on {check.fixture}"
    assert check.fix and len(check.fix) > 20, f"{check.name}: a failure names its compliant fix"


# A tier with no pool sheet yet is stood in for by its clean SYNTHETIC sheet, so the quiet-on-a-clean-sheet
# half of the proof is not vacuous before the exemplar lands (feature 254 T12; T17 retires the stand-in when
# the shrine's fixtures are cut from the exemplar).
CLEAN_STANDIN = {"country-shrines": os.path.join(FIX, "shrine-synthetic.svg")}


def _pool_sheets() -> list[tuple[str, str]]:
    out = []
    for b in poolmaps.bundles(trees=(poolmaps.LIVE_TREE,), kinds={"compound"}, skill_dir=SKILL):
        if os.path.isfile(b.path(".svg")):
            out.append((b.tier, b.path(".svg")))
    for tier, path in CLEAN_STANDIN.items():
        if not any(t == tier for t, _ in out):
            out.append((tier, path))
    return out


@pytest.mark.parametrize("check", R.CHECKS, ids=[c.name for c in R.CHECKS])
def test_every_check_passes_the_pool_sheets_of_its_tiers(check: R.Check) -> None:
    """The hand-drawn sheets are present in every checkout; a draft's svg exists only once its gen ran."""
    seen = 0
    for tier, path in _pool_sheets():
        if not check.applies_to(tier):
            continue
        seen += 1
        ctx = _ctx(path)
        assert not check.run(R.Context(ctx.plan, ctx.text, bt.by_tier(tier), pa.read_form(path))), f"{check.name} fires on the shipped sheet {os.path.basename(path)}"
    assert seen, f"{check.name}: no pool sheet of its tiers on disk"


def test_names_are_unique_and_declarations_name_registered_checks() -> None:
    names = [c.name for c in R.CHECKS]
    assert len(set(names)) == len(names)
    for t in bt.load_types():
        unknown = set(t.checks) - set(names)
        assert not unknown, f"{t.tier} declares checks the registry does not have: {sorted(unknown)}"
        for c in R.CHECKS:
            if not c.shared:
                assert c.types, f"{c.name} is per-type but no declaration lists it"
            else:
                assert c.name not in t.checks, f"{c.name} is shared; a declaration need not list it"


def test_checks_for_and_run_checks_follow_the_types() -> None:
    shared = R.checks_for(None)
    assert all(c.shared and c.types is None for c in shared) and len(shared) >= 11
    magi = {c.name for c in R.checks_for("magistracies")}
    assert {"coverage_band", "perimeter_hugging", "two_court_zoning", "notice_board_adrift", "fire_water_adrift"} <= magi
    shrine = {c.name for c in R.checks_for("country-shrines")}
    assert "fire_water_adrift" in shrine and "coverage_band" not in shrine
    assert R.Check("x", lambda ctx: [], False, "f", "fix").applies_to("b") is False and R.Check("x", lambda ctx: [], False, "f", "fix").types == frozenset()
    ctx = _ctx(os.path.join(FIX, "ochiba-no-scale-red.svg"))
    fired = {ch.name for ch, found in R.run_checks(ctx, None) if found}
    assert fired == {"scale_bar_present"}
    assert R.ft(30.0) == 10.0
