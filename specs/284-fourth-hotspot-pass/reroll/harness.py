"""Feature 284: a re-roll resumed at the seats against a re-roll built from scratch, on the maps that re-roll (research R8).

    make spec-harness SPEC=specs/284-fourth-hotspot-pass/reroll OUT=<json>

Per map that strands a house on its first roll (R4's table at the 10 px lattice): the first roll built with its snapshot,
the stranded seats read by the driver's own predicate, then the re-roll made both ways - `build` on a fresh copy of the
plan with that avoid list, and `resume` from the snapshot - and each finished to a scratch svg and page. The manifests,
the svgs and the pages must be byte-identical. Times: the first roll with and without the snapshot, and each re-roll.
"""

from __future__ import annotations

import copy
import json
import os
import tempfile
import time
from pathlib import Path

OUT = Path(os.environ.get("HARNESS_OUT") or "/tmp/reroll-284.json")
SPECS = {
    "kashikawa": dict(name="Kashikawa", seed=3, households=20, down_deg=315, water_sink="offmap", brook_side=-1, bamboo="both"),
}


def _finished(s, d, name) -> tuple[str, bytes, bytes]:
    base = os.path.join(d, name)
    s.finish(base, render=False)
    return json.dumps(s.M, sort_keys=True, default=str), Path(base + ".svg").read_bytes(), Path(base + ".html").read_bytes() if Path(base + ".html").exists() else b""


def test_reroll_resume() -> None:
    from l7r.diagram.hamletgen import driver
    from l7r.diagram.hamletgen.plan import HamletSpec, plan_site

    specs = dict(SPECS)
    for sp in driver.cohort_specs(24, first_seed=1):
        if sp.seed in (1, 5, 17, 18, 19):
            specs[f"cohort-{sp.seed:02d}"] = sp
    rows = {}
    for key, kw in specs.items():
        spec = HamletSpec(**kw) if isinstance(kw, dict) else kw
        plan = plan_site(spec)
        t = time.perf_counter()
        driver.build(copy.deepcopy(plan))
        plain = time.perf_counter() - t
        snap: list = []
        t = time.perf_counter()
        first = driver.build(copy.deepcopy(plan), snapshot=snap)
        with_snap = time.perf_counter() - t
        avoid = [(float(x), float(y)) for x, y, _d in driver.unreached_houses(first.M)]
        t = time.perf_counter()
        full = driver.build(copy.deepcopy(plan), avoid=avoid)
        t_full = time.perf_counter() - t
        t = time.perf_counter()
        res, _plan = driver.resume(snap, avoid)
        t_res = time.perf_counter() - t
        with tempfile.TemporaryDirectory() as d:
            a, b = _finished(full, d, "full"), _finished(res, d, "res")
        rows[key] = {"avoid": len(avoid), "first_s": round(plain, 3), "first_with_snapshot_s": round(with_snap, 3), "reroll_full_s": round(t_full, 3), "reroll_resume_s": round(t_res, 3), "manifest_equal": a[0] == b[0], "svg_equal": a[1] == b[1], "page_equal": a[2] == b[2], "page_bytes": len(a[2])}
    rows["load"] = os.getloadavg()[0]  # type: ignore[assignment]
    OUT.write_text(json.dumps(rows, indent=1))
