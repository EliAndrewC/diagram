"""Gate segments (field cover and cremation; keys 0285_092-0286_024) - bodies verbatim, registry order preserved."""

from typing import Any

from .common_01_geometry import point_in_poly
from .common_03_capacity import _UNBOUND, _kept


def _seg_0285_092__barren(*, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0285.092 (barren) - body verbatim from _seg_0285__wells_clear_of_shrine_and_torii (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'village', 'hamlet') and scale in ('town', 'village', 'hamlet', 'city'):
        barren = []  # type: ignore[var-annotated]
    return _kept(locals(), ('barren',))


def _seg_0285_093__barren_1(
    *,
    barren: Any = _UNBOUND,
    c: Any = _UNBOUND,
    commons: Any = _UNBOUND,
    fields_ol: Any = _UNBOUND,
    gx: Any = _UNBOUND,
    gy: Any = _UNBOUND,
    n_inside: Any = _UNBOUND,
    n_open: Any = _UNBOUND,
    ol: Any = _UNBOUND,
    p: Any = _UNBOUND,
    poly: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    step: Any = _UNBOUND,
    xs: Any = _UNBOUND,
    ys: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0285.093 (barren, c, gx, gy) - body verbatim from _seg_0285__wells_clear_of_shrine_and_torii (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'village', 'hamlet') and scale in ('town', 'village', 'hamlet', 'city'):
        for c in commons:
            poly = c.get("poly")
            if not poly:
                continue
            xs = [p[0] for p in poly]
            ys = [p[1] for p in poly]
            n_inside: int = 0  # type: ignore[no-redef]
            n_open: int = 0  # type: ignore[no-redef]
            step = max(6.0, min(max(xs) - min(xs), max(ys) - min(ys)) / 12.0)
            gy = min(ys)
            while gy <= max(ys):
                gx = min(xs)
                while gx <= max(xs):
                    if point_in_poly(gx, gy, poly):
                        n_inside += 1
                        if not any(point_in_poly(gx, gy, ol) for ol in fields_ol):
                            n_open += 1
                    gx += step
                gy += step
            if n_inside and not n_open:
                barren.append((round(c["x"]), round(c["y"])))
    return _kept(locals(), ('barren', 'c', 'gx', 'gy', 'n_inside', 'n_open', 'ol', 'p', 'poly', 'step', 'xs', 'ys'))


def _seg_0285_094__commons_clear_of_paddies(*, barren: Any = _UNBOUND, check: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0285.094 (commons_clear_of_paddies) - body verbatim from _seg_0285__wells_clear_of_shrine_and_torii (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'village', 'hamlet'):  # noqa: SIM102 - comment bank under the guard; combining would orphan it (023 convention)
        if scale in ('town', 'village', 'hamlet', 'city'):
            check(
                "commons_clear_of_paddies",
                not barren,
                f"fuel/fodder commons patch(es) lie ENTIRELY over flooded paddy, so they clothe nothing and draw nothing: {barren[:3]} - the commons is NON-arable degraded grazing, never the productive wet paddy; put the patch where there is open ground",
            )
    return _kept(locals(), ())


# MANAGED-WOODLAND patches must not OVERLAP the crops nor BLOCK THEIR LIGHT (GM). Both the placement and
# this check enforce it. A tree canopy over a crop competes for root/light; and the sun is to the SOUTH
# (maps are north-up), so a tree casts its shadow toward the NORTH - a patch may sit just north/beside a
# crop, but on the crop's SOUTH (sunny) side it must stand well back (a canopy's shadow reach) or it
# shades the field. Covers BOTH the paddy and the dry hatake plots. Distances: a fixed crown-radius
# no-overhang CLEAR, plus a real-world shadow reach on the south side (feet -> px at the map's ftpx).


# WEALTH VARIATION: farmhouses are not one uniform size - a modest wealth tier (recorded as `wealth`)
# scales the rendered house and, with it, the grove, so holdings read as ranging from the landless
# mizunomi to a honbyakushO landholder. Verify the tiers are ACTIVE so a regression that flattens
# them to one size is caught. (Only the house + grove carry the signal; the yard/garden/shed stay
# uniform - scaling them coupled into farmstead placement and dropped houses.) WHY: settlements.md.


def _seg_0285_098__h_3(*, h: Any = _UNBOUND, houses: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0285.098 (h, plain) - body verbatim from _seg_0285__wells_clear_of_shrine_and_torii (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'village', 'hamlet') and scale in ('town', 'village', 'hamlet', 'city'):
        plain = [h for h in houses if h.get("role") != "headman"]
    return _kept(locals(), ('h', 'plain'))


def _seg_0285_099__farmhouse_sizes_vary(
    *,
    _eff: Any = _UNBOUND,
    areas: Any = _UNBOUND,
    check: Any = _UNBOUND,
    h: Any = _UNBOUND,
    houses: Any = _UNBOUND,
    lop: Any = _UNBOUND,
    med: Any = _UNBOUND,
    plain: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    varied: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0285.099 (farmhouse_aspect_in_range, farmhouse_sizes_vary) - body verbatim from _seg_0285__wells_clear_of_shrine_and_torii (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'village', 'hamlet') and scale in ('town', 'village', 'hamlet', 'city') and len(plain) >= 10:
        # measure the ACTUAL rendered-footprint spread, which is carried TWO ways: the DISPERSED path
        # keeps a uniform base w x h and scales the drawn house by a `wealth` tier (0.9/1.0/1.12), while
        # the NUCLEATED path jitters the base w x h (length/depth) directly at wealth 1.0. Fold both in
        # via effective area = w * h * wealth^2 (the wealth factor scales each dimension), so a regression
        # that flattens houses to one size is caught under EITHER encoding.
        def _eff(h: dict[str, Any]) -> float:
            return float(h["w"] * h["h"] * (h.get("wealth", 1.0) ** 2))

        areas = sorted(_eff(h) for h in plain)
        med = areas[len(areas) // 2] or 1
        varied = sum(1 for h in plain if abs(_eff(h) - med) > 0.05 * med)
        check(
            "farmhouse_sizes_vary",
            varied >= 0.2 * len(plain),
            f"farmhouses show no size variation ({varied}/{len(plain)} off the median footprint) - a modest spread of homestead sizes is expected (they look flattened to one size)",
        )
        # a minka is rectangular but within the ~1.3-2.5:1 norm - a house grew by adding bays
        # (longer), never into a 4:1 shed. Guard the aspect so the length jitter stays plausible.
        lop = [[round(h["x"]), round(h["y"])] for h in houses if min(h["w"], h["h"]) > 0 and max(h["w"], h["h"]) / min(h["w"], h["h"]) > 2.7]
        check("farmhouse_aspect_in_range", not lop, f"farmhouse(s) {lop[:3]} are more than 2.7:1 long-to-wide - a minka stays roughly 1.3-2.5:1 (it lengthened by bays, it did not become a shed)")
    return _kept(locals(), ('_eff', 'areas', 'h', 'lop', 'med', 'varied'))


# THE DEAD - a full funerary geography. Every settlement above a hamlet buries its cremated dead
# (a hamlet's go to the village district's ground, just as it has no shrine or headman). GRAVEYARDS
# are temple parish grounds: the state merged Shinsei and Fortune worship, so ANY temple may host
# one (a temple opts out with graveyard=False - a new or special-purpose hall). A Shinto SHRINE
# keeps death-pollution (kegare) at arm's length, so no grave site sits hard against a shrine. A
# CITY additionally shows 2-4 graveyards split inside/outside the walls, the ruling clan's walled
# MAUSOLEUM by the samurai quarter, an extramural CREMATION GROUND, and a pauper OSSUARY beside it.


# PRESENCE: a village/town has >=1 graveyard; a city shows 2-4 (a few parish grounds,
# consolidated over the centuries - not one, not a dozen)


# CHURCHYARD (L7R): a village SHRINE is officially Shinseist and its monk performs the funerary rites, so
# the graveyard sits IN the shrine's precinct - like a Buddhist-temple parish ground - NOT held away from
# it (real-Japan Shinto kegare does NOT apply: the shrine IS the death-handling institution). Only the
# sacred HALL + its TORII gateway stay clear: graves fill the yard AROUND them, never ON them. WHY:
# settlements.md "Historical grounding" (Brotherhood of Shinsei monks tend the country shrines and the dead).


# MARSH is unbuildable wet ground: no SACRED hall and no BURIAL ground sits on a reed marsh - you would
# never raise a shrine or dig graves in a bog (they belong on DRY ground, the spur / high ground). The
# `toe` marsh is the wet valley floor; a `pond_fringe` (a thin decorative shore ring) is exempt. GM 2026-07.


# PRECINCT (village): the village graveyard sits BY the shrine (the Shinsei monk's funerary ground),
# mirroring the town/city temple-precinct rule. A HILLTOP shrine is exempt (graves do not climb the
# sacred hill, and a prominent hill-shrine is not the humble earth-god monk's funerary base - as with
# remote_shrine_has_own_well); if every shrine is hilltop, the ground is placed by eye. A hamlet has no
# shrine at all (its dead go to the village district's ground).


# WATER SET-BACK: burial grounds keep a clear margin from OPEN WATER (the moat, a stream, or a
# pond), and that margin SCALES WITH THE WATERWAY'S SIZE (water_setback() - a creek needs little,
# a moat/river much more) because a burial ground by big water floods out. The CREMATION ground
# may sit NEARER the water (fire/ritual), so the graveyard naturally lands beyond it. Non-overlap
# is not enough. (Thin irrigation channels are NOT open water and don't trigger this.)
# the moat is OUTSIDE the wall, so an INSIDE-wall ground is shielded from it by the rampart and is
# exempt from the moat term (streams/ponds apply regardless of which side they sit on).


#                      trickle - so a burial ground keeps a clear margin from its edge (more than a creek)


# THE CREMATORY ADJOINS AN EXTERNAL BURIAL GROUND: the body is burned and its cremated bones
# interred next door, so a cremation ground sits ADJACENT to an EXTERNAL (outside-the-walls)
# cemetery - together they form the extramural funerary complex beyond a gate. (An unwalled
# settlement has no walls, so any of its cemeteries counts as external.)
