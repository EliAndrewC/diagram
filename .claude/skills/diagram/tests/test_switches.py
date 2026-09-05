"""The iteration switches (feature 132). TWO DIRECTIONS, ALWAYS: each refusal is proven to FIRE
under the thrown switch and to stay QUIET on the default - a guard that refuses correct work teaches
a session that the override is routine."""

from __future__ import annotations

import os
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
    assert s == sw.DEFAULTS and not s.remote_off and not s.error


def test_release_returns_the_default(skill: Path) -> None:
    s = sw.write(skill, "remote", "on", "done iterating", who="GM")
    assert not s.remote_off and s.remote.who == "GM" and s.remote.why == "done iterating"


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
    # feature 185: the two `scope` bodies were malformed ONLY because of the retired axis. Unknown
    # keys are IGNORED now (FR-007a), so they are valid and belong in the test below instead.
    # `'{"remote": "on"}'` reaches `_axis`'s not-an-object branch, which the removed scope cases used
    # to cover - a test deleted with its subject must not take a SURVIVING branch's coverage with it.
    ["not json", "[1, 2]", '{"remote": {"state": "sometimes"}}', '{"remote": "on"}'],
)
def test_malformed_file_fails_closed(skill: Path, body: str) -> None:
    (skill / "dev" / "switches.json").write_text(body)
    s = sw.read(skill)
    assert s.error and s.remote_off
    assert "MALFORMED" in sw.describe(s)
    # the throw/release is the repair: a write replaces the corrupt file with a well-formed one
    fixed = sw.write(skill, "remote", "on", "repair")
    assert not fixed.error and not fixed.remote_off


def test_who_falls_back_when_git_has_no_identity(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # "no identity" must be MADE, not assumed: since 2026-08-27 (feature 133 T51) every container carries
    # the GM's identity in the shared ~/.claude/gitconfig, included from ~/.gitconfig, so `git config
    # user.name` answers outside any repo - which is exactly the state this test needs to be absent
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    (tmp_path / "dev").mkdir()
    s = sw.write(tmp_path, "remote", "off", "x")  # not a git repo at all
    assert s.remote.who == "unknown"


# ---- the refusals ------------------------------------------------------------------------------


def test_defaults_refuse_nothing(skill: Path) -> None:
    assert sw.refusal(sw.DEFAULTS, "remote", "ci-check") is None
    assert sw.check(skill, "remote", "ci-check")


def test_remote_off_refusal_names_the_release_and_the_local_route(skill: Path) -> None:
    sw.write(skill, "remote", "off", "budget month exhausted")
    text = sw.refusal(sw.read(skill), "remote", "ci-check")
    assert text is not None
    for needle in ("REFUSED", "ci-check", "remote is OFF", "budget month exhausted", "Test Operator", "make ci-on", "make done", "sync-with-main.sh done"):
        assert needle in text


def test_unknown_axis_is_an_error() -> None:
    with pytest.raises(ValueError, match="unknown axis"):
        sw.refusal(sw.DEFAULTS, "gears", "x")


def test_describe_shows_defaults_and_set_axes(skill: Path) -> None:
    assert "(default)" in sw.describe(sw.DEFAULTS)
    sw.write(skill, "remote", "off", "why not")
    d = sw.describe(sw.read(skill))
    assert "remote  off" in d and "why not" in d


# ---- the CLI (runs under make, so the invocation guard passes) -------------------------------


def test_cli_show_set_check(skill: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.chdir(skill)
    assert sw.main(["show"]) == 0 and "(default)" in capsys.readouterr().out
    assert sw.main(["set", "remote", "off"]) == 1 and "reason is required" in capsys.readouterr().err
    assert sw.main(["check", "remote", "ci-check"]) == 0
    # `state` and a SUCCESSFUL `set`: both were covered only through the retired scope axis
    # (`main(["state","scope"])`, `main(["set","scope",...])`), so removing those cases left two
    # surviving CLI branches uncovered. The 100% floor named them, which is what it is for.
    assert sw.main(["state", "remote"]) == 0 and "on" in capsys.readouterr().out
    assert sw.main(["set", "remote", "off", "--why", "a real reason"]) == 0
    assert "a real reason" in capsys.readouterr().out
    assert sw.main(["state", "remote"]) == 0 and "off" in capsys.readouterr().out
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
    # THE PARENT RUN'S VARIABLES ARE STRIPPED, and the list is one variable wider than it was.
    #
    # MAKEFLAGS (feature 145): under `make test-full` the parent make exports `COV_FLOORS=1` through
    # MAKEFLAGS, and the fixture's make then inherited it - no `-m "not rolls_map"`, no
    # `--ignore=tests/full` - so these two tests failed in every FULL run and passed everywhere else.
    #
    # FULL and REF_WHY (feature 166): the same defect one variable over, and it hid for the same reason -
    # it can only be seen from inside a FULL run. A variable set on make's COMMAND LINE is exported into
    # the environment of its recipes, so `make done FULL=1` puts FULL=1 in os.environ, the fixture's own
    # `make done` inherits it, and that make meets the FULL prompt with no terminal to answer it and
    # refuses. Clearing MAKEFLAGS never touched it, because FULL arrives as a plain environment variable
    # rather than through the flags. Measured 2026-08-30: this is why the target failed on both FULL runs
    # of feature 166 and passes at every other scope.
    return subprocess.run(
        ["make", "--no-print-directory", "-C", str(skill), *args],
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
        env={**os.environ, "MAKEFLAGS": "", "MFLAGS": "", "FULL": "", "REF_WHY": ""},
    )


# `regressions` left this list with feature 166: the target rebuilt the frozen negative-fixture corpus,
# and the corpus was a set of bad manifests each proving one retired check still fired.
LOCKED_TARGETS = ("cohort", "test-full", "cache-audit", "perf", "perf-gate", "done FULL=1", "ci-check FULL=1", "ci-check TARGET=cohort", "ci-merge FULL=1", "maps SCOPE=all")


def _marker(skill: Path, pid: int) -> None:
    (skill / ".git").mkdir(exist_ok=True)
    (skill / ".git" / "idle-tests.running").write_text(f"{pid}\n")


def test_idle_context_needs_the_marker_an_ancestor_and_the_timers_command_line(skill: Path) -> None:
    """The GM (2026-08-28): relax the lock "when the tests are being run in the idle context" - and
    ONLY then. Four ways to not be that context, one way to be it."""
    timer_cmd = "/bin/bash /diagram/scripts/idle-tests-hooks.sh timer /diagram/.clones/x x sid"
    assert not sw.idle_context(skill, ancestors=lambda _p: [4242, 1], cmdline=lambda _p: timer_cmd, pid=99), "no marker file"
    _marker(skill, 4242)
    assert sw.idle_context(skill, ancestors=lambda _p: [4242, 1], cmdline=lambda _p: timer_cmd, pid=99)
    assert not sw.idle_context(skill, ancestors=lambda _p: [7, 1], cmdline=lambda _p: timer_cmd, pid=99), "the timer is not an ancestor"
    assert not sw.idle_context(skill, ancestors=lambda _p: [4242, 1], cmdline=lambda _p: "/bin/bash -c make done", pid=99), "the marker names a process that is not the timer"
    assert not sw.idle_context(skill, ancestors=lambda _p: [4242, 1], cmdline=lambda _p: "idle-tests-hooks.sh prompt", pid=99), "a hook mode other than timer"
    (skill / ".git" / "idle-tests.running").write_text("not-a-pid\n")
    assert not sw.idle_context(skill, ancestors=lambda _p: [4242, 1], cmdline=lambda _p: timer_cmd, pid=99), "a malformed marker"


def test_the_real_process_tree_is_not_the_idle_context(skill: Path) -> None:
    """This test process descends from pytest, never from the timer: even with a marker naming a
    live ancestor, the command-line check refuses it - a session cannot forge the context by writing
    the file."""
    import os

    _marker(skill, os.getppid())
    assert not sw.idle_context(skill)


def test_the_idle_subcommand_prints_a_BARE_FLAG_the_Makefile_can_read(capsys) -> None:
    """Feature 174. `switches idle` is how a shell asks whether this process descends from the idle
    timer (feature 136) - the answer gates the scope-lock relaxation, and it is deliberately `1`/`0`
    rather than prose so a Makefile can test it directly.

    A session's own process does NOT descend from the timer, which is the whole point: the
    relaxation is unforgeable by a session (`switches.idle_context`).
    """
    from l7r.diagram import switches

    assert switches.main(["idle"]) == 0
    assert capsys.readouterr().out.strip() == "0", "this process is not the idle timer's child"


def test_the_ancestor_walk_ends_at_INIT_at_a_VANISHED_process_and_at_its_own_depth_cap() -> None:
    """Three exits, and which one a live process tree happens to reach is the machine's decision, not
    the test's. Feature 174 measured that: the "no parent" exit was covered by one `make test-full`
    and missed by the very next `make done` on identical code, because a reparented process came and
    went between the two runs. So the reader is injected and each exit is driven directly."""
    from l7r.diagram import switches as sw

    tree = {5: "PPid:\t4\n", 4: "PPid:\t3\n", 3: "PPid:\t1\n"}
    assert sw._ancestors(5, status_of=lambda p: tree.get(p, "")) == [4, 3, 1], "the chain up to init"

    orphan = {5: "PPid:\t0\n"}
    assert sw._ancestors(5, status_of=lambda p: orphan.get(p, "")) == [], "a process reporting no parent ends the walk"

    gone = {5: "PPid:\t4\n"}
    assert sw._ancestors(5, status_of=lambda p: gone.get(p, "")) == [4], "a process that exited under us ends it where it can still be read"

    loop = dict.fromkeys(range(2, 200), "PPid:\t2\n")
    assert len(sw._ancestors(199, status_of=lambda p: loop.get(p, ""))) == 64, "and the depth cap holds against a cycle"

    assert sw._proc_status(-1) == "", "the real reader answers empty rather than raising for a pid that is not there"


def test_an_unknown_key_is_IGNORED_not_failed_closed(skill: Path) -> None:
    """The property feature 185 depends on, and the one an implementer would break by "fixing" it.

    A clone checked out from before the scope lock was retired still carries a `scope` block in its
    `dev/switches.json`. `read()` names only `remote`, through `data.get`, with no key iteration and
    no schema validation - so the stray block is simply not looked at. Making it strict would send
    that file down `_closed()`, and failing closed means REMOTE OFF in every clone that has one.

    `_closed()` has exactly three entrances: a JSON parse failure, a non-dict top level, or `_axis`
    rejecting a NAMED key. Never an unrecognized one.
    """
    (skill / "dev" / "switches.json").write_text('{"remote": {"state": "on", "why": "w", "who": "t", "utc": "u"}, "scope": {"state": "reference"}}')
    s = sw.read(skill)
    assert not s.error, "a leftover scope block must not fail closed"
    assert not s.remote_off, "and must not turn remote OFF"
    assert s.remote.state == "on"
