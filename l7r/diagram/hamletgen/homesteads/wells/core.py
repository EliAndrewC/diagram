"""The wells' constants and helpers, a row village's shared wells and the grove farms' water (split from `homesteads/wells.py` at
the 1,000-line bar, feature 444 T33).

Research: well arithmetic - NONE: distances, scores and ground tests; the units that decide carry their own claims
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement._geom.indexes import PointGrid
from l7r.diagram.settlement.shrines_wells.wells import well_gap_to_dwellings as well_gap_to_dwellings  # re-exported: the tests ask it here
from l7r.diagram.work_counts import OPS

from ...consts import Pt
from ...plan import SitePlan
from ..holds import release_held

_WELL_DRAWN_R = 12.376
"""The wellhead's DRAWN half-extent, used when asking how far a candidate seat would push the crop: the glyph's own `vr`
(`Settlement._well_vr`, the well-house roof's half-size, 12.376 ft on a to-scale map - the hamlet's 1 ft per px), not the
`r` clearance radius, because the frame follows the ink. `drawn_r` asks the glyph; this is its value where the
settlement is a stand-in that draws no well (feature 328: it was a separate 12, with a docstring saying 16 px across).

Research: wellhead drawn extent - CONVENTION: the glyph's 12.376 ft roof half-size, a marker larger than life (0196)
"""


def drawn_r(s: Any) -> float:
    """The wellhead's drawn half-extent on `s`: its glyph's `vr`, or `_WELL_DRAWN_R` on a stand-in with no glyph.

    Research: wellhead drawn extent - NONE: reads the glyph's `vr`, or the stand-in value
    """
    return float(s._well_vr()) if hasattr(s, "_well_vr") else _WELL_DRAWN_R


# THE AMONG-THE-DWELLINGS RULE lives with the wellhead (`settlement/shrines_wells/wells.py`: `WELL_AMONG_DWELLINGS_PX`,
# `well_gap_to_dwellings`, feature 287, homes H09); `seat_wells` asks it at each seat, against its own `gap` (feature 374 wave 154: the 80 ft seat, the 95 ft check)


def crop_box(s: Any, xs: Sequence[float], ys: Sequence[float]) -> tuple[float, float, float, float]:
    """The crop's predicted box (x0, x1, y0, y1): `_crop_boxes`, what `content_view` reads, or the house centers' box on a
    settlement that keeps none. Taken once per well landed by `seat_wells` (feature 387: 13,205 builds a roll, 11.8 s profiled).

    Research: the crop's box - NONE: `crop_extent_added`'s own reading, taken once"""
    boxes = s._crop_boxes(city=False) if hasattr(s, "_crop_boxes") else []
    return (
        min((b[0] for b in boxes), default=min(xs)),
        max((b[1] for b in boxes), default=max(xs)),
        min((b[2] for b in boxes), default=min(ys)),
        max((b[3] for b in boxes), default=max(ys)),
    )


def extent_past(box: tuple[float, float, float, float], r: float, c: Pt) -> float:
    """How far a wellhead of drawn radius `r` at `c` reaches past `box` (x0, x1, y0, y1) - 0 inside it.

    Research: past the crop - NONE: arithmetic; the rule is `crop_extent_added`'s"""
    bx0, bx1, by0, by1 = box
    return max(0.0, bx0 - (c[0] - r), (c[0] + r) - bx1, by0 - (c[1] - r), (c[1] + r) - by1)


WELL_SEAT_FT = 80.0
"""How near a dwelling's wall a communal well is seated: "the map places its wells a little closer than" the 95 ft check
(0196), so a seat the placer takes always passes the check with room (feature 374 wave 154).

Research: seated a little closer than the check - GUESS research/questions/0196-communal-wells-ido.drawing.html: "a little closer than" the 95 ft, 80 ft its calibration, a GUESS the page names"""

WELL_SERVES_MAX = 10
"""The most households one communal well is the nearest well to, where a seat keeps it so: "the five to ten houses that each
dug well served at Karihama" (0196).

Research: five to ten houses a well - research/questions/0196-communal-wells-ido.drawing.html: the five to ten houses each dug well served at Karihama"""


#: the old neighborhood ladder: the third-nearest house within 190, 300, 520 px, then two houses
THREE_THEN_TWO = ((190.0, 3), (300.0, 3), (520.0, 3), (520.0, 2))
"""Research: three, then two houses - GUESS research/questions/0196-communal-wells-ido.drawing.html: the cluster form's only where fewer than five households share a well, and the fallback's, as the page records; the lane-side form's neighborhood (no page gives one) and the 190/300/520 px reaches are this project's"""


def mark_form(s: Any, x: float, y: float, form: str) -> None:
    """Record on the well just drawn at (x, y) the form that seated it (feature 374 wave 154) - `pocket`, `cluster`, `lane`
    or `fallback` - where the manifest holds it.

    Research: a well's form recorded - NONE: the manifest's record of which form seated each well
        its salts, guards and sentinels - NONE: they decide nothing about the place - 0.06 (float tolerance, matching the well record)
    """
    for w in reversed((getattr(s, "M", None) or {}).get("wells") or []):
        if abs(float(w["x"]) - round(x, 1)) < 0.06 and abs(float(w["y"]) - round(y, 1)) < 0.06:
            w["form"] = form
            return


def grid_points(x0: float, x1: float, y0: float, y1: float, step: float) -> list[Pt]:
    """The lattice over a box, row by row, `step` apart (the sweep `seat_wells` offers by default).

    Research: well lattice - NONE: the sweep's own geometry"""
    out: list[Pt] = []
    y = y0
    while y <= y1:
        x = x0
        while x <= x1:
            out.append((x, y))
            x += step
        y += step
    return out


def first_share_middle(houses: Sequence[Mapping[str, Any]], n: int) -> Pt:
    """The middle of the first of `n` equal shares of `houses`, the shares cut along the cluster's long axis (the principal
    axis of the house centers): where the first of `n` wells stands so each later one, seated by the worst-served walk, takes
    a share of its own (feature 374 wave 155).

    Research: the first well at its share's middle - GUESS research/questions/0196-communal-wells-ido.drawing.html: five to ten houses a well at Karihama; the shares cut along the long axis are this project's choice, no page says how a hamlet's wells divided its houses"""
    xs, ys = [float(h["x"]) for h in houses], [float(h["y"]) for h in houses]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys, strict=True))
    th = 0.5 * math.atan2(2.0 * sxy, sxx - syy)
    along = sorted(zip(xs, ys, strict=True), key=lambda q: (q[0] - mx) * math.cos(th) + (q[1] - my) * math.sin(th))
    share = along[: max(1, round(len(along) / max(n, 1)))]
    return sum(q[0] for q in share) / len(share), sum(q[1] for q in share) / len(share)


def most_served_after(c: tuple[float, float, float], houses: Sequence[Mapping[str, Any]], wells: Sequence[Pt]) -> int:
    """How many households the busiest well is nearest to, once a well is dug at `c` (`c` = (_, x, y)).

    Research: households a well serves - NONE: each household counted to its nearest well"""
    pts = [*wells, (c[1], c[2])]
    count = [0] * len(pts)
    for h in houses:
        count[min(range(len(pts)), key=lambda i: math.hypot(h["x"] - pts[i][0], h["y"] - pts[i][1]))] += 1
    return max(count)


def well_target(households: int) -> int:
    """How many communal draw-wells a hamlet of this size keeps.

    One per ~6 households, but never past the two a hamlet draws: 0196's drawing page reads the 2-20 households a well
    serves at hamlet scale as "a hamlet draws one or two" (feature 328: the cap was 6, so 16-20 households drew three).

    Research: how many wells - research/questions/0196-communal-wells-ido.drawing.html: one per 6 households, one or two
    """
    return max(1, min(2, round(households / 6.0)))


def own_well_clear(s: Settlement, x: float, y: float, half: float, boxes: Sequence[tuple[float, float, float, float]]) -> bool:
    """May a farm's own wellhead of drawn half-size `half` stand at (x, y)? Tested by FOOTPRINT: its box a 2 ft gap off
    every reserved box (`boxes`: the placed boxes but the farm's own frame, and the grove bands), and the engine's own
    ground tests - no water, crop or bog (`_well_ground_clear`), no scrub cover, nothing blocked. `well_at` asks `_fits`,
    whose circumscribed circle round a 150 ft grove band covered most of the farm it shelters (Kashikawa: 0 wells).

    Research:
        its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 55 (wellhead kept off the sheet edges); 88 (wellhead kept off the sheet edges); 26 (wellhead kept off the sheet edges)
        its well gap - GUESS: searched, the record silent (feature 417 T38, 2026-10-25) - 2 (wellhead kept 2 ft off every reserved box)
    """
    if x < 55 or y < 88 or x > s.W - 55 or y > s.H - 26:
        return False
    if s._in_scrub_cover(x, y) or not s._well_ground_clear(x, y) or s._in_blocked(x, y):
        return False
    return not any(abs(x - bx) < half + bw / 2 + 2.0 and abs(y - by) < half + bh / 2 + 2.0 for bx, by, bw, bh in boxes)


WATER_REACH_FT = 760.0
"""The watering rule's reach (`surface_water_dist` against 760 ft, `place_wells` below; the gate's `WATER_REACH_FT`).

Research: watering reach - research/questions/0033-row-villages-resson.drawing.html, research/questions/0196-communal-wells-ido.drawing.html: 760 ft
"""


BEND_LOOK_FT = 40.0
"""How far along the street, either way, a shared well's mark looks for a bend (the law's zigzag run, `law.BEND_RUN_FT`).

Research: well arithmetic - GUESS: the bend rule's look-along; the 40 ft is the zigzag run of research/questions/0081-village-lanes.drawing.html
"""

BEND_WELL_DEG = 30.0
"""The street's turn, over `BEND_LOOK_FT` either way, past which no shared well is dug at a mark (feature 315): a GUESS, the
law's zigzag turn (50 degrees) less a margin, so a bend the street may yet be straightened through is left clear.

Research: well arithmetic - GUESS: no shared well where the street turns 30 degrees (a placement rule)
"""


def street_turns_at(line: Sequence[Pt], arc: Sequence[float], u: float, look: float) -> float:
    """How far, in degrees, the street `line` (its running lengths `arc`) turns on either side of the point `u` along it - the
    larger of its turn from `look` before to `u` and from `u` to `look` after. Either side alone, not end to end: a step in
    the street turns one way and back, and its two turns cancel between the far ends."""

    def heading(at: float) -> float:
        at = max(0.0, min(arc[-1], at))
        k = max(0, min(len(arc) - 2, next((j for j in range(len(arc) - 1) if arc[j + 1] >= at), len(arc) - 2)))
        a, b = line[k], line[k + 1]
        return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))

    def between(p: float, q: float) -> float:
        turn = abs(heading(q) - heading(p)) % 360.0
        return min(turn, 360.0 - turn)

    return max(between(u - look, u), between(u, u + look))


def shared_row_wells(s: Settlement, houses: Sequence[Mapping[str, Any]], streets: Sequence[Sequence[Pt]]) -> int:
    """A row village that shares its water (`row_water` shared, feature 291 plan D18): along each street, wells beside the
    street, one at the middle of each equal stretch of the row no longer than 1.6 reaches (the watering rule's reach), so
    every farm of every row stands within reach of one. A seat is tried at each mark and a half and a quarter lot either
    way, on either side of the tread. Returns the wells seated.

    Research:
        shared wells spaced - research/questions/0033-row-villages-resson.drawing.html: one at the middle of each stretch of at most 1.6 reaches
        beside the street - research/questions/0196-communal-wells-ido.drawing.html: the lane-side form, on the verge clear of the tread, either side
        off the tread - GUESS: the wellhead's half-extent and 8 ft off the street's centerline
        no well in a street bend - GUESS: no shared well at a mark where the street turns `BEND_WELL_DEG` (30 degrees) or more within `BEND_LOOK_FT` (40 ft, the zigzag run) on either side; no page gives a bend rule for wells
        fallback seats along the street - GUESS: a seat tried at the mark, then a half and a quarter lot either way along the street; no page gives the offsets
        a farm counted to each street within two farmstead frames - GUESS: every street within two frames of it, not only the nearest (`d <= 2.0 * frame_w`); no page gives how far a row's farm may stand from its street
        its figures from 0033 - research/questions/0033-row-villages-resson.drawing.html: 240 (fallback frame width)
    """
    if not streets or not houses:
        return 0
    half = s._well_vr()
    boxes = [(float(p[0]), float(p[1]), float(p[2]), float(p[3])) for p in s.placed] + [
        (float(g["x"]), float(g["y"]), float(g["w"]), float(g["h"])) for g in s.M.get("groves", []) if all(k in g for k in ("x", "y", "w", "h"))
    ]
    frame_w = max((max(float(b[2]), float(b[3])) for b in ((h.get("geom") or {}).get("bbox") for h in houses) if b), default=s.px(240.0))
    # ...EACH MARK'S SEATS IN RUST (feature 444 T33 D7b, `l7r_phases.row_wells`): the marks along each street and their tries a
    # half and a quarter lot either way, either side of the tread, off the street's bends; each asked here in that order
    from ...phases_ext import phases

    got = phases().row_wells(
        {
            "streets": [[(float(q[0]), float(q[1])) for q in line] for line in streets if len(line) >= 2],
            "farms": [(float(h["x"]), float(h["y"])) for h in houses],
            "frame": float(frame_w),
            "reach": float(s.px(WATER_REACH_FT)),
            "off": float(half + s.px(8.0)),  # off the street's tread, beside it
            "bend": (float(s.px(BEND_LOOK_FT)), float(BEND_WELL_DEG)),
        }
    )
    for k, c in got["counts"].items():  # the Rust's counted work on the stage's (feature 444 D5)
        OPS[k] += c
    n = 0
    for seats in got["marks"]:
        for x, y in seats:
            if __debug__:
                OPS["candidate@shared_row_wells"] += 1
            if own_well_clear(s, x, y, half, boxes):
                s.well(x, y)
                boxes.append((x, y, 2 * half, 2 * half))
                n += 1
                break
    return n


def grove_water(s: Settlement, plan: SitePlan, farms: Sequence[Mapping[str, Any]]) -> int:
    """Each grove farm's water, by its settlement's knob (feature 291 FR-018 and FR-019), from the well pocket its seating
    laid in its dooryard (`dispersed.canonical_farmstead`, feature 287's guarantee that a household is watered where it is
    seated): a row that SHARES its water digs wells beside its streets (`shared_row_wells`) and a dispersed farm on the
    CHANNEL form takes a channel into its grounds (`farm_channels`); a farm either serves releases its pocket, and every
    other farm draws its own well there. Returns the private wells drawn.

    Research:
        a row's water - research/questions/0033-row-villages-resson.drawing.html: shared wells along the streets, or a well at every farm
        a scattered farm's water - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: a channel, or its own well in its dooryard pocket
    """
    streets = getattr(s, "_row_streets", None) or []
    served: list[Mapping[str, Any]] = []
    if plan.settlement_form == "linear" and plan.row_water == "shared" and streets:
        shared_row_wells(s, farms, streets)
        reach = s.px(WATER_REACH_FT)
        shared = [(float(w["x"]), float(w["y"])) for w in s.M.get("wells") or [] if not w.get("private")]
        served = [h for h in farms if any(math.dist((float(h["x"]), float(h["y"])), q) <= reach for q in shared)]
    elif plan.settlement_form == "dispersed" and plan.farm_water == "channel":
        from ..farm_water import farm_channels  # local: it reads the ways' routing, a later layer

        dry = farm_channels(s, farms)
        served = [h for h in farms if h not in dry]
    s.M["meta"]["row_water_drawn"] = plan.row_water if plan.settlement_form == "linear" else None
    s.M["meta"]["farm_water_drawn"] = plan.farm_water if plan.settlement_form == "dispersed" else None
    n = 0
    for h in farms:
        pocket = h.get("well_pocket")
        if not pocket:
            continue
        release_held(s, "wells", float(pocket[0]), float(pocket[1]))
        if h not in served:
            s.well(float(pocket[0]), float(pocket[1]), private=True)
            n += 1
    return n


def watered_by_open_water(s: Settlement, houses: Sequence[Mapping[str, Any]], reach: float) -> list[bool]:
    """Is each house within `reach` of open water (`surface_water_dist <= reach`), each asked of the water's segments near it - a
    `PointGrid` of `water_lines`' segments built once - rather than of every segment (the appurtenances' fanout of 2026-11-06:
    82,496 distances for 40 houses).

    Research: plumbing - NONE: the same distances decide; the index leaves out the segments too far to"""
    from l7r.diagram.settlement.land.wet import surface_water_within, water_lines

    index = PointGrid()
    index.extend([(a, b, min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])) for ln in water_lines(s.M) for a, b in zip(ln, ln[1:], strict=False)])
    return [surface_water_within(s.M, float(h["x"]), float(h["y"]), reach, index) for h in houses]
