"""Feature 284: does the fabric push's box prefilter answer Sawada's real calls as the old walk did (research R6)?

    make spec-harness SPEC=specs/284-fourth-hotspot-pass/push OUT=<json>
"""

from __future__ import annotations

import json
import os
from pathlib import Path

OUT = Path(os.environ.get("HARNESS_OUT") or "/tmp/push-284.json")


def test_push() -> None:
    from l7r.diagram.hamletgen import driver
    from l7r.diagram.hamletgen.plan import HamletSpec, plan_site
    from l7r.diagram.hamletgen.ways import track
    from l7r.diagram.settlement._geom import edge_dist

    real = track.push_clear_of_fabric
    rows = []

    def old(base, unit, edge, fabric, gap=None):
        from l7r.diagram.hamletgen.consts import TRACK_FABRIC_GAP

        gap = TRACK_FABRIC_GAP if gap is None else gap
        for _ in range(24):
            gx, gy = base[0] + unit[0] * edge, base[1] + unit[1] * edge
            if not any(edge_dist(gx, gy, poly) < gap for poly in fabric):
                return (gx, gy)
            edge += 6.0
        return (base[0] + unit[0] * edge, base[1] + unit[1] * edge)

    def spy(base, unit, edge, fabric, *a, **k):
        got = real(base, unit, edge, fabric, *a, **k)
        want = old(base, unit, edge, fabric, *a, **k)
        rows.append({"got": got, "want": want, "polys": len(fabric), "empty": sum(1 for p in fabric if not p), "short": sum(1 for p in fabric if 0 < len(p) < 3)})
        return got

    track.push_clear_of_fabric = spy
    try:
        driver.build(plan_site(HamletSpec(name="Sawada", seed=24, households=19, down_deg=225, water_sink="offmap", intake="open", lane_web="alleys")))
    finally:
        track.push_clear_of_fabric = real
    OUT.write_text(json.dumps(rows, indent=1))
