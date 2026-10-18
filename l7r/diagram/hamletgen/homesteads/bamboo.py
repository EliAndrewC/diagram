"""Split from hamletgen/homesteads.py by feature 173 - see this package's CLAUDE.md for the index.

Research: strip geometry - NONE: frames, indexes and ground lookups; the units that decide carry their own claims
"""

from __future__ import annotations

import math
import os
from collections.abc import Iterator, Mapping, Sequence
from typing import Any, NamedTuple

from l7r.diagram.settlement import Settlement, point_in_poly, seg_dist, segments_cross
from l7r.diagram.settlement._geom import PointGrid, boxed_grid, boxed_ring_hit, boxed_rings, boxed_segs, indexed_grid
from l7r.diagram.settlement._geom.water_index import crosses_a_stream
from l7r.diagram.settlement.homestead_parts.bamboo_keepout import stand_spares_seats
from l7r.diagram.settlement.homestead_parts.fixture_seats import weighted
from l7r.diagram.settlement.homestead_parts.groves import HOUSEHOLD_BAMBOO_PREVALENCE as HOUSEHOLD_BAMBOO_PREVALENCE
from l7r.diagram.settlement.homestead_parts.tree_shade import BAMBOO_SHADE_FT
from l7r.diagram.settlement.land.wet import marsh_ground
from l7r.diagram.settlement.rolling.bearing import turned_box

from ..consts import Poly, Pt
from ..plan import SitePlan
from .household_ways import box_poly, seated_parts

# HOUSEHOLD BAMBOO (feature 133 T48, GM 2026-08-27; research/questions/0075-bamboo-groves-chikurin.html,
# the T48 pass). READ: on the Tonami plain every farmstead stood in its own
# grove (kainyo) and bamboo was one of its named species beside a dominant cedar, valued as "important
# daily-life material"; the bamboo stood WITH the storehouses on the plot's south side there, and at a
# plot's wet edge for its roots elsewhere; the grove as a whole faces the local wind (N+W, W, or S+W by
# region). THE WIND SIDE IS READ NOW, not summary-only (269 B29; research/questions/0075-bamboo-groves-chikurin.html): on the Tonami
# plain bamboo was often mixed into the grove from the west round to the north of the house, and the Sendai igune's
# bamboo filled its low part against the wind. So the SIDE is rolled per farmstead, weighted toward the back, the
# wind side and the shed's side, never fixed. The weights are a GUESS - no page gives a share per side; `wind` was
# raised from .15 to .30 when the wind side was read, taken from `back` and `shed`: `back` stays the likeliest, then
# `wind`, then `shed`, then the other flank.
# The PRESENCE rate is a GUESS - no source gives a share; "one of several secondary
# species" says common but not universal - set like the shed's, and labeled. Sizes are a working strip.
# HOUSEHOLD_BAMBOO_PREVALENCE lives with the grove drawer (settlement/homestead_parts/groves.py) since feature 291: a
# farm with its own grove draws its bamboo in that grove, so the drawing makes the same positional roll.
HOUSEHOLD_BAMBOO_FT = (22.0, 16.0)
"""Research: strip size - research/questions/0075-bamboo-groves-chikurin.drawing.html: 22 x 16 ft"""
_HOUSEHOLD_BAMBOO_SIDES = (("back", 0.35), ("shed", 0.25), ("wind", 0.30), ("side", 0.10))
"""Research: strip side - research/questions/0075-bamboo-groves-chikurin.html, research/questions/0075-bamboo-groves-chikurin.drawing.html: back 35, shed 25, wind 30, other flank 10 in 100"""


_DIAGONAL = math.sin(math.radians(22.5))  # a wind component past this on both axes is a diagonal wind (NW, not N)


def wind_seat(wlx: float, wly: float, hw: float, hh: float, gap: float, sw: float, sh: float) -> tuple[float, float, float, float]:
    """The windward strip's (center x, center y, w, h) in the house's frame, for a wind (`wlx`, `wly`) pointing where it
    comes FROM (269 B29). A diagonal wind seats it on the windward CORNER, a near-cardinal one on the windward FACE -
    either way `gap` clear of the walls. It used to scale the half-sizes by the wind's components, which for a diagonal
    wind put the strip's center ~0.7 of the way out and its body over the house's own corner: the near seat was refused
    on every NW-wind hamlet in the pool, so the side rolled "wind" fell through to another side and raising its weight
    moved nothing.

    Research: windward seat - research/questions/0075-bamboo-groves-chikurin.drawing.html: the windward corner for a diagonal wind, the windward face otherwise
    """
    if abs(wlx) > _DIAGONAL and abs(wly) > _DIAGONAL:
        return (math.copysign(hw / 2 + gap + sw / 2, wlx), math.copysign(hh / 2 + gap + sh / 2, wly), sw, sh)
    if abs(wly) >= abs(wlx):
        return (0.0, math.copysign(hh / 2 + gap + sh / 2, wly), sw, sh)
    return (math.copysign(hw / 2 + gap + sh / 2, wlx), 0.0, sh, sw)


def in_the_sun(cx: float, cy: float, w: float, h: float, sun: Sequence[tuple[float, float, float, float]]) -> bool:
    """Does the `w` x `h` rect centered (`cx`, `cy`) overlap any sun box (center x, center y, half-w, half-h) in `sun`?"""
    return any(abs(cx - bx) < w / 2 + bw and abs(cy - by) < h / 2 + bh for bx, by, bw, bh in sun)


def household_bamboo(
    s: Settlement,
    plan: SitePlan,
    houses: Sequence[Mapping[str, Any]],
    parts: Sequence[Poly] = (),
    belt: Sequence[Pt] | None = None,
    skip: frozenset[tuple[float, float, float, float]] = frozenset(),
) -> list[Poly]:
    """Seat a small bamboo strip beside each farmstead that keeps one, per the `bamboo` knob.

    Seated by `seat_strips` in `stage_hinterland`, AFTER the web and before the scrub (T49): seated with the sheds it was in the
    web's way. Feature 374 wave 149 seated it ahead of the ways five ways - laid in the bundle with the sheds and beds (with and
    without the copse seats kept off it, and a way kept 7 ft off its own beds) and at the seating's end - and each re-dealt the
    seats or the ways and moved a refusal into the pool or the cohort (`m:w149-route-matrix`); the round arbiter ruled the order
    kept (ask:b13-w149-route-matrix), the row waiting on the web settle. Clear of every placed part by itself (`parts`, each kept
    `PART_GAP_FT` off) and of the belt (`belt`), 6 ft off every lane, and held as fabric for what is laid after. The scrub keeps
    out of it (a soft keep-out, like every wood). Drawn by `stage_bamboo` with the stand glyph. Per house: presence by `HOUSEHOLD_BAMBOO_PREVALENCE`, side by the weighted roll
    above, both from the house's own position (positional randomness). A candidate that lands on a
    footprint, a lane, a paddy, the marsh or the pond is refused and the next side tried; a farmstead
    with no room keeps none. Returns the count seated.

    Research:
        which farms keep bamboo - research/questions/0075-bamboo-groves-chikurin.drawing.html: `HOUSEHOLD_BAMBOO_PREVALENCE` by each house's position hash
        strip size - research/questions/0075-bamboo-groves-chikurin.drawing.html: `HOUSEHOLD_BAMBOO_FT`, a strip 22 x 16 ft
        side rolled, then the others - research/questions/0075-bamboo-groves-chikurin.drawing.html: the weighted side first, the rest in listed order
        a grove farm's bamboo in its grove - research/questions/0075-bamboo-groves-chikurin.drawing.html: no strip, counted for the grove
        strip clearances - UNRESEARCHED: 6 ft off the walls and every lane, `PART_GAP_FT` off every seated part
        strip out of the sun - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: kept 50 ft (bamboo's reach) off every yard's and bed's sun
        strip off the copse seats - UNRESEARCHED: off every household's reserved copse seats by the bamboo keep-out
        strip on its house's bank - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: refused across a stream
        strip seated after the lanes - CANON: seated after the web; no page gives an order, and the GM ruled it an implementation detail (2026-10-12: "the ordering is an implementation detail") so long as no lane crosses a strip
        a stepped strip its own farm's - UNRESEARCHED: none seated nearer another house's center than its own
        row farm's bamboo to the south - research/questions/0033-row-villages-resson.drawing.html, research/questions/0075-bamboo-groves-chikurin.drawing.html: on a
            row village that rolled the second form and a map whose farmsteads keep bamboo, every farm the grove row across its street shelters
            keeps it, a band along its south side (`south_band`)
    """
    out: list[Poly] = []
    keeps = plan.bamboo in ("homestead", "both")
    if not houses or not keeps:
        return out
    px = s.px
    fields = [list(f) for f in s.field_polys]
    marsh = marsh_ground(s.M)
    lanes = [([(float(a), float(b)) for a, b in ln["pts"]], float(ln.get("w", 3)) / 2 + px(6.0)) for ln in s.M.get("lanes", []) if len(ln.get("pts") or []) >= 2]
    ground = StripGround(
        fields=fields,
        marsh=marsh,
        pond=s.M.get("pond"),
        lanes=lanes,
        footing=Footing(s, fields, marsh),  # the static ground, indexed once for every strip this pass tests (feature 218)
        seats=[(float(p[0]), float(p[1])) for q in s.M.get("houses") or [] for p in (q.get("wood_share") or {}).get("seats") or ()],
        # ...AND EVERY PLOT'S SUN GROUND at bamboo's reach (feature 315): gathered once - every plot stands, as seated or drawn
        sun=s._sun_keepouts((-1e9, -1e9, 1e9, 1e9), BAMBOO_SHADE_FT),
        belt=plan.belt if belt is None else belt,
        skip=skip,
        near=StripNear(s, lanes),  # what stands, filed once for the pass (feature 387)
    )
    centers = [(float(q["x"]), float(q["y"])) for q in houses]
    meta = s.M["meta"]
    for h in houses:
        hx, hy = float(h["x"]), float(h["y"])
        # A SHELTERED ROW FARM KEEPS ITS BAMBOO WHERE THE FARMSTEADS DO (374 wave 153): always, not three in five, but never on a map
        # whose knob gave its farmsteads none - "none" is the cold upland where madake does not grow (0075)
        if not h.get("sheltered") and s._hjit(hx, hy, 95.0) >= HOUSEHOLD_BAMBOO_PREVALENCE:
            continue
        # A FARM WITH ITS OWN GROVE KEEPS ITS BAMBOO IN THAT GROVE (feature 291; research/contents.json#vegetation
        # "Bamboo groves (chikurin)"). Its deep windward bands draw
        # the windbreak mix, which carries the bamboo; a separate strip would stand exactly where the grove already does -
        # and did not: once the dispersed and linear forms rolled again, every seat (back, shed, side, wind) lay in the
        # grove and Kashikawa's 12 expected strips silently became 0. Counted, so the knob's household half is on record.
        if (h.get("geom") or {}).get("groves") and not h.get("sheltered"):  # a sheltered row farm's bamboo is its south band (374 wave 153)
            meta["household_bamboo_in_grove"] = int(meta.get("household_bamboo_in_grove", 0)) + 1
            meta.setdefault("household_bamboo_in_grove_farms", []).append([round(hx, 1), round(hy, 1)])  # which, for `row_rules.bamboo_mismatch`
            continue
        offers = south_band(h, px) if h.get("sheltered") else strip_candidates(h, plan.wind, px, s._hjit(hx, hy, 96.0))
        mine = own_ground(ground, s.M.get("lanes", []), (hx, hy)) if h.get("sheltered") else ground
        for cx, cy, cw, ch in offers:
            if strip_refused(s, cx, cy, cw, ch, (hx, hy), mine, parts):
                continue
            # A STEPPED-OUT SEAT STAYS ITS OWN FARMSTEAD'S: none nearer another house's center than its own (the round-3 decide
            # of feature 374 wave 149 - 54 ft out, a strip could stand at a neighbor's door)
            if min(centers, key=lambda c: math.dist(c, (cx, cy))) != (hx, hy):
                continue
            ring = [(cx - cw / 2, cy - ch / 2), (cx + cw / 2, cy - ch / 2), (cx + cw / 2, cy + ch / 2), (cx - cw / 2, cy + ch / 2)]
            plan.bamboo_of[len(plan.bamboo_polys) + len(out)] = (hx, hy)  # its owner, for the stand's record (`of`)
            out.append(ring)
            plan.bamboo_roles.append("homestead")
            s.placed.append((cx, cy, cw, ch))
            s.block_polys.append(ring)
            break
    return out


BAND_STEPS_OUT = 6
"""Research: the band stepped further south - GUESS research/questions/0075-bamboo-groves-chikurin.drawing.html: moved further south when its ground is taken, how far a GUESS; room before packing (the GM, 2026-10-12), out to six strip depths past its
plots' sun ground (96 ft), where a strip steps three; still its own farmstead's (none nearer another house's center)"""


def own_ground(ground: StripGround, lanes: Sequence[Mapping[str, Any]], house: Pt) -> StripGround:
    """The strip ground with the lanes that serve `house` itself - its own door path - left out of the lanes a band may not stand
    across from its house: a farm's own path to its street runs between its house and its south bamboo, as the path to a farm's
    front does (feature 374 wave 153: every sheltered band on valley seed 3 stood across its own door path).

    Research: its own path no bar - UNRESEARCHED: the household's own door path parts no farm from its bamboo; a public lane still does"""
    keep = [k for k, ln in enumerate(ln for ln in lanes if len(ln.get("pts") or []) >= 2) if not (ln.get("serves") and math.dist((float(ln["serves"][0]), float(ln["serves"][1])), house) < 0.5)]
    return ground._replace(lanes=[ground.lanes[k] for k in keep if k < len(ground.lanes)])


def south_band(h: Mapping[str, Any], px: Any) -> Iterator[tuple[float, float, float, float]]:
    """A sheltered row farm's bamboo seats, first choice first, each (cx, cy, w, h): a band along its whole south side - as wide
    as the farmstead's frame, a strip deep - just past its plots' sun ground, then stepped further south a strip's depth at a
    time (`BAND_STEPS_OUT`), true south whatever the map's wind; a farmstead-wide span is stepped all the way south before a
    narrower one is tried (`band_spans`), as the page moves the band before it gives it up (feature 374 wave 153: the glyph
    check found bands only the house-and-beds wide, a third of a 222-249 ft farm, floating between two farms).

    Research:
        a madake grove along its south side - research/questions/0033-row-villages-resson.drawing.html, research/questions/0075-bamboo-groves-chikurin.html: the bamboo set south where the row across broke the wind, all along the farm's south side, as wide as the farmstead
        the band's depth - GUESS: a farm's bamboo strip's 16 ft (`HOUSEHOLD_BAMBOO_FT`)
        past the plots' sun - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: no canopy, bamboo included, within 50 ft south of a yard or bed (`BAMBOO_SHADE_FT`)
        stepped further south - GUESS research/questions/0075-bamboo-groves-chikurin.drawing.html: moved further south when its ground is taken, a strip's depth a step, out to `BAND_STEPS_OUT`"""
    g = h.get("geom") or {}
    boxes = [b for b in ([g.get("house")] + [g.get("yard")] + list(g.get("gardens") or ())) if b]
    if not boxes:
        return
    spans = band_spans(g, boxes)
    south = max(float(b[1]) + float(b[3]) / 2 for b in boxes)
    depth = px(HOUSEHOLD_BAMBOO_FT[1])
    for west, east in spans:
        for k in range(BAND_STEPS_OUT + 1):
            yield ((west + east) / 2, south + px(BAMBOO_SHADE_FT) + px(1.0) + depth / 2 + k * depth, east - west, depth)


def band_spans(g: Mapping[str, Any], boxes: Sequence[Sequence[float]]) -> list[tuple[float, float]]:
    """The (west, east) spans a sheltered farm's south band is offered, widest first, each once: the frame's whole width (its
    `bbox`), then the frame between its west- and east-facing grove bands - each as wide as the farmstead. A farm with no
    frame is offered its house, yard and beds across.

    Research:
        as wide as the farmstead - research/questions/0075-bamboo-groves-chikurin.drawing.html, research/questions/0033-row-villages-resson.drawing.html: a band as wide as the farmstead, all along its south side
        inside its own side groves - UNRESEARCHED: the frame less its west and east grove bands, the farmstead's width within its grove
        a farm with no frame - UNRESEARCHED: its house, yard and beds across"""
    own = (min(float(b[0]) - float(b[2]) / 2 for b in boxes), max(float(b[0]) + float(b[2]) / 2 for b in boxes))
    bbox = g.get("bbox")
    if not bbox:
        return [own]
    fw, fe = float(bbox[0]) - float(bbox[2]) / 2, float(bbox[0]) + float(bbox[2]) / 2
    side = {(int(f[0]), int(f[1])): float(r[2]) for r, (f, _d) in zip(g.get("groves") or (), g.get("grove_faces") or (), strict=False)}
    inner = (fw + side.get((-1, 0), 0.0), fe - side.get((1, 0), 0.0))
    out: list[tuple[float, float]] = []
    for s in ((fw, fe), inner):
        if s[1] - s[0] > 0 and s not in out:
            out.append(s)
    return out


class StripGround(NamedTuple):
    """What a strip is tested against, gathered once per pass (`household_bamboo`): the paddy, the marsh and the pond, the
    lanes standing (with their 6 ft), the footing index, the reserved copse seats, the plots' sun at bamboo's reach, the belt
    and the bundle boxes to excuse.

    Research: strip ground - NONE: the ground gathered once for the strip tests"""

    fields: Sequence[Poly]
    marsh: Sequence[Poly]
    pond: Any
    lanes: Sequence[tuple[Poly, float]]
    footing: Footing
    seats: Sequence[Pt]
    sun: Sequence[tuple[float, float, float, float]]
    belt: Sequence[Pt] | None
    skip: frozenset[tuple[float, float, float, float]]
    near: StripNear


def strip_candidates(h: Mapping[str, Any], wind: Pt, px: Any, roll: float) -> Iterator[tuple[float, float, float, float]]:
    """A farm's strip seats, first choice first, each (cx, cy, w, h): the side `roll` picks first, then the others in listed
    order, each against the house and stepped out (`STRIP_SEATS`).

    Research:
        side rolled, then the others - research/questions/0075-bamboo-groves-chikurin.drawing.html: the weighted side first, the rest in listed order
        the shed side - UNRESEARCHED: local -x, the doma and stable end, or behind the house where the kura stands on the north wall
        the near seat - UNRESEARCHED: 6 ft off the wall, the strip's long side along it"""
    hx, hy, hw, hh = float(h["x"]), float(h["y"]), float(h["w"]), float(h["h"])
    sw, sh = px(HOUSEHOLD_BAMBOO_FT[0]), px(HOUSEHOLD_BAMBOO_FT[1])
    th = math.radians(float(h.get("rot", 0.0)))
    ca, sa = math.cos(th), math.sin(th)
    gap = px(6.0)
    shed_side = h.get("shed_side", "W")
    local = {
        "back": (0.0, -(hh / 2 + gap + sh / 2), sw, sh),
        "shed": ((-(hw / 2 + gap + sh / 2)) if shed_side != "N" else 0.0, 0.0 if shed_side != "N" else -(hh / 2 + gap + sh / 2), sh if shed_side != "N" else sw, sw if shed_side != "N" else sh),
        "side": (hw / 2 + gap + sh / 2, 0.0, sh, sw),
        "wind": wind_seat(wind[0] * ca + wind[1] * sa, -wind[0] * sa + wind[1] * ca, hw, hh, gap, sw, sh),  # the wind in the house's frame
    }
    first = weighted(_HOUSEHOLD_BAMBOO_SIDES, roll)
    for name in [first] + [nm for nm, _ in _HOUSEHOLD_BAMBOO_SIDES if nm != first]:
        lx0, ly0, cw, ch = local[name]
        d = math.hypot(lx0, ly0) or 1.0
        for k, j in STRIP_SEATS:
            lx, ly = lx0 + lx0 / d * k * sh - ly0 / d * j * sw, ly0 + ly0 / d * k * sh + lx0 / d * j * sw
            yield (hx + lx * ca - ly * sa, hy + lx * sa + ly * ca, cw, ch)


def strip_refused(s: Settlement, cx: float, cy: float, cw: float, ch: float, house: Pt, ground: StripGround, parts: Sequence[Poly]) -> bool:
    """Is the strip `cw` x `ch` at (cx, cy) refused - on a footprint, the paddy, the marsh, the pond, the water or a crown
    (`_strip_blocked`), in the belt, on a seated part (`PART_GAP_FT`), on a reserved copse seat, in a plot's sun, across a
    stream or a lane from its `house`?

    Research:
        strip clearances - UNRESEARCHED: 6 ft off the walls, `PART_GAP_FT` off every seated part
        strip out of the sun - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: kept 50 ft (bamboo's reach) off every yard's and bed's sun
        strip off the copse seats - UNRESEARCHED: off every household's reserved copse seats by the bamboo keep-out
        strip on its house's bank - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: refused across a stream
        no strip in the belt - UNRESEARCHED: no strip with its center or a corner inside the belt (`in_belt`)
        the strip on its house's side of a lane - UNRESEARCHED: no lane's centerline between a house and its strip (`across_a_lane`)"""
    hx, hy = house
    g = ground
    if _strip_blocked(s, cx, cy, cw, ch, hx, hy, g.fields, g.marsh, g.pond, g.lanes, g.footing, g.skip, near=g.near) or in_belt(g.belt, cx, cy, cw, ch):
        return True
    if parts_hit(cx, cy, cw, ch, parts, s.px(PART_GAP_FT)):  # a homestead as seated, its own included
        return True
    # ...and off every household's reserved copse seats by the copse's bamboo keep-out (feature 280's copse off the bamboo, feature
    # 287 woods W25's seats planted where reserved - `stand_spares_seats`); the strip is drawn axis-aligned in (cw, ch) at (cx, cy)
    if not stand_spares_seats(cx, cy, cw, ch, g.seats, s.bscale):
        return True
    if in_the_sun(cx, cy, cw, ch, g.sun):  # a stand throws a timber bamboo's shadow: none in a yard's or bed's sun (feature 315)
        return True
    # the household's strip stands on its house's bank (feature 287, homes H01) ...and on its house's side of every lane (glyph
    # check, feature 302: Sawada's strip across a lane)
    return crosses_a_stream((hx, hy), (cx, cy), s.M.get("streams", [])) or across_a_lane((hx, hy), (cx, cy), g.lanes)


STRIP_STEPS_OUT = 3
"""How many strip depths past its near seat a strip is offered, each also slid one strip's width along its side either way: out to
6 + 3 x 16 = 54 ft off the wall. The farmstead's own parts stand where the near seat often is (feature 374 wave 149: with the
bundle box no longer refusing every strip, the near seat and one step out seated 2 of the 69 strips the roll asked over 20 cohort
seeds, a probe; out to three steps with the slides 29). The rest find no room: the strip as a part the bundle packer lays is
filed with the five-route matrix (`m:w149-route-matrix`).

Research: strip reach - GUESS research/questions/0075-bamboo-groves-chikurin.drawing.html: stepped out until it stands clear, 38 to 54 ft off the wall, a GUESS the page names"""

STRIP_SEATS = tuple((float(k), float(j)) for k in range(STRIP_STEPS_OUT + 1) for j in (0, 1, -1))
"""Research:
    strip seats - GUESS research/questions/0075-bamboo-groves-chikurin.drawing.html: each step out, the side's own seat first
    the slide along the side - UNRESEARCHED: slid one strip's width one way and the other; the page gives no slide"""

PART_GAP_FT = 2.0
"""How far a strip keeps off a homestead's seated part - the gap `_strip_blocked` keeps off a placed box.

Research: off the seated parts - UNRESEARCHED: 2 ft, the gap a strip keeps off any placed box"""


def parts_hit(cx: float, cy: float, cw: float, ch: float, parts: Sequence[Poly], gap: float) -> bool:
    """Does the `cw` x `ch` strip centered (`cx`, `cy`) come within `gap` of any part's box (its ring's bounding box)?

    Research: off the seated parts - UNRESEARCHED: the strip and a part's box, `gap` apart"""
    for ring in parts:
        xs, ys = [p[0] for p in ring], [p[1] for p in ring]
        if cx + cw / 2 + gap > min(xs) and cx - cw / 2 - gap < max(xs) and cy + ch / 2 + gap > min(ys) and cy - ch / 2 - gap < max(ys):
            return True
    return False


def seat_strips(s: Settlement, plan: SitePlan) -> int:
    """Seat the farms' bamboo strips (`stage_hinterland`, after the web): against every homestead's part by itself (`seated_parts`,
    and each grove farm's bands) and the belt (`plan.belt`); added to the plan's stands and held as fabric for what is laid
    after (`s._household_strips`, read by `fabric._homestead_polys`), and the farms that rolled one recorded with how many found
    no room (`meta.household_bamboo_wanted` / `_no_room`, feature 374 wave 149). Returns the count seated.

    Research:
        strip seated after the lanes - CANON: seated after the web; no page gives an order, and the GM ruled it an implementation detail (2026-10-12: "the ordering is an implementation detail") so long as no lane crosses a strip
        off the grove farms' bands - UNRESEARCHED: every grove farm's band a part the strip keeps off
        the ground between held clear - UNRESEARCHED: the strip and its hull to the house held as fabric for the lanes laid after"""
    from ..hinterland.belt import belt_polygon  # local: the hinterland imports this package

    parts = [p for p, _own, kind in seated_parts(s) if kind != "wood seats"]  # the wood seats: `stand_spares_seats`, as before
    parts += [box_poly(b) for h in s.M.get("houses") or [] for b in (h.get("geom") or {}).get("groves") or () if len(b) == 4]
    # ...EACH PART BY ITSELF, SO NOT THE BUNDLES THEY STAND IN (`skip`): a household's placed box is its whole bundle, which takes in
    # the ground beside its house where its strip would go - so every strip on every map was refused by its own farm (cohort
    # seeds 2, 3, 5 and 6: 53 seats refused, none by the sun or the parts; the pool drew none - feature 374 wave 149). The strips
    # seated here stay walls to one another, being placed after the set is taken.
    houses = s.M.get("houses") or []
    bundles = frozenset((float(b[0]), float(b[1]), float(b[2]), float(b[3])) for h in houses if len(b := (h.get("geom") or {}).get("bbox") or ()) == 4)
    n0 = len(plan.bamboo_polys)
    strips = household_bamboo(s, plan, houses, parts=parts, belt=plan.belt or belt_polygon(s, plan), skip=bundles)
    plan.bamboo_polys += strips
    # ...THE STRIP AND THE GROUND BETWEEN IT AND ITS HOUSE (`between`): no lane runs between a house and its bamboo (feature 302's
    # glyph check of Sawada, `across_a_lane`) - the lanes laid after the strip keep off that ground as the strip kept off theirs
    held = [(ring, None, "bamboo_stands") for ring in strips]
    held += [(between(plan.bamboo_of[n0 + k], ring), None, "bamboo_stands") for k, ring in enumerate(strips) if n0 + k in plan.bamboo_of]
    s._household_strips = held  # type: ignore[attr-defined]
    want = household_bamboo_wanted(s, plan, houses)
    s.M["meta"]["household_bamboo_wanted"] = want
    s.M["meta"]["household_bamboo_no_room"] = want - len(strips)
    return len(strips)


def household_bamboo_wanted(s: Settlement, plan: SitePlan, houses: Sequence[Mapping[str, Any]]) -> int:
    """How many farms roll a strip of their own: the `bamboo` knob keeps one, the farm rolls one (`HOUSEHOLD_BAMBOO_PREVALENCE`
    by its position) and keeps no grove of its own (whose bamboo is in the grove).

    Research:
        which farms keep bamboo - research/questions/0075-bamboo-groves-chikurin.drawing.html: `HOUSEHOLD_BAMBOO_PREVALENCE` by each house's position hash
        a sheltered row farm keeps bamboo - research/questions/0033-row-villages-resson.drawing.html, research/questions/0075-bamboo-groves-chikurin.drawing.html: the bamboo set south where a row of grove farms across the road broke the wind, on a map whose farmsteads keep bamboo"""
    if plan.bamboo not in ("homestead", "both"):
        return 0
    return sum(1 for h in houses if h.get("sheltered") or (s._hjit(float(h["x"]), float(h["y"]), 95.0) < HOUSEHOLD_BAMBOO_PREVALENCE and not (h.get("geom") or {}).get("groves")))


def between(house: Pt, strip: Sequence[Pt]) -> Poly:
    """The ground between a house's center and its strip: the convex hull of the center and the strip's corners.

    Research: no lane between a house and its bamboo - UNRESEARCHED: the hull of the house's center and the strip's corners; no page says how far a lane keeps off a farm's bamboo"""
    from shapely.geometry import (
        MultiPoint,  # noqa: PLC0415
        Polygon,  # noqa: PLC0415
    )

    hull = MultiPoint([(float(house[0]), float(house[1])), *((float(p[0]), float(p[1])) for p in strip)]).convex_hull
    ring = hull.exterior.coords if isinstance(hull, Polygon) else hull.coords  # a strip in line with its house: no area, its line
    return [(float(x), float(y)) for x, y in list(ring)[: -1 if isinstance(hull, Polygon) else None]]


def across_a_lane(house: Pt, strip: Pt, lanes: Sequence[tuple[Poly, float]]) -> bool:
    """Does a lane run between a house and its bamboo strip - the line from the house's center to the strip's crossing a lane's
    centerline? The household's bamboo grows in its own grove (research/vegetation/150): the glyph check of Sawada (feature 302)
    found a strip 6.7 ft past a 3 ft lane from its house, which the stream test (`crosses_a_stream`, homes H01) never asked.

    Research: the strip on its house's side of a lane - research/questions/0075-bamboo-groves-chikurin.html: the household's own bamboo, no lane between
    """
    return any(segments_cross(house, strip, a, b) for pts, _half in lanes for a, b in zip(pts, pts[1:], strict=False))


def in_belt(belt: Sequence[Pt] | None, cx: float, cy: float, cw: float, ch: float) -> bool:
    """Does a household strip centered (cx, cy), cw x ch, reach into the windbreak belt (its center or a corner inside)? The
    stands are drawn after the belt's crowns, so a strip in the belt painted its culms over the conifers - the reverse of the
    belt's own order, conifers over the bamboo between them (269 B30; settlement-review of Inashiro, feature 280).

    Research: no strip in the belt - UNRESEARCHED: no strip seated with its center or a corner inside the belt
    """
    if not belt or len(belt) < 3:
        return False
    pts = [(cx, cy)] + [(cx + sx * cw / 2, cy + sy * ch / 2) for sx in (-1.0, 1.0) for sy in (-1.0, 1.0)]
    return any(point_in_poly(x, y, list(belt)) for x, y in pts)


class Footing:
    """The static ground a household strip or a tree trunk is tested against, indexed ONCE per pass
    (feature 218). `_strip_blocked` and `_trunk_blocked` used to walk every edge of every paddy and
    marsh polygon per corner of every candidate, and asked `_on_watercourse` with no `near`, which
    REBUILT the watercourse segment list (the laterals re-split into taper pieces) on every corner -
    210 rebuilds and 0.55 s of profiled time on the reference roll's 1,064 strip tests. A caller
    builds one of these after it gathers `fields` and `marsh` and passes it in; a call without one
    builds its own (slower, never wrong), which is what keeps the old positional signature and its
    unit tests valid. The rings carry the wider of the two pads the callers apply (6 ft for a paddy
    or the marsh, 3 ft for a dry plot); the exact tests are the ones each caller ran."""

    __slots__ = ("dry", "rings", "water")

    def __init__(self, s: Settlement, fields: Sequence[Poly], marsh: Sequence[Poly]) -> None:
        self.rings: PointGrid = boxed_grid(boxed_rings([p for p in list(fields) + list(marsh) if len(p) >= 3], 6.0))
        dry = [[(float(a), float(b)) for a, b in o.get("poly") or []] for o in s.M.get("dry_plots", [])]
        self.dry: PointGrid = boxed_grid(boxed_rings([p for p in dry if len(p) >= 3], 3.0))
        self.water: PointGrid = boxed_grid(boxed_segs(s._watercourse_segs(4.0)))

    def on_water(self, s: Settlement, x: float, y: float) -> bool:
        """`_on_watercourse(x, y, pad=4.0)`, answered from the grid - the crescent pond still by `s`."""
        return s._on_watercourse(x, y, pad=4.0, near=self.water.near)


_KINDS = ("wells", "kosatsuba", "byres", "farm_sheds", "retirement_houses")  # everything seated between the sheds and the strips (T49)


class StripNear:
    """What stands near a candidate strip, filed ONCE per pass (feature 387, plan D5) - the placed boxes, every farmhouse's turned
    box, the wells, notice board, byres, sheds and retirement houses, each lane segment and each drawn crown - so `_strip_blocked`
    tests the items near the strip, not every item on the map (1,102 candidates at 40 households asked 693,184 items of the
    straight scan, `m:counts-before`). A PREFILTER: the grid hands back every item whose box comes within the strip's reach
    (and some that do not); the exact test each item met before still decides, so the verdict is the straight scan's.

    `s.placed` is the one thing the pass adds to as it runs (each seated strip a wall to the next), so its grid is the
    registry's own (`indexed_grid`, extended on an append, rebuilt on anything else); the rest is filed at construction. Under
    `L7R_CHECK_CACHES=1` (the suite) each query checks those still hold what was filed and raises if not.

    Research:
        what a strip keeps off, found near it - NONE: plumbing; the clearances are `_strip_blocked`'s claims
        a fixture with no recorded size - UNRESEARCHED: taken as 16 ft across (`r` 8), as `_strip_blocked` always took it"""

    __slots__ = ("_filed", "crowns", "houses", "kinds", "lanes", "s", "segs")

    def __init__(self, s: Settlement, lanes: Sequence[tuple[Poly, float]]) -> None:
        self.s, self.lanes = s, lanes
        houses = []
        for o in s.M.get("houses", []):
            ox, oy = float(o["x"]), float(o["y"])
            _, _, ow, oh = turned_box((ox, oy, float(o["w"]), float(o["h"])), float(o.get("rot", 0.0)))
            houses.append((ox, oy, ow, oh, ox - ow / 2, oy - oh / 2, ox + ow / 2, oy + oh / 2))
        self.houses = boxed_grid(houses)
        kinds = []
        for key in _KINDS:
            for o in s.M.get(key, []):
                ow, oh = float(o.get("w", 2 * float(o.get("r", 8)))), float(o.get("h", 2 * float(o.get("r", 8))))
                x, y = float(o["x"]), float(o["y"])
                kinds.append((x, y, ow, oh, x - ow / 2, y - oh / 2, x + ow / 2, y + oh / 2))
        self.kinds = boxed_grid(kinds)
        segs = []
        for lane in lanes:
            pts, half = lane
            for k in range(len(pts) - 1):
                a, b = pts[k], pts[k + 1]
                segs.append((lane, a, b, min(a[0], b[0]) - half, min(a[1], b[1]) - half, max(a[0], b[0]) + half, max(a[1], b[1]) + half))
        self.segs = boxed_grid(segs)
        tc = s.M.get("tree_crowns") or []
        crowns = []
        for k in range(0, len(tc) - 2, 3):
            tx, ty, r = float(tc[k]), float(tc[k + 1]), float(tc[k + 2]) + 0.6
            crowns.append((tx, ty, float(tc[k + 2]), tx - r, ty - r, tx + r, ty + r))
        self.crowns = boxed_grid(crowns)
        self._filed = self._state()

    def _state(self) -> tuple[Any, ...]:
        M = self.s.M
        return (*(getattr(M.get(k), "version", len(M.get(k) or ())) for k in ("houses", *_KINDS)), len(M.get("tree_crowns") or ()), len(self.lanes))

    def placed(self) -> PointGrid:
        """The placed boxes, from `s.placed`'s own versioned grid."""

        def build(lst: Any) -> PointGrid:
            grid = PointGrid()
            add(grid, lst)
            return grid

        def add(grid: PointGrid, items: Any) -> None:
            grid.extend((*b[:4], float(b[0]) - float(b[2]) / 2, float(b[1]) - float(b[3]) / 2, float(b[0]) + float(b[2]) / 2, float(b[1]) + float(b[3]) / 2) for b in items)

        return indexed_grid(self.s.placed, "strip_near_placed", build, add)

    def check(self) -> None:
        """Under the suite: the registries filed once still hold what was filed."""
        if os.environ.get("L7R_CHECK_CACHES") and self._state() != self._filed:
            raise AssertionError(f"StripNear is stale: what it filed changed mid-pass ({self._filed} -> {self._state()})")

    def count(self, cx: float, cy: float, cw: float, ch: float) -> int:
        """How many items a strip here is tested against (SC-001's count)."""
        pad = max(cw, ch) / 2 + 6.0
        return sum(len(g.near(cx, cy, pad)) for g in (self.placed(), self.houses, self.kinds, self.segs, self.crowns))


def _strip_blocked(
    s: Settlement,
    cx: float,
    cy: float,
    cw: float,
    ch: float,
    hx: float,
    hy: float,
    fields: Sequence[Poly],
    marsh: Sequence[Poly],
    pond: Any,
    lanes: Sequence[tuple[Poly, float]],
    footing: Footing | None = None,
    skip: frozenset[tuple[float, float, float, float]] = frozenset(),
    *,
    near: StripNear,
) -> bool:
    """Would a household bamboo strip centered here stand on something? Its own farmhouse is not something, and neither
    is a reserved box in `skip` (a caller whose parts are each registered passes the homestead BUNDLE boxes: feature 261,
    the fixtures pass, where a steading's own bundle and a neighbor's refused the open ground of its flanks).

    Research:
        off the paddy - research/questions/0075-bamboo-groves-chikurin.drawing.html: no stand on a paddy
        what a strip or fixture keeps off - UNRESEARCHED: the pads, 2 ft off placed boxes and houses, 6 ft off wells and sheds and paddy or marsh, 3 ft off dry plots, off water and crowns, 20 ft past the pond
        no lane across it - research/questions/0075-bamboo-groves-chikurin.drawing.html: no lane or well is drawn across a strip; a tread within its half-width of a corner, or crossing an edge, refuses it
        off the notice board, byres and retirement houses - UNRESEARCHED: 6 ft off each, as off wells and sheds
    """
    if cx - cw / 2 < 30 or cy - ch / 2 < 30 or cx + cw / 2 > s.W - 30 or cy + ch / 2 > s.H - 30:
        return True
    ft = footing or Footing(s, fields, marsh)  # a caller that tests many seats builds one and passes it (feature 218)
    corners = [(cx - cw / 2, cy - ch / 2), (cx + cw / 2, cy - ch / 2), (cx + cw / 2, cy + ch / 2), (cx - cw / 2, cy + ch / 2), (cx, cy)]
    near.check()
    reach = max(cw, ch) / 2 + 6.0  # past every margin a test below keeps (2 and 6 ft), the lanes' own half-widths filed in their boxes
    for px_, py_, pw, ph, *_ in near.placed().near(cx, cy, reach):
        if (px_ == hx and py_ == hy) or (px_, py_, pw, ph) in skip:
            continue
        if abs(cx - px_) < (cw + pw) / 2 + 2 and abs(cy - py_) < (ch + ph) / 2 + 2:
            return True
    # EVERY OTHER FARMHOUSE, as drawn: a caller that passes the bundle boxes in `skip` excuses a neighbor's bundle, and on a
    # map whose houses carry no separate placed box that excused the neighbor's house as well - Kuwabata's woodpile landed
    # on the next house's gable once the 269 landing's bearing fix moved the row (the retired finished-map overlap test; since
    # feature 287 M8 the registry of what stands refuses it at record time, `overlap/registry.py`).
    for ox, oy, ow, oh, *_ in near.houses.near(cx, cy, reach):
        if abs(ox - hx) < 0.5 and abs(oy - hy) < 0.5:
            continue
        if abs(cx - ox) < (cw + ow) / 2 + 2 and abs(cy - oy) < (ch + oh) / 2 + 2:
            return True
    for ox, oy, ow, oh, *_ in near.kinds.near(cx, cy, reach):  # everything seated between the sheds and this pass (T49)
        if abs(cx - ox) < (cw + ow) / 2 + 6 and abs(cy - oy) < (ch + oh) / 2 + 6:
            return True
    if any(boxed_ring_hit(q[0], q[1], ft.rings.near(q[0], q[1]), 6.0) for q in corners):  # a paddy or the marsh, inside or within 6 ft of an edge
        return True
    # A LANE THROUGH THE STRIP, not only past its corners (feature 137, cohort seed 03): five sample
    # points on a 22 by 16 ft strip let a lane cross it diagonally between them, and
    # `lanes_clear_of_bamboo` walks the tread's quarter-points. So the tread is also tested as a
    # segment against the strip's edges - a crossing, or an end inside, is a stand on a lane.
    _edges = [(corners[k], corners[(k + 1) % 4]) for k in range(4)]
    # ...a lane list narrower than the index's (`own_ground`: a sheltered farm's lanes less its own door path) keeps its own lanes
    mine = None if lanes is near.lanes else {id(ln) for ln in lanes}
    for lane, a, b, *_ in near.segs.near(cx, cy, max(cw, ch) / 2):
        if mine is not None and id(lane) not in mine:
            continue
        half = lane[1]
        if any(seg_dist(q[0], q[1], a, b) < half for q in corners):
            return True
        if any(segments_cross(a, b, e0, e1) for e0, e1 in _edges) or any(abs(p[0] - cx) < cw / 2 and abs(p[1] - cy) < ch / 2 for p in (a, b)):
            return True
    # the dry hem's plots and the watercourses (unlock tripwire seed 47: a fixture on a dry plot and one
    # on the stream - neither is a paddy, a lane or the pond, so nothing above saw them), and any crown
    # already drawn (seed 37: a fixture seated under a grove crown drawn two stages earlier)
    if any(boxed_ring_hit(q[0], q[1], ft.dry.near(q[0], q[1]), 3.0) for q in corners):  # a dry plot, inside or within 3 ft
        return True
    if any(ft.on_water(s, q[0], q[1]) for q in corners):
        return True
    for tx, ty, tr, *_ in near.crowns.near(cx, cy, max(cw, ch) / 2):
        # the stand is drawn axis-aligned (cw x ch), so a crown is measured to its own box: squaring it on the half-diagonal, as
        # a raked footprint is, made a sheltered farm's 240 x 16 ft south band a 240 ft square that every crown within 120 ft of
        # it refused (feature 374 wave 153: Kashikawa's 77 frame-wide offers all refused, the bands left a third of the farm wide)
        if max(abs(cx - tx) - cw / 2, 0.0) ** 2 + max(abs(cy - ty) - ch / 2, 0.0) ** 2 < (tr + 0.6) ** 2:
            return True
    return bool(pond) and ((cx - pond[0]) / (pond[2] + 20.0)) ** 2 + ((cy - pond[1]) / (pond[3] + 20.0)) ** 2 <= 1.0
