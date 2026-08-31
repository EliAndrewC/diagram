"""Part of the Shiro Daika map, split from shiro-daika.gen.py by feature 173.

Importing this module EXECUTES this part of the drawing. See CLAUDE.md in this directory.
"""

import math

from .frame import s

# ---- private dojos (count rolled from the samurai cohort - the 1-per-200 formula holds
# at this tier; the hanko is the capital's gain, not more private halls) and the walled
# MERCHANT ESTATES of the counts table, both seated before the packs
s.dojos([(1230, 1650), (760, 1680), (2250, 1175), (1610, 1480), (1000, 1480), (2200, 1520), (700, 1600), (1750, 1950)])
for _dj in s.M.get("dojos", []):
    _djx, _djy = _dj["x"], _dj["y"]
    s.block_polys.append([(_djx - 40, _djy - 40), (_djx + 40, _djy - 40), (_djx + 40, _djy + 40), (_djx - 40, _djy + 40)])
    s.placed.append((_djx, _djy, 64, 64))  # a dojo compound reserves its ground before the packs (the engine glyph alone did not)
s.theater_stage(2062, 1712, w=66, h=48, label="theater", kind="machi", rot=127)  # the entertainment quarter beside the wharf gate (the brokers' money builds the theaters)
s.theater_stage(1740, 1695, w=64, h=46, rot=-120, label=None)  # opens toward the Benten hall (its temple)
s.district("entertainment quarter", "entertainment", [(2000, 1620), (2115, 1620), (2115, 1800), (2000, 1800)], rank_band=None)
# market-day flophouses at the working gates, seated BEFORE the packs (the first seats
# landed on the moat band and the Shiro Kyo roadbed once the suburbs grew around them)
_fh_s = s.open_seat((1425, 2515, 1500, 2615), s.px(104), s.px(46)) or (1450, 2560)
s.flophouse(_fh_s[0], _fh_s[1])  # beside the south gate road, not 278 ft off it (GM 2026-08-11)
s.flophouse(2700, 1310)  # on the E gate road's south verge, inside the market's own strip
s.flophouse(1325, 80)
s.merchant_estates([(1330, 1830, "east"), (950, 1700, "south"), (1550, 1950, "north"), (1080, 1768, "south"), (1240, 1898, "east"), (1188, 1816, "west"), (1650, 1700, "south"), (1120, 1930, "north")])
# ---- the TRADE WORKS + GATE CARAVAN PROGRAM (the urban battery's full demand; all
# compounds seated BEFORE the packs). Nuisance trades take the lee-and-downstream arc
# (wind_from="northwest"): the dyer and both tanneries stand on the moat DRAIN south of
# the wharf, the kiln smokes outside the southwest wall.
# monk housing beside each rim temple + the teramachi cluster's wayside shrines
s.rowpack((2028, 462, 2080, 508), (["monk_house"] * 2)[:2], court_every=3)  # Bishamon's adepts NE of the hall, against the ring verge's adepts NE of the hall, against the ring verge
s.rowpack((2174, 1939, 2216, 1995), (["monk_house"] * 2)[:2], court_every=3)  # tucked between Ebisu and the connector's kido crossing
s.rowpack((990, 2166, 1042, 2226), (["monk_house"] * 3)[:3], court_every=3)
s.rowpack((464, 1268, 505, 1313), (["monk_house"] * 2)[:2], court_every=3)
s.rowpack((641, 545, 685, 587), (["monk_house"] * 2)[:2], court_every=3)  # west of the Hotei hall, under the ring curve
s.small_shrine(547, 1395)
s.small_shrine(681, 1565)
s.small_shrine(866, 2032)
s.small_shrine(619, 1635)
s.small_shrine(479, 1095)
s.brewery(1130, 1700)
s.brewery(1690, 1935)
s.oil_press(1000, 1690)
s.pawnshop(1245, 1690)
s.pawnshop(1874, 1786)  # the second commercial quarter's pawnshop (Edo ran one per ~400 residents; two drawn, the rest implied in the rows)
s.bathhouses([(900, 1750), (1278, 1980), (1668, 1740), (2060, 1640), (1080, 1860), (1550, 1830), (2250, 1050)])
s.dye_yard(2114.8, 2493.8, rot=29.4)
s.dye_yard(2049.9, 2403.7, rot=108.9)  # ...the dyers' row (Konya-machi): contiguous lots up the drain's west bank
s.dye_yard(2051.4, 2458.0, rot=29.4)
s.tanning_yard(2000.3, 2491.2, rot=29.4, water="stream")  # ON the moat drain's west bank (its wash water; the towpath owns the river bank here) - GM 2026-08-10
s.tanning_yard(2060.1, 2524.9, rot=29.4, water="stream")  # the pair shares the drain's downstream bank
s.kiln(268, 2166)
s.kiln(
    176, 2196
)  # the second works of the kiln quarter - beside the first, sharing the pit and the fuel road  # ON the SW approach road's outer leg (a kiln hauls fuel and clay by cart, so it stands on its haul road, not adrift in the fields - GM 2026-08-10)
# the in-wall doss-house needs a HUMBLE quarter around it (>=115px merchant/temple-free,
# research: the doya-gai sat among day-laborer rows) - the 4-mix machi has a merchant
# everywhere, so carve a laborer-only pocket and seat the doss at its heart
s.placed.append((1153, 2284, 46, 334))  # hold the doss seat before the rows fill in
s.placed.append((1837, 1352, 34, 24))  # keep the SE pasture verge clear (a lone well-less seat kept landing here)
s.rowpack((1045, 1920, 1330, 2060), ["laborer_large"] * 4 + ["laborer"] * 34, fill=True)
# DERIVED from the southwest approach road itself: a point 40% out along it, stepped off its
# own normal by a verge. A doss-house outside a gate exists to catch travelers coming UP that road.
_SWR = [(636, 1772), (0, 2200)]
_swdx, _swdy = _SWR[1][0] - _SWR[0][0], _SWR[1][1] - _SWR[0][1]
_swl = math.hypot(_swdx, _swdy)
_swp = (_SWR[0][0] + _swdx * 0.4, _SWR[0][1] + _swdy * 0.4)
_fh_sw = s.open_seat((_swp[0] - 10, _swp[1] + 8, _swp[0] + 60, _swp[1] + 68), s.px(104), s.px(46)) or (_swp[0] + 24, _swp[1] + 36)
s.flophouse(_fh_sw[0], _fh_sw[1])  # outside the SW gate, ON its approach road (GM 2026-08-11: it was ~300 ft adrift)
# caravan facilities just inside each gate: inn + big stables (open ground kept by their
# own reserves; the packs flow around)
s.inn(1330, 300)
# the N caravan yard: beside its inn but OFF every estate's gate approach (GM 2026-08-10).
# The band between the ring road and the estate row is corridor-bound, so the engine picks
# the best clear seat in the wider gate quarter and the inn/flophouse keep it company.
# the N caravan yard stands OUTSIDE the gate with the market it feeds (GM 2026-08-10: it was
# on the Nio/Seki estates' gate approach, and the in-wall band between ring road and estate
# row is corridor-bound). Caravans halt outside the gate anyway - that is where the toll,
# the flophouses and the fodder are - so the yard joins the guan-xiang strip.
# the N caravan yard stays INSIDE the gate (city_gate_caravan_facilities: the inn, stables and
# flophouse serve arriving traffic within the walls) but OFF every estate's gate approach - the
# north band's compounds all gate SOUTH onto the y475 lane, so the yard takes the band's west
# end, past Yodo, where no compound faces it (GM 2026-08-10)
_ESTATE_GATES = [(1150, 454), (1250, 453), (1520, 418), (1660, 412), (1760, 453), (1830, 454)]
_yardseat = s.open_seat((1430, 225, 1560, 330), 100, 96, footprint=False, clear_of=_ESTATE_GATES) or (1470, 262)
s.stables(_yardseat[0], _yardseat[1])
s.placed.append((_yardseat[0], _yardseat[1], 100, 96))  # the N caravan yard - beside its inn at (1330,300), off the estate gates (GM 2026-08-10)
s.well(_yardseat[0] + 46, _yardseat[1] - 40)  # the yard's own trough water, pre-seeded (the dig path predates placed-reserves)
s.block_polys.append([(1505, 308), (1615, 308), (1615, 416), (1505, 416)])
s.placed.append((1560, 362, 112, 32))  # N caravan yard (uniform doctrine: every gate stables keeps open ground)
s.inn(2437, 1413)
s.stables(2426, 1241)
s.block_polys.append([(2371, 1188), (2481, 1188), (2481, 1298), (2371, 1298)])
s.placed.append((2426, 1241, 196, 228))  # the caravan yard keeps OPEN ground for the animals
s.inn(1330, 2368)
s.stables(1512, 2392)
s.block_polys.append([(1415, 2314), (1525, 2314), (1525, 2422), (1415, 2422)])
s.placed.append((1470, 2312, 112, 300))  # S caravan yard: open ground for the animals (crowd rule) - the reserve STOPS at the rampart (it used to run 114px past it and hold the gate market's ground)
s.well(1458, 2416)  # the yard's public well - pre-seeded so the stables' own-well dig path (which predates placed-reserves) stays idle
s.flophouse(1455, 300)
s.flophouse(2421, 1343)
s.flophouse(1370, 2341)
s.flophouse(
    1153, 2284, rot=0
)  # the in-wall doss-house, deep in the laborer core. Its angle is STATED rather than derived: the band street it fronts is laid after this point in the draw order, so the derivation would take the bearing of a way that is merely nearest at THIS moment (it took 90 deg from a vertical lane, against the street's 180)
s.flophouse(586, 1856)  # INSIDE the SW gate with its inn and stables (city_gate_caravan_facilities); seat computed clear of wall, ring, road and every solid
s.inn(629, 1938)
s.stables(673, 1915)
# two more public wells where the warren outgrew its water. ASKED, not guessed: a hand-picked
# seat here landed on a lane (this skill's CLAUDE.md, "Ask the ENGINE where a feature fits").
s.well(700, 1940)  # pre-seeded: the yard's own-well dig path was putting one on the SW gate road
s.block_polys.append([(521, 1896), (631, 1896), (631, 2004), (521, 2004)])
s.placed.append((690, 1912, 150, 130))  # the SW yard's animal ground, east of the stables where the crescent rows press  # SW caravan yard (uniform doctrine) - likewise kept inside the wall
s.street([(1850, 1688), (1850, 1852)], width=s.lw(10))  # the Benten sando's monzen lane (the hall faces its own lane - capitals.md)
s.street([(950, 1482), (950, 1560)], width=s.lw(10))  # the Jurojin sando's monzen lane
s.frontage([(950, 1492), (950, 1550)], ["shop"], width=6, spacing=26, setback=3, dense=True)  # the sando's own stalls
s.frontage(
    [(1850, 1700), (1850, 1845)], (["merchant", "shop"] * 2)[:3], width=8, spacing=16, setback=3, jitter=1, dense=True
)  # Benten monzen. ONE-SIDED, and honestly so: a walled manor court stands ~25 px off the sando's east flank, so every east seat is refused and the approach's shops line the WEST side only. The call still asks both sides - the ground decides, and here it decides one
s.rowpack((918, 1462, 946, 1560), (["merchant", "shop"] * 10)[:0], court_every=6)  # Jurojin monzen flanks its north sando
s.rowpack((954, 1462, 982, 1560), (["shop", "merchant"] * 10)[:0], court_every=6)

s.rowpack((2135, 1818, 2280, 1925), ["laborer", "servant", "merchant_house"] * 10, court_every=8, fill=True)
s.rowpack((2285, 1565, 2430, 1700), ["laborer", "merchant_house"] * 12, court_every=8, fill=True)


# THE CASTLE'S FIREBREAK RING, slim (the wall-settles-first pass, GM 2026-08-10): the
# umamawari is a kept CLEAR BAND around the citadel's moat - ~65px (195 ft) of bare ground -
# not a district-scale waste; with the settled wall the interior packs tight around it and
# the slack check holds the whole map to <= 15% open.
s.commons([(880, 545), (948, 545), (948, 1235), (880, 1235)], role="pasture", render="bare")
s.commons([(640, 730), (784, 730), (784, 1240), (640, 1240)], role="pasture", render="bare")
s.commons([(1345, 265), (1555, 265), (1555, 430), (1345, 430)], role="pasture", render="bare")
s.commons([(1852, 545), (1922, 545), (1922, 1245), (1852, 1245)], role="pasture", render="bare")
s.commons([(950, 452), (1850, 452), (1850, 512), (950, 512)], role="pasture", render="bare")
s.commons([(1240, 1266), (1560, 1266), (1560, 1352), (1240, 1352)], role="muster ground", render="bare")  # the ote front's hirokoji
s.commons([(1918, 1478), (2000, 1478), (2000, 1588), (1918, 1588)], role="festival ground", render="bare")  # Benten's east green
s.commons([(1900, 1590), (1985, 1590), (1985, 1700), (1900, 1700)], role="festival ground", render="bare")
s.commons([(318, 1100), (438, 1100), (438, 1560), (318, 1560)], role="pasture", render="bare")  # the west verge inside the wall's tightest arc

# the thread street's west run fronts the government quarter's forecourt apron, and the
# band street's west run faces the rampart approach - both CLAIMED open ground, not slack
s.commons([(1290, 1398), (1553, 1398), (1553, 1448), (1290, 1448)], render="bare")
s.commons([(1000, 2242), (1270, 2242), (1270, 2338), (1000, 2338)], render="bare")
s.commons([(1355, 2244), (1595, 2244), (1595, 2336), (1355, 2336)], render="bare")  # the S-gate approach: the column ground where the Imperial road crosses the band street
s.commons([(1130, 2150), (1240, 2150), (1240, 2242), (1130, 2242)], render="bare")  # the infill block's open court - the collision-circle waste never lets rows take it

# the N band's two open cores are the garrison's drill grounds - CLAIMED working
# ground (samurai band; the housing budget has no seats for them and the ground is real)
s.commons([(1138, 256), (1268, 256), (1268, 338), (1138, 338)], render="bare")
s.commons([(1505, 253), (1637, 253), (1637, 330), (1505, 330)], render="bare")
s.commons([(1090, 1300), (1195, 1300), (1195, 1390), (1090, 1390)], render="bare")  # the shrunk detached file's freed strip - moat-side firebreak ground
s.commons([(1815, 355), (1925, 355), (1925, 440), (1815, 440)], render="bare")
s.commons([(535, 635), (640, 635), (640, 725), (535, 725)], render="bare")
s.commons([(830, 470), (945, 470), (945, 560), (830, 560)], render="bare")
s.commons([(2052, 1662), (2150, 1662), (2150, 1750), (2052, 1750)], render="bare")
s.commons([(1640, 1250), (1732, 1250), (1732, 1332), (1640, 1332)], render="bare")

_mseat = s.open_seat((1240, 1420, 1720, 1560), 62, 46) or (1466, 1530)
s.mausoleum(_mseat[0], _mseat[1], 58, 42, label="Ancestral Mausoleum", gate_dir="south")

s.frontage(
    [(1210, 2210), (1580, 2210)], ["shop"], width=8, spacing=25, setback=3, jitter=1, dense=True
)  # the band street's north face. The ask is ONE shop: the packed rows either side of this street were already built when it was cut, so its frontage is what the leftover ground holds, not the 1,140 ft of shopfront the first draft asked for - it had 1,140 ft bare on both sides
