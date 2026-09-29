"""Feature 284: cohort seed 15 lost its connector in the clone - which change (research R6).

    make spec-harness SPEC=specs/284-fourth-hotspot-pass/c15 OUT=<json>
"""

from __future__ import annotations

import importlib.util
import json
import math
import os
from pathlib import Path

OUT = Path(os.environ.get("HARNESS_OUT") or "/tmp/c15-284.json")
STRAND = Path(__file__).resolve().parents[4] / "specs/284-fourth-hotspot-pass/strand/harness.py"


def _roll(dijkstra: bool, base_fit: bool) -> dict:
    from l7r.diagram.hamletgen import driver
    from l7r.diagram.hamletgen.plan import HamletSpec
    from l7r.diagram.hamletgen.water import fit
    from l7r.diagram.hamletgen.ways import route, track

    spec = importlib.util.spec_from_file_location("strand_h", STRAND)
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)  # type: ignore[union-attr]
    h.__file__ = __file__  # its base-fit copy resolves from the test node's place, as it does when it runs as one
    real = (route.lattice_search, fit._fit_at_aspect, track.connector_track, track._thread_the_fabric, track.route_around)
    seen: dict = {}

    def spy(*a, **k):
        got = real[2](*a, **k)
        seen["connector_track_len"] = round(sum(math.dist(p, q) for p, q in zip(got, got[1:], strict=False)))
        return got

    if dijkstra:
        route.lattice_search = h._dijkstra
    if base_fit:
        fit._fit_at_aspect = h._base_fit()._fit_at_aspect
    track.connector_track = spy

    def spy_around(*a, **k):
        got = real[4](*a, **k)
        seen.setdefault("route_around_lens", []).append(round(sum(math.dist(p, q) for p, q in zip(got, got[1:], strict=False))))
        return got

    def spy_thread(*a, **k):
        got = real[3](*a, **k)
        seen.setdefault("thread_lens", []).append(round(sum(math.dist(p, q) for p, q in zip(got, got[1:], strict=False))) if got else 0)
        return got

    track.route_around, track._thread_the_fabric = spy_around, spy_thread
    import traceback

    from l7r.diagram.settlement import Settlement

    real_drop = Settlement.drop_lanes

    def spy_drop(self, idxs):
        idxs = list(idxs)
        for i in idxs:
            ln = self.M["lanes"][i]
            if ln.get("connector"):
                seen.setdefault("connector_dropped_by", []).append([f"{f.filename.rsplit('/', 1)[-1]}:{f.lineno} {f.name}" for f in traceback.extract_stack()[-6:-1]] + [len(ln["pts"])])
        return real_drop(self, idxs)

    Settlement.drop_lanes = spy_drop
    try:
        rep = driver.generate(HamletSpec(name="Audit-15", seed=15, households=16), out_base=None, render=False)
    finally:
        route.lattice_search, fit._fit_at_aspect, track.connector_track, track._thread_the_fabric, track.route_around = real
        Settlement.drop_lanes = real_drop
    lanes = (rep.manifest or {}).get("lanes", [])
    seen["connector_drawn"] = [round(sum(math.dist(p, q) for p, q in zip(ln["pts"], ln["pts"][1:], strict=False))) for ln in lanes if ln.get("connector")]
    seen["acres"] = rep.plan.acres
    return seen


def test_c15() -> None:
    OUT.write_text(json.dumps({f"dijkstra={d} base_fit={b}": _roll(d, b) for d in (False,) for b in (False, True)}, indent=1))
