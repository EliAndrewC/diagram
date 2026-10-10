"""`scripts/reviews/review_cost.py` - a review run's wall time and tokens, read off its transcript (feature 294, FR-010)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("review_cost", REPO / "scripts/reviews/review_cost.py")
assert _spec and _spec.loader
rc = importlib.util.module_from_spec(_spec)
sys.modules["review_cost"] = rc
_spec.loader.exec_module(rc)


def _line(ts: str, req: str | None, usage: dict | None, mid: str | None = None) -> str:
    msg: dict = {"role": "assistant"}
    if usage is not None:
        msg["usage"] = usage
    if mid:
        msg["id"] = mid
    d: dict = {"timestamp": ts, "message": msg}
    if req:
        d["requestId"] = req
    return json.dumps(d)


U = {"input_tokens": 2, "cache_read_input_tokens": 1000, "cache_creation_input_tokens": 500, "output_tokens": 300}


def test_a_streamed_call_is_counted_once_and_the_wall_spans_the_transcript() -> None:
    lines = [
        json.dumps({"timestamp": "2026-10-01T10:00:00Z", "message": {"role": "user", "content": "go"}}),
        _line("2026-10-01T10:00:05Z", "r1", {**U, "output_tokens": 1}),
        _line("2026-10-01T10:00:06Z", "r1", {**U, "output_tokens": 300}),  # the same call, streamed: its last line counts
        _line("2026-10-01T10:01:40Z", None, U, mid="m2"),
        _line("2026-10-01T10:01:41Z", "r3", None),
        "not json",
    ]
    c = rc.cost(lines)
    assert c == {"wall_s": 101, "input": 3004, "cache_read": 2000, "cache_write": 1000, "output": 600, "calls": 2}
    assert rc.cells(c) == "101 s | 3k in (2k cached) / 0.6k out"
    assert rc.cost([])["wall_s"] == 0


def test_main_finds_the_newest_transcript_or_says_it_has_none(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    d = tmp_path / "proj" / "sess" / "subagents"
    d.mkdir(parents=True)
    (d / "agent-abc.jsonl").write_text(_line("2026-10-01T10:00:00Z", "r1", U) + "\n" + _line("2026-10-01T10:00:10Z", "r2", U) + "\n")
    assert rc.main(["--agent", "abc", "--root", str(tmp_path)]) == 0
    assert capsys.readouterr().out.strip() == "10 s | 3k in (2k cached) / 0.6k out"
    assert rc.main(["--agent", "zzz", "--root", str(tmp_path)]) == 1
    assert "no transcript" in capsys.readouterr().err


def _prompt(ts: str, text: str) -> str:
    return json.dumps({"timestamp": ts, "message": {"role": "user", "content": text}})


def test_a_resumed_agent_is_split_at_each_new_prompt_and_main_prints_a_line_per_return(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Feature 371 (plan review 2): each return of a resumed agent is its own pass with its own cost. A tool result is not a
    prompt, so a transcript that returned once stays one segment and prints as it always did."""
    u = {"input_tokens": 100, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0, "output_tokens": 10}
    tool = json.dumps({"timestamp": "2026-10-10T10:00:10Z", "message": {"role": "user", "content": [{"type": "tool_result", "content": "x"}]}})
    one = [_prompt("2026-10-10T10:00:00Z", "go"), tool, _line("2026-10-10T10:00:30Z", "r1", u)]
    assert len(rc.segments(one)) == 1
    two = [*one, _prompt("2026-10-10T11:00:00Z", "round 2"), _line("2026-10-10T11:00:40Z", "r2", u)]
    parts = rc.segments(two)
    assert len(parts) == 2 and rc.cost(parts[1])["wall_s"] == 40 and rc.cost(parts[0])["wall_s"] == 30
    d = tmp_path / "p" / "s" / "subagents"
    d.mkdir(parents=True)
    (d / "agent-r.jsonl").write_text("\n".join(two) + "\n")
    assert rc.main(["--agent", "r", "--root", str(tmp_path)]) == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0].startswith("return 1: 30 s |") and out[1].startswith("return 2: 40 s |")
