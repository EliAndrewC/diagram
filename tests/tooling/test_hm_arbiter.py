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
    numbered = "1. **the dike's breadth** told as a convention\n\n- the sluices match the page and are fine\n"
    assert ab.mark_rounds([numbered]) == [[("NEW", "**the dike's breadth** told as a convention")]], "confirmations are no finding"
    bold = "**COVERAGE** clean.\n\n- the mottled band is told on the tab\n\n**1. D3: the breadth is told as a convention**\n"
    assert ab.mark_rounds([bold]) == [[("NEW", "D3: the breadth is told as a convention**")]], "the bold numbered heading is read"


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
    (modal / "door.md").write_text("About: a door.\n\nName: door\n")
    reply = tmp_path / "r.md"
    reply.write_text("1. the door's About repeats the Name\n\nEDIT l7r/diagram/interactive/assets/modals/sheet/door.md\n<<<\na door.\n===\na plank door.\n>>>\n")
    (root / ".git" / "checks-open.json").write_text(json.dumps({"dispatches": {"t1": {"check": "modal-form", "subjects": ["modal:sheet/door"], "t": 1, "state": "answered", "reply": str(reply)}}}))
    assert ha.unit_of("round:modal-form|modal:sheet/door@3") == "modal-form|modal:sheet/door" and ha.unit_of("red-gate") == ""
    manifest = ab.bundle(root, "round:modal-form|modal:sheet/door@3", tmp_path / "out").read_text()
    assert "### Round 1: modal-form" in manifest and "the owed round is the counter's round 3" in manifest.lower()
    assert "- NOT APPLIED: l7r/diagram/interactive/assets/modals/sheet/door.md: 'a door.' -> 'a plank door.'" in manifest
    assert "(not in arbiter-owed.json; the unit read from the trigger)" in manifest
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
