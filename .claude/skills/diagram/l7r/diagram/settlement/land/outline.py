"""A MARSH'S NATURAL OUTLINE (feature 299): rounded corners and a slow irregular wave along its edges.

The wet-toe band is laid as straight strips (`toe_band`, the hinterland's ring strips), so a marsh met the scrub on a ruled line
and stopped at right-angled corners - which feature 298's hard-edged reed tile showed, where the old reed scatter had thinned out
over its last 46 ft and hidden it. The GM (2026-10-01): the boundary "is just a straight line which is not how that would actually
look", and at a corner "It would be more like a rounded curve". A MAP DRAWING CONVENTION: the laid band is this engine's
construction, not a finding, and the shaping is how a mapmaker draws wet ground.

THE SHAPING ONLY TAKES GROUND AWAY. The outline is rounded by an inward-then-outward buffer (which rounds the convex corners and
adds nothing) and waved by moving each point of it INWARD by a depth that rises and falls along the edge; the result is cut to
the rounded outline. So the shaped marsh lies within the laid one, and every rule that reads the marsh - a lane's end off it, a
house off it, its no-build ground - holds as before; the scrub fills what the marsh gives up."""

from __future__ import annotations

import math
from typing import Any

#: The corner rounding's radius in feet (x the map's `bscale`), halved until the rounding keeps `ROUND_KEEP` of the area - a
#: band narrower than twice the radius would vanish under it. Calibrated by eye on Inashiro's toe (the GM's "a rounded curve"):
#: 60 ft reads as a curve at fit zoom on a marsh some 1,300 ft across.
ROUND_FT = 60.0
ROUND_KEEP = 0.85
#: The wave's deepest bite in feet (x bscale) and the range of its three lengths along the edge: a slow wave, not a fringe -
#: deep enough to break a ruled line at fit zoom (25 ft read as nearly straight on Inashiro's toe, 2026-10-01), long enough not
#: to read as a scallop.
WAVE_DEPTH_FT = 40.0
WAVE_LENGTH_FT = (180.0, 480.0)
#: The wave's three components: a LEAD of length 180-240 ft weighted 2, and two slower ones of 240-480 ft weighted 0.5 each for
#: the irregularity. Three equal components rolled anywhere in the range could all come out long or cancel each other, and a
#: slow sine near its inflection lies within the 1 ft simplify of a straight line for 150 ft and more: Inashiro's toe, regenerated
#: under feature 302, drew a 165 ft ruled stretch on its left edge. Measured on that laid marsh over 200 seeds (2026-10-01): the
#: longest straight chord on open ground was 312 ft with three equal components (75 seeds over the 120 ft bar, two thirds of the
#: shortest length), 225 ft with all three in 180-300 ft, and 113 ft with this lead (none over) - the lead's own bend over any
#: 120 ft window, half its length at most, is more than the slower two can straighten.
WAVE_LEAD_FT = 240.0
WAVE_WEIGHTS = (2.0, 0.5, 0.5)
#: The spacing of the points the wave moves (a dozen to the shortest wave), and the tolerance the waved outline is simplified to:
#: every reader of the marsh walks its ring - the title pocket's box test point by point - and at 8 ft unsimplified a large
#: marsh carried about a thousand vertices where its laid strips had a handful, which made Sawada's ground-cover stage 0.45 ->
#: 0.8-1.1 s (2026-10-01, `stagemin.sh` and the wall-clock sampler: the title pocket's `point_in_poly`).
WAVE_STEP_FT = 15.0
SIMPLIFY_FT = 1.0


def natural_outline(poly: Any, seed: int, bs: float = 1.0) -> list[tuple[float, float]]:
    """`poly`'s outline rounded and waved - within `poly` (the module's note). The wave's three lengths and phases are rolled from
    `seed` (a lead and two slower ones, `WAVE_LEAD_FT`); each length is fitted to a whole number of waves round the outline, so it closes without a step. Returns the shaped
    exterior, or `poly` itself where shapely cannot read it as an area."""
    import numpy as np
    from shapely.geometry import Polygon
    from shapely.geometry.polygon import orient

    pts = [(float(q[0]), float(q[1])) for q in poly]
    laid = _largest(Polygon(pts).buffer(0)) if len(pts) >= 3 else None
    if laid is None:
        return pts
    rounded = laid
    r = ROUND_FT * bs
    while r >= 5.0 * bs:
        trial = _largest(laid.buffer(-r, quad_segs=8).buffer(r, quad_segs=8))
        if trial is not None and trial.area >= ROUND_KEEP * laid.area:
            rounded = trial.intersection(laid)
            rounded = _largest(rounded) or laid
            break
        r /= 2.0
    ring = orient(rounded, sign=1.0).exterior  # counter-clockwise: the inward normal is the tangent turned left
    length = ring.length
    n = max(12, int(length / (WAVE_STEP_FT * bs)))
    s = np.linspace(0.0, length, n, endpoint=False)
    xy = np.array([ring.interpolate(float(v)).coords[0] for v in s])
    rng = np.random.default_rng(seed)
    wave = np.zeros(n)
    lengths = np.array([rng.uniform(WAVE_LENGTH_FT[0], WAVE_LEAD_FT), *rng.uniform(WAVE_LEAD_FT, WAVE_LENGTH_FT[1], 2)]) * bs
    for wl, ph, wt in zip(lengths, rng.uniform(0.0, 2.0 * math.pi, 3), WAVE_WEIGHTS, strict=True):
        k = max(1, round(length / wl))  # whole waves round the ring: it closes without a step
        wave += wt * np.sin(2.0 * math.pi * k * s / length + ph)
    depth = WAVE_DEPTH_FT * bs * (0.5 + 0.5 * wave / sum(WAVE_WEIGHTS))
    tangent = np.roll(xy, -1, axis=0) - np.roll(xy, 1, axis=0)
    norm = np.hypot(tangent[:, 0], tangent[:, 1])
    norm[norm == 0.0] = 1.0
    inward = np.stack([-tangent[:, 1], tangent[:, 0]], axis=1) / norm[:, None]
    waved = _largest(Polygon((xy + inward * depth[:, None]).tolist()).buffer(0).intersection(rounded))
    shape = waved if waved is not None and waved.area >= 0.5 * rounded.area else rounded
    shape = _largest(shape.simplify(SIMPLIFY_FT * bs, preserve_topology=True)) or shape
    return [(round(x, 1), round(y, 1)) for x, y in list(shape.exterior.coords)[:-1]]


def _largest(g: Any) -> Any:
    """The largest polygon of `g`, or None where it has no area."""
    parts = [p for p in getattr(g, "geoms", [g]) if p.geom_type == "Polygon" and not p.is_empty and p.area > 0.0]
    return max(parts, key=lambda p: p.area) if parts else None
