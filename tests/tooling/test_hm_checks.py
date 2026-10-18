"""`scripts/hooks/lib/hm_checks.py` - decide, then freeze (feature 375, FR-003(b)(c), FR-010; plan D4).

Feature 372's 0105 went through about four rounds of five to seven checks in wave 108 because the page was edited while its
checks ran. Each case below is a rule a later session could break without noticing: an edit while a check runs, a check
re-dispatched into an open round, an edit in the apply pass that no check proposed, a different replacement at a proposed
place, a third round with no ruling - and the escapes from a deadlock: a dispatch another guard refused, a check answered.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from tests.tooling.test_modal_checks import _load

hc = _load("hm_checks")


@pytest.fixture(autouse=True)
def _isolated_census(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """An escape taken here is recorded - in a throwaway census, never the live one (feature 169)."""
    monkeypatch.setenv("GUARD_LOG_DIR", str(tmp_path / "guard-log"))


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


def _read(st: dict, tid: str) -> None:
    """The dispatch `tid` read: its agent started and came back with a reply - only then is it a round (feature 385 T41)."""
    hc.launched(st, tid, f"ag-{tid}", True)
    hc.returned(st, f"ag-{tid}", "a reading")


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


def test_a_split_bundles_batches_go_out_together_in_one_round() -> None:
    """`make check-bundle` splits a long question's bundle into `batch-N/` directories; the second batch's dispatch is the same
    round as the first's, never refused as a re-dispatch nor counted as a round of its own (feature 374 wave 151: 0049's
    quote-check batch-2 was refused while batch-1 ran)."""
    st: dict = {}
    assert hc.dispatch(st, "t1", "quote-check", "/tmp/l7r-check/q-0105-quote-check/batch-1/MANIFEST.md", MANIFEST, 0) == ""
    hc.launched(st, "t1", "ag1", True)
    assert hc.dispatch(st, "t2", "quote-check", "/tmp/l7r-check/q-0105-quote-check/batch-2/MANIFEST.md", MANIFEST, 1) == ""
    assert hc.batch_root("/tmp/l7r-check/q-0105-quote-check/batch-2/MANIFEST.md") == "/tmp/l7r-check/q-0105-quote-check"
    assert hc.batch_root("/tmp/l7r-check/q-0105-quote-check/MANIFEST.md") == ""
    assert "already in q:0105's round" in hc.dispatch(st, "t3", "quote-check", "/tmp/l7r-check/q-0105-quote-check/MANIFEST.md", MANIFEST, 2), "an unbatched re-dispatch"
    hc.launched(st, "t2", "ag2", True)
    hc.returned(st, "ag1", "a reading")  # both batches read: the round counts once they reply (feature 385 T41)
    hc.returned(st, "ag2", "a reading")
    assert st["rounds"]["quote-check|q:0105"] == 1, "one round for the two batches"


def _clone(tmp: pathlib.Path) -> pathlib.Path:
    (tmp / ".git").mkdir()
    (tmp / ".specify").mkdir()
    (tmp / ".specify" / "feature.json").write_text('{"feature_directory": "specs/375-x"}')
    return tmp


def test_the_third_round_goes_to_the_arbiter(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """FR-010/FR-011: the record checks' cap of two rounds per subject per feature; the third trips the arbiter, whose
    `continue` lifts the cap by one and whose `accept` closes the unit for good."""
    root = _clone(tmp_path)
    ha, ro = _load("hm_arbiter"), _load("record_owed")
    store = tmp_path / "record-checks"
    monkeypatch.setenv("RECORD_CHECKS_DIR", str(store))
    st: dict = {}
    for i in range(2):
        assert hc.dispatch(st, f"t{i}", "quote-check", "/m", MANIFEST, i, root) == ""
        _read(st, f"t{i}")
        hc.answered(st, "quote-check", ["q:0105"])
    msg = hc.dispatch(st, "t9", "quote-check", "/m", MANIFEST, 5, root)
    assert "round 3 of `quote-check` on q:0105 in this feature passes its cap of 2" in msg and "make arbiter-bundle" in msg
    assert list(ha.owed(root)) == ["round:quote-check|q:0105@3"]
    ha.record_ruling(root, "round:quote-check|q:0105@3", {"ruling": "continue", "why": "a new finding each round", "what": "the notes"}, "round-arbiter")
    assert hc.dispatch(st, "t9", "quote-check", "/m", MANIFEST, 5, root) == "" and ha.owed(root) == {}
    _read(st, "t9")
    hc.answered(st, "quote-check", ["q:0105"])
    assert "passes its cap of 3" in hc.dispatch(st, "t10", "quote-check", "/m", MANIFEST, 6, root)
    ha.record_ruling(root, "round:quote-check|q:0105@4", {"ruling": "accept", "why": "what is left is wording"}, "round-arbiter")
    for slug, fp in (("quote-check:0105.drawing#bath-size", "abc123"), ("quote-check:0105#well", "x")):
        ro.write_answer(store, slug, fp, "accepted")  # what the accept answers (hm_arbiter.accept_answers)
    assert "the round arbiter closed quote-check|q:0105 (accept)" in hc.dispatch(st, "t11", "quote-check", "/m", MANIFEST, 7, root)
    moved = MANIFEST.replace("abc123", "def456")  # a later change re-owes the unit: the accept no longer closes it (374 FR-005)
    for i in range(2):
        assert hc.dispatch(st, f"m{i}", "quote-check", "/m", moved, 8 + i, root) == "", "the new change's rounds count afresh"
        _read(st, f"m{i}")
        hc.answered(st, "quote-check", ["q:0105"])
    assert "round 6 of `quote-check` on q:0105 in this feature passes its cap of 5" in hc.dispatch(st, "m2", "quote-check", "/m", moved, 11, root)
    assert hc.dispatch(st, "ti", "impl-drift", "/m", "unit: impl-drift:x 1\n", 5) == "" and st["dispatches"]["ti"]["subjects"] == []


def test_a_first_reading_of_new_notes_is_not_a_repeat_round(tmp_path: pathlib.Path) -> None:
    """The round arbiter on 0104 (2026-10-10): three features each added their own notes to one page, and the third
    source-reader dispatch - the first reading of the third feature's notes - tripped the cap. A note-scoped dispatch whose
    notes no earlier round read is a first reading; one that re-reads a note, or follows a whole-page reading, is a round."""
    root = _clone(tmp_path)
    scoped = lambda *ns: MANIFEST + f"| the question - ONLY the notes {', '.join(ns)} and the blocks that carry them |\n"  # noqa: E731
    assert hc.notes_of_manifest(scoped("a", "b")) == {"a", "b"} and hc.notes_of_manifest(MANIFEST) == set()
    st: dict = {}
    for i, notes in enumerate((("a", "b"), ("c",), ("d", "e"))):
        assert hc.dispatch(st, f"t{i}", "quote-check", "/m", scoped(*notes), i, root) == "", notes
        _read(st, f"t{i}")
        hc.answered(st, "quote-check", ["q:0105"])
    assert st["rounds"]["quote-check|q:0105"] == 1
    assert hc.dispatch(st, "t5", "quote-check", "/m", scoped("c"), 5, root) == ""  # re-reads c: round 2
    _read(st, "t5")
    hc.answered(st, "quote-check", ["q:0105"])
    assert "round 3 of `quote-check` on q:0105" in hc.dispatch(st, "t6", "quote-check", "/m", scoped("a", "z"), 6, root)
    st2: dict = {}
    for i in range(2):  # a whole-page reading reads every note: a later scoped one is a round
        assert hc.dispatch(st2, f"w{i}", "quote-check", "/m", MANIFEST if i == 0 else scoped("q"), i, root) == ""
        _read(st2, f"w{i}")
        hc.answered(st2, "quote-check", ["q:0105"])
    assert st2["rounds"]["quote-check|q:0105"] == 2


def test_a_dispatch_another_guard_refused_never_freezes_the_page() -> None:
    st: dict = {}
    hc.dispatch(st, "t1", "quote-check", "/m", MANIFEST, 0)
    assert hc.edit_refusal(st, PAGE, "a", "b", hc.PENDING_S + 1) == "", "never launched: it stops counting"
    hc.dispatch(st, "t2", "modal-depiction", "/m", MODAL, 0)
    hc.launched(st, "t2", "ag2", background=False)
    assert st["dispatches"]["t2"]["state"] == "returned"
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
    frozen_ok = {**agent, "tool_use_id": "t2", "tool_input": {"subagent_type": "quote-check", "prompt": f'{m} FREEZE_OK="a backfill run"'}}
    assert hc.handle("dispatch", frozen_ok, 3) == ""
    assert hc.handle("launched", {**frozen_ok, "tool_response": {"status": "async_launched", "agentId": "ag2"}}, 3) == ""
    assert hc.handle("dispatch", {**agent, "tool_input": {"subagent_type": "Explore", "prompt": "x"}}, 3) == ""
    assert hc.handle("returned", {"cwd": cwd, "agent_id": "ag1", "last_assistant_message": REPLY}, 4) == ""
    assert hc.handle("returned", {"cwd": cwd, "agent_id": "ag2", "last_assistant_message": REPLY}, 4) == ""
    assert hc.handle("edit", {"cwd": cwd, "tool_name": "Bash", "tool_input": {"command": 'make apply-edits FROM=x FREEZE_OK="a test escape"'}}, 5) == ""
    assert hc.handle("edit", {"cwd": cwd, "tool_name": "Bash", "tool_input": {"command": "ls"}}, 5) == ""
    assert hc.handle("other", {"cwd": cwd}, 5) == ""
    state = json.loads((tmp_path / ".git" / hc.STATE).read_text())
    assert state["feature"] == "375-x" and state["rounds"] == {"quote-check|q:0105": 2}, "a FREEZE_OK dispatch is a round too"
    hc.record_answer(tmp_path, "quote-check", ["quote-check:0105#well"])
    assert json.loads((tmp_path / ".git" / hc.STATE).read_text())["dispatches"]["t1"]["state"] == "answered"
    (tmp_path / ".specify" / "feature.json").write_text('{"feature_directory": "specs/376-y"}')
    assert hc.handle("dispatch", agent, 6) == ""
    assert json.loads((tmp_path / ".git" / hc.STATE).read_text())["rounds"] == {}, "a new feature counts afresh - a round once it is read"
    monkeypatch.chdir(tmp_path)
    assert hc.main(["close", "q:0105", "x"]) == 2
    st = json.loads((tmp_path / ".git" / hc.STATE).read_text())
    st["dispatches"]["t9"] = {"check": "quote-check", "subjects": ["q:0105"], "t": 0, "state": "running"}
    (tmp_path / ".git" / hc.STATE).write_text(json.dumps(st))
    assert hc.close(tmp_path, "q:0105", "the agent died silently", hc.STALE_S - 1) == 0
    out = capsys.readouterr().out
    assert "0 silent dispatch(es)" in out and "still running and not silent" in out, "a live check is never closed"
    assert hc.main(["close", "q:0105", "the agent died silently"]) == 0 and "1 silent dispatch(es) on q:0105 closed" in capsys.readouterr().out
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


def test_a_modal_research_dispatch_is_closed_by_its_three_answers() -> None:
    """Feature 374 FR-005: one `modal-research` dispatch is answered as `modal-accuracy`, `modal-references` and
    `modal-gaps`; matched by the unit's name it stayed open, its round never ended, and its next round was refused."""
    st = {"dispatches": {"t1": {"check": "modal-research", "subjects": ["modal:sheet/x"], "state": "returned"}}}
    assert hc.answered(st, "modal-accuracy", ["modal:sheet/x"]) == 1
    assert st["dispatches"]["t1"]["state"] == "answered"
    other = {"dispatches": {"t1": {"check": "modal-form", "subjects": ["modal:sheet/x"], "state": "returned"}}}
    assert hc.answered(other, "modal-accuracy", ["modal:sheet/x"]) == 0, "a research answer closes no other check"


# ---- feature 371: every check's pass is logged at its return, with its cost cells ------------------------------------------


def _transcript(tmp: pathlib.Path, name: str, prompt: str, stamps: tuple[str, str] = ("2026-10-10T10:00:00Z", "2026-10-10T10:01:20Z")) -> pathlib.Path:
    """A minimal agent transcript: the dispatch's prompt, then one model call with its usage."""
    t = tmp / f"agent-{name}.jsonl"
    t.write_text(
        json.dumps({"timestamp": stamps[0], "message": {"role": "user", "content": prompt}})
        + "\n"
        + json.dumps(
            {
                "timestamp": stamps[1],
                "message": {"role": "assistant", "usage": {"input_tokens": 1000, "cache_read_input_tokens": 2000, "cache_creation_input_tokens": 0, "output_tokens": 500}, "content": []},
            }
        )
        + "\n"
    )
    return t


def _log(tmp: pathlib.Path) -> list[dict]:
    p = tmp / hc.PASS_LOG
    return [json.loads(ln) for ln in p.read_text().splitlines()] if p.is_file() else []


def test_a_checks_return_appends_one_pass_with_the_transcripts_cells(tmp_path: pathlib.Path) -> None:
    """FR-001 / SC-004: the cells are the ones review_cost computes from the same transcript."""
    _lint, rc = hc._reviews()
    t = _transcript(tmp_path, "a1", "Check the bundle at /tmp/x/MANIFEST.md | read it\nmore")
    assert hc.log_pass(tmp_path, "returned", {"agent_type": "glyph-check", "agent_id": "a1", "agent_transcript_path": str(t)}, 0.0)
    (rec,) = _log(tmp_path)
    assert rec["check"] == "glyph-check" and rec["agent"] == "a1" and rec["subject"] == "Check the bundle at /tmp/x/MANIFEST.md read it"
    assert f"{rec['wall']} | {rec['tokens']}" == rc.cells(rc.cost(t.read_text().splitlines()))


def test_an_agent_that_is_not_a_check_logs_nothing(tmp_path: pathlib.Path) -> None:
    t = _transcript(tmp_path, "a2", "help")
    for kind in ("general-purpose", "round-arbiter", "Explore"):
        assert not hc.log_pass(tmp_path, "returned", {"agent_type": kind, "agent_id": "a2", "agent_transcript_path": str(t)}, 0.0)
    assert _log(tmp_path) == []


def test_each_return_of_a_resumed_check_is_logged_with_its_own_cells(tmp_path: pathlib.Path) -> None:
    """Plan review 2: the second stop's cells are the resumed segment's alone; the same return seen twice is logged once; a
    background launch waits for its return."""
    _lint, rc = hc._reviews()
    t = _transcript(tmp_path, "a3", "MODE 2")
    payload = {"agent_type": "spec-fidelity", "agent_id": "a3", "agent_transcript_path": str(t)}
    assert hc.log_pass(tmp_path, "returned", payload, 0.0)
    assert not hc.log_pass(tmp_path, "returned", payload, 0.0), "the same return seen again is not a second pass"
    with t.open("a") as fh:  # resumed: a new prompt, then a second call
        fh.write(json.dumps({"timestamp": "2026-10-10T11:00:00Z", "message": {"role": "user", "content": "round 2, please"}}) + "\n")
        fh.write(
            json.dumps(
                {
                    "timestamp": "2026-10-10T11:00:40Z",
                    "requestId": "r2",
                    "message": {"role": "assistant", "content": [], "usage": {"input_tokens": 100, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0, "output_tokens": 50}},
                }
            )
            + "\n"
        )
    assert hc.log_pass(tmp_path, "returned", payload, 0.0)
    first, second = _log(tmp_path)
    assert (first["segment"], second["segment"]) == (0, 1), "each line names its return, for ledger_owed to settle"
    assert second["wall"] == "40 s" and (first["wall"], first["tokens"]) != (second["wall"], second["tokens"])
    assert f"{second['wall']} | {second['tokens']}" == rc.cells(rc.cost(rc.segments(t.read_text().splitlines())[-1]))
    bg = {"tool_input": {"subagent_type": "spec-fidelity"}, "tool_response": {"status": "async_launched", "agentId": "a3"}}
    assert not hc.log_pass(tmp_path, "launched", bg, 0.0) and len(_log(tmp_path)) == 2


def test_one_return_seen_twice_as_its_transcript_grows_is_one_pass(tmp_path: pathlib.Path) -> None:
    """2026-10-10: each of 0104's source-reader passes was listed twice by `make ledger-owed`, the first with the cells of a
    transcript not yet finished. The same segment seen again is the same pass, logged once by its `segment`; its cells are
    provisional, and `ledger_owed.py` recomputes them from the finished transcript (374 batch 2's design, kept at the merge)."""
    t = _transcript(tmp_path, "a5", "Check the bundle")
    payload = {"agent_type": "source-reader", "agent_id": "a5", "agent_transcript_path": str(t)}
    assert hc.log_pass(tmp_path, "returned", payload, 0.0)
    with t.open("a") as fh:  # the last turn written after the first stop event
        fh.write(
            json.dumps(
                {
                    "timestamp": "2026-10-10T10:09:00Z",
                    "requestId": "r9",
                    "message": {"role": "assistant", "content": [], "usage": {"input_tokens": 10, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0, "output_tokens": 900}},
                }
            )
            + "\n"
        )
    assert not hc.log_pass(tmp_path, "returned", payload, 0.0)
    (only,) = _log(tmp_path)
    assert only["segment"] == 0 and only["agent"] == "a5"


def test_a_foreground_check_is_logged_when_its_tool_call_completes(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _lint, rc = hc._reviews()
    t = _transcript(tmp_path, "a4", "Check the claims bundle")
    monkeypatch.setattr(rc, "transcript", lambda aid, root=None: t if aid == "a4" else None)
    fg = {"tool_input": {"subagent_type": "impl-drift"}, "tool_response": {"status": "completed", "agentId": "a4"}}
    assert hc.log_pass(tmp_path, "launched", fg, 0.0)
    assert _log(tmp_path)[0]["check"] == "impl-drift"


def test_a_return_with_no_transcript_or_a_broken_one_never_raises(tmp_path: pathlib.Path) -> None:
    assert not hc.log_pass(tmp_path, "returned", {"agent_type": "glyph-check", "agent_id": "a5", "agent_transcript_path": str(tmp_path / "gone.jsonl")}, 0.0)
    assert not hc.log_pass(tmp_path / "no-such-dir", "returned", {"agent_type": "glyph-check", "agent_id": "a6", "agent_transcript_path": str(_transcript(tmp_path, "a6", "x"))}, 0.0)


def test_a_foreground_check_keeps_its_reply_and_its_edits(tmp_path: pathlib.Path) -> None:
    """The round arbiter on 0104 (2026-10-10) found "no reply kept" for every source-reader round: a foreground check's
    SubagentStop fires while its dispatch is pending, so its reply is taken from the tool's response at PostToolUse."""
    st: dict = {}
    hc.dispatch(st, "t1", "quote-check", "/m", MANIFEST, 0)
    hc.launched(st, "t1", "ag1", False, hc.response_text({"content": [{"type": "text", "text": REPLY}]}), tmp_path / "keep")
    d = st["dispatches"]["t1"]
    assert d["state"] == "returned" and pathlib.Path(d["reply"]).read_text() == REPLY
    assert st["edits"]["q:0105"] == [["research/questions/0105-baths-furo.drawing.html", "about 10 by 8 ft", "about 10 by 8 feet"]]
    assert hc.response_text({"content": "plain"}) == "plain" and hc.response_text({}) == ""


def test_the_refusal_names_the_escape_that_reaches_its_rule() -> None:
    assert hc.escape_for("the round arbiter closed quote-check|q:0105 (accept)") == "ARBITER_OK"
    assert hc.escape_for("round 3 of `quote-check` on q:0105 ... make arbiter-bundle") == "ARBITER_OK"
    assert hc.escape_for("`quote-check` is already in q:0105's round") == "FREEZE_OK"


def test_a_dispatch_keeps_why_its_units_were_due_and_a_late_reply(tmp_path: pathlib.Path) -> None:
    """Feature 374 (the round arbiter's tooling fixes): each dispatch keeps the `owed:` lines of its bundle, and a reply that
    arrives after the answer closed the dispatch is still kept, so the arbiter's bundle has every round's reply."""
    st: dict = {}
    hc.dispatch(st, "t1", "modal-depiction", "/m", MODAL + "owed: modal-depiction:sheet/bath - a page its Drawing: names moved\n", 0)
    assert st["dispatches"]["t1"]["owed"] == ["modal-depiction:sheet/bath - a page its Drawing: names moved"]
    hc.launched(st, "t1", "ag1", True)
    hc.answered(st, "modal-depiction", ["modal:sheet/bath"])
    hc.returned(st, "ag1", "1. a finding", tmp_path / "keep")
    assert pathlib.Path(st["dispatches"]["t1"]["reply"]).read_text() == "1. a finding"


def test_checks_launched_at_once_each_keep_their_agent(tmp_path: pathlib.Path) -> None:
    """Feature 374 wave 120: six checks launched in one message ran one hook process each, and an unlocked read-modify-write
    kept only the last writer - three dispatches lost their agent id, so their replies were never kept and the round arbiter
    read "no reply kept". Twenty launches at once must each keep theirs."""
    import subprocess
    import sys

    (tmp_path / ".git").mkdir()
    state = {"dispatches": {f"t{i}": {"check": "modal-form", "subjects": [f"modal:sheet/m{i}"], "state": "pending", "t": 1.0} for i in range(20)}}
    path = hc.state_path(str(tmp_path))
    hc.save(path, state)
    lib = str(pathlib.Path(hc.__file__).parent)
    code = (
        "import sys; sys.path.insert(0, sys.argv[1]); import hm_checks as h; i = sys.argv[3]; "
        "h.handle('launched', {'cwd': sys.argv[2], 'tool_name': 'Agent', 'tool_use_id': f't{i}', "
        "'tool_response': {'agentId': f'a{i}', 'status': 'async_launched', 'content': []}})"
    )
    procs = [subprocess.Popen([sys.executable, "-c", code, lib, str(tmp_path), str(i)]) for i in range(20)]
    assert all(p.wait(timeout=60) == 0 for p in procs)
    kept = hc.load(path)["dispatches"]
    assert sorted(d.get("aid") for d in kept.values()) == sorted(f"a{i}" for i in range(20)), kept
    assert not list(tmp_path.glob(".git/*.tmp")), "each writer's temporary file is its own and is renamed into place"


def test_a_first_look_at_sentences_other_checks_added_is_no_round(tmp_path: pathlib.Path) -> None:
    """Feature 374 wave 120, the round arbiter on 0190: record-format's third round was owed only by sentences the depiction
    checks had asked for, and the cap fired on text the check had never read. Unread sentences from OTHER checks' edits are
    a first look; a sentence inside the check's OWN proposed edit is its fix read again, a repeat; no history counts."""
    assert hc.sentences(["One. Two  words!", "Three?"]) == ["One.", "Two words!", "Three?"]
    unit = "record-format|modal:sheet/x"
    state: dict = {}
    assert not hc.first_look(state, unit, ["A new sentence."]), "no reading recorded: counted as before"
    state["seen"] = {unit: [hc._sentence_key("Old sentence.")]}
    assert not hc.first_look(state, unit, ["Old sentence."]), "nothing unread"
    assert hc.first_look(state, unit, ["Old sentence.", "Added for depiction."])
    state["own_edits"] = {unit: ["Old sentence. Its own fix, as proposed."]}
    assert not hc.first_look(state, unit, ["Old sentence.", "Its own fix, as proposed."]), "its own fix read again"
    # through dispatch: the third round after two counted ones is let through, uncounted, when its text is new to it
    root = tmp_path / "c"
    (root / ".git").mkdir(parents=True)
    modal = root / "l7r/diagram/interactive/assets/modals/sheet/x.md"
    modal.parent.mkdir(parents=True)
    modal.write_text("About: Old sentence.\n")
    st: dict = {"rounds": {"modal-form|modal:sheet/x": hc.ROUND_CAP}}
    text = "MANIFEST\nunit: modal-form:sheet/x abc123\n"
    subjects = hc.subjects_of_manifest(text)
    assert subjects == ["modal:sheet/x"], subjects
    st["seen"] = {"modal-form|modal:sheet/x": [hc._sentence_key(s) for s in hc.sentences(hc.subject_blocks(root, "modal:sheet/x"))]}
    modal.write_text("About: Old sentence. Added for depiction.\n")
    assert hc.dispatch(st, "t1", "modal-form", "m", text, 1.0, root) == ""
    assert st["rounds"]["modal-form|modal:sheet/x"] == hc.ROUND_CAP, "a first look is not counted"


def test_a_later_batch_counts_its_rounds_afresh_and_a_batch_s_own_edits_do_not(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The round arbiter's tooling fix (round:modal-depiction|modal:hamlet/woodland-commons@3, feature 374 batch 9), corrected in
    batch 11: a unit's rounds count afresh only in a LATER BATCH (another `origin/main` than every counted round's); within a
    batch every round counts, edits and all - told by fingerprint, any edit restarted the count and the cap never tripped."""
    root = _clone(tmp_path)
    assert hc.batch_of(None) == "" and isinstance(hc.batch_of(root), str), "no root, no batch; a clone with or without a remote"
    batch = {"b": "main-1"}
    monkeypatch.setattr(hc, "batch_of", lambda r: batch["b"])
    st: dict = {}
    edited = "owed-checks: quote-check\nunit: quote-check:0105.drawing#bath-size zzz999\n"  # the round's own edit moved the words
    for i, m in enumerate((MANIFEST, edited)):
        assert hc.dispatch(st, f"t{i}", "quote-check", "/m", m, i, root) == ""
        _read(st, f"t{i}")
        hc.answered(st, "quote-check", ["q:0105"])
    assert "passes its cap of 2" in hc.dispatch(st, "t2", "quote-check", "/m", "owed-checks: quote-check\nunit: quote-check:0105#x yyy\n", 2, root), (
        "the same batch: round 3 trips, edits notwithstanding"
    )
    batch["b"] = "main-2"  # a landing: a later batch owes the unit
    for i in range(2):
        assert hc.dispatch(st, f"n{i}", "quote-check", "/m", MANIFEST, 3 + i, root) == "", "a later batch's rounds count afresh"
        _read(st, f"n{i}")
        hc.answered(st, "quote-check", ["q:0105"])
    assert "passes its cap of 4" in hc.dispatch(st, "n2", "quote-check", "/m", MANIFEST, 5, root), "and are capped like any other"
    assert not hc.new_cause({}, "u", "b") and not hc.new_cause({"round_batch": {"u": "a"}}, "u", ""), "no counted round, no batch: no new cause"
    assert hc.new_cause({"round_batch": {"u": "a"}}, "u", "b") and not hc.new_cause({"round_batch": {"u": "a"}}, "u", "a")


def _wave_transcript(tmp_path: pathlib.Path, name: str, task: str) -> str:
    """A workflow agent's transcript as the harness writes it (feature 383's probe, research R20): a framed relay of the user's
    request, then the computed task text, every line indented."""
    framed = "[Workflow harness - computed task] ... The computed task text follows:\n" + "\n".join("  " + ln for ln in task.splitlines())
    rows = [{"type": "user", "message": {"role": "user", "content": "[Workflow harness - user request] the GM's words"}}, {"type": "user", "message": {"role": "user", "content": framed}}]
    p = tmp_path / f"{name}.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    return str(p)


def test_a_check_wave_unit_pairs_at_its_return_by_its_prompt(tmp_path: pathlib.Path) -> None:
    """Feature 383 amendment 7 (SC-033): no PostToolUse gives a workflow agent's id, so its SubagentStop pairs it - by the prompt
    its task text begins with - and the freeze holds from dispatch to return; a re-launch of a unit that came back with nothing,
    and a declared verify step (its prompt then the reply before it), pair the same way."""
    st: dict = {}
    prompt = "Read /tmp/b/MANIFEST.md\nand rule on it."
    assert hc.dispatch(st, "wave:r1:0", "quote-check", "/m", MANIFEST, 0) == ""
    st["dispatches"]["wave:r1:0"].update(wave=hc._wave_key(prompt), wave_len=len(hc._collapsed(prompt)))
    assert "frozen" in hc.edit_refusal(st, PAGE, "a", "b", 600), "a wave unit waits in the queue past PENDING_S, still frozen"
    assert hc.edit_refusal(st, PAGE, "a", "b", hc.WAVE_PENDING_S + 1) == "", "...but not for ever"
    hc.pair_wave(st, "agX", _wave_transcript(tmp_path, "other", "Read /tmp/zzz/MANIFEST.md"))
    assert st["dispatches"]["wave:r1:0"].get("aid") is None, "another unit's agent does not pair"
    hc.pair_wave(st, "ag1", _wave_transcript(tmp_path, "a1", prompt))
    assert st["dispatches"]["wave:r1:0"]["aid"] == "ag1" and st["dispatches"]["wave:r1:0"]["state"] == "running"
    hc.returned(st, "ag1", "")
    hc.pair_wave(st, "ag2", _wave_transcript(tmp_path, "a2", prompt))
    assert st["dispatches"]["wave:r1:0"]["aid"] == "ag2", "the re-launch of a unit that came back with nothing pairs to it"
    hc.returned(st, "ag2", REPLY)
    assert st["edits"]["q:0105"], "...and its reply's EDIT blocks are kept as a hand launch's are"
    step = "Verify /tmp/b/MANIFEST.md"
    assert hc.dispatch(st, "wave:r1:0.0", "source-reader", "/m2", MANIFEST, 10, freeze_ok=True) == ""
    st["dispatches"]["wave:r1:0.0"].update(wave=hc._wave_key(step), wave_len=len(hc._collapsed(step)))
    hc.pair_wave(st, "ag3", _wave_transcript(tmp_path, "a3", step + "\n\nThe reply of the quote-check check before you:\n" + REPLY))
    assert st["dispatches"]["wave:r1:0.0"]["aid"] == "ag3", "a verify step pairs by its declared prompt, the reply after it"
    for tid, text in (("wave:r2:0", "Judge page 1"), ("wave:r2:1", "Judge page 12")):
        hc.dispatch(st, tid, "source-reader", f"/m-{tid}", "", 20)
        st["dispatches"][tid].update(wave=hc._wave_key(text), wave_len=len(text))
    hc.pair_wave(st, "ag12", _wave_transcript(tmp_path, "a12", "Judge page 12"))
    assert st["dispatches"]["wave:r2:1"]["aid"] == "ag12" and "aid" not in st["dispatches"]["wave:r2:0"], "the longest match wins"


def test_a_refused_wave_run_drops_its_dispatches(tmp_path: pathlib.Path) -> None:
    """A check-wave run a guard refused launches nothing, so its units already recorded must not freeze a page (plan D48)."""
    clone = tmp_path / "c"
    (clone / ".git").mkdir(parents=True)
    path = clone / ".git" / hc.STATE
    st: dict = {}
    hc.dispatch(st, "wave:r9:0", "quote-check", "/m", MANIFEST, 0)
    hc.dispatch(st, "toolu_hand", "quote-check", "/m", MODAL, 0)
    hc.save(path, st)
    hc.drop_run(str(clone), "wave:r9:")
    assert list(hc.load(path)["dispatches"]) == ["toolu_hand"]
    hc.drop_run(str(tmp_path / "nowhere"), "wave:")  # no clone: nothing to drop, and no error


def test_a_dispatch_a_later_hook_refused_is_no_round(tmp_path: pathlib.Path) -> None:
    """Feature 385 T41 (the round arbiter on round:source-reader|q:0081@3): the pair hook refused two source-reader dispatches
    before any agent started, and the counter counted both - the cap fired on zero readings. A round counts only once its agent
    started and came back with a reply: a refused dispatch, or one that kept no reply, leaves the count unchanged."""
    root = _clone(tmp_path)
    st: dict = {}
    assert hc.dispatch(st, "r1", "quote-check", "/m", MANIFEST, 0, root) == ""
    assert st.get("rounds", {}).get("quote-check|q:0105", 0) == 0, "sent, never launched: no round"
    assert hc.dispatch(st, "r2", "quote-check", "/m", MANIFEST, 1, root) == ""
    hc.launched(st, "r2", "a2", True)
    hc.returned(st, "a2", "")
    assert st.get("rounds", {}).get("quote-check|q:0105", 0) == 0, "started, kept no reply: no round"
    assert hc.dispatch(st, "r3", "quote-check", "/m", MANIFEST, 2, root) == ""
    hc.launched(st, "r3", "a3", False, reply="quote-check: 1 VERBATIM")
    hc.returned(st, "a3", "quote-check: 1 VERBATIM")
    assert st["rounds"]["quote-check|q:0105"] == 1, "a reading counts, once"
