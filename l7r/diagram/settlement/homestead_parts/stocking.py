"""The windbreak's stocking rules: when a scatter of clumps stocks its ground, which clumps make the main stand, and the
box a grove records - split out of `stands.py` at the 1,000-line bar (feature 328).
Research: plumbing - NONE"""

import math
from collections.abc import Sequence
from typing import Any


def grove_stocked(clumps: Any, w: float, h: float, floor: float = 1.5) -> bool:
    """THE ONE PREDICATE of `test_every_recorded_grove_holds_trees` (feature 287, woods W15): a recorded grove holds at least
    `floor` clumps per 100,000 sq px of its recorded w x h - a grove that declares an extent and draws almost nothing in it
    leaves the dooryards it should have greened bare.
    Research: a recorded grove is stocked - UNRESEARCHED: at least 1.5 clumps per 100,000 sq px of its extent"""
    return w * h <= 0 or len(clumps) * 1e5 / (w * h) >= floor


def stocked_copse(clumps: list[tuple[float, float]], pad: float, kept: frozenset[tuple[float, float]] = frozenset()) -> list[tuple[float, float]]:
    """A copse's clumps with its stragglers dropped - the clump farthest from the clumps' centroid, one at a time - until the extent the copse is
    recorded at (its clumps' box grown by `pad`) is `grove_stocked` (feature 287, woods W15). It terminates: one clump's extent is a square of `2 * pad`,
    far above the floor. A clump in `kept` - a household's reserved share of the wood floor (woods W25) - is never a straggler: the drop stops when only kept clumps are left.
    Research:
        copse clumps farthest from the centroid dropped until stocked - UNRESEARCHED
        reserved share never a straggler - UNRESEARCHED: a household's reserved share of the wood floor (woods W25) is kept"""
    out = list(clumps)
    while len(out) > 1:
        xs, ys = [c[0] for c in out], [c[1] for c in out]
        if grove_stocked(out, max(xs) - min(xs) + 2 * pad, max(ys) - min(ys) + 2 * pad):
            break
        mx, my = sum(xs) / len(out), sum(ys) / len(out)
        loose = [k for k in range(len(out)) if out[k] not in kept]
        if not loose:
            break
        del out[max(loose, key=lambda k: math.hypot(out[k][0] - mx, out[k][1] - my))]
    return out


Box = tuple[float, float, float, float]


def grove_extent(clumps: Sequence[Sequence[float]], pad: float) -> Box:
    """The box (x0, y0, x1, y1) a grove's clumps span, grown by `pad` - the extent it is drawn at."""
    xs, ys = [float(c[0]) for c in clumps], [float(c[1]) for c in clumps]
    return (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)


def stocked_at_grain(clumps: Sequence[Sequence[float]], box: Box) -> bool:
    """`grove_stocked` over `box` as the record writes it (`record_box`: `w`, `h` to 0.1 px), so the rounding cannot tip a
    grove at the floor under it."""
    return grove_stocked(clumps, round(box[2] - box[0], 1), round(box[3] - box[1], 1))


def main_stand(clumps: Sequence[Sequence[float]], pad: float) -> list[Sequence[float]]:
    """The grove's MAIN STAND: its clumps split, while a part's extent (`grove_extent`) is not `grove_stocked`, across the
    widest gap along that extent's longer side, keeping the part with more clumps (the lower side on a tie). Terminates -
    each split keeps a nonempty proper part, and one clump's extent is a `2 * pad` square, far above the floor - and the
    part it returns is stocked in its own extent (feature 287, woods W15)."""
    part = list(clumps)
    while len(part) > 1:
        x0, y0, x1, y1 = grove_extent(part, pad)
        if stocked_at_grain(part, (x0, y0, x1, y1)):
            break
        k = 0 if x1 - x0 >= y1 - y0 else 1
        vals = sorted(float(c[k]) for c in part)
        cut = max(range(len(vals) - 1), key=lambda i: vals[i + 1] - vals[i])
        lo = [c for c in part if float(c[k]) <= vals[cut]]
        hi = [c for c in part if float(c[k]) > vals[cut]]
        part = lo if len(lo) >= len(hi) else hi
    return part


def stocked_box(clumps: Sequence[Sequence[float]], box: Box, pad: float) -> Box:
    """THE EXTENT A GROVE IS RECORDED AT, `grove_stocked` by construction (feature 287, woods W15 - the one predicate of
    `test_every_recorded_grove_holds_trees`): `box` where its clumps stock it - a windbreak's band, whose position is its
    meaning - else the extent its clumps are drawn at, else the extent of its main stand (`main_stand`), which its clumps
    stock since they include the stand's. A grove with no clump records no extent (a zero box at `box`'s center)."""
    if not clumps:
        cx, cy = (box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0
        return (cx, cy, cx, cy)
    if stocked_at_grain(clumps, box):
        return box
    ext = grove_extent(clumps, pad)
    if stocked_at_grain(clumps, ext):
        return ext
    return grove_extent(main_stand(clumps, pad), pad)


def record_box(g: dict[str, Any], box: Box) -> None:
    """Write `box` (x0, y0, x1, y1) into a grove record's `x`, `y`, `w`, `h`, at the record's grain."""
    g["x"], g["y"] = round((box[0] + box[2]) / 2, 1), round((box[1] + box[3]) / 2, 1)
    g["w"], g["h"] = round(box[2] - box[0], 1), round(box[3] - box[1], 1)
