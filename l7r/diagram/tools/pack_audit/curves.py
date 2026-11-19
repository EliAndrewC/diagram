"""A curve's drawn points, as the sheets' reader flattens it (feature 449 T152: moved here from `l7r/diagram/labels/hand_sheet.py` when the
Python labels package was deleted - the audit's tagged walk reads a curve by them, and the Rust reader is `rust/mode_a/src/labels/hand_sheet/read.rs`).

Research: the curve flattening - NONE: a path's curves as points within a drawn tolerance, deciding nothing about a building
"""

from __future__ import annotations

import math

#: A point.
Pt = tuple[float, float]

DISC_SAG_PX = 0.05
"""How far a disc's drawn curve, sampled as a polygon, may stand inside the true curve (px): a leader's end on it lands within its
1 px trim and this of the curve (feature 449 T192).

Research: a disc's sampled curve - CONVENTION: a disc's drawn curve sampled finely enough that no chord stands more than 0.05 px inside it - a drawn size on the sheet, not in the world; the sample count is the least whose chord sag R(1 - cos(pi / n)) is within it, R bounding the curve's half-axes (the pool's largest disc half-axis is 45 px, 80 samples at the bound)"""


def _bezier(cp: tuple[Pt, ...], tol: float) -> list[Pt]:
    """A cubic or quadratic Bezier's points after its start, in the fewest equal steps of its parameter whose chords stand within `tol`
    of the curve: Wang's bound, n(n - 1) / 8 times the largest second difference of the control points, over the square of the steps."""
    deg = len(cp) - 1
    dd = max(math.hypot(cp[k][0] - 2 * cp[k + 1][0] + cp[k + 2][0], cp[k][1] - 2 * cp[k + 1][1] + cp[k + 2][1]) for k in range(deg - 1))
    n = max(1, math.ceil(math.sqrt(deg * (deg - 1) / 8 * dd / tol)))
    out: list[Pt] = []
    for k in range(1, n + 1):
        t = k / n
        w = [math.comb(deg, j) * t**j * (1 - t) ** (deg - j) for j in range(deg + 1)]
        out.append((sum(wj * p[0] for wj, p in zip(w, cp, strict=True)), sum(wj * p[1] for wj, p in zip(w, cp, strict=True))))
    out[-1] = cp[-1]
    return out


def _arc(p0: Pt, rx: float, ry: float, rot: float, large: bool, sweep: bool, e: Pt, tol: float) -> list[Pt]:
    """An elliptical arc's points after its start, as SVG draws it (SVG 1.1 appendix F.6): none where it ends where it starts, a
    straight step where a radius is 0, its radii scaled up where they cannot reach the end, and its center found from its flags;
    flattened in equal steps of its angle whose chords stand within `tol` of the curve, R(1 - cos(half a step)), R its larger radius."""
    if p0 == e:
        return []
    rx, ry = abs(rx), abs(ry)
    if rx == 0.0 or ry == 0.0:
        return [e]
    phi = math.radians(rot)
    cp, sp = math.cos(phi), math.sin(phi)
    dx, dy = (p0[0] - e[0]) / 2, (p0[1] - e[1]) / 2
    x1, y1 = cp * dx + sp * dy, -sp * dx + cp * dy
    lam = x1 * x1 / (rx * rx) + y1 * y1 / (ry * ry)
    if lam > 1.0:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1 * y1 - ry * ry * x1 * x1
    co = math.sqrt(max(0.0, num / (rx * rx * y1 * y1 + ry * ry * x1 * x1)))
    if large == sweep:
        co = -co
    cx1, cy1 = co * rx * y1 / ry, -co * ry * x1 / rx
    cx, cy = cp * cx1 - sp * cy1 + (p0[0] + e[0]) / 2, sp * cx1 + cp * cy1 + (p0[1] + e[1]) / 2
    ux, uy, vx, vy = (x1 - cx1) / rx, (y1 - cy1) / ry, (-x1 - cx1) / rx, (-y1 - cy1) / ry
    t1 = math.atan2(uy, ux)
    dt = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
    if sweep and dt < 0:
        dt += 2 * math.pi
    elif not sweep and dt > 0:
        dt -= 2 * math.pi
    r = max(rx, ry)
    n = max(1, math.ceil(abs(dt) / (2 * math.acos(max(-1.0, 1 - tol / r)))))
    out = []
    for k in range(1, n + 1):
        t = t1 + dt * k / n
        out.append((cx + rx * math.cos(t) * cp - ry * math.sin(t) * sp, cy + rx * math.cos(t) * sp + ry * math.sin(t) * cp))
    out[-1] = e
    return out
