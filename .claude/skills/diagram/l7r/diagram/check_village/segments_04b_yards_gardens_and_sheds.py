"""Gate segments (yards gardens and sheds; keys 0285_006-0285_065) - bodies verbatim, registry order preserved."""

import math
from typing import Any

from l7r.diagram.settlement import FARMHOUSE_EAVE_GAP_FT, surface_water_dist

from .common_01_geometry import (
    _OVERLAP_STRUCTS,
    _struct_rect,
    point_in_poly,
    rect_corners,
    seg_dist,
    segments_cross,
    within_edge_gap,
)
from .common_02_overlap_policy import in_ellipse
from .common_03_capacity import _UNBOUND, _kept


def _seg_0285_006__settlement_has_wells(
    *,
    M: Any = _UNBOUND,
    REACH: Any = _UNBOUND,
    SHRINE_FAR: Any = _UNBOUND,
    SHRINE_WELL_GAP: Any = _UNBOUND,
    b: Any = _UNBOUND,
    c: Any = _UNBOUND,
    check: Any = _UNBOUND,
    d: Any = _UNBOUND,
    dry: Any = _UNBOUND,
    dwell: Any = _UNBOUND,
    h: Any = _UNBOUND,
    i: Any = _UNBOUND,
    lines: Any = _UNBOUND,
    ln: Any = _UNBOUND,
    meta: Any = _UNBOUND,
    pond: Any = _UNBOUND,
    r: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    shrine_hill: Any = _UNBOUND,
    st: Any = _UNBOUND,
    wellless: Any = _UNBOUND,
    wells: Any = _UNBOUND,
    wl: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0285.006 (remote_shrine_has_own_well, settlement_dwellings_watered, settlement_has_wells) - body verbatim from _seg_0285__wells_clear_of_shrine_and_torii (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'village', 'hamlet') and dwell:
        check(
            "settlement_has_wells",
            len(wells) >= max(1, round(len(dwell) / 25)),
            f"a {scale} of {len(dwell)} households has only {len(wells)} communal well(s) - every settlement "
            f"keeps wells (about one per 20-25 households); scatter them among the dwellings with s.place_wells(...)",
        )
        lines = [c["poly"] for c in M.get("channels", [])] + [st["poly"] for st in M.get("streams", [])] + ([M["moat"]] if M.get("moat") else [])
        pond = M.get("pond")
        REACH = round(760 / float(meta.get("ftpx") or meta.get("ft_per_px") or 2.0))  # ~760 ft, in px at this map's scale (380 at 2 ft/px)
        dry = []
        for h in dwell:
            # the surface-water half is the SHARED predicate `settlement.surface_water_dist` -
            # the same call hamletgen.place_wells makes when deciding which houses need a well
            # (known-open ledger 2026-08-16: two definitions of "needs a well" had drifted).
            # `lines`/`pond` above stay bound for downstream-segment parity; the verdict reads
            # the helper.
            d = min((math.hypot(h["x"] - wl["x"], h["y"] - wl["y"]) for wl in wells), default=1e9)
            d = min(d, surface_water_dist(M, h["x"], h["y"]))
            if d > REACH:
                dry.append((round(h["x"]), round(h["y"])))
        check(
            "settlement_dwellings_watered",
            not dry,
            f"{len(dry)} household(s) more than {REACH}px from any water source - a well, or an irrigation channel / pond / stream / moat: {dry[:4]} - put a well within reach",
        )

        # A shrine/temple set sufficiently APART from the village keeps its OWN WELL close by for purification
        # (temizu): too far to walk to the village's shared wells, it needs a dedicated draw-point right beside
        # it - and specifically a WELL, not just any water (a ditch/pond is not an ablution source). A shrine
        # AMONG or near the houses shares the village wells (exempt). "Set apart" = the nearest dwelling is more
        # than SHRINE_FAR px away; "close by" = a well within SHRINE_WELL_NEAR px.
        SHRINE_FAR, SHRINE_WELL_GAP = 150, 70
        shrine_hill = M.get("hill")
        wellless = []
        for r in M.get("religious", []):
            if shrine_hill and in_ellipse(r["x"], r["y"], shrine_hill):
                continue  # a hilltop/mountain shrine draws from a spring/basin, not a dug well
            if min((math.hypot(r["x"] - b["x"], r["y"] - b["y"]) for b in dwell), default=1e9) <= SHRINE_FAR:
                continue  # among/near the houses -> shares the village wells
            if not any(within_edge_gap(r, wl, SHRINE_WELL_GAP) for wl in wells):  # the TRUE gap to the hall's edge (a big monastery's well sits further out)
                wellless.append((round(r["x"]), round(r["y"])))
        check(
            "remote_shrine_has_own_well",
            not wellless,
            f"{len(wellless)} shrine/temple(s) set apart from the village (>{SHRINE_FAR}px from any house) with no well beside them - a remote shrine keeps its own well for ablution: {wellless[:4]}",
        )
    return _kept(locals(), ('REACH', 'SHRINE_FAR', 'SHRINE_WELL_GAP', 'b', 'c', 'd', 'dry', 'h', 'i', 'lines', 'ln', 'pond', 'r', 'shrine_hill', 'st', 'wellless', 'wl'))


def _seg_0285_007__fdef(*, fdef: Any = _UNBOUND, fields: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0285.007 (fdef, fields_ol) - body verbatim from _seg_0285__wells_clear_of_shrine_and_torii (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'village', 'hamlet') and scale in ('town', 'village', 'hamlet', 'city'):
        fields_ol = [fdef["outline"] for fdef in fields]
    return _kept(locals(), ('fdef', 'fields_ol'))


def _seg_0285_008__yards(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0285.008 (yards) - body verbatim from _seg_0285__wells_clear_of_shrine_and_torii (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'village', 'hamlet') and scale in ('town', 'village', 'hamlet', 'city'):
        yards = M.get("threshing_yards", [])
    return _kept(locals(), ('yards',))


# the HEADMAN is NOT exempt (GM 2026-07-21, caught on Hikari no Sato): the old role=="headman"
# carve-out here existed only because the dispersed-style headman() predated the homestead
# bundle and drew a lone house - the check was written around the bug. The headman is the
# LARGEST farmstead in the village and threshes its own rice like every other household.


# the work yard (niwa) was UNIVERSAL: EVERY farmhouse threshed and dried its own rice on its own
# yard, so EVERY farmhouse must have one (a firm 100%). The generator guarantees this by making
# the yard integral to farmstead placement - a house is only sited where its yard also fits
# (nudging it as needed) - so a farmhouse without a yard is a generator bug, not a density limit.


# the yard is the farmstead's own dry work apron, SMALLER than the house it serves (not a
# second dwelling). Each yard records `of` = its parent farmhouse center.


# the yard is the maeniwa - the SOUTH-facing front work yard. Rice must dry in the SUN and
# minka face south, so the yard sits on the house's south/front side (or, if the paddy blocks
# that, a side), but NEVER the shady NORTH back. +y is south here, so a yard must not sit
# meaningfully north of (above) its own farmhouse center (`of[1]`).


# the yard is a DRY tamped floor: its whole footprint must stay out of the flooded paddies.


# the yard abuts its OWN farmhouse (intentional, overlap-exempt) but must touch NOTHING else -
# not another farmhouse, a shop, a civic building, or a kura (parent matched by `of`). This is
# the dedicated guard the exemption would otherwise skip - a feature placed before the yard
# (a shop) OR after it (a hand-placed building) must not end up under it.


def _seg_0285_020__k(*, M: Any = _UNBOUND, k: Any = _UNBOUND, s: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0285.020 (k, others, s) - body verbatim from _seg_0285__wells_clear_of_shrine_and_torii (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'village', 'hamlet') and scale in ('town', 'village', 'hamlet', 'city'):
        others = [s for k in _OVERLAP_STRUCTS for s in M.get(k, [])] + M.get("storehouses", []) + M.get("merchant_estates", [])
    return _kept(locals(), ('k', 'others', 's'))


# ATTACHED KURA STOREHOUSE: a farm's fireproof grain store is drawn as an annex on the house's back
# wall, so every one that exists must ABUT a farmhouse - never float detached in the courtyard (that
# reads as a shed nobody owns). ~30% of farms carry one (a wealth marker), so it is not REQUIRED, but
# any present must be attached. Guards the regression where a move-procedure strands the shed.


def _seg_0285_024__sheds(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0285.024 (sheds) - body verbatim from _seg_0285__wells_clear_of_shrine_and_torii (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'village', 'hamlet') and scale in ('town', 'village', 'hamlet', 'city'):
        sheds = M.get("farm_sheds", [])
    return _kept(locals(), ('sheds',))


# DOORYARD KITCHEN GARDEN (saien). Every farmstead kept a small intensive vegetable plot for
# the household's daily greens - as universal as the work yard, so EVERY farmhouse must have one
# (a firm 100%, guaranteed by making the garden integral to farmstead placement). It sits on a
# sunny SIDE (preferring the east kitchen end), NOT the north shade and NOT the south front (the
# threshing apron's ground), is SMALLER than the farmhouse, stays on DRY ground off the paddies,
# and abuts only its own house. (Why a side, not the south front: settlements.md "Dooryard gardens".)


def _seg_0285_026__gardens(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0285.026 (gardens) - body verbatim from _seg_0285__wells_clear_of_shrine_and_torii (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'village', 'hamlet') and scale in ('town', 'village', 'hamlet', 'city'):
        gardens = M.get("gardens", [])
    return _kept(locals(), ('gardens',))


# ... and off the IRRIGATION LINES too: the feeder CHANNELS, the in-field/drain DITCHES, and any
# STREAM. A raised-bed vegetable plot cannot sit in a running ditch; `gardens_clear_of_paddies`
# covers the flooded basin, but a feeder channel or the drain ditch threads the DRY village margin
# where the gardens are, so test each garden footprint against every water polyline (its own
# half-width + a little). Same full-footprint test used for structures vs a channel/stream.


def _seg_0285_036__c(*, M: Any = _UNBOUND, c: Any = _UNBOUND, d: Any = _UNBOUND, scale: Any = _UNBOUND, st: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0285.036 (c, d, st, waterlines) - body verbatim from _seg_0285__wells_clear_of_shrine_and_torii (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'village', 'hamlet') and scale in ('town', 'village', 'hamlet', 'city'):
        waterlines = (
            [(c["poly"], c.get("w", 2.5) / 2 + 3) for c in M.get("channels", [])]
            + [(d["poly"], d.get("w", 7) / 2 + 3) for d in M.get("field_ditches", [])]
            + [(st["poly"], st.get("w", 9) / 2 + 3) for st in M.get("streams", [])]
        )
    return _kept(locals(), ('c', 'd', 'st', 'waterlines'))


def _seg_0285_037__g_on_water(*, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0285.037 (g_on_water) - body verbatim from _seg_0285__wells_clear_of_shrine_and_torii (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'village', 'hamlet') and scale in ('town', 'village', 'hamlet', 'city'):
        g_on_water = []  # type: ignore[var-annotated]
    return _kept(locals(), ('g_on_water',))


def _seg_0285_038__cx(
    *,
    cx: Any = _UNBOUND,
    cy: Any = _UNBOUND,
    e: Any = _UNBOUND,
    g_on_water: Any = _UNBOUND,
    gardens: Any = _UNBOUND,
    gc: Any = _UNBOUND,
    gd: Any = _UNBOUND,
    k: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    waterlines: Any = _UNBOUND,
    whw: Any = _UNBOUND,
    wp: Any = _UNBOUND,
    wx: Any = _UNBOUND,
    wy: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0285.038 (cx, cy, e, g_on_water) - body verbatim from _seg_0285__wells_clear_of_shrine_and_torii (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'village', 'hamlet') and scale in ('town', 'village', 'hamlet', 'city'):
        for gd in gardens:
            gc = rect_corners(_struct_rect(gd))
            for wp, whw in waterlines:
                if (
                    any(seg_dist(cx, cy, wp[k], wp[k + 1]) < whw for cx, cy in gc for k in range(len(wp) - 1))
                    or any(point_in_poly(wx, wy, gc) for wx, wy in wp)
                    or any(segments_cross(wp[k], wp[k + 1], gc[e], gc[(e + 1) % 4]) for k in range(len(wp) - 1) for e in range(4))
                ):
                    g_on_water.append((round(gd["x"]), round(gd["y"])))
                    break
    return _kept(locals(), ('cx', 'cy', 'e', 'g_on_water', 'gc', 'gd', 'k', 'whw', 'wp', 'wx', 'wy'))


def _seg_0285_039__gardens_clear_of_channels(*, check: Any = _UNBOUND, g_on_water: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0285.039 (gardens_clear_of_channels) - body verbatim from _seg_0285__wells_clear_of_shrine_and_torii (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'village', 'hamlet') and scale in ('town', 'village', 'hamlet', 'city'):
        check(
            "gardens_clear_of_channels",
            not g_on_water,
            f"kitchen garden(s) overlap an irrigation channel/ditch: {g_on_water[:3]} - a raised-bed saien sits on dry ground, never in a running feeder channel, field ditch, or stream",
        )
    return _kept(locals(), ())


# the garden and the farmhouse's STOREHOUSE/shed must never overlap - the shed sits on a wall the
# garden does not use (west for a dispersed farm, the shaded north for a nucleated one). The shed is
# a recorded annex (M['farm_sheds']), so read its actual footprint straight from there.


# A dooryard bed and a threshing yard were HAND-worked plots bent to paths and soil, not surveyed
# rectangles - the generator draws each as a slightly-irregular 4-sided quad (a garden more irregular,
# a swept work yard near-square). Validate the SHAPE it records: every garden/yard with a `poly` must
# carry exactly 4 vertices, be non-degenerate (real area), and stay INSCRIBED in its recorded w x h
# bounds (the jitter only pulls corners INWARD, so a poly poking outside its rect means the overlap
# checks - which use that rect - were cleared against the wrong footprint). WHY quads: settlements.md
# "Dooryard kitchen gardens" / "Threshing yards" (irregular-plot grounding).


# GARDEN AREA is held to a HISTORICAL band. Unlike the house/yard (drawn oversized against the
# fields for legibility), a dooryard kitchen garden at 1 px = 2 ft is near its TRUE size, so its area
# is a real quantity we can check against the ground a household could hand-work. The saien is the
# small intensive daily-greens bed by the kitchen (the bulk vegetable growing was out in the hatake
# dry fields, not here): historically a few tsubo up to ~1.4 se - roughly 10-140 m^2 (1 tsubo = 3.31
# m^2; 1 se = 30 tsubo ~ 99 m^2). We sum ALL of a household's garden beds (a fragmented plot is still
# one household's garden) and require the TOTAL in that band. WHY the numbers: settlements.md "Dooryard
# kitchen gardens" (area grounding). Scale override via meta.ft_per_px for any non-standard map.


# HOMESTEAD GROVE (yashikirin) - the farmhouse windbreak. A dense L-BELT of shelter trees on the
# WINDWARD side(s) of the house (one record per belt ARM), blocking the cold prevailing wind while
# leaving the SUNNY lee open. Default windward NW: the East Asian winter monsoon blows NW across
# China and Japan alike, so N+W is windward, S/E the sheltered sunny side - a map keys it off its
# own geography with meta(windward=...). The grove is NEAR-UNIVERSAL (meta.grove_prevalence) and
# the LARGEST homestead appurtenance - bigger than the house. We gate GEOMETRY per arm (windward,
# off the paddy, off other buildings), the typical grove's SCALE (groves_are_substantial), a
# presence FLOOR scaled to the knob, and (city) that NO intramural farm carries one. WHY (the ~30-40
# tree stand, the windward rule, the firewood/timber/bamboo it gave): settlements.md "Homestead groves".


def _seg_0285_057__groves(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0285.057 (groves) - body verbatim from _seg_0285__wells_clear_of_shrine_and_torii (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'village', 'hamlet') and scale in ('town', 'village', 'hamlet', 'city'):
        groves = M.get("groves", [])
    return _kept(locals(), ('groves',))


def _seg_0285_058__grove_of(*, groves: Any = _UNBOUND, gv: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0285.058 (grove_of, gv) - body verbatim from _seg_0285__wells_clear_of_shrine_and_torii (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'village', 'hamlet') and scale in ('town', 'village', 'hamlet', 'city'):
        grove_of = {(round(gv["of"][0]), round(gv["of"][1])) for gv in groves}  # distinct farms with a grove
    return _kept(locals(), ('grove_of', 'gv'))


def _seg_0285_059__WINDV(*, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0285.059 (WINDV) - body verbatim from _seg_0285__wells_clear_of_shrine_and_torii (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'village', 'hamlet') and scale in ('town', 'village', 'hamlet', 'city'):
        WINDV = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0), "NW": (-1, -1), "NE": (1, -1), "SW": (-1, 1), "SE": (1, 1)}
    return _kept(locals(), ('WINDV',))


def _seg_0285_060__windward(*, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0285.060 (windward) - body verbatim from _seg_0285__wells_clear_of_shrine_and_torii (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'village', 'hamlet') and scale in ('town', 'village', 'hamlet', 'city'):
        windward = str(meta.get("windward", "NW")).upper().strip()
    return _kept(locals(), ('windward',))


def _seg_0285_061__wvx(*, WINDV: Any = _UNBOUND, scale: Any = _UNBOUND, windward: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0285.061 (wvx, wvy) - body verbatim from _seg_0285__wells_clear_of_shrine_and_torii (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'village', 'hamlet') and scale in ('town', 'village', 'hamlet', 'city'):
        wvx, wvy = WINDV.get(windward, (-1, -1))
    return _kept(locals(), ('wvx', 'wvy'))


# TWO FARMHOUSES MUST SHED SEPARATELY. A minka carries a steep kayabuki thatch (45 deg or steeper -
# thatch has to shed hard or it rots), so each roof throws its own drip line, and two of them set a
# couple of feet apart pool their runoff against each other's walls. `research/buildings.md` already
# records the principle for a building standing against a compound wall - "rear wall a foot or two
# off it so the two roofs shed separately" - and the same physics governs two houses.
#
# THE DEFECT IT CATCHES, and why a rule was needed at all (settlement-review on Mizuguchi,
# 2026-08-17): a re-pack flipped one house's rake from -4.0 to +4.4 deg so a neighboring pair
# diverged instead of running parallel, and their raked-corner gap fell 3.6 -> 2.0 ft. At 1 px = 1 ft
# that is two pixels between two dark roof strokes; at fit zoom they merge and read as ONE long
# building rather than two households. Nothing caught it, because house-to-house separation had no
# rule at all - `no_structure_overlaps` only fires at zero.
#
# THE NUMBER, and its headroom. 8 ft: two drip lines plus a footpath between them, which is the
# least ground that reads as a gap rather than a seam. It is deliberately far below what the pool
# actually does - the scripted hamlets sit at 23-29 ft minimum - so this fires on a merge, never on
# a tight-but-honest nucleus. A denser tier may legitimately approach it; it may not cross it.
#
# IN FEET, NOT PIXELS. The rule is a physical clearance, so it converts through `meta.ftpx` rather
# than being a raw px literal that would silently mean 8 ft at a hamlet and 16 ft at a village.
# GAP VERDICT family: `within_edge_gap` on real rotated corners, never centers (dev/placement.md).
#
# THE TIER GUARD IS DECLARED, not incidental (settlement-review on Mizuguchi, 2026-08-17: 'a check
# that never RUNS looks exactly like a check that passes'). It runs at town/village/hamlet and NOT
# at city, and that is deliberate: a city's dwellings are `buildings` on a street wall, where
# sharing a party wall is the correct machiya form, not a merge. City maps do carry `houses`
# records, and the rule was run against the whole pool with the guard bypassed - no city map
# violates it - so the guard currently hides nothing.
#
# A PIXEL FLOOR WAS CONSIDERED AND NOT ADDED. The motivating defect was both physical (two roofs
# with nowhere to shed) and PERCEPTUAL (two dark strokes 2 px apart merging into one building),
# and only the physical half converts through ftpx: 8 ft is 8 px at a hamlet but 4 px at a village
# and 2.7 px at a city, which is the very seam width that read as one building here. Declined for
# now because no map at those tiers is near the line and a floor nothing exercises is a rule
# nobody has tested; the trigger to add one is the first village or town map that draws a
# legal-in-feet pair under ~4 px. Recorded so the next reader knows it was a decision.


def _seg_0606__farmhouses_shed_separately(*, M: Any = _UNBOUND, check: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0606 (farmhouses_shed_separately) - added 2026-08-17, see the note above.

    Numbered past the legacy range (the number is a LABEL; the registry tuple is the execution
    order). It binds only M/check/scale, all established long before any homestead segment, so its
    position carries no dependency."""
    if scale in ('town', 'village', 'hamlet'):
        _fh = [h for h in M.get("houses", []) if h.get("kind") != "abandoned"]
        _lim = FARMHOUSE_EAVE_GAP_FT / float(M["meta"].get("ftpx", 1) or 1)
        _merged = []
        for _i in range(len(_fh)):
            for _j in range(_i + 1, len(_fh)):
                if within_edge_gap(_fh[_i], _fh[_j], _lim):
                    _merged.append((round(_fh[_i]["x"]), round(_fh[_i]["y"])))
        check(
            "farmhouses_shed_separately",
            not _merged,
            f"{len(_merged)} farmhouse pair(s) stand closer than {FARMHOUSE_EAVE_GAP_FT:.0f} ft wall to wall, at {_merged[:4]} - "
            f"two steep thatched roofs need their own drip lines and a way between them; at this range the pair merges into one long building on the sheet",
        )
    return _kept(locals(), ())


def _seg_0609__byres_stand_in_their_declared_form(*, M: Any = _UNBOUND, check: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0609 (byre_form_declared, courtyard_byres_annex_their_homestead) - added
    2026-08-18 with the `byre_form` knob. Numbered past the legacy range; the number is a LABEL.

    TWO CHECKS, BECAUSE A KNOB HAS TWO WAYS TO FAIL. The first is the declaration-exists invariant
    this engine keeps re-learning: a rule that hides behind `if meta.get(...)` is indistinguishable
    from a rule that passes, so a map that draws byres and names no form is a failure in itself, not
    a map the geometry check quietly skips. The second holds the DRAWING to the DECLARATION, which is
    the live hazard here - the overlap registry asserted for months that a byre "is an ANNEX abutting
    its own farmhouse (draft_byres places it against the wall)" while the placer had long since been
    spreading detached sheds by minimax across the whole cluster, and nothing noticed because nothing
    measured it. Only the courtyard form has geometry to hold: `detached_commons` says the shed is on
    the shared ground, which is not a claim about any one homestead."""
    # GUARDED ON THE DECLARATION, NEVER ON THE DRAWING (corrected 2026-08-18, same day, by all four
    # settlement-reviews independently). The first cut of this segment opened
    # `if generated_by and M.get("byres")` - so a map that drew ZERO byres skipped both checks,
    # including the declaration-exists one, which is the single state they were written for. It shipped
    # that way and it immediately hid a real regression: the courtyard form seated nothing at all on
    # Mizuguchi, 3 byres -> 0, and the gate said nothing. Guarding a declaration check on the presence
    # of the thing being declared is the `if meta.get(...)` trap this segment's own docstring names one
    # paragraph above, and writing the warning did not stop me reintroducing it in the same commit.
    # The guard is now the SCALE - every settlement at these tiers plows, so every one of them runs
    # `draft_byres`, which records `byre_form` and `byre_target` unconditionally before it seats
    # anything.
    if M["meta"].get("generated_by") and M["meta"].get("scale") in ("hamlet", "village"):
        _byf = M["meta"].get("byre_form")
        check(
            "byre_form_declared",
            _byf in ("courtyard", "detached_commons"),
            f"the map draws {len(M.get('byres') or [])} byre(s) but declares byre_form={_byf!r} - a settlement must record WHICH of the two "
            f"attested forms it used (the owner's own stable wing, or a shared shed on the commons), or nothing can hold the drawing to it",
        )
        # AND THE ASK IS RECORDED, so a silent shortfall is a failure rather than an absence. The
        # placer walks its candidate pool and simply stops when nothing fits; with no record of what
        # it MEANT to seat, "this hamlet has one byre" and "this hamlet wanted four and could only
        # place one" are the same manifest. `byre_target` is written by `draft_byres` from the same
        # expression it loops on, so the check cannot drift from the ask.
        # `_byt is None` is a FAILURE, not a pass. The first cut wrote `_byt is None or _byn >= _byt`
        # and Mizuguchi - the map with zero byres, the whole reason this check exists - sailed through
        # it, because the target was not being recorded yet. That is the third shape of the same trap
        # in one segment: guard on the drawing, guard on the declaration, then let a missing input
        # stand in for a satisfied one. `draft_byres` records the target unconditionally, so on any
        # map that reaches this guard its absence means the placer never ran.
        _byt = M["meta"].get("byre_target")
        _byn = len(M.get("byres") or [])
        check(
            "byres_meet_their_target",
            _byt is not None and _byn >= _byt,
            f"the placer asked for {_byt} byre(s) and seated {_byn} - a wet-rice settlement plows with a draft team, so a "
            f"shortfall is a placement failure, not a settlement without oxen. Check the form's seat search: the courtyard "
            f"form has only its owner's own walls to work with, and a homestead ringed by its yard and garden can refuse it",
        )
        # `courtyard_byres_annex_their_house` RETIRED WITH ITS CHECK, AND THE MEASURE KEPT (feature 146).
        # It held that a byre in the COURTYARD form stands against its owner's own wall: it took each byre's
        # nearest farmhouse and failed the map when the two stood further apart than
        # `courtyard_annex_span(house w, house h, byre h) + 2 px`. Feature 141 cut it as a check that
        # re-measures what the placer guarantees - the courtyard seat search only ever offers seats on the
        # owner's walls, so the distance cannot come out wrong - and this feature removes the loop it left
        # standing, which walked every byre on every hamlet and village gate and appended to a list nothing
        # read. `courtyard_annex_span` itself is live and is where the rule now lives.
    return _kept(locals(), ())


# WHY: <one paragraph - what the research found, the decision it drove, the departure taken>.
# Declare EVERY input the body reads as a keyword parameter (an undeclared one is a NameError at
# gate time, not at import), and keep the `_kept` tuple a LITERAL of the names this body binds.


# `HOUSE_PADDY_GAP_FT` and its why live with the placer (settlement/houses.py) - placement and its check read ONE number.


# WHY: <one paragraph - what the research found, the decision it drove, the departure taken>.
# Declare EVERY input the body reads as a keyword parameter (an undeclared one is a NameError at
# gate time, not at import), and keep the `_kept` tuple a LITERAL of the names this body binds.


# FARMSTEAD FIXTURES (feature 133 T53-T59, GM 2026-08-27). The T52 completeness pass listed what a
# paddy farmstead had that the map did not draw, and the GM chose: the privy, the woodpile, the
# manure heap, the bath shed, the chicken coop (in imperial China's proportions), the household
# shrine (rare, in the religious red) and the persimmon. Each is an ANNEX of one farmhouse, seated by
# `hamletgen/homesteads.py::farmstead_fixtures` against its own wall (or, for the hokora, its plot's
# corner; the persimmon beside it, one crown out) - so the two rules here are the annex rule and the
# declaration rule: (1) every fixture stands within a short walk of ITS OWN house - Nipponica: the
# privy was an independent building "at the back door, by the naya, or at the gate"; the hokora at
# the plot's corner; the persimmon "shades the house in summer" - a fixture far from every house is a
# placer fault; (2) the shares the hamlet ROLLED are declared in meta and the sheet agrees: one of a
# kind per house at most, a rare shrine that stays rare (Sugiura 1973: 3 per 100 households; the
# GM: "very rare, but notable"), and at least one privy on any hamlet that declared them near-
# universal. Research: research/homesteads.md "The farmstead's fixtures".
FIXTURE_REACH_FT = {"privy": 20.0, "manure": 26.0, "bath": 20.0, "coop": 20.0, "woodpile": 20.0, "shrine": 30.0}
PERSIMMON_REACH_FT = 50.0
