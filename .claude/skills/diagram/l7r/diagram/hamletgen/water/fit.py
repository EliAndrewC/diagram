"""STAGE 2's SOLVER - the size search that lands the acreage the households need, and the fan-legality predicates it scores with.

Split from `hamletgen/water.py` by feature 230 (constitution X clause 13); bodies verbatim.
See `CLAUDE.md` in this directory.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

from l7r.diagram.sitegen.geom import SQ_FT_PER_ACRE
from l7r.diagram.waterfields import CombCarve, carve_comb, finish_comb

from ..consts import (
    BROOK_FAN_TRIM,
    FAN_ASPECTS,
    GRAIN,
    REF_CANAL_A,
    REF_CANAL_B,
    REF_FIELD_FALL,
    Pt,
)
from ..plan import SitePlan, _roll

# ---- STAGE 2: the field the water shapes --------------------------------------------------------


def fit_field(plan: SitePlan, sluice: Pt, seed: int, plot_across: float, row_step: tuple[float, float], tolerance: float = 0.06, rounds: int = 9) -> dict[str, Any]:
    """SOLVE the comb for the acreage the household count demands, instead of guessing a fall length.

    `build_comb` takes a `field_fall` in PIXELS, and the relationship between that number and the
    acreage that comes out is not analytic - the carve drops sectors too narrow to plant, the fan's
    width follows the canal lengths, and the envelope's shape depends on where the threads clamp. An
    author picks a number, looks at the render, and adjusts; Ikegami's 1150 is such a number, and it
    lands 24% under the acreage its own docstring asks for.

    A script does not have to guess. `carve_comb` is pure and deterministic, so this bisects a
    single SIZE multiplier - applied to the fall length AND both canal lengths together, so the fan
    scales without changing shape - until the drawn plot area is within `tolerance` of the target.
    Returns the best net found, which is the one whose acreage is closest, not merely the last.

    THE SEARCH CARVES; ONLY THE WINNER IS FINISHED (feature 220, GM 2026-09-09). Each guess used to
    run the whole `build_comb` - and seam closing, added after this docstring first promised a build
    "well under a second", had grown to two thirds of one: on the reference hamlet four full builds
    at 1.35 s each made a 5.4 s stage, three of them thrown away. The scorers below read only the
    carved plots and the channels, so each guess is a `carve_comb` (about a third of a build), the
    best carve is kept, and `finish_comb` runs once on it. The acreage each guess is scored on is the
    carve's PREDICTION of the finished acreage (`CombCarve.planted_area`: the plots plus the bare
    ground the seam pass will plant) - the carve alone under-reads it by the pockets, 11-21% on the
    reference fan, and a first cut that scored the bare carve overshot the target by 12% (specs/220
    research R2). The prediction is within 0.05% of the finish, so the search lands on the size the
    full build landed on; a map on which it does not is a map that moved, judged by the gate and a
    settlement-review like any other change.

    The multiplier is bracketed rather than solved because acreage is monotone in it but stepwise:
    a small change can add or drop a whole plot row, so the curve has small flats and the bisection
    is on a monotone-but-lumpy function. Nine rounds resolves the multiplier to ~0.3%, far finer
    than one plot row; the cost is the carves (specs/220 research R2 has the measured figure)."""
    best: tuple[tuple[bool, float], CombCarve] | None = None
    # THE ASPECT IS PART OF THE SEARCH, not just a roll. A fan's legality - whether its supply canal
    # dies among the plots, whether its collector folds back on itself - depends on its SHAPE as much
    # as its size, and a roll can land on an aspect at which no size is legal. So the rolled aspect
    # is tried first and the rest follow in order; the first legal fan wins, and if none is legal the
    # closest-on-acreage is kept so the failure is a gate message rather than an exception.
    best_aspect = plan.fan_aspect
    for aspect in [plan.fan_aspect] + [a for a in FAN_ASPECTS if a != plan.fan_aspect]:
        found = _fit_at_aspect(plan, sluice, seed, plot_across, row_step, aspect, tolerance, rounds)
        if best is None or found[0] < best[0]:
            best, best_aspect = found, aspect
        # a legal fan alone is not enough to stop the search: the supply-bank hem (2026-08-15)
        # drops the quads wedged between near-parallel channels, and on some seeds the first
        # LEGAL aspect leaves the acreage well short of the household target (cohort seed 44:
        # 11.0 against 13.0, past the 15% ratchet, with the gate itself green). Keep trying
        # aspects until one is legal AND lands the acreage; `best` already orders (illegal, err),
        # so a seed whose first legal aspect met tolerance breaks exactly where it always did and
        # every such map is byte-identical.
        if not found[0][0] and found[0][1] <= tolerance:
            break
    assert best is not None
    if best[0][0] or best[0][1] > tolerance:
        # NO ASPECT LANDED THE TARGET, so the probe that ended each saturated aspect after two carves
        # (see `_fit_at_aspect`) has left the best aspect less refined than the full search would - and
        # this is the map whose acreage the household ratchet will judge. Give that one aspect the full
        # search now; the cost is paid only on the maps that need it.
        again = _fit_at_aspect(plan, sluice, seed, plot_across, row_step, best_aspect, tolerance, rounds, probe=False)
        if again[0] < best[0]:
            best = again
    return finish_comb(best[1])  # ONE finish per roll: the seams closed, the dry plots laid, on the winner alone


def _fit_at_aspect(
    plan: SitePlan, sluice: Pt, seed: int, plot_across: float, row_step: tuple[float, float], aspect: float, tolerance: float, rounds: int, probe: bool = True
) -> tuple[tuple[bool, float], CombCarve]:
    """`fit_field`'s search at ONE fan aspect. Returns ((illegal, acreage error), the best CARVE).

    `probe`: when the first carve (k = 1) falls short, the second goes straight to the bracket's END
    - the largest fan this aspect can draw. If even that is short of the target by more than the
    tolerance, the aspect SATURATES (the envelope clamps the fan; cohort seed 47 sat at 16-17 acres
    against 19.5 at four of its five aspects, and burned nine carves at each proving it) and the
    search stops after those two carves, keeping the better. `fit_field` re-runs the best aspect
    with `probe=False` when no aspect lands the target, so the refinement is never lost on the map
    that needs it."""
    lo, hi = 0.35, 2.2
    best: tuple[tuple[bool, float], CombCarve] | None = None
    # PREDICT THE MULTIPLIER, THEN BRACKET IT (feature 145, GM 2026-08-28: "maps are now allowed to
    # move ... we should just go ahead and fix it"). The fan scales in both dimensions with k, so
    # its acreage goes roughly as k^2: from one carve the size that lands the target is
    # k * sqrt(target / acres), and from two carves a power law through both points is better
    # still. The bisection ignored that and halved the bracket blindly - seven carves of ~0.9 s to
    # find what the first carve already predicted to within a plot row. The bracket is kept and the
    # prediction is clamped INTO it (and falls back to the midpoint when it lands on a bracket end,
    # which is how a lumpy acreage curve is stopped from re-proposing the same k), so every guarantee
    # of the old loop holds: monotone narrowing, termination at `rounds`, the best legal net kept.
    # Measured on the reference (seed 4): 4 carves -> 2; the cohort's worst field seeds 7 -> 2-3.
    pts: list[tuple[float, float]] = []  # (k, acres) of every carve so far, for the power-law step
    _trim_a = BROOK_FAN_TRIM if plan.brook_side < 0 else 1.0
    _trim_b = BROOK_FAN_TRIM if plan.brook_side > 0 else 1.0
    # THE SLOWDOWN THIS FEATURE CARRIES, ITS CAUSE, AND THE LEVER THAT IS NOT PULLED (feature 230).
    # Cutting one flank's canal to `BROOK_FAN_TRIM` takes about (1 - trim) / 2 of the fan's area with it, so at
    # the same `k` a trimmed fan draws ~14% fewer acres and the bracket's ceiling comes down with it: seeds near
    # the acreage ceiling SATURATE at every aspect, the search spends two carves proving it at each, then re-runs
    # the best unprobed - 15 carves on cohort seed 25 against 3 before the feature.
    #
    # MEASURED ALTERNATELY with a detached worktree at the pre-feature commit, so the same machine load fell on
    # both (the GM asked whether the box was simply busy; it was not): baseline 27.9 / 28.3 / 28.4 s against this
    # feature's 35.6 / 36.3 s, about +27%, three rounds each, interleaved.
    #
    # THE LEVER: scaling the bracket by the area the trim removes (`lo, hi, k *= sqrt(2 / (1 + BROOK_FAN_TRIM))`)
    # is exact arithmetic rather than a tuning knob, and it MEASURED -3.6% - faster than the code before the
    # feature. It is not taken, because it changes the size every fan is fitted at, and the gate measured what
    # that costs at the fan's toe: one basin of 618 tapering below the 15 degree needle bar, and no flooded plot
    # painted at all on the reference roll, so the sheet loses the wet-paddy class it exists to exhibit. Both are
    # the closing rank coming out in slivers at the larger size. The fan's toe geometry is what a future feature
    # must fix first; until it does, the honest trade is the slower search and the sound field.
    k = 1.0
    for _ in range(rounds):
        k = min(max(k, lo + 1e-3), hi - 1e-3)
        carve = carve_comb(
            plan.W,
            plan.H,
            sluice,
            seed,
            down_deg=plan.down_deg,
            field_fall=REF_FIELD_FALL * k / aspect,
            # the fan is cut AWAY from the brook's flank (`BROOK_FAN_TRIM`): canal A hems the -1 side, canal B
            # the +1 side, so whichever of them faces the brook is the one that stops short of it
            canal_a_len=(REF_CANAL_A[0] * k * aspect * _trim_a, REF_CANAL_A[1] * k * aspect * _trim_a),
            canal_b_len=(REF_CANAL_B[0] * k * aspect * _trim_b, REF_CANAL_B[1] * k * aspect * _trim_b),
            offtakes_a=plan.offtakes_a,
            offtakes_b=plan.offtakes_b,
            plot_across=plot_across,
            row_step=row_step,
            grain_drift=plan.grain_drift,
            grain=GRAIN,
            head_deg=plan.head_deg,  # the race leaves the brook's bank at the offtake angle (feature 230), not straight down the fall
            head_len=plan.head_lead,
            supply_banks=True,  # bunds hem onto the supply strokes' banks (GM 2026-08-15); scripted tier only, see paddy_bunds_clear_the_supply_channels
        )
        net = carve.net  # the two keys the scorers read: the carved plots and the channels
        acres = carve.planted_area() * plan.ftpx * plan.ftpx / SQ_FT_PER_ACRE  # what the finish will plant, predicted (see `fit_field`); `net_acres`'s own conversion
        err = abs(acres - plan.target_acres) / plan.target_acres

        # A DANGLING CANAL TAIL disqualifies a fan before its acreage is even considered. Whatever
        # supply canal runs on past its last delivery ditch has to die among the plots it waters;
        # ending outside the planted extent is runoff dying in bare ground
        # (`watercourse_ends_reach_water`). The offtake ladder keeps the tail SHORT, but whether a
        # short tail lands inside depends on how wide the fan happens to be there - so the bisection
        # picks the best fan that is legal rather than the best fan and then hoping.
        score = (tail_dangles(net) or net_bends_acutely(net), err)
        if best is None or score < best[0]:
            best = (score, carve)
        if err <= tolerance and not score[0]:
            break
        if acres < plan.target_acres:
            lo = k
        else:
            hi = k
        pts.append((k, acres))
        # A COLLAPSED BRACKET IS AN ANSWER. Cohort seed 47 (2026-08-28): at four of its five aspects the fan
        # SATURATES - the envelope clamps it and the acreage sits at 16-17 against a 19.5 target however
        # large k gets - and the old loop spent its last four carves at k = 2.16, 2.18, 2.19, 2.195 drawing
        # the same 16.35 acres each time. A plot row is worth ~0.03 of k, so a bracket narrower than that
        # cannot change the fan; stop, keep the best, and let the next aspect have the time.
        if hi - lo < 0.03:
            break
        if probe and len(pts) == 1 and acres < plan.target_acres:
            k = hi - 1e-3  # the probe: the largest fan this aspect can draw
            continue
        # A SECOND SATURATION BREAK STOOD HERE AND WAS DEAD - the collapsed bracket above already does its
        # job (removed with the proof, feature 146). Both arrived together in 145. The probe sets
        # `k = hi - 1e-3`, so on the next round either the fan is still short of the target and `lo = k`
        # collapses the bracket to 1e-3 - caught by `hi - lo < 0.03` one line up - or it is not short, and
        # then the saturation test's own `acres < target * (1 - tolerance)` is false by construction.
        # There is no third case, which is why no seed ever entered it. The saving it was written for is
        # real and is being delivered; it is delivered by the line above.
        k = _predict_k(pts, plan.target_acres, lo, hi)
    assert best is not None
    return best


def _predict_k(pts: list[tuple[float, float]], target: float, lo: float, hi: float) -> float:
    """The next size multiplier to carve at: a power-law step through the last two (k, acres)
    points, a square-root step from one, the bracket's midpoint when the prediction is useless.

    Useless means: the two acreages coincide (a flat in the lumpy curve - no slope to follow), an
    acreage of zero (nothing carved), or a prediction outside the open bracket (the curve is not
    the power law where it matters, so the bracket's own halving takes over, exactly as before)."""
    (k1, a1) = pts[-1]
    if a1 <= 0:
        return (lo + hi) / 2.0
    if len(pts) >= 2 and pts[-2][1] > 0 and pts[-2][1] != a1 and pts[-2][0] != k1:
        (k0, a0) = pts[-2]
        p = math.log(a1 / a0) / math.log(k1 / k0)  # the local exponent; ~2 for a fan scaling in both dimensions
        k = k1 * (target / a1) ** (1.0 / p) if 0.2 < p < 6.0 else k1 * math.sqrt(target / a1)
    else:
        k = k1 * math.sqrt(target / a1)
    return k if lo < k < hi else (lo + hi) / 2.0


HEAD_OFFSETS: tuple[tuple[str, float], ...] = (("head_left", -0.24), ("head_center", -0.05), ("head_center", 0.05), ("head_right", 0.24))


def head_sluice(plan: SitePlan) -> tuple[Pt, str]:
    """WHERE THE WATER REACHES THE FIELD - the intake, at the field's HIGH head.

    Gravity settles this: a comb is fed from its high end, so the sluice sits at the upslope end of
    the ground the field will occupy, and the only real freedom is WHICH point of that head margin -
    a brook coming down the left shoulder, the right, or straight into the middle.

    This is deliberately NOT the engine's `water_source_anchor`. That helper resolves the knob
    catalog's `edge_N`/`edge_W`-style positions against a canvas-relative box, so a lateral entry
    (`edge_W` on a south-falling map) lands at the box's MID-height: legal by the gravity test, but
    it leaves the fan only half the canvas to run down, and the field then saturates far under the
    acreage the household count needs. That was the first real bug in this experiment and it is the
    kind a map-by-map author never meets, because they pick the number that makes the picture work.
    Anchoring on the fall axis instead makes the intake a consequence of the slope, which is what it
    is in the world."""
    dx, dy = plan.fall
    cx, cy = plan.W / 2.0, plan.H / 2.0
    px, py = -dy, dx  # across the fall
    name, lateral = _roll(plan.spec.seed, "head_offset", HEAD_OFFSETS)
    span = float(min(plan.W, plan.H))
    return (cx - dx * span * 0.36 + px * span * lateral, cy - dy * span * 0.36 + py * span * lateral), str(name)


def tail_dangles(net: Mapping[str, Any], margin: float = 18.0) -> bool:
    """Does any supply-canal end fall outside the fan's planted extent? See `fit_field`."""
    xs = [v[0] for p in net["plots"] for v in p["poly"]]
    ys = [v[1] for p in net["plots"] for v in p["poly"]]
    if not xs:
        return True
    x0, y0, x1, y1 = min(xs) - margin, min(ys) - margin, max(xs) + margin, max(ys) + margin
    # ONLY the supply canals ("main"), and only their FREE ends.
    #
    # Two exclusions, and both were learned by getting them wrong. The DRAIN's downstream end is
    # SUPPOSED to sit outside the crop - it is the outfall, and the brook or the tameike ditch
    # attaches to it there. And a main's UPSTREAM end is the head sluice or a junction with the
    # previous main, which is also outside the plots by construction: testing it made this return
    # True for every fan ever built, which turned the disqualifier off while leaving it looking like
    # it worked, and quietly cost five times the generation work for nothing.
    #
    # A free end is one no other main starts or ends at.
    ends = [q for c in net["channels"] if c["role"] == "main" for q in (c["pts"][0], c["pts"][-1])]
    free = [q for q in ends if sum(1 for r in ends if math.hypot(q[0] - r[0], q[1] - r[1]) < 5.0) == 1]
    return any(not (x0 <= q[0] <= x1 and y0 <= q[1] <= y1) for q in free[1:])  # [1:] drops the head intake, which is always outside the plots


def net_bends_acutely(net: Mapping[str, Any]) -> bool:
    """Does any channel in the fan fold back through less than 90 degrees?

    `water_channels_obtuse_turns` forbids it - a dug ditch does not make a hairpin - and the fan's
    own collector occasionally produces one at a particular size. Disqualifying the candidate is far
    cheaper than trying to repair the geometry afterwards, and `fit_field` has eight other fans to
    choose from."""
    for c in net["channels"]:
        pts = c["pts"]
        for i in range(1, len(pts) - 1):
            ax_, ay_ = pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]
            bx_, by_ = pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]
            la, lb = math.hypot(ax_, ay_), math.hypot(bx_, by_)
            if la >= 3 and lb >= 3 and (ax_ * bx_ + ay_ * by_) / (la * lb) < 0.0:
                return True
    return False
