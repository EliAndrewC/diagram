"""The measurement reports feature 375 put to the GM: the review checks' yield (amendment 8, FR-037), the cohort's seeds
(amendment 8, FR-038), and the model's time per turn (amendment 7, FR-034)."""

from __future__ import annotations

import importlib.util
import json
import pathlib
from types import ModuleType

import pytest

MEASURE = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "measure"
pytestmark = pytest.mark.tooling


def _load(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, MEASURE / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ry = _load("review_yield")
cs = _load("cohort_seeds")
tt = _load("turn_time")

LEDGER = """
| date | check | subject | verdict | finding | class | missed | acted on | wall | tokens |
|---|---|---|---|---|---|---|---|---|---|
| 2026-09-20 | glyph-check | 300 well | FINDINGS 1 | too old | judgment | yes | fixed | 60 s | 10k in / 1.0k out |
| 2026-10-01 | glyph-check | 310 well | FINDINGS 1 | the well reads as a pond | geometric | yes | applied | 1800 s | 100k in / 2.0k out |
| 2026-10-01 | glyph-check | 311 byre | FINDINGS 1 | a shade too dark | judgment | no | verified (it is the convention) | 1800 s | 100k in / 3.0k out |
| 2026-10-02 | glyph-check | 311 byre | FINDINGS 1 | a size question | judgment | yes | put to the GM | 1800 s | 100k in / 1.0k out |
| 2026-10-02 | spec-fidelity | feature 312 spec | FAITHFUL | - | nothing | no | verified | 600 s | 50k in / 4.0k out |
| 2026-10-03 | spec-fidelity | feature 312 plan | BLOCKED 1 | a decision unrecorded | judgment | yes | re-dispatched | 600 s | 50k in / 4.0k out |
| 2026-10-03 | quote-check | 0021 | PASS | - | nothing | no | - | ? | ? |
| 2026-10-04 | a short row | 9 cells | x | x | x | x | x | 1 s |
"""


def test_review_yield_counts_each_column_from_its_cells() -> None:
    rows = ry.rows(LEDGER, "2026-09-26")
    assert len(rows) == 5, "before --since, no wall time and a short row are not measured rows"
    t = ry.table(rows)
    g = t["glyph-check"]
    assert (g["passes"], g["with a finding"], g["acted on"], g["dismissed"], g["deferred"], g["author missed"]) == (3, 3, 1, 1, 1, 2)
    assert g["hours"] == 1.5 and g["k tokens out"] == 6.0 and g["features"] == 2 and g["acted on per hour"] == 0.7
    s = t["spec-fidelity"]
    assert (s["with a finding"], s["acted on"], s["not acted on"], s["features"]) == (1, 0, 1, 1), "a re-dispatch changed nothing"
    out = ry.render(t, "2026-09-26", len(rows))
    assert out.index("| glyph-check |") < out.index("| spec-fidelity |"), "sorted by hours"


@pytest.mark.parametrize(
    ("cell", "outcome"),
    [
        ("applied", "acted on"),
        ("fixed (the EDIT applied)", "acted on"),
        ("index recorded; round 2", "acted on"),
        ("filed as rows", "acted on"),
        ("to the follow-up", "acted on"),
        ("not applied: carried in specs/335/briefs", "acted on"),
        ("nothing", "dismissed"),
        ("nothing for the GM", "dismissed"),
        ("answered in feature 328", "dismissed"),
        ("left: the reason is the GM's allowance", "dismissed"),
        ("verified", "dismissed"),
        ("spec accepted", "dismissed"),
        ("none", "dismissed"),
        ("accepted (the drift already on the report)", "dismissed"),
        ("plan accepted", "dismissed"),
        ("declined: contradicts FR-015", "dismissed"),
        ("no change", "dismissed"),
        ("no-change", "dismissed"),
        ("put to the GM", "deferred"),
        ("left for the next session", "deferred"),
        ("not applied: needs a new passage", "deferred"),
        ("-", "not acted on"),
        ("re-dispatched; engine frozen", "not acted on"),
    ],
)
def test_review_yield_reads_each_kind_of_acted_on_cell(cell: str, outcome: str) -> None:
    """The plan review (amendment 8): "nothing" in 64 cells, "answered" and a bare "left" were counted as acted on; a
    finding filed elsewhere is acted on (FR-037: fixed, filed) whatever its cell opens with."""
    assert ry.outcome(cell) == outcome


def test_review_yield_records_its_table(tmp_path: pathlib.Path) -> None:
    ledger, m = tmp_path / "ledger.md", tmp_path / "m.json"
    ledger.write_text(LEDGER, encoding="utf-8")
    m.write_text("{}", encoding="utf-8")
    assert ry.main(["--ledger", str(ledger), "--record", str(m), "--key", "k"]) == 0
    assert json.loads(m.read_text())["k"]["value"]["by check"]["glyph-check"]["passes"] == 3
    assert ry.main(["--ledger", str(ledger), "--record", str(m)]) == 2, "--record needs --key"


def _record(tmp: pathlib.Path, name: str, commit: str, seeds: list[tuple[int, list[str]]], feature: str | None = None) -> None:
    rec = {"commit": commit, "seeds": [{"seed": s, "failures": f} for s, f in seeds]}
    if feature is not None:
        rec["feature"] = feature
    (tmp / f"{name}.json").write_text(json.dumps(rec), encoding="utf-8")


def test_cohort_seeds_names_each_failure_its_seeds_the_span_and_the_fewest_first_seeds(tmp_path: pathlib.Path) -> None:
    _record(tmp_path, "a", "c1", [(3, []), (10, ["refused:WebRefused"]), (20, ["refused:WebRefused"])])
    _record(tmp_path, "b", "c2", [(7, ["wells_are_shared[1]"]), (901, ["row_rules[2]"])], feature="380")
    _record(tmp_path, "c", "c3", [(31, ["wells_are_shared[2]"]), (12, [])], feature="")
    (tmp_path / "features.json").write_text('{"c1": "374"}', encoding="utf-8")
    s = cs.summary(*cs.load(tmp_path))
    assert s["changes"] == ["feature 374", "feature 380", "unattributed (c3)"], "a map for old records, else by commit"
    assert s["failures"]["refused:WebRefused"] == {"seeds": [10, 20], "changes": ["feature 374"]}
    assert s["failures"]["wells_are_shared"]["seeds"] == [7, 31], "a failure is named without its count"
    assert s["fewest first seeds finding every failure"] == 10, "WebRefused first found at 10, wells at 7"
    assert s["failures only a pinned seed found"] == ["row_rules"]
    out = cs.render(s)
    assert "3 change(s)" in out and "pinned rows for row_rules" in out


def test_cohort_seeds_reports_fresh_records_as_a_rate_and_leaves_them_out_of_the_fewest_seeds(tmp_path: pathlib.Path) -> None:
    """Feature 386: a fresh block is a RATE, never in the fewest-first-seeds count; a pinned seed is one of the six, not "901 on"."""
    _record(tmp_path, "a", "c1", [(10, ["lane_knots[1]"]), (907, ["row_rules[1]"])])
    (tmp_path / "f.json").write_text(
        json.dumps(
            {
                "utc": "u1",
                "commit": "c2",
                "first_seed": 12000,
                "seeds": [
                    {"seed": 12000, "failures": ["refused:SiteRefused"], "verdict": "refused"},
                    {"seed": 12001, "failures": [], "verdict": "pass"},
                    {"seed": 901, "failures": [], "verdict": "pass"},
                ],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "g.json").write_text(
        json.dumps(
            {
                "utc": "u2",
                "commit": "c3",
                "first_seed": 400,
                "fresh": True,
                "seeds": [{"seed": 400, "failures": [], "verdict": "pass"}, {"seed": 403, "failures": ["lane_knots[1]"], "verdict": "fail"}],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "h.json").write_text(
        json.dumps(
            {"utc": "u3", "commit": "c4", "first_seed": 1, "seeds": [{"seed": 1, "failures": [], "verdict": "pass"}, {"seed": 50000, "failures": ["water_rules[1]"], "verdict": "fail", "fresh": True}]}
        ),
        encoding="utf-8",
    )
    s = cs.summary(*cs.load(tmp_path))
    assert "water_rules" not in s["failures"], "a record's own fresh block stays out of the fixed reading"
    assert "refused:SiteRefused" not in s["failures"], "a fresh record's failures stay out of the fixed reading"
    assert s["failures"]["lane_knots"]["seeds"] == [10], "nor do its seeds join a fixed failure"
    assert s["fewest first seeds finding every failure"] == 907 and s["failures only a pinned seed found"] == [], "907 is not a pinned row"
    assert [(f["failed"], f["rolled"]) for f in s["fresh"]] == [(1, 2), (1, 2), (1, 1)], "the pinned row is not counted in the rate"
    out = cs.render(s)
    assert "u1 c2 from 12000: 1 of 2 failed (50%) - seeds 12000" in out and "pooled: 3 of 5 failed (60%)" in out and "u3 c4 from 50000: 1 of 1" in out


def test_cohort_seeds_with_no_records_and_its_record(tmp_path: pathlib.Path) -> None:
    s = cs.summary(*cs.load(tmp_path))
    assert s["fewest first seeds finding every failure"] == 0 and "no failures recorded" in cs.render(s)
    m = tmp_path.parent / f"{tmp_path.name}-m.json"  # beside the records, never among them
    m.write_text("{}", encoding="utf-8")
    assert cs.main(["--log", str(tmp_path), "--record", str(m), "--key", "k"]) == 0 and json.loads(m.read_text())["k"]["value"]["records"] == 0
    assert cs.main(["--log", str(tmp_path), "--record", str(m)]) == 2


def _line(kind: str, t: str, **extra: object) -> str:
    return json.dumps({"type": kind, "timestamp": t, **extra})


def test_turn_time_measures_reply_after_a_tool_result_and_fits_it(tmp_path: pathlib.Path) -> None:
    tool = {"message": {"content": [{"type": "tool_result"}]}}
    lines = []
    for i, (ctx, gap, out) in enumerate([(100_000, 6.0, 1000), (300_000, 8.0, 1000), (500_000, 11.0, 2000), (700_000, 14.0, 3000)]):
        lines.append(_line("user", f"2026-10-12T00:{i:02d}:00Z", **tool))
        lines.append(_line("assistant", f"2026-10-12T00:{i:02d}:{int(gap):02d}Z", requestId=f"r{i}", message={"usage": {"cache_read_input_tokens": ctx, "output_tokens": out}}))
    lines.append(_line("assistant", "2026-10-12T00:09:00Z", requestId="r3", message={"usage": {}}))  # a repeat of r3, and no tool result before it
    lines.append("not json")
    pts = tt.turns(lines)
    assert [p[1] for p in pts] == [6.0, 8.0, 11.0, 14.0]
    s = tt.summary(pts)
    assert s["turns"] == 4 and s["median turn s"] == 9.5 and set(s["median turn s by context (200k bands)"]) == {"0-200k", "200-400k", "400-600k", "600-800k"}
    assert s["fit: s fixed, per 100k context, per 1k output"] == [4.0, 1.0, 1.0], "4 s fixed, 1 s per 100k read, 1 s per 1k written"
    f = tmp_path / "t.jsonl"
    f.write_text("\n".join(lines), encoding="utf-8")
    m = tmp_path / "m.json"
    m.write_text("{}", encoding="utf-8")
    assert tt.main([str(f), "--record", str(m), "--key", "k"]) == 0 and json.loads(m.read_text())["k"]["value"]["turns"] == 4
    assert tt.main([str(f), "--record", str(m)]) == 2
    (tmp_path / "e.jsonl").write_text("", encoding="utf-8")
    assert tt.main([str(tmp_path / "e.jsonl")]) == 2, "no turns"
