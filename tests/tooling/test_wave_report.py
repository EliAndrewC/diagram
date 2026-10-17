"""`scripts/measure/wave_report.py` - a wave's cost through `check-wave` against the last hand-launched wave (feature 383
amendment 7, FR-046, plan D50)."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("wave_report", REPO / "scripts/measure/wave_report.py")
assert spec and spec.loader
wr = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = wr
spec.loader.exec_module(wr)


def _agent(d: pathlib.Path, aid: str, start: str, read: int, written: int, meta: dict) -> None:
    d.mkdir(parents=True, exist_ok=True)
    (d / f"agent-{aid}.meta.json").write_text(json.dumps(meta), encoding="utf-8")
    usage = {"cache_read_input_tokens": read, "cache_creation_input_tokens": written}
    rows = [{"type": "user", "timestamp": start, "message": {"role": "user", "content": "go"}},
            {"type": "assistant", "timestamp": start, "message": {"id": f"m-{aid}", "usage": usage, "content": []}}]
    (d / f"agent-{aid}.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\nnot json\n", encoding="utf-8")


def _note(t: str, tool_use: str) -> dict:
    return {"type": "user", "timestamp": t, "message": {"role": "user", "content": f"<task-notification>\n<task-id>x</task-id>\n<tool-use-id>{tool_use}</tool-use-id>\n</task-notification>"}}


def _turn(t: str, context: int) -> dict:
    return {"type": "assistant", "timestamp": t, "message": {"id": f"w{t}", "usage": {"cache_read_input_tokens": context, "cache_creation_input_tokens": 0}, "content": []}}


def test_a_workflow_wave_against_the_last_hand_launched_one(tmp_path: pathlib.Path) -> None:
    proj = tmp_path / "-diagram"
    session = proj / "s1"
    run = session / "subagents" / "workflows" / "wf_1"
    for i, (read, written) in enumerate([(0, 6178), (3462, 2716), (3462, 2716), (3462, 2716)]):
        _agent(run, f"w{i}", f"2026-10-17T22:34:4{i + 1}.000Z", read, written, {"agentType": "claims-triage"})
    (run / "journal.jsonl").write_text(json.dumps({"type": "result", "agentId": "w3"}) + "\n", encoding="utf-8")
    hand = [f"toolu_h{i}" for i in range(4)]
    for i, tid in enumerate(hand):
        _agent(session / "subagents", f"h{i}", f"2026-10-17T20:00:0{i}.000Z", 2336 if i == 0 else 4443, 4620 if i == 0 else 2514, {"agentType": "quote-check", "toolUseId": tid})
    # the hand wave: one message written as one record per tool call, under the message's id
    launches = [{"type": "assistant", "timestamp": "2026-10-17T19:59:59.000Z", "message": {"id": "launch", "content": [
        {"type": "tool_use", "id": tid, "name": "Agent", "input": {"subagent_type": "quote-check"}}]}} for tid in hand]
    main = [*launches, _note("2026-10-17T20:01:00.000Z", "toolu_h0"), _turn("2026-10-17T20:01:01.000Z", 400_000),
            _note("2026-10-17T20:02:00.000Z", "toolu_h1"), _turn("2026-10-17T20:02:01.000Z", 410_000),
            _note("2026-10-17T20:03:00.000Z", "toolu_other"), _turn("2026-10-17T20:03:01.000Z", 1),
            _note("2026-10-17T22:34:44.500Z", "toolu_wf"), _turn("2026-10-17T22:34:45.000Z", 930_000)]
    (proj / "s1.jsonl").write_text("\n".join(json.dumps(r) for r in main) + "\n", encoding="utf-8")
    out = wr.report(run)
    assert "WORKFLOW RUN wf_1 (s1): 4 agent(s)" in out
    assert "read       0  written   6,178" in out and out.count("read   3,462  written   2,716") == 3
    assert "main-session wakes: 1, median context re-read 930k" in out, "the run's one notification"
    assert "LAST HAND-LAUNCHED WAVE: 4 quote-check in one message (-diagram/s1)" in out
    assert "main-session wakes: 2, median context re-read 405k" in out, "the wave's own notifications only"
    assert wr.newest_run(proj) == run
    assert wr.main(["--run", str(run)]) == 0


def test_nothing_to_measure(tmp_path: pathlib.Path, capsys) -> None:  # noqa: ANN001
    run = tmp_path / "-diagram" / "s" / "subagents" / "workflows" / "wf_0"
    run.mkdir(parents=True)
    assert "has no agent with a request yet" in wr.report(run)
    _agent(run, "a", "2026-10-17T10:00:00.000Z", 0, 100, {})
    (tmp_path / "-diagram" / "s.jsonl").write_text("", encoding="utf-8")
    assert "no hand-launched wave of 4+ before it" in wr.report(run)
    assert wr.main(["--root", str(tmp_path / "none")]) == 1 and "no workflow run" in capsys.readouterr().out
