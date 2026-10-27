"""Split from hamletgen/homesteads.py by feature 173 - see this package's CLAUDE.md for the index.

Research: well arithmetic - NONE: distances, scores and ground tests; the units that decide carry their own claims
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, seg_dist, surface_water_dist
from l7r.diagram.settlement._geom.indexes import PointGrid
from l7r.diagram.settlement._geom.primitives import points_in_poly, seg_dists
from l7r.diagram.settlement.homestead_parts.wood_share import ReservedSeats, well_keepout
from l7r.diagram.settlement.shrines_wells.wells import WELL_AMONG_DWELLINGS_PX
from l7r.diagram.settlement.shrines_wells.wells import well_gap_to_dwellings as well_gap_to_dwellings  # re-exported: the tests ask it here

from ..consts import WELL_VERGE_FT, Pt
from ..plan import SitePlan
from .holds import release_held
from .well_seats import PairAhead, PoolScore, SeatSweep, SeatTest, cells, discs_cover

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


def crop_extent_added(s: Any, c: Pt, xs: Sequence[float], ys: Sequence[float]) -> float:
    """How far past the crop's predicted box a wellhead at `c` (its drawn radius included) reaches - 0 inside it
    (feature 287, homes H12). The box is `_crop_boxes`, what `content_view` reads; a settlement that keeps none (a
    stand-in) is judged against the house centers' own box."""
    return extent_past(crop_box(s, xs, ys), drawn_r(s), c)


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


PAIR_LOOK = 40
"""How many of the seats nearest the first share's middle the first well's look ahead ranks (feature 374 wave 155): a
bound on the pairs it measures, the nearest 40 of a rung's few hundred seats.

Research: the look ahead's bound - GUESS: no source could speak to it, an algorithm's breadth of ours (feature 427 T06, 2026-10-26); the 40 seats nearest the first share's middle are the only ones re-ranked by whether a second well keeps both at ten, so it moves which seat the first of two wells takes"""


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


def worst_after(c: tuple[float, float, float], needy: Sequence[Mapping[str, Any]], standing: Sequence[float]) -> float:
    """The walk of the household WORST served once a well is dug at `c` - the minimax objective of the greedy
    pass in `place_wells`, lifted out (feature 223). `standing[i]` is needy house i's distance to its nearest
    well already standing, computed once per sort by the caller; the house's walk after the dig is the smaller
    of that and its distance to `c`, and the seat's score is the largest such walk."""
    return max(min(sd, math.hypot(h["x"] - c[1], h["y"] - c[2])) for h, sd in zip(needy, standing, strict=True))


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
    reach = s.px(WATER_REACH_FT)
    n = 0
    for line in streets:
        if len(line) < 2:
            continue
        arc = [0.0]
        for a, b in zip(line, line[1:], strict=False):
            arc.append(arc[-1] + math.dist(a, b))

        def along(p: Pt, _line: Sequence[Pt] = line, _arc: Sequence[float] = arc) -> tuple[float, float, Pt]:
            best = min(((seg_dist(p[0], p[1], a, b), i) for i, (a, b) in enumerate(zip(_line, _line[1:], strict=False))), key=lambda t: t[0])
            a, b = _line[best[1]], _line[best[1] + 1]
            seg = math.dist(a, b) or 1.0
            t = max(0.0, min(1.0, ((p[0] - a[0]) * (b[0] - a[0]) + (p[1] - a[1]) * (b[1] - a[1])) / (seg * seg)))
            q = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            return _arc[best[1]] + seg * t, best[0], q

        mine = sorted(((along((float(h["x"]), float(h["y"]))), h) for h in houses), key=lambda t: t[0][0])
        mine = [(u, h) for (u, d, _q), h in mine if d <= 2.0 * frame_w]
        if not mine:
            continue
        us = [u for u, _h in mine]
        # SPACED BY DISTANCE ALONG THE STREET, not by farms: a both-sided row has two farms at every step, and a stride in
        # farms dug a well at every one and a half lots (Kashikawa: 16 wells for 20 farms). The row is cut into equal
        # stretches no longer than 1.6 reaches and a well dug at each one's middle: every farm is then within 0.8 of a
        # reach of one along the street, the rest of the reach left for the lot's depth across it.
        span = us[-1] - us[0]
        stretches = max(1, math.ceil(span / (1.6 * reach)))
        for u in [us[0] + span * (j + 0.5) / stretches for j in range(stretches)]:
            for du in (0.0, frame_w / 2, -frame_w / 2, frame_w / 4, -frame_w / 4):
                uu = max(0.0, min(arc[-1], u + du))
                if street_turns_at(line, arc, uu, s.px(BEND_LOOK_FT)) >= BEND_WELL_DEG:
                    continue  # ...never in the street's bend (feature 315, cohort seed 903: a well in the inside of a step in the
                    # street held the street to its two right-angle turns, a kink on a tree lane, and the web was refused)
                k = max(0, min(len(arc) - 2, next(j for j in range(len(arc) - 1) if arc[j + 1] >= uu)))
                a, b = line[k], line[k + 1]
                seg = math.dist(a, b) or 1.0
                f = (uu - arc[k]) / seg
                p = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
                nx, ny = -(b[1] - a[1]) / seg, (b[0] - a[0]) / seg
                seated = False
                for sgn in (1.0, -1.0):
                    off = half + s.px(8.0)  # off the street's tread, beside it
                    x, y = p[0] + sgn * nx * off, p[1] + sgn * ny * off
                    if own_well_clear(s, x, y, half, boxes):
                        s.well(x, y)
                        boxes.append((x, y, 2 * half, 2 * half))
                        n += 1
                        seated = True
                        break
                if seated:
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
        from .farm_water import farm_channels  # local: it reads the ways' routing, a later layer

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


def place_wells(s: Settlement, plan: SitePlan, houses: Sequence[Mapping[str, Any]]) -> int:
    """Seat the communal wells INSIDE the house cloud, not on a box around it.

    The engine's `place_wells` sweeps a grid over a bbox, which is right for a town's street blocks
    and wrong for a loose farm cluster: the bbox corners are open ground, so a well lands past the
    outermost homestead and, being a hard crop feature with a 16 px extent, drags the map's frame
    out after it and leaves a band of empty scrub on that side
    (`crop_not_held_open_by_one_feature`). Insetting the bbox was tried first and is not the fix -
    it starves an elongated cluster of wells entirely, because the inset box no longer holds a grid
    cell (`settlement_has_wells`, seed 3).

    A grove farm takes its own water; the communal wells are ALL seated by the hamlet's rolled `well_siting` (feature 374
    waves 154 and 155): the cluster form here (`seat_cluster`), among the houses before the lanes; the lane-side form once
    the lanes stand (`stage_lane_wells`), with the wells the water reach still owes (`reach_wells`). `seat_wells` carries the
    seat search and `well_at` the engine's own verdict on each seat.

    Research:
        no well in a household's homestead - research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.drawing.html, research/questions/0196-communal-wells-ido.drawing.html: the well shared off the farmstead, by the lane or among the houses, never a pocket inside one household's homestead
        grove farms take their own water - research/questions/0196-communal-wells-ido.drawing.html, research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: a dispersed farm draws from its own channel or well, not the shared-well rule of towns, so every grove farm takes its own water (`grove_water`) and is left out of the communal wells
        the wells' siting rolled - research/questions/0196-communal-wells-ido.drawing.html: by the lane or among the houses, a knob; the cluster form seated before the lanes, the lane-side form tried beside the track first and seated on a lane's verge once the lanes stand
        its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N3, 2026-10-25) - 11 (lattice step, lane-side seats)
    """
    grove_farms = [h for h in houses if (h.get("geom") or {}).get("groves")]
    if grove_farms:
        grove_water(s, plan, grove_farms)
        houses = [h for h in houses if h not in grove_farms]  # the communal wells serve the rest, if any
        if not houses:
            return len(s.M.get("wells", []))
    want = well_target(plan.spec.households)
    placed: list[Pt] = []
    # NO WELL POCKET IN A CLUSTERED HAMLET'S HOMESTEADS (feature 374 wave 155, row 787): the seating laid the first household
    # a well inside its own homestead, before its yard, and this drew it there - where 0028 draws "the well, shared off the
    # farmstead". Every well `well_target` owes is now a shared well of the rolled siting, and the water reach the pocket
    # carried by construction is held by the wells once the lanes stand (`reach_wells`). No ring probe and no `open_seat`
    # rescue (feature 287, homes H10-H12): no well is drawn outside its among-the-dwellings floor or past the crop to rescue one.
    # THE ROLLED SITING (feature 374 wave 154, 0196's knob): the cluster form is seated now, among the houses before the lanes
    # are laid; the lane-side form waits for the lanes (`stage_lane_wells`), as do any wells the cluster form could not seat
    s.M.setdefault("meta", {})["well_siting"] = plan.well_siting
    if plan.well_siting == "cluster":
        seat_cluster(s, plan, houses, placed, want)
    else:
        # ...the lane-side form first beside the way already laid - the track out, through the open ground at the cluster's
        # gateway, a wayside well (0196) - since the web's lanes run between the homesteads, where a verge is a yard or a
        # bed (measured on the 44 rolls: no lane-side seat beside a web lane ever cleared them)
        seat_wells(s, plan, houses, placed, want, THREE_THEN_TWO, "lane", seat_ok=on_a_verge(s), step=11.0)
    s._wells_owed = (want, ("cluster",) if plan.well_siting == "cluster" else ())  # type: ignore[attr-defined]
    return len(placed)


def stage_kept(s: Settlement, key: Any, make: Callable[[], Any]) -> Any:
    """What `make` builds, kept under `key` while `stage_lane_wells` holds its memo (only wells are added inside it); built
    afresh outside it (feature 427 T05).

    Research: plumbing - NONE: a cache, deciding nothing about the place"""
    memo: dict[Any, Any] | None = getattr(s, "_well_memo", None)
    if memo is None:
        return make()
    if key not in memo:
        memo[key] = make()
    return memo[key]


def seat_wells(
    s: Settlement,
    plan: SitePlan,
    houses: Sequence[Mapping[str, Any]],
    placed: list[Pt],
    want: int,
    rungs: Sequence[tuple[float, int]],
    form: str,
    gap: float = 0.0,
    seat_ok: SeatTest | None = None,
    candidates: Sequence[Pt] | None = None,
    step: float = 22.0,
) -> list[Pt]:
    """Seat communal wells among `houses` until `placed` holds `want`: the neighborhood ladder `rungs` - (third, want_near):
    the `want_near`-th nearest house within `third` px - over the lattice (or `candidates`), each seat with a dwelling's wall
    within `gap` (`WELL_SEAT_FT` by default), passing `seat_ok`, ranked by the worst-served household's walk with no well
    serving more than `WELL_SERVES_MAX` households where a seat avoids it, and the engine's `well_at` verdict. Each well it
    draws records its `form`. Returns the seats drawn. (Lifted out of `place_wells`, feature 374 wave 154.)

    Research:
        wells among the houses - research/questions/0196-communal-wells-ido.drawing.html: seats with a dwelling near and a neighborhood round them, each later one serving the worst-served household
        the first well's seat - GUESS: the innermost seat where one well is owed; where two or more are, the middle of its own share of the houses, the shares cut along the cluster's long axis (`first_share_middle`)
        seated a little closer than the check - GUESS research/questions/0196-communal-wells-ido.drawing.html: a dwelling's wall within `WELL_SEAT_FT` (80 ft, a GUESS the page names), the 95 ft check unchanged
        no well serving more than ten - research/questions/0196-communal-wells-ido.drawing.html: the five to ten houses each dug well served at Karihama; a seat that keeps every well at ten or fewer ranked first
        not in the windbreak - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: belt seats sorted last, never refused
        surface water counts - research/questions/0196-communal-wells-ido.drawing.html: a house within 760 ft (over the map's ft per px) of surface water needs no well
        wells apart - GUESS: searched, the record silent (feature 417 T29 pass C, 2026-10-25); 170 px between wells
        no well past the crop - research/questions/0196-communal-wells-ido.drawing.html: every well stands among the houses it serves; refused where the wellhead would widen the crop
        no well over a household's wood floor - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass C, 2026-10-25); no well seated over a household's reserved wood-floor seats
        later wells by the worst walk - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass C, 2026-10-25); ranked by the worst-served household's walk after the dig, in 66 px buckets, the crop's overreach added 1:1
        ties among later wells - GUESS: no source could speak to it, an algorithm's order, breadth or tolerance of ours (feature 417 T29 pass E, judged by the session from the code, 2026-10-25); the belt, then the crop's overreach, then the exact worst walk, then the want_near-th nearest house
        its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N3, 2026-10-25) - 22 (default lattice step); 120 (sweep box pad)
        its salts, guards and sentinels - NONE: they decide nothing about the place - 0.01 (divide-by-zero guard)
    """
    new: list[Pt] = []
    if not houses or len(placed) >= want:
        return new
    gap = gap or WELL_SEAT_FT / max(plan.ftpx, 0.01)
    seat_ok = seat_ok or ANYWHERE
    xs = [h["x"] for h in houses]
    ys = [h["y"] for h in houses]
    ccx, ccy = sum(xs) / len(xs), sum(ys) / len(ys)
    served = list(houses)
    # A WELLHEAD MAY NOT STAND IN THE SHELTER BELT (settlement-review, Inashiro 2026-08-18). The
    # belt is drawn later, but `village_grove` SKIPS any clump whose canopy would reach a wellhead
    # (`wells_clear_of_trees` - a well lost under the grove reads wrong), so a well seated inside
    # the belt's footprint silently deletes the clumps around it. Measured on Inashiro after the
    # tie-break change moved a well to (1098,1387), inside the belt's own footprint: the 40 ft band
    # at y1360-1400 went from 8 clumps to 1, and the belt acquired its first zero-canopy latitude in
    # a 930 ft run - a hole straight through the WINDWARD side, which is the entire point of a
    # windbreak. Nothing caught it: the belt's continuity is not gated, and the well checks are all
    # about the well.
    #
    # The belt is DERIVED from the houses, which already stand, so the prospective footprint can be
    # asked for now - the same expression `stage_woodland` will call, so the two cannot disagree.
    # This is a PREFERENCE and not a veto, per this function's standing rule that a settlement with
    # a badly-placed well beats one with no well: it sorts belt seats last, so one is taken only
    # when nothing outside the belt serves at all. It also happens to push wells toward the
    # dooryards, which is where the idiom 井戸端会議 puts them.
    from ..hinterland import belt_polygon  # local: hinterland is a later stage, module-level would invert the pipeline's reading order

    # ...ONCE A STAGE WHERE THE STAGE HOLDS A MEMO (feature 427 T05): inside `stage_lane_wells` only wells are added, and the belt
    # reads the houses, the lanes and the crop - eight calls rebuilt the same polygon on a 40-household roll
    memo: dict[Any, Any] | None = getattr(s, "_well_memo", None)
    _belt = stage_kept(s, "belt", lambda: belt_polygon(s, plan))

    # ...each seat asked once for the stage, every seat of a pool in one array (feature 435 T06): the belt stands still while wells land
    _belt_of: dict[tuple[float, float], int] = stage_kept(s, "belt_of", dict)

    def _belt_all(seats: Sequence[tuple[float, float, float]]) -> None:
        new = [(c[1], c[2]) for c in seats if (c[1], c[2]) not in _belt_of]
        for xy, inside in zip(new, points_in_poly(new, _belt) if _belt and new else [False] * len(new), strict=True):
            _belt_of[xy] = int(inside)

    def _in_belt(c: tuple[float, float, float]) -> int:
        """Asked once per seat, not once per sort (feature 427 T05, D5): every seat of a rung is asked by `_belt_all` first."""
        return _belt_of[(c[1], c[2])]

    # THE MINIMAX SERVES THE HOUSES THAT NEED A WELL (known-open ledger 2026-08-16): the
    # worst-served objective used to count every house, including those
    # `settlement_dwellings_watered` already treats as watered by a nearby stream / channel /
    # pond (Kashikawa's SW pocket, 77-182 ft from the stream head - the GM-settled "no redundant
    # well beside a living stream" case), so the objective and the check read two definitions of
    # "needs a well". `surface_water_dist` is the check's own predicate; a house within its
    # reach of surface water drops out of the objective and out of the rescue pass below. If
    # EVERY house is surface-watered the objective falls back to all of them - wells are still
    # dug (well_target), they just stop chasing houses the water already serves.
    _sw_reach = 760.0 / max(plan.ftpx, 0.01)
    needy = [h for h in houses if surface_water_dist(s.M, h["x"], h["y"]) > _sw_reach] or list(houses)
    # A RELAXATION LADDER, not a single rule. The tight neighborhood test is right for a compact
    # cluster and impossible for a stretched one: an `elongated` cluster strung along a margin has
    # no point with three homesteads inside 190 px, so the strict pass found nothing at all and the
    # map shipped with no well (seeds 3 and 12). A settlement WITHOUT a well is a much worse map
    # than one whose well sits a little wide, so the test loosens until it finds seats. It never
    # loosens into "anywhere": every seat still has to be nearer a house than the crop.
    # Only the THIRD-nearest distance relaxes - the "is this in a neighborhood" test. The gap to the
    # NEAREST house never relaxes: every rung holds it to `well_gap_to_dwellings` <= 95 px, the rule's
    # own predicate (feature 287, FR-003 - the rungs used to ask a house CENTER within 105-112 px, which
    # admitted a wall 99 px off). A well 220 px from its closest farmhouse is standing in the fields by
    # any measure, and relaxing that rung traded one failure for another.
    # The last rung also serves a PAIR. Every rung above asks for three homesteads around a seat,
    # which is the right shape for a nucleus and leaves a two-farm satellite with no well of its own
    # - and then the coverage pass cannot rescue it either, because the ground among two farms is
    # their own courtyards. Seed 18 stranded exactly that: a pair 500 px off the cluster, 760 and
    # 777 px from the nearest well, with all 118 legal-neighborhood probes around them refused.
    # Two households sharing a draw-well is an ordinary thing; three is not a threshold nature knows.
    reach_r = max((math.hypot(h["w"], h["h"]) / 2 for h in houses), default=0.0)  # the prefilter's widest house
    # ...AND NO WELL OVER A HOUSEHOLD'S SHARE OF THE WOOD FLOOR (feature 287, woods W25): the copse keeps its clumps off a
    # wellhead, so a well seated among the reserved seats would take the ground the household's floor stands on
    _wood = ReservedSeats(houses)
    _well_r = well_keepout(s) if _wood.grid.n else 0.0  # nothing reserved (a settlement seated without shares): nothing held
    # ONE WELL INDEX FOR THE WHOLE LADDER (dev/performance.md, `frozen_terrain`): a well laid here moves no water and no crop,
    # and each `well_at` built the water, dry-plot and wet-ring grids again for its one seat (cohort seed 44: 71 builds);
    # the scope asserts on exit that the terrain it froze is the terrain that stands
    sweep: SeatSweep | None = None
    # ...AND A SEAT `well_at` REFUSED IS NOT ASKED AGAIN BY A LATER RUNG (feature 427 T05): the terrain is frozen and inside this
    # call (and inside `stage_lane_wells`, whose memo keeps the set) only a well that lands changes what stands, which can add a refusal and never lift one (seed 25 at 40 households
    # asked 21,093 times, most of them seats an earlier rung had already been refused)
    _refused: set[tuple[float, float]] = memo.setdefault("refused", set()) if memo is not None else set()

    # `seat_ok` and the wood floor, neither reading the wells placed (feature 427 T05), ASKED OF THE LATTICE AS ARRAYS AND KEPT ON
    # THE SWEEP (feature 435 T06): every seat a rung reaches asked at once, each verdict read by every later rung and call
    _centers = None

    def _many(P: Any) -> Any:
        nonlocal _centers
        import numpy as np

        if _centers is None:
            _centers = np.asarray(_wood.pts, dtype=float).reshape(-1, 2)
        return np.asarray(seat_ok.many(P), dtype=bool) & ~discs_cover(P, _centers, _well_r)

    many = ((seat_ok.key, _well_r), _many)

    with s.frozen_terrain():
        for third, want_near in rungs:
            if len(placed) >= want:
                break
            seats: list[tuple[float, float, float]] = []
            # THE SWEEP BOX IS THE HOMESTEADS', NOT THE HOUSE CENTERS' (2026-08-15, cohort seed 44).
            # A bundle's courtyard ground extends ~a house-length past its house CENTER, so a cluster
            # strung along its field margin can keep every legal well pocket just OUTSIDE the centers'
            # bbox - seed 44 had 84 legal seats, nearly all north-west of min(xs)/min(ys), and the
            # unpadded grid visited none of them (0 of 1440 probes passed; the map shipped well-less).
            # The pad only restores ground the bundles themselves cover: every rung still demands a
            # dwelling's wall within 95 px, so an open-field corner of the padded box is rejected exactly
            # as the docstring above promises.
            pad = 120.0
            if sweep is None:  # ...ONE DISTANCE TABLE FOR EVERY RUNG (feature 387, plan D9): the lattice and the houses do not change
                # ...and for every call of the stage that asks the same lattice of the same houses at the same gap (feature 427 T05):
                # the sweep's wall gaps hold for its gap's reach, and nothing it measures moves while only wells are added
                key = ("sweep", step, gap, reach_r, tuple(candidates or ()), tuple((h["x"], h["y"], h["w"], h["h"], h.get("rot", 0.0), h.get("kind")) for h in houses))
                sweep = stage_kept(
                    s, key, lambda pad=pad: SeatSweep(list(candidates) if candidates is not None else list(grid_points(min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad, step)), houses)
                )
            seats, _near_of = sweep.seats(third, want_near, gap, reach_r, seat_ok, (ccx, ccy), many)
            _belt_all(seats)
            # GREEDY COVERAGE, not central-first throughout (settlement-review, Mizuguchi/Sawada
            # 2026-08-15): sorting every well toward the centroid put both of Mizuguchi's wells in one
            # lobe of a two-lobed cluster - the six eastern households walked 248-424 ft while the west
            # had a well within 63. The FIRST well is central (innermost legal seat, as before); every
            # LATER well takes the legal seat FARTHEST from the wells already standing, ties toward the
            # center - i.e. it serves the households the placed wells do not, which is why a real hamlet
            # digs a second well at all.
            # THE FIRST OF SEVERAL WELLS AT ITS SHARE'S MIDDLE (feature 374 wave 155): with the pocket gone, a first well at the
            # cluster's middle left the second, held 170 px off it, three or four households - the first served 12 or 13 on four
            # of the 44 rolls (m:w155-wells). Seated at the middle of its own share of the houses, the shares split along the
            # cluster's long axis, it leaves the second the other share (`first_share_middle`)
            _fx, _fy = first_share_middle(houses, want - len(placed)) if not placed and want - len(placed) >= 2 else (ccx, ccy)
            pool = sorted(seats, key=lambda c: (_in_belt(c), math.hypot(c[1] - _fx, c[2] - _fy)))  # never in the belt if anywhere else will do
            if not placed and want - len(placed) >= 2:
                # ...AND ONE STEP AHEAD: the nearest seats to the share's middle are ranked by whether the best second well
                # this rung offers, 170 px off, would leave both at ten or fewer (`well_seats.PairAhead`) - a first seat the rung's
                # ground pushed off its share left the second three or four households on three of the 44 rolls (m:w155-wells)
                ahead = PairAhead(seats, served)  # the second seats and the households, as arrays once (feature 387)
                pool[:PAIR_LOOK] = sorted(pool[:PAIR_LOOK], key=lambda c: not ahead.keeps_ten(c))
            # RE-SORTED ONLY WHEN A WELL HAS LANDED (feature 278, FR-004). The key reads the wells placed and the crop boxes, and
            # inside this loop only a well that lands changes either - so a pass that popped a seat and placed nothing left a
            # list already sorted by the key it would be sorted by again (Kuwabata: 168 sorts, 72,324 key evaluations, the
            # most of its 1.8 s appurtenance stage). The house-distance part of the key never reads the wells, so it is
            # computed once per seat.
            _sorted_at = -1
            _crop_box: tuple[int, tuple[float, float, float, float]] | None = None
            _score = PoolScore(pool, served, needy)  # the pool's seats-by-households distances, once a rung (feature 427 T05)
            while pool and len(placed) < want:
                if placed and len(placed) != _sorted_at:
                    # ...by MINIMAX NEED, in ~3-grid-step buckets, centrality breaking ties inside a
                    # bucket. Two failed rankings led here, and both are worth remembering. Strict
                    # farthest-first (the 2026-08-15 greedy-coverage fix) let a seat 91 px OUTSIDE the
                    # cluster beat an interior seat covering the same households - the exterior well
                    # held Sawada's whole frame open (crop_not_held_open_by_one_feature). Bucketing
                    # that same farthest-first score fixed the frame and re-broke coverage the other
                    # way: on Mizuguchi the spread rung walked EAST past the last house into scrub
                    # while the one under-served household stood at the WEST end (settlement-review
                    # 2026-08-16). Both fail because "far from the standing wells" is a proxy for the
                    # real quantity, which is the walk of the household WORST served after the well is
                    # dug - so score that directly: pick the seat minimizing the farthest any house
                    # would remain from its nearest well. A seat past the row's end cannot beat an
                    # in-row seat (it serves nobody the row seat does not), and a seat in an unserved
                    # lobe wins outright, which is what the greedy fix was for in the first place.
                    # ONCE PER SORT, ONCE PER CANDIDATE (feature 223, GM 2026-09-11: "the wells key"). The standing wells do
                    # not change while the pool is sorted, so each needy house's walk to its nearest standing well is
                    # taken once here, and the key tuple below is built once per candidate - it used to call
                    # `_worst_after` and `_extent_added` twice each per candidate and re-derive every house's walk to every
                    # standing well inside each call (70,416 calls, 1.2 million terms on Kuwabata). Same numbers, same
                    # order: `worst_after` is the lifted body, held to the nested form by its test.
                    _standing = [min(math.hypot(h["x"] - wx, h["y"] - wy) for wx, wy in placed) for h in needy]

                    # AND AN INTERIOR SEAT BEATS A PADDED ONE THAT SERVES THE SAME HOUSEHOLDS. The sweep
                    # box above is padded 120 px past the house CENTERS because a bundle's courtyard
                    # really does reach that far, and without the pad seed 44 shipped well-less. But the
                    # pad is symmetric, so it equally offers seats BEYOND the outermost homestead on
                    # every side - and a wellhead is a hard crop feature with a 16 px extent, so one
                    # seated out there drags the map's frame after it and leaves a band of empty scrub
                    # (`crop_not_held_open_by_one_feature`). The RESCUE pass below already refuses
                    # exactly that, with its `min(xs) <= x <= max(xs)` test and a comment giving this
                    # very reason; the greedy pass did not - two passes carrying two definitions of
                    # "inside the house cloud", with the looser one running first.
                    #
                    # MEASURED on cohort seed 41: the second well won its minimax bucket on the strength
                    # of one north-east household, then seated 76 px NORTH of that household and 66 px
                    # past every other feature on the map. The minimax objective is right and is not
                    # what moved here - the tie-break was, because distance-to-centroid cannot express
                    # "this seat is outside the settlement".
                    #
                    # SO IT IS A TIE-BREAK AHEAD OF CENTRALITY, NOT A FILTER. The padded ground stays in
                    # the pool and still wins when nothing inside the cloud serves the same households,
                    # which is what the pad was added for; it simply can no longer outrank an interior
                    # seat that does. Same shape as every other rule in this function: relax rather than
                    # forbid, because a settlement with a badly-placed well beats one with no well.
                    # OUTSIDE WHAT, EXACTLY - the CROP's own box, not a box round the house CENTERS. The
                    # first version of this tie-break tested `min(xs)..max(xs)`, an AABB of house centers,
                    # and settlement-review (Inashiro 2026-08-17) named the flaw before it bit: an AABB
                    # cannot tell "in the settlement" from "in the box", so on a two-lobed cluster the
                    # ~345 px of grove and scrub BETWEEN the lobes scores as interior, exactly like a
                    # courtyard. Cohort seed 29 then did bite - a well 64 px north of every other feature,
                    # inside the centers' box and holding the whole frame open.
                    #
                    # `_crop_boxes` is what `content_view` itself reads, so asking it is asking the
                    # question the check will ask: a seat inside the box the crop will set cannot hold the
                    # frame open, whatever its relation to the house centers. Same-source doctrine, and it
                    # picks up the houses' DRAWN extents plus their yards, gardens, sheds and byres rather
                    # than a point per house. (The box can only GROW later - the woodland and the pond are
                    # placed after - so this is conservative in the safe direction.)
                    _cb = s._crop_boxes(city=False)
                    _bx0 = min((b[0] for b in _cb), default=min(xs))
                    _bx1 = max((b[1] for b in _cb), default=max(xs))
                    _by0 = min((b[2] for b in _cb), default=min(ys))
                    _by1 = max((b[3] for b in _cb), default=max(ys))

                    # A TIE-BREAK CANNOT REACH A SEAT WITH NO RIVAL IN ITS BUCKET, so the FRAME goes into
                    # the score itself. Ranking outside-ness ahead of centrality fixed cohort seed 29 and
                    # left seed 7 failing for the reason a tie-break always leaves one: its pad seat was
                    # alone in its minimax bucket, so there was nothing to break the tie against. Seed 7's
                    # well sits 25 px past the northernmost byre and holds the whole frame open
                    # (`crop_not_held_open_by_one_feature`), because a wellhead is a hard crop feature with
                    # a 16 px extent and the crop follows it out.
                    #
                    # THE EXCHANGE RATE IS 1:1 IN PIXELS, which is what makes this a rule rather than a
                    # knob: a seat that drags the frame out by N px must save at least N px of the
                    # worst-served household's walk to be worth it. Both quantities are distances in the
                    # same units, so no weighting has to be invented - and the well that genuinely serves
                    # an outlying lobe still wins, because the coverage it buys is real.
                    # (the overreach: how far past the crop's predicted box a seat, drawn radius included, reaches - `PoolScore`)

                    # ...AND THE LAST TIE-BREAK IS THE NEIGHBORHOOD, NOT THE CENTROID (settlement-review,
                    # Sawada 2026-08-18). Once the minimax bucket and the frame term are equal, the
                    # remaining sort was `c[0]` - the seat's distance to the cluster CENTROID, computed
                    # when the pool was built. On a ONE-lobed cluster that reads as "the most central
                    # seat wins" and is fine. On a TWO-lobed one the centroid is the empty ground
                    # BETWEEN the lobes, so the tie-break actively prefers the gap: Sawada's second well
                    # moved off a seat serving 11 households within 300 ft onto one serving 5, and the
                    # worst walk went 364 -> 493 ft. Same family as the `_extent_added` fix above and as
                    # the standing rule against letting an aggregate stand in for the distributed thing
                    # a verdict is about - a centroid is not a place anybody lives.
                    #
                    # The measure that IS the question: how tightly is this seat surrounded by
                    # homesteads - the distance to the `want_near`-th nearest house, which is exactly
                    # the rung's own "is this in a neighborhood" test, reused rather than restated.
                    # Distance to the SINGLE nearest house was the ledger's sketch and is rejected: it
                    # is minimized by hugging one outlying farmhouse, which is the same mistake in the
                    # other direction. Every seat in the pool already passed the rung, so this only
                    # orders seats that are all legally "among the dwellings".
                    # (the neighborhood: the rung's own want_near-th nearest house, taken once by the sweep - `SeatSweep.seats`)

                    # THE BELT TERM SITS BEHIND COVERAGE, not in front of it. Ranked first it is a
                    # filter, and it behaved like every other filter this function has tried: Mizuguchi's
                    # second well moved off a seat inside the belt and its worst walk went 203 -> 264 ft,
                    # on a map whose belt hole turned out not to be well-caused at all, so the trade
                    # bought nothing. Behind the minimax bucket it can only decide between seats that
                    # serve the households equally well - which is all "do not stand in the windbreak"
                    # was ever entitled to decide.
                    # ...THE KEY ABOVE, FOR THE WHOLE POOL AT ONCE (feature 427 T05, D5): `_worst_after`, `_extent_added`,
                    # `most_served_after` and `_neighborhood` per seat walked every household against every standing well -
                    # 2.19M inner calls at 40 households (the T01 survey); `PoolScore` computes the same key in array
                    # operations, the one-seat forms kept as its reference (`tests/hamletgen/homesteads/test_pool_score.py`)
                    _keys = _score.keys(pool, placed, _standing, (_bx0, _bx1, _by0, _by1), drawn_r(s), _in_belt, _near_of, WELL_SERVES_MAX, 66.0)  # the worst walk's bucket, in px (the claim above)
                    _order = sorted(range(len(pool)), key=_keys.__getitem__)
                    pool[:] = [pool[i] for i in _order]
                    _sorted_at = len(placed)
                _, x, y = pool.pop(0)
                if any(math.hypot(x - px, y - py) < 170.0 for px, py in placed):
                    continue  # `wells_not_clustered`: shared wells serve separate courtyards
                if _crop_box is None or _crop_box[0] != len(placed):  # the crop's box moves only when a well lands (feature 387)
                    _crop_box = (len(placed), crop_box(s, xs, ys))
                if extent_past(_crop_box[1], drawn_r(s), (x, y)) > 0.0:
                    # NO WELL HOLDS THE CROP OPEN (feature 287, homes H12): the frame term was a score because a padded seat was
                    # sometimes the only way to water a household; a lattice well that reaches past the box the crop will set
                    # is refused, not drawn, and the reach is held by `reach_wells` (feature 374 wave 155)
                    continue
                if (x, y) in _refused:
                    continue
                if s.well_at(x, y):
                    mark_form(s, x, y, form)
                    placed.append((x, y))
                    new.append((x, y))
                else:
                    _refused.add((x, y))
    return new


def seat_cluster(s: Settlement, plan: SitePlan, houses: Sequence[Mapping[str, Any]], placed: list[Pt], want: int) -> list[Pt]:
    """The cluster form (feature 374 wave 154): wells in the open ground among five houses, the neighborhood's reach widened
    (190, 300, 520 px, then 0196's 760 ft) before the count gives way; three, then two, only where fewer than five households
    need the communal wells. Returns the seats drawn.

    Research:
        among five to ten houses - research/questions/0196-communal-wells-ido.drawing.html: the cluster form in the open ground among five to ten houses, off every lane
        the reach widens first - GUESS research/questions/0196-communal-wells-ido.drawing.html: how far round a seat the five may stand is this project's choice - 190, 300, 520 px, then 760 ft - widened before the count gives way
        off every lane - research/questions/0196-communal-wells-ido.drawing.html: the cluster well off every lane, its verge included (`on_a_verge`)
        three, then two, only where five cannot be gathered - research/questions/0196-communal-wells-ido.drawing.html: a household is still owed a well within reach
        its figures from 0196 - research/questions/0196-communal-wells-ido.drawing.html: 5 (fewer than five households: three, then two)
        its salts, guards and sentinels - NONE: they decide nothing about the place - 0.01 (divide-by-zero guard)
    """
    reach = max(520.0, 760.0 / max(plan.ftpx, 0.01))
    verge = on_a_verge(s)
    off_lanes = SeatTest("off-verge", lambda x, y: not verge(x, y), lambda P: ~verge.many(P))  # off every lane, its verge included (0196), where lanes stand
    new = seat_wells(s, plan, houses, placed, want, ((190.0, 5), (300.0, 5), (520.0, 5), (reach, 5)), "cluster", seat_ok=off_lanes)
    if len(placed) < want and len(houses) < 5:
        new += seat_wells(s, plan, houses, placed, want, THREE_THEN_TWO, "cluster", seat_ok=off_lanes)
    return new


def _anywhere_many(P: Any) -> Any:
    import numpy as np

    return np.ones(len(P), dtype=bool)


ANYWHERE = SeatTest("anywhere", lambda _x, _y: True, _anywhere_many)
"""Research: plumbing - NONE: the seat test of a form that sets none"""


def on_a_verge(s: Settlement) -> SeatTest:
    """The lane-side form's seat test: the wellhead's curb within `WELL_VERGE_FT` of a lane's tread - its center no farther
    from the tread's edge than the wellhead's half-extent and the verge (a curb ON the tread is `well_at`'s to refuse).

    Research: a lane-side well's seat - research/questions/0196-communal-wells-ido.drawing.html: on a lane's verge, clear of the tread, its curb within `WELL_VERGE_FT`"""
    # the lanes standing and the households' ways the seating reserved (`access_corridors`), drawn as lanes later: a cluster well
    # seated before the web keeps their verges too (feature 374 wave 154: two cohort wells stood on an access way's verge)
    memo: dict[Any, Any] | None = getattr(s, "_well_memo", None)
    if memo is not None and "verge" in memo:
        return memo["verge"]  # the lanes stand still while `stage_lane_wells` adds wells: one test, its answers kept (feature 427 T05)
    M = getattr(s, "M", None) or {}
    lanes = [([(float(p[0]), float(p[1])) for p in ln["pts"]], float(ln.get("w", 3.0)) / 2) for ln in [*(M.get("lanes") or []), *(M.get("access_corridors") or [])] if len(ln.get("pts") or []) >= 2]
    reach = s._well_vr() + s.px(WELL_VERGE_FT) if lanes else 0.0
    # ...EACH LEG FILED ONCE, its box padded by its half-width and the reach (feature 387): a seat asks the legs near it, not every
    # leg of every lane (the lattice at 11 px asked them all, seat by seat)
    entries = [
        (a, b, half, min(a[0], b[0]) - half - reach, min(a[1], b[1]) - half - reach, max(a[0], b[0]) + half + reach, max(a[1], b[1]) + half + reach)
        for pts, half in lanes
        for a, b in zip(pts, pts[1:], strict=False)
    ]
    legs = PointGrid()
    legs.extend(entries)

    asked: dict[tuple[float, float], bool] = {}

    def ok(x: float, y: float) -> bool:
        if (x, y) not in asked:
            asked[(x, y)] = any(seg_dist(x, y, a, b) - half <= reach for a, b, half, *_ in legs.near(x, y, 0.0))
        return asked[(x, y)]

    def many(P: Any) -> Any:
        """`ok` for every seat of `P` at once (feature 435 T06): each cell's seats against the legs whose padded box meets it."""
        import numpy as np

        out = np.zeros(len(P), dtype=bool)
        if not entries:
            return out
        box = np.asarray([e[3:] for e in entries], dtype=float)
        halves = np.asarray([e[2] for e in entries], dtype=float)
        for rows in cells(P):
            B = P[rows]
            (x0, y0), (x1, y1) = B.min(axis=0), B.max(axis=0)
            near = np.nonzero((box[:, 0] <= x1) & (box[:, 2] >= x0) & (box[:, 1] <= y1) & (box[:, 3] >= y0))[0]
            if len(near):
                out[rows] = ((seg_dists(B, [(entries[i][0], entries[i][1]) for i in near]) - halves[near][None, :]) <= reach).any(axis=1)
        return out

    test = SeatTest("verge", ok, many)
    if memo is not None:
        memo["verge"] = test
    return test


def stage_lane_wells(s: Settlement, plan: SitePlan) -> None:
    """THE WELLS THE LANES WAIT FOR (feature 374 wave 154): once the web stands, the communal wells still owed - the
    lane-side form's, or the cluster form's that found no seat - are seated: on a lane's verge (unless the lane-side form
    was tried), then among five houses (unless the cluster form was), then by the old three-then-two ladder at the 95 ft
    check, each such well marked `fallback` and counted (`meta.well_fallback`) - a recorded deviation, never silent.

    Steps:
        l7r.diagram.hamletgen.homesteads.wells.lane_and_fallback_wells
        l7r.diagram.hamletgen.homesteads.wells.reach_wells
        l7r.diagram.hamletgen.homesteads.wells.record_over_ten

    Research:
        lane-side wells after the lanes - research/questions/0196-communal-wells-ido.drawing.html: the lane-side form on a lane verge, clear of the tread, within reach of the houses
        the other form only after the reach widened - research/questions/0196-communal-wells-ido.drawing.html: both forms the research's
        the old ladder a recorded deviation - DEVIATION research/questions/0196-communal-wells-ido.drawing.html: three, then two houses at the 95 ft check, marked `fallback`, past both forms"""
    owed = getattr(s, "_wells_owed", None)
    if not owed:
        return
    s._well_memo = {}  # type: ignore[attr-defined]  # the belt and the seat sweeps, kept while only wells are added (`seat_wells`)
    try:
        lane_and_fallback_wells(s, plan, owed)
        reach_wells(s, plan)
    finally:
        s._well_memo = None  # type: ignore[attr-defined]
        record_over_ten(s)


def dry_households(s: Settlement, houses: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    """The households beyond `WATER_REACH_FT` of every communal well and of open water (`surface_water_dist`, the measure
    the seat search and the gate's watered rule read).

    Research: every household watered - research/questions/0196-communal-wells-ido.drawing.html: a well, channel, pond or stream within 760 ft"""
    reach = s.px(WATER_REACH_FT)
    ws = [(float(w["x"]), float(w["y"])) for w in s.M.get("wells") or [] if not w.get("private") and not w.get("shrine")]
    return [h for h in houses if not any(math.hypot(float(h["x"]) - x, float(h["y"]) - y) <= reach for x, y in ws) and surface_water_dist(s.M, float(h["x"]), float(h["y"])) > reach]


def reach_wells(s: Settlement, plan: SitePlan) -> None:
    """THE WATER REACH HELD BY THE WELLS (feature 374 wave 155, row 787): the guarantee the first household's well pocket
    carried by construction - every household within `WATER_REACH_FT` of a well or open water - is held here, once the forms
    have seated what `well_target` owes. While a household is dry, one more shared well is seated: the rolled form first, then
    the other, then the recorded fallback, each ranking the seat that best serves the worst-served household. A well beyond
    `well_target` is counted (`meta.wells_for_reach`), and a household still dry past all three (`meta.dry_households`).
    ...AND THE CEILING OF TEN (feature 374 wave 155, W155-6): while a well is nearest to more than `WELL_SERVES_MAX`
    households, one more shared well is seated the same way (`meta.wells_for_ten` counts those) - a clustered hamlet's
    homesteads stand edge to edge, and with no pocket no seat among a full share's houses may be open; a third well for
    sixteen households is one to five, within the record's one to 2-20 for a hamlet (0196).

    Research:
        a well for every household beyond reach - research/questions/0196-communal-wells-ido.drawing.html: every household within 760 ft of a well or open water, one more shared well where the houses spread past the hamlet's one or two
        one more well where one serves more than ten - research/questions/0196-communal-wells-ido.drawing.html: the five to ten houses a Karihama well served, a hamlet's wells as many as one to 2-20 households
        the forms' order - research/questions/0196-communal-wells-ido.drawing.html: the rolled siting first, the other form, then the fallback (`lane_and_fallback_wells`)
        its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N3, 2026-10-25) - 11 (lattice step)
    """
    houses = [h for h in s.M.get("houses") or [] if not (h.get("geom") or {}).get("groves") and h.get("kind") != "abandoned"]
    added = over = 0
    last = len(houses) + 1
    for _ in range(len(houses)):
        placed = [(float(w["x"]), float(w["y"])) for w in s.M.get("wells") or [] if not w.get("private") and not w.get("shrine")]
        most = most_served_after((0.0, placed[-1][0], placed[-1][1]), houses, placed[:-1]) if placed else 0
        busy = most > WELL_SERVES_MAX and most < last  # a well that left the busiest count where it was is not tried again
        if not dry_households(s, houses) and not busy:
            break
        last, over = most, over + int(busy)
        want = len(placed) + 1
        for form in (plan.well_siting, "cluster" if plan.well_siting == "lane" else "lane"):
            if len(placed) < want:
                if form == "lane":
                    seat_wells(s, plan, houses, placed, want, THREE_THEN_TWO, "lane", seat_ok=on_a_verge(s), step=11.0)
                else:
                    seat_cluster(s, plan, houses, placed, want)
        if len(placed) < want:
            if not seat_wells(s, plan, houses, placed, want, THREE_THEN_TWO, "fallback", gap=WELL_AMONG_DWELLINGS_PX):
                break
            s.M["meta"]["well_fallback"] = int(s.M["meta"].get("well_fallback", 0)) + 1
        added += 1
    if added - over:
        s.M["meta"]["wells_for_reach"] = added - over
    if over:
        s.M["meta"]["wells_for_ten"] = over
    dry = dry_households(s, houses)
    if dry:
        s.M["meta"]["dry_households"] = len(dry)


def record_over_ten(s: Settlement) -> None:
    """A communal well nearest to more than `WELL_SERVES_MAX` households, recorded (`meta.wells_over_ten`: each such well's
    count) - a recorded deviation, never silent: the seat search ranks a seat that keeps every well at ten first, and where
    none does the well stands and is counted.

    Research: more than ten to a well, recorded - DEVIATION research/questions/0196-communal-wells-ido.drawing.html: the well serving more than ten stands where no seat keeps every well to ten, marked on the map's record"""
    ws = [(float(w["x"]), float(w["y"])) for w in s.M.get("wells") or [] if not w.get("private") and not w.get("shrine")]
    houses = [h for h in s.M.get("houses") or [] if not (h.get("geom") or {}).get("groves") and h.get("kind") != "abandoned"]
    if not ws or not houses:
        return
    count = [0] * len(ws)
    for h in houses:
        count[min(range(len(ws)), key=lambda i: math.hypot(float(h["x"]) - ws[i][0], float(h["y"]) - ws[i][1]))] += 1
    over = [c for c in count if c > WELL_SERVES_MAX]
    if over:
        s.M["meta"]["wells_over_ten"] = over


def lane_and_fallback_wells(s: Settlement, plan: SitePlan, owed: tuple[int, Sequence[str]]) -> None:
    """The wells still owed once the lanes stand: the lane-side form, the cluster form, then the recorded fallback.

    Research:
        the order of the forms - research/questions/0196-communal-wells-ido.drawing.html: the lane-side form on a verge once the lanes stand, the other form where no verge has room
        the fallback - DEVIATION research/questions/0196-communal-wells-ido.drawing.html: among three houses, then two, at the 95 ft, where neither form finds a seat, marked `fallback`
        its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N3, 2026-10-25) - 11 (lattice step)
    """
    want, tried = owed
    houses = [h for h in s.M.get("houses") or [] if not (h.get("geom") or {}).get("groves")]
    placed = [(float(w["x"]), float(w["y"])) for w in s.M.get("wells") or [] if not w.get("private") and not w.get("shrine")]
    if len(placed) >= want or not houses:
        return
    if "lane" not in tried:
        # the lattice at 11 px, half its step elsewhere: the verge test admits a band only `WELL_VERGE_FT` wide beside each
        # lane, which a 22 px lattice steps over rather than samples - the same ground offered, never a tighter fit
        # (hour:374-match-the-research-continued@3 ruled the step and the seat gap fixed: make room, never pack)
        seat_wells(s, plan, houses, placed, want, THREE_THEN_TWO, "lane", seat_ok=on_a_verge(s), step=11.0)
    if len(placed) < want and "cluster" not in tried:
        seat_cluster(s, plan, houses, placed, want)
    if len(placed) < want:
        n = len(seat_wells(s, plan, houses, placed, want, THREE_THEN_TWO, "fallback", gap=WELL_AMONG_DWELLINGS_PX))
        s.M["meta"]["well_fallback"] = int(s.M["meta"].get("well_fallback", 0)) + n
