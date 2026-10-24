"""Era means and conversions for China's basket and its money, for feature 412 session 3.

Every figure printed is this project's arithmetic on cells of public files or on figures quoted from texts; the
questions it serves are research/questions/0288-what-did-a-years-necessities-and-a-days-labor-cost-in-china-era-by-era.html
(B) and research/questions/0289-what-was-a-tael-a-string-of-cash-and-a-chinese-dollar-worth-in-silver.html (D).

Inputs, in this order (all downloaded 2026-10-24):
  1. https://gpih.ucdavis.edu/files/China_1730-1933_Allen_et_al.xls - sheets "Beijing prices" (grams of silver) and
     "Figures2-6" (silver wages, grams a day).
  2. https://gpih.ucdavis.edu/files/Beijing_prices_1900-1924.xls - sheet "Prices", the local-currency columns B-H
     (dollars a 100 catties).
  3. https://gpih.ucdavis.edu/files/China_wages_1807-1925.xls - sheet "Wages Beijing Urban", column B (silver cents).
  4. https://gpih.ucdavis.edu/files/China_rice_prices_%20961-1910.xls - sheet "Peng rice series", rows 30-59 (Song
     decades, grams of silver a hectoliter).

  python3 -I specs/412-money-basket-every-era/measure/china_eras.py <xls1> <xls2> <xls3> <xls4>
Its output is china_eras.out.txt beside it. Cell dumps of the four files: measure/china_*_cells_by_address.txt.
"""

from __future__ import annotations

import sys

import xlrd


def rows(book, sheet):
    sh = book.sheet_by_name(sheet)
    return [sh.row_values(r) for r in range(sh.nrows)]


def num(v):
    return v if isinstance(v, float) and v != 0.0 else None


def mean_by_years(table, col, lo, hi):
    vals = [num(r[col]) for r in table if isinstance(r[0], float) and lo <= r[0] <= hi]
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    return sum(vals) / len(vals), min(vals), max(vals), len(vals)


def fmt(m):
    return "-" if m is None else f"{m[0]:.3f} ({m[1]:.3f}-{m[2]:.3f}, n {m[3]})"


def main(allen, bjp, wages, rice):
    a = xlrd.open_workbook(allen)
    bp = rows(a, "Beijing prices")
    cols = {"wheat flour": 3, "millet": 4, "bean flour": 5, "corn flour": 6, "rice (lao mi)": 7, "beans": 8,
            "sorghum": 9, "meat": 10, "edible oil": 12, "cloth (sq m)": 14, "lamp oil": 16, "fuel (M BTU)": 17}
    print("== Allen et al. Beijing prices, grams of silver (per kg; oils per liter; cloth per sq m; fuel per M BTU)")
    for lo, hi in [(1738, 1760), (1745, 1754), (1820, 1830)]:
        print(f"-- {lo}-{hi}")
        for name, c in cols.items():
            print(f"   {name}: {fmt(mean_by_years(bp, c, lo, hi))}")
    fw = rows(a, "Figures2-6")
    print("== Allen et al. silver wages, grams a day (Figures2-6: F Beijing, G Suzhou, H Canton)")
    for name, c, lo, hi in [("Beijing", 5, 1738, 1760), ("Beijing", 5, 1820, 1830), ("Suzhou", 6, 1750, 1799),
                            ("Canton", 7, 1830, 1839)]:
        print(f"   {name} {lo}-{hi}: {fmt(mean_by_years(fw, c, lo, hi))}")

    b = xlrd.open_workbook(bjp)
    pr = rows(b, "Prices")
    print("== Meng and Gamble, Beijing retail, dollars a 100 catties")
    for lo, hi in [(1900, 1909), (1910, 1919)]:
        print(f"-- {lo}-{hi}")
        for name, c in {"flour": 1, "wheat": 2, "rice": 3, "bean flour": 4, "millet retail": 5, "corn flour": 7}.items():
            print(f"   {name}: {fmt(mean_by_years(pr, c, lo, hi))}")

    w = xlrd.open_workbook(wages)
    wu = rows(w, "Wages Beijing Urban")
    print("== Meng and Gamble, Beijing unskilled construction wage, silver cents a day (with food)")
    for lo, hi in [(1900, 1909), (1910, 1919), (1900, 1919)]:
        print(f"   {lo}-{hi}: {fmt(mean_by_years(wu, 1, lo, hi))}")

    r = xlrd.open_workbook(rice)
    pg = rows(r, "Peng rice series")
    song = [(row[0].strip(), row[1]) for row in pg[29:59]]
    print("== Peng's Song decades via Liu, grams of silver a hectoliter")
    for lab, v in song:
        print(f"   {lab}: {v}")
    for name, lo, hi in [("961-1120 (to the Jin war)", 0, 16), ("1001-1100", 4, 14), ("1141-1260", 18, 30),
                         ("all 30 decades", 0, 30)]:
        vals = [v for _, v in song[lo:hi]]
        print(f"   mean {name}: {sum(vals) / len(vals):.2f} (n {len(vals)}, {min(vals)}-{max(vals)})")

    print("== Cash a tael, from the texts")
    pairs = {
        "1632 Songjiang (120 wen = 0.1 tael)": 120 / 0.1,
        "1671 Songjiang (1,300 wen = 1.1 tael)": 1300 / 1.1,
        "1672 Songjiang (700 wen = 0.63 tael)": 700 / 0.63,
        "1678-79 low (1,000 = 0.93)": 1000 / 0.93,
        "1678-79 high (1,000 = 0.87)": 1000 / 0.87,
        "1682 Songjiang (350 wen = 0.315)": 350 / 0.315,
        "1690 low (1,000 = 1.03)": 1000 / 1.03,
        "1690 high (1,000 = 1.02)": 1000 / 1.02,
        "c.1628-30 capital (1,000 = 1.2)": 1000 / 1.2,
        "c.1628-30 provinces (1,000 = 0.9)": 1000 / 0.9,
        "1638 (1,000 = 0.6)": 1000 / 0.6,
        "Ming Hongzhi (700 to a tael)": 700,
        "1508 (70 wen = 0.1)": 70 / 0.1,
        "1525 (7 = 0.01)": 7 / 0.01,
        "Longqing (8 = 0.01)": 8 / 0.01,
        "Wanli gold-back first cast (10 = 0.01)": 10 / 0.01,
        "Wanli gold-back later (5 = 0.01)": 5 / 0.01,
        "1628 casting (55 = 0.1)": 55 / 0.1,
    }
    for k, v in pairs.items():
        print(f"   {k}: {v:.0f}")

    print("== Rice in Suzhou-Songjiang (Qian Yong), taels a shi = wen a sheng x 100 / cash a tael")
    for lab, wen, lo, hi in [("mid-Qianlong 14-15 wen at 760-840", (14, 15), 760, 840),
                             ("after 1785, 27-35 wen at 1,300-1,400 (1796)", (27, 35), 1300, 1400)]:
        print(f"   {lab}: {wen[0] * 100 / hi:.2f}-{wen[1] * 100 / lo:.2f}")

    print("== Silver")
    print(f"   a dollar at 0.72 tael x 37 g: {0.72 * 37:.2f} g")
    print(f"   a tael at Liu's kuping 36.9 / 37.3 g; Song 37.68 g; Allen 37 g")
    print(f"   a mace (0.1 tael) at 37 g: {3.7:.1f} g; Beijing 1736 75 cash at 800 a tael: {75 / 800:.4f} tael, "
          f"{75 / 800 * 37:.2f} g")
    print(f"   grams a 1,000 cash at 37 g a tael: 700 -> {37000 / 700:.1f}; 800 -> {37000 / 800:.1f}; "
          f"1,000 -> {37000 / 1000:.1f}; 1,200 -> {37000 / 1200:.1f}; 1,300 -> {37000 / 1300:.1f}; "
          f"1,400 -> {37000 / 1400:.1f}; 2,000 -> {37000 / 2000:.1f}")
    print(f"   Gamble rent $5-12 a year = ${5 / 12:.2f}-{12 / 12:.2f} a month = {5 * 26.64:.0f}-{12 * 26.64:.0f} g a year")
    print(f"   Meng-Gamble wage 19.1-27.2 cents x 26.64 g/$: {0.191 * 26.64:.2f}-{0.272 * 26.64:.2f} g")


if __name__ == "__main__":
    main(*sys.argv[1:5])
