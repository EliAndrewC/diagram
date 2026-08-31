"""The classifier walks every path KIND and pins each one (T007) - a new kind cannot be silently
engine or silently docs - and the delta is what OUR commits changed, never what main contributed (R1)."""

from __future__ import annotations

from pathlib import Path

import pytest

from l7r.diagram.ci.delta import SKILL, Delta, compute_delta, engine_key, engine_key_worktree, is_engine
from tests.tooling.ci.conftest import commit, git

S = ".claude/skills/diagram/"

ENGINE = [
    S + "l7r/diagram/settlement/houses.py",
    S + "pool/hamlets/inashiro/inashiro.gen.py",
    S + "pool/hamlets/inashiro/inashiro.json",
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
    S + "pool/hamlets/inashiro/inashiro.notes.md",
    S + "pool/hamlets/inashiro/inashiro.png",
    S + "pool/hamlets/inashiro/inashiro.svg",
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


def test_a_comment_only_engine_edit_routes_direct(repo: Path) -> None:
    """GM 2026-08-28: a comment, docstring or formatting edit to engine Python is not engine content -
    the gate's key has ignored it since 2026-08-26, and the router must agree (it used to send a wording
    sweep down the gated route, which then demanded a spec-kit feature the sweep did not have)."""
    commit(repo, S + "l7r/diagram/m.py", 'x = 3  # the stop-work ritual\n')
    git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    commit(repo, S + "l7r/diagram/m.py", '"""doc."""\n\nx = 3  # the stop-work procedure\n')
    d = compute_delta(repo)
    assert d.files == (S + "l7r/diagram/m.py",) and d.engine == () and d.route == "DIRECT", d
    commit(repo, S + "l7r/diagram/m.py", '"""doc."""\n\nx = 4\n')  # a token that runs re-opens the route
    assert compute_delta(repo).route == "GATED"
    commit(repo, S + "pool/hamlets/inashiro/inashiro.json", "{}\n")  # a non-.py engine file has no semantic form: always engine
    assert S + "pool/hamlets/inashiro/inashiro.json" in compute_delta(repo).engine


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


def test_coverage_scope_names_only_the_changed_engine_modules(repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Feature 135, second pass: the gate traces the packages the diff touched - committed since the merge
    base, modified in the worktree, or untracked - and nothing else; tests and docs never count."""
    from l7r.diagram.ci.__main__ import main
    from l7r.diagram.ci.delta import coverage_scope

    assert coverage_scope(repo) == []
    monkeypatch.chdir(repo)
    assert main(["cov-scope"]) == 0 and capsys.readouterr().out.strip() == "-o addopts= --no-cov"
    commit(repo, S + "l7r/diagram/settlement/land.py", "y = 1\n")  # committed since the merge base
    (repo / S / "l7r" / "diagram" / "m.py").write_text("x = 9\n", encoding="utf-8")  # modified, uncommitted
    (repo / S / "l7r" / "diagram" / "sitegen" / "__init__.py").parent.mkdir(parents=True)
    (repo / S / "l7r" / "diagram" / "sitegen" / "__init__.py").write_text("", encoding="utf-8")  # untracked package
    commit(repo, S + "tests/settlement/test_land.py", "def test_x(): pass\n")
    commit(repo, "docs/x.md", "prose\n")
    assert coverage_scope(repo) == ["l7r/diagram", "l7r/diagram/settlement", "l7r/diagram/sitegen"]
    assert main(["cov-scope"]) == 0
    assert capsys.readouterr().out.strip() == "-o addopts=--cov=l7r/diagram --cov=l7r/diagram/settlement --cov=l7r/diagram/sitegen"


def test_a_maps_notes_and_the_non_engine_directories_are_not_engine_code() -> None:
    """Feature 174: the two early exits in `is_engine`, which decide the ROUTE a push takes.

    A `.notes.md` beside a map and anything under the non-engine directories are docs: they take the
    DIRECT route and owe no build. Asserted beside a path that IS engine code, so the test would fail
    if the function simply started answering False.
    """
    assert not is_engine(f"{SKILL}pool/hamlets/inashiro/inashiro.notes.md"), "a map's notes are prose"
    assert not is_engine(f"{SKILL}tests/settlement/test_core.py"), "tests are not engine code (feature 132 FR-024)"
    assert is_engine(f"{SKILL}l7r/diagram/settlement/core.py"), "...but the engine itself is"
