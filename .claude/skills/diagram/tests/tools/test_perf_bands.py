"""The GM's three-band matrix, pinned on both measurements, per environment (feature 129, T008)."""

from __future__ import annotations

from typing import Any

import pytest

from l7r.diagram.tools import perf_bands as pb


def snap(label: str, seconds: dict[int, float], environment: str | None = "local", stages: dict[int, dict[str, float]] | None = None) -> dict[str, Any]:
    rows = [{"seed": s, "seconds": v, "stages": (stages or {}).get(s, {"web": v * 0.8, "field": v * 0.2})} for s, v in seconds.items()]
    d: dict[str, Any] = {"label": label, "utc": "20260825T000000Z", "commit": "abc1234", "rows": rows}
    if environment is not None:
        d["environment"] = environment
    return d


def test_the_lines_are_the_GMs_numbers() -> None:
    assert (pb.BAND2_TOTAL_PCT, pb.BAND2_SEED_PCT, pb.BAND3_TOTAL_PCT, pb.BAND3_SEED_PCT) == (5.0, 10.0, 10.0, 20.0)


def test_faster_or_unchanged_owes_nothing() -> None:
    v = pb.evaluate(snap("s", {1: 100.0, 2: 100.0}), snap("e", {1: 99.0, 2: 100.0}))
    assert v.band == 0 and v.crossed == () and "nothing" in v.owes and v.total_pct == -0.5


def test_any_increase_on_a_seed_is_band_1_even_when_the_total_falls() -> None:
    v = pb.evaluate(snap("s", {1: 100.0, 2: 100.0}), snap("e", {1: 100.5, 2: 90.0}))
    assert v.band == 1 and v.seeds == {1: 0.5, 2: -10.0} and v.total_pct == -4.8
    assert "explanation" in v.owes and "perf-confirm" in v.owes


def test_band_2_on_the_total_and_on_a_seed() -> None:
    assert pb.evaluate(snap("s", {1: 100.0, 2: 100.0}), snap("e", {1: 106.0, 2: 105.0})).band == 2  # total +5.5
    v = pb.evaluate(snap("s", {1: 100.0, 2: 100.0}), snap("e", {1: 111.0, 2: 95.0}))  # total +3, seed +11
    assert v.band == 2 and v.crossed == ("seed 1 +11.0% > 10%",) and "perf-audit" in v.owes
    assert pb.evaluate(snap("s", {1: 100.0}), snap("e", {1: 105.0})).band == 1, "exactly 5% is not over the line"


def test_feature_128s_pair_is_band_3_despite_a_faster_total() -> None:
    """SC-002b: total -29.9%, seed 47 +30.7% - the case the per-seed numbers exist for."""
    base = snap("128-start", {4: 23.7, 25: 222.7, 39: 67.8, 47: 68.3})
    end = snap("128-end", {4: 26.8, 25: 80.6, 39: 71.5, 47: 89.3})
    v = pb.evaluate(base, end)
    assert v.total_pct == -29.9 and v.seeds[47] == 30.7 and v.band == 3
    assert "seed 47 +30.7% > 20%" in v.crossed and "seed 47 +30.7% > 10%" in v.crossed
    assert "GM" in v.owes and "perf-signoff" in v.owes
    assert v.measurements == {"total_pct": -29.9, "seeds": {"4": 13.1, "25": -63.8, "39": 5.5, "47": 30.7}}


def test_band_3_on_the_total() -> None:
    v = pb.evaluate(snap("s", {1: 100.0, 2: 100.0}), snap("e", {1: 112.0, 2: 109.0}))
    assert v.band == 3 and "total +10.5% > 10%" in v.crossed and "total +10.5% > 5%" in v.crossed


def test_cross_environment_is_REFUSED_not_displayed() -> None:
    with pytest.raises(pb.EnvironmentMismatch) as e:
        pb.evaluate(snap("s", {1: 100.0}, "local"), snap("e", {1: 50.0}, "codebuild"))
    assert "codebuild" in str(e.value) and "local" in str(e.value) and "FR-014" in str(e.value)


def test_a_snapshot_without_the_field_is_laptop_era_local() -> None:
    assert pb.environment_of({}) == "local"
    assert pb.environment_of({"host": "codebuild:BUILD_GENERAL1_XLARGE"}) == "codebuild", "the transitional shape from build a6e2afe6"
    assert pb.environment_of({"environment": "codebuild", "host": "laptop"}) == "codebuild", "the explicit field wins"
    v = pb.evaluate(snap("s", {1: 100.0}, None), snap("e", {1: 101.0}, "local"))
    assert v.environment == "local" and v.band == 1


def test_seeds_only_in_one_snapshot_are_ignored_and_a_zero_base_is_safe() -> None:
    v = pb.evaluate(snap("s", {1: 100.0, 9: 0.0}), snap("e", {1: 100.0, 2: 50.0, 9: 0.0}))
    assert set(v.seeds) == {1, 9} and v.seeds[9] == 0.0 and v.band == 0, "seed 2 has no base and is ignored; a zero base divides safely"


def test_render_names_the_measurement_the_stage_that_grew_and_what_is_owed() -> None:
    base = snap("s", {25: 80.0}, stages={25: {"web": 60.0, "field": 20.0}})
    end = snap("e", {25: 92.0}, stages={25: {"web": 71.0, "field": 21.0}})
    text = pb.render(pb.evaluate(base, end))
    assert text.splitlines()[0] == "perf bands [local]: e vs s -> band 3"
    assert "seed  25   +15.0%; grew: web +11.0s, field +1.0s" in text
    assert "crossed: seed 25 +15.0% > 10%" in text and "owes: bands 1 and 2, plus the GM" in text
    quiet = pb.render(pb.evaluate(snap("s", {1: 10.0}), snap("e", {1: 9.0})))
    assert "grew" not in quiet and "owes: nothing" in quiet
