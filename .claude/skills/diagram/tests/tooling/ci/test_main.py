"""The CLI: every subcommand reachable under make (the suite runs under make, so the guard passes);
a bare invocation outside make is refused and names `make ci-status` (T013)."""

from __future__ import annotations

import functools
import json
from pathlib import Path

import pytest

from l7r.diagram import _invocation
from l7r.diagram.ci import __main__ as cli
from l7r.diagram.ci import config, dispatch, state
from tests.tooling.ci.conftest import FakeClient, ScriptedSh, commit, git

S = ".claude/skills/diagram/"


@pytest.fixture
def roots(repo: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(cli, "_roots", lambda: (repo, repo / S))
    monkeypatch.setattr(dispatch, "Boto3Client", lambda secrets: FakeClient())
    monkeypatch.setattr(dispatch, "Context", functools.partial(dispatch.Context, sh=ScriptedSh(), sleep=lambda s: None, stream_poll_s=0))
    monkeypatch.setattr(config, "load_secrets", lambda root: config.Secrets("r", "a", "s", "b", "e", "g", "p", "m"))
    monkeypatch.delenv("SPECIFY_FEATURE", raising=False)
    return repo


def test_state_subcommand_writes_the_file(roots: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["state", "green-local", "quick"]) == 0
    assert state.read(roots).target == "quick"  # type: ignore[union-attr]
    assert "recorded" in capsys.readouterr().out
    with pytest.raises(SystemExit):
        cli.main(["state", "green-local"])


def test_door_and_remote_spend(roots: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["door"]) == 1
    assert "no FULL entry" in capsys.readouterr().out
    assert cli.main(["remote-spend"]) == 0
    assert "Remote spend" in capsys.readouterr().out


def test_status_route_only_and_full_status(roots: Path, capsys: pytest.CaptureFixture[str]) -> None:
    commit(roots, "docs/x.md", "d\n")
    assert cli.main(["status", "--route"]) == 0
    assert capsys.readouterr().out.strip() == "DIRECT"
    assert cli.main(["status"]) == 0
    out = capsys.readouterr().out
    assert "route DIRECT" in out and "Remote spend" in out


def test_status_without_secrets_still_answers(roots: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    def boom(root: Path) -> config.Secrets:
        raise FileNotFoundError("no ini")

    monkeypatch.setattr(config, "load_secrets", boom)
    assert cli.main(["status"]) == 0
    assert "(no AWS lookup: no ini)" in capsys.readouterr().out


def test_check_and_merge_run_the_dispatcher(roots: Path, capsys: pytest.CaptureFixture[str]) -> None:
    commit(roots, S + "l7r/diagram/m.py", "x = 2\n")
    state.write(roots, state.GREEN, "quick")
    assert cli.main(["check"]) == 0
    logs = list((roots / S / "dev" / "run-log").glob("*.json"))
    assert len(logs) == 1 and json.loads(logs[0].read_text(encoding="utf-8"))["target"] == "ci-check"
    assert cli.main(["merge"]) == 1, "no complete feature named: the merge refuses"
    assert "feature-complete" in capsys.readouterr().out
    assert (roots / ".git" / "ci-verdict").read_text(encoding="utf-8").strip() == "REFUSE(feature-complete)"


def test_a_cheap_operation_is_refused_as_a_remote_target_and_an_expensive_one_dispatches(roots: Path, capsys: pytest.CaptureFixture[str]) -> None:
    commit(roots, S + "l7r/diagram/m.py", "x = 2\n")
    state.write(roots, state.GREEN, "quick")
    assert cli.main(["check", "--target", "site-justice"]) == 1
    assert "only an EXPENSIVE operation" in capsys.readouterr().out
    assert cli.main(["check", "--target", "not-a-target"]) == 1
    assert cli.main(["check", "--target", "cohort N=48", "--compute", "BUILD_GENERAL1_2XLARGE"]) == 0
    entry = json.loads(next((roots / S / "dev" / "run-log").glob("*.json")).read_text(encoding="utf-8"))
    assert entry["scope"] == "operation" and entry["reason"] == "cohort N=48" and entry["compute"] == "BUILD_GENERAL1_2XLARGE"


def test_measure_dispatches_with_NO_engine_delta_and_says_what_it_buys(roots: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Feature 177: the CLI end of the measurement route, on the delta that refuses every other one.

    A DOCS-ONLY commit is the case: `check` refuses it at `route-is-gated` and `measure` runs, which
    is the whole reason the route exists - feature 175 owed a FULL-scope timing and could not take it
    because there was no engine change to point at."""
    commit(roots, "docs/only.md", "d\n")
    state.write(roots, state.GREEN, "quick")
    assert cli.main(["check"]) == 1
    assert "REFUSE(route-is-gated)" in capsys.readouterr().out
    assert cli.main(["measure"]) == 0
    out = capsys.readouterr().out
    assert "buys a NUMBER - no verified record, no push" in out, "the operator is told what this run cannot do"
    assert "BYPASSED" in out, "and the bypassed condition is still printed"


def test_engine_key_subcommand(roots: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["engine-key"]) == 0
    key = capsys.readouterr().out.strip()
    assert len(key) == 64
    assert cli.main(["engine-key", "HEAD^{tree}"]) == 0 and capsys.readouterr().out.strip() == key


def test_image_and_target_validation(roots: Path) -> None:
    assert cli.main(["image"]) == 0
    with pytest.raises(SystemExit):
        cli.main(["merge", "--target", "cohort"])


def test_bare_invocation_outside_make_is_refused_and_names_the_target(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """The suite itself runs under make, so the refusal is exercised by standing the verdict down
    (the way tests/test_invocation.py does) rather than by spawning a process that would inherit make."""
    monkeypatch.setattr(_invocation, "_verdict", (False, "not invoked through make"))
    with pytest.raises(SystemExit) as e:
        _invocation.assert_via_make("l7r.diagram.ci", _invocation.target_for("l7r.diagram.ci"))
    assert e.value.code == 2 and "make ci-status" in capsys.readouterr().err
    assert _invocation.target_for("l7r.diagram.ci") == "ci-status"


def test_roots_resolve_to_this_repository() -> None:
    root, skill = cli._roots()
    assert skill == root / ".claude" / "skills" / "diagram" and (root / ".git").exists()
    assert git(root, "rev-parse", "--show-toplevel") == str(root)


# ---- REMOTE OFF (feature 132): no client is ever constructed --------------------------------------


@pytest.fixture
def remote_off(roots: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    from l7r.diagram import switches

    switches.write(roots / S, "remote", "off", "no AWS this week", who="GM")

    def never(secrets: config.Secrets) -> FakeClient:
        raise AssertionError("a client was constructed with remote off")

    monkeypatch.setattr(dispatch, "Boto3Client", never)
    return roots


def test_remote_off_route_and_status_need_no_client(remote_off: Path, capsys: pytest.CaptureFixture[str]) -> None:
    commit(remote_off, S + "l7r/diagram/m.py", "x = 2\n")
    assert cli.main(["status", "--route"]) == 0 and capsys.readouterr().out.strip() == "GATED-LOCAL"
    assert cli.main(["status"]) == 0
    out = capsys.readouterr().out
    assert "[--] remote-enabled" in out and "no AWS this week" in out
    commit(remote_off, "docs/x.md", "d\n")
    git(remote_off, "update-ref", "refs/remotes/origin/main", "HEAD")  # a DIRECT delta stays DIRECT
    assert cli.main(["status", "--route"]) == 0 and capsys.readouterr().out.strip() == "DIRECT"


def test_remote_off_check_and_image_refuse_and_name_ci_on(remote_off: Path, capsys: pytest.CaptureFixture[str]) -> None:
    commit(remote_off, S + "l7r/diagram/m.py", "x = 2\n")
    state.write(remote_off, state.GREEN, "quick")
    assert cli.main(["check"]) == 1
    err = capsys.readouterr().err
    assert "remote is OFF" in err and "make ci-on" in err and "ci-check" in err
    assert cli.main(["image"]) == 1 and "ci-image" in capsys.readouterr().err
    from l7r.diagram.ci import runlog

    assert runlog.remote_entries(remote_off / S) == []  # no remote run was attempted - only would-have-dispatched entries (feature 133)


def test_remote_off_merge_is_local_gated(remote_off: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    commit(remote_off, S + "l7r/diagram/m.py", "x = 2\n")
    state.write(remote_off, state.GREEN, "quick")
    # no complete feature: refused, with the merge-and-rerun instruction, and the verdict file written
    assert cli.main(["merge"]) == 1
    out = capsys.readouterr().out
    assert "LOCAL-GATED" in out and "REFUSE(feature-complete)" in out
    assert (remote_off / ".git" / "ci-verdict").read_text(encoding="utf-8").strip() == "REFUSE(feature-complete)"
    # a complete feature but only `make quick` green: nothing vouches for the merged engine content
    d = remote_off / "specs" / "132-x"
    d.mkdir(parents=True)
    (d / "tasks.md").write_text("- [x] T001 done\n", encoding="utf-8")
    (d / "spec.md").write_text("FAITHFUL\n", encoding="utf-8")
    monkeypatch.setenv("SPECIFY_FEATURE", "132-x")
    assert cli.main(["merge"]) == 1
    out = capsys.readouterr().out
    assert "REFUSE(remote-enabled)" in out and "git pull --no-rebase origin main" in out and "make done" in out
    # a green local `make done` on exactly this engine content: SKIP-VERIFIED - the caller pushes, no build
    state.write(remote_off, state.GREEN, "done")
    assert cli.main(["merge"]) == 0
    out = capsys.readouterr().out
    assert "SKIP-VERIFIED" in out and "no build" in out
    assert (remote_off / ".git" / "ci-verdict").read_text(encoding="utf-8").strip() == "SKIP-VERIFIED"


def test_verified_done_subcommand(roots: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["verified-done"]) == 1 and "no local check" in capsys.readouterr().out
    state.write(roots, state.GREEN, "done")
    assert cli.main(["verified-done"]) == 0 and "already verified" in capsys.readouterr().out


# ---- the would-have-dispatched trail (feature 133 FR-004): every refused paid attempt is on record --


def test_remote_off_refusals_leave_would_have_entries(remote_off: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    from l7r.diagram.ci import runlog

    skill = remote_off / S
    commit(remote_off, S + "l7r/diagram/m.py", "x = 2\n")
    state.write(remote_off, state.GREEN, "quick")
    assert cli.main(["check"]) == 1 and "would-have-dispatched" in capsys.readouterr().err
    assert cli.main(["image"]) == 1
    assert cli.main(["remote-ok", "ci-check"]) == 1 and "would-have-dispatched" in capsys.readouterr().err
    assert cli.main(["remote-ok", "ci-image"]) == 1
    rows = runlog.would_have_entries(skill)
    assert [r["target"] for r in rows] == ["ci-check", "ci-image", "ci-check", "ci-image"]
    assert runlog.month_to_date(skill) == 0.0
    # a merge that WOULD have dispatched (complete feature, green quick, nothing verified) is recorded too
    d = remote_off / "specs" / "133-x"
    d.mkdir(parents=True)
    (d / "tasks.md").write_text("- [x] T001 done\n", encoding="utf-8")
    (d / "spec.md").write_text("FAITHFUL\n", encoding="utf-8")
    monkeypatch.setenv("SPECIFY_FEATURE", "133-x")
    assert cli.main(["merge"]) == 1 and "would-have-dispatched" in capsys.readouterr().out
    assert runlog.would_have_entries(skill)[-1]["target"] == "ci-merge"
    # ...and one that is SKIP-VERIFIED is not: nothing would have run
    state.write(remote_off, state.GREEN, "done")
    n = len(runlog.would_have_entries(skill))
    assert cli.main(["merge"]) == 0 and len(runlog.would_have_entries(skill)) == n
    assert "Would have dispatched" in runlog.remote_spend_report(skill)


def test_remote_ok_passes_when_remote_is_on(roots: Path) -> None:
    assert cli.main(["remote-ok", "ci-check"]) == 0


def test_the_tooling_freshness_subcommands_round_trip(roots: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Feature 174: `tooling-fresh` and `tooling-green` - the pair `make quick` uses to decide
    whether to collect `tests/tooling/` at all.

    Both directions asserted: fresh is FALSE (exit 1) before anything is recorded, TRUE (exit 0)
    once `tooling-green` records the hash. A test of one direction alone passes with the comparison
    inverted, which is the whole point of the exit code.
    """
    assert cli.main(["tooling-fresh"]) == 1, "nothing recorded yet, so the tooling is not vouched for"
    assert cli.main(["tooling-green"]) == 0
    assert "recorded green" in capsys.readouterr().out
    assert cli.main(["tooling-fresh"]) == 0, "and now it is - `make quick` may skip the tooling tests"
