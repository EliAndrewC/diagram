"""`scripts/hooks/lib/hm_checks.py` - decide, then freeze (feature 375, FR-003(b)(c), FR-010; plan D4).

Feature 372's 0105 went through about four rounds of five to seven checks in wave 108 because the page was edited while its
checks ran. Each case below is a rule a later session could break without noticing: an edit while a check runs, a check
re-dispatched into an open round, an edit in the apply pass that no check proposed, a different replacement at a proposed
place, a third round with no ruling - and the escapes from a deadlock: a dispatch another guard refused, a check answered.
"""

from __future__ import annotations

import json
import pathlib

from tests.tooling.test_modal_checks import _load

hc = _load("hm_checks")

MANIFEST = "owed-checks: quote-check\nunit: quote-check:0105.drawing#bath-size abc123\nunit: quote-check:0105#well x\n"
MODAL = "owed-checks: modal-depiction\nunit: modal-depiction:sheet/bath f00\n"
PAGE = "/c/research/questions/0105-baths-furo.drawing.html"
REPLY = "quote-check: 0105 - 1 finding\n\n1. the size.\n   EDIT research/questions/0105-baths-furo.drawing.html\n   <<<\n   about 10 by 8 ft\n   ===\n   about 10 by 8 feet\n   >>>\n"


def test_subjects() -> None:
    assert hc.subjects_of_manifest(MANIFEST) == ["q:0105"] and hc.subjects_of_manifest(MODAL) == ["modal:sheet/bath"]
    assert hc.subject_of_path(PAGE) == "q:0105" and hc.subject_of_path("/c/research/questions/0105-baths-furo.notes.html") == "q:0105"
    assert hc.subject_of_path("/c/l7r/diagram/interactive/assets/modals/sheet/bath.md") == "modal:sheet/bath"
    assert hc.subject_of_path("/c/docs/buildings.md") == "" and hc.subject_of_unit("x") == ""


def test_a_page_is_frozen_while_its_check_runs_and_takes_only_the_proposed_edits_after() -> None:
    st: dict = {}
    assert hc.dispatch(st, "t1", "quote-check", "/m", MANIFEST, 0) == ""
    assert "frozen while its checks run (quote-check)" in hc.edit_refusal(st, PAGE, "a", "b", 1), "pending, not yet launched"
    hc.launched(st, "t1", "ag1", background=True)
    assert "frozen" in hc.edit_refusal(st, PAGE, "a", "b", 500), "running: frozen however long"
    assert "silent past 90 minutes" in hc.edit_refusal(st, PAGE, "a", "b", 6000)
    assert hc.edit_refusal(st, "/c/docs/buildings.md", "a", "b", 1) == "", "another file is not frozen"
    hc.returned(st, "ag1", REPLY)
    assert st["edits"]["q:0105"] == [["research/questions/0105-baths-furo.drawing.html", "about 10 by 8 ft", "about 10 by 8 feet"]]
    assert hc.edit_refusal(st, PAGE, "about 10 by 8 ft", "about 10 by 8 feet", 2) == "", "the proposed edit"
    assert hc.edit_refusal(st, PAGE, "8 ft", "8 feet", 2) == "", "a part of it, in place"
    assert "none of the 1 edit(s) they proposed" in hc.edit_refusal(st, PAGE, "8 ft", "9 ft", 2), "another replacement there"
    assert "none of the 1" in hc.edit_refusal(st, PAGE, "the well", "a well", 2), "an edit nobody proposed"
    hc.answered(st, "quote-check", ["q:0105"])
    assert hc.edit_refusal(st, PAGE, "the well", "a well", 3) == "", "answered: free again"


def test_a_check_is_not_re_dispatched_into_a_round_that_is_still_running() -> None:
    st: dict = {}
    hc.dispatch(st, "t1", "quote-check", "/m", MANIFEST, 0)
    hc.dispatch(st, "t2", "record-format", "/m2", MANIFEST.replace("quote-check", "record-format"), 0)
    hc.launched(st, "t1", "ag1", True)
    hc.launched(st, "t2", "ag2", True)
    hc.returned(st, "ag1", "no edits")
    assert "already in q:0105's round" in hc.dispatch(st, "t3", "quote-check", "/m", MANIFEST, 1), "record-format still runs"
    hc.returned(st, "ag2", "")
    assert "no edit to apply" in hc.edit_refusal(st, PAGE, "a", "b", 2)
    assert hc.dispatch(st, "t3", "quote-check", "/m", MANIFEST, 2) == "", "all returned: the next round may start"


def _clone(tmp: pathlib.Path) -> pathlib.Path:
    (tmp / ".git").mkdir()
    (tmp / ".specify").mkdir()
    (tmp / ".specify" / "feature.json").write_text('{"feature_directory": "specs/375-x"}')
    return tmp


def test_the_third_round_goes_to_the_arbiter(tmp_path: pathlib.Path) -> None:
    """FR-010/FR-011: the record checks' cap of two rounds per subject per feature; the third trips the arbiter, whose
    `continue` lifts the cap by one and whose `accept` closes the unit for good."""
    root = _clone(tmp_path)
    ha = _load("hm_arbiter")
    st: dict = {}
    for i in range(2):
        assert hc.dispatch(st, f"t{i}", "quote-check", "/m", MANIFEST, i, root) == ""
        hc.answered(st, "quote-check", ["q:0105"])
    msg = hc.dispatch(st, "t9", "quote-check", "/m", MANIFEST, 5, root)
    assert "round 3 of `quote-check` on q:0105 in this feature passes its cap of 2" in msg and "make arbiter-bundle" in msg
    assert list(ha.owed(root)) == ["round:quote-check|q:0105@3"]
    ha.record_ruling(root, "round:quote-check|q:0105@3", {"ruling": "continue", "why": "a new finding each round", "what": "the notes"}, "round-arbiter")
    assert hc.dispatch(st, "t9", "quote-check", "/m", MANIFEST, 5, root) == "" and ha.owed(root) == {}
    hc.answered(st, "quote-check", ["q:0105"])
    assert "passes its cap of 3" in hc.dispatch(st, "t10", "quote-check", "/m", MANIFEST, 6, root)
    ha.record_ruling(root, "round:quote-check|q:0105@4", {"ruling": "accept", "why": "what is left is wording"}, "round-arbiter")
    assert "the round arbiter closed quote-check|q:0105 (accept)" in hc.dispatch(st, "t11", "quote-check", "/m", MANIFEST, 7, root)
    assert hc.dispatch(st, "ti", "impl-drift", "/m", "unit: impl-drift:x 1\n", 5) == "" and st["dispatches"]["ti"]["subjects"] == []


def test_a_dispatch_another_guard_refused_never_freezes_the_page() -> None:
    st: dict = {}
    hc.dispatch(st, "t1", "quote-check", "/m", MANIFEST, 0)
    assert hc.edit_refusal(st, PAGE, "a", "b", hc.PENDING_S + 1) == "", "never launched: it stops counting"
    hc.dispatch(st, "t2", "modal-depiction", "/m", MODAL, 0)
    hc.launched(st, "t2", "ag2", background=False)
    assert "no edit to apply" in hc.edit_refusal(st, "/c/l7r/diagram/interactive/assets/modals/sheet/bath.md", "a", "b", 1), "a foreground check returns with its call"
    hc.launched(st, "unknown", "agX", True)


def test_apply_edits_takes_only_the_round_s_own_blocks(tmp_path: pathlib.Path) -> None:
    st: dict = {}
    hc.dispatch(st, "t1", "quote-check", "/m", MANIFEST, 0)
    hc.launched(st, "t1", "ag1", True)
    reply = tmp_path / "reply.txt"
    reply.write_text(REPLY)
    cmd = f"make apply-edits FROM={reply}"
    assert "frozen" in hc.apply_refusal(st, cmd, 1)
    hc.returned(st, "ag1", REPLY)
    assert hc.apply_refusal(st, cmd, 2) == ""
    other = tmp_path / "other.txt"
    other.write_text(REPLY.replace("10 by 8 feet", "12 by 9 feet"))
    assert "not one its round's checks returned" in hc.apply_refusal(st, f"make apply-edits FROM={other}", 2)
    assert hc.apply_refusal(st, "make quick", 2) == ""
    log = tmp_path / "agent.output"
    log.write_text(json.dumps({"message": {"content": [{"type": "text", "text": REPLY}]}}) + "\nnot json\n")
    assert hc.apply_refusal(st, f"make apply-edits FROM={log}", 2) == ""
    assert hc._reply_file(str(tmp_path / "missing.txt")) == "" and hc._reply_of(str(tmp_path / "missing.jsonl"), "") == ""


def test_the_hook_entry_points_and_the_state_file(tmp_path: pathlib.Path, monkeypatch, capsys) -> None:  # noqa: ANN001
    (tmp_path / ".git").mkdir()
    (tmp_path / ".specify").mkdir()
    (tmp_path / ".specify" / "feature.json").write_text('{"feature_directory": "specs/375-x"}')
    m = tmp_path / "MANIFEST.md"
    m.write_text(MANIFEST)
    cwd = str(tmp_path)
    agent = {"cwd": cwd, "tool_name": "Agent", "tool_use_id": "t1", "tool_input": {"subagent_type": "quote-check", "prompt": f"read {m}"}}
    assert hc.handle("dispatch", agent, 0) == ""
    assert hc.handle("launched", {**agent, "tool_response": {"status": "async_launched", "agentId": "ag1"}}, 1) == ""
    edit = {"cwd": cwd, "tool_name": "Edit", "tool_input": {"file_path": PAGE, "old_string": "a", "new_string": "b"}}
    assert "frozen" in hc.handle("edit", edit, 2)
    assert hc.handle("edit", {**edit, "tool_input": {**edit["tool_input"], "new_string": 'b FREEZE_OK="the GM asked for it"'}}, 2) == ""
    assert hc.handle("dispatch", {**agent, "tool_input": {"subagent_type": "quote-check", "prompt": f'{m} FREEZE_OK="a backfill run"'}}, 3) == ""
    assert hc.handle("dispatch", {**agent, "tool_input": {"subagent_type": "Explore", "prompt": "x"}}, 3) == ""
    assert hc.handle("returned", {"cwd": cwd, "agent_id": "ag1", "last_assistant_message": REPLY}, 4) == ""
    assert hc.handle("edit", {"cwd": cwd, "tool_name": "Bash", "tool_input": {"command": 'make apply-edits FROM=x FREEZE_OK="a test escape"'}}, 5) == ""
    assert hc.handle("edit", {"cwd": cwd, "tool_name": "Bash", "tool_input": {"command": "ls"}}, 5) == ""
    assert hc.handle("other", {"cwd": cwd}, 5) == ""
    state = json.loads((tmp_path / ".git" / hc.STATE).read_text())
    assert state["feature"] == "375-x" and state["rounds"] == {"quote-check|q:0105": 1}
    hc.record_answer(tmp_path, "quote-check", ["quote-check:0105#well"])
    assert json.loads((tmp_path / ".git" / hc.STATE).read_text())["dispatches"]["t1"]["state"] == "answered"
    (tmp_path / ".specify" / "feature.json").write_text('{"feature_directory": "specs/376-y"}')
    assert hc.handle("dispatch", agent, 6) == ""
    assert json.loads((tmp_path / ".git" / hc.STATE).read_text())["rounds"] == {"quote-check|q:0105": 1}, "a new feature counts afresh"
    monkeypatch.chdir(tmp_path)
    assert hc.main(["close", "q:0105", "x"]) == 2
    assert hc.main(["close", "q:0105", "the agent died silently"]) == 0 and "1 dispatch(es) on q:0105 closed" in capsys.readouterr().out
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO(json.dumps({**edit, "tool_input": {**edit["tool_input"]}})))
    assert hc.main(["edit"]) == 0
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO("not json"))
    assert hc.main(["edit"]) == 0
    assert hc.handle("edit", {"cwd": "/", "tool_name": "Edit"}) == "", "outside any clone"
    wt = tmp_path / "wt"
    wt.mkdir()
    (wt / ".git").write_text(f"gitdir: {tmp_path / '.git' / 'worktrees' / 'wt'}\n")
    (tmp_path / ".git" / "worktrees" / "wt").mkdir(parents=True)
    (tmp_path / ".git" / "worktrees" / "wt" / "commondir").write_text("../..\n")
    assert hc.state_path(str(wt)) == (tmp_path / ".git" / hc.STATE).resolve()
    assert hc.load(tmp_path / "missing.json") == {}


def test_a_ruled_trigger_is_never_put_to_the_arbiter_again(tmp_path: pathlib.Path) -> None:
    """FR-011: one ruling per trigger, binding - the session cannot re-dispatch the arbiter for another answer."""
    root = _clone(tmp_path)
    ha = _load("hm_arbiter")
    m = tmp_path / "MANIFEST.md"
    m.write_text("# Round arbiter bundle\n\ntrigger: reversal:/a.md\n")
    agent = {"cwd": str(root), "tool_name": "Agent", "tool_use_id": "a1", "tool_input": {"subagent_type": "round-arbiter", "prompt": f"{m}"}}
    assert hc.handle("dispatch", agent, 0) == ""
    ha.trip(root, "reversal:/a.md", "reversal", "/a.md", "d", 0)
    page = {"cwd": str(root), "tool_name": "Agent", "tool_use_id": "q1", "tool_input": {"subagent_type": "quote-check", "prompt": "x"}}
    assert "a tripwire is owed its ruling first" in hc.handle("dispatch", page, 1), "a reversal holds every check"
    ha.record_ruling(root, "reversal:/a.md", {"ruling": "accept", "why": "the second wording is the right one"}, "round-arbiter")
    assert "already ruled" in hc.handle("dispatch", agent, 2)
    assert hc.handle("dispatch", page, 3) == ""
    ha.trip(root, "red-gate@1", "red-gate", "", "two red gates", 4)
    gate = {"cwd": str(root), "tool_name": "Bash", "tool_input": {"command": "cd x && make done"}}
    assert "a tripwire is owed its ruling first (red-gate@1" in hc.handle("edit", gate, 5)
    assert hc.handle("edit", {**gate, "tool_input": {"command": 'ARBITER_OK="ruled by hand, GM present" make done'}}, 5) == ""


def test_a_dropped_block_coming_back_between_dispatches_trips_the_reversal_wire(tmp_path: pathlib.Path) -> None:
    """FR-010, from the subject's own history: the versions each dispatch found (feature 372's bath bullet was put back by a
    script, never an Edit)."""
    root = _clone(tmp_path)
    ha = _load("hm_arbiter")
    q = root / "research" / "questions"
    q.mkdir(parents=True)
    page = q / "0105-baths-furo.drawing.html"
    m = tmp_path / "MANIFEST.md"
    m.write_text(MANIFEST)
    bullet = "<li>A plan may draw its bath larger as one of its resident's particulars, up to 18 by 12 ft.</li>\n"
    base = "<h2 id='b'>Baths</h2>\n<ul>\n<li>The bath is drawn 10 by 8 ft beside the kitchen.</li>\n"
    for i, body in enumerate((base + bullet, base, base + bullet.replace("up to", "as large as"))):
        page.write_text(body + "</ul>\n")
        agent = {"cwd": str(root), "tool_name": "Agent", "tool_use_id": f"t{i}", "tool_input": {"subagent_type": "quote-check", "prompt": str(m)}}
        out = hc.handle("dispatch", agent, i)
        if i < 2:
            assert out == ""
            hc.handle("launched", {**agent, "tool_response": {"status": "async_launched", "agentId": f"a{i}"}}, i)
            hc.handle("returned", {"cwd": str(root), "agent_id": f"a{i}", "last_assistant_message": "ok"}, i)
            hc.record_answer(root, "quote-check", ["quote-check:0105#x"])
    assert "a tripwire is owed its ruling first (reversal:q:0105@3" in out
    assert list(ha.owed(root)) == ["reversal:q:0105@3"]
    assert hc.subject_blocks(root, "modal:sheet/none") == []
