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


tt = _load("turn_time")


def _record(tmp: pathlib.Path, name: str, commit: str, seeds: list[tuple[int, list[str]]], feature: str | None = None) -> None:
    rec = {"commit": commit, "seeds": [{"seed": s, "failures": f} for s, f in seeds]}
    if feature is not None:
        rec["feature"] = feature
    (tmp / f"{name}.json").write_text(json.dumps(rec), encoding="utf-8")


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
