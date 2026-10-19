"""City knob helpers - the machi mouths (feature 145: moved out of _knobs.py, whose knob engine every map executes).

Research: plumbing - NONE
"""

import math
from typing import Any

from .._geom import point_in_poly, seg_intersect, segments_cross


def machi_mouths(M: Any) -> list[tuple[float, float]]:
    """Every point where a town street ENTERS a machi-kind district - the ward mouths the kido
    mesh bars at night (research 021 item 6: Edo's machi-kido, Qing's zhalan; ward_style
    "mesh" has NO ward walls - the block's own gate closes its mouth). THE SINGLE SOURCE for
    both the placer (Settlement.kido_mesh) and the validator (kido_close_the_machi_mouths),
    same doctrine as bridge_carried_ways. Out-wall suburb districts are skipped: the gate
    wards live outside the curfew mesh (their bar is the city gate itself). Mouths within
    40px collapse to one (a street grazing a district corner is one entry, not two).

    Research:
        a gate at every ward mouth - research/questions/0160-city-wards-and-the-gates-that-shut-them-at-night-machi-kido.html: every street entering a machi district
        suburb wards outside the mesh - UNRESEARCHED: out-wall machi districts get no mouths
        mouth merge radius - NONE: crossings within 40 px are one entry
    """
    wall = M.get("wall")
    out: list[tuple[float, float]] = []
    for d in M.get("districts", []):
        if d.get("kind") != "machi":
            continue
        poly = d["poly"]
        if wall:
            cx = sum(p[0] for p in poly) / len(poly)
            cy = sum(p[1] for p in poly) / len(poly)
            if not point_in_poly(cx, cy, wall):
                continue
        ring = [tuple(p) for p in poly] + [tuple(poly[0])]
        for st in M.get("town_streets", []):
            pts = st["pts"]
            for i in range(len(pts) - 1):
                for j in range(len(ring) - 1):
                    if not segments_cross(tuple(pts[i]), tuple(pts[i + 1]), ring[j], ring[j + 1]):
                        continue
                    xpt = seg_intersect(tuple(pts[i]), tuple(pts[i + 1]), ring[j], ring[j + 1])
                    if xpt is not None and not any(math.hypot(xpt[0] - ox, xpt[1] - oy) < 40 for ox, oy in out):
                        out.append((xpt[0], xpt[1]))
    return out
