"""The classifier walks every path KIND and pins each one (T007) - a new kind cannot be silently
engine or silently docs - and the delta is what OUR commits changed, never what main contributed (R1)."""

from __future__ import annotations

from pathlib import Path

import pytest

from l7r.diagram.ci.delta import Delta, compute_delta, engine_key, engine_key_worktree, is_engine
from tests.ci.conftest import commit, git

S = ".claude/skills/diagram/"

ENGINE = [
    S + "l7r/diagram/settlement/houses.py",
    S + "l7r/diagram/ci/dispatch.py",
    S + "tests/settlement/test_houses.py",
    S + "tests/fixtures/gate_check_names.json",
    S + "pool/hamlets/inashiro.gen.py",
    S + "pool/hamlets/inashiro.json",
]
NOT_ENGINE = [
    S + "SKILL.md",
    S + "CLAUDE.md",
    S + "dev/run-log/20260825T000000000000-1.json",
    S + "dev/bypass-log/20260825T000000000000-1.json",
    S + "dev/perf-log/20260825T000000Z-130-start-x.json",
    S + "dev/loop.md",
    S + "future-work/something.md",
    S + "settlements/water.md",
    S + "buildings/manor.md",
    S + "research/farms.md",
    S + "pool/hamlets/inashiro.notes.md",
    S + "pool/hamlets/inashiro.png",
    S + "pool/hamlets/inashiro.svg",
    S + "timings.md",
    S + "l7r/diagram/settlement/CLAUDE.md",
    # how the gate RUNS, not what it tests (GM 2026-08-25): covered locally, never dispatched
    S + "Makefile",
    S + "pyproject.toml",
    S + "requirements.txt",
    S + "requirements-dev.in",
    "CLAUDE.md",
    "docs/session-clones.md",
    "specs/130-codebuild-merge-gate/tasks.md",
    "scripts/sync-with-main.sh",
    "buildspec/merge.yml",
    ".specify/memory/constitution.md",
]


@pytest.mark.parametrize("path", ENGINE)
def test_engine_kinds_are_engine(path: str) -> None:
    assert is_engine(path), path


@pytest.mark.parametrize("path", NOT_ENGINE)
def test_non_engine_kinds_are_not(path: str) -> None:
    assert not is_engine(path), path


def test_route_and_reason() -> None:
    assert Delta("b", (), ()).route == "DIRECT"
    assert "nothing to push" in Delta("b", (), ()).reason
    d = Delta("b", ("docs/x.md",), ())
    assert d.route == "DIRECT" and "none of them diagram engine code" in d.reason
    g = Delta("b", tuple(ENGINE), tuple(ENGINE))
    assert g.route == "GATED" and "+2 more" in g.reason and "6 engine path" in g.reason


def test_delta_is_our_commits_only(repo: Path) -> None:
    """Main advances with an engine change; we merge it in; our own delta is still docs-only (R1)."""
    # main gets an engine commit "elsewhere": build it on a branch and move origin/main to it
    git(repo, "checkout", "-q", "-b", "upstream")
    commit(repo, S + "l7r/diagram/m.py", "x = 2\n", "main-side engine change")
    git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    git(repo, "checkout", "-q", "main")
    commit(repo, "docs/note.md", "ours\n", "our docs commit")
    git(repo, "merge", "-q", "--no-edit", "upstream")
    d = compute_delta(repo)
    assert d.files == ("docs/note.md",), d.files
    assert d.route == "DIRECT"


def test_delta_sees_our_engine_change(repo: Path) -> None:
    commit(repo, S + "l7r/diagram/m.py", "x = 3\n")
    d = compute_delta(repo)
    assert d.engine == (S + "l7r/diagram/m.py",) and d.route == "GATED"


def test_a_clone_at_main_has_an_empty_delta(repo: Path) -> None:
    assert compute_delta(repo).files == ()


def test_the_engine_key_ignores_docs_and_moves_with_engine_content(repo: Path) -> None:
    """A green build vouches for the ENGINE content; a docs edit afterwards keeps the key (GM 2026-08-25)."""
    k0 = engine_key(repo, "HEAD")
    commit(repo, "docs/note.md", "docs only\n")
    commit(repo, S + "SKILL.md", "skill docs\n")
    commit(repo, S + "dev/run-log/x.json", "{}\n")
    assert engine_key(repo, "HEAD") == k0, "docs, skill docs and a run-log entry do not move the key"
    commit(repo, S + "l7r/diagram/m.py", "x = 2\n")
    k1 = engine_key(repo, "HEAD")
    assert k1 != k0
    assert engine_key(repo, "HEAD^{tree}") == k1, "a tree ref keys identically to its commit"
    assert len(k1) == 64


def test_the_worktree_key_equals_the_tree_key_for_the_same_content(repo: Path) -> None:
    """A `make done` before committing keys the content the commit will carry - one formula, two sources."""
    assert engine_key_worktree(repo) == engine_key(repo, "HEAD")
    (repo / S / "l7r/diagram/m.py").write_text("x = 7\n", encoding="utf-8")  # uncommitted engine edit
    k_wt = engine_key_worktree(repo)
    assert k_wt != engine_key(repo, "HEAD"), "the working tree moved, HEAD did not"
    commit(repo, S + "l7r/diagram/m.py", "x = 7\n")
    assert engine_key(repo, "HEAD") == k_wt, "once committed, the tree keys identically"
    (repo / S / "l7r/diagram/new.py").write_text("y = 1\n", encoding="utf-8")  # untracked engine file counts
    assert engine_key_worktree(repo) != k_wt


# ---- the GATE key (feature 132 amendment): the engine key plus what shapes the gate --------------


@pytest.mark.parametrize(
    "path",
    [
        S + "Makefile",
        S + "pyproject.toml",
        S + "requirements.txt",
        S + "requirements-dev.in",
        "scripts/gate-stamp.py",
        "scripts/x-hooks.sh",
        S + "l7r/diagram/m.py",
        S + "tests/test_x.py",
        S + ".explain.py",
        S + "wip/shiro-daika.gen.py",
    ],
)
def test_gate_kinds_are_gate(path: str) -> None:
    from l7r.diagram.ci.delta import is_gate

    assert is_gate(path)


@pytest.mark.parametrize("path", ["docs/x.md", "CLAUDE.md", S + "dev/switches.md", S + "dev/switches.json", S + "pool/hamlets/x.notes.md", "specs/132-x/spec.md", S + "SKILL.md"])
def test_docs_and_settings_are_not_gate(path: str) -> None:
    from l7r.diagram.ci.delta import is_gate

    assert not is_gate(path)


def test_the_gate_key_moves_with_the_makefile_but_not_with_docs(repo: Path) -> None:
    from l7r.diagram.ci.delta import gate_key_worktree

    k0 = gate_key_worktree(repo)
    (repo / "docs").mkdir(exist_ok=True)
    (repo / "docs" / "x.md").write_text("docs\n")
    assert gate_key_worktree(repo) == k0
    (repo / S / "Makefile").write_text("all:\n\t@true\n")
    k1 = gate_key_worktree(repo)
    assert k1 != k0 and engine_key_worktree(repo) == engine_key(repo, "HEAD")  # the ENGINE key did not move: the Makefile is gate-only
