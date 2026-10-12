"""The GM's three-band matrix, pinned on both measurements, per environment (feature 129, T008) - since feature 375 amendment 5
a FLAG with the 5% band-1 line in every environment, judged in CPU seconds where both snapshots have them."""

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


def test_a_seed_over_the_line_is_band_1_even_when_the_total_falls() -> None:
    v = pb.evaluate(snap("s", {1: 100.0, 2: 100.0}), snap("e", {1: 105.5, 2: 90.0}))
    assert v.band == 1 and v.seeds == {1: 5.5, 2: -10.0} and v.total_pct == -2.2
    assert "flag" in v.owes and "nothing waits" in v.owes, "a band is a flag since feature 375 amendment 5, never a record owed"


def test_band_2_on_the_total_and_on_a_seed() -> None:
    assert pb.evaluate(snap("s", {1: 100.0, 2: 100.0}), snap("e", {1: 106.0, 2: 105.0})).band == 2  # total +5.5
    v = pb.evaluate(snap("s", {1: 100.0, 2: 100.0}), snap("e", {1: 111.0, 2: 95.0}))  # total +3, seed +11
    assert v.band == 2 and v.crossed == ("seed 1 +11.0% > 10%",) and "flag" in v.owes
    assert pb.evaluate(snap("s", {1: 100.0}), snap("e", {1: 105.0})).band == 0, "exactly 5% is not over the band-1 line, and not band 2's either"


def test_feature_128s_pair_is_band_3_despite_a_faster_total() -> None:
    """SC-002b: total -29.9%, seed 47 +30.7% - the case the per-seed numbers exist for."""
    base = snap("128-start", {4: 23.7, 25: 222.7, 39: 67.8, 47: 68.3})
    end = snap("128-end", {4: 26.8, 25: 80.6, 39: 71.5, 47: 89.3})
    v = pb.evaluate(base, end)
    assert v.total_pct == -29.9 and v.seeds[47] == 30.7 and v.band == 3
    assert "seed 47 +30.7% > 20%" in v.crossed and "seed 47 +30.7% > 10%" in v.crossed
    assert "flag" in v.owes and "nothing waits" in v.owes, "band 3 is a flag to mention at landing (feature 375 amendment 5)"
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
    v = pb.evaluate(snap("s", {1: 100.0}, None), snap("e", {1: 106.0}, "local"))
    assert v.environment == "local" and v.band == 2


def test_seeds_only_in_one_snapshot_are_ignored_and_a_zero_base_is_safe() -> None:
    v = pb.evaluate(snap("s", {1: 100.0, 9: 0.0}), snap("e", {1: 100.0, 2: 50.0, 9: 0.0}))
    assert set(v.seeds) == {1, 9} and v.seeds[9] == 0.0 and v.band == 0, "seed 2 has no base and is ignored; a zero base divides safely"


def test_render_names_the_measurement_the_stage_that_grew_and_what_is_owed() -> None:
    base = snap("s", {25: 80.0}, stages={25: {"web": 60.0, "field": 20.0}})
    end = snap("e", {25: 92.0}, stages={25: {"web": 71.0, "field": 21.0}})
    text = pb.render(pb.evaluate(base, end))
    assert text.splitlines()[0] == "perf bands [local]: e vs s -> band 3, in wall seconds"
    assert "seed  25   +15.0%; grew: web +11.0s, field +1.0s" in text
    assert "crossed: seed 25 +15.0% > 10%" in text and "FLAG: this looks slower - total +15.0%, seed 25 +15.0%" in text
    assert "It may be the machine's load" in text and "nothing waits on it" in text
    quiet = pb.render(pb.evaluate(snap("s", {1: 10.0}), snap("e", {1: 9.0})))
    assert "grew" not in quiet and "FLAG" not in quiet


# --- feature 179: the band-1 line is PER ENVIRONMENT -------------------------------------------
# The GM's own number ("a noise floor of about two percent"), and the measurement behind needing one:
# three snapshots of IDENTICAL code on the same CodeBuild box fired band 1 on 5 of 6 pairwise
# comparisons. These pin that the floor exists, that it is applied on BOTH measurements, that it
# leaves local strict, and - the property that makes it safe - that bands 2 and 3 do not move.


def test_the_band1_line_is_5_percent_in_every_environment() -> None:
    """Feature 375 amendment 5 (the GM 2026-10-11: "let's extent it from 2% to 5% for the jitter")."""
    assert pb.BAND1_PCT == {"local": 5.0, "codebuild": 5.0}
    assert pb.BAND1_DEFAULT_PCT == 5.0


def test_local_noise_under_the_line_is_not_flagged() -> None:
    v = pb.evaluate(snap("s", {1: 100.0, 2: 100.0}, "local"), snap("e", {1: 105.0, 2: 105.0}, "local"))
    assert v.band == 0 and v.total_pct == 5.0, "every seed and the total at exactly the line: unflagged"
    over = pb.evaluate(snap("s", {1: 100.0, 2: 100.0}, "local"), snap("e", {1: 105.1, 2: 100.0}, "local"))
    assert over.band == 1 and over.seeds[1] == 5.1, "a tenth of a point over on one seed is flagged"


def test_codebuild_noise_under_the_floor_does_not_reach_band_1() -> None:
    # +1.16% is the WORST seed feature 129 measured on identical code. It must not owe an explanation.
    v = pb.evaluate(snap("s", {1: 100.0}, "codebuild"), snap("e", {1: 101.16}, "codebuild"))
    assert v.band == 0 and v.total_pct == 1.2


def test_codebuild_over_the_floor_still_reaches_band_1() -> None:
    v = pb.evaluate(snap("s", {1: 100.0, 2: 100.0}, "codebuild"), snap("e", {1: 107.0, 2: 100.0}, "codebuild"))
    assert v.band == 1


def test_the_floor_applies_to_a_single_seed_not_only_the_total() -> None:
    # total is NEGATIVE, one seed is over the line - feature 128's shape, one rung down.
    v = pb.evaluate(snap("s", {1: 100.0, 2: 100.0}, "codebuild"), snap("e", {1: 106.0, 2: 90.0}, "codebuild"))
    assert v.total_pct < 0 and v.seeds[1] == 6.0 and v.band == 1
    # and the same shape UNDER the line owes nothing
    quiet = pb.evaluate(snap("s", {1: 100.0, 2: 100.0}, "codebuild"), snap("e", {1: 104.0, 2: 90.0}, "codebuild"))
    assert quiet.seeds[1] == 4.0 and quiet.band == 0


def test_exactly_the_floor_is_not_over_the_line() -> None:
    v = pb.evaluate(snap("s", {1: 100.0}, "codebuild"), snap("e", {1: 105.0}, "codebuild"))
    assert v.total_pct == 5.0 and v.band == 0, "`>` not `>=`, matching BAND2's own boundary"


def test_an_unknown_environment_takes_the_same_line() -> None:
    assert pb.evaluate(snap("s", {1: 100.0}, "somebox"), snap("e", {1: 104.0}, "somebox")).band == 0
    v = pb.evaluate(snap("s", {1: 100.0, 2: 100.0}, "somebox"), snap("e", {1: 106.0, 2: 100.0}, "somebox"))
    assert v.band == 1, "a new environment arrives with the 5% the GM chose for all"


def test_the_floor_does_not_move_bands_2_and_3() -> None:
    # This is the property that makes the mute safe: a real regression escalates exactly as before.
    over2 = pb.evaluate(snap("s", {1: 100.0}, "codebuild"), snap("e", {1: 106.0}, "codebuild"))
    assert over2.band == 2
    over3 = pb.evaluate(snap("s", {1: 100.0}, "codebuild"), snap("e", {1: 111.0}, "codebuild"))
    assert over3.band == 3
    seed2 = pb.evaluate(snap("s", {1: 100.0, 2: 100.0}, "codebuild"), snap("e", {1: 111.0, 2: 80.0}, "codebuild"))
    assert seed2.seeds[1] == 11.0 and seed2.band == 2, "a seed over 10% escalates though the total fell"


def test_band0_no_longer_claims_there_was_no_increase() -> None:
    v = pb.evaluate(snap("s", {1: 100.0}, "codebuild"), snap("e", {1: 101.0}, "codebuild"))
    assert v.band == 0 and "no increase on the total or on any seed" not in v.owes


def test_a_muted_increase_is_still_fully_visible_on_the_page() -> None:
    # FR-011: no disclosure machinery was added because none is needed - render() already prints
    # every seed and the total unconditionally, whatever the band.
    text = pb.render(pb.evaluate(snap("s", {1: 100.0}, "codebuild"), snap("e", {1: 101.0}, "codebuild")))
    assert "+1.0%" in text and "band 0" in text


# --- feature 375 amendment 5: CPU seconds where both snapshots have them, and the machine's state in the flag ----------------


def test_a_pair_is_judged_in_cpu_seconds_when_both_carry_them_and_in_wall_seconds_otherwise() -> None:
    base, end = snap("s", {1: 100.0}), snap("e", {1: 130.0})  # wall: +30%
    for s, cpu in ((base, 50.0), (end, 51.0)):  # CPU: +2%
        s["rows"][0]["cpu_seconds"], s["rows"][0]["cpu_stages"] = cpu, {"web": cpu}
    v = pb.evaluate(base, end)
    assert v.metric == "cpu_seconds" and v.band == 0 and v.seeds[1] == 2.0 and "in CPU seconds" in pb.render(v)
    del base["rows"][0]["cpu_seconds"]
    w = pb.evaluate(base, end)
    assert w.metric == "seconds" and w.band == 3, "a base from before CPU timing is judged on wall time, never muted"


def test_the_flag_carries_both_snapshots_machine_state() -> None:
    base, end = snap("s", {1: 100.0}), snap("e", {1: 112.0})
    base["machine_before"] = {"load": [0.5, 0.4, 0.3], "ram_available_mb": 8192, "ram_total_mb": 15360, "disk_free_gb": 120.0}
    end["machine_after"] = {"load": [9.0, 7.0, 5.0]}
    text = pb.flag(pb.evaluate(base, end))
    assert "s: at its start load 0.5/0.4/0.3, 8.0 of 15.0 GB RAM free, 120 GB disk free; at its end not recorded" in text
    assert "e: at its start not recorded; at its end load 9.0/7.0/5.0" in text and "seed 1 +12.0%" in text
