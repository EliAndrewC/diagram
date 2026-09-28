"""Feature 284 T15 probe: the seam closing, commons, flush and grove fill re-profiled on Sawada and Kashikawa.

    make spec-harness SPEC=specs/284-fourth-hotspot-pass/t15 OUT=<txt>
"""

from __future__ import annotations

import cProfile
import io
import os
import pstats
import tempfile
from pathlib import Path

OUT = Path(os.environ.get("HARNESS_OUT") or "/tmp/t15-284.txt")
SPECS = {
    "sawada": dict(name="Sawada", seed=24, households=19, down_deg=225, water_sink="offmap", intake="open", lane_web="alleys"),
    "kashikawa": dict(name="Kashikawa", seed=3, households=20, down_deg=315, water_sink="offmap", brook_side=-1, bamboo="both"),
}


def test_t15_profile() -> None:
    from l7r.diagram.hamletgen import driver
    from l7r.diagram.hamletgen.plan import HamletSpec, plan_site

    buf = io.StringIO()
    for key, kw in SPECS.items():
        pr = cProfile.Profile()
        pr.enable()
        s = driver.build(plan_site(HamletSpec(**kw)))
        with tempfile.TemporaryDirectory() as tmp:
            s.finish(os.path.join(tmp, "x"), render=False)
        pr.disable()
        buf.write(f"===== {key}\n")
        st = pstats.Stats(pr, stream=buf)
        st.sort_stats("tottime").print_stats(45)
        st.print_callees(r"siting.py.*place_kosatsuba|siting.py.*_sitable|siting.py.*board_caption_level|cover.py.*hinterland|web.py.*stage_web")
        st.sort_stats("cumulative").print_stats(r"diagram/", 40)
    OUT.write_text(buf.getvalue())
