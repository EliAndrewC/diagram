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


# ---- the local short-circuit (feature 132 amendment) ---------------------------------------------


def test_already_verified_only_after_a_green_done_against_unchanged_gate_content(repo: Path) -> None:
    ok, why = state.already_verified(repo)
    assert not ok and "no local check" in why
    state.write(repo, state.GREEN, "quick")
    ok, why = state.already_verified(repo)
    assert not ok and "only a green `make done`" in why
    state.write(repo, state.FAILED, "done")
    assert not state.already_verified(repo)[0]
    st = state.write(repo, state.GREEN, "done")
    assert st.gate_key and state.read(repo).gate_key == st.gate_key  # type: ignore[union-attr]
    ok, why = state.already_verified(repo)
    assert ok and "already verified" in why and st.commit in why
    (repo / "docs").mkdir(exist_ok=True)
    (repo / "docs" / "note.md").write_text("only documentation\n")
    assert state.already_verified(repo)[0], "a docs-only change keeps the verdict"
    (repo / S / "Makefile").write_text("all:\n\t@true\n")
    ok, why = state.already_verified(repo)
    assert not ok and "changed since" in why
    state.write(repo, state.GREEN, "done")
    (repo / S / "l7r" / "diagram" / "m.py").write_text("x = 'edited'\n")
    assert not state.already_verified(repo)[0], "an engine edit invalidates it too"


def test_the_gate_key_contains_everything_the_stamp_hashes(repo: Path) -> None:
    """FR-019: the short-circuit re-writes the gate-stamp, which is safe ONLY if every file the
    stamp hashes is in the gate key. Proven against gate-stamp's own file lists, in the real
    repository, both areas - including a .py under the skill outside l7r/, tests/ and pool/."""
    from l7r.diagram.ci.delta import is_gate
    from tests.ci.conftest import REPO_ROOT

    gs = state._gate_stamp(REPO_ROOT)
    for _area, (area_path, patterns) in gs.AREAS.items():
        files = gs._area_files(REPO_ROOT, area_path, patterns)
        assert files, area_path
        for f in files:
            assert is_gate(str(f.relative_to(REPO_ROOT))), f"{f} is hashed by gate-stamp but outside the gate key"
    assert is_gate(S + ".explain.py") and is_gate(S + "wip/x.gen.py")
