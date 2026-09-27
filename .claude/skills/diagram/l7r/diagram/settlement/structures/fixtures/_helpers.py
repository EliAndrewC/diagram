"""Split from settlement/structures/fixtures.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
from typing import Any

# The lane clearance `place_kosatsuba` asks of the caption room beside a candidate board seat - a SITING heuristic
# (is there room for a caption here?), not a caption seat: the caption itself is seated by the one placer
# (feature 266), which scores a lane crossed within the gate's 2 ft notch at Esri's way weight.
CAPTION_LANE_TARGET_FT = 3.0

# THE BOARD IS ROADSIDE (GM 2026-08-26, feature 133 T13: *"I would expect it to be essentially
# roadside ... puts it right next to one of the village lanes"*). Real feet from the tread's EDGE to
# the board's near edge. Research (research/urban-features.html): the kosatsu stood where traffic
# passed - the village entrance, the roadside, a crossroads, a bridgehead, the headman's gate - so a
# board 24 ft off its lane (Inashiro before this) is set back from the very thing it is for. The
# placer searched out to 60 ft and ranked caption clearance above nearness, which is how it walked
# out. Now: at the hamlet and village tiers only seats inside this band are eligible when any fits
# (the 60 ft band remains the fallback, and `kosatsuba_by_the_road` tightens to this band at those
# tiers); towns and cities keep the 60 ft rule until their pool maps are re-rolled at unlock.
KOSATSUBA_VERGE_FT = 6.0

KOSATSUBA_ENTRANCE_REACH_FT = 100.0
"""How near a dwelling the approach must come before it counts as having ARRIVED at the settlement.

THE ENTRANCE IS THE FIRST BUILDINGS, NOT A RADIUS (settlement-review, feature 154). The first version
measured arrival against the cluster's own reach - the greatest distance from any house to the house
centroid - which is isotropic, and a settlement is not. On Sawada, a ribbon cluster of drawn aspect
4.06, that radius is set by the ribbon's HALF-LENGTH: 382 ft. The approach crossed that circle 148 ft
from the nearest house, out in the woodland and 3 ft above the top edge of the drawn sheet, so the
board was sited off the page, `stage_notice`'s frame guard threw the seat away, and the map recorded
an `entrance` placement it had not drawn.

100 ft is not a new figure: it is the reach `farmhouses_reach_a_way` uses to decide whether a dwelling
is served by a way at all. Where the approach first comes within serving distance of a house is where
a walker would say the hamlet begins, and it is the same measure the rest of the engine already makes."""

KOSATSUBA_ANCHOR_BAND_FT = 60.0
"""How far from the best seat at an anchored placement another seat may stand and still compete.

Not a new figure: it is `place_kosatsuba`'s own siting band, the ~60 real feet within which a board
counts as belonging to the way it stands on (`kosatsuba_by_the_road`'s fallback tolerance). Reused
here so an anchored placement admits the seats that genuinely front the entrance or the gate, and no
others, and then hands the choice to the caption and roadside preferences that already existed.
Making it TIGHTER would let a caption-blocked seat win on a foot of proximity; making it LOOSER would
let the traffic term drag the board off the anchor, which is the defect this feature exists to fix."""


def kosatsuba_affordances(M: Any) -> dict[str, bool]:
    """Which board placements this map can SITE, read from the manifest the validator reads.

    The same-source doctrine: a guard against a placement asks the question the checks ask. An
    approach is a recorded road or a connector track; an official's gate is a house carrying
    `role == "headman"`, which every pool VILLAGE records exactly once and no hamlet records at all.
    """
    lanes = M.get("lanes") or []
    has_approach = bool(M.get("road") or (M.get("roads") or []) or any(ln.get("connector") for ln in lanes))
    return {
        "has_approach": has_approach,
        "has_headman_house": any(h.get("role") == "headman" for h in (M.get("houses") or [])),
    }


def kosatsuba_anchor(M: Any, placement: str) -> tuple[float, float] | None:
    """The point an anchored placement is measured to, or None when the placement is not anchored.

    `center` returns None ON PURPOSE, and that is the whole reason this function has a null case: the
    settlement center IS the traffic objective - *"the village center ... or the place where villagers
    assembled"* - which `place_kosatsuba` already computes by counting dwellings around each seat, far
    better than a centroid would. Returning the centroid here would replace a measure of where people
    ARE with a measure of where the middle IS, and on a crescent or a ribbon cluster those are not the
    same point. So `center` keeps today's behavior byte for byte, and only the two placements that
    need a landmark get one.

    `entrance` is the MOUTH, not the nearest point: the approach is walked from its far end inward and
    the anchor is where it first reaches the cluster. Taking the nearest point instead would put the
    anchor at the deepest point of the track's run past the houses, i.e. inside the settlement, which
    is the opposite of an entrance.
    """
    houses = [(float(h["x"]), float(h["y"])) for h in (M.get("houses") or []) if "x" in h]
    if not houses or placement == "center":
        return None
    if placement == "frontage":
        gate = next((h for h in (M.get("houses") or []) if h.get("role") == "headman" and "x" in h), None)
        return (float(gate["x"]), float(gate["y"])) if gate else None

    def _at_the_buildings(q: tuple[float, float]) -> bool:
        """Has the approach arrived? Measured to the nearest DWELLING, never to a centroid radius."""
        return min(math.hypot(q[0] - h[0], q[1] - h[1]) for h in houses) <= KOSATSUBA_ENTRANCE_REACH_FT

    runs: list[list[tuple[float, float]]] = []
    if M.get("road"):
        runs.append([(float(p[0]), float(p[1])) for p in M["road"]])
    runs += [[(float(p[0]), float(p[1])) for p in (r.get("pts") or [])] for r in (M.get("roads") or [])]
    runs += [[(float(x), float(y)) for x, y in (ln.get("pts") or [])] for ln in (M.get("lanes") or []) if ln.get("connector")]
    best: tuple[float, tuple[float, float]] | None = None
    for run in runs:
        if len(run) < 2:
            continue
        # walk from whichever end is FURTHER out, so "first reach" means arriving rather than leaving
        _far = min(math.hypot(run[0][0] - h[0], run[0][1] - h[1]) for h in houses)
        _near = min(math.hypot(run[-1][0] - h[0], run[-1][1] - h[1]) for h in houses)
        walk = run if _far >= _near else run[::-1]
        # SAMPLED ALONG THE SEGMENTS, NOT AT THE VERTICES. A track is recorded with as few points as
        # its shape needs, so one that runs straight through the cluster can have no vertex inside it
        # at all - the first version of this tested vertices and returned "no entrance" for a
        # two-point track passing right through the houses, caught by its own unit test rather than by
        # a map, because the pool's connectors happen to be densely recorded.
        acc = 0.0
        for u, v in zip(walk, walk[1:], strict=False):
            seg = math.dist(u, v)
            steps = max(1, int(seg / 5.0))
            for k in range(1, steps + 1):
                q = (u[0] + (v[0] - u[0]) * k / steps, u[1] + (v[1] - u[1]) * k / steps)
                if _at_the_buildings(q) and (best is None or acc + seg * k / steps < best[0]):
                    best = (acc + seg * k / steps, q)
                    break
            if best is not None:
                break
            acc += seg
    return best[1] if best else None
