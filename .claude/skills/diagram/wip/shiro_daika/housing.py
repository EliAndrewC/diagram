"""Part of the Shiro Daika map, split from shiro-daika.gen.py by feature 173.

Importing this module EXECUTES this part of the drawing. See CLAUDE.md in this directory.
"""

# THE ORDER IS A CONTRACT, AND THIS IMPORT IS WHAT HOLDS IT. `s` comes from the part IMMEDIATELY
# ABOVE this one, not from `frame`, so Python cannot execute this part until that one has
# finished drawing. The first cut of this split had every part import from `frame`, which
# constrained only that `frame` ran first - and `ruff`'s isort then sorted the list in
# `__init__.py` ALPHABETICALLY, so `fields` (which calls `s.finish()`) ran fourth of seven and
# the wharf, the yashiki band and the trade works drew into a map already written to disk.
# Caught by settlement-review, 2026-08-31; invisible to the gate, which rolls no wip map.
from .wharf import s

# ---- BUDGET RECONCILIATION (feature 021, T002 - BEFORE any pack runs). From the recorded
# budget block: band targets yashiki 53 / detached 133 / terrace 79 (ranges of ~8 cells ->
# ~10 ranges) / packed 2,160 families; 2,472 dwellings total, of which ~2,430 in-wall and
# ~42-47 samurai households out-wall (SAMURAI_INWALL_FRAC) in the gate suburbs. Ground:
# wall interior 3,043,172 px^2 == the budget's required 3,043,258 px^2 (the wall IS the
# budget's output); standing 019/020 structures 736,580 px^2 (castle 598,000 dominant);
# housing gross need 2,092,330 px^2 + remaining civic ~65,000 px^2 against ~2,306,600 px^2
# free = ~5% slack. NO TARGET IS CAPPED - the packs aim at the full band numbers, and a
# pack that cannot seat its target is a siting bug to fix, not a target to trim (the
# Minami unmeetable-target lesson runs the OTHER way here, by design of the 018 budget).

# ===================== FEATURE 021: THE HOUSING FABRIC =====================
# DRAW ORDER: streets first (packs front them), then the walled yashiki band around the
# castle (each compound reserves its own ground), then detached / terraces / machi packs.

# ---- the machi STREET MESH (south half; the ote-suji, Imperial road and ring road are the
# spines already). Ordinary streets 15 real ft, the market cross main at 18 (Honcho-dori
# class stays the ote-suji's alone). Ends meet the ring road for circulation; the E-W pair
# at y=1350 stops clear of the government band (no street across the ministry fronts).
s.street([(620, 1770), (2180, 1770)], width=s.lw(18), main=True)  # ends short of the rampart's tower line
s.street([(802, 2005), (1799, 2005)], width=s.lw(15))  # dropped south of the Temple of Inari's hall (992,1937)
s.street([(1040, 1284), (1040, 2238)], width=s.lw(15))  # x=1040 clears the Temple of Inari's hall (~x992)
s.street([(1800, 1300), (1800, 1540)], width=s.lw(15))  # stops at the Benten precinct's reserved ground
s.street([(1800, 1700), (1800, 2236)], width=s.lw(15))  # ...and resumes south of it (a precinct blocks a street; the walls are the dead end)
s.street(
    [(2130, 1250), (2130, 1620), (2185, 1668), (2180, 1770)], width=s.lw(15)
)  # east of Kurogi; bends EAST around the Temple of Ebisu (2127,1686) to tie the NE grid into the y=1770 main street (021: streets_connected)
s.street([(800, 1560), (803.9, 2239.0)], width=s.lw(15))  # meets the y=1375 street
s.street([(329.6, 1376.0), (1240, 1375)], width=s.lw(15))  # west end lands on the ring's inner edge  # y=1375: under the west band tail, over the kagi leg
s.street([(1560, 1390), (2387, 1390)], width=s.lw(15))  # threaded between Kurogi's south wall (y1372) and the Imperial Magistracy's north wall (y1407)

# ---- the YASHIKI BAND (T007): 53 walled compounds of Ranks 8-12 wrap the castle N / E / W
# per the jokamachi law (rank = proximity to the court). The EIGHT lineage estates already
# stand in this band and count among the 53, so 45 anonymous compounds join them:
# 18 north (+ yodo/nio/seki = 21), 14 east (+ hazama/utsuro/kurogi = 17), 13 west
# (+ tokiwa/anzu = 15). Each fronts a band lane by its south/east/west gate; sizes jitter
# around the C_YASHIKI footprint (~60 x 50 px at 3 ft/px).
s.district("north yashiki band", "yashiki", [(1100, 268), (2010, 268), (2010, 505), (1100, 505)], rank_band="yashiki")
s.district("east yashiki band", "yashiki", [(1855, 555), (2165, 555), (2165, 1760), (1855, 1760)], rank_band="yashiki")
s.district("west yashiki band", "yashiki", [(590, 555), (945, 555), (945, 1460), (590, 1460)], rank_band="yashiki")
s.district("ote west yashiki flank", "yashiki", [(1150, 1290), (1315, 1290), (1315, 1540), (1150, 1540)], rank_band="yashiki")
s.district("ote east yashiki flank", "yashiki", [(1560, 1290), (1855, 1290), (1855, 1390), (1560, 1390)], rank_band="yashiki")
s.lane([(1140, 475), (1870, 475)], width=7)
s.lane([(1965, 1270), (1965, 1770)], width=7)  # the southern leg, west of Kurogi + the Benten precinct - it RUNS TO the y1770 street rather than halting 90 ft short of it (GM 2026-08-11)
s.lane([(1205, 1300), (1205, 1520)], width=7)  # the ote west flank's own lane

_YJ = ((2, -2), (-4, 2), (4, 4), (-2, -4), (0, 2), (3, -3))  # deterministic size jitter, no stream draw


def _yashiki(x: float, y: float, gate_dir: str, i: int) -> None:
    _w = 60 + _YJ[i % 6][0] + round(2 * s._hjit(x, y, 31.0)) - 1  # survey jitter: 42 plots in 6 exact
    _h = 50 + _YJ[i % 6][1] + round(2 * s._hjit(x, y, 32.0)) - 1  # size classes read stamped (review 2026-08-10)
    s.manor(x, y, _w, _h, None, gate_dir=gate_dir)


# north band: ONE row sharing the estates' line (gates south onto the y=475 lane). The
# wall and ring slant hard across y~270-450 here (vertices at (1082,290)/(1718,290) with
# the ring 30 inside), and the NW diagonal road owns the band's west half - both ate the
# planned second row, so the band runs east of the karamete corridor's flanks only.
for _i, _x in enumerate((1250, 1760, 1830, 1900)):  # x1325 went to the N caravan yard; the band keeps its count on the east end (GM 2026-08-10)
    _yashiki(_x, 430, "south", _i + 3)
# east band: a west file on the band lane (starting BELOW the Temple of Bishamon's ground
# at (1928,531)), a south file flanking the lane's lower leg around the reserved Benten
# precinct (~x1785-1915, y1570-1670), and east-side compounds in the lineage-estate gaps
for _i, _y in enumerate((673, 751, 829, 907, 985, 1063, 1141, 1219)):  # x1918: 7px clear of Hazama's west wall (x1925 shared it)
    _yashiki(1918, _y, "east", _i)
for _i, _y in enumerate((1300, 1490, 1715)):
    _yashiki(1905, _y, "east", _i + 2)
for _i, _y in enumerate((1490, 1565)):
    _yashiki(2040, _y, "west", _i + 1)
for _i, _y in enumerate((628, 850, 1120, 1195)):  # 628: the file's head clears the resized ring and Hazama's court
    _yashiki(2075, _y, "west", _i + 2)
# west band: an east file facing the lane, plus west-side compounds in the estate gaps
# (the file's head stays clear of the Temple of Hotei at (764,615))
for _i, _y in enumerate((592, 666, 740, 814, 888, 962, 1036, 1110, 1184, 1258)):
    _yashiki(860, _y, "west", _i + 1)
for _i, _y in enumerate((850, 1090, 1165, 1240, 1315, 1420)):  # the y=595 head slot died on the ring corridor + the Temple of Hotei
    _yashiki(700, _y, "east", _i + 4)
# the ote flanks: senior households as near the government band as the standoffs allow -
# a west file on its own lane, and a north file whose gates open south onto the threaded
# y=1390 street between Kurogi's walls and the Imperial Magistracy
for _i, _y in enumerate((1330, 1405, 1480)):
    _yashiki(1255, _y, "west", _i + 1)
for _i, _x in enumerate((1600, 1680)):  # x=1780 died on the x=1800 street
    _yashiki(_x, 1330, "south", _i + 2)

# ---- T009: RETAINER TERRACES (79 units target; 10 ranges of 8). The kumi-yashiki go where
# junior samurai serve: flanking the karamete approach (the castle guard), and inside each
# working gate (the gate watch). Placed BEFORE the machi packs so the rows flow around them.
s.district("karamete terraces", "terrace", [(1340, 290), (1460, 290), (1460, 440), (1340, 440)], rank_band="terrace")
for _ty in (352, 420):  # the left file starts lower - the NW diagonal road passes y~308 here
    s.terrace(1372, _ty, units=8, rot=90)
for _ty in (334, 399):
    s.terrace(1428, _ty, units=8, rot=90)
s.district("east gate terraces", "terrace", [(2225, 1130), (2290, 1130), (2290, 1270), (2225, 1270)], rank_band="terrace")
s.terrace(2255, 1148, units=8)
s.terrace(2255, 1252, units=8)
s.district("south gate terraces", "terrace", [(1325, 2050), (1475, 2050), (1475, 2120), (1325, 2120)], rank_band="terrace")
s.terrace(1352, 2085, units=8, rot=90)
s.terrace(1448, 2085, units=8, rot=90)
s.district("southwest gate terraces", "terrace", [(730, 1800), (790, 1800), (790, 1855), (730, 1855)], rank_band="terrace")
s.terrace(762, 1828, units=8, rot=90)  # vertical ranges: the only window between the x=740 alley and the x=800 street
s.terrace(775, 1828, units=8, rot=90)

# alleys BEFORE the packs (each reserves its corridor; no block core sits >95px from a way)
s.alley([(640, 1375), (640, 1552)])  # the D5/west mid-band pocket (x=640: clear of the (700,1420) compound)
# the east gate ward (its road runs ~y1170)
s.alley([(2305, 2080), (2440, 1910)])  # the wharf's upstream bank boxes
# the east approach samurai seats
s.alley([(530, 770), (532, 1470)])  # the west rim's spine (early: wells must not seat on its line)
s.alley([(740, 1585), (740, 1880)])  # stops short of the SW terrace window
s.alley([(880, 1560), (880, 2005)])  # runs THROUGH to the y2005 street (it stopped 23px short)  # snapped: kagi road leg to the ring's SW curve
s.alley([(1180, 1560), (1180, 2095)])
s.alley([(1300, 1560), (1300, 2112)])
s.alley([(1565, 1390), (1565, 2103)])  # runs up past the kagi to serve the magistracy flank
s.alley([(1655, 1585), (1655, 2090)])  # east columns clear the hanko (x1415-1549) and the (1905,1715) compound
# x1690 alley dropped: it ran through the (1690,1935) brewery; x1655 and the x1800 street cover the cores
s.alley([(2000, 1585), (2000, 1938)])  # stops inside the wall's south curve
s.alley([(2200, 760), (2200, 1290)])
s.alley([(2290, 891), (2290, 1290)])  # both start below the NE wall's tower course
s.alley([(2260, 1290), (2260, 1590)])

# the machi + suburb DISTRICTS, declared before the mesh and the packs (kido_mesh and
# the band checks read them; a mesh run before the declarations bars nothing)
s.district("southwest machi", "machi", [(552, 1570), (1395, 1570), (1395, 2110), (552, 2110)], rank_band=None)
s.district("southeast machi", "machi", [(1405, 1575), (2120, 1575), (2120, 2110), (1405, 2110)], rank_band=None)
s.district("east gate machi", "machi", [(1940, 550), (2405, 550), (2405, 1310), (1940, 1310)], rank_band=None)
s.district("east street machi", "machi", [(2140, 1420), (2385, 1420), (2385, 1725), (2140, 1725)], rank_band=None)
s.district("west rim machi", "machi", [(430, 750), (590, 750), (590, 1445), (430, 1445)], rank_band=None)
s.district("Benten monzen", "monzen", [(1762, 1636), (1938, 1636), (1938, 1855), (1762, 1855)], rank_band=None)
s.district(
    "Jurojin monzen", "monzen", [(820, 1478), (1120, 1478), (1120, 1585), (820, 1585)], rank_band=None
)  # the lay quarter strings ALONG the kagi road both ways from the sando mouth (Jurojin rolled the full 7-arch avenue, so it commands a full monzen)

s.district("wharf suburb", "machi", [(2020, 1940), (2540, 1940), (2540, 2545), (2020, 2545)], rank_band=None)
s.district("south gate ward", "machi", [(1028, 2590), (1625, 2590), (1625, 3042), (1028, 3042)], rank_band=None)
s.district("east gate ward", "machi", [(2440, 770), (2945, 770), (2945, 1495), (2440, 1495)], rank_band=None)
s.district("towpath shore", "machi", [(1548, 2530), (2100, 2530), (2100, 2885), (1548, 2885)], rank_band=None)
s.district("northeast riverside", "machi", [(2440, 770), (2760, 770), (2760, 1180), (2440, 1180)], rank_band=None)
s.district("west approach", "machi", [(52, 1978), (368, 1978), (368, 2442), (52, 2442)], rank_band=None)
s.district("southwest road wing", "machi", [(52, 1978), (368, 1978), (368, 2442), (52, 2442)], rank_band=None)
s.district("north gate ward", "machi", [(775, -60), (1655, -60), (1655, 172), (775, 172)], rank_band=None)
