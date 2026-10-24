"""Row dumps and this project's arithmetic on the Mitsui Bunko price and wage cells, for feature 412 session 1.

The file is J.-P. Bassino's transcription of Mitsui Bunko (1989) Tables 6-8 for the Global Price and Income History
Group: https://gpih.ucdavis.edu/files/Japan_1710-1871.xls (sheets "Mitsui Bunko Kyoto T6", "Mitsui Bunko Edo T7",
"Mitsui Bunko Osaka T8"; "Sources and conversion" holds its notes). Every cell read is a QUARTERLY one (columns D on,
"Spring"/"Fall"), never the file's own yearly averages; row numbers are the sheet's, counted from 1.

What it prints, each figure this project's arithmetic:
- research/questions/0273-what-did-salt-cost.html: Kyoto salt (塩, silver monme a koku), the twenty seasons of
  1745-1754, their mean and range, and the mean a sho (a tenth of a to, a hundredth of a koku). A price by weight
  needs a weight of a koku of salt, which no source read gives; the per-kg line is printed at an ASSUMED 1.0 to 1.2 kg
  a liter of salt (a guess, labeled so in the question) and the file's 180.891 liters a koku.
- research/questions/0279-what-did-charcoal-cost.html: Kyoto firewood (薪, silver monme for 10 kan); the mean over the
  same twenty seasons, a kilogram at the file's 1 kan = 3.75 kg, and a million BTU (1,055.06 MJ) at 15.5 MJ a kg,
  FAO Forestry Paper 93's gross heating value of seasoned, air-dried wood at 20 percent moisture (a modern figure,
  not a measurement of Kyoto's wood). Edo's charcoal (炭) and firewood 1710-1716 and 1818-1823, and Osaka's
  1818-1823, the cells as they stand.
- research/questions/0250-what-did-an-unskilled-laborer-earn.html: the day laborer's wage (日雇賃, silver monme a
  man) by decade and by the spans the question names, Kyoto and Edo: the mean of every quarterly cell in the span,
  each cell weighted alike (n is the count of cells). (The search pass averaged the file's yearly cells instead, which
  weights a year with one season as much as a year with two, so a few of its means differ in the second decimal.)
- Edo's salt a koku by decade from 1818, and every Edo cell of 1842, for 0273 and 0279.

Run on the copy downloaded 2026-10-24 (sha256 b30c04bd7329dc6112fda7247b9fbfd6a3cc28d1e0e9eb66f6a193da1f8952a9):
  python3 -I specs/412-money-basket-every-era/measure/mitsui_basket.py <Japan_1710-1871.xls>
Its output is mitsui_basket.out.txt beside it.
"""

from __future__ import annotations

import statistics
import sys

import xlrd

KYOTO = "Mitsui Bunko Kyoto T6"
EDO = "Mitsui Bunko Edo T7"
OSAKA = "Mitsui Bunko Osaka T8"

# quarterly columns (0-based) of each sheet, from its header rows 1-5
COLS = {
    KYOTO: {"salt": 6, "firewood": 13, "wage": 16},
    EDO: {"salt": 6, "charcoal": 13, "firewood": 14, "wage": 17},
    OSAKA: {"salt": 6, "charcoal": 13, "firewood": 14},
}

LITERS_A_KOKU = 180.891  # the file's "1 koku = 180.891 liters" (sheet "Sources and conversion", row 27)
KG_A_KAN = 3.75  # the file's "1 kan = 3.75 kg" (row 24)
MJ_A_KG = 15.5  # FAO Forestry Paper 93, Appendix IV, Table 2: seasoned wood (air-dried), 20 percent, 15.5 MJ/kg
MJ_A_MMBTU = 1055.06  # a million British thermal units, by definition
SALT_KG_A_LITER = (1.0, 1.2)  # ASSUMED, a guess: no weight of a measure of salt was found


def seasons(sheet):
    """Yield (row number, year, season, row values) for every quarterly row."""
    year = None
    for r in range(8, sheet.nrows):
        vals = sheet.row_values(r)
        if isinstance(vals[0], float):
            year = int(vals[0])
        season = vals[2]
        if year is not None and season in ("Spring", "Fall"):
            yield r + 1, year, season, vals


def cell(vals, col):
    v = vals[col]
    return v if isinstance(v, float) else None


def dump(sheet, name, cols, first, last):
    print(f"\n== row dump: sheet {name!r}, {first}-{last}, columns " + ", ".join(cols))
    for row, year, season, vals in seasons(sheet):
        if first <= year <= last:
            shown = " | ".join(f"{c} {vals[COLS[name][c]]!r}" for c in cols)
            print(f"row {row}: {year} {season} | {shown}")


def span_mean(sheet, name, col, first, last):
    xs = [cell(v, COLS[name][col]) for _, y, _, v in seasons(sheet) if first <= y <= last]
    xs = [x for x in xs if x is not None]
    return (statistics.mean(xs), min(xs), max(xs), len(xs)) if xs else None


def main(path: str) -> None:
    book = xlrd.open_workbook(path)
    k, e, o = (book.sheet_by_name(n) for n in (KYOTO, EDO, OSAKA))

    dump(k, KYOTO, ["salt", "firewood", "wage"], 1745, 1754)
    print("\n== Kyoto 1745-1754, quarterly cells")
    salt = span_mean(k, KYOTO, "salt", 1745, 1754)
    wood = span_mean(k, KYOTO, "firewood", 1745, 1754)
    print(f"salt a koku: mean {salt[0]:.2f}, range {salt[1]}-{salt[2]}, n {salt[3]}")
    print(f"salt a sho: {salt[0] / 100:.3f} monme")
    for d in SALT_KG_A_LITER:
        kg = LITERS_A_KOKU * d
        print(f"  at an ASSUMED {d} kg a liter: a koku {kg:.0f} kg, {salt[0] / kg:.4f} monme a kg")
    print(f"firewood 10 kan: mean {wood[0]:.3f}, range {wood[1]}-{wood[2]}, n {wood[3]}")
    per_kg = wood[0] / (10 * KG_A_KAN)
    kg_mmbtu = MJ_A_MMBTU / MJ_A_KG
    print(f"firewood a kg: {per_kg:.4f} monme; a million BTU = {kg_mmbtu:.1f} kg at {MJ_A_KG} MJ/kg,"
          f" {per_kg * kg_mmbtu:.2f} monme")
    wage = span_mean(k, KYOTO, "wage", 1745, 1754)
    print(f"day wage: mean {wage[0]:.3f}, range {wage[1]}-{wage[2]}, n {wage[3]}")
    print(f"  salt a day's wage bought: {wage[0] / (salt[0] / 100):.1f} sho;"
          f" firewood: {wage[0] / per_kg:.1f} kg")

    dump(e, EDO, ["charcoal", "firewood"], 1710, 1716)
    dump(e, EDO, ["charcoal", "firewood"], 1818, 1823)
    dump(o, OSAKA, ["charcoal", "firewood"], 1818, 1823)
    for sheet, name in ((e, EDO), (o, OSAKA)):
        for a, b in ((1710, 1716), (1818, 1823)):
            c, w = span_mean(sheet, name, "charcoal", a, b), span_mean(sheet, name, "firewood", a, b)
            if c and w:
                print(f"{name} {a}-{b}: charcoal mean {c[0]:.2f} (n {c[3]}), firewood mean {w[0]:.2f} (n {w[3]}),"
                      f" charcoal / firewood {c[0] / w[0]:.2f}")

    print("\n== Edo salt (塩, a koku) by span, quarterly cells, and the cells of 1842")
    for a, b in ((1710, 1716), (1818, 1829), (1830, 1839), (1840, 1849), (1850, 1859)):
        m = span_mean(e, EDO, "salt", a, b)
        print(f"{EDO} {a}-{b}: mean {m[0]:.2f}, range {m[1]}-{m[2]}, n {m[3]}; a sho {m[0] / 100:.3f}")
    dump(e, EDO, ["salt", "charcoal", "firewood", "wage"], 1842, 1842)

    print("\n== day wage (日雇賃) by span, quarterly cells")
    spans = {
        KYOTO: [(1741, 1749), (1750, 1759), (1760, 1762), (1780, 1789), (1791, 1799), (1800, 1809), (1810, 1819),
                (1820, 1829), (1830, 1839), (1840, 1849), (1850, 1859), (1860, 1867), (1868, 1871),
                (1804, 1829), (1830, 1844), (1818, 1859), (1872, 1879)],
        EDO: [(1710, 1716), (1818, 1829), (1830, 1839), (1840, 1849), (1850, 1859), (1818, 1859), (1860, 1867),
              (1868, 1871), (1804, 1830), (1830, 1844), (1872, 1879)],
    }
    for sheet, name in ((k, KYOTO), (e, EDO)):
        for a, b in spans[name]:
            m = span_mean(sheet, name, "wage", a, b)
            print(f"{name} {a}-{b}: " + (f"mean {m[0]:.3f}, range {m[1]}-{m[2]}, n {m[3]}" if m else "no cell"))
    dump(k, KYOTO, ["wage"], 1741, 1871)
    dump(e, EDO, ["wage"], 1710, 1871)


if __name__ == "__main__":
    main(sys.argv[1])
