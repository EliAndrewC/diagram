"""How ruled is a marsh's VISIBLE free edge? (feature 294 B2, the review's "ruled or plumb edges on non-brook shapes" class)

The reviews found ruled and plumb marsh limits six times (features 133, 268, 279): a toe marsh meeting the scrub on a straight
line, axis-aligned edges of 450-590 ft. Feature 299 now rounds and waves the marsh's outline; this measures what a reader sees.
An edge counts where the page's id map (`interactive/raster.id_map`, the hover regions as drawn, which is how a marsh's reed
tile shows - its class group holds the tile's hit polygon) has the marsh on one side and nothing but open ground - the scrub,
the woods, bare land - for `FREE_REACH_FT` on the other: an edge that runs beside a dike, a field or a lane is that feature's
edge, drawn by it. The frame's own edge is not an edge of the marsh (`FRAME_PAD_FT`)."""

from __future__ import annotations

import io
import math
import re
from collections.abc import Mapping, Sequence
from typing import Any

#: the classes that are open ground beside a marsh (the id map's unpainted ground is open too)
OPEN_GROUND = frozenset({"scrub and rough grazing", "woodland commons", "copse", "windbreak"})
FREE_REACH_FT = 40.0  # GUESS: nothing but open ground this far beyond the edge, or it is another feature's edge
FRAME_PAD_FT = 12.0  # an edge this near the view's edge is the frame clipping the marsh
_STEP_FT = 2.0


def _sides(svg_text: str) -> tuple[Any, dict[str, int], tuple[float, float, float, float]] | None:
    import numpy as np
    from PIL import Image

    from l7r.diagram.interactive import raster

    keys = raster.class_keys(svg_text)
    vb = re.search(r'viewBox="([^"]+)"', svg_text)
    if not keys or not vb:
        return None
    png, palette = raster.id_map(svg_text, keys)
    if png is None:
        return None
    red = np.asarray(Image.open(io.BytesIO(png)).convert("RGBA"))[:, :, 0].astype(int)
    x0, y0, w, h = (float(v) for v in vb.group(1).split())
    return red, {v: int(k) for k, v in palette.items() if "," not in k}, (x0, y0, w, h)


def free_runs(svg_text: str, rings: Sequence[Sequence[Sequence[float]]], ftpx: float) -> list[list[list[tuple[float, float]]]] | None:
    """Per ring (a marsh record's outline): its stretches of VISIBLE FREE EDGE, each a list of points two feet apart along the
    ring. None without resvg or class groups."""
    got = _sides(svg_text)
    if got is None:
        return None
    red, by_key, (vx, vy, vw, vh) = got
    marsh = by_key.get("marsh")
    free = {0, -1} | {by_key[k] for k in OPEN_GROUND if k in by_key}

    def at(x: float, y: float) -> int:
        i, j = int(y - vy), int(x - vx)
        return int(red[i, j]) if 0 <= i < red.shape[0] and 0 <= j < red.shape[1] else -1

    pad, step = FRAME_PAD_FT / ftpx, _STEP_FT / ftpx
    out = []
    for ring in rings:
        pts = [(float(p[0]), float(p[1])) for p in ring]
        runs: list[list[tuple[float, float]]] = []
        cur: list[tuple[float, float]] = []
        for a, b in zip(pts, [*pts[1:], pts[0]], strict=True):
            length = math.dist(a, b)
            if length == 0:
                continue
            ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
            for k in range(int(length // step) + 1):
                px, py = a[0] + ux * k * step, a[1] + uy * k * step
                inside_frame = vx + pad < px < vx + vw - pad and vy + pad < py < vy + vh - pad
                left, right = at(px - uy * step, py + ux * step), at(px + uy * step, py - ux * step)
                out_dir = 1.0 if left == marsh else -1.0
                beyond = {at(px + out_dir * uy * d / ftpx, py - out_dir * ux * d / ftpx) for d in range(2, int(FREE_REACH_FT) + 2, 4)}  # the side away from the marsh
                if inside_frame and (left == marsh) != (right == marsh) and beyond <= free:
                    cur.append((px, py))
                    continue
                if len(cur) > 2:
                    runs.append(cur)
                cur = []
        if len(cur) > 2:
            runs.append(cur)
        out.append(runs)
    return out


def axis_run_ft(run: Sequence[tuple[float, float]], ftpx: float, eps_deg: float) -> float:
    """The longest stretch of `run` along which every step lies within `eps_deg` of ONE screen axis, in feet (a corner from one
    axis to the other ends the stretch)."""
    best = cur = 0.0
    last = None
    for a, b in zip(run, run[1:], strict=False):
        deg = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 180.0
        axis = "h" if min(deg, 180.0 - deg) < eps_deg else "v" if abs(deg - 90.0) < eps_deg else None
        cur = (cur if axis == last else 0.0) + math.dist(a, b) * ftpx if axis else 0.0
        last = axis
        best = max(best, cur)
    return best


def ruled_edges(runs: Sequence[Sequence[tuple[float, float]]], ftpx: float, rules: Mapping[str, float]) -> list[str]:
    """What breaks the rules over one marsh's free runs: the straightest run past `share` of the visible free edge once that
    edge is `min_len` long (the brook's W03, `straightest_run` at `tol`), and an axis-aligned stretch past `axis_run`."""
    from l7r.diagram.hamletgen.water.brook_rules import straightest_run

    total = sum(math.dist(a, b) for r in runs for a, b in zip(r, r[1:], strict=False)) * ftpx
    straight = max((straightest_run(list(r), rules["tol"] / ftpx) for r in runs), default=0.0) * ftpx
    axis = max((axis_run_ft(r, ftpx, rules["eps_deg"]) for r in runs), default=0.0)
    out = []
    if total >= rules["min_len"] and straight > rules["share"] * total:
        out.append(f"a straight run of {straight:.0f} ft on {total:.0f} ft of visible edge")
    if axis > rules["axis_run"]:
        out.append(f"{axis:.0f} ft of visible edge along a screen axis")
    return out
