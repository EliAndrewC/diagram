"""What is left of `python3 -m l7r.diagram.ci`: the planner, until T071 (the rest is `rust/gate/src/ci/main/tests.rs`)."""

from __future__ import annotations

from pathlib import Path

import pytest

from l7r.diagram import _invocation
from l7r.diagram.ci import __main__ as cli


def test_incremental_subcommand_reaches_the_planner(repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Feature 207: `ci incremental <word>` is the Makefile's route to the planner; `where` names the baseline directory."""
    monkeypatch.chdir(repo)
    assert cli.main(["incremental", "where"]) == 0
    assert capsys.readouterr().out.strip().endswith("gate-baseline")
    assert cli.main(["incremental", "mode"]) == 0 and capsys.readouterr().out.strip() == "full"


def test_anything_else_is_the_usage(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["status"]) == 2 and "usage:" in capsys.readouterr().err


def test_bare_invocation_outside_make_is_refused_and_names_the_target(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """The suite itself runs under make, so the refusal is exercised by standing the verdict down."""
    monkeypatch.setattr(_invocation, "_verdict", (False, "not invoked through make"))
    with pytest.raises(SystemExit) as e:
        _invocation.assert_via_make("l7r.diagram.ci", _invocation.target_for("l7r.diagram.ci"))
    assert e.value.code == 2 and "make ci-status" in capsys.readouterr().err
    assert _invocation.target_for("l7r.diagram.ci") == "ci-status"
