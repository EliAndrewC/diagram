"""Feature 284, FR-006's second half: what the page's own passes cost over the strings it still parses (the blade slots
aside), on Kashikawa and Sawada - each pass timed around its call inside `render_page`, fastest of three finishes.

    make spec-harness SPEC=specs/284-fourth-hotspot-pass/parse OUT=<json>
"""

from __future__ import annotations

import copy
import json
import os
import tempfile
import time
from pathlib import Path

OUT = Path(os.environ.get("HARNESS_OUT") or "/tmp/parse-284.json")
SPECS = {
    "kashikawa": dict(name="Kashikawa", seed=3, households=20, down_deg=315, water_sink="offmap", brook_side=-1, bamboo="both"),
    "sawada": dict(name="Sawada", seed=24, households=19, down_deg=225, water_sink="offmap", intake="open", lane_web="alleys"),
}
PASSES = (("raster", "drop_offmap"), ("page", "merge_primitives"), ("page", "marks_region"), ("page", "hit_layer"), ("page", "hit_copies"), ("page", "render_page"), ("page", "ink_census"))


def test_parse() -> None:
    from l7r.diagram.hamletgen import driver
    from l7r.diagram.hamletgen.plan import HamletSpec, plan_site
    from l7r.diagram.interactive import page, raster

    mods = {"page": page, "raster": raster}
    out: dict = {}
    for key, kw in SPECS.items():
        s0 = driver.build(plan_site(HamletSpec(**kw)))
        best: dict[str, float] = {}
        for _ in range(3):
            acc: dict[str, float] = {}
            saved = {}
            for mod, fn in PASSES:
                real = getattr(mods[mod], fn)
                saved[(mod, fn)] = real

                def timed(*a, _real=real, _fn=fn, **k):
                    t = time.perf_counter()
                    try:
                        return _real(*a, **k)
                    finally:
                        acc[_fn] = acc.get(_fn, 0.0) + time.perf_counter() - t

                setattr(mods[mod], fn, timed)
            try:
                s = copy.deepcopy(s0)
                with tempfile.TemporaryDirectory() as d:
                    os.environ["DIAGRAM_SKIP_RENDER"] = "1"
                    s.finish(os.path.join(d, "x"), render=False)
            finally:
                for (mod, fn), real in saved.items():
                    setattr(mods[mod], fn, real)
            for k, v in acc.items():
                best[k] = min(best.get(k, 1e9), v)
        out[key] = {k: round(v, 4) for k, v in best.items()}
    out["load"] = os.getloadavg()[0]
    OUT.write_text(json.dumps(out, indent=1))
