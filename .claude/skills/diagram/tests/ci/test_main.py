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
from tests.ci.conftest import FakeClient, ScriptedSh, commit, git

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
