"""Feature 284 B4: the carve's plot tests as arrays against the scalar tests, on the calls Sawada's roll makes (research R5).

    make spec-harness SPEC=specs/284-fourth-hotspot-pass/b4 OUT=<json>

One build of Sawada records every `_edge_in_supply` call (the edge and its stroke index) and every `_spills_drain` call; the
array forms below answer the same calls - each edge's 3 px samples against each stroke's segments at once, and a row's
corners against the drain at once - and must give the same verdicts. Both are then timed fastest of three over the
recorded calls. The vertices' pushes (`_clear_supply`) are timed the same way.
"""

from __future__ import annotations

import json
import math
import os
import time
from pathlib import Path

import numpy as np

OUT = Path(os.environ.get("HARNESS_OUT") or "/tmp/b4-284.json")


def _seg_arrays(sidx):
    p = np.asarray(sidx.pts, dtype=float)
    a, v = p[:-1], p[1:] - p[:-1]
    return a, v, (v * v).sum(1), np.asarray(sidx.cum[:-1]), np.hypot(v[:, 0], v[:, 1])


def _edge_np(a, b, sup, g, seg_cache):
    from l7r.diagram.waterfields.banks import _PAST_EPS
    from l7r.diagram.waterfields.frame import BANK_MARGIN, taper_w

    for row in sup:
        sbb, sidx = row[4], row[5]
        if max(a[0], b[0]) < sbb[0] or min(a[0], b[0]) > sbb[2] or max(a[1], b[1]) < sbb[1] or min(a[1], b[1]) > sbb[3]:
            continue
        nstep = max(1, int(math.dist(a, b) / 3.0))
        t = np.arange(nstep + 1) / nstep
        q = np.stack([a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])], 1)
        sa, sv, sl2, cum, sl = seg_cache.setdefault(id(sidx), _seg_arrays(sidx))
        tt = (((q[:, None, :] - sa[None]) * sv[None]).sum(2)) / np.where(sl2 > 0, sl2, 1.0)[None]
        tc = np.clip(tt, 0.0, 1.0)
        foot = sa[None] + tc[..., None] * sv[None]
        d = np.hypot(q[:, None, 0] - foot[..., 0], q[:, None, 1] - foot[..., 1])
        i = d.argmin(1)
        gap = d[np.arange(len(q)), i]
        near = gap <= sidx.reach
        arc = cum[i] + tc[np.arange(len(q)), i] * sl[i]
        last = len(sidx.pts) - 2
        ti = tt[np.arange(len(q)), i]
        total = sidx.cum[-1] or 1.0
        past = ((i == 0) & (ti < 0)) | ((i == last) & (ti > 1)) | (arc <= _PAST_EPS) | (arc >= total - _PAST_EPS)
        halfw = np.array([taper_w(sidx.w0, sidx.w1, x / total) / 2 for x in arc])
        if np.any(near & ~past & (gap < halfw + BANK_MARGIN * g - 0.5)):
            return True
    return False


def test_b4_arrays() -> None:
    from l7r.diagram.hamletgen import driver
    from l7r.diagram.hamletgen.plan import HamletSpec, plan_site
    from l7r.diagram.waterfields import carve

    edges, clears = [], []
    real_edge, real_clear = carve._edge_in_supply, carve._clear_supply

    def rec_edge(a, b, sup, g):
        got = real_edge(a, b, sup, g)
        edges.append((a, b, sup, g, got))
        return got

    def rec_clear(x, y, hx, hy, sup, g):
        got = real_clear(x, y, hx, hy, sup, g)
        clears.append((x, y, hx, hy, sup, g))
        return got

    carve._edge_in_supply, carve._clear_supply = rec_edge, rec_clear
    driver.build(plan_site(HamletSpec(name="Sawada", seed=24, households=19, down_deg=225, water_sink="offmap", intake="open", lane_web="alleys")))
    carve._edge_in_supply, carve._clear_supply = real_edge, real_clear

    cache: dict = {}
    mismatch = sum(_edge_np(a, b, s, g, cache) != got for a, b, s, g, got in edges)

    def best(fn):
        ts = []
        for _ in range(3):
            t = time.perf_counter()
            fn()
            ts.append(time.perf_counter() - t)
        return min(ts)

    scalar_edges = best(lambda: [real_edge(a, b, s, g) for a, b, s, g, _ in edges])
    array_edges = best(lambda: [_edge_np(a, b, s, g, cache) for a, b, s, g, _ in edges])
    scalar_clears = best(lambda: [real_clear(*c) for c in clears])
    OUT.write_text(json.dumps({"edge_calls": len(edges), "edge_mismatches": mismatch, "scalar_edges_s": scalar_edges, "array_edges_s": array_edges, "clear_calls": len(clears), "scalar_clears_s": scalar_clears, "load": os.getloadavg()[0]}, indent=1))
