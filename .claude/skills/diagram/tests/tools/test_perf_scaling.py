"""The perf bookend's scaling leg (feature 304, plan D1-D4): the reference spec timed at 10, 20 and 40 households beside the
15-household reference, each size banded against its own history, and the hamlet band lifted for the measuring tool alone.

WHY (the GM, 2026-10-01, before the village tier: "I want to make sure there's no more low hanging fruit"). Every performance
guard timed only 15 households, while the homesteads stage grew 17-24x for 4x the households and 139x on seed 47
(specs/304-homesteads-at-scale/research.md R1): a change harmless at 15 and ruinous at 40 landed green."""

from __future__ import annotations

import pathlib
from typing import Any

import pytest

from l7r.diagram.hamletgen import HamletSpec
from l7r.diagram.hamletgen.plan import beyond_the_band
from l7r.diagram.tools import perf_bands as pb
from l7r.diagram.tools import perf_snapshot as ps

SKILL = pathlib.Path(ps.SKILL)


# ---- D2: the band is lifted by the measuring tool alone (FR-003) ------------------------------------


def test_a_spec_past_the_hamlet_band_is_refused_outside_the_measuring_tool_and_admitted_inside_it() -> None:
    with pytest.raises(ValueError, match="outside the hamlet band"):
        HamletSpec("Probe", seed=4, households=40)
    with beyond_the_band():
        assert HamletSpec("Probe", seed=4, households=40).households == 40
    with pytest.raises(ValueError, match="outside the hamlet band"):
        HamletSpec("Probe", seed=4, households=40)


def test_no_pool_generator_lifts_the_band() -> None:
    """A GM-written hamlet is held to the band; only `perf_snapshot.measure` may step past it."""
    named = [p for p in (SKILL / "pool").rglob("*.py") if "beyond_the_band" in p.read_text(encoding="utf-8")]
    assert named == []


# ---- D1: the snapshot measures sizes ----------------------------------------------------------------


def _stand_in_stages(monkeypatch: pytest.MonkeyPatch, raise_at: int | None = None) -> None:
    """Stages that do nothing (feature 214's stand-ins), one of which refuses when the plan asks `raise_at` households."""
    from l7r.diagram.hamletgen import driver
    from l7r.diagram.hamletgen.ways.last_resort import WebRefused

    def stage_field(s: Any, plan: Any) -> None:  # noqa: ARG001
        return None

    def stage_web(s: Any, plan: Any) -> None:  # noqa: ARG001
        if plan.spec.households == raise_at:
            raise WebRefused("lanes 1 (skeleton) still break a rule of the lane law")

    monkeypatch.setattr(driver, "STAGES", (stage_field, stage_web))
    clock = iter(i * 0.05 for i in range(10_000))
    monkeypatch.setattr(ps.time, "time", lambda: next(clock))


def test_measure_rolls_the_size_it_is_asked_and_records_the_placer_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    _stand_in_stages(monkeypatch)
    rows = ps.measure((6,), households=40)
    assert len(rows) == 1
    row = rows[0]
    assert row["households"] == 40 and row["asked"] == 40 and row["seed"] == 6
    assert row["stages"] == {"field": 0.05, "web": 0.05}
    assert row["placer_calls"] == 0, "no seating ran, so the seat search's counter reads none"
    assert "refused" not in row


def test_measure_with_no_size_rolls_the_reference_as_before(monkeypatch: pytest.MonkeyPatch) -> None:
    _stand_in_stages(monkeypatch)
    row = ps.measure((6,))[0]
    assert row["asked"] == ps.REFERENCE["households"] and "households" not in row


def test_a_refused_roll_is_recorded_as_refused_never_swapped_out(monkeypatch: pytest.MonkeyPatch) -> None:
    """Spec Edge Cases: the four reference seeds are kept at every size; a refusal is that row's result."""
    _stand_in_stages(monkeypatch, raise_at=40)
    row = ps.measure((6,), households=40)[0]
    assert row["refused"].startswith("WebRefused: lanes 1") and "seconds" not in row and row["seed"] == 6


def test_the_reference_refusing_still_stops_the_bookend(monkeypatch: pytest.MonkeyPatch) -> None:
    """Only a scaling row records a refusal: the 15-household reference refusing is a defect the bookend stops on, as it always
    did (specs/297 research R8: `make perf` failing on main is how a refused seed 4 was found)."""
    from l7r.diagram.hamletgen.ways.last_resort import WebRefused

    _stand_in_stages(monkeypatch, raise_at=ps.REFERENCE["households"])
    with pytest.raises(WebRefused):
        ps.measure((6,))


def test_the_scaling_sizes_are_the_specs() -> None:
    """FR-001: 10, 20 and 40 beside the 15-household reference; 80 refuses in the field (research R5)."""
    assert ps.SCALING_SIZES == (10, 20, 40)


def test_record_writes_the_reference_rows_and_a_scaling_row_per_size_and_seed(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    import json

    monkeypatch.setattr(ps, "LOG_DIR", str(tmp_path))
    monkeypatch.setattr(ps, "_where", lambda: "diagram-performance")
    monkeypatch.setattr(ps, "_git", lambda *a: "abc1234")

    def fake(seeds: tuple[int, ...], households: int | None = None) -> list[dict[str, Any]]:
        extra = {} if households is None else {"households": households}
        return [{"seed": s, "seconds": float(households or 15), "stages": {"homesteads": 1.0}, "houses": households or 15, "asked": households or 15, "placer_calls": 9, **extra} for s in seeds]

    monkeypatch.setattr(ps, "measure", fake)
    path = ps.record("304-x", (4, 25))
    snap = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    assert [r["seed"] for r in snap["rows"]] == [4, 25] and snap["total_seconds"] == 30.0, "the reference rows exactly as before"
    assert sorted((r["households"], r["seed"]) for r in snap["scaling"]) == [(h, s) for h in (10, 20, 40) for s in (4, 25)]


# ---- D3, D4: each size banded against its own history (FR-002) ---------------------------------------


def _snap(label: str, ref: dict[int, float], scaling: dict[int, dict[int, float]] | None) -> dict[str, Any]:
    d: dict[str, Any] = {"label": label, "utc": "20261002T000000Z", "commit": "abc1234", "environment": "local"}
    d["rows"] = [{"seed": s, "seconds": v, "stages": {"homesteads": v / 2, "web": v / 2}} for s, v in ref.items()]
    if scaling is not None:
        d["scaling"] = [{"households": h, "seed": s, "seconds": v, "stages": {"homesteads": v / 2, "web": v / 2}} for h, by_seed in scaling.items() for s, v in by_seed.items()]
    return d


REF = {4: 3.0, 25: 3.0, 39: 3.0, 47: 3.0}
SIZES = {10: {4: 2.0, 25: 2.0, 39: 2.0, 47: 2.0}, 20: {4: 4.0, 25: 4.0, 39: 4.0, 47: 4.0}, 40: {4: 14.0, 25: 14.0, 39: 14.0, 47: 14.0}}


def test_a_fault_quadratic_in_the_households_raises_the_40_leg_while_the_reference_stays_quiet() -> None:
    """SC-001's seeded fault: a homesteads cost of 0.002 s x households^2 - 0.2 s at 10 households, 3.2 s at 40 - with the
    15-household reference left unchanged, as a fault confined to the larger seatings would leave it."""
    fault = {h: {s: v + 0.002 * h * h for s, v in by_seed.items()} for h, by_seed in SIZES.items()}
    v = pb.evaluate(_snap("s", REF, SIZES), _snap("e", REF, fault))
    assert v.legs[10] is not None and v.legs[40] is not None
    assert v.legs[40].band == 3 and v.legs[40].total_pct == 22.9
    assert v.legs[10].band == 2, "+10.0% a seed and in total: over band 2's total line, at band 2's seed line"
    assert v.total_pct == 0.0 and v.band == 3, "the reference is quiet; the band owed is the maximum over it and the legs"
    assert any(c.startswith("40 households: ") for c in v.crossed)


def test_the_reference_alone_is_judged_as_before_when_no_leg_moved() -> None:
    v = pb.evaluate(_snap("s", REF, SIZES), _snap("e", REF, SIZES))
    assert v.band == 0 and all(leg is not None and leg.band == 0 for leg in v.legs.values())
    assert v.measurements["total_pct"] == 0.0


def test_a_base_from_before_this_feature_has_no_baseline_for_the_legs_not_an_error() -> None:
    v = pb.evaluate(_snap("s", REF, None), _snap("e", REF, {40: {4: 99.0}}))
    assert v.legs == {40: None} and v.band == 0
    assert "40 households: no baseline" in pb.render(v)


def test_a_snapshot_with_no_legs_keeps_its_review_binding() -> None:
    """A review record is bound to `measurements` (perf_review.binding); a pair with no scaling legs on either side must bind
    to the same numbers it did before this feature, or every recorded review would be orphaned."""
    v = pb.evaluate(_snap("s", REF, None), _snap("e", REF, None))
    assert v.legs == {} and set(v.measurements) == {"total_pct", "seeds"}


def test_a_refused_row_is_left_out_of_the_sums_and_said() -> None:
    base = _snap("s", REF, SIZES)
    cur = _snap("e", REF, SIZES)
    for r in cur["scaling"]:
        if r["households"] == 40 and r["seed"] == 47:
            del r["seconds"]
            r["refused"] = "WebRefused: lanes 1"
    v = pb.evaluate(base, cur)
    assert v.legs[40] is not None and 47 not in v.legs[40].seeds and v.legs[40].band == 0
    assert "seed  47 refused (WebRefused: lanes 1)" in pb.render(v)


def test_the_report_prints_every_leg_under_the_reference(tmp_path: Any, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    import json

    monkeypatch.setattr(ps, "LOG_DIR", str(tmp_path))
    for utc, label in (("20261002T000000Z", "304-start"), ("20261002T010000Z", "304-end")):
        d = _snap(label, REF, SIZES)
        d.update(utc=utc, total_seconds=12.0, median_seconds=3.0, worst_seconds=3.0)
        (tmp_path / f"{utc}-{label}.json").write_text(json.dumps(d), encoding="utf-8")
    assert ps.report("304-start") == 0
    out = capsys.readouterr().out
    for h in (10, 20, 40):
        assert f"{h} households:" in out
