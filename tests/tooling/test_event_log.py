"""`scripts/measure/event_log.py` and `feature_report.py` - the event log and the report built on it (feature 375, FR-008/FR-009).

The hook's own payload cases are `tests/hooks/test-event-log-hooks.sh`; these pin the parts a session reads back: the
transcript converter (the source for every feature before the hooks existed, and for 375 itself), how a session's time is
split, the rounds and reversals counted, and the report end to end over a throwaway repository.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from tests._scripts import script


def _load(name: str):  # noqa: ANN202 - a module loaded by path
    path = script(name)
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


el = _load("event_log")
fr = _load("feature_report")


def _tool_use(t: str, tid: str, name: str, inp: dict, stop: str | None = None) -> dict:
    msg = {"content": [{"type": "tool_use", "id": tid, "name": name, "input": inp}]}
    if stop:
        msg["stop_reason"] = stop
    return {"type": "assistant", "timestamp": t, "sessionId": "s", "message": msg}


def _result(t: str, tid: str, resp: dict | None = None) -> dict:
    return {"type": "user", "timestamp": t, "sessionId": "s", "toolUseResult": resp or {}, "message": {"content": [{"type": "tool_result", "tool_use_id": tid, "content": "ok"}]}}


TRANSCRIPT = [
    {"type": "user", "timestamp": "2026-10-10T10:00:00.000Z", "sessionId": "s", "message": {"content": "please work 375"}},
    {"type": "user", "timestamp": "2026-10-10T10:00:00.500Z", "sessionId": "s", "isMeta": True, "message": {"content": "<system-reminder>x"}},
    _tool_use("2026-10-10T10:00:10.000Z", "t1", "Bash", {"command": "make quick"}),
    _result("2026-10-10T10:00:40.000Z", "t1"),
    _tool_use("2026-10-10T10:01:00.000Z", "t2", "Agent", {"subagent_type": "quote-check", "prompt": "/tmp/l7r-check/0105-quote-check/MANIFEST.md"}),
    _result("2026-10-10T10:01:01.000Z", "t2", {"status": "async_launched", "agentId": "ag1"}),
    {"type": "assistant", "timestamp": "2026-10-10T10:01:05.000Z", "sessionId": "s", "message": {"content": [{"type": "text", "text": "waiting"}], "stop_reason": "end_turn"}},
    {"type": "queue-operation", "operation": "enqueue", "timestamp": "2026-10-10T10:05:00.000Z", "sessionId": "s", "content": "<task-notification> <task-id>ag1</task-id>"},
    {"type": "queue-operation", "operation": "enqueue", "timestamp": "2026-10-10T10:05:00.000Z", "sessionId": "s", "content": "<task-notification> <task-id>bash9</task-id>"},
    {"type": "user", "timestamp": "2026-10-10T10:05:00.100Z", "sessionId": "s", "message": {"content": "<task-notification> <task-id>ag1</task-id>"}},
    _tool_use("2026-10-10T10:06:00.000Z", "t3", "Edit", {"file_path": "/c/specs/375-x/plan.md", "old_string": "A", "new_string": "B"}),
    _result("2026-10-10T10:06:01.000Z", "t3"),
    {"type": "assistant", "isSidechain": True, "timestamp": "2026-10-10T10:06:02.000Z", "sessionId": "s", "message": {"content": [{"type": "tool_use", "id": "side", "name": "Read", "input": {}}]}},
]


def test_a_transcript_becomes_the_hooks_events() -> None:
    evs = el.from_transcript(TRANSCRIPT)
    kinds = [(e["ev"], e.get("tool") or e.get("agent") or "") for e in evs]
    assert kinds == [
        ("UserPromptSubmit", ""),
        ("PreToolUse", "Bash"),
        ("PostToolUse", "Bash"),
        ("PreToolUse", "Agent"),
        ("PostToolUse", "Agent"),
        ("SubagentStart", "quote-check"),
        ("Stop", ""),
        ("SubagentStop", "quote-check"),
        ("PreToolUse", "Edit"),
        ("PostToolUse", "Edit"),
    ]
    agent = next(e for e in evs if e["ev"] == "PostToolUse" and e["tool"] == "Agent")
    assert agent["aid"] == "ag1" and agent["cat"] == "record check"
    edit = next(e for e in evs if e["ev"] == "PreToolUse" and e["tool"] == "Edit")
    assert edit["old"] == el.digest("A") and edit["new"] == el.digest("B")


def test_categories_and_make_targets() -> None:
    assert el.make_target("cd /x && make -C y --no-print-directory test-file FILE=a") == "test-file"
    assert el.make_target("FULL=1 make done") == "done"
    assert el.make_target("echo make") == ""
    assert el.category("Write", {}) == "edit"
    assert el.category("Bash", {"command": "make claim SLUG=x"}) == "spec-kit step"
    assert el.category("Agent", {"subagent_type": "impl-drift"}) == "claims check"
    assert el.category("Agent", {"subagent_type": "general-purpose", "prompt": "x/modal-triage/MANIFEST.md"}) == "record check"
    assert el.category("Agent", {"subagent_type": "spec-fidelity-verify"}) == "spec review"
    assert el.category("Agent", {"subagent_type": "round-arbiter"}) == "round arbiter"
    assert el.category("Agent", {"subagent_type": "Explore"}) == "other subagent"
    assert el.category("Skill", {"skill": "dataviz"}) == "other tool"
    w = el.line({"hook_event_name": "PreToolUse", "tool_name": "Write", "tool_input": {"file_path": "/a", "content": "c"}})
    assert w["new"] == el.digest("c") and w["path"] == "/a"
    nb = el.line({"hook_event_name": "PreToolUse", "tool_name": "NotebookEdit", "tool_input": {"notebook_path": "/n"}})
    assert nb["path"] == "/n" and "new" not in nb
    odd = el.line({"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": "not a mapping"})
    assert odd["cat"] == "other tool"


def test_a_worktree_logs_to_its_clones_git_dir(tmp_path: Path) -> None:
    clone = tmp_path / "clone"
    subprocess.run(["git", "init", "-q", str(clone)], check=True)
    subprocess.run(
        ["git", "-C", str(clone), "commit", "-q", "--allow-empty", "-m", "x"],
        check=True,
        env={"GIT_AUTHOR_NAME": "a", "GIT_AUTHOR_EMAIL": "a@b", "GIT_COMMITTER_NAME": "a", "GIT_COMMITTER_EMAIL": "a@b", "PATH": "/usr/bin:/bin"},
    )
    wt = tmp_path / "wt"
    subprocess.run(["git", "-C", str(clone), "worktree", "add", "-q", "--detach", str(wt)], check=True)
    assert el.common_git_dir(wt) == (clone / ".git").resolve()
    assert el.common_git_dir(clone) == clone / ".git"
    assert el.clone_root(str(wt)) == wt.resolve()
    assert el.feature_of(wt) == ""
    (wt / ".specify").mkdir()
    (wt / ".specify" / "feature.json").write_text('{"feature_directory": "specs/375-x/"}')
    assert el.feature_of(wt) == "375-x"
    path = el.append({"hook_event_name": "Stop", "session_id": "s", "cwd": str(wt)})
    assert path == (clone / ".git").resolve() / "l7r-events" / "375-x.jsonl"
    (tmp_path / "bad.jsonl").write_text('{"t": "x"}\nnot json\n\n')
    assert list(el.read_jsonl(tmp_path / "bad.jsonl")) == [{"t": "x"}]


def test_the_command_line(tmp_path: Path, monkeypatch, capsys) -> None:  # noqa: ANN001
    (tmp_path / "t.jsonl").write_text("".join(json.dumps(r) + "\n" for r in TRANSCRIPT))
    assert el.main(["from-transcript", str(tmp_path / "t.jsonl")]) == 0
    assert capsys.readouterr().out.count("\n") == 10
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO("not json"))
    assert el.main(["hook"]) == 0
    assert el.main([]) == 2


def test_the_time_is_split_by_what_the_session_was_doing() -> None:
    split = fr.split_time(el.from_transcript(TRANSCRIPT), "375-x")
    assert split["thinking"] == 10 + 20 + 4  # prompt->Bash, Bash->Agent, the agent's start->Stop
    assert split["dispatching: record check"] == 1
    assert split["quick test"] == 30
    assert split["waiting: quote-check"] == 235
    assert split["writing the spec"] == 60  # the agent's return to an edit of the feature's own plan
    assert split["edit"] == 1
    late = [
        {"t": "2026-10-10T10:00:00Z", "sid": "s", "ev": "Stop"},
        {"t": "2026-10-10T12:00:00Z", "sid": "s", "ev": "UserPromptSubmit"},
        {"t": "2026-10-10T12:00:01Z", "sid": "s", "ev": "Stop"},
        {"t": "2026-10-10T12:00:30Z", "sid": "s", "ev": "UserPromptSubmit"},
        {"t": "2026-10-10T12:00:40Z", "sid": "s", "ev": "Stop"},
        {"t": "2026-10-10T12:00:50Z", "sid": "s", "ev": "PreToolUse", "tool": "Bash", "id": "x", "cat": "gate"},
        {"t": "2026-10-10T12:01:50Z", "sid": "s", "ev": "PreToolUse", "tool": "Bash", "id": "y", "cat": "other tool"},
        {"t": "2026-10-10T12:01:50Z", "sid": "s", "ev": "PostToolUse", "tool": "Bash", "id": "y"},
    ]
    split = fr.split_time(late, "375-x")
    assert split["idle (over an hour)"] == 7200 and split["waiting: the GM"] == 29
    assert split["waiting: a background run"] == 10 and split["gate"] == 60


def test_rounds_reversals_and_subjects() -> None:
    evs = [
        {"t": "1", "ev": "PreToolUse", "tool": "Agent", "agent": "quote-check", "manifest": "/tmp/l7r-check/0105-quote-check/MANIFEST.md"},
        {"t": "2", "ev": "PreToolUse", "tool": "Agent", "agent": "quote-check", "manifest": "/tmp/l7r-check/0105-quote-check/MANIFEST.md"},
        {"t": "3", "ev": "PreToolUse", "tool": "Agent", "agent": "spec-fidelity"},
        {"t": "4", "ev": "PreToolUse", "tool": "Edit", "path": "/a.md", "old": "A", "new": "B"},
        {"t": "5", "ev": "PreToolUse", "tool": "Edit", "path": "/a.md", "old": "B", "new": "A"},
        {"t": "6", "ev": "PreToolUse", "tool": "Edit", "path": "/b.md", "old": "B", "new": "A"},
    ]
    by_type, rounds = fr.dispatches(evs)
    assert by_type == {"quote-check": 2, "spec-fidelity": 1} and rounds == {("quote-check", "0105"): 2}
    assert fr.reversals(evs) == [("/a.md", "5")]
    assert fr.subject("/tmp/l7r-check/claims-triage/MANIFEST.md") == "claims-triage"
    assert fr.spec_rounds("- Round 1 (spec-fidelity, d): CHANGES REQUIRED - x\n- Round 2 (v, d): FAITHFUL - y\n") == {"CHANGES REQUIRED": 1, "FAITHFUL": 1}
    assert fr._hm(3700) == "1 h 02 min" and fr._hm(90) == "2 min"


def _git(repo: Path, *args: str) -> None:
    env = {
        "GIT_AUTHOR_NAME": "a",
        "GIT_AUTHOR_EMAIL": "a@b",
        "GIT_COMMITTER_NAME": "a",
        "GIT_COMMITTER_EMAIL": "a@b",
        "PATH": "/usr/bin:/bin",
        "GIT_AUTHOR_DATE": "2026-10-10T10:00:30Z",
        "GIT_COMMITTER_DATE": "2026-10-10T10:00:30Z",
    }
    subprocess.run(["git", "-C", str(repo), *args], check=True, env=env, capture_output=True)


def test_the_report_end_to_end(tmp_path: Path, capsys) -> None:  # noqa: ANN001
    repo = tmp_path / "repo"
    d = repo / "specs" / "375-x"
    d.mkdir(parents=True)
    _git(repo, "init", "-q")
    (d / "spec.md").write_text("- Round 1 (spec-fidelity, d): FAITHFUL - ok\n")
    (d / "tasks.md").write_text("- [x] T01 a\n- [ ] T02 b\n")
    (d / "plan-review.json").write_text('{"verdict": "BLOCKED"}')
    (repo / "tool.py").write_text("a\nb\nc\nd\n")
    (repo / "x.svg").write_text("<svg/>\n" * 50)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "Feature 375 T01: the tool")
    sha = subprocess.run(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    log = repo / "dev" / "run-log" / "2026-10"
    log.mkdir(parents=True)
    (log / "a.json").write_text(json.dumps({"utc": "2026-10-10T10:00:20Z", "target": "done", "result": "failed: test-full", "commit": sha}))
    (log / "b.json").write_text(json.dumps({"utc": "2026-10-10T10:00:25Z", "target": "done", "result": "green", "commit": sha}))
    (log / "c.json").write_text(json.dumps({"utc": "2026-10-10T10:00:26Z", "target": "quick", "result": "green", "commit": sha}))
    (log / "d.json").write_text("not json")
    (tmp_path / "t.jsonl").write_text("".join(json.dumps(r) + "\n" for r in TRANSCRIPT))
    events = repo / ".git" / "l7r-events"
    events.mkdir()
    (events / "375-x.jsonl").write_text(json.dumps({"t": "2026-10-10T10:07:00Z", "sid": "s", "ev": "Stop"}) + "\n")
    text = fr.report(repo, "375", [tmp_path / "t.jsonl"], clones=tmp_path / "no-clones")
    assert "| quick test | 0 min |" in text and "| record check" not in text
    assert "gates: green 1, red 1" in text and "plan reviews BLOCKED: 1" in text
    assert "check dispatches 1 over 4 changed lines: cascade ratio 0.25" in text  # the SVG is not the feature's own diff
    assert "tasks ticked: 1 of 2" in text and "spec rounds: FAITHFUL 1" in text
    assert fr.main(["375", "--root", str(repo), "--write", "--transcript", str(tmp_path / "t.jsonl")]) == 0
    assert (d / "report.md").is_file() and "written to specs/375-x/report.md" in capsys.readouterr().out
    empty = fr.report(repo, "375", since="2030-01-01T00:00:00Z", clones=tmp_path / "no-clones")
    assert "no event log and no transcript" in empty
    try:
        fr.report(repo, "999")
    except SystemExit as exc:
        assert "no specs/999-*" in str(exc)
    else:
        raise AssertionError("a missing feature must refuse")


def test_a_returned_agent_s_verdict_is_read_from_its_reply() -> None:
    assert el.verdict_of("**Verdict: CHANGES REQUIRED.** I reviewed") == "CHANGES REQUIRED"
    assert el.verdict_of("The plan is **BLOCKED**, and the verdict is recorded") == "BLOCKED"
    assert el.verdict_of("modal-depiction: shrine.SumoRing - COVERAGE 0 findings; TRUTH 0; LINKS 0\n\nmore") == "clean"
    assert el.verdict_of("modal-depiction: x - COVERAGE 1 findings; TRUTH 0; LINKS 0") == "findings"
    assert el.verdict_of("No claims are touched.") == ""
    stop = el.line({"hook_event_name": "SubagentStop", "agent_type": "spec-fidelity", "agent_id": "a", "last_assistant_message": "**FAITHFUL**"})
    assert stop["verdict"] == "FAITHFUL"
    rows = [
        _tool_use("2026-10-10T10:00:00Z", "t1", "Agent", {"subagent_type": "spec-fidelity", "prompt": "p"}),
        _result("2026-10-10T10:00:01Z", "t1", {"status": "async_launched", "agentId": "ag1"}),
        {
            "type": "queue-operation",
            "operation": "enqueue",
            "timestamp": "2026-10-10T10:03:00Z",
            "sessionId": "s",
            "content": "<task-notification> <task-id>ag1</task-id> <result>**Round 3 verdict: CLEAR.** I recorded it</result>",
        },
    ]
    assert el.from_transcript(rows)[-1]["verdict"] == "CLEAR"
    assert fr.verdicts(el.from_transcript(rows)) == {"spec-fidelity": {"CLEAR": 1}}
