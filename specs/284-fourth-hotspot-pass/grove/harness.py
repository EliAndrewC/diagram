"""Feature 284, SC-009's grove draw and seam closing: what each costs on the engine that ships - the grove draw
(`_draw_grove`) with the share of its crown seat test (`CrownIndex.clear`), and the seam closing (`close_seams`) with its
pocket welds (`_absorb`) - timed around the calls inside one build of Kashikawa and one of Sawada, fastest of three.

    make spec-harness SPEC=specs/284-fourth-hotspot-pass/grove OUT=<json>
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

OUT = Path(os.environ.get("HARNESS_OUT") or "/tmp/grove-284.json")
SPECS = {
    "kashikawa": dict(name="Kashikawa", seed=3, households=20, down_deg=315, water_sink="offmap", brook_side=-1, bamboo="both"),
    "sawada": dict(name="Sawada", seed=24, households=19, down_deg=225, water_sink="offmap", intake="open", lane_web="alleys"),
}


def test_grove() -> None:
    from l7r.diagram.hamletgen import driver
    from l7r.diagram.hamletgen.plan import HamletSpec, plan_site
    from l7r.diagram.settlement.homestead_parts import groves
    from l7r.diagram.settlement.shrines_wells import woods
    from l7r.diagram.waterfields import comb
    from l7r.diagram.waterfields.seams import close

    targets = ((groves.GrovesMixin, "_draw_grove"), (woods.CrownIndex, "clear"), (comb, "close_seams"), (close, "_absorb"))  # each patched where it is CALLED from: both are bound by name at import
    out: dict = {}
    for key, kw in SPECS.items():
        best: dict[str, float] = {}
        for _ in range(3):
            acc: dict[str, float] = {}
            saved = []
            for owner, name in targets:
                real = getattr(owner, name)
                saved.append((owner, name, real))

                def timed(*a, _real=real, _n=name, **k):
                    t = time.perf_counter()
                    try:
                        return _real(*a, **k)
                    finally:
                        acc[_n] = acc.get(_n, 0.0) + time.perf_counter() - t

                setattr(owner, name, timed)
            try:
                t = time.perf_counter()
                driver.build(plan_site(HamletSpec(**kw)))
                acc["build"] = time.perf_counter() - t
            finally:
                for owner, name, real in saved:
                    setattr(owner, name, real)
            for k, v in acc.items():
                best[k] = min(best.get(k, 1e9), v)
        out[key] = {k: round(v, 4) for k, v in best.items()}
    out["load"] = os.getloadavg()[0]
    OUT.write_text(json.dumps(out, indent=1))
