"""The classifier walks every path KIND and pins each one (T007) - a new kind cannot be silently
engine or silently docs - and the delta is what OUR commits changed, never what main contributed (R1)."""

from __future__ import annotations

from pathlib import Path

import pytest

from l7r.diagram.ci.delta import Delta, compute_delta, engine_key, engine_key_worktree, is_engine
from tests.tooling.ci.conftest import commit, git

S = ".claude/skills/diagram/"

ENGINE = [
    S + "l7r/diagram/settlement/houses.py",
    S + "pool/hamlets/inashiro.gen.py",
    S + "pool/hamlets/inashiro.json",
]
NOT_ENGINE = [
    # l7r/diagram/ci/ (feature 132 FR-025, the GM: "isn't it actually test code?"): tooling, DIRECT
    S + "l7r/diagram/ci/dispatch.py",
    S + "l7r/diagram/ci/CLAUDE.md",
    # tests/ (feature 132 FR-024, the GM's ruling "Yes, locally AND on AWS"): a tests-only delta is DIRECT
    S + "tests/settlement/test_houses.py",
    S + "tests/fixtures/gate_check_names.json",
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
    assert g.route == "GATED" and "3 engine path" in g.reason


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


def test_the_key_is_blind_to_comments_docstrings_and_formatting(repo: Path) -> None:
    """A record-the-why comment must not re-open the gate (GM 2026-08-26, feature 133 T11): the key
    is the docstring-stripped AST of each .py, so only tokens that RUN move it; a .json keys on bytes."""
    commit(repo, S + "l7r/diagram/m.py", "def f(x):\n    return x + 1\n")
    k0 = engine_key(repo, "HEAD")
    commit(repo, S + "l7r/diagram/m.py", '"""doc"""\n# why: see research\n\n\ndef f(x):\n    """f."""\n    return  x+1  # note\n')
    assert engine_key(repo, "HEAD") == k0, "comments, docstrings and formatting do not move the key"
    assert engine_key_worktree(repo) == k0, "...on the working tree either"
    commit(repo, S + "l7r/diagram/m.py", "def f(x):\n    return x + 2\n")
    assert engine_key(repo, "HEAD") != k0, "one code token moves it"
    (repo / S / "pool").mkdir(exist_ok=True)
    commit(repo, S + "pool/a.json", "{}\n")
    k1 = engine_key(repo, "HEAD")
    commit(repo, S + "pool/a.json", "{} \n")
    assert engine_key(repo, "HEAD") != k1, "a manifest keys on its bytes - any edit moves it"


# ---- the short-circuit key IS the remote key (feature 132, second amendment) ---------------------


@pytest.mark.parametrize("path", [S + "Makefile", S + "pyproject.toml", S + "requirements.txt", S + "requirements-dev.in", "scripts/gate-stamp.py", "scripts/x-hooks.sh", S + "dev/switches.json"])
def test_config_scripts_and_settings_are_not_engine(path: str) -> None:
    """The GM's second amendment: a Makefile, config or scripts/ change does not owe `make done` - the
    engine key does not move, exactly as it does not move for the remote gate."""
    assert not is_engine(path)


def test_the_worktree_key_ignores_the_makefile_and_docs(repo: Path) -> None:
    k0 = engine_key_worktree(repo)
    (repo / "docs").mkdir(exist_ok=True)
    (repo / "docs" / "x.md").write_text("docs\n")
    (repo / S / "Makefile").write_text("all:\n\t@true\n")
    assert engine_key_worktree(repo) == k0
    (repo / S / "tests").mkdir(exist_ok=True)
    (repo / S / "tests" / "test_new.py").write_text("def test_x(): pass\n")
    assert engine_key_worktree(repo) == k0, "a test is NOT engine content (FR-024, the GM's ruling)"
    (repo / S / "pool").mkdir(exist_ok=True)
    (repo / S / "pool" / "x.json").write_text("{}\n")
    assert engine_key_worktree(repo) != k0, "a pool manifest is"
