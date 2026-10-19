"""`scripts/measure/fix_yield.py` and `hm_arbiter.fix_measure_of` - each tooling fix's yield (feature 385 T119, D139-D141).

The GM, 2026-10-19 (amendment 10, change 3): each fix's yield measured against the time it was meant to save, so a fix that
saves nothing is retired. 49 of the first 60 hourly step-backs had named a fix, and nothing said whether any saved its time.
"""

from __future__ import annotations

import datetime
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "measure"))
sys.path.insert(0, str(REPO / "scripts" / "reviews"))
sys.path.insert(0, str(REPO / "scripts" / "hooks" / "lib"))
import fix_yield as fy  # noqa: E402
import hm_arbiter as ha  # noqa: E402

T0 = datetime.datetime(2026, 10, 19, tzinfo=datetime.UTC).timestamp()


def _iso(t: float) -> str:
    return datetime.datetime.fromtimestamp(t, datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _session(hours: float, start: float, every: float, cmd: str, secs: float, agent: str = "") -> list[dict]:
    """A main session `hours` long with a record each minute, and every `every` seconds a Bash call of `cmd` lasting `secs`
    (or an Agent dispatch of `agent`)."""
    out, t, n = [], start, 0
    while t < start + hours * 3600:
        out.append({"timestamp": _iso(t), "message": {"content": [{"type": "text", "text": "x"}]}})
        if t - start >= n * every:
            if agent:
                use = {"type": "tool_use", "id": f"a{t}", "name": "Agent", "input": {"subagent_type": agent}}
                out.append({"timestamp": _iso(t), "message": {"content": [use]}})
            else:
                use = {"type": "tool_use", "id": f"b{t}", "name": "Bash", "input": {"command": cmd}}
                out.append({"timestamp": _iso(t), "message": {"content": [use]}})
                out.append({"timestamp": _iso(t + secs), "message": {"content": [{"type": "tool_result", "tool_use_id": f"b{t}"}]}})
            n += 1
        t += 60
    return out


def test_a_fix_whose_rate_fell_is_saving_and_one_whose_rate_held_saves_nothing() -> None:
    before = _session(6, T0, 600, "make cohort", 300)  # 5 min of cohort every 10 min
    fix = {"trigger": "hour:x@1", "tooling_fix": "f", "fix_measure": r"make cohort\b", "fix_minutes": 12, "utc": _iso(T0 + 6 * 3600), "status": "done", "settled": _iso(T0 + 6 * 3600)}
    fell = fy.verdict(fix, before + _session(4, T0 + 7 * 3600, 1200, "make cohort", 60))
    assert fell["verdict"] == "saving" and fell["after"] < fell["before"] and fell["after_hours"] >= fy.YIELD_MIN_HOURS
    held = fy.verdict(fix, before + _session(4, T0 + 7 * 3600, 600, "make cohort", 300))
    assert held["verdict"].startswith("saves nothing")
    early = fy.verdict(fix, before + _session(1, T0 + 7 * 3600, 1200, "make cohort", 60))
    assert early["verdict"] == "too early"
    other = fy.verdict({**fix, "fix_measure": "make quick"}, before + _session(4, T0 + 7 * 3600, 600, "make cohort", 300))
    assert other["before"] == 0 and other["after"] == 0 and other["verdict"].startswith("saves nothing"), "nothing to cut, nothing cut"


def test_an_agent_measure_counts_that_check_s_dispatches_and_a_fix_unmade_or_unmeasured_is_named() -> None:
    recs = _session(6, T0, 1800, "", 0, agent="impl-drift") + _session(4, T0 + 7 * 3600, 3600, "", 0, agent="impl-drift")
    fix = {"trigger": "t", "tooling_fix": "f", "fix_measure": "agent:impl-drift", "utc": _iso(T0 + 6 * 3600), "status": "done", "settled": _iso(T0 + 6.5 * 3600)}
    row = fy.verdict(fix, recs)
    assert row["verdict"] == "saving" and row["before"] == pytest.approx(2, abs=0.2) and row["after"] == pytest.approx(1, abs=0.2)
    assert fy.verdict({**fix, "status": "declined"}, recs)["verdict"] == "not made (declined)"
    assert fy.verdict({k: v for k, v in fix.items() if k != "fix_measure"}, recs)["verdict"].startswith("unmeasured")
    table = fy.table([row])
    assert "| t | `agent:impl-drift` | - |" in table and "saving" in table


def test_fixes_pairs_each_ruling_with_its_settling_and_an_assigned_measure() -> None:
    rows = [
        {"trigger": "a", "tooling_fix": "fa", "utc": "u1"},
        {"trigger": "b", "tooling_fix": "fb", "fix_measure": "own", "fix_minutes": 3, "utc": "u2"},
        {"trigger": "c", "ruling": "continue"},
        {"fix_of": "a", "status": "done", "utc": "u3"},
    ]
    got = {f["trigger"]: f for f in fy.fixes(rows, {"a": {"fix_measure": "make x", "by": "T119"}, "b": {"fix_measure": "not this"}})}
    assert set(got) == {"a", "b"}
    assert got["a"]["fix_measure"] == "make x" and got["a"]["status"] == "done" and got["a"]["settled"] == "u3" and "by" not in got["a"]
    assert got["b"]["fix_measure"] == "own" and got["b"]["status"] == "open", "a ruling's own measure wins"


def test_a_ruling_naming_a_fix_is_refused_without_a_measure() -> None:
    """D139: 46 fixes were ruled as free sentences, and none could be measured afterwards."""
    for bad in ({}, {"fix_measure": "make x"}, {"fix_minutes": 10}, {"fix_measure": "agent:", "fix_minutes": 1}, {"fix_measure": "make (", "fix_minutes": 1}, {"fix_measure": "x", "fix_minutes": -1}):
        with pytest.raises(ValueError, match="fix_measure"):
            ha.fix_measure_of(bad)
    assert ha.fix_measure_of({"fix_measure": "agent:impl-drift", "fix_minutes": "12"}) == {"fix_measure": "agent:impl-drift", "fix_minutes": 12.0}


def test_the_report_reads_the_feature_s_record_and_its_assigned_measures(tmp_path: pathlib.Path) -> None:
    d = tmp_path / "specs" / "385-x"
    d.mkdir(parents=True)
    assert fy.report(tmp_path, d, []) == "(no tooling fix ruled)\n"
    (d / "arbiter.jsonl").write_text(json.dumps({"trigger": "a", "tooling_fix": "fa", "utc": _iso(T0)}) + "\n")
    (d / "fix-measures.json").write_text(json.dumps({"a": {"fix_measure": "make x"}}))
    out = fy.report(tmp_path, d, [])
    assert "| a | `make x` | - |" in out and "not made (open)" in out
