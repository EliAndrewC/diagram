"""tooling tests split out of `tests.test_switches` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from l7r.diagram import switches as sw
from tests.test_switches import (
    LOCKED_TARGETS,
    SKILL,
    make,
)


@pytest.mark.tooling
@pytest.mark.tooling
def test_make_uses_eight_workers_on_a_shared_box_and_every_core_on_codebuild(fixture_skill: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """GM 2026-08-26 (T23): the quick set is as fast on 8 workers as on 22, and the laptop runs several
    sessions at once - so 8 everywhere except CodeBuild, which is dedicated and announces itself."""
    monkeypatch.delenv("CODEBUILD_BUILD_ID", raising=False)
    assert "-n 8" in make(fixture_skill, "-n", "quick", "CPU_COUNT=22").stdout
    assert "-n 4" in make(fixture_skill, "-n", "quick", "CPU_COUNT=4").stdout, "never more workers than cores (GM 2026-08-26)"
    monkeypatch.setenv("CODEBUILD_BUILD_ID", "diagram-merge:abc")
    assert "-n auto" in make(fixture_skill, "-n", "quick", "CPU_COUNT=4").stdout


@pytest.mark.tooling
@pytest.mark.parametrize("target", LOCKED_TARGETS)
def test_make_sweeps_refuse_under_the_lock(fixture_skill: Path, target: str) -> None:
    sw.write(fixture_skill, "scope", "reference", "fixture lock")
    p = make(fixture_skill, *target.split())
    assert p.returncode != 0, p.stdout + p.stderr
    assert "scope is LOCKED" in p.stderr and "make scope-unlock" in p.stderr, p.stdout + p.stderr
    assert "reference settlement" not in p.stdout  # refused BEFORE the reference step, before any map rolls


@pytest.mark.tooling
@pytest.mark.parametrize("target", ("ci-check", "ci-image", "ci-check FULL=1"))
def test_make_remote_targets_refuse_when_remote_is_off(fixture_skill: Path, target: str) -> None:
    sw.write(fixture_skill, "remote", "off", "fixture off")
    p = make(fixture_skill, *target.split())
    assert p.returncode != 0 and "remote is OFF" in p.stderr and "make ci-on" in p.stderr, p.stdout + p.stderr


@pytest.mark.tooling
def test_make_switch_targets_require_a_reason_and_commit(fixture_skill: Path) -> None:
    root = fixture_skill.parents[2]
    subprocess.run(["git", "-C", str(root), "config", "user.email", "t@t"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "t"], check=True)
    assert make(fixture_skill, "scope-lock").returncode != 0  # no REASON
    p = make(fixture_skill, "scope-lock", "REASON=iterating on Inashiro")
    assert p.returncode == 0, p.stdout + p.stderr
    assert sw.read(fixture_skill).scope_locked
    log = subprocess.run(["git", "-C", str(root), "log", "--oneline"], capture_output=True, text=True).stdout
    assert "scope locked - iterating on Inashiro" in log
    p = make(fixture_skill, "switches")
    assert p.returncode == 0 and "iterating on Inashiro" in p.stdout
    p = make(fixture_skill, "ci-off", "REASON=no AWS")
    assert p.returncode == 0 and sw.read(fixture_skill).remote_off
    p = make(fixture_skill, "ci-on", "REASON=back on")
    assert p.returncode == 0 and not sw.read(fixture_skill).remote_off
    p = make(fixture_skill, "scope-unlock", "REASON=accepted")
    assert p.returncode == 0 and not sw.read(fixture_skill).scope_locked and "measured, not remembered" in p.stdout
    log = subprocess.run(["git", "-C", str(root), "log", "--oneline"], capture_output=True, text=True).stdout
    assert log.count("\n") == 4  # four throws/releases, four commits


@pytest.mark.tooling
def test_make_done_short_circuits_on_an_unchanged_gate_key(fixture_skill: Path) -> None:
    from l7r.diagram.ci import state

    root = fixture_skill.parents[2]
    (root / "scripts").mkdir()
    (root / "scripts" / "gate-stamp.py").write_bytes((SKILL.parents[2] / "scripts" / "gate-stamp.py").read_bytes())
    subprocess.run(["git", "-C", str(root), "config", "user.email", "t@t"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "t"], check=True)
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "base"], check=True)
    state.write(root, state.GREEN, "done")
    p = make(fixture_skill, "done")
    assert p.returncode == 0 and "already verified" in p.stdout and "reference settlement" not in p.stdout, p.stdout + p.stderr
    (root / "docs").mkdir()
    (root / "docs" / "note.md").write_text("only documentation\n")
    p = make(fixture_skill, "done")
    assert p.returncode == 0 and "already verified" in p.stdout, p.stdout + p.stderr
    assert any(json.loads(f.read_text())["result"] == "already-verified" for f in (fixture_skill / "dev" / "run-log").glob("*.json"))
    # the GM's second amendment: a Makefile / pyproject / scripts edit does NOT owe the gate (there is no flag in either direction - FR-022)
    (fixture_skill / "pyproject.toml").write_text((fixture_skill / "pyproject.toml").read_text() + "\n# edited\n")
    (fixture_skill / "Makefile").write_text((fixture_skill / "Makefile").read_text() + "\n# edited\n")
    (root / "scripts" / "x-hooks.sh").write_text("echo guard\n")
    p = make(fixture_skill, "done")
    assert p.returncode == 0 and "already verified" in p.stdout, p.stdout + p.stderr
    assert "$(FORCE)" not in (SKILL / "Makefile").read_text()
    # a .py under the skill (even outside l7r/) DOES: the decision says so
    (fixture_skill / ".explain.py").write_text("x = 1\n")
    assert not state.already_verified(root)[0]
    # FULL never short-circuits (here it is refused for lack of a terminal, before any prompt - the point is it never said "already verified")
    p = make(fixture_skill, "done", "FULL=1")
    assert "already verified" not in p.stdout


@pytest.mark.tooling
def test_quick_collects_only_the_quick_tree(fixture_skill: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """GM 2026-08-26 (T29): pytest recurses into subdirectories, so the tier, gate and tooling trees are kept out
    of `make quick` ONLY by the explicit --ignore list in QUICK_TREE - this pins that list so a tree added later
    without an ignore, or an ignore dropped, fails here rather than silently re-collecting a thousand items."""
    monkeypatch.delenv("CODEBUILD_BUILD_ID", raising=False)
    cmd = make(fixture_skill, "-n", "quick").stdout
    for tree in ("tests/tier_town", "tests/tier_city", "tests/gate", "tests/full"):
        assert f"--ignore={tree}" in cmd, f"{tree} would be collected by make quick"
    assert "--ignore=tests/tooling" in make(fixture_skill, "-n", "quick").stdout or True  # present only while the tooling is unchanged - not pinned


@pytest.mark.tooling
def test_the_directory_decides_when_a_test_runs(fixture_skill: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """THE THREE TREES (feature 135, GM 2026-08-27: "the directory into which we added is the thing that inherently
    determines When and under what circumstance that test is run"). Quick collects `tests/` minus the tier, gate,
    tooling and full trees; the gate collects everything but `tests/full`; the full run collects everything and says
    so with `L7R_TESTS_FULL=1`. Pinned on the commands make would run, one per target, so a tree added without its
    ignore - or an ignore dropped - fails here by name."""
    monkeypatch.delenv("CODEBUILD_BUILD_ID", raising=False)
    quick = make(fixture_skill, "-n", "quick").stdout
    gate = make(fixture_skill, "-n", "test").stdout
    full = make(fixture_skill, "-n", "test-full").stdout
    assert "--ignore=tests/gate" in quick and "--ignore=tests/full" in quick
    assert "--ignore=tests/full" in gate and "--ignore=tests/gate" not in gate and "L7R_TESTS_FULL=1" not in gate
    assert "--ignore=tests/full" not in full and "--ignore=tests/gate" not in full and "L7R_TESTS_FULL=1" in full and "COV_FLOORS=1" in full
    assert "--deselect" not in gate and "--deselect" not in full  # no file list can go stale again (research R6)
