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
    row = ha.record_ruling(root, "reversal:/a.md", {"ruling": "process-fault", "why": "an oscillation over the bath bullet", "tooling_fix": "x"}, "round-arbiter", "2026-10-10T00:00:00Z")
    assert row["kind"] == "reversal" and ha.owed(root) == {}
    d = root / "specs" / "375-x"
    assert json.loads((d / "gm-review.jsonl").read_text())["ruling"] == "process-fault"
    assert ha.open_fixes(d) == [("reversal:/a.md", "x")], "a process fault is an open tooling fix (feature 379)"
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


ab = _load("arbiter_bundle")


def test_findings_are_marked_new_repeated_or_reversing() -> None:
    r1 = "1. the bath size has no footnote\n2. a tooltip is missing on doma\n\nEDIT a.html\n<<<\n10 by 8 ft\n===\n12 by 9 ft\n>>>\n"
    r2 = "1. the bath size has no footnote\n2. the well sits wrong now\n\nEDIT a.html\n<<<\n12 by 9 ft\n===\n10 by 8 ft\n>>>\n"
    m1, m2 = ab.mark_rounds([r1, r2])
    assert [k for k, _f in m1] == ["NEW", "NEW"]
    assert [k for k, _f in m2] == ["REPEATED", "NEW", "REVERSING"]


def test_the_bundle_carries_the_rounds_the_cascade_and_the_feature(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    import subprocess

    root = tmp_path / "c"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / ".specify").mkdir()
    (root / ".specify" / "feature.json").write_text('{"feature_directory": "specs/375-x"}')
    d = root / "specs" / "375-x"
    d.mkdir(parents=True)
    (d / "request.md").write_text("the GM's words")
    (d / "spec.md").write_text("the spec")
    q = root / "research" / "questions"
    q.mkdir(parents=True)
    (q / "0105-baths.html").write_text("<p>a</p>")
    reply = tmp_path / "r1.md"
    reply.write_text("1. the bath size has no footnote at all\n")
    (root / ".git" / "checks-open.json").write_text(
        json.dumps(
            {
                "dispatches": {
                    "t1": {"check": "quote-check", "subjects": ["q:0105"], "t": 1, "state": "answered", "reply": str(reply)},
                    "t2": {"check": "quote-check", "subjects": ["q:0105"], "t": 2, "state": "answered"},
                }
            }
        )
    )
    ha.trip(root, "round:quote-check|q:0105@3", "round", "quote-check|q:0105", "round 3 of quote-check on q:0105", 3)
    monkeypatch.delenv("L7R_EVENTS_DIR", raising=False)
    el = _load("event_log")
    el.append({"hook_event_name": "PreToolUse", "cwd": str(root), "tool_name": "Edit", "tool_input": {"file_path": str(q / "0105-baths.html"), "old_string": "a", "new_string": "b"}})
    manifest = ab.bundle(root, "round:quote-check|q:0105@3", tmp_path / "out").read_text()
    assert "trigger: round:quote-check|q:0105@3" in manifest and "### Round 1" in manifest and "### Round 2" in manifest
    assert "- NEW: the bath size has no footnote at all" in manifest and "(no reply kept for this round)" in manifest
    assert (tmp_path / "out" / "round-1-quote-check.md").read_text() == "1. the bath size has no footnote at all\n"
    assert "The whole reply: `round-1-quote-check.md`" in manifest
    assert (tmp_path / "out" / "request.md").read_text() == "the GM's words" and (tmp_path / "out" / "edits.diff").is_file()
    assert "0105-baths.html" in (tmp_path / "out" / "cascade.txt").read_text()
    assert ab.subject_files(root, "modal:sheet/bath") == ["l7r/diagram/interactive/assets/modals/sheet/bath.md"]
    assert ab.subject_files(root, "x") == []
    assert "trigger: red-gate" in ab.bundle(root, "red-gate", tmp_path / "out2").read_text()
    monkeypatch.chdir(root)
    assert ab.main(["red-gate", "--root", str(root), "--out", str(tmp_path / "out3")]) == 0
    v = tmp_path / "v.json"
    v.write_text(json.dumps({"ruling": "accept", "why": "the finding repeats a wording preference"}))
    assert ha.main(["ruled", "round:quote-check|q:0105@3", str(v), "--as", "main"]) == 2
    assert ha.main(["ruled", "round:quote-check|q:0105@3", str(v), "--as", "round-arbiter"]) == 0
    assert ha.main(["ruled", "round:quote-check|q:0105@3", str(v), "--as", "round-arbiter"]) == 1, "binding: once"
    assert ha.main(["bogus"]) == 2


def test_the_cascade_wire_stays_live_after_any_ruling(tmp_path: pathlib.Path) -> None:
    """The plan review of amendment 1: after a ruling the id advances and the count restarts from the dispatches then - an
    `accept` does not switch the wire off, and a `continue` allows a round's worth of checks, not a threshold's."""
    root = _clone(tmp_path)
    assert ha.cascade_state(root) == ("cascade@1", 0)
    assert ha.cascade(12, 10) and not ha.cascade(9, 1), "ten dispatches before the ratio means anything"
    ha.trip(root, "cascade@1", "cascade", "", "12 check dispatches over 10 changed lines", 1)
    ha.record_ruling(root, "cascade@1", {"ruling": "accept", "why": "the checks found real defects each time"}, "round-arbiter")
    assert ha.cascade_state(root) == ("cascade@2", 12)
    assert not ha.cascade(20, 10, 12) and ha.cascade(22, 10, 12), "live again a round of checks after the ruling"


def test_an_accept_on_a_round_cap_answers_its_units(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 374 FR-005: an `accept` closed the unit to dispatches while the record gate went on owing it, so the push
    refused what the arbiter accepted; a modal-research accept answers its three units, a page's check its question."""
    import sys
    import types

    calls: list[tuple[str, dict]] = []
    fake = types.ModuleType("record_owed")
    fake.answer = lambda root, check, result, **kw: calls.append((check, kw)) or [f"{check}:x"]  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "record_owed", fake)
    root = pathlib.Path("/r")
    assert ha.accept_answers(root, "modal-research|modal:sheet/x", "accepted") == ["modal-accuracy:x", "modal-references:x", "modal-gaps:x"]
    assert ha.accept_answers(root, "quote-check|q:0091", "accepted") == ["quote-check:x"]
    assert calls[-1] == ("quote-check", {"q": "0091"}) and calls[0] == ("modal-accuracy", {"kind": "sheet/x"})
    assert ha.accept_answers(root, "impl-drift|", "accepted") == [], "no subject: nothing to answer"
