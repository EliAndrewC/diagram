"""The `rolls_map` marker must not rot (feature 127).

WHY THIS GUARD EXISTS. `make quick` used to deselect two FILES and announce, in its own output, that
"the map-rolling tests are NOT included". That was false: the three polder tests in
`hamletgen/test_water.py` each roll a hamlet and cost 110 s, 86 s and 63 s, and they ran on every
invocation. `quick` measured 254 SECONDS while every blocked command was being funnelled toward it
as the cheap option - a guard pointing at a fast path that was not fast.

A file list cannot track which tests roll a map: a new one lands in an unlisted file and the target
silently gets slower. A marker travels with the test, and this is what makes the marker true.

IT MATCHES CALLS, NOT TEXT, and that lesson was learned three times in one day. The first version
regex'd the source, so a test whose DOCSTRING mentioned "cohort()'s pool children" was reported as
unmarked. The same defect made the command hook block a grep, a commit message and its own test
harness. Walking the AST for real call nodes cannot make that mistake, because prose is not a call.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

from tests._scope import EXHAUSTIVE

# THE RECEIVER IS PART OF THE SIGNAL, and leaving it out was the fourth instance of this feature's
# recurring mistake. `build` and `generate` are ordinary words: `tests/check_village/` passes a
# callable named `build` as a PARAMETRIZED FIXTURE ARGUMENT, so matching the bare name reported two
# gate tests as un-marked map-rollers. They roll nothing.
#
# So a dotted call must come off the generator module, and only the distinctive bare names count.
ROLLING_ATTRS = frozenset({"build", "generate", "main", "roll_village", "cohort", "gate_obtain", "hamlet", "report"})
ROLLING_RECEIVERS = frozenset({"hg", "hamletgen", "driver", "rollcache"})  # rollcache.hamlet / .report roll on a miss (feature 135)
ROLLING_BARE = frozenset({"roll_village", "cohort", "gate_obtain"})

# ADDED AFTER PROFILING RATHER THAN BY GUESSING, and the two additions were the two most expensive
# tests in the suite: `hg.main([...])` runs the generator through its CLI (24.8 s) and
# `gencache.run_and_record` regenerates a real scripted hamlet (58.5 s). Neither matched the first
# list, so both kept running inside `make quick` while the marker guard reported everything clean.
#
# `run_and_record` and `gencache` were tried here and REMOVED. They caught 20 cache tests that use
# tiny synthetic gens and finish in milliseconds - marking those would have cost `make quick` real
# coverage to save nothing. Only ONE cache test rolls a real map, and it is marked by hand.
#
# THE LESSON, which is why this comment exists: a list of "calls that roll a map" is a GUESS unless
# it is checked against a MEASUREMENT, and the guess errs in both directions. `make durations` is the
# check - and `make quick` now enforces its own time budget, so a slow unmarked test makes the target
# fail rather than quietly making it slower.
TESTS = pathlib.Path(__file__).resolve().parent


# A STUB IS NOT A ROLL (feature 135 T11, GM 2026-08-27). Seven CLI tests `monkeypatch.setattr(hg.driver, "cohort", ...)`
# or `"generate"` and then call `hg.main` / `hg.cohort` - the call is real, the roll is not, and they measure in
# milliseconds. Matching the call alone put them in the gate tree carrying `rolls_map`. So the walk first reads the
# stubs: with `generate` stubbed nothing below it can roll; with `cohort` stubbed, `main`/`cohort` calls roll nothing
# (`build`, `generate`, `roll_village`, `gate_obtain` still do). Both directions are pinned by the unit test below.
_STUBBABLE = frozenset({"cohort", "generate"})
_VIA_COHORT = frozenset({"main", "cohort"})


def _stubbed(node: ast.AST) -> set[str]:
    out: set[str] = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute) and sub.func.attr == "setattr" and len(sub.args) >= 2:
            tgt, name = sub.args[0], sub.args[1]
            on_driver = (isinstance(tgt, ast.Attribute) and tgt.attr == "driver") or (isinstance(tgt, ast.Name) and tgt.id == "driver")
            if on_driver and isinstance(name, ast.Constant) and name.value in _STUBBABLE:
                out.add(str(name.value))
    return out


def _rolls_a_map(node: ast.AST) -> bool:
    """Does this test actually CALL something that generates a settlement - and not a stub of it?"""
    stubs = _stubbed(node)
    if "generate" in stubs:
        return False
    for sub in ast.walk(node):
        if not isinstance(sub, ast.Call):
            continue
        fn = sub.func
        if isinstance(fn, ast.Attribute) and fn.attr in ROLLING_ATTRS:
            if isinstance(fn.value, ast.Name) and fn.value.id in ROLLING_RECEIVERS and not ("cohort" in stubs and fn.attr in _VIA_COHORT):
                return True
        elif isinstance(fn, ast.Name) and fn.id in ROLLING_BARE and not ("cohort" in stubs and fn.id == "cohort"):
            return True
    return False


def test_a_stubbed_generator_is_not_a_roll_and_a_real_one_is() -> None:
    """The guard's two directions (feature 135 T11): the same call, stubbed and not."""

    def fn(src: str) -> ast.AST:
        return next(n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef))

    assert _rolls_a_map(fn("def test_x():\n    hg.main(['--batch', '1'])\n"))
    assert _rolls_a_map(fn("def test_x():\n    hg.cohort(4, first_seed=41, jobs=1)\n"))
    assert not _rolls_a_map(fn("def test_x(monkeypatch):\n    monkeypatch.setattr(hg.driver, 'cohort', lambda n, first_seed=1, jobs=None: [])\n    hg.main(['--batch', '1'])\n"))
    assert not _rolls_a_map(fn("def test_x(monkeypatch):\n    monkeypatch.setattr(hg.driver, 'generate', fake)\n    hg.cohort(3, first_seed=5, jobs=1)\n"))
    # a stubbed cohort does not excuse a direct build
    assert _rolls_a_map(fn("def test_x(monkeypatch):\n    monkeypatch.setattr(hg.driver, 'cohort', lambda n: [])\n    hg.build(plan)\n"))


def test_tiers_markers_name_only_real_tiers() -> None:
    """The `tiers` marker (feature 133 T17) is only useful if its names are the five the conftest knows."""
    import ast
    import re

    bad = []
    for path in sorted(TESTS.glob("**/*.py")):
        for m in re.finditer(r"@pytest\.mark\.tiers\((.*?)\)", path.read_text(encoding="utf-8")):
            names = ast.literal_eval("(" + m.group(1) + ",)")
            if not names or any(n not in ("hamlet", "village", "town", "city", "capital") for n in names):
                bad.append((path.name, m.group(1)))
    assert not bad, f"tiers markers with unknown or empty tier names: {bad}"


def test_the_tier_option_deselects_only_tests_tagged_for_other_tiers(pytester) -> None:  # type: ignore[no-untyped-def]
    """Fire-proof for the conftest hook: under --tier hamlet, a city-only test is deselected, a
    hamlet-inclusive one and an untagged one run; without --tier all three run."""
    pytester.makeconftest(
        (TESTS / "conftest.py").read_text(encoding="utf-8").split("pytest_plugins")[0] + "\n" + (TESTS / "conftest.py").read_text(encoding="utf-8").split('pytest_plugins = ["pytester"]')[1]
    )
    pytester.makeini("[pytest]\nmarkers =\n    tiers(*names): tiers\n")
    pytester.makepyfile(
        """
        import pytest
        @pytest.mark.tiers("city", "town")
        def test_city_only(): pass
        @pytest.mark.tiers("hamlet", "village")
        def test_lane_tiers(): pass
        def test_untagged(): pass
        """
    )
    r = pytester.runpytest_inprocess("-p", "no:cacheprovider", "--tier", "hamlet", "-q")
    r.assert_outcomes(passed=2, deselected=1)
    r = pytester.runpytest_inprocess("-p", "no:cacheprovider", "-q")
    r.assert_outcomes(passed=3)


@pytest.mark.skipif(
    not EXHAUSTIVE, reason="a whole-tree source scan (~1 s) that guards a roster, not a map; under EXHAUSTIVE=1 and at the gate (GM 2026-08-26, T21) - last exhaustive green 2026-08-26"
)
def test_every_map_rolling_test_carries_the_rolls_map_marker() -> None:
    missing: list[str] = []
    for p in sorted(TESTS.rglob("test_*.py")):
        tree = ast.parse(p.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef) or not node.name.startswith("test_"):
                continue
            if not _rolls_a_map(node):
                continue
            decorated = {d.attr for dec in node.decorator_list for d in ast.walk(dec) if isinstance(d, ast.Attribute)}
            if "rolls_map" not in decorated:
                missing.append(f"{p.relative_to(TESTS)}::{node.name}")
    assert not missing, "these tests generate a settlement but carry no @pytest.mark.rolls_map, so `make quick` would run them and get slower without saying so:\n  " + "\n  ".join(missing)
