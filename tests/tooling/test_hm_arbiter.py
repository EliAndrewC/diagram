"""`scripts/hooks/lib/hm_arbiter.py` - tripwires and the round arbiter's rulings (feature 375, FR-010, FR-011).

The GM wanted progress never to stop at a round cap, and a loop caught when it happens: a trigger is owed one binding ruling,
holds only the next dispatch on its unit (or the next gate), and every ruling becomes a row of the GM's review.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

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
    row = ha.record_ruling(
        root,
        "reversal:/a.md",
        {"ruling": "process-fault", "why": "an oscillation over the bath bullet", "tooling_fix": "x", "fix_measure": "x", "fix_minutes": 10},
        "round-arbiter",
        "2026-10-10T00:00:00Z",
    )
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
    numbered = "1. **the dike's breadth** told as a convention\n\n- the sluices match the page and are fine\n"
    assert ab.mark_rounds([numbered]) == [[("NEW", "**the dike's breadth** told as a convention")]], "confirmations are no finding"
    bold = "**COVERAGE** clean.\n\n- the mottled band is told on the tab\n\n**1. D3: the breadth is told as a convention**\n"
    assert ab.mark_rounds([bold]) == [[("NEW", "D3: the breadth is told as a convention**")]], "the bold numbered heading is read"


def test_a_clean_round_lists_no_findings() -> None:
    """A reply whose summary counts are all nought lists none of its passes as findings (the round arbiter on
    round:quote-check|q:0049@3: a clean round's "clean" and "What this round covered" bullets were marked NEW findings)."""
    clean = "quote-check: round 2, question 0049 - 2 changed blocks, no findings; 0 unfootnoted assertions; 0 EDITs\n\n- **Size bullet**: clean, both problems fixed.\n- **What this round covered.** the two changed blocks of the drawing page\n"
    assert ab.mark_rounds([clean]) == [[]]


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
                    "t1": {"check": "quote-check", "subjects": ["q:0105"], "t": 1, "state": "answered", "reply": str(reply), "owed": ["quote-check:0105#bath - a note's passage changed"]},
                    "t2": {"check": "quote-check", "subjects": ["q:0105"], "t": 2, "state": "answered"},
                    "t3": {"check": "quote-check", "subjects": ["q:0105"], "t": 2.5, "state": "answered", "aid": "a77"},
                }
            }
        )
    )
    ha.trip(root, "round:quote-check|q:0105@3", "round", "quote-check|q:0105", "round 3 of quote-check on q:0105", 3)
    monkeypatch.delenv("L7R_EVENTS_DIR", raising=False)
    el = _load("event_log")
    el.append({"hook_event_name": "PreToolUse", "cwd": str(root), "tool_name": "Edit", "tool_input": {"file_path": str(q / "0105-baths.html"), "old_string": "a", "new_string": "b"}})
    # a round whose reply the hook missed (its answer was recorded first) is read from the agent's own transcript (374)
    sub = tmp_path / "projects" / "-x" / "s1" / "subagents"
    sub.mkdir(parents=True)
    (sub / "agent-a77.jsonl").write_text(json.dumps({"message": {"content": [{"type": "text", "text": "1. the well sits wrong in the yard\n"}]}}) + "\n")
    monkeypatch.setattr(ab, "TRANSCRIPTS", tmp_path / "projects")
    with pytest.raises(ab.MissingRecord, match=r"no reply kept for round 2 \(quote-check"):
        ab.bundle(root, "round:quote-check|q:0105@3", tmp_path / "out")  # 368's rulings: never a bundle of "no reply kept"
    assert not (tmp_path / "out").exists()
    manifest = ab.bundle(root, "round:quote-check|q:0105@3", tmp_path / "out", "round 2 ran before replies were kept").read_text()
    assert "## Missing from the record (bundled anyway: round 2 ran before replies were kept)" in manifest
    assert "Owed by: quote-check:0105#bath - a note's passage changed" in manifest, "what made the round due"
    assert "Owed by: (not recorded" in manifest and "- NEW: the well sits wrong in the yard" in manifest
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


def test_an_edit_reversal_bundles_every_check_on_its_file_and_its_history(tmp_path: pathlib.Path, monkeypatch, capsys) -> None:  # noqa: ANN001
    """368's ruling on 0047 (2026-10-11): a reversal the edit wire caught names a FILE, and its bundle had no rounds, no diffs and
    an empty cascade. Now its rounds are every check's on the file's subject and its A -> B -> A the file's own history; with
    neither it is refused."""
    import subprocess

    root = tmp_path / "c"
    root.mkdir()
    git = ["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / ".specify").mkdir()
    (root / ".specify" / "feature.json").write_text('{"feature_directory": "specs/343-x"}')
    (root / "specs" / "368-x").mkdir(parents=True)
    monkeypatch.setenv("L7R_FEATURE_DIRECTORY", "specs/368-x")
    monkeypatch.setenv("L7R_EVENTS_DIR", str(tmp_path / "events"))
    q = root / "research" / "questions"
    q.mkdir(parents=True)
    page = q / "0047-privies.drawing.html"
    for text in ("<p>far corner</p>", "<p>center</p>", "<p>far corner</p>"):
        page.write_text(text)
        subprocess.run([*git, "add", "-A"], check=True)
        subprocess.run([*git, "commit", "-qm", text], check=True)
    trigger = f"reversal:{page}"
    ha.trip(root, trigger, "reversal", str(page), "A -> B -> A", 1)
    reply = tmp_path / "r.md"
    reply.write_text("1. the reach is measured from the privy's far corner\n")
    (root / ".git" / "checks-open.json").write_text(
        json.dumps(
            {
                "dispatches": {
                    "t1": {"check": "record-format", "subjects": ["q:0047"], "t": 1, "state": "answered", "reply": str(reply)},
                    "t2": {"check": "quote-check", "subjects": ["q:0047"], "t": 2, "state": "answered", "reply": str(reply)},
                    "t3": {"check": "quote-check", "subjects": ["q:0105"], "t": 3, "state": "answered", "reply": str(reply)},
                }
            }
        )
    )
    manifest = ab.bundle(root, trigger, tmp_path / "out").read_text()
    assert "## Rounds - every check on q:0047" in manifest and "### Round 1: record-format" in manifest and "### Round 2: quote-check" in manifest
    assert "### Round 3" not in manifest, "another subject's round is not this file's"
    diff = (tmp_path / "out" / "edits.diff").read_text()
    assert "research/questions/0047-privies.drawing.html" in manifest and diff.count("+<p>far corner</p>") == 2 and "+<p>center</p>" in diff
    ha.trip(root, "reversal:q:0047@4", "reversal", "q:0047", "a block dropped earlier is back", 2)  # the block wire's form
    sub = ab.bundle(root, "reversal:q:0047@4", tmp_path / "out1").read_text()
    assert "## Rounds - every check on q:0047" in sub and "### Round 2: quote-check" in sub and (tmp_path / "out1" / "edits.diff").is_file()
    (root / ".git" / "checks-open.json").write_text("{}")
    other = root / "a.md"
    ha.trip(root, f"reversal:{other}", "reversal", str(other), "A -> B -> A", 2)
    assert ab.main([f"reversal:{other}", "--root", str(root), "--out", str(tmp_path / "out2")]) == 2
    assert "a reversal with no check rounds" in capsys.readouterr().err and not (tmp_path / "out2").exists()
    assert ab.main([f"reversal:{other}", "--root", str(root), "--out", str(tmp_path / "out2"), "--missing-ok", "gone"]) == 2, "two words"
    assert ab.main([f"reversal:{other}", "--root", str(root), "--out", str(tmp_path / "out2"), "--missing-ok", "a hand edit"]) == 0
    el = _load("event_log")
    assert el.feature_of(root) == "368-x", "a page session logs under its own feature, not the clone's"


def test_a_feature_with_no_event_log_bundles_an_empty_cascade(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    # 368's check session, 2026-10-10: a reversal tripwire on a feature whose sessions had logged nothing crashed the bundle
    import subprocess

    root = tmp_path / "c"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / ".specify").mkdir()
    (root / ".specify" / "feature.json").write_text('{"feature_directory": "specs/368-x"}')
    (root / "specs" / "368-x").mkdir(parents=True)
    monkeypatch.setenv("L7R_EVENTS_DIR", str(tmp_path / "no-events"))
    manifest = ab.bundle(root, "red-gate", tmp_path / "out").read_text()
    assert "the last 0 edits and dispatches on the feature" in manifest
    assert (tmp_path / "out" / "cascade.txt").read_text() == "\n"


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


def test_a_finding_is_read_whole_and_a_re_raised_one_is_repeated() -> None:
    """343's and 368's rulings, 2026-10-11: a summary cut at the colon leading into its bullets; re-raised findings marked NEW
    when reworded; bundle paths and confirmations listed as findings; a fix that put back words another fix took out unseen."""
    r1 = (
        "1. the tract rule reads over the holdings: no tract is turned apart from the next:\n   - 0006 says each holding\n"
        "   - claims.md agrees\n\n- /tmp/l7r-check/x/MANIFEST.md\n- the rest of the tab matches the pages\n"
    )
    (f,) = ab.findings_of(r1)
    assert f.startswith("the tract rule") and "0006 says each holding" in f and "claims.md agrees" in f, f
    assert ab.findings_of("- /tmp/l7r-check/x/MANIFEST.md\n- **VOCABULARY** 'genka' is not glossed\n- ok, nothing else\n") == ["**VOCABULARY** 'genka' is not glossed"]
    assert ab._repeats('GAPS: 0076 says "pines lined the approach to the hall"', ['ACCURACY 2: the modal leaves out "pines lined the approach to the hall"'])
    assert ab._repeats("D2: 0115 gives the gate's roof and lookout windows", ["D2 the roof of the gate and its lookout windows, from 0115"])
    assert not ab._repeats("D2: 0115 gives the gate's roof", ["D3: 0090 names the clerks"])
    (m1, m2) = ab.mark_rounds(["1. the posts are drawn too dark for a gate\n", "1. a gate's posts drawn too dark\n"])
    assert m1[0][0] == "NEW"
    edit = "EDIT modals/sheet/garden-pond.md\n<<<\na dry garden of raked sand\n===\na dry garden of stones and raked gravel\n>>>\n"
    others = [("a dry garden of stones and gravel", "a dry garden")]  # another check's fix took 'stones' and 'gravel' out
    marks = ab.mark_rounds([edit], others)[0]
    assert any(k == "REVERSING" and "adds back" in f for k, f in marks), marks
    assert not any(k == "REVERSING" for k, _f in ab.mark_rounds([edit], [("a dry garden of reeds", "a dry garden")])[0]), "no words back: no reversal"


def test_a_round_trigger_lost_from_the_owed_record_still_bundles_its_rounds(tmp_path: pathlib.Path) -> None:
    """343's M1c: a wave of 13 refused modal-form rounds kept few of their triggers (an unlocked write), and each bundle came
    out with no Rounds and no edits. The unit is read from the trigger; a round trigger with no rounds at all is refused."""
    import subprocess

    root = tmp_path / "c"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / ".specify").mkdir()
    (root / ".specify" / "feature.json").write_text('{"feature_directory": "specs/343-x"}')
    (root / "specs" / "343-x").mkdir(parents=True)
    modal = root / "l7r" / "diagram" / "interactive" / "assets" / "modals" / "sheet"
    modal.mkdir(parents=True)
    (modal / "door.md").write_text("About: a door.\n\nName: door\nEntry: research/questions/0104-genkan.html\n")
    (root / "research" / "questions").mkdir(parents=True)
    (root / "research" / "questions" / "0104-genkan.html").write_text("<p>a page</p>")
    reply = tmp_path / "r.md"
    reply.write_text("1. the door's About repeats the Name\n\nEDIT l7r/diagram/interactive/assets/modals/sheet/door.md\n<<<\na door.\n===\na plank door.\n>>>\n")
    (root / ".git" / "checks-open.json").write_text(json.dumps({"dispatches": {"t1": {"check": "modal-form", "subjects": ["modal:sheet/door"], "t": 1, "state": "answered", "reply": str(reply)}}}))
    assert ha.unit_of("round:modal-form|modal:sheet/door@3") == "modal-form|modal:sheet/door" and ha.unit_of("red-gate") == ""
    manifest = ab.bundle(root, "round:modal-form|modal:sheet/door@3", tmp_path / "out").read_text()
    assert "### Round 1: modal-form" in manifest and "the owed round is the counter's round 3" in manifest.lower()
    assert "- NOT APPLIED: l7r/diagram/interactive/assets/modals/sheet/door.md: 'a door.' -> 'a plank door.'" in manifest
    assert "(not in arbiter-owed.json) - the unit read from the trigger" in manifest
    # 368's privy ruling: the pages a pop-up's Entry: and Drawing: name are in edits.diff, since an edit there re-owes it
    assert ab.subject_files(root, "modal:sheet/door") == ["l7r/diagram/interactive/assets/modals/sheet/door.md", "research/questions/0104-genkan.html"]
    assert "research/questions/0104-genkan.html" in manifest
    with pytest.raises(ab.MissingRecord, match="a round trigger with no rounds"):
        ab.bundle(root, "round:modal-form|modal:sheet/gate@3", tmp_path / "out2")


def test_a_unit_s_cascade_and_oscillation_are_its_own_files(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """343's clerks--seats and office-hall rulings: feature 368's 0047 reversal was listed under every pop-up's Oscillation."""
    root = _clone(tmp_path)
    (root / "specs" / "375-x").mkdir(parents=True)
    monkeypatch.setenv("L7R_EVENTS_DIR", str(tmp_path / "ev"))
    el = _load("event_log")
    for path, old, new in (("/c/q/0047.drawing.html", "a", "b"), ("/c/q/0047.drawing.html", "b", "a"), ("/c/m/door.md", "x", "y")):
        el.append({"hook_event_name": "PreToolUse", "cwd": str(root), "tool_name": "Edit", "tool_input": {"file_path": path, "old_string": old, "new_string": new}})
    out = tmp_path / "o"
    out.mkdir()
    cascade, osc = ab.flow_sections(root, out, root / "specs" / "375-x", ["m/door.md"])
    assert "none on the unit's files" in osc and "0047" not in (out / "cascade.txt").read_text() and "door.md" in (out / "cascade.txt").read_text()
    _c, osc_all = ab.flow_sections(root, out, root / "specs" / "375-x", [])
    assert "0047.drawing.html" in osc_all, "a feature-wide trigger keeps the feature's oscillation"


def test_a_unit_s_cascade_falls_back_to_its_git_log(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """374's bridgehead ruling: cascade.txt read 0 edits on the pop-up beside three commits on it - apply-edits and scripted
    edits never pass the Edit tool, so the event log held none; the git log of the unit's files stands in."""
    import subprocess

    root = tmp_path / "c"
    root.mkdir()
    git = ["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / ".specify").mkdir()
    (root / ".specify" / "feature.json").write_text('{"feature_directory": "specs/375-x"}')
    (root / "specs" / "375-x").mkdir(parents=True)
    (root / "m").mkdir()
    for text, msg in (("a", "first words"), ("b", "second words")):
        (root / "m" / "door.md").write_text(text)
        subprocess.run([*git, "add", "-A"], check=True)
        subprocess.run([*git, "commit", "-q", "-m", msg], check=True)
    (root / "other.md").write_text("x")
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "not the unit"], check=True)
    monkeypatch.setenv("L7R_EVENTS_DIR", str(tmp_path / "no-events"))
    out = tmp_path / "o"
    out.mkdir()
    cascade, _osc = ab.flow_sections(root, out, root / "specs" / "375-x", ["m/door.md"])
    lines = (out / "cascade.txt").read_text().splitlines()
    assert [ln.split(" ", 3)[3] for ln in lines] == ["first words", "second words"], lines
    assert "the last 2 edits on the unit's files (from the git log" in cascade
    assert ab.git_flow(tmp_path / "not-a-repo", ["m/door.md"]) == []


def test_triggers_tripped_at_once_are_all_kept(tmp_path: pathlib.Path) -> None:
    """The lost-write race behind 343's empty bundles: 20 processes tripping at once each keep their trigger."""
    import subprocess
    import sys

    root = _clone(tmp_path)
    lib = str(pathlib.Path(ha.__file__).parent)
    code = "import sys, pathlib; sys.path.insert(0, sys.argv[1]); import hm_arbiter as h; i = sys.argv[3]; h.trip(pathlib.Path(sys.argv[2]), f'round:modal-form|modal:sheet/m{i}@3', 'round', f'modal-form|modal:sheet/m{i}', 'd', 1.0)"
    procs = [subprocess.Popen([sys.executable, "-c", code, lib, str(root), str(i)]) for i in range(20)]
    assert all(p.wait(timeout=60) == 0 for p in procs)
    assert len(ha.owed(root)) == 20


def test_an_ask_an_earlier_round_said_no_page_holds_is_repeated() -> None:
    """343's main-gate ruling: round 1 said the posts' real color needs new research (D2); round 2 asked for it as NEW."""
    r1 = "1. D3 the gate's roof is drawn flat\n\nThe posts' real color (D2): no page holds it - supplying it needs new research from 0093.\n"
    r2 = "1. D2: 0093 - the tab should give the posts' real color, not the drawn dark\n"
    m1, m2 = ab.mark_rounds([r1, r2])
    assert [k for k, _f in m1] == ["NEW"] and m2[0][0] == "REPEATED", (m1, m2)


def test_the_cascade_counts_only_the_dispatches_since_the_last_landing(tmp_path: pathlib.Path) -> None:
    """Feature 374 (the round arbiter's cascade@1 tooling fix): a landed batch's dispatches were counted against the next
    batch's changed lines; the window opens at the merge base's commit time, and a ruling made before it sets no floor."""
    hc = _load("hm_checks")
    state = {"dispatches": {"a": {"t": 10.0}, "b": {"t": 20.0}, "c": {"t": 30.0}, "d": {}}}
    assert hc.dispatches_since(state, 15.0) == 2 and hc.dispatches_since(state, 0.0) == 4
    state["dispatches"]["e"] = {"t": 40.0, "prewrite": True}
    assert hc.dispatches_since(state, 0.0) == 4, "feature 398's cascade@1: a pre-write source-reader read is not counted"
    rec: dict = {}
    hc.dispatch(rec, "n", "source-reader", "m", "owed-checks: source-reader\n", 1.0)
    hc.dispatch(rec, "u", "source-reader", "m", "owed-checks: source-reader\nunit: source-reader:0270#k abc\n", 1.0)
    assert rec["dispatches"]["n"]["prewrite"] and not rec["dispatches"]["u"]["prewrite"]
    assert hc.window_start(tmp_path) == 0.0, "no repository: the window is the whole state"
    root = tmp_path / "c"
    root.mkdir()
    (root / ".git").mkdir()
    (root / ".specify").mkdir()
    (root / ".specify" / "feature.json").write_text('{"feature_directory": "specs/375-x"}')
    ha.trip(root, "cascade@1", "cascade", "", "40 check dispatches over 10 changed lines", 1)
    ha.record_ruling(root, "cascade@1", {"ruling": "continue", "why": "a landed batch's checks"}, "round-arbiter", now="2026-10-10T01:00:00Z")
    assert ha.cascade_state(root, 0.0) == ("cascade@2", 40)
    after = ha._epoch("2026-10-11T00:00:00Z")
    assert ha.cascade_state(root, after) == ("cascade@2", 0), "a ruling before the window sets no floor"
    assert ha._epoch("not a time") == 0.0


def test_the_manifest_names_only_the_feature_files_it_copied(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 335's round arbiter, 2026-10-11, `ask:f335-garden-modal-depiction`: the MANIFEST said `request.md` and
    `spec.md` were beside it, and the bundle had neither."""
    import subprocess

    root = tmp_path / "c"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / ".specify").mkdir()
    (root / ".specify" / "feature.json").write_text('{"feature_directory": "specs/368-x"}')
    (root / "specs" / "368-x").mkdir(parents=True)
    monkeypatch.setenv("L7R_EVENTS_DIR", str(tmp_path / "no-events"))
    manifest = ab.bundle(root, "red-gate", tmp_path / "out").read_text()
    assert "beside this file: `request.md`" not in manifest.lower() and "`spec.md` beside this file" not in manifest
    assert "NOT in this bundle: request.md, spec.md - found in none of: specs/368-x" in manifest
    assert not (tmp_path / "out" / "request.md").exists() and not (tmp_path / "out" / "spec.md").exists()
    # an ask naming its feature finds that feature's files where the active one has none; a half-present pair names its half
    d = root / "specs" / "335-garden"
    d.mkdir()
    (d / "request.md").write_text("the GM's words")
    manifest = ab.bundle(root, "ask:f335-garden-modal-depiction", tmp_path / "out2").read_text()
    assert "Beside this file: `request.md` (the GM's words, from specs/335-garden)." in manifest
    assert "NOT in this bundle: spec.md" in manifest and (tmp_path / "out2" / "request.md").read_text() == "the GM's words"
    (d / "spec.md").write_text("the spec")
    manifest = ab.bundle(root, "ask:f335-garden-modal-depiction", tmp_path / "out3").read_text()
    assert "`spec.md` (the spec, from specs/335-garden)" in manifest and "NOT in this bundle" not in manifest
    assert (tmp_path / "out3" / "spec.md").read_text() == "the spec"


def test_the_nit_an_accept_asked_for_answers_its_unit_again(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 374 wave 120: the bridgehead pop-up's nit, made as the accept asked, re-owed the check the ruling had closed and
    a second ruling was spent on it. `make arbiter-nit` answers the unit again - only for the wording the ruling quotes."""
    import json
    import sys
    import types

    calls: list[tuple[str, dict]] = []
    fake = types.ModuleType("record_owed")
    fake.answer = lambda root, check, result, **kw: calls.append((check, kw)) or [f"{check}:x"]  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "record_owed", fake)
    monkeypatch.delenv("L7R_FEATURE_DIRECTORY", raising=False)
    root = _clone(tmp_path)
    d = root / "specs" / "375-x"
    d.mkdir(parents=True)
    trig = "round:modal-depiction|modal:choice/b@3"
    row = {
        "trigger": trig,
        "kind": "round",
        "unit": "modal-depiction|modal:choice/b",
        "ruling": "accept",
        "why": "converged",
        "what": "About says 'where most people passed' where 0190 says 'where people passed'",
    }
    (d / "arbiter.jsonl").write_text(json.dumps(row) + "\n")
    modal = root / "l7r/diagram/interactive/assets/modals/choice/b.md"
    modal.parent.mkdir(parents=True)
    modal.write_text("About: boards stood where most people passed.\n")
    with pytest.raises(ValueError, match="must hold NEW"):
        ha.nit_answers(root, trig, "where most people passed", "where people passed")
    modal.write_text("About: boards stood where people passed.\n")
    with pytest.raises(ValueError, match="must quote both"):
        ha.nit_answers(root, trig, "stood where", "where people passed")
    with pytest.raises(ValueError, match="no `accept` ruling"):
        ha.nit_answers(root, "round:modal-form|modal:choice/b@3", "where most people passed", "where people passed")
    assert calls == []
    assert ha.nit_answers(root, trig, "where most people passed", "where people passed") == ["modal-depiction:x"]
    assert calls == [("modal-depiction", {"kind": "choice/b"})]


def test_a_capped_round_names_what_owes_it(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 374 wave 120, the arbiter on the seat pop-ups: the round-3 cause (one word on a drawing page) was named nowhere
    in the MANIFEST. The section lists the record's owed reason and the commits on the unit's files since the last round."""
    import subprocess
    import sys
    import time
    import types

    root = tmp_path / "c"
    root.mkdir()
    git = ["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / "m.md").write_text("About: the old word.\n")
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "before the round", "--date", "2020-01-01T00:00:00"], check=True, env={**__import__("os").environ, "GIT_COMMITTER_DATE": "2020-01-01T00:00:00"})
    since = time.time() - 5
    (root / "m.md").write_text("About: the new word.\n")
    subprocess.run([*git, "commit", "-qam", "one word on the page"], check=True)
    unit = types.SimpleNamespace(slug="modal-depiction:choice/x", occasion="a page its Drawing: names moved", check="modal-depiction", subject="choice/x")
    fake = types.ModuleType("record_owed")
    fake.unanswered = lambda r: [unit]  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "record_owed", fake)
    out = tmp_path / "o"
    out.mkdir()
    lines = "\n".join(ab.capped_round_cause(root, out, "modal-depiction", "modal:choice/x", ["m.md"], since))
    assert "## What owes the capped round" in lines and "`modal-depiction:choice/x`: a page its Drawing: names moved" in lines
    assert "one word on the page" in lines and "before the round" not in lines, lines
    assert "+About: the new word." in (out / "owes-round.diff").read_text()
    assert "names moved - NO changed line in `owes-round.diff` names `choice/x`" in lines, "each owe says whether the diff shows its cause"


def test_the_owes_round_diff_starts_at_each_owing_keys_own_last_read() -> None:
    """The round arbiter on round:source-reader|q:0262@8: the diff began at the unit's last dispatch (a read of another key) and
    hid a change made to the owing key after its own clean round."""
    import types

    rounds = [{"t": 100.0, "notes": ["nagaya"]}, {"t": 200.0, "notes": ["izakaya"]}]
    owing = [types.SimpleNamespace(subject="0262#nagaya")]
    assert ab.key_since(rounds, owing, 200.0) == 100.0, "from nagaya's own read, not izakaya's"
    assert ab.key_since(rounds + [{"t": 300.0, "notes": []}], owing, 300.0) == 300.0, "a whole-page round read every key"
    assert ab.key_since(rounds, [types.SimpleNamespace(subject="0262")], 200.0) == 200.0, "a page unit keeps the unit's start"


def test_each_owe_says_whether_the_rounds_diff_shows_its_cause() -> None:
    """The round arbiter's tooling fix on 0219 (feature 374 wave 122): translation-check was owed on a note the diff held only
    as context, and the bundle did not say so - every owed unit now carries whether a changed line names it."""
    diff = "--- a/x.notes.html\n+++ b/x.notes.html\n-<li data-note=\"jawiki-4\">Main-house</li>\n+<li data-note=\"jawiki-4\">Head</li>\n <li data-note=\"kameyama\">same</li>\n"
    assert ab.owe_evidence("translation-check:0219#jawiki-4", diff) == "a changed line in `owes-round.diff` names it"
    assert "NO changed line in `owes-round.diff` names `kameyama`" in ab.owe_evidence("translation-check:0219#kameyama", diff)
    assert "NO changed line" in ab.owe_evidence("record-format:0219", "--- a/0219.html\n+++ b/0219.html\n")  # no note: its subject
    assert ab.owe_evidence("quote-check:0219.drawing#unfootnoted", "") == "a changed line in `owes-round.diff` names it"
    page = "diff --git a/research/questions/0091-x.drawing.html b/research/questions/0091-x.drawing.html\n--- a/research/questions/0091-x.drawing.html\n+++ b/research/questions/0091-x.drawing.html\n-<li>old</li>\n+<li>new</li>\n"
    assert ab.owe_evidence("record-format:0091", page) == "`owes-round.diff` changes a file of 0091", "a page-scoped unit is named by its file"


def test_owe_evidence_names_a_modal_units_keyed_lines() -> None:
    """The round arbiter on inner-court's third depiction round (feature 374 wave 126): a pop-up's own lines never carry
    its path, so the bundle said no line named it while the hunks were its Entry: line and 0091's drawing page."""
    diff = (
        "diff --git a/l7r/diagram/interactive/assets/modals/sheet/inner-court.md b/l7r/diagram/interactive/assets/modals/sheet/inner-court.md\n"
        "--- a/l7r/diagram/interactive/assets/modals/sheet/inner-court.md\n+++ b/l7r/diagram/interactive/assets/modals/sheet/inner-court.md\n"
        "-Entry: research/questions/0091-x.html\n+Entry: research/questions/0116-y.html, research/questions/0091-x.html\n"
        "+a second line of prose\n"
        "diff --git a/research/questions/0091-x.drawing.html b/research/questions/0091-x.drawing.html\n"
        "--- a/research/questions/0091-x.drawing.html\n+++ b/research/questions/0091-x.drawing.html\n-<li>old</li>\n+<li>new</li>\n"
    )
    got = ab.owe_evidence("modal-depiction:sheet/inner-court", diff)
    assert got == "`owes-round.diff` changes its Entry, a continuation, the page 0091-x.drawing.html line(s)", got
    own = diff.split("diff --git a/research")[0]
    assert "NO changed line" in ab.owe_evidence("modal-depiction:sheet/well", own), "another pop-up's file is not its cause"


def test_review_verdicts_reads_the_earlier_rounds_where_the_check_state_kept_none(tmp_path: pathlib.Path) -> None:
    """The round arbiter on three building reviews (feature 374 batch 4): both rounds ran before the check state kept review
    dispatches, and the bundle said there were none to rule on while the verdict record and the ledger had both."""
    (tmp_path / ".git" / "review-verdicts").mkdir(parents=True)
    (tmp_path / ".git" / "review-verdicts" / "building-review--ubame-magistracy.json").write_text('{"verdict": "PASS"}')
    (tmp_path / "dev").mkdir()
    (tmp_path / "dev" / "review-ledger.md").write_text("| 2026-10-10 | building-review | ubame-magistracy round 2 | clean |\n| 2026-10-10 | glyph-check | ubame-magistracy | clean |\n")
    out = tmp_path / "out"
    out.mkdir()
    got = "\n".join(ab.review_verdicts(tmp_path, out, "building-review--ubame-magistracy"))
    assert "ubame-magistracy round 2" in got and "glyph-check" not in got
    assert (out / "earlier-verdict.json").read_text() == '{"verdict": "PASS"}'
    assert ab.review_verdicts(tmp_path, out, "building-review--hayakawa-magistracy") == [], "no record, so the gap stands"
    # ...and what was done about that round: the dispositions, the measurements verifying a finding, the sheet's edits since
    (tmp_path / ".git" / "review-dispositions").mkdir()
    (tmp_path / ".git" / "review-dispositions" / "building-review--ubame-magistracy.json").write_text('{"C1": "a confirmation"}')
    (tmp_path / "specs" / "999-x").mkdir(parents=True)
    (tmp_path / "specs" / "999-x" / "measurements.json").write_text(
        json.dumps({"b4-ub-e1": {"verifies": "E1", "subject": "building-review--ubame-magistracy", "method": "the band 140 x 11 ft"}, "other": 3})
    )
    got = "\n".join(ab.review_verdicts(tmp_path, out, "building-review--ubame-magistracy"))
    assert "`b4-ub-e1` verifies E1: the band 140 x 11 ft" in got
    assert (out / "dispositions.json").is_file() and (out / "edits-since-verdict.diff").is_file()


def test_a_batch_members_directory_never_starts_with_a_dash() -> None:
    """The round arbiter's tooling fix (feature 374 batch 4): the tail of a long trigger's slug began with '-'."""
    long = "round:building-review|building-review--county-magistracy-example@4"
    assert not ab.batch_dir(long).startswith("-") and ab.batch_dir(long).endswith("county-magistracy-example-4")


def test_a_modal_form_replys_fix_and_note_lines_are_findings_and_repeat_by_their_rule() -> None:
    """The round arbiter on the servants' quarters form (feature 374 batch 4): its rounds showed no findings, which hid that
    round 3's two research findings repeated round 1's."""
    r1 = "modal-form: x - 2 findings\n\nFIX M5 - About never says what the quarters were built of, or their walls and roof.\nEDIT: none - this needs research.\n\nNOTE M18 - chugen appears unglossed in the Miwa sentence.\n"
    r3 = "FIX M5 - About does not say what the quarters were built of: their walls, their roof and materials are skipped.\nEDIT: none\n"
    assert ab.findings_of(r1) == ["FIX M5 - About never says what the quarters were built of, or their walls and roof.", "NOTE M18 - chugen appears unglossed in the Miwa sentence."]
    marked = ab.mark_rounds([r1, r3])
    assert marked[1][0][0] == "REPEATED", marked
    assert not ab._repeats("FIX M3 - the second paragraph runs to six sentences", ab.findings_of(r1))


def test_the_bundle_prints_the_round_counters_epoch_and_what_it_counted(tmp_path: pathlib.Path) -> None:
    """Feature 374 batch 5, the round arbiter's tooling fix: the counter reported round 5 for a batch's first round, and the
    bundle could not show why. It now prints the epoch and the rounds counted after it; a bare key reads as epoch 0."""
    import subprocess

    def git(*a: str) -> None:
        subprocess.run(["git", "-C", str(tmp_path), "-c", "user.email=t@t", "-c", "user.name=t", *a], check=True, capture_output=True)

    git("init", "-q")
    assert ab.round_counter(tmp_path, "u") == [], "no record: nothing printed"
    (tmp_path / ".specify").mkdir()
    (tmp_path / ".specify" / "feature.json").write_text('{"feature_directory": "specs/900-x"}')
    (tmp_path / ".git" / "review-rounds.json").write_text('{"specs/900-x": {"u": ["k1", "k2@1000", "k3@4000000000"]}}')
    assert "never (nothing landed)" in ab.round_counter(tmp_path, "u")[0] and "3 of the 3" in ab.round_counter(tmp_path, "u")[0]
    (tmp_path / "specs" / "900-x").mkdir(parents=True)
    (tmp_path / "specs" / "900-x" / "tasks.md").write_text("# Tasks\n")
    git("add", "-A")
    git("commit", "-qm", "landed")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    line = ab.round_counter(tmp_path, "u")[0]
    assert "1 of the 3" in line and "k3@4000000000" in line and "k1," not in line, line


def test_a_record_checks_round_counter_reads_the_record_checks_count(tmp_path: pathlib.Path) -> None:
    """Feature 374 batch 7, the round arbiter's tooling fix (round:quote-check|q:0019@3): the bundle read the review checks'
    counter for a record check and printed "0 of the 0 kept" for a trigger that fired at round 3. A record check's unit is
    counted by `hm_checks.py`, so its count and its rebase are read from that state."""
    import subprocess

    subprocess.run(["git", "-C", str(tmp_path), "init", "-q"], check=True, capture_output=True)
    (tmp_path / ".git" / "checks-open.json").write_text('{"rounds": {"quote-check|q:0019": 3}, "rebased": {"record-format|q:0019": {"fp": "x", "n": 2}}}')
    line = ab.round_counter(tmp_path, "quote-check|q:0019")[0]
    assert "3 round(s) counted" in line and "quote-check|q:0019" in line and "rebased" not in line, line
    (tmp_path / ".git" / "checks-open.json").write_text('{"rounds": {"record-format|q:0019": 4}, "rebased": {"record-format|q:0019": {"fp": "x", "n": 2}}}')
    assert "rebased the count at round 2" in ab.round_counter(tmp_path, "record-format|q:0019")[0]
    assert ab.record_round_counter(tmp_path, "nothing|q:1") == []


def test_an_accept_on_a_review_unit_stands_while_its_sheet_reads_as_ruled(tmp_path: pathlib.Path) -> None:
    """Feature 374 batch 5: the review gate refused two sheets the round arbiter had accepted - their last verdicts were
    NEEDS-WORK at an older key. A unit's round ruling now carries the sheet's content key, and stands for it while it holds."""
    d = tmp_path / "specs" / "900-x"
    d.mkdir(parents=True)
    rows = [
        {"trigger": "round:building-review|u@3", "unit": "u", "ruling": "continue", "content_key": "k1"},
        "not json",
        {"trigger": "round:building-review|u@4", "unit": "u", "ruling": "accept", "content_key": "k2"},
    ]
    (d / "arbiter.jsonl").write_text("\n".join(r if isinstance(r, str) else json.dumps(r) for r in rows) + "\n")
    assert ha.unit_ruled(d, "u", "k2") == "round:building-review|u@4"
    assert ha.unit_ruled(d, "u", "k1") == "", "a continue is no verdict"
    assert ha.unit_ruled(d, "u", "k3") == "" and ha.unit_ruled(d, "u", "") == "", "the sheet moved since the ruling"
    assert ha.unit_ruled(tmp_path, "u", "k2") == "", "no arbiter record"
    assert ha.row_unit({}, "round:building-review|u@4") == ha.unit_of("round:building-review|u@4")
    assert ha.unit_content_key(tmp_path, "building-review--nowhere") == ""


def test_a_red_gate_bundle_names_what_each_red_gate_failed_on(tmp_path: pathlib.Path) -> None:
    """The round arbiter's tooling fixes on red-gate@2026-10-12T13:55:48Z (feature 374 batch 10) and red-gate@2026-10-17T17:21:08Z
    (feature 385): a red-gate trigger's bundle carries the red `make done` runs of the run log - their phases and failure counts -
    and each run's OWN failed tests by name, never pytest's cumulative lastfailed (stale probe files and other units' tests)."""
    log = tmp_path / "dev" / "run-log" / "2026-10"
    log.mkdir(parents=True)
    (log / "a.json").write_text(
        json.dumps({"utc": "t1", "target": "done", "result": "failed: test-full", "commit": "abc", "failed_tests": 1, "failed_names": ["tests/test_y.py::test_y"]}), encoding="utf-8"
    )
    (log / "b.json").write_text(json.dumps({"utc": "t2", "target": "done", "result": "green"}), encoding="utf-8")
    (log / "c.json").write_text("not json", encoding="utf-8")
    cache = tmp_path / ".pytest_cache" / "v" / "cache"
    cache.mkdir(parents=True)
    (cache / "lastfailed").write_text(json.dumps({"tests/test_zz_probe_a05.py::test_x": True}), encoding="utf-8")
    (runs,) = ab.red_gate_runs(tmp_path)
    assert "t1 at abc: failed: test-full, 1 test(s) failed" in runs and "  - tests/test_y.py::test_y" in runs and "t2" not in runs
    assert "zz_probe" not in runs, "the cumulative cache is not read"
    (empty,) = ab.red_gate_runs(tmp_path / "nowhere")
    assert "(no red make done in the run log)" in empty


def test_a_red_gate_bundle_skips_a_tree_moved_abort_and_shows_the_diff_between_reds(tmp_path: pathlib.Path) -> None:
    """Feature 385 T49 (the round arbiter's fix on red-gate@2026-10-18T16:44:54Z): a tree-moved abort, whose test-full never ran,
    is not among the counted reds, and between two reds the bundle carries the diff between their commits, its stat first; two reds
    on one commit say that nothing between them is recorded."""

    def git(*a: str) -> str:
        return subprocess.run(["git", "-C", str(tmp_path), *a], capture_output=True, text=True, check=True).stdout.strip()

    git("init", "-q")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    (tmp_path / "f.py").write_text("x = 1\n")
    git("add", "-A")
    git("commit", "-qm", "one")
    c1 = git("rev-parse", "HEAD")
    (tmp_path / "f.py").write_text("x = 2\n")
    git("commit", "-qam", "two")
    c2 = git("rev-parse", "HEAD")
    log = tmp_path / "dev" / "run-log" / "2026-10"
    log.mkdir(parents=True)
    rows = [("a", "t1", c1, "failed: test-full"), ("b", "t2", c2, "failed: tree moved"), ("c", "t3", c2, "failed: coverage"), ("d", "t4", c2, "failed: lint")]
    for name, utc, commit, result in rows:
        (log / f"{name}.json").write_text(json.dumps({"utc": utc, "target": "done", "result": result, "commit": commit}), encoding="utf-8")
    (runs,) = ab.red_gate_runs(tmp_path)
    assert "t2" not in runs, "the tree-moved abort is no red gate"
    assert f"between {c1} and {c2}:" in runs and "-x = 1" in runs and "+x = 2" in runs and "f.py | 2 +-" in runs, "the diff, its stat first"
    assert "the same commit; uncommitted edits between them are not recorded" in runs, "t3 and t4 share a commit"


def test_a_red_gate_bundle_counts_only_its_own_lines_runs_and_caps_a_huge_diff(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """Feature 392 (the round arbiter's fixes on red-gate@2026-10-19T00:59:47Z and 02:31:38Z): the shared run log carried another
    session's red (a land-tooling gate on main's tree) into this feature's bundle, with a 4 MB diff. Only runs on HEAD's
    first-parent line are counted, and a diff past the cap is shown by its stat."""

    def git(*a: str) -> str:
        return subprocess.run(["git", "-C", str(tmp_path), *a], capture_output=True, text=True, check=True).stdout.strip()

    git("init", "-q", "-b", "main")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    (tmp_path / "f.py").write_text("x = 1\n")
    git("add", "-A")
    git("commit", "-qm", "one")
    c1 = git("rev-parse", "HEAD")
    git("checkout", "-qb", "side")
    (tmp_path / "g.py").write_text("y = 1\n")
    git("add", "-A")
    git("commit", "-qm", "side")
    other = git("rev-parse", "HEAD")
    git("checkout", "-q", "main")
    (tmp_path / "f.py").write_text("x = 2\n" * 40)
    git("commit", "-qam", "two")
    git("merge", "-q", "--no-edit", "side")
    c2 = git("rev-parse", "HEAD")
    log = tmp_path / "dev" / "run-log" / "2026-10"
    log.mkdir(parents=True)
    for name, utc, commit in (("a", "t1", c1), ("b", "t2", other[:9]), ("c", "t3", c2)):
        (log / f"{name}.json").write_text(json.dumps({"utc": utc, "target": "done", "result": "failed: test-full", "commit": commit}), encoding="utf-8")
    monkeypatch.setattr(ab, "BETWEEN_DIFF_LINES", 10)
    (runs,) = ab.red_gate_runs(tmp_path)
    assert "t2" not in runs, "a red on another line (the merged side branch) is not this feature's"
    assert "t1" in runs and "t3" in runs
    assert "its stat alone" in runs and "+x = 2" not in runs, "the long diff is cut to its stat"


def test_the_exported_feature_outranks_the_pointer(tmp_path: pathlib.Path, monkeypatch) -> None:  # noqa: ANN001
    """The round arbiter on hour:391-comparative-money-sources@2 (2026-10-18): a session working 390 with SPECIFY_FEATURE
    exported, while `.specify/feature.json` named 391 (its last claim), had every hour charged to 391. The exported feature wins
    when its directory exists; a page session's own directory still outranks both; an unknown name falls back to the pointer."""
    root = tmp_path / "c"
    for d in ("specs/390-a", "specs/391-b", "specs/368-x", ".specify"):
        (root / d).mkdir(parents=True)
    (root / ".specify" / "feature.json").write_text('{"feature_directory": "specs/391-b"}')
    monkeypatch.delenv("L7R_FEATURE_DIRECTORY", raising=False)
    monkeypatch.setenv("SPECIFY_FEATURE", "390-a")
    assert ha.feature_dir(root) == root / "specs" / "390-a"
    monkeypatch.setenv("SPECIFY_FEATURE", "999-gone")
    assert ha.feature_dir(root) == root / "specs" / "391-b", "a name with no directory falls back to the pointer"
    monkeypatch.setenv("L7R_FEATURE_DIRECTORY", "specs/368-x")
    assert ha.feature_dir(root) == root / "specs" / "368-x", "a page session's own directory outranks both"


def test_the_gate_asks_whether_a_red_gate_is_owed(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Feature 405 T44 (D18): T11's 05:09 `make land` ran its gate past `red-gate@2026-10-21T05:02:38Z`, owed and never ruled -
    the hook asks only of a typed `make done`; the `done` recipe and `make land` now ask `gate-held` themselves."""
    root = _clone(tmp_path)
    monkeypatch.chdir(root)
    assert ha.main(["gate-held"]) == 0, "nothing owed: the gate runs"
    ha.trip(root, "round:quote-check|q:1@3", "round", "quote-check|q:1", "d", 1)
    assert ha.main(["gate-held"]) == 0, "a round trigger holds its unit, not the gate"
    ha.trip(root, "red-gate@2026-10-21T05:02:38Z", "red-gate", "", "a second red make done in a row", 2)
    assert ha.main(["gate-held"]) == 1
    assert 'make arbiter-bundle TRIGGER="red-gate@2026-10-21T05:02:38Z"' in capsys.readouterr().err
    done = pathlib.Path(__file__).resolve().parents[2].joinpath("Makefile").read_text(encoding="utf-8").split("\ndone:", 1)[1]
    assert "hm_arbiter.py\"; [ ! -f \"$$h\" ] || python3 \"$$h\" gate-held" in done.splitlines()[1], "the gate's first step"


def test_an_asked_spec_review_s_accept_stands_as_the_spec_s_verdict(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Feature 409: 408's `ask:408-spec-round3` accept named no review, and `review-gate.sh` ran a third spec round anyway."""
    root = _clone(tmp_path)
    d = root / "specs" / "375-x"
    d.mkdir(parents=True)
    (d / "spec.md").write_text("# Feature 375\n\n## Requirements\n\n- FR-001: x.\n")
    monkeypatch.chdir(root)
    assert ha.main(["ask", "375-spec-round3", "may the spec stand without a third round?", "both"]) == 2, "spec or plan only"
    assert ha.main(["ask", "375-spec-round3", "may the spec stand without a third round?", "spec"]) == 0
    said = capsys.readouterr().out
    assert "an accept stands as the spec review's verdict" in said
    assert ha.owed(root)["ask:375-spec-round3"]["review"] == "spec"
    assert "an accept stands as the spec review's verdict" in ha.owed(root)["ask:375-spec-round3"]["detail"], "the arbiter's bundle shows it"
    ruling = root / "r.json"
    ruling.write_text(json.dumps({"ruling": "accept", "why": "converged, one wording fix", "what": "the spec stands"}))
    assert ha.main(["ruled", "ask:375-spec-round3", str(ruling), "--as", "round-arbiter"]) == 0
    assert ha.spec_ruled(d) == "ask:375-spec-round3", "the ruling is the spec's verdict"
    (d / "spec.md").write_text((d / "spec.md").read_text() + "- FR-002: y.\n")
    assert ha.spec_ruled(d) == "", "a spec edited after the ruling is not covered by it"


def test_an_ask_with_no_review_is_recorded_as_before_and_a_review_like_subject_only_hints(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Feature 409 FR-001: no REVIEW=, no review, whatever the SUBJECT says - a hint, recording nothing more."""
    root = _clone(tmp_path)
    monkeypatch.chdir(root)
    assert ha.main(["ask", "375-plan-round3", "may the plan stand without a third round?", ""]) == 0
    assert "hint - if this asks about a spec or plan review" in capsys.readouterr().out
    assert "review" not in ha.owed(root)["ask:375-plan-round3"]
    assert ha.main(["ask", "which-route", "which route should the landing take?"]) == 0
    assert "hint" not in capsys.readouterr().out and "review" not in ha.owed(root)["ask:which-route"]


def test_make_arbiter_ask_passes_review_through() -> None:
    repo = pathlib.Path(__file__).resolve().parents[2]
    dry = subprocess.run(["make", "-n", "-C", str(repo), "arbiter-ask", "SUBJECT=s", "WHY=why it is asked", "REVIEW=plan"], capture_output=True, text=True, check=False).stdout
    assert 'hm_arbiter.py ask "s" "why it is asked" "plan"' in dry


def test_an_ask_naming_a_feature_by_number_is_filed_under_that_feature(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """2026-10-24: `ask:414-round3`, asked while the clone's active feature was 416, was filed and ruled under 416."""
    root = _clone(tmp_path)
    for name in ("375-x", "414-price-stability"):
        (root / "specs" / name).mkdir(parents=True)
    monkeypatch.chdir(root)
    assert ha.main(["ask", "414-round3", "may the sixteen units close on round 2?"]) == 0
    assert ha.owed(root)["ask:414-round3"]["feature"] == "414-price-stability"
    ruling = root / "r.json"
    ruling.write_text(json.dumps({"ruling": "accept", "why": "round 2 found only wording"}))
    assert ha.main(["ruled", "ask:414-round3", str(ruling), "--as", "round-arbiter"]) == 0
    d = root / "specs" / "414-price-stability"
    assert "ask:414-round3" in (d / "arbiter.jsonl").read_text() and (d / "gm-review.jsonl").is_file()
    assert not (root / "specs" / "375-x" / "arbiter.jsonl").exists(), "the active feature holds none of it"
    assert ha.main(["ask", "414-round3", "may the sixteen units close on round 2?"]) == 1, "already ruled, found in 414"
    assert ha.feature_dir(root, "ask:which-route") == root / "specs" / "375-x", "an ask naming no feature stays with the active one"
