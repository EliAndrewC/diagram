"""The hill-rice field engines - contour terraces and the ribbon valley (feature 145: moved out of polder.py, whose dike-and-drain builder the hamlet path executes; FIELD_ARCHETYPES deliberately holds neither of these, consts.py)."""

import math
import random
from typing import Any

from .banks import hem_to_bank, round_channel_joints
from .frame import Poly, Pt, _poly_area
from .palette import FLOODED, PADDY_CELL_ACRES, RICE_GREENS


def build_terraces(
    W: float,
    H: float,
    top: Pt,
    seed: int,
    down_deg: float = 90,
    n_terraces: int = 32,
    cross_width: float = 820,
    fall: float = 1500,
    ftpx: float = 1.0,
    cell_acres: float = PADDY_CELL_ACRES,
) -> dict[str, Any]:
    """Contour TERRACES (梯田): stacked thin paddies following the hillside contours, stepping downhill from
    `top` (the high catchment where water enters). Each terrace step is a gently curved band PERPENDICULAR to
    the fall, itself SPLIT ALONG THE CONTOUR into individual leveled cells; a supply channel runs down one
    flank and the stack cascades to a drain at the foot. Returns the same keys as `build_comb` so
    `Settlement.draw_comb_field` can draw it, plus `bund_lines` (the retaining-wall lip at each terrace's
    downhill edge, drawn by the gen). China-first grounding (research.md D4): the south-China / SE-Asia rice
    terrace (Yuanyang 元陽, Longsheng 龍勝) is THE field archetype for HILL ground.

    CELL SIZE (GM 2026-07-22): a terrace step is a ROW of SEPARATE small leveled paddies of varying size, NOT
    one field-wide band - a terrace paddy is a leveled cell like any other and the leveled-cell principle
    (water held even) makes it SMALL. Grounding: at Longsheng the LARGEST terrace is 0.62 mu (~0.10 acre) and
    most are far smaller (some hold three rice plants), 15,862 terraces in one village. So each step is split
    along the contour into cells of ~`cell_acres` (the universal PADDY_CELL_ACRES target, derived at this
    map's `ftpx`), and `n_terraces` is set so the step DEPTH stays shallow enough that a cell reads wider than
    deep (a terrace runs long along the contour, short down the fall). See settlements.md 'Paddy cell size'."""
    R = random.Random(seed)
    dx, dy = math.cos(math.radians(down_deg)), math.sin(math.radians(down_deg))  # downhill unit
    ux, uy = -dy, dx  # cross-slope (contour) unit
    hw = cross_width / 2
    step = fall / n_terraces
    plots: list[dict[str, Any]] = []
    bund_lines: list[Poly] = []

    def contour_pt(s: float, amp: float, phase: float, t: float) -> Pt:
        # a point on the contour at downhill distance s and cross-slope parameter t in [-1, 1], curved by a
        # gentle sine (organic terracing); the hillside narrows slightly downhill (a spur), width tapers with s
        w = hw * (1.0 - 0.12 * s / fall)
        base = s + amp * math.sin(phase + t * math.pi * 1.15)
        return (top[0] + dx * base + ux * (t * w), top[1] + dy * base + uy * (t * w))

    def contour(s: float, amp: float, phase: float, n: int = 14) -> Poly:
        return [contour_pt(s, amp, phase, -1.0 + 2.0 * k / n) for k in range(n + 1)]

    # per-boundary curve params (adjacent terraces SHARE a boundary, so there is no gap between them)
    b_par = [(16.0 + R.uniform(-4, 7), R.uniform(0, 2 * math.pi)) for _ in range(n_terraces + 1)]
    # cell width along the contour, from the real-feet cell target and the step DEPTH (converted at ftpx):
    # a cell is cell_acres = cell_across x step, so cell_across = area / step (floored so a shallow step still
    # yields a sane count)
    cell_across = max(24.0, cell_acres * 43560.0 / (ftpx * ftpx) / step)
    for i in range(n_terraces):
        a_up, p_up = b_par[i]
        a_lo, p_lo = b_par[i + 1]
        s_up, s_lo = i * step, (i + 1) * step
        w_lo = hw * (1.0 - 0.12 * s_lo / fall)
        ncell = max(3, round(2 * w_lo / cell_across))  # this step's cell count, from its (tapered) width
        # split points across the contour (t in [-1, 1]); interior positions JITTERED so terraces vary in size
        ts = [-1.0] + [(-1.0 + 2.0 * k / ncell) + R.uniform(-0.7, 0.7) / ncell for k in range(1, ncell)] + [1.0]
        low = i >= n_terraces - 3  # the low terraces sit wettest - the topography, not the tint (feature 010)
        for k in range(ncell):
            t0, t1 = ts[k], ts[k + 1]
            poly = [contour_pt(s_up, a_up, p_up, t0), contour_pt(s_up, a_up, p_up, t1), contour_pt(s_lo, a_lo, p_lo, t1), contour_pt(s_lo, a_lo, p_lo, t0)]
            fill = FLOODED if low else R.choice(RICE_GREENS)
            plots.append({"poly": [(round(x, 1), round(y, 1)) for x, y in poly], "fill": fill, "low": low})
        bund_lines.append([(round(x, 1), round(y, 1)) for x, y in contour(s_lo, a_lo, p_lo)])  # the retaining lip at each terrace's low edge (full contour)

    # envelope: the two flank edges + the top and bottom contours (the outer boundary of the whole stack)
    top_c = contour(0.0, 22.0, 0.0)
    bot_c = contour(fall, 22.0, 0.0)
    envelope = [*top_c, *reversed(bot_c), top_c[0]]
    # a supply canal runs DOWN the high (t=-1) flank, then TURNS INTO the field foot (so its tail sits inside the
    # terraces and the source->field feed anchors); a drain collects along the foot and DESCENDS to the low-flank
    # outfall (so it flows downhill); a brook carries the drain off-map continuing the drain's own heading.
    # a gentle diagonal supply: from the sluice (high-west shoulder) descending toward the field-center foot, so
    # its fork sits INSIDE the terraces (the source->field feed anchors) with no hairpin turn
    n_sup = 8
    flank = []
    for k in range(n_sup + 1):
        f = k / n_sup
        s_pos = fall * 0.9 * f
        lat = -hw * 0.92 * (1.0 - f * 0.8)  # from the west flank toward the center as it descends
        flank.append((top[0] + dx * s_pos + ux * lat, top[1] + dy * s_pos + uy * lat))
    # the drain is a STRAIGHT descending collector along the foot (a straight amp=0 contour, not the wiggly
    # terrace bottom - following the sine would hairpin), sloping steadily to the low-flank outfall, then turning
    # downhill so the brook continues without an acute bend
    foot = contour(fall, 0.0, 0.0)  # (drain widens downstream below - the collector gathers; GM 2026-07-23)
    fe, fw = foot[0], foot[-1]  # east / west foot ends
    n_d = 8
    drain_pts = []
    for k in range(n_d + 1):
        f = k / n_d
        x = fe[0] + (fw[0] - fe[0]) * f + dx * 40 * f
        y = fe[1] + (fw[1] - fe[1]) * f + dy * 40 * f
        drain_pts.append((round(x, 1), round(y, 1)))
    drain_pts.append((round(drain_pts[-1][0] + dx * 66, 1), round(drain_pts[-1][1] + dy * 66, 1)))  # the outfall TURNS DOWNHILL
    sluice = flank[0]
    channels = [
        {"pts": [(round(x, 1), round(y, 1)) for x, y in flank], "role": "main", "w": 6.0, "w_tail": 3.0},
        {"pts": drain_pts, "role": "drain", "w": 1.5, "w_tail": 5.0},  # gathers fe -> fw: a THREAD at its head (see build_comb's drain), full at the low-flank outfall
    ]
    brook = [drain_pts[-1], (round(drain_pts[-1][0] + dx * 300, 1), round(drain_pts[-1][1] + dy * 300, 1))]  # straight downhill off-map
    # the toe stops at the ditch's BANK: the last terrace's low edge is a WIGGLY contour and the
    # collector along the foot is a STRAIGHT descending line, so they cross unless held apart. The
    # retaining LIP goes through the same pass - it is the thick brown line a reader actually sees,
    # and on Tanada it was the one standing in the drain (see `hem_to_bank`).
    for p in plots:
        p["poly"] = hem_to_bank(p["poly"], drain_pts, down_deg, 1.5, 5.0)
    bund_lines = [hem_to_bank(bl, drain_pts, down_deg, 1.5, 5.0) for bl in bund_lines]
    acres = sum(_poly_area(p["poly"]) for p in plots) * 4 / 43560
    round_channel_joints(channels)  # earthen water turns on a swept bend, not a mitred corner
    return {
        "channels": channels,
        "plots": plots,
        "threads": [],
        "drain": drain_pts,
        "brook": brook,
        "envelope": [(round(x, 1), round(y, 1)) for x, y in envelope],
        "acres": acres,
        "dry_plots": [],
        "dry_acres": 0.0,
        "bund_beans": [],
        "bund_lines": bund_lines,
        "furrows_vary": False,
        "sluice": (round(sluice[0], 1), round(sluice[1], 1)),
    }


def build_ribbon(
    W: float,
    H: float,
    top: Pt,
    seed: int,
    down_deg: float = 90,
    length: float = 1900,
    width: float = 300,
    n_bands: int = 48,
    ftpx: float = 1.0,
    cell_acres: float = PADDY_CELL_ACRES,
) -> dict[str, Any]:
    """RIBBON VALLEY (谷地田 / a narrow valley-floor strip): a long, NARROW paddy strung along a MEANDERING
    valley floor, the field archetype for a confined valley where the flat ground is only a thin winding
    ribbon beside the brook. Returns build_comb-compatible keys. China-first grounding (research.md D4): the
    valley-bottom rice ribbon of hill country - the brook runs down the center, paddy bands flank it, and the
    whole strip WANDERS with the valley (the distinguishing read against the broad comb fan or the polder).

    CELL SIZE (GM 2026-07-22): the valley floor steps down in cross-bunds AND is split across its width into
    individual leveled cells - a ribbon paddy is a leveled cell like any other (the same small ~`cell_acres`
    as a comb or terrace paddy; a hill valley floor cannot hold one field-wide sheet level over any slope).
    `n_bands` sets the cross-bund (down-valley) step and the width is split into cells of that target, derived
    at this map's `ftpx`. See settlements.md 'Paddy cell size'."""
    R = random.Random(seed)
    dx, dy = math.cos(math.radians(down_deg)), math.sin(math.radians(down_deg))
    ux, uy = dy, -dx
    hw = width / 2
    step = length / n_bands
    amp = width * 0.62  # how far the valley meanders laterally
    wl = length / 2.4  # meander wavelength
    ph = R.uniform(0, 2 * math.pi)

    def cline(s: float) -> float:  # lateral offset of the valley center at downhill s (the meander)
        return amp * math.sin(ph + s / wl * 2 * math.pi)

    def edge(s: float, side: float) -> Pt:
        lat = cline(s) + side * hw * (0.9 + 0.2 * math.sin(s / 90.0))
        return (top[0] + dx * s + ux * lat, top[1] + dy * s + uy * lat)

    # each down-valley band is split ACROSS the width into cells of ~cell_acres (cell_across = area / step),
    # so the ribbon reads as a chain of small leveled paddies, not one long field-wide sheet
    cell_across = max(24.0, cell_acres * 43560.0 / (ftpx * ftpx) / step)
    plots: list[dict[str, Any]] = []
    for i in range(n_bands):
        s0, s1 = i * step, (i + 1) * step
        ncell = max(2, round(width / cell_across))  # cells across this band
        sides = [-1.0] + [(-1.0 + 2.0 * k / ncell) + R.uniform(-0.6, 0.6) / ncell for k in range(1, ncell)] + [1.0]
        low = i >= n_bands - 3  # the lowest bands down the valley floor (feature 010)
        for j in range(ncell):
            c0, c1 = sides[j], sides[j + 1]
            quad = [edge(s0, c0), edge(s0, c1), edge(s1, c1), edge(s1, c0)]
            fill = FLOODED if low else R.choice(RICE_GREENS)
            plots.append({"poly": [(round(x, 1), round(y, 1)) for x, y in quad], "fill": fill, "low": low})
    left = [edge(i * step, -1) for i in range(n_bands + 1)]
    right = [edge(i * step, 1) for i in range(n_bands + 1)]
    envelope = [*left, *reversed(right), left[0]]
    # the valley BROOK runs down the meandering center (the source: a stream, entering at the high end); a drain
    # continues it off-map at the foot. Supply is the brook itself, so the 'main' ditch traces the centerline.
    center = [(top[0] + dx * (i * step) + ux * cline(i * step), top[1] + dy * (i * step) + uy * cline(i * step)) for i in range(n_bands + 1)]
    flank = [
        (round(x, 1), round(y, 1)) for x, y in center[: n_bands // 2 + 1]
    ]  # the upper valley brook is the supply reach; its fork sits mid-valley so the source->field feed anchors INSIDE the ribbon
    # a short CROSS-SLOPE collector across the ribbon at the foot (perpendicular to the fall), then a downhill
    # outfall so the brook leaves smoothly (a valley ribbon still gathers its tail-water in a cross drain)
    foot = center[-1]
    drain_pts = [
        (round(foot[0] - ux * hw * 0.9, 1), round(foot[1] - uy * hw * 0.9, 1)),
        (round(foot[0], 1), round(foot[1], 1)),
        (round(foot[0] + ux * hw * 0.9, 1), round(foot[1] + uy * hw * 0.9, 1)),
    ]
    drain_pts.append((round(drain_pts[-1][0] + dx * 60, 1), round(drain_pts[-1][1] + dy * 60, 1)))
    sluice = flank[0]
    channels = [
        {"pts": flank, "role": "main", "w": 5.0, "w_tail": 3.0},
        {
            "pts": drain_pts,
            "role": "drain",
            "w": 1.5,
            "w_tail": 5.0,
        },  # gathers across the foot into the outfall at its FAR end (drain_pts runs near flank -> center -> far flank -> downhill stub, and the brook leaves from that stub), so the taper is monotone like every other collector: a thread where it starts, full where it discharges. (An older comment here claimed the outfall was central and the width therefore constant - the geometry above says otherwise.)
    ]
    brook = [drain_pts[-1], (round(drain_pts[-1][0] + dx * 300, 1), round(drain_pts[-1][1] + dy * 300, 1))]
    # the ribbon's bands end AT the foot, i.e. on the cross-drain's centerline - so its bottom bund
    # was drawn under the ditch. Hold the last band off to the bank (see `hem_to_bank`).
    for p in plots:
        p["poly"] = hem_to_bank(p["poly"], drain_pts, down_deg, 1.5, 5.0)
    acres = sum(_poly_area(p["poly"]) for p in plots) * 4 / 43560
    round_channel_joints(channels)  # earthen water turns on a swept bend, not a mitred corner
    return {
        "channels": channels,
        "plots": plots,
        "threads": [],
        "drain": drain_pts,
        "brook": brook,
        "envelope": [(round(x, 1), round(y, 1)) for x, y in envelope],
        "acres": acres,
        "dry_plots": [],
        "dry_acres": 0.0,
        "bund_beans": [],
        "furrows_vary": False,
        "sluice": (round(sluice[0], 1), round(sluice[1], 1)),
    }
