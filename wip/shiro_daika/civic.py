"""Part of the Shiro Daika map, split from shiro-daika.gen.py by feature 173.

Importing this module EXECUTES this part of the drawing. See CLAUDE.md in this directory.
"""

from .frame import RING

# THE ORDER IS A CONTRACT, AND THIS IMPORT IS WHAT HOLDS IT. `s` comes from the part IMMEDIATELY
# ABOVE this one, not from `frame`, so Python cannot execute this part until that one has
# finished drawing. The first cut of this split had every part import from `frame`, which
# constrained only that `frame` ran first - and `ruff`'s isort then sorted the list in
# `__init__.py` ALPHABETICALLY, so `fields` (which calls `s.finish()`) ran fourth of seven and
# the wharf, the yashiki band and the trade works drew into a map already written to disk.
# Caught by settlement-review, 2026-08-31; invisible to the gate, which rolls no wip map.
from .trades import s

# ---- T016: the kido MESH, before the packs (each gate reserves its ground; the mouths
# derive from the declared districts + streets via the shared machi_mouths source)
# ---- T015: fire towers over the dense fabric, placed first so the rows flow around them
# (research 021 item 5: the 1723 mandate - per-machi hinomi at the capital count ~10-15)
for _fx, _fy in ((850, 1650), (1200, 1900), (1600, 1900), (1900, 1780), (2250, 900), (2274, 1536), (495, 1100), (2300, 1830), (940, 1990), (1265, 1662), (905, 2275), (553, 1710)):
    s.fire_tower(_fx, _fy, label=None)
s.alley([(2115, 640), (2255, 640)])  # east of the x2075 yashiki file; ends inside the ring (wall's east arc is x~2300 here)
s.alley([(2190.8, 568.9), (2200, 1235)])  # the deep E machi block's roji (before the wells, so the well grid dodges them)

# ---- T013/T014: the PUBLIC WELLS, before the packs so the rows ring their courts.
for _hw in (
    (2240, 758),
    (2260, 622),
    (2210, 706),
    (2168, 700),
):
    if any((_w8["x"] - _hw[0]) ** 2 + (_w8["y"] - _hw[1]) ** 2 <= 50 * 50 for _w8 in s.M.get("wells", [])):
        continue  # one wellhead per 150 ft neighborhood (GM 2026-08-10: knots of 4-6 read wrong)
    s.well(_hw[0], _hw[1])  # hand-seeded court wells for the pockets the grids kept missing

# The josui-ido band first: cistern-wells on the gate road within ~600 ft of the settling
# basin (research item 4); dug draw-wells serve everything else.
# the deep-file quarters (the E gate machi's long rows, the mid-south strip) carry the most
# households per wellhead, so they get a second, tighter gap-fill pass of their own
for _dq in ((2150, 660, 2400, 1200), (1050, 1830, 1400, 1960), (1650, 1830, 2060, 1990), (2090, 1830, 2180, 1960), (2150, 1450, 2380, 1660)):
    for _dx in range(int(_dq[0]), int(_dq[2]), 40):
        for _dy in range(int(_dq[1]), int(_dq[3]), 40):
            if any((_w["x"] - _dx) ** 2 + (_w["y"] - _dy) ** 2 <= 70 * 70 for _w in s.M.get("wells", [])):
                continue
            _dseat = s.open_seat((_dx - 22, _dy - 22, _dx + 22, _dy + 22), 9, 9, well=True)
            if _dseat and sum(1 for _w in s.M.get("wells", []) if (_w["x"] - _dseat[0]) ** 2 + (_w["y"] - _dseat[1]) ** 2 <= 50 * 50) < 3:
                s.well(_dseat[0], _dseat[1])

s.place_wells(
    (2250, 1350, 2400, 1425), spacing=74, kind="cistern", coverage=False
)  # the josui-ido file inside the E gate, on the buried main from the new settling basin (laterals under the roji, research item 4)
# WELL GRIDS ARE DERIVED, NOT HAND-TUNED (GM 2026-08-10: 27 hand boxes, many overlapping,
# had knotted 4-7 wellheads together in several quarters). For each machi QUARTER we split
# its bbox at the streets and alleys that actually cross it and lay one grid per resulting
# BLOCK, inset off the beds - so wells sit in block interiors by construction, no two grids
# cover the same ground, and re-flowing a street moves the wells with it.
s.street([(1040, 2238.1), (2005.3, 2234.1)], width=s.lw(15))
# ways declared LATE (the machi roji) are hoisted here: the well grids read the way
# list at the moment they run, so an alley drawn after them cannot be dodged (GM
# 2026-08-10: wells sat on the S band roji for exactly this reason)
s.alley([(1741, 256), (1738, 348)])
s.alley([(532, 1470), (535, 1975)])  # the crescent's spine
s.alley([(500, 1767), (620, 1760)])
s.alley([(880, 2005), (879, 2274)])  # starts ON the y2005 street
s.alley([(1560, 2005), (1560, 2236)])
s.alley([(1760, 2005), (1766, 2235)])
s.alley([(1990, 1875), (1990, 2140)])
s.alley([(1900, 2008), (2100, 2008)])
# the shore path serving the towpath-side porters' rows
# the shore rows' spine (before its packs)


def _well_blocks(x0, y0, x1, y1, spacing, inset=30):
    """Lay one well grid per BLOCK: take the quarter's bbox, cut out the bands the streets and
    alleys crossing it occupy (bed half-width + inset), and grid each surviving rectangle."""

    def _free(lo, hi, bands):
        out, cur = [], lo
        for b0, b1 in sorted(bands):
            if b1 <= cur:
                continue
            if b0 > cur:
                out.append((cur, min(b0, hi)))
            cur = max(cur, b1)
            if cur >= hi:
                break
        if cur < hi:
            out.append((cur, hi))
        return [(a, b) for a, b in out if b - a >= 40]

    xb, yb = [], []
    for _w in s.M.get("town_streets", []) + s.M.get("alleys", []):
        _pts = _w["pts"]
        _hw = _w.get("w", 12) / 2 + inset
        for _i in range(len(_pts) - 1):
            (ax, ay), (bx, by) = _pts[_i], _pts[_i + 1]
            if abs(ax - bx) < 6 and x0 < ax < x1 and min(ay, by) < y1 and max(ay, by) > y0:
                xb.append((ax - _hw, ax + _hw))
            elif abs(ay - by) < 6 and y0 < ay < y1 and min(ax, bx) < x1 and max(ax, bx) > x0:
                yb.append((ay - _hw, ay + _hw))
            elif max(ax, bx) > x0 and min(ax, bx) < x1 and max(ay, by) > y0 and min(ay, by) < y1:
                # an OBLIQUE way (the shore paths, the diagonal roji): cut its whole span on
                # the axis it travels least, so no grid cell straddles its bed
                if abs(ax - bx) < abs(ay - by):
                    xb.append((min(ax, bx) - _hw, max(ax, bx) + _hw))
                else:
                    yb.append((min(ay, by) - _hw, max(ay, by) + _hw))
    for bx0, bx1 in _free(x0, x1, xb):
        for by0, by1 in _free(y0, y1, yb):
            # ONE wellhead per grid CELL, sited by the engine (open_seat consults _fits, so it
            # will not stand on a lane, a corridor or a roof the way a raw grid seat can), and
            # only where no well already serves that 150 ft neighborhood
            nx = max(1, int((bx1 - bx0) // spacing))
            ny = max(1, int((by1 - by0) // spacing))
            for _cx in range(nx):
                for _cy in range(ny):
                    cell = (
                        bx0 + (bx1 - bx0) * _cx / nx,
                        by0 + (by1 - by0) * _cy / ny,
                        bx0 + (bx1 - bx0) * (_cx + 1) / nx,
                        by0 + (by1 - by0) * (_cy + 1) / ny,
                    )
                    seat = s.open_seat(cell, 9, 9, well=True)
                    # the cluster rule allows up to FOUR wellheads inside a 150 ft radius; test
                    # the SEAT, not the cell center, or a dense quarter's cells all seat toward
                    # one corner and knot anyway (GM 2026-08-10)
                    if seat and sum(1 for _w in s.M.get("wells", []) if (_w["x"] - seat[0]) ** 2 + (_w["y"] - seat[1]) ** 2 <= 50 * 50) < 3:
                        s.well(seat[0], seat[1])


_WELL_QUARTERS = (
    # (x0, y0, x1, y1, cell) - DISJOINT quarters, cell sized so each wellhead serves ~15-20
    # households at that quarter's row density (machi ~1.15 dwellings/kpx2 -> ~96px cells;
    # the burakumin rows and doss pocket run court_every=3, roughly double, so ~68px).
    # Spacings are set from that arithmetic, never by nudging a multiplier (GM 2026-08-10).
    (615, 1575, 1395, 1830, 58),  # SW machi
    (615, 1830, 1395, 2040, 50),  # ...its southern burakumin/doss strip: ~2x the row density
    (1405, 1575, 2120, 1840, 53),  # SE machi - cell tightened 58->53 when the denser machiya rows raised its household count
    (1405, 1840, 2120, 2040, 45),  # ...and its own dense southern strip, same reason
    (790, 2100, 1995, 2345, 50),  # the S band machi
    (2145, 635, 2405, 1250, 46),  # the E gate machi
    (2140, 1440, 2320, 1640, 60),  # the E street machi
    (430, 750, 590, 1445, 60),  # the W rim machi
    (445, 1450, 610, 2075, 48),  # the W crescent machi
    (1090, 1265, 1365, 1520, 63),  # the SW approach machi
    (1575, 1300, 1836, 1440, 63),  # the thread machi
    (2000, 1620, 2115, 1800, 60),  # the entertainment quarter
    (1762, 1636, 1938, 1855, 63),  # Benten's monzen
    (960, 1478, 1120, 1585, 63),  # Jurojin's monzen (east of the civic band)
    (1840, 1300, 1990, 1440, 60),  # the thread machi's east files
    (1900, 545, 1986, 640, 46),  # the N band's servant rows
    (395, 525, 482, 608, 48),  # the NW monk-house court
)
for _q in _WELL_QUARTERS:
    _well_blocks(*_q)


def _point_in(px, py, poly):
    inside = False
    for _i in range(len(poly)):
        x1, y1 = poly[_i]
        x2, y2 = poly[(_i + 1) % len(poly)]
        if (y1 > py) != (y2 > py) and px < (x2 - x1) * (py - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside


# COVERAGE GAP-FILL: the per-quarter cells leave holes where a block's grid could not seat
# (a court, a fence corridor, a temple apron), and those holes are what leave one wellhead
# doing three blocks' work. Walk the machi ground on a lattice and seat a well wherever the
# nearest one is more than ~110px off, honoring the same 4-per-150ft ceiling.
for _gx in range(440, 2400, 42):
    for _gy in range(520, 2350, 42):
        if not any(_q2[0] <= _gx <= _q2[2] and _q2[1] <= _gy <= _q2[3] for _q2 in _WELL_QUARTERS):
            continue
        if any((_w["x"] - _gx) ** 2 + (_w["y"] - _gy) ** 2 <= 78 * 78 for _w in s.M.get("wells", [])):
            continue
        if any(  # never inside a samurai/civic district - that quarter draws from its own compound wells
            _d2.get("rank_band") in ("yashiki", "detached", "terrace") or _d2.get("kind") in ("yashiki", "detached", "terrace", "civic", "government")
            for _d2 in s.M.get("districts", [])
            if _point_in(_gx, _gy, _d2["poly"])
        ):
            continue
        _gseat = s.open_seat((_gx - 26, _gy - 26, _gx + 26, _gy + 26), 9, 9, well=True)
        if _gseat and sum(1 for _w in s.M.get("wells", []) if (_w["x"] - _gseat[0]) ** 2 + (_w["y"] - _gseat[1]) ** 2 <= 50 * 50) < 3:
            s.well(_gseat[0], _gseat[1])

# ---- T008: DETACHED SAMURAI (133 target) - the middle band, rowpacked at the loose samurai
# court pitch (the Tango idiom, which is what C_SPACED was measured from).
_SAM = ["samurai"] * 4 + ["samurai_large"]
s.district("moat-south detached band", "detached", [(615, 1268), (1145, 1268), (1145, 1392), (615, 1392)], rank_band="detached")
s.rowpack((620, 1275, 1140, 1362), _SAM * 15, court_every=8, fill=True)
s.rowpack((1150, 1275, 1240, 1362), (_SAM * 4)[:0], court_every=8)
s.rowpack((1470, 285, 1730, 415), _SAM * 12, court_every=8, fill=True)  # the karamete-east shelf inside the ring curve
s.rowpack((900, 348, 1072, 386), (_SAM * 5)[:9], court_every=8)  # the NW shelf between the ring and the diagonal road
s.district("magistracy detached flank", "detached", [(1555, 1290), (1865, 1290), (1865, 1560), (1555, 1560)], rank_band="detached")
s.rowpack((1560, 1408, 1660, 1555), (_SAM * 4)[:3], court_every=8)
s.rowpack((1808, 1408, 1852, 1555), (_SAM * 2)[:7], court_every=8)
s.district("west detached pocket", "detached", [(470, 1400), (790, 1400), (790, 1745), (470, 1745)], rank_band="detached")
s.district("civic west detached", "detached", [(855, 1400), (1145, 1400), (1145, 1560), (855, 1560)], rank_band="detached")
s.district("east street detached", "detached", [(2140, 1250), (2445, 1250), (2445, 1428), (2140, 1428)], rank_band="detached")
s.district("north band detached west", "detached", [(1060, 260), (1340, 260), (1340, 370), (1060, 370)], rank_band="detached")
s.district("north band detached east", "detached", [(1640, 260), (1840, 260), (1840, 362), (1640, 362)], rank_band="detached")
s.rowpack((1062, 266, 1335, 368), _SAM * 10, court_every=8, fill=True)
s.rowpack((1852, 266, 1962, 372), _SAM * 8, court_every=8, fill=True)
s.rowpack((930, 452, 1075, 548), _SAM * 8, court_every=8, fill=True)  # officials' houses on the karamete's west shelf
s.rowpack((700, 430, 830, 520), _SAM * 6, court_every=8, fill=True)  # ...and its west neighbor
s.rowpack(
    (1770, 520, 1910, 610), (_SAM * 6)[:0], court_every=8
)  # the Bishamon ward's officials' file  # the N band's east shelf: officials' houses, in no rank district  # the tight wall's N band holes take the missing detached files
s.rowpack((1688, 268, 1832, 352), (_SAM * 4)[:10], court_every=8)
s.district("west crescent machi", "machi", [(445, 1450), (625, 1450), (625, 2075), (445, 2075)], rank_band=None)
s.block_polys.append([(592, 1738), (662, 1738), (662, 1818), (592, 1818)])
s.placed.append((627, 1778, 70, 80))  # the crescent kido's crossing (reserved before the rows)
s.rowpack((450, 1460, 620, 2070), ["laborer", "servant", "merchant_house", "laborer"] * 42, court_every=8, fill=True)
s.district("south band machi", "machi", [(790, 2050), (1995, 2050), (1995, 2345), (790, 2345)], rank_band=None)
s.block_polys.append([(895, 2245), (990, 2245), (990, 2340), (895, 2340)])  # Inari's backstrip stays lean (the temple rode the wall inward)


s.block_polys.append([(815, 2237), (2020, 2237), (2020, 2264), (815, 2264)])  # the band street's own corridor, held against the row pitch  # the band's own through-street

s.rowpack((800, 2100, 1330, 2320), ["laborer", "servant", "merchant_house", "laborer"] * 124, court_every=11, fill=True)
s.rowpack((1350, 2100, 1985, 2320), ["laborer", "servant", "merchant_house", "laborer"] * 104, court_every=11, fill=True)
s.rowpack((1060, 1270, 1360, 1515), ["laborer", "servant", "merchant_house"] * 34, court_every=10, fill=True)  # the freed SW approach ground joins the machi
s.district("southwest approach machi", "machi", [(1055, 1265), (1365, 1265), (1365, 1520), (1055, 1520)], rank_band=None)
s.district("thread machi", "machi", [(1575, 1295), (1905, 1295), (1905, 1440), (1575, 1440)], rank_band=None)
s.rowpack((1590, 1402, 1858, 1438), (["merchant_house", "laborer"] * 12)[:2], court_every=8)  # the households behind the thread frontage (ends clear of the 1905 kido's reserve)
s.rowpack((1580, 1300, 1900, 1438), ["laborer", "servant", "merchant_house"] * 44, court_every=8, fill=True)
s.frontage([(1595, 1390), (2130, 1390)], ["merchant", "shop"] * 4, width=8, spacing=21, setback=3, dense=True)  # the thread street's own commerce
s.rowpack((1552, 1448, 1700, 1558), _SAM * 11, court_every=8, fill=True)  # the magistracy flank keeps its detached files
s.district("east rim detached", "detached", [(2245, 1660), (2405, 1660), (2405, 1800), (2245, 1800)], rank_band="detached")
s.rowpack((2250, 1665, 2335, 1795), _SAM * 4, court_every=8, fill=True)
s.rowpack((1565, 1300, 1660, 1435), (_SAM * 6)[:0], court_every=8)  # the S band's cleared ground inside the new arc
s.rowpack((628, 1326, 772, 1362), (_SAM * 3)[:0], court_every=8)
s.rowpack((628, 1390, 772, 1424), (_SAM * 3)[:0], court_every=8)
s.rowpack((604, 1406, 790, 1556), _SAM * 8, court_every=8, fill=True)
s.rowpack((475, 1440, 595, 1740), (_SAM * 7)[:2], court_every=8)
s.rowpack((860, 1408, 1140, 1462), _SAM * 8, court_every=8, fill=True)  # ends above the Jurojin monzen (021)
s.rowpack((652, 1302, 1040, 1386), _SAM * 16, court_every=8, fill=True)  # the moat-south detached band fills its declared ground
s.rowpack((1188, 1596, 1224, 1714), (_SAM * 3)[:1], court_every=8)  # the dojo's own file (a hall stands among the samurai it serves)
s.rowpack((2145, 1255, 2420, 1415), _SAM * 17, court_every=8, fill=True)
s.rowpack((1860, 470, 1950, 650), (_SAM * 7)[:0], court_every=8)  # the moat-corner pocket (east of the moat, west of the band lane)

s.bound = [list(p) for p in RING]  # HARD RESTORE: a ward block above lost its bound restore once, and every later pack silently clipped to that stale box ('UNVISITED' ground)

# ---- T010: THE COMMONER MACHI (2,160 packed target: 960 laborer / 480 servant / 600
# merchant / 120 burakumin). Burakumin strips seat FIRST at the settlement edge (the two
# in-wall quarters of the counts table); the big machi packs then flow around them and
# around every standing compound, temple, precinct reservation and street.
s.district("southwest machi", "machi", [(615, 1575), (1395, 1575), (1395, 2110), (615, 2110)], rank_band=None)
s.district("southeast machi", "machi", [(1405, 1575), (2120, 1575), (2120, 2110), (1405, 2110)], rank_band=None)
s.district("east gate machi", "machi", [(2145, 635), (2405, 635), (2405, 1310), (2145, 1310)], rank_band=None)
s.district("east street machi", "machi", [(2140, 1420), (2440, 1420), (2440, 1660), (2140, 1660)], rank_band=None)
s.block_polys.append([(2082, 1732), (2158, 1732), (2158, 1810), (2082, 1810)])
s.placed.append((2120, 1770, 82, 80))
s.block_polys.append([(2145, 1687), (2220, 1687), (2220, 1764), (2145, 1764)])
s.placed.append((2182, 1725, 80, 78))  # SE kido crossings held BEFORE every machi pack (order, not coordinates, was the bug)
s.district("west rim machi", "machi", [(430, 750), (590, 750), (590, 1445), (430, 1445)], rank_band=None)
s.frontage([(1400, 1600), (1400, 2090)], ["merchant", "shop"] * 8, width=8, spacing=22, setback=12, dense=True)  # the Imperial road's in-machi commerce
s.frontage([(830, 1560), (1350, 1560)], ["merchant", "shop"] * 10, width=8, spacing=22, setback=3, dense=True)  # the kagi leg
s.frontage([(620, 1770), (1355, 1770)], (["merchant", "merchant", "shop"] * 7)[:20], width=8, spacing=20, setback=3, dense=True)
s.frontage([(1455, 1770), (2085, 1770)], (["merchant", "merchant", "shop"] * 6)[:17], width=8, spacing=20, setback=3, dense=True)  # gap at the x=1405 kido mouth
s.frontage([(990, 2005), (1085, 2005)], (["merchant", "shop"] * 2)[:3], width=8, spacing=20, setback=3, dense=True)
s.frontage([(1290, 2005), (1355, 2005)], ["shop"] * 3, width=8, spacing=20, setback=3, dense=True)  # split around the doss pocket's face - no fancy shopfronts against the humble quarter
s.frontage([(1455, 2005), (1795, 2005)], ["merchant", "shop"] * 8, width=8, spacing=20, setback=3, dense=True)
s.frontage([(1040, 1640), (1040, 2070)], ["merchant"] * 12, width=8, spacing=21, setback=3, dense=True)  # starts below the x=1040 machi mouth
s.frontage([(1800, 1710), (1800, 2050)], ["merchant"] * 10, width=8, spacing=21, setback=3, dense=True)
s.rowpack((775, 1838, 1020, 2016), (["burakumin"] * 5 + ["servant"] * 4) * 20, court_every=3, fill=True)
s.rowpack((1792, 1848, 1995, 2016), (["burakumin"] * 5 + ["servant"] * 4) * 22, court_every=3, fill=True)
# T011 first: the adept-monk houses by the two sovereign precincts (budget: 2.5/precinct) -
# seated BEFORE the big packs so the precinct-adjacent ground is theirs
s.rowpack((1700, 1585, 1780, 1660), (["monk_house"] * 3)[:3], court_every=3)
s.rowpack((1020, 1585, 1100, 1660), (["monk_house"] * 2)[:2], court_every=3)
_MIX = ["laborer", "laborer", "servant", "merchant_house"]  # lean interior mix; the wealth minority packs its own rows (a diluted mix cost ~180 families of ground)
_RICH = ["laborer_large", "laborer_large", "merchant_large"]
s.rowpack((640, 1600, 1080, 1660), _RICH * 14, court_every=6, fill=True)  # the wealth rows front the machi's north streets
s.rowpack((1440, 1600, 1900, 1660), _RICH * 14, court_every=6, fill=True)
s.rowpack((640, 1690, 1020, 1740), (["laborer_large"] * 24)[:15], court_every=6)
s.rowpack((2160, 940, 2390, 1000), ["laborer_large"] * 24, court_every=6, fill=True)
s.rowpack((1440, 1690, 1900, 1740), (["laborer_large"] * 24)[:2], court_every=6)
s.rowpack((556, 1576, 1390, 2072), _MIX * 448, court_every=11, fill=True)  # ...and the same west of the road
s.rowpack((1410, 1576, 1934, 2072), _MIX * 372, court_every=11, fill=True)  # more courts: the block's households had outgrown their wells
s.rowpack((1080, 2100, 1290, 2240), _MIX * 40, court_every=9, fill=True)  # the S-band dead-core infill (021 endgame)
s.rowpack((2000, 1580, 2115, 2085), (["laborer", "laborer_large", "servant"]) * 28, court_every=6, fill=True)  # the SE-east strip carries a wealth band (labL toward the 6% floor)
s.rowpack((1950, 560, 1978, 1310), ["laborer", "merchant_house"] * 40, court_every=6, fill=True)
s.rowpack((2002, 560, 2430, 1310), (["laborer", "merchant_house"]) * 400, court_every=6, fill=True)
s.rowpack((2145, 1425, 2330, 1615), _MIX * 26, court_every=6, fill=True)
s.rowpack((2150, 1625, 2255, 1715), _MIX * 8, court_every=6, fill=True)
s.rowpack((1740, 1295, 1852, 1385), (_MIX * 8)[:0], court_every=6)
s.rowpack((432, 755, 512, 1155), _MIX * 22, court_every=6, fill=True)
s.rowpack((440, 1250, 510, 1445), _MIX * 9, court_every=6, fill=True)  # resumes south of the Temple of Daikoku (501,1200)
s.rowpack((550, 760, 598, 1445), _MIX * 18, court_every=6, fill=True)


# 021 endgame: the last density pockets get their wells AFTER the packs, seated by the
# engine among the drawn courts (open_seat sees the court lanes and standing rows; the
# pre-pack grids tried first kept landing wells on the packs' own court lanes)
# ---- the SUBURBS (021): a capital houses part of its packed cohort OUTSIDE the wall - the
# kashi wharf suburb (its brokers and warehouse folk live at the landing) and the guan-xiang
# gate wards on the approach roads, both the lawful outside categories the commoner rule
# names. The packs honor s.bound, so each suburb temporarily owns its own bound box.
_CITY_BOUND2 = s.bound
# the wharf suburb: bank-aligned boxes between the MOAT's outer edge and the river, stepping
# down the diagonal shore with the broker street (the first cut boxed the whole quay and
# packed rows onto the moat band)
s.bound = [[2020, 1950], [2520, 1950], [2520, 2530], [2020, 2530]]
s.rowpack((2338, 2010, 2410, 2090), (["merchant_house", "laborer", "laborer"] * 5)[:8], court_every=3)
s.rowpack((2276, 2110, 2346, 2190), (["merchant_house", "laborer", "laborer"] * 5)[:3], court_every=3)
s.rowpack((2205, 2205, 2280, 2285), (["merchant_house", "laborer"] * 6)[:2], court_every=3)
s.rowpack((2135, 2300, 2225, 2372), (["laborer", "servant"] * 3)[:6], court_every=3)
s.rowpack((2092, 2400, 2152, 2467), (["laborer", "servant"] * 4)[:8], court_every=3)
# the TOWPATH SHORE (the haulage side of the wharf): porters' and boatmen's rows on the
# land between the wall's south arc and the river, within the wharf's own reach
s.bound = [[2080, 2310], [2175, 2310], [2175, 2465], [2080, 2465]]
s.granary(
    2196, 2430, n=3, w=22, h=14, gap=9, label="brokers' warehouses", append=True, rot=-64.1
)  # the row lies along the river's LOCAL bearing here (115.9 deg), not the wharf's upstream one  # the merchants' own bulk store on the quay - the wharf chain's missing link (GM 2026-08-10)
s.rowpack(
    (2086, 2306, 2158, 2470), (["laborer", "laborer", "servant"] * 11)[:-9], court_every=6, fill=True
)  # box densely verified clear of moat, wall, river and drain  # the porters' rows, landward of the warehouses they load
s.bound = [[1820, 2450], [2100, 2450], [2100, 2810], [1820, 2810]]
s.cemetery(1640, 2680, 84, 60, parish=False, label="common burial ground")
# THE FULL FUNERARY GEOGRAPHY (GM 2026-08-10: "I don't see a cremation ground or pauper's
# burial mound at all... I also don't see a mausoleum"). The whole funerary block was gated on
# scale in (village, town, city) and the capital tier skipped it - a city of 12,400 with no
# crematory, no ossuary and no clan crypt. Sited by the same doctrine the provincial cities
# follow: the crematory OUTSIDE the walls beyond a gate (smoke and pollution), the pauper
# ossuary beside it, both by the common burial ground on the way out; the clan's ancestral
# mausoleum INSIDE, by the government quarter, a walled crypt precinct.
s.cremation_ground(1748, 2668)
s.ossuary(1572, 2718)
s.rowpack((2184, 2300, 2262, 2478), (["laborer", "servant"] * 15)[:0], court_every=6)  # ...and the boatmen's rows, the other side of the porters' block
# the gate wards, each hugging its approach road inside the guan-xiang reach
s.placed.append((1204, 2561, 22, 18))
s.placed.append((1204, 2585, 22, 18))
s.bound = [[1195, 2546], [1770, 2546], [1770, 2981], [1195, 2981]]
# (the x1205-1295 head block stays open: the relay yard takes it)
s.bound = [[2565, 1113], [3015, 1113], [3015, 1273], [2565, 1273]]
s.bound = [[2535, 753], [2815, 753], [2815, 1113], [2535, 1113]]

s.bound = [[1225, 53], [1430, 53], [1430, 135], [1225, 135]]
s.placed.append((1017, 115, 107, -9))
s.placed.append((1033, 63, 107, -9))  # the N market's scan-seated shops hold their ground before the ward rows
s.bound = [[860, 60], [1360, 60], [1360, 210], [860, 210]]
s.bound = [[1410, 35], [1810, 35], [1810, 160], [1410, 160]]
s.bound = [[895, 0], [1170, 182], [1170, 182], [895, 0]]
s.bound = [[895, 0], [1170, 0], [1170, 182], [895, 182]]
s.bound = [[250, 2180], [450, 2180], [450, 2310], [250, 2310]]
_SWB = s.bound
s.bound = [[220, 1990], [505, 1990], [505, 2430], [220, 2430]]
_MKB = s.bound
_MKB = s.bound
s.bound = [[250, 1830], [700, 1830], [700, 2210], [250, 2210]]
s.frontage([(478, 2006), (320, 2105), (180, 2160)], ["shop"] * 9, width=8, spacing=24, setback=14, jitter=1, dense=True)  # SW gate market, on the road itself
s.place_caption("gate market", s.frontage_box, 10)  # the southwest strip
s.bound = [[1300, 2500], [1500, 2500], [1500, 2860], [1300, 2860]]
s.frontage([(1400, 2512), (1400, 2830)], ["shop"] * 13, width=8, spacing=22, setback=3, jitter=1, dense=True)  # S gate market, down the Imperial road
s.place_caption("gate market", s.frontage_box, 10)  # the south strip, on the Imperial road
s.bound = [[830, 40], [1500, 40], [1500, 215], [830, 215]]  # the box must reach the GATE (x1400) or the strip's head is refused - the market has to start at the mouth (GM 2026-08-10)
s.frontage([(1400, 120), (1200, 92), (1000, 116)], ["shop"] * 6, width=8, spacing=22, setback=3, jitter=1, dense=True)
s.place_caption("gate market", s.frontage_box, 10)  # the north strip
# the strip HEAD: the only ground within 200 ft of the N gate that clears the moat band,
# the road corridor and the gate tower is the pocket east of the road's turn, so the
# market crowds in there and strings west from it (GM 2026-08-10, probed not guessed)
s.frontage([(1408, 104), (1470, 140)], ["shop", "merchant"], width=8, spacing=20, setback=3, jitter=1, dense=True)
# NO inner file here (2026-08-11): the strip between the road and the moat bank is ~26 ft of
# usable ground once the road's cleared band and the bank are taken out, and a 14-shop ask
# placed exactly ZERO. The market is the outer file plus the head pocket; the record now says so.
s.bound = [[2430, 1200], [2830, 1200], [2830, 1400], [2430, 1400]]
s.frontage([(2545, 1306), (2800, 1247)], ["shop"] * 9, width=8, spacing=21, setback=3, jitter=1, dense=True)  # E gate market on the Fox-lands road
s.place_caption("gate market", s.frontage_box, 10)  # the east gate, on the Fox-lands road
s.bound = _MKB
s.bound = _SWB  # guan-xiang shops strung along the SW approach road
s.bound = [[119, 1687], [391, 1687], [391, 2237], [119, 2237]]
s.bound = [[421, 2087], [766, 2087], [766, 2282], [421, 2282]]
s.bound = [[886, 2337], [1291, 2337], [1291, 2497], [886, 2497]]
s.bound = _CITY_BOUND2


# the suburbs are DISTRICTS like any fabric (the band-target check counts by district)

# ---- the OUT-WALL SAMURAI (the budget's other 47: CAPITAL_SAMURAI_INWALL_FRAC leaves 15%
# of the cohort in country seats on the approaches - the Tango out-wall precedent; they
# count in the census but belong to NO rank district, so the in-wall band targets stand)
# A COUNTRY SEAT IS A WALLED COMPOUND, NOT A ROW (GM 2026-08-10, and the settlement-review
# said the same of the first pass): the budget's out-wall samurai are landed retainers on the
# approaches, so they take walled estates with their own ground - the machi-form rowpacks that
# stood here read as suburb tenements with samurai labels, and left 24 free-standing samurai
# houses outside the walls where city_samurai_houses_inside_walls rightly wants none.
_CB3 = s.bound
# ...and they stand on the NORTHEAST approach, the road to Otosan Uchi: an out-wall estate
# faces the capital (city_estates_toward_capital), and the three vary in size the way three
# lineages' seats would. Seats computed clear of wall, moat, roads and every standing solid.
s.bound = [[2560, 120], [3130, 120], [3130, 640], [2560, 640]]
s.manor(2680, 210, 118, 92, None, gate_dir="west")
s.manor(2640, 450, 96, 74, None, gate_dir="west")
s.manor(2900, 330, 78, 62, None, gate_dir="south")
s.bound = _CB3


# ---- the market-day flophouses at the working gates (outside, by the gate markets) and
# the merchant kura attached behind the shopfronts (counts table ~20)
# ---- T023: the RELAY (tenma) STABLES + FARRIER at the south gate market - the Imperial
# road's post service, largest class (a domain capital is a first-rank relay stop); iron
# shoeing per canon (the Imperial relay puts institutional demand on the forge)
s.stables(1248, 2320, rot=0)
s.farrier(1185, 2272, rot=0)
s.merchant_storehouses(count=20)

# ---- declared quarters (feature 020 re-zone): the CIVIC quarter is the ground the government
# actually occupies - the ote-suji band south of the ote-mon, ministries to chancellery - not a
# wedge picked before the castle was placed. The four interior wedges split at the kagi-no-te
# junction, where the avenue meets the through-road, and carry no zone stronger than "mixed"
# until feature 021 packs them. Quarters are declarative overlays, so the civic band riding over
# the wedge seams is intentional.
# 021 re-zone: a capital's quarters follow its FABRIC, not compass wedges - the old wedges
# averaged the castle moat into machi density and could never read right. Zones "castle"
# and "samurai" are exempt from the residential density body by the checks' own zone
# filter (senior compounds at C_YASHIKI are ~0.24 dwellings/1000px^2, legitimately under
# the machi floor); the south "mixed" wedge is where the density band bites.
s.quarter([(949, 504), (1851, 504), (1851, 1256), (949, 1256)], "castle")
s.quarter([(1057, 219), (1400, 163), (1743, 219), (2052, 383), (1851, 504), (949, 504)], "samurai")  # north band
s.quarter([(1851, 504), (2052, 383), (2246, 608), (2378, 904), (2510, 1313), (2378, 1496), (2160, 1390), (1855, 1390), (1851, 1256)], "samurai")  # east band + gate machi rim
s.quarter([(949, 504), (748, 383), (502, 637), (422, 904), (290, 1313), (422, 1496), (560, 1390), (1150, 1390), (1150, 1290), (949, 1256)], "samurai")  # west band
s.quarter([(1315, 1290), (1560, 1290), (1560, 1720), (1315, 1720)], "civic")  # the government band proper
s.quarter(
    [(422, 1496), (502, 1989), (748, 2243), (1057, 2407), (1400, 2463), (1743, 2407), (2052, 2243), (2246, 1792), (2378, 1496), (2160, 1390), (1150, 1390), (560, 1390)], "mixed"
)  # the machi south
