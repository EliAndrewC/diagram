"""Feature 284: which change makes Kashikawa's first roll strand a house (research R8) - the clone as it is, and with the
router's search ordered by cost alone (Dijkstra, the base's order) in place of A*.

    make spec-harness SPEC=specs/284-fourth-hotspot-pass/strand OUT=<json>
"""

from __future__ import annotations

import heapq
import json
import math
import os
from pathlib import Path

OUT = Path(os.environ.get("HARNESS_OUT") or "/tmp/strand-284.json")
KASHIKAWA = dict(name="Sawada", seed=24, households=19, down_deg=225, water_sink="offmap", intake="open", lane_web="alleys")


def _dijkstra(start, goal, nx, ny, is_free, in_band, toll, cell):
    sx, sy = start
    gx, gy = goal
    dist = {(sx, sy): 0.0}
    prev = {}
    heap = [(0.0, sx, sy)]
    while heap:
        d, ix, iy = heapq.heappop(heap)
        if (ix, iy) == (gx, gy):
            break
        if d > dist.get((ix, iy), 1e18):
            continue
        for dx2 in (-1, 0, 1):
            for dy2 in (-1, 0, 1):
                jx, jy = ix + dx2, iy + dy2
                if (dx2 or dy2) and 0 <= jx < nx and 0 <= jy < ny and is_free(jx, jy) and (not (dx2 and dy2) or (is_free(jx, iy) and is_free(ix, jy))):
                    nd = d + math.hypot(dx2, dy2) * cell + (toll if toll and in_band(jx, jy) and not in_band(ix, iy) else 0.0)
                    if nd < dist.get((jx, jy), 1e18):
                        dist[(jx, jy)] = nd
                        prev[(jx, jy)] = (ix, iy)
                        heapq.heappush(heap, (nd, jx, jy))
    return dist, prev


def _base_fit():
    import types

    mod = types.ModuleType("l7r.diagram.hamletgen.water.base_fit")
    mod.__package__ = "l7r.diagram.hamletgen.water"
    exec(compile((Path(__file__).resolve().parents[4] / "specs/284-fourth-hotspot-pass/strand/base_fit.py.txt").read_text(), "base_fit.py", "exec"), mod.__dict__)  # noqa: S102 - the base's own fit.py
    return mod


def _first_roll(patch: bool, base_fit: bool = False) -> list[int]:
    from l7r.diagram.hamletgen import driver
    from l7r.diagram.hamletgen.plan import HamletSpec
    from l7r.diagram.hamletgen.ways import route

    real_search, real_unreached = route.lattice_search, driver.unreached_houses
    counts: list[int] = []

    def counted(M):
        got = real_unreached(M)
        counts.append(len(got))
        return got

    from l7r.diagram.hamletgen.water import fit

    real_fit = fit._fit_at_aspect
    if patch:
        route.lattice_search = _dijkstra
    if base_fit:
        fit._fit_at_aspect = _base_fit()._fit_at_aspect
    driver.unreached_houses = counted
    try:
        driver.generate(HamletSpec(**KASHIKAWA), out_base=None, render=False)
    finally:
        route.lattice_search, driver.unreached_houses, fit._fit_at_aspect = real_search, real_unreached, real_fit
    return counts


def test_strand() -> None:
    OUT.write_text(json.dumps({"clone_a_star": _first_roll(False), "clone_dijkstra": _first_roll(True)}))
