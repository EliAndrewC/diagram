"""The retirement house (inkyoya) - a second, smaller roof of one family in its own homestead (269 B42).

research/settlements/035-households-how-many-live-in-a-house-and-under-how-many-roofs-ie.html: a farm family took one
of two attested forms - the generations under one roof, or a farmhouse with a small retirement house in the same yard, with an
entrance of its own. A choice between forms, so the `family_form` knob rolls it per settlement from the map's seed and
declares it as `meta.family_form`. A retirement house belongs to its farmhouse's household - one family living as two
households - so it is recorded under its own key, `retirement_houses`, never in `houses`: it counts neither toward the
households nor against the band of occupied farmhouses (research/rendering/settlements/035-how-our-maps-count-and-draw-households.html).
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any

from l7r.diagram.settlement._knobs import Knob, knob_rng, register_knob

from .holds import release_held

if TYPE_CHECKING:
    from l7r.diagram.settlement import Settlement

    from ..plan import SitePlan

# THE TWO FAMILY FORMS (settlements/035). The record reads both and weighs neither against the other ("how the two forms
# are weighted against each other in the roll" is a GUESS), so the roll is even. `one_roof` is the default: it is the
# no-pin, no-roll fallback and what every map drew before the knob.
FAMILY_FORMS = ("one_roof", "retirement_house")
FAMILY_FORM = register_knob(Knob("family_form", list(FAMILY_FORMS), default="one_roof"))

# HOW MANY OF A SETTLEMENT'S HOMESTEADS KEEP ONE, where the custom is kept (settlements/035): "where the custom was kept
# thoroughly, every house had one", and no page read gives a share (the entry's absence note). A degree, so a band rolled
# per settlement: the top stops short of every house because a household holds a retired couple for only part of its
# cycle, and the bottom keeps the form legible on the sheet - both ends a GUESS.
RETIREMENT_SHARE = (0.30, 0.70)

# ITS SIZE (settlements/035 says "a small retirement house" and gives no dimension; no page read does). Three ken by two
# and a half, about eight tsubo - a room or two and an earth-floored entry, well under the farmhouse's 1,000-1,700 sq ft
# and a size apart from the 16 x 11 ft byre and the kura: a GUESS.
RETIREMENT_FT = (18.0, 15.0)

# WHERE IN THE YARD (settlements/035: "most retirement houses stood inside the family's house plot, with an entrance of
# their own"). How far from the farmhouse no page gives: one ken off the back wall or a flank, a second ken out when that
# is taken - the eaves drip and a path between the two roofs - is a GUESS. The front is the work yard and garden's.
RETIREMENT_GAP_FT = (6.0, 12.0)

# WHICH SIDE is a GUESS, rolled per homestead among the back wall and the two flanks. The record holds one lead
# (research/homesteads/260, wang-ochiai-2022): in Arakawa village, Shiga, under the Hira windstorms from the west, "Among the
# 11 retirement houses, 63.6% were located in a westerly direction", standing with the storage buildings as "wind fences"
# for the ground before the entrance. TRIED AND REVERTED (269 E8, settlement-review F1, 2026-09-28): the windward side first
# in 7 of 11 homesteads (the settlement's `SitePlan.wind`) seated 17 of 22 pool retirement houses to windward and every
# target still met, but it pressed them into the ground the village windbreak belt is laid on and re-laid the lane web, and
# three pool tests the rolled side passes went red - Inashiro's lanes ended in a 5.4 ft hook at (968, 650), Kuwabata's
# lanes split into two networks, and Mizuguchi's belt lost every judged depth bin. None of the three stood at a retirement
# house. One windstorm village carried to every settlement was already a liberty, and on these maps the wind fence is the
# belt, so the side stays rolled until the record finds the side beyond that village; the lane and belt measures that
# broke are recorded in specs/269-research-backfill/briefs/engine/log.md (B42).


def retirement_share(seed: int) -> float:
    """The settlement's share of homesteads keeping a retirement house, rolled once within `RETIREMENT_SHARE`."""
    lo, hi = RETIREMENT_SHARE
    return round(lo + knob_rng(seed, "retirement_house").random() * (hi - lo), 3)


def retirement_quota(s: Settlement, households: int) -> dict[str, float]:
    """The retirement house as a household's part (feature 287, homes H32 and plan D9): on the `retirement_house` form, the
    share the households' lots keep it at - at least one household, as the settlement always asked - and nothing on
    `one_roof`. The lots lay it in the bundle, off the back wall or a flank, before the fixtures (`fixture_seats`)."""
    if s.resolve("family_form") != "retirement_house":
        return {}
    return {"retirement": max(retirement_share(s.seed), 1.0 / max(1, households))}


def retirement_seats(h: Mapping[str, Any], w: float, d: float, gaps: Sequence[float], turn: int) -> list[tuple[float, float, float]]:
    """The candidate seats of a retirement house `w` wide and `d` deep off farmhouse `h`, as `(x, y, rot)`.

    In the house's own frame: the back wall and each flank, at each gap in turn; `turn` rotates the three sides so the
    houses of one hamlet do not all stand at the same bearing. The house is turned so its long side faces the farmhouse
    wall and its own door (drawn on its local +y face) opens AWAY from the farmhouse - its own entrance."""
    hw, hh, rot = float(h["w"]), float(h["h"]), float(h.get("rot", 0.0) or 0.0)
    hx, hy = float(h["x"]), float(h["y"])
    th = math.radians(rot)
    c, s = math.cos(th), math.sin(th)
    out: list[tuple[float, float, float]] = []
    for gap in gaps:
        sides = [(0.0, -(hh / 2 + gap + d / 2), 180.0), (hw / 2 + gap + d / 2, 0.0, -90.0), (-(hw / 2 + gap + d / 2), 0.0, 90.0)]
        k = turn % 3
        for lx, ly, face in sides[k:] + sides[:k]:
            out.append((hx + lx * c - ly * s, hy + lx * s + ly * c, rot + face))
    return out


def turned_box(w: float, d: float, rot: float) -> tuple[float, float]:
    """The axis-aligned extent of a `w` x `d` rectangle turned `rot` degrees."""
    c, s = abs(math.cos(math.radians(rot))), abs(math.sin(math.radians(rot)))
    return w * c + d * s, w * s + d * c


def retirement_glyph(cx: float, cy: float, w: float, d: float, rot: float) -> str:
    """A small thatched dwelling in the farmhouse's own vocabulary - the two-tone roof and its ridge - smaller, and with
    its door on the face away from the farmhouse (local +y)."""
    return (
        f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot:.2f})">'
        f'<rect x="{-w / 2:.1f}" y="{-d / 2:.1f}" width="{w:.1f}" height="{d / 2:.1f}" fill="#A98C58"/>'
        f'<rect x="{-w / 2:.1f}" y="0" width="{w:.1f}" height="{d / 2:.1f}" fill="#C9B07C"/>'
        f'<rect x="{-w / 2:.1f}" y="{-d / 2:.1f}" width="{w:.1f}" height="{d:.1f}" rx="2" fill="none" stroke="#5A4326" stroke-width="1.2"/>'
        f'<line x1="{-w * 0.28:.1f}" y1="0" x2="{w * 0.28:.1f}" y2="0" stroke="#E2CB98" stroke-width="1.5"/>'
        f'<rect x="-2.5" y="{d / 2 - 1.6:.1f}" width="5" height="2.6" fill="#5A4326" opacity="0.85"/>'
        "</g>"
    )


def retirement_houses(s: Settlement, plan: SitePlan) -> int:
    """Seat the retirement houses the settlement's family form asks for, and return how many were drawn.

    `family_form` is resolved and declared (`meta.family_form`); on `one_roof` nothing is drawn. On `retirement_house` a
    share of the households (`RETIREMENT_SHARE`, rolled, `meta.retirement_share`) is asked for (`meta.retirement_target`),
    the owners taken in an order rolled from the seed - a retired couple is a stage of a family's life, not a mark of its
    wealth - and each seated off its own farmhouse's back wall or a flank (`retirement_seats`, the side rolled), clear of everything but
    that farmhouse (the byre's annex test, which reads the placed index). A household with no room passes its turn to the
    next one. Each record's geometry is complete when appended, and names its farmhouse (`of`). WHERE THE HOUSEHOLDS WERE
    SEATED WITH THEIR LOTS (feature 287, homes H32, plan D9) nothing is sought: each keeper's house was laid in its bundle
    (`retirement_quota`, `fixture_seats`) and is drawn where it stands, so none is dropped - the search above is the
    path of a settlement seated without lots."""
    form = s.M["meta"]["family_form"] = s.resolve("family_form")
    s.M.setdefault("retirement_houses", [])
    if form != "retirement_house":
        return 0
    houses = [h for h in s.M.get("houses") or [] if h.get("kind") == "plain"]
    share = s.M["meta"]["retirement_share"] = retirement_share(s.seed)
    w, d = s.px(RETIREMENT_FT[0]), s.px(RETIREMENT_FT[1])
    # THE HOUSES THE SEATING LAID (feature 287, homes H32 and plan D9): where the households were seated with their lots,
    # each keeper's retirement house is a part of its homestead, laid inside the envelope that admitted it - drawn where it
    # stands, every one, the count the lots' quota
    if any("fixtures" in h for h in houses):
        laid = [(h, f) for h in houses for f in h.get("fixtures") or () if f["kind"] == "retirement"]
        s.M["meta"]["retirement_target"] = len(laid)
        for h, f in laid:
            release_held(s, "retirement_houses", f)  # held since the seating (`hold_laid_parts`, feature 287 M8)
            _draw_retirement(s, h, float(f["x"]), float(f["y"]), w, d, retirement_face(h, float(f["x"]), float(f["y"])))
        s.M["meta"]["retirement_houses"] = len(laid)
        return len(laid)
    rng = knob_rng(s.seed, "retirement_house")
    rng.random()  # the share's draw (`retirement_share`), so the order and the sides below roll as they always did
    target = s.M["meta"]["retirement_target"] = max(1, round(len(houses) * share)) if houses else 0
    order = sorted(houses, key=lambda h: (float(h["x"]), float(h["y"])))
    rng.shuffle(order)
    gaps = [s.px(g) for g in RETIREMENT_GAP_FT]
    seated = 0
    for h in order:
        if seated >= target:
            break
        for cx, cy, rot in retirement_seats(h, w, d, gaps, rng.randrange(3)):
            aw, ah = turned_box(w, d, rot)
            rec = {"x": round(cx, 1), "y": round(cy, 1), "w": round(w, 1), "h": round(d, 1), "rot": round(rot, 1), "of": [round(float(h["x"]), 1), round(float(h["y"]), 1)]}
            if s._byre_clear_of_all_but(cx, cy, aw, ah, h) and s.admits("retirement_houses", rec):  # ...and the registry (M8)
                _draw_retirement(s, h, cx, cy, w, d, rot)
                seated += 1
                break
    s.M["meta"]["retirement_houses"] = seated
    return seated


def retirement_face(h: Mapping[str, Any], x: float, y: float) -> float:
    """The turn a retirement house laid at (x, y) is drawn at: its farmhouse's, plus the face its seat takes off the back
    wall (180) or a flank (-90 east, 90 west) - its long side to the farmhouse wall, its door away (`retirement_seats`)."""
    rot = float(h.get("rot", 0.0) or 0.0)
    th = math.radians(rot)
    dx, dy = x - float(h["x"]), y - float(h["y"])
    lx, ly = dx * math.cos(th) + dy * math.sin(th), -dx * math.sin(th) + dy * math.cos(th)
    if ly < 0.0 and abs(ly) - float(h["h"]) / 2 >= abs(lx) - float(h["w"]) / 2:
        return rot + 180.0
    return rot + (-90.0 if lx > 0.0 else 90.0)


def _draw_retirement(s: Settlement, h: Mapping[str, Any], cx: float, cy: float, w: float, d: float, rot: float) -> None:
    aw, ah = turned_box(w, d, rot)
    s.add(retirement_glyph(cx, cy, w, d, rot), cls="retirement house")
    s.placed.append((cx, cy, aw, ah))
    s.M["retirement_houses"].append({"x": round(cx, 1), "y": round(cy, 1), "w": round(w, 1), "h": round(d, 1), "rot": round(rot, 1), "of": [round(float(h["x"]), 1), round(float(h["y"]), 1)]})
