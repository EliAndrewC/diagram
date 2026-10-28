"""`land.revert_ticks` - a failed push's ticks put back, and the message true to what happened (2026-10-25, 422 T02)."""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess

import pytest

pytestmark = pytest.mark.tooling

REPO = pathlib.Path(__file__).resolve().parents[2]


def _land():
    spec = importlib.util.spec_from_file_location("land_under_test", REPO / "scripts" / "land.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _git(root: pathlib.Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False).stdout.strip()


def _repo(tmp_path: pathlib.Path) -> pathlib.Path:
    root = tmp_path / "clone"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "t@example.org")
    _git(root, "config", "user.name", "t")
    (root / "tasks.md").write_text("- [ ] T01\n")
    (root / "glossary.json").write_text("base\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "base")
    return root


def test_a_clean_clone_reverts_the_tick_and_says_so(tmp_path: pathlib.Path) -> None:
    root = _repo(tmp_path)
    (root / "tasks.md").write_text("- [x] T01\n")
    _git(root, "commit", "-q", "-am", "T01 ticked")
    said = _land().revert_ticks(root, _git(root, "rev-parse", "HEAD"))
    assert said.startswith("its ticks reverted")
    assert (root / "tasks.md").read_text() == "- [ ] T01\n"


def test_a_merge_left_in_progress_keeps_the_tick_and_says_so(tmp_path: pathlib.Path) -> None:
    """The push's pull stopped on a conflict: git refuses the revert, and the message must not claim it happened."""
    root = _repo(tmp_path)
    _git(root, "checkout", "-q", "-b", "other")
    (root / "glossary.json").write_text("theirs\n")
    _git(root, "commit", "-q", "-am", "theirs")
    _git(root, "checkout", "-q", "main")
    (root / "glossary.json").write_text("ours\n")
    (root / "tasks.md").write_text("- [x] T01\n")
    _git(root, "commit", "-q", "-am", "T01 ticked")
    tick = _git(root, "rev-parse", "HEAD")
    _git(root, "merge", "other")  # conflicts on glossary.json, as the push's pull did
    said = _land().revert_ticks(root, tick)
    assert "could NOT be reverted" in said and tick[:9] in said and "sync-with-main.sh done" in said
    assert (root / "tasks.md").read_text() == "- [x] T01\n", "the tick stands"


def test_the_push_names_the_feature_being_landed(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    """`make claim` points .specify/feature.json at a feature filed mid-task; the push's gated merge must read the landing's own
    feature, so `push` names it (2026-10-28: 443 T12's landing refused as 445's after its whole gate)."""
    land = _land()
    seen: dict[str, str] = {}

    def run(cmd, cwd=None, env=None, **_kw):  # type: ignore[no-untyped-def]
        seen.update(env or {})
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(land.subprocess, "run", run)
    monkeypatch.setenv("SPECIFY_FEATURE", "445-claims-switch")
    assert land.push(tmp_path, ["T12"], tmp_path / "specs" / "443-work-budget-tooling") == 0
    assert seen["SPECIFY_FEATURE"] == "443-work-budget-tooling" and seen["L7R_LAND_TICKS"] == "T12"
    assert land.push(tmp_path, ["T12"]) == 0 and seen["SPECIFY_FEATURE"] == "445-claims-switch", "no feature given: the caller's own"
