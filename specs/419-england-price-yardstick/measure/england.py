#!/usr/bin/env python3
"""Feature 419 (diagram#15): how far English prices moved under commodity money - this project's arithmetic from the
Bank of England's millennium dataset and Clark's English prices and wages, the comparative yardstick beside the Edo and
Qing series (0290) and the modern one (0291).

    python3 -I england.py <boe.xlsx> <clark.xls>

The first file is the Bank of England's "A millennium of macroeconomic data for the UK" (version 3.1, fetched 2026-10-25):
https://www.bankofengland.co.uk/-/media/boe/files/statistics/research-datasets/a-millennium-of-macroeconomic-data-for-the-uk.xlsx
read from sheet "A47. Wages and prices", column D, "Consumer Price Index (CPI) - preferred measure".
The second is Clark's series as reformatted by Peter Lindert for the GPIH site (fetched 2026-10-25):
http://gpih.ucdavis.edu/files/England_1209-1914_(Clark).xls
read from its "main data sheet", one column per good, prices in pence.
The measure is the one 0290 and 0291 use, the standard deviation of annual log changes (population SD, as a percent),
between consecutive years both present; drift is the mean log change a year from the year before the first to the last.
"""

from __future__ import annotations

import math
import statistics
import sys

import openpyxl
import xlrd

PERIODS = [(1210, 1499), (1500, 1650), (1651, 1750), (1751, 1913), (1821, 1913), (1972, 2016), (1984, 2016)]
CENTURIES = [(1300, 1400), (1400, 1500), (1500, 1600), (1600, 1700), (1700, 1800), (1800, 1900), (1900, 2000)]
GOOD_PERIODS = [(1210, 1499), (1500, 1650), (1651, 1750), (1751, 1869)]
GOODS = ["Wheat", "Barley", "Oats", "Peas", "Salt", "Charcoal", "Firewood", "Oil-lamp", "Woolcloth", "Wage, bldg laborer", "Wage, farm"]


def boe(path: str) -> tuple[dict[int, float], dict[int, float], str]:
    """({year: CPI}, {year: the sheet's Clark (2009,2014) consumer price column}, the CPI column's source note) from A47."""
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True)["A47. Wages and prices"]
    rows = list(ws.iter_rows(min_row=1, max_row=830, values_only=True))
    clark_col = next(i for i, h in enumerate(rows[2]) if h and "Consumer Price indices" in str(h) and str(rows[4][i]).startswith("Clark"))
    cpi: dict[int, float] = {}
    col: dict[int, float] = {}
    for r in rows[6:]:
        try:
            y = int(r[0])
        except TypeError, ValueError:
            continue
        if isinstance(r[3], (int, float)):
            cpi[y] = float(r[3])
        if isinstance(r[clark_col], (int, float)):
            col[y] = float(r[clark_col])
    return cpi, col, str(rows[4][3])


def clark(path: str) -> dict[str, dict[int, float]]:
    """{good: {year: price in pence}} for GOODS, positive values only."""
    s = xlrd.open_workbook(path).sheet_by_name("main data sheet")
    names = [str(c.value) for c in s.row(5)]
    out: dict[str, dict[int, float]] = {}
    for good in GOODS:
        c = names.index(good)
        ser: dict[int, float] = {}
        for r in range(8, s.nrows):
            try:
                y, v = int(float(s.cell_value(r, 0))), float(s.cell_value(r, c))
            except ValueError:
                continue
            if v > 0:
                ser[y] = v
        out[good] = ser
    return out


def changes(p: dict[int, float], lo: int, hi: int) -> list[float]:
    return [100 * math.log(p[y] / p[y - 1]) for y in range(lo, hi + 1) if y in p and y - 1 in p]


def main() -> None:
    cpi, col, note = boe(sys.argv[1])
    print("## Bank of England, CPI preferred measure (sheet A47, column D)\n")
    print(f"- years {min(cpi)}-{max(cpi)}; the column's source note: {note}")
    ratios = sorted({round(cpi[y] / col[y], 5) for y in range(min(cpi), 1661) if y in col})
    print(f"- CPI over the sheet's Clark (2009,2014) consumer price column, {min(cpi)}-1660: {ratios}\n")
    print("| years | drift a year | SD of annual changes | years moving more than 10% |")
    print("|---|---|---|---|")
    for lo, hi in PERIODS:
        xs = changes(cpi, lo, hi)
        drift = 100 * math.log(cpi[hi] / cpi[lo - 1]) / (hi - lo + 1)
        big = sum(1 for x in xs if abs(x) > 10)
        print(f"| {lo}-{hi} | {drift:+.2f}% | {statistics.pstdev(xs):.1f}% ({len(xs)}) | {big} of {len(xs)} |")
    print("\n| century | price level, end over start | a year |")
    print("|---|---|---|")
    for a, b in CENTURIES:
        print(f"| {a}-{b} | x{cpi[b] / cpi[a]:.2f} | {100 * ((cpi[b] / cpi[a]) ** 0.01 - 1):+.2f}% |")
    d = [100 * math.log(cpi[y + 10] / cpi[y]) for y in range(1210, 1490) if y in cpi and y + 10 in cpi]
    print(f"\n- ten-year log changes 1210-1499: mean {statistics.mean(d):+.1f}%, SD {statistics.pstdev(d):.1f}, from {min(d):+.1f}% to {max(d):+.1f}% ({len(d)})\n")
    print("## Clark, English prices and wages (GPIH, main data sheet)\n")
    print("SD of annual log changes, with the number of year pairs; over the whole series, the largest rise and fall and the")
    print("year pairs with no change at all (a flat run can be a fixed price or a gap filled by its compiler; the file does not")
    print("say which).\n")
    print("| good | " + " | ".join(f"{lo}-{hi}" for lo, hi in GOOD_PERIODS) + " | largest rise, fall | unchanged |")
    print("|---|" + "---|" * (len(GOOD_PERIODS) + 2))
    for good, ser in clark(sys.argv[2]).items():
        cells = []
        for lo, hi in GOOD_PERIODS:
            xs = changes(ser, lo, hi)
            cells.append(f"{statistics.pstdev(xs):.1f}% ({len(xs)})" if len(xs) > 10 else "-")
        allx = changes(ser, min(ser) + 1, max(ser))
        rise, fall = math.exp(max(allx) / 100) - 1, math.exp(min(allx) / 100) - 1
        flat = sum(1 for x in allx if x == 0)
        print(f"| {good} | " + " | ".join(cells) + f" | {100 * rise:+.0f}%, {100 * fall:+.0f}% | {flat} of {len(allx)} |")


if __name__ == "__main__":
    main()
