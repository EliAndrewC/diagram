"""The 100% coverage floor is enforced ON `make done` ITSELF (feature 174).

GM 2026-08-31: *"we want to enforce one hundred percent coverage in whatever the relevant place is
... so that in the future, we literally cannot complete our make done in order to merge back into
main, and there will no longer be any mechanism by which this can be accomplished."*

The floor itself is proved by the gate every time it runs - that is what a floor IS. What needs its
own test is the WIRING, because the wiring is what a later edit can quietly undo: the phase list, the
switch that turns the floors on, and the stamp key that stops a record taken under the old standard
from satisfying a push under the new one. Each of these was, before this feature, exactly one word
away from letting a merge through below the floor.

`tooling`, because it reads the real Makefile and the real guard script.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.tooling

SKILL = Path(__file__).resolve().parents[2]
MAKEFILE = (SKILL / "Makefile").read_text(encoding="utf-8")


def _done_recipe() -> str:
    """The `done` target's recipe, from `done:` to the next target at column 0."""
    start = re.search(r"^done:", MAKEFILE, re.M)
    assert start, "the Makefile has a `done` target"
    rest = MAKEFILE[start.end() :]
    end = re.search(r"^[A-Za-z0-9_.-]+:", rest, re.M)
    return rest[: end.start()] if end else rest


def test_a_plain_make_done_runs_the_FLOORED_test_phase_on_both_branches() -> None:
    """The floors live behind `COV_FLOORS=1`, which is also the switch that turns every deselection
    off - and a deselected test takes its coverage with it, so there is no arrangement that holds a
    100% floor over a partial suite. That is why the phase is `test-full` whether or not FULL is set,
    and why a phase list that reverts to a bare `test` on the plain branch is the regression this
    guards: it would restore the *"coverage floors: deferred"* path the GM's request abolished."""
    phases = re.search(r"for phase in (.+?); do", _done_recipe())
    assert phases, "the gate runs a phase loop"
    line = phases.group(1)
    assert "test-full" in line, f"the floored phase runs on the plain branch too: {line}"
    assert not re.search(r"\btest\b(?!-full)", line.replace("hooks-test", "")), f"and the unfloored `test` phase is NOT in the list: {line}"
    assert "$(if $(FULL),perf-gate,)" in line, f"FULL adds the perf bookends, which is what still distinguishes it: {line}"


def test_COV_FLOORS_stays_OFF_by_default_because_make_quick_was_exempted() -> None:
    """The GM exempted the cheap loop in the same request (*"I don't think we need to do this for our
    make quick"*), and `quick` reaches `test` directly. So the switch is off by default and the gate
    turns it on, rather than the default moving and `quick` having to turn it back off."""
    assert re.search(r"^COV_FLOORS =\s*$", MAKEFILE, re.M), "COV_FLOORS is empty by default"


def test_the_floor_phase_asks_coverage_for_ONE_HUNDRED_and_reports_every_floor_together() -> None:
    """`--fail-under=100` is the number the GM asked for, in the place it is read. The three floors
    also still report TOGETHER (feature 145): a first floor that `exit 1`s hides every floor after
    it, which once made the hamlet floor unreachable for a day."""
    assert "--fail-under=100" in MAKEFILE, "the global floor is 100, not a ratchet"
    assert MAKEFILE.count("cov_ec=1") >= 3, "each floor records its own failure instead of exiting"
    assert "exit $$cov_ec" in MAKEFILE, "and the phase exits non-zero once, at the end"


def test_the_gates_own_STANDARD_is_part_of_the_stamp_key() -> None:
    """A stamp says "the gate has seen exactly this code and passed", and `sync-with-main.sh --check`
    is the whole of what the push demands. Every stamp written before this feature certifies a run
    that was ALLOWED to finish below the floor, so the key has to move when the standard does -
    otherwise the first push after the change rides a record of the old one."""
    import importlib.util

    path = SKILL.parents[2] / "scripts" / "gate-stamp.py"
    spec = importlib.util.spec_from_file_location("_gate_stamp_under_test", path)
    assert spec and spec.loader
    gs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gs)

    assert gs.GATE_RECIPE, "there is a recipe string to key on"
    before = gs.hash_files([path])
    gs.GATE_RECIPE = gs.GATE_RECIPE + "/next"
    after = gs.hash_files([path])
    assert before != after, "bumping the recipe retires every existing stamp, which is the point"
