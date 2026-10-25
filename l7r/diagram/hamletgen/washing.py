"""WASHING PLACES AT THE WATER'S EDGE (feature 374 wave 150): where a stream or ditch passes a settlement's houses, the places
its households washed clothes and vegetables - shared footings of steps down the bank, or one step at each house where a channel
runs past the houses, a knob rolled per settlement (research/questions/0065-washing-places-at-the-waters-edge.html, the record;
its drawing page, the rule).

Research: washing places plumbing - NONE: the courses, the seats asked of the registry, the glyph's strokes; the units that decide carry their own claims
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, seg_closest

from .consts import Poly, Pt
from .plan import SitePlan, _roll

WASHING_FORMS = ("shared", "each_house")
"""The two forms 0065 records, rolled per settlement at even odds.

Research:
    shared or one at each house - research/questions/0065-washing-places-at-the-waters-edge.html, research/questions/0065-washing-places-at-the-waters-edge.drawing.html: a footing shared by the neighbors on a channel, or set at a single house
    at even odds - GUESS research/questions/0065-washing-places-at-the-waters-edge.drawing.html: "the record gives no shares between the two, so the odds are arbitrary"
"""

WASHING_FT = (4.0, 6.0)
"""A washing place's footing: 4 ft wide along the bank, 6 ft down it to the water.

Research:
    footing width - GUESS research/questions/0065-washing-places-at-the-waters-edge.drawing.html: a footing of steps down the bank, about 4 ft wide, a GUESS the page names
    footing depth - GUESS: the footing runs 6 ft down the bank, a few steps; 0065 found no page giving a washing footing's form or size"""

HOUSEHOLDS_PER_WASHING = 4
"""How many households on a bank share one washing place.

Research: one for every few households - GUESS research/questions/0065-washing-places-at-the-waters-edge.drawing.html: "one for every few households on that bank (a guess)", four taken for the few"""

PASS_REACH_FT = 120.0
"""How near a stream or ditch must run to a house to pass it: the household then washes there.

Research: water passing the houses - GUESS research/questions/0065-washing-places-at-the-waters-edge.drawing.html: within about 120 ft of the houses it serves; no page gives how far a household walked to wash"""

BANK_SHIFTS_FT = (0.0, 8.0, -8.0, 16.0, -16.0, 24.0, -24.0, 32.0, -32.0)
"""Where a footing's first seat is taken (a lane, a bridge, a building), the seats offered along the bank instead.

Research: a seat along the bank - GUESS research/questions/0065-washing-places-at-the-waters-edge.drawing.html: moved along the bank where a lane, a bridge or a building takes the spot, up to about 32 ft either way, in 8 ft steps"""

STEP_STONE = "#CFC6B2"
"""The footing's pale stone fill.

Research: a pale stone footing - CONVENTION: pale, to read as worked stone against the bank's green and the water's blue"""

STEP_EDGE = "#8C8070"
"""The footing's edge and its step lines.

Research: the steps drawn as lines - CONVENTION: a darker stone line for the edge and each step"""


def washing_form(plan: SitePlan, M: Mapping[str, Any]) -> str:
    """This settlement's form: rolled from its seed between the two (`WASHING_FORMS`); the one-at-each-house form is taken only
    where a farm channel runs to the houses (`farm_channels`), and the shared form otherwise.

    Research:
        one at each house where a channel runs past - research/questions/0065-washing-places-at-the-waters-edge.drawing.html: "where a channel runs past the houses, one step at each house on it"
        the two forms - research/questions/0065-washing-places-at-the-waters-edge.html: a footing shared by the neighbors on a channel, or set at a single house"""
    form = str(_roll(plan.spec.seed, "washing_form", WASHING_FORMS))
    return form if form == "shared" or M.get("farm_channels") else "shared"


def passing_courses(M: Mapping[str, Any]) -> list[tuple[list[Pt], float]]:
    """The waters a washing place may stand on, each (its centerline, its half-width): the brook, the head race led from its
    intake (`channels`), every field ditch, the drain among them, and every farm channel led to the houses - 0065 names any
    stream or ditch that passes the houses, the shared footing "on the channel or stream bank".

    Research: a stream, a ditch or a channel - research/questions/0065-washing-places-at-the-waters-edge.drawing.html: where a stream or ditch passes the houses, a shared one on the channel or stream bank
        its fallback stream width - GUESS: searched, the record silent (feature 417 T38, 2026-10-25) - 9 (fallback stream width, halved; the brook is drawn 7 ft)
        its figures from 0068 - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: 6 (fallback channel width); 1.5 (fallback field-ditch width)
        its figures from 0031 - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: 2.5 (fallback farm-channel width)
    """
    out = [([(float(a), float(b)) for a, b in st["poly"]], float(st.get("w", 9.0)) / 2.0) for st in M.get("streams") or [] if len(st.get("poly") or []) >= 2]
    out += [([(float(a), float(b)) for a, b in c["poly"]], float(c.get("w", 6.0)) / 2.0) for c in M.get("channels") or [] if len(c.get("poly") or []) >= 2]
    out += [([(float(a), float(b)) for a, b in d["poly"]], float(d.get("w", 1.5)) / 2.0) for d in M.get("field_ditches") or [] if len(d.get("poly") or []) >= 2]
    out += [
        ([(float(a), float(b)) for a, b in ch.get("poly") or ch.get("pts") or []], float(ch.get("w", 2.5)) / 2.0)
        for ch in M.get("farm_channels") or []
        if len(ch.get("poly") or ch.get("pts") or []) >= 2
    ]
    return out


def nearest_on(course: Sequence[Pt], p: Pt) -> tuple[Pt, float, int]:
    """The point of `course` nearest `p`, its distance, and the index of its segment.

    Research: plumbing - NONE: a nearest point on a polyline"""
    best: tuple[Pt, float, int] = (course[0], math.inf, 0)
    for k, (a, b) in enumerate(zip(course, course[1:], strict=False)):
        q = seg_closest(p[0], p[1], a, b)
        d = math.dist(p, q)
        if d < best[1]:
            best = ((float(q[0]), float(q[1])), d, k)
    return best


def footing(course: Sequence[Pt], at: Pt, seg: int, half_w: float, toward: Pt, along: float, px: Any) -> dict[str, Any]:
    """The footing record set on `course`'s bank at `at` (on segment `seg`), slid `along` px along it, on the side of `toward`:
    its long side down the bank, its foot at the water's edge.

    Research: a footing on the bank, on the households' side - research/questions/0065-washing-places-at-the-waters-edge.drawing.html: a footing of steps down the bank"""
    a, b = course[seg], course[min(seg + 1, len(course) - 1)]
    ln = math.dist(a, b) or 1.0
    ux, uy = (b[0] - a[0]) / ln, (b[1] - a[1]) / ln
    nx, ny = -uy, ux
    if (toward[0] - at[0]) * nx + (toward[1] - at[1]) * ny < 0:
        nx, ny = -nx, -ny
    w, h = px(WASHING_FT[0]), px(WASHING_FT[1])
    cx, cy = at[0] + ux * along + nx * (half_w + h / 2.0), at[1] + uy * along + ny * (half_w + h / 2.0)
    rot = math.degrees(math.atan2(uy, ux))
    return {"x": round(cx, 1), "y": round(cy, 1), "w": round(w, 1), "h": round(h, 1), "rot": round(rot, 1)}


def shared_places(s: Settlement, M: Mapping[str, Any]) -> list[dict[str, Any]]:
    """The shared form: each household washes at its nearest water that passes it (`PASS_REACH_FT`); the households of one
    bank of one water (`bank_of`) taken in their order along it, one footing for every `HOUSEHOLDS_PER_WASHING` of them, at
    the bank point nearest their middle household, on their side, the first seat along the bank the registry admits
    (`BANK_SHIFTS_FT`); a group with no seat keeps none, counted (`meta.washing_no_seat`).

    Research:
        one for every few households on that bank - GUESS research/questions/0065-washing-places-at-the-waters-edge.drawing.html: one for every few households on that bank
        its nearest water - GUESS: searched, the record silent (feature 417 T36 pass P7, 2026-10-25); a household washes at the passing water nearest it; no page says which of two it used
        nearest the households it serves - GUESS research/questions/0065-washing-places-at-the-waters-edge.drawing.html: at the point nearest the middle of those households, on their side of the water"""
    reach = s.px(PASS_REACH_FT)
    courses = passing_courses(M)
    if not courses:
        return []
    banks: dict[tuple[int, int], list[tuple[int, float, Pt, Pt]]] = {}
    for hx in M.get("houses") or []:
        h = (float(hx["x"]), float(hx["y"]))
        near = [(nearest_on(course, h), k) for k, (course, _hw) in enumerate(courses)]
        (q, d, seg), k = min(near, key=lambda n: n[0][1])
        if d <= reach:
            banks.setdefault((k, bank_of(courses[k][0], seg, h)), []).append((seg, math.dist(courses[k][0][seg], q), h, q))
    out: list[dict[str, Any]] = []
    for (k, _side), near in sorted(banks.items()):
        course, hw = courses[k]
        near.sort()
        for g in range(0, len(near), HOUSEHOLDS_PER_WASHING):
            group = near[g : g + HOUSEHOLDS_PER_WASHING]
            seg, _t, h, q = group[len(group) // 2]
            for shift in BANK_SHIFTS_FT:
                rec = footing(course, q, seg, hw, h, s.px(shift), s.px)
                if s.admits("washing_places", rec):
                    out.append(rec)
                    s.M.setdefault("washing_places", []).append(rec)  # held at once, so the next group's seat keeps off it
                    break
            else:
                no_seat(s.M)
    return out


def bank_of(course: Sequence[Pt], seg: int, p: Pt) -> int:
    """Which bank of `course` the point `p` stands on, beside segment `seg`: 1 on its left, -1 on its right.

    Research: plumbing - NONE: the side of a line a point is on"""
    a, b = course[seg], course[min(seg + 1, len(course) - 1)]
    return 1 if (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= 0 else -1


def no_seat(M: Any) -> None:
    """Count a washing place no seat along its bank admits (`meta.washing_no_seat`).

    Research: a footing with no seat left out - NONE: the count of a refusal"""
    M["meta"]["washing_no_seat"] = int(M["meta"].get("washing_no_seat", 0)) + 1


def each_house_places(s: Settlement, M: Mapping[str, Any]) -> list[dict[str, Any]]:
    """The one-at-each-house form: a step at the end of each farm's channel, in its dooryard, laid along the channel's last leg,
    where the registry admits it, slid at most 16 ft along the channel (the first five `BANK_SHIFTS_FT`).

    Research:
        one step at each house on the channel - research/questions/0065-washing-places-at-the-waters-edge.drawing.html: where a channel runs past the houses, one step at each house on it
        slid at most 16 ft - GUESS: searched, the record silent (feature 417 T36 pass P7, 2026-10-25); a step in its own dooryard, so no farther along the channel than 16 ft
        its figures from 0031 - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: 2.5 (fallback farm-channel width at the step)
    """
    out: list[dict[str, Any]] = []
    for ch in M.get("farm_channels") or []:
        pts = [(float(a), float(b)) for a, b in ch.get("poly") or ch.get("pts") or []]
        if len(pts) < 2:
            continue
        end, prev = pts[-1], pts[-2]
        house = (float(ch["of"][0]), float(ch["of"][1])) if ch.get("of") else end
        for shift in BANK_SHIFTS_FT[:5]:
            rec = footing([prev, end], end, 0, s.px(float(ch.get("w", 2.5))) / 2.0, house, s.px(shift), s.px)
            if s.admits("washing_places", rec):
                out.append(rec)
                s.M.setdefault("washing_places", []).append(rec)
                break
        else:
            no_seat(s.M)
    return out


def draw_washing_place(s: Settlement, rec: Mapping[str, Any]) -> None:
    """A footing of pale stone with its steps: a small quad turned to the bank, two step lines across it.

    Research: drawn as a stone footing - CONVENTION: a pale stone quad with step lines, the footing's real size
        its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 6 (step lines at plus and minus one sixth of the footing)
    """
    x, y, w, h, rot = float(rec["x"]), float(rec["y"]), float(rec["w"]), float(rec["h"]), math.radians(float(rec["rot"]))
    ux, uy, nx, ny = math.cos(rot), math.sin(rot), -math.sin(rot), math.cos(rot)

    def at(a: float, b: float) -> Pt:
        return (x + ux * a + nx * b, y + uy * a + ny * b)

    ring: Poly = [at(-w / 2, -h / 2), at(w / 2, -h / 2), at(w / 2, h / 2), at(-w / 2, h / 2)]
    path = "M" + "L".join(f"{p[0]:.1f},{p[1]:.1f}" for p in ring) + "Z"
    steps = "".join(f"M{at(-w / 2, k * h / 6)[0]:.1f},{at(-w / 2, k * h / 6)[1]:.1f}L{at(w / 2, k * h / 6)[0]:.1f},{at(w / 2, k * h / 6)[1]:.1f}" for k in (-1, 1))
    s.add(f'<path d="{path}" fill="{STEP_STONE}" stroke="{STEP_EDGE}" stroke-width="0.6"/><path d="{steps}" stroke="{STEP_EDGE}" stroke-width="0.5"/>', cls="washing place")


def stage_washing(s: Settlement, plan: SitePlan) -> None:
    """Washing places where water passes the houses, after every way and crossing they keep clear of: the form rolled
    (`washing_form`), its places seated, each drawn, the form and count recorded (`meta.washing_form`, `washing_places`).

    Steps:
        l7r.diagram.hamletgen.washing.washing_form
        l7r.diagram.hamletgen.washing.shared_places
        l7r.diagram.hamletgen.washing.each_house_places

    Research: after the ways and crossings - GUESS research/questions/0065-washing-places-at-the-waters-edge.drawing.html: where a lane, a bridge or a building takes the spot, the washing place is moved along the bank; set last of the ground's features, so each seat is asked of every way, bridge and building already standing; no page orders them"""
    form = washing_form(plan, s.M)
    places = each_house_places(s, s.M) if form == "each_house" else shared_places(s, s.M)
    for rec in places:
        draw_washing_place(s, rec)
    s.M["meta"]["washing_form"] = form
    s.M["meta"]["washing_places"] = len(places)
