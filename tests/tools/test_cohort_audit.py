"""The cohort harness (`tools/cohort_audit.py`).

Feature 174, under the GM's 2026-09-02 ruling; the module had never been measured. Three properties
here were each learned by paying for them, and they are what these tests pin:

- the reference settlement is a GATE, not a suggestion (GM 2026-08-24). A cohort is 20-25 minutes and
  the reference map is 60 seconds; feature 126 ran SIX cohorts in one sitting, most of them launched
  when the failures were already known. `make maps` already gated on this and it did not help,
  because this module has its own entry point - a guard on one door is not a guard.
- the scope lock comes FIRST, before even that, and no flag walks around it.
- the audit rolls through `generate`, not `build` - "a harness that exercises a different code path
  than production reports on a map nobody will ever see".

The generator is stubbed throughout: what is under test is the harness, and rolling real hamlets to
check a report's arithmetic would cost minutes per assertion.
"""

from __future__ import annotations

import concurrent.futures
import sys
from pathlib import Path
from typing import Any

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.tools import cohort_audit as ca

pytestmark = pytest.mark.tooling


def _report(failures: list[str], lines: list[str] | None = None) -> Any:
    plan = type("P", (), {"down_deg": 90.0, "water_sink": "pond", "cluster_shape": "crescent", "lane_skeleton": "spine"})()
    return type("R", (), {"failures": failures, "fail_lines": lines if lines is not None else [f"{f}: it failed" for f in failures], "plan": plan})()


@pytest.fixture(autouse=True)
def _record_dir(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    """Every audit writes its per-seed record (feature 375 amendment 7): here, never into the repository's dev/cohort-log/."""
    monkeypatch.setattr(ca, "LOG_DIR", str(tmp_path / "cohort-log"))


def _patch_roll(monkeypatch: pytest.MonkeyPatch, fn: Any, how: str = "rolled") -> None:
    """Stand in for one seed's roll: `fn(spec)` gives the verdict, `how` whether the roll cache served it."""
    monkeypatch.setattr(ca, "roll_how", lambda spec: (fn(spec), how))


@pytest.fixture
def _clean(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(hg, "generate", lambda spec, out_base, render: _report([]))


def test_a_FAILING_reference_settlement_stops_the_cohort_and_says_what_to_do(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """The 60-second question that gates the 25-minute answer. The message hands over the next
    command, and names the override rather than hiding it."""
    monkeypatch.setattr(hg, "generate", lambda spec, out_base, render: _report(["village_windbreak_is_continuous[2]"]))
    started: list[int] = []
    monkeypatch.setattr(ca, "audit", lambda *a, **k: started.append(1) or 0)

    assert ca.main(["--count", "48"]) == 2
    out = capsys.readouterr().out
    assert "REFERENCE SETTLEMENT IS FAILING" in out
    assert "Then: make cohort" in out and "--anyway overrides" in out
    assert started == [], "25 minutes not spent"


def test_ANYWAY_skips_the_reference_gate_because_a_rule_with_no_escape_gets_worked_around(monkeypatch: pytest.MonkeyPatch) -> None:
    """ "deliberately awkward to type" - but it exists, and it must actually reach the cohort."""
    rolled: list[Any] = []
    monkeypatch.setattr(hg, "generate", lambda spec, out_base, render: rolled.append(spec) or _report(["anything"]))
    monkeypatch.setattr(ca, "audit", lambda *a, **k: 0)
    assert ca.main(["--count", "2", "--anyway"]) == 0
    assert rolled == [], "the reference map was not even rolled"


def test_a_clean_reference_runs_the_cohort_and_passes_its_arguments_through(_clean, monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, Any] = {}
    monkeypatch.setattr(
        ca,
        "audit",
        lambda count, seed, only, jobs, households, fresh, fresh_from, *modes: (
            seen.update(count=count, seed=seed, only=only, jobs=jobs, households=households, fresh=fresh, fresh_from=fresh_from, modes=modes) or 0
        ),
    )
    assert ca.main(["--count", "6", "--seed", "9", "--only", "wells", "--jobs", "2", "--households", "40", "--fresh", "4", "--fresh-from", "12345"]) == 0
    assert seen == {"count": 6, "seed": 9, "only": "wells", "jobs": 2, "households": 40, "fresh": 4, "fresh_from": 12345, "modes": (False, False, False, None)}


def test_roll_one_goes_through_GENERATE_which_is_the_path_that_ships(monkeypatch: pytest.MonkeyPatch) -> None:
    """It called `build` directly, which skips everything `generate` does around the stages - so a
    fix living in `generate` was invisible to the cohort, measured on seed 5. The header carries the
    plan's own rolled knobs, which is what makes a failing line reproducible."""
    seen: dict[str, Any] = {}

    def roll(spec: Any) -> Any:
        seen.update(name=spec.name, seed=spec.seed)
        return "plan", {}, _report(["a_check[1]"])

    from l7r.diagram.pipeline import rollcache

    # rollcache._roll_payload IS generate(spec, out_base=None, render=False), the gate's roll; the cohort's obtain produces it
    monkeypatch.setattr(rollcache, "_roll_payload", roll)
    monkeypatch.setattr(rollcache, "obtain", lambda subject, produce, recorded=None: (produce(), "MISS"))
    header, failures, lines = ca.roll_one((7, 13))
    assert seen["seed"] == 7
    assert "seed=7 households=13" in header and "sink=pond" in header and "shape=crescent" in header
    assert failures == ["a_check[1]"] and lines


def test_audit_tallies_the_residue_by_CHECK_and_its_rc_is_the_verdict(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """The report's whole value is the residue table: which check is failing, how often, across the
    cohort. The seed index is stripped so the same check on four maps tallies as four, not one each."""
    answers = {1: [], 2: ["wells_are_shared[3]"], 3: ["wells_are_shared[9]"], 4: ["lanes_reach_something[1]"]}
    # every row knob value rolled somewhere, so the "never rolled" line adds no failure of its own
    _patch_roll(
        monkeypatch,
        lambda spec: (
            f"--- seed {spec[0]} row={('street/one/own', 'edge/both/shared')[spec[0] % 2]} water={('channel', 'well')[spec[0] % 2]}",
            answers.get(spec[0], []),
            [f"{f} detail" for f in answers.get(spec[0], [])],
        ),
    )
    assert ca.audit(4, 1, jobs=1) == 1
    out = capsys.readouterr().out
    assert f"{1 + len(ca.PINNED_ROWS)}/{4 + len(ca.PINNED_ROWS)} passed the whole gate" in out
    assert "2  wells_are_shared" in out and "1  lanes_reach_something" in out

    _patch_roll(monkeypatch, lambda spec: (f"--- seed {spec[0]} row={('street/one/own', 'edge/both/shared')[spec[0] % 2]} water={('channel', 'well')[spec[0] % 2]}", [], []))
    assert ca.audit(2, 1, jobs=1) == 0
    assert f"{2 + len(ca.PINNED_ROWS)}/{2 + len(ca.PINNED_ROWS)} passed" in capsys.readouterr().out

    seen: list[tuple] = []
    _patch_roll(monkeypatch, lambda spec: seen.append(spec) or (f"--- seed {spec[0]} row={('street/one/own', 'edge/both/shared')[spec[0] % 2]} water={('channel', 'well')[spec[0] % 2]}", [], []))
    ca.audit(2, 39, jobs=1, households=40)
    assert seen == [(39, 40), (40, 40)], "feature 328: every seed at the size asked, the pinned rows left out"


def test_only_narrows_both_the_tally_and_the_printed_lines(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """`--only` is for chasing one check across the cohort; a map whose only failures are other
    checks must drop out of the count entirely, not appear with an empty body."""
    _patch_roll(monkeypatch, lambda spec: ("--- h", ["wells_are_shared[1]", "lanes_reach_something[2]"], ["wells_are_shared detail", "lanes_reach_something detail"]))
    assert ca.audit(1, 1, only="wells", jobs=1) == 1
    out = capsys.readouterr().out
    assert "wells_are_shared detail" in out and "lanes_reach_something detail" not in out

    _patch_roll(monkeypatch, lambda spec: ("--- h", ["lanes_reach_something[2]"], ["lanes detail"]))
    assert ca.audit(1, 1, only="wells", jobs=1) == 0, "no map failed the check being chased"


def test_the_rolls_FAN_OUT_across_processes_and_the_report_stays_in_seed_order(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """ "a map is a pure function of its spec, so parallelism can only change the wall clock, never a
    verdict" - and results are collected in seed order so the report reads identically to a serial
    one. A pool that returned out of order would make two runs of the same cohort disagree on paper."""

    class _Pool:
        def __init__(self, max_workers: int) -> None:
            seen["jobs"] = max_workers

        def __enter__(self) -> _Pool:
            return self

        def __exit__(self, *_a: Any) -> None:
            return None

        def map(self, fn: Any, specs: Any) -> Any:
            return [fn(s) for s in specs]

    seen: dict[str, Any] = {}
    monkeypatch.setattr(concurrent.futures, "ProcessPoolExecutor", _Pool)
    _patch_roll(monkeypatch, lambda spec: (f"--- seed {spec[0]}", ["c[1]"], [f"seed {spec[0]} detail"]))
    assert ca.audit(3, 5, jobs=3) == 1
    out = capsys.readouterr().out
    assert seen["jobs"] == 3
    assert out.index("seed 5 detail") < out.index("seed 6 detail") < out.index("seed 7 detail")


def test_the_skill_root_is_put_on_sys_path_when_it_is_not_already_there(monkeypatch: pytest.MonkeyPatch) -> None:
    import importlib

    monkeypatch.setattr(sys, "path", [p for p in sys.path if Path(p).resolve() != Path(ca.HERE).resolve()])
    reloaded = importlib.reload(ca)
    assert Path(reloaded.HERE).resolve() in [Path(p).resolve() for p in sys.path]


def test_roll_one_reports_a_scatter_frame_breach_the_manifest_records(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 224 FR-002: a rolled map whose view reached past the scatter's predicted frame carries
    `meta.scatter_frame_breach`, and the cohort reports it as a failure so the pad is revisited."""
    rep = _report([])
    rep.manifest = {"meta": {"scatter_frame_breach": [-261.3, 5.6, -120.2, -307.7]}}
    monkeypatch.setattr(ca, "_report_of", lambda spec: (rep, "MISS"))
    _header, failures, lines = ca.roll_one((13, 13))
    assert failures == ["scatter_frame_breach"] and "5.6" in lines[-1]


def test_roll_one_reports_a_household_shortfall_the_manifest_records(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 226: a roll that seated fewer households than its spec declared is a cohort failure - the roll's own
    verdict counts stranded houses only, and a seed that seated 13 of 20 read as a pass."""
    rep = _report([])
    rep.manifest = {"meta": {"roll_placed": 13}}
    monkeypatch.setattr(ca, "_report_of", lambda spec: (rep, "MISS"))
    _header, failures, lines = ca.roll_one((25, 20))
    assert failures == ["households_seated"] and "13 of 20" in lines[-1]
    rep2 = _report([])
    rep2.manifest = {"meta": {"roll_placed": 20}}
    monkeypatch.setattr(ca, "_report_of", lambda spec: (rep2, "MISS"))
    assert ca.roll_one((25, 20))[1] == []


def test_roll_one_reports_farmstead_parts_across_the_brook_and_an_offwind_seat(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 261 SC-009: a garden standing across the brook from the house it names is a cohort failure; a map whose
    seat fell back off the wind says so in its header."""
    brook = {"poly": [[0.0, 50.0], [200.0, 50.0]]}
    rep = _report([])
    rep.manifest = {
        "meta": {"seat_offwind": True},
        "streams": [brook, {"poly": [[1.0, 1.0]]}],
        "gardens": [{"x": 10.0, "y": 80.0, "of": [10.0, 20.0]}, {"x": 30.0, "y": 25.0, "of": [10.0, 20.0]}],
        "persimmons": [{"x": 5.0, "y": 5.0}],
    }
    monkeypatch.setattr(ca, "_report_of", lambda spec: (rep, "MISS"))
    header, failures, lines = ca.roll_one((9, 12))
    assert failures == ["farmstead_across_brook"] and "1 farmstead part" in lines[-1] and header.endswith("seat=OFFWIND")
    assert ca.parts_across_brook({}) == 0


def test_the_audit_asks_the_placers_own_same_bank_predicate(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 417 T04 (D12): the cohort's "across the brook" is `crosses_a_stream`, the predicate the placers ask - one rule,
    one body - so the check and the placing cannot disagree."""
    asked: list[tuple] = []
    monkeypatch.setattr(ca, "crosses_a_stream", lambda house, part, streams: asked.append((tuple(house), part)) or True)
    assert ca.parts_across_brook({"streams": [], "gardens": [{"x": 1.0, "y": 2.0, "of": [3.0, 4.0]}]}) == 1
    assert asked == [((3.0, 4.0), (1.0, 2.0))]


def test_roll_one_reports_the_matrix_and_the_grove_rules(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 291: the cohort's verdict reads the overlap matrix and the grove predicates on every roll - the retired
    battery had been the only thing that saw 126's grove defects."""
    rep = _report([])
    rep.manifest = {"meta": {}}
    monkeypatch.setattr(ca, "_report_of", lambda spec: (rep, "MISS"))
    monkeypatch.setattr(ca, "matrix_violations", lambda M: [("groves", "lanes", 1, 2)])
    monkeypatch.setattr(ca, "gardens_east_shaded", lambda M: [((0.0, 0.0), {})])
    _header, failures, lines = ca.roll_one((9, 12))
    assert failures == ["features_do_not_overlap", "gardens_east_shaded"], failures
    assert any("1 forbidden overlap" in ln for ln in lines)


@pytest.mark.parametrize(("form", "want"), [("linear", "row=street/both/shared"), ("dispersed", "water=channel")])
def test_roll_one_s_header_names_the_row_or_the_farm_water_knob(monkeypatch: pytest.MonkeyPatch, form: str, want: str) -> None:
    """Feature 291: a linear roll's header carries its row knobs, a dispersed roll's its farm water - what the "knob values
    never rolled" line reads."""

    def report_of(spec: Any) -> Any:
        r = _report([])
        for k, v in {"settlement_form": form, "grove_sides": 2, "row_line": "street", "row_sides": "both", "row_water": "shared", "farm_water": "channel"}.items():
            setattr(r.plan, k, v)
        return r, "MISS"

    monkeypatch.setattr(ca, "_report_of", report_of)
    header, _f, _l = ca.roll_one((7, 13))
    assert f"form={form}" in header and want in header


def test_a_refused_roll_is_reported_by_name_not_raised(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Feature 291 on 287: a roll that raises a refusal is that seed's verdict - its form and the refusal by name - and the
    audit goes on to the other seeds."""
    from l7r.diagram.tools import cohort_audit as ca

    class Refused(ValueError):
        pass

    def refuse(*a, **k):  # type: ignore[no-untyped-def]
        raise Refused("no margin seats all 12")

    monkeypatch.setattr(ca, "_report_of", refuse)
    header, failures, lines = ca.roll_one((901, 12, {"row_line": "street"}))
    assert header.startswith("Audit-901 households=12 form=linear") and header.endswith("REFUSED")
    assert failures == ["refused:Refused"] and lines == ["FAIL refused:Refused -> no margin seats all 12"]


def test_roll_one_reports_lane_ends_knotted_short_of_a_join(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 328 wave 93: the knot rule the pool's seed test holds (`ways.knots.lane_knots`, 0081: ends within 25 ft are
    joined at a single point) is a cohort failure too - without it a change that knotted three pool maps read 54/54."""
    rep = _report([])
    rep.manifest = {"lanes": [{"pts": [[0.0, 0.0], [100.0, 0.0]]}, {"pts": [[110.0, 10.0], [200.0, 10.0]]}]}  # two ends 14 ft apart
    monkeypatch.setattr(ca, "_report_of", lambda spec: (rep, "MISS"))
    _header, failures, lines = ca.roll_one((13, 13))
    assert "lane_knots" in failures and any("FAIL lane_knots" in ln for ln in lines)


# ---- feature 375 amendment 7, FR-029: the cohort through the roll cache, and its per-seed record --------------------------------


def test_a_served_roll_says_so_and_the_audit_writes_its_per_seed_record(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
    import json

    monkeypatch.setattr(ca, "_report_of", lambda spec: (_report(["wells_are_shared[1]"] if spec.seed == 2 else []), "HIT" if spec.seed == 1 else "MISS"))
    assert ca.roll_how((1, 12))[1] == "served" and ca.roll_how((2, 12))[1] == "rolled"

    def refuse(spec: Any) -> Any:
        raise ValueError("no seat")

    monkeypatch.setattr(ca, "_report_of", lambda spec: refuse(spec) if spec.seed == 3 else (_report([]), "HIT"))
    assert ca.roll_how((3, 12, {"row_line": "street"}))[1] == "rolled", "a crash is rolled, never served"
    stored = ca.Refusal("builtins", "ValueError", "no seat")
    monkeypatch.setattr(ca, "_report_of", lambda spec: (stored, "HIT"))
    (header, failures, _l), how = ca.roll_how((3, 12, {"row_line": "street"}))
    assert how == "served" and failures == ["refused:ValueError"] and header.endswith("REFUSED"), "a stored refusal, served, by name"
    rolled = [
        (("--- a form=linear", [], []), "served"),
        (("--- b", ["wells_are_shared[1]"], ["    FAIL lane_knots -> 4 knot(s), e.g. []".strip(), "x"]), "rolled"),
        (("--- c REFUSED", ["refused:ValueError"], ["y"]), "served"),
    ]
    path = ca.write_record([(1, 12), (2, 12), (3, 12, {"row_line": "street"})], rolled, 1, None)
    rec = json.loads(Path(path).read_text(encoding="utf-8"))
    assert path.startswith(str(tmp_path)) and rec["count"] == 3 and rec["served"] == 2 and rec["first_seed"] == 1
    assert [(s["seed"], s["how"], s["verdict"]) for s in rec["seeds"]] == [(1, "served", "pass"), (2, "rolled", "fail"), (3, "served", "refused")]
    assert rec["seeds"][0]["form"] == "linear" and rec["seeds"][1]["failures"] == ["wells_are_shared[1]"] and rec["seeds"][2]["pins"] == {"row_line": "street"}
    assert rec["seeds"][1]["counts"] == {"lane_knots": 4} and rec["seeds"][0]["counts"] == {}, "each failing rule's count (feature 385 T03)"


def test_the_fresh_block_is_rolled_beside_the_fixed_seeds_and_is_a_rate_never_the_verdict(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Any) -> None:
    """Feature 386 (the GM 2026-10-17: "a block of fresh seeds that rotates each run, recorded as a failure rate rather than a
    pass/fail"): the block rolls in the same run and record, each seed marked; its failures print as a rate and leave the pass count
    and the exit code to the fixed seeds and the pinned rows."""
    import json

    seen: list[tuple] = []
    _patch_roll(
        monkeypatch,
        lambda spec: (
            seen.append(spec)
            or (f"--- seed {spec[0]} row={('street/one/own', 'edge/both/shared')[spec[0] % 2]} water={('channel', 'well')[spec[0] % 2]}", ["lane_knots[1]"] if spec[0] == 20001 else [], [])
        ),
    )
    assert ca.audit(2, 1, jobs=1, fresh=3, fresh_from=20000) == 0, "a failing fresh seed never fails the cohort"
    out = capsys.readouterr().out
    assert f"{2 + len(ca.PINNED_ROWS)}/{2 + len(ca.PINNED_ROWS)} passed the whole gate" in out and "lane_knots" not in out.split("passed the whole gate")[0]
    assert "fresh block from seed 20000: 1 of 3 failed (33%) - seeds 20001; a rate, never a pass/fail" in out
    assert [s[0] for s in seen][-3:] == [20000, 20001, 20002]
    rec = json.loads(next((tmp_path / "cohort-log").glob("*.json")).read_text(encoding="utf-8"))
    assert [s["seed"] for s in rec["seeds"] if s.get("fresh")] == [20000, 20001, 20002] and (rec["fresh_first"], rec["fresh_count"]) == (20000, 3)
    assert not any(s.get("fresh") for s in rec["seeds"][:-3])
    seen.clear()
    ca.audit(1, 1, jobs=1, households=40, fresh=3, fresh_from=20000)
    assert seen == [(1, 40)], "a scaling roll rolls no fresh block, as it rolls no pinned row"
    assert ca.fresh_specs(3, None) == [] and ca.fresh_specs(0, 5) == []


def test_the_audit_writes_one_record_a_run(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
    _patch_roll(monkeypatch, lambda spec: (f"--- seed {spec[0]} row={('street/one/own', 'edge/both/shared')[spec[0] % 2]} water={('channel', 'well')[spec[0] % 2]}", [], []), how="served")
    ca.audit(2, 1, jobs=1)
    files = list((tmp_path / "cohort-log").glob("*.json"))
    assert len(files) == 1


def test_the_cohort_gets_its_roll_from_the_roll_cache_and_a_refusal_is_stored_by_name(monkeypatch: pytest.MonkeyPatch) -> None:
    from l7r.diagram.pipeline import rollcache

    seen: list[Any] = []
    monkeypatch.setattr(rollcache, "obtain", lambda subject, produce, recorded=None: seen.append(subject) or (("plan", "manifest", "rep"), "HIT"))
    spec = hg.HamletSpec(name="Audit-01", seed=1, households=12)
    assert ca._report_of(spec) == ("rep", "HIT") and seen == [f"cohort:{spec!r}"]
    monkeypatch.setattr(rollcache, "obtain", lambda subject, produce, recorded=None: (produce(), "MISS"))

    class WebRefused(ValueError):
        pass

    def refuse(spec: Any) -> Any:
        raise WebRefused("no lane reaches the well")

    monkeypatch.setattr(rollcache, "_roll_payload", refuse)
    payload, how = ca._report_of(spec)
    assert isinstance(payload, ca.Refusal) and payload.name == "WebRefused" and how == "MISS", "stored as a payload, by name"
    assert type(payload.exception()).__name__ == "WebRefused" and str(payload.exception()) == "no lane reaches the well"
    assert type(ca.Refusal("builtins", "ValueError", "x").exception()) is ValueError, "an importable class is itself"

    def crash(spec: Any) -> Any:
        raise MemoryError("out of memory")

    monkeypatch.setattr(rollcache, "_roll_payload", crash)
    with pytest.raises(MemoryError):
        ca._report_of(spec)


def test_a_refusal_crosses_a_real_roll_child_as_the_class_the_audit_knows() -> None:
    """The plan review (round 2): a `Refusal` unpickled from the child was not the class `cohort_audit` held when it ran as
    `__main__`. One class now lives in `cohort_roll`, and the child's payload is that class."""
    from l7r.diagram.pipeline import rollcache
    from l7r.diagram.tools import cohort_roll

    payload, _deps = rollcache._in_child("tests.tools._cohort_child:refuse", "seed 7")
    assert type(payload) is cohort_roll.Refusal and ca.Refusal is cohort_roll.Refusal
    assert (payload.module, payload.name) == ("tests.tools._cohort_child", "WebRefused") and "seed 7" in payload.message
    assert type(payload.exception()).__name__ == "WebRefused", "the parent re-imports the class by name"


def test_run_under_another_module_name_the_audit_shares_the_one_refusal_and_an_importable_target() -> None:
    """`make cohort` runs `python3 -m ...cohort_audit` (`__main__`) and fans out to a process pool (`__mp_main__`): in both
    the module's `Refusal` is `cohort_roll.Refusal` and its child target imports by name (the plan review measured
    `__mp_main__:_roll_or_refusal`, which no child can import). Run in a fresh interpreter as a pool worker runs it; as
    `__main__` the body is the same and only its guard differs."""
    import subprocess

    probe = (
        "import importlib, runpy;"
        f"g = runpy.run_module('l7r.diagram.tools.cohort_audit', run_name={'__mp_main__'!r});"
        "from l7r.diagram.tools import cohort_roll;"
        "mod, fn = g['ROLL_TARGET'].rsplit(':', 1);"
        "assert g['Refusal'] is cohort_roll.Refusal, 'one class';"
        "assert getattr(importlib.import_module(mod), fn) is cohort_roll.roll_or_refusal, 'an importable target';"
        "print('ok')"
    )
    p = subprocess.run([sys.executable, "-c", probe], cwd=str(Path(__file__).resolve().parents[2]), capture_output=True, text=True, check=False)
    assert p.returncode == 0 and p.stdout.startswith("ok"), p.stderr[-800:]


def test_make_cohorts_record_lands_in_the_clone_and_names_itself_for_the_commit(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
    """FR-029: with no test directory, the record goes under the clone's `dev/cohort-log/` and its path into the git dir's
    `last-cohort-record`, which `make cohort`'s `commit-run-record.sh` reads to commit that one file."""
    import subprocess

    repo = tmp_path / "clone"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    monkeypatch.setattr(ca, "HERE", str(repo))
    monkeypatch.setattr(ca, "LOG_DIR", None)
    path = ca.write_record([(1, 12)], [(("--- a form=nucleated", [], []), "rolled")], 1, None)
    assert path.startswith(str(repo / "dev" / "cohort-log"))
    assert (repo / ".git" / "last-cohort-record").read_text(encoding="utf-8") == path


def test_a_cohort_record_names_the_feature_it_was_rolled_for(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
    """Feature 375 amendment 8 (FR-038): `make cohort-seeds` counts the changes the records span by this field - the
    number of SPECIFY_FEATURE; empty where a session exported none."""
    import json

    monkeypatch.setenv("SPECIFY_FEATURE", "375-enforced-wave-process")
    path = ca.write_record([(1, 12)], [(("--- a form=nucleated", [], []), "rolled")], 1, None)
    assert json.loads(Path(path).read_text(encoding="utf-8"))["feature"] == "375"
    monkeypatch.delenv("SPECIFY_FEATURE")
    path = ca.write_record([(1, 12)], [(("--- a form=nucleated", [], []), "rolled")], 1, None)
    assert json.loads(Path(path).read_text(encoding="utf-8"))["feature"] == ""


def test_a_knob_value_rolled_three_times_and_never_drawn_fails_the_cohort() -> None:
    """The round arbiter's tooling fix (ask:w154-lane-wells): a clustered hamlet's well siting rolled three times or more and
    drawn on none is named; drawn once, or rolled fewer times, it passes."""
    from l7r.diagram.tools.cohort_audit import never_drawn

    dead = [f"--- Audit-0{i} form=nucleated wells=lane/cluster+pocket" for i in range(3)]
    assert never_drawn(dead) == ["well_siting=lane"]
    assert never_drawn([*dead, "--- Audit-09 form=nucleated wells=lane/lane+pocket"]) == [], "drawn once"
    assert never_drawn(dead[:2]) == [], "rolled only twice"
    assert never_drawn(["--- Audit-05 form=linear row=street/one/own"]) == []


def test_the_cohort_names_a_well_siting_rolled_and_never_drawn(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """A clustered hamlet's header carries its rolled well siting and the forms drawn; the audit fails a value rolled three
    times and drawn on none (the round arbiter's tooling fix on ask:w154-lane-wells)."""
    rep = _report([])
    rep.plan.settlement_form = "nucleated"
    rep.plan.well_siting = "lane"
    rep.manifest = {"meta": {}, "wells": [{"x": 1.0, "y": 1.0, "form": "pocket"}, {"x": 300.0, "y": 1.0, "form": "cluster"}, {"x": 600.0, "y": 1.0, "private": True}]}
    monkeypatch.setattr(ca, "_report_of", lambda spec: (rep, "MISS"))
    header, _failures, _lines = ca.roll_one((7, 16))
    assert header.endswith(" wells=lane/cluster+pocket")
    rows = "row=street/one/own water=channel", "row=edge/both/shared water=well"
    _patch_roll(monkeypatch, lambda spec: (f"--- seed {spec[0]} {rows[spec[0] % 2]} form=nucleated wells=lane/cluster+pocket", [], []), how="rolled")
    assert ca.audit(3, 1, jobs=1) == 1
    out = capsys.readouterr().out
    assert "knob values rolled but never drawn: well_siting=lane" in out and "knob_value_never_drawn" in out
