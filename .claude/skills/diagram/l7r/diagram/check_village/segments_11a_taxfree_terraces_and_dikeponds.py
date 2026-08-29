"""Gate segments (taxfree terraces and dikeponds; keys 0564-0580) - bodies verbatim, registry order preserved."""

from typing import Any

from l7r.diagram.settlement import seg_in_ellipse_core

from .common_01_geometry import poly_area
from .common_03_capacity import _UNBOUND, _kept

# Tax-free (temple/monk glebe) plots are OPTIONAL - marking them on the map is a choice, not a
# requirement. The check only validates the COUNT when a map opts in (it drew some, or meta asks for
# them); a village that does not denote them at all is fine.


# TORII COUNTS ARE NUMEROLOGICAL (GM 2026-07-21): in Rokugan the number 7 is even more significant
# than in the real world, so every PROPER religious site - shrine, monastery, temple - carries exactly
# 1, 3, or 7 torii, never another number, unless the hall is specifically marked an outlier
# (shrine_hall(torii_outlier=True), recorded on the religious rec). The rolled distribution per tier
# lives in settlement.roll_torii_count and settlements.md 'Torii'. The floor is 1: a proper hall with
# NO torii reads as the abandoned/anomalous case (historically rare enough that each had a story).
# kind='small_shrine' is EXEMPT - the hokora/wayside tier draws its own miniature token torii as part
# of the glyph and historically mostly had none; it is also excluded from ATTRIBUTION, so a wayside
# shed near a temple's sando cannot steal the temple's gates (that misattribution hid Tango's Daikoku
# pair during the first survey). Each recorded torii is attributed to the NEAREST proper hall.


# A declared LAND-USE overlay must actually be DRAWN (feature 005 US4): a village that says it grows
# mulberry-fishpond / rape / lotus / hill-tea must show plots (or a tea fringe) of it, not just a label.


# NO `dikeponds_are_clustered` CHECK - deliberately, and this is worth recording so nobody "adds
# the missing check" later. The dike-pond conversion really did spread plot-by-plot in patches
# (挖塘培基, a one-plot job in one dry season), and `_pick_overlay_plots` models that. But it is
# NOT INDEPENDENTLY OBSERVABLE here: the eligible set is always a thin contiguous strip of low
# ground (comb = plots abutting the drain, polder = the lowest rows, terraces/ribbon = the lowest
# bands), and every subset of a strip is "clustered" by any nearest-neighbor-vs-span metric. A
# version of this check was written, and an EVEN random scatter of the same count passed it - so
# it would have been a check that cannot fail, which is worse than no check. If a future field
# archetype ever yields a genuinely 2-D eligible region, this becomes testable and worth adding.


# IN-FIELD PADDY FEATURES (feature 012) must honor the per-archetype ELIGIBILITY MATRIX
# (specs/012-.../research.md): a low-pocket pond, a bedrock rock outcrop, or a rare grave island appear
# only where their archetype allows, and NEVER on mulberry_dike_fishpond (open water is its fabric).
# Ponds must additionally sit on LOW/WET ground (the pocket that determines them) - teeth from `wet_plots`
# (written by the field pass) vs the pond record (written by the feature pass), two independent sources.


# A feature-012 pond is sunk INTO one paddy plot - the field tiles AROUND it (the overlap
# registry's own words). Low/wet eligibility (`field_ponds_on_low_ground`, above) cannot hold that:
# it reads the host plot's flag, not the ellipse's extent, so Inashiro (2026-08-16) shipped green
# with a bbox-sized pond in a fan-toe WEDGE - the ellipse spilled over three neighboring wedge
# plots and two drain-hem plots, spoke bunds drawn straight through open water. The bund geometry
# here (`plot_rings` + `drain_hem`) is the FIELD pass's record and the pond is the FEATURE pass's,
# two independent sources; the core inset (4 px, in `seg_in_ellipse_core`) is the rim allowance -
# a bund may TOUCH the shore (the host plot's own ring does), it may not run through the water.


def _seg_0577_500__field_ponds_sunk_into_one_plot(
    *,
    M: Any = _UNBOUND,
    check: Any = _UNBOUND,
    fld: Any = _UNBOUND,
    fp: Any = _UNBOUND,
    spilled: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 577.5 (field_ponds_sunk_into_one_plot) - no bund/hem line through a field pond's water."""
    if M.get("field_ponds"):
        spilled = []
        for fp in M["field_ponds"]:
            for fld in M.get("fields") or []:
                if any(
                    seg_in_ellipse_core(ring[i], ring[(i + 1) % len(ring)], fp["x"], fp["y"], fp["rx"], fp["ry"])
                    for ring in (fld.get("plot_rings") or []) + (fld.get("drain_hem") or [])
                    for i in range(len(ring))
                ):
                    spilled.append([fp["x"], fp["y"]])
                    break
        check(
            "field_ponds_sunk_into_one_plot",
            not spilled,
            f"{len(spilled)} field pond(s) crossed by bund/hem lines (e.g. {spilled[:2]}) - a feature-012 pond is sunk INTO one plot and the field tiles AROUND it; an ellipse spanning plots reads as a flood, not a low pocket",
        )
    return _kept(locals(), ('fld', 'fp', 'spilled'))


# A contour-TERRACES field (feature 005 US4) must actually read as STEPPED CROSS-SLOPE BANDS: enough terrace
# retaining bunds, each running roughly PERPENDICULAR to the fall (a terrace lip follows the contour, across
# the slope - a bund that ran downhill would be a channel, not a terrace step). This is the archetype's teeth.


# A POLDER-grid field (feature 005 US4) is a solid rectilinear BLOCK - it FILLS its bounding box (unlike the
# comb fan or the contour terraces, whose outline covers a small fraction of its bbox). That fill ratio is
# the archetype's teeth: a polder reads as a surveyed rectangle, not an organic field.


def _seg_0579__polder_fills_its_bbox(
    *, b: Any = _UNBOUND, bbox_area: Any = _UNBOUND, check: Any = _UNBOUND, fields: Any = _UNBOUND, fill_ratio: Any = _UNBOUND, meta: Any = _UNBOUND, pf: Any = _UNBOUND
) -> dict[str, Any]:
    """Gate segment 579 (polder_fills_its_bbox) - body verbatim from the legacy gate() (feature 022)."""
    if meta.get("field_archetype") == "polder_grid" and fields:
        pf = fields[0]
        b = pf.get("bbox") or [0, 0, 1, 1]
        bbox_area = max(1.0, (b[2] - b[0]) * (b[3] - b[1]))
        fill_ratio = poly_area(pf["outline"]) / bbox_area
        check(
            "polder_fills_its_bbox",
            fill_ratio >= 0.82,
            f"a polder_grid field must FILL its bounding box (a surveyed rectangular block), but its outline covers only {fill_ratio:.0%} of its bbox - that reads as a fan/terraced field, not a polder",
        )
    return _kept(locals(), ('b', 'bbox_area', 'fill_ratio', 'pf'))


# A MULBERRY-DIKE FISH-POND field (feature 005 US4, 桑基魚塘) is a filled block whose cells are FISH PONDS
# rimmed by mulberry dikes - so it must both fill its bbox (a reclaimed block) AND carry a mulberry_fishpond
# land-use over most of it. China-first: the Pearl-delta closed sericulture-aquaculture system.
