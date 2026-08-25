"""The build-side FULL door FIRES (no entry; cancelled; inherited from main; env var alone) and STAYS
QUIET for a committed `permitted` entry authored by this work (T056, T057)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from l7r.diagram.ci import door
from tests.ci.conftest import commit, git

S = ".claude/skills/diagram/"


def _entry(root: Path, name: str, outcome: str, target: str, commit_sha: str) -> None:
    (root / S / "dev" / "bypass-log" / name).write_text(json.dumps({"utc": "2026-08-25T00:00:00Z", "target": target, "commit": commit_sha, "outcome": outcome, "why": "the reason"}), encoding="utf-8")


def test_no_entry_at_all(repo: Path) -> None:
    ok, why = door.check(repo, repo / S)
    assert not ok and "no FULL entry" in why


def test_cancelled_entry_does_not_open(repo: Path) -> None:
    sha = git(repo, "rev-parse", "--short", "HEAD")
    _entry(repo, "a.json", "cancelled", "done FULL", sha)
    ok, why = door.check(repo, repo / S)
    assert not ok and "cancelled, refused, or inherited" in why


def test_entry_inherited_from_main_authorizes_nothing(repo: Path) -> None:
    sha = git(repo, "rev-parse", "--short", "HEAD")  # HEAD == origin/main: an ancestor of both
    _entry(repo, "a.json", "permitted", "done FULL", sha)
    ok, _ = door.check(repo, repo / S)
    assert not ok


def test_env_var_alone_opens_nothing(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REF_WHY", "I really mean it")
    monkeypatch.setenv("CODEBUILD_BUILD_ID", "gm-assistant-merge:x")
    ok, _ = door.check(repo, repo / S)
    assert not ok


def test_a_permitted_entry_authored_by_this_work_opens(repo: Path) -> None:
    sha = commit(repo, S + "l7r/diagram/m.py", "x = 2\n", "our work")[:8]
    _entry(repo, "b.json", "permitted", "ci-merge FULL", sha)
    _entry(repo, "c.json", "permitted", "done", sha)  # not a FULL entry: ignored
    _entry(repo, "broken.json", "permitted", "done FULL", sha)
    (repo / S / "dev" / "bypass-log" / "broken.json").write_text("{", encoding="utf-8")
    ok, why = door.check(repo, repo / S)
    assert ok and "b.json" in why and "authorizes FULL" in why


def test_a_permitted_entry_whose_commit_is_not_in_history_does_not_open(repo: Path) -> None:
    commit(repo, S + "l7r/diagram/m.py", "x = 2\n", "our work")
    _entry(repo, "b.json", "permitted", "done FULL", "0000000")
    ok, _ = door.check(repo, repo / S)
    assert not ok
