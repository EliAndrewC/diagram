"""Part of the Shiro Daika map, split from shiro-daika.gen.py by feature 173.

Importing this module EXECUTES this part of the drawing. See CLAUDE.md in this directory.
"""

import math

from l7r.diagram.citybudget import CapitalProgram, budget_to_manifest, plan_capital
from l7r.diagram.settlement import Settlement
from l7r.diagram.waterfields import paddy_grain

PLOT_ACROSS, ROW_STEP = paddy_grain(3)  # the capital's 3 ft/px paddy grain


s = Settlement(3200, 3050, seed=61)
s.meta(
    water_flow=135,  # DRAINAGE BEARING: the land falls NE -> SW, the way the river runs (0=E, 90=S)
    name="Shiro Daika",
    scale="capital",
    walled=True,
    population=12_360,
    ftpx=3,
    wall_defense="siege",  # the Crab border lies south: built to survive a siege even after a long peace
    imperial_road=True,
    clan="Scorpion",
    capital_dir="northeast",  # the Imperial capital lies NORTHEAST of Shiro Daika (GM 2026-08-11). NOTE: the Imperial road as drawn leaves this map to the NORTHWEST, so one of the two needs to move - flagged for the GM rather than silently re-routed
    # THE LINEAGE DECLARATION (feature 020). Bands track HOUSEHOLDS HOUSED, never the rank of the
    # head: the chargen weights ([house][[daika]]) give six chancellors (daika 19, hazama 16,
    # utsuro 15, tokiwa 14, anzu 12, kurogi 11) and three below the threshold (yodo 5, nio 4,
    # seki 4). kurogi is PROVINCIAL (seated in Moriguchi), so its chancellor keeps a capital
    # estate that is visibly smaller - most of the kurogi live around their own provincial city.
    # The ruling daika lineage has NO compound: its seat IS the castle.
    lineages={"hazama": "grand", "utsuro": "grand", "tokiwa": "grand", "anzu": "grand", "kurogi": "estate", "yodo": "house", "nio": "house", "seki": "house"},
    ruling_lineage="daika",
    # The gates' furniture, the wharf works, the towpath and the aqueduct are the only features
    # outside the rampart until feature 021 fills the interior - the frame reads sparse, not wrong.
    # temple doctrine (020): the rim BELTS the rampart as part of the defenses; the two
    # sovereign precincts are the "two great complexes" and the five modest rim temples are
    # lineage bodaiji (Hotei is Tokiwa's). "large" is the recognized exception slug.
    temple_exception="large",
    temple_fortunes=["Benten", "Bishamon", "Daikoku", "Ebisu", "Hotei", "Inari", "Jurojin"],
    # THE WIND (T021, research item 10): continental east-coast monsoon - winter NW is the
    # design wind (fire season, steadiest flow); nuisance trades sit in the lee-and-
    # downstream arc (S-SW riverward, below the wharf).
    wind_from="northwest",
    # INTERIOR WARD GATES: OFF for Shiro Daika (GM 2026-08-10). The doctrine (capitals.md:
    # kido at the block and lane mouths, no continuous ward fence) stands and the knob stays
    # for other cities - but the mesh this map derived wandered mid-street and read as neither
    # a wall nor a gate, so the capital ships without interior gates until the placement rule
    # is reworked. The rampart gates, the samurai ward's own seal and the castle stand as they were.
    ward_gates=False,
    waivers={
        "population_consistent_with_housing": "First-pass fabric at the settled wall: every band drew, but realized machi density leaves the census ~130 households short of 12,360/5; the GM (2026-08-10) deferred interior fullness to the fabric-first regeneration (future-work/ #2/#5) rather than grind the packs further this pass.",
        "city_no_large_empty_space": "The ~1.5-acre pockets that remain rotate to a new spot on every reflow because the first-pass packs under-fill the settled wall by ~8%; the stable cores are all claimed (the drill grounds, the moat firebreak, the rampart approach, the S-gate column ground) and the rotating residue is the same deferred-fullness gap (GM 2026-08-10, future-work/ #5).",
    },
    crop_outlier_ok="Outside the rampart the map carries only the gate furniture, the wharf works, the towpath and the aqueduct until feature 021 fills the interior; sparse outliers at this stage are the build order showing through, not a siting error.",
)

# ---- BUDGET-FIRST (feature 018): the wall is an OUTPUT of the declared program, never a guess.
# A capital cannot be sized from population the way a provincial city nearly can - a median castle
# alone is ~85% of an entire provincial city's interior.
BUDGET = plan_capital(CapitalProgram(population=12_360, river=True, castle_seat="ring", imperial_granary_seat="wharf"), canvas=(3200, 3050))
s.meta(budget=budget_to_manifest(BUDGET))

CX, CY = 1400, 1313
# the SETTLED rampart (021, GM 2026-08-10, third and final derivation - the wall-settles-first
# pass): packed-tight C_PACKED_CAPITAL 950 + CIRC 0.15 + the wharf-hamlet extramural ruling
# give required ~3.92M px^2; this 1110x1150 ellipse encloses it at ~+0.9%, recentered on the
# CASTLE AXIS (x=1400) so the Imperial road runs straight through both its gates again.
# History of the first wall: sized with Tango's C_PACKED
# (690 px2/family) and the capital's as-built machi delivers ~1,367 - so 57% of the packed
# cohort ended up outside the walls against the researched 30% suburb share. The budget now
# prices the in-wall packed line with C_PACKED_CAPITAL (1350, measured on this map's own
# fabric), required interior 4.23M px2, and this ellipse encloses it at ~+2%. The center
# moved SW (the castle now sits NE-of-center, the honmaru-at-the-back pattern) because the
# east is pinned by the river and the west by the canvas; the river's mid-course shifts
# ~140px east to keep the ~200px wall-to-river band the wharf chain needs.
RX, RY = 1110, 1150
NRING = 20
WALL = [(round(CX + RX * math.cos(-math.pi / 2 + 2 * math.pi * i / NRING)), round(CY + RY * math.sin(-math.pi / 2 + 2 * math.pi * i / NRING))) for i in range(NRING)]
NGATE, EGATE, SGATE, SWGATE = WALL[0], WALL[5], WALL[10], WALL[13]

# ---- the river: NE -> SW past the southeast flank, off both edges. Upstream (NE) first, which is
# the convention every junction-angle rule keys on.
# Held ~200px off the moat at its closest approach: the ring is 1,055x983 px of pushed-out wall,
# and the first cut ran the river straight through the southeast arc.
RIVER = [(3200, 640), (2960, 1100), (2640, 1720), (2260, 2380), (1900, 3120)]
s.river(RIVER)

# ---- the rampart and its four gates, then the moat and the patrol road inside it
s.city_wall(WALL, gates=[NGATE, EGATE, SGATE, SWGATE])
MOAT = s.moat(WALL, gap=26)
RING = s.ring_road(WALL, inset=30)
s.bound = [list(p) for p in RING]

# ---- THE WAYS. The Imperial road runs south gate -> north gate and bends NORTHWEST beyond it
# toward Shiro Kyo; its label sits OUTSIDE the wall, because inside the rampart the same roadway
# is a city street the city maintains, not an Imperial responsibility.
# THE KAGI-NO-TE. The first cut ran this road dead straight from gate to gate at x=1400 - and the
# castle stands on x=1400, so the roadbed crossed its moat, entered the ote-mon, ran 2,100 ft
# through the blank court and pierced the north rampart where there IS no gate. Invisible on the
# render only because the court fill is drawn over it (settlement-review, 2026-08-09).
#
# The fix is the historically right one rather than a nudge: the jokamachi rule is that the main
# road passes the castle's FRONT, not through it, and a castle town deliberately bends its highway
# rather than offering a mile-long straight run at the daimyo's gate - that bend is the kagi-no-te.
# So the road comes north to the castle's south front, turns west past it, and comes back to the
# north gate. The bend sits at y=1560 (feature 020 moved it south from 1420) so the ote-suji stub
# is long enough to carry three ministry compounds a side with the 14px office standoffs.
KAGI_Y = 1560
# ...with straight STUBS through the north gate (GM 2026-08-09: the old geometry bent AT the
# gate point, so the roadbed rode along the rampart stroke): the diagonal legs meet a short
# perpendicular run on each side of the gate, and the bed passes clean through the gap.
s.road(
    [
        (SGATE[0], 3095),
        (SGATE[0], SGATE[1]),
        (1400, KAGI_Y),
        (800, KAGI_Y),
        (800, 470),
        (1400, 300),
        (NGATE[0], NGATE[1]),
        (1400, 110),
        (1200, 92),
        (1040, 108),
        (860, 150),
        (660, 110),
        (500, 20),
        (460, -60),
    ],
    label="Imperial Road",
    label_xy=(SGATE[0] + 145, 2620),  # up the road, beside the built ground: a caption left out in the open holds the crop open with it (GM 2026-08-11)
)
# the same road is Imperial on BOTH sides of the city (GM 2026-08-09) - the run toward Shiro
# Kyo carries its own caption, tilted along the branch per the linear rule
s.label(1170, 66, "Imperial Road", 11, italic=True, color="#6E5B38", rot=195, linear=True)
s.road([(2387, 1390), (2385, 1313), (EGATE[0], EGATE[1]), (2820, 1240), (3200, 1150)])  # east, to the Fox lands - the first leg runs INSIDE the gate to join the ring road (gate_roads_join_the_ring)
# the karamete approach is the STRAIGHT CONTINUATION of the north gate's street (GM 2026-08-09:
# the first cut hung it off the diagonal mid-slope and the two beds read as overlapping roads):
# city gate -> due south -> the castle's rear gate, dead-ending at its moat and tower exactly as
# a castle-town street aimed at the works should, while the Imperial through-road leaves the
# street at the (1400, 300) junction and bends west around the castle front (the kagi-no-te).
s.road([(1400, 300), (1400, 520)])  # stops at the karamete tower's foot, as the ote-suji stops at the ote-mon's
s.road([(636, 1772), (664, 1844), (SWGATE[0], SWGATE[1]), (300, 2120), (0, 2200)])  # southwest, into the domain - the first leg runs INSIDE the gate to join the ring road (gate_roads_join_the_ring)

# ---- THE OTE-SUJI (feature 020): the ceremonial avenue from the castle's front gate south to the
# Imperial road at the kagi-no-te bend. Drawn as a road (M["roads"]) so the shared crossing source
# carries it over the castle moat, and UNLABELED - only the Imperial road is named.
# 45 REAL FEET (GM 2026-08-09, "it looks huge"): the first draft passed width=32 raw PIXELS -
# 96 ft at this scale, nearly 4x the Imperial highway - where the engine's convention is real
# feet through lw() (the road default is lw(26), the Tokaido's width). The honest ceremonial
# band is Edo's own grand avenues: Honcho-dori 13.8 m (~45 ft), Nihonbashi-dori 18.2 m (~60 ft)
# - and that is the SHOGUN'S capital, so a domain capital's ote-suji takes the Honcho class:
# 45 ft, exactly half again the 30 ft highway it meets (26 ft until feature 144). research/cities/capitals.md, "Street widths".
OTE_X = 1400
s.road([(OTE_X, 1240), (OTE_X, KAGI_Y)], width=s.lw(45))  # starts just south of the ote-mon's gate tower
