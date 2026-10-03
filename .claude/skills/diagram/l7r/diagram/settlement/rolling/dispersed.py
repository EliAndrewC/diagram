"""The DISPERSED farmstead's layout: the house, its yard and garden, and its own grove on the sides its settlement rolled
(feature 291). Module-level and pure, so it is tested with plain numbers; `BundleMixin._bundle_layout` calls it.

THE CANONICAL FRAME. Every farmstead is laid out as if the cold wind came from the northwest - the grove's deep bands
on the north and west, the threshing yard on the south front, the garden against the east wall - and then carried to
the map's own wind by a symmetry of the square (`grove_sides.bundle_turn`). Before feature 291 the layout stopped at the
canonical frame, so a map that declared another wind still drew its groves on the north and west.
"""

from __future__ import annotations

from typing import Any

from ..homestead_parts.grove_sides import THIN_BAND_FT as THIN_BAND_FT
from ..homestead_parts.grove_sides import E, N, S, Turn, W, turn_face, turns_axes

# THE GARDEN'S MORNING SUN: no grove band stands within this reach east of a garden across its height - the reach
# `_east_trees` reads (px at the village grain, scaled by `bscale`; research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html).
EAST_SHADE_REACH = 22.0
# THE YARD'S DRYING SUN, AS A SEATING PREFERENCE: the strip south of a threshing yard a grove BAND is kept out of when a farm is
# seated (`_yard_sun_conflict`'s 22 px strip), which keeps bands whole; the sun rule itself is the crown's - no crown in any
# plot's sun ground, `CANOPY_SHADE_FT` (feature 310, `KeepoutsMixin._sun_keepouts`).
YARD_SUN_STRIP = 22.0
# THE WAY IN THROUGH A RING. A grove round all four sides must still let the farm be reached: its front band is broken
# once, at the yard's middle, for a way wide enough that a lane can be ROUTED through it - the router keeps a footpath's
# fabric gap plus 0.71 of its planning cell off every band on each side, 22.2 ft at its 10 ft cell (measured on cohort
# seed 12, whose rings were first opened 12 ft, two treads: no route at cells 10, 5 or 3, and 14 of 17 farms stranded).
# A physical necessity; the width is a GUESS - no old page gives an opening's width, and the old entrances found stood on
# a grove's open side, which a ring does not have (research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.html).
WAY_IN_FT = 36.0
# THE LANE'S ROOM BETWEEN TWO FARMS' GROVES: a farm's frame is padded by half of it on every side, so two neighbors' groves
# stand at least this far apart. Unpadded, the frames packed 2-3 ft apart (16 of seed 12's 17 farms) and the neighbors'
# bands walled off every front, so the web could reach no door. `MIN_WEB_GAP` (hamletgen/consts.py, 18 ft: both
# neighbors' clearance and the tread between them) was the first figure and is not enough: the router PLANS a lane at a
# footpath's fabric gap plus 0.71 of its cell off each band (as `WAY_IN_FT` measures), and at 18 ft seed 12's web still
# stranded at least eight farms (the trace listed eight before it was cut), at 32 none. A physical necessity at a
# GUESSED width - no page gives the gap between two groves.
LANE_ROOM_FT = 32.0
# THE SERVICE STRIP BEHIND THE HOUSE AND OFF ITS WINDWARD END: the windward stand stands this far off the back wall and
# the west end wall (`canonical_farmstead`), so a wood shed (24 x 12 ft,
# `FIXTURE_FT`) fits a step (`_WOODSHED_STEP_FT`, 6 ft) off it with a wall gap to spare. Hard against the wall, the stand
# took every wood-shed seat: once the dispersed and linear forms rolled again, Kashikawa seated 1 of 7 rolled wood sheds
# and Mizuguchi 1 of 5 (settlement-review, 2026-09-29). Where on the plot a wood shed stood no page says (a GUESS, as the
# shed's own seat is), so the strip is sized to the shed, not to a finding: the wall gap (3.5 ft), the step (6 ft), the
# shed's depth (12 ft) and the 2 ft the fixture placer keeps off a footprint, with half a foot over - at 21 ft, without
# the placer's gap, the back seats ended 1.5 ft off the band and Mizuguchi's largest farmhouse seated no shed.
SERVICE_STRIP_FT = 24.0
# THE WINDWARD STAND'S DEPTH, in house depths: the grove ~6x the house (research/contents.json#homesteads, the grove's real scale).
DEEP_BAND_HOUSE_DEPTHS = 1.57

Rect = tuple[float, float, float, float]


def _box(x0: float, y0: float, x1: float, y1: float) -> Rect:
    return ((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0)


def _edges(r: Rect) -> tuple[float, float, float, float]:
    return r[0] - r[2] / 2, r[1] - r[3] / 2, r[0] + r[2] / 2, r[1] + r[3] / 2


def canonical_farmstead(
    cw: float,
    ch: float,
    gap: float,
    garden: tuple[float, float],
    yard: tuple[float, float],
    *,
    sides: int,
    garden_by_yard: bool,
    thin: float,
    sun_east: float,
    way_in: float,
    yard_sun: float = YARD_SUN_STRIP,
    sun_band: bool = False,
    back: float = 0.0,
    well: float = 0.0,
) -> dict[str, Any]:
    """The farmstead in the canonical frame, about a house of `cw` x `ch` centered on the origin: `yard`, `garden`, and
    `groves` as (rect, face, "deep" | "thin") - the deep north and west bands; with three sides a thin east band; with four
    a thin south band too, broken at the yard's middle for the way in. The corners close: the north and south bands run
    the whole width, the west and east bands between them. Each thin band stands clear of what the ground it closes needs
    - the east band beyond the garden's morning-sun reach, the south band beyond the yard's drying strip; with `sun_band` (a map
    keeping every canopy tree out of the plots' sun, feature 310) the garden stands beside the yard and the east band closes
    the house's east side only, ending at its front wall, north of every plot's sun ground. With `well` (the
    pocket's side), `well`: the farm's OWN WELL POCKET beside the yard, on its west, away from the garden and off the way in."""
    gw, gh = garden
    yw, yh = yard
    yard_r = (0.0, ch / 2 + gap + yh / 2, yw, yh)
    # beside the yard, at its far end (the yard keeps the garden's sky open to the south), or against the house's east
    # wall, at its mid-height
    garden_r = (yw / 2 + gap + gw / 2, yard_r[1], gw, gh) if garden_by_yard or sun_band else (cw / 2 + gap + gw / 2, 0.0, gw, gh)
    if sun_band:  # ...and wholly south of the front wall, where the east band ends: a bed taller than the yard, centered on it, rose
        # past the band's end into its morning shade (feature 315; cohort seeds 14, 15 and 906, which the south nudge had moved into
        # a persimmon's sun ground instead)
        garden_r = (garden_r[0], max(garden_r[1], ch / 2 + gap + gh / 2), gw, gh)
    works = [(-cw / 2, -ch / 2, cw / 2, ch / 2), _edges(yard_r), _edges(garden_r)]
    # A GROVE FARM CARRIES ITS OWN WATER FROM ITS SEATING (feature 291 FR-018 and FR-019 on feature 287's seating, homes H09):
    # the pocket a wellhead needs, laid in the dooryard beside the yard - where on the plot the well stood no page read says
    # (a GUESS, as it was for the ring search this replaces) - so the placer admits the farm only with room for its water
    # (`lot.watered`). Drawn as its own well, or released where a channel or a row's shared well serves the farm instead.
    # ...at the yard's middle, or as far down as its WELLHEAD needs to clear the house's front wall, by a foot (a third of
    # `gap`): at the middle of a shallow yard narrower than the house, the wellhead (the pocket less its 3 ft margin, `gap`)
    # stood on its own house, which the matrix refuses (Kashikawa, once its row's lots were capped at 240 ft). Only a
    # wellhead that would stand on the house moves, and no further: moving every pocket a gap clear of the wall shifted
    # five cohort seeds' farms onto failures, and a wellhead a gap clear two (2026-10-01)
    under = yw / 2 + gap < cw / 2
    well_r = (-(yw / 2 + gap + well / 2), max(yard_r[1], ch / 2 + well / 2 - gap + gap / 3) if under else yard_r[1], well, well) if well > 0 else None
    if well_r is not None:
        works.append(_edges(well_r))
    # `back`: the service strip (`SERVICE_STRIP_FT`) on BOTH windward sides - behind the house, and off its west end wall,
    # where the bath room is joined at the stable end and the wood shed takes a flank seat: hard against that wall, the
    # west band stood on every bath room Mizuguchi drew (3 of 3) and on its one wood shed
    west_in = min(e[0] for e in works) - gap - back
    north_in = min(e[1] for e in works) - gap - back
    east_w = max(e[2] for e in works)
    south_w = max(e[3] for e in works)
    b = DEEP_BAND_HOUSE_DEPTHS * ch
    east_out = east_w + max(gap, sun_east + 1.0) + thin if sides >= 3 else east_w  # +1 px: the reach is a strict bound
    south_in = south_w + max(gap, yard_sun + 1.0)  # +1 px, the same
    south_out = south_in + thin if sides == 4 else south_w
    groves: list[tuple[Rect, tuple[int, int], str]] = [
        (_box(west_in - b, north_in - b, east_out, north_in), N, "deep"),
        (_box(west_in - b, north_in, west_in, south_out), W, "deep"),
    ]
    if sides >= 3:
        # ...ALONG THE HOUSE ONLY, ON A MAP THAT KEEPS EVERY TREE OUT OF THE PLOTS' SUN (feature 310, GM 2026-10-02): the garden then
        # stands beside the yard (`sun_band`), every plot's sun ground begins at the house's front line, and a band run on past it
        # was stripped to a stub (the glyph-check, Kashikawa); standing it the reach out instead widened the frame past the
        # record's widest row frontage, 240 ft (research/questions/0033-row-villages-resson.html). So it closes the house's east side
        east_end = ch / 2 if sun_band else (south_out if sides == 4 else south_w)
        groves.append((_box(east_out - thin, north_in, east_out, east_end), E, "thin"))
    if sides == 4:
        mid = yard_r[0]
        groves.append((_box(west_in - b, south_in, mid - way_in / 2, south_out), S, "thin"))
        groves.append((_box(mid + way_in / 2, south_in, east_out, south_out), S, "thin"))
    return {"yard": yard_r, "garden": garden_r, "groves": groves, "well": well_r}


def _carried(r: Rect, t: Turn, hx: float, hy: float) -> Rect:
    """A canonical rect carried by the turn `t` about the house at (hx, hy): its center turned, its sides swapped where
    the turn exchanges the axes."""
    x, y = t[0] * r[0] + t[1] * r[1], t[2] * r[0] + t[3] * r[1]
    w, h = (r[3], r[2]) if turns_axes(t) else (r[2], r[3])
    return (hx + x, hy + y, w, h)


def dispersed_layout(
    hx: float,
    hy: float,
    hw: float,
    hh: float,
    gap: float,
    garden: tuple[float, float],
    yard: tuple[float, float],
    *,
    sides: int,
    turn: Turn,
    thin: float,
    sun_east: float,
    way_in: float,
    yard_sun: float = YARD_SUN_STRIP,
    sun_band: bool = False,
    pad: float = 0.0,
    back: float = 0.0,
    well: float = 0.0,
) -> dict[str, Any]:
    """The dispersed farmstead about a house at (hx, hy) of `hw` x `hh` (as drawn), carried from the canonical frame by
    `turn`: `house`, `yard`, `garden`, `gardens` (one bed), `groves` (rects), `grove_faces` ((face, depth) beside each,
    the face as turned), `well` (the farm's own well pocket, with `well` its side) and `_frame` (the box round the whole
    grove and ground, unraked). In every frame but the unchanged
    northwest one the garden goes beside the yard (plan D3): turned or mirrored, the east wall it stands against would be
    the house's north wall or its west, where the house takes its sun."""
    moved = turn != (1, 0, 0, 1)
    cw, ch = (hh, hw) if turns_axes(turn) else (hw, hh)
    can = canonical_farmstead(cw, ch, gap, garden, yard, sides=sides, garden_by_yard=moved, thin=thin, sun_east=sun_east, yard_sun=yard_sun, sun_band=sun_band, way_in=way_in, back=back, well=well)
    yard_r = _carried(can["yard"], turn, hx, hy)
    garden_r = _carried(can["garden"], turn, hx, hy)
    well_r = _carried(can["well"], turn, hx, hy) if can["well"] is not None else None
    groves = [_carried(r, turn, hx, hy) for r, _f, _d in can["groves"]]
    faces = [(turn_face(turn, f), d) for _r, f, d in can["groves"]]
    edges = [_edges(r) for r in (*groves, yard_r, garden_r, (hx, hy, hw, hh), *([well_r] if well_r else []))]
    # the frame the placer reserves, padded by `pad` (half the lane's room, `LANE_ROOM_FT`) so neighbors leave a lane between
    frame = _box(min(e[0] for e in edges) - pad, min(e[1] for e in edges) - pad, max(e[2] for e in edges) + pad, max(e[3] for e in edges) + pad)
    out = {"house": (hx, hy, hw, hh), "yard": yard_r, "garden": garden_r, "gardens": [garden_r], "groves": groves, "grove_faces": faces, "_frame": frame}
    if well_r is not None:
        out["well"] = well_r
    return out


def clear_east_of_beds(groves: list[Rect], beds: list[Rect], reach: float) -> list[Rect]:
    """The bands, each band standing in a bed's east reach (its west edge from 2 px inside the bed's east edge to `reach` past
    it, `grove_rules.gardens_east_shaded`'s test) and overlapping the bed's height cut back at its near end to a pixel clear of the
    bed's edge.

    The bands are drawn unraked and the bed is turned with its house about the house's center (`_rake_parts`), so at a rake a
    bed laid wholly south of the band's end can rise past it by its distance from the house times the rake's sine - 1.3 ft
    on cohort seed 906 at -8 degrees (feature 315). A band left shorter than it is wide is not cut (its run would be a stub)."""
    out = []
    for r in groves:
        x, y, w, h = r
        for bx, by, bw, bh in beds:
            east = bx + bw / 2
            top, bottom = by - bh / 2, by + bh / 2
            if not (east - 2 <= x - w / 2 < east + reach and y - h / 2 < bottom and top < y + h / 2):
                continue
            y0, y1 = (y - h / 2, top - 1.0) if y < by else (bottom + 1.0, y + h / 2)  # a pixel clear: both records are rounded to 0.1
            if y1 - y0 >= w:
                x, y, w, h = x, (y0 + y1) / 2, w, y1 - y0
        out.append((x, y, w, h))
    return out
