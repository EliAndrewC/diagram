"""`scripts/_agent_census.py` (feature 251, FR-001): what each subagent check cost, from the transcripts.

WHAT THESE PROVE. The one trap the script exists to avoid - a transcript repeats a message's usage on
every content block, with `output_tokens` growing - is tested directly: three records of one message
count once, at the largest figure. The rest is the table: runs counted per agent type, a `SINCE` filter,
the ad-hoc block naming the model a no-model dispatch inherited, and the walk taking only this
repository's projects.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[5]


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_agent_census", REPO / "scripts" / "_agent_census.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ac = _load()


def _rec(mid: str, out: int, *, cached: int = 100, fresh: int = 10, create: int = 5, thinking: int = 0, model: str = "claude-opus-5", ts: str = "2026-09-10T00:00:00Z") -> dict:
    usage = {"input_tokens": fresh, "cache_creation_input_tokens": create, "cache_read_input_tokens": cached, "output_tokens": out, "output_tokens_details": {"thinking_tokens": thinking}}
    return {"type": "assistant", "timestamp": ts, "message": {"id": mid, "model": model, "usage": usage}}


def test_a_message_written_once_per_block_counts_once_at_its_largest_usage():
    """R2: the first record of a message carries an early output count; the last carries the real one."""
    folded = ac.fold_usage([_rec("m1", 4), _rec("m1", 4), _rec("m1", 262, thinking=40), _rec("m2", 150)])
    assert folded["turns"] == 2
    assert folded["output"] == 262 + 150
    assert folded["thinking"] == 40
    assert folded["cached"] == 200, "cached input is per message, not per block"
    assert folded["fresh"] == 30, "fresh input is uncached plus cache-creation"


def test_records_that_are_not_assistant_usage_are_ignored():
    records = [{"type": "user", "timestamp": "2026-09-01T00:00:00Z", "message": {"role": "user"}}, {"type": "assistant", "message": {"id": "m0"}}, _rec("m1", 9)]
    folded = ac.fold_usage(records)
    assert folded["turns"] == 1 and folded["output"] == 9
    assert folded["started"] == "2026-09-01T00:00:00Z", "the run starts at its first record, whatever its type"


def test_a_run_that_never_answered_is_a_run_with_no_model():
    folded = ac.fold_usage([])
    assert folded == {"fresh": 0, "cached": 0, "output": 0, "thinking": 0, "turns": 0, "model": "none", "started": ""}


def _run(kind: str, out: int, *, meta_model: str | None = None, model: str = "claude-opus-5", ts: str = "2026-09-10T00:00:00Z") -> tuple[dict, dict]:
    meta = {"agentType": kind}
    if meta_model is not None:
        meta["model"] = meta_model
    return meta, ac.fold_usage([_rec("m", out, model=model, ts=ts)])


def test_rows_group_by_agent_type_and_order_by_input():
    runs = [_run("quote-check", 10), _run("quote-check", 30), _run("entry-drift", 5)]
    table, adhoc = ac.rows(runs)
    assert [r["agent"] for r in table] == ["quote-check", "entry-drift"]
    assert table[0]["runs"] == 2 and table[0]["output"] == 40
    assert table[0]["models"] == {"claude-opus-5": 2}
    assert adhoc == [], "a named check is not ad-hoc"


def test_the_ad_hoc_block_names_the_model_a_no_model_dispatch_ran_on():
    """FR-010's measurement: a `general-purpose` dispatch with no model inherits the session's."""
    runs = [
        _run("general-purpose", 1, model="claude-fable-5-1"),
        _run("general-purpose", 1, meta_model="inherit", model="claude-fable-5-1"),
        _run("general-purpose", 1, meta_model="sonnet", model="claude-sonnet-5"),
    ]
    _, adhoc = ac.rows(runs)
    assert adhoc == [{"agent": "general-purpose", "runs": 3, "no_model": 2, "inherited": {"claude-fable-5-1": 2}}]


def test_since_drops_the_runs_that_started_before_it():
    runs = [_run("source-reader", 1, ts="2026-09-01T10:00:00Z"), _run("source-reader", 1, ts="2026-09-19T10:00:00Z")]
    table, _ = ac.rows(runs, since="2026-09-10")
    assert table[0]["runs"] == 1


def test_a_run_with_no_agent_type_is_counted_as_unknown():
    table, _ = ac.rows([({}, ac.fold_usage([_rec("m", 2)]))])
    assert table[0]["agent"] == "unknown"


def _tree(root: pathlib.Path, project: str, agent_id: str, kind: str, lines: list[str]) -> None:
    sub = root / project / "session-1" / "subagents"
    sub.mkdir(parents=True, exist_ok=True)
    (sub / f"agent-{agent_id}.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (sub / f"agent-{agent_id}.meta.json").write_text(json.dumps({"agentType": kind}), encoding="utf-8")


def test_the_walk_takes_this_repositorys_projects_and_no_other(tmp_path, capsys):
    good = [json.dumps(_rec("m1", 7)), "not json at all"]
    _tree(tmp_path, "-diagram", "a1", "quote-check", good)
    _tree(tmp_path, "-diagram--clones-diagram-research", "a2", "quote-check", good)
    _tree(tmp_path, "-gm-assistant", "a3", "voice-audit", good)
    assert len(ac.transcripts(tmp_path)) == 2
    assert ac.transcripts(tmp_path / "absent") == []
    out_json = tmp_path / "census.json"
    assert ac.main(["--root", str(tmp_path), "--json", str(out_json)]) == 0
    printed = capsys.readouterr().out
    assert "quote-check" in printed and "voice-audit" not in printed
    saved = json.loads(out_json.read_text())
    assert saved["agents"][0]["runs"] == 2 and saved["agents"][0]["output"] == 14


def test_a_transcript_with_no_meta_still_counts(tmp_path):
    sub = tmp_path / "-diagram" / "s" / "subagents"
    sub.mkdir(parents=True)
    (sub / "agent-x.jsonl").write_text(json.dumps(_rec("m1", 3)) + "\n", encoding="utf-8")
    meta, use = ac.read_run(sub / "agent-x.jsonl")
    assert meta == {} and use["output"] == 3


def test_render_prints_per_run_means_and_the_ad_hoc_block():
    table, adhoc = ac.rows([_run("general-purpose", 100, model="claude-fable-5-1"), _run("general-purpose", 300, model="claude-fable-5-1")])
    text = ac.render(table, adhoc)
    assert "general-purpose" in text and "200" in text, "out/run is the mean of 100 and 300"
    assert "with no model: claude-fable-5-1 x2" in text
    assert ac.render([], []).count("\n") == 1, "an empty census is a header and a rule"
