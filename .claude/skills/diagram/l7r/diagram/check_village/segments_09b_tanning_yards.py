"""Gate segments (tanning yards; keys 0562_000-0562_042) - bodies verbatim, registry order preserved."""

import math
from typing import Any

from .common_01_geometry import seg_dist
from .common_03_capacity import _UNBOUND, _kept

# TANNING YARDS (GM 2026-07-24; the "why" lives in settlements.md "TANNING YARDS"). Unlike the
# other trade works these are NOT a city-only feature: a county town's burakumin hold the whole
# county's carcass rights (danna-ba), so the town tans too - just at ~4 pits rather than ~12.
# WATER, not settlement size, is the gate: tanning is a water process (shironameshi stakes hides
# in the river for 1-2 weeks before de-hairing) and every attested tannery sits on a watercourse
# at the settlement's edge - the caste's own name for itself was kawaramono, "riverbed people".


def _seg_0562_005___ty_yards(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0562.005 (_ty_yards) - body verbatim from _seg_0562__settlement_has_tanning_yard (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city'):
        _ty_yards = M.get("tanning_yards") or []
    return _kept(locals(), ('_ty_yards',))


# A settlement with BOTH a burakumin quarter and running water tans its own hides; one with
# no watercourse at all keeps no tannery, whatever its size, and is exempt.
# meta(tannery=False) is the documented opt-out for a settlement that HAS water but no
# legitimate site on it - the same "declare the deliberate exception" pattern as
# monastery_fortunes. Tango is the case: its only downstream watercourse is tapped for
# irrigation ~100 px below the moat, and the sole ground below that tap drags the frame
# far enough south to strand other off-map features. A dry inland seat sends its hides
# away, exactly as it buys its timber elsewhere for want of navigable water.


# DOWNSTREAM OF EVERY DRAW (GM 2026-07-25). The rule tanneries actually turn on: the
# foul water must not reach anything anyone draws from. This is NOT testable by
# projecting onto the map's drainage bearing - Hoshizora's yard sits on a watercourse
# hydrologically separate from the town's, so a single-bearing projection calls it
# "upstream" of a town it cannot reach. It IS testable now that flow direction is
# recorded, in two clauses against the yard's OWN course:
#   (a) that course must not DISCHARGE into anything drawn from - a pond, a field, the
#       moat, an irrigation ditch. Emptying to off-map (or into a field drain that
#       does) is the only honest ending for a tannery's water.
#   (b) no intake may sit DOWNSTREAM of the yard along that same course. Graph
#       topology alone cannot see this - a channel tapping the river 200 ft below the
#       yard and one tapping it 200 ft above are the same edge - so this clause
#       compares ARC POSITION along the course, oriented by the recorded flow.


def _seg_0562_010___ty_arc(
    *,
    _ty_yards: Any = _UNBOUND,
    at: Any = _UNBOUND,
    ax: Any = _UNBOUND,
    ay: Any = _UNBOUND,
    best: Any = _UNBOUND,
    bx: Any = _UNBOUND,
    by: Any = _UNBOUND,
    d: Any = _UNBOUND,
    i: Any = _UNBOUND,
    poly: Any = _UNBOUND,
    run: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    x: Any = _UNBOUND,
    y: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0562.010 (_ty_arc, run) - body verbatim from _seg_0562__settlement_has_tanning_yard (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city') and _ty_yards:

        def _ty_arc(poly: Any, x: float, y: float) -> tuple[float, float]:
            """(arc length to the closest point on `poly`, total length)."""
            best, run, at = None, 0.0, 0.0
            for i in range(len(poly) - 1):
                ax, ay, bx, by = poly[i][0], poly[i][1], poly[i + 1][0], poly[i + 1][1]
                seg = math.hypot(bx - ax, by - ay)
                d = seg_dist(x, y, poly[i], poly[i + 1])
                if best is None or d < best:
                    t_par = 0.0 if seg == 0 else max(0.0, min(1.0, ((x - ax) * (bx - ax) + (y - ay) * (by - ay)) / (seg * seg)))
                    best, at = d, run + t_par * seg
                run += seg
            return at, run

    return _kept(locals(), ('_ty_arc', 'run'))


# Stench separation from ordinary dwellings. The burakumin's OWN houses are exempt by
# design, not by oversight: kawaramono lived on the ground they worked, and that
# adjacency is what the segregated quarter IS. The floor is the crematory's existing
# 120 ft (town_has_cremation_ground) - the established project figure for "a nuisance
# kept off the houses" - rather than a fresh invented number.


# ---- THE YARD SHARES THE QUARTER'S SIDE OF THE SETTLEMENT (GM 2026-07-27) --------------
# The rule kegare actually follows is DIRECTIONAL, not metric: pollution leaves a
# settlement ONE way, and the outcast quarter is the marker of which way that is. Edo
# stacked the Asakusa outcast community, the Kozukappara execution ground and the
# Yoshiwara at the northeast kimon; Kyoto put its communities on the riverbeds and the
# southern roads out. So this is deliberately NOT a distance rule, and an earlier draft
# that measured feet was WRONG: a walled city legitimately keeps its quarter inside at
# the margin (siege labor, night soil, corpse and execution duty, and the leather CRAFT -
# sandals, drum heads, armor lacing - which is clean, quiet work done at home) while the
# wet, stinking phase of the trade (soak, unhair, dry) goes out to the water. Nagahara's
# yard stands ~1,390 ft from its quarter and is correct. What is NOT correct is the yard
# facing the opposite way out of town from the quarter, which puts the tanners' daily
# carcass haul straight through the rest of the settlement - the traffic real castle
# towns routed around with designated carcass ways.
# Same form and same threshold as execution_ground_on_the_outcast_side, whose rule this
# simply extends to the other burakumin-run works: a dot product against the quarter's
# bearing from the core, i.e. "within the same half of the compass". The CREMATION ground
# is deliberately NOT covered - it is monk-run and follows the temple/funerary complex,
# which need not be the outcast side at all (Hoshizora's stands 130 ft from its monastery
# and almost exactly opposite the quarter, and that is a correct map).


# The core counts EVERY dwelling including the quarter's own (the same population
# execution_ground_on_the_outcast_side measures from - the quarter is part of the
# settlement). That makes the test meaningless when the quarter is ALL there is: the
# core lands on the quarter and no bearing exists. A settlement with nothing but
# burakumin dwellings has no "rest of town" for the works to be on the far side of, so
# the rule abstains rather than firing on a degenerate vector.


# ... AND THE YARD'S GROUND NEVER OVERLAPS THE WATER (GM 2026-07-25, after the real
# Tango yard drifted ~10 ft into its stream and the Hoshizora yard landed on a drain
# ditch; both frozen in pool/regressions/). Same doctrine as lumber_yard_clear_of_water:
# tanning_yard_on_water demands the bank within ~20 ft, but the tamped ground itself
# stays DRY - the soaking pits are dug earth (a pit dug below the waterline is just
# more stream) and the racks cure hides for 2-4 months, which standing water would rot.
# The staking frames are the ONE sanctioned in-water element: s.tanning_yard draws them
# BEYOND the ground rect, out in the shallows, so this check never sees them - a yard
# that reads as "a platform over the water" is this defect, not a design. Tested with
# the rect's true rotation against every watercourse's REAL half-width (the lumber-yard
# lesson: the generic ~6px check misses a wide river), via seg_to_rect_dist so a thin
# field ditch THREADING UNDER the rect between its corners is caught too (the Hoshizora
# capture; corner-sampling cannot see it). Exact abutment of the bank line is legal.


# ... NOR CROPLAND. The trade's whole siting logic is MARGINAL riverbank ground - the
# caste's own name, kawaramono ("riverbed people"), records that they worked the
# unplowable floodway edges precisely because taxed, producing land was never theirs
# to take. A paddy is a flooded basin (no tamped work floor stands in one), and the
# pits' lime and bate liquor poison the soil for cropping - so a yard drawn on a field
# asserts ground that is simultaneously worked by a farmer and ruined for farming.


# ... AND IT LIES ALONG THE BANK IT WORKS (GM 2026-07-26). A tanning yard is a working
# FRONTAGE, not a building: the soaking pits and the intake sit on the water side
# (local -y), the drying racks stand behind them, and every hide crosses from one to
# the other. So the yard's long axis runs WITH the watercourse - a stream at 30 deg
# takes a yard at 30 deg. Set the yard square to the map instead and the near corner
# goes in the water while the far corner strands a yard-length inland: the pits at one
# end sit on the bank and the pits at the other end do not, which is the one thing this
# layout cannot absorb, since the whole point of the ground is that the pit rank and
# the staking frames share a single edge of water. Riverside works follow their bank
# for the same reason a wharf does. Shape is city_wall_towers_aligned's: compare the
# RECORDED rot against the bearing of the water it fronts, mod 180 (a 180 deg flip is
# the same yard; a 90 deg turn stands it ACROSS the bank instead of along it).
#
# WHICH course is "its water" is decided by REACH, not by nearest. A yard at a
# confluence legitimately fronts either course that meets there, and the
# nearest-by-centerline answer is not even stable: Hoshizora's yard sits 3 px from a
# drain ditch bearing 43 deg and 5 px from the channel its intake cut actually taps at
# 83 deg, so by centerline the ditch wins and by intent the channel does. The reference
# set is therefore every course whose BANK - centerline distance minus that course's
# REAL half-width, the same measure tanning_yard_clear_of_water uses, since a 40px
# river's centerline is 20px from a yard that abuts it - falls inside the same ~20 ft
# reach tanning_yard_on_water calls "on the water", and the yard need only be square to
# ONE of them. A yard with NO bank in that reach is already failing
# tanning_yard_on_water, so this check abstains rather than reporting one defect twice.
#
# TOLERANCE is 15 deg - the wall-towers figure, not the gate furniture's 6 - because
# rot is set by hand against a hand-drawn meandering polyline, so a correct yard sits a
# few degrees off whichever segment it happens to be measured against (Hoshizora's own
# fronting channel bends from 83 to 56 deg within 50 px). It still separates cleanly,
# because the failure mode is not a small wobble but an AXIS-ALIGNED yard on a diagonal
# bank, which is 20-45 deg off: the pool's three good yards sit at 2.1, 3.8 and 7.2 deg
# while the pre-fix Tango yard sat at 22.9 (frozen in pool/regressions/).
