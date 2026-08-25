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
    assert st.event == state.GREEN and st.target == "quick" and st.hash == state.current_hash(repo) and st.commit
    again = state.read(repo)
    assert again == st
    assert "current code" in state.describe(again, state.current_hash(repo))
    (repo / S / "l7r/diagram/m.py").write_text("x = 99\n", encoding="utf-8")  # a source edit, not even committed
    assert state.current_hash(repo) != st.hash
    assert "DIFFERENT code" in state.describe(again, state.current_hash(repo))


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
