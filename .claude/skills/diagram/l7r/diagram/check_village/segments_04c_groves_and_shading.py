"""Gate segments (groves and shading; keys 0285_066-0598) - bodies verbatim, registry order preserved."""

import math
from typing import Any

from .common_01_geometry import (
    point_in_poly,
    seg_dist,
)
from .common_03_capacity import _UNBOUND, _kept

# SUN: a threshing yard dries rice in the SOUTHERN sun, so no grove may sit in the strip directly
# SOUTH of a yard (a neighbor's grove there would shade it). A grove is N/W of its OWN house, far
# from its own yard's southern corridor, so this only catches a grove shading a NEIGHBOR's yard.


# ...AND NOT BY A NEIGHBOR'S FARMHOUSE, which is the taller obstacle and was never
# tested (GM 2026-08-13: "would the shadow from the farmhouse directly to the south
# block too much light?"). Researched in research/homesteads.md, "The threshing yard's
# sun": thatch is pitched 45 deg or steeper, so the 46x28 ft minka's ridge stands ~20 ft
# up, and at 38N in the 10th month that throws 21 ft of shadow at noon and 39 ft by 9am.
# 39 ft is the rule, because the drying day that matters is 9-to-3.
#
# GATED ON `meta.generated_by`, and that gate IS the GM's decision (2026-08-13). Every
# hand-authored nucleated map in the pool breaks this - Ueda has 45 of 85 yards shaded at
# noon, Hoshigaoka 31 of 70, Ubame 21 of 36, with neighbors' walls 2-8 ft off the yard
# edge - and re-packing them all was judged the wrong trade. Instead the rule binds the
# SCRIPTED path, and each legacy map inherits it at the moment it is converted to a
# generator. The exemption therefore cannot rot: it is not a list anyone has to prune,
# it is the absence of a tag that conversion adds.
#
# WHAT COUNTS AS A NEIGHBOR TO THE SOUTH: a FARMHOUSE (`houses`), with ANY lateral overlap of the
# yard's span. Byres and sheds are not in the list on purpose - a ~10 ft ridge throws ~19 ft at the
# 28 deg shoulder sun, inside the yard's own 3 ft gap tolerance of the rule's intent - so a byre
# 25 ft south of a yard is not a finding (settlement-review, Inashiro 2026-08-26, measured one).


# ...AND THE KITCHEN GARDEN GETS THE SAME CORRIDOR (feature 133 T10, GM 2026-08-25: "there is not
# enough space for sunlight to hit the gardens and thrashing yards"). The rule above was stated for
# the yard and never for the garden - the one-obstacle shape the yard rule itself was missed by -
# and on the reference hamlet 7 of 16 gardens stood with a neighbor's wall 4-38 ft to their south
# while every yard passed. A dooryard garden's binding season is the same shoulder month as the
# drying yard's (autumn greens and daikon under a 28 deg 9am sun), so the number is the yard's 39
# ft, not a second constant; the derivation is in research/homesteads.md, "The garden's sun".
# Gated on `meta.generated_by` for the reason 071 gives. A bed's own house is exempt by position
# (a bed is never placed north of its house - `gardens_on_sunny_side`), so only NEIGHBORS count.


# THE WINDBREAK KEEPS OUT OF THE AFTERNOON SUN (feature 133 T10, GM 2026-08-25: "the windbreak
# forest ... is so close to the gardens ... that I do not believe that those gardens would get
# sufficient sunlight"). A belt is the tallest thing on the map - a working igune measures ~10 m -
# and at 3pm in the shoulder month a 33 ft belt throws ~50 ft of shadow EASTWARD (sun at 28 deg,
# azimuth ~232). So no windbreak clump may stand within 50 ft WEST of a yard's or bed's west edge,
# from its north edge to 50 ft below its south edge (the southwest). A square, not a solar wedge -
# the yard's south corridor takes the same knowing departure. WINDBREAK-ROLE groves only: the copse
# is the dooryard's persimmon and bamboo, which the record puts IN the sunlit yard. Gated on
# `meta.generated_by` like 071 (the frozen pool never opted in). research/homesteads.md.


# SAME sun rule for the COMMUNAL fengshui trees: no village-grove CLUMP may sit in the southern sun-
# corridor of a threshing yard OR a kitchen garden (both need the drying/growing sun from the south).
# The scatter records its real clumps, so test those, not the bounding poly. WHY: settlements.md 'Village windbreak'.


def _column_in_belt(t: float, px: float, py: float, wx: float, wy: float, poly: list[tuple[float, float]], view: Any = None) -> bool:
    """Does the belt's own footprint have any VISIBLE depth at this across-wind column?

    The continuity walk projects onto a straight axis; a belt that bows around a plot has columns on
    that axis where its polygon simply is not. Sampling the column along the WIND axis, across the
    polygon's own extent, answers whether there is belt there to be holed.

    AND ON THE PAGE (settlement-review 2026-08-29, acceptance re-check; measured the same day). The
    window this feeds is the belt POLYGON's extent, which is the honest bound for "the planting stops
    before the belt does" - but a footprint runs off the page as freely as a clump does, and demanding
    canopy out there fails a belt for ground no reader can see. Measured on Kuwabata: the polygon runs
    693..1440 along its own axis, only 790..1327 of that is inside the view, and the planting covers
    734..1330 - so the belt is continuous across every column that is drawn, and the 110 ft "gap" at
    the high end is entirely off-page. Without this clause the check failed Kuwabata and Kashikawa for
    exactly that invisible tail."""
    _c = [(q[0] * px + q[1] * py, q[0] * wx + q[1] * wy) for q in poly]
    _d0, _d1 = min(q[1] for q in _c), max(q[1] for q in _c)
    # 25 samples was a 14.7 px step on Kuwabata against a decisive on-page window of 13.0 px - that
    # column's verdict was decided at the sampling limit (settlement-review 2026-08-29). A miss falls
    # toward leniency (a dropped column resets the run) so it cannot manufacture a failure, but it can
    # hide one on a hook whose arms lie far apart along the wind axis. 200 samples is a ~1.8 px step
    # there, well under a crown.
    _n = 200
    for _k in range(_n + 1):
        _d = _d0 + (_d1 - _d0) * _k / _n
        _qx, _qy = t * px + _d * wx, t * py + _d * wy
        if not point_in_poly(_qx, _qy, poly):
            continue
        if view and not (view[0] <= _qx <= view[0] + view[2] and view[1] <= _qy <= view[1] + view[3]):
            continue
        return True
    return False


def _seg_0285_073__cx_1(*, M: Any = _UNBOUND, cx: Any = _UNBOUND, cy: Any = _UNBOUND, g: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0285.073 (cx, cy, g, vg_clumps) - body verbatim from _seg_0285__wells_clear_of_shrine_and_torii (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'village', 'hamlet') and scale in ('town', 'village', 'hamlet', 'city'):
        vg_clumps = [(cx, cy, g.get("r", 6)) for g in M.get("village_groves", []) for cx, cy in g.get("clumps", [])]
    return _kept(locals(), ('cx', 'cy', 'g', 'vg_clumps'))


# EAST SUN (option): a kitchen garden on a house's lee/EAST side loses its MORNING sun if a neighbor's
# grove arm (or a copse) stands hard against its east. Where a small SOUTHWARD nudge into open ground
# would clear it (the tree then falls to the garden's NE), the placement takes it (_relax_gardens_south).
# This fires ONLY on an AVOIDABLE case - a garden still east-shaded though a clear south-shift existed -
# so a garden genuinely boxed in to the south (paddy/lane/neighbor) is exempt. WHY: settlements.md 'gardens'.
# scoped to the BUNDLE-path farmsteads (villages + to-scale hamlets), where _relax_gardens_south runs;
# a town/city places its outside farms on the legacy path (no south-nudge), so the rule does not apply.


# SCALE: the typical grove must read as the LARGEST homestead appurtenance - a real stand of dozens
# of trees, not a clump. The median grove's total footprint (its arms) must be >= ~0.75x the house
# it shelters (the spacious farms run well above; a single-arm grove on a cramped farm pulls the
# median but stays substantial). This catches a regression that shrinks groves back to a few trees.


# VISIBLE: the dooryard garden must not be buried under a grove (the homestead solver spaces the
# garden to the LEE side and the grove to the windward, so they never stack). A garden substantially
# overlapped by a grove arm is a regression. WHY: settlements.md "Homestead groves".


# WHERE POSSIBLE: a grove is drawn on EVERY farmhouse that has windward room - the yashikirin ringed
# every dispersed farmstead - so a grove-LESS farm must be one whose windward side is genuinely blocked
# (a paddy, a neighbor, or the sun-corridor south of a yard). If a grove-less farm has CLEAR windward
# room, the generator omitted a grove it could have placed. Replaces the old blunt presence floor.


# NUCLEATED villages shelter behind a COMMUNAL fengshui WINDBREAK (风水林), NOT per-house groves: a
# dense grove belt on the high WINDWARD back edge (the winter-monsoon wall + sacred back-village
# grove), a smaller cluster at the low water-mouth entrance, and scattered bamboo/fruit copses. So a
# nucleated village is NOT required to grove every farm (groves_where_possible is skipped above for
# meta.nucleated); instead it MUST carry the village windbreak, on the windward side, off the paddies.
# WHY (the fengshui-forest research - ~2 groves/village, a ~1-2 ha back grove at ~3,400 stems/ha, a
# water-mouth cluster, kept off the crops and the road): settlements.md 'Village windbreak'.


def _seg_0285_082__vgroves(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0285.082 (vgroves) - body verbatim from _seg_0285__wells_clear_of_shrine_and_torii (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'village', 'hamlet') and scale in ('town', 'village', 'hamlet', 'city'):
        vgroves = M.get("village_groves", [])
    return _kept(locals(), ('vgroves',))


def _seg_0285_083__village_windbreak_present(
    *,
    M: Any = _UNBOUND,
    c: Any = _UNBOUND,
    canopy: Any = _UNBOUND,
    ccx: Any = _UNBOUND,
    ccy: Any = _UNBOUND,
    check: Any = _UNBOUND,
    fline: Any = _UNBOUND,
    fnear: Any = _UNBOUND,
    forest_shelters: Any = _UNBOUND,
    g: Any = _UNBOUND,
    h: Any = _UNBOUND,
    houses: Any = _UNBOUND,
    i: Any = _UNBOUND,
    lee: Any = _UNBOUND,
    meta: Any = _UNBOUND,
    nestle_d: Any = _UNBOUND,
    roofs: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    subst_wb: Any = _UNBOUND,
    vgroves: Any = _UNBOUND,
    windbreaks: Any = _UNBOUND,
    windward: Any = _UNBOUND,
    wvx: Any = _UNBOUND,
    wvy: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0285.083 (village_windbreak_embraces_cluster, village_windbreak_on_windward_side, village_windbreak_present, village_windbreak_scales_with_cluster) - body verbatim from _seg_0285__wells_clear_of_shrine_and_torii (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'village', 'hamlet') and scale in ('town', 'village', 'hamlet', 'city') and meta.get("nucleated") and len(houses) >= 10:
        windbreaks = [g for g in vgroves if g.get("role") == "windbreak"]
        check(
            "village_windbreak_present",
            bool(windbreaks),
            "a nucleated village shelters behind a COMMUNAL windbreak (a fengshui back-village grove), but "
            "no role='windbreak' village grove is present - add s.village_grove(..., role='windbreak') on the "
            "high windward edge",
        )
        # the belt backs the cluster on the WINDWARD/high side (default NW) - its centroid must lie
        # windward of the house-cluster centroid, so the wall faces the cold wind, not the sunny field side
        ccx = sum(h["x"] for h in houses) / len(houses)
        ccy = sum(h["y"] for h in houses) / len(houses)
        lee = [(round(g["x"]), round(g["y"])) for g in windbreaks if (g["x"] - ccx) * wvx + (g["y"] - ccy) * wvy <= 0]
        # THE BELT EMBRACES THE CLUSTER - the doctrine's "nestles against and embraces"
        # (GM 2026-07), automated via a form-aware ADJACENCY metric after the windward-
        # canopy-fraction metric failed calibration (approved Kikuta scores 4-18% on it):
        # at least one SUBSTANTIAL windbreak grove (>= 12 clumps) must stand within 150px
        # of a farmhouse. Far corner forest masses are welcome extras; a map with ONLY far
        # masses is decoration, not a wind wall. Calibrated 2026-07: approved maps nestle
        # at 37-131px (Kikuta's ribbon belt is the 131 outlier).
        # a map whose wood is a REAL FOREST (M["forest"], the edge-feature wood) can let that
        # forest BE the windbreak - the strongest wind wall of all - but ONLY where the wood
        # actually shelters THIS cluster: its tree line must come within the same NESTLE
        # distance of a farmhouse AND stand WINDWARD of the cluster centroid. A blanket
        # "has a forest -> exempt" is what let Moritono pass with an 11-clump belt while its
        # Shirin Forest sat 1,089 ft away on the LEE (E) side under an NW wind (GM 2026-07-25):
        # a wood downwind and a fifth of a mile off breaks no wind. Small forest_patches do NOT exempt.
        fline = M.get("forest") or []
        fnear = min(((seg_dist(h["x"], h["y"], fline[i], fline[i + 1]), fline[i]) for h in houses for i in range(len(fline) - 1)), default=None)
        forest_shelters = fnear is not None and fnear[0] <= 150 and (fnear[1][0] - ccx) * wvx + (fnear[1][1] - ccy) * wvy > 0
        subst_wb = [] if forest_shelters else [g for g in windbreaks if len(g.get("clumps", [])) >= 12]
        nestle_d = min((min(math.hypot(c[0] - h["x"], c[1] - h["y"]) for c in g["clumps"] for h in houses) for g in subst_wb), default=None)
        check(
            "village_windbreak_embraces_cluster",
            forest_shelters or (bool(subst_wb) and nestle_d is not None and nestle_d <= 150),
            f"no substantial windbreak belt (>= 12 clumps) nestles against the farm cluster (nearest {None if nestle_d is None else round(nestle_d)}px; want <= 150) - "
            f"the back-village grove EMBRACES the houses' windward fringe; far corner masses alone are decoration",
        )
        pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
        # THE BELT SCALES WITH THE CLUSTER (GM 2026-07-25, after Moritono's belt read as a few
        # blobs behind 16 farmhouses). The >= 12-clump embrace test above is a FIXED floor, so a
        # belt sized for a 5-house corner passes unchanged behind a whole hamlet. Measure the
        # SHELTER the map actually draws - the windbreak's canopy disks plus any per-house
        # yashikirin footprints (a map may do both, e.g. Hikari-no-Sato) - against the ROOF area
        # it shelters. Both sides are px^2, so the ratio is scale-free (a 2 ft/px village draws
        # smaller roofs AND, per meta()'s village bscale exemption, larger clumps; the ratio is
        # unaffected). WHY this framing: the doctrine (settlements.md 'Village windbreak') wants
        # the belt to be the settlement's LARGEST vegetation feature, and the research figure -
        # a modest village back grove under 1 ha, ~1,800 sq ft per household - sits near ratio
        # ~1.3 at our house sizes. So 0.40 is a floor against absurdity, not a target: a wind
        # wall covering less than half the ground its own roofs do is decoration. Calibrated on
        # the pool 2026-07-25: approved maps run 0.45 (Hoshizora, a town whose farm zone is a
        # thin wedge) through 7.27 (Hikari-no-Sato); Moritono's belt scored 0.30.
        canopy = sum(len(g.get("clumps", [])) * math.pi * g.get("r", 14) ** 2 for g in windbreaks)
        canopy += sum(g.get("w", 0) * g.get("h", 0) for g in M.get("groves", []))
        roofs = sum(h.get("w", 0) * h.get("h", 0) for h in houses)
        check(
            "village_windbreak_scales_with_cluster",
            forest_shelters or canopy >= 0.40 * roofs,
            f"the windbreak is too small for the cluster it shelters: {round(canopy)}px^2 of canopy over "
            f"{len(houses)} farmhouses covering {round(roofs)}px^2 of roof (ratio {canopy / roofs if roofs else 0:.2f}; want >= 0.40) - "
            f"the back-village grove is the settlement's LARGEST vegetation feature, so deepen the belt "
            f"(more clump rows) or wrap it further around the windward faces",
        )
    return _kept(locals(), ('c', 'canopy', 'ccx', 'ccy', 'fline', 'fnear', 'forest_shelters', 'g', 'h', 'i', 'lee', 'nestle_d', 'roofs', 'subst_wb', 'windbreaks'))


# every village grove (of any role) is DRY woodland - no TREE may stand in a flooded paddy. Test the
# DRAWN CLUMPS, not the recorded bbox center (GM 2026-07-25, same correction commons_clear_of_paddies
# already took): a back-village belt is a long crescent hugging the field edge, so the center of the
# box around it can sit over the crop while every tree in it stands on dry ground - Ueda's 87-clump
# belt scored exactly that. Testing the clumps also gives the check MORE teeth, not less: it now
# measures the same thing the placement does (village_grove skips a clump landing in a field), so a
# gen whose engine-side field list is empty - the recurring trap - is caught here instead of hidden.
# A grove that records no clumps at all falls back to its center, for older maps; one that records
# neither (a bare poly, as some check fixtures carry) contributes no test point rather than raising.


# A grove clump (a tree blob, radius r) may abut a farmstead - trees stand right up against a house
# wall - but it must NOT OVERLAP a building/yard/garden footprint (a tree drawn ON the roof reads
# wrong). Both the placement (the village_grove keep-out uses the clump's FULL radius) and this check
# enforce it. The nominal blob radius is the measure; canopy leaves spilling a few px onto the eaves
# are "adjacent," which is fine. Covers the whole homestead: house, threshing yard, kitchen garden,
# draft byre, farm shed. WHY (trees beside, not on, the buildings): settlements.md 'Village windbreak'.


# FUEL-AND-FODDER COMMONS - the degraded open grazing/scrub on the far side, BEYOND the back-grove.
# South China's hills were stripped for fuel/timber over a millennium (open pine + grass + erosion),
# so past the protected grove is NON-ARABLE waste: coarse grass, brush, scraggly pines - a commons,
# not a field, and never the flooded paddy. The land toposequence is village -> back-grove -> fuel
# commons, so the commons sits on the WINDWARD/high side and FURTHER out than the windbreak. WHY (the
# denuded hills + back-slope waste; graves + dry hill-crops also live here): settlements.md 'Village windbreak'.
# Test the DRAWN OUTCOME, not the patch's bbox CENTER. `commons()` skips every paddy point when it
# scatters, so scrub can never actually be drawn on a flooded field - "is the center over water" was
# only ever a PROXY for that, and a wrong one: an INTERIOR fill (the patch that clothes the voids an
# irregular field leaves inside its own bbox) legitimately has its center on the crop while every
# glyph it draws falls in the voids around it. Scoring the center would fail a correct patch, which
# is the same bbox-stands-in-for-real-geometry mistake as the phantom field tail. What genuinely
# goes wrong is a patch placed where it can clothe NOTHING - it silently draws nothing at all - so
# that is what we test: sample each patch and require real open (non-crop) ground under it.


def _seg_0285_091__commons(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0285.091 (commons) - body verbatim from _seg_0285__wells_clear_of_shrine_and_torii (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'village', 'hamlet') and scale in ('town', 'village', 'hamlet', 'city'):
        commons = M.get("commons", [])
    return _kept(locals(), ('commons',))


def _seg_0598__nucleated_records_cluster_seeding(*, M: Any = _UNBOUND, check: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 598 (settlement_records_cluster_seeding) - hand-added 2026-08-16 past the
    legacy range (see _seg_0595 in segments_08 for the numbering convention). New-style:
    writes=()."""
    # A KNOB THAT CAN SILENTLY NOT-RECORD IS THE "CHECK THAT NEVER RUNS" SHAPE (known-open
    # ledger 2026-08-16, Kashikawa: the front rows + lane frontage seated all 20 houses, the
    # cluster-seeds cloud never ran, and the rolled cluster_shape knob went unhonored with
    # no trace on the manifest - the twin-detector axis silently fell back to the bbox
    # aspect). The declaration-exists ratchet (settlement_declares_a_land_fall is the
    # model): a nucleated scripted map must record either the honored knob
    # (meta.cluster_shape, written by cluster_seeds when the cloud runs) or the seeding
    # mode that replaced it (meta.cluster_seeding, written by stage_homesteads).
    if M["meta"].get("generated_by") and M["meta"].get("nucleated"):
        _cs_ok = ("cluster_shape" in M["meta"]) or ("cluster_seeding" in M["meta"])
        check(
            "settlement_records_cluster_seeding",
            _cs_ok,
            "a nucleated scripted map records neither meta.cluster_shape (the cluster-seeds cloud ran and honored the knob) nor meta.cluster_seeding (the rows/frontage passes seated every house and the rolled shape went unhonored) - a rolled knob must leave a trace either way, or it can silently not-record with nothing warning; stage_homesteads records the seeding mode",
        )
    return _kept(locals(), ())


_BELT_MAX_GAP_FT = 30.0
"""The widest hole a windbreak belt may carry, measured ACROSS the wind.

WHAT THIS IS NOT, because the first version got it wrong and failed 17 of 48 held-out cohort seeds:
it is not a minimum DEPTH per column. A belt is a jittered scatter, not a wall of masonry -
`village_grove` lays clumps on a 20 px grid with a 14 px radius and +/-10 px of jitter, so two
neighbors can sit 40 px apart and leave a single 10 ft column with no clump centre near it. Demanding
canopy in every column measures the scatter's pitch, not the belt's integrity, and a rule calibrated
that way passes the four maps whose belts happen to be dense and fails a third of the cohort.

What a reader actually sees, and what a wind wall actually fails at, is a GAP: a RUN of bare columns
wide enough to see through. 30 ft is a clump's own drawn diameter (28 ft) rounded up - narrower than
that and the neighboring canopies close the view. The two real breaches this rule exists for
measured ~45 ft (a wellhead seated inside the belt) and ~60 ft (a peer session's lane crossing it);
a scatter's own worst pitch is ~12 ft.
"""


def _seg_0613__village_windbreak_is_continuous(*, M: Any = _UNBOUND, check: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0613 (village_windbreak_is_continuous) - added 2026-08-18.

    NOTHING MEASURED THIS, and a wind wall with a hole through it passed every check we had. Inashiro
    shipped one that morning: a wellhead seated inside the belt suppressed the clumps around it (the
    grove keeps canopy off a well) and took a 40 ft band from six clumps to one. It was fixed, and
    then a peer session's lane web crossed the belt on the same map and took the belt-wide minimum
    from 17.1 ft to 4.8 ft - a 3 ft footpath removing ~45 ft of wall. Two different causes, one
    invisible failure, because every windbreak check we had asks about the belt's POSITION (windward
    side, embraces the cluster, scales with the cluster) and none about whether it is a wall.

    MEASURED ALONG THE WIND, PER COLUMN ACROSS IT - and that is the correction two reviewers made to
    my first framing. A bare LATITUDE is not a hole: wind crossing it still meets canopy north and
    south, and a per-latitude scan flags a perfectly healthy diagonal belt while missing a genuinely
    thin window. What matters is how much canopy the wind passes through, so the belt is projected
    onto the wind axis and the across-wind axis, and each column's covered depth is summed with
    overlaps merged."""
    _wb = [g for g in M.get("village_groves", []) if g.get("role") == "windbreak" and g.get("clumps")]
    if M["meta"].get("generated_by") and _wb:
        _wv = {"N": (0.0, -1.0), "NE": (0.7071, -0.7071), "E": (1.0, 0.0), "SE": (0.7071, 0.7071), "S": (0.0, 1.0), "SW": (-0.7071, 0.7071), "W": (-1.0, 0.0), "NW": (-0.7071, -0.7071)}
        _wx, _wy = _wv.get(str(M["meta"].get("windward", "S")), (0.0, 1.0))
        _px, _py = -_wy, _wx  # the across-wind axis
        _thin: list[tuple[int, int, int]] = []
        for _g in _wb:
            _r = float(_g.get("r", 6))
            # AN OFF-PAGE CLUMP STILL FILLS AN ON-PAGE COLUMN, and that asymmetry with the window is
            # DELIBERATE (feature 137 T05, re-tested 2026-08-29). The acceptance review read it as a
            # one-sided test - the window is clipped to the page, so why is the planting not - and the
            # symmetric version was implemented and rolled: credit a clump only where its crown reaches
            # the view. It fails Mizuguchi with a 60 ft run at x 1133..1183, where the belt polygon holds
            # 48 px of visible ground (y 1902..1950) at the frame's bottom edge and the nearest clumps
            # sit at y 1971-1983 with their crowns 5 px short of it.
            #
            # THAT GROUND IS A HOMESTEAD, and the belt is FORBIDDEN to plant on it: one farmhouse, two
            # threshing yards, two kitchen gardens and a persimmon stand within 90 ft of (1160, 1925),
            # and a yard's southern sun corridor and a garden's eastern one are keep-outs the seating
            # must respect. So the symmetric check demands canopy where the generator is right to refuse
            # it - a check failing for something a placement rule already gets right, which is the exact
            # class the GM ruled out (2026-08-29). The reader loses nothing: the canopy visible in that
            # gap is the copse, which is what a dooryard grove is for.
            #
            # The asymmetry is therefore kept and now has a reason: the WINDOW asks "is there belt here
            # for a reader to see", and the PLANTING asks "is the belt holed", which a clump answers
            # whether or not the frame happens to cut it. What the review is right about is that the
            # guarantee is weaker than it looks - delete Mizuguchi's copse and this still passes. Closing
            # that needs the check to know the seating's keep-outs, which is a second copy of the
            # generator inside the gate; not worth it for one column at one page edge.
            _pr = [(c[0] * _px + c[1] * _py, c[0] * _wx + c[1] * _wy, c[0], c[1]) for c in _g["clumps"] + (_g.get("clumps_offpage") or [])]
            # AN EMPTY COLUMN IS THE WORST CASE, NOT A SKIPPED ONE. The first cut of this check wrote
            # `if _spans:` and so scored a column with NO canopy as nothing at all - it passed a
            # sabotaged Inashiro with a 60 ft band cut clean out of its belt, which is the exact
            # shape both real causes produced. A check that cannot see the total absence of the thing
            # it measures is the `if meta.get(...)` trap in another costume, and this segment is the
            # third time today it has been written by accident.
            #
            # The ENDS are excluded by one clump radius at each side: a belt tapers where it stops,
            # and the outermost column of a diagonal belt legitimately carries one clump's worth.
            # ...AND A COLUMN THE BELT DOES NOT OCCUPY IS NOT A HOLE IN IT (feature 152, GM ruling
            # 2026-08-29: "we should just do whatever was historically true"). The research pass that
            # ruling authorized found that neither literature describes a belt as a closed perimeter:
            # a Chinese village's fengshui forest is a SYSTEM OF SEPARATE PATCHES with open ground
            # between them by design, and Honda Seiroku's 1915 founding definition of `yashikirin` puts
            # the Japanese farmstead grove on the west and north sides only, leaving the entrance side
            # open. So the defect is a hole in the PLANTED RUN, and the absence of belt is not one -
            # see settlements/vegetation.md, "A shelter belt is not a RING".
            #
            # This walk projects onto a straight across-wind axis, so on a belt that BOWS around a plot
            # the chord between its outermost clumps crosses ground the belt's own footprint never
            # covers. Measured on Kuwabata: the flagged 40 ft run leaves the belt polygon after 14 ft,
            # and no amount of seating will fill ground the band does not occupy. Columns are therefore
            # counted only where the belt's own polygon has depth.
            _poly = [(float(_a), float(_b)) for _a, _b in (_g.get("poly") or [])]
            # THE WINDOW IS THE BELT'S OWN FOOTPRINT, NOT ITS LAST CLUMP (settlement-review 2026-08-29,
            # acceptance re-check). Bounding the scan by `max(clump) - r` makes the check structurally
            # unable to see the one failure that matters most: a belt whose PLANTING stops before its
            # polygon does. On Kuwabata the scan ended at u=1301 while the polygon ran to 1350 and the
            # easternmost farmhouse sat at 1339 - so the column a reader would point at was outside the
            # window by construction, and "the belt stops before the cluster does" could not fail.
            # The polygon is the belt's own statement of the ground it holds; it is the honest window.
            # The window is the whole polygon; `_column_in_belt` drops the columns of it that are off
            # the page, so the scan asks for canopy exactly where a reader can look for it.
            _pu = [q[0] * _px + q[1] * _py for q in _poly] if _poly else []
            _lo = (min(_pu) if _pu else min(p[0] for p in _pr)) + _r
            _hi = (max(_pu) if _pu else max(p[0] for p in _pr)) - _r
            _run = 0.0
            _t = _lo
            while _t <= _hi:
                if any(abs(p[0] - _t) <= _r for p in _pr):
                    _run = 0.0
                elif _poly and not _column_in_belt(_t, _px, _py, _wx, _wy, _poly, M["meta"].get("view")):
                    _run = 0.0  # the belt does not reach this column: its edge, not its hole
                else:
                    _run += 10.0
                    if _run > _BELT_MAX_GAP_FT:
                        _near = min(_pr, key=lambda p: abs(p[0] - _t))
                        _thin.append((round(_near[2]), round(_near[3]), round(_run)))
                _t += 10.0
        check(
            "village_windbreak_is_continuous",
            not _thin,
            f"the windbreak carries a gap wider than {_BELT_MAX_GAP_FT:.0f} ft at {len(_thin)} point(s): {sorted(set(_thin))[:4]} "
            f"(x, y, ft of bare run ACROSS the wind) - a belt with a hole in it is not a wind wall. Measured as a RUN of bare columns rather than "
            f"as depth per column, because a belt is a jittered scatter and its own pitch leaves single columns empty. Let the belt re-seat around "
            f"whatever blocked it rather than losing the column",
        )
    return _kept(locals(), ())


def _cluster_aspect(xs: Any, ys: Any) -> float:
    """The house cloud's long:short ratio on ITS OWN principal axis - the mirror of
    `hamletgen.homesteads.cluster_aspect`.

    Duplicated because the gate may not import the generator (`hamletgen` imports `check_village`, not
    the reverse), and pinned to it by `tests/hamletgen/test_cluster_shape.py`, which evaluates BOTH on
    the same point sets rather than comparing source text.

    A page-axis bbox ratio was the first cut here and it was wrong in both directions across the
    shipped pool - it tends to 1.0 for a band on a diagonal, so it recorded Kashikawa's visibly 3.8:1
    ribbon as 1.22 and denied its honest `elongated`, while honoring Sawada's `round` on a cluster
    drawing 3.02:1. See the generator's docstring for the measurements."""
    _n = len(xs)
    if _n < 2:
        return 1.0
    _mx, _my = sum(xs) / _n, sum(ys) / _n
    _sxx = sum((x - _mx) ** 2 for x in xs) / _n
    _syy = sum((y - _my) ** 2 for y in ys) / _n
    _sxy = sum((x - _mx) * (y - _my) for x, y in zip(xs, ys, strict=True)) / _n
    _th = 0.5 * math.atan2(2.0 * _sxy, _sxx - _syy)
    _c, _s = math.cos(_th), math.sin(_th)
    _along = [x * _c + y * _s for x, y in zip(xs, ys, strict=True)]
    _across = [-x * _s + y * _c for x, y in zip(xs, ys, strict=True)]
    _du = max(_along) - min(_along)
    _dv = max(_across) - min(_across)
    return float(max(_du, _dv) / max(1.0, min(_du, _dv)))


def _seg_0615__cluster_shape_matches_the_drawing(*, M: Any = _UNBOUND, check: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0615 (cluster_shape_matches_the_drawing) - added 2026-08-19.

    A DECLARED KNOB MUST DESCRIBE THE SHEET. `cluster_shape` is rolled per settlement and printed in
    every cohort-audit header, and until this rule it was honored on NO map: it fed only the cloud
    seeding pass, which never runs because the front rows and lane frontage seat every household.
    Round, elongated and crescent all drew the same 3:1 band, and a peer session spent an attempt
    blaming the knob for a placement failure it could not have caused, because nothing read it.

    It binds at the cluster band and the front row's reach now - but NOT above the lane skeleton,
    which on a large hamlet seats most of the cluster and spreads it whatever the band says. So the
    generator declares the shape only where the drawing has it and records
    `cluster_shape_unhonored` where the skeleton overrode it. This holds that honest: a stamped
    shape whose drawn aspect contradicts it is a lie `TWIN_AXES` would read and act on, and a map
    that declares NEITHER key has silently dropped the record altogether."""
    if M["meta"].get("generated_by") and M["meta"].get("scale") in ("hamlet", "village") and M.get("houses"):
        _cs = M["meta"].get("cluster_shape")
        _cu = M["meta"].get("cluster_shape_unhonored")
        # The DRAWN aspect band per shape - the observable, not the generator's band parameter.
        # Mirrors `hamletgen.consts.CLUSTER_DRAWN_ASPECT`, which carries the reasoning and the
        # measurements; the gate may not import the generator, so `tests/hamletgen/test_cluster_shape.py`
        # pins the two copies equal. Comparing against the BAND parameter instead is the bug this
        # replaced - see that docstring.
        _asp = {"round": (1.0, 2.0), "crescent": (1.9, 4.2), "elongated": (2.8, 12.0), "split": (1.9, 4.2)}
        check(
            "cluster_shape_matches_the_drawing",
            bool(_cs or _cu),
            "the map records neither `cluster_shape` nor `cluster_shape_unhonored` - the rolled shape has to leave a trace either way, "
            "or a knob that never binds looks exactly like one that always does",
        )
        if _cs:
            _xs = [h["x"] for h in M["houses"]]
            _ys = [h["y"] for h in M["houses"]]
            _dr = _cluster_aspect(_xs, _ys)
            _lo, _hi = _asp.get(str(_cs), (1.9, 4.2))
            check(
                "cluster_shape_matches_the_drawing",
                _lo <= _dr <= _hi,
                f"the map declares cluster_shape={_cs!r}, which wants a drawn cluster between {_lo:.1f}:1 and {_hi:.1f}:1, and draws "
                f"{_dr:.1f}:1 - a declared knob that the sheet does not carry is worse than an undeclared one, because TWIN_AXES reads it. "
                f"Record `cluster_shape_unhonored` instead when the lane skeleton overrides the band",
            )
    return _kept(locals(), ())


def _seg_0616__copse_stands_clear_of_the_belt(*, M: Any = _UNBOUND, check: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0616 (copse_stands_clear_of_the_belt) - added 2026-08-19.

    ONE GROVE MAY NOT BE PLANTED INSIDE ANOTHER. The copse and the windbreak are different features
    doing different jobs - `settlements/vegetation.md` says outright that "the copse, not the belt,
    fills the inner gaps" - and the copse is seated AFTER the belt, with nothing in the keep-out list
    stopping it landing on the belt's own ground. Measured on Inashiro before the fix (settlement-
    review, this date): clump-to-nearest-belt-clump distances of 9, 8, 6, 4, 6, 4, 11, 9, 26, 30 and
    83 ft against a belt clump radius of 14 - **10 of 11 copse clumps inside the belt's canopy**,
    spanning x 1096-1188 while the houses span 1108-1331. The dooryards got no greenery at all and a
    whole feature was invisible on the sheet while every check stayed green.

    This is the invisible-feature class, and it is exactly why it needs a rule rather than only a
    keep-out: a copse hidden in the belt looks identical, from the manifest, to a copse that is
    there. Measured to the RECORDED clumps, not to the grove bbox - a belt's bbox is a long rectangle
    whose corners are open ground the copse may legitimately use, so a bbox test would forbid seats
    that are correct."""
    if M["meta"].get("generated_by") and M["meta"].get("scale") in ("hamlet", "village"):
        _belts = [g for g in M.get("village_groves", []) if g.get("role") in ("windbreak", "water_mouth")]
        _copses = [g for g in M.get("village_groves", []) if g.get("role") == "copse"]
        _buried: list[tuple[int, int]] = []
        for _cp in _copses:
            for _cl in _cp.get("clumps") or []:
                for _b in _belts:
                    _br = float(_b.get("r") or 0.0)
                    if any((float(_cl[0]) - float(_bc[0])) ** 2 + (float(_cl[1]) - float(_bc[1])) ** 2 < _br * _br for _bc in (_b.get("clumps") or [])):
                        _buried.append((round(float(_cl[0])), round(float(_cl[1]))))
                        break
        check(
            "copse_stands_clear_of_the_belt",
            not _buried,
            f"{len(_buried)} dooryard-copse clump(s) stand INSIDE the windbreak's canopy at {_buried[:4]} - the copse fills the gaps among the "
            f"houses and the belt is the wind wall; a clump planted in the belt is ink nobody can see, and the dooryards it should have greened "
            f"stay bare. Add the planted groves' clumps to the copse's keep-out (homestead_parts.village_grove's `occ`)",
        )
    return _kept(locals(), ())


def _seg_0618__village_groves_visibly_stocked(*, M: Any = _UNBOUND, check: Any = _UNBOUND) -> dict[str, Any]:
    """A DECLARED GROVE MUST ACTUALLY HOLD TREES - added 2026-08-20 (settlement-review, Inashiro).

    Every other grove rule asks where the clumps are relative to something ELSE: clear of the belt, of
    the paddies, of the structures, of the lanes. Not one asks whether the feature the record declares
    was drawn at all. So Inashiro shipped `village_groves[1]` - role copse, w 255.0, h 740.9 - holding
    exactly ONE clump, and the whole battery stayed green. A 255 x 741 ft grove with one tree in it.

    THE CAUSE WAS THE PREVIOUS CHECK. 0616's keep-out reserves the belt's canopy against the copse;
    Inashiro's windbreak has 227 clumps along the cluster's west fringe, the copse is seated after it
    over the same house cloud, and a blocked clump in a SPARSE grove used to be dropped rather than
    relocated - so the copse went 11 -> 1. 0616 went green and nothing measured what survived. This is
    the companion rule that would have caught it, and it is the general form: fixing where a feature
    may not go says nothing about whether any of it remains.

    THE FLOOR, measured across the four scripted hamlets as clumps per 100k sq px of recorded
    footprint: inashiro copse 0.53 (the defect), mizuguchi 4.24, sawada 3.90, kashikawa 4.43, and a
    dense belt ~110. Set at 1.5 - 2.6x below the healthiest scatter and 2.8x above the defect. It is a
    floor on VISIBILITY, not a density target: how many gaps a cluster leaves for its copse is the
    map's business, and `settlements/vegetation.md` only requires that the copse fill them."""
    if M["meta"].get("generated_by") and M["meta"].get("scale") in ("hamlet", "village"):
        _bare: list[str] = []
        for _g in M.get("village_groves", []):
            _area = float(_g.get("w") or 0.0) * float(_g.get("h") or 0.0)
            if _area <= 0:
                continue
            _n = len(_g.get("clumps") or [])
            _dens = _n * 1e5 / _area
            if _dens < 1.5:
                _bare.append(f"{_g.get('role') or 'grove'} {float(_g.get('w') or 0):.0f}x{float(_g.get('h') or 0):.0f}px holds {_n} clump(s) ({_dens:.2f}/100k)")
        check(
            "village_groves_visibly_stocked",
            not _bare,
            f"{len(_bare)} recorded grove(s) hold almost no trees: {_bare[:3]} (floor 1.5 clumps per 100k sq px) - the map DECLARES a feature it does not "
            f"draw, so the dooryards it should have greened stay bare while every other grove rule reads green. Let the sparse scatter re-seat around "
            f"local obstacles instead of dropping the clump (homestead_parts._reseat)",
        )
    return _kept(locals(), ())


def _seg_0617__captions_clear_the_ways_they_stand_on(*, M: Any = _UNBOUND, check: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0617 (captions_clear_the_ways_they_stand_on) - added 2026-08-19.

    A CAPTION'S HALO MUST NOT NOTCH THE WAY ITS SUBJECT STANDS ON. Captions are drawn with a 3 px
    background halo (`paint-order="stroke"`), and a kosatsuba is sited ON a verge by construction - so
    the default seat lands on the lane about as often as not. Measured on Inashiro before the fix: the
    halo knocked a visible notch out of the map's busiest internal lane, between the words "notice"
    and "board". The founding-run "caption pierced by its own feature" defect, inverted.

    WHY A RULE AND NOT JUST A BETTER SEAT. The seat logic now ladders through candidate positions, and
    on three of four maps it finds one with real clearance - but it found 0.2 ft on the fourth and
    called that a pass, because nothing measured it. A clearance that holds by luck is the shape this
    engine keeps producing: green today, a defect after the next re-pack, with no test that notices.

    Measured against the RECORDED caption box, not its anchor - the halo follows the box - and against
    the lane's EDGE, not its centerline. 2 ft of margin: a 3 px halo plus the antialiasing either side,
    which is the least that guarantees no ink touches the tread."""
    if M["meta"].get("generated_by") and M["meta"].get("scale") in ("hamlet", "village"):
        _notched: list[tuple[int, int, int]] = []
        for _lab in M.get("labels") or []:
            if len(_lab) < 6:
                continue
            _lx0, _ly0, _lx1, _ly1 = (float(_lab[0]), float(_lab[1]), float(_lab[2]), float(_lab[3]))
            _corners = ((_lx0, _ly0), (_lx1, _ly0), (_lx0, _ly1), (_lx1, _ly1), ((_lx0 + _lx1) / 2, (_ly0 + _ly1) / 2))
            for _ln in M.get("lanes") or []:
                _pts = _ln.get("pts") or []
                _half = float(_ln.get("w") or 3) / 2.0
                for _i in range(len(_pts) - 1):
                    if any(seg_dist(_cx, _cy, _pts[_i], _pts[_i + 1]) - _half < 2.0 for _cx, _cy in _corners):
                        _notched.append((round(_lx0), round(_ly0), round(_half * 2)))
                        break
                else:
                    continue
                break
        check(
            "captions_clear_the_ways_they_stand_on",
            not _notched,
            f"{len(_notched)} caption(s) sit within 2 ft of a lane's tread at {_notched[:3]} (x, y, lane width) - the 3 px halo notches the way, "
            f"and a reader sees a break in the roadway rather than a label beside it. The seat ladders through candidate positions "
            f"(fixtures.py's kosatsuba); the clearance is not monotonic in the offset, so the ladder has to reach past the first dip",
        )
    return _kept(locals(), ())


# WHY: <one paragraph - what the research found, the decision it drove, the departure taken>.
# Declare EVERY input the body reads as a keyword parameter (an undeclared one is a NameError at
# gate time, not at import), and keep the `_kept` tuple a LITERAL of the names this body binds.


# WHY: <one paragraph - what the research found, the decision it drove, the departure taken>.
# Declare EVERY input the body reads as a keyword parameter (an undeclared one is a NameError at
# gate time, not at import), and keep the `_kept` tuple a LITERAL of the names this body binds.


# WHY: <one paragraph - what the research found, the decision it drove, the departure taken>.
# Declare EVERY input the body reads as a keyword parameter (an undeclared one is a NameError at
# gate time, not at import), and keep the `_kept` tuple a LITERAL of the names this body binds.


def _seg_0618_502__bamboo_stands_clear_of_paddies(
    *,
    M: Any = _UNBOUND,
    check: Any = _UNBOUND,
    meta: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    bamboo_stands_clear_of_paddies_bad: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment (bamboo_stands_clear_of_paddies) - no vertex of a bamboo stand lies inside a paddy outline: a take-yabu stands on the dry margin above the rice, never in it (feature 133 T47)."""
    if scale in ("hamlet", "village", "town"):
        bamboo_stands_clear_of_paddies_bad = []
        _bcp_fields = [[(float(a), float(b)) for a, b in f["outline"]] for f in (M.get("fields") or []) if f.get("outline")]
        # THE DRY CROP IS CROP TOO (settlement-review, Mizuguchi, feature 145): this read paddy outlines alone, so a
        # take-yabu standing 12.2 ft inside a soybean plot passed the gate green. The placer refuses both now
        # (hamletgen.bamboo_seats); the check measures both, so placement and its check read the same ground.
        _bcp_fields += [[(float(a), float(b)) for a, b in (o.get("poly") or [])] for o in (M.get("dry_plots") or []) if len(o.get("poly") or []) >= 3]
        for _b in M.get("bamboo_stands") or []:
            _bp = [(float(a), float(c)) for a, c in (_b.get("poly") or [])]
            if any(point_in_poly(q[0], q[1], fp) for fp in _bcp_fields for q in _bp):
                bamboo_stands_clear_of_paddies_bad.append((round(float(_b["x"])), round(float(_b["y"]))))
        check(
            "bamboo_stands_clear_of_paddies",
            not bamboo_stands_clear_of_paddies_bad,
            f"bamboo stand(s) at {bamboo_stands_clear_of_paddies_bad[:3]} stand in the crop (a flooded paddy or a dry plot) - a take-yabu grows on the margin, not among the beans; the seat scan keeps 12 ft off the outline (hamletgen.bamboo_seats)",
        )
    return _kept(locals(), ("bamboo_stands_clear_of_paddies_bad",))


# WHY: <one paragraph - what the research found, the decision it drove, the departure taken>.
# Declare EVERY input the body reads as a keyword parameter (an undeclared one is a NameError at
# gate time, not at import), and keep the `_kept` tuple a LITERAL of the names this body binds.


def _seg_0618_503__tree_crowns_not_subsumed(
    *,
    M: Any = _UNBOUND,
    check: Any = _UNBOUND,
    meta: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    tree_crowns_not_subsumed_bad: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0618_503 (tree_crowns_not_subsumed) - no canopy tree's center lies under another
    crown. Edge overlap is allowed (neighboring canopies interlace); a crown centered inside another
    is a tree drawn wholly under a neighbor - a suppressed understory stem, which the canopy layer
    this map draws does not show.

    WHY (GM 2026-08-28, on the interactive map's highlight): *"practically every tree might have a
    smaller tree underneath it ... I don't see a single tree which is entirely subsumed within the
    branch structure of a different tree"*. Measured before the rule on Inashiro: 298 of 1,728
    crowns wholly inside another (17%). The rule at the emitters is `woods._crown_seat_clear`; this
    reads M['tree_crowns'] (flat x, y, r runs) with a grid so 2,000 crowns cost a few ms. Tolerance
    0.15 px: the record rounds to 0.1. research/vegetation.md 'Forest density and crown size'."""
    _tc = M.get("tree_crowns") or []
    _crowns = [(_tc[i], _tc[i + 1], _tc[i + 2]) for i in range(0, len(_tc) - 2, 3)]
    if _crowns:
        _cell = 2.0 * max(c[2] for c in _crowns) + 1.0
        _grid: dict[tuple[int, int], list[int]] = {}
        for _i, (_x, _y, _r) in enumerate(_crowns):
            _grid.setdefault((int(_x // _cell), int(_y // _cell)), []).append(_i)
        tree_crowns_not_subsumed_bad = []
        for _i, (_x, _y, _r) in enumerate(_crowns):
            _gx, _gy = int(_x // _cell), int(_y // _cell)
            for _dx in (-1, 0, 1):
                for _dy in (-1, 0, 1):
                    for _j in _grid.get((_gx + _dx, _gy + _dy), ()):
                        if _j <= _i:
                            continue
                        _x2, _y2, _r2 = _crowns[_j]
                        if (_x - _x2) ** 2 + (_y - _y2) ** 2 < (max(_r, _r2) - 0.15) ** 2:
                            tree_crowns_not_subsumed_bad.append((round(_x), round(_y)))
        check(
            "tree_crowns_not_subsumed",
            not tree_crowns_not_subsumed_bad,
            f"{len(tree_crowns_not_subsumed_bad)} tree crown(s) centered under another crown, e.g. {tree_crowns_not_subsumed_bad[:3]} - a canopy tree never stands wholly under a neighbor (woods._crown_seat_clear); the stand or clump that drew it did not see the crowns already on the map",
        )
    return _kept(locals(), ("tree_crowns_not_subsumed_bad",))
