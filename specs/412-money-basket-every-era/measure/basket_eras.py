"""Era means of the basket's goods in Japan, and the silver of each era's money, for feature 412 session 2.

Every figure printed is this project's arithmetic on cells of public files; the questions it serves are
research/questions/0286-what-did-a-years-necessities-cost-in-japan-era-by-era.html (A) and
research/questions/0287-how-much-silver-was-a-monme-a-ryo-and-a-bu-coinage-by-coinage.html (C).

Inputs, in this order (all downloaded 2026-10-24):
  1. https://gpih.ucdavis.edu/files/Japan_1710-1871.xls - Bassino's transcription of Mitsui Bunko (1989) Tables 6-8.
     QUARTERLY cells only (Spring/Fall), each weighted alike, as session 1's mitsui_basket.py.
  2. https://gpih.ucdavis.edu/files/Japanese%20Wages.xlsx - Kumon (2022), sheet "Japan". A cell with a yellow fill is
     imputed ("yellow highlight indicates years where there are no underlying data and it is imputed", sheet
     "Sources & Notes" row 9): only cells WITHOUT the fill are averaged. Prices in silver monme to 1867 (row 7 of the
     notes), whatever the sheet's own header says.
  3. https://gpih.ucdavis.edu/files/Osaka_1600-1650.xls - Jacks's transcription of Kimura (1987): local-unit columns.
  4. https://gpih.ucdavis.edu/files/Japan_rice_P_1620-1867.xls - Iwahashi (1981) Appendix Table 1, sheet "koku of rice":
     Osaka in monme (column B) and Osaka in ryo (column K); B / K is the gold-silver rate Iwahashi used (Saito's note,
     "Sources and notes" rows 23-26).
  5. https://coin-walk.site/J063.htm - a chronology transcribing 『日本史資料総覧』 (1986): its gold column (monme a
     ryo) and copper column (kanmon a ryo); a year's figure is the middle of its range.

  python3 -I specs/412-money-basket-every-era/measure/basket_eras.py <xls1> <xlsx2> <xls3> <xls4> <J063.htm>
Its output is basket_eras.out.txt beside it.

Conversions (the files' own): 1 koku = 180.891 L (Mitsui) or 180.391 L (Kimura, Iwahashi, as their files print);
1 koku of rice = 150 kg; 1 kan = 3.75 kg; 1 monme = 3.75 g of metal. Grams of pure silver a monme of chogin = 3.75 x
the prescribed fineness (jawiki 丁銀): Keicho 0.80, Genroku 0.64, Futatsu-takara 0.50, Eiji 0.40, Mitsu-takara 0.32,
Yotsu-takara 0.20, Shotoku/Kyoho 0.80, Genbun 0.46, Bunsei 0.36, Tenpo 0.26, Ansei 0.13 (the article's 13%, marked
sic; 14% by its own reckoning).
"""

from __future__ import annotations

import html
import re
import statistics
import sys

import openpyxl
import xlrd

FINENESS = {"Keicho": 0.80, "Genroku": 0.64, "Futatsu-takara": 0.50, "Eiji": 0.40, "Mitsu-takara": 0.32,
            "Yotsu-takara": 0.20, "Shotoku/Kyoho": 0.80, "Genbun": 0.46, "Bunsei": 0.36, "Tenpo": 0.26,
            "Ansei": 0.13, "Ansei (14%)": 0.14}
G_A_MONME = 3.75

MITSUI = {
    "Mitsui Bunko Kyoto T6": {"rice": 3, "mugi": 4, "salt": 6, "firewood": 13, "lampoil": 14, "wage": 16},
    "Mitsui Bunko Edo T7": {"rice": 3, "mugi": 4, "salt": 6, "charcoal": 13, "firewood": 14, "lampoil": 15,
                            "wage": 17},
    "Mitsui Bunko Osaka T8": {"rice": 3, "mugi": 4, "salt": 6, "charcoal": 13, "firewood": 14, "lampoil": 15},
}
ERAS_MITSUI = [
    ("Kyoto T6", 1713, 1713), ("Edo T7", 1710, 1716), ("Osaka T8", 1713, 1713),
    ("Kyoto T6", 1745, 1754), ("Kyoto T6", 1791, 1799), ("Kyoto T6", 1800, 1817),
    ("Edo T7", 1818, 1829), ("Kyoto T6", 1818, 1829), ("Osaka T8", 1818, 1829),
    ("Kyoto T6", 1830, 1844), ("Edo T7", 1830, 1844), ("Osaka T8", 1830, 1844),
    ("Kyoto T6", 1850, 1859), ("Edo T7", 1850, 1859), ("Osaka T8", 1850, 1859),
    ("Kyoto T6", 1860, 1867), ("Edo T7", 1860, 1867), ("Osaka T8", 1860, 1867),
]
KUMON_COLS = {"wage": 1, "rice": 3, "soy": 4, "beans": 5, "barley": 6, "buckwheat": 7, "fish": 8, "edoil": 9,
              "sake": 10, "lampoil": 11, "cloth": 12}  # 0-based columns of sheet "Japan", header rows 6-10
ERAS = [(1620, 1650), (1690, 1739), (1690, 1699), (1700, 1709), (1710, 1719), (1720, 1729), (1730, 1739),
        (1745, 1754), (1780, 1789), (1790, 1799), (1800, 1817), (1818, 1829), (1830, 1844), (1850, 1859),
        (1860, 1867)]


def mean(xs):
    xs = [x for x in xs if x is not None]
    return (statistics.mean(xs), min(xs), max(xs), len(xs)) if xs else None


def fmt(m, d=2):
    return "-" if m is None else f"{m[0]:.{d}f} ({m[1]:g}-{m[2]:g}, n {m[3]})"


def mitsui(path):
    print("== Mitsui Bunko (GPIH Japan_1710-1871.xls), quarterly cells, silver monme of account")
    print("   rice, mugi, salt, lamp oil a koku; firewood, charcoal 10 kan; wage a day")
    book = xlrd.open_workbook(path)
    for short, a, b in ERAS_MITSUI:
        name = "Mitsui Bunko " + short
        sh, cols = book.sheet_by_name(name), MITSUI["Mitsui Bunko " + short]
        rows, year = [], None
        for r in range(8, sh.nrows):
            v = sh.row_values(r)
            if isinstance(v[0], float):
                year = int(v[0])
            if year is not None and a <= year <= b and v[2] in ("Spring", "Fall"):
                rows.append(v)
        out = []
        for good, c in cols.items():
            m = mean([x[c] if isinstance(x[c], float) else None for x in rows])
            out.append(f"{good} {fmt(m)}")
        print(f"{short} {a}-{b}: " + "; ".join(out))
    sh = book.sheet_by_name("Mitsui Bunko Kyoto T6")
    print("Kyoto salt cells by year, 1741-1762 and 1791-1800 (the drop):")
    year = None
    for r in range(8, sh.nrows):
        v = sh.row_values(r)
        if isinstance(v[0], float):
            year = int(v[0])
        if year and (1758 <= year <= 1762 or 1791 <= year <= 1793) and v[2] in ("Spring", "Fall"):
            print(f"  row {r + 1}: {year} {v[2]} salt {v[6]!r}")


def kumon(path):
    print("\n== Kumon (GPIH Japanese Wages.xlsx), sheet Japan, OBSERVED cells only (no yellow fill)")
    print("   wage: a farm servant's year, monme; rice..fish a kg; oils, sake a liter; cloth a tan")
    ws = openpyxl.load_workbook(path)["Japan"]
    data = {}
    for row in ws.iter_rows(min_row=11):
        y = row[0].value  # column A is the year
        if not isinstance(y, (int, float)):
            continue
        y = int(y)
        cells = {}
        for good, c in KUMON_COLS.items():
            cell = row[c]
            fill = cell.fill.fgColor.rgb if cell.fill and cell.fill.fill_type else None
            yellow = isinstance(fill, str) and fill.upper().endswith("FFFF00")
            cells[good] = (cell.value, yellow)
        data[y] = cells
    for a, b in ERAS:
        out = []
        for good in KUMON_COLS:
            xs = [data[y][good][0] for y in range(a, b + 1)
                  if y in data and isinstance(data[y][good][0], (int, float)) and not data[y][good][1]]
            m = mean(xs)
            if m:
                out.append(f"{good} {fmt(m, 4)}")
        print(f"{a}-{b}: " + "; ".join(out))
    print("Imputed (yellow) count by good, 1620-1867:")
    for good in KUMON_COLS:
        n = sum(1 for y in range(1620, 1868) if y in data and data[y][good][1])
        print(f"  {good}: {n} imputed of {sum(1 for y in range(1620, 1868) if y in data)} years")
    for y in (1620, 1650, 1700, 1720, 1735, 1750, 1786, 1820, 1842, 1867):
        if y in data:
            print(f"  row {y}: " + ", ".join(f"{g} {v!r}{'*' if yl else ''}" for g, (v, yl) in data[y].items()))


def kimura(path):
    print("\n== Kimura via Jacks (GPIH Osaka_1600-1650.xls), local-unit cells, silver monme, 1620-1650")
    book = xlrd.open_workbook(path)
    specs = [("starches", {"rice /koku": 1, "soybeans /koku": 2, "soya /sho": 3}),
             ("misc", {"salt /to": 1, "oil /sho": 4, "sake /to": 5}),
             ("cloth", {"white cloth /tan": 1, "cloth /tan": 3, "bleached cotton /tan": 4})]
    for sheet, cols in specs:
        sh = book.sheet_by_name(sheet)
        for good, c in cols.items():
            xs = []
            for r in range(sh.nrows):
                v = sh.row_values(r)
                if isinstance(v[0], float) and 1620 <= v[0] <= 1650 and isinstance(v[c], float):
                    xs.append((int(v[0]), v[c]))
            m = mean([x for _, x in xs])
            print(f"{good}: {fmt(m)} cells {xs}")


def iwahashi(path):
    print("\n== Iwahashi (GPIH Japan_rice_P_1620-1867.xls), sheet koku of rice")
    sh = xlrd.open_workbook(path).sheet_by_name("koku of rice")
    rows = {}
    for r in range(8, sh.nrows):
        v = sh.row_values(r)
        if isinstance(v[0], float):
            rows[int(v[0])] = v
    col = {"Osaka monme": 1, "Hiroshima monme": 5, "Edo ryo": 9, "Osaka ryo": 10}
    for a, b in ERAS:
        out = []
        for name, c in col.items():
            m = mean([rows[y][c] if y in rows and isinstance(rows[y][c], float) else None for y in range(a, b + 1)])
            out.append(f"{name} {fmt(m, 3)}")
        ratio = mean([rows[y][1] / rows[y][10] for y in range(a, b + 1) if y in rows
                      and isinstance(rows[y][1], float) and isinstance(rows[y][10], float) and rows[y][10]])
        print(f"{a}-{b}: " + "; ".join(out) + f"; Osaka monme / Osaka ryo (gold rate) {fmt(ratio, 1)}")
    for y in (1701, 1710, 1720, 1736, 1750, 1786):
        if y in rows:
            print(f"  row {y}: Osaka monme {rows[y][1]!r}, Osaka ryo {rows[y][10]!r}")
    return rows


def coinwalk(path):
    print("\n== coin-walk J063 (transcribing 日本史資料総覧 1986): gold monme a ryo, copper kanmon a ryo, mid of range")
    t = open(path, encoding="utf-8-sig").read()
    gold, copper = {}, {}
    for r in re.split(r"<TR[^>]*>", t):
        cells = [html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<!-+>", "", c))).strip()
                 for c in re.split(r"<TD[^>]*>", r)[1:]]
        if len(cells) >= 7 and re.fullmatch(r"1[5-8]\d\d", cells[1]):
            y = int(cells[1])
            for store, c in ((gold, cells[5]), (copper, cells[6])):
                if "公定" in c or not c:
                    continue
                # only rows quoting one money: a lone range or figure, nothing coin-specific
                m = re.fullmatch(r"(?:江戸の相場\s*)?([\d.,]+)(?:～([\d.,]+))?", re.sub(r"\s+", "", c))
                if m:
                    lo = float(m.group(1).replace(",", ""))
                    hi = float((m.group(2) or m.group(1)).replace(",", ""))
                    store[y] = (lo + hi) / 2
    for a, b in ERAS + [(1722, 1735), (1737, 1739), (1740, 1749), (1780, 1786), (1860, 1867), (1855, 1859)]:
        g = mean([gold.get(y) for y in range(a, b + 1)])
        c = mean([copper.get(y) for y in range(a, b + 1)])
        print(f"{a}-{b}: gold {fmt(g, 1)}; copper kanmon a ryo {fmt(c, 3)}")
    return gold, copper


def silver(gold_cw, copper_cw):
    print("\n== grams of pure silver a monme, a ryo and a mon (this project's arithmetic)")
    for coin, f in FINENESS.items():
        print(f"{coin}: {G_A_MONME * f:.4f} g a monme")
    # era -> (chogin, monme a ryo, mon a ryo), each rate named with its source in the question
    eras = [
        ("Osaka 1620-1650, legal 1609", "Keicho", 50, 4000),
        ("Osaka 1620-1650, c.43 monme (三貨制度)", "Keicho", 43, None),
        ("1690-1694 coin-walk", "Keicho", mean([gold_cw.get(y) for y in range(1690, 1695)])[0], None),
        ("1700 legal", "Genroku", 60, 4000),
        ("1700 market 47-48 (coin-walk)", "Genroku", 47.5, 3710),
        ("1722-1735 coin-walk", "Shotoku/Kyoho", mean([gold_cw.get(y) for y in range(1722, 1736)])[0],
         1000 * mean([copper_cw.get(y) for y in range(1722, 1736)])[0]),
        ("1737-1739 coin-walk", "Genbun", mean([gold_cw.get(y) for y in range(1737, 1740)])[0],
         1000 * mean([copper_cw.get(y) for y in range(1737, 1740)])[0]),
        ("Kyoto 1745-1754 coin-walk", "Genbun", mean([gold_cw.get(y) for y in range(1745, 1755)])[0],
         1000 * mean([copper_cw.get(y) for y in range(1745, 1755)])[0]),
        ("Osaka 1780-1786 coin-walk", "Genbun", mean([gold_cw.get(y) for y in range(1780, 1787)])[0],
         1000 * mean([copper_cw.get(y) for y in range(1780, 1787)])[0]),
        ("Osaka 1787-1789 RIEB (0277)", "Genbun", 55.6, 5860),
        ("Kyoto 1790-1799 at Osaka RIEB (0277)", "Genbun", 60.6, 6470),
        ("Kyoto 1800-1817 at Osaka RIEB 1800s/1810s (0277)", "Genbun", (64.3 + 64.6) / 2, (6990 + 7060) / 2),
        ("Edo 1818-1829, Osaka RIEB 1820s (0277), Genbun", "Genbun", 63.4, 6880),
        ("Edo 1818-1829, Osaka RIEB 1820s (0277), Bunsei", "Bunsei", 63.4, 6880),
        ("Edo 1818-1829, Edo mon a ryo 1820s 6,610 (0277)", "Bunsei", 63.4, 6610),
        ("1830-1844 Osaka RIEB 1830s (0277), Bunsei", "Bunsei", 61.8, 6790),
        ("1830-1844 Osaka RIEB 1840-43 (0277), Tenpo", "Tenpo", 62.8, 6790),
        ("1850-1859 Osaka RIEB 1850-54 (0277), Tenpo", "Tenpo", 64.1, 6710),
        ("1850-1859 Osaka RIEB 1855-59 (0277), Tenpo", "Tenpo", 70.9, 6740),
        ("1860-1867 coin-walk, Tenpo", "Tenpo", mean([gold_cw.get(y) for y in range(1860, 1868)])[0],
         1000 * mean([copper_cw.get(y) for y in range(1860, 1868)])[0]),
        ("1860-1867 coin-walk, Ansei", "Ansei", mean([gold_cw.get(y) for y in range(1860, 1868)])[0],
         1000 * mean([copper_cw.get(y) for y in range(1860, 1868)])[0]),
        ("1860-1867 coin-walk, Ansei at 14%", "Ansei (14%)", mean([gold_cw.get(y) for y in range(1860, 1868)])[0],
         1000 * mean([copper_cw.get(y) for y in range(1860, 1868)])[0]),
    ]
    for label, coin, monme_ryo, mon_ryo in eras:
        g = G_A_MONME * FINENESS[coin]
        line = f"{label}: {coin} {g:.3f} g/monme; {monme_ryo:.1f} monme a ryo = {monme_ryo * g:.1f} g a ryo"
        line += f", a bu {monme_ryo * g / 4:.1f} g"
        if mon_ryo:
            mon_monme = mon_ryo / monme_ryo
            line += (f"; {mon_ryo:.0f} mon a ryo, {mon_monme:.1f} mon a monme, a mon {g / mon_monme:.4f} g,"
                     f" a kanmon {1000 * g / mon_monme:.1f} g")
        print(line)
    print("\nCoins themselves:")
    print(f"nanryo nishugin 1772: 2.7 monme x 3.75 x 0.9781 = {2.7 * 3.75 * 0.9781:.2f} g; 8 to the ryo"
          f" {8 * 2.7 * 3.75 * 0.9781:.1f} g; wiki 21.6 monme a ryo = {21.6 * 3.75:.1f} g")
    print(f"Bunsei nanryo 1824: 2 monme x 3.75 x 0.9796 = {2 * 3.75 * 0.9796:.2f} g; 8 to the ryo"
          f" {8 * 2 * 3.75 * 0.9796:.1f} g")
    print(f"Tenpo ichibu-gin 1837: 2.3 x 3.75 x 0.9886 = {2.3 * 3.75 * 0.9886:.2f} g; 4 to the ryo"
          f" {4 * 2.3 * 3.75 * 0.9886:.1f} g; wiki 9.2 monme = {9.2 * 3.75:.1f} g, Tenpo chogin 15.6 monme ="
          f" {15.6 * 3.75:.1f} g")
    print(f"Ansei ichibu-gin 1859: 2.3 x 3.75 x 0.8936 = {2.3 * 3.75 * 0.8936:.2f} g; 4 to the ryo"
          f" {4 * 2.3 * 3.75 * 0.8936:.1f} g")
    print(f"1773 order: 24 monme pure = {24 * 3.75:.0f} g a ryo; 60 monme circulating -> {24 * 3.75 / 60:.2f} g"
          f" a monme; Genbun prescribed {3.75 * 0.46:.3f}")
    print(f"Genbun ryo at 60 monme by fineness: {60 * 3.75 * 0.46:.1f} g (wiki 27.6 monme = {27.6 * 3.75:.1f} g)")
    print("Koban gold: " + ", ".join(f"{n} {w * 3.75 * f:.2f} g" for n, w, f in (
        ("Keicho", 4.76, 0.843), ("Keicho 86.8%", 4.76, 0.868), ("Genroku", 4.76, 0.574), ("Hoei", 2.5, 0.843),
        ("Shotoku", 4.76, 0.843), ("Kyoho", 4.76, 0.868), ("Genbun", 3.5, 0.657), ("Bunsei", 3.5, 0.564),
        ("Tenpo", 3.0, 0.568), ("Ansei", 2.4, 0.568), ("Man'en", 0.88, 0.568))))
    print("Bassino and Ma 3.11 g / 3.75 g = {:.3f}".format(3.11 / 3.75))


def main(argv):
    mitsui(argv[1])
    kumon(argv[2])
    kimura(argv[3])
    iwahashi(argv[4])
    gold, copper = coinwalk(argv[5])
    silver(gold, copper)


if __name__ == "__main__":
    main(sys.argv)
