"""The iteration switches (feature 132). TWO DIRECTIONS, ALWAYS: each refusal is proven to FIRE
under the thrown switch and to stay QUIET on the default - a guard that refuses correct work teaches
a session that the override is routine."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from l7r.diagram import switches as sw

SKILL = Path(__file__).resolve().parents[1]


@pytest.fixture
def skill(tmp_path: Path) -> Path:
    (tmp_path / "dev").mkdir()
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "Test Operator"], check=True)
    return tmp_path


# ---- the file --------------------------------------------------------------------------------


def test_absent_file_means_defaults(skill: Path) -> None:
    s = sw.read(skill)
    assert s == sw.DEFAULTS and not s.remote_off and not s.scope_locked and not s.error


def test_write_round_trip_keeps_the_other_axis(skill: Path) -> None:
    sw.write(skill, "remote", "off", "  no AWS this week  ")
    s = sw.write(skill, "scope", "reference", "reference hamlet only")
    assert s.remote_off and s.scope_locked
    assert s.remote.why == "no AWS this week" and s.remote.who == "Test Operator" and s.remote.utc.endswith("Z")
    again = sw.read(skill)
    assert again == s
    data = json.loads((skill / "dev" / "switches.json").read_text())
    assert set(data) == {"remote", "scope"} and set(data["remote"]) == {"state", "why", "who", "utc"}  # no `commit` field (fidelity round 1)


def test_release_returns_the_default(skill: Path) -> None:
    sw.write(skill, "scope", "reference", "lock")
    s = sw.write(skill, "scope", "unlocked", "done iterating", who="GM")
    assert not s.scope_locked and s.scope.who == "GM" and s.scope.why == "done iterating"


def test_empty_reason_and_unknown_state_are_refused(skill: Path) -> None:
    with pytest.raises(ValueError, match="reason is required"):
        sw.write(skill, "remote", "off", "   ")
    with pytest.raises(ValueError, match="unknown switch"):
        sw.write(skill, "remote", "maybe", "x")
    with pytest.raises(ValueError, match="unknown switch"):
        sw.write(skill, "gears", "off", "x")
    assert not (skill / "dev" / "switches.json").exists()


@pytest.mark.parametrize(
    "body",
    ["not json", "[1, 2]", '{"remote": {"state": "sometimes"}}', '{"scope": "reference"}', '{"remote": {"state": "on"}, "scope": {"state": "all"}}'],
)
def test_malformed_file_fails_closed(skill: Path, body: str) -> None:
    (skill / "dev" / "switches.json").write_text(body)
    s = sw.read(skill)
    assert s.error and s.remote_off and s.scope_locked
    assert "MALFORMED" in sw.describe(s)
    # the throw/release is the repair: a write replaces the corrupt file with a well-formed one
    fixed = sw.write(skill, "remote", "on", "repair")
    assert not fixed.error and not fixed.remote_off and not fixed.scope_locked


def test_who_falls_back_when_git_has_no_identity(tmp_path: Path) -> None:
    (tmp_path / "dev").mkdir()
    s = sw.write(tmp_path, "scope", "reference", "x")  # not a git repo at all
    assert s.scope.who == "unknown"


# ---- the refusals ------------------------------------------------------------------------------


def test_defaults_refuse_nothing(skill: Path) -> None:
    assert sw.refusal(sw.DEFAULTS, "remote", "ci-check") is None
    assert sw.refusal(sw.DEFAULTS, "scope", "cohort") is None
    assert sw.check(skill, "remote", "ci-check") and sw.check(skill, "scope", "cohort")


def test_remote_off_refusal_names_the_release_and_the_local_route(skill: Path) -> None:
    sw.write(skill, "remote", "off", "budget month exhausted")
    text = sw.refusal(sw.read(skill), "remote", "ci-check")
    assert text is not None
    for needle in ("REFUSED", "ci-check", "remote is OFF", "budget month exhausted", "Test Operator", "make ci-on", "make done", "sync-with-main.sh done"):
        assert needle in text
    assert sw.refusal(sw.read(skill), "scope", "cohort") is None  # the OTHER axis is untouched


def test_scope_lock_refusal_names_the_release_and_the_one_map_route(skill: Path, capsys: pytest.CaptureFixture[str]) -> None:
    sw.write(skill, "scope", "reference", "reference hamlet acceptance (feature 133)")
    assert not sw.check(skill, "scope", "cohort")
    err = capsys.readouterr().err
    for needle in ("REFUSED", "cohort", "scope is LOCKED", "feature 133", "make scope-unlock", "make reference", "make map GEN=<one gen>"):
        assert needle in err
    assert sw.check(skill, "remote", "ci-check")


def test_unknown_axis_is_an_error() -> None:
    with pytest.raises(ValueError, match="unknown axis"):
        sw.refusal(sw.DEFAULTS, "gears", "x")


def test_describe_shows_defaults_and_set_axes(skill: Path) -> None:
    assert "(default)" in sw.describe(sw.DEFAULTS)
    sw.write(skill, "remote", "off", "why not")
    d = sw.describe(sw.read(skill))
    assert "remote  off" in d and "why not" in d and "scope   unlocked   (default)" in d


# ---- the CLI (runs under make, so the invocation guard passes) -------------------------------


def test_cli_show_set_check(skill: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.chdir(skill)
    assert sw.main(["show"]) == 0 and "(default)" in capsys.readouterr().out
    assert sw.main(["check", "scope", "cohort"]) == 0
    assert sw.main(["set", "scope", "reference", "--why", "lock it"]) == 0 and "lock it" in capsys.readouterr().out
    assert sw.main(["check", "scope", "cohort"]) == 1 and "make scope-unlock" in capsys.readouterr().err
    assert sw.main(["set", "scope", "unlocked", "--why", "release"]) == 0
    assert "what accumulated is measured" in capsys.readouterr().out  # the unlock reminder
    assert sw.main(["set", "remote", "off"]) == 1 and "reason is required" in capsys.readouterr().err
    assert sw.main(["check", "remote", "ci-check"]) == 0
    with pytest.raises(SystemExit):
        sw.main(["set", "gears", "off", "--why", "x"])


# ---- THE MAKEFILE REFUSALS, for real (FR-014/FR-015): a fixture skill dir with the real Makefile -


@pytest.fixture
def fixture_skill(tmp_path: Path) -> Path:
    """A tree shaped like a clone's skill dir: the real Makefile, `l7r` symlinked, no `.clones/`
    (so `guard` passes), and the switch file under our control."""
    root = tmp_path / "repo"
    skill = root / ".claude" / "skills" / "diagram"
    skill.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (skill / "Makefile").write_bytes((SKILL / "Makefile").read_bytes())
    (skill / "pyproject.toml").write_bytes((SKILL / "pyproject.toml").read_bytes())
    (skill / "l7r").symlink_to(SKILL / "l7r", target_is_directory=True)
    (skill / "dev").mkdir()
    return skill


def make(skill: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["make", "--no-print-directory", "-C", str(skill), *args], capture_output=True, text=True, stdin=subprocess.DEVNULL)


LOCKED_TARGETS = ("cohort", "tripwire", "test-full", "cache-audit", "regressions", "perf", "perf-gate", "done FULL=1", "ci-check FULL=1", "ci-check TARGET=cohort", "ci-merge FULL=1", "maps SCOPE=all")


@pytest.mark.tooling
@pytest.mark.tooling
def test_make_uses_eight_workers_on_a_shared_box_and_every_core_on_codebuild(fixture_skill: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """GM 2026-08-26 (T23): the quick set is as fast on 8 workers as on 22, and the laptop runs several
    sessions at once - so 8 everywhere except CodeBuild, which is dedicated and announces itself."""
    monkeypatch.delenv("CODEBUILD_BUILD_ID", raising=False)
    assert "-n 8" in make(fixture_skill, "-n", "quick").stdout
    monkeypatch.setenv("CODEBUILD_BUILD_ID", "diagram-merge:abc")
    assert "-n auto" in make(fixture_skill, "-n", "quick").stdout


def test_make_test_defers_the_map_rolling_tests_under_the_lock(fixture_skill: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """GM 2026-08-26: the 4-minute gate under the lock was the `rolls_map` tests rolling OTHER maps;
    the lock now deselects them in `test`, says so, and never under the coverage floors."""
    from l7r.diagram import switches

    assert "not rolls_map" not in make(fixture_skill, "-n", "test").stdout
    switches.write(fixture_skill, "scope", "reference", "test", who="t")
    out = make(fixture_skill, "-n", "test").stdout
    assert '-m "not rolls_map"' in out and "DEFERRED" in out
    assert "not rolls_map" not in make(fixture_skill, "-n", "test", "COV_FLOORS=1").stdout
    monkeypatch.chdir(fixture_skill)
    assert switches.main(["state", "scope"]) == 0 and capsys.readouterr().out.strip() == "reference"


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


# ---- THE LOCAL SHORT-CIRCUIT of `make done` (feature 132 amendment, FR-019..FR-023) ----------------


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
