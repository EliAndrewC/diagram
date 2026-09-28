"""Feature 276's measurement harness - the SAME code takes the before and the after figures.

Run it from the skill directory through a pytest node (the engine refuses in-process calls outside make):

    cp ../../../specs/276-engine-hotspots-and-test-scans/harness.py tests/test_zz_harness_276_tmp.py
    make test-file FILE=tests/test_zz_harness_276_tmp.py      # writes $H276_OUT (default /tmp/h276.json)
    rm tests/test_zz_harness_276_tmp.py

Every timing is wall-clock, unprofiled, the best of `REPEAT` runs in one process (the first run pays imports).
What each section measures:

- `tests`: each named test ALONE in a fresh interpreter, its setup + call time from `--durations`, xdist off.
- `homesteads`: `stage_homesteads` on the toy site of `tests/hamletgen/test_homesteads.py` - the rescue-rounds
  scenario verbatim, then the open toy at 20 / 40 / 80 households (the density question) - with the count of
  full fit tests (`_bundle_fits` + `_envelope_blocked`, whichever the placer calls) and houses seated.
- `seams`: `build_comb` at the comb-topology seeds, total and inside `close_seams`.
- `track`: one reference roll (Inashiro, seed 4) with `stage_track` and `path_violations` timed inside it.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

REPEAT = 3
SKILL = Path(__file__).resolve().parents[1] if (Path(__file__).resolve().parents[1] / "Makefile").exists() else Path.cwd()
OUT = Path(os.environ.get("H276_OUT", "/tmp/h276.json"))

TESTS = [
    "tests/test_memory.py::test_no_engine_module_imports_a_heavy_library_at_import_time",
    "tests/hamletgen/test_driver.py::test_every_loop_that_runs_the_stages_sits_inside_a_roll_scope",
    "tests/test_package_surfaces.py::test_the_census_found_the_tree",
    "tests/settlement/test_water_ways.py::test_no_pass_deletes_a_lane_record_without_its_ink_slot",
    "tests/interactive/test_record.py::test_every_link_in_a_record_page_resolves[religion-and-death.html]",
    "tests/interactive/test_record.py::test_every_link_in_a_record_page_resolves[buildings.html]",
    "tests/interactive/test_record.py::test_no_tracked_file_names_a_retired_rule_file",
    "tests/interactive/test_record.py::test_no_md_token_anywhere_resolves_to_a_converted_record_file",
    "tests/interactive/test_record_format.py::test_every_glossary_term_is_used_by_a_modal_or_a_record_page",
    "tests/hamletgen/test_homesteads.py::test_a_quota_the_ranks_cannot_seat_reaches_the_rescue_rounds",
    "tests/waterfields/test_seams.py::test_a_map_whose_blue_sample_is_all_demoted_still_exhibits_one_flooded_basin",
    "tests/waterfields/test_comb_topology.py::test_every_channel_is_a_real_run_rather_than_a_stub[11]",
    "tests/settlement/test_core.py::test_build_comb_supply_banks_hems_bunds_onto_the_channel_banks",
]

_DUR = re.compile(r"^([0-9.]+)s (setup|call|teardown)\s+(\S+)", re.M)


def _tests() -> dict[str, float]:
    out = {}
    for nid in TESTS:
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:xdist", "-p", "no:cacheprovider", "--no-cov", "--durations=0", "--durations-min=0", nid],
            cwd=SKILL, capture_output=True, text=True,
            env={**os.environ, "GATE_NO_CACHE": "1"},  # a comb test must BUILD, not read the roll cache
        )
        tot = sum(float(m.group(1)) for m in _DUR.finditer(r.stdout) if m.group(2) != "teardown")
        out[nid] = round(tot, 3) if r.returncode == 0 else -1.0
    return out


def _best(fn):
    best = None
    res = None
    for _ in range(REPEAT):
        t = time.perf_counter()
        res = fn()
        dt = time.perf_counter() - t
        best = dt if best is None else min(best, dt)
    return best, res


def _homesteads() -> dict:
    from l7r.diagram.hamletgen.homesteads import stage_homesteads
    from l7r.diagram.settlement import Settlement
    from tests.hamletgen.test_homesteads import _toy_hamlet

    counted = {"fits": 0}
    patched = []
    for name in ("_bundle_fits", "_envelope_blocked"):
        if hasattr(Settlement, name):
            real = getattr(Settlement, name)

            def wrap(self, *a, _real=real, **k):
                counted["fits"] += 1
                return _real(self, *a, **k)

            setattr(Settlement, name, wrap)
            patched.append((name, real))
    rows = {}
    try:
        def rescue():
            s, plan = _toy_hamlet(20)
            cx_, cy_ = float(plan.seat["cx"]), float(plan.seat["cy"])
            s.block_polys.append([(cx_ - 2000.0, cy_ - 2000.0), (cx_ + 2000.0, cy_ - 2000.0), (cx_ + 2000.0, cy_ - 260.0), (cx_ - 2000.0, cy_ - 260.0)])
            s.block_polys.append([(cx_ - 2000.0, cy_ + 260.0), (cx_ + 2000.0, cy_ + 260.0), (cx_ + 2000.0, cy_ + 2000.0), (cx_ - 2000.0, cy_ + 2000.0)])
            counted["fits"] = 0
            stage_homesteads(s, plan)
            return len(s.M["houses"]), counted["fits"]

        dt, (houses, fits) = _best(rescue)
        rows["rescue-20"] = {"s": round(dt, 3), "houses": houses, "fit_tests": fits}
        for n in (10, 20):  # the hamlet band is 10-20 households; a larger quota is a village
            def open_toy(n=n):
                s, plan = _toy_hamlet(n)
                counted["fits"] = 0
                stage_homesteads(s, plan)
                return len(s.M["houses"]), counted["fits"]

            dt, (houses, fits) = _best(open_toy)
            rows[f"open-{n}"] = {"s": round(dt, 3), "houses": houses, "fit_tests": fits, "s_per_house": round(dt / max(houses, 1), 4)}
        # THE DENSITY QUESTION, on the placement primitive: `try_place` for N seeds on a jittered grid at a
        # CONSTANT density - the site grows with N, as a city's does - so a placer whose cost per house is flat
        # shows a flat `s_per_house`, and one that re-tests every placed house per candidate grows with N.
        import random as _r

        for n in (60, 120, 240):
            def dense(n=n):
                side = int((n ** 0.5) * 95) + 400
                s = Settlement(side, side, seed=7)
                s.meta(name="D", scale="hamlet", ftpx=1, toscale=True, households=15, down_deg=90, water_flow=90, nucleated=True)
                rng = _r.Random(n)
                k = int(n ** 0.5) + 1
                counted["fits"] = 0
                seated = 0
                for i in range(n):
                    gx, gy = i % k, i // k
                    x = 200 + gx * 95 + rng.uniform(-20, 20)
                    y = 200 + gy * 95 + rng.uniform(-20, 20)
                    if s.try_place(x, y, "plain"):
                        seated += 1
                return seated, counted["fits"]

            dt, (houses, fits) = _best(dense)
            rows[f"dense-{n}"] = {"s": round(dt, 3), "houses": houses, "fit_tests": fits, "s_per_house": round(dt / max(houses, 1), 4)}
    finally:
        for name, real in patched:
            setattr(Settlement, name, real)
    return rows


def _seams() -> dict:
    from l7r.diagram.waterfields import comb

    inside = {"t": 0.0}
    real = comb.close_seams

    def timed(*a, **k):
        t = time.perf_counter()
        try:
            return real(*a, **k)
        finally:
            inside["t"] += time.perf_counter() - t

    comb.close_seams = timed
    rows = {}
    try:
        for seed in (5, 11, 17):
            def build(seed=seed):
                inside["t"] = 0.0
                comb.build_comb(2400, 2400, (300.0, 300.0), seed=seed, down_deg=90)
                return inside["t"]

            dt, seam = _best(build)
            rows[f"seed-{seed}"] = {"build_s": round(dt, 3), "close_seams_s": round(seam, 3)}
    finally:
        comb.close_seams = real
    return rows


def _track() -> dict:
    from l7r.diagram import hamletgen as hg
    from l7r.diagram.hamletgen.ways import track

    acc = {"stage": 0.0, "checks": 0.0, "calls": 0}
    real_stage, real_pv = track.stage_track, track.path_violations

    def stage(*a, **k):
        t = time.perf_counter()
        try:
            return real_stage(*a, **k)
        finally:
            acc["stage"] += time.perf_counter() - t

    def pv(*a, **k):
        acc["calls"] += 1
        t = time.perf_counter()
        try:
            return real_pv(*a, **k)
        finally:
            acc["checks"] += time.perf_counter() - t

    track.path_violations = pv
    import l7r.diagram.hamletgen.driver as drv
    stages_before = drv.STAGES
    try:
        drv.STAGES = tuple(stage if f is real_stage else f for f in stages_before)
        best = None
        for _ in range(REPEAT):
            acc.update(stage=0.0, checks=0.0, calls=0)
            hg.generate(hg.HamletSpec(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond"), render=False)
            row = {"stage_s": round(acc["stage"], 3), "path_checks_s": round(acc["checks"], 3), "calls": acc["calls"]}
            if best is None or row["stage_s"] < best["stage_s"]:
                best = row
        return best or {}
    finally:
        track.path_violations = real_pv
        drv.STAGES = stages_before


def test_harness_276() -> None:
    result = {"tests": _tests(), "homesteads": _homesteads(), "seams": _seams(), "track": _track()}
    OUT.write_text(json.dumps(result, indent=2))
