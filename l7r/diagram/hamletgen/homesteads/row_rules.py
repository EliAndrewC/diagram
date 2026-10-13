"""THE ROW VILLAGE'S AND THE GROVE FARM'S RULES, read off a finished manifest (feature 291 amendment 3, plan D19; SC-007,
SC-008). Pure functions of the manifest, each returning what breaks its rule - empty when the map keeps it - run by
`tools/cohort_audit` on every roll and by the gate test on the pool's grove maps, beside `grove_rules`.

- `row_rules`: a linear map's farms stand within a frame depth of a street, none behind another on its side of its
  street, each street drawn as one continuous way, every far-row farm with its holding drawn behind it, every row farm's
  way ending on its own street (FR-013 to FR-017);
- `water_rules`: a dispersed farm's own water as `farm_water` says - a channel into its frame, or its own well in its
  dooryard, off its way in; a linear map's `row_water` drawn - own wells,
  or every farm within reach of a shared one (FR-018);
- `bamboo_mismatch`: the farms drawing grove bamboo exactly the farms that rolled a household bamboo stand (FR-019).

Here, not beside `grove_rules` in the settlement engine, because the door is the ways' (`ways/serve.front_door`) and the
engine does not import the generator.

Research: manifest reading - NONE: polyline distances, keys and joins; each rule function carries its own claims
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import seg_dist

from ..consts import FOOTPATH_FABRIC_GAP, Pt
from ..ways.serve import DOOR_REACH_FT, front_door
from .wells import WATER_REACH_FT


def _segs(pts: Sequence[Sequence[float]]) -> list[tuple[Pt, Pt]]:
    return [((float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) for a, b in zip(pts, pts[1:], strict=False)]


def _dist(p: Pt, segs: Sequence[tuple[Pt, Pt]]) -> float:
    return min((seg_dist(p[0], p[1], a, b) for a, b in segs), default=float("inf"))


def _key(p: Sequence[float]) -> tuple[float, float]:
    return (round(float(p[0]), 1), round(float(p[1]), 1))


def _frame(h: Mapping[str, Any]) -> tuple[float, float, float, float] | None:
    b = (h.get("geom") or {}).get("bbox")
    return (float(b[0]), float(b[1]), float(b[2]), float(b[3])) if b else None


def continuous(pieces: Sequence[Sequence[Sequence[float]]], tol: float = 1.5) -> bool:
    """Do these polylines join end to end (or end on another's tread) into ONE way? True for one piece or none."""
    if len(pieces) <= 1:
        return True
    comp = list(range(len(pieces)))

    def find(i: int) -> int:
        while comp[i] != i:
            comp[i] = comp[comp[i]]
            i = comp[i]
        return i

    segs = [_segs(p) for p in pieces]
    for i, p in enumerate(pieces):
        for e in (p[0], p[-1]):
            for j in range(len(pieces)):
                if j != i and _dist((float(e[0]), float(e[1])), segs[j]) <= tol:
                    comp[find(i)] = find(j)
    return len({find(i) for i in range(len(pieces))}) == 1


def row_rules(M: Mapping[str, Any]) -> list[tuple[str, Any]]:
    """Each (rule, subject) a linear map breaks; [] for another form. A linear map with no seated street breaks the first
    rule of all - its farms stand in no row (plan D15).

    Research:
        farms on their street - research/questions/0033-row-villages-resson.html, research/questions/0033-row-villages-resson.drawing.html: within a frame of a street, none more than half a frame behind another on its side
        street one continuous way - research/questions/0033-row-villages-resson.drawing.html: each planned street drawn unbroken
        far-row holding drawn - research/questions/0033-row-villages-resson.drawing.html: every reserved holding drawn behind its farm
        way ends on its own street - research/questions/0033-row-villages-resson.drawing.html: the door within reach of its street, or a door path to it
        door reach of a street - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a door within `DOOR_REACH_FT` (60 ft) of its street needs no door path
    """
    meta = M.get("meta") or {}
    plans = M.get("row_street_plans") or []
    if meta.get("settlement_form") != "linear":
        return []
    if not plans:
        return [("no_row_street", len(M.get("houses") or []))]
    out: list[tuple[str, Any]] = []
    streets = [_segs(p) for p in plans]
    houses = list(M.get("houses") or [])
    lanes = list(M.get("lanes") or [])
    own: dict[tuple[float, float], int] = {}
    drawn_st = {k: [sg for ln in lanes if ln.get("street") and ln.get("street_index") == k for sg in _segs(ln["pts"])] for k in range(len(plans))}
    for h in houses:
        c = (float(h["x"]), float(h["y"]))
        fr = _frame(h)
        size = max(fr[2], fr[3]) if fr else 240.0  # the house may stand at its frame's far side from the street
        d = [_dist(c, s) for s in streets]
        door = front_door(h, FOOTPATH_FABRIC_GAP + 4.0) or c
        own[_key(c)] = min(range(len(streets)), key=lambda i: _dist(door, drawn_st.get(i) or streets[i]))  # the street its door faces, as drawn (`serve.own_street`)
        if min(d) > size:
            out.append(("farm_off_its_street", _key(c)))
    # NOT BEHIND ANOTHER on its side of its street: two farms of one street, one side, overlapping along it, one standing
    # more than half a frame deeper than the other
    for k, segs in enumerate(streets):
        mine = [h for h in houses if own.get(_key((h["x"], h["y"]))) == k]
        arc = [0.0]
        for a, b in segs:
            arc.append(arc[-1] + math.dist(a, b))
        placed: list[tuple[float, float, int, Any]] = []
        for h in mine:
            c = (float(h["x"]), float(h["y"]))
            i = min(range(len(segs)), key=lambda j: seg_dist(c[0], c[1], *segs[j]))
            a, b = segs[i]
            L = math.dist(a, b) or 1.0
            tx, ty = (b[0] - a[0]) / L, (b[1] - a[1]) / L
            u = arc[i] + (c[0] - a[0]) * tx + (c[1] - a[1]) * ty
            v = (c[0] - a[0]) * -ty + (c[1] - a[1]) * tx
            placed.append((u, abs(v), 1 if v >= 0 else -1, h))
        for i, (u1, v1, s1, h1) in enumerate(placed):
            fr = _frame(h1)
            w = max(fr[2], fr[3]) if fr else 240.0
            for u2, v2, s2, h2 in placed[i + 1 :]:
                if s1 == s2 and abs(u1 - u2) < w / 2 and abs(v1 - v2) > (min(fr[2], fr[3]) if fr else 240.0) / 2:
                    out.append(("farm_behind_another", (_key((h1["x"], h1["y"])), _key((h2["x"], h2["y"])))))
    # EACH STREET ONE CONTINUOUS WAY
    for k in range(len(plans)):
        pieces = [ln["pts"] for ln in lanes if ln.get("street") and ln.get("street_index") == k]
        if not pieces:
            out.append(("street_not_drawn", k))
        elif not continuous(pieces):
            out.append(("street_broken", k))
    # EVERY FAR-ROW FARM WITH ITS HOLDING DRAWN
    drawn = {int(p["holding"]) for p in M.get("dry_plots") or [] if p.get("holding") is not None}
    for rec in M.get("row_holdings") or []:
        if int(rec["id"]) not in drawn:
            out.append(("holding_not_drawn", _key(rec["of"])))
    # EVERY ROW FARM'S WAY ENDS ON ITS OWN STREET: its door within the door reach of that street, or a door path serving it
    served = {_key(ln["serves"]) for ln in lanes if ln.get("serves")}
    for h in houses:
        door = front_door(h, FOOTPATH_FABRIC_GAP + 4.0)
        k = own.get(_key((h["x"], h["y"])))
        if door is None or k is None:
            continue
        if _dist(door, drawn_st.get(k, [])) > DOOR_REACH_FT and _key((h["x"], h["y"])) not in served:
            out.append(("farm_not_on_its_street", _key((h["x"], h["y"]))))
    return out


def water_rules(M: Mapping[str, Any]) -> list[tuple[str, Any]]:
    """Each (rule, subject) a non-nucleated map's water breaks (FR-018): a dispersed farm under `farm_water` channel without
    a channel ending inside its frame (amendment 5); a dispersed farm under `well` - or a linear farm under `own` - without a
    private well inside its frame and off its way in; a linear farm under `shared` farther than the watering reach from
    every well.

    Research:
        a scattered farm's own water - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: its channel ends in its frame, or its own well in its frame off its way in
        a row's water - research/questions/0033-row-villages-resson.drawing.html: own wells, or every farm within `WATER_REACH_FT` of a shared one
        well in the way in - UNRESEARCHED: a private well within 12 ft of the house-to-door line counts as in the way
    """
    meta = M.get("meta") or {}
    form = meta.get("settlement_form")
    if form not in ("dispersed", "linear"):
        return []
    wells = [(float(w["x"]), float(w["y"]), bool(w.get("private"))) for w in M.get("wells") or []]
    out: list[tuple[str, Any]] = []
    shared = form == "linear" and meta.get("row_water") == "shared"
    channel = form == "dispersed" and meta.get("farm_water") == "channel"
    ends = {_key(c["of"]): c["pts"][-1] for c in M.get("farm_channels") or [] if c.get("of") and c.get("pts")}
    for h in M.get("houses") or []:
        if not (h.get("geom") or {}).get("groves"):
            continue
        c = (float(h["x"]), float(h["y"]))
        if shared:
            if min((math.dist(c, (x, y)) for x, y, _p in wells), default=float("inf")) > WATER_REACH_FT:
                out.append(("farm_beyond_a_shared_well", _key(c)))
            continue
        fr = _frame(h)
        if channel:
            e = ends.get(_key(c))
            if e is None or not fr or abs(float(e[0]) - fr[0]) > fr[2] / 2 or abs(float(e[1]) - fr[1]) > fr[3] / 2:
                out.append(("farm_without_its_channel", _key(c)))
            continue
        mine = [(x, y) for x, y, p in wells if p and fr and abs(x - fr[0]) <= fr[2] / 2 and abs(y - fr[1]) <= fr[3] / 2]
        if not mine:
            out.append(("farm_without_its_well", _key(c)))
            continue
        door = front_door(h, FOOTPATH_FABRIC_GAP + 4.0)
        if door is not None and all(seg_dist(x, y, c, door) < 12.0 for x, y in mine):
            out.append(("well_in_the_way_in", _key(c)))
    return out


def bamboo_mismatch(M: Mapping[str, Any]) -> list[tuple[str, tuple[float, float]]]:
    """The farms whose grove draws bamboo but rolled no household stand, and the reverse (FR-019).

    Research: grove bamboo as rolled - research/questions/0075-bamboo-groves-chikurin.drawing.html: the grove draws bamboo exactly where the farm rolled a stand
    """
    rolled = {_key(p) for p in (M.get("meta") or {}).get("household_bamboo_in_grove_farms") or []}
    drawing = {_key(g["of"]) for g in M.get("groves") or [] if g.get("bamboo") and g.get("of")}
    return [("draws_unrolled", k) for k in sorted(drawing - rolled)] + [("rolled_undrawn", k) for k in sorted(rolled - drawing)]
