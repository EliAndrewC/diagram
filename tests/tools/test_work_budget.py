"""`make work-budget` (feature 443 T02, D4): the counts summarized per stage and size, the exponent, the budget's ratio, the
standing record written - its rolls stubbed (a real run is the standing record's own measurement)."""

import json
from pathlib import Path

import pytest

from l7r.diagram.tools import work_budget as wb


def _row(seed: int, h: int, scale: float, refused: str | None = None) -> dict:
    return {
        "seed": seed,
        "households": h,
        "refused": refused,
        "stages": {
            "field": {"ops": {"pt_test@a": int(100 * scale), "placed@Standing.record": 5}, "placed": 10, "seconds": 0.1, "calls": 1000},
            "homesteads": {"ops": {"candidate@_fits": int(50 * scale * scale)}, "placed": h, "seconds": 0.2, "calls": 2000},
        },
    }


def test_total_leaves_out_outcomes_and_exponent_fits_the_slope() -> None:
    assert wb.total({"dist@a": 3, "candidate@b": 4, "placed@c": 9, "dropped@d": 1, "moved@e": 2}) == 7
    assert wb.exponent([(20, 100.0), (40, 400.0), (80, 1600.0)]) == pytest.approx(2.0)
    assert wb.exponent([(20, 100.0)]) is None and wb.exponent([(20, 0.0), (40, 0.0)]) is None
    assert wb.exponent([(40, 100.0), (40, 400.0)]) is None, "one size twice: no slope"


def test_summarize_averages_the_seeds_and_reads_the_budget() -> None:
    rows = [_row(s, h, h / 20) for s in (4, 25) for h in (20, 40, 80)]
    table = {"program": {"ops_at_40": 1000}, "stages": {"homesteads": {"status": "accepted", "per_thing": 10}}}
    out = wb.summarize(rows, table)
    hs = out["stages"]["homesteads"]
    assert hs["per"][40]["ops"] == 200 and hs["exponent"] == pytest.approx(2.0) and hs["status"] == "accepted"
    assert hs["budget_at_40"] == 400 and hs["ratio"] == pytest.approx(0.5)
    assert out["stages"]["field"]["status"] == "unbudgeted" and out["stages"]["field"]["ratio"] is None
    roll = out["stages"]["roll"]
    assert roll["per"][40]["ops"] == 400 and roll["budget_at_40"] == 1000 and roll["status"] == "budgeted"
    assert wb.summarize(rows, {"program": {}, "stages": {}})["stages"]["roll"]["status"] == "unbudgeted"


def test_a_stage_missing_at_a_size_is_left_out_of_it() -> None:
    rows = [_row(4, 20, 1.0), {**_row(4, 40, 2.0), "stages": {"field": _row(4, 40, 2.0)["stages"]["field"]}}]
    out = wb.summarize(rows, {})
    assert 40 not in out["stages"]["homesteads"]["per"] and 40 in out["stages"]["field"]["per"]


def test_the_record_lists_every_stage_and_the_roll(tmp_path: Path) -> None:
    rows = [_row(s, h, h / 20) for s in (4,) for h in (10, 20, 40, 80)]
    table = {"program": {"ops_at_40": 1000}, "stages": {"homesteads": {"per_thing": 10}}}
    md = wb.table_md(wb.summarize(rows, table), {"utc": "T", "commit": "abc", "code_id": "k", "seeds": [4], "refused": ["seed 9 at 80: X"]})
    assert "| homesteads |" in md and "| **the whole roll** |" in md and "ops @80" in md and "Refused rolls" in md
    assert "0.5x" in md and "unbudgeted" in md
    lone = wb.table_md(wb.summarize([_row(4, 20, 1.0)], {}), {"utc": "T", "commit": "a", "code_id": "k", "seeds": [4]})
    assert "| field | 100 |" in lone and "Refused" not in lone


def test_budgets_absent_reads_empty(tmp_path: Path) -> None:
    assert wb.budgets(str(tmp_path / "none.json")) == {"program": {}, "stages": {}}
    (tmp_path / "b.json").write_text(json.dumps({"program": {"ops_at_40": 5}, "stages": {}}))
    assert wb.budgets(str(tmp_path / "b.json"))["program"]["ops_at_40"] == 5


def test_run_writes_the_run_and_the_record(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(wb, "RUN_DIR", str(tmp_path / "runs"))
    monkeypatch.setattr(wb, "RECORD", str(tmp_path / "work-budget.md"))
    monkeypatch.setattr(wb, "BUDGETS", str(tmp_path / "none.json"))
    monkeypatch.setattr(wb, "_code_id", lambda: "key123")
    monkeypatch.setattr(wb, "_commit", lambda: "abc")
    calls = {4: {"field": 11, "homesteads": 22}}
    monkeypatch.setattr(wb, "roll", lambda seed, h: _row(seed, h, h / 20, refused="ValueError: no" if h == 80 else None))
    summary, path, record = wb.run((4,), (20, 40, 80), calls=lambda seeds, h: calls)
    saved = json.loads(Path(path).read_text())
    assert path.endswith("-key123.json") and saved["meta"]["refused"] == ["seed 4 at 80: ValueError: no"]
    assert saved["rows"][0]["stages"]["field"]["calls"] == 11 and 80 not in summary["sizes"]
    assert "| field |" in Path(record).read_text()
    monkeypatch.setattr(wb, "run", lambda seeds, sizes: (summary, path, record))
    assert wb.main(["--seed", "4", "--sizes", "20,40"]) == 0
    assert "wrote" in capsys.readouterr().out
    assert wb.main([]) == 0


def test_one_roll_counts_each_stage_and_what_it_placed(monkeypatch: pytest.MonkeyPatch) -> None:
    """`roll` on stand-in stages: each stage's counts and things placed taken across it, a refusal keeping the stages before it."""
    import contextlib
    import types

    from l7r.diagram import work_counts
    from l7r.diagram.hamletgen import driver
    from l7r.diagram.settlement._geom.primitives import point_in_poly

    ring = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]

    def stage_field(s, plan):  # type: ignore[no-untyped-def]
        point_in_poly(5.0, 5.0, ring)
        s.M["houses"].append({"x": 1})

    def stage_web(s, plan):  # type: ignore[no-untyped-def]
        raise ValueError("the web refused")

    def stage_after(s, plan):  # type: ignore[no-untyped-def]
        raise AssertionError("not reached")

    class S:
        def __init__(self, **_kw):  # type: ignore[no-untyped-def]
            self.M = {"houses": []}
            self.standing = types.SimpleNamespace(resync=lambda: None)

    monkeypatch.setattr(driver, "STAGES", (stage_field, stage_web, stage_after))
    monkeypatch.setattr(driver, "roll_scope", lambda spec=None: contextlib.nullcontext())
    import l7r.diagram.hamletgen as hg
    import l7r.diagram.settlement as st

    monkeypatch.setattr(hg, "plan_site", lambda spec: types.SimpleNamespace(W=10, H=10, spec=types.SimpleNamespace(seed=spec.seed)))
    monkeypatch.setattr(st, "Settlement", S)
    work_counts.reset()
    r = wb.roll(25, 10)
    assert r["refused"] == "ValueError: the web refused" and list(r["stages"]) == ["field", "web"]
    assert r["stages"]["field"]["ops"] == {"pt_test@point_in_poly": 1} and r["stages"]["field"]["placed"] == 1
    assert r["stages"]["web"]["ops"] == {} and r["stages"]["web"]["placed"] == 0


def test_the_engine_key_and_commit_name_the_tree() -> None:
    assert len(wb._code_id()) == 12 and wb._commit()


def _accepted(per_thing: float = 10, at40: float = 1500, at80: float = 3500) -> dict:
    return {"stages": {"web": {"status": "accepted", "per_thing": per_thing, "accepted": {"40": at40, "80": at80}}, "track": {"status": "unbudgeted"}}}


def _run_file(run_dir: Path, code_id: str, ops40: float, ops80: float, placed: float = 200, stamp: str = "20261028T000000Z") -> None:
    per = {"40": {"ops": ops40, "placed": placed}, "80": {"ops": ops80, "placed": placed * 2}}
    run_dir.mkdir(exist_ok=True)
    (run_dir / f"{stamp}-{code_id}.json").write_text(json.dumps({"summary": {"stages": {"web": {"per": per}}}}))


def test_the_ratchet_holds_an_accepted_stage_to_its_figure_and_its_budget(tmp_path: Path) -> None:
    """Feature 443 T04 (FR-006, SC-003): over the accepted figure refuses, over the budget refuses, under both passes, and the
    refusal names the stage, the figures and `make budget-change`."""
    runs = tmp_path / "runs"
    _run_file(runs, "abc", 1400, 3400)
    rc, msg = wb.review("GATED", _accepted(), "abc", str(runs))
    assert rc == 0 and "within its figures" in msg
    _run_file(runs, "abc", 1600, 3400, stamp="20261028T010000Z")  # the newest run at the code id is the one read
    rc, msg = wb.review("GATED", _accepted(), "abc", str(runs))
    assert rc == 1 and "web: 1,600 counted operations at 40 households, over its accepted 1,500" in msg and "make budget-change PHASE=" in msg
    rc, msg = wb.review("GATED-LOCAL", _accepted(per_thing=7), "abc", str(runs))  # budget 7 x 200 = 1,400 at 40
    assert rc == 1 and "over its budget 1,400 (7 per thing x 200)" in msg
    assert wb.held(_accepted(), {"stages": {"web": {"per": {"40": {"ops": 1, "placed": 1}}}}}) == ["web: the run has no roll at 80 households to hold it to"]


def test_the_ratchet_holds_nothing_unaccepted_or_off_the_engine_and_refuses_a_missing_run(tmp_path: Path) -> None:
    assert wb.review("GATED", {"stages": {"web": {"status": "budgeted"}}}, "abc", str(tmp_path)) == (0, "work-budget-review: no stage is accepted - nothing to hold")
    assert wb.review("DIRECT", _accepted(), "abc", str(tmp_path))[0] == 0, "a push with no engine code holds nothing"
    rc, msg = wb.review("GATED", _accepted(), "abc", str(tmp_path / "none"))
    assert rc == 1 and "no work-budget run at the pushed engine (code id abc): run `make work-budget`" in msg
    _run_file(tmp_path, "other", 1, 1)
    assert wb.review("GATED", _accepted(), "abc", str(tmp_path))[0] == 1, "a run at another engine is not this one's"


def test_the_review_flag_prints_the_verdict(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(wb, "review", lambda route: (1, f"refused on {route}"))
    assert wb.main(["--review", "GATED"]) == 1 and "refused on GATED" in capsys.readouterr().out


def test_the_review_reads_the_table_and_the_engine_key_by_default(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(wb, "budgets", _accepted)
    monkeypatch.setattr(wb, "_code_id", lambda: "k")
    _run_file(tmp_path, "k", 1, 1)
    assert wb.review("GATED", run_dir=str(tmp_path))[0] == 0
