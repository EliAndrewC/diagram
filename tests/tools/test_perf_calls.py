"""`tools/perf_calls.py` (feature 427 T03, D3): the call counts are what is watched - the line, the version guard, a `-start`
with no counts, a decrease, the arbiter's accept and the refusal's command."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from l7r.diagram.tools import perf_calls as pc

V = {"python": "3.14.0", "numpy": "2.3.0", "shapely": "2.1.0"}


def _snap(calls: dict[str, int], versions: dict[str, str] | None = None, scaling: dict[str, int] | None = None, commit: str = "c2") -> dict[str, Any]:
    out: dict[str, Any] = {"versions": V if versions is None else versions, "commit": commit, "rows": [{"seed": 4, "calls": calls}]}
    if scaling is not None:
        out["scaling"] = [{"seed": 4, "households": 40, "calls": scaling}]
    return out


def test_an_increase_over_the_stage_line_is_owed_and_one_under_it_is_not() -> None:
    base = _snap({"web": 100_000, "field": 900_000})
    assert pc.compare(base, _snap({"web": 104_000, "field": 900_000})).owed == [], "4% in a stage, 0.4% in the total: under both lines"
    v = pc.compare(base, _snap({"web": 106_000, "field": 900_000}))
    assert v.owed == ["web on seed 4: 100,000 -> 106,000 calls (+6%)"], "6% in web; the total's 0.6% is under its line"
    assert v.lines == ["calls: 1,000,000 -> 1,006,000 (+0.6%) over 2 stage rolls"]


def test_the_total_line_and_the_scaling_sizes() -> None:
    base = _snap({"web": 100_000, "field": 100_000}, scaling={"web": 1_000_000})
    v = pc.compare(base, _snap({"web": 104_000, "field": 104_000}, scaling={"web": 1_030_000}))
    assert v.owed == ["the total: 1,200,000 -> 1,238,000 calls (+3.2%)"], "each stage under 5%, the total over 2%"
    v = pc.compare(base, _snap({"web": 100_000, "field": 100_000}, scaling={"web": 1_100_000}))
    assert "web on seed 4 at 40 households: 1,000,000 -> 1,100,000 calls (+10%)" in v.owed


def test_a_small_stage_and_a_decrease_owe_nothing() -> None:
    assert pc.compare(_snap({"burial": 17, "web": 100_000}), _snap({"burial": 40, "web": 90_000})).owed == [], "17 -> 40 calls: under the floor"
    assert pc.compare(_snap({"web": 100_000}), _snap({"web": 50_000})).lines == ["calls: 100,000 -> 50,000 (-50.0%) over 1 stage rolls"]


def test_a_pair_on_other_versions_or_without_counts_is_not_compared_and_owes_a_ruling() -> None:
    """D3: never passes silently - the -start re-taken on the current versions, or a ruling."""
    v = pc.compare(_snap({"web": 1}), _snap({"web": 1}, versions={**V, "shapely": "2.2.0"}))
    assert len(v.owed) == 1 and "different versions" in v.owed[0] and v.lines == []
    v = pc.compare({"versions": V, "rows": [{"seed": 4}]}, _snap({"web": 1}))
    assert v.owed == ["the -start carries no call counts (a snapshot from before feature 427 T02): not compared"]
    v = pc.compare(_snap({"web": 1}), {"versions": V, "rows": [{"seed": 4}]})
    assert "the -end carries no call counts" in v.owed[0]


def test_the_arbiter_s_accept_and_the_refusal_s_command(tmp_path: Path) -> None:
    cur = _snap({"web": 1}, commit="abc1234")
    assert pc.subject("427", cur) == "427-calls-abc1234"
    specs = tmp_path / "specs"
    (specs / "427-x").mkdir(parents=True)
    assert not pc.accepted(specs, "427", cur)
    (specs / "427-x" / "arbiter.jsonl").write_text("not json\n" + json.dumps({"trigger": "ask:427-calls-abc1234", "ruling": "continue"}) + "\n")
    assert not pc.accepted(specs, "427", cur), "only an accept clears it"
    with (specs / "427-x" / "arbiter.jsonl").open("a") as fh:
        fh.write(json.dumps({"trigger": "ask:427-calls-abc1234", "ruling": "accept"}) + "\n")
    assert pc.accepted(specs, "427", cur)
    text = pc.refusal("427", cur, ['web on seed 4: 1 -> 2 calls (+100%) "quoted"'])
    assert "REFUSED" in text and 'make arbiter-ask SUBJECT=427-calls-abc1234 WHY="web on seed 4' in text and '"quoted"' not in text.split("WHY=")[1].split(" - the")[0]
