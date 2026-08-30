"""The derived per-suite dependency set (feature 172).

The failure mode that matters here is UNDER-running: a derivation that misses a dependency skips a
suite a change has broken, and reports green. Over-running is merely slow. Every assertion below is
written in that direction.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

SCRIPTS = pathlib.Path(__file__).resolve().parents[5] / "scripts"
_spec = importlib.util.spec_from_file_location("_hookdeps", SCRIPTS / "_hookdeps.py")
assert _spec and _spec.loader
hookdeps = importlib.util.module_from_spec(_spec)
sys.modules["_hookdeps"] = hookdeps
_spec.loader.exec_module(hookdeps)


def test_a_dependency_reached_only_through_another_helper_still_counts() -> None:
    """THE WHOLE SUBTLETY OF THIS FEATURE.

    `readme-hooks.sh` names `_guardlog.sh` and never names the matcher. But `_guardlog.sh`'s
    `escape_or_refuse` calls it (feature 170), so a change to the escape family CAN break the readme
    suite. A direct-reference derivation would skip it and report green.
    """
    deps = hookdeps.deps_for("readme-hooks.sh")
    assert "_guardlog.sh" in deps, "the direct reference"
    assert "_hm_escape.py" in deps, (
        "reached only THROUGH _guardlog.sh - a direct-only derivation under-runs here, which is the "
        "one failure mode worse than the over-running this feature replaces"
    )
    assert "_hm_shape.py" in deps, "and one hop further: the escape family stands on the shape primitives"


def test_every_suite_depends_on_its_own_guard_and_its_own_test() -> None:
    """The floor. A suite that did not depend on its own two files would never re-run at all."""
    for guard in sorted(p.name for p in SCRIPTS.glob("*-hooks.sh") if not p.name.startswith("test-")):
        deps = hookdeps.deps_for(guard)
        assert guard in deps, f"{guard} does not depend on itself"
        assert f"test-{guard}" in deps, f"{guard}'s suite does not depend on its own test file"


def test_the_orchestrating_three_still_depend_on_everything() -> None:
    """`sync-with-main.sh`, `review-gate.sh` and `gate-stamp.py` drive the other scripts, so any script
    is an input to what their suites assert. Feature 135's judgment, deliberately unchanged - the
    refinement must not "optimize" these into missing a real dependency."""
    for guard in ("sync-with-main.sh", "review-gate.sh", "gate-stamp.py"):
        deps = hookdeps.deps_for(guard)
        assert len(deps) > 20, f"{guard} should depend on the whole script tree, got {len(deps)}"
        assert "_hookmatch.py" in deps and "_guardlog.sh" in deps


def test_the_refinement_actually_narrows_the_two_helpers_it_was_built_for() -> None:
    """SC-002. `_gatecost.py` is referenced by two guards and `test_hooks_cases.py` by three suites;
    before this feature both re-ran all 21. If these numbers grow, the win has been lost and somebody
    should know why."""
    guards = sorted(p.name for p in SCRIPTS.glob("*-hooks.sh") if not p.name.startswith("test-"))
    gatecost = [g for g in guards if "_gatecost.py" in hookdeps.deps_for(g)]
    cases = [g for g in guards if "test_hooks_cases.py" in hookdeps.deps_for(g)]
    assert len(gatecost) <= 4, f"_gatecost.py's blast radius grew to {gatecost}"
    assert len(cases) <= 5, f"test_hooks_cases.py's blast radius grew to {cases}"


def test_the_helpers_that_churn_are_NOT_narrowed_and_that_is_correct() -> None:
    """The disappointment, asserted so it is not mistaken for a bug later.

    The ESCAPE family and `_guardlog.sh` are genuinely used by nearly every guard - every guard reaches
    its escape through them - so their derived sets stay near the total however the files are cut. A
    future change that made these numbers SMALL would almost certainly be a derivation that had stopped
    following the graph, which is why this asserts a FLOOR rather than a ceiling.

    Note what the split did and did not do: `_hm_make.py` and `_hm_shape.py` are down to 3 guards each,
    and `_hookmatch.py` itself is down to 2 because guards call the leaves - but the escape family is
    exactly as wide as it was, and that is correct rather than a miss.
    """
    guards = sorted(p.name for p in SCRIPTS.glob("*-hooks.sh") if not p.name.startswith("test-"))
    matcher = [g for g in guards if "_hm_escape.py" in hookdeps.deps_for(g)]
    logging = [g for g in guards if "_guardlog.sh" in hookdeps.deps_for(g)]
    assert len(matcher) >= len(guards) - 3, f"only {len(matcher)} guards depend on the matcher - has the derivation stopped following references?"
    assert len(logging) >= len(guards) - 3, f"only {len(logging)} guards depend on _guardlog.sh - same question"


def test_the_key_changes_when_a_dependency_changes(tmp_path, monkeypatch) -> None:
    """A freshness key that did not move when an input moved would skip a suite forever."""
    before = hookdeps.key_for("readme-hooks.sh")
    real = hookdeps._text

    def fake(name: str) -> str:
        # NOT a `#` comment: the deriver strips those now, so a comment-shaped change would correctly
        # leave the key alone and this test would be asserting nothing.
        return real(name) + ("\nECHO_CHANGED=1\n" if name == "_hm_escape.py" else "")

    monkeypatch.setattr(hookdeps, "_text", fake)
    assert hookdeps.key_for("readme-hooks.sh") != before, (
        "the key ignored a change to a transitive dependency"
    )


def test_every_shared_helper_on_disk_is_known_to_the_deriver() -> None:
    """A NEW LEAF MUST NOT BE INVISIBLE (round 2 of this feature's review, and it had already happened).

    The first implementation propagated a hardcoded five-name roster. This feature's own split then
    added three leaves it did not know, so a guard calling a leaf directly would have re-run ZERO
    suites when that leaf changed - the under-run FR-001 calls the whole subtlety, produced by the
    feature that exists to prevent it.
    """
    on_disk = {p.name for p in SCRIPTS.glob("_*.py")} | {p.name for p in SCRIPTS.glob("_*.sh")}
    missing = on_disk - set(hookdeps._SHARED)
    assert not missing, f"shared helpers the deriver cannot see: {sorted(missing)}"


def test_a_filename_in_prose_is_not_a_dependency() -> None:
    """The mention-versus-invocation rule, applied to the deriver itself.

    `make-only-hooks.sh` says "detection lives in _hookmatch.py" in a comment and INVOKES `_hm_make.py`.
    Before comments and docstrings were stripped, every guard depended on every leaf and the split
    delivered nothing three times over (research.md R4).
    """
    code = hookdeps._code("make-only-hooks.sh")
    assert "_hm_make.py" in code, "the invocation must survive stripping"
    guards = sorted(p.name for p in SCRIPTS.glob("*-hooks.sh") if not p.name.startswith("test-"))
    make_family = [g for g in guards if "_hm_make.py" in hookdeps.deps_for(g)]
    assert len(make_family) <= 5, (
        f"the make/rewrite family should reach a handful of guards, not {len(make_family)} - "
        "has a mention started counting as a dependency again?"
    )


def test_gate_stamp_derives_to_the_whole_tree_from_the_code_not_the_prose() -> None:
    """Round 2: the glob must be matched as the CODE writes it. `gate-stamp.py`'s docstring mentions
    `scripts/*.sh`; the line that globs is `("scripts", ("*.sh", "*.py"))`. Matching the prose made the
    row true by accident, and a reword would have silently narrowed it."""
    assert len(hookdeps.deps_for("gate-stamp.py")) > 20
    assert hookdeps._globs_tree("gate-stamp.py")
