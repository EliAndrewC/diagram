"""`tools/rust_gate.py` (feature 444 amendment 5, FR-019 and FR-020; SC-012, SC-013): the seeds with no fixed block, the checks
asked by what they read, and the failing list - a failing seed added with its stage and frozen input, kept until both pass."""

from __future__ import annotations

import json
import pathlib
from typing import Any

import pytest

from l7r.diagram.hamletgen import rust_prefix as rp
from l7r.diagram.tools import rust_gate as rg


def _wf(s: object, plan: object) -> None:  # a stand-in water_frame: writes the plan's form into the meta, rolls no map
    s.M.setdefault("meta", {})["settlement_form"] = plan.settlement_form  # type: ignore[attr-defined]


_wf.__name__ = "stage_water_frame"


def test_the_seeds_are_a_fresh_block_and_the_pinned_variants_on_fresh_seeds() -> None:
    specs = rg.gate_specs(50000)
    assert len(specs) == rg.SEEDS + len(rg.PINNED_ROWS) and min(s for s, _n, _p in specs) == 50000, "no fixed seed"
    assert [p for _s, _n, p in specs[rg.SEEDS :]] == [dict(p) for p in rg.PINNED_ROWS]
    assert all(10 <= n <= 20 for _s, n, _p in specs)


def test_a_check_is_asked_where_all_it_reads_is_rust_owned_or_held_by_the_fresh_map(monkeypatch: pytest.MonkeyPatch) -> None:
    """The plan review of T21 (D2a, D2b): a check reading an input the fresh settlement holds beside the Rust output is asked; a
    Rust-owned part judged even where it came out empty; a check reading a part only a later stage writes is not asked."""
    checks = (
        ("ours", lambda M: [1] if M.get("meta").get("fall") is not None and M.get("canvas") else []),
        ("empty", lambda M: [] if M.get("plots") else ["no plot"]),
        ("theirs", lambda M: [1] if M.get("lanes") is None else []),
    )
    monkeypatch.setattr(rg, "POST_CHECKS", checks)
    lines = rg.judge({"canvas": [1], "meta": {}}, {"canvas": [1], "meta": {"fall": 90}}, owned={"meta.fall", "plots"})
    assert [line for line, _reads in lines] == ["FAIL ours -> 1, e.g. [1]", "FAIL empty -> 1, e.g. ['no plot']"], "theirs reads lanes: a later stage's"


def test_the_real_rust_stage_passes_a_seed() -> None:
    r = rg.roll(10000, 12, {}, [_wf])
    owned = [set().union(*(w for _n, _f, w in r["trace"]))]
    assert rg.verdict(r, owned) == ([], None, None)


def _stage(_s: object, _plan: object) -> None:  # a Rust stage that does nothing, named as a stage is
    pass


_stage.__name__ = "stage_water_frame"


def _wire(monkeypatch: pytest.MonkeyPatch, fails: dict[int, list[str]], replays: dict[str, list[str]]) -> None:
    def roll(seed: int, _n: int, _pins: dict[str, str], _stages: Any) -> dict[str, Any]:
        lines = fails.get(seed, [])
        return {"lines": lines, "stage": "water_frame" if lines else None, "frozen": b"state" if lines else None, "trace": [], "before": {}, "manifest": {}}

    monkeypatch.setattr(rg, "roll", roll)
    monkeypatch.setattr(rg, "replay", lambda path, _stage, _stages, _owned: replays.get(path, []))
    monkeypatch.setattr(rg, "gate_specs", lambda start: [(start, 12, {}), (start + 1, 13, {})])


def test_a_failing_seed_joins_the_list_with_its_frozen_input_and_leaves_only_when_both_pass(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    failing, frozen = str(tmp_path / "failing.json"), str(tmp_path / "frozen")
    _wire(monkeypatch, {101: ["FAIL refused:SiteRefused -> x"]}, {})
    rec = rg.run(100, stages=[_stage], failing_path=failing, frozen_dir=frozen)
    assert rec["failing"] == 1
    listed = json.loads(pathlib.Path(failing).read_text())
    assert [(e["seed"], e["stage"]) for e in listed] == [(101, "water_frame")] and pathlib.Path(listed[0]["frozen"]).read_bytes() == b"state"
    fixture = listed[0]["frozen"]
    # the next run: a new fresh block (200), the listed seed rolled again - and now passing, while its fixture still fails
    _wire(monkeypatch, {}, {fixture: ["FAIL lane_knots -> 1"]})
    rec = rg.run(200, stages=[_stage], failing_path=failing, frozen_dir=frozen)
    assert {r["seed"] for r in rec["seeds"]} == {200, 201, 101}, "the listed seed is rolled beside the fresh block"
    assert rec["failing"] == 1 and json.loads(pathlib.Path(failing).read_text())[0]["seed_passes"] is True, "kept: its fixture fails"
    # both pass: the entry and its fixture leave
    _wire(monkeypatch, {}, {})
    rec = rg.run(300, stages=[_stage], failing_path=failing, frozen_dir=frozen)
    assert rec["failing"] == 0 and json.loads(pathlib.Path(failing).read_text()) == [] and not pathlib.Path(fixture).exists()


def test_a_fixture_that_no_longer_loads_is_a_failure_never_dropped(tmp_path: pathlib.Path) -> None:
    bad = tmp_path / "x.pkl"
    bad.write_bytes(b"not a pickle")
    assert rg.replay(str(bad), "water_frame", [_wf], [set()])[0].startswith("FAIL frozen_input_unloadable")
    assert rg.load_failing(str(tmp_path / "absent.json")) == []


def test_main_refuses_a_rust_stage_off_the_front_and_records_a_run(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(rg, "off_the_front", lambda *_a: ["field"])
    assert rg.main(["--start", "1"]) == 1 and "not the front of STAGES" in capsys.readouterr().err
    monkeypatch.setattr(rg, "off_the_front", lambda *_a: [])
    monkeypatch.setattr(
        rg, "run", lambda start: {"rust_stages": ["water_frame"], "start": start, "seeds": [{"seed": 7, "stage": "water_frame", "failures": ["FAIL x -> 1"]}], "replays": [], "failing": 1}
    )
    monkeypatch.setattr(rg, "write_record", lambda record: str(tmp_path / "r.json"))
    assert rg.main(["--start", "1"]) == 1
    out = capsys.readouterr().out
    assert "seed 7 (water_frame): FAIL x -> 1" in out and "1 failing" in out


def test_write_record_names_the_engine(tmp_path: pathlib.Path) -> None:
    path = rg.write_record({"failing": 0}, log=str(tmp_path))
    assert json.loads(pathlib.Path(path).read_text())["engine"]


def test_each_way_a_seed_fails_and_a_replay_that_loads(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A plan that cannot be rolled fails the first Rust stage; a stage that raises fails by its name and leaves its input; a
    check that fails is the stage's that last wrote what it read, frozen as that stage started; a frozen input replays."""
    import pickle  # noqa: PLC0415

    def boom(_s: object, _plan: object) -> None:
        raise ValueError("no seat")

    boom.__name__ = "stage_boom"
    wf = _wf
    lines, stage, frozen = rg.verdict(rg.roll(10000, 12, {}, [wf, boom]), [set(), set()])
    assert lines[0].startswith("FAIL refused:ValueError") and stage == "boom" and frozen is not None
    path = tmp_path / "f.pkl"
    path.write_bytes(frozen)
    assert rg.replay(str(path), "boom", [wf, boom], [set(), set()])[0].startswith("FAIL refused:ValueError"), "replayed from boom on"
    s, plan = pickle.loads(frozen)  # noqa: S301 - the module's own fixture
    path.write_bytes(pickle.dumps((s, plan)))
    assert rg.replay(str(path), "nowhere", [wf], [set()]) == [], "a stage it does not name: every Rust stage, passing"
    r = rg.roll(10000, 12, {}, [wf])
    monkeypatch.setattr(rg, "judge", lambda _b, _m, _o: [("FAIL lane_knots -> 1", {"meta.settlement_form"})])
    lines, stage, frozen = rg.verdict(r, [set()])
    assert lines == ["FAIL lane_knots -> 1"] and stage == "water_frame" and frozen == r["trace"][0][1]
    monkeypatch.setattr(rg.hg, "plan_site", lambda _spec: (_ for _ in ()).throw(RuntimeError("no fall")))
    lines, stage, frozen = rg.verdict(rg.roll(10000, 12, {"row_line": "edge"}, [wf]), [set()])
    assert lines[0].startswith("FAIL refused:RuntimeError") and stage == "water_frame" and frozen is None


def test_a_stage_that_ends_failing_is_charged_though_a_later_stage_rewrites_the_part(monkeypatch: pytest.MonkeyPatch) -> None:
    """The plan review of T21, round 2 (D1b): the checks are judged where EACH Rust stage completes. Stage A ends with a part a
    check refuses, stage B rewrites it: judged once at the end the gate would never see A's failure; it charges A, with A's input."""

    def a(s: Any, _plan: Any) -> None:
        s.M["meta"]["mark"] = "bad"

    def b(s: Any, _plan: Any) -> None:
        s.M["meta"]["mark"] = "good"

    a.__name__, b.__name__ = "stage_a", "stage_b"
    monkeypatch.setattr(rg, "POST_CHECKS", (("mark_good", lambda M: ["bad mark"] if M.get("meta").get("mark") == "bad" else []),))
    wf = _wf
    r = rg.roll(10000, 12, {}, [wf, a, b])
    owned = [set().union(*(w for _n, _f, w in r["trace"][: i + 1])) for i in range(3)]
    lines, stage, frozen = rg.verdict(r, owned)
    assert lines == ["FAIL mark_good -> 1, e.g. ['bad mark']"] and stage == "a" and frozen == r["trace"][1][1]


def test_a_check_reaches_the_plan_only_through_the_recorded_meta() -> None:
    """The plan review of T21, round 3 (D2's condition): a check is handed the map alone, and the plan reaches the map only as
    its `meta` - whose reads are recorded - so no check reads the plan unseen and goes unasked."""
    import inspect  # noqa: PLC0415

    assert all(len(inspect.signature(check).parameters) == 1 for _name, check in rg.POST_CHECKS), "each check takes the map alone"
    r = rg.roll(10000, 12, {}, [_wf])
    seen: set[str] = set()
    rp.Reads(r["manifest"], seen)["meta"].get("settlement_form")
    assert "meta.settlement_form" in seen, "the plan's fields reach a check as meta reads, recorded"
