"""`scripts/hooks/lib/hm_arbiter.py` - tripwires and the round arbiter's rulings (feature 375, FR-010, FR-011).

The GM wanted progress never to stop at a round cap, and a loop caught when it happens: a trigger is owed one binding ruling,
holds only the next dispatch on its unit (or the next gate), and every ruling becomes a row of the GM's review.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from tests.tooling.test_modal_checks import _load

ha = _load("hm_arbiter")


def _clone(tmp: pathlib.Path) -> pathlib.Path:
    (tmp / ".git").mkdir()
    (tmp / ".specify").mkdir()
    (tmp / ".specify" / "feature.json").write_text('{"feature_directory": "specs/375-x"}')
    return tmp


def test_a_trigger_holds_only_its_unit_or_the_gate_until_ruled(tmp_path: pathlib.Path) -> None:
    root = _clone(tmp_path)
    assert ha.trip(root, "round:quote-check|q:0105@3", "round", "quote-check|q:0105", "d", 1)
    assert not ha.trip(root, "round:quote-check|q:0105@3", "round", "quote-check|q:0105", "d", 2), "once"
    assert ha.blocking(root, "quote-check|q:0105") == ["round:quote-check|q:0105@3"] and ha.blocking(root, "record-format|q:0105") == []
    ha.trip(root, "red-gate", "red-gate", "", "two red gates", 3)
    assert ha.blocking(root, gate=True) == ["red-gate"] and "red-gate" not in ha.blocking(root, "x")
    ha.trip(root, "reversal:/a.md", "reversal", "/a.md", "A -> B -> A", 4)
    assert "reversal:/a.md" in ha.blocking(root, "anything"), "a reversal holds every check"
    assert "make arbiter-bundle" in ha.refusal(["red-gate"]) and ha.refusal([]) == ""


def test_a_ruling_is_binding_once_and_reaches_the_gm(tmp_path: pathlib.Path) -> None:
    root = _clone(tmp_path)
    ha.trip(root, "reversal:/a.md", "reversal", "/a.md", "A -> B -> A", 1)
    with pytest.raises(PermissionError):
        ha.record_ruling(root, "reversal:/a.md", {"ruling": "accept", "why": "x"}, "main")
    with pytest.raises(ValueError, match="one of"):
        ha.record_ruling(root, "reversal:/a.md", {"ruling": "maybe", "why": "x"}, "round-arbiter")
    row = ha.record_ruling(root, "reversal:/a.md", {"ruling": "process-fault", "why": "an oscillation over the bath bullet"},
                           "round-arbiter", "2026-10-10T00:00:00Z")
    assert row["kind"] == "reversal" and ha.owed(root) == {}
    d = root / "specs" / "375-x"
    assert json.loads((d / "gm-review.jsonl").read_text())["ruling"] == "process-fault"
    assert json.loads((d / "found.jsonl").read_text())["block"] == "reversal:/a.md", "a process fault is filed as a tooling row"
    with pytest.raises(ValueError, match="already ruled"):
        ha.record_ruling(root, "reversal:/a.md", {"ruling": "accept", "why": "again"}, "round-arbiter")
    assert not ha.trip(root, "reversal:/a.md", "reversal", "/a.md", "again", 2), "a ruled trigger does not fire again"
    assert ha.closed(root, "reversal:") == "process-fault" and ha.continues(root, "reversal:") == 0
    (d / "arbiter.jsonl").write_text((d / "arbiter.jsonl").read_text() + "not json\n")
    assert list(ha.rulings(root)) == ["reversal:/a.md"]
    (root / ".specify" / "feature.json").write_text("not json")
    with pytest.raises(ValueError, match="no active feature"):
        ha.record_ruling(root, "x", {"ruling": "accept", "why": "y"}, "round-arbiter")


def test_the_wires() -> None:
    log = [{"ev": "PreToolUse", "tool": "Edit", "path": "/a.md", "old": "A", "new": "B"}]
    assert ha.reversal(log, "/a.md", "B", "A") and not ha.reversal(log, "/b.md", "B", "A") and not ha.reversal(log, "/a.md", "A", "C")
    assert ha.cascade(10, 5) and not ha.cascade(9, 1) and not ha.cascade(10, 20)
    assert ha.env_ok("X_OK", 'X_OK="a reason here"') and not ha.env_ok("X_OK", "none")


def test_a_worktree_shares_its_clone_s_state(tmp_path: pathlib.Path) -> None:
    (tmp_path / "c").mkdir()
    root = _clone(tmp_path / "c")
    wt = tmp_path / "wt"
    wt.mkdir()
    (root / ".git" / "worktrees" / "wt").mkdir(parents=True)
    (root / ".git" / "worktrees" / "wt" / "commondir").write_text("../..\n")
    (wt / ".git").write_text(f"gitdir: {root / '.git' / 'worktrees' / 'wt'}\n")
    assert ha.common_dir(wt) == (root / ".git").resolve()
