"""The verification state: written by the targets, keyed on gate-stamp's hash, reset by an edit (R6)."""

from __future__ import annotations

from pathlib import Path

import pytest

from l7r.diagram.ci import state
from tests.ci.conftest import commit

S = ".claude/skills/diagram/"


def test_absent_then_green_then_hash_changes_on_edit(repo: Path) -> None:
    assert state.read(repo) is None
    st = state.write(repo, state.GREEN, "quick")
    assert st.event == state.GREEN and st.target == "quick" and st.hash == state.current_hash(repo) and st.commit and len(st.engine_key) == 64
    again = state.read(repo)
    assert again == st
    assert "current code" in state.describe(again, state.current_hash(repo))
    (repo / S / "l7r/diagram/m.py").write_text("x = 99\n", encoding="utf-8")  # a source edit, not even committed
    assert state.current_hash(repo) != st.hash
    assert "DIFFERENT code" in state.describe(again, state.current_hash(repo))


def test_a_comment_edit_keeps_the_hash(repo: Path) -> None:
    """The stamp's hash is gate-stamp's semantic one: a comment appended to engine Python after a green
    run does not read as different code (GM 2026-08-26)."""
    before = state.current_hash(repo)
    (repo / S / "l7r/diagram/m.py").write_text("# the why\nx = 1  # still 1\n", encoding="utf-8")
    assert state.current_hash(repo) == before
    (repo / S / "l7r/diagram/m.py").write_text("x = 11\n", encoding="utf-8")
    assert state.current_hash(repo) != before


def test_a_green_subset_run_does_not_forget_a_green_done(repo: Path) -> None:
    """GM 2026-08-26: `make quick` after a green `make done` on identical content must not cost the
    next `make done` its short-circuit; a red run, or a changed source, still replaces the record."""
    state.write(repo, state.GREEN, "done")
    assert state.already_verified(repo)[0]
    st = state.write(repo, state.GREEN, "quick")
    assert st.target == "done" and state.already_verified(repo)[0], "the green gate still stands after a green quick"
    state.write(repo, state.FAILED, "quick")
    assert not state.already_verified(repo)[0], "a red run replaces it"
    state.write(repo, state.GREEN, "done")
    (repo / S / "l7r/diagram/m.py").write_text("x = 5\n", encoding="utf-8")
    st = state.write(repo, state.GREEN, "quick")
    assert st.target == "quick", "changed content: the quick record is the truth now"


def test_a_locked_scope_record_does_not_survive_the_unlock(repo: Path) -> None:
    """Under `scope reference` the gate defers the map-rolling tests (GM 2026-08-26), so its green
    record is reused while the lock holds and refused the moment it is released."""
    from l7r.diagram import switches

    skill = repo / S
    switches.write(skill, "scope", "reference", "test", who="t")
    st = state.write(repo, state.GREEN, "done")
    assert st.scope == "reference"
    assert state.already_verified(repo)[0], "still locked: the record stands"
    switches.write(skill, "scope", "unlocked", "test", who="t")
    ok, why = state.already_verified(repo)
    assert not ok and "deferred" in why and "LOCKED" in why
    st2 = state.write(repo, state.GREEN, "done")
    assert st2.scope == "unlocked" and state.already_verified(repo)[0]


def test_failed_gate_is_recorded_and_describe_handles_none(repo: Path) -> None:
    st = state.write(repo, state.FAILED, "done")
    assert st.event == state.FAILED
    assert state.describe(None, "x") == "no local check recorded in this clone"


def test_an_unknown_event_is_refused(repo: Path) -> None:
    with pytest.raises(ValueError):
        state.write(repo, "maybe", "quick")


def test_the_hash_is_gate_stamps_not_a_reimplementation(repo: Path) -> None:
    """A new untracked .py under the area changes the hash - gate-stamp's `-co` rule, inherited."""
    before = state.current_hash(repo)
    (repo / S / "l7r/diagram/new.py").write_text("y = 1\n", encoding="utf-8")
    assert state.current_hash(repo) != before
    commit(repo, S + "SKILL.md", "docs\n")  # a docs file does not move it
    after_docs = state.current_hash(repo)
    (repo / S / "SKILL.md").write_text("more docs\n", encoding="utf-8")
    assert state.current_hash(repo) == after_docs


# ---- the local short-circuit (feature 132 amendment; re-keyed by the second amendment) -----------


def test_already_verified_only_after_a_green_done_against_unchanged_engine_content(repo: Path) -> None:
    ok, why = state.already_verified(repo)
    assert not ok and "no local check" in why
    state.write(repo, state.GREEN, "quick")
    ok, why = state.already_verified(repo)
    assert not ok and "only a green `make done`" in why
    state.write(repo, state.FAILED, "done")
    assert not state.already_verified(repo)[0]
    st = state.write(repo, state.GREEN, "done")
    ok, why = state.already_verified(repo)
    assert ok and "already verified" in why and st.commit in why
    # the GM's second amendment: docs, the Makefile, config and scripts/ do NOT owe the gate
    (repo / "docs").mkdir(exist_ok=True)
    (repo / "docs" / "note.md").write_text("only documentation\n")
    (repo / S / "Makefile").write_text("all:\n\t@true\n")
    (repo / S / "pyproject.toml").write_text("[tool.x]\n")
    (repo / "scripts" / "x-hooks.sh").write_text("echo guard\n")
    assert state.already_verified(repo)[0], "a docs / Makefile / config / scripts change keeps the verdict"
    # a .py under the skill OUTSIDE l7r/, tests/ and pool/ still invalidates it: the hash is gate-stamp's
    (repo / S / ".explain.py").write_text("x = 1\n")
    ok, why = state.already_verified(repo)
    assert not ok and "Python changed" in why
    state.write(repo, state.GREEN, "done")
    assert state.already_verified(repo)[0]
    # a tests-only edit KEEPS it (FR-024, the GM's ruling "Yes, locally AND on AWS") - neither the hash nor the key sees tests/
    (repo / S / "tests").mkdir(exist_ok=True)
    (repo / S / "tests" / "test_new.py").write_text("def test_x(): pass\n")
    assert state.already_verified(repo)[0], "a tests-only edit does not owe the gate"
    # a pool manifest edit invalidates it (the engine key)
    (repo / S / "pool").mkdir(exist_ok=True)
    (repo / S / "pool" / "x.json").write_text("{}\n")
    ok, why = state.already_verified(repo)
    assert not ok and "pool" in why


def test_the_short_circuit_key_contains_everything_the_stamp_hashes(repo: Path) -> None:
    """FR-019: the short-circuit re-writes the gate-stamp. Safe because the check compares the SAME
    hash the stamp writes - gate-stamp's diagram area, loaded from the script itself."""
    from tests.ci.conftest import REPO_ROOT

    gs = state._gate_stamp(REPO_ROOT)
    area_path, patterns = gs.AREAS["diagram"]
    assert state.current_hash(REPO_ROOT) == str(gs.hash_files(gs._area_files(REPO_ROOT, area_path, patterns), REPO_ROOT))  # with the root, so the semantic cache serves it (2.7 s -> ms without)
